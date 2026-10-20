"""Shot detection with ffmpeg."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from runtime import fmt_time, run

HARD_CUT_SCORE = 0.40   # scene score >= this reads as a hard cut; below as soft (dissolve/wipe/fast motion)
MIN_SHOT = 0.20         # ignore "cuts" closer together than this (flashes, strobes)
ANALYSIS_WIDTH = 320    # analyse a downscaled copy: faster, same cut timing


def _input_range(start: float | None, end: float | None) -> list[str]:
    args: list[str] = []
    if start:
        args += ["-ss", f"{start:.3f}"]
    if start is not None and end is not None:
        args += ["-t", f"{max(0.0, end - start):.3f}"]
    elif end is not None:
        args += ["-t", f"{end:.3f}"]
    return args


def detect_cuts(video: str, start: float | None = None, end: float | None = None,
                threshold: float = 0.20, width: int = ANALYSIS_WIDTH) -> list[dict]:
    vf = f"scale={width}:-2,select='gt(scene,{threshold})',metadata=mode=print:file=-"
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostats",
           *_input_range(start, end), "-i", str(Path(video).resolve()),
           "-an", "-vf", vf, "-f", "null", "-"]
    proc = run(cmd)
    offset = start or 0.0
    cuts: list[dict] = []
    t: float | None = None
    for line in proc.stdout.splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m:
            t = float(m.group(1))
            continue
        m = re.search(r"lavfi\.scene_score=([\d.]+)", line)
        if m and t is not None:
            cuts.append({"t": round(t + offset, 3), "score": round(float(m.group(1)), 3)})
            t = None
    return cuts


def build_shots(cuts: list[dict], t0: float, t1: float, min_shot: float = MIN_SHOT) -> list[dict]:
    if t1 <= t0:
        return []
    bounds: list[tuple[float, float | None]] = [(t0, None)]
    last = t0
    for c in sorted(cuts, key=lambda c: c["t"]):
        if c["t"] - last < min_shot or t1 - c["t"] < min_shot:
            continue
        bounds.append((c["t"], c["score"]))
        last = c["t"]
    shots = []
    for i, (start, score) in enumerate(bounds):
        end = bounds[i + 1][0] if i + 1 < len(bounds) else t1
        if i == 0:
            transition = "start"
        else:
            transition = "cut" if (score or 0) >= HARD_CUT_SCORE else "soft"
        shots.append({
            "id": i + 1,
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": round(end - start, 3),
            "transition_in": transition,
            "cut_score": score,
        })
    return shots


def detect_black_freeze(video: str, start: float | None = None, end: float | None = None,
                        width: int = ANALYSIS_WIDTH, black_min: float = 0.1,
                        freeze_min: float = 1.0) -> dict:
    vf = (f"scale={width}:-2,blackdetect=d={black_min}:pix_th=0.10,"
          f"freezedetect=n=-60dB:d={freeze_min}")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "info", "-nostats",
           *_input_range(start, end), "-i", str(Path(video).resolve()),
           "-an", "-vf", vf, "-f", "null", "-"]
    proc = run(cmd)
    offset = start or 0.0
    black = []
    for m in re.finditer(r"black_start:([\d.]+)\s+black_end:([\d.]+)\s+black_duration:([\d.]+)", proc.stderr):
        s, e, d = (float(x) for x in m.groups())
        black.append({"start": round(s + offset, 3), "end": round(e + offset, 3), "duration": round(d, 3)})

    starts = [float(x) for x in re.findall(r"freeze_start:\s*([\d.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"freeze_end:\s*([\d.]+)", proc.stderr)]
    freeze = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else None
        freeze.append({"start": round(s + offset, 3), "end": None if e is None else round(e + offset, 3)})
    return {"black": black, "freeze": freeze}


def close_open_freezes(freeze: list[dict], t1: float) -> list[dict]:
    out = []
    for f in freeze:
        end = t1 if f["end"] is None else f["end"]
        out.append({"start": f["start"], "end": round(end, 3), "duration": round(max(0.0, end - f["start"]), 3)})
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: shots.py <video> [threshold]", file=sys.stderr)
        raise SystemExit(2)
    from probe import probe
    meta = probe(sys.argv[1])
    thr = float(sys.argv[2]) if len(sys.argv) > 2 else 0.20
    shots = build_shots(detect_cuts(sys.argv[1], threshold=thr), 0.0, meta["duration"])
    for s in shots:
        print(f"#{s['id']:>3}  {fmt_time(s['start'], 1)} -> {fmt_time(s['end'], 1)}  "
              f"({s['duration']:.2f}s)  {s['transition_in']}")
