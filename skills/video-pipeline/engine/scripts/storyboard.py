"""Storyboard skeleton.

Everything measurable is filled in by code (timecodes, durations, transitions,
spoken words, pacing, audio). Everything that needs eyes (framing, movement,
on-screen text, purpose, hook pattern, takeaways) is left as the marker
`⟨fill⟩` for Claude. `lint` fails while any marker remains, so a half-filled
storyboard never gets treated as finished.
"""
from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

from frames import cell_ref
from runtime import fmt_time

FILL = "⟨fill⟩"
MAX_SPOKEN = 110


def _esc(text: str) -> str:
    return (text or "").replace("|", "/").replace("\n", " ").strip()


def _clip(text: str, n: int = MAX_SPOKEN) -> str:
    text = _esc(text)
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def render(analysis: dict, transcript: dict | None, intent: str | None,
           sheets: list[dict] | None, hook_sheets: list[dict] | None) -> str:
    meta, pacing = analysis["meta"], analysis.get("pacing", {})
    speech = analysis.get("speech") or {}
    audio = analysis.get("audio") or {}
    loud = audio.get("loudness") or {}
    shots = analysis.get("shots", [])
    rng = analysis.get("range", {})
    title = meta.get("title") or meta.get("filename")
    engine = (f"{transcript['engine']} {transcript['model']}" if transcript else "none")

    out: list[str] = []
    out += ["---",
            f"source: {meta.get('filename')}",
            f"analyzed: {_dt.datetime.now().isoformat(timespec='seconds')}",
            f"range: {fmt_time(rng.get('start', 0))}-{fmt_time(rng.get('end', meta['duration']))}",
            f"video: {meta['width']}x{meta['height']} {meta['orientation']} @ {meta['fps']} fps",
            f"transcript: {engine}",
            "---", "", f"# Storyboard: {_esc(title)}", ""]

    out += ["## Intent lens", intent or "General: how is this video built, and what can I reuse in my own edits?", ""]
    out += ["## One-paragraph read", f"{FILL} (what the video is, who for, and the single trick that makes it work)", ""]
    out += ["## Beat sheet", f"{FILL} Replace this line with 4-8 beats (hook, setup, ..., payoff, CTA), each with a "
            "timecode range, what happens, and why it works.", ""]

    # --- measured pacing
    out += ["## Measured pacing (automatic)"]
    if pacing.get("shot_count"):
        out += [
            f"- {pacing['shot_count']} shots, {pacing['cuts_per_minute']} cuts/min, "
            f"median shot {pacing['median_shot_length']}s ({pacing['pace']}), "
            f"p10-p90 {pacing['p10_shot_length']}-{pacing['p90_shot_length']}s",
            f"- soft transitions (dissolve/wipe/fast motion): {int(pacing['soft_transition_share'] * 100)}% of cuts",
            f"- longest shot #{pacing['longest_shot']['id']} ({pacing['longest_shot']['duration']}s), "
            f"shortest #{pacing['shortest_shot']['id']} ({pacing['shortest_shot']['duration']}s)",
        ]
        curve = " · ".join(f"{fmt_time(c['start'])} {c['cuts_per_minute']}" for c in pacing.get("curve", []))
        out += [f"- pacing curve (cuts/min per {pacing['curve_window_seconds']}s window): {curve}", ""]

    # --- audio / speech
    out += ["## Audio and speech (automatic)"]
    if loud.get("integrated_lufs") is not None:
        out += [f"- loudness {loud['integrated_lufs']} LUFS (range {loud.get('loudness_range_lu')} LU, "
                f"true peak {loud.get('true_peak_dbtp')} dBTP); silence "
                f"{int((audio.get('silence_ratio') or 0) * 100)}% of runtime"]
    if speech.get("has_speech"):
        out += [f"- speech: {speech.get('words_per_minute')} wpm, first word at {speech['time_to_first_word']}s, "
                f"{speech['pauses_per_minute']} pauses/min (longest {speech['longest_pause']}s), "
                f"{speech['fillers_per_minute']} fillers/min"]
        ca = analysis.get("cut_alignment") or {}
        if ca.get("total"):
            c = ca["counts"]
            out += [f"- cut vs speech (heuristic): {c['on_pause']} on pauses, {c['j_lead']} J-lead, "
                    f"{c['l_trail']} L-trail, {c['mid_speech']} mid-sentence"]
    else:
        out += ["- no speech detected" if transcript else "- speech not analysed (no transcript)"]
    if transcript and transcript.get("sound_cues"):
        cues = ", ".join(f"{_esc(c['text'])}@{fmt_time(c['start'])}" for c in transcript["sound_cues"][:12])
        out += [f"- sound cues heard: {cues}"]
    out += [""]

    # --- hook
    hook_end = min(rng.get("end", meta["duration"]), rng.get("start", 0) + 10)
    out += [f"## Hook ({fmt_time(rng.get('start', 0))}-{fmt_time(hook_end)})"]
    if transcript:
        opening = " ".join(w["w"] for w in transcript["words"] if w["start"] < hook_end)
        out += [f"- words spoken: {_esc(opening) or '(none)'}"]
    h = pacing.get("hook") or {}
    if h:
        out += [f"- first shot {h['first_shot_duration']}s; cuts in first 3s: {h['cuts_in_first_3s']}, "
                f"in first 10s: {h['cuts_in_first_10s']}"]
    out += [f"- hook pattern and why it holds attention: {FILL}", ""]

    # --- shot list
    out += ["## Shot list",
            "Frame = contact-sheet cell (S2·5 = sheet 2, cell 5; labels on the sheet show #shot and time). "
            "Replace the six marked cells per row with short tags (see references/storyboard-schema.md). "
            "You may merge a run of near-identical shots into one row (e.g. `#14-19`).", "",
            "| # | Time | Dur | In | Frame | Spoken | Framing | Move | On-screen text | Audio | Purpose |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in shots:
        trans = s["transition_in"] + (f"·{s['cut_audio']}" if s.get("cut_audio") else "")
        out.append(
            f"| {s['id']} | {fmt_time(s['start'], 1)} | {s['duration']:.1f}s | {trans} | "
            f"{cell_ref(sheets, 'S', s['id'], s)} | {_clip(s.get('text', ''))} | "
            f"{FILL} | {FILL} | {FILL} | {FILL} | {FILL} |")
    out += [""]

    out += ["## Editing style notes", f"{FILL} (cuts, zooms, transitions, captions, text, music, colour: what the editor does)", "",
            "## Reusable takeaways for my edits",
            f"{FILL} 5-8 concrete, numeric rules I can apply (e.g. 'new visual every ~1.8s', 'first word by 0.4s').", ""]

    # --- transcript
    out += ["## Transcript"]
    if transcript and transcript["segments"]:
        for seg in transcript["segments"]:
            sid = next((s["id"] for s in shots if s["start"] <= seg["start"] < s["end"]), None)
            ref = f" #{sid}" if sid else ""
            out.append(f"- [{fmt_time(seg['start'], 1)}{ref}] {_esc(seg['text'])}")
    else:
        out.append("- (no transcript)")
    out.append("")
    return "\n".join(out)


def lint(path: Path) -> list[str]:
    """Return a list of 'line N: text' for every unfilled marker."""
    problems = []
    for i, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if FILL in line:
            n = line.count(FILL)
            squashed = re.sub(r"\s+", " ", line)[:90]
            problems.append(f"line {i}: {n} unfilled · {squashed}")
    return problems
