# 🎬 Video Editor Skills for Coding Agents

> **Autonomous, CLI-first video editing pipeline for AI agents.**  
> Transform raw creator footage into broadcast-grade short-form and long-form video across 9 verified quality gates—powered by `whisper.cpp`, `HyperFrames CLI`, `FFmpeg`, `RNNoise`, and an offline tactile sound palette.

[![Tests](https://img.shields.io/badge/tests-136%20passed-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)]()
[![Architecture](https://img.shields.io/badge/engine-CLI--first-blue.svg)]()
[![Audio](https://img.shields.io/badge/audio-EBU%20R128-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

---

## ⚡ Architecture & Pipeline Contract

The system enforces a strict project isolation and execution contract:

```text
~/VideoEditing/ (Workspace Root)
├── references/                       # [STYLE & BENCHMARK INSPIRATION HUB]
│   ├── benchmark-reel.mp4            # Inspiration video to learn pacing & cuts from
│   ├── brand-style-guide.pdf         # Brand guidelines, colors & typography rules
│   └── layout-reference.png          # Target lower-third or graphic layout screenshot
│
├── sound-palette/                    # [OFFLINE TACTILE SOUND PALETTE]
│   ├── audio/                        # 19 pre-trimmed, -3 dBFS peak-normalized SFX
│   └── sound-palette.json            # Acoustic hierarchy and cue mappings
│
└── videos/                           # [VIDEO PRODUCTION PROJECTS]
    ├── _shared/                      # Reusable assets across projects (logos, fonts, SFX)
    └── <project-id>/                 # Project-specific workspace
        ├── raw/                      # [STRICT INPUT BOUNDARY] User footage & mic audio
        │   ├── C0001.MP4             # Raw creator talking-head footage
        │   ├── screen-demo.mov       # Screen captures / product demos
        │   └── mic-audio.wav         # Primary audio recording
        │
        ├── hyperframes/              # [CLI-FIRST COMPOSITION ENGINE]
        │   ├── index.html            # Root composition contract
        │   ├── input-video.mp4       # Conformed flat cut
        │   ├── compositions/         # Modular catalog blocks & dynamic captions
        │   │   ├── captions.html     # Typographic caption rail
        │   │   └── stat-callout.html # Lower-third metric pill
        │   ├── sfx/                  # Peak-normalized (-3 dBFS) sound effects
        │   └── broll/                # Conformed AI & stock cutaways
        │
        └── processed/                # [VERSION-CONTROLLED DELIVERABLES]
            ├── <project-id>-v1.mp4   # Master render (EBU R128 mastered, BT.709 tagged)
            └── <project-id>-v2.mp4   # Clean output (transient reports purged post-review)
```

- **Strict Raw Ingestion (`/raw`)**: All skills and tools strictly ingest assets located within `videos/<project-id>/raw/`. External mentions are treated as advisory context only.
- **CLI-First Composition (`/hyperframes`)**: Fully decoupled from desktop GUI applications. Compositions are authored, validated, previewed, and rendered 100% via CLI (`npx hyperframes check`, `npx hyperframes preview`, `render.py`).
- **Offline Curated Sound Palette**: 19 pre-trimmed, peak-normalized (-3 dBFS) tactile SFX in `sound-palette/` (clicks, swooshes, pops, camera shutters, paper slides, riser swells) resolved offline without requiring cloud accounts.
- **Dynamic Style-Aware Cut Padding**: Dynamic tempo/WPM-based margins (35–50ms for aggressive hooks; 65–85ms for investigative teardowns; 100–130ms for conversational pacing) with 8–15ms audio micro-fades.
- **Automated Verification & Post-Review Purge**: Structural (`VERIFY.md`), acoustic (`audio.json`), and visual (`REVIEW.md`, `review-sheet.png`) quality gates run on the binary MP4. Once review succeeds, `clean-temp.py --clean-reports` automatically purges intermediate dumps, leaving only the clean deliverable.

---

## 📂 The `references/` Folder (Inspiration & Benchmark Hub)

The `references/` folder at your workspace root serves as the **creative and technical benchmark library** for the agent. Before editing your footage, the agent inspects this folder to analyze pacing, visual aesthetics, color grading, and motion graphics from high-performing benchmark content.

### What users should add to `references/`:

1. **Benchmark / Inspiration Videos (`.mp4`, `.mov`)**:
   - High-retention Instagram Reels, YouTube Shorts, or long-form videos whose editing style, pacing, and retention rhythm you want to emulate (e.g. `references/finance-explainer-benchmark.mp4`).
   - The `video-watch` skill inspects these files via `python3 "$ENG/scripts/watch.py" ref "references/<video>.mp4"`, extracting:
     - **Median Shot Duration** (e.g. 1.4s fast-paced vs 3.2s conversational).
     - **Pacing & Cut Frequency** (J-cut/L-cut transitions, camera resets).
     - **Acoustic Loudness Profile** (integrated LUFS and background bed ducking depth).
     - **Visual Fingerprint** (`watch/fingerprint.json` and contact sheets).
2. **Brand Guidelines & Color Kits (`.pdf`, `.png`, `style.json`)**:
   - Brand books, official color codes (primary, secondary, background, text), and contrast themes.
   - The `video-style` skill reads these assets to extract verified color tokens and typography stacks.
3. **Typography & Font Specimens (`.ttf`, `.otf`, `.woff2`)**:
   - Custom fonts for brand titles, lower thirds, and captions.
4. **Layout Screenshots & Graphics References (`.png`, `.jpg`)**:
   - Screenshots of lower-third banners, stat counters, split-screen layouts, or paper textures you want the agent to match using HyperFrames catalog blocks.
5. **Topic & Narrative Benchmarks (`.md`, `.txt`)**:
   - Script teardowns, competitor hook formulas, or research notes used by `video-researcher` during Gate 0.

---

## 📦 Install

From the folder you will open in Claude Code, Antigravity, or Cursor (your workspace root), run the installer:

```bash
mkdir -p ~/VideoEditing && cd ~/VideoEditing
bash /path/to/video-editor-skills/install.sh
```

### What it does:
1. **System Tools**: Installs `node` (22+), `ffmpeg`, `sox`, and `whisper-cpp` via Homebrew.
2. **Models & Neural Weights**: Downloads Whisper model (`ggml-large-v3.bin`), RNNoise neural voice denoiser (`sh.rnnn`), and OpenCV YuNet ONNX face detection model.
3. **Python Environment**: Configures `./.venv` with `numpy`, `pillow`, `opencv-python-headless`, `auto-editor`, and `google-genai`.
4. **Skills & Sound Palette**: Installs 18 specialized skills into `~/.agents/skills/` and links the 19 pre-trimmed audio effects into `./sound-palette/` and `videos/_shared/sfx/`.
5. **HyperFrames Engine**: Pins CLI version in `package.json`, installs headless browser, and copies offline GSAP runtime.
6. **Keys & Environment**: Creates private `.env` and exports `VIDEO_SOUND_PALETTE`, `RNNOISE_MODEL`, and `YUNET_MODEL`.
7. **Agent Wiring**: Writes `agent-env.sh` and an `AGENTS.md` block for seamless agent startup.
8. **Automated Verification**: Executes test suites (136 unit & integration tests) and diagnostic checks.

---

### Any Agent (Claude Code, Gemini CLI, Antigravity, Cursor)

The skills follow the standard Agent Skills format (each directory contains a `SKILL.md`):

```bash
# Link skills to another agent's skills directory:
bash /path/to/video-editor-skills/install.sh --link <other-agent-skills-dir>

# Start any terminal agent with project environment:
source agent-env.sh
```

---

## 🛠️ Build Status & Skill Matrix

| Phase | Skills | Responsibility |
|---|---|---|
| **1. Ingest & Audio** | `video-watch`, `video-transcribe`, `video-audio` | Whisper speech-to-text, RNNoise neural voice isolation, 80Hz rumble cut, SNR measurement. |
| **1.5. Research** | `video-researcher` | Internet category intelligence, viral benchmark analysis, SVG vector logo extraction/generation. |
| **2. Pacing & Cut** | `video-plan-storyboard`, `video-cut-audit`, `video-take-geometry`, `video-short-form` | Narrative hook design, dynamic style-aware cut padding, jump-frame alignment, YuNet face-tracked reframing (9:16). |
| **3. Layout & Polish**| `video-style`, `video-format`, `video-motion-graphics`, `video-captions` | 225-Style taxonomy, HyperFrames catalog block wiring, lower-third headroom protection, typographic caption rails. |
| **4. Sound & Delivery**| `video-sound-design`, `video-generate`, `video-omni-restyle`, `video-render`, `video-review-gate` | Curated sound palette sync, ducked bed mixing (-18 dB), BT.709 color tagging, EBU R128 mastering, automated review purge. |
| **Custom Style** | `business-reels-style` | Bespoke Indian startup, creator & business reel style guide (Inter, Noto Sans Devanagari, minimal sound design). |

---

## 🛡️ Anti-Hardcoding & Grounding Contract

Every skill operates under a strict anti-hallucination and zero-guesswork standard:
- **No Mock or Placeholder URLs**: Never output dummy URLs (`example.com`). All citations, articles, and references must be live URLs fetched during the session.
- **Measured Visual Tokens**: Colors and layout dimensions are extracted directly from vector logos (`extract_colors_from_svg`) or measured footage frames (`palette.py`).
- **Real Platform Metrics**: Creator handles, reference view counts, and retention claims must be observed real numbers.
- **Clean Headroom Enforcement**: No floating checklist pills or sticky banners over the creator's forehead or hairline (`y: 0.08 – 0.35`). Overlays stay in the lower third (`y: 0.58 – 0.75`).
- **Natural Spoken Caption Flow**: Phrases grouped into natural syntactic units (4–6 words per phrase), pause break threshold at 0.30s, and zero awkward orphan single words.

---

## 📜 Licences

The engine and scripts are licensed under the **MIT License**.  
Bundled open-source typography (DM Sans, Poppins, Inter, Noto Sans Devanagari) is distributed under the **SIL Open Font License**.  
Full license texts reside in [`LICENSES/`](file:///Users/mahesh/lmc/video-editor-skills/LICENSES).
