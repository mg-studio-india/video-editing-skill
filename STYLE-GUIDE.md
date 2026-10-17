# Master Style & Format Guide

This guide establishes the visual, spatial, and motion standards for the video editing system. It supports the full 225-Style Taxonomy (`video-editing-styles-master.md`), adapting dynamically to each project's context rather than imposing a single rigid layout.

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
| **Primary Display & Punch** | `Poppins Black (900)` or `Anton` | All-Caps, punch words 1.35x–1.5x |
| **Accent / Elegance** | `Syne Bold (800)` or `Playfair Bold Italic` | For hook keywords, topic tags |
| **Supporting / Body / Captions** | `Inter Bold (700)` or `Poppins Medium (500)` | Clean legibility, high contrast |
| **Hindi / Devanagari** | `Noto Sans Devanagari` | Local font file, rendered automatically |

---

## 4. Captions (Natural Flowing Cadence)

| Parameter | Standard | Rule |
|---|---|---|
| **Phrase Flow** | Natural syntactic phrases (4 to 6 words, 26 to 34 characters) | Phrased as spoken, not choppy stubs |
| **Zero Orphan Words** | **Strictly prohibited** | Single words (like "ya", "so") are merged into adjacent clauses |
| **Flow Mode** | `phrase` / `flow` (default) or `karaoke` | Phrase fades and settles; active word highlights smoothly |
| **Placement** | Vertical center at `0.65 – 0.68` of frame height | Below face (eye-line at 0.38), above platform interaction bar |
| **Step-Aside** | Drops to `0.84 – 0.86` during active lower-third panels | Never collides with graphics |
| **Case** | As spoken or upper based on format | Conversational and natural |

---

## 5. Layout, Overlays & Headroom Rules

| Element | Placement | Guardrails |
|---|---|---|
| **Headroom Space** | Top `0.0 – 0.35` | **Strict Clean Headroom Rule:** Never place floating checklist pills or sticky headline bands over the speaker's forehead/hairline. |
| **Lower Third Cards** | `y: 0.58 – 0.75` | Sits comfortably in lower third; staggered entrances (`0.08s delay`). |
| **Split-Screen Seams** | Center divider (44% top / 56% bottom) | 2–3px glowing or charcoal seam. |
| **Paper Drawers** | Slides in from side/bottom (`y: 0.60 – 0.75`) | Max 12 words, dismisses smoothly. |
| **Platform Safe Zones** | Top 180px, bottom 320px, sides 80px | Keep free of critical copy to prevent platform UI overlap. |

---

## 6. Motion Graphics & Dynamics (HyperFrames Catalog-First)

| Element | Timing | Physics & Easing |
|---|---|---|
| **Default Edit** | Hard cuts snapped to speech margins (100–150ms safety padding) | 0 clipped syllables |
| **Lower-Third / Card Entrance** | 0.24s – 0.32s | `power3.out`, spring settling from `y: 35px` |
| **Card Stagger Delay** | 0.08s (80ms) per item | Decelerating cascade inertia |
| **Punch-Word Scale Pop** | 0.16s | Soft pop (`scale: 0.90 -> 1.06 -> 1.00`), `back.out(1.3)` |
| **Camera Punch-In** | 0.12s on syllable onset | 1.08x – 1.12x scale switch, 0 float |
| **Optical Transition** | 2 frames white peak, 0.18s decay | `flash-through-white` or light leak on topic shifts |
