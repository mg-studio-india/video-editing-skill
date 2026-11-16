# 🎬 AI Video Editor for Coding Agents

> Turn raw footage into a polished, research-backed video with your coding agent: studio-clean voice, Hinglish
> captions in sync, tight cuts, HyperFrames graphics, one approval before render.

[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## 🚀 Quick start

**1. Install** (in the folder you will edit in):

```bash
curl -fsSL https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.sh | bash
```

Windows PowerShell: `irm https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.ps1 | iex`.
Details and options: [SETUP.md](SETUP.md).

**Verify** before the first edit: `bash tools/test-package-manager.sh` sets nothing up unless you add `--fix`, checks
every tool, model and skill, and renders a sample edit end to end. `READY` means your edits will come out right.

**2. Add footage:** `videos/<name>/raw/<clip>.mp4`. Optional: look references in `videos/<name>/references/`, your
brand files (logo, colours, fonts, guide) in `brand/`.

**3. Ask your agent** in a new conversation:

> "Edit videos/my-reel into a 9:16 Instagram Reel. Research the topic and add graphics that explain it."

More in [PROMPTS.md](PROMPTS.md).

## ✨ What you get by default

| | |
|---|---|
| 🎧 **Studio-clean voice** | Two passes, each run once: echo and noise removed (WPE + DeepFilterNet, strength measured per recording), then polish, de-ess, gentle compression and −14 LUFS mastering. A before/after clip to listen to before you approve. |
| 🗣️ **Hinglish transcript** | Hindi and English exactly as spoken, in Roman script, from a Hinglish Whisper model. Words are snapped to the real speech, so captions, cuts and graphics land on the right word. |
| ✂️ **Tight, word-safe cuts** | Retakes, restarts, fillers and dead air removed; every cut sits in silence, so no word is clipped. Always ends with a held frame that fades to black. |
| 🔎 **Research → graphics, sound, b-roll** | The agent researches your topic and the numbers you mention, then builds charts, headlines, counters and b-roll from sourced facts, plus a few purposeful sound effects. |
| 🧩 **HyperFrames catalog first** | Every graphic comes from the installed HyperFrames catalog (searchable index) before anything custom is built. |
| 💬 **Simple keyword captions** | Semi-bold, sentence case, white; only the keywords light up in the accent colour with a small pop. |
| 🎨 **Default styles** | `clean-creator`, `business-explainer`, `tech-minimal`, `cinematic-story`, or one matched to your references. Brand rules come only from your own files; nothing is assumed. |
| ✅ **You stay in control** | One review (cut, style, every graphic with its source, sounds), one approval, then render, verification and `Exports/<name>-vN.mp4`. |

## 📁 Workspace

```text
YOUR WORKSPACE
├── brand/                     # optional: your logo, colours, fonts, brand guide (shared by every video)
├── sound-palette/             # 19 offline sound effects
└── videos/<name>/
    ├── raw/                   # your original footage (never modified)
    ├── references/            # optional: reels or images whose look you want
    ├── .video-pipeline/       # working files: cleaned audio, transcript, cut, research, storyboard, reports
    └── Exports/               # verified, versioned results
```

## 🧠 The skills

| Skill | Role |
|---|---|
| `video-pipeline` | the entry point: analyze → research → storyboard → approve → assemble |
| `video-watch` | studies reference videos (and any video) as measurements and frames |
| `video-style` | picks a default style, applies brand files, grades and fixes footage, sets the format |
| `video-audio` | the two audio passes |
| `video-transcribe` | Hinglish transcripts in sync; fixing misheard names |
| `video-researcher` | topic research → graphics, sounds and b-roll plans with sources |
| `video-plan-storyboard` | the storyboard, built from the HyperFrames catalog |
| `video-captions` | keyword captions |
| `video-generate` | paid AI b-roll, only when you agree |

## 🔄 Updates

`video-skills check` · `video-skills update` · `video-skills changelog` · `video-skills rollback` · `video-skills doctor`.
Your own skill edits are kept; conflicting updates are saved as a diff for review.

## 📜 License

[MIT](LICENSE). Bundled assets and downloaded models (Hinglish Whisper: Apache-2.0; DeepFilterNet: MIT/Apache-2.0)
have their own terms.
