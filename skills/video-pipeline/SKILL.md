---
name: video-pipeline
description: Runs the professional video editing system with step-based user interaction. Owns project state, interactive verification gates, HyperFrames catalog-first priority, studio-grade audio, kinetic multi-font captions, and automated lifecycle temp cleanup.
---

# Video Pipeline (Production-Ready)

> **Styles:** Pipeline architecture and the editor's style-rule checklist (from the style catalog appendix): `references/pipeline-architecture.md`.

Orchestrates the complete professional editing workflow. Transforms raw creator footage into high-retention, studio-grade videos (Reels, Shorts, YouTube) through a **step-based interactive workflow** where the user verifies and approves creative decisions before combining everything into the final deliverable.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## Core Principles

1. **Creative, Innovative & Trendy by Default (Never Static Full-Screen Talking Head):** Static full-frame talking-head videos with basic subtitles slapped on top are strictly rejected. The default editing style must be high-production, visually dynamic, and trendy (Vox / MagnatesMedia / top-tier creator caliber):
   - **Multi-Layout A-Roll Dynamism:** The editor must actively choreograph A-roll shifts across narrative beats:
     - *Full Camera:* For opening hooks, personal assertions, and emotional climaxes.
     - *Corner PiP / Floating Window:* The A-roll minimizes smoothly into a floating corner squircle/circle (clearing platform interaction zones), opening 65-75% of the canvas.
     - *Split-Screen / Stacked View:* Presenter shifts to top or side (35-45% of screen), leaving a massive dedicated graphical canvas.
     - *Speaker Cutout & Matting:* Speaker's silhouette extracted or framed over modern graphical, neutral dark (#0f172a, #111), clean white, or cinematic gradient backdrops.
   - **Creative Canvas Space Utilization:** The empty space created by A-roll minimization must actively showcase:
     - *Researcher Articles & Media:* News clippings, financial report excerpts, newspaper mastheads, and tweet/Reddit callouts with animated fluorescent marker pens sweeping across key sentences.
     - *Kinetic Data Charts & Visualizations:* Animated bar charts, line growth curves, stat comparison meters, and live metric counters timed to spoken claims.
     - *3D Objects & Depth Cards:* Isometric cards, floating device mockups, and 3D rotating graphics with natural drop shadows.
     - *Natural Physics & Springs:* Damped harmonic motion (`power3.out`, `back.out(1.4)`), physical inertia, and momentum-driven slide-ins.
2. **Kinetic Caption Standard (Weight-Shift or Caption-Highlight with Punch Words):** The default caption style is **strictly either `weight-shift` or `caption-highlight` with punch word(s) emphasis**. Inactive words remain clean while active words dynamically shift typographic weight (400 -> Black 900) or receive a fluid fluorescent highlight sweep, with critical keywords encased in high-contrast badge pills. Zero user micromanagement required.
3. **Context-Driven Dynamic Format Selection (Nothing Hardcoded):** The recommended auto-default format **strictly depends on the video context and can be ANY format** from the 225-Style Taxonomy. The engine analyzes the transcript, topic, aspect ratio, and asset inventory:
   - Technical demos / code / browser walkthroughs $\rightarrow$ `screen-plus-facecam` or `corner-pip`
   - Investigative reporting / finance / market teardowns $\rightarrow$ `split-screen` with dedicated data canvas
   - High-energy hooks / personal storytelling / viral reels $\rightarrow$ `multi-dynamic` (Hook full -> PiP/Split -> Cutout)
   - Product unboxings / hardware demos $\rightarrow$ `corner-pip`
   - Bold claims / statistics / empire breakdowns $\rightarrow$ `layered-head` (graphics behind speaker)
   - Reactions / reviews $\rightarrow$ `stacked-split`
   - Keynotes / speeches $\rightarrow$ `full-camera` with snapped camera punch-ins
4. **Specification Extraction & Interactive Missing-Step Resolution (spec-resolver.py & Gate 1):** The pipeline automatically extracts all user specifications from their prompt across 6 creative dimensions (apart from raw footage):
   - *Formats & Multi-Layout Dynamism* (Context-derived from the 225-Style Taxonomy)
   - *Sounds, SFX & Music Bed* (Curated tactile clicks, whooshes, paper tears; ducked lofi or synth bed)
   - *Caption Styles & Typography* (`weight-shift` or `caption-highlight` with punch words)
   - *Color Grading Presets & 3-Way Formula* (10 Cinema/Studio presets: Kodak Portra Warm, Hollywood Teal & Orange, Vox Documentary, Magnates Gold, Fuji Pro, Modern Tech, Moody Film, Vibrant Pop, Nordic Cold, Studio Clean Balanced)
   - *Graphics & Visual Elements* (researcher article clippings, kinetic data charts, 3D depth cards)
   - *Audio Processing & Noise Filtering* (neural DeepFilterNet3 for road/car/traffic rumble, RNNoise, auto)
    The engine audits extracted specs against master catalogs (`spec-resolver.py audit`). For any missing dimension, the agent explicitly prompts the user with choices from master data (max 10 choices), and **strictly provides an explicit option to choose automatically** (`[Recommended] Choose automatically based on video context & brand memory`). Proactively checks with the user on high-impact quality flags (`--denoise neural` active for indoor/outdoor, `--reframe yunet` active for vertical delivery, `--resolution uhd` 4K). Caption engine must be explicitly asked from the user (defaulting to weight-shift or caption-highlight with punch words, or layered-head if big figures/large backdrop text mentioned, only if auto-selected). Writes `$W/resolved-spec.json` before storyboarding.
5. **Strict Adherence to User Inputs in `/raw`:** User inputs reside in the project's root folder (`videos/<project-id>/` or `<project-id>/`), specifically inside `/raw`. Even if the user mentions other folders or files, all editing skills MUST strictly adhere to sourcing raw footage and assets from this `/raw` directory. Proactively suggest additional b-roll recording if visual gaps exist.
6. **No Mandatory Top Overlays or Awkward Ceilings:** Floating words, top banners, and checklist pill stacks must NEVER be plastered by default above or over the creator's forehead/hairline. Presence of overlays is strictly contextual; when used, position them in safe zones (lower thirds, side panels, or dedicated cutaways).
7. **Dynamic Captions & Framing (No Hardcoded Restrictions):** Caption placement, font sizing, and phrase grouping are calculated dynamically from raw video frames and transcript pacing. The vertical position is derived dynamically from the speaker's detected chin line and framing (with zero arbitrary height clamping). Typography size scales responsively with video resolution (`W` x `H`), speech velocity (WPM), and line width. Phrase grouping adapts dynamically to acoustic breath pauses and natural cadence rather than fixed word counts. Orphan single-word stubs are strictly merged away.
8. **3-Way Formula Color Grading Engine (Shadows, Midtones, Highlights, Contrast, Saturation):** Never rely on flat generic grades. Use `grade.py`'s 3-way color balance formula and 10 cinema-tested presets (Kodak Portra, Hollywood Teal/Orange, Vox Documentary, Magnates Gold, etc.) with side-by-side preview sheets for user verification.
9. **HyperFrames Catalog First & CLI Architecture:** Search and install verified components from the 450+ component HyperFrames catalog (`npx hyperframes catalog --query ...` and `npx hyperframes add <component>`). Store all composition files inside the dedicated `/hyperframes/` directory (`hyperframes/index.html`, `hyperframes/compositions/`), keeping everything 100% editable via CLI tools without requiring the desktop GUI app. Author seek-safe GSAP motion graphics adhering to physical spring dynamics.
10. **Storyboarding BEFORE Cutting:** Never cut footage blindly based on raw silences. The creative narrative, hook angle, visual beats, and scene breakdown are planned and verified with the user *before* curating the flat cut.
11. **Studio-Grade Voice & Sound:** Dialogue isolation, surgical EQ, transparent multiband de-essing, broadcast leveling (-14 LUFS), and complete stripping of background chatter and vehicle/road sounds.
12. **Lifecycle Cleanup & Version-Controlled Renders:** All final deliveries are saved with version control in `/processed` (`<project-id>-v1.mp4`, etc.). Transient audio stems, chunks, auto-editor dumps, and un-mastered raw renders are purged automatically via `clean-temp.py`.
13. **Strict Anti-Hardcoding & Dynamic Calculation Contract:** All values across every skill in this pipeline must be grounded in real measurements, live internet searches, parsed assets, or explicit user intent. Never hardcode fake URLs, fabricated view counts, placeholder metrics, or arbitrary fallback hexes. All canvas dimensions, camera origins, safe zones, and caption layout metrics must be calculated dynamically from raw video frames and transcript pacing.
14. **Project Virtual Environment Restriction (STRICT):** All pipeline scripts must strictly execute within the project virtual environment (`"$PROJECT/.venv/bin/python3"`). Never invoke system python. The engine automatically enforces `.venv` execution.
15. **Hinglish Transcription & Caption Rule (STRICT):** Never use Devanagari script in transcription or captions. All Hindi and code-switched speech must ALWAYS be transcribed and rendered in clean Roman script (Hinglish). Transcriptions and captions automatically transliterate Devanagari to Hinglish.
16. **Immutable Raw Ingest & Strict Asset Caching (STRICT):** Transcripts (`transcript.words.json`, `transcript.json`) and dialogue-isolated master audio stems (`audio-clean.wav`) represent grounded immutable facts of the raw media take. They must NEVER be repeatedly re-transcribed or re-filtered across downstream user revisions (cuts, caption restyling, graphics, color grading). All scripts (`transcribe.py`, `audio-chain.py`, `verify-words.py`) reuse existing cached outputs by default unless explicitly invoked with `--force`. `clean-temp.py` strictly protects `audio-clean.wav` and transcripts from lifecycle purging.

---

## Strict Anti-Hardcoding & Zero-Hallucination Grounding Contract

Every skill in the `video-editing-skill` ecosystem adheres to this universal contract:
1. **Zero Placeholder URLs & Data:** Never generate or commit placeholder links (`example.com`, fake YouTube/Instagram links, dummy citations). Any URL present in project files (`research.json`, `plan.md`, `style.json`) must be a live, verified URL fetched during the active session. If an item has not been researched yet, it must remain `null` or `[]`.
2. **Measured & Derived Visual Tokens:** Colors, font weights, and layout dimensions must never be arbitrary hardcoded guesses. Brand colors must be dynamically extracted from real logo vector files (`extract_colors_from_svg`) or measured footage frames (`palette.py`).
3. **No Fabricated Benchmarks or Performance Claims:** Reference view counts, creator handles, and viral retention stats must be real observed numbers from platform searches. Never invent metrics or estimates.
4. **Dynamic Entity & Category Intelligence:** No fixed hardcoded dictionaries for tools or genres. All entities, jargon, and topics must be parsed dynamically from the creator's transcript or input brief.
5. **Context-Driven Formats:** Do not copy-paste a single hardcoded layout across projects. Select styles dynamically from `video-plan-storyboard/references/style-catalog.md` matching the specific category and creator footage.
6. **Dynamic Geometry & Layout from Raw Video Frames & Transcript:** Never impose hardcoded pixel sizes, rigid aspect ratios, resolution assumptions, or restricted caption coordinates. Canvas dimensions, camera transform origins, speaker clearance zones, speech tempo (WPM), cut padding, and caption typography scale must all be dynamically measured and calculated directly from raw video footage frames and the audio transcript.

---

## Streamlined Verification Gates (Gate 1 through Gate 6)

| Gate | Phase | Action | User Verification Checkpoint |
|---|---|---|---|
| **Gate 1** | **Creative Specification & Context Audit** | Ingest persistent creator memory (`brand/MEMO.md`), parse prompt across 6 creative dimensions with `spec-resolver.py`, dynamically detect video context and recommend format, audit missing steps against master catalogs (max 10 choices), and check proactive quality flags (`--denoise neural` active for indoor/outdoor, `--reframe yunet` active for vertical delivery, `--resolution uhd` 4K). Caption engine explicitly asked from user (defaulting to weight-shift or highlight with punch words, or layered-head if big figures/large backdrop text mentioned, only if auto-selected). Writes `$W/resolved-spec.json`. | **Approved Creative Specification:** Dimensions resolved via user selection or context-derived auto-orchestration; quality flags confirmed. |
| **Gate 2** | **Ingest, Speech & Blueprint Match** | Isolate dialogue and cut 80Hz rumble on `$W/raw/`, transcribe audio with whisper.cpp, verify words with `verify-words.py` (audit misspellings & enforce Roman Hinglish), audit raw asset inventory in `$W/raw/`, and match raw take + transcript against 50 style blueprints (`match.py` $\rightarrow$ `ROADMAP.md`). | **Approved Ingest & Roadmap:** Speech transcript verified; available vs missing raw assets confirmed; style blueprint roadmap selected. |
| **Gate 3** | **Narrative Architecture & Storyboard** | Construct narrative storyboard (`storyboard.plan.json` & `plan.md`) anchored to resolved spec and blueprint: Hook 0-3s, retention loops, scene breakdown, multi-layout choreography (when A-roll shifts to split, pip, cutout), and empty canvas visual planning (researcher articles, kinetic charts, 3D cards). | **Approved Storyboard:** Hook angle, visual narrative, layout shifts, and scene sequence approved before cutting footage. |
| **Gate 4** | **Precision Cut & Tone Grade** | Precision paper cut anchored to approved storyboard with tempo-aware speech breath padding (`apply-cut.py`); 3-way formula color grading preview sheet (`grade.py preview`) comparing 10 cinema presets and custom shadow/mid/high balance. | **Approved Cut & Tone Grade:** Kept/dropped takes approved; pacing confirmed; cinema color grade preset or formula selected. |
| **Gate 5** | **Kinetic Captions & Motion Graphics** | Author kinetic captions using `weight-shift` or `caption-highlight` with punch words (`captions.py`); query HyperFrames catalog (`npx hyperframes catalog`), install registry blocks into `$W/hyperframes/`, and wire layout into `hyperframes/index.html`. | **Approved Captions & Graphics:** Caption sample inspected; composition validated via `npx hyperframes check` (0 errors). |
| **Gate 6** | **Master Render & Quality Gate** | Render composite composition from `$W/hyperframes`, apply BT.709 color tags, master audio with adaptive/neural noise filtering (-14 LUFS, -1.0 dBTP ceiling), validate structural & review sheets (`VERIFY.md`, `REVIEW.md`), and automatically clear temporary scratch files via `clean-temp.py`. | **Final Delivery:** Version-controlled master in `$W/processed/<project>-v<N>.mp4` + fully CLI-editable `/hyperframes` project. |

---

## Tool Priority

1. **HyperFrames CLI Engine (Priority 1):** Catalog blocks and components (`npx hyperframes catalog`), `add`, `check`, `snapshot`, and `render` via CLI.
2. **Local Precision Engine (Priority 2):** whisper.cpp, `grade.py` color grading, ffmpeg audio chain, `apply-cut.py`, `clean-temp.py`.
3. **Generative Assets (Priority 3):** Veo & Gemini Flash for visual inserts (cost approved).

---

## Project Hygiene & Temp File Cleanup

Run upon completing review:
```bash
"$PROJECT/.venv/bin/python3" "$ENG/scripts/clean-temp.py" "$W" --clean-reports
```
Removes all transient audio stems (`audio-raw.wav`, `intro_dialogue_enhanced.m4a`), auto-editor cache (`speech.v1`), intermediate un-mastered video renders (`processed/*-raw.mp4`), and verification/review reports (`*-VERIFY.md`, `*-audio.json`, `*-REVIEW.md`, `*-review-sheet.png`), leaving exclusively the clean master deliverable in `processed/` and editable project assets in `hyperframes/`.
