# 🎬 AI Video Editor for Coding Agents

> **Turn raw creator footage into polished, high-retention videos using your AI coding agent (Antigravity, Claude Code, Cursor, etc.).**  
> Automatically cuts dead air, cleans audio, adds animated captions, matches your brand, and delivers crisp 4K videos—with previews at every step so you're always in control.

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-blue.svg)]()
[![Resolution](https://img.shields.io/badge/output-UHD%204K-gold.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

---

### ⚡ Quick Navigation
[🚀 Quick Start](#-quick-start-3-steps) • [🔄 Updates](#-staying-up-to-date) • [💬 Prompts to Try](#-prompts-to-try) • [✨ What It Does For You](#-what-it-does-for-you) • [📁 Folder Structure](#-how-your-workspace-is-organized) • [⚙️ Under the Hood](#️-under-the-hood-technical-details)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install
Open your terminal in the folder you want as your video workspace and paste one line:

```bash
# macOS, Linux, WSL, Git Bash
mkdir -p ~/VideoWorkspace && cd ~/VideoWorkspace
curl -fsSL https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.sh | bash
```
```powershell
# Windows PowerShell (checks what is missing, then installs through Git Bash)
irm https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.ps1 | iex
```

The installer downloads the latest release, sets up every skill for your agents (Claude Code, Antigravity, Cursor), and asks for your API keys (all optional). Anything your system is missing is installed for you or printed as one command to run. Check it any time with `video-skills doctor`.

<details>
<summary><b>Install options</b></summary>

Add options after `bash -s --`, for example:
`curl -fsSL .../get.sh | bash -s -- --project ~/VideoWorkspace --model large-v3-turbo --yes`

- `--project DIR`: your workspace folder (default: the current folder)
- `--model NAME`: Whisper model, `large-v3` (default, ~3 GB) or `large-v3-turbo`
- `--version X.Y.Z`: install a specific release
- `--yes`: no questions; keep existing keys
- `--force`: replace skills copied by an older manual install (your copies are backed up first)
</details>

### Step 2: Add your footage
Put your raw recording inside `videos/<project-name>/raw/` (e.g. `videos/my-first-video/raw/take1.mp4`).

### Step 3: Tell your AI agent what to make
Open your coding agent (Antigravity, Claude Code, Cursor) and type:
> *"Edit `videos/my-first-video/raw/take1.mp4` into a 9:16 vertical reel for Instagram."*

Your agent will inspect the clip, clean the speech, cut the pauses, propose visual styles, and ask you to approve previews before exporting the final 4K video!

---

## 🔄 Staying Up to Date

Your agent tells you at the start of a project when a new version is out. Nothing updates without you.

| Command | What it does |
|---|---|
| `video-skills check` | Is a new version out? |
| `video-skills changelog` | What changed since your version |
| `video-skills update` | Update everything to the latest release |
| `video-skills update video-captions` | Update just one skill |
| `video-skills rollback` | Go back to the previous version |
| `video-skills doctor` | Check that every skill and agent folder is set up correctly |
| `video-skills setup` | Re-run setup (e.g. to add API keys, or after fixing a missing tool) |

**Your edits are safe:** if you changed a skill and an update changes it too, your version is kept and the differences are saved to `~/.video-skills/conflicts/` for you to review.

---

## 💬 Prompts to Try

Here are copy-paste prompts you can give your AI agent:

### 📱 Quick Reel / Short
```text
Edit videos/sample/raw/take1.mp4 into a punchy 9:16 vertical reel for Instagram with animated captions.
```
*What happens:* Isolates your voice, trims pauses, adds dynamic captions, and exports a 9:16 4K video.

### 💻 Tech Walkthrough / Screencast
```text
Edit videos/tutorial/raw/screen.mov into a YouTube tutorial with modern tech colors and clean lower-third titles.
```
*What happens:* Puts focus on your demo screen, adds lower-third titles, and removes keyboard clatter.

### 🎙️ Talking-Head / Interview
```text
Make a clean YouTube video from videos/interview/raw/pod.mp4 with warm cinematic colors and natural pauses.
```
*What happens:* Applies cinematic color grading, keeps conversational breathing room, and balances background music.

### 🎯 Full Production Brief
<details>
<summary><b>Click to view an advanced production prompt</b></summary>

```text
Edit videos/finance-01/raw/pitch.mp4 into a high-retention breakdown:
- Format: Split-screen (creator on left, dynamic graphics on right).
- Look: Warm cinematic grade with soft highlights.
- Captions: Poppins bold font, pop key words when mentioned.
- Sound: Remove background room noise, duck music during speech, and add subtle paper slides on graphic reveals.
- Delivery: 9:16 vertical UHD 4K.
```
</details>

---

## ✨ What It Does For You

- ✂️ **Cuts Dead Air Naturally**: Scans your voice waveform to remove awkward pauses and filler silences without making you sound rushed.
- 🗣️ **Crystal-Clear Voice**: Automatically removes AC hum, echo, and background noise so your speech sounds like it was recorded in a studio.
- 🔤 **Punchy, Readable Captions**: Adds modern animated captions (using clear fonts like Inter, Poppins, or DM Sans) with zero blurry shadows.
- 🎨 **Natural, Vibrant Colors**: Uses studio color presets (warm film, modern tech, clean documentary) that look great on any phone or screen.
- 🧠 **Remembers Your Brand**: Saves your social handles, colors, fonts, and logo in `brand/MEMO.md` so you only set them once.
- 🎵 **Offline Sound Effects**: Includes 19 tactile sound effects (pops, clicks, whooshes, page turns) that work offline without paid API credits.
- 🚦 **You're Always in Control**: The pipeline pauses at key milestones to show you visual previews and asks for your approval before final rendering.

---

## 📁 How Your Workspace is Organized

Your creative workspace stays clean and organized:

```text
📂 YOUR VIDEO WORKSPACE (~/VideoWorkspace)
├── brand/            # Your handles, logos, fonts, and brand colors (set once, reused forever)
├── references/       # Inspiration clips, style links, or reference videos
├── sound-palette/    # 19 built-in clicks, pops, whooshes, and transitions
└── videos/<id>/      # Your videos:
    ├── raw/          # Put your original camera or screen recordings here
    ├── hyperframes/  # Visual layout templates and graphic animations
    └── processed/    # Your finished, polished 4K videos appear here
```

---

## 💻 System Requirements

The installer tells you if anything here is missing. Node.js 22 and whisper.cpp are installed for you (privately, no admin rights) where your system doesn't have them.

| System | You install first | Installed for you |
|---|---|---|
| **macOS** | [Homebrew](https://brew.sh) | Node.js, FFmpeg, SoX, whisper.cpp (via Homebrew), DeepFilterNet |
| **Ubuntu / Debian** | `sudo apt-get install -y ffmpeg sox libsox-fmt-all libgomp1 python3-venv curl git` | Node.js 22, whisper.cpp, DeepFilterNet |
| **Fedora** | `sudo dnf install -y ffmpeg-free sox libgomp python3 git` | Node.js 22, whisper.cpp, DeepFilterNet |
| **Windows** | `winget install --id Git.Git -e` plus `Python.Python.3.12`, `Gyan.FFmpeg`, `ChrisBagwell.SoX` | Node.js 22, whisper.cpp, DeepFilterNet |
| **Windows (WSL2)** | the Ubuntu line, inside WSL | as Ubuntu |

Everything lives in `~/.video-skills/` and `~/.config/video-skills/`; your workspace only holds your own files. Rendering uses Chrome (downloaded automatically on Intel/AMD machines; on Linux ARM, install Chromium and set `HYPERFRAMES_BROWSER_PATH`).

<details>
<summary><b>Manual install without the package manager (no updates or rollback)</b></summary>

```bash
git clone https://github.com/mg-studio-india/video-editing-skill.git ~/video-editing-skill
cd ~/VideoWorkspace && bash ~/video-editing-skill/install.sh
```
</details>

<details>
<summary><b>Publishing a release (maintainers)</b></summary>

Work on a `release/vX.Y.Z` branch, then:
```bash
bash tools/test-package-manager.sh
python3 tools/release.py X.Y.Z --note "What users get"
```
Run `release.py` without `--push` on the release branch, then open a pull request to `main`: CI (`.github/workflows/install.yml`) installs and tests on Ubuntu, macOS and Windows for every PR, and only then. After the merge, publish: `git push origin vX.Y.Z && gh release create vX.Y.Z --notes-file <(sed -n '/## \[X.Y.Z\]/,/^## \[/p' CHANGELOG.md)`.
</details>

---

## ⚙️ Under the Hood (Technical Details)

<details>
<summary><b>Click to expand: The 6 Quality Review Steps (Gate 1 to Gate 6)</b></summary>

Rather than rendering blindly in one shot, the pipeline walks through 6 checkpoints:
1. **Gate 1 (Spec & Goal Audit)**: Checks your instructions, desired resolution (4K default), and brand preferences.
2. **Gate 2 (Footage & Audio Analysis)**: Transcribes speech accurately, audits speech pace, and matches reference styles.
3. **Gate 3 (Story & Layout Plan)**: Designs the hook (first 0–3 seconds), pacing, and visual layout (full screen, split screen, or picture-in-picture).
4. **Gate 4 (Rough Cut & Silence Trimming)**: Trims dead air to a natural 0.25–0.30s breath margin and shows you a `PAPER-CUT.md` edit list.
5. **Gate 5 (Captions & Typography Check)**: Generates a snapshot of your captions and fonts over your video for you to approve.
6. **Gate 6 (Final 4K Master Render)**: Encodes crisp 4K video, masters audio volume (-14 LUFS broadcast standard), and checks for any glitch frames.

</details>

<details>
<summary><b>Click to expand: Cinema Color Presets (`grade.py`)</b></summary>

Includes 10 built-in color grades:
- `kodak-portra`: Warm, golden skin tones with soft creamy highlights.
- `hollywood-teal`: High-contrast blockbuster look with teal shadows.
- `modern-tech`: Crisp, clean shadows with cool tech accents.
- `studio-clean`: Color-accurate, natural neutral look for everyday videos.
- `vox-doc`: Documentary style with deep blacks and rich contrast.
- `magnates-gold`: Rich bronze and gold tones for business and finance.
- `fuji-pro`: Emerald greens and soft sky blues.
- `vibrant-pop`: Punchy, high-saturation colors for viral reels.
- `moody-film`: Low-key dramatic shadow aesthetics.
- `nordic-cold`: Desaturated blue undertones for serious stories.

</details>

<details>
<summary><b>Click to expand: Typography & Caption Standards</b></summary>

- **5 Screen-Tested Fonts**: `DM Sans`, `Inter`, `Poppins`, `Google Sans`, and `Roboto` (from regular 400 to emphatic 900 Black).
- **Crisp Vector Captions**: Zero blurry drop shadows by default so text stays readable on any background (customizable if you prefer shadows).
- **Animation Modes**: `weight-shift` (word-by-word bold highlighting) or `caption-highlight` (neon bar sweeps).

</details>

<details>
<summary><b>Click to expand: Dead-Air Elimination vs. Speech Stretching</b></summary>

Automated speech-to-text models (like Whisper) often stretch word timestamps over pauses, hiding dead air. The pipeline checks the actual audio waveform loudness (`dead-air.py`) to find real silences, compressing pauses over 0.40s down to natural 0.25–0.30s conversational gaps.

</details>

<details>
<summary><b>Click to expand: Color Consistency & File Size (SDR vs HDR)</b></summary>

Most phone cameras shoot in HDR, which can cause washed-out colors on web players and generate massive 30 GB temporary caches. By default, the pipeline renders in universal Standard Dynamic Range (SDR with BT.709 tags), keeping files small (~2 GB cache) and colors accurate across all devices. HDR mode can be enabled with `--hdr`.

</details>

<details>
<summary><b>Click to expand: Persistent Brand Memory (`brand/MEMO.md`)</b></summary>

Stores your channel details in `brand/MEMO.md`. Your agent reads and updates this automatically:
```bash
# View saved brand settings
python3 "$ENG/scripts/memo.py" get --json

# Update your Instagram handle
python3 "$ENG/scripts/memo.py" set "Instagram" "@your_channel"
```

</details>

<details>
<summary><b>Click to expand: Style Blueprint Library (`video-reference-match`)</b></summary>

Includes 50 pre-analyzed style blueprints (`B01`–`B50`). When you start a project, the agent can recommend matching layouts, cut pacing, and caption styles based on successful creator formats.

</details>

---

## 🛡️ Quality Promises

- **No Awkward Pauses**: Dead air is detected from sound waveforms, not guessed from transcripts.
- **No Blurry Text**: Captions and graphics stay vector-sharp on all screen sizes.
- **Face Protection**: Text cards and overlays never cover the speaker's face or forehead.
- **Proper Volume**: Speech is mastered to clear, standard loudness (-14 LUFS) so viewers never have to adjust their volume.
- **Consistent Colors**: Looks identical whether viewed on an iPhone, Mac, Android, or PC.

---

## 📜 License

The engine and scripts are licensed under the **MIT License**.  
Bundled open-source typography (DM Sans, Poppins, Inter, Noto Sans Devanagari) is distributed under the **SIL Open Font License**.  
Full license texts reside in [`LICENSES/`](file:///Users/mahesh/lmc/video-editing-skill/LICENSES).
