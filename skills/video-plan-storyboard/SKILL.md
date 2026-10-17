---
name: video-plan-storyboard
description: Plans the narrative, creative hook, visual storyboard, video effects, motion dynamics/physics, typography, and color grading BEFORE making cuts or assembling the video. Owns Gate 1.
---

# Plan & Storyboard (Pre-Cut Creative & Physics Architecture)

Professional videos succeed or fail in the storyboard. **Storyboarding must happen BEFORE cutting raw footage or generating edits.** Cutting without a storyboard results in disjointed, mechanical clips that lack retention, context, and emotional pull.

Before writing a single beat of the storyboard, the editor MUST conduct an interactive pre-storyboarding alignment with the user (**Gate 0.5**). Never assume a generic video format or force a cookie-cutter template.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## 1. Mandatory Gate 0.5: Pre-Storyboarding Collaborative Alignment

Before generating `plan.md` or `storyboard.plan.json`, the editor MUST discuss the following key dimensions with the user:

1. **Context-Driven Video Format & Composition:**
   - Review the transcription context and propose 3–4 tailored formats from the 225-Style Taxonomy (`video-editing-styles-master.md`), e.g.:
     - *Clean Authority Talking-Head:* Framed presenter, subtle cinematic grade, clean lower-third name/topic tag, flowing captions. Zero clutter over the head.
     - *Stacked Split-Screen:* 44% presenter top, 56% demo/b-roll bottom, branded divider.
     - *Fast-Paced High-Retention Reel:* 1.4s cuts, camera punches, dynamic HyperFrames motion graphics, SFX accents.
     - *Structured Step-by-Step Breakdown:* Lower-third chapter cards, animated step markers, clean pacing.
   - **Ask the user to confirm their preferred format.** Never default to "general video editing".
2. **Visual Direction & Overlay Rules (No Cluttered Forehead Overlays):**
   - **Strict Rule:** Never place persistent top headline bands or floating checklist card pills over the creator's forehead or hairline. Floating boxes pinned to the ceiling look amateur and awkward.
   - Overlays (cards, lower thirds, callouts) must be contextual and positioned in lower safe zones (`y: 0.58 – 0.75`), side panels, or dedicated cutaways.
3. **Cuts & Pacing:**
   - Discuss cut rhythm (fast retention cuts 1.2–1.8s vs relaxed conversational pauses 2.5–4.0s).
   - Identify retakes, stumbles, and tangent lines to cut or keep.
4. **Effects & Optical Transitions:**
   - Agree on transition styles: hard cuts, light leaks, white flashes, film grain, or camera punches.
5. **References & Inspirations:**
   - Incorporate reference reels from `references/` or specific creator benchmarks from Gate 0 (`research.md`).
6. **Input Folder Inventory & Strict Raw Ingestion:**
   - **Audit the raw input folder:** Inspect `videos/<project>/raw/` and list every provided file (face camera, screen recordings, b-roll, audio, photos).
   - **Strict Adherence Boundary:** All user raw inputs must be sourced exclusively from `videos/<project>/raw/`. If the user mentions other folders or external files, only assets located within `raw/` are ingested and processed. External mentions are treated as advisory context only.
   - **Suggest recording more content:** If the speaker mentions a product, screen demo, website, or action that lacks footage, actively suggest:
     > *"You discuss [X] at [timestamp]. We don't have b-roll for it in the raw input folder. Would you like to record a quick 5–10 second b-roll / screen capture of [X] and drop it into raw/? It will make this moment significantly more compelling! Otherwise, we can design an animated graphic card or generate an image."*
7. **Generative Assets vs HyperFrames Animations:**
   - Discuss whether AI stills (Gemini Flash), AI video inserts (Veo), or HyperFrames/Remotion programmatic animations are needed.
8. **Color Grading Intent & Preview:**
   - Run `python3 "$ENG/scripts/grade.py" preview --input "$W/raw/<clip>" --out "$W/grade-preview.jpg"` to generate a side-by-side comparison sheet.
   - Present the 6 curated presets (`commercial-clean`, `cinematic-warm`, `modern-tech`, `moody-film`, `vibrant-pop`, `neutral-correct`) and agree on the look.
9. **Natural Caption Flow & Hierarchy:**
   - Confirm caption style: natural spoken phrases (4–6 words per phrase, zero orphan single words like "ya"), smooth phrase fade/karaoke, and accent highlight color.

---

## 2. Complete Storyboard Matrix (Per-Beat Specification)

Every beat in `plan.md` and `storyboard.plan.json` must define 5 architectural pillars:

### A. Video Effects (VFX) & Transitions
Specify the optical treatment for transitions and overlays:
- **Optical Flashes:** `flash-through-white` (hold 2 frames, decay 0.18s), `light-leak-warm`, `lens-flare-anamorphic`.
- **Atmospheric FX:** Film grain overlay (8-12% opacity, fine 35mm), vignette edge falloff (15-20% black curve).
- **Surface & Texture:** Glassmorphism frosted backdrops (`backdrop-filter: blur(16px)`, border: 1.5px solid rgba(255,255,255,0.15)), paper tear edges, glow drop-shadows.

### B. Color Grading & Lighting Intent
Set the mood and color palette per scene:
- **Grade Style:** Calibrated preset from `grade.py` (e.g. `commercial-clean`, `cinematic-warm`, `modern-tech`).
- **Contrast & Exposure:** Contrast ratio 1.15, highlights restrained, warm skin-tone protection, shadows crushed for depth.

### C. Exact Typography & Font Hierarchy
No generic fonts. Explicitly specify font families, weights, sizing, and stroke parameters:
- **Punch Font (Power Keywords):** `Poppins Black (900)` or `Anton Display`, All-Caps, size 72–84px, letter-spacing -0.02em, text-stroke: 3px rgba(0,0,0,0.92).
- **Display Accent Font (Curiosity/Elegance):** `Syne Bold (800)` or `Playfair Bold Italic (700)`.
- **Supporting / Body Font:** `Inter Bold (700)` or `Poppins Medium (500)`, size 48–56px.
- **Micro / Subtext:** Size 32–38px, uppercase, letter-spacing +0.05em, opacity 0.85.

### D. Kinetics, Dynamics & Motion Physics
Specify exact movement curves, physics parameters, and timing behaviors:
- **Physics Engine Standard:** Damped harmonic motion (`damping: 14 – 18`, `stiffness: 160 – 200`, `mass: 1.0`).
- **Easing Curve:** `power3.out` for snappy entrances, `back.out(1.3)` for subtle scale-overshoot, `power2.in` for fast exits. Never use cartoonish high-bounce curves.
- **Scale Dynamics:** Micro scale pop (`scale: 0.90` -> `1.06` -> `1.00` in 0.18s) with physical momentum.
- **Tilt Physics:** Micro-rotation (`-2.0deg` to `+2.0deg`) on entrance settling to `0deg`.
- **Stagger Physics:** Multi-item cards enter with an 80ms cascade delay (`stagger: 0.08s`), moving upward with decelerating inertia (`y: 35px` -> `0px`).
- **Camera Punch Dynamics:** 1.08x – 1.12x scale zoom snapped in 0.12s on key trigger syllables.

### E. HyperFrames Catalog Foundation
- Query and install verified blocks: `npx hyperframes catalog --query "<treatment>"` and `npx hyperframes add <component>`.

---

## 3. Storyboard Spec Schema (`storyboard.plan.json`)

```json
{
  "id": "reel-plan",
  "program": "short",
  "target_duration": 38.5,
  "style": {
    "color_grade": {
      "preset": "commercial-clean",
      "contrast": 1.12,
      "saturation": 1.12,
      "color_temperature": "6200K",
      "skin_tone_protection": true
    },
    "typography": {
      "primary_punch": "Poppins-Black (900)",
      "accent_display": "Syne-ExtraBold (800)",
      "body_text": "Poppins-Bold (700)",
      "stroke": "3px rgba(0,0,0,0.92)"
    },
    "motion_physics": {
      "entrance_ease": "power3.out",
      "pop_curve": "back.out(1.3)",
      "damping": 16,
      "stiffness": 180,
      "tilt_degrees": -1.5
    }
  },
  "beats": [
    {
      "id": "beat-01-hook",
      "time_range": "0.0s - 3.2s",
      "anchor": "first key claim",
      "visual_action": "Creator makes bold statement to camera; snap punch-in 1.10x",
      "vfx": "transitions-light flash into scene; subtle 8% 35mm grain",
      "catalog_block": "lt-minimal-glow",
      "typography": "Poppins-Black 900 · 76px · #ffffff with #ffd700 punch words",
      "physics": "Fade and settle y: 20px -> 0px, power3.out, 0.24s duration",
      "sfx": "whoosh-fast"
    },
    {
      "id": "beat-02-cards",
      "time_range": "19.1s - 25.1s",
      "anchor": "three steps",
      "visual_action": "Creator explains core breakdown; lower-third card reveals",
      "vfx": "frosted glass backdrop; 1.5px subtle border",
      "catalog_block": "mk-specs-list",
      "y": 0.62,
      "typography": "Header: Syne-ExtraBold 40px #ffd700; Items: Poppins-Bold 48px #ffffff",
      "physics": "Card stagger 0.08s, spring slide-up from y: 35px, back.out(1.3), settling in 0.32s",
      "sfx": "card-pop"
    }
  ]
}
```

---

## 4. Gate 1: Interactive Storyboard & Technical Approval

Generate `plan.md` containing the complete narrative, visual matrix, typography pairings, color grading profile, and physics dynamics.

Present to the user:
1. **Narrative & Hook Strategy**
2. **Visual & Layout Breakdown (VFX, transitions, catalog blocks, clean headroom)**
3. **Typography & Font Choice (Fonts, weights, sizing, letter-spacing)**
4. **Color Grading & Mood (Selected grade.py preset, contrast, palette)**
5. **Kinetics & Physics (Scale pops, spring curves, camera punch-ins)**
6. **Asset Checklist (Confirmed b-roll, generated assets, or user-recorded additions)**

> **User Prompt Rule:** Ask for feedback and approval. Never cut the raw video or build components until the user approves or refines the storyboard.
