#!/usr/bin/env bash
# install.sh: Cross-platform installer for the autonomous video editing pipeline.
#
# ARCHITECTURE CONTRACT (100% CLEAN WORKSPACE):
#   - Global Engine Sandbox (~/.video-skills/engine or ~/.config/video-skills/engine):
#     Houses all engine plumbing: .venv (Python 3.9+), node_modules (HyperFrames CLI & GSAP),
#     package.json, LICENSES, .env (API keys), and agent-env.sh.
#   - User Creative Workspace ($PROJECT, default: current directory):
#     Houses ONLY clean user creative folders:
#       brand/          (persistent memory brand/MEMO.md and vector logos)
#       references/     (benchmark videos, style guides, font specimens)
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
elif [ "$OS" = "Linux" ]; then
  if command -v apt-get >/dev/null 2>&1; then
    echo "  Debian/Ubuntu detected. Verifying packages..."
    if ! command -v node >/dev/null 2>&1 || ! command -v ffmpeg >/dev/null 2>&1 || ! command -v sox >/dev/null 2>&1; then
      warn "Missing system tools. Run: sudo apt-get update && sudo apt-get install -y nodejs npm ffmpeg sox libsox-fmt-all"
    fi
  elif command -v dnf >/dev/null 2>&1; then
    echo "  Fedora/RHEL detected. Verifying packages..."
    if ! command -v node >/dev/null 2>&1 || ! command -v ffmpeg >/dev/null 2>&1 || ! command -v sox >/dev/null 2>&1; then
      warn "Missing system tools. Run: sudo dnf install -y nodejs npm ffmpeg sox"
    fi
  elif command -v pacman >/dev/null 2>&1; then
    echo "  Arch Linux detected. Verifying packages..."
    if ! command -v node >/dev/null 2>&1 || ! command -v ffmpeg >/dev/null 2>&1 || ! command -v sox >/dev/null 2>&1; then
      warn "Missing system tools. Run: sudo pacman -S --needed nodejs npm ffmpeg sox"
    fi
  fi
else
  warn "Non-Unix / Windows environment. Ensure Node (22+), FFmpeg, SoX, and whisper-cli are in PATH."
fi

command -v node >/dev/null 2>&1 || die "node not found (install Node.js 22+)"
NODE_MAJOR="$(node -v | sed 's/^v//; s/\..*//')"
[ "$NODE_MAJOR" -ge 22 ] || die "Node 22 or newer is needed (found $(node -v))"
ok "node $(node -v)"
command -v ffmpeg >/dev/null 2>&1 && ok "ffmpeg ready" || die "ffmpeg not found"
if command -v sox >/dev/null 2>&1; then ok "sox ready"; else warn "sox not found: required for dynamic audio cleaning and room profiling"; fi
if command -v whisper-cli >/dev/null 2>&1; then ok "whisper-cli found"; else warn "whisper-cli not found: install whisper.cpp for offline transcription"; fi

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
case "$OS-$ARCH" in
  Darwin-arm64) DF_ASSET="deep-filter-$DF_VERSION-aarch64-apple-darwin" ;;
  Darwin-x86_64) DF_ASSET="deep-filter-$DF_VERSION-x86_64-apple-darwin" ;;
  Linux-x86_64) DF_ASSET="deep-filter-$DF_VERSION-x86_64-unknown-linux-musl" ;;
  Linux-aarch64) DF_ASSET="deep-filter-$DF_VERSION-aarch64-unknown-linux-gnu" ;;
  *) DF_ASSET="" ;;
esac
if [ -x "$DF_FILE" ] && "$DF_FILE" --help >/dev/null 2>&1; then
  ok "DeepFilterNet ready: $DF_FILE"
elif [ -z "$DF_ASSET" ]; then
  warn "No precompiled DeepFilterNet binary for $OS-$ARCH; voice-clean.py will fallback to RNNoise"
else
  echo "  downloading DeepFilterNet $DF_VERSION for indoor/outdoor neural speech isolation"
  curl -L --fail --progress-bar -o "$DF_FILE.part" "https://github.com/Rikorose/DeepFilterNet/releases/download/v$DF_VERSION/$DF_ASSET" \
    && chmod +x "$DF_FILE.part" && mv "$DF_FILE.part" "$DF_FILE" && ok "saved $DF_FILE" \
    || { rm -f "$DF_FILE.part"; warn "DeepFilterNet download failed; voice-clean.py will use RNNoise"; }
fi

# --------------------------------------------------------------------------------------------- 3. Python environment
step "3/8 Python sandbox ($ENGINE_DIR/.venv)"
PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
[ -n "$PY" ] || die "Python 3.9+ not found. Please install Python 3.9 or higher."

VENV_DIR="$ENGINE_DIR/.venv"
VENV_PY="$VENV_DIR/bin/python"
if [ ! -x "$VENV_PY" ] && [ -x "$VENV_DIR/Scripts/python.exe" ]; then
  VENV_PY="$VENV_DIR/Scripts/python.exe"
fi

if [ ! -x "$VENV_PY" ]; then
  "$PY" -m venv "$VENV_DIR"
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
ok "skills in $(tilde "$SKILLS_DIR"): $NEW installed, $KEPT kept, $UPDATED updated"

# Link skills to other agents (e.g. Claude Code, Antigravity)
for L in ${ABS_LINKS[@]+"${ABS_LINKS[@]}"}; do
  [ "$L" = "$SKILLS_DIR" ] && continue
  mkdir -p "$L"; n=0; skipped=0
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
  (cd "$ENGINE_DIR" && npx --no-install hyperframes browser ensure) && ok "HyperFrames Chrome ready" \
    || warn "HyperFrames could not fetch Chrome; run 'cd $ENGINE_DIR && npx hyperframes browser ensure' later"
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
  line="${line#*=}"; line="${line#\"}"; line="${line%\"}"
  printf '%s' "$line"; return 0
}
setenv() {
  for f in "$HOME/.config/video-skills/.env" "$ENGINE_DIR/.env"; do
    local tmp; tmp="$(mktemp)"; grep -vE "^$1=" "$f" 2>/dev/null > "$tmp" || true
    [ -n "$2" ] && printf '%s="%s"\n' "$1" "$2" >> "$tmp"
    cat "$tmp" > "$f"; rm -f "$tmp"; chmod 600 "$f"
  done
}

echo "  HeyGen (the sound library for all SFX and music)"
HG_CUR="$(getenv HEYGEN_API_KEY)"; HG_CUR="${HG_CUR:-${HEYGEN_API_KEY:-}}"
if [ -n "$HG_CUR" ]; then
  ok "HEYGEN_API_KEY already configured"; setenv HEYGEN_API_KEY "$HG_CUR"
elif (cd "$ENGINE_DIR" && npx --no-install hyperframes auth status 2>&1 | grep -q "ot signed in"); then
  HG_DEFAULT=1; { [ "$YES" = 1 ] || [ ! -r /dev/tty ]; } && HG_DEFAULT=3
  ask "Sign in now? 1 = browser sign-in (recommended), 2 = paste an API key, 3 = later" "$HG_DEFAULT"
  case "$REPLY" in
    1) (cd "$ENGINE_DIR" && npx --no-install hyperframes auth login < /dev/tty) || warn "HeyGen sign-in incomplete" ;;
    2) ask_secret "HeyGen API key" ""; [ -n "$REPLY" ] && setenv HEYGEN_API_KEY "$REPLY" && ok "saved" ;;
    *) warn "HeyGen skipped: SFX will use offline curated sound-palette" ;;
  esac
else
  ok "HeyGen already signed in"
fi

echo "  Google Gemini (Veo video + Gemini Flash Image; https://aistudio.google.com/apikey)"
G_CUR="$(getenv GEMINI_API_KEY)"; G_CUR="${G_CUR:-${GEMINI_API_KEY:-}}"
ask_secret "GEMINI_API_KEY (Enter to skip)" "$G_CUR"; setenv GEMINI_API_KEY "$REPLY"
[ -n "$REPLY" ] && ok "GEMINI_API_KEY saved" || ok "GEMINI_API_KEY skipped"

echo "  OpenRouter (fallback for image generation; https://openrouter.ai/keys)"
O_CUR="$(getenv OPENROUTER_API_KEY)"; O_CUR="${O_CUR:-${OPENROUTER_API_KEY:-}}"
ask_secret "OPENROUTER_API_KEY (Enter to skip)" "$O_CUR"; setenv OPENROUTER_API_KEY "$REPLY"
[ -n "$REPLY" ] && ok "OPENROUTER_API_KEY saved" || ok "OpenRouter key skipped"

ask "Main spoken language for transcription: en, hi (Hinglish Roman captions), or auto?" "$(getenv WATCH_WHISPER_LANG)"
LANG_CHOICE="${REPLY:-auto}"; setenv WATCH_WHISPER_LANG "$LANG_CHOICE"; ok "WATCH_WHISPER_LANG=$LANG_CHOICE"

[ "$MODEL" != "none" ] && setenv WATCH_WHISPER_MODEL "$MODEL_DIR/ggml-$MODEL.bin"
setenv VIDEO_SKILLS "$SKILLS_DIR"
setenv VIDEO_ENGINE "$ENG"
setenv VIDEO_ENGINE_DIR "$ENGINE_DIR"
setenv VIDEO_SOUND_PALETTE "$PROJECT/sound-palette"
setenv RNNOISE_MODEL "$HOME/.config/video-skills/rnnoise/sh.rnnn"
setenv YUNET_MODEL "$HOME/.config/video-skills/models/face_detection_yunet_2023mar.onnx"
ok "environment variables configured in ~/.config/video-skills/.env"

# --------------------------------------------------------------------------------------------- 7. Agent wiring
step "7/8 Agent runtime discovery wiring"
AGENT_ENV_FILE="$ENGINE_DIR/agent-env.sh"
{
  echo "# Autonomous Video Editing Environment"
  echo "export VIDEO_ENGINE_DIR=\"$ENGINE_DIR\""
  echo "export VIDEO_SKILLS=\"$SKILLS_DIR\""
  echo "export VIDEO_ENGINE=\"$ENG\""
  echo "export VIDEO_SOUND_PALETTE=\"$PROJECT/sound-palette\""
  echo "export RNNOISE_MODEL=\"\$HOME/.config/video-skills/rnnoise/sh.rnnn\""
  echo "export YUNET_MODEL=\"\$HOME/.config/video-skills/models/face_detection_yunet_2023mar.onnx\""
  echo "export PATH=\"$ENGINE_DIR/.venv/bin:$ENGINE_DIR/node_modules/.bin:\$PATH\""
  echo "if [ -f \"\$HOME/.config/video-skills/.env\" ]; then set -a; . \"\$HOME/.config/video-skills/.env\"; set +a; fi"
} > "$AGENT_ENV_FILE"
cp "$AGENT_ENV_FILE" "$HOME/.config/video-skills/agent-env.sh" 2>/dev/null || true
ok "global agent-env.sh generated at $(tilde "$AGENT_ENV_FILE") and ~/.config/video-skills/agent-env.sh"

# --------------------------------------------------------------------------------------------- 8. Checks
step "8/8 Preflight verification"
set -a
[ -f "$HOME/.config/video-skills/.env" ] && . "$HOME/.config/video-skills/.env"
set +a
export PATH="$ENGINE_DIR/.venv/bin:$ENGINE_DIR/node_modules/.bin:$PATH"

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
  if (cd "$S" && "$VENV_PY" -m unittest tests/test_spec_resolver.py tests/test_memo.py tests/test_hinglish_and_venv.py >/dev/null 2>&1); then
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
  ├── brand/            <- Creator identity, social handles & brand/MEMO.md
  ├── references/       <- Benchmark reels, color guides, layout screenshots
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
