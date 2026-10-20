#!/usr/bin/env python3
"""palette.py: the dominant colours in a region of one or more frames, measured, not guessed."""
from __future__ import annotations

import argparse
import colorsys
import json
import sys

import numpy as np


def load(paths: list[str], box: tuple[float, float, float, float] | None, per_image: int = 20000) -> np.ndarray:
    from PIL import Image
    rng = np.random.default_rng(0)
    out = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        if box:
            w, h = im.size
            im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
        a = np.asarray(im).reshape(-1, 3).astype(np.float64)
        if len(a) > per_image:
            a = a[rng.choice(len(a), per_image, replace=False)]
        out.append(a)
    return np.concatenate(out)


def kmeans(px: np.ndarray, k: int, iters: int = 25) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(1)
    k = max(1, min(k, len(px)))
    c = px[rng.choice(len(px), k, replace=False)]
    for _ in range(iters):
        lab = np.argmin(((px[:, None, :] - c[None, :, :]) ** 2).sum(-1), axis=1)
        new = np.array([px[lab == i].mean(0) if np.any(lab == i) else c[i] for i in range(k)])
        if np.allclose(new, c):
            break
        c = new
    share = np.bincount(lab, minlength=k) / len(px)
    order = np.argsort(-share)
    return c[order], share[order]


def describe(rgb) -> dict:
    r, g, b = [int(round(x)) for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    if l < 0.12:
        kind = "near-black"
    elif l > 0.88 and (s <= 0.35 or l > 0.94):
        kind = "near-white"
    elif s < 0.15:
        kind = "grey"
    else:
        names = ["red", "orange", "yellow", "lime", "green", "teal", "cyan", "blue", "indigo", "violet", "magenta", "pink"]
        kind = names[int(((h * 360 + 15) % 360) // 30)]
    return {"hex": "#%02X%02X%02X" % (r, g, b), "kind": kind, "lightness": round(l, 2), "saturation": round(s, 2)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("frames", nargs="+")
    ap.add_argument("--box")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    box = tuple(float(x) for x in a.box.split(",")) if a.box else None
    px = load(a.frames, box)
    centres, share = kmeans(px, a.k)
    rows = [{**describe(c), "share": round(float(s), 3)} for c, s in zip(centres, share)]
    if a.json:
        print(json.dumps(rows, indent=1))
        return
    print("%d frame(s), region %s" % (len(a.frames), a.box or "whole frame"))
    for r in rows:
        print("  %s  %5.1f%%  %-10s L%.2f S%.2f" % (r["hex"], 100 * r["share"], r["kind"], r["lightness"], r["saturation"]))
    accents = [r for r in rows if r["kind"] not in ("near-black", "near-white", "grey") and r["saturation"] > 0.45]
    if accents:
        print("accent candidates: " + ", ".join(r["hex"] for r in accents))


if __name__ == "__main__":
    main()
