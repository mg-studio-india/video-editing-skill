"""Style fingerprint: a compact, reusable profile of how a video is edited."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime import read_json, write_json

QUALITATIVE_TEMPLATE = {
    "hook_type": None,            # question | contrarian claim | in-medias-res | demo-first | cold open | ...
    "hook_text": None,            # the actual opening line(s)
    "structure": None,            # list of beats with timestamps: hook, setup, payoff, CTA...
    "framing_mix": None,          # e.g. "70% close-up talking head, 20% screen capture, 10% B-roll"
    "camera_movement": None,      # static / handheld / punch-ins / pans ...
    "b_roll_ratio": None,         # share of runtime that is not the main subject (0-1, estimate)
    "on_screen_text": None,       # style, placement, frequency
    "caption_style": {"present": None, "position": None, "words_per_caption": None,
                      "emphasis": None, "font_feel": None},
    "transitions_used": None,     # hard cuts, whip, zoom, glitch, dissolve, J/L cuts...
    "zoom_punch_ins": None,       # frequency and size
    "music": {"present": None, "mood": None, "ducking_under_voice": None},
    "color_grade": None,
    "notes": None,
}


def build(analysis: dict) -> dict:
    meta = analysis["meta"]
    pacing = analysis.get("pacing", {})
    speech = analysis.get("speech") or {"has_speech": False}
    audio = analysis.get("audio") or {}
    loud = audio.get("loudness") or {}
    sil = audio.get("silences") or []
    dur = (analysis.get("range") or {}).get("duration") or meta.get("duration") or 0.0
    silence_total = sum(s["duration"] for s in sil)
    ca = analysis.get("cut_alignment") or {}
    counts = ca.get("counts") or {}
    total_cuts = ca.get("total") or 0
    freeze_total = sum(f["duration"] for f in analysis.get("freeze", []))

    fp = {
        "schema": "watch.fingerprint/1",
        "source": meta.get("filename"),
        "duration": round(dur, 2),
        "resolution": [meta.get("width"), meta.get("height")],
        "orientation": meta.get("orientation"),
        "fps": meta.get("fps"),
        "pacing": {
            "cuts_per_minute": pacing.get("cuts_per_minute"),
            "mean_shot_length": pacing.get("mean_shot_length"),
            "median_shot_length": pacing.get("median_shot_length"),
            "p10_shot_length": pacing.get("p10_shot_length"),
            "p90_shot_length": pacing.get("p90_shot_length"),
            "pace": pacing.get("pace"),
            "soft_transition_share": pacing.get("soft_transition_share"),
            "hook": pacing.get("hook"),
            "curve_cuts_per_minute": [c["cuts_per_minute"] for c in pacing.get("curve", [])],
            "curve_window_seconds": pacing.get("curve_window_seconds"),
        },
        "speech": {k: v for k, v in speech.items()},
        "audio": {
            "integrated_lufs": loud.get("integrated_lufs"),
            "loudness_range_lu": loud.get("loudness_range_lu"),
            "true_peak_dbtp": loud.get("true_peak_dbtp"),
            "silence_count": len(sil),
            "silence_ratio": round(silence_total / dur, 3) if dur else None,
            "longest_silence": max((s["duration"] for s in sil), default=0.0),
        },
        "cut_alignment": {
            "counts": counts,
            "j_or_l_share": round((counts.get("j_lead", 0) + counts.get("l_trail", 0)) / total_cuts, 2)
            if total_cuts else None,
            "on_pause_share": round(counts.get("on_pause", 0) / total_cuts, 2) if total_cuts else None,
        },
        "visual": {
            "black_frame_runs": len(analysis.get("black", [])),
            "static_share": round(min(1.0, freeze_total / dur), 3) if dur else None,
        },
        "qualitative": json.loads(json.dumps(QUALITATIVE_TEMPLATE)),
    }
    return fp


# ---------------------------------------------------------------- comparison
def _get(d: dict, path: str):
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


# (label, path, kind, tolerance, unit)   kind: rel = relative tolerance, abs = absolute
METRICS = [
    ("Cuts per minute", "pacing.cuts_per_minute", "rel", 0.25, ""),
    ("Median shot length", "pacing.median_shot_length", "rel", 0.25, "s"),
    ("Longest typical shot (p90)", "pacing.p90_shot_length", "rel", 0.30, "s"),
    ("Cuts in first 10s", "pacing.hook.cuts_in_first_10s", "abs", 1.5, ""),
    ("First shot length", "pacing.hook.first_shot_duration", "abs", 1.0, "s"),
    ("Time to first word", "speech.time_to_first_word", "abs", 0.5, "s"),
    ("Words per minute", "speech.words_per_minute", "rel", 0.15, ""),
    ("Pauses per minute", "speech.pauses_per_minute", "abs", 3.0, ""),
    ("Longest pause", "speech.longest_pause", "abs", 0.6, "s"),
    ("Fillers per minute", "speech.fillers_per_minute", "abs", 1.0, ""),
    ("Integrated loudness", "audio.integrated_lufs", "abs", 1.5, " LUFS"),
    ("Silence share of runtime", "audio.silence_ratio", "abs", 0.05, ""),
    ("Cuts with J/L audio overlap", "cut_alignment.j_or_l_share", "abs", 0.10, ""),
]


def compare(ref: dict, mine: dict) -> list[dict]:
    rows = []
    for label, path, kind, tol, unit in METRICS:
        r, m = _get(ref, path), _get(mine, path)
        if r is None or m is None:
            rows.append({"metric": label, "reference": r, "mine": m, "delta": None,
                         "verdict": "n/a", "note": "not measurable in one of the videos"})
            continue
        delta = m - r
        if kind == "rel":
            off = abs(delta) / abs(r) if r else (0 if delta == 0 else 1)
            how = f"{delta / r * 100:+.0f}%" if r else f"{delta:+.2f}"
        else:
            off = abs(delta)
            how = f"{delta:+.2f}{unit}"
        verdict = "similar" if off <= tol else ("higher" if delta > 0 else "lower")
        rows.append({"metric": label, "reference": r, "mine": m, "delta": round(delta, 3),
                     "verdict": verdict, "note": f"{how} vs reference"})
    return rows


def compare_markdown(rows: list[dict]) -> str:
    lines = ["| Metric | Reference | Mine | Difference | Verdict |", "|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['metric']} | {r['reference']} | {r['mine']} | {r['note']} | {r['verdict']} |")
    return "\n".join(lines)


def count_unfilled(fp: dict) -> int:
    def walk(node) -> int:
        if isinstance(node, dict):
            return sum(walk(v) for v in node.values())
        return 1 if node is None else 0
    return walk(fp.get("qualitative", {}))


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("build", "compare"):
        print("usage: fingerprint.py build <analysis.json> [out.json]\n"
              "       fingerprint.py compare <reference-fp.json> <mine-fp.json>", file=sys.stderr)
        raise SystemExit(2)
    if sys.argv[1] == "build":
        fp = build(read_json(Path(sys.argv[2])))
        out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("fingerprint.json")
        write_json(out, fp)
        print(out.resolve())
    else:
        print(compare_markdown(compare(read_json(Path(sys.argv[2])), read_json(Path(sys.argv[3])))))
