---
name: video-pipeline
description: Runs the professional video editing system with step-based user interaction. Owns project state, interactive verification gates, HyperFrames catalog-first priority, studio-grade audio, kinetic multi-font captions, and automated lifecycle temp cleanup.
---

# Video Pipeline (Production-Ready)

Orchestrates the complete professional editing workflow. Transforms raw creator footage into high-retention, studio-grade videos (Reels, Shorts, YouTube) through a **step-based interactive workflow** where the user verifies and approves creative decisions before combining everything into the final deliverable.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## Core Principles

1. **Context-Driven Format Selection (No Blanket General Video Route):** Never assume a single generic video editing style. After transcribing the footage, analyze the subject matter, context, and creator intent, present 3–4 tailored formats from the 225-Style Taxonomy (`video-editing-styles-master.md`), and ask the user to pick their desired format.
2. **Interactive Pre-Storyboarding Discussion (Gate 0.5):** Every critical dimension (visuals, cuts, pacing, effects, references, b-roll, generated images/clips, HyperFrames/Remotion, color grading, and caption flow) MUST be discussed and aligned with the user *before* drafting the narrative storyboard.
3. **Strict Adherence to User Inputs in `/raw`:** User inputs reside in the project's root folder (`videos/<project-id>/` or `<project-id>/`), specifically inside `/raw`. Even if the user mentions other folders or files, all editing skills MUST strictly adhere to sourcing raw footage and assets from this `/raw` directory. Proactively suggest additional b-roll recording if visual gaps exist.
4. **No Mandatory Top Overlays or Awkward Ceilings:** Floating words, top banners, and checklist pill stacks must NEVER be plastered by default above or over the creator's forehead/hairline. Presence of overlays is strictly contextual; when used, position them in safe zones (lower thirds, side panels, or dedicated cutaways).
5. **Dynamic Captions & Framing (No Hardcoded Restrictions):** Caption placement, font sizing, and phrase grouping are calculated dynamically from raw video frames and transcript pacing. The vertical position is derived dynamically from the speaker's detected chin line and framing (with zero arbitrary height clamping). Typography size scales responsively with video resolution (`W` x `H`), speech velocity (WPM), and line width. Phrase grouping adapts dynamically to acoustic breath pauses and natural cadence rather than fixed word counts. Orphan single-word stubs are strictly merged away.
6. **Cinematic Color Grading Engine:** Raw mobile or camera footage must never remain dull or un-graded. Use `grade.py` to preview and apply calibrated color grading profiles (`commercial-clean`, `cinematic-warm`, `modern-tech`, `moody-film`, `vibrant-pop`, `neutral-correct`) with side-by-side preview sheets for user verification.
7. **HyperFrames Catalog First & CLI Architecture:** Search and install verified components from the 450+ component HyperFrames catalog (`npx hyperframes catalog --query ...` and `npx hyperframes add <component>`). Store all composition files inside the dedicated `/hyperframes/` directory (`hyperframes/index.html`, `hyperframes/compositions/`), keeping everything 100% editable via CLI tools without requiring the desktop GUI app. Author seek-safe GSAP motion graphics adhering to physical spring dynamics.
8. **Storyboarding BEFORE Cutting:** Never cut footage blindly based on raw silences. The creative narrative, hook angle, visual beats, and scene breakdown are planned and verified with the user *before* curating the flat cut.
9. **Studio-Grade Voice & Sound:** Dialogue isolation, surgical EQ, transparent multiband de-essing, broadcast leveling (-14 LUFS), and complete stripping of background chatter.
10. **Lifecycle Cleanup & Version-Controlled Renders:** All final deliveries are saved with version control in `/processed` (`<project-id>-v1.mp4`, etc.). Transient audio stems, chunks, auto-editor dumps, and un-mastered raw renders are purged automatically via `clean-temp.py`.
11. **Strict Anti-Hardcoding & Dynamic Calculation Contract:** All values across every skill in this pipeline must be grounded in real measurements, live internet searches, parsed assets, or explicit user intent. Never hardcode fake URLs, fabricated view counts, placeholder metrics, or arbitrary fallback hexes. All canvas dimensions, camera origins, safe zones, and caption layout metrics must be calculated dynamically from raw video frames and transcript pacing.

---

## Strict Anti-Hardcoding & Zero-Hallucination Grounding Contract

Every skill in the `video-editor-skills` ecosystem adheres to this universal contract:
1. **Zero Placeholder URLs & Data:** Never generate or commit placeholder links (`example.com`, fake YouTube/Instagram links, dummy citations). Any URL present in project files (`research.json`, `plan.md`, `style.json`) must be a live, verified URL fetched during the active session. If an item has not been researched yet, it must remain `null` or `[]`.
2. **Measured & Derived Visual Tokens:** Colors, font weights, and layout dimensions must never be arbitrary hardcoded guesses. Brand colors must be dynamically extracted from real logo vector files (`extract_colors_from_svg`) or measured footage frames (`palette.py`).
3. **No Fabricated Benchmarks or Performance Claims:** Reference view counts, creator handles, and viral retention stats must be real observed numbers from platform searches. Never invent metrics or estimates.
4. **Dynamic Entity & Category Intelligence:** No fixed hardcoded dictionaries for tools or genres. All entities, jargon, and topics must be parsed dynamically from the creator's transcript or input brief.
5. **Context-Driven Physics & Formats:** Do not copy-paste a single hardcoded layout across projects. Select styles dynamically from `video-editing-styles-master.md` matching the specific category and creator footage.
6. **Dynamic Geometry & Layout from Raw Video Frames & Transcript:** Never impose hardcoded pixel sizes, rigid aspect ratios, resolution assumptions, or restricted caption coordinates. Canvas dimensions, camera transform origins, speaker clearance zones, speech tempo (WPM), cut padding, and caption typography scale must all be dynamically measured and calculated directly from raw video footage frames and the audio transcript.

---

## Step-Based Workflow & Verification Gates

| Step | Phase | Action | User Verification Gate |
|---|---|---|---|
| **1** | `video-watch` & `video-audio` (Clean) | Deep voice isolation, 80Hz rumble cut, room noise & background dialogue stripping on `$W/raw/`. | Audio clarity verified; silence between dialogue confirmed. |
| **1.2** | `video-transcribe` & Asset Inventory | Transcribe audio, audit `$W/raw/` for all user-provided clips/assets, and identify narrative gaps. | Transcript accuracy confirmed; inventory of available vs missing assets established. |
| **1.4** | Context Classification & Format Selection | Categorize context from transcription; propose 3–4 tailored formats from 225-Style Taxonomy (`video-editing-styles-master.md`). | **Format Gate:** User selects the overarching visual format and layout for their video (no general video assumptions). |
| **1.6** | `video-researcher` | Research topic on internet, extract live benchmark videos, resolve/generate crisp vector logos (`research.json` & `research.md`). | **Gate 0 (Research & References):** User verifies facts, logos, and approved reference direction. |
| **1.8** | Pre-Storyboarding Collaborative Alignment | Discuss all creative & technical dimensions: visuals, cuts, pacing, transitions, b-roll, generated assets, color grade, and caption styling. | **Gate 0.5 (Creative Alignment):** User aligns on visuals, pacing, b-roll decisions (or decides to record additional footage). |
| **2** | `video-plan-storyboard` | Construct **Narrative Storyboard** anchored to alignment decisions (Hook 0-3s, retention loops, beats, catalog components). | **Gate 1 (Story & Hook):** User reviews and approves the hook angle, visual narrative, and scene order. |
| **3** | `video-cut-audit` & `grade.py preview` | Precision paper cut anchored to approved storyboard (snapped frame edges, dynamic speech safety margins); preview color grading sheet. | **Gate 2 (Cut & Color Grade):** User approves kept/dropped takes, target pacing, and selects preferred color grade preset. |
| **4** | `video-style` | Select brand color palette, display font pairings, and contrast themes informed by research and format choice. | **Gate 3 (Theme & Styling):** User verifies mood, colors, and typography choices. |
| **5** | `video-captions` | Author natural flowing multi-font captions (4–6 words per phrase, zero orphan words, smooth word highlight). | **Gate 4 (Caption Sample):** User inspects visual sample of caption flow & hierarchy before batch generation. |
| **6** | `video-format` & `video-motion-graphics` | Query catalog (`npx hyperframes catalog`), install registry blocks into `$W/hyperframes/`, wire layout into `hyperframes/index.html`. | Checked via `npx hyperframes lint "$W/hyperframes"` & `check` (0 errors). |
| **7** | `video-sound-design` & `video-take-geometry` | Sync sound palette / catalog SFX cues (whooshes, pops, shutters), camera punch-ins, and ducked background music (-18dB). | Timing & sound alignment verified against visual beats. |
| **8** | `video-render` & `video-audio` (Master) | Render composition from `$W/hyperframes`, apply BT.709 color tags, master audio (-14 LUFS, -1.0 dBTP ceiling), save versioned master to `$W/processed/<project>-v<N>.mp4`. | Frame contact sheet and structural checks validated. |
| **9** | `video-review-gate` & `clean-temp` | Generate review, verify CLI accessibility, and automatically clear scratch files and temporary review reports. | **Gate 5 (Final Delivery):** User receives version-controlled master in `/processed` + fully CLI-editable `/hyperframes` project. |

---

## Tool Priority

1. **HyperFrames CLI Engine (Priority 1):** Catalog blocks and components (`npx hyperframes catalog`), `add`, `check`, `snapshot`, and `render` via CLI.
2. **Local Precision Engine (Priority 2):** whisper.cpp, `grade.py` color grading, ffmpeg audio chain, `apply-cut.py`, `clean-temp.py`.
3. **Generative Assets (Priority 3):** Veo & Gemini Flash for visual inserts (cost approved).

---

## Project Hygiene & Temp File Cleanup

Run upon completing review:
```bash
python3 "$ENG/scripts/clean-temp.py" "$W" --clean-reports
```
Removes all transient audio stems (`audio-raw.wav`, `intro_dialogue_enhanced.m4a`), auto-editor cache (`speech.v1`), intermediate un-mastered video renders (`processed/*-raw.mp4`), and verification/review reports (`*-VERIFY.md`, `*-audio.json`, `*-REVIEW.md`, `*-review-sheet.png`), leaving exclusively the clean master deliverable in `processed/` and editable project assets in `hyperframes/`.
