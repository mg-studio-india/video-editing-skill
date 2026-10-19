#!/usr/bin/env bash
# test-package-manager.sh: end-to-end test of tools/release.py + bin/video-skills in a throwaway sandbox
# (fake HOME, a git copy of this repo as the release source). Touches nothing outside the sandbox. Run before releasing:
#   bash tools/test-package-manager.sh
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
pass=0; fail=0
ok()  { pass=$((pass + 1)); printf '  ok    %s\n' "$1"; }
bad() { fail=$((fail + 1)); printf '  FAIL  %s\n' "$1"; }
expect() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }

mkdir -p "$T/home" "$T/bin" "$T/ws"
rsync -a --exclude .git --exclude __pycache__ --exclude VERSION --exclude manifest.json --exclude CHANGELOG.md "$REPO_DIR/" "$T/src/"
cd "$T/src"; git init -q; git config user.email t@t; git config user.name t; git config commit.gpgsign false; git config tag.gpgsign false
git add -A; git commit -qm init
export HOME="$T/home" VIDEO_SKILLS_HOME="$T/home/.video-skills" VIDEO_SKILLS_BIN="$T/bin" VIDEO_SKILLS_SOURCE="$T/src" PATH="$T/bin:$PATH"
VS="$T/home/.video-skills"; SK="$T/home/.agents/skills"

echo "release 1.0.0 + install"
python3 tools/release.py 1.0.0 --note "First managed release" >/dev/null
cd "$T/ws"; python3 "$T/src/bin/video-skills" install --skip-setup >/dev/null
n=$(ls "$SK" | wc -l | tr -d ' ')
expect "all skills linked ($n)" '[ "$n" -ge 15 ] && [ -L "$SK/video-audio" ]'
expect "command installed" 'command -v video-skills >/dev/null'
expect "version 1.0.0" '[ "$(video-skills version)" = "video-skills v1.0.0" ]'

echo "user edit + release 1.1.0 + check + update"
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

echo "force, rollback, partial update"
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

echo "legacy copy migration, prune, doctor, uninstall"
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
video-skills uninstall >/dev/null
expect "uninstall removes links and command" '[ ! -L "$SK/video-audio" ] && [ ! -e "$T/bin/video-skills" ]'

echo "$pass passed, $fail failed"
[ "$fail" = 0 ]
