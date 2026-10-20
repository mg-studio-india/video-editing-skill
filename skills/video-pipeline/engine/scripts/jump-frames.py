#!/usr/bin/env python3
"""jump-frames.py: the exact frame where each jump cut happens, measured from the picture."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

import numpy as np

W, H = 160, 90
SEARCH = 4


def frame_diffs(video: str, fps: int) -> np.ndarray:
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={fps},scale={W}:{H},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    if p.returncode != 0:
        sys.exit(p.stderr.decode(errors="replace")[-400:])
    f = np.frombuffer(p.stdout, dtype=np.uint8)
    f = f[: len(f) // (W * H) * (W * H)].reshape(-1, H, W).astype(np.int16)
    d = np.zeros(len(f))
    d[1:] = np.abs(f[1:] - f[:-1]).mean(axis=(1, 2))
    return d


def locate(cuts: list[float], diffs: np.ndarray, fps: int) -> list[dict]:
    out = []
    for c in cuts:
        i = int(round(c * fps))
        lo, hi = max(1, i - SEARCH), min(len(diffs) - 1, i + SEARCH)
        if hi < lo:
            out.append({"cut": c, "frame": None, "set_at": round(c, 3), "confidence": 0.0})
            continue
        win = diffs[lo:hi + 1]
        j = lo + int(np.argmax(win))
        med = float(np.median(win)) or 1e-6
        out.append({"cut": c, "frame": j, "set_at": round(j / fps - 0.003, 3),
                    "offset_frames": j - i, "confidence": round(float(diffs[j]) / med, 1)})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--video", required=True)
    ap.add_argument("--cut-map", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()
    cuts = json.load(open(a.cut_map))["cuts"]
    res = locate(cuts, frame_diffs(a.video, a.fps), a.fps)
    json.dump({"fps": a.fps, "jumps": res}, open(a.out, "w"), indent=1)
    weak = [r for r in res if r["confidence"] < 2.0]
    moved = [r for r in res if r.get("offset_frames")]
    print(f"{len(res)} cuts measured, {len(moved)} off their listed frame, {len(weak)} weak (same framing both sides)")
    for r in res:
        flag = "  weak: check the frames" if r["confidence"] < 2.0 else ""
        print(f"  cut {r['cut']:8.3f} -> set at {r['set_at']:8.3f}  ({r.get('offset_frames', 0):+d} f, x{r['confidence']}){flag}")


if __name__ == "__main__":
    main()
