#!/usr/bin/env python3
"""heygen-sound.py: sound effects from local sound-palette and HeyGen's sound library, through HyperFrames' audio engine."""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runtime
runtime.ensure_project_venv()



def find_sound_palette() -> str | None:
    cands = [
        os.environ.get("VIDEO_SOUND_PALETTE", ""),
        os.path.join(os.getcwd(), "sound-palette"),
        os.path.join(os.environ.get("VIDEO_SKILLS", ""), "sound-palette") if os.environ.get("VIDEO_SKILLS") else "",
        os.path.abspath(os.path.join(HERE, "../../../..", "sound-palette")),
        os.path.expanduser("~/.config/video-skills/sound-palette"),
        os.path.expanduser("~/.video-skills/engine/sound-palette"),
        os.path.expanduser("~/.agents/skills/sound-palette")
    ]
    for c in cands:
        if c and os.path.isfile(os.path.join(c, "sound-palette.json")):
            return c
    return None


def find_media_use() -> str | None:
    cands = [os.environ.get("HF_MEDIA_USE_DIR", ""),
             os.path.join(os.environ.get("VIDEO_SKILLS", ""), "media-use") if os.environ.get("VIDEO_SKILLS") else "",
             os.path.join(os.getcwd(), ".agents", "skills", "media-use"),
             os.path.join(os.getcwd(), ".claude", "skills", "media-use"), os.path.expanduser("~/.claude/skills/media-use"),
             os.path.expanduser("~/.agents/skills/media-use")]
    for c in cands:
        if c and os.path.isfile(os.path.join(c, "audio", "scripts", "audio.mjs")):
            return c
    return None


def signed_in() -> tuple[bool, str]:
    if os.environ.get("HEYGEN_API_KEY"):
        return True, "HEYGEN_API_KEY is set"
    try:
        r = subprocess.run(["npx", "hyperframes", "auth", "status"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, "could not run `npx hyperframes auth status`: %s" % e
    text = (r.stdout + r.stderr).strip()
    return ("not signed in" not in text.lower() and r.returncode == 0), text.splitlines()[0] if text else "unknown"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "sfx"


def resolve_from_palette(sfx_list: list[dict], public_dir: str) -> tuple[list[dict], list[dict], list[dict]]:
    palette_dir = find_sound_palette()
    if not palette_dir:
        return sfx_list, [], []

    try:
        manifest = json.load(open(os.path.join(palette_dir, "sound-palette.json")))
    except Exception:
        return sfx_list, [], []

    palette_items = manifest.get("palette", [])
    os.makedirs(os.path.join(public_dir, "sfx"), exist_ok=True)

    unmatched = []
    resolved = []
    ledger = []

    def find_match(req_name: str) -> dict | None:
        req_slug = slug(req_name)
        req_tokens = set(req_slug.split("-"))
        # 1. Exact ID, slug, or name
        for item in palette_items:
            i_id = item.get("id", "").lower().replace("_", "-")
            if req_slug == i_id or req_name.lower() == item.get("name", "").lower() or req_slug == slug(item.get("name", "")):
                return item
        # 2. Trigger phrases match
        for item in palette_items:
            for t in item.get("triggers", []):
                t_tokens = set(slug(t).split("-"))
                if t_tokens.issubset(req_tokens) or req_tokens.issubset(t_tokens) or (len(t_tokens & req_tokens) >= 2):
                    return item
        # 3. Stem & core token overlap
        for item in palette_items:
            stem_tokens = set(slug(os.path.splitext(item.get("file", ""))[0]).split("-"))
            if len(stem_tokens & req_tokens) >= 1 and any(core in req_tokens for core in [
                "click", "pop", "whoosh", "paper", "impact", "riser", "ping", "chime", "glitch", "buzzer", "typing", "shutter", "key", "bell"
            ]):
                return item
        return None

    for s in sfx_list:
        if s.get("src") and s.get("dur"):
            resolved.append(s)
            continue
        req_name = (s.get("name") or s.get("id") or "").strip()
        matched_item = find_match(req_name)
        if matched_item:
            src_audio = os.path.join(palette_dir, "audio", matched_item["file"])
            if os.path.isfile(src_audio):
                dst_rel = "sfx/%s.wav" % slug(req_name)
                dst_path = os.path.join(public_dir, dst_rel)
                p = subprocess.run([runtime.get_project_venv_python(), os.path.join(HERE, "sfx-prep.py"), src_audio, dst_path, "--max", "3.0"],
                                   capture_output=True, text=True)
                if p.returncode == 0:
                    dur = round(duration(dst_path), 3)
                    s["src"] = dst_rel
                    s["dur"] = dur
                    s.setdefault("volume", matched_item.get("volume", 0.25))
                    resolved.append(s)
                    ledger.append({"name": s.get("name") or matched_item.get("name"), "file": dst_rel, "source": "sound-palette"})
                    continue
        unmatched.append(s)

    return unmatched, resolved, ledger


def build_request(sfx: list[dict], music: str | None) -> dict:
    names = []
    for s in sfx:
        n = s.get("name")
        if n and n not in names:
            names.append(n)
    return {"lines": [{"id": "sfx-%d" % i, "text": "", "sfx": [n]} for i, n in enumerate(names)],
            "bgm": {"mode": "retrieve", "query": music} if music else {"mode": "none"}}


def apply_results(plan: dict, by_name: dict[str, dict]) -> tuple[dict, list[str]]:
    missing = []
    for s in plan.get("sfx", []):
        hit = by_name.get(s.get("name"))
        if hit:
            s["src"], s["dur"] = hit["src"], hit["dur"]
            s.setdefault("volume", 0.3)
        elif s.get("name") and not (s.get("src") and s.get("dur")):
            missing.append(s["name"])
    return plan, missing


def duration(path: str) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plan")
    ap.add_argument("--public")
    ap.add_argument("--hyperframes", dest="public", help="alias for --public (e.g. W/hyperframes)")
    ap.add_argument("--music", help="music mood to retrieve, e.g. 'calm lo-fi under voice' (omit for no music)")
    ap.add_argument("--allow-bundled", action="store_true", help="the user agreed to HyperFrames' bundled effects without HeyGen")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    mu = find_media_use()
    pal = find_sound_palette()
    ok, why = signed_in()
    if a.check:
        print("media-use: %s" % (mu or "NOT FOUND: npx hyperframes skills update media-use"))
        print("sound-palette: %s" % (pal or "NOT FOUND"))
        print("HeyGen: %s (%s)" % ("signed in" if ok else "not signed in", why))
        return
    if not (a.plan and a.public):
        ap.error("--plan and --public are required")

    plan = json.load(open(a.plan))
    proj = os.path.dirname(os.path.abspath(a.plan))
    os.makedirs(os.path.join(a.public, "sfx"), exist_ok=True)

    # 1. Resolve matching sound effects from local sound-palette first
    unmatched_sfx, resolved_sfx, pal_led = resolve_from_palette(plan.get("sfx", []), a.public)

    # If all sfx are resolved and no external music retrieval is requested, finish cleanly
    if not unmatched_sfx and (not a.music or not ok):
        json.dump(plan, open(a.plan, "w"), indent=1, ensure_ascii=False)
        if pal_led:
            lp = os.path.join(proj, "sound-ledger.json")
            old = json.load(open(lp)) if os.path.isfile(lp) else []
            stamp = dt.datetime.now().isoformat(timespec="seconds")
            json.dump(old + [{**e, "at": stamp} for e in pal_led], open(lp, "w"), indent=1, ensure_ascii=False)
            for e in pal_led:
                print("  %-28s %-14s %s" % (e["name"], e["source"], e["file"]))
        if a.music and not ok:
            print("no music retrieved for %r (HeyGen not signed in)" % a.music)
        return

    req = build_request(unmatched_sfx, a.music if ok else None)
    if not req["lines"] and req["bgm"]["mode"] == "none":
        json.dump(plan, open(a.plan, "w"), indent=1, ensure_ascii=False)
        return

    if not mu:
        sys.exit("media-use is not installed: npx hyperframes skills update media-use")
    if not ok and not a.allow_bundled:
        if resolved_sfx:
            json.dump(plan, open(a.plan, "w"), indent=1, ensure_ascii=False)
            unmatched_names = [s.get("name") or s.get("id") for s in unmatched_sfx]
            sys.exit("HeyGen is not signed in (%s).\n%d effect(s) were resolved from local sound-palette, but %d were unmatched: %s.\n"
                     "Sign in with `npx hyperframes auth login` (or set HEYGEN_API_KEY), or name unmatched sounds from the sound-palette." % (
                         why, len(resolved_sfx), len(unmatched_names), ", ".join(unmatched_names)))
        sys.exit("HeyGen is not signed in (%s).\nSign in with `npx hyperframes auth login` (or set HEYGEN_API_KEY), then run "
                 "again. Without HeyGen, music is skipped and effects can only come from local sound-palette or HyperFrames' bundled files "
                 "(--allow-bundled, with the user's agreement)." % why)

    work = tempfile.mkdtemp(prefix="heygen-sound-")
    json.dump(req, open(os.path.join(work, "req.json"), "w"))
    r = subprocess.run(["node", os.path.join(mu, "audio", "scripts", "audio.mjs"), "--request", "req.json",
                        "--out", "meta.json", "--only", "sfx,bgm"], cwd=work, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0 or not os.path.isfile(os.path.join(work, "meta.json")):
        sys.exit("the HyperFrames audio engine failed: %s" % (r.stderr.strip()[-600:] or "no output"))
    meta = json.load(open(os.path.join(work, "meta.json")))

    by_name, ext_led = {}, []
    for s in meta.get("sfx", []):
        src = os.path.join(work, s["file"])
        dst_rel = "sfx/%s.wav" % slug(s["name"])
        p = subprocess.run([runtime.get_project_venv_python(), os.path.join(HERE, "sfx-prep.py"), src, os.path.join(a.public, dst_rel), "--max", "2.5"],
                           capture_output=True, text=True)
        if p.returncode != 0:
            print("  %s: could not prepare (%s); skipped" % (s["name"], p.stderr.strip()[-200:]))
            continue
        by_name[s["name"]] = {"src": dst_rel, "dur": round(duration(os.path.join(a.public, dst_rel)), 3)}
        ext_led.append({"name": s["name"], "file": dst_rel, "source": "heygen" if s.get("source") == "heygen" else "bundled"})

    music = None
    if meta.get("bgm") and meta["bgm"].get("path"):
        os.makedirs(os.path.join(proj, "music"), exist_ok=True)
        music = os.path.join(proj, "music", os.path.basename(meta["bgm"]["path"]))
        shutil.copyfile(os.path.join(work, meta["bgm"]["path"]), music)
        ext_led.append({"name": "music: " + (a.music or ""), "file": os.path.relpath(music, proj), "source": "heygen"})

    plan, missing = apply_results(plan, by_name)
    json.dump(plan, open(a.plan, "w"), indent=1, ensure_ascii=False)

    total_led = pal_led + ext_led
    if total_led:
        lp = os.path.join(proj, "sound-ledger.json")
        old = json.load(open(lp)) if os.path.isfile(lp) else []
        stamp = dt.datetime.now().isoformat(timespec="seconds")
        json.dump(old + [{**e, "at": stamp} for e in total_led], open(lp, "w"), indent=1, ensure_ascii=False)
        for e in total_led:
            print("  %-28s %-14s %s" % (e["name"], e["source"], e["file"]))

    if missing:
        print("no match for: %s (name them more concretely, or pick from sound-palette.json)" % ", ".join(missing))
    if a.music and not music:
        print("no music retrieved for %r%s" % (a.music, "" if ok else " (HeyGen not signed in)"))
    if music:
        print("music bed: %s -> render with --music %s" % (os.path.relpath(music, proj), music))
    for anomaly in (meta.get("anomalies") or []):
        print("  note: %s" % anomaly)


if __name__ == "__main__":
    main()
