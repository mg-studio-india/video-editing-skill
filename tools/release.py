#!/usr/bin/env python3
"""release.py: cut a release of video-editing-skill (maintainers).

  python3 tools/release.py 1.2.0 --note "Reference index with 50 style blueprints" --note "Faster dead-air scan" [--push]
  python3 tools/release.py 1.2.0 --dry-run          show what would change, write nothing

1. refuses a dirty working tree (commit your work first) and a version that is not newer than VERSION
2. writes manifest.json: package version + date, and per skill its file hashes, tree hash and version; a skill whose
   files changed since the previous release gets the new version, an unchanged skill keeps its previous version
3. prepends a CHANGELOG.md section (your --note lines + the list of changed skills)
4. writes VERSION, commits the three files, tags vX.Y.Z
5. --push: git push origin HEAD vX.Y.Z, then `gh release create` with the changelog section as notes
   (users get it with `video-skills update`; `video-skills check` and the pipeline's project-start check announce it)
"""
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IGNORE = {"__pycache__", ".DS_Store", ".git"}


def git(*a, check=True):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=check).stdout.strip()


def vkey(v):
    return tuple(int(x) for x in v.split("."))


def file_hashes(root):
    out = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if p.is_file() and not (set(rel.parts) & IGNORE) and p.suffix != ".pyc" and "assets/vendor/" not in rel.as_posix() + "/":
            out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("version")
    ap.add_argument("--note", action="append", default=[], help="a changelog line (repeat)")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true", help="release with uncommitted changes (not recommended)")
    ap.add_argument("--trailer", action="append", default=[], help='commit trailer line, e.g. "Co-Authored-By: Name <mail>"')
    a = ap.parse_args()
    v = a.version.lstrip("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", v):
        sys.exit("version must be X.Y.Z")
    prev = (ROOT / "VERSION").read_text().strip() if (ROOT / "VERSION").is_file() else None
    if prev and vkey(v) <= vkey(prev):
        sys.exit("v%s is not newer than the current VERSION %s" % (v, prev))
    if git("tag", "-l", "v" + v):
        sys.exit("tag v%s already exists" % v)
    dirty = git("status", "--porcelain")
    if dirty and not (a.allow_dirty or a.dry_run):
        sys.exit("working tree has uncommitted changes; commit them first (the tag must contain them):\n" + dirty)

    old = json.loads((ROOT / "manifest.json").read_text()) if (ROOT / "manifest.json").is_file() else {"skills": {}}
    skills, changed = {}, []
    for d in sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir()):
        files = file_hashes(d)
        th = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
        o = old.get("skills", {}).get(d.name)
        sv = o["version"] if o and o.get("tree") == th else v
        if not o or o.get("tree") != th:
            changed.append("%s %s" % (d.name, ("%s -> %s" % (o["version"], v)) if o else "(new)"))
        skills[d.name] = {"version": sv, "tree": th, "files": files}
    removed = sorted(set(old.get("skills", {})) - set(skills))
    today = datetime.date.today().isoformat()
    man = {"schema": "video-skills-manifest/1", "version": v, "released": today, "repo": "mg-studio-india/video-editing-skill",
           "skills": skills}

    sec = ["## [%s] - %s" % (v, today), ""] + ["- %s" % n for n in a.note]
    if changed:
        sec += ["", "Skills changed: " + ", ".join(changed)]
    if removed:
        sec += ["", "Skills removed: " + ", ".join(removed)]
    section = "\n".join(sec).strip() + "\n"
    print(section)
    print("%d skills, %d changed%s" % (len(skills), len(changed), ", %d removed" % len(removed) if removed else ""))
    if a.dry_run:
        return

    cl = ROOT / "CHANGELOG.md"
    body = cl.read_text() if cl.is_file() else "# Changelog\n\nEvery release of video-editing-skill. Update with `video-skills update`.\n"
    head, sep, rest = body.partition("\n## ")
    cl.write_text(head.rstrip() + "\n\n" + section + ("\n## " + rest if sep else ""))
    (ROOT / "manifest.json").write_text(json.dumps(man, indent=1) + "\n")
    (ROOT / "VERSION").write_text(v + "\n")
    git("add", "VERSION", "manifest.json", "CHANGELOG.md")
    git("commit", "-m", "release v%s" % v + ("\n\n" + "\n".join(a.trailer) if a.trailer else ""))
    git("tag", "-a", "v" + v, "-m", "video-editing-skill v%s" % v)
    print("committed and tagged v%s" % v)
    if a.push:
        git("push", "origin", "HEAD", "v" + v)
        subprocess.run(["gh", "release", "create", "v" + v, "--title", "v" + v, "--notes", section], cwd=ROOT, check=True)
        print("pushed and published v%s" % v)
    else:
        print("publish with: git push origin HEAD v%s && gh release create v%s --notes-file <(sed -n '/## \\[%s\\]/,/^## \\[/p' CHANGELOG.md)" % (v, v, v))


if __name__ == "__main__":
    main()
