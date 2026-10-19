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

The pipeline enforces strict separation between isolated engine plumbing and your creative workspace:

```text
⚙️ GLOBAL ENGINE SANDBOX (~/.video-skills/engine)
├── .venv/ (Python 3.9+ runtime & dependencies: numpy, opencv, scipy, auto-editor)
├── node_modules/ (Pinned HyperFrames CLI & GSAP runtime)
└── .env & agent-env.sh (API keys & environment bootstrap)

📂 USER CREATIVE WORKSPACE (~/VideoWorkspace)
├── brand/            # Persistent memory: MEMO.md, STYLE-GUIDE.md, brand-style-guide.pdf, assets/
├── references/       # Style & benchmark inspiration reels, viral hooks, layouts
├── sound-palette/    # 19 curated offline tactile SFX & acoustic hierarchy
└── videos/<id>/      # Production projects: raw/ footage, hyperframes/ (input-video.mp4), processed/
```

---

## 📦 Installation & Setup

One line, from the folder you want as your creative workspace:

```bash
# macOS, Linux, Windows WSL / Git Bash
mkdir -p ~/VideoWorkspace && cd ~/VideoWorkspace
curl -fsSL https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.sh | bash
```
```powershell
# Windows PowerShell (checks prerequisites, then runs the same installer in Git Bash)
irm https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.ps1 | iex
```

Installs the latest **tagged release** into `~/.video-skills/pkg/<version>/`, links every skill into `~/.agents/skills` (and Claude Code), adds the `video-skills` command to `~/.local/bin` (appending a PATH line to `~/.zshrc` / `~/.bashrc` if needed), and runs `install.sh` for the engine, models and workspace. Options go after `bash -s --`, e.g. `… | bash -s -- --project ~/VideoWorkspace --version 1.0.0 --model large-v3-turbo`.

### Updates & package management (`video-skills`)

| Command | What it does |
|---|---|
| `video-skills check` | Is a newer release out? The pipeline also checks (cached, once a day) at every project start and **tells you**; it never updates on its own. |
| `video-skills changelog` | What changed between your version and the latest. |
| `video-skills update` | Update every skill + the engine to the latest release. |
| `video-skills update video-captions video-audio` | Update only those skills; the rest stay on your version. |
| `video-skills update --version 1.2.0` | Move to a specific release. |
| `video-skills list` / `status` | Each skill's version, latest version, edited or clean; paths, history, conflicts. |
| `video-skills rollback [X.Y.Z]` | Back to the previous (or named) version; skills are relinked instantly. |
| `video-skills setup` | Re-run the engine setup for your version (after fixing whatever stopped the installer). |
| `video-skills prune --keep 2` · `doctor` · `uninstall [--purge]` | Delete unused old versions · check links, PATH and engine · remove links and command (your workspace is never touched). |

**Your edits are safe.** Each skill is a link into a versioned copy. If you edited a skill and a release changes the same skill, `update` keeps yours, writes a diff to `~/.video-skills/conflicts/<skill>-<version>.diff` and tells you; merge what you want, then `video-skills update <skill> --force` (your copy is backed up to `~/.video-skills/backups/` first). Edited skills that a release did not touch stay as you have them.

**Already installed with the old `install.sh`?** Run the one-liner once with `--force` (`… | bash -s -- --force`): your copied skills are backed up and replaced by managed links.

**Windows:** use Git Bash (Git for Windows) or WSL. `get.ps1` lists any missing prerequisite with its `winget` line. Under Git Bash, skills are linked with directory junctions when symlinks are not allowed (no admin needed), the `video-skills` command gets a `video-skills.cmd` twin for cmd/PowerShell, and paths in `.env` are written as `C:/...` for the Windows Python.

### Publishing a release (maintainers)

```bash
bash tools/test-package-manager.sh                      # sandbox test: release, install, update, conflict, rollback
python3 tools/release.py 1.1.0 --note "What users get" --push
```
`release.py` refuses uncommitted work, writes `manifest.json` (per-skill versions and file hashes; a skill gets the new version only when its files changed), prepends the `CHANGELOG.md` section, commits, tags `v1.1.0`, pushes and creates the GitHub release. Users see it on their next `video-skills check` or project start.

### Manual install (no package manager)

```bash
bash /path/to/video-editing-skill/install.sh            # copies skills; no update notices or rollback
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

## 💡 Prompt Examples

Interact with your coding agent (Antigravity, Claude Code, Cursor) using simple instructions or detailed production briefs:

### Basic Prompts
- **9:16 Vertical Reel**: `Edit videos/test-01/raw/take1.mp4 into a 9:16 vertical reel for Instagram.`
- **Code Screencast**: `Edit videos/tutorial/raw/screen.mov into a YouTube tutorial with modern tech styling.`
- **Conversational Talking Head**: `Make a clean YouTube video from videos/interview/raw/pod.mp4 with warm Kodak Portra colors.`

### Production Brief Example
```text
Edit videos/finance-01/raw/pitch.mp4 into a high-retention financial teardown:
- Format: Split-screen 40/60 (creator on left, dynamic research canvas on right).
- Grading: Kodak Portra warm tone grade with soft shadow rolloff.
- Graphics: Highlight research clippings with fluorescent yellow sweeps, animated revenue charts, and glassmorphic stat counter.
- Captions: weight-shift style with Poppins font, punch words scaled 1.25x.
- Audio: Neural speech isolation; tactile paper slide and typewriter SFX.
- Delivery: 9:16 vertical UHD 4K.
```

---

## 💻 Cross-Platform Support

Install these first (the installer prints the same line for your system if something is missing):

| Platform | You install | The installer adds, privately in the engine (no sudo) |
|---|---|---|
| **macOS** | Homebrew; the installer runs `brew install node ffmpeg sox whisper-cpp` | DeepFilterNet |
| **Ubuntu / Debian** | `sudo apt-get install -y ffmpeg sox libsox-fmt-all libgomp1 python3-venv curl git` | Node.js 22 (if the system one is missing or older), whisper.cpp, DeepFilterNet |
| **Fedora** | `sudo dnf install -y ffmpeg-free sox libgomp python3 git` (full ffmpeg: RPM Fusion) | Node.js 22, whisper.cpp, DeepFilterNet |
| **Arch** | `sudo pacman -S --needed ffmpeg sox python git` | Node.js 22, whisper.cpp, DeepFilterNet |
| **Windows (Git Bash)** | `winget install --id Git.Git -e`, `Python.Python.3.12`, `Gyan.FFmpeg`, `ChrisBagwell.SoX` | Node.js 22, whisper.cpp, DeepFilterNet (x64) |
| **Windows (WSL2)** | the Ubuntu line, inside WSL | as Ubuntu |

Everything lands in `~/.video-skills/engine` (`node/`, `whisper/`, `.venv/`, `node_modules/`) and `~/.config/video-skills/`. When the private Node is installed, one marked line in `~/.bashrc` / `~/.zshrc` puts it first on PATH so `npx hyperframes` gets Node 22. Rendering needs Chrome: HyperFrames downloads its own on x64; on Linux ARM (no Chrome build exists) install a non-snap Chromium and set `HYPERFRAMES_BROWSER_PATH`.

---

## 🛠️ Offline Tactile Sound Palette

Bundles 19 pre-trimmed, peak-normalized (-3 dBFS) offline tactile SFX in `sound-palette/`:
- **Pops & Clicks**: `pop-clean.wav`, `click-switch.wav`, `click-soft.wav`
- **Paper & Textures**: `paper-slide.wav`, `paper-turn.wav`, `typewriter-ding.wav`
- **Movement & Accents**: `swoosh-fast.wav`, `swoosh-deep.wav`, `whoosh-subtle.wav`
- **Impacts & Shutters**: `camera-shutter.wav`, `camera-click.wav`, `thud-accent.wav`
- **Transitions & Swells**: `riser-swell.wav`, `reverse-cymbal.wav`, `sub-drop.wav`

---

## 🛡️ Anti-Hallucination & Quality Contract

- **Universal SDR Delivery**: Renders in Standard Dynamic Range with BT.709 tags (`--sdr` default) to prevent gamma washouts and excessive cache usage.
- **Zero-Shadow Vectors**: Captions default to zero text-shadow and blur for crisp legibility (customizable on request).
- **Waveform Dead-Air Cuts**: Silence detection via waveform RMS energy (`dead-air.py`), compressing pauses >0.40s to 0.25–0.30s breath margins.
- **Approved 5-Typeface Catalog**: Restricted to `DM Sans`, `Inter`, `Poppins`, `Google Sans`, and `Roboto` (400–900 weights).
- **Hinglish Transliteration**: Strictly Latin script (`yeh ek startup hai`, never Devanagari script).
- **Real Visual Grounding**: Colors and dimensions measured from real SVG vector logos or video frames.
- **Headroom Protection**: Overlays restricted to lower thirds (`y: 0.58 - 0.75`), protecting face and forehead (`y: 0.08 - 0.35`).
- **Automated Verification**: Gate 6 verifies loudness (-14 LUFS), zero black frames, and audio sync.

---

## 🚦 Streamlined Verification Gates (Gate 1 through Gate 6)

The pipeline executes through 6 sequential verification checkpoints:
- **Gate 1 (Spec & Context Audit)**: Audits prompt dimensions (`spec-resolver.py`), brand tokens (`memo.py`), and quality flags (`--denoise neural`, `--reframe yunet`, `--resolution uhd`).
- **Gate 2 (Video Watch & Speech Ingest)**: Pacing/silence audit (`watch.py mine`), dialogue isolation, Whisper transcription (Roman Hinglish), and blueprint matching (`match.py`).
- **Gate 3 (Narrative & Storyboard)**: Hook design (0–3s), pacing rhythm, scene breakdown, and layout choreography (`storyboard.py`).
- **Gate 4 (Precision Cut & Dead-Air)**: Waveform RMS silence detection (`dead-air.py`), breath margin compression (0.25–0.30s), and `PAPER-CUT.md` ledger.
- **Gate 5 (Kinetic Captions & Typography)**: Dynamic captions (`weight-shift` / `caption-highlight`) from 5 approved fonts with mandatory pre-render visual snapshot.
- **Gate 6 (Master Render & Quality Gate)**: UHD 4K SDR (BT.709) render, EBU R128 loudness mastering (-14 LUFS), structural review (`review.py`), and temp cleanup.

---

## 🎨 3-Way Tone Formula & Cinema Color Grading (`grade.py`)

Formulaic 3-way tone mapping (black floor lift, midtone skin gamma, soft highlight rolloff) with bundled cinema presets:
`kodak-portra`, `hollywood-teal`, `vox-doc`, `magnates-gold`, `fuji-pro`, `modern-tech`, `moody-film`, `vibrant-pop`, `nordic-cold`, and `studio-clean`.

---

## 🔤 Razor-Sharp Typography & Kinetic Caption Contract

- **5 Approved Typefaces**: `DM Sans`, `Inter`, `Poppins`, `Google Sans`, `Roboto` (weights 400 to 900).
- **Clean Vectors by Default**: Zero text-shadow and zero blur by default to eliminate fuzzy halos (customizable on request).
- **Engines**: `weight-shift` (active word emphasis) and `caption-highlight` (fluorescent sweeps) with Gate 5 pre-render approval.

---

## ✂️ Waveform Dead-Air Elimination & The ASR Stretching Trap

Avoids Whisper ASR word-stretching inaccuracies by scanning audio waveform RMS energy (`dead-air.py` / `silencedetect`). Compresses pauses >0.40s down to 0.25–0.30s conversational breath margins, documented in `PAPER-CUT.md` before applying cuts.

---

## 📺 Universal Standard Dynamic Range (SDR) & Color Integrity

Renders in Standard Dynamic Range with Rec.709/BT.709 color tags by default (`--sdr`), preventing HDR tone-mapping washouts and reducing intermediate cache from ~30 GB to ~2 GB. Pass `--hdr` when wide gamut is explicitly required.

---

## 🧠 Persistent Brand Memory (`brand/MEMO.md`)

Maintains creator preferences across sessions (social handles, logos, font choices, caption engine, brand colors, default layouts, and audio targets). Inspected and updated via `python3 "$ENG/scripts/memo.py" [get|set]`.

---

## 🗂️ Built-in Style Blueprint Index (`video-reference-match`)

Ships with 50 measured, anonymous style blueprints (`B01`–`B50`). At project start, footage is matched against blueprint pacing, layout, and caption heuristics to generate `$W/reference-match/ROADMAP.md` before cuts are applied.

---

## 📜 License

The engine and scripts are licensed under the **MIT License**.  
Bundled open-source typography (DM Sans, Poppins, Inter, Noto Sans Devanagari) is distributed under the **SIL Open Font License**.  
Full license texts reside in [`LICENSES/`](file:///Users/mahesh/lmc/video-editing-skill/LICENSES).
