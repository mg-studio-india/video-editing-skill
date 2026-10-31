# 🎬 AI Video Editor for Coding Agents

> Turn your footage into a thoughtful, polished video with your coding agent. Shape the edit around what is really in the footage, bring in your references and brand, and review the plan before the final render.

[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

---

### ⚡ Quick Navigation

[🚀 Quick Start](#-quick-start-3-steps) • [🔄 Staying Up to Date](#-staying-up-to-date) • [💬 Prompts to Try](#-prompts-to-try) • [✨ What It Does For You](#-what-it-does-for-you) • [📁 Your Workspace](#-how-your-workspace-is-organized) • [💻 Platform Support](#-platform-support)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install

Create or open the folder you want to use for video work. Open a terminal in that folder and paste **one line**.

**macOS, Linux, WSL 2, or Git Bash:**

```bash
curl -fsSL https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.sh | bash
```

**Windows PowerShell:**

```powershell
irm https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.ps1 | iex
```

The installer sets up the editing tools and connects the skills to your coding agent. If something your computer needs is missing, it tells you what to install and what to run next.

### Step 2: Add your footage, references, and brand

Put your original video in `videos/<project-name>/raw/`. Add any inspiration videos or images to `references/`, and your logo and brand guide to `brand/`. The agent checks the materials before suggesting the edit.

### Step 3: Tell your agent what you want

Open your coding agent in the workspace and start a fresh conversation. For example:

> “Edit `videos/my-first-video/raw/take1.mp4` into a 9:16 Instagram Reel. Keep the product demonstration, including the silent shots. Look at my references and brand guide, then show me the edit plan before rendering.”

The agent reviews the footage and asks one short batch of questions about anything you have not decided, such as what to keep, where the video will be posted, how to frame it, captions, or sound. You approve the plan before the final edit is assembled.

---

## 🔄 Staying Up to Date

Your agent can let you know when an update is available. Nothing updates without your choice.

| Command | What it does |
|---|---|
| `video-skills check` | Check whether a new version is available |
| `video-skills changelog` | See what changed |
| `video-skills update` | Update the pipeline |
| `video-skills rollback` | Return to an earlier version |
| `video-skills doctor` | Check that the installation is connected properly |

Your personal skill edits are kept during updates. If an update changes the same skill, the package manager saves the differences for you to review.

---

## 💬 Prompts to Try

Choose a prompt that fits your footage, change the parts in brackets, and give it to your agent. [PROMPTS.md](PROMPTS.md) has complete prompts for ten kinds of video, including product showcases, interviews, tutorials, documentaries, social cutdowns, and reference-led films.

### 📱 Social Reel

```text
Make a 9:16 Reel from [video]. Find the strongest complete moments in the footage and keep the point clear. Check whether the crop keeps the important action in frame. Keep the current simple phrase captions. Show me the proposed cut before rendering.
```

### 📦 Product Showcase

```text
Create a visual-first showcase from [video]. Build the edit around the product actions and details that are actually visible. Keep the silent product shots; do not invent features or claims. Review my references and brand guide, then show me the plan before rendering.
```

### 💻 Tutorial or Screen Recording

```text
Make a [platform / aspect] tutorial from [video]. Keep the real interface legible and the steps in order. Use callouts only for controls and instructions that are actually shown or spoken. Show me any proposed crop or zoom before rendering.
```

### 🎙️ Interview or Conversation

```text
Find a clear, self-contained exchange in [video]. Keep enough of each question and answer to preserve its meaning, and use reactions only when they are in the footage. Show me the selected passage and cut before rendering.
```

---

## ✨ What It Does For You

- 🎬 **Finds the edit in your footage:** The story follows what the camera recorded and what people actually said. Silent product moments stay in unless you approve removing them.
- 📚 **Uses your references and brand:** References guide the visual feel; your brand guide sets the rules for color, type, logos, and other assets.
- 🧭 **Offers ideas when you have no reference:** The pipeline can suggest visual directions from its style index and waits for you to choose one.
- 💬 **Keeps you in control:** The agent asks about unanswered choices, shows you the plan, and waits for approval before rendering.
- 🔤 **Keeps captions simple by default:** The current phrase-style captions stay in place unless you ask for a different treatment.
- 🎧 **Treats audio with care:** Strong dereverb is selected by default to reduce room echo. The agent should review the result because some echo can remain and processing can affect speech.
- ✨ **Uses motion with purpose:** The HyperFrames catalog is installed once and shared across projects. Only the few blocks chosen for an edit are staged with that video's hidden working files.

---

## 📁 How Your Workspace is Organized

The workspace stays tidy. Your originals remain in place, pipeline work is kept out of sight, and finished videos go in one place.

```text
📂 YOUR VIDEO WORKSPACE
├── brand/                 # Your brand guide, logo, and approved assets
├── references/            # Inspiration videos, images, or PDFs
├── videos/<project>/raw/  # Your original camera or screen recordings
├── .video-pipeline/       # Hidden analysis and review files
└── Exports/               # Verified, versioned final videos
```

The folder you open for the edit is the project's workspace. The agent reads the `brand/` and `references/` folders in that workspace and keeps its working files and exports there. Editing tools are shared on your computer; each video folder keeps the files for that edit. If you provide a different project folder, put that project's references and brand materials in it too.

---

## 💻 Platform Support

The one-line installer is available for:

- **macOS** — paste the Bash command above in Terminal. If Homebrew is missing, the installer explains how to add it.
- **Linux** — paste the Bash command above in a terminal. Ubuntu/Debian, Fedora, and Arch-based systems are supported; missing system tools are reported with the command to install them.
- **Windows** — paste the PowerShell command above. It checks for Git for Windows, Python, FFmpeg, and SoX, and prints the `winget` commands for anything missing.
- **WSL 2** — use the Bash installer inside your Linux distribution.

Windows runs the installer through Git Bash. The install workflow covers Ubuntu, macOS, and Windows. On Linux ARM, the installer may ask you to provide a local Chromium browser for video rendering.

---

## 📜 License

This project is distributed under the [MIT License](LICENSE). Some bundled assets may have separate terms; check their accompanying license information before redistributing them.
