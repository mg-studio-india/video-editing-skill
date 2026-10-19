#!/usr/bin/env bash
# get.sh: one-line installer for video-editing-skill (macOS, Linux, WSL / Git Bash).
#
#   curl -fsSL https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.sh | bash
#
# Run it from the folder you want as your creative workspace (brand/, references/, videos/), or pass options:
#   curl -fsSL .../get.sh | bash -s -- --project ~/VideoWorkspace [--version 1.2.0] [any install.sh option]
#
# It downloads the latest tagged release into ~/.video-skills/pkg/<version>/, links every skill into
# ~/.agents/skills (and Claude Code), installs the `video-skills` command into ~/.local/bin, and runs install.sh for
# the engine, models and workspace. Afterwards: `video-skills check`, `video-skills update`, `video-skills rollback`.
set -euo pipefail

REPO="${VIDEO_SKILLS_REPO:-mg-studio-india/video-editing-skill}"
VS_HOME="${VIDEO_SKILLS_HOME:-$HOME/.video-skills}"
VERSION=""; PASS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --version) VERSION="${2#v}"; shift ;;
    *) PASS+=("$1") ;;
  esac
  shift
done

say() { printf '%s\n' "$*"; }
die() { printf 'video-skills: %s\n' "$*" >&2; exit 1; }

# Python 3.9+ runs the package manager (the pipeline needs it anyway)
PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  if [ "$(uname -s)" = Darwin ] && command -v brew >/dev/null 2>&1; then
    say "installing Python with Homebrew..."; brew install python; PY=python3
  else
    die "Python 3.9+ is required: macOS 'brew install python', Ubuntu 'sudo apt install python3', Fedora 'sudo dnf install python3'"
  fi
fi
command -v curl >/dev/null 2>&1 || die "curl is required"

# Which release?
if [ -z "$VERSION" ]; then
  VERSION="$(curl -fsSL -H 'Accept: application/vnd.github+json' "https://api.github.com/repos/$REPO/releases/latest" 2>/dev/null \
    | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["tag_name"].lstrip("v"))' 2>/dev/null || true)"
fi
if [ -z "$VERSION" ]; then
  VERSION="$(curl -fsSL "https://api.github.com/repos/$REPO/tags?per_page=100" 2>/dev/null | "$PY" -c '
import json,re,sys
t=[x["name"].lstrip("v") for x in json.load(sys.stdin) if re.fullmatch(r"v?\d+\.\d+\.\d+", x["name"])]
print(max(t, key=lambda v: tuple(map(int, v.split(".")))) if t else "")' 2>/dev/null || true)"
fi
[ -n "$VERSION" ] || die "no release of $REPO is published yet (or GitHub is unreachable)"

# Bootstrap the manager from that release, then let it do the rest
mkdir -p "$VS_HOME/bootstrap"
BOOT="$VS_HOME/bootstrap/video-skills"
curl -fsSL "https://raw.githubusercontent.com/$REPO/v$VERSION/bin/video-skills" -o "$BOOT" || die "could not download the manager for v$VERSION"
chmod +x "$BOOT"
say "video-skills v$VERSION"
exec "$PY" "$BOOT" install --version "$VERSION" ${PASS[@]+"${PASS[@]}"}
