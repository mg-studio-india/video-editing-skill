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
| **Clean Authority Talking-Head** | Full-bleed creator footage (resolution probed dynamically from raw video), subtle cinematic grade, dynamic lower-third tags. | Headroom kept clean of clutter. Captions positioned dynamically below the speaker's detected chin line. |
| **Stacked Split-Screen** | Split seam dynamically calculated to frame speaker head/torso comfortably while giving demo/b-roll optimal area. 2–3px clean divider seam. | Speaker pane centered on detected face. Demo pane houses product walkthrough or try-on visuals. |
| **Framed Branded Container** | Creator footage inside rounded container floating over textured or animated branded backdrop. | Proportional margins (~4–6% of canvas width). Side progress rail or adaptive lower card drawer. |
| **Picture-in-Picture (PiP)** | Full-frame b-roll/screen recording with presenter facecam squircle in corner. | Inset window dynamically placed to dodge active UI regions in the background recording. |
| **Step-by-Step Breakdown** | Full-bleed footage with animated chapter cards entering in clear visual zones, accompanied by an animated progress counter. | Captions dynamically shift to clear active graphic cards. No cards on speaker's forehead. |

---

## 2. Dynamic Headroom & Spatial Guardrails

1. **Strict Clean Headroom Rule:**
   - **Never** place headline bars, floating checklist pills, or topic badges directly over the creator's forehead, hair, or ceiling space.
   - Plastering checklist cards in the top air (as seen in awkward amateur videos) creates visual claustrophobia.
2. **Dedicated Graphic Zones:**
   - On-screen cards, list items, specs, and badges are placed dynamically in the lower visual region, side rails, or dedicated full cutaways.
3. **Proportional Platform Safe Margins (Resolution-Agnostic):**
   - Safe margins scale proportionally with probed canvas dimensions (`W` x `H`):
     - **Top Margin (~9.4% of H):** Clears platform search, sound bar, and camera cutout.
     - **Bottom Margin (~16.5% of H):** Reserved for platform interaction bar, description drawer, and captions.
     - **Side Margin (~7.5% of W):** Safe distance from right-hand engagement buttons (like, comment, bookmark, share).
   - This ensures safe zones remain mathematically exact whether editing 4K (`2160x3840`), Full HD (`1080x1920`), horizontal, or square videos.

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
