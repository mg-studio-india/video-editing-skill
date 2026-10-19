# Setup check

`install.sh` (in the package, run from the project folder) does all of this; re-running it is the simplest fix, since
finished steps are skipped and installed skills are kept. Commands assume the project folder as the working directory;
`npx hyperframes` uses the copy pinned in `package.json`. The agent's shell needs `.venv`, the keys and `VIDEO_ENGINE`:
start the agent after `source agent-env.sh` (Claude Code also gets them from `.claude/settings.local.json`). Check each line, install what is missing (ask before anything needing admin rights).

| Needs | Check | Install when missing |
|---|---|---|
| Node.js 22+ | `node -v` | `brew install node`; on Linux/Windows install.sh puts a private Node 22 in `$VIDEO_ENGINE_DIR/node` (on PATH via `agent-env.sh` and a marked shell-rc line) |
| HyperFrames CLI | `npx hyperframes --version`, then `npx hyperframes doctor` | comes through npx; `doctor` lists anything else |
| ffmpeg + ffprobe | `ffmpeg -version` | `brew install ffmpeg` · `sudo apt-get install -y ffmpeg` · `sudo dnf install -y ffmpeg-free` · `winget install --id Gyan.FFmpeg -e` |
| whisper.cpp + model | `python3 $ENG/scripts/watch.py check` | `brew install whisper-cpp`; on Linux/Windows install.sh downloads the prebuilt release into `$VIDEO_ENGINE_DIR/whisper` and sets `WATCH_WHISPER_CPP_BIN`; model steps in the `video-transcribe` skill |
| Python 3 + numpy | `python3 -c "import numpy"` | `python3 -m pip install numpy` |
| auto-editor | `auto-editor --version` | `pip install auto-editor` (speech chunks for the cut) |
| Pillow (optional) | `python3 -c "import PIL"` | `python3 -m pip install pillow` (contact sheets) |
| OpenCV | `python3 -c "import cv2"` | `python3 -m pip install 'opencv-python-headless>=4.9,<5'` (face-tracked reframing) |
| Google Chrome | snapshots and page captures run in it | google.com/chrome |
| HyperFrames skills | `ls ~/.claude/skills/hyperframes-core ~/.agents/skills/hyperframes-core` | `npx hyperframes skills update hyperframes-core` (installs the core set) |
| GSAP, local copy | `ls $ENG/assets/vendor/gsap.min.js` | `mkdir -p $ENG/assets/vendor && curl -sL https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js -o $ENG/assets/vendor/gsap.min.js` (renders then work offline) |
| HeyGen sign-in | `python3 $ENG/scripts/heygen-sound.py --check` | `npx hyperframes auth login` (or `HEYGEN_API_KEY`); the sound library needs it |
| AudioCraft (only if asked) | `python3 -c "import audiocraft"` | `pip install audiocraft` (pulls torch; weights are non-commercial, see `video-sound-design`) |
| Gemini API key (optional) | `echo $GEMINI_API_KEY` set | `video-generate` / `video-omni-restyle` (Veo, Gemini Flash Image); then `pip install google-genai` |
| OpenRouter key (optional) | `echo $OPENROUTER_API_KEY` set | the generation fallback |

Tests (one suite, `$ENG/tests`, covering the engine and the scripts owned by single skills): `cd "$ENG" && python3 -m unittest discover -s tests -t .`. It
must end with `OK` (apart from known failures noted in the run). Run it after touching any engine script or a skill-owned script.
