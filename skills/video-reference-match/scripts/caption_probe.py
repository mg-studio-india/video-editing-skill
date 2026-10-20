#!/usr/bin/env python3
"""caption_probe.py: measure how captions / on-screen text look and move in a reference video."""
import argparse
import json
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont


IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")


def is_image(path):
    return path.lower().endswith(IMAGE_EXT)


def probe(video):
    if is_image(video):                       # a still (e.g. a HyperFrames snapshot PNG): one frame, fps irrelevant
        w, h = Image.open(video).size
        return w, h, 30.0
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "json", video], capture_output=True, text=True).stdout
    s = json.loads(out)["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(n) / float(d)


def frame_at(video, t):
    if is_image(video):
        return Image.open(video).convert("RGB")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % max(0, t), "-i", video, "-frames:v", "1",
                          "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(raw)).convert("RGB")


def frames_from(video, t0, dur):
    if is_image(video):
        return [Image.open(video).convert("RGB")]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % max(0, t0), "-t", "%.3f" % dur, "-i", video,
                          "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    from io import BytesIO
    imgs, i = [], 0
    sig = b"\x89PNG\r\n\x1a\n"
    parts = raw.split(sig)
    for p in parts[1:]:
        imgs.append(Image.open(BytesIO(sig + p)).convert("RGB"))
    return imgs


def font(sz):
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def grid(img):
    W, H = img.size
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    f = font(max(12, W // 45))
    for k in range(1, 20):
        x, y = W * k / 20, H * k / 20
        a = 150 if k % 2 == 0 else 70
        d.line([(x, 0), (x, H)], fill=(0, 255, 255, a), width=1)
        d.line([(0, y), (W, y)], fill=(0, 255, 255, a), width=1)
        if k % 2 == 0:
            d.text((3, y - f.size - 1), "%d%%" % (k * 5), font=f, fill=(255, 255, 0, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
            d.text((x + 2, 3), "%d" % (k * 5), font=f, fill=(255, 255, 0, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


ROW_MIN_FRAC = 0.002   # a text row needs >= 0.2 % of the box width in ink pixels (was 0.4 %: lost light-weight descenders)


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)])


def text_bbox(img, box, ink=None):
    W, H = img.size
    x0, y0, x1, y1 = int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)
    a = np.asarray(img.crop((x0, y0, x1, y1))).astype(int)
    if ink:
        col, tol = ink
        mask = np.sqrt(((a - col) ** 2).sum(2)) < tol
        white = mask
        accent = np.zeros_like(mask)
    else:
        mx, mn = a.max(2), a.min(2)
        white = mn > 225
        accent = ((mx - mn) > 110) & (mx > 150)
        mask = white | accent
    rows = np.where(mask.sum(1) >= max(2, int(ROW_MIN_FRAC * (x1 - x0))))[0]   # low threshold: keeps thin descenders
    cols = np.where(mask.sum(0) > 1)[0]
    if len(rows) == 0:
        return None
    # split into text lines by gaps of empty rows
    lines, start = [], rows[0]
    for r0, r1 in zip(rows, rows[1:]):
        if r1 - r0 > 4:
            lines.append((start, r0))
            start = r1
    lines.append((start, rows[-1]))
    return {"top_px": int(y0 + rows[0]), "bottom_px": int(y0 + rows[-1]), "left_px": int(x0 + cols[0]),
            "right_px": int(x0 + cols[-1]),
            "top_pct": round(100 * (y0 + rows[0]) / H, 1), "bottom_pct": round(100 * (y0 + rows[-1]) / H, 1),
            "center_y_pct": round(100 * (y0 + (rows[0] + rows[-1]) / 2) / H, 1),
            "width_pct_of_frame": round(100 * (cols[-1] - cols[0]) / W, 1),
            "lines_px": [[int(y0 + a_), int(y0 + b_), int(b_ - a_ + 1)] for a_, b_ in lines],
            "lines": [line_extent(mask, a_, b_, x0, y0, W, H) for a_, b_ in lines],
            "line_heights_pct_of_H": [round(100 * (b_ - a_ + 1) / H, 2) for a_, b_ in lines],
            "white_px": int(white.sum()), "accent_px": int(accent.sum())}


def line_extent(mask, a_, b_, x0, y0, W, H):
    cols = np.where(mask[a_:b_ + 1].sum(0) > 0)[0]
    return {"top_pct": round(100 * (y0 + a_) / H, 1), "height_pct_of_H": round(100 * (b_ - a_ + 1) / H, 2),
            "left_pct": round(100 * (x0 + cols[0]) / W, 1) if len(cols) else None,
            "width_pct_of_W": round(100 * (cols[-1] - cols[0]) / W, 1) if len(cols) else None}


def kmeans_colors(img, box, k=6):
    W, H = img.size
    a = np.asarray(img.crop((int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)))).reshape(-1, 3).astype(float)
    if len(a) > 40000:
        a = a[np.random.default_rng(0).choice(len(a), 40000, replace=False)]
    c = a[np.linspace(0, len(a) - 1, k).astype(int)]
    for _ in range(12):
        lab = ((a[:, None, :] - c[None]) ** 2).sum(2).argmin(1)
        c = np.array([a[lab == j].mean(0) if (lab == j).any() else c[j] for j in range(k)])
    share = np.bincount(lab, minlength=k) / len(a)
    o = np.argsort(-share)
    return [{"hex": "#%02X%02X%02X" % tuple(int(round(v)) for v in c[j]), "share": round(float(share[j]), 3)} for j in o]


def tile(frames, t0, fps, cols=6, tw=240):
    if not frames:
        return None
    th = int(frames[0].size[1] * tw / frames[0].size[0])
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    f = font(13)
    for i, fr in enumerate(frames):
        x, y = (i % cols) * tw, (i // cols) * (th + 18)
        sheet.paste(fr.resize((tw, th)), (x, y + 18))
        d.text((x + 4, y + 2), "+%df  %.3fs" % (i, t0 + i / fps), font=f, fill=(255, 255, 255))
    return sheet


def scan(video, box, top=14, gap=0.35):
    W, H, fps = probe(video)
    w, h = W // 4, H // 4
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", "scale=%d:%d,format=gray" % (w, h), "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    v = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.int16)
    x0, y0, x1, y1 = int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)
    d = np.abs(np.diff(v, axis=0))
    inside = d[:, y0:y1, x0:x1].mean((1, 2))
    whole = d.mean((1, 2))
    score = inside - 0.6 * whole
    order = np.argsort(-score)
    picks = []
    for i in order:
        t = (i + 1) / fps
        if all(abs(t - p) > gap for p, _ in picks):
            picks.append((t, float(score[i])))
        if len(picks) >= top:
            break
    picks.sort()
    print("caption-region changes (time s, score): " + ", ".join("%.2f (%.1f)" % p for p in picks))
    return picks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out")
    ap.add_argument("--at")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--ink", help="comma list of #RRGGBB:tolerance text colours to measure, e.g. #FFFFFF:60,#7404E6:70")
    ap.add_argument("--box", help="x0,y0,x1,y1 fractions: the caption region to measure")
    ap.add_argument("--strip", type=float, default=0.7)
    a = ap.parse_args()
    box = [float(v) for v in a.box.split(",")] if a.box else None
    if a.scan:
        scan(a.video, box or [0, 0.3, 1, 0.9])
        return
    os.makedirs(a.out, exist_ok=True)
    W, H, fps = probe(a.video)
    inks = [(hexrgb(x.split(":")[0]), float(x.split(":")[1]) if ":" in x else 60.0, x.split(":")[0]) for x in a.ink.split(",")] if a.ink else []
    report = {"video": os.path.basename(a.video), "size": [W, H], "fps": round(fps, 3), "box": box, "times": {}}
    for t in [float(v) for v in a.at.split(",")]:
        tag = ("%.2f" % t).rstrip("0").rstrip(".")
        img = frame_at(a.video, t)
        grid(img).save(os.path.join(a.out, "grid_%s.jpg" % tag), quality=88)
        fr = frames_from(a.video, t - 0.10, a.strip)
        sh = tile(fr, t - 0.10, fps)
        if sh:
            sh.save(os.path.join(a.out, "anim_%s.jpg" % tag), quality=85)
        if box:
            Wb, Hb = img.size
            crop = img.crop((int(box[0] * Wb), int(box[1] * Hb), int(box[2] * Wb), int(box[3] * Hb)))
            crop.resize((crop.size[0] * 2, crop.size[1] * 2), Image.LANCZOS).save(os.path.join(a.out, "crop_%s.jpg" % tag), quality=92)
            entry = {"box": box, "ink_args": a.ink, "colors": kmeans_colors(img, box)}   # per-time box: runs can differ
            if inks:
                entry["ink"] = {name: (lambda b: b and {**b, "box": box})(text_bbox(img, box, (col, tol))) for col, tol, name in inks}
                entry["per_frame_ink"] = [{"t": round(t - 0.10 + 2 * j / fps, 3),
                                           **{name: (lambda b: b and {k: b[k] for k in ("top_pct", "bottom_pct", "center_y_pct", "width_pct_of_frame", "line_heights_pct_of_H")})(text_bbox(f_, box, (col, tol)))
                                              for col, tol, name in inks}} for j, f_ in enumerate(fr[::2])]
            else:
                entry["text"] = text_bbox(img, box)
            report["times"][tag] = entry
        print("t=%s: grid_%s.jpg anim_%s.jpg (%d frames)%s" % (tag, tag, tag, len(fr), " crop + measure" if box else ""))
    if box:
        path = os.path.join(a.out, "measure.json")
        old = json.load(open(path)) if os.path.exists(path) else {"times": {}}
        for tag, new in report["times"].items():          # same time measured again (another colour / box): merge inks
            prev = old["times"].get(tag) or {}
            if "ink" in prev and "ink" in new:
                new["ink"] = {**prev["ink"], **new["ink"]}
            old["times"][tag] = {**prev, **new}
        report["times"] = old["times"]
        json.dump(report, open(path, "w"), indent=1)


if __name__ == "__main__":
    main()
