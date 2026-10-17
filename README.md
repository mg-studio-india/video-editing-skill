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
videos/<project-id>/
├── raw/                              # [STRICT INPUT BOUNDARY]
│   ├── C0001.MP4                     # Raw creator talking-head footage
│   ├── screen-demo.mov               # Screen captures / product demos
│   └── mic-audio.wav                 # Primary audio recording
│
├── hyperframes/                      # [CLI-FIRST COMPOSITION ENGINE]
│   ├── index.html                    # Root composition contract
│   ├── input-video.mp4               # Conformed flat cut
│   ├── compositions/                 # Modular catalog blocks & dynamic captions
│   │   ├── captions.html             # Typographic caption rail
│   │   └── stat-callout.html         # Lower-third metric pill
│   ├── sfx/                          # Peak-normalized (-3 dBFS) sound effects
│   └── broll/                        # Conformed AI & stock cutaways
│
└── processed/                        # [VERSION-CONTROLLED DELIVERABLES]
    ├── <project-id>-v1.mp4           # Master render (EBU R128 mastered, BT.709 tagged)
    └── <project-id>-v2.mp4           # Clean output (transient reports purged post-review)
```

- **Strict Raw Ingestion (`/raw`)**: All skills and tools strictly ingest assets located within `videos/<project-id>/raw/`. External mentions are treated as advisory context only.
- **CLI-First Composition (`/hyperframes`)**: Fully decoupled from desktop GUI applications. Compositions are authored, validated, previewed, and rendered 100% via CLI (`npx hyperframes check`, `npx hyperframes preview`, `render.py`).
- **Offline Curated Sound Palette**: 19 pre-trimmed, peak-normalized (-3 dBFS) tactile SFX in `sound-palette/` (clicks, swooshes, pops, camera shutters, paper slides, riser swells) resolved offline without requiring cloud accounts.
- **Dynamic Style-Aware Cut Padding**: Dynamic tempo/WPM-based margins (35–50ms for aggressive hooks; 65–85ms for investigative teardowns; 100–130ms for conversational pacing) with 8–15ms audio micro-fades.
- **Automated Verification & Post-Review Purge**: Structural (`VERIFY.md`), acoustic (`audio.json`), and visual (`REVIEW.md`, `review-sheet.png`) quality gates run on the binary MP4. Once review succeeds, `clean-temp.py --clean-reports` automatically purges intermediate dumps, leaving only the clean deliverable.

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
