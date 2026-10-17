"""Turn analysis of the user's OWN footage into concrete edit decisions.

Outputs (all deterministic, all suggestions for Claude and the user to review):
  * QA flags            what is likely to hurt the edit, with plain-language fixes
  * keep ranges         a tight cut: fillers, long pauses and retakes removed
  * edit-plan.json      clips / captions / zoom slots on tracks, in seconds, ready to be
                        mapped onto a Hyperframes composition (see references/hyperframes-mapping.md)
  * preview.mp4         optional quick ffmpeg render of the keep ranges
"""
from __future__ import annotations

import difflib
import re
from pathlib import Path

from runtime import ToolError, fmt_time, log, run
from speech import find_fillers, norm
from transcribe_cpp import words_to_segments

DEFAULT_OPTS = {
    "max_pause": 0.70,     # pauses longer than this are shortened...
    "keep_pause": 0.25,    # ...to this
    "pad": 0.06,           # breathing room kept around speech at the start/end
    "min_keep": 0.30,      # drop kept fragments shorter than this
    "merge_gap": 0.10,     # merge kept fragments closer than this
    "cut_fillers": True,
    "cut_retakes": True,
    "trim_ends": True,     # trim dead lead-in/tail around speech (talking-video default)
    "caption_words": 3,
    "target_lufs": -14.0,
    "jump_cut_zoom": False,
}


# ---------------------------------------------------------------- retakes
def detect_retakes(segments: list[dict], max_gap: float = 20.0, ratio: float = 0.72) -> list[dict]:
    """Find an earlier sentence that the speaker immediately re-did.
    Keeps the LATER take, flags the earlier one. Heuristic: review before trusting."""
    flagged: dict[int, dict] = {}
    toks = [[norm(w) for w in s["text"].split() if norm(w)] for s in segments]
    for i, a in enumerate(segments):
        for j in range(i + 1, min(i + 4, len(segments))):
            b = segments[j]
            if b["start"] - a["end"] > max_gap:
                break
            wa, wb = toks[i], toks[j]
            if len(wa) < 3 or len(wb) < 3:
                continue
            false_start = len(wa) < len(wb) and wa == wb[:len(wa)]
            similar = difflib.SequenceMatcher(None, " ".join(wa), " ".join(wb)).ratio() >= ratio
            if false_start or similar:
                flagged[i] = {"start": a["start"], "end": a["end"], "text": a["text"],
                              "reason": "retake", "superseded_by": j}
                break
    return [flagged[k] for k in sorted(flagged)]


# ---------------------------------------------------------------- keep ranges
def _merge(intervals: list[tuple[float, float, set]]) -> list[tuple[float, float, set]]:
    out: list[tuple[float, float, set]] = []
    for s, e, r in sorted(intervals, key=lambda x: (x[0], x[1])):
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e), out[-1][2] | r)
        else:
            out.append((s, e, set(r)))
    return out


def build_keep_ranges(words: list[dict], segments: list[dict], t0: float, t1: float,
                      opts: dict | None = None) -> tuple[list[dict], list[dict]]:
    """Return (keep, removed). keep=[{'in','out'}]; removed=[{'start','end','reasons','text'}]."""
    o = {**DEFAULT_OPTS, **(opts or {})}
    if not words:
        return [{"in": round(t0, 3), "out": round(t1, 3)}], []

    cut: list[tuple[float, float, set]] = []
    labels: dict[tuple[float, float], str] = {}

    if o["cut_fillers"]:
        for f in find_fillers(words):
            if f["kind"] == "hard":
                cut.append((max(t0, f["start"] - 0.02), min(t1, f["end"] + 0.02), {"filler"}))
                labels[(round(f["start"], 3), round(f["end"], 3))] = f["text"]
    if o["cut_retakes"]:
        # Finer sentence splits than the transcript view: false starts often follow a short pause.
        fine = words_to_segments(words, gap=0.45, max_words=18)
        for r in detect_retakes(fine):
            cut.append((max(t0, r["start"] - 0.03), min(t1, r["end"] + 0.03), {"retake"}))
            labels[(round(r["start"], 3), round(r["end"], 3))] = r["text"]

    half = o["keep_pause"] / 2
    for a, b in zip(words, words[1:]):
        gap = b["start"] - a["end"]
        if gap > o["max_pause"]:
            cut.append((a["end"] + half, b["start"] - half, {"pause"}))
    if o["trim_ends"]:
        if words[0]["start"] - t0 > o["pad"] + 0.05:
            cut.append((t0, words[0]["start"] - o["pad"], {"lead-in"}))
        if t1 - words[-1]["end"] > o["pad"] + 0.05:
            cut.append((words[-1]["end"] + o["pad"], t1, {"tail"}))

    cut = [c for c in cut if c[1] > c[0]]
    removed_iv = _merge(cut)

    keep_iv: list[tuple[float, float]] = []
    cursor = t0
    for s, e, _ in removed_iv:
        if s > cursor:
            keep_iv.append((cursor, s))
        cursor = max(cursor, e)
    if cursor < t1:
        keep_iv.append((cursor, t1))

    merged: list[list[float]] = []
    for s, e in keep_iv:
        if merged and s - merged[-1][1] < o["merge_gap"]:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    keep = [{"in": round(s, 3), "out": round(e, 3)} for s, e in merged if e - s >= o["min_keep"]]

    removed = []
    for s, e, reasons in removed_iv:
        text = " ".join(t for (ls, le), t in labels.items() if ls < e and le > s)
        removed.append({"start": round(s, 3), "end": round(e, 3), "duration": round(e - s, 3),
                        "reasons": sorted(reasons), "text": text})
    return keep or [{"in": round(t0, 3), "out": round(t1, 3)}], removed


def cutlist_stats(keep: list[dict], removed: list[dict], t0: float, t1: float) -> dict:
    new = sum(k["out"] - k["in"] for k in keep)
    by_reason: dict[str, float] = {}
    for r in removed:
        for reason in r["reasons"]:
            by_reason[reason] = round(by_reason.get(reason, 0.0) + r["duration"], 2)
    return {"original_duration": round(t1 - t0, 2), "new_duration": round(new, 2),
            "removed_total": round((t1 - t0) - new, 2),
            "removed_share": round(1 - new / (t1 - t0), 3) if t1 > t0 else 0.0,
            "removed_seconds_by_reason": by_reason, "clip_count": len(keep)}


# ---------------------------------------------------------------- timeline mapping
def timeline_map(keep: list[dict]) -> list[tuple[float, float, float]]:
    out, tl = [], 0.0
    for k in keep:
        out.append((k["in"], k["out"], tl))
        tl += k["out"] - k["in"]
    return out


def map_time(t: float, tmap: list[tuple[float, float, float]]) -> float | None:
    for s, e, tl in tmap:
        if s <= t <= e:
            return round(tl + (t - s), 3)
    return None


def build_captions(words: list[dict], tmap, words_per_caption: int = 3) -> list[dict]:
    """Group kept words into short on-screen captions with per-word timing (timeline seconds)."""
    mapped = []
    for w in words:
        mid = (w["start"] + w["end"]) / 2
        if map_time(mid, tmap) is None:
            continue
        s = map_time(max(w["start"], next(a for a, b, _ in tmap if a <= mid <= b)), tmap)
        e = map_time(min(w["end"], next(b for a, b, _ in tmap if a <= mid <= b)), tmap)
        if s is None or e is None:
            continue
        mapped.append({"w": w["w"], "start": s, "end": max(e, s + 0.05)})
    captions, cur = [], []

    def flush():
        if cur:
            captions.append({"start": cur[0]["start"], "duration": round(cur[-1]["end"] - cur[0]["start"], 3),
                             "text": " ".join(x["w"] for x in cur), "words": list(cur)})
            cur.clear()

    for w in mapped:
        if cur and (w["start"] - cur[-1]["end"] > 0.5):
            flush()
        cur.append(w)
        if len(cur) >= words_per_caption or re.search(r"[.!?…]$", w["w"]):
            flush()
    flush()
    return captions


def make_edit_plan(meta: dict, keep: list[dict], words: list[dict], opts: dict | None = None,
                   style_targets: dict | None = None) -> dict:
    o = {**DEFAULT_OPTS, **(opts or {})}
    tmap = timeline_map(keep)
    clips, tl = [], 0.0
    for i, k in enumerate(keep):
        d = round(k["out"] - k["in"], 3)
        clips.append({"id": f"c{i + 1}", "src": meta["path"], "source_in": k["in"], "source_out": k["out"],
                      "start": round(tl, 3), "duration": d})
        tl += d
    zooms = []
    if o["jump_cut_zoom"]:
        for i, c in enumerate(clips):
            if i % 2 == 1:
                zooms.append({"clip": c["id"], "scale": 1.08, "reason": "alternate punch-in to mask jump cut"})
    return {
        "schema": "watch.edit-plan/1",
        "units": "seconds",
        "source": meta["path"],
        "canvas": {"width": meta["width"], "height": meta["height"], "fps": meta["fps"]},
        "duration": round(tl, 3),
        "tracks": [
            {"id": "video", "type": "video", "clips": clips},
            {"id": "audio", "type": "audio", "linked_to": "video",
             "clips": [{**c, "id": c["id"].replace("c", "a", 1)} for c in clips]},
            {"id": "captions", "type": "captions",
             "clips": build_captions(words, tmap, o["caption_words"])},
        ],
        "zooms": zooms,
        "transitions": [],   # Claude fills from the reference storyboard
        "overlays": [],      # titles, lower thirds, B-roll slots
        "music": {"target_lufs": o["target_lufs"], "duck_db": None},
        "style_targets": style_targets or {},
        "notes": [],
    }


# ---------------------------------------------------------------- QA
def qa_flags(analysis: dict, ref_fp: dict | None = None, target_lufs: float | None = None) -> list[dict]:
    flags: list[dict] = []

    def add(sev, issue, fix, where=None):
        flags.append({"severity": sev, "issue": issue, "suggestion": fix,
                      "where": [round(where[0], 2), round(where[1], 2)] if where else None})

    speech = analysis.get("speech") or {}
    pacing = analysis.get("pacing") or {}
    audio = analysis.get("audio") or {}
    loud = audio.get("loudness") or {}
    has_speech = speech.get("has_speech")

    if has_speech:
        for s in (audio.get("silences") or []):
            if s["duration"] >= 1.2:
                add("medium", f"Dead air {s['duration']:.1f}s at {fmt_time(s['start'], 1)}",
                    "Trim or cover with B-roll / a zoom.", (s["start"], s["end"]))
        ttfw = speech.get("time_to_first_word")
        if ttfw is not None and ttfw > 1.5:
            add("medium", f"First word arrives at {ttfw:.1f}s", "Cut the lead-in so speech starts within ~1s.")
        if speech.get("fillers_per_minute") and speech["fillers_per_minute"] > 4:
            add("medium", f"High filler density ({speech['fillers_per_minute']}/min)",
                "Use the suggested cut list to remove um/uh.")
        wpm = speech.get("words_per_minute")
        if wpm and (wpm < 120 or wpm > 190):
            add("low", f"Speaking pace {wpm:.0f} wpm", "Very slow or very fast; consider tightening pauses or adding captions.")

    hook = pacing.get("hook") or {}
    if hook.get("first_shot_duration", 0) > 5 and hook.get("cuts_in_first_10s", 0) < 2:
        add("medium", "Slow visual hook (long opening shot, almost no cuts in 10s)",
            "Add a cut, punch-in or B-roll inside the first 5s.")
    if ref_fp:
        r_cuts = (ref_fp.get("pacing", {}).get("hook") or {}).get("cuts_in_first_10s")
        if r_cuts is not None and r_cuts - hook.get("cuts_in_first_10s", 0) >= 3:
            add("medium", f"Hook is slower than the reference ({hook.get('cuts_in_first_10s', 0)} vs {r_cuts} cuts in 10s)",
                "Add visual changes in the first 10s to match the reference.")

    limit = 10.0
    if ref_fp and ref_fp.get("pacing", {}).get("p90_shot_length"):
        limit = max(4.0, ref_fp["pacing"]["p90_shot_length"] * 1.5)
    longs = sorted((s for s in analysis.get("shots", []) if s["duration"] > limit),
                   key=lambda s: -s["duration"])[:5]
    for s in longs:
        add("low", f"Long unbroken shot {s['duration']:.1f}s at {fmt_time(s['start'], 1)}",
            "Add a punch-in, cutaway or on-screen text to refresh attention.", (s["start"], s["end"]))

    target = target_lufs if target_lufs is not None else (
        (ref_fp or {}).get("audio", {}).get("integrated_lufs") or DEFAULT_OPTS["target_lufs"])
    i_lufs = loud.get("integrated_lufs")
    if i_lufs is not None and abs(i_lufs - target) > 2.0:
        add("medium", f"Loudness {i_lufs} LUFS (target about {target})",
            f"Normalise with ffmpeg loudnorm I={target:g}:TP=-1.5:LRA=11.")
    tp = loud.get("true_peak_dbtp")
    if tp is not None and tp > -1.0:
        add("high", f"True peak {tp} dBTP: clipping risk", "Lower gain or add a limiter before export.")

    mid_black = [b for b in analysis.get("black", [])
                 if b["start"] > 0.3 and b["end"] < (analysis["meta"]["duration"] - 0.3)]
    for b in mid_black[:5]:
        add("low", f"Black frames {b['duration']:.1f}s at {fmt_time(b['start'], 1)}",
            "Intentional? If not, trim the gap.", (b["start"], b["end"]))
    return flags


# ---------------------------------------------------------------- preview render
def render_preview(src: str, keep: list[dict], out_path: Path, has_audio: bool, height: int = 720) -> Path:
    n = len(keep)
    lines = []
    for i, k in enumerate(keep):
        lines.append(f"[0:v]trim=start={k['in']}:end={k['out']},setpts=PTS-STARTPTS[v{i}];")
        if has_audio:
            lines.append(f"[0:a]atrim=start={k['in']}:end={k['out']},asetpts=PTS-STARTPTS[a{i}];")
    pairs = "".join(f"[v{i}][a{i}]" if has_audio else f"[v{i}]" for i in range(n))
    lines.append(f"{pairs}concat=n={n}:v=1:a={1 if has_audio else 0}[vc]" + ("[ac];" if has_audio else ";"))
    lines.append(f"[vc]scale=-2:{height},format=yuv420p[v]")
    filter_str = "\n".join(lines)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(Path(src).resolve()),
           "-filter_complex", filter_str, "-map", "[v]"]
    if has_audio:
        cmd += ["-map", "[ac]", "-c:a", "aac", "-b:a", "128k"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "24", str(out_path)]
    log(f"rendering preview of {n} clip(s)…")
    run(cmd)
    return out_path
