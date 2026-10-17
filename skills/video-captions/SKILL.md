---
name: video-captions
description: Generates high-retention kinetic captions with typographical hierarchy (different fonts, sizes, weights, rotation, and badge pills) timed to the final cut. Ensures captions look professional and catch attention without obstructing the creator's face.
---

# Captions (Natural Flow & Kinetic Typographical Hierarchy)

Captions succeed when they read like natural human speech while commanding visual focus. Choppy single-word fragments (like an isolated "ya") or chaotic word-by-word bouncing distract viewers and look amateur. Professional reels utilize **natural phrase grouping, conversational cadence, zero orphan words, and smooth highlighting**.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## 1. Natural Spoken Phrase Flow Rules

1. **Conversational Phrase Grouping:**
   - Group words into syntactic phrase chunks (typically **4 to 6 words**, **26 to 34 characters**).
   - Pause threshold is set to **0.35s – 0.40s** (never 0.15s, which chops ordinary conversational breaths into fragmented stubs).
2. **Zero Orphan Single Words (Strict Guardrail):**
   - Single isolated words (such as "ya", "so", "and", "the") must **never** be displayed alone as a lone group on screen.
   - The engine automatically merges 1-word stubs into their adjacent clause, ensuring complete, readable phrases.
3. **Smooth Flow Modes (`captions.py`):**
   - **`phrase` / `flow` (Default Standard):** The complete natural phrase enters smoothly (`opacity: 0 -> 1`, `y: 8px -> 0px` in 0.18s). As the speaker speaks each word, the active word highlights with accent color or a badge pill without jarring text reflow.
   - **`karaoke`:** Entire phrase remains anchored on screen while a fluid color sweep highlights words in real time.
   - **`pop` (Softened):** Subtle micro-pop (`scale: 0.90 -> 1.00`) on emphasized punch words, avoiding extreme rubber-band bouncing (`back.out(2)`).

---

## 2. Typographical Scale & Weight Hierarchy

Every caption phrase is divided into distinct visual layers:

| Layer | Relative Size | Font Weight & Style | Purpose | Example |
|---|---|---|---|---|
| **Punch / Power Word** | **1.35x – 1.60x** | ExtraBold / Black (900), All-Caps, Accent Color or Badge Pill | Commands visual focus, drives narrative impact | `UNDER ₹400`, `INSANE`, `SHOCKING` |
| **Action / Subject** | **1.00x – 1.15x** | Bold (700), Crisp Sans / Display | Carries the core clause | `ordered these dresses` |
| **Connectors & Prepositions** | **0.80x – 0.90x** | Medium (500), Muted White / 80% Opacity | De-emphasized to prevent visual clutter | `from`, `and`, `to the` |

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

## 4. Placement & Safe-Zone Rules

- **Vertical Centre:** Position at `0.65 – 0.68` of frame height in 9:16 portrait.
  - Sits comfortably below the creator's face (which rests at eye-line ~0.38) and safely above platform UI drawers (TikTok/Instagram engagement bar sits below 0.82).
- **Step-Aside for Lower Panels:** When a card list or drawer is displayed in the lower half, captions temporarily transition to the low rail (`0.84 – 0.86`).
- **Never Cover the Face or Forehead:** Captions must never float above `0.60` height in standard vertical portrait shots.

---

## 5. Interactive User Verification Gate (Gate 4)

Before batch-generating captions across the entire video:
1. Present a **live visual sample phrase** (e.g., a 5-word sentence) demonstrating:
   - Primary and punch font pairings
   - Color hierarchy (inactive text, active highlight, punch badge)
   - Flow mode (`phrase`, `karaoke`, or `pop`)
2. Ask for user confirmation:
   > *"Here is how your captions will flow naturally across the video: [sample preview]. Does this style and pace work for you, or would you prefer a different highlight color/font pairing?"*
