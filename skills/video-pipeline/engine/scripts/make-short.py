#!/usr/bin/env python3
"""make-short.py: cut one Short out of the flat cut, every edge snapped to a word boundary.

A Short can be one stretch or several stitched together (a hook line from later, then the explanation). Ranges are
flat-cut seconds ("A-B") or phrases ("@first words..@last words"). Each start moves to the first word starting at or
after it, minus a 0.08 s lead-in (never into the previous word); each end to the last word ending at or before it,
plus a 0.15 s tail (never into the next word). Then apply-cut.py makes the file, so the Short gets the same
frame-accurate encode and its own cut-map.json.

Usage:
  python3 make-short.py --flat W/public/input-video.mp4 --transcript W/transcript.json --out-dir W/shorts/01 \
      --range 412.3-438.9 [--range "@the real reason..@nobody tells you"] [--max 60]
Writes: <out-dir>/cut-list.json, <out-dir>/cut-map.json, <out-dir>/public/input-video.mp4, <out-dir>/short.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runtime
runtime.ensure_project_venv()

LEAD, TAIL = 0.08, 0.15



def _words_mod():
    spec = importlib.util.spec_from_file_location("resolve_anchors", os.path.join(HERE, "resolve-anchors.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def parse_range(spec: str, W) -> tuple[float, float]:
    if spec.startswith("@"):
        a, _, b = spec[1:].partition("..")
        b = b[1:] if b.startswith("@") else b
        ha = W.find(a)
        if ha is None:
            raise SystemExit(f"phrase not found: {a!r}")
        hb = W.find(b, ha[0])
        if hb is None:
            raise SystemExit(f"phrase not found after {ha[0]:.2f}: {b!r}")
        return ha[0], hb[1]
    a, b = spec.split("-")
    return float(a), float(b)


def snap(a: float, b: float, words: list[dict], duration: float) -> tuple[float, float]:
    """Pure function (tested). Word-boundary snap with lead-in and tail, never into a neighbouring word."""
    inside = [w for w in words if w["start"] >= a - 1e-6 and w["end"] <= b + 1e-6]
    if not inside:
        raise SystemExit(f"no whole word inside {a:.2f}-{b:.2f}")
    first, last = inside[0], inside[-1]
    prev_end = max([w["end"] for w in words if w["end"] <= first["start"] + 1e-6] or [0.0])
    next_start = min([w["start"] for w in words if w["start"] >= last["end"] - 1e-6] or [duration])
    return round(max(prev_end, first["start"] - LEAD, 0.0), 3), round(min(next_start, last["end"] + TAIL, duration), 3)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--flat", required=True)
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--range", action="append", required=True, help="A-B seconds or @phrase..@phrase; repeatable")
    ap.add_argument("--max", type=float, default=60.0, help="warn above this length (seconds)")
    a = ap.parse_args()
    t = json.load(open(a.transcript))
    words = t["words"] if isinstance(t, dict) else t
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.flat],
                               capture_output=True, text=True, check=True).stdout.strip())
    W = _words_mod().Words(words)
    kept = []
    for spec in a.range:
        s, e = snap(*parse_range(spec, W), words, dur)
        kept.append({"start": s, "end": e})
    os.makedirs(os.path.join(a.out_dir, "public"), exist_ok=True)
    total = round(sum(k["end"] - k["start"] for k in kept), 3)
    cl = os.path.join(a.out_dir, "cut-list.json")
    json.dump({"source": os.path.abspath(a.flat), "source_duration": dur, "kept_seconds": total, "kept": kept},
              open(cl, "w"), indent=1)
    r = subprocess.run([runtime.get_project_venv_python(), os.path.join(HERE, "apply-cut.py"), "--input", a.flat, "--cut-list", cl,
                        "--out", os.path.join(a.out_dir, "public", "input-video.mp4")], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        sys.exit(r.stderr.strip() or "apply-cut failed")
    text = " ".join(w.get("text") or w.get("w") for k in kept for w in words
                    if w["start"] >= k["start"] - 1e-6 and w["end"] <= k["end"] + 1e-6)
    json.dump({"ranges_flat": kept, "seconds": total, "text": text, "from": os.path.abspath(a.flat)},
              open(os.path.join(a.out_dir, "short.json"), "w"), indent=1)
    print(f"short: {total:.1f} s from {len(kept)} range(s)")
    print(f"  starts: {text[:90]!r}")
    if total > a.max:
        print(f"WARN: {total:.1f} s is over {a.max:.0f} s")
    if total < 10:
        print(f"WARN: {total:.1f} s is very short; does it still pay off?")


if __name__ == "__main__":
    main()
