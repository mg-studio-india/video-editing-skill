# Setup

About 30 to 45 minutes, most of it downloads. You need a Mac and a coding agent that can run shell commands, read and
edit files, and look at images: Claude Code by default (the desktop app or `claude` in a terminal), or another agent
(see "Using other agents"). Editing full videos uses a lot of usage; set up on the latest model, edit on whichever suits.

## 1. Install

Make the folder you will open in Claude Code, and run the installer from inside it:

```bash
mkdir -p ~/VideoEditing && cd ~/VideoEditing
unzip ~/Downloads/video-editor-skills-complete.zip -d ~/Downloads
bash ~/Downloads/video-editor-skills/install.sh
```

Run it from your project folder, not from inside the package (it refuses if you do). If Homebrew is missing, it stops
and points you to https://brew.sh: install that, open a new terminal, and run it again.

### What the installer does

| Step | Result |
|---|---|
| 1. System tools | `node` (22+), `ffmpeg`, `whisper-cpp` via Homebrew |
| 2. Whisper model | `ggml-large-v3.bin` (~3 GB) in `~/.cache/whisper.cpp`, shared by all projects |
| 3. Python | `./.venv` with numpy, Pillow, OpenCV 4, auto-editor, google-genai |
| 4. Skills and folders | the 18 skills (`video-*` and `business-reels-style`) in `~/.agents/skills/`, shared by every project and agent, linked into `~/.claude/skills/` when Claude Code is installed and into any `--link` folders; `./videos/`, `./videos/_shared/`, `./references/`, `./LICENSES/` |
| 5. HyperFrames | the CLI pinned in `./package.json`, its Chrome, its skills (`hyperframes-core`, `media-use`, `embedded-captions` and their dependencies), a local GSAP copy for offline renders |
| 6. Accounts and keys | HeyGen sign-in, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, your main spoken language, all in `./.env` |
| 7. Agent wiring | `./agent-env.sh` (source it before starting any agent), a marked block in `./AGENTS.md`, and for Claude Code `./.claude/settings.local.json` (every session gets the `.venv`, HyperFrames, keys and paths) |
| 8. Checks | transcription, HeyGen, Gemini model names, and the 128 engine tests |

Anything unfinished is listed at the end under "To finish later". The installer is safe to run again: finished steps are
skipped, your keys are kept, and installed skills are never overwritten.

### Options

| Option | Use |
|---|---|
| `--skills-dir DIR` | where the skills go (default `~/.agents/skills`, shared; a relative path such as `.claude/skills` installs for this project only) |
| `--no-claude-link` | don't link the skills into `~/.claude/skills` (done automatically when Claude Code is installed) |
| `--link DIR` | also expose the skills in DIR as links to the one copy (repeatable), so several agents share them |
| `--no-claude-settings` | skip `.claude/settings.local.json` (it is written automatically when `.claude` is a target) |
| `--model large-v3-turbo` | a faster, slightly less accurate whisper model (`none` skips the download) |
| `--update-skills` | replace installed skills with this package's versions; the old ones are backed up first |
| `--yes` | no questions: keeps existing keys, skips the ones not already set |
| `--no-system` | you installed node, ffmpeg and whisper-cpp yourself |
| `--no-browser` | skip HyperFrames' Chrome download |
| `--skip-pip`, `--skip-tests` | reuse the existing `.venv`; skip the tests |
| `--hf-version V` | pin a different HyperFrames version (the default is the one the skills were tested with) |

## 2. Accounts and keys

| What | Needed for | How |
|---|---|---|
| HeyGen | all sound effects and music (HeyGen's sound library) | the installer offers a browser sign-in; later: `npx hyperframes auth login` |
| Google Gemini key | generated shots: Veo video, Gemini Flash Image stills | https://aistudio.google.com/apikey |
| OpenRouter key | fallback for generated images | https://openrouter.ai/keys |

Without HeyGen there is no music, and sound effects only come from HyperFrames' 21 built-in sounds (Claude asks first).
Without the Gemini key, everything works except generated shots.

Keys live in `~/VideoEditing/.env`, readable only by you. To change one, edit `.env` (or delete the line) and run the
installer again with `--skip-pip --skip-tests`, so Claude Code's settings pick up the change. Never share or commit
`.env` or `.claude/settings.local.json`; the installer adds both to `.gitignore`.

## 3. First run in Claude Code

1. Open Claude Code in `~/VideoEditing`: Local, this folder, the latest model, permissions on Auto.
2. Type: **"Run the video-pipeline setup check and fix anything it finds."**
3. Start a **new thread** (skills load when a thread starts).
4. Put a 30 to 60 second clip in `videos/test-01/raw/` and use the first prompt in `PROMPTS.md`.

## Using other agents

The skills are plain Agent Skills folders and find their engine through `VIDEO_ENGINE` and `VIDEO_SKILLS`, so any agent
that can run shell commands, edit files and view images can use them.

1. Find the folder your agent loads skills from (its documentation), then install there, linking Claude Code too if you
   use more than one: `bash ~/Downloads/video-editor-skills/install.sh --link <that folder>` (the skills stay in
   `~/.agents/skills`; Claude Code's `~/.claude/skills` is linked automatically).
   With links, a rule saved through one agent applies to all of them.
2. In the terminal you start that agent from, run `source agent-env.sh` first. Claude Code does not need this; its
   settings file does it.
3. Agents that read project instructions but not skills get pointed to `video-pipeline/SKILL.md` by the block the
   installer adds to `AGENTS.md`.

The workflow (gates, evidence rules, "save this to the skill") was tested with Claude; other models may follow it less
closely, so watch the first edit's gates.

## 4. Check it yourself

From `~/VideoEditing`, after `source agent-env.sh` (which also loads your keys and paths):

```bash
E="$VIDEO_ENGINE/scripts"
python $E/watch.py check              # ffmpeg, whisper-cli and the model all OK
python $E/heygen-sound.py --check     # media-use found, HeyGen signed in
python $E/generate.py models          # the Veo and Gemini image models exist on your key
npx hyperframes doctor                # HyperFrames' own checks
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| The agent doesn't use the skills | start it in the project folder, from a new session; for non-Claude agents install into the folder it scans (`--skills-dir`) and `source agent-env.sh` first |
| "engine not found" / `VIDEO_ENGINE` empty | `source agent-env.sh` in the agent's terminal, or re-run the installer |
| `whisper-cli` missing | `brew install whisper-cpp` |
| Whisper model missing | run the installer again (or `--model large-v3-turbo` for a smaller download) |
| Transcript in the wrong language, or translated | set `WATCH_WHISPER_LANG` in `.env` (`en`, `hi`) and re-run the installer with `--skip-pip --skip-tests` |
| `generate.py models` says NOT FOUND | Google renamed a model: add `VEO_MODEL="<a listed name>"` (or `GEMINI_IMAGE_MODEL`) to `.env`, re-run the installer |
| HeyGen not signed in | `npx hyperframes auth login`, then `heygen-sound.py --check` |
| "no Haar face detector" when making a Short | OpenCV 5 got installed: `.venv/bin/python -m pip install "opencv-python-headless>=4.9,<5"` |
| HyperFrames cannot render or snapshot | `npx hyperframes browser ensure`, then `npx hyperframes doctor` |
| Keys missing inside the agent | Claude Code: re-run the installer with `--skip-pip --skip-tests`; other agents: `source agent-env.sh` before starting them |
| Tests fail at the end | open `/tmp/video-skills-tests.log` and paste it into Claude Code |
| A render is very slow | that is normal on CPU for 4K; use `--resolution portrait` for Shorts, and see the render skill for long videos |

## Updating

- **A new version of this package:** unzip it and run its `install.sh --update-skills` from your project folder. Your
  old skills are backed up to `~/.agents/skills-backup-<date>`; ask your agent to merge any rules you had saved
  back in. Installs from before the `video-` names are moved to `*-legacy-backup-<date>` automatically.
- **HyperFrames:** `npx hyperframes@latest upgrade --project . --check` reports whether a newer version exists. Upgrade
  only when you want to, then run `npx hyperframes check` on a recent project.

## Removing it

- **One project:** delete its folder (`agent-env.sh`, keys, footage and project state are inside it). The shared skills
  stay for your other projects.
- **Everything:** also delete the shared pieces: our skills in `~/.agents/skills/` (`video-*` and
  `business-reels-style`) and their links in `~/.claude/skills/`; HyperFrames' skills in both folders (`hyperframes*`,
  `media-use`, `embedded-captions`, `talking-head-recut`, `motion-graphics`) if nothing else uses them; the whisper model
  in `~/.cache/whisper.cpp`; and the Homebrew tools.
