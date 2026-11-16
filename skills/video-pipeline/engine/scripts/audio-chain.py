#!/usr/bin/env python3
"""audio-chain.py: audio pass 2 of 2. Polish the cleaned voice, mix sound effects and music, master once.

  voice.wav (already dereverbed + denoised by pass 1) -> high-pass, gentle EQ, de-ess, gentle compression
  + sound effects (the HyperFrames render's own audio, untouched) + music (ducked under the voice)
  -> loudness to the delivery target -> true-peak limiter -> fade out over the tail -> mix.wav (48 kHz, 24-bit)

Nothing here denoises, gates or dereverbs: pass 1 did that once. Running those again is what made voices robotic.
Modes: `measure MEDIA` prints loudness and noise numbers; `master` writes the final mix.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime import ToolError, ensure_project_venv, run  # noqa: E402
ensure_project_venv()

import numpy as np  # noqa: E402

PRESETS = {
    # integrated LUFS, true-peak ceiling dBTP
    "youtube":   {"lufs": -14.0, "tp": -1.0},
    "shorts":    {"lufs": -14.0, "tp": -1.0},
    "longform":  {"lufs": -16.0, "tp": -1.5},   # podcast-style long talks
    "broadcast": {"lufs": -23.0, "tp": -1.0},   # EBU R128
}
# Voice polish. Broad, small moves only: cut low-mid mud, a little presence for clarity, a touch of air.
TONES = {
    "neutral": ["equalizer=f=250:t=q:w=1.0:g=-2", "equalizer=f=3500:t=q:w=0.9:g=1.5", "highshelf=f=10000:g=1"],
    "clear":   ["equalizer=f=250:t=q:w=1.0:g=-2.5", "equalizer=f=3500:t=q:w=0.9:g=2.5", "highshelf=f=10000:g=2"],
    "warm":    ["lowshelf=f=150:g=1.5", "equalizer=f=350:t=q:w=1.2:g=-1", "equalizer=f=3000:t=q:w=1.0:g=1",
                "highshelf=f=9000:g=-0.5"],
}
HIGHPASS = "highpass=f=80:poles=2"
DEESSER = "deesser=i=0.3:m=0.5:f=0.5"
# Smooth levelling: low ratio, soft knee, slow enough release that sentence ends do not pump.
COMPRESSOR = "acompressor=threshold=-22dB:ratio=2.5:attack=15:release=160:knee=6:makeup=1"


# ---------------------------------------------------------------- measuring
def has_stream(media: str, kind: str) -> bool:
    p = run(["ffprobe", "-v", "error", "-select_streams", f"{kind}:0", "-show_entries", "stream=index",
             "-of", "csv=p=0", str(media)], check=False)
    return bool(p.stdout.strip())


def loudness(media: str) -> dict:
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(media), "-vn", "-af", "ebur128=peak=true",
             "-f", "null", "-"])
    s = p.stderr[p.stderr.rfind("Summary:"):]
    grab = lambda pat: (float(m.group(1)) if (m := re.search(pat, s)) else None)
    return {"integrated_lufs": grab(r"\bI:\s+(-?[\d.]+) LUFS"), "range_lu": grab(r"LRA:\s+(-?[\d.]+) LU"),
            "true_peak_dbtp": grab(r"Peak:\s+(-?[\d.]+) dBFS")}


def decode_pcm(media: str) -> np.ndarray:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(media), "-vn", "-ac", "1",
                        "-ar", "16000", "-f", "s16le", "-"], capture_output=True)
    if p.returncode != 0:
        raise ToolError(f"ffmpeg could not decode {media}: {p.stderr.decode(errors='replace')[-400:]}")
    return np.frombuffer(p.stdout, dtype=np.int16)


def frame_db(pcm: np.ndarray, rate: int = 16000) -> np.ndarray:
    n = rate // 20
    frames = len(pcm) // n
    if frames == 0:
        return np.array([-120.0])
    x = pcm[: frames * n].astype(np.float64).reshape(frames, n) / 32768.0
    return 20 * np.log10(np.maximum(np.sqrt((x ** 2).mean(axis=1)), 1e-6))


def measure(media: str) -> dict:
    d = frame_db(decode_pcm(media))
    floor, speech = float(np.percentile(d, 10)), float(np.percentile(d, 90))
    return {**loudness(media), "noise_floor_dbfs": round(floor, 1), "speech_dbfs": round(speech, 1),
            "snr_db": round(speech - floor, 1)}


def gain_to(target: float, current: float) -> float:
    return round(target - current, 2)


# ---------------------------------------------------------------- mastering
def ffmpeg_audio(inputs: list[list[str]], graph: str, out: str) -> None:
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for spec in inputs:
        cmd += spec
    cmd += ["-filter_complex", graph, "-map", "[a]", "-ar", "48000", "-c:a", "pcm_s24le", str(out)]
    run(cmd)


def master(args) -> dict:
    p = PRESETS[args.preset]
    voice = args.voice
    duration = float(args.duration) if args.duration else float(
        run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", voice]).stdout.strip())
    before = measure(voice)
    tmp = Path(tempfile.mkdtemp(prefix="audio-master-", dir=args.scratch_dir or None))
    try:
        voice_chain = [HIGHPASS, *TONES[args.tone], DEESSER, COMPRESSOR]
        inputs = [["-i", str(voice)]]
        split = ",asplit=2[v][sc]" if args.music else "[v]"
        graph = ["[0:a]aresample=48000,aformat=channel_layouts=mono,%s,aformat=channel_layouts=stereo%s"
                 % (",".join(voice_chain), split)]
        mix = ["[v]"]
        if args.sfx and Path(args.sfx).is_file():
            inputs.append(["-i", str(args.sfx)])
            graph.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo[fx]" % (len(inputs) - 1))
            mix.append("[fx]")
        if args.music:
            inputs.append(["-stream_loop", "-1", "-i", str(args.music)])
            k = len(inputs) - 1
            thr = 10 ** (-args.duck_db / 20)
            graph.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo,volume=%sdB,afade=t=in:d=1.5[bed]"
                         % (k, args.music_db))
            graph.append("[bed][sc]sidechaincompress=threshold=%.4f:ratio=8:attack=20:release=400[duck]" % thr)
            mix.append("[duck]")
        graph.append("%samix=inputs=%d:duration=first:normalize=0,apad,atrim=end=%.6f[a]"
                     % ("".join(mix), len(mix), duration))
        stage = tmp / "stage.wav"
        ffmpeg_audio(inputs, ";".join(graph), str(stage))

        # loudness: linear gain to the target, then a true-peak limiter under the ceiling; tighten once if over
        lufs = loudness(str(stage))["integrated_lufs"]
        silent = lufs is None or lufs < -60.0           # no speech (a silent montage): never pump up the noise floor
        if silent:
            lufs = p["lufs"]
        ceiling = p["tp"] - 0.5
        fade = max(0.0, min(float(args.fade_out or 0.0), duration))
        fade_f = ",afade=t=out:st=%.6f:d=%.6f" % (duration - fade, fade) if fade > 0 else ""
        final = tmp / "final.wav"
        got, tail = {}, []
        for _ in range(3):
            gain = gain_to(p["lufs"], lufs)
            tail = [f"volume={gain}dB", f"alimiter=limit={10 ** (ceiling / 20):.4f}:attack=5:release=60:level=disabled"]
            ffmpeg_audio([["-i", str(stage)]], "[0:a]%s%s[a]" % (",".join(tail), fade_f), str(final))
            got = loudness(str(final))
            if got["true_peak_dbtp"] is None or got["true_peak_dbtp"] <= p["tp"]:
                break
            ceiling -= 0.5
        if not silent and got.get("integrated_lufs") is not None and p["lufs"] - got["integrated_lufs"] > 0.5 and not fade:
            lufs -= (p["lufs"] - got["integrated_lufs"])
            gain = gain_to(p["lufs"], lufs)
            tail = [f"volume={gain}dB", f"alimiter=limit={10 ** (ceiling / 20):.4f}:attack=5:release=60:level=disabled"]
            ffmpeg_audio([["-i", str(stage)]], "[0:a]%s[a]" % ",".join(tail), str(final))
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(final, args.out)
        after = measure(args.out)
        ok = silent or (after["integrated_lufs"] is not None and abs(after["integrated_lufs"] - p["lufs"]) <= 1.0
                        and after["true_peak_dbtp"] is not None and after["true_peak_dbtp"] <= p["tp"] + 0.1)
        return {"mode": "master", "pass": 2, "preset": args.preset, "target": p, "tone": args.tone,
                "voice_chain": voice_chain, "sfx": args.sfx or None, "music": args.music or None,
                "mastering": tail + ([fade_f.lstrip(",")] if fade_f else []), "duration": round(duration, 3),
                "before_voice": before, "after": after, "silent": silent, "ok": ok}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["measure", "master"])
    ap.add_argument("media", nargs="?", help="media to measure (measure mode)")
    ap.add_argument("--voice", help="cleaned flat-cut voice WAV (master)")
    ap.add_argument("--sfx", help="sound-effects track from the HyperFrames render (master, optional)")
    ap.add_argument("--music", help="music bed, ducked under the voice (master, optional)")
    ap.add_argument("--out", help="mix WAV to write (master)")
    ap.add_argument("--duration", type=float, help="exact output length in seconds (default: the voice length)")
    ap.add_argument("--fade-out", type=float, default=0.0, help="fade the whole mix to silence over the last N s")
    ap.add_argument("--preset", choices=sorted(PRESETS), default="shorts")
    ap.add_argument("--tone", choices=sorted(TONES), default="neutral")
    ap.add_argument("--music-db", type=float, default=-20.0, help="music bed level before ducking")
    ap.add_argument("--duck-db", type=float, default=30.0, help="sidechain threshold depth (higher = ducks sooner)")
    ap.add_argument("--report", help="write the numbers as JSON here")
    ap.add_argument("--scratch-dir", help="parent folder for disposable intermediates")
    a = ap.parse_args()
    if a.mode == "measure":
        if not a.media:
            ap.error("measure needs MEDIA")
        rep = measure(a.media)
        print(json.dumps(rep, indent=1))
    else:
        if not (a.voice and a.out):
            ap.error("master needs --voice and --out")
        rep = master(a)
        b, f = rep["before_voice"], rep["after"]
        print("pass 2 master (%s, tone=%s): voice %s LUFS -> mix %s LUFS, true peak %s dBTP%s%s -> %s"
              % (a.preset, a.tone, b.get("integrated_lufs"), f.get("integrated_lufs"), f.get("true_peak_dbtp"),
                 ", sfx" if rep["sfx"] else "", ", music" if rep["music"] else "", a.out))
        print("PASS" if rep["ok"] else "FAIL: loudness or true peak off target (see numbers above)")
    if a.report:
        Path(a.report).write_text(json.dumps(rep, indent=1))
    if rep.get("ok") is False:
        sys.exit(1)


if __name__ == "__main__":
    main()
