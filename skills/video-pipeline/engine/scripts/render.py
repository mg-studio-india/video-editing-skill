#!/usr/bin/env python3
"""render.py: one command from a checked composition to a deliverable file, with no step skipped."""
import argparse, os, subprocess, sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runtime
runtime.ensure_project_venv()

PRESETS = {
    "portrait": (1080, 1920, "25M"),
    "portrait-4k": (2160, 3840, "45M"),
    "portrait-uhd": (2160, 3840, "45M"),
    "landscape": (1920, 1080, "25M"),
    "landscape-4k": (3840, 2160, "45M"),
    "landscape-uhd": (3840, 2160, "45M"),
    "square": (1080, 1080, "20M"),
    "square-4k": (2160, 2160, "35M"),
    "square-uhd": (2160, 2160, "35M"),
    "uhd": (2160, 3840, "45M"),
    "4k": (2160, 3840, "45M"),
}

ALIAS_TO_HF = {
    "uhd": "portrait-4k",
    "4k": "portrait-4k",
    "portrait-uhd": "portrait-4k",
    "landscape-uhd": "landscape-4k",
    "square-uhd": "square-4k",
}


def step(name, cmd):
    print("== %s" % name)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit("%s failed (exit %d): %s" % (name, r.returncode, " ".join(cmd)))


def find_hyperframes_cmd() -> list[str]:
    bin_name = "hyperframes.cmd" if os.name == "nt" else "hyperframes"
    cands = [
        runtime.find_engine_dir() / "node_modules" / ".bin" / bin_name,
        Path.cwd() / ".engine" / "node_modules" / ".bin" / bin_name,
        Path.cwd() / "node_modules" / ".bin" / bin_name,
    ]
    for c in cands:
        if c.is_file():
            return [str(c)]
    return ["npx", "hyperframes"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--public", help="path to composition directory (e.g. W/hyperframes)")
    ap.add_argument("--hyperframes", dest="public", help="alias for --public (e.g. W/hyperframes)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--resolution", default="portrait-4k", choices=sorted(PRESETS),
                    help="render resolution preset (default: portrait-4k / UHD)")
    ap.add_argument("--audio-preset", default="shorts", choices=["youtube", "shorts", "longform", "broadcast"])
    ap.add_argument("--denoise", default="auto", choices=["auto", "off", "light", "medium", "strong", "neural"],
                    help="denoising level for audio master (default: auto)")
    ap.add_argument("--music")
    ap.add_argument("--raw", help="an existing render to finish (skips the HyperFrames render)")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--workers", default="auto")
    ap.add_argument("--bitrate", help="override the preset's video bitrate, e.g. 16M")
    ap.add_argument("--sdr", action="store_true", default=True,
                    help="force SDR output (default: True, matches BT.709 mastering)")
    ap.add_argument("--hdr", dest="sdr", action="store_false",
                    help="allow HDR output when source is HDR")
    a = ap.parse_args()
    if not a.public:
        ap.error("--public or --hyperframes is required")
    w, h, br = PRESETS[a.resolution]
    br = a.bitrate or br
    hf_res = ALIAS_TO_HF.get(a.resolution, a.resolution)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    stem = os.path.splitext(a.out)[0]
    raw, tagged = a.raw or stem + "-raw.mp4", stem + "-tagged.mp4"
    if not a.raw:
        hf_bin = find_hyperframes_cmd()
        cmd = [*hf_bin, "render", a.public, "--resolution", hf_res, "--video-bitrate", br,
               "--workers", str(a.workers), "-o", raw]
        if a.sdr:
            cmd.append("--sdr")
        if a.gpu:
            cmd.append("--gpu")
        step("render (%s, %s)" % (hf_res, br), cmd)
    step("BT.709 tags", ["ffmpeg", "-y", "-v", "error", "-i", raw, "-c", "copy", "-color_primaries", "bt709",
                         "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
                         "-movflags", "+write_colr+faststart", tagged])
    master = [runtime.get_project_venv_python(), os.path.join(HERE, "audio-chain.py"), "master", tagged, "--out", a.out,
              "--preset", a.audio_preset, "--report", stem + "-audio.json"]
    if a.denoise:
        master += ["--denoise", a.denoise]
    if a.music:
        master += ["--music", a.music]
    step("audio master (%s, denoise=%s)" % (a.audio_preset, a.denoise), master)
    os.remove(tagged)
    vcmd = [runtime.get_project_venv_python(), os.path.join(HERE, "verify-render.py"), "--render", a.out, "--res", "%dx%d" % (w, h),
            "--out", stem + "-VERIFY.md"]
    idx = os.path.join(a.public, "index.html")
    if os.path.isfile(idx):
        vcmd += ["--index", idx]
    r = subprocess.run(vcmd)
    print("deliverable: %s\nverify: %s-VERIFY.md (%s)" % (a.out, stem, "PASS" if r.returncode == 0 else "FAIL: do not deliver"))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
