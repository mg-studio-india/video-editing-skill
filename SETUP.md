# Setup

About 20-40 minutes, mostly downloads. You need macOS, Linux (or WSL 2) or Windows with Git Bash, and a coding agent
that can run shell commands, edit files and look at images (Claude Code by default).

## 1. Install

From the folder you will edit in:

```bash
mkdir -p ~/VideoEditing && cd ~/VideoEditing
curl -fsSL https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.sh | bash
```

Without the package manager: `bash /path/to/video-editing-skill/install.sh` from your workspace folder.

| Step | Result |
|---|---|
| 1. System tools | Node 22, FFmpeg, whisper.cpp, SoX (Homebrew / your package manager; missing ones are listed with the command) |
| 2. Models | Hinglish Whisper model `ggml-apex-hinglish-q8_0.bin` (~850 MB, Apache-2.0, writes Hindi/English speech in Roman script), DeepFilterNet 3 (voice denoise), YuNet (face-aware reframe), all shared in `~/.cache` / `~/.config/video-skills` |
| 3. Python | the engine venv in `~/.video-skills/engine/.venv` (numpy, scipy, soundfile, nara_wpe, OpenCV, Pillow, PDF readers) |
| 4. Skills | 9 skills in `~/.agents/skills/` (linked into `~/.claude/skills/`); 1.x skills that were merged are removed |
| 5. HyperFrames | pinned CLI + Chrome + GSAP in the engine, the full composition catalog in `~/.video-skills/engine/compositions`, indexed for search (`catalog.json`) |
| 6. Keys | optional `GEMINI_API_KEY` / `OPENROUTER_API_KEY` (generated b-roll), HeyGen sign-in (sound library), stored in `~/.config/video-skills/.env` |
| 7. Wiring | `~/.config/video-skills/agent-env.sh` for agents that need paths and keys in their shell |
| 8. Check | preflight: FFmpeg, whisper-cli, model, DeepFilterNet, catalog index |

Re-running is safe: finished steps are skipped, keys kept.

### Options

| Option | Use |
|---|---|
| `--model large-v3` | stock Whisper instead of the Hinglish model (Hindi is then decoded as Hindi and romanised) |
| `--skills-dir DIR`, `--link DIR`, `--no-claude-link` | where the skills go and which agent folders link to them |
| `--update-skills` | replace installed skills with this package's versions (old ones backed up) |
| `--clean-workspace` | opt-in: remove old engine plumbing (package.json, node_modules, .venv) from the workspace |
| `--yes`, `--no-system`, `--no-browser`, `--skip-pip`, `--hf-version V` | non-interactive; skip system tools / Chrome / pip; pin HyperFrames |

## 2. First run

1. Open your agent in the workspace folder and start a new conversation.
2. Ask: **"Run the video-pipeline setup check."** It runs `setup.py` and lists anything missing.
3. Put a 30-60 s clip in `videos/test/raw/` and use a prompt from `PROMPTS.md`.

## Verify before editing

```bash
bash tools/test-package-manager.sh                 # from the package; or: bash ~/.video-skills/engine/test-package-manager.sh
bash tools/test-package-manager.sh --quick         # tools, models, flags and skills only (~10 s)
bash tools/test-package-manager.sh --fix           # run the setup if something required is missing, then verify again
bash tools/test-package-manager.sh --package-only  # maintainers: the sandboxed package-manager test before a release
```

From the package folder the full run first tests the package manager in a throwaway sandbox (release, install,
update with a local edit, rollback, a release that drops a skill, doctor, uninstall; needs git and rsync). It then
renders a short sample edit through the real pipeline (spoken clip with echo and noise → analyze →
approve → assemble) and checks: audio cleaned once and aligned, Hinglish words with timing, the pause tightened, no cut
inside a word, a silent composition picture (no doubled voice), a catalog block staged, −14 LUFS, the render check
passing and the last frame black. `READY` (exit 0) means edits will work; fix every `FAIL` first. Add `--keep` to keep
the sample project for inspection.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Anything below | run `bash tools/test-package-manager.sh --fix` first; it names the exact problem |
| Transcript is English instead of Hinglish, or in Devanagari | the Hinglish model is missing: re-run setup (or set `WATCH_WHISPER_MODEL`); remove any old `WATCH_WHISPER_LANG=en` from `~/.config/video-skills/.env` |
| Words in captions are a little early/late | your whisper-cli lacks DTW: `brew upgrade whisper-cpp` (words are still snapped to the speech energy) |
| "DeepFilterNet is not installed" | re-run setup; or set `VIDEO_DEEPFILTER=/path/to/deep-filter` |
| "catalog index missing" | `"$VIDEO_ENGINE_PYTHON" "$VIDEO_ENGINE/scripts/catalog.py" build` |
| HyperFrames cannot render | `"$VIDEO_ENGINE_DIR/node_modules/.bin/hyperframes" browser ensure`, then `doctor` |
| Old `brand/MEMO.md` / `STYLE-GUIDE.md` | 1.x templates, now ignored: delete them; put your real brand files in `brand/` |
| The agent ignores the skills | start a new conversation in the workspace folder; other agents: `source agent-env.sh` first |

## Updating and removing

`video-skills update` / `rollback` / `doctor` manage versions. To remove everything: `video-skills uninstall --purge`,
then delete the Whisper model in `~/.cache/whisper.cpp` if nothing else uses it.
