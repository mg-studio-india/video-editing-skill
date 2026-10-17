#!/usr/bin/env python3
"""render.py: one command from a checked composition to a deliverable file, with no step skipped.

  1. npx hyperframes render  (resolution preset, bitrate for the platform)
  2. BT.709 tags, lossless  (the render leaves them unknown; QuickTime then shows faces darker and redder)
  3. audio master            (audio-chain.py: loudness to the preset, true-peak limit, optional ducked music)
  4. verify-render.py        (resolution, tags, bitrate, duration, A/V, black frames) -> VERIFY.md; exit 1 = do not deliver

Usage:
  python3 render.py --public W/hyperframes --out W/processed/<project>-v1.mp4 --resolution portrait --audio-preset shorts
      [--music W/music/bed.wav] [--gpu] [--workers N]
  --raw FILE skips step 1 and finishes an existing render.
Resolution presets (HyperFrames): portrait 1080x1920, portrait-4k 2160x3840, landscape 1920x1080, landscape-4k
3840x2160, square 1080x1080. Over ~2 minutes of 4K, see the render traps in motion-graphics/references/kit-motion.md.
"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRESETS = {"portrait": (1080, 1920, "12M"), "portrait-4k": (2160, 3840, "45M"), "landscape": (1920, 1080, "12M"),
           "landscape-4k": (3840, 2160, "45M"), "square": (1080, 1080, "10M"), "square-4k": (2160, 2160, "35M")}


def step(name, cmd):
    print("== %s" % name)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit("%s failed (exit %d): %s" % (name, r.returncode, " ".join(cmd)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--public", help="path to composition directory (e.g. W/hyperframes)")
    ap.add_argument("--hyperframes", dest="public", help="alias for --public (e.g. W/hyperframes)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--resolution", default="portrait", choices=sorted(PRESETS))
    ap.add_argument("--audio-preset", default="shorts", choices=["youtube", "shorts", "longform", "broadcast"])
    ap.add_argument("--music")
    ap.add_argument("--raw", help="an existing render to finish (skips the HyperFrames render)")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--workers", default="auto")
    ap.add_argument("--bitrate", help="override the preset's video bitrate, e.g. 16M")
    a = ap.parse_args()
    if not a.public:
        ap.error("--public or --hyperframes is required")
    w, h, br = PRESETS[a.resolution]
    br = a.bitrate or br
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    stem = os.path.splitext(a.out)[0]
    raw, tagged = a.raw or stem + "-raw.mp4", stem + "-tagged.mp4"
    if not a.raw:
        cmd = ["npx", "hyperframes", "render", a.public, "--resolution", a.resolution, "--video-bitrate", br,
               "--workers", str(a.workers), "-o", raw]
        if a.gpu:
            cmd.append("--gpu")
        step("render (%s, %s)" % (a.resolution, br), cmd)
    step("BT.709 tags", ["ffmpeg", "-y", "-v", "error", "-i", raw, "-c", "copy", "-color_primaries", "bt709",
                         "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
                         "-movflags", "+write_colr+faststart", tagged])
    master = [sys.executable, os.path.join(HERE, "audio-chain.py"), "master", tagged, "--out", a.out,
              "--preset", a.audio_preset, "--report", stem + "-audio.json"]
    if a.music:
        master += ["--music", a.music]
    step("audio master (%s)" % a.audio_preset, master)
    os.remove(tagged)
    vcmd = [sys.executable, os.path.join(HERE, "verify-render.py"), "--render", a.out, "--res", "%dx%d" % (w, h),
            "--out", stem + "-VERIFY.md"]
    idx = os.path.join(a.public, "index.html")
    if os.path.isfile(idx):
        vcmd += ["--index", idx]
    r = subprocess.run(vcmd)
    print("deliverable: %s\nverify: %s-VERIFY.md (%s)" % (a.out, stem, "PASS" if r.returncode == 0 else "FAIL: do not deliver"))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
