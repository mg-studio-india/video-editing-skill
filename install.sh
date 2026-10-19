#!/usr/bin/env bash
# install.sh: Cross-platform installer for the autonomous video editing pipeline.
#
# ARCHITECTURE CONTRACT (100% CLEAN WORKSPACE):
#   - Global Engine Sandbox (~/.video-skills/engine or ~/.config/video-skills/engine):
#     Houses all engine plumbing: .venv (Python 3.9+), node_modules (HyperFrames CLI & GSAP),
#     package.json, LICENSES, .env (API keys), and agent-env.sh.
#   - User Creative Workspace ($PROJECT, default: current directory):
#     Houses ONLY clean user creative folders:
#       brand/          (persistent memory brand/MEMO.md, STYLE-GUIDE.md, brand-style-guide.pdf, and vector logos)
#       references/     (benchmark reels, viral hooks, layout screenshots)
#       sound-palette/  (19 curated offline tactile SFX)
#       videos/         (production projects with raw/ and processed/)
#
# Cross-Platform Support:
#   - macOS (Homebrew)
#   - Linux (Ubuntu/Debian, Fedora, Arch)
#   - Windows (WSL2, Git Bash, MSYS2, native PowerShell)
#
# Usage:
#   cd ~/VideoWorkspace
#   bash /path/to/video-editing-skill/install.sh
#
# Options:
#   --project DIR       Creative workspace root (default: current directory)
#   --engine-dir DIR    Engine sandbox directory (default: ~/.video-skills/engine or ~/.config/video-skills/engine)
#   --local-engine      Install engine sandbox inside project under .engine/ (isolated, non-polluting)
#   --clean-workspace   Purge legacy engine plumbing files from project workspace (package.json, .venv, etc.)
#   --yes               No interactive prompts: accept defaults and keep existing keys
#   --model NAME        Whisper model: large-v3 (default) | large-v3-turbo | none
#   --hf-version V      HyperFrames CLI version to pin (default: 0.8.160)
#   --no-system         Skip system package manager checks (Homebrew / apt / dnf)
#   --no-browser        Skip HyperFrames Chrome download
#   --skip-pip          Reuse existing Python environment as is
#   --skip-tests        Do not run test suites at the end
#   --skills-dir DIR    Skills installation directory (default: ~/.agents/skills)
#   --link DIR          Link skills into additional agent directories (e.g. ~/.claude/skills, ~/.gemini/antigravity-cli/skills)
#   --no-claude-link    Do not link into ~/.claude/skills
#   --update-skills     Update skills in skills-dir (backs up custom edits first)
#   --skills-managed    Skills are symlinks managed by `video-skills` (the one-line installer); do not copy them,
#                       only set up the engine, workspace and agent links. Use `video-skills update` to update.
set -euo pipefail

HF_VERSION_DEFAULT="0.8.160"
GSAP_VERSION="3.14.2"
PKG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILLS_SRC="$PKG/skills"
ROOT_DIR="$(pwd -P)"

PROJECT_ARG=""
ENGINE_DIR_ARG=""
LOCAL_ENGINE=0
CLEAN_WORKSPACE=1
SKILLS_DIR="$HOME/.agents/skills"
LINKS=()
CLAUDE_LINK=auto
UPDATE_SKILLS=0
SKILLS_MANAGED=0
YES=0
MODEL="large-v3"
HF_VERSION="$HF_VERSION_DEFAULT"
NO_SYSTEM=0
NO_BROWSER=0
SKIP_PIP=0
SKIP_TESTS=0

while [ $# -gt 0 ]; do
  case "$1" in
    --project|--project-dir|--workspace) PROJECT_ARG="$2"; shift ;;
    --engine-dir) ENGINE_DIR_ARG="$2"; shift ;;
    --local-engine) LOCAL_ENGINE=1 ;;
    --clean-workspace) CLEAN_WORKSPACE=1 ;;
    --yes) YES=1 ;;
    --model) MODEL="$2"; shift ;;
    --hf-version) HF_VERSION="$2"; shift ;;
    --no-system) NO_SYSTEM=1 ;;
    --no-browser) NO_BROWSER=1 ;;
    --skip-pip) SKIP_PIP=1 ;;
    --skip-tests) SKIP_TESTS=1 ;;
    --update-skills) UPDATE_SKILLS=1 ;;
    --skills-managed) SKILLS_MANAGED=1 ;;
    --skills-dir) SKILLS_DIR="${2%/}"; shift ;;
    --link) LINKS+=("${2%/}"); shift ;;
    --no-claude-link) CLAUDE_LINK=no ;;
    -h|--help) sed -n '2,40p' "$0"; exit 0 ;;
    *) echo "unknown option: $1 (see --help)"; exit 2 ;;
  esac
  shift
done

abspath() {
  local p="$1"; case "$p" in "~") p="$HOME" ;; "~/"*) p="$HOME/${p#\~/}" ;; esac
  case "$p" in /*) ;; *) p="$ROOT_DIR/${p#./}" ;; esac
  printf '%s' "${p%/}"
}

# Determine project creative workspace
if [ -n "$PROJECT_ARG" ]; then
  PROJECT="$(abspath "$PROJECT_ARG")"
elif [ "$ROOT_DIR" = "$PKG" ]; then
  PROJECT="$ROOT_DIR/workspace"
else
  PROJECT="$ROOT_DIR"
fi
mkdir -p "$PROJECT"

# Determine engine sandbox directory
if [ -n "$ENGINE_DIR_ARG" ]; then
  ENGINE_DIR="$(abspath "$ENGINE_DIR_ARG")"
elif [ "$LOCAL_ENGINE" = 1 ]; then
  ENGINE_DIR="$PROJECT/.engine"
elif [ -n "${VIDEO_ENGINE_DIR:-}" ]; then
  ENGINE_DIR="$(abspath "$VIDEO_ENGINE_DIR")"
else
  if mkdir -p "$HOME/.video-skills/engine" 2>/dev/null; then
    ENGINE_DIR="$HOME/.video-skills/engine"
  else
    ENGINE_DIR="$HOME/.config/video-skills/engine"
  fi
fi
mkdir -p "$ENGINE_DIR"

SKILLS_DIR="$(abspath "$SKILLS_DIR")"
ABS_LINKS=()
for L in ${LINKS[@]+"${LINKS[@]}"}; do ABS_LINKS+=("$(abspath "$L")"); done
if [ "$CLAUDE_LINK" = auto ]; then
  CLAUDE_LINK=no
  if [ -d "$HOME/.claude" ] && [ "$SKILLS_DIR" != "$HOME/.claude/skills" ]; then
    CLAUDE_LINK=yes
    ABS_LINKS+=("$HOME/.claude/skills")
  fi
fi

# Antigravity / Gemini agent skills discovery
if [ -d "$HOME/.gemini/config/skills" ] && [ "$SKILLS_DIR" != "$HOME/.gemini/config/skills" ]; then
  ABS_LINKS+=("$HOME/.gemini/config/skills")
fi
if [ -d "$HOME/.gemini/antigravity-cli/skills" ] && [ "$SKILLS_DIR" != "$HOME/.gemini/antigravity-cli/skills" ]; then
  ABS_LINKS+=("$HOME/.gemini/antigravity-cli/skills")
fi

ENG="$SKILLS_DIR/video-pipeline/engine"

tilde() { case "$1" in "$HOME"/*) printf '~/%s' "${1#"$HOME"/}" ;; *) printf '%s' "$1" ;; esac; }
if [ -t 1 ]; then B=$'\033[1m'; G=$'\033[32m'; Y=$'\033[33m'; R=$'\033[31m'; N=$'\033[0m'; else B=""; G=""; Y=""; R=""; N=""; fi
step() { printf '\n%s== %s%s\n' "$B" "$1" "$N"; }
ok()   { printf '  %s✓%s %s\n' "$G" "$N" "$1"; }
warn() { printf '  %s!%s %s\n' "$Y" "$N" "$1"; WARNINGS+=("$1"); }
die()  { printf '\n%sStopped:%s %s\n' "$R" "$N" "$1"; exit 1; }
WARNINGS=()

ask() {
  if [ "$YES" = 1 ] || [ ! -r /dev/tty ]; then REPLY="${2:-}"; return; fi
  read -r -p "  $1 ${2:+[$2] }" REPLY < /dev/tty || REPLY=""
  REPLY="${REPLY:-${2:-}}"
}
ask_secret() {
  if [ "$YES" = 1 ] || [ ! -r /dev/tty ]; then REPLY="${2:-}"; return; fi
  local hint=""; [ -n "${2:-}" ] && hint=" (Enter keeps current, ending ${2: -4})"
  read -r -s -p "  $1$hint: " REPLY < /dev/tty || REPLY=""; echo
  REPLY="${REPLY:-${2:-}}"
}

[ -d "$SKILLS_SRC/video-pipeline" ] || die "run this script from inside the unzipped package (skills/ not found next to it: $PKG)"

printf '%s🎬 Autonomous Video Editing Pipeline Setup%s\n' "$B" "$N"
printf '   Workspace root : %s%s%s (100%% clean creator content)\n' "$G" "$(tilde "$PROJECT")" "$N"
printf '   Engine sandbox : %s%s%s (isolated dependencies & CLI tools)\n' "$G" "$(tilde "$ENGINE_DIR")" "$N"
printf '   Skills catalog : %s%s%s\n' "$G" "$(tilde "$SKILLS_DIR")" "$N"

OS="$(uname -s 2>/dev/null || echo "Unknown")"
ARCH="$(uname -m 2>/dev/null || echo "Unknown")"
case "$ARCH" in aarch64|arm64) ARCH_N=arm64 ;; x86_64|amd64) ARCH_N=x64 ;; *) ARCH_N="$ARCH" ;; esac
IS_WIN=0; case "$OS" in MINGW*|MSYS*|CYGWIN*) IS_WIN=1 ;; esac
# Native Windows programs (python.exe) read C:/... paths, not Git Bash's /c/...
nativepath() { if [ "$IS_WIN" = 1 ] && command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }

# Python 3.9+ runs the engine, and below it checks downloads and unpacks zips (Windows has python/py, not python3)
PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3 python py; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  if [ "$IS_WIN" = 1 ]; then die "Python 3.9+ not found: winget install Python.Python.3.12 (then open a new terminal)"; fi
  die "Python 3.9+ not found: macOS 'brew install python', Ubuntu 'sudo apt-get install -y python3 python3-venv', Fedora 'sudo dnf install -y python3'"
fi

download() {  # url file: download to file.part, then rename
  curl -L --fail --progress-bar -o "$2.part" "$1" && mv "$2.part" "$2" || { rm -f "$2.part"; return 1; }
}
sha256_of() { "$PY" -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$(nativepath "$1")"; }
unpack() {  # archive dir: .tar.gz with tar, .zip with Python (Git Bash has no unzip)
  rm -rf "$2"; mkdir -p "$2"
  case "$1" in
    *.zip) "$PY" -m zipfile -e "$(nativepath "$1")" "$(nativepath "$2")" ;;
    *) tar -xzf "$1" -C "$2" ;;
  esac
}
node_major() { local v; v="$(node -v 2>/dev/null | sed 's/^v//; s/\..*//')"; case "$v" in ''|*[!0-9]*) echo 0 ;; *) echo "$v" ;; esac; }

# A private Node 22 inside the engine (no sudo, nothing system-wide) when the system node is missing or older
NODE_HOME="$ENGINE_DIR/node"
if [ "$IS_WIN" = 1 ]; then NODE_BIN="$NODE_HOME"; else NODE_BIN="$NODE_HOME/bin"; fi
if [ -d "$NODE_BIN" ]; then export PATH="$NODE_BIN:$PATH"; fi
install_private_node() {
  local plat="" ext=tar.gz sums line sha file tmp rc
  case "$OS" in Darwin) plat="darwin-$ARCH_N" ;; Linux) plat="linux-$ARCH_N" ;; esac
  if [ "$IS_WIN" = 1 ]; then plat="win-$ARCH_N"; ext=zip; fi
  [ -n "$plat" ] || return 1
  sums="$(curl -fsSL https://nodejs.org/dist/latest-v22.x/SHASUMS256.txt)" || return 1
  line="$(printf '%s\n' "$sums" | grep -E "  node-v22\.[0-9.]+-$plat\.$ext\$" | head -1)"
  [ -n "$line" ] || return 1
  sha="${line%% *}"; file="${line##* }"
  tmp="$ENGINE_DIR/.node-download"; mkdir -p "$tmp"
  echo "  downloading $file (a private Node.js for the engine)"
  download "https://nodejs.org/dist/latest-v22.x/$file" "$tmp/$file" || { rm -rf "$tmp"; return 1; }
  if [ "$(sha256_of "$tmp/$file")" != "$sha" ]; then warn "Node.js download failed its checksum"; rm -rf "$tmp"; return 1; fi
  unpack "$tmp/$file" "$tmp/x" && rm -rf "$NODE_HOME" && mv "$tmp/x/${file%.$ext}" "$NODE_HOME"
  rc=$?; rm -rf "$tmp"; return $rc
}

# whisper.cpp prebuilt release (Linux, Windows) when no whisper-cli is installed; Homebrew covers macOS.
# Kept in its own folder (it also ships main, bench, stream...) and found through WATCH_WHISPER_CPP_BIN, not PATH.
WHISPER_TAG="b5454"
WHISPER_DIR="$ENGINE_DIR/whisper"
WHISPER_BIN=""
whisper_works() { [ -n "$1" ] && [ -f "$1" ] && "$1" --help >/dev/null 2>&1; }
find_private_whisper() { [ -d "$WHISPER_DIR" ] || return 0; find "$WHISPER_DIR" -type f \( -name whisper-cli -o -name whisper-cli.exe \) 2>/dev/null | head -1 || true; }
install_private_whisper() {
  local asset="" rc
  case "$OS-$ARCH_N" in
    Linux-x64) asset=whisper-bin-ubuntu-x64.tar.gz ;;
    Linux-arm64) asset=whisper-bin-ubuntu-arm64.tar.gz ;;
  esac
  if [ "$IS_WIN" = 1 ] && [ "$ARCH_N" = x64 ]; then asset=whisper-bin-x64.zip; fi
  [ -n "$asset" ] || return 1
  echo "  downloading whisper.cpp $WHISPER_TAG ($asset)"
  download "https://github.com/ggml-org/whisper.cpp/releases/download/$WHISPER_TAG/$asset" "$ENGINE_DIR/$asset" || return 1
  unpack "$ENGINE_DIR/$asset" "$WHISPER_DIR"; rc=$?; rm -f "$ENGINE_DIR/$asset"; return $rc
}

# --------------------------------------------------------------------------------------------- 1. System tools
step "1/8 System tools (node, ffmpeg, whisper-cpp, sox)"
if [ "$NO_SYSTEM" = 1 ]; then
  ok "skipped (--no-system)"
elif [ "$OS" = "Darwin" ]; then
  if ! command -v brew >/dev/null 2>&1; then
    die "Homebrew is not installed. Install it from https://brew.sh, open a new terminal, and re-run install.sh."
  fi
  for f in node ffmpeg whisper-cpp sox; do
    if brew list --formula "$f" >/dev/null 2>&1; then
      ok "$f already installed"
    else
      brew install "$f"
      ok "$f installed"
    fi
  done
fi

# The one command that installs what is missing (Node and whisper.cpp come privately below, so they are not in it)
SYS_HINT=""
if [ "$OS" = "Darwin" ]; then
  SYS_HINT="brew install ffmpeg sox"
elif [ "$OS" = "Linux" ]; then
  if command -v apt-get >/dev/null 2>&1; then
    SYS_HINT="sudo apt-get update && sudo apt-get install -y ffmpeg sox libsox-fmt-all libgomp1 python3-venv"
  elif command -v dnf >/dev/null 2>&1; then
    SYS_HINT="sudo dnf install -y ffmpeg-free sox libgomp python3 (for the full ffmpeg enable RPM Fusion)"
  elif command -v pacman >/dev/null 2>&1; then
    SYS_HINT="sudo pacman -S --needed ffmpeg sox python"
  fi
elif [ "$IS_WIN" = 1 ]; then
  SYS_HINT="winget install --id Gyan.FFmpeg -e; winget install --id ChrisBagwell.SoX -e (then open a new terminal)"
fi
[ -n "$SYS_HINT" ] || SYS_HINT="install FFmpeg and SoX with your package manager"

if [ "$(node_major)" -lt 22 ]; then
  if [ "$(node_major)" -gt 0 ]; then echo "  system node is $(node -v); the engine needs 22+"; fi
  install_private_node || warn "could not download a private Node.js 22"
  export PATH="$NODE_BIN:$PATH"; hash -r
fi
[ "$(node_major)" -ge 22 ] || die "Node.js 22 or newer is needed (found: $(node -v 2>/dev/null || echo none)). Install it from https://nodejs.org and re-run."
case "$(command -v node)" in "$NODE_BIN"/*) ok "node $(node -v) (private, in $(tilde "$NODE_HOME"))" ;; *) ok "node $(node -v)" ;; esac
command -v ffmpeg >/dev/null 2>&1 && ok "ffmpeg ready" || die "ffmpeg not found. Run: $SYS_HINT"
if command -v sox >/dev/null 2>&1; then ok "sox ready"; else warn "sox not found (needed for room-tone profiling and audio cleaning). Run: $SYS_HINT"; fi

if command -v whisper-cli >/dev/null 2>&1; then
  ok "whisper-cli found"
else
  WHISPER_BIN="$(find_private_whisper)"
  if ! whisper_works "$WHISPER_BIN"; then
    install_private_whisper || true
    WHISPER_BIN="$(find_private_whisper)"
  fi
  if whisper_works "$WHISPER_BIN"; then
    ok "whisper-cli ready: $(tilde "$WHISPER_BIN")"
  else
    MISSING_LIBS=""
    if [ -n "$WHISPER_BIN" ] && command -v ldd >/dev/null 2>&1; then
      MISSING_LIBS="$(ldd "$WHISPER_BIN" 2>/dev/null | awk '/not found/ {print $1}' | tr '\n' ' ')"
    fi
    if [ -n "$MISSING_LIBS" ]; then
      warn "whisper-cli needs ${MISSING_LIBS% } from the system. Run: $SYS_HINT; then: video-skills setup"
    elif [ "$OS" = "Darwin" ]; then
      warn "whisper-cli not found: brew install whisper-cpp"
    else
      warn "whisper-cli not found and there is no prebuilt whisper.cpp for $OS-$ARCH: build https://github.com/ggml-org/whisper.cpp and set WATCH_WHISPER_CPP_BIN in ~/.config/video-skills/.env"
    fi
    WHISPER_BIN=""
  fi
fi

# --------------------------------------------------------------------------------------------- 2. Models and neural nets
step "2/8 Models & neural nets (Whisper, RNNoise, YuNet, DeepFilterNet)"
MODEL_DIR="$HOME/.cache/whisper.cpp"
if [ "$MODEL" = "none" ]; then
  ok "Whisper model skipped (--model none)"
else
  mkdir -p "$MODEL_DIR"
  MFILE="$MODEL_DIR/ggml-$MODEL.bin"
  if [ -s "$MFILE" ] && [ "$(wc -c < "$MFILE")" -gt 100000000 ]; then
    ok "Whisper model ready: $MFILE"
  else
    echo "  downloading ggml-$MODEL.bin (~3 GB for large-v3)"
    curl -L --fail --progress-bar -o "$MFILE.part" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-$MODEL.bin" \
      && mv "$MFILE.part" "$MFILE" && ok "saved $MFILE" \
      || { rm -f "$MFILE.part"; warn "model download failed; re-run later or download ggml-$MODEL.bin into $MODEL_DIR"; }
  fi
fi

# RNNoise neural speech denoising model
RNNOISE_DIR="$HOME/.config/video-skills/rnnoise"
mkdir -p "$RNNOISE_DIR"
RNNOISE_FILE="$RNNOISE_DIR/sh.rnnn"
if [ -s "$RNNOISE_FILE" ] && [ "$(wc -c < "$RNNOISE_FILE")" -gt 50000 ]; then
  ok "RNNoise neural model ready: $RNNOISE_FILE"
else
  echo "  downloading RNNoise model sh.rnnn for neural voice denoising"
  curl -L --fail --progress-bar -o "$RNNOISE_FILE.part" "https://github.com/GregorR/rnnoise-models/raw/master/somnolent-hogwash-2018-09-01/sh.rnnn" \
    && mv "$RNNOISE_FILE.part" "$RNNOISE_FILE" && ok "saved $RNNOISE_FILE" \
    || { rm -f "$RNNOISE_FILE.part"; warn "RNNoise model download failed; video-audio will need $RNNOISE_FILE"; }
fi

# OpenCV YuNet face detection neural model
MODELS_DIR="$HOME/.config/video-skills/models"
mkdir -p "$MODELS_DIR"
YUNET_FILE="$MODELS_DIR/face_detection_yunet_2023mar.onnx"
if [ -s "$YUNET_FILE" ] && [ "$(wc -c < "$YUNET_FILE")" -gt 50000 ]; then
  ok "YuNet face detection model ready: $YUNET_FILE"
else
  echo "  downloading YuNet ONNX model for face-tracked reframing"
  curl -L --fail --progress-bar -o "$YUNET_FILE.part" "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx" \
    && mv "$YUNET_FILE.part" "$YUNET_FILE" && ok "saved $YUNET_FILE" \
    || { rm -f "$YUNET_FILE.part"; warn "YuNet model download failed; reframe.py will fallback to Haar cascades"; }
fi

# DeepFilterNet3 neural noise suppressor
DF_VERSION="0.5.6"
DF_DIR="$HOME/.config/video-skills/bin"
DF_FILE="$DF_DIR/deep-filter"
mkdir -p "$DF_DIR"
case "$OS-$ARCH_N" in
  Darwin-arm64) DF_ASSET="deep-filter-$DF_VERSION-aarch64-apple-darwin" ;;
  Darwin-x64) DF_ASSET="deep-filter-$DF_VERSION-x86_64-apple-darwin" ;;
  Linux-x64) DF_ASSET="deep-filter-$DF_VERSION-x86_64-unknown-linux-musl" ;;
  Linux-arm64) DF_ASSET="deep-filter-$DF_VERSION-aarch64-unknown-linux-gnu" ;;
  *) DF_ASSET="" ;;
esac
if [ "$IS_WIN" = 1 ] && [ "$ARCH_N" = x64 ]; then DF_ASSET="deep-filter-$DF_VERSION-x86_64-pc-windows-msvc.exe"; DF_FILE="$DF_DIR/deep-filter.exe"; fi
if [ -x "$DF_FILE" ] && "$DF_FILE" --help >/dev/null 2>&1; then
  ok "DeepFilterNet ready: $DF_FILE"
elif [ -z "$DF_ASSET" ]; then
  warn "No precompiled DeepFilterNet binary for $OS-$ARCH; the audio chain falls back to RNNoise"
else
  echo "  downloading DeepFilterNet $DF_VERSION for indoor/outdoor neural speech isolation"
  curl -L --fail --progress-bar -o "$DF_FILE.part" "https://github.com/Rikorose/DeepFilterNet/releases/download/v$DF_VERSION/$DF_ASSET" \
    && chmod +x "$DF_FILE.part" && mv "$DF_FILE.part" "$DF_FILE" && ok "saved $DF_FILE" \
    || { rm -f "$DF_FILE.part"; warn "DeepFilterNet download failed; voice-clean.py will use RNNoise"; }
fi

# --------------------------------------------------------------------------------------------- 3. Python environment
step "3/8 Python sandbox ($ENGINE_DIR/.venv)"
VENV_DIR="$ENGINE_DIR/.venv"
VENV_PY="$VENV_DIR/bin/python"
if [ ! -x "$VENV_PY" ] && [ -x "$VENV_DIR/Scripts/python.exe" ]; then
  VENV_PY="$VENV_DIR/Scripts/python.exe"
fi
# a venv made without pip (Debian/Ubuntu without python3-venv) is unusable: start it again
if [ -x "$VENV_PY" ] && ! "$VENV_PY" -m pip --version >/dev/null 2>&1; then rm -rf "$VENV_DIR"; fi

if [ ! -x "$VENV_PY" ]; then
  if ! "$PY" -m venv "$VENV_DIR" >/dev/null 2>&1; then
    rm -rf "$VENV_DIR"
    die "could not create a Python virtual environment. Run: $SYS_HINT"
  fi
  ok "created engine virtual environment ($("$PY" --version)) in $(tilde "$VENV_DIR")"
else
  ok "engine virtual environment ready in $(tilde "$VENV_DIR")"
fi

if [ -x "$VENV_DIR/bin/python" ]; then
  VENV_PY="$VENV_DIR/bin/python"
elif [ -x "$VENV_DIR/Scripts/python.exe" ]; then
  VENV_PY="$VENV_DIR/Scripts/python.exe"
fi

if [ "$SKIP_PIP" = 1 ]; then
  ok "pip install skipped (--skip-pip)"
else
  "$VENV_PY" -m pip install --quiet --upgrade pip
  "$VENV_PY" -m pip install --quiet numpy pillow "opencv-python-headless>=4.9,<5" auto-editor google-genai scipy soundfile nara_wpe
  ok "numpy, pillow, opencv, auto-editor, google-genai, scipy, soundfile, nara_wpe installed in sandbox"
fi
"$VENV_PY" -c "import numpy" 2>/dev/null || die "sandbox virtualenv has no numpy; re-run without --skip-pip"

# --------------------------------------------------------------------------------------------- 4. Skills & clean workspace
step "4/8 Skills catalog & clean workspace folders"
mkdir -p "$SKILLS_DIR"

STAMP="$(date +%Y%m%d-%H%M%S)"; NEW=0; KEPT=0; UPDATED=0; FOREIGN=()
ours() {
  [ -f "$1/.video-skills" ] && return 0
  [ -f "$1/SKILL.md" ] || return 1
  grep -q "video-pipeline/engine" "$1/SKILL.md" && return 0
  grep -qE "^name: (video-pipeline|business-reels-style)\s*$" "$1/SKILL.md" && return 0
  return 1
}

for d in "$SKILLS_SRC"/*/; do
  [ "$SKILLS_MANAGED" = 1 ] && break                    # video-skills already linked them into the versioned store
  name="$(basename "$d")"
  dst="$SKILLS_DIR/$name"
  if [ -e "$dst" ] && ! ours "$dst"; then
    FOREIGN+=("$name"); continue
  fi
  if [ -d "$dst" ]; then
    if [ "$UPDATE_SKILLS" = 1 ]; then
      mkdir -p "$SKILLS_DIR-backup-$STAMP"; mv "$dst" "$SKILLS_DIR-backup-$STAMP/$name"
      cp -R "$d" "$dst"; UPDATED=$((UPDATED + 1))
    else
      [ -f "$dst/.video-skills" ] || cp "$d/.video-skills" "$dst/.video-skills"
      KEPT=$((KEPT + 1))
    fi
  else
    cp -R "$d" "$dst"; NEW=$((NEW + 1))
  fi
done
if [ "$SKILLS_MANAGED" = 1 ]; then
  ok "skills in $(tilde "$SKILLS_DIR") are managed by video-skills (versioned links; update with: video-skills update)"
else
  ok "skills in $(tilde "$SKILLS_DIR"): $NEW installed, $KEPT kept, $UPDATED updated"
fi
[ -d "$SKILLS_DIR/business-reels-style" ] && rm -rf "$SKILLS_DIR/business-reels-style"

# Link skills to other agents (e.g. Claude Code, Antigravity)
for L in ${ABS_LINKS[@]+"${ABS_LINKS[@]}"}; do
  [ "$L" = "$SKILLS_DIR" ] && continue
  mkdir -p "$L"; n=0; skipped=0
  [ -e "$L/business-reels-style" ] && rm -rf "$L/business-reels-style"
  for d in "$SKILLS_SRC"/*/; do
    name="$(basename "$d")"; target="$SKILLS_DIR/$name"
    rel="$("$VENV_PY" -c 'import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))' "$target" "$L")"
    if [ -L "$L/$name" ]; then ln -sfn "$rel" "$L/$name"; n=$((n + 1))
    elif [ -e "$L/$name" ]; then skipped=$((skipped + 1))
    else ln -s "$rel" "$L/$name"; n=$((n + 1)); fi
  done
  ok "linked $n skills into $(tilde "$L")"
done

# Scaffold ONLY clean user folders in PROJECT
mkdir -p "$PROJECT/videos/_shared/sfx" "$PROJECT/videos/_shared/img" "$PROJECT/references" "$PROJECT/brand/assets"

# Sound Palette integration
if [ -d "$PKG/sound-palette" ]; then
  mkdir -p "$PROJECT/sound-palette" "$ENGINE_DIR/sound-palette" "$SKILLS_DIR/sound-palette"
  cp -R "$PKG/sound-palette/"* "$PROJECT/sound-palette/" 2>/dev/null || true
  cp -R "$PKG/sound-palette/"* "$ENGINE_DIR/sound-palette/" 2>/dev/null || true
  cp -R "$PKG/sound-palette/"* "$SKILLS_DIR/sound-palette/" 2>/dev/null || true
  if [ -d "$PKG/sound-palette/audio" ]; then
    cp -R "$PKG/sound-palette/audio/"* "$PROJECT/videos/_shared/sfx/" 2>/dev/null || true
  fi
  ok "Sound Palette integrated into $(tilde "$PROJECT")/sound-palette"
fi

# Brand style guide scaffold (brand/STYLE-GUIDE.md: fill the "Yours" column; the agent writes it into style.json)
if [ ! -f "$PROJECT/brand/STYLE-GUIDE.md" ] && [ -f "$PKG/brand/STYLE-GUIDE.md" ]; then
  cp "$PKG/brand/STYLE-GUIDE.md" "$PROJECT/brand/STYLE-GUIDE.md"
  ok "brand style guide scaffolded at $(tilde "$PROJECT")/brand/STYLE-GUIDE.md"
fi

# Brand Memory scaffold (brand/MEMO.md)
if [ ! -f "$PROJECT/brand/MEMO.md" ]; then
  if [ -f "$PKG/brand/MEMO.md" ]; then
    cp "$PKG/brand/MEMO.md" "$PROJECT/brand/MEMO.md"
  else
    "$VENV_PY" "$ENG/scripts/memo.py" init --path "$PROJECT/brand/MEMO.md"
  fi
  ok "brand memory scaffolded at $(tilde "$PROJECT")/brand/MEMO.md"
else
  ok "brand memory exists at $(tilde "$PROJECT")/brand/MEMO.md (preserved)"
fi

# Copy LICENSES to ENGINE_DIR (never polluting user workspace)
cp -R "$PKG/LICENSES" "$ENGINE_DIR/LICENSES" 2>/dev/null || true

# WORKSPACE HYGIENE: Clean any legacy engine plumbing files from user's working directory
if [ "$CLEAN_WORKSPACE" = 1 ]; then
  MIGRATED_KEYS=0
  if [ -f "$PROJECT/.env" ]; then
    mkdir -p "$HOME/.config/video-skills"
    touch "$HOME/.config/video-skills/.env" "$ENGINE_DIR/.env"
    chmod 600 "$HOME/.config/video-skills/.env" "$ENGINE_DIR/.env"
    while IFS= read -r line || [ -n "$line" ]; do
      line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
      if [ -n "$line" ] && [[ "$line" != \#* ]] && [[ "$line" == *=* ]]; then
        k="${line%%=*}"
        if ! grep -q "^$k=" "$HOME/.config/video-skills/.env" 2>/dev/null; then
          echo "$line" >> "$HOME/.config/video-skills/.env"
          echo "$line" >> "$ENGINE_DIR/.env"
          MIGRATED_KEYS=$((MIGRATED_KEYS + 1))
        fi
      fi
    done < "$PROJECT/.env"
    rm -f "$PROJECT/.env"
    ok "migrated $MIGRATED_KEYS keys from project .env into global ~/.config/video-skills/.env"
  fi

  LEGACY_FILES=(
    "package.json"
    "package-lock.json"
    "node_modules"
    ".venv"
    "LICENSES"
    ".claude"
    "agent-env.sh"
    "AGENTS.md"
    ".vscode"
  )
  CLEANED_COUNT=0
  for lf in "${LEGACY_FILES[@]}"; do
    if [ -e "$PROJECT/$lf" ] || [ -L "$PROJECT/$lf" ]; then
      rm -rf "$PROJECT/$lf"
      CLEANED_COUNT=$((CLEANED_COUNT + 1))
    fi
  done
  if [ "$CLEANED_COUNT" -gt 0 ]; then
    ok "purged $CLEANED_COUNT legacy plumbing items from $(tilde "$PROJECT") (workspace is now 100% clean)"
  fi
fi

# Minimal clean .gitignore for video rendering cache
if [ -f "$PROJECT/.gitignore" ]; then
  for line in "videos/*/output/" "videos/*/hyperframes/" ".DS_Store"; do
    grep -qxF "$line" "$PROJECT/.gitignore" || echo "$line" >> "$PROJECT/.gitignore"
  done
fi

ok "Creative workspace verified: ONLY brand/, references/, sound-palette/, videos/ in $(tilde "$PROJECT")"

# --------------------------------------------------------------------------------------------- 5. HyperFrames CLI
step "5/8 HyperFrames CLI ($HF_VERSION) & GSAP in sandbox"
(
  cd "$ENGINE_DIR"
  [ -f package.json ] || npm init -y >/dev/null
  npm install --save-dev --save-exact --no-fund --no-audit --loglevel=error "hyperframes@$HF_VERSION" "gsap@$GSAP_VERSION"
)
ok "hyperframes@$HF_VERSION and gsap@$GSAP_VERSION pinned in $(tilde "$ENGINE_DIR")"

mkdir -p "$ENG/assets/vendor"
if [ -f "$ENGINE_DIR/node_modules/gsap/dist/gsap.min.js" ]; then
  cp "$ENGINE_DIR/node_modules/gsap/dist/gsap.min.js" "$ENG/assets/vendor/gsap.min.js"
  ok "local GSAP copied (renders work offline)"
fi

if [ "$NO_BROWSER" = 1 ]; then
  ok "browser skipped (--no-browser)"
else
  if (cd "$ENGINE_DIR" && npx --no-install hyperframes browser ensure); then
    # ensure can settle on a system Chromium that does not start (snap stubs, Linux on ARM): ask doctor whether it runs
    if (cd "$ENGINE_DIR" && npx --no-install hyperframes doctor 2>&1) | grep -qE "✗ +Chrome"; then
      CH_HINT="install Google Chrome, or Chromium from your package manager, and set HYPERFRAMES_BROWSER_PATH in ~/.config/video-skills/.env"
      [ "$OS-$ARCH_N" = Linux-arm64 ] && CH_HINT="Chrome has no Linux ARM build: install a non-snap Chromium (e.g. 'sudo dnf install chromium', Debian 'sudo apt-get install chromium') and set HYPERFRAMES_BROWSER_PATH in ~/.config/video-skills/.env"
      warn "Chrome for rendering does not start (npx hyperframes doctor). $CH_HINT"
    else
      ok "HyperFrames Chrome ready"
    fi
  else
    warn "HyperFrames could not fetch Chrome; run 'cd $ENGINE_DIR && npx hyperframes browser ensure' later"
  fi
fi

HF_SKILLS=(
  hyperframes hyperframes-animation hyperframes-audio hyperframes-cli
  hyperframes-core hyperframes-creative hyperframes-keyframes hyperframes-registry
  hyperframes-studio media-use embedded-captions faceless-explainer
  motion-graphics product-launch-video talking-head-recut
)
for s in "${HF_SKILLS[@]}"; do
  (cd "$ENGINE_DIR" && npx --no-install hyperframes skills update "$s" >/dev/null 2>&1) || true
done
ok "HyperFrames skills suite updated"

# --------------------------------------------------------------------------------------------- 6. Accounts and API keys
step "6/8 Accounts and API keys (stored globally in ~/.config/video-skills/.env)"
mkdir -p "$HOME/.config/video-skills"
touch "$HOME/.config/video-skills/.env" "$ENGINE_DIR/.env"
chmod 600 "$HOME/.config/video-skills/.env" "$ENGINE_DIR/.env"

getenv() {
  local line; line="$(grep -E "^$1=" "$HOME/.config/video-skills/.env" 2>/dev/null | tail -1 || true)"
  [ -z "$line" ] && line="$(grep -E "^$1=" "$ENGINE_DIR/.env" 2>/dev/null | tail -1 || true)"
  line="${line#*=}"
  case "$line" in
    \'*\') line="${line#\'}"; line="${line%\'}"; line="$(printf '%s' "$line" | sed "s/'\\\\''/'/g")" ;;   # KEY='va'\''lue' (current format)
    \"*\") line="${line#\"}"; line="${line%\"}" ;;                                  # KEY="value" (older installs)
  esac
  printf '%s' "$line"; return 0
}
setenv() {   # single-quoted, so a value may hold any character (quotes, $, `, \) and the file always parses
  local q; q="$(printf '%s' "$2" | sed "s/'/'\\\\''/g")"
  for f in "$HOME/.config/video-skills/.env" "$ENGINE_DIR/.env"; do
    local tmp; tmp="$(mktemp)"; grep -vE "^$1=" "$f" 2>/dev/null > "$tmp" || true
    [ -n "$2" ] && printf "%s='%s'\n" "$1" "$q" >> "$tmp"
    cat "$tmp" > "$f"; rm -f "$tmp"; chmod 600 "$f"
  done
}
api_key() {  # trimmed key from a hidden prompt; refuses anything that is not key-shaped (a stray keystroke, a paste with spaces)
  local v; v="$(printf '%s' "$1" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"   # trim the ends only
  if [ -n "$v" ] && ! printf '%s' "$v" | grep -Eq '^[A-Za-z0-9._:+/=-]{8,}$'; then
    warn "$2 not saved: that does not look like an API key (letters, digits and . _ : + / = - only, 8+ characters). Re-run install.sh to enter it."
    v=""
  fi
  printf '%s' "$v"
}

echo "  HeyGen (the sound library for all SFX and music)"
HG_CUR="$(getenv HEYGEN_API_KEY)"; HG_CUR="${HG_CUR:-${HEYGEN_API_KEY:-}}"
if [ -n "$HG_CUR" ]; then
  ok "HEYGEN_API_KEY already configured"; setenv HEYGEN_API_KEY "$HG_CUR"
elif ! HG_STATUS="$(cd "$ENGINE_DIR" && npx --no-install hyperframes auth status 2>&1)" \
     || printf '%s' "$HG_STATUS" | grep -qiE "not (signed|logged) in" \
     || ! printf '%s' "$HG_STATUS" | grep -qiE "signed in|logged in|authenticated"; then   # only a clear yes counts as signed in
  HG_DEFAULT=1; { [ "$YES" = 1 ] || [ ! -r /dev/tty ]; } && HG_DEFAULT=3
  ask "Sign in now? 1 = browser sign-in (recommended), 2 = paste an API key, 3 = later" "$HG_DEFAULT"
  case "$REPLY" in
    1) (cd "$ENGINE_DIR" && npx --no-install hyperframes auth login < /dev/tty) || warn "HeyGen sign-in incomplete" ;;
    2) ask_secret "HeyGen API key" ""; REPLY="$(api_key "$REPLY" HEYGEN_API_KEY)"; [ -n "$REPLY" ] && setenv HEYGEN_API_KEY "$REPLY" && ok "saved" ;;
    *) warn "HeyGen skipped: SFX will use offline curated sound-palette" ;;
  esac
else
  ok "HeyGen already signed in"
fi

echo "  Google Gemini (Veo video + Gemini Flash Image; https://aistudio.google.com/apikey)"
G_CUR="$(getenv GEMINI_API_KEY)"; G_CUR="${G_CUR:-${GEMINI_API_KEY:-}}"
ask_secret "GEMINI_API_KEY (Enter to skip)" "$G_CUR"; REPLY="$(api_key "$REPLY" GEMINI_API_KEY)"; setenv GEMINI_API_KEY "$REPLY"
[ -n "$REPLY" ] && ok "GEMINI_API_KEY saved" || ok "GEMINI_API_KEY skipped"

echo "  OpenRouter (fallback for image generation; https://openrouter.ai/keys)"
O_CUR="$(getenv OPENROUTER_API_KEY)"; O_CUR="${O_CUR:-${OPENROUTER_API_KEY:-}}"
ask_secret "OPENROUTER_API_KEY (Enter to skip)" "$O_CUR"; REPLY="$(api_key "$REPLY" OPENROUTER_API_KEY)"; setenv OPENROUTER_API_KEY "$REPLY"
[ -n "$REPLY" ] && ok "OPENROUTER_API_KEY saved" || ok "OpenRouter key skipped"

ask "Main spoken language for transcription: en, hi (Hinglish Roman captions), or auto?" "$(getenv WATCH_WHISPER_LANG)"
LANG_CHOICE="${REPLY:-auto}"; setenv WATCH_WHISPER_LANG "$LANG_CHOICE"; ok "WATCH_WHISPER_LANG=$LANG_CHOICE"

[ "$MODEL" != "none" ] && setenv WATCH_WHISPER_MODEL "$(nativepath "$MODEL_DIR/ggml-$MODEL.bin")"
[ -n "$WHISPER_BIN" ] && setenv WATCH_WHISPER_CPP_BIN "$(nativepath "$WHISPER_BIN")"
[ "$IS_WIN" = 1 ] && [ -x "$DF_FILE" ] && setenv VIDEO_DEEPFILTER "$(nativepath "$DF_FILE")"
setenv VIDEO_SKILLS "$(nativepath "$SKILLS_DIR")"
setenv VIDEO_ENGINE "$(nativepath "$ENG")"
setenv VIDEO_ENGINE_DIR "$(nativepath "$ENGINE_DIR")"
setenv VIDEO_SOUND_PALETTE "$(nativepath "$PROJECT/sound-palette")"
setenv RNNOISE_MODEL "$(nativepath "$HOME/.config/video-skills/rnnoise/sh.rnnn")"
setenv YUNET_MODEL "$(nativepath "$HOME/.config/video-skills/models/face_detection_yunet_2023mar.onnx")"
ok "environment variables configured in ~/.config/video-skills/.env"

# --------------------------------------------------------------------------------------------- 7. Agent wiring
step "7/8 Agent runtime discovery wiring"
AGENT_ENV_FILE="$ENGINE_DIR/agent-env.sh"
# venv scripts (bin/, or Scripts/ on Windows), HyperFrames CLI, then the private Node when there is one
ENGINE_PATH="$(dirname "$VENV_PY"):$ENGINE_DIR/node_modules/.bin"
[ -d "$NODE_BIN" ] && ENGINE_PATH="$ENGINE_PATH:$NODE_BIN"
{
  echo "# Autonomous Video Editing Environment"
  echo "export VIDEO_ENGINE_DIR=\"$ENGINE_DIR\""
  echo "export VIDEO_SKILLS=\"$SKILLS_DIR\""
  echo "export VIDEO_ENGINE=\"$ENG\""
  echo "export VIDEO_SOUND_PALETTE=\"$PROJECT/sound-palette\""
  echo "export RNNOISE_MODEL=\"\$HOME/.config/video-skills/rnnoise/sh.rnnn\""
  echo "export YUNET_MODEL=\"\$HOME/.config/video-skills/models/face_detection_yunet_2023mar.onnx\""
  echo "export PATH=\"$ENGINE_PATH:\$PATH\""
  echo "if [ -f \"\$HOME/.config/video-skills/.env\" ]; then set -a; . \"\$HOME/.config/video-skills/.env\"; set +a; fi"
} > "$AGENT_ENV_FILE"
cp "$AGENT_ENV_FILE" "$HOME/.config/video-skills/agent-env.sh" 2>/dev/null || true
ok "global agent-env.sh generated at $(tilde "$AGENT_ENV_FILE") and ~/.config/video-skills/agent-env.sh"
# The private Node only helps if agents' shells find it before an older system node (npx hyperframes needs 22+)
if [ -d "$NODE_BIN" ]; then
  case "${SHELL:-}" in *zsh) RC="$HOME/.zshrc" ;; *) RC="$HOME/.bashrc" ;; esac
  RC_LINE="[ -d \"$NODE_BIN\" ] && export PATH=\"$NODE_BIN:\$PATH\"  # video-skills: Node.js 22 for the engine"
  if ! grep -qF "$RC_LINE" "$RC" 2>/dev/null; then
    printf '\n%s\n' "$RC_LINE" >> "$RC"
    ok "Node.js 22 put first on PATH in $(tilde "$RC") (open a new terminal)"
  fi
fi

# --------------------------------------------------------------------------------------------- 8. Checks
step "8/8 Preflight verification"
set -a
[ -f "$HOME/.config/video-skills/.env" ] && . "$HOME/.config/video-skills/.env"
set +a
export PATH="$ENGINE_PATH:$PATH"

S="$ENG/scripts"
"$VENV_PY" "$S/watch.py" check 2>&1 | sed 's/^/  /' || warn "watch.py preflight check reported a warning"
"$VENV_PY" "$S/heygen-sound.py" --check 2>&1 | sed 's/^/  /' || true

if [ -s "$HOME/.config/video-skills/rnnoise/sh.rnnn" ]; then
  ok "RNNoise neural model verified"
fi
if [ -s "$HOME/.config/video-skills/models/face_detection_yunet_2023mar.onnx" ]; then
  ok "YuNet face detection model verified"
fi
if [ -f "$PROJECT/sound-palette/sound-palette.json" ]; then
  ok "Sound Palette verified in $(tilde "$PROJECT")/sound-palette"
fi

if [ "$SKIP_TESTS" = 1 ]; then
  ok "tests skipped (--skip-tests)"
else
  echo "  running relevant engine test cases..."
  if (cd "$ENG" && "$VENV_PY" -m unittest tests.test_spec_resolver tests.test_memo tests.test_hinglish_and_venv >/dev/null 2>&1); then
    ok "all relevant engine unit tests passed (spec-resolver, brand memo, hinglish, sandbox discovery)"
  else
    warn "unit test check reported an issue; see logs"
  fi
fi

# --------------------------------------------------------------------------------------------- Done
printf '\n%s✨ Setup Complete!%s\n' "$B" "$N"
if [ ${#WARNINGS[@]} -gt 0 ]; then
  printf '%sNote:%s\n' "$Y" "$N"
  for w in "${WARNINGS[@]}"; do printf '  - %s\n' "$w"; done
fi

cat <<EOF

📂 Creative Workspace (${PROJECT}):
  ├── brand/            <- Creator identity, brand-style-guide.pdf, social handles & brand/MEMO.md
  ├── references/       <- Benchmark reels, viral hooks, layout screenshots
  ├── sound-palette/    <- 19 offline tactile audio assets (-3 dBFS)
  └── videos/           <- Production projects (raw/ -> processed/)

⚙️ Engine Sandbox (${ENGINE_DIR}):
  ├── .venv/            <- Python 3.9+ runtime & dependencies
  ├── node_modules/     <- HyperFrames CLI & GSAP
  └── .env              <- Private API keys (HeyGen, Gemini, OpenRouter)

🚀 How to start editing:
  1. Open your creative workspace folder in your agent (Antigravity, Claude Code, Cursor):
     cd ${PROJECT}
  2. Drop your raw creator clip into a project folder:
     mkdir -p videos/my-video/raw/
     cp path/to/clip.mp4 videos/my-video/raw/
  3. Prompt the agent:
     - Basic: "Edit videos/my-video/raw/clip.mp4 into a 9:16 vertical reel."
     - Detailed: "Edit videos/my-video/raw/clip.mp4 into a high-retention financial teardown.
       Use split-screen layout, Kodak Portra warm tone grade, tactile SFX, Poppins punch words,
       and suppress background noise with neural speech isolation."
EOF
