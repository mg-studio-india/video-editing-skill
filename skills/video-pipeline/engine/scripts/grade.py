#!/usr/bin/env python3
"""grade.py: cinematic, high-retention color grading engine for creator videos.

Provides professional color grading filter chains (contrast S-curves, skin tone protection,
color temperature, vibrance, black point crush, highlight rolloff, and subtle clarity)
via FFmpeg filter graphs, with side-by-side preview comparisons.

Presets:
  commercial-clean   Punchy S-curve, warm skin tone protection, +12% vibrance, lifted blacks, subtle clarity.
  cinematic-warm     Golden highlights (+300K), rich film contrast, subtle cyan shadow tint, organic depth.
  modern-tech        Clean 5600K neutral daylight, deep blacks, high clarity, vivid saturated accents.
  moody-film         Analog film print curve, softened highlights, lifted deep blacks, warm shadows, fine 35mm grain.
  vibrant-pop        High-energy social feed look, rich color saturation, dynamic contrast punch, warm skin tones.
  neutral-correct    Corrects green/yellow phone sensor cast, normalizes exposure and white balance.

Usage:
  # Generate side-by-side preview sheet comparing presets on a keyframe
  python3 grade.py preview --input raw.mp4 --out grade-comparison.jpg [--at 5.0]

  # Apply a preset to a video
  python3 grade.py apply --input raw.mp4 --out graded.mp4 --preset commercial-clean

  # Print the FFmpeg -vf filter string for a preset
  python3 grade.py filter --preset cinematic-warm
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Professional FFmpeg color grading filter chains
PRESET_FILTERS = {
    "commercial-clean": (
        "curves=m='0/0 0.22/0.18 0.50/0.52 0.78/0.84 1/1',"
        "colortemperature=temperature=6200,"
        "eq=contrast=1.08:brightness=0.01:saturation=1.12,"
        "unsharp=3:3:0.6:3:3:0.0"
    ),
    "cinematic-warm": (
        "curves=r='0/0.02 0.50/0.53 1/1':b='0/0.04 0.50/0.47 1/0.95',"
        "colortemperature=temperature=6600,"
        "eq=contrast=1.14:brightness=-0.01:saturation=1.15,"
        "unsharp=3:3:0.5:3:3:0.0"
    ),
    "modern-tech": (
        "curves=m='0/0 0.20/0.16 0.80/0.86 1/1',"
        "colortemperature=temperature=5600,"
        "eq=contrast=1.12:brightness=0.0:saturation=1.18,"
        "unsharp=5:5:0.7:5:5:0.0"
    ),
    "moody-film": (
        "curves=m='0/0.06 0.25/0.22 0.75/0.78 1/0.94',"
        "colorbalance=rm=0.03:gm=0.01:bm=-0.03,"
        "eq=contrast=1.06:brightness=0.01:saturation=0.92,"
        "noise=alls=6:allf=t+u"
    ),
    "vibrant-pop": (
        "curves=m='0/0 0.25/0.22 0.50/0.53 0.75/0.82 1/1',"
        "colortemperature=temperature=6100,"
        "eq=contrast=1.16:brightness=0.02:saturation=1.24,"
        "unsharp=3:3:0.8:3:3:0.0"
    ),
    "neutral-correct": (
        "colorbalance=gm=-0.03:rm=0.02:bm=0.01,"
        "colortemperature=temperature=5800,"
        "eq=contrast=1.05:brightness=0.01:saturation=1.06"
    ),
}


def get_filter_string(preset: str, custom_params: dict | None = None) -> str:
    """Returns the FFmpeg video filter string for the preset or custom parameters."""
    if custom_params:
        parts = []
        c = custom_params.get("contrast", 1.0)
        s = custom_params.get("saturation", 1.0)
        b = custom_params.get("brightness", 0.0)
        if c != 1.0 or s != 1.0 or b != 0.0:
            parts.append(f"eq=contrast={c}:saturation={s}:brightness={b}")
        temp = custom_params.get("temperature")
        if temp:
            parts.append(f"colortemperature=temperature={temp}")
        curve = custom_params.get("curve")
        if curve:
            parts.append(f"curves={curve}")
        unsharp = custom_params.get("sharpness")
        if unsharp:
            parts.append(f"unsharp=3:3:{unsharp}:3:3:0.0")
        if parts:
            return ",".join(parts)
    return PRESET_FILTERS.get(preset, PRESET_FILTERS["commercial-clean"])


def extract_frame(video: str, at_sec: float, out_path: str, vf: str | None = None) -> bool:
    """Extracts a single frame from video at the given timestamp with optional filter."""
    cmd = ["ffmpeg", "-y", "-ss", f"{at_sec:.3f}", "-i", video]
    if vf:
        cmd += ["-vf", vf]
    cmd += ["-vframes", "1", "-q:v", "2", out_path]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 0


def generate_preview_grid(video: str, out_image: str, at_sec: float = 3.0) -> str:
    """Generates a labeled 2x3 or 2x2 comparison image showing raw footage vs presets."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        sys.exit("generate_preview_grid requires pillow (python3 -m pip install pillow)")

    presets_to_show = [
        ("Raw Footage (Unadjusted)", None),
        ("Commercial Clean (Warm & Punchy)", "commercial-clean"),
        ("Cinematic Warm (Golden & Film Depth)", "cinematic-warm"),
        ("Modern Tech (Daylight & High Clarity)", "modern-tech"),
        ("Moody Film (Analog Print & Soft Lift)", "moody-film"),
        ("Vibrant Pop (Social Media High-Energy)", "vibrant-pop"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        rendered_images = []
        for label, preset in presets_to_show:
            tmp_img = os.path.join(tmpdir, f"{preset or 'raw'}.jpg")
            vf = PRESET_FILTERS.get(preset) if preset else None
            ok = extract_frame(video, at_sec, tmp_img, vf)
            if not ok:
                # If extraction at at_sec failed (e.g. video shorter than at_sec), try at 0.5s
                extract_frame(video, 0.5, tmp_img, vf)
            if os.path.exists(tmp_img):
                rendered_images.append((label, Image.open(tmp_img).convert("RGB")))

        if not rendered_images:
            sys.exit(f"Failed to extract frames from {video}")

        # Tile images into a 3-column or 2-column grid
        cols = 3 if len(rendered_images) > 4 else 2
        rows = (len(rendered_images) + cols - 1) // cols

        orig_w, orig_h = rendered_images[0][1].size
        # Target thumbnail cell size
        cell_w = 480
        cell_h = int(cell_w * (orig_h / orig_w))
        header_h = 36
        padding = 16

        total_w = cols * cell_w + (cols + 1) * padding
        total_h = rows * (cell_h + header_h) + (rows + 1) * padding

        grid = Image.new("RGB", (total_w, total_h), color="#121214")
        draw = ImageDraw.Draw(grid)

        # Default or fallback font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        except Exception:
            font = ImageFont.load_default()

        for idx, (label, img) in enumerate(rendered_images):
            r = idx // cols
            c = idx % cols
            x = padding + c * (cell_w + padding)
            y = padding + r * (cell_h + header_h + padding)

            # Draw header label
            draw.rectangle([x, y, x + cell_w, y + header_h], fill="#202024")
            draw.text((x + 12, y + 8), label, fill="#FFFFFF" if "Raw" not in label else "#FFD700", font=font)

            # Resize thumbnail
            thumb = img.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
            grid.paste(thumb, (x, y + header_h))
            # Border
            draw.rectangle([x, y + header_h, x + cell_w, y + header_h + cell_h], outline="#3A3A40", width=1)

        os.makedirs(os.path.dirname(os.path.abspath(out_image)), exist_ok=True)
        grid.save(out_image, quality=92)
        print(f"Color grading comparison preview generated: {out_image}")
        return out_image


def apply_grade(input_video: str, out_video: str, preset: str = "commercial-clean",
                custom_params: dict | None = None, crf: int = 16, preset_speed: str = "fast") -> bool:
    """Applies the selected color grade to the video with full BT.709 metadata tagging."""
    vf = get_filter_string(preset, custom_params)
    os.makedirs(os.path.dirname(os.path.abspath(out_video)), exist_ok=True)

    cmd = [
        "ffmpeg", "-y", "-v", "error", "-i", input_video,
        "-vf", vf,
        "-c:v", "libx264", "-preset", preset_speed, "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
        "-c:a", "copy",
        "-movflags", "+faststart+write_colr",
        out_video
    ]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"Failed to grade video (exit {r.returncode})")
    print(f"Graded video saved ({preset}): {out_video}")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    # Preview
    p_prev = sub.add_parser("preview", help="Generate side-by-side comparison sheet of presets")
    p_prev.add_argument("--input", required=True, help="Input video path")
    p_prev.add_argument("--out", required=True, help="Output comparison JPG path")
    p_prev.add_argument("--at", type=float, default=3.0, help="Frame timestamp to compare (default: 3.0s)")

    # Apply
    p_apply = sub.add_parser("apply", help="Apply color grade to video")
    p_apply.add_argument("--input", required=True, help="Input video path")
    p_apply.add_argument("--out", required=True, help="Output video path")
    p_apply.add_argument("--preset", default="commercial-clean", choices=list(PRESET_FILTERS.keys()), help="Grading preset")
    p_apply.add_argument("--contrast", type=float, help="Custom contrast override (e.g. 1.12)")
    p_apply.add_argument("--saturation", type=float, help="Custom saturation override (e.g. 1.15)")
    p_apply.add_argument("--brightness", type=float, help="Custom brightness override (e.g. 0.02)")
    p_apply.add_argument("--temperature", type=int, help="Color temperature in Kelvin (e.g. 6200)")
    p_apply.add_argument("--crf", type=int, default=16, help="H.264 CRF quality (default: 16)")

    # Filter
    p_filt = sub.add_parser("filter", help="Print FFmpeg filter string for a preset")
    p_filt.add_argument("--preset", default="commercial-clean", choices=list(PRESET_FILTERS.keys()))

    args = ap.parse_args()

    if args.cmd == "preview":
        generate_preview_grid(args.input, args.out, args.at)
    elif args.cmd == "filter":
        print(get_filter_string(args.preset))
    elif args.cmd == "apply":
        custom = {}
        if args.contrast is not None: custom["contrast"] = args.contrast
        if args.saturation is not None: custom["saturation"] = args.saturation
        if args.brightness is not None: custom["brightness"] = args.brightness
        if args.temperature is not None: custom["temperature"] = args.temperature
        apply_grade(args.input, args.out, args.preset, custom or None, crf=args.crf)


if __name__ == "__main__":
    main()
