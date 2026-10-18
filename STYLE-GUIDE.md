# Master Style & Format Guide

This guide establishes the visual, spatial, and motion standards for the video editing system. It supports the full 225-Style Taxonomy (`video-plan-storyboard/references/style-catalog.md`), adapting dynamically to each project's context rather than imposing a single rigid layout.

Fill in the **Yours** column with anything you want customized, or tell the agent: **"Here's my style guide. Update the style to match."** The agent writes it into the project's `style.json`.

---

## 1. Color Grading & Lighting

Raw footage straight from smartphones or cameras often has flat contrast or green/yellow casts. Calibrated color grading must be chosen and previewed with the user via `grade.py preview`:

| Profile | Look & Treatment | Best For |
|---|---|---|
| **Commercial Clean** | S-curve contrast, warm skin protection, +12% vibrance, lifted blacks, gentle clarity | Fashion hauls, unboxings, e-commerce, lifestyle |
| **Cinematic Warm** | Golden highlights (+300K), rich film contrast, subtle cyan shadow tint, organic depth | Storytelling, founder reels, high-production documentaries |
| **Modern Tech** | Neutral 5600K daylight, deep blacks, high clarity, vivid saturated accents | SaaS walkthroughs, coding, AI reviews, tech breakdown |
| **Moody Film** | Analog film print curve, softened highlights, lifted deep blacks, warm shadows, fine 35mm grain | Cinematic mood pieces, aesthetic vlogs, reflective commentary |
| **Vibrant Pop** | High-energy social look, rich color saturation, dynamic contrast punch, warm skin tones | High-tempo entertainment, street interviews, viral hooks |
| **Neutral Correct** | Corrects green/yellow phone sensor cast, normalizes exposure and white balance | Clean corporate interviews, medical, educational talks |

---

## 2. Colours & Surface Palette

| Role | Default | Basis | Yours |
|---|---|---|---|
| Background, split-screen gaps | Charcoal `#121214` | Default | |
| Raised panel, glass cards | Frosted dark `rgba(20, 20, 24, 0.82)` | Default | |
| Text (Primary) | Crisp warm white `#FFFFFF` | Default | |
| Text (Secondary / Inactive) | Muted white `rgba(255, 255, 255, 0.70)` | Default | |
| Accent Punch (Active words, markers) | Vibrant Gold `#FFD700` or High-Trust Emerald `#10B981` | Contextual | |
| Card borders & dividers | Subtle glow `rgba(255, 255, 255, 0.16)` | Default | |

*Rule:* Maintain natural skin tones; never apply a blanket dark grade over the speaker's face.

---

## 3. Fonts & Typography

| Use | Standard Pairings | Notes |
|---|---|---|
| **Primary Display & Punch** | `Poppins Black (900)` or `Anton` | All-Caps, punch words 1.35x-1.5x |
| **Accent / Elegance** | `Syne Bold (800)` or `Playfair Bold Italic` | For hook keywords, topic tags |
| **Supporting / Body / Captions** | `Inter Bold (700)` or `Poppins Medium (500)` | Clean legibility, high contrast |
| **Hindi / Hinglish** | `Poppins`, `Inter`, `Anton` (Roman script) | ALWAYS Roman Hinglish, never Devanagari script |

---

## 4. Captions (Dynamic Flow & Responsive Sizing)

> [!IMPORTANT]
> **Script Rule (STRICT)**: Never use Devanagari script in transcription or captions. Always render Hindi and Hinglish speech in clean Roman script (Hinglish).

| Parameter | Standard | Rule |
|---|---|---|
| **Phrase Flow** | Dynamically calculated from transcript pace (2-6 words based on speech WPM & natural breath pauses) | Phrased as spoken, adapting to speech speed |
| **Typography Size** | Calculated dynamically from video resolution (`W` x `H`), speech tempo, and phrase length | Scales up for short punch words, scales comfortably for longer clauses |
| **Zero Orphan Words** | **Strictly prohibited** | Single words (like "ya", "so") are automatically merged into adjacent clauses |
| **Flow Mode** | `phrase` / `flow` (default), `karaoke`, or `pop` | Phrase settles smoothly; active word highlights in brand accent |
| **Placement** | Calculated dynamically from raw frames (comfortably below detected chin line & shoulders) | Zero arbitrary height clamping; creators have full placement freedom |
| **Step-Aside** | Dynamically adjusts vertical coordinates to clear active lower graphics | Resumes natural placement once graphic dismisses |
| **Case** | As spoken or upper based on style | Natural human cadence |

---

## 5. Layout, Overlays & Spatial Guardrails

| Element | Placement | Guardrails |
|---|---|---|
| **Headroom Space** | Upper visual area above speaker | **Strict Clean Headroom Rule:** Never place floating checklist pills or sticky headline bands over the speaker's forehead or hair. |
| **Lower Third Cards** | Clear visual zones outside speaker bounding box | Dynamically calculated safe regions; staggered entrances (`0.08s delay`). |
| **Split-Screen Seams** | Dynamically calculated divider seam | Split ratio derived dynamically from speaker bounding box vs demo content. |
| **Paper Drawers** | Lower or side visual clearance zones | Clean entry, max 12 words, dismisses smoothly. |
| **Platform Safe Zones** | Proportional to canvas dimensions (top ~9.4%, bottom ~16.5%, sides ~7.5%) | Mathematically exact across 1080p, 4K, horizontal, or square formats. |

---

## 6. Motion Graphics & Dynamics (HyperFrames Catalog-First)

| Element | Timing | Physics & Easing |
|---|---|---|
| **Default Edit** | Hard cuts snapped to speech margins (100-150ms safety padding) | 0 clipped syllables |
| **Lower-Third / Card Entrance** | 0.24s - 0.32s | `power3.out`, spring settling from `y: 35px` |
| **Card Stagger Delay** | 0.08s (80ms) per item | Decelerating cascade inertia |
| **Punch-Word Scale Pop** | 0.16s | Soft pop (`scale: 0.90 -> 1.06 -> 1.00`), `back.out(1.3)` |
| **Camera Punch-In** | 0.12s on syllable onset | 1.08x - 1.12x scale switch, 0 float |
| **Optical Transition** | 2 frames white peak, 0.18s decay | `flash-through-white` or light leak on topic shifts |
