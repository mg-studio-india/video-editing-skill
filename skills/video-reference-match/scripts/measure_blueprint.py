#!/usr/bin/env python3
"""measure_blueprint.py <video> --watch <dir> [--out measured.json]: the "measured" block of a new blueprint."""
import json
import os
import subprocess
import sys

import numpy as np


def frames(video, n=24, w=180):
    d = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height",
                                   "-select_streams", "v:0", "-of", "json", video], capture_output=True, text=True).stdout)
    dur = float(d["format"]["duration"]); W, H = d["streams"][0]["width"], d["streams"][0]["height"]
    h = int(round(H * w / W / 2)) * 2
    out = []
    for t in np.linspace(0.04 * dur, 0.96 * dur, n):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % t, "-i", video, "-frames:v", "1", "-vf",
                              "scale=%d:%d" % (w, h), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        if len(raw) == w * h * 3:
            out.append(np.frombuffer(raw, np.uint8).reshape(h, w, 3).astype(float))
    return out, dur


def grade(fr):
    a = np.stack([f for f in fr if f.mean() > 12])           # skip black frames
    luma = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    rg, yb = a[..., 0] - a[..., 1], 0.5 * (a[..., 0] + a[..., 1]) - a[..., 2]
    colorful = np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2)
    mid = (luma > 50) & (luma < 205)
    warm = float((a[..., 0] - a[..., 2])[mid].mean())
    tint = float((a[..., 1] - 0.5 * (a[..., 0] + a[..., 2]))[mid].mean())
    H, W = luma.shape[1:]
    c = luma[:, H // 4:3 * H // 4, W // 4:3 * W // 4].mean()
    ring = np.concatenate([luma[:, :H // 10].ravel(), luma[:, -H // 10:].ravel(), luma[:, :, :W // 10].ravel(), luma[:, :, -W // 10:].ravel()]).mean()
    px = a.reshape(-1, 3)[::7]
    k = 6
    cent = px[np.linspace(0, len(px) - 1, k).astype(int)]
    for _ in range(15):
        lab = ((px[:, None] - cent[None]) ** 2).sum(-1).argmin(1)
        cent = np.array([px[lab == j].mean(0) if (lab == j).any() else cent[j] for j in range(k)])
    share = np.bincount(lab, minlength=k) / len(px)
    pal = [{"hex": "#%02X%02X%02X" % tuple(int(v) for v in cent[j]), "share": round(float(share[j]), 3)} for j in np.argsort(-share)]
    return {"black_point": round(float(np.percentile(luma, 2)), 1), "midtone": round(float(np.percentile(luma, 50)), 1),
            "white_point": round(float(np.percentile(luma, 98)), 1), "contrast_range": round(float(np.percentile(luma, 98) - np.percentile(luma, 2)), 1),
            "luma_std": round(float(luma.std()), 1), "saturation": round(float(sat.mean()), 3), "colorfulness": round(float(colorful), 1),
            "warmth_r_minus_b": round(warm, 1), "tint_g": round(tint, 1), "vignette_centre_over_edge": round(float(c / max(ring, 1)), 2),
            "palette": pal,
            "label": label_grade(np.percentile(luma, 98) - np.percentile(luma, 2), sat.mean(), warm)}


def label_grade(contrast, sat, warm):
    c = "high-contrast" if contrast > 215 else ("low-contrast" if contrast < 170 else "mid-contrast")
    s = "saturated" if sat > 0.42 else ("muted" if sat < 0.25 else "natural-saturation")
    t = "warm" if warm > 18 else ("cool" if warm < 0 else "neutral-warm")
    return "%s, %s, %s" % (c, s, t)


def layout(fr):
    lb, split = 0, 0
    for f in fr:
        luma = f.mean(-1)
        rows = luma.mean(1)
        top = np.argmax(rows > 14) if (rows > 14).any() else 0
        bot = np.argmax(rows[::-1] > 14) if (rows > 14).any() else 0
        if (top + bot) / len(rows) > 0.08:
            lb += 1
        g = np.abs(np.diff(luma, axis=0))
        band = g[int(0.25 * len(g)):int(0.75 * len(g))]
        full = (band > 25).mean(1)                            # share of the width that changes sharply on this row
        if full.max() > 0.85:
            split += 1
    n = max(1, len(fr))
    return {"letterbox_share": round(lb / n, 2), "split_divider_share": round(split / n, 2)}


def sound(video, idx_dir):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(float)
    if len(x) < 16000:
        return {"has_audio": False}
    hop = 160
    n = len(x) // hop
    fr = x[:n * hop].reshape(n, hop)
    lvl = 10 * np.log10((fr ** 2).mean(1) + 1e-10)
    # onset envelope: positive spectral flux on 512-pt frames
    win = 512
    m = (len(x) - win) // hop
    idx = np.arange(win)[None] + hop * np.arange(m)[:, None]
    S = np.abs(np.fft.rfft(x[idx] * np.hanning(win), axis=1))
    flux = np.maximum(np.diff(np.log1p(S), axis=0), 0).sum(1)
    flux = (flux - flux.mean()) / (flux.std() + 1e-9)
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
    ac /= ac[0]
    lo, hi = int(0.333 * 100), int(1.0 * 100)               # 60-180 BPM
    k = lo + int(np.argmax(ac[lo:hi]))
    beat = float(ac[k])
    # speech gaps from the transcript
    tr = os.path.join(idx_dir, "full", "transcript.json")
    words = json.load(open(tr)).get("words", []) if os.path.isfile(tr) else []
    speech = np.zeros(n, bool)
    for w in words:
        speech[int(w["start"] * 100):int(w["end"] * 100) + 1] = True
    sp_lvl = np.median(lvl[speech]) if speech.any() else np.median(lvl)
    gaps = lvl[~speech]
    gap_rel = float(np.median(gaps) - sp_lvl) if len(gaps) > 50 else None
    speech_cov = float(speech.mean())
    if speech_cov < 0.15:
        likely = "music-only" if np.median(lvl) > -40 else "silent / ambience"
    elif beat > 0.30 or (gap_rel is not None and gap_rel > -16):
        likely = "music bed likely"
    elif beat > 0.18 or (gap_rel is not None and gap_rel > -24):
        likely = "possible music bed"
    else:
        likely = "voice only (no bed detected)"
    # transients on hard cuts
    an = json.load(open(os.path.join(idx_dir, "full", "analysis.json")))
    cuts = [s["start"] for s in an["shots"] if s.get("transition_in") == "cut"]
    hits = 0
    for c in cuts:
        i = int(c * 100)
        if 8 < i < len(flux) - 8:
            local = flux[i - 30:i + 30]
            if flux[i - 3:i + 4].max() > max(2.5, np.percentile(local, 90)):
                hits += 1
    return {"has_audio": True, "speech_coverage": round(speech_cov, 2), "beat_periodicity": round(beat, 2),
            "beat_bpm_est": round(6000 / k) if beat > 0.18 else None,
            "gap_level_rel_speech_db": round(gap_rel, 1) if gap_rel is not None else None,
            "music": likely, "hard_cuts": len(cuts), "cut_hit_share": round(hits / len(cuts), 2) if cuts else None,
            "method": "heuristic (onset-envelope beat periodicity + level in speech gaps); not a classifier"}


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video"); ap.add_argument("--watch", required=True); ap.add_argument("--out")
    a = ap.parse_args()
    fr, dur = frames(a.video)
    out = {"grade": grade(fr), "layout": layout(fr), "sound": sound(a.video, a.watch)}
    out["grade"].pop("palette", None)
    out["sound"].pop("hard_cuts", None)
    txt = json.dumps(out, indent=1)
    if a.out:
        open(a.out, "w").write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
