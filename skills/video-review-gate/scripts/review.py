#!/usr/bin/env python3
"""review.py: gate 4. Everything a reviewer needs on one page, from the FINAL file, not the composition.

Checks (each PASS / FAIL / SKIP, written to REVIEW.md next to the file):
  structure   verify-render.py: resolution, BT.709 tags, bitrate, duration, A/V offset, black frames
  loudness    integrated LUFS within 1 LU of the preset, true peak under its ceiling
  captions    words heard in the final vs the flat-cut transcript (needs --render-words, from transcribe.py on the final)
  frames      a contact sheet of the final at every beat midpoint and around every jump cut, for eyes
Then the notes table: each note the user gives is mapped to the step that owns it.

Usage:
  python3 review.py --final W/output/p-v1.mp4 --preset shorts [--storyboard W/storyboard.json] [--cut-map W/cut-map.json]
      [--transcript W/transcript.json --render-words W/output/p-v1-words.json] [--res 1080x1920]
Exit 1 when any check fails.
"""
import argparse, importlib.util, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _engine_scripts():
    """The shared engine scripts (video-pipeline/engine/scripts): $VIDEO_ENGINE, the sibling skill, or ~/.agents/skills."""
    env = os.environ.get("VIDEO_ENGINE")
    for c in ((os.path.join(env, "scripts") if env else ""), os.path.join(HERE, "..", "..", "video-pipeline", "engine", "scripts"),
              os.path.expanduser("~/.agents/skills/video-pipeline/engine/scripts")):
        if c and os.path.isfile(os.path.join(c, "runtime.py")):
            return os.path.abspath(c)
    raise SystemExit("video-pipeline engine not found: set VIDEO_ENGINE or install the skills side by side")


ENG = _engine_scripts()
sys.path.insert(0, ENG)
import runtime
runtime.ensure_project_venv()

TARGETS = {"youtube": (-14.0, -1.0), "shorts": (-14.0, -1.0), "longform": (-16.0, -1.5), "broadcast": (-23.0, -1.0)}
OWNERS = [("a cut, a word lost, a pause", "video-cut-audit"), ("what appears when, missing or extra moments", "video-plan-storyboard"),
          ("framing, zoom, crop, face covered", "video-take-geometry"), ("layout, size, overlap, a treatment", "video-format"),
          ("how something moves, timing feel", "video-motion-graphics"), ("caption words, timing, look", "video-captions"),
          ("colours, fonts, the overall look", "video-style"), ("a sound effect or music", "video-sound-design"),
          ("level, noise, harshness", "video-audio"), ("a generated shot", "video-generate / video-omni-restyle")]


def mod(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), os.path.join(ENG, name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def loudness_verdict(m, preset):
    """Pure (tested)."""
    lufs, tp = TARGETS[preset]
    ok = m.get("integrated_lufs") is not None and abs(m["integrated_lufs"] - lufs) <= 1.0 \
        and m.get("true_peak_dbtp") is not None and m["true_peak_dbtp"] <= tp + 0.1
    return ok, "%s LUFS, %s dBTP (target %.0f LUFS, peak <= %.1f)" % (m.get("integrated_lufs"), m.get("true_peak_dbtp"), lufs, tp)


def moments(storyboard, cut_map, duration):
    """Pure (tested): beat midpoints plus a frame either side of each jump cut, inside the file."""
    ts = set()
    for b in (storyboard or {}).get("beats", []):
        if isinstance(b.get("in"), (int, float)) and isinstance(b.get("out"), (int, float)):
            ts.add(round((b["in"] + b["out"]) / 2, 2))
    for c in (cut_map or {}).get("cuts", []):
        ts.update({round(c - 0.05, 2), round(c + 0.05, 2)})
    if not ts:
        ts = {round(duration * f, 2) for f in (0.05, 0.25, 0.5, 0.75, 0.95)}
    return sorted(t for t in ts if 0 <= t < duration)[:24]


def _has_drawtext():
    try:
        r = subprocess.run(["ffmpeg", "-filters"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        return "drawtext" in (r.stdout or "")
    except Exception:
        return False


def sheet(final, ts, out):
    sel = "+".join("between(t,%.3f,%.3f)" % (t, t + 0.034) for t in ts)
    cols = 6 if len(ts) > 8 else 4
    rows = (len(ts) + cols - 1) // cols
    vf_parts = ["select='%s'" % sel, "scale=270:-2"]
    if _has_drawtext():
        vf_parts.append("drawtext=text='%{pts\\:hms}':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6")
    vf_parts.append("tile=%dx%d" % (cols, rows))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", final, "-vf",
                    ",".join(vf_parts), "-frames:v", "1", "-fps_mode", "passthrough", out], check=False)
    return os.path.isfile(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--final", required=True)
    ap.add_argument("--preset", default="shorts", choices=sorted(TARGETS))
    ap.add_argument("--storyboard"); ap.add_argument("--cut-map")
    ap.add_argument("--transcript"); ap.add_argument("--render-words")
    ap.add_argument("--res")
    a = ap.parse_args()
    stem = os.path.splitext(a.final)[0]
    rows = []
    vcmd = [runtime.get_project_venv_python(), os.path.join(ENG, "verify-render.py"), "--render", a.final, "--out", stem + "-VERIFY.md"]
    if a.res:
        vcmd += ["--res", a.res]
    if a.transcript and a.render_words:
        vcmd += ["--words", a.render_words, "--kept", a.transcript]
    r = subprocess.run(vcmd, capture_output=True, text=True)
    rows.append(("structure%s" % (" + captions/words" if a.render_words else ""), "PASS" if r.returncode == 0 else "FAIL",
                 "see %s-VERIFY.md" % os.path.basename(stem)))
    if not a.render_words:
        rows.append(("captions vs speech", "SKIP", "transcribe the final (transcribe.py) and pass --render-words"))
    m = mod("audio-chain").measure(a.final)
    ok, txt = loudness_verdict(m, a.preset)
    rows.append(("loudness (%s)" % a.preset, "PASS" if ok else "FAIL", txt))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.final],
                               capture_output=True, text=True).stdout.strip())
    sb = json.load(open(a.storyboard)) if a.storyboard and os.path.isfile(a.storyboard) else None
    cm = json.load(open(a.cut_map)) if a.cut_map and os.path.isfile(a.cut_map) else None
    ts = moments(sb, cm, dur)
    sh = stem + "-review-sheet.png"
    rows.append(("frames", "LOOK" if sheet(a.final, ts, sh) else "FAIL", "%s at %s" % (os.path.basename(sh), ", ".join("%.2f" % t for t in ts))))
    failed = any(s == "FAIL" for _, s, _ in rows)
    md = ["# Review: %s" % os.path.basename(a.final), "", "| Check | Result | Detail |", "|---|---|---|"]
    md += ["| %s | %s | %s |" % row for row in rows]
    md += ["", "Read the frame sheet: face clear, text readable, nothing under the platform buttons, no flash frames, "
           "captions match the words. Watch the whole file once at phone size with sound.", "",
           "## Notes go to the step that owns them", "", "| The note is about... | Owner |", "|---|---|"]
    md += ["| %s | %s |" % o for o in OWNERS]
    md += ["", "Verdict: **%s**" % ("do not deliver: fix the FAIL rows" if failed else "ready for the user's review")]
    open(stem + "-REVIEW.md", "w").write("\n".join(md) + "\n")
    for row in rows:
        print("%-28s %-5s %s" % row)
    print("-> %s-REVIEW.md" % stem)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
