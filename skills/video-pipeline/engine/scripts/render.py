#!/usr/bin/env python3
"""render.py: one command from a staged composition to a verified deliverable.

  1. HyperFrames renders the picture. The base video is muted in the composition, so the render's own audio holds
     only sound effects (and anything a catalog block plays).
  2. audio-chain.py master (pass 2) polishes the lossless voice, mixes the effects and optional music, masters once
     and fades out over the tail.
  3. One mux: picture stream-copied, mix encoded to AAC once, BT.709 tags, exact composition length.
  4. verify-render.py checks resolution, colour tags, duration, A/V length, black frames and writes a frame sheet.
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runtime
runtime.ensure_project_venv()

PRESETS = {
    "portrait": (1080, 1920, "25M"),
    "portrait-4k": (2160, 3840, "45M"),
    "landscape": (1920, 1080, "25M"),
    "landscape-4k": (3840, 2160, "45M"),
    "square": (1080, 1080, "20M"),
    "square-4k": (2160, 2160, "35M"),
}


def step(name, cmd):
    print("== %s" % name)
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit("%s failed (exit %d): %s" % (name, r.returncode, " ".join(str(c) for c in cmd)))


def find_hyperframes_cmd() -> list[str]:
    bin_name = "hyperframes.cmd" if os.name == "nt" else "hyperframes"
    for c in (runtime.find_engine_dir() / "node_modules" / ".bin" / bin_name,
              Path.cwd() / ".engine" / "node_modules" / ".bin" / bin_name):
        if c.is_file():
            return [str(c)]
    raise RuntimeError("Local HyperFrames CLI not found. Run `video-skills setup`; refusing to fetch an unpinned package.")


def composition_duration(index: str) -> float | None:
    try:
        html = open(index, encoding="utf-8").read()
    except OSError:
        return None
    root = re.search(r'<div[^>]*data-composition-id="[^"]+"[^>]*>', html)
    m = root and re.search(r'data-duration="([\d.]+)"', root.group(0))
    return float(m.group(1)) if m else None


def has_audio(media: str) -> bool:
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=index",
                        "-of", "csv=p=0", media], capture_output=True, text=True)
    return bool(p.stdout.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--public", "--hyperframes", dest="public", required=True, help="composition folder (W/hyperframes)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice", required=True, help="lossless flat-cut voice WAV from apply-cut.py (pass-1 cleaned)")
    ap.add_argument("--resolution", default="portrait", choices=sorted(PRESETS))
    ap.add_argument("--audio-preset", default="shorts", choices=["youtube", "shorts", "longform", "broadcast"])
    ap.add_argument("--tone", default="neutral", choices=["neutral", "clear", "warm"])
    ap.add_argument("--music", help="music bed inside the project folder (ducked under the voice)")
    ap.add_argument("--music-db", type=float, default=-20.0)
    ap.add_argument("--fade-out", type=float, default=1.0, help="audio fade over the last N seconds (match the picture fade)")
    ap.add_argument("--raw", help="an existing HyperFrames render to finish (skips the render)")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--workers", default="auto")
    ap.add_argument("--scratch-dir", help="folder for disposable render intermediates")
    ap.add_argument("--bitrate", help="override the preset's video bitrate, e.g. 16M")
    a = ap.parse_args()

    w, h, br = PRESETS[a.resolution]
    br = a.bitrate or br
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    scratch = Path(a.scratch_dir).expanduser().resolve() if a.scratch_dir else Path(os.path.dirname(os.path.abspath(a.out)))
    scratch.mkdir(parents=True, exist_ok=True)
    stem = str(scratch / Path(a.out).stem)
    raw = a.raw or stem + "-raw.mp4"
    index = os.path.join(a.public, "index.html")
    if not a.raw:
        cmd = [*find_hyperframes_cmd(), "render", a.public, "--resolution", a.resolution, "--video-bitrate", br,
               "--workers", str(a.workers), "--sdr", "-o", raw]
        if a.gpu:
            cmd.append("--gpu")
        step("render picture (%s, %s)" % (a.resolution, br), cmd)

    duration = composition_duration(index)
    if duration is None:
        p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
                            "-of", "csv=p=0", raw], capture_output=True, text=True)
        duration = float(p.stdout.strip() or 0)

    sfx = None
    if has_audio(raw):
        sfx = stem + "-sfx.wav"
        step("extract effects track", ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", raw, "-map", "0:a:0",
                                       "-vn", "-ar", "48000", "-c:a", "pcm_f32le", sfx])

    mix = stem + "-mix.wav"
    report = stem + "-audio.json"
    cmd = [runtime.get_project_venv_python(), os.path.join(HERE, "audio-chain.py"), "master", "--voice", a.voice,
           "--out", mix, "--duration", "%.6f" % duration, "--fade-out", str(a.fade_out), "--preset", a.audio_preset,
           "--tone", a.tone, "--report", report, "--scratch-dir", str(scratch), "--music-db", str(a.music_db)]
    if sfx:
        cmd += ["--sfx", sfx]
    if a.music:
        cmd += ["--music", a.music]
    step("audio pass 2: voice polish + effects + music, one master", cmd)

    step("mux picture + master (one AAC encode, BT.709 tags)", [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", raw, "-i", mix,
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-t", "%.6f" % duration, "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-color_range", "tv", "-movflags", "+write_colr+faststart", a.out])

    vcmd = [runtime.get_project_venv_python(), os.path.join(HERE, "verify-render.py"), "--render", a.out,
            "--res", "%dx%d" % (w, h), "--out", stem + "-VERIFY.md", "--fade-out", str(a.fade_out)]
    if os.path.isfile(index):
        vcmd += ["--index", index]
    r = subprocess.run(vcmd)
    print("deliverable: %s\nverify: %s-VERIFY.md (%s)\naudio report: %s" % (a.out, stem, "PASS" if r.returncode == 0 else "FAIL: do not deliver", report))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
