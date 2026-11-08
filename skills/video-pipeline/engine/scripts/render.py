#!/usr/bin/env python3
"""render.py: one command from a checked composition to a deliverable file, with no step skipped."""
import argparse, json, os, subprocess, sys
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
    raise RuntimeError("Local HyperFrames CLI not found. Install it in the configured video engine with the pipeline setup; refusing to fetch or run an unpinned package.")


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
    ap.add_argument("--dereverb", default="strong", choices=["off", "light", "medium", "strong"],
                    help="late-reflection suppression strength for the audio master")
    ap.add_argument("--music")
    ap.add_argument("--raw", help="an existing render to finish (skips the HyperFrames render)")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--workers", default="auto")
    ap.add_argument("--scratch-dir", help="parent folder for disposable render and verification intermediates")
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
    scratch = Path(a.scratch_dir).expanduser().resolve() if a.scratch_dir else Path(os.path.dirname(os.path.abspath(a.out)))
    scratch.mkdir(parents=True, exist_ok=True)
    stem = str(scratch / Path(a.out).stem)
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
    # Keep both mastering passes lossless. Pass one runs the existing audio chain
    # on the rendered mix; pass two consumes that cleaned WAV and runs the same
    # chain again. Optional music is mixed only once, during pass one.
    audio_source = Path(stem + "-audio-source.wav")
    pass1_audio = Path(stem + "-audio-pass-1.wav")
    pass2_audio = Path(stem + "-audio-pass-2.wav")
    pass1_report = Path(stem + "-audio-pass-1.json")
    pass2_report = Path(stem + "-audio-pass-2.json")
    report_path = Path(stem + "-audio.json")
    step("extract lossless audio for two-pass master", [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", tagged,
        "-map", "0:a:0", "-vn", "-ar", "48000", "-c:a", "pcm_s24le", str(audio_source),
    ])

    def audio_master(media, out, report, pass_scratch, include_music=False):
        cmd = [runtime.get_project_venv_python(), os.path.join(HERE, "audio-chain.py"), "master",
               str(media), "--out", str(out), "--preset", a.audio_preset,
               "--report", str(report), "--scratch-dir", str(pass_scratch)]
        if a.denoise:
            cmd += ["--denoise", a.denoise]
        cmd += ["--dereverb", a.dereverb]
        if include_music and a.music:
            cmd += ["--music", a.music]
        return cmd

    step("audio master pass 1/2 (%s, denoise=%s)" % (a.audio_preset, a.denoise),
         audio_master(audio_source, pass1_audio, pass1_report, scratch / "audio-chain" / "pass-1",
                      include_music=True))
    step("audio master pass 2/2 from pass 1 cleaned audio (%s, denoise=%s)" %
         (a.audio_preset, a.denoise),
         audio_master(pass1_audio, pass2_audio, pass2_report, scratch / "audio-chain" / "pass-2"))

    step("attach pass-2 audio to rendered picture", [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", tagged, "-i", str(pass2_audio),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
        "-ar", "48000", "-shortest", "-movflags", "+faststart", a.out,
    ])

    # Preserve the existing summary report path while retaining each pass's
    # detailed measurements for review.
    pass1_data = json.loads(pass1_report.read_text(encoding="utf-8"))
    pass2_data = json.loads(pass2_report.read_text(encoding="utf-8"))
    report_path.write_text(json.dumps({
        "mode": "two-pass-master",
        "preset": a.audio_preset,
        "denoise": a.denoise,
        "dereverb": a.dereverb,
        "music_mixed_on_pass": 1 if a.music else None,
        "passes": [
            {"pass": 1, "input": str(audio_source), "output": str(pass1_audio), "report": pass1_data},
            {"pass": 2, "input": str(pass1_audio), "output": str(pass2_audio), "report": pass2_data},
        ],
        "deliverable": a.out,
    }, indent=2), encoding="utf-8")
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
