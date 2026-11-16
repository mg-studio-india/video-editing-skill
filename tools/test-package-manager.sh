#!/usr/bin/env bash
# test-package-manager.sh: verify the package manager and the video editing environment BEFORE editing (and set it
# up when asked), so an edit cannot fail half-way or come out wrong because a tool, model, flag or skill is missing.
#
#   bash tools/test-package-manager.sh                 parts A + B + C below (~2-5 min)
#   bash tools/test-package-manager.sh --quick         part B only: tools, models, flags and skills (~10 s)
#   bash tools/test-package-manager.sh --package-only  part A only (run it before every release)
#   bash tools/test-package-manager.sh --fix           if something required is missing: run the setup, then verify again
#   options: --no-package (skip A)  --keep (keep the sample project)  --workspace DIR (workspace for --fix)
#
# A. Package manager (needs this package folder, git and rsync): end-to-end test of tools/release.py + bin/video-skills
#    in a throwaway sandbox (fake HOME, a git copy of this package as the release source): release, install, update
#    with a user edit (conflict kept), --force, rollback, partial update, legacy-copy migration, prune, doctor, a
#    release that drops a skill (retired, restored by rollback), uninstall. Touches nothing outside the sandbox.
# B. Environment: package health, installed skills, engine, FFmpeg filters, whisper flags, the Hinglish model,
#    DeepFilterNet, HyperFrames + catalog index, fonts, sound palette.
# C. Sample edit: a short portrait clip with spoken words, room echo and noise through the real pipeline - analyze ->
#    storyboard (a caption keyword, a sound effect, a HyperFrames catalog block) -> approve -> assemble - checking:
#    audio cleaned once and aligned, Hinglish words with timing, the pause tightened, no cut inside a word, the
#    fade-out tail, no doubled voice, the catalog block staged, loudness on target, render check PASS, last frame black.
#
# Exit code 0 = ready. Anything marked FAIL must be fixed first; WARN lowers quality but does not block.
# Installed copy (for agents; parts B and C): $VIDEO_ENGINE_DIR/test-package-manager.sh
set -o pipefail

QUICK=0; FIX=0; KEEP=0; PKG_TEST=1; PKG_ONLY=0; WORKSPACE="$(pwd -P)"
while [ $# -gt 0 ]; do
  case "$1" in
    --quick) QUICK=1 ;;
    --fix) FIX=1 ;;
    --keep) KEEP=1 ;;
    --no-package) PKG_TEST=0 ;;
    --package-only) PKG_ONLY=1 ;;
    --workspace) WORKSPACE="$2"; shift ;;
    -h|--help) sed -n '2,23p' "$0"; exit 0 ;;
    *) echo "unknown option: $1 (see --help)"; exit 2 ;;
  esac
  shift
done

if [ -t 1 ]; then G=$'\033[32m'; Y=$'\033[33m'; R=$'\033[31m'; B=$'\033[1m'; N=$'\033[0m'; else G=""; Y=""; R=""; B=""; N=""; fi
PASS=0; WARNS=(); FAILS=(); NEED_SETUP=0
pass() { PASS=$((PASS + 1)); printf '  %sPASS%s  %s\n' "$G" "$N" "$1"; }
warn() { WARNS+=("$1"); printf '  %sWARN%s  %s\n' "$Y" "$N" "$1"; }
fail() { FAILS+=("$1"); printf '  %sFAIL%s  %s\n' "$R" "$N" "$1"; }
setup_fail() { NEED_SETUP=1; fail "$1"; }
section() { printf '\n%s== %s%s\n' "$B" "$1" "$N"; }

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
PKG=""
[ -f "$HERE/../install.sh" ] && PKG="$(cd "$HERE/.." && pwd -P)"
SKILLS=(video-pipeline video-watch video-style video-audio video-transcribe video-captions video-researcher
        video-plan-storyboard video-generate)
RETIRED=(video-cut-audit video-motion-graphics video-sound-design video-format video-take-geometry video-reference-match
         video-render video-review-gate video-omni-restyle video-short-form)

load_env() {
  set -a
  [ -f "$HOME/.config/video-skills/.env" ] && . "$HOME/.config/video-skills/.env" 2>/dev/null
  set +a
  ENGINE_DIR="${VIDEO_ENGINE_DIR:-}"
  if [ -z "$ENGINE_DIR" ] || [ ! -d "$ENGINE_DIR" ]; then
    for d in "$HOME/.video-skills/engine" "$HOME/.config/video-skills/engine"; do [ -d "$d" ] && { ENGINE_DIR="$d"; break; }; done
  fi
  PY="${VIDEO_ENGINE_PYTHON:-}"
  if [ -z "$PY" ] || [ ! -x "$PY" ]; then
    PY=""
    for c in "$ENGINE_DIR/.venv/bin/python3" "$ENGINE_DIR/.venv/bin/python" "$ENGINE_DIR/.venv/Scripts/python.exe"; do
      [ -x "$c" ] && { PY="$c"; break; }
    done
  fi
  SK="${VIDEO_SKILLS:-$HOME/.agents/skills}"
  ENG="$SK/video-pipeline/engine"
  [ -d "$ENG" ] || { [ -n "$PKG" ] && ENG="$PKG/skills/video-pipeline/engine"; }
  HF="$ENGINE_DIR/node_modules/.bin/hyperframes"
  [ -f "$HF" ] || HF="$ENGINE_DIR/node_modules/.bin/hyperframes.cmd"
  export PATH="$(dirname "${PY:-/x}"):$ENGINE_DIR/node_modules/.bin:$PATH"
  export VIDEO_ENGINE_DIR="$ENGINE_DIR"
}

# ------------------------------------------------------------------------------------------------ A. package manager
# The original end-to-end test of tools/release.py + bin/video-skills, plus the release-that-drops-a-skill case.
package_manager_test() (
  set -euo pipefail
  REPO_DIR="$PKG"
  for t in git rsync python3; do
    command -v "$t" >/dev/null 2>&1 || { printf '  FAIL  %s is required for the package-manager test\n' "$t"; exit 1; }
  done
  TD="${TMPDIR:-/tmp}"; TD="${TD%/}"
  T="$(mktemp -d "$TD/video-skills-pm.XXXXXX")"; trap 'rm -rf "$T"' EXIT
  pass=0; fail=0
  ok()  { pass=$((pass + 1)); printf '  ok    %s\n' "$1"; }
  bad() { fail=$((fail + 1)); printf '  FAIL  %s\n' "$1"; }
  expect() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
  NSK="$(ls -d "$REPO_DIR"/skills/*/ | wc -l | tr -d ' ')"

  mkdir -p "$T/home" "$T/bin" "$T/ws"
  rsync -a --exclude .git --exclude __pycache__ --exclude _archive --exclude VERSION --exclude manifest.json \
    --exclude CHANGELOG.md "$REPO_DIR/" "$T/src/"
  cd "$T/src"; git init -q; git config user.email t@t; git config user.name t; git config commit.gpgsign false; git config tag.gpgsign false
  git add -A; git commit -qm init
  export HOME="$T/home" VIDEO_SKILLS_HOME="$T/home/.video-skills" VIDEO_SKILLS_BIN="$T/bin" VIDEO_SKILLS_SOURCE="$T/src" PATH="$T/bin:$PATH"
  VS="$T/home/.video-skills"; SK="$T/home/.agents/skills"

  echo "  release 1.0.0 + install"
  python3 tools/release.py 1.0.0 --note "First managed release" >/dev/null
  cd "$T/ws"; python3 "$T/src/bin/video-skills" install --skip-setup >/dev/null
  n=$(ls "$SK" | wc -l | tr -d ' ')
  expect "all skills linked ($n of $NSK)" '[ "$n" -ge "$NSK" ] && [ -L "$SK/video-audio" ]'
  expect "command installed" 'command -v video-skills >/dev/null'
  expect "version 1.0.0" '[ "$(video-skills version)" = "video-skills v1.0.0" ]'

  echo "  user edit + release 1.1.0 + check + update"
  echo "house rule" >> "$SK/video-captions/SKILL.md"
  cd "$T/src"; echo "- audio" >> skills/video-audio/SKILL.md; echo "- captions" >> skills/video-captions/SKILL.md
  git add -A; git commit -qm change; python3 tools/release.py 1.1.0 --note "Better audio notes" >/dev/null; cd "$T/ws"
  expect "check announces 1.1.0 with headline" 'video-skills check | grep -q "v1.0.0 -> v1.1.0 — Better audio notes"'
  out="$(video-skills update --skip-setup)"
  expect "unedited changed skill updated" 'grep -q "video-audio .*updated" <<<"$out"'
  expect "edited changed skill kept as CONFLICT" 'grep -q "video-captions .*CONFLICT" <<<"$out"'
  expect "user edit still in place" 'grep -q "house rule" "$SK/video-captions/SKILL.md"'
  expect "conflict diff written" '[ -s "$VS/conflicts/video-captions-1.1.0.diff" ]'
  expect "unchanged skill keeps its skill version" 'video-skills list | grep -E "^video-watch +1.0.0 +1.1.0 +clean" >/dev/null'

  echo "  force, rollback, partial update"
  video-skills update video-captions --force --skip-setup >/dev/null
  expect "forced: new release linked" '[ "$(readlink "$SK/video-captions")" = "$VS/pkg/1.1.0/skills/video-captions" ]'
  expect "forced: edit backed up" 'grep -rq "house rule" "$VS/backups"'
  expect "forced: old store copy restored to pristine" '! grep -q "house rule" "$VS/pkg/1.0.0/skills/video-captions/SKILL.md"'
  video-skills rollback --skip-setup >/dev/null
  expect "rollback to 1.0.0" '[ "$(video-skills version)" = "video-skills v1.0.0" ] && [ "$(readlink "$SK/video-audio")" = "$VS/pkg/1.0.0/skills/video-audio" ]'
  expect "rollback leaves no edited skills" '! video-skills list | grep -q edited'
  expect "rollback keeps the newest manager (check still shows the headline)" 'video-skills check | grep -q "v1.0.0 -> v1.1.0 — Better audio notes"'
  mkdir -p "$VS/pkg/1.0.0/skills/video-pipeline/engine/assets/vendor"; echo "// gsap" > "$VS/pkg/1.0.0/skills/video-pipeline/engine/assets/vendor/gsap.min.js"
  expect "setup-generated vendor files are not edits" '! video-skills list | grep -E "^video-pipeline .*edited" >/dev/null'
  video-skills update video-audio --version 1.1.0 --skip-setup >/dev/null
  expect "partial update moves one skill only" '[ "$(readlink "$SK/video-audio")" = "$VS/pkg/1.1.0/skills/video-audio" ] && [ "$(readlink "$SK/video-watch")" = "$VS/pkg/1.0.0/skills/video-watch" ]'

  echo "  legacy copy migration, prune, doctor"
  rm "$SK/video-watch"; cp -R "$VS/pkg/1.0.0/skills/video-watch" "$SK/video-watch"
  out="$(video-skills update --version 1.1.0 --skip-setup)"
  expect "unedited old copy migrated to a link" 'grep -q "video-watch .*migrated" <<<"$out" && [ -L "$SK/video-watch" ]'
  video-skills prune --keep 1 >/dev/null
  expect "prune keeps versions in use" '[ -d "$VS/pkg/1.1.0" ]'
  expect "doctor all good" 'video-skills doctor | grep -q "all good"'
  mkdir -p "$T/home/.gemini/config"; ln -s "$SK" "$T/home/.gemini/config/skills"
  expect "agent folder that links to the skills folder is fine" 'video-skills doctor | grep -q "all good"'
  mkdir -p "$T/home/.claude/skills"
  expect "agent folder missing the skills is flagged" 'video-skills doctor | grep -q "FIX   agent folder .*claude/skills"'
  rm -rf "$T/home/.claude"; rm "$SK/video-watch"; ln -s ../../../.agents/skills/video-watch "$SK/video-watch"   # the link the old installer wrote
  expect "self-referencing skill link is flagged" 'video-skills doctor | grep -q "FIX   skill video-watch"'
  video-skills update --force --version 1.1.0 --skip-setup >/dev/null
  expect "update --force repairs it" 'video-skills doctor | grep -q "all good"'

  echo "  a release that drops a skill (as 2.0 did with 10 merged skills)"
  mkdir -p "$T/home/.claude/skills"
  for d in "$SK"/*; do ln -s "$d" "$T/home/.claude/skills/$(basename "$d")"; done
  cd "$T/src"; git rm -rq skills/video-generate; git commit -qm "drop video-generate"
  python3 tools/release.py 1.2.0 --note "Drop video-generate" >/dev/null; cd "$T/ws"
  out="$(video-skills update --skip-setup)"
  expect "dropped skill reported as retired" 'grep -q "video-generate .*retired" <<<"$out"'
  expect "its link is removed (its old rules stop loading)" '[ ! -e "$SK/video-generate" ] && [ ! -L "$SK/video-generate" ]'
  expect "the agent-folder link to it is removed" '[ ! -L "$T/home/.claude/skills/video-generate" ]'
  expect "doctor all good after the drop (state forgets it)" 'video-skills doctor | grep -q "all good"'
  expect "list no longer shows it" '! video-skills list | grep -q "^video-generate "'
  video-skills rollback --skip-setup >/dev/null
  expect "rollback restores the dropped skill" '[ -L "$SK/video-generate" ] && [ "$(video-skills version)" = "video-skills v1.1.0" ]'
  rm -rf "$T/home/.claude"

  echo "  uninstall"
  video-skills uninstall >/dev/null
  expect "uninstall removes links and command" '[ ! -L "$SK/video-audio" ] && [ ! -e "$T/bin/video-skills" ]'

  echo "  $pass passed, $fail failed"
  [ "$fail" = 0 ]
)

run_package_test() {
  section "A. Package manager (sandbox: release, install, update, rollback, retire, doctor, uninstall)"
  if [ -z "$PKG" ] || [ ! -f "$PKG/tools/release.py" ] || [ ! -f "$PKG/bin/video-skills" ]; then
    warn "package-manager test skipped: run this script from the package folder (tools/ next to bin/ and skills/)"
    return
  fi
  if package_manager_test; then pass "package manager works end to end"; else fail "package manager test failed (see above)"; fi
}

# ------------------------------------------------------------------------------------------------ B. checks
run_checks() {
  PASS=0; WARNS=(); FAILS=(); NEED_SETUP=0
  load_env

  section "B1. Installed package and skills"
  if command -v video-skills >/dev/null 2>&1; then
    pass "video-skills $(video-skills version 2>/dev/null | head -1)"
    doc="$(video-skills doctor 2>&1)"
    nfix="$(printf '%s\n' "$doc" | grep -c '  FIX ' || true)"
    if [ "$nfix" = 0 ]; then pass "video-skills doctor: all links and the store are healthy"
    else setup_fail "video-skills doctor found $nfix problem(s):"; printf '%s\n' "$doc" | grep '  FIX ' | sed 's/^/          /'; fi
  else
    warn "video-skills is not on PATH (installed without the package manager: updates are manual)"
  fi
  if [ -n "$PKG" ] && [ -f "$PKG/VERSION" ]; then
    want="$(tr -d '[:space:]' < "$PKG/VERSION")"
    if grep -q "name: video-pipeline" "$SK/video-pipeline/SKILL.md" 2>/dev/null && grep -q "catalog.py" "$SK/video-plan-storyboard/SKILL.md" 2>/dev/null; then
      pass "installed skills are the $want generation"
    else
      setup_fail "installed skills are older than this package ($want): run setup / install.sh --update-skills"
    fi
  fi
  for s in "${SKILLS[@]}"; do
    if [ -f "$SK/$s/SKILL.md" ] && grep -qE "^name: *$s *\$" "$SK/$s/SKILL.md"; then pass "skill $s"
    else setup_fail "skill $s is missing from $SK"; fi
  done
  old=()
  for r in "${RETIRED[@]}"; do [ -e "$SK/$r" ] && old+=("$r"); [ -e "$HOME/.claude/skills/$r" ] && old+=("~/.claude/skills/$r"); done
  if [ ${#old[@]} -eq 0 ]; then pass "no retired 1.x skills still loaded"
  else setup_fail "retired 1.x skills still loaded (their old rules conflict): ${old[*]}"; fi
  if [ -d "$HOME/.claude" ]; then
    miss=(); for s in "${SKILLS[@]}"; do [ -e "$HOME/.claude/skills/$s/SKILL.md" ] || miss+=("$s"); done
    if [ ${#miss[@]} -eq 0 ]; then pass "Claude Code sees all skills (~/.claude/skills)"
    else warn "Claude Code does not see: ${miss[*]} (run setup)"; fi
  fi

  section "B2. Engine, system tools and FFmpeg"
  if [ -n "$PY" ]; then pass "engine Python $("$PY" --version 2>&1) ($PY)"; else setup_fail "engine virtual environment not found (expected $ENGINE_DIR/.venv)"; fi
  if [ -n "$PY" ]; then
    missing="$("$PY" - <<'EOF' 2>&1
import importlib.util
need = ["numpy", "scipy", "soundfile", "nara_wpe", "cv2", "PIL", "pypdf", "pypdfium2"]
print(" ".join(m for m in need if importlib.util.find_spec(m) is None))
EOF
)"
    if [ -z "$missing" ]; then pass "Python packages: numpy scipy soundfile nara_wpe opencv pillow pypdf pypdfium2"
    else setup_fail "Python packages missing in the engine: $missing"; fi
  fi
  for t in ffmpeg ffprobe node; do
    if command -v "$t" >/dev/null 2>&1; then pass "$t: $("$t" -version 2>/dev/null | head -1 | cut -c1-60)"
    else setup_fail "$t not found"; fi
  done
  if command -v ffmpeg >/dev/null 2>&1; then
    filters="$(ffmpeg -hide_banner -filters 2>/dev/null)"
    miss=()
    for f in acompressor alimiter amix apad aresample asplit atrim afade aformat adelay sidechaincompress deesser \
             equalizer highpass highshelf lowshelf loudnorm ebur128 silencedetect blackdetect tpad concat trim setpts \
             select showinfo volume colorlevels colortemperature eq unsharp crop scale sendcmd; do
      printf '%s\n' "$filters" | grep -qE "^ [A-Z.|]+ $f " || miss+=("$f")
    done
    if [ ${#miss[@]} -eq 0 ]; then pass "FFmpeg has every filter the pipeline uses"; else fail "FFmpeg lacks filters: ${miss[*]} (install a full FFmpeg build)"; fi
    printf '%s\n' "$filters" | grep -qE "^ [A-Z.|]+ zscale " && printf '%s\n' "$filters" | grep -qE "^ [A-Z.|]+ tonemap " \
      && pass "HDR tone mapping available (zscale + tonemap)" \
      || warn "FFmpeg has no zscale/tonemap: HDR phone footage is converted without tone mapping (flatter colours)"
    printf '%s\n' "$filters" | grep -qE "^ [A-Z.|]+ drawtext " || warn "FFmpeg has no drawtext: render sheets have no time labels"
    (set +o pipefail; ffmpeg -hide_banner -h full 2>/dev/null | grep -q -- "-fps_mode") && pass "FFmpeg supports -fps_mode (constant frame rate ingest)" \
      || fail "FFmpeg is too old for -fps_mode (needs 5.1+): upgrade FFmpeg"
  fi

  section "B3. Transcription (Hinglish, in sync)"
  if [ -n "$PY" ] && [ -d "$ENG" ]; then
    eval "$("$PY" - "$ENG/scripts" <<'EOF' 2>/dev/null
import sys, shlex
sys.path.insert(0, sys.argv[1])
import config, setup
st = setup.check()
cfg = config.load()
model = st.get("whisper_model") or ""
caps = (st.get("whisper_cli") or {}).get("capabilities") or {}
vals = {
  "W_BIN": (st.get("whisper_cli") or {}).get("path") or "",
  "W_MODEL": model,
  "W_HINGLISH": "1" if st.get("hinglish_model") else "0",
  "W_LANG": config.whisper_lang(cfg, model) if model else "",
  "W_DTW": config.dtw_preset(cfg, model) or "",
  "C_DTW": "1" if caps.get("dtw") else "0",
  "C_OJF": "1" if caps.get("output_json_full") else "0",
  "C_NFA": "1" if caps.get("no_flash_attn") else "0",
  "C_SOW": "1" if caps.get("word_split") else "0",
  "W_PROMPT": cfg.get("WATCH_WHISPER_PROMPT", ""),
  "DF_BIN": st.get("deep_filter") or "",
  "CAT_INDEX": st.get("catalog_index") or "",
}
for k, v in vals.items():
    print("%s=%s" % (k, shlex.quote(str(v))))
EOF
)"
  fi
  W_BIN="${W_BIN:-}"; W_MODEL="${W_MODEL:-}"; W_HINGLISH="${W_HINGLISH:-0}"; W_LANG="${W_LANG:-}"; W_DTW="${W_DTW:-}"
  C_DTW="${C_DTW:-0}"; C_OJF="${C_OJF:-0}"; C_NFA="${C_NFA:-0}"; C_SOW="${C_SOW:-0}"; W_PROMPT="${W_PROMPT:-}"
  DF_BIN="${DF_BIN:-}"; CAT_INDEX="${CAT_INDEX:-}"
  if [ -n "$W_BIN" ]; then pass "whisper-cli: $W_BIN"; else setup_fail "whisper-cli not found (macOS: brew install whisper-cpp)"; fi
  if [ -n "$W_BIN" ]; then
    [ "$C_SOW" = 1 ] && pass "whisper-cli has word splitting (-ml 1 -sow)" || fail "whisper-cli lacks --split-on-word/--max-len: upgrade whisper.cpp"
    if [ "$C_DTW" = 1 ] && [ "$C_OJF" = 1 ]; then pass "whisper-cli has DTW word timing + full JSON"
    else warn "whisper-cli lacks DTW or full JSON: word timing falls back to segments + speech-energy snapping (upgrade whisper.cpp)"; fi
    [ "$C_NFA" = 1 ] || warn "whisper-cli has no --no-flash-attn flag (older build; DTW may be ignored)"
  fi
  if [ -z "$W_MODEL" ]; then setup_fail "no Whisper model found (setup downloads the Hinglish model)"
  elif [ "$W_HINGLISH" = 1 ]; then pass "Hinglish model: $(basename "$W_MODEL") (Roman Hinglish, decoder token '$W_LANG', DTW preset '${W_DTW:-none}')"
  else
    warn "stock Whisper model $(basename "$W_MODEL"): Hindi is decoded and romanised; install the Hinglish model for natural spelling"
    [ "$W_LANG" = "en" ] && fail "WATCH_WHISPER_LANG=en with a stock model TRANSLATES Hindi: set WATCH_WHISPER_LANG=auto in ~/.config/video-skills/.env"
  fi
  if [ -n "$W_PROMPT" ] && [ "$(printf '%s' "$W_PROMPT" | wc -w | tr -d ' ')" -gt 12 ]; then
    warn "WATCH_WHISPER_PROMPT looks like a sentence; a topic sentence leaks into transcripts (names only)"
  fi

  section "B4. Audio (DeepFilterNet)"
  if [ -n "$DF_BIN" ] && "$DF_BIN" --help >/dev/null 2>&1; then
    pass "DeepFilterNet runs: $DF_BIN"
    help="$("$DF_BIN" --help 2>&1)"
    printf '%s' "$help" | grep -q -- "--compensate-delay" && pass "DeepFilterNet delay compensation (-D)" \
      || warn "DeepFilterNet has no -D: the pipeline removes the delay by cross-correlation instead"
    printf '%s' "$help" | grep -q -- "--atten-lim" && pass "DeepFilterNet strength control (--atten-lim)" \
      || warn "DeepFilterNet has no --atten-lim: denoise always runs at full strength (can sound thin on clean rooms)"
    printf '%s' "$help" | grep -q -- "--pf" && pass "DeepFilterNet post-filter (--pf) for noisy rooms" || warn "DeepFilterNet has no --pf"
  else
    setup_fail "DeepFilterNet (deep-filter) not found or not runnable: audio pass 1 needs it"
  fi

  section "B5. HyperFrames, catalog, fonts, sounds"
  if [ -f "$HF" ]; then
    pass "HyperFrames CLI $("$HF" --version 2>/dev/null | head -1)"
    if "$HF" doctor 2>&1 | grep -qE "✗ +Chrome"; then fail "HyperFrames cannot start Chrome: run \"$HF\" browser ensure"; else pass "HyperFrames doctor: Chrome OK"; fi
  else
    setup_fail "HyperFrames CLI not found in $ENGINE_DIR/node_modules"
  fi
  comps="$ENGINE_DIR/compositions"
  ncomp="$(find "$comps" -name '*.html' 2>/dev/null | wc -l | tr -d ' ')"
  [ "${ncomp:-0}" -gt 0 ] && pass "HyperFrames catalog installed: $ncomp compositions" || setup_fail "HyperFrames catalog not installed in $comps"
  if [ -n "$CAT_INDEX" ] && [ -n "$PY" ]; then
    hits="$("$PY" "$ENG/scripts/catalog.py" search --json 2>/dev/null | "$PY" -c 'import json,sys; print(len(json.load(sys.stdin)))' 2>/dev/null || echo 0)"
    [ "${hits:-0}" -gt 0 ] && pass "catalog index searchable ($CAT_INDEX)" || fail "catalog index is empty or unreadable: catalog.py build"
  elif [ "${ncomp:-0}" -gt 0 ] && [ -n "$PY" ]; then
    if "$PY" "$ENG/scripts/catalog.py" build >/dev/null 2>&1; then pass "catalog index built now"; CAT_INDEX="$comps/catalog.json"
    else fail "catalog index missing and could not be built: \"$PY\" \"$ENG/scripts/catalog.py\" build"; fi
  else
    setup_fail "catalog index missing"
  fi
  [ -f "$ENG/assets/vendor/gsap.min.js" ] && pass "local GSAP" || setup_fail "local GSAP missing ($ENG/assets/vendor/gsap.min.js)"
  [ -f "$ENG/assets/fonts/inter/Inter-Variable.ttf" ] && pass "caption font Inter (variable, semi-bold 600)" || fail "caption font missing ($ENG/assets/fonts/inter)"
  pal="$(ls "$ENGINE_DIR/sound-palette/audio/"*.mp3 "$SK/sound-palette/audio/"*.mp3 2>/dev/null | wc -l | tr -d ' ')"
  [ "${pal:-0}" -gt 0 ] && pass "sound palette ($pal effects)" || warn "sound palette not found (sound effects need a project file)"
  [ -s "$HOME/.config/video-skills/models/face_detection_yunet_2023mar.onnx" ] && pass "YuNet face model (reframe)" \
    || warn "YuNet face model missing: reframing falls back to a weaker face detector"

  section "B6. Workspace"
  for legacy in MEMO.md STYLE-GUIDE.md; do
    [ -f "$WORKSPACE/brand/$legacy" ] && warn "brand/$legacy is a 1.x template; it is ignored now (delete it, or add your real brand files)"
  done
  pass "workspace: $WORKSPACE"
}

do_setup() {
  section "Setting up (something required is missing)"
  if command -v video-skills >/dev/null 2>&1; then
    (cd "$WORKSPACE" && video-skills setup -- --yes) || return 1
  elif [ -n "$PKG" ]; then
    (cd "$WORKSPACE" && bash "$PKG/install.sh" --yes --update-skills) || return 1
  else
    echo "  No video-skills command and no package folder next to this script. Install with:"
    echo "  curl -fsSL https://raw.githubusercontent.com/mg-studio-india/video-editing-skill/main/get.sh | bash"
    return 1
  fi
}

# ------------------------------------------------------------------------------------------------ sample edit
sample_edit() {
  section "C. Sample edit (analyze -> approve -> assemble)"
  TD="${TMPDIR:-/tmp}"; TD="${TD%/}"
  TMP="$(mktemp -d "$TD/video-skills-test.XXXXXX")"
  PROJ="$TMP/videos/smoke-test"
  mkdir -p "$PROJ/raw"
  P="$ENG/scripts/parallel_pipeline.py"

  # spoken words: macOS `say`, else espeak-ng/espeak, else tone bursts (transcript checks then become warnings)
  SPEECH=0
  s1="Namaste dosto. Aaj hum ek chhota sa test video bana rahe hain."
  s2="Is video mein do sau crore ka IPO aur profit ki baat hogi."
  if command -v say >/dev/null 2>&1 && say -o "$TMP/s1.aiff" "$s1" 2>/dev/null && say -o "$TMP/s2.aiff" "$s2" 2>/dev/null; then
    SPEECH=1; E1="$TMP/s1.aiff"; E2="$TMP/s2.aiff"
  elif command -v espeak-ng >/dev/null 2>&1 || command -v espeak >/dev/null 2>&1; then
    ES="$(command -v espeak-ng || command -v espeak)"
    "$ES" -w "$TMP/s1.wav" "$s1" && "$ES" -w "$TMP/s2.wav" "$s2" && { SPEECH=1; E1="$TMP/s1.wav"; E2="$TMP/s2.wav"; }
  fi
  if [ "$SPEECH" = 0 ]; then
    ffmpeg -v error -f lavfi -i "sine=frequency=220:duration=2.5" "$TMP/s1.wav" -y
    ffmpeg -v error -f lavfi -i "sine=frequency=330:duration=2.5" "$TMP/s2.wav" -y
    E1="$TMP/s1.wav"; E2="$TMP/s2.wav"
    warn "no text-to-speech here (say / espeak): the sample uses tones, so transcript checks are skipped"
  fi
  # 0.8 s lead, sentence, 1.6 s pause (must be tightened), sentence, 1.2 s tail; room echo + light noise to clean
  graph="[0:a]aresample=48000,aformat=channel_layouts=mono,adelay=800:all=1,apad=pad_dur=1.6[a0];"
  graph="$graph[1:a]aresample=48000,aformat=channel_layouts=mono,apad=pad_dur=1.2[a1];"
  graph="$graph[a0][a1]concat=n=2:v=0:a=1,aecho=0.8:0.55:45|95:0.35|0.22[v];"
  graph="$graph[v][2:a]amix=inputs=2:duration=first:normalize=0[a]"
  if ! ffmpeg -v error -y -i "$E1" -i "$E2" -f lavfi -i "anoisesrc=color=pink:amplitude=0.006:sample_rate=48000" \
      -filter_complex "$graph" -map "[a]" -c:a pcm_s16le "$TMP/voice.wav"; then
    fail "could not build the sample audio with FFmpeg"; return
  fi
  dur="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/voice.wav")"
  ffmpeg -v error -y -f lavfi -i "testsrc2=size=720x1280:rate=30" -i "$TMP/voice.wav" -t "$dur" \
    -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "$PROJ/raw/clip.mp4" \
    || { fail "could not build the sample clip with FFmpeg"; return; }
  pass "sample clip: $(printf '%.1f' "$dur") s, 720x1280, speech=$([ "$SPEECH" = 1 ] && echo yes || echo tones), echo + noise"

  echo "  analyze (audio pass 1, transcript, cut)..."
  if ! "$PY" "$P" analyze --input "$PROJ/raw/clip.mp4" --project "$PROJ" --prompt "environment test" > "$TMP/analyze.log" 2>&1; then
    fail "analyze failed (log: $TMP/analyze.log)"; tail -15 "$TMP/analyze.log" | sed 's/^/          /'; KEEP=1; return
  fi
  pass "analyze completed"

  "$PY" - "$PROJ/.video-pipeline" "$ENG/scripts" "$SPEECH" > "$TMP/checks.txt" 2>&1 <<'EOF'
import json, sys
from pathlib import Path
W, scripts, speech = Path(sys.argv[1]), sys.argv[2], sys.argv[3] == "1"
sys.path.insert(0, scripts)
def out(kind, msg): print("%s|%s" % (kind, msg))
def j(p):
    return json.loads((W / p).read_text(encoding="utf-8"))
rep = j("audio/voice-clean.json")
dn = rep.get("denoise")
if isinstance(dn, dict):
    out("PASS", "audio pass 1 ran once: dereverb %s + DeepFilterNet %s, SNR %s -> %s dB"
        % (rep.get("dereverb"), dn.get("label"), rep["before"]["snr_db"], rep["after"]["snr_db"]))
else:
    out("FAIL", "audio pass 1 did not run DeepFilterNet (denoise=%s)" % dn)
lag = abs(float(rep.get("lag_corrected_ms") or 0))
out("PASS" if lag < 25 else "WARN", "cleaned voice aligned to the picture (lag corrected: %.2f ms)" % lag)
ab = W / "preview" / "audio-before-after.wav"
out("PASS" if ab.is_file() else "FAIL", "before/after listening clip %s" % ("written" if ab.is_file() else "missing"))
t = j("transcript.source.json")
words = t.get("words", [])
if speech:
    out("PASS" if words else "FAIL", "Hinglish transcript: %d words, e.g. \"%s\"" % (len(words), " ".join(w["text"] for w in words[:8])))
    deva = [w["text"] for w in words if any("ऀ" <= c <= "ॿ" for c in w["text"])]
    out("PASS" if not deva else "FAIL", "transcript is Roman script" + ("" if not deva else " (Devanagari found: %s)" % deva[:3]))
    out("PASS" if t.get("timing") == "dtw" else "WARN", "word timing: %s" % t.get("timing"))
cm, cut = j("cut-map.json"), j("cut-list.json")
src_d = cut["source_duration"]
out("PASS" if abs(cm["tail"] - 1.5) < 0.05 else "FAIL", "fade-out tail %.2f s added" % cm["tail"])
if speech and words:
    out("PASS" if cm["content_duration"] < src_d - 1.0 else "FAIL",
        "tight cut: %.2f s kept of %.2f s (lead-in, the 1.6 s pause and the end trimmed)" % (cm["content_duration"], src_d))
    import speechmask
    mask = speechmask.build(str(W / "audio" / "voice-clean.wav"))
    bad = [round(t_, 2) for k in cut["kept"] for t_ in (k["start"], k["end"]) if not mask.is_quiet(t_)]
    out("PASS" if not bad else "FAIL", "no cut inside a word (%d edges checked%s)" % (2 * len(cut["kept"]), "" if not bad else "; in speech at %s" % bad))
for f in ("hyperframes/input-video.mp4", "hyperframes/voice.wav", "hyperframes/transcript.json", "REVIEW.md", "source-evidence.json"):
    out("PASS" if (W / f).is_file() else "FAIL", "%s %s" % (f, "written" if (W / f).is_file() else "missing"))

# a minimal approved plan: default style, a caption keyword, one sound effect, one catalog block
style_src = Path(scripts).parents[2] / "video-style" / "styles" / "clean-creator.json"
(W / "style.json").write_text(style_src.read_text(encoding="utf-8"), encoding="utf-8")
(W / "resolved-spec.json").write_text(json.dumps({"user_answers": {"platform_aspect": "9:16 test", "style": "clean-creator",
    "cut": "test", "captions": "keywords", "sound": "palette"}, "audio": {"preset": "shorts", "tone": "neutral"}}), encoding="utf-8")
sb = j("storyboard.json")
ev = j("source-evidence.json")
ref = (ev.get("speech_segments") or [{}])[0].get("id") or next(
    (v["id"] for v in ev.get("visual_samples", []) if v.get("flat_time") is not None), None)
fw = j("hyperframes/transcript.json").get("words", [])
sb["captions"] = {"source": "transcript.json", "keywords": [fw[0]["text"]] if fw else []} if fw else None
D = float(sb["duration"])
sb["sfx"] = [{"id": "s1", "src": "pop.mp3", "at": 0.4, "dur": 0.7, "volume": 0.3, "refs": [ref]}] if ref else []
block = None
try:
    import catalog
    items = [i for i in catalog.load() if i.get("type") == "block" and not i["src"].startswith("components/")]
    pref = [i for i in items if any(t in ("lower-third", "title", "text") for t in i.get("tags", []))]
    block = (pref or items or [None])[0]
except SystemExit:
    block = None
if block and ref:
    sb["beats"] = [{"id": "b1", "type": "block", "src": block["src"], "comp_id": block["comp_id"], "vars": {},
                    "in": 0.3, "out": round(max(0.8, min(2.3, D - 1.6)), 3), "refs": [ref], "why": "environment test"}]
    out("PASS", "storyboard uses catalog block '%s'" % block["name"])
else:
    sb["beats"] = []
    out("WARN", "no catalog block or evidence id available; the sample renders without a block")
(W / "storyboard.json").write_text(json.dumps(sb, indent=2), encoding="utf-8")
(W.parent.parent.parent / "block.txt").write_text(block["src"] if block and ref else "", encoding="utf-8")
EOF
  while IFS='|' read -r kind msg; do
    case "$kind" in PASS) pass "$msg" ;; WARN) warn "$msg" ;; FAIL) fail "$msg" ;; *) [ -n "$kind$msg" ] && echo "          $kind$msg" ;; esac
  done < "$TMP/checks.txt"

  echo "  approve + assemble (grade, stage, HyperFrames render, audio pass 2, verify)..."
  if ! "$PY" "$P" approve --project "$PROJ" --user-approved --note "environment test" > "$TMP/approve.log" 2>&1; then
    fail "approve rejected the sample plan (log: $TMP/approve.log)"; tail -5 "$TMP/approve.log" | sed 's/^/          /'; KEEP=1; return
  fi
  pass "approval gate accepted the sample plan"
  if ! "$PY" "$P" assemble --project "$PROJ" > "$TMP/assemble.log" 2>&1; then
    fail "assemble failed (log: $TMP/assemble.log)"; tail -20 "$TMP/assemble.log" | sed 's/^/          /'; KEEP=1; return
  fi
  pass "assemble completed"

  EXP="$PROJ/Exports/smoke-test-v1.mp4"
  W="$PROJ/.video-pipeline"
  if [ ! -f "$EXP" ]; then fail "no export at $EXP"; KEEP=1; return; fi
  pass "export written: Exports/smoke-test-v1.mp4"
  size="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$EXP")"
  [ "$size" = "1080x1920" ] && pass "export is 1080x1920 (9:16)" || fail "export size is $size, expected 1080x1920"
  [ -n "$(ffprobe -v error -select_streams a:0 -show_entries stream=index -of csv=p=0 "$EXP")" ] && pass "export has sound" || fail "export has no audio track"
  [ -z "$(ffprobe -v error -select_streams a:0 -show_entries stream=index -of csv=p=0 "$W/hyperframes/base.mp4" 2>/dev/null)" ] \
    && pass "composition picture is silent (the voice cannot be doubled into an echo)" || fail "composition base video carries audio"
  grep -q "cap-rail" "$W/hyperframes/index.html" && [ "$SPEECH" = 1 ] && pass "captions staged (keywords mode)"
  grep -q "fade-black" "$W/hyperframes/index.html" && pass "fade to black staged" || fail "fade to black missing from the composition"
  blk="$(cat "$TMP/block.txt" 2>/dev/null)"
  if [ -n "$blk" ]; then
    { [ -f "$W/hyperframes/compositions/$blk" ] && grep -q "data-composition-src=\"compositions/$blk\"" "$W/hyperframes/index.html"; } \
      && pass "catalog block staged and referenced at compositions/$blk" || fail "catalog block not staged where the page loads it ($blk)"
  fi
  vr="$(ls "$W/review/"*-VERIFY.md 2>/dev/null | head -1)"
  if [ -n "$vr" ] && grep -q '^\*\*PASS\*\*' "$vr"; then pass "render verification PASS ($(basename "$vr"))"
  else fail "render verification did not pass: ${vr:-no report}"; [ -n "$vr" ] && sed -n '1,20p' "$vr" | sed 's/^/          /'; fi
  "$PY" - "$W" > "$TMP/audio.txt" 2>&1 <<'EOF'
import json, sys
from pathlib import Path
W = Path(sys.argv[1])
reps = sorted((W / "review").glob("*-audio.json"))
if not reps:
    print("FAIL|no audio report from pass 2"); sys.exit()
r = json.loads(reps[-1].read_text())
a = r.get("after", {})
print("%s|audio pass 2 master: %s LUFS, true peak %s dBTP (target %s)" % ("PASS" if r.get("ok") else "FAIL",
      a.get("integrated_lufs"), a.get("true_peak_dbtp"), r.get("target")))
print("%s|sound effect mixed after the voice processing" % ("PASS" if r.get("sfx") else "WARN"))
EOF
  while IFS='|' read -r kind msg; do case "$kind" in PASS) pass "$msg" ;; WARN) warn "$msg" ;; FAIL) fail "$msg" ;; esac; done < "$TMP/audio.txt"
  yavg="$(ffmpeg -hide_banner -sseof -0.05 -i "$EXP" -vf "signalstats,metadata=print:key=lavfi.signalstats.YAVG" -frames:v 1 -f null - 2>&1 \
          | grep -o 'YAVG=[0-9.]*' | head -1 | cut -d= -f2)"
  if [ -n "$yavg" ]; then
    awk -v y="$yavg" 'BEGIN { exit !(y < 24) }' && pass "ends on black (last frame luma $yavg)" || fail "last frame is not black (luma $yavg)"
  else
    warn "could not measure the last frame"
  fi
  [ "$KEEP" = 1 ] || rm -rf "$TMP"
  [ "$KEEP" = 1 ] && echo "  sample project kept: $PROJ (logs in $TMP)"
}

# ------------------------------------------------------------------------------------------------ main
printf '%sVideo editing package + environment check%s%s\n' "$B" "$N" "$( [ -n "$PKG" ] && printf ' (package %s)' "$(cat "$PKG/VERSION" 2>/dev/null)")"
if [ "$PKG_ONLY" = 1 ]; then
  run_package_test
  printf '\n%s== Result%s\n  %d passed, %d warning(s), %d failure(s)\n' "$B" "$N" "$PASS" "${#WARNS[@]}" "${#FAILS[@]}"
  [ ${#FAILS[@]} -eq 0 ]; exit $?
fi
PKG_PASS=0; PKG_WARNS=(); PKG_FAILS=()
if [ "$PKG_TEST" = 1 ] && [ "$QUICK" = 0 ]; then
  run_package_test
  PKG_PASS=$PASS; PKG_WARNS=(${WARNS[@]+"${WARNS[@]}"}); PKG_FAILS=(${FAILS[@]+"${FAILS[@]}"})
fi
run_checks
if [ "$NEED_SETUP" = 1 ] && [ "$FIX" = 1 ]; then
  if do_setup; then
    printf '\n%sRe-checking after setup%s\n' "$B" "$N"
    run_checks
  else
    fail "setup did not finish (see above)"
  fi
fi
# run_checks resets its counters: carry part A's results into the totals
PASS=$((PASS + PKG_PASS))
WARNS=(${PKG_WARNS[@]+"${PKG_WARNS[@]}"} ${WARNS[@]+"${WARNS[@]}"})
FAILS=(${PKG_FAILS[@]+"${PKG_FAILS[@]}"} ${FAILS[@]+"${FAILS[@]}"})
if [ "$QUICK" = 0 ]; then
  if [ ${#FAILS[@]} -eq 0 ]; then sample_edit
  else printf '\n  Sample edit skipped: fix the FAIL items first%s.\n' "$( [ "$FIX" = 0 ] && printf ' (or re-run with --fix)')"; fi
fi

printf '\n%s== Result%s\n  %d passed, %d warning(s), %d failure(s)\n' "$B" "$N" "$PASS" "${#WARNS[@]}" "${#FAILS[@]}"
if [ ${#FAILS[@]} -gt 0 ]; then
  printf '%s  NOT READY.%s Fix:\n' "$R" "$N"
  for f in "${FAILS[@]}"; do printf '   - %s\n' "$f"; done
  [ "$NEED_SETUP" = 1 ] && [ "$FIX" = 0 ] && printf '  Setup can fix some of these: bash %s --fix\n' "$0"
  exit 1
fi
if [ ${#WARNS[@]} -gt 0 ]; then
  printf '%s  READY, with warnings%s (quality may be lower):\n' "$Y" "$N"
  for w in "${WARNS[@]}"; do printf '   - %s\n' "$w"; done
else
  printf '%s  READY to edit.%s\n' "$G" "$N"
fi
exit 0
