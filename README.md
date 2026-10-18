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
> **Zero Workspace Pollution & Single Source of Truth**:
> - **Workspace Cleanliness**: Your creative directory contains **ONLY** `brand/`, `references/`, `sound-palette/`, and `videos/`. No `node_modules`, no `package.json`, no `.venv`, and no messy config files will ever clutter your project workspace.
> - **Single Conformed Video**: The cut video lives **strictly** at `videos/<project-id>/hyperframes/input-video.mp4`. It is never duplicated at the project root (`input-video.mp4`).
> - **Zero Temporary Data Sprawl**: No temporary preview directories (`preview-*`, loose `snapshots/`, test compositions) or copied frames persist in the project. All transient preview artifacts are automatically purged by `clean-temp.py`.

---

## 🚦 Streamlined Verification Gates (Gate 1 through Gate 6)

The pipeline executes sequentially through 6 unified verification checkpoints, ensuring deterministic quality and strict interactive user verification:

| Gate | Phase | Tools & Responsibility | Checkpoint & Deliverables |
|---|---|---|---|
| **Gate 1** | **Creative Spec & Context Audit** | `spec-resolver.py audit`, `memo.py` | Extracts prompt dimensions across 6 creative areas. If any dimension is missing, presents master catalog options (max 10 choices) with Option 1 strictly reserved for `(Recommended) Choose automatically based on video context & brand memory`. Proactively verifies quality flags (`--denoise neural` for indoor/outdoor, `--reframe yunet` for 9:16 vertical delivery, `--resolution uhd` for 4K). Audits typography catalog and caption engines. Emits `$W/resolved-spec.json`. |
| **Gate 2** | **Mandatory Video Watch & Speech Ingest** | `watch.py mine`, `whisper.cpp`, `verify-words.py`, `match.py` | **MANDATORY**: Runs `watch.py mine` as Step 1 to inspect pacing, speech velocity (WPM), silence distribution, and visual contact sheets. Dialogue isolation, speech-to-text with misspelling audit, and Roman Hinglish enforcement (strictly zero Devanagari script). **Strict Asset Caching**: transcripts and audio cleanup are cached and never regenerated unnecessarily. Emits `$W/reference-match/ROADMAP.md` matching against 50 style blueprints. |
| **Gate 3** | **Narrative Architecture & Storyboard** | `video-plan-storyboard`, `storyboard.py` | Hook design (0-3s), retention rhythm, scene breakdown, and multi-layout choreography (when A-roll shifts to split, pip, cutout, or layered canvas). Emits `$W/storyboard.plan.json`. |
| **Gate 4** | **Precision Cut & Dead-Air Elimination** | `dead-air.py`, `apply-cut.py`, `grade.py preview` | **Waveform Silence Elimination**: Scans real audio waveform RMS energy (`dead-air.py` / ffmpeg `silencedetect`) to catch dead air hidden by Whisper ASR stretching. Generates `PAPER-CUT.md` with explicit tables of dropped pauses (>0.40s compressed to 0.25-0.30s breath margins). 3-way color grading preview sheet comparing 10 cinema presets. |
| **Gate 5** | **Kinetic Captions & Typography Review** | `captions.py`, `compose.py`, HyperFrames CLI | Authors kinetic captions using `weight-shift` (Black 900 active word) or `caption-highlight` (fluorescent sweep) with scale-pop punch words. Selected from 5 approved typefaces (`DM Sans`, `Inter`, `Poppins`, `Google Sans`, `Roboto`). **Zero-Shadow by Default**: Defaults to zero text-shadow and zero blur (customizable on request). **Mandatory visual preview** presented to user for approval before rendering. |
| **Gate 6** | **Master Render & Quality Gate** | `render.py`, `review.py`, `clean-temp.py` | Composite UHD 4K render in **Standard Dynamic Range (SDR with `--sdr` default)** with lossless BT.709 color tags (prevents HDR washouts and 30GB cache spikes), EBU R128 loudness mastering (-14 LUFS, -1.0 dBTP), structural verification (`VERIFY.md`, `REVIEW.md`), and automated temp file purge. Output in `processed/<project>-v<N>.mp4`. |

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

## 🔤 Razor-Sharp Typography & Kinetic Caption Contract

Amateur video edits frequently suffer from blurry text, excessive drop shadows, and random font mismatches. The pipeline enforces a broadcast-grade typography standard:

### 1. The Approved 5-Typeface Catalog
All on-screen titles, lower-thirds, and kinetic captions are strictly selected from five verified typography families:
- **`DM Sans`**: Clean geometric sans with friendly rounded curves; outstanding for tech, creator, and lifestyle content.
- **`Inter`**: Highly articulate grotesque sans engineered for screen legibility; ideal for finance, data, and documentary authority.
- **`Poppins`**: Wide geometric display sans; high visual impact, authoritative, and viral-tested for high-CTR reels.
- **`Google Sans` / `Open Sans`**: Human-centered neutral typography; ideal for product demos and educational walkthroughs.
- **`Roboto`**: Balanced industrial grotesque; neutral, crystal-clear legibility across all screen densities.

### 2. Systematic Weight & Sizing Hierarchy
- **Regular (400) / Medium (500)**: Secondary words, conversational connectors, inactive spoken text.
- **SemiBold (600) / Bold (700)**: Card headers, section tags, active spoken words.
- **ExtraBold (800) / Black (900)**: Emphatic punch words, key financial figures, statistics, and critical assertions.

### 3. Zero-Shadow & Zero-Blur by Default (Creator-Customizable)
> [!NOTE]
> **Clean Vectors by Default**: By default, captions and badge pills render with **`text-shadow: none`**, **`box-shadow: none`**, and **zero artificial blur** to eliminate fuzzy edges and muddy halo artifacts.
> Contrast is achieved purely through high-contrast solid vectors:
> - **Inactive Words**: Clean 85% opacity white text (`rgba(255, 255, 255, 0.85)`).
> - **Active Spoken Word**: Dynamic high-contrast brand accents (`#FFD700` Gold, `#00E5FF` Cyan, `#00E676` Emerald, `#FF9100` Amber).
> - **Punch Words**: Solid, opaque rounded badge pills with bold Black 900 typography in solid `#000000` text, slightly tilted (-1.5° to -2°) for visual dynamism.
> 
> *Zero-shadow is a sensible default standard, not an inflexible rule: creators can freely choose to add drop shadows, outer glows, or blurs whenever requested for their custom creative aesthetic.*

### 4. Mandatory Gate 5 Pre-Render Review
Before any final video render, the pipeline presents a rendered snapshot comparing typography styles directly over the creator's footage, allowing creators to inspect and approve font pairings, weights, and badge pill colors before encoding.

---

## ✂️ Waveform Dead-Air Elimination & The ASR Stretching Trap

A major reason automated video editing pipelines leave awkward silences and dead air in raw footage is the **ASR Stretching Trap**:

```text
REAL AUDIO WAVEFORM:  [ "tumhare" ] ─── 1.60s DEAD SILENCE ─── [ "pas" ]
                                     ▲
WHISPER ASR TIMESTAMPS: [ tumhare: 2.66s ──────────────────── 6.00s ] [ pas: 6.00s ]
                                     ▲ (Gap calculation: 6.00 - 6.00 = 0.0s! Dead air hidden!)
```

### How the Pipeline Solves This:
1. **Audio Waveform RMS Energy Detection**: Instead of trusting Whisper word boundaries, the pipeline runs `dead-air.py` and ffmpeg `silencedetect=noise=-28dB:d=0.28` directly on the audio track.
2. **Precision Silence Compression**: Every dead-air pause > 0.40s is identified and compressed down to a crisp, natural 0.25s - 0.30s conversational breath margin. Leading silence (>0.12s) and trailing hesitation (>0.15s) are cleanly clipped.
3. **Interactive `PAPER-CUT.md`**: Before making permanent cuts, Gate 4 generates a complete cut ledger detailing original duration, proposed cut duration, exact timestamps of every dropped pause, and kept speech segments for creator approval.

---

## 📺 Universal Standard Dynamic Range (SDR) & Color Integrity

Modern smartphones (e.g., iPhone 14/15/16 Pro) capture video in 10-bit Dolby Vision / HLG HDR. While HDR looks vibrant on phone screens, processing HDR in browser-based composition engines introduces critical points of failure:

| Challenge | HDR Processing | Pipeline SDR Default (`--sdr`) |
|---|---|---|
| **Intermediate Cache Size** | Chrome decodes 10-bit HDR into 16-bit uncompressed buffers, consuming **~30 GB of disk** for a 60-second video. | Converted to crisp Rec.709 SDR at ingest, keeping intermediate frame cache at **~2 GB**. |
| **Color Fidelity & Gamma Shifts** | QuickTime, Instagram, and web players frequently apply inconsistent tone-mapping curves, causing washed-out skin tones or blown-out highlights. | Rendered with lossless BT.709 color tags (`bt709`), ensuring 100% color accuracy across all platforms. |
| **Cross-Platform Compatibility** | Inconsistent rendering between macOS, Linux, Windows, and mobile devices. | Universally compatible across iOS, Android, macOS, Windows, and all social platforms without color grading distortion. |

> [!NOTE]
> All renders execute with `--sdr` by default. When an end-to-end HDR workflow is explicitly requested, `--hdr` can be passed to preserve native wide gamut color spaces.

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

- **Universal SDR Delivery**: Videos strictly render in **Standard Dynamic Range with lossless BT.709 color tags (`--sdr` enabled by default)**, preventing QuickTime gamma washouts, extreme tone mapping variations across platforms, and 30 GB intermediate cache spikes.
- **Zero-Shadow Typography by Default**: Captions and punch badge pills default to zero text-shadow, zero box-shadow, and zero blur, preventing muddy halos while remaining fully customizable if the creator requests shadows or glows.
- **Audio Waveform Dead-Air Elimination**: All silence detection operates on real audio waveform RMS energy (`dead-air.py`), catching dead air hidden by Whisper ASR word stretching. Every pause > 0.40s is compressed to a natural 0.25-0.30s conversational pace.
- **Approved 5-Typeface Catalog**: Restricted to verified, high-CTR typefaces (`DM Sans`, `Inter`, `Poppins`, `Google Sans`, `Roboto`) across 400-900 weight hierarchy with mandatory Gate 5 visual preview before rendering.
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
