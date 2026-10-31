# Setup check

The installer (`video-skills`, from the one-line install) does this; `video-skills setup` re-runs it and keeps completed steps. `video-skills doctor` checks skill links. Commands use the selected video folder as `$ROOT`; pipeline work stays under `$ROOT/.video-pipeline`. The agent shell needs the configured shared engine environment, `VIDEO_ENGINE`, `VIDEO_ENGINE_DIR`, and `VIDEO_ENGINE_PYTHON`. Start it after `source agent-env.sh` (Claude Code also reads `.claude/settings.local.json`). Tools are installed once in the shared engine; FFmpeg comes from the system and the Whisper model stays in the shared user cache.

| Needs | Check | Install when missing |
|---|---|---|
| Node.js 22+ | `node -v` | `brew install node`; on Linux/Windows install.sh puts a private Node 22 in `$VIDEO_ENGINE_DIR/node` (on PATH via `agent-env.sh` and a marked shell-rc line) |
| HyperFrames CLI | `"$VIDEO_ENGINE_DIR/node_modules/.bin/hyperframes" --version`, then `doctor` | install through the video-skills setup into the configured engine; never use `npx` during an edit |
| HyperFrames composition catalog | `test -d "$VIDEO_COMPOSITIONS"` | installed once by video-skills setup into the shared engine; each project stages only its selected blocks |
| ffmpeg + ffprobe | `ffmpeg -version` | `brew install ffmpeg` · `sudo apt-get install -y ffmpeg` · `sudo dnf install -y ffmpeg-free` · `winget install --id Gyan.FFmpeg -e` |
| whisper.cpp + model | `"$VIDEO_ENGINE_PYTHON" "$ENG/scripts/watch.py" check` | `brew install whisper-cpp`; on Linux/Windows install.sh downloads the prebuilt release into the shared `$VIDEO_ENGINE_DIR/whisper`; the model is shared in `~/.cache/whisper.cpp` |
| Python 3 + numpy | `"$VIDEO_ENGINE_PYTHON" -c "import numpy"` | installed once from `engine/requirements.txt` into the shared engine `.venv` |
| auto-editor | `auto-editor --version` | installed from `engine/requirements.txt` into the engine `.venv` |
| Pillow | `"$VIDEO_ENGINE_PYTHON" -c "import PIL"` | installed once from `engine/requirements.txt` into the shared engine `.venv` |
| OpenCV | `"$VIDEO_ENGINE_PYTHON" -c "import cv2"` | installed once from `engine/requirements.txt` into the shared engine `.venv` |
| PDF text and visual review | `"$VIDEO_ENGINE_PYTHON" -c "import pypdf, pypdfium2"` | installed once from `engine/requirements.txt` into the shared engine `.venv` |
| Google Chrome | snapshots and page captures run in it | google.com/chrome |
| HyperFrames skills | check that the installed `hyperframes-*` skills are available to the agent | install through the supported video-skills setup, not an ad hoc package command |
| GSAP, local copy | `ls "$ENG/assets/vendor/gsap.min.js"` | repair with the pinned video-skills setup; staging fails if the local file is missing |
| HeyGen sign-in (only when requested) | `"$VIDEO_ENGINE_PYTHON" "$ENG/scripts/heygen-sound.py" --check` | use the configured shared HyperFrames CLI or `HEYGEN_API_KEY`; the pipeline does not sign in or fetch sounds automatically |
| AudioCraft (only if asked) | `python3 -c "import audiocraft"` | `pip install audiocraft` (pulls torch; weights are non-commercial, see `video-sound-design`) |
| Gemini API key (optional) | `echo $GEMINI_API_KEY` set | `video-generate` / `video-omni-restyle` (Veo, Gemini Flash Image); then `pip install google-genai` |
| OpenRouter key (optional) | `echo $OPENROUTER_API_KEY` set | the generation fallback |

Run repository checks when the user requests verification or when the task instructions require it.
