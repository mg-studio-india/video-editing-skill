#!/usr/bin/env python3
"""grade.py: cinematic, high-retention color grading engine for creator videos.

Provides professional 3-way color grading filter chains (shadows/lift, midtones/gamma,
highlights/gain, contrast S-curves, skin tone protection, color temperature, vibrance,
and unsharp clarity) via FFmpeg filter graphs, with side-by-side preview comparisons.

Presets (10 Studio & Cinema Presets):
  kodak-portra-warm      Kodak Portra 400: Golden skin tones, soft highlight rolloff, lifted blacks, organic contrast.
  hollywood-teal-orange  Blockbuster cinema: Teal shadow split, warm amber midtones/highlights, punchy dynamic range.
  fuji-pro-cinematic     Fuji Eterna / Pro 400H: Pastel greens/cool mids, soft rolloff, natural documentary skin tones.
  vox-documentary        Investigative journalism: Deep true blacks, crisp micro-clarity, 5600K neutral daylight.
  magnates-gold          MagnatesMedia style: Amber-gold midtone bias, rich contrast with deep true blacks, rich accents.
  modern-tech            Clean 5800K daylight, deep blacks, high clarity, vivid saturated tech accents.
  moody-film             Analog 35mm print curve, softened highlights, lifted deep blacks, warm shadows, fine grain.
  vibrant-pop            High-energy social feed look, rich color saturation, dynamic contrast punch, warm skin tones.
  nordic-cold            Desaturated Scandinavian drama look, cool blue shadows, muted mids, soft silvery highlights.
  studio-clean-balanced  Precision Rec.709 balanced studio correction, phone sensor cast removal, neutral skin fidelity.

Formula Mode:
  Explicitly control the 3-way color wheels:
    --shadows       (-1.0 to 1.0): Black floor lift/crush and low-tone density
    --midtones      (0.5 to 1.8): Midtone gamma exposure and voice clarity
    --highlights    (-1.0 to 1.0): White ceiling rolloff and clipping protection
    --contrast      (0.8 to 1.5): Contrast S-curve
    --saturation    (0.0 to 2.0): Global color saturation and vibrance
    --temperature   (Kelvin): Color temperature balance (e.g. 5600, 6400)
    --sharpness     (0.0 to 1.5): Unsharp mask clarity

Usage:
  # Generate comparison preview grid of top presets on a keyframe
  python3 grade.py preview --input raw.mp4 --out grade-comparison.jpg [--at 3.0]

  # Apply a preset to a video
  python3 grade.py apply --input raw.mp4 --out graded.mp4 --preset kodak-portra-warm

  # Apply custom formula 3-way grade
  python3 grade.py apply --input raw.mp4 --out graded.mp4 --formula --shadows 0.03 --midtones 1.08 --highlights -0.04 --contrast 1.14 --saturation 1.12
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runtime
runtime.ensure_project_venv()

# -----------------------------------------------------------------------------
# 10 Professional Master Presets (Cinema & Digital Creator Standards)
# -----------------------------------------------------------------------------

PRESET_FILTERS = {
    "kodak-portra-warm": (
        "colorlevels=rimin=0.03:gimin=0.03:bimin=0.03:rimax=0.96:gimax=0.96:bimax=0.96,"
        "colorbalance=rm=0.05:gm=0.02:bm=-0.04:rh=0.03:gh=0.02:bh=-0.03,"
        "colortemperature=temperature=6400,"
        "eq=gamma=1.06:gamma_weight=0.6:contrast=1.12:saturation=1.10,"
        "unsharp=3:3:0.5:3:3:0.0"
    ),
    "hollywood-teal-orange": (
        "colorlevels=rimin=0.01:gimin=0.01:bimin=0.02:rimax=0.98:gimax=0.98:bimax=0.98,"
        "colorbalance=rs=-0.04:gs=0.02:bs=0.08:rm=0.06:gm=0.01:bm=-0.05:rh=0.07:gh=0.03:bh=-0.06,"
        "eq=gamma=1.08:gamma_weight=0.5:contrast=1.18:saturation=1.20,"
        "unsharp=3:3:0.6:3:3:0.0"
    ),
    "fuji-pro-cinematic": (
        "colorlevels=rimin=0.04:gimin=0.04:bimin=0.04:rimax=0.95:gimax=0.95:bimax=0.95,"
        "colorbalance=rs=0.0:gs=0.03:bs=0.02:rm=0.02:gm=0.01:bm=0.0:rh=-0.02:gh=0.01:bh=-0.02,"
        "eq=gamma=1.05:gamma_weight=0.7:contrast=1.08:saturation=0.96,"
        "unsharp=3:3:0.4:3:3:0.0"
    ),
    "vox-documentary": (
        "colorlevels=rimin=0.01:gimin=0.01:bimin=0.01:rimax=0.99:gimax=0.99:bimax=0.99,"
        "colortemperature=temperature=5600,"
        "colorbalance=rm=0.01:gm=0.0:bm=-0.01,"
        "eq=gamma=1.02:gamma_weight=0.5:contrast=1.14:saturation=1.08,"
        "unsharp=5:5:0.8:5:5:0.0"
    ),
    "magnates-gold": (
        "colorlevels=rimin=0.02:gimin=0.01:bimin=0.01:rimax=0.97:gimax=0.97:bimax=0.95,"
        "colorbalance=rm=0.08:gm=0.04:bm=-0.07:rh=0.06:gh=0.04:bh=-0.05,"
        "colortemperature=temperature=6300,"
        "eq=gamma=1.05:gamma_weight=0.5:contrast=1.20:saturation=1.16,"
        "unsharp=3:3:0.7:3:3:0.0"
    ),
    "modern-tech": (
        "colorlevels=rimin=0.02:gimin=0.02:bimin=0.02:rimax=0.98:gimax=0.98:bimax=0.98,"
        "colortemperature=temperature=5800,"
        "colorbalance=rs=-0.02:bs=0.04:rm=0.02:bm=0.02,"
        "eq=gamma=1.05:contrast=1.12:saturation=1.18,"
        "unsharp=5:5:0.7:5:5:0.0"
    ),
    "moody-film": (
        "colorlevels=rimin=0.06:gimin=0.06:bimin=0.06:rimax=0.94:gimax=0.94:bimax=0.94,"
        "colorbalance=rs=0.04:gs=0.01:bs=-0.03:rm=0.03:gm=0.01:bm=-0.02,"
        "eq=contrast=1.06:brightness=0.01:saturation=0.92,"
        "noise=alls=5:allf=t+u"
    ),
    "vibrant-pop": (
        "colorlevels=rimin=0.01:gimin=0.01:bimin=0.01:rimax=0.98:gimax=0.98:bimax=0.98,"
        "colortemperature=temperature=6100,"
        "colorbalance=rm=0.04:gm=0.01:bm=-0.02,"
        "eq=gamma=1.08:contrast=1.16:brightness=0.01:saturation=1.24,"
        "unsharp=3:3:0.8:3:3:0.0"
    ),
    "nordic-cold": (
        "colorlevels=rimin=0.03:gimin=0.03:bimin=0.05:rimax=0.96:gimax=0.96:bimax=0.98,"
        "colorbalance=rs=-0.05:gs=0.01:bs=0.08:rm=-0.03:bm=0.04,"
        "eq=gamma=1.02:contrast=1.10:saturation=0.85,"
        "unsharp=3:3:0.5:3:3:0.0"
    ),
    "studio-clean-balanced": (
        "colorbalance=rs=0.01:gs=-0.02:bs=0.01:rm=0.02:gm=-0.01:bm=0.0:rh=0.0:gh=-0.01:bh=0.0,"
        "colortemperature=temperature=5800,"
        "eq=gamma=1.04:gamma_weight=0.5:contrast=1.08:saturation=1.08,"
        "unsharp=3:3:0.5:3:3:0.0"
    ),
}

# Backward compatibility alias
PRESET_FILTERS["commercial-clean"] = PRESET_FILTERS["studio-clean-balanced"]
PRESET_FILTERS["cinematic-warm"] = PRESET_FILTERS["kodak-portra-warm"]
PRESET_FILTERS["neutral-correct"] = PRESET_FILTERS["studio-clean-balanced"]


# -----------------------------------------------------------------------------
# 3-Way Formula Engine
# -----------------------------------------------------------------------------

def build_tone_formula(
    shadows: float = 0.0,
    midtones: float = 1.0,
    highlights: float = 0.0,
    contrast: float = 1.10,
    saturation: float = 1.10,
    temperature: int | None = None,
    sharpness: float = 0.5,
    tint: float = 0.0,
) -> str:
    """Calculates a custom 3-way color grade filter string from acoustic/visual tone parameters.

    shadows:    -1.0 (deep crush) to +1.0 (lifted film black)
    midtones:    0.5 (darker mood) to 1.8 (bright exposure)
    highlights: -1.0 (soft rolloff/protect) to +1.0 (specular pop)
    contrast:    0.8 to 1.5
    saturation:  0.0 to 2.0
    temperature: Kelvin (e.g. 5600 daylight, 6400 warm)
    sharpness:   0.0 to 1.5 unsharp mask
    """
    parts = []

    # 1. Color Levels (Black Floor & White Ceiling)
    # Map shadows (-1.0 to 1.0) -> rimin/gimin/bimin (0.0 to 0.08)
    imin = max(0.0, min(0.12, round(0.02 + shadows * 0.04, 3)))
    # Map highlights (-1.0 to 1.0) -> rimax/gimax/bimax (0.92 to 1.0)
    imax = max(0.88, min(1.0, round(0.98 + highlights * 0.03, 3)))
    parts.append(f"colorlevels=rimin={imin}:gimin={imin}:bimin={imin}:rimax={imax}:gimax={imax}:bimax={imax}")

    # 2. Color Balance (Low, Mid, High Tones & Tint)
    cb_args = []
    if tint != 0.0:
        # Green/Magenta tint correction
        cb_args.append(f"gm={round(-tint * 0.04, 3)}")
    if cb_args:
        parts.append(f"colorbalance={':'.join(cb_args)}")

    # 3. Color Temperature
    if temperature:
        parts.append(f"colortemperature=temperature={int(temperature)}")

    # 4. Midtones (Gamma), Contrast & Saturation
    gamma = max(0.6, min(1.6, round(midtones, 2)))
    c = max(0.8, min(1.5, round(contrast, 2)))
    s = max(0.0, min(2.0, round(saturation, 2)))
    parts.append(f"eq=gamma={gamma}:gamma_weight=0.5:contrast={c}:saturation={s}")

    # 5. Micro-Clarity / Sharpness
    if sharpness > 0:
        sh = max(0.1, min(1.2, round(sharpness, 2)))
        parts.append(f"unsharp=3:3:{sh}:3:3:0.0")

    return ",".join(parts)


def get_filter_string(preset: str, custom_params: dict | None = None) -> str:
    """Returns the FFmpeg video filter string for the preset or custom parameters."""
    if custom_params:
        if custom_params.get("formula"):
            return build_tone_formula(
                shadows=custom_params.get("shadows", 0.0),
                midtones=custom_params.get("midtones", 1.0),
                highlights=custom_params.get("highlights", 0.0),
                contrast=custom_params.get("contrast", 1.10),
                saturation=custom_params.get("saturation", 1.10),
                temperature=custom_params.get("temperature"),
                sharpness=custom_params.get("sharpness", 0.5),
            )
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
    return PRESET_FILTERS.get(preset, PRESET_FILTERS["kodak-portra-warm"])


def extract_frame(video: str, at_sec: float, out_path: str, vf: str | None = None) -> bool:
    """Extracts a single frame from video at the given timestamp with optional filter."""
    cmd = ["ffmpeg", "-y", "-ss", f"{at_sec:.3f}", "-i", video]
    if vf:
        cmd += ["-vf", vf]
    cmd += ["-vframes", "1", "-q:v", "2", out_path]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 0


def generate_preview_grid(video: str, out_image: str, at_sec: float = 3.0) -> str:
    """Generates a labeled comparison grid showing raw footage vs curated presets."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        sys.exit("generate_preview_grid requires pillow (python3 -m pip install pillow)")

    presets_to_show = [
        ("Raw Footage (Unadjusted)", None),
        ("Kodak Portra Warm (Golden Skin & Soft Lift)", "kodak-portra-warm"),
        ("Hollywood Teal & Orange (Cinema Depth)", "hollywood-teal-orange"),
        ("Vox Documentary (Crisp Micro-Clarity & Neutral)", "vox-documentary"),
        ("Magnates Gold (Luxury Wealth Breakdown)", "magnates-gold"),
        ("Fuji Pro Cinematic (Pastel Film Tones)", "fuji-pro-cinematic"),
        ("Modern Tech (Clean 5800K & High Vibrance)", "modern-tech"),
        ("Moody Film (35mm Analog Print & Soft Grain)", "moody-film"),
        ("Vibrant Pop (Social Media High-Energy)", "vibrant-pop"),
        ("Nordic Cold (Cool Cyan Drama & Muted)", "nordic-cold"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        rendered_images = []
        for label, preset in presets_to_show:
            tmp_img = os.path.join(tmpdir, f"{preset or 'raw'}.jpg")
            vf = PRESET_FILTERS.get(preset) if preset else None
            ok = extract_frame(video, at_sec, tmp_img, vf)
            if not ok:
                extract_frame(video, 0.5, tmp_img, vf)
            if os.path.exists(tmp_img):
                rendered_images.append((label, Image.open(tmp_img).convert("RGB")))

        if not rendered_images:
            sys.exit(f"Failed to extract frames from {video}")

        # Tile images into a responsive grid
        cols = 3 if len(rendered_images) >= 6 else 2
        rows = (len(rendered_images) + cols - 1) // cols

        orig_w, orig_h = rendered_images[0][1].size
        cell_w = 460
        cell_h = int(cell_w * (orig_h / orig_w))
        header_h = 36
        padding = 16

        total_w = cols * cell_w + (cols + 1) * padding
        total_h = rows * (cell_h + header_h) + (rows + 1) * padding

        grid = Image.new("RGB", (total_w, total_h), color="#0e121a")
        draw = ImageDraw.Draw(grid)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17)
        except Exception:
            font = ImageFont.load_default()

        for idx, (label, img) in enumerate(rendered_images):
            r = idx // cols
            c = idx % cols
            x = padding + c * (cell_w + padding)
            y = padding + r * (cell_h + header_h + padding)

            # Draw header banner
            header_color = "#1f2937" if "Raw" not in label else "#b45309"
            draw.rectangle([x, y, x + cell_w, y + header_h], fill=header_color)
            draw.text((x + 12, y + 8), label, fill="#FFFFFF" if "Raw" not in label else "#FEF08A", font=font)

            thumb = img.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
            grid.paste(thumb, (x, y + header_h))
            draw.rectangle([x, y + header_h, x + cell_w, y + header_h + cell_h], outline="#374151", width=1)

        os.makedirs(os.path.dirname(os.path.abspath(out_image)), exist_ok=True)
        grid.save(out_image, quality=92)
        print(f"Color grading comparison preview generated: {out_image}")
        return out_image


def apply_grade(
    input_video: str,
    out_video: str,
    preset: str = "kodak-portra-warm",
    custom_params: dict | None = None,
    crf: int = 16,
    preset_speed: str = "fast"
) -> bool:
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

    p_prev = sub.add_parser("preview", help="Generate side-by-side comparison sheet of presets")
    p_prev.add_argument("--input", required=True, help="Input video path")
    p_prev.add_argument("--out", required=True, help="Output comparison JPG path")
    p_prev.add_argument("--at", type=float, default=3.0, help="Frame timestamp to compare (default: 3.0s)")

    p_apply = sub.add_parser("apply", help="Apply color grade to video")
    p_apply.add_argument("--input", required=True, help="Input video path")
    p_apply.add_argument("--out", required=True, help="Output video path")
    p_apply.add_argument("--preset", default="kodak-portra-warm", choices=list(PRESET_FILTERS.keys()), help="Grading preset")
    p_apply.add_argument("--formula", action="store_true", help="Enable 3-way tone formula mode")
    p_apply.add_argument("--shadows", type=float, default=0.0, help="Shadows/low tones (-1.0 to 1.0)")
    p_apply.add_argument("--midtones", type=float, default=1.0, help="Midtones gamma exposure (0.5 to 1.8)")
    p_apply.add_argument("--highlights", type=float, default=0.0, help="Highlights ceiling rolloff (-1.0 to 1.0)")
    p_apply.add_argument("--contrast", type=float, default=1.12, help="Custom contrast (0.8 to 1.5)")
    p_apply.add_argument("--saturation", type=float, default=1.12, help="Custom saturation (0.0 to 2.0)")
    p_apply.add_argument("--temperature", type=int, help="Color temperature in Kelvin (e.g. 6400)")
    p_apply.add_argument("--sharpness", type=float, default=0.5, help="Unsharp micro-clarity (0.0 to 1.5)")
    p_apply.add_argument("--crf", type=int, default=16, help="H.264 CRF quality (default: 16)")

    p_filt = sub.add_parser("filter", help="Print FFmpeg filter string for a preset or formula")
    p_filt.add_argument("--preset", default="kodak-portra-warm", choices=list(PRESET_FILTERS.keys()))
    p_filt.add_argument("--formula", action="store_true", help="Print 3-way tone formula filter")
    p_filt.add_argument("--shadows", type=float, default=0.0)
    p_filt.add_argument("--midtones", type=float, default=1.0)
    p_filt.add_argument("--highlights", type=float, default=0.0)
    p_filt.add_argument("--contrast", type=float, default=1.12)
    p_filt.add_argument("--saturation", type=float, default=1.12)
    p_filt.add_argument("--temperature", type=int)
    p_filt.add_argument("--sharpness", type=float, default=0.5)

    args = ap.parse_args()

    if args.cmd == "preview":
        generate_preview_grid(args.input, args.out, args.at)
    elif args.cmd == "filter":
        if args.formula:
            print(build_tone_formula(
                shadows=args.shadows,
                midtones=args.midtones,
                highlights=args.highlights,
                contrast=args.contrast,
                saturation=args.saturation,
                temperature=args.temperature,
                sharpness=args.sharpness,
            ))
        else:
            print(get_filter_string(args.preset))
    elif args.cmd == "apply":
        custom = {}
        if args.formula:
            custom["formula"] = True
            custom["shadows"] = args.shadows
            custom["midtones"] = args.midtones
            custom["highlights"] = args.highlights
            custom["contrast"] = args.contrast
            custom["saturation"] = args.saturation
            custom["temperature"] = args.temperature
            custom["sharpness"] = args.sharpness
        else:
            if args.contrast != 1.12: custom["contrast"] = args.contrast
            if args.saturation != 1.12: custom["saturation"] = args.saturation
            if args.temperature is not None: custom["temperature"] = args.temperature
        apply_grade(args.input, args.out, args.preset, custom or None, crf=args.crf)


if __name__ == "__main__":
    main()
