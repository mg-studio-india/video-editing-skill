---
name: video-style
description: Curates the visual identity (color palette, typography pairings, card themes, color grading profiles, and motion physics) as style.json. Enables interactive user verification before visual elements are built. Owns Gate 3.
---

# Style & Visual Identity (Color Grading, Typography, Layout & Physics)

Visual consistency and polished styling separate professional content from messy amateur video. **The styling, formatting, typography, color grading profiles, and physical motion kinetics must be explicitly verified with the user before building on-screen elements.**

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## 1. Unified Style Architecture (`style.json`)

> [!IMPORTANT]
> **Brand Memory Integration (`brand/MEMO.md`):**
> Before generating `style.json`, always inspect `brand/MEMO.md` (or `$PROJECT/brand/MEMO.md`) and corporate style guides in `brand/` (e.g. `brand/brand-style-guide.pdf`). If present, its colors, typography, handles, logo assets, layout preferences, and thinking process must seed `style.json`. User brand memory strictly overrides generic defaults.

A production-grade `style.json` governs five interdependent visual pillars:

```json
{
  "theme": "high-ctr-creator",
  "format_layout": "clean-authority-framed",
  "palette": {
    "background": "#100e0d",
    "surface_glass": "rgba(16, 14, 12, 0.82)",
    "text_primary": "#ffffff",
    "text_secondary": "#cccccc",
    "accent_punch": "#ffd700",
    "accent_secondary": "#ff4d4d",
    "border_subtle": "rgba(255, 215, 0, 0.35)"
  },
  "typography": {
    "font_family_catalog": ["DM Sans", "Inter", "Poppins", "Google Sans", "Roboto"],
    "primary_punch": {
      "family": "Poppins",
      "weight": 900,
      "style": "normal",
      "letter_spacing": "-0.02em",
      "color": "#ffd700",
      "pill_background": "#ffd700",
      "pill_text_color": "#000000",
      "shadow": "none"
    },
    "card_header": {
      "family": "Inter",
      "weight": 700,
      "color": "#ffffff",
      "letter_spacing": "-0.01em"
    },
    "body_support": {
      "family": "DM Sans",
      "weight": 500,
      "color": "#f8fafc",
      "line_height": 1.25
    },
    "caption_inactive": {
      "family": "Inter",
      "weight": 400,
      "color": "rgba(255, 255, 255, 0.70)"
    }
  },
  "color_grading": {
    "preset": "commercial-clean",
    "contrast": 1.12,
    "saturation": 1.12,
    "temperature": 6200,
    "skin_tone_protection": true,
    "preview_sheet": "grade-preview.jpg"
  },
  "captions": {
    "mode": "phrase",
    "case": "as_spoken",
    "inactive_color": "rgba(255, 255, 255, 0.70)",
    "active_color": "#ffd700",
    "emphasis_bg": "rgba(255, 215, 0, 0.18)"
    // Note: y, size, max_words, and max_chars are calculated dynamically from raw video frames and transcript when omitted.
  },
  "motion_physics": {
    "entrance_ease": "power3.out",
    "pop_curve": "back.out(1.3)",
    "damping": 16,
    "stiffness": 180,
    "mass": 1.0,
    "tilt_angle_deg": -1.5,
    "scale_overshoot_pct": 6,
    "camera_punch_scale": 1.10
  }
}
```

---

## 2. Professional Color Grading Engine (`grade.py`)

Raw camera/phone footage is almost always flat, slightly green/yellow-tinted, or washed out. Use `grade.py` to generate side-by-side preview comparisons and apply calibrated color grading:

```bash
# Generate 6-preset comparison contact sheet
python3 "$ENG/scripts/grade.py" preview --input "$W/raw/<clip>.mp4" --out "$W/grade-preview.jpg" --at 3.0
```

### The 6 Core Grading Presets:
| Preset | Characteristics & Look | Best For |
|---|---|---|
| **`commercial-clean`** | S-curve contrast, warm skin tone protection, +12% vibrance, lifted blacks, subtle clarity. | E-commerce, fashion hauls, unboxings, lifestyle reels. |
| **`cinematic-warm`** | Golden highlights (+300K), rich film contrast, subtle cyan shadow tint, organic depth. | Storytelling, founder journeys, high-production documentaries. |
| **`modern-tech`** | Clean 5600K neutral daylight, deep blacks, high clarity, vivid saturated accents. | SaaS product tours, coding, AI reviews, electronics. |
| **`moody-film`** | Analog film print curve, softened highlights, lifted deep blacks, warm shadows, fine 35mm grain. | Aesthetic vlogs, cinematic mood pieces, moody commentary. |
| **`vibrant-pop`** | High-energy social feed look, rich color saturation, dynamic contrast punch, warm skin tones. | High-tempo entertainment, street interviews, viral TikToks. |
| **`neutral-correct`** | Corrects green/yellow phone sensor cast, normalizes exposure and natural white balance. | Corporate interviews, medical, educational lectures. |

---

## 3. Formatting & Overlay Placement Rules

1. **Clean Headroom (Anti-Pattern: Forehead Clutter):**
   - **Never** place sticky headline banners or floating checklist cards over the creator's forehead/hairline (`y: 0.08 - 0.25` in portrait).
   - This looks awkward and suffocating (as seen in bad amateur edits).
2. **Safe Lower Third & Side Zones:**
   - On-screen cards, checklists, and specs must live in the lower half (`y: 0.58 - 0.75`), side panels, or dedicated cutaway scenes.
   - When lower panels appear, captions gracefully step aside to `low_y: 0.86`.
3. **Format Layout Consistency:**
   - The selected format from the 225-Style Taxonomy dictates container borders, background gradient/texture, and aspect ratio padding.

---

## 4. Gate 3: Interactive Style & Color Grade Verification

Before assembling the video or generating components, present `style.json` and the color preview to the user:
1. **Color Grade Preview:** Display `$W/grade-preview.jpg` comparing the raw footage against the proposed preset.
2. **Typography & Font Choice:** Explicitly present font family (from `DM Sans`, `Inter`, `Poppins`, `Google Sans`, `Roboto`), weight hierarchy (400 -> 700 -> 900), and verify zero text-shadow and zero blur by default (confirm if creator wishes to add custom drop shadows, glows, or blurs).
3. **Font-Coloring Hierarchy:** Inactive text color, active highlight accent, punch word badge pill background and text colors.
4. **Color Palette & Contrast:** Background, text, accent, and card glass surfaces.
5. **Motion Dynamics & Physics:** Easing curves, tilt angles, scale overshoot, and entrance springs.
6. **Captions Flow:** Natural phrase mode (`weight-shift` or `caption-highlight`), font pairing, and highlight color.

> Save the verified settings into `$W/style.json` and ensure all downstream components reference these exact tokens. Review with user again at Gate 5 before rendering.
