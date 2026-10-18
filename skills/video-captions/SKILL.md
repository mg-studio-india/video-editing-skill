---
name: video-captions
description: Generates high-retention kinetic captions with typographical hierarchy (different fonts, sizes, weights, rotation, and badge pills) timed to the final cut. Ensures captions look professional and catch attention without obstructing the creator's face.
---

# Captions (Natural Flow & Kinetic Typographical Hierarchy)

> **Styles:** Caption & typography styles #21-45 of the 225-style catalog: `references/styles-captions-typography.md`.

Captions succeed when they read like natural human speech while commanding visual focus. Choppy single-word fragments (like an isolated "ya") or chaotic word-by-word bouncing distract viewers and look amateur. Professional reels utilize **natural phrase grouping, conversational cadence, zero orphan words, and smooth highlighting**.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

> [!IMPORTANT]
> **Virtual Environment (STRICT)**: ALWAYS run caption tools using the project's virtual environment (`"$PROJECT/.venv/bin/python3"`). Never invoke system python.
> **Zero Devanagari Rule (STRICT)**: Captions must NEVER render in Devanagari script. All Hindi and Hinglish speech must ALWAYS be rendered in Roman Hinglish script. Standard display fonts (Poppins, Inter, Anton) are used.


---

## 1. Dynamic Spoken Phrase Flow (Transcript-Driven)

Phrase grouping is **calculated dynamically from speech velocity (WPM), acoustic breath pauses, and clause syntax** directly from the transcript:

1. **Adaptive Phrase Grouping:**
   - **Fast-Paced Hook / High-Tempo Reel (175+ WPM):** Dynamically groups **4 to 6 words** (**28 to 36 characters**) so captions maintain readability without strobe-like flickering.
   - **Conversational Tempo (135-175 WPM):** Dynamically groups **3 to 5 words** (**22 to 30 characters**).
   - **Deliberate / Punchy Delivery (<135 WPM):** Dynamically groups **2 to 4 words** (**14 to 22 characters**) for rhythmic punch.
   - **Dynamic Pause Detection:** Pause thresholds are computed from the natural pause distribution in the transcript rather than a fixed arbitrary number.
2. **Zero Orphan Single Words (Strict Guardrail):**
   - Single isolated words (such as "ya", "so", "and", "the") must **never** be displayed alone as a lone group on screen.
   - The engine automatically merges 1-word stubs into their adjacent clause, ensuring complete, readable phrases.
3. **Smooth Flow Modes (`captions.py`):**
   - **`phrase` / `flow` (Default Standard):** The complete natural phrase enters smoothly (`opacity: 0 -> 1`, `y: 8px -> 0px` in 0.18s). As the speaker speaks each word, the active word highlights with accent color or a badge pill without jarring text reflow.
   - **`karaoke`:** Entire phrase remains anchored on screen while a fluid color sweep highlights words in real time.
   - **`pop` (Softened):** Subtle micro-pop (`scale: 0.90 -> 1.00`) on emphasized punch words, avoiding extreme rubber-band bouncing (`back.out(2)`).

---

## 2. Dynamic Typographical Scale & Responsive Sizing

Caption sizing and scale hierarchy are **calculated dynamically from video dimensions, phrase character density, and speech pace with no arbitrary restrictions**:

- **Dynamic Font Size Calculation:**
  - Font size scales responsively with canvas dimensions (`W` x `H`) and line character length:
    - Punchy, short 2-3 word phrases scale up dynamically to fill the visual focal area with high impact.
    - Longer conversational phrases scale dynamically so the clause breathes comfortably on a single line without awkward line breaks.
  - Creators and styles have **complete freedom over font size and weight hierarchy**—no rigid multiplier clamps (e.g. 1.35x vs 1.60x) are enforced by the engine.
- **Visual Weight Hierarchy:**
  - **Punch / Power Words:** Emphasized via heavier font weight (Bold/Black 900), brand accent colors, or dynamic background pill badges.
  - **Body / Action Clauses:** Clean sans/display font carrying narrative clarity.
  - **Connectors & Prepositions:** Muted opacity (~70-80%) to maintain clear visual hierarchy without distraction.

---

## 3. Kinetic Caption Presets

1. **Natural Phrase Glow (Default):**
   - Multi-word phrase fades in smoothly, secondary words at 70% opacity white, active word highlights in vibrant brand accent with soft glow shadow (`text-shadow: 0 4px 18px rgba(0,0,0,0.6)`).
2. **Hormozi Pop & Badge:**
   - Punch words wrapped in a high-contrast pill backdrop (`background: #ffd700; color: #000; border-radius: 12px; transform: rotate(-2deg);`).
   - Micro scale-pop entrance: scales from `0.90` to `1.06` to `1.00` in 0.16s.
3. **Editorial Dual-Font:**
   - Pairs a modern grotesque sans (e.g. Poppins / Inter) with an expressive display accent or italic serif for punch words.
4. **Clean Minimalist:**
   - Clean heavy sans with a subtle animated highlight bar underneath the active keyword.

---

## 4. Dynamic Placement & Frame-Aware Positioning

Caption positioning is **calculated dynamically from raw video frames and speaker geometry with zero arbitrary height restrictions**:

- **Frame-Aware Vertical Positioning:**
  - In talking-head shots, caption rail height `y` is calculated dynamically from the speaker's detected face and chin position:
    `y = min(0.88, max(0.40, chin_y + clearance_margin))`
    Adapts automatically whether the speaker is framed in tight close-up, medium shot, wide shot, or seated off-center.
  - In B-roll, screencasts, or split-screen shots without a talking head, `y` dynamically centers in the visual clearance zone or lower safe region.
  - **No Height Clamping:** Creators have total artistic freedom to position captions anywhere (top, center, lower, or floating dynamically alongside the speaker).
- **Dynamic Step-Aside for Graphic Panels:**
  - When lower-third cards, specs drawers, or checklist pills appear, captions dynamically shift their vertical coordinates based on the bounding box of the active graphics, resuming their natural position once the panel dismisses.
- **Visual Clearance:**
  - Captions dynamically dodge speaker facial features and platform interaction drawers.

---

---

## 5. Kinetic Caption Standard (`weight-shift` or `caption-highlight` with Punch Words)

The default caption style is **strictly either `weight-shift` or `caption-highlight` with punch word(s) emphasis**:

| Video Pace & Energy | Default Kinetic Style | Typographical & Motion Behavior |
|---|---|---|
| **Conversational / Authority Pace (<170 WPM)** | **`weight-shift` + Punch Word Pop** | Inactive words remain clean at font-weight 400; as the speaker speaks each word, the active word dynamically shifts to **Black 900**, with key claims/numbers receiving a spring scale pop (`0.90 -> 1.06 -> 1.00`). |
| **High Energy / Rapid Hook (170+ WPM)** | **`caption-highlight` + Badged Pills** | Natural 4-6 word clauses; a fluid fluorescent highlight sweep glides across the active word in real time; punch words/numbers are encased in vibrant rounded pills (`#ffd700`, `#00c3ff`, `#00e676`). |
| **Docu-Style / Investigative Teardown** | **`weight-shift` (Editorial Dual-Font)** | Grotesque body text paired with expressive serif/display for power words; words dynamically scale and gain weight with zero awkward text reflow. |

The editor proactively orchestrates this standard automatically, with zero user micromanagement required.

---

## 6. Interactive User Verification Gate (Gate 5)

Before batch-generating captions across the entire video:
1. Present a **live visual sample phrase** (e.g., a 5-word sentence) demonstrating:
   - Primary and punch font pairings (e.g. Poppins Black 900 / Inter Bold)
   - Color hierarchy (inactive text, active highlight, punch badge pill)
   - Flow mode (`weight-shift` or `caption-highlight`)
2. Confirm with user before proceeding to Gate 6:
   > *"Here is how your captions will flow naturally across the video: [sample preview]. Does this weight-shift / highlight flow and pace look great, or would you like to adjust font weight or badge accents?"*
