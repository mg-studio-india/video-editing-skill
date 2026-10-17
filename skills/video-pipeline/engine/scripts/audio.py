"""Audio analysis using ffmpeg filters only (no extra dependencies)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from runtime import run


def _input_range(start: float | None, end: float | None) -> list[str]:
    args: list[str] = []
    if start:
        args += ["-ss", f"{start:.3f}"]
    if start is not None and end is not None:
        args += ["-t", f"{max(0.0, end - start):.3f}"]
    elif end is not None:
        args += ["-t", f"{end:.3f}"]
    return args


def loudness(video: str, start: float | None = None, end: float | None = None) -> dict:
    """Integrated loudness (LUFS), loudness range (LU) and true peak (dBTP)."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-loglevel", "info",
           *_input_range(start, end), "-i", str(Path(video).resolve()),
           "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"]
    proc = run(cmd)
    text = proc.stderr
    # The summary block is printed once at the end; take the last occurrence.
    summary = text[text.rfind("Summary:"):] if "Summary:" in text else text

    def grab(pattern: str) -> float | None:
        m = re.search(pattern, summary)
        if not m:
            return None
        val = float(m.group(1))
        return None if val < -70 and "LUFS" in pattern else round(val, 1)

    return {
        "integrated_lufs": grab(r"\bI:\s+(-?[\d.]+)\s+LUFS"),
        "loudness_range_lu": grab(r"\bLRA:\s+(-?[\d.]+)\s+LU"),
        "true_peak_dbtp": grab(r"Peak:\s+(-?[\d.]+)\s+dBFS"),
    }


def silences(video: str, start: float | None = None, end: float | None = None,
             noise_db: float = -35.0, min_duration: float = 0.4,
             total_duration: float | None = None) -> list[dict]:
    """Stretches quieter than noise_db for at least min_duration seconds."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-loglevel", "info",
           *_input_range(start, end), "-i", str(Path(video).resolve()),
           "-vn", "-af", f"silencedetect=noise={noise_db}dB:d={min_duration}", "-f", "null", "-"]
    proc = run(cmd)
    offset = start or 0.0
    starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", proc.stderr)]
    ends = [(float(a), float(b)) for a, b in
            re.findall(r"silence_end:\s*(-?[\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)", proc.stderr)]
    out = []
    for i, s in enumerate(starts):
        s = max(0.0, s)
        if i < len(ends):
            e = ends[i][0]
        elif total_duration is not None:
            e = total_duration - offset  # silence runs to the end of the clip
        else:
            continue
        end_abs = e + offset
        if total_duration is not None:  # AAC padding can overshoot the real end
            end_abs = min(end_abs, total_duration)
        start_abs = s + offset
        out.append({"start": round(start_abs, 3), "end": round(end_abs, 3),
                    "duration": round(max(0.0, end_abs - start_abs), 3)})
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: audio.py <video>", file=sys.stderr)
        raise SystemExit(2)
    print(loudness(sys.argv[1]))
    print(silences(sys.argv[1]))
