#!/usr/bin/env python3
"""memo.py: Brand memory manager (brand/MEMO.md)."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runtime  # noqa: E402
runtime.ensure_project_venv()

DEFAULT_MEMO_TEMPLATE = """# Brand Memory & Creative Preferences (MEMO.md)
> Persistent memory for video editing preferences, brand identity, and creative decisions. Prioritized across all future edits.

## 1. Identity & Profiles
- **Creator / Channel:** {creator}
- **Handles:**
  - Instagram: {instagram}
  - YouTube: {youtube}
  - X / Twitter: {twitter}
  - LinkedIn: {linkedin}
- **Website:** {website}
- **Logos & Badges:**
  - Primary Vector: {logo}
  - Monogram / Avatar: {avatar}
  - Verified Badge: {verified}
- **Core Topics:** {topics}

## 2. Creative Philosophy & Thinking Process
- **Default Standard:** {default_standard}
- **Anti-Pattern (Forbidden):** Never lock the edit into a static full-screen talking head with floating text overlays slapped on top.
- **Multi-Layout A-Roll Dynamism:**
  - *Full Camera:* Opening bold hook and closing CTA only.
  - *Corner PiP Minimization:* A-roll minimizes into a floating rounded squircle/circle (~28-34% width, clearing platform interaction buttons), opening 65-75% of the canvas.
  - *Split View / Stacked:* 35-45% presenter pane + 55-65% dedicated data/media canvas with styled 2-3px divider.
  - *Speaker Cutout / Matte:* Speaker silhouette extracted over modern graphical, deep neutral dark (#0e121a, #111116), clean white, or cinematic gradient mesh backdrops.
- **Empty Canvas Space Utilization:**
  - *Researcher Articles:* Newspaper/journal mastheads, report clippings with animated fluorescent marker pen sweeps (width: 0% -> 100%).
  - *Kinetic Data Charts:* Animated bar charts (scaleY: 0 -> 1), line growth curves, and live metric counters.
  - *3D Depth & Mockups:* Isometric tilted cards (perspective: 1000px, rotateY(-15deg), rotateX(8deg)) with soft ambient drop shadows.
  - *Natural Physics:* Momentum-driven entries, damped harmonic springs (power3.out, back.out(1.4)).

## 3. Typography & Captions
- **Autonomous Selection:** {autonomous_captions}
- **Primary Caption Engine:** {caption_engine}
- **Display / Punch Font:** {punch_font}
- **Body Font:** {body_font}
- **Language / Script:** {language_script}

## 4. Color Palette & Grading
- **Canvas / Dark:** {color_dark}
- **Surface / Cards:** {color_surface}
- **Text:** Primary {color_text_primary}, Secondary {color_text_secondary}
- **Accents:**
  - Gold / Primary: {color_accent_gold}
  - Cyan / Tech: {color_accent_cyan}
  - Green / Growth: {color_accent_green}
  - Red / Contrast: {color_accent_red}
- **Color Grading Preset:** {grade_preset}

## 5. Audio & Voice Master
- **Noise Suppression:** {audio_noise}
- **Target Loudness:** {audio_lufs}
- **Music Bed:** {audio_music}

## 6. Video Delivery & Quality Specifications
- **Video Quality / Resolution:** {video_quality}
- **Video Bitrate:** {video_bitrate}
- **Color Space:** {video_colorspace}

## 7. Outro & Call to Action
- **Card Style:** {outro_style}
- **Placement:** {outro_placement}
"""


def find_brand_dir(start: Path | str | None = None) -> Path:
    p = Path(start or os.getcwd()).resolve()
    for d in [p] + list(p.parents):
        cand = d / "brand"
        if cand.is_dir() or (d / "videos").is_dir() or (d / "package.json").is_file():
            return cand
    return p / "brand"


def find_memo(start: Path | str | None = None) -> Path:
    b = find_brand_dir(start)
    return b / "MEMO.md"


def init_memo(target: Path | str | None = None, values: dict | None = None) -> Path:
    memo_file = Path(target) if target else find_memo()
    memo_file.parent.mkdir(parents=True, exist_ok=True)
    if memo_file.exists():
        return memo_file

    defaults = {
        "creator": "Creator",
        "instagram": "@handle",
        "youtube": "@handle",
        "twitter": "@handle",
        "linkedin": "handle",
        "website": "",
        "logo": "brand/assets/logo.svg",
        "avatar": "brand/assets/avatar.png",
        "verified": "true",
        "topics": "Insights, Technology, Business",
        "default_standard": "Creative, innovative, high-retention creator style (Vox / MagnatesMedia / Raj Shamani caliber)",
        "autonomous_captions": "Active by default (zero user burden)",
        "caption_engine": "focus-blur-resolve (inactive blurred 3px, active in focus, punch in badge pills)",
        "punch_font": "Poppins Black (900) or Anton Display",
        "body_font": "Poppins Bold (700) or Inter",
        "language_script": "100% Roman Hinglish strictly (Devanagari forbidden)",
        "color_dark": "#0e121a",
        "color_surface": "rgba(14, 18, 26, 0.88)",
        "color_text_primary": "#ffffff",
        "color_text_secondary": "#94a3b8",
        "color_accent_gold": "#ffd700",
        "color_accent_cyan": "#00c3ff",
        "color_accent_green": "#00e676",
        "color_accent_red": "#ef4444",
        "grade_preset": "commercial-clean (Contrast 1.12, skin-tones protected)",
        "audio_noise": "DeepFilterNet3 (--denoise neural) or RNNoise (sh.rnnn) for road/car rumble",
        "audio_lufs": "-14.0 LUFS, True Peak <= -1.0 dBTP",
        "audio_music": "Ducked under speech by -18 dB (attack: 15ms, release: 350ms)",
        "video_quality": "UHD / 4K (2160x3840 for 9:16 vertical / 3840x2160 for 16:9 landscape)",
        "video_bitrate": "45M (Ultra High Bitrate mastering)",
        "video_colorspace": "BT.709 lossless color tags",
        "outro_style": "Interactive Instagram follow card (+1 Follower heart bounce, verified handle)",
        "outro_placement": "Final 2.5-3.0s of reel",
    }
    if values:
        defaults.update(values)

    content = DEFAULT_MEMO_TEMPLATE.format(**defaults)
    memo_file.write_text(content, encoding="utf-8")
    return memo_file


def parse_memo(memo_path: Path | str | None = None) -> dict:
    p = Path(memo_path) if memo_path else find_memo()
    if not p.is_file():
        return {}

    text = p.read_text(encoding="utf-8")
    out: dict[str, dict[str, str]] = {}
    current_sec = "global"
    out[current_sec] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            sec_name = line[3:].strip()
            # simplify section key
            m = re.match(r"^\d+\.\s*(.*)", sec_name)
            current_sec = m.group(1).lower().replace(" ", "_") if m else sec_name.lower().replace(" ", "_")
            out[current_sec] = {}
            continue

        if line.startswith("- **") and ":**" in line:
            k, v = line[4:].split(":**", 1)
            out[current_sec][k.strip().lower().replace(" ", "_")] = v.strip()
        elif line.startswith("- ") and ":" in line:
            k, v = line[2:].split(":", 1)
            out[current_sec][k.strip().lower().replace(" ", "_")] = v.strip()

    return out


def update_memo_field(key: str, value: str, memo_path: Path | str | None = None) -> bool:
    p = Path(memo_path) if memo_path else find_memo()
    if not p.is_file():
        init_memo(p)

    text = p.read_text(encoding="utf-8")
    # Pattern 1: - **Key:** Value
    pat1 = re.compile(rf"(- \*\*{re.escape(key)}:\*\*)(.*)", re.IGNORECASE)
    if pat1.search(text):
        new_text = pat1.sub(rf"\g<1> {value}", text)
        p.write_text(new_text, encoding="utf-8")
        return True

    # Pattern 2: - Key: Value
    pat2 = re.compile(rf"(- {re.escape(key)}:)(.*)", re.IGNORECASE)
    if pat2.search(text):
        new_text = pat2.sub(rf"\g<1> {value}", text)
        p.write_text(new_text, encoding="utf-8")
        return True

    # Pattern 3: Key: Value inside sub-bullets (e.g. Instagram)
    pat3 = re.compile(rf"(\s*-\s*{re.escape(key)}:\s*)(.*)", re.IGNORECASE)
    if pat3.search(text):
        new_text = pat3.sub(rf"\g<1>{value}", text)
        p.write_text(new_text, encoding="utf-8")
        return True

    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init", help="Initialize brand/MEMO.md")
    p_init.add_argument("--path", help="Path to write MEMO.md")
    p_init.add_argument("--creator", help="Creator name")
    p_init.add_argument("--instagram", help="Instagram handle")

    p_get = sub.add_parser("get", help="Get brand memo data")
    p_get.add_argument("--json", action="store_true", help="Print as JSON")
    p_get.add_argument("--path", help="Path to MEMO.md")

    p_set = sub.add_parser("set", help="Update a specific field in MEMO.md")
    p_set.add_argument("field", help="Field name (e.g. Instagram, Creator / Channel, Primary Caption Engine)")
    p_set.add_argument("value", help="New value")
    p_set.add_argument("--path", help="Path to MEMO.md")

    a = ap.parse_args()
    if a.cmd == "init":
        vals = {}
        if a.creator:
            vals["creator"] = a.creator
        if a.instagram:
            vals["instagram"] = a.instagram
        f = init_memo(a.path, vals)
        print(f"Initialized brand memo at: {f}")
    elif a.cmd == "get":
        data = parse_memo(a.path)
        if a.json:
            print(json.dumps(data, indent=2))
        else:
            for sec, fields in data.items():
                print(f"[{sec}]")
                for k, v in fields.items():
                    print(f"  {k}: {v}")
    elif a.cmd == "set":
        ok = update_memo_field(a.field, a.value, a.path)
        if ok:
            print(f"Updated {a.field} -> {a.value}")
        else:
            sys.exit(f"Field {a.field!r} not found in MEMO.md")
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
