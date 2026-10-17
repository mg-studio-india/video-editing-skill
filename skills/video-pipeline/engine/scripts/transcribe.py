#!/usr/bin/env python3
"""transcribe.py: word-level transcript of a clip with whisper.cpp, in the shape every engine script reads.

Replaces `npx hyperframes transcribe --engine parakeet`. Output (transcript.json):
  {"engine": "whisper.cpp", "model": ..., "language": ..., "duration": ...,
   "words": [{"text": "today", "w": "today", "start": 0.70, "end": 1.10}, ...],
   "segments": [...], "sound_cues": [...], "loops_collapsed": N, "windows": [[a, b], ...]}
Every word carries both "text" (the cut tools: paper-cut, hand-cut, edge-audit, beat-check, phrase-times, dead-air,
stutter-scan) and "w" (the watch tools), so one file serves both.

Usage:
  python3 transcribe.py MEDIA --out W/transcript.json                 # one pass
  python3 transcribe.py MEDIA --out W/transcript-raw.json --window 25 # long raw takes: windows split at silences
  python3 transcribe.py MEDIA --out W/transcript.json --no-fillers    # drop the filler-keeping prompt

Why windows: on long raw takes whisper can skip a retake that repeats the previous sentence, and it can loop on long
silences. Windows of ~25 s that start and end inside silences keep each retake in view. Windows are chosen by
ffmpeg silencedetect; a stretch with no silence is split hard at the limit.

Fillers: whisper drops "um" and "uh" by default, and the cut tools need them to find restarts. Unless --no-fillers (or
WATCH_WHISPER_PROMPT is set), the prompt "Um, uh, you know, I mean, like." is passed, which keeps them.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
from runtime import run  # noqa: E402
from transcribe_cpp import collapse_loops, transcribe, words_to_segments  # noqa: E402

FILLER_PROMPT = "Um, uh, you know, I mean, like."


def media_duration(media: str) -> float:
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(media)])
    return float(p.stdout.strip())


def silences(media: str, noise_db: float = -35.0, min_len: float = 0.3) -> list[tuple[float, float]]:
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(media), "-vn",
             "-af", f"silencedetect=noise={noise_db}dB:d={min_len}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", p.stderr)]
    return [(s, e) for s, e in zip(starts, ends) if e > s]


def plan_windows(duration: float, quiet: list[tuple[float, float]], limit: float) -> list[tuple[float, float]]:
    """Split [0, duration] into windows no longer than `limit`, each boundary at the middle of a silence when one
    falls in the back half of the window; otherwise a hard split at the limit. Pure function (tested)."""
    mids = sorted((s + e) / 2 for s, e in quiet)
    out, a = [], 0.0
    while duration - a > limit:
        lo, hi = a + limit * 0.5, a + limit
        inside = [m for m in mids if lo <= m <= hi]
        b = inside[-1] if inside else hi
        out.append((round(a, 3), round(b, 3)))
        a = b
    out.append((round(a, 3), round(duration, 3)))
    return out


def merge(parts: list[dict]) -> tuple[list[dict], list[dict], str | None]:
    words, cues, lang = [], [], None
    for p in parts:
        lang = lang or p.get("language")
        last = words[-1]["end"] if words else -1.0
        words += [w for w in p["words"] if w["start"] >= last - 0.01]   # never overlap at a window seam
        cues += p.get("sound_cues", [])
    return words, cues, lang


def to_engine_shape(words: list[dict]) -> list[dict]:
    return [{"text": w["w"], "w": w["w"], "start": w["start"], "end": w["end"]} for w in words]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("media")
    ap.add_argument("--out", required=True, help="transcript.json to write")
    ap.add_argument("--window", type=float, default=0.0, help="window length in seconds (0 = one pass)")
    ap.add_argument("--lang", help="force a language code (en, hi, ...); default from config or auto")
    ap.add_argument("--prompt", help="initial prompt: names, jargon (fillers prompt is added unless --no-fillers)")
    ap.add_argument("--no-fillers", action="store_true", help="do not ask whisper to keep um/uh")
    ap.add_argument("--fix", help="corrections.json to apply (default: corrections.json next to --out, when present)")
    a = ap.parse_args()

    cfg = config.load()
    import importlib.util
    _spec = importlib.util.spec_from_file_location("fix_words", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fix-words.py"))
    FW = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(FW)
    fix_path = a.fix or os.path.join(os.path.dirname(os.path.abspath(a.out)), "corrections.json")
    corrections = FW.load_corrections(fix_path)
    if a.lang:
        cfg["WATCH_WHISPER_LANG"] = a.lang
    prompt = a.prompt or cfg.get("WATCH_WHISPER_PROMPT") or ""
    names = [v for v in dict.fromkeys(corrections.values()) if v.lower() not in prompt.lower()][:20]
    if names:                                  # the correct spellings as hints, so whisper gets them right more often
        prompt = (prompt + " " + ", ".join(names) + ".").strip()
    if not a.no_fillers and FILLER_PROMPT.lower() not in prompt.lower():
        prompt = (FILLER_PROMPT + " " + prompt).strip()
    cfg["WATCH_WHISPER_PROMPT"] = prompt

    dur = media_duration(a.media)
    wins = plan_windows(dur, silences(a.media), a.window) if a.window > 0 else [(0.0, dur)]
    work = Path(tempfile.mkdtemp(prefix="transcribe-"))
    parts = []
    for i, (s, e) in enumerate(wins):
        if len(wins) > 1:
            print(f"window {i + 1}/{len(wins)}  {s:.2f}-{e:.2f}", file=sys.stderr)
        parts.append(transcribe(a.media, work, s if len(wins) > 1 else None, e if len(wins) > 1 else None, cfg))
    words, cues, lang = merge(parts)
    words, removed = collapse_loops(words)
    shaped, changes = FW.apply(to_engine_shape(words), corrections) if corrections else (to_engine_shape(words), [])
    out = {"engine": "whisper.cpp", "model": parts[0].get("model"), "language": lang, "duration": round(dur, 3),
           "words": shaped, "corrections_applied": len(changes), "segments": words_to_segments(words), "sound_cues": cues,
           "loops_collapsed": removed + sum(p.get("loops_collapsed", 0) for p in parts),
           "windows": [list(w) for w in wins]}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(f"{a.out}: {len(shaped)} words, language={lang}, windows={len(wins)}, loops_collapsed={out['loops_collapsed']}"
          + (f", {len(changes)} corrections from {os.path.basename(fix_path)}" if corrections else ""))
    for w in shaped[:8]:
        print(f"  {w['start']:8.2f}  {w['w']}")


if __name__ == "__main__":
    main()
