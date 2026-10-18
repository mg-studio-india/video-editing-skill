#!/usr/bin/env python3
"""fit_font.py: solve the font size (px at a 1080x1920 canvas) that reproduces a reference's measured calibration word.

  fit_font.py --font "Inter 900" --word quality --ink 14.61 --width 85.4 [--canvas 1080x1920]
  fit_font.py --font "Inter 900" --word "KEY WORD" --px 292 [--tracking -0.03]   expected ink / width at a given size
  fit_font.py --spec <blueprint or caption-spec.json> [--write]   every tier with a calibration entry + closest local font

Renders the word with the local font file (Pillow/FreeType, same outlines the browser uses), measures its ink height
(% of canvas height) and ink width (% of canvas width), and returns the px that matches the height, the px that matches
the width, and the compromise that keeps both inside the VERIFY tolerances (±0.5 % H, ±2 % W) when possible.
--write stores {"verified_px", "fit": {...}} on each tier of the spec.
Notes: the local DM Sans files are the static "9 pt" optical cut (wide, loose) - poor for display-size matches, prefer
Inter; Playfair here is upright only, so italic-serif fits are approximate; scripts/handwriting have no local match.
"""
import argparse
import glob
import json
import os
import re

from PIL import Image, ImageDraw, ImageFont

FONTS = os.path.expanduser("~/.agents/skills/video-pipeline/engine/assets/fonts")
STATIC = {("poppins", 500): "poppins/Poppins-Medium.ttf", ("poppins", 600): "poppins/Poppins-Bold.ttf",
          ("poppins", 700): "poppins/Poppins-Bold.ttf", ("poppins", 800): "poppins/Poppins-ExtraBold.ttf",
          ("poppins", 900): "poppins/Poppins-Black.ttf", ("anton", 400): "anton/Anton-Regular.ttf"}
VARIABLE = {"inter": "inter/Inter-Variable.ttf", "syne": "syne/Syne-Variable.ttf",
            "playfair display": "playfair/PlayfairDisplay-Variable.ttf", "playfair": "playfair/PlayfairDisplay-Variable.ttf",
            "jetbrains mono": "jetbrains-mono/JetBrainsMono-Variable.ttf",
            "noto sans devanagari": "noto-devanagari/NotoSansDevanagari-Variable.ttf"}
DMSANS = {400: "DMSans-400.woff2", 500: "DMSans-500.woff2", 700: "DMSans-700.woff2"}


def parse(fontspec):
    m = re.match(r"\s*([A-Za-z][A-Za-z ]*?)\s+(\d{3})", fontspec or "")
    if not m:
        m2 = re.match(r"\s*([A-Za-z][A-Za-z ]*)", fontspec or "")
        return (m2.group(1).strip().lower(), 400) if m2 else (None, None)
    return m.group(1).strip().lower(), int(m.group(2))


def load(family, weight, px):
    if family == "dm sans":
        print("note: local DM Sans is the 9 pt optical cut (wide); display-size fits will look off - consider Inter")
        w = min(DMSANS, key=lambda k: abs(k - weight))
        return ImageFont.truetype(os.path.join(FONTS, DMSANS[w]), px)
    if family in VARIABLE:
        f = ImageFont.truetype(os.path.join(FONTS, VARIABLE[family]), px)
        try:
            vals = []
            for ax in f.get_variation_axes():          # browser behaviour: wght = weight, opsz = px (auto optical sizing)
                nm = (ax.get("name") or b"")
                nm = nm.decode() if isinstance(nm, bytes) else str(nm)
                lo, hi = ax["minimum"], ax["maximum"]
                if "eight" in nm:
                    vals.append(max(lo, min(hi, weight)))
                elif "ptical" in nm:
                    vals.append(max(lo, min(hi, px)))
                else:
                    vals.append(ax.get("default", lo))
            f.set_variation_by_axes(vals)
        except Exception as e:
            print("variation warning:", e)
        return f
    key = min((k for k in STATIC if k[0] == family), key=lambda k: abs(k[1] - weight), default=None)
    if key:
        return ImageFont.truetype(os.path.join(FONTS, STATIC[key]), px)
    raise SystemExit("no local font for %r (have: poppins, inter, anton, syne, dm sans, playfair, jetbrains mono, noto sans devanagari)" % family)


def measure(family, weight, px, word, upper=False, W=1080, H=1920, tracking=0.0):
    """Ink height % of H and ink width % of W; tracking (em, CSS letter-spacing) adds (chars-1) * tracking * px."""
    f = load(family, weight, px)
    t = word.upper() if upper else word
    l, top, r, b = ImageDraw.Draw(Image.new("L", (10, 10))).textbbox((0, 0), t, font=f)
    img = Image.new("L", (r - l + 40, b - top + 40), 0)
    ImageDraw.Draw(img).text((20 - l, 20 - top), t, font=f, fill=255)
    bb = img.point(lambda v: 255 if v > 128 else 0).getbbox()
    wpx = (bb[2] - bb[0]) + (len(t) - 1) * tracking * px
    return 100.0 * (bb[3] - bb[1]) / H, 100.0 * wpx / W


def em(v):
    m = re.search(r"(-?\d*\.?\d+)\s*em", str(v or ""))
    return float(m.group(1)) if m else 0.0


def fit(fontspec, word, ink, width, upper=False, W=1080, H=1920, tracking=0.0):
    fam, wt = parse(fontspec)
    h100, w100 = measure(fam, wt, 100, word, upper, W, H, tracking)
    px_h = 100 * ink / h100 if ink else None
    px_w = 100 * width / w100 if width else None
    cands = [p for p in (px_h, px_w) if p]
    best, best_err = None, None
    if px_h and px_w:
        lo, hi = sorted([px_h, px_w])
        for i in range(0, 101):
            p = lo + (hi - lo) * i / 100
            eh, ew = abs(h100 * p / 100 - ink) / 0.5, abs(w100 * p / 100 - width) / 2.0
            e = max(eh, ew)
            if best_err is None or e < best_err:
                best, best_err = p, e
    else:
        best, best_err = cands[0], 0.0
    hh, ww = measure(fam, wt, round(best), word, upper, W, H, tracking)
    return {"font": fontspec, "word": word, "tracking_em": tracking, "px_for_height": round(px_h, 1) if px_h else None,
            "px_for_width": round(px_w, 1) if px_w else None, "verified_px": int(round(best)),
            "at_verified_px": {"ink_pct_of_H": round(hh, 2), "width_pct_of_W": round(ww, 1)},
            "within_tolerance": bool(best_err is not None and best_err <= 1.0)}


def tiers(spec):
    t = (spec.get("captions") or spec.get("captions_spec") or {}).get("type") or {}   # caption-spec or blueprint
    return [(name, tier) for name, tier in t.items() if isinstance(tier, dict)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font"); ap.add_argument("--word"); ap.add_argument("--ink", type=float); ap.add_argument("--width", type=float)
    ap.add_argument("--px", type=float, help="report the expected ink height / width of --word at this size");
    ap.add_argument("--upper", action="store_true"); ap.add_argument("--spec"); ap.add_argument("--write", action="store_true")
    ap.add_argument("--canvas", default="1080x1920"); ap.add_argument("--tracking", type=float, default=0.0, help="letter-spacing in em")
    a = ap.parse_args()
    W, H = (int(v) for v in a.canvas.split("x"))
    if a.spec:
        spec = json.load(open(a.spec))
        if spec.get("reference_canvas") and spec["reference_canvas"][0] > spec["reference_canvas"][1]:
            W, H = 1920, 1080
        for name, tier in tiers(spec):
            cal = tier.get("calibration")
            local = (tier.get("closest_match") or {}).get("local")
            if not cal or not local:
                continue
            cal = cal if isinstance(cal, list) else [cal]
            fits = []
            for c in cal:
                if not c.get("word"):
                    continue
                up = "upper" in str(tier.get("case", "")).lower() or c["word"].isupper()
                try:
                    fits.append(fit(local, c["word"], c.get("ink_pct_of_H"), c.get("width_pct_of_W"), up, W, H, em(tier.get("tracking"))))
                except SystemExit as e:
                    print("%s/%s: %s" % (spec.get("id"), name, e))
            if fits:
                px = int(round(sum(f["verified_px"] for f in fits) / len(fits)))
                print("%s/%s %s: verified_px %d %s" % (spec.get("id"), name, local, px,
                      "; ".join("%s h%s/w%s -> %d (%s)" % (f["word"], f["px_for_height"], f["px_for_width"], f["verified_px"],
                                "ok" if f["within_tolerance"] else "font proportions differ") for f in fits)))
                if a.write:
                    tier["verified_px"] = px
                    tier["fit"] = fits
        if a.write:
            json.dump(spec, open(a.spec, "w"), indent=1, ensure_ascii=False)
        return
    if a.px:
        fam, wt = parse(a.font)
        h, w = measure(fam, wt, a.px, a.word, a.upper, W, H, a.tracking)
        print(json.dumps({"font": a.font, "word": a.word, "px": a.px, "tracking_em": a.tracking,
                          "expected_ink_pct_of_H": round(h, 2), "expected_width_pct_of_W": round(w, 1)}, indent=1))
        return
    if a.ink is None and a.width is None:
        raise SystemExit("give --px (expected size of a word) or --ink/--width (solve px from a measurement)")
    print(json.dumps(fit(a.font, a.word, a.ink, a.width, a.upper, W, H, a.tracking), indent=1))


if __name__ == "__main__":
    main()
