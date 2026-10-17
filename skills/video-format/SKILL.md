---
name: video-format
description: Lays out visual scenes with HyperFrames Catalog as the first-class foundation. Replaces ad-hoc custom containers with polished registry blocks, wires layouts, and keeps compositions fully editable via CLI tools and modular sub-compositions.
---

# Format & Layout (HyperFrames Catalog-First & Composition Architecture)

Never write arbitrary custom CSS boxes or amateur developer containers. **The HyperFrames Catalog (~450 production-grade blocks and components) combined with the 225-Style Taxonomy (`video-editing-styles-master.md`) forms the first-class spatial foundation for all on-screen graphics.**

Formatting is not just dumping random cards onto raw footage. It is the deliberate spatial architecture of canvas framing, background containers, typography hierarchies, safe-zone margins, and motion graphics.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## 1. Context-Driven Layout Formats (No Generic Defaults)

The layout must match the video format selected by the user at Gate 0.5:

| Layout Format | Composition Architecture | Safe Zones & Placement |
|---|---|---|
| **Clean Authority Talking-Head** | Full-bleed creator footage (`1080x1920`), subtle cinematic grade, clean lower-third name/topic tags (`y: 0.70`). | Headroom kept completely clean (zero text or boxes above the forehead). Captions at `0.66`. |
| **Stacked Split-Screen** | Top 44% creator talking-head / bottom 56% demo, product try-on, or b-roll. 2–3px glowing or charcoal divider seam. | Top pane center face at 22% frame height. Bottom pane houses product specs or live demo. |
| **Framed Branded Container** | Creator footage inside rounded card container (`radius: 24px`, subtle border & drop shadow) floating over a dark textured or animated branded backdrop. | Symmetrical padding (40px margins). Side progress rail or lower card drawer. |
| **Picture-in-Picture (PiP)** | Full-frame b-roll/screen capture with 32% width rounded squircle presenter facecam in top-left or bottom-right corner. | Inset window dodges active UI elements in the background recording. |
| **Step-by-Step Breakdown** | Full-bleed footage with animated chapter cards entering in lower third (`y: 0.58 – 0.72`), accompanied by an animated progress counter. | Captions drop to `0.86` while cards are active. No cards on forehead. |

---

## 2. Headroom & Spatial Guardrails (Anti-Clutter Floor)

1. **Strict Clean Headroom Rule:**
   - **Never** place headline bars, floating checklist pills, or topic badges directly over the creator's forehead, hair, or ceiling space (`y: 0.08 – 0.35` in vertical portrait).
   - Plastering checklist cards in the top air (as seen in awkward amateur videos) creates visual claustrophobia.
2. **Dedicated Graphic Zones:**
   - On-screen cards, list items, specs, and badges must be placed in the lower-third zone (`y: 0.58 – 0.75`), in side panels, or in full cutaways.
3. **Platform Safe Margins:**
   - Top 180px: clear of critical text (platform header bar & search icon).
   - Bottom 320px: reserved for captions (`0.66`) and platform interaction drawers (captions drop to `0.86` during active lower panels).
   - Sides 80px: safe margin from right-hand engagement buttons (like, comment, share).

---

## 3. Catalog First Execution Protocol

Before writing any HTML or CSS:
1. **Search the Catalog:**
   ```bash
   npx hyperframes catalog --query "<what you want to show>" --json
   ```
2. **Install the Component:**
   ```bash
   cd "$W/hyperframes" && npx hyperframes add <component-name> --no-clipboard && cd -
   ```
3. **Inspect the Component:**
   Read the installed file in `$W/hyperframes/compositions/` to discover its parameters, CSS variables, and layout contracts.
4. **Wire into Storyboard:**
   Mount as a modular sub-composition (`block`) or component snippet inside `$W/hyperframes/index.html`.

---

## 4. Catalog Mapping by Use Case

| Visual Intent | HyperFrames Catalog Query | Verified Catalog Components |
|---|---|---|
| **Clean Lower Third & Header** | `query "lower third headline banner"` | `lt-minimal-glow`, `lt-headline-banner`, `headline-ticker` |
| **Product / Feature Specs Card** | `query "product card feature showcase"` | `mk-specs-list`, `feature-pill-card`, `grid-card-assemble` |
| **Metric Badge & Stat Counter** | `query "metric badge callout pill"` | `stat-callout-counter`, `badge-pill-pill`, `counter-flip` |
| **Optical Transition & Light Leak**| `query "flash transition light leak"` | `flash-through-white`, `transitions-light`, `editorial-flash-overlay` |
| **Split-Screen & Comparison** | `query "split screen comparison"` | `comparison-split`, `before-after-wipe`, `split-tilt-cards` |
| **Paper / Texture Accents** | `query "paper rip collage texture"` | `torn-paper-rip`, `paper-collage-reveal`, `marker-checklist-card` |

---

## 5. CLI Composability & Composition Hygiene

To guarantee that the video is seamlessly composable and verifiable via CLI tools:
- **Modular Sub-compositions:** Place distinct visual treatments in `$W/hyperframes/compositions/<name>.html` rather than pasting hundreds of messy DOM nodes into one giant monolithic file.
- **Semantic Track Structure:** Use clean track indexing (`data-track-index`):
  - Track 1: Base creator video.
  - Track 10-20: Transitions & flashes.
  - Track 30-40: Catalog overlays, cards, and banners.
  - Track 50-60: Natural flowing captions rail.
  - Track 70+: SFX audio cues.
- **Relative Coordinates & Variables:** Use semantic CSS variables for fonts, primary colors, and accent colors defined in `style.json`.
- **Validation:** Always verify with `npx hyperframes lint "$W/hyperframes"` and `npx hyperframes check "$W/hyperframes"` before user handover.
