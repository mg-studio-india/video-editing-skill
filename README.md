# 🎬 Autonomous Video Editing Pipeline for Coding Agents

> **Broadcast-grade, CLI-first video editing pipeline powered by AI agents.**  
> Transform raw creator footage into high-retention short-form and long-form video across 6 verified quality gates—powered by `whisper.cpp`, `HyperFrames CLI`, `FFmpeg`, `RNNoise`, `DeepFilterNet3`, `YuNet`, and an offline tactile sound palette.

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-blue.svg)]()
[![Architecture](https://img.shields.io/badge/engine-global%20sandbox-blueviolet.svg)]()
[![Resolution](https://img.shields.io/badge/output-UHD%204K-gold.svg)]()
[![Audio](https://img.shields.io/badge/audio-EBU%20R128-orange.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

---

## ⚡ Architecture: Global Engine Sandbox vs. Clean Workspace

To keep your working directory 100% spotless across all platforms (**macOS, Linux, Windows**), the pipeline enforces a strict separation between **Engine Plumbing** and **Creative Workspace**:

```text
⚙️ GLOBAL ENGINE SANDBOX (~/.video-skills/engine or ~/.config/video-skills/engine)
├── .venv/                            # Python 3.9+ runtime & isolated dependencies
│   ├── bin/python3 (or Scripts/python.exe on Windows)
│   └── lib/python*/site-packages/    # numpy, opencv, pillow, auto-editor, scipy, etc.
├── node_modules/                     # Pinned HyperFrames CLI & GSAP runtime
├── package.json & package-lock.json  # NPM lockfiles isolated from user space
├── LICENSES/                         # Third-party font & open-source licenses
├── .env                              # Private API keys (chmod 600)
└── agent-env.sh                      # Global environment bootstrap

───────────────────────────────────────────────────────────────────────────────────

📂 USER CREATIVE WORKSPACE (~/VideoWorkspace or your project folder)
├── brand/                            # [PERSISTENT BRAND MEMORY & PREFERENCES]
│   ├── MEMO.md                       # Active memory: styling, handles, fonts, layout
│   └── assets/                       # Vector logos (.svg), avatars, monograms, badges
│
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
        ├── hyperframes/              # [CLI COMPOSITION ENGINE]
        │   ├── index.html            # Root composition contract
        │   ├── input-video.mp4       # Conformed flat cut
        │   └── compositions/         # Modular catalog blocks & dynamic captions
        │
        └── processed/                # [DELIVERABLES]
            └── <project-id>-v1.mp4   # Master UHD 4K render (EBU R128 mastered, BT.709)
```

> [!IMPORTANT]
> **Zero Workspace Pollution**: Your creative directory contains **ONLY** `brand/`, `references/`, `sound-palette/`, and `videos/`. No `node_modules`, no `package.json`, no `.venv`, and no messy config files will ever clutter your project workspace. The runtime automatically discovers the engine sandbox on any OS.

---

## 🚦 Streamlined Verification Gates (Gate 1 through Gate 6)

The pipeline executes sequentially through 6 unified verification checkpoints, ensuring deterministic quality and strict interactive user verification:

| Gate | Phase | Tools & Responsibility | Checkpoint & Deliverables |
|---|---|---|---|
| **Gate 1** | **Creative Spec & Context Audit** | `spec-resolver.py audit`, `memo.py` | Extracts prompt dimensions across 6 creative areas. If any dimension is missing, presents master catalog options (max 10 choices) with Option 1 strictly reserved for `(Recommended) Choose automatically based on video context & brand memory`. Proactively verifies quality flags (`--denoise neural` for indoor/outdoor, `--reframe yunet` for 9:16 vertical delivery, `--resolution uhd` for 4K). Emits `$W/resolved-spec.json`. |
| **Gate 2** | **Ingest, Speech & Blueprint Match** | `whisper.cpp`, `verify-words.py`, `match.py` | Audio isolation, speech-to-text with misspelling audit, and Roman Hinglish enforcement (strictly zero Devanagari script). **Strict Asset Caching**: transcripts and audio cleanup are cached and never regenerated unnecessarily. Emits `$W/reference-match/ROADMAP.md` matching against 50 style blueprints. |
| **Gate 3** | **Narrative Architecture & Storyboard** | `video-plan-storyboard`, `storyboard.py` | Hook design (0-3s), retention rhythm, scene breakdown, and multi-layout choreography (when A-roll shifts to split, pip, cutout, or layered canvas). Emits `$W/storyboard.plan.json`. |
| **Gate 4** | **Precision Cut & Tone Grade** | `apply-cut.py`, `grade.py preview` | Frame-accurate cut with acoustic breath safety padding; 3-way formula color grading preview sheet comparing 10 cinema presets and custom shadow/mid/high balance. |
| **Gate 5** | **Kinetic Captions & Motion Graphics** | `captions.py`, `compose.py`, HyperFrames CLI | Authors kinetic captions using `weight-shift` (Black 900 active word) or `caption-highlight` (fluorescent sweep) with scale-pop punch words (or `layered-head` behind speaker for large background numbers). Installs HyperFrames catalog blocks and wires layout. |
| **Gate 6** | **Master Render & Quality Gate** | `render.py`, `review.py`, `clean-temp.py` | Final composite UHD 4K render (2160x3840 / 3840x2160 @ 45M bitrate), BT.709 color tags, EBU R128 loudness mastering (-14 LUFS, -1.0 dBTP), structural verification (`VERIFY.md`, `REVIEW.md`), and automated temp file purge. Output in `processed/<project>-v<N>.mp4`. |

---

## 🎨 3-Way Tone Formula & Cinema Color Grading (`grade.py`)

No generic washed-out video filters. The engine applies formulaic 3-way tone adjustments:
- **Low-Tones & Shadows**: Black floor lift (`colorlevels` min input calibration) to eliminate muddy black clipping.
- **Midtones**: Gamma curves preserving natural skin-tone luminance.
- **High-Tones & Highlights**: Soft white ceiling rolloff preventing blown-out exposure.
- **Contrast & Saturation**: S-curve tone mapping with selective color vibrance.

### Bundled Studio Cinema Presets:
1. `kodak-portra`: Warm, golden skin tones with soft creamy highlight rolloff.
2. `hollywood-teal`: High-contrast blockbuster look with warm facial tones and cool teal shadows.
3. `vox-doc`: Clean documentary styling with rich deep blacks and clinical contrast.
4. `magnates-gold`: Rich luxury gold and bronze tones for business and finance teardowns.
5. `fuji-pro`: Atmospheric emerald greens, cool sky blues, and organic portrait softness.
6. `modern-tech`: Crisp ultra-clean neutral shadows with subtle cyan accents for tech reviews.
7. `moody-film`: Low-key dramatic shadow crush with desaturated film grain aesthetics.
8. `vibrant-pop`: High-saturation punchy primaries for viral lifestyle and product shorts.
9. `nordic-cold`: Desaturated steel-blue undertones for serious investigative journalism.
10. `studio-clean`: Natural, color-accurate neutral grade calibrated for broadcast compliance.

---

## 🧠 Persistent Brand Memory (`brand/MEMO.md`)

The `brand/MEMO.md` file serves as the **persistent creator memory** across all video projects. The pipeline reads and updates this file at runtime, eliminating repetitive questions about your social handles, font preferences, or outro cards:

```bash
# Read brand memory as structured JSON
python3 "$ENG/scripts/memo.py" get --json

# Update creator preferences at runtime
python3 "$ENG/scripts/memo.py" set "Instagram" "@founder_daily"
python3 "$ENG/scripts/memo.py" set "Primary Caption Engine" "weight-shift"
python3 "$ENG/scripts/memo.py" set "Video Quality" "UHD / 4K (2160x3840 @ 45M bitrate)"
```

### What is stored in `brand/MEMO.md`:
- **Identity & Profiles**: Social handles (`@instagram`, `@youtube`, `@x`), web URLs, and brand logos (`brand/assets/logo.svg`).
- **Creative Dynamic Layout**: Default layout transitions (Full $\rightarrow$ Split 40/60 $\rightarrow$ Corner PiP $\rightarrow$ Layered Canvas).
- **Typography & Captions**: Primary font family (Inter, Poppins, DM Sans), caption engine (`weight-shift` / `caption-highlight`), and Roman Hinglish enforcement.
- **Color Tokens**: Primary brand hex, accent highlights, and glassmorphism card surfaces.
- **Audio Master Defaults**: Neural speech isolation (`--denoise neural`), -14 LUFS loudness target, and -18 dB music ducking depth.
- **Video Delivery Specs**: UHD / 4K resolution (2160x3840 @ 45M bitrate, BT.709 color tags).

---

## 💡 Prompt Examples

You can interact with your coding agent (Antigravity, Claude Code, Cursor) using simple conversational instructions or comprehensive production briefs:

### 1. Basic Prompt Examples

#### Quick 9:16 Vertical Reel
```text
Edit videos/test-01/raw/take1.mp4 into a 9:16 vertical reel for Instagram.
```
*What happens automatically:*
- Ingests `take1.mp4`, performs speech-to-text, and enforces Roman Hinglish transliteration.
- Detects video context and defaults to `multi-dynamic` format with `weight-shift` captions.
- Applies DeepFilterNet3 neural denoise for clean voice isolation and YuNet face tracking.
- Renders master output in UHD 4K (2160x3840) with EBU R128 loudness mastering.

#### Technical Code Screencast
```text
Edit videos/tutorial/raw/screen.mov into a YouTube tutorial with modern tech styling.
```
*What happens automatically:*
- Detects technical walkthrough context and selects `screen-plus-facecam` layout.
- Applies `modern-tech` color grading and crisp lower-third headline callouts.
- Ducks ambient keyboard clicks while preserving crisp vocal presence.

#### Conversational Talking Head
```text
Make a clean YouTube video from videos/interview/raw/pod.mp4 with warm Kodak Portra colors.
```
*What happens automatically:*
- Selects conversational single-host pacing with natural breath safety margins.
- Applies `kodak-portra` 3-way tone grading preview and subtle lofi background music.

---

### 2. Detailed Production Prompt Examples

#### High-Retention Investigative Financial Teardown
```text
Edit videos/finance-01/raw/pitch.mp4 into a high-retention financial teardown:
- Format: Split-screen 40/60 (creator on left, dynamic research canvas on right).
- Grading: Kodak Portra warm tone grade with soft shadow rolloff.
- Graphics: Highlight research clippings with fluorescent yellow sweeps, draw animated revenue charts, and pop a glassmorphic stat counter for '$12.4M ARR'.
- Captions: weight-shift style with Poppins font, scaling punch words like 'valuation' and 'crash' by 1.25x.
- Audio: Enable neural speech isolation to eliminate room echo and AC hum. Add tactile paper slide and typewriter SFX on document reveals.
- Delivery: 9:16 vertical UHD 4K.
```

#### Viral Startup Founder Commentary
```text
Transform videos/founder-update/raw/camera.mp4 into a viral business reel:
- Pace: Punchy 1.4s median shot duration; cut all filler words and pauses >0.3s.
- Layout: Multi-dynamic choreography (start full-camera 0-3s, drop to bottom corner PiP when displaying competitor metrics, shift to cutout canvas on hook punchline).
- Tone Grade: Modern Tech cinema preset with crisp deep shadows and neutral skin tones.
- Captions: caption-highlight engine with neon green fluorescent bar sweep and Roman Hinglish transliteration.
- Face Tracking: Keep face centered using YuNet ONNX neural tracking.
- Outro: Animate brand card from brand/assets/logo.svg with Instagram handle from brand/MEMO.md.
```

#### Luxury Business Empire Breakdown
```text
Edit videos/empire/raw/host.mp4 into an executive brand documentary:
- Format: Layered-head canvas with large bold backdrop text numbers ('₹500 CRORE') floating seamlessly behind the speaker's shoulders.
- Grading: Magnates Gold preset with rich bronze shadows and elevated warm highlights.
- Sound Design: Minimal acoustic sound palette; soft riser swell on topic transitions, subtle vinyl clicks on bullet points, and upbeat lofi music ducked to -19 dB during speech.
- Outro: Smooth scale-down into brand badge with subscribe trigger pill.
- Resolution: Master at 2160x3840 UHD 4K @ 45 Mbps with BT.709 tags.
```

---

## 📦 Installation & Setup

Run the cross-platform installer from your creative workspace:

```bash
# 1. Create or navigate to your video workspace folder
mkdir -p ~/VideoWorkspace && cd ~/VideoWorkspace

# 2. Run the installer (macOS, Linux, Windows WSL)
bash /path/to/video-editing-skill/install.sh
```

### Installation Options:
- `--project DIR`: Set custom creative workspace root (default: current directory).
- `--engine-dir DIR`: Custom engine sandbox location (default: `~/.video-skills/engine`).
- `--local-engine`: Install engine sandbox inside `.engine/` in the project directory.
- `--model NAME`: Whisper model (`large-v3` default, or `large-v3-turbo`).
- `--skip-pip`: Reuse existing Python virtual environment as is.
- `--skills-dir DIR`: Directory to install agent skills (default: `~/.agents/skills`).
- `--link DIR`: Link skills into other agents (e.g. `~/.claude/skills`, `~/.gemini/antigravity-cli/skills`).

---

## 💻 Cross-Platform Support

| Platform | System Tools Setup | Python Runtime | Engine Sandbox |
|---|---|---|---|
| **macOS** | `brew install node ffmpeg sox whisper-cpp` | Apple Silicon / Intel Python 3.9+ | `~/.video-skills/engine` |
| **Linux (Ubuntu/Debian)** | `sudo apt install nodejs npm ffmpeg sox libsox-fmt-all` | Python 3.9+ (`python3-venv`) | `~/.config/video-skills/engine` |
| **Linux (Fedora/RHEL)** | `sudo dnf install nodejs npm ffmpeg sox` | Python 3.9+ | `~/.config/video-skills/engine` |
| **Linux (Arch)** | `sudo pacman -S nodejs npm ffmpeg sox` | Python 3.9+ | `~/.config/video-skills/engine` |
| **Windows (WSL2)** | Native Ubuntu setup inside WSL2 | Ubuntu Python 3.9+ | `~/.video-skills/engine` |
| **Windows (Native)** | `winget install Gyan.FFmpeg OpenJS.NodeJS ChrisBagwell.SoX` | Python 3.9+ (`Scripts/python.exe`) | `%USERPROFILE%\.video-skills\engine` |

---

## 🛠️ Offline Tactile Sound Palette

The pipeline bundles 19 pre-trimmed, peak-normalized (-3 dBFS) tactile sound effects in `sound-palette/`:
- **Pops & Clicks**: `pop-clean.wav`, `click-switch.wav`, `click-soft.wav`
- **Paper & Textures**: `paper-slide.wav`, `paper-turn.wav`, `typewriter-ding.wav`
- **Movement & Accents**: `swoosh-fast.wav`, `swoosh-deep.wav`, `whoosh-subtle.wav`
- **Impacts & Shutters**: `camera-shutter.wav`, `camera-click.wav`, `thud-accent.wav`
- **Transitions & Swells**: `riser-swell.wav`, `reverse-cymbal.wav`, `sub-drop.wav`

All audio effects work completely offline without requiring cloud API credits. When a HeyGen API key is configured, the agent seamlessly blends expanded online tracks with this local palette.

---

## 🛡️ Anti-Hallucination & Quality Contract

- **Strict Hinglish Roman Transliteration**: Captions never mix Devanagari script into Latin captions (`yeh ek startup hai`, not `यह ek startup hai`).
- **Real Visual Grounding**: Colors and dimensions are measured from real SVG vector logos or video frames. No arbitrary hex guesses (`#FFFFFF`).
- **No Placeholder URLs**: Never generates fake citations (`example.com`). All references must be live URLs fetched during the session.
- **Headroom Protection**: Overlays and checklists never cover the speaker's face or forehead (`y: 0.08 - 0.35`). Graphic cards strictly occupy the lower third (`y: 0.58 - 0.75`).
- **Automated Verification & Review**: Gate 6 verifies loudness compliance (-14 LUFS), black-frame absence, and audio sync before finalizing the MP4.

---

## 📜 License

The engine and scripts are licensed under the **MIT License**.  
Bundled open-source typography (DM Sans, Poppins, Inter, Noto Sans Devanagari) is distributed under the **SIL Open Font License**.  
Full license texts reside in [`LICENSES/`](file:///Users/mahesh/lmc/video-editing-skill/LICENSES).
