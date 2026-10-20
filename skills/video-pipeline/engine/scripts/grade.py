#!/usr/bin/env python3
"""grade.py: cinematic, high-retention color grading engine for creator videos."""
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
# Photographic Color Correction & Enhancement Standards (No Stylized Filters)
# -----------------------------------------------------------------------------

PRESET_FILTERS = {
    "enhanced-natural": (
        "colortemperature=temperature=5650,"
        "colorlevels=rimin=0.005:gimin=0.005:bimin=0.005:rimax=0.995:gimax=0.995:bimax=0.995,"
        "eq=gamma=1.02:gamma_weight=0.5:contrast=1.05:saturation=1.05,"
        "unsharp=3:3:0.12:3:3:0.0"
    ),
    "vibrant-enhanced": (
        "colortemperature=temperature=5600,"
        "colorlevels=rimin=0.004:gimin=0.004:bimin=0.004:rimax=0.996:gimax=0.996:bimax=0.996,"
        "eq=gamma=1.03:gamma_weight=0.5:contrast=1.08:saturation=1.08,"
        "unsharp=3:3:0.18:3:3:0.0"
    ),
    "neutral-true": (
        "colortemperature=temperature=5650,"
        "colorlevels=rimin=0.002:gimin=0.002:bimin=0.002:rimax=0.998:gimax=0.998:bimax=0.998,"
        "eq=contrast=1.03:saturation=1.02"
    ),
}

# Compatibility aliases
PRESET_FILTERS["studio-clean-balanced"] = PRESET_FILTERS["enhanced-natural"]
PRESET_FILTERS["kodak-portra-warm"] = PRESET_FILTERS["enhanced-natural"]
PRESET_FILTERS["commercial-clean"] = PRESET_FILTERS["enhanced-natural"]
PRESET_FILTERS["neutral-correct"] = PRESET_FILTERS["neutral-true"]
PRESET_FILTERS["hollywood-teal-orange"] = PRESET_FILTERS["vibrant-enhanced"]
PRESET_FILTERS["vox-documentary"] = PRESET_FILTERS["enhanced-natural"]
PRESET_FILTERS["magnates-gold"] = PRESET_FILTERS["vibrant-enhanced"]
PRESET_FILTERS["fuji-pro-cinematic"] = PRESET_FILTERS["enhanced-natural"]
PRESET_FILTERS["moody-film"] = PRESET_FILTERS["enhanced-natural"]
PRESET_FILTERS["nordic-cold"] = PRESET_FILTERS["neutral-true"]
PRESET_FILTERS["vibrant-pop"] = PRESET_FILTERS["vibrant-enhanced"]



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


def is_hlg_hdr(video_path: str | None) -> bool:
    if not video_path or not os.path.exists(video_path):
        return False
    try:
        cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=color_transfer,color_primaries,pix_fmt",
               "-of", "json", video_path]
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(r.stdout)
        s = data.get("streams", [{}])[0]
        trc = s.get("color_transfer", "").lower()
        pri = s.get("color_primaries", "").lower()
        return "arib-std-b67" in trc or "bt2020" in pri
    except Exception:
        return False


def get_base_format_filter(input_video: str | None = None) -> str:
    if input_video and is_hlg_hdr(input_video):
        return "colorspace=all=bt709:iprimaries=bt2020:ispace=bt2020nc:itrc=bt2020-10:format=yuv420p"
    return "format=yuv420p"


def calculate_dynamic_color_correction(
    video_path: str,
    timestamps: list[float] | None = None
) -> dict:
    default_res = {
        "vf": PRESET_FILTERS["enhanced-natural"],
        "params": {"imin": 0.005, "imax": 0.995, "gamma": 1.02, "contrast": 1.05, "saturation": 1.05, "temperature": 5650, "sharpness": 0.12},
        "metrics": {"p1_shadow": 1.0, "p50_mid": 128.0, "p99_highlight": 254.0, "mean_saturation": 0.30}
    }
    if not video_path or not os.path.exists(video_path):
        return default_res

    try:
        import cv2
        import numpy as np
    except ImportError:
        return default_res

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return default_res

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    duration = max(1.0, total_frames / fps)

    if not timestamps:
        timestamps = [duration * p for p in [0.15, 0.35, 0.60, 0.85]]

    all_y = []
    all_sat = []
    all_r, all_g, all_b = [], [], []
    lap_vars = []

    for ts in timestamps:
        cap.set(cv2.CAP_PROP_POS_MSEC, ts * 1000)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        h, w = frame.shape[:2]
        # Crop center 70% width, 80% height (speaker/subject focus)
        cy0, cy1 = int(h * 0.1), int(h * 0.9)
        cx0, cx1 = int(w * 0.15), int(w * 0.85)
        crop = frame[cy0:cy1, cx0:cx1]

        b, g, r = cv2.split(crop)
        yuv = cv2.cvtColor(crop, cv2.COLOR_BGR2YUV)
        y = yuv[:, :, 0]
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        sat = hsv[:, :, 1] / 255.0

        all_y.append(y.flatten())
        all_sat.append(sat.flatten())
        all_r.append(r.flatten())
        all_g.append(g.flatten())
        all_b.append(b.flatten())

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        lap_vars.append(cv2.Laplacian(gray, cv2.CV_64F).var())

    cap.release()

    if not all_y:
        return default_res

    concat_y = np.concatenate(all_y)
    concat_sat = np.concatenate(all_sat)
    concat_r = np.concatenate(all_r)
    concat_g = np.concatenate(all_g)
    concat_b = np.concatenate(all_b)

    # 1. Luminance & Dynamic Range
    p1 = float(np.percentile(concat_y, 1.0))
    p99 = float(np.percentile(concat_y, 99.0))
    p50 = float(np.median(concat_y))
    std_y = float(np.std(concat_y))

    # Black floor lift / White ceiling clamp
    imin = round(max(0.004, min(0.08, (p1 / 255.0) * 0.85)), 3)
    imax = round(min(0.998, max(0.92, (p99 / 255.0) + (1.0 - p99 / 255.0) * 0.3)), 3)

    # 2. Midtones (Gamma) & Contrast
    curr_mid = p50 / 255.0
    gamma = round(max(0.92, min(1.15, (0.48 / max(0.2, curr_mid)) ** 0.5)), 2)

    if std_y < 45.0:
        contrast = 1.08
    elif std_y > 65.0:
        contrast = 1.02
    else:
        contrast = round(1.0 + (55.0 - std_y) * 0.002, 2)
        contrast = max(1.02, min(1.10, contrast))

    # 3. Saturation & Vibrance
    mean_sat = float(np.mean(concat_sat))
    if mean_sat < 0.24:
        sat_boost = round(min(1.25, max(1.04, 0.28 / max(0.12, mean_sat))), 2)
    elif mean_sat > 0.38:
        sat_boost = 0.98
    else:
        sat_boost = 1.05

    # 4. Color Balance (Temperature / Tint)
    mean_r, mean_g, mean_b = float(np.mean(concat_r)), float(np.mean(concat_g)), float(np.mean(concat_b))
    rb_ratio = mean_r / max(1.0, mean_b)
    if rb_ratio > 1.08:
        temp = 5400  # cool down warm cast
    elif rb_ratio < 0.92:
        temp = 6200  # warm up cool cast
    else:
        temp = 5650  # neutral balanced daylight

    # 5. Clarity
    mean_lap = float(np.mean(lap_vars)) if lap_vars else 100.0
    sharpness = 0.12 if mean_lap < 300 else 0.08

    vf = (
        f"colortemperature=temperature={temp},"
        f"colorlevels=rimin={imin}:gimin={imin}:bimin={imin}:rimax={imax}:gimax={imax}:bimax={imax},"
        f"eq=gamma={gamma}:gamma_weight=0.5:contrast={contrast}:saturation={sat_boost},"
        f"unsharp=3:3:{sharpness}:3:3:0.0"
    )

    metrics = {
        "p1_shadow": round(p1, 1),
        "p50_mid": round(p50, 1),
        "p99_highlight": round(p99, 1),
        "std_y_contrast": round(std_y, 1),
        "mean_saturation": round(mean_sat, 3),
        "mean_r": round(mean_r, 1),
        "mean_g": round(mean_g, 1),
        "mean_b": round(mean_b, 1),
        "rb_ratio": round(rb_ratio, 2),
        "laplacian_clarity": round(mean_lap, 1)
    }

    params = {
        "imin": imin,
        "imax": imax,
        "gamma": gamma,
        "contrast": contrast,
        "saturation": sat_boost,
        "temperature": temp,
        "sharpness": sharpness
    }

    return {
        "vf": vf,
        "params": params,
        "metrics": metrics
    }


def get_filter_string(preset: str = "dynamic", custom_params: dict | None = None, input_video: str | None = None) -> str:
    base = get_base_format_filter(input_video)
    if custom_params:
        if custom_params.get("formula"):
            tone = build_tone_formula(
                shadows=custom_params.get("shadows", 0.0),
                midtones=custom_params.get("midtones", 1.0),
                highlights=custom_params.get("highlights", 0.0),
                contrast=custom_params.get("contrast", 1.10),
                saturation=custom_params.get("saturation", 1.10),
                temperature=custom_params.get("temperature"),
                sharpness=custom_params.get("sharpness", 0.5),
            )
            return f"{base},{tone}"
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
            return f"{base},{','.join(parts)}"

    # If dynamic calculation is requested or input_video provided with dynamic/enhanced-natural
    if preset in ("dynamic", "auto") or (input_video and preset in ("enhanced-natural", "dynamic")):
        if input_video and os.path.exists(input_video):
            dyn = calculate_dynamic_color_correction(input_video)
            return f"{base},{dyn['vf']}"

    filt = PRESET_FILTERS.get(preset, PRESET_FILTERS["enhanced-natural"])
    return f"{base},{filt}"


def extract_frame(video: str, at_sec: float, out_path: str, vf: str | None = None) -> bool:
    cmd = ["ffmpeg", "-y", "-ss", f"{at_sec:.3f}", "-i", video]
    base = get_base_format_filter(video)
    if vf:
        full_vf = vf if ("format=" in vf or "colorspace=" in vf) else f"{base},{vf}"
        cmd += ["-vf", full_vf]
    else:
        cmd += ["-vf", base]
    cmd += ["-vframes", "1", "-q:v", "2", out_path]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 0


def generate_frame_correction_sheet(video: str, out_image: str, timestamps: list[float] | None = None,
                                    preset: str = "dynamic") -> str:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        sys.exit("generate_frame_correction_sheet requires pillow (python3 -m pip install pillow)")

    if not timestamps:
        timestamps = [3.0, 15.0, 30.0, 45.0]

    dyn_info = None
    if preset in ("dynamic", "enhanced-natural", "auto"):
        dyn_info = calculate_dynamic_color_correction(video, timestamps=timestamps)
        vf = dyn_info["vf"]
    else:
        vf = PRESET_FILTERS.get(preset, PRESET_FILTERS["enhanced-natural"])

    with tempfile.TemporaryDirectory() as tmpdir:
        pairs = []
        for idx, ts in enumerate(timestamps):
            raw_img = os.path.join(tmpdir, f"raw_{idx}.jpg")
            enh_img = os.path.join(tmpdir, f"enh_{idx}.jpg")

            extract_frame(video, ts, raw_img, vf=None)
            extract_frame(video, ts, enh_img, vf=vf)

            if os.path.exists(raw_img) and os.path.exists(enh_img):
                pairs.append((ts, Image.open(raw_img).convert("RGB"), Image.open(enh_img).convert("RGB")))

        if not pairs:
            sys.exit(f"Failed to extract frames for color correction comparison from {video}")

        orig_w, orig_h = pairs[0][1].size
        cell_w = 480
        cell_h = int(cell_w * (orig_h / orig_w))
        header_h = 42
        padding = 16

        cols = 2
        rows = len(pairs)

        total_w = cols * cell_w + (cols + 1) * padding
        total_h = rows * (cell_h + header_h) + (rows + 1) * padding

        sheet = Image.new("RGB", (total_w, total_h), color="#0f172a")
        draw = ImageDraw.Draw(sheet)

        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17)
        except Exception:
            font = ImageFont.load_default()

        for r_idx, (ts, img_raw, img_enh) in enumerate(pairs):
            y = padding + r_idx * (cell_h + header_h + padding)

            # Left: Raw
            x_raw = padding
            draw.rectangle([x_raw, y, x_raw + cell_w, y + header_h], fill="#334155")
            draw.text((x_raw + 14, y + 10), f"Frame at {ts:.1f}s · Original Camera Take", fill="#f1f5f9", font=font)
            thumb_raw = img_raw.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
            sheet.paste(thumb_raw, (x_raw, y + header_h))
            draw.rectangle([x_raw, y + header_h, x_raw + cell_w, y + header_h + cell_h], outline="#475569", width=1)

            # Right: Dynamic Corrected & Enhanced
            x_enh = padding + cell_w + padding
            draw.rectangle([x_enh, y, x_enh + cell_w, y + header_h], fill="#047857")
            if dyn_info and "params" in dyn_info:
                p = dyn_info["params"]
                title_enh = f"Frame at {ts:.1f}s · Dynamic Correction ({p['imin']}-{p['imax']}, γ{p['gamma']}, {p['saturation']}x)"
            else:
                title_enh = f"Frame at {ts:.1f}s · Color Corrected & Enhanced"
            draw.text((x_enh + 14, y + 10), title_enh, fill="#ecfdf5", font=font)
            thumb_enh = img_enh.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
            sheet.paste(thumb_enh, (x_enh, y + header_h))
            draw.rectangle([x_enh, y + header_h, x_enh + cell_w, y + header_h + cell_h], outline="#059669", width=2)

        os.makedirs(os.path.dirname(os.path.abspath(out_image)), exist_ok=True)
        sheet.save(out_image, quality=94)
        print(f"Dynamic color correction comparison sheet generated: {out_image}")
        return out_image


# Alias for backward compatibility
generate_preview_grid = generate_frame_correction_sheet



def apply_grade(
    input_video: str,
    out_video: str,
    preset: str = "kodak-portra-warm",
    custom_params: dict | None = None,
    crf: int = 16,
    preset_speed: str = "fast"
) -> bool:
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
