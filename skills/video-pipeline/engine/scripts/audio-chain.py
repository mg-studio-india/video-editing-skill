#!/usr/bin/env python3
"""audio-chain.py: voice processing in the right order, with ffmpeg only, measured before and after.

Order (fixed, the reason is in the audio skill):
  gain staging -> high-pass -> noise reduction -> [expander] -> de-ess -> compression -> tonal EQ -> loudness -> limiter
  (the expander runs in master only: it keeps compression from lifting the pauses and the hiss back up)

Modes
  measure  MEDIA                                  print loudness, true peak, range, noise floor; change nothing
  clean    MEDIA --out OUT                        light early pass: gain staging, high-pass, adaptive noise reduction.
                                                  Run on the raw camera file before transcription and cutting.
  master   MEDIA --out OUT --preset youtube       full chain on the final mix, optional ducked music bed, loudness to
           [--music bed.wav --duck-db 18]         the preset target, a limiter under the true-peak ceiling, verified.

A video input keeps its picture untouched (stream copy); only the audio is replaced. --report writes the numbers as JSON.

Noise reduction is adaptive, because over-processing a clean file is what creates artifacts (watery highs, pumping):
  noise floor below -62 dBFS   -> none
  -62 to -50                   -> light   (afftdn nr 6)
  -50 to -40                   -> medium  (afftdn nr 10)
  above -40                    -> strong  (afftdn nr 14), plus arnndn when an RNNoise model is available
The floor is the 10th percentile of 50 ms RMS frames, and afftdn gets nf = floor + 12 dB
(it works per band), never closer than 15 dB to the speech level. An RNNoise model (.rnnn) is used from --rnn-model, or the first
file in ~/.config/video-skills/rnnoise/. arnndn runs with mix 0.85 so a little dry signal masks its artifacts.
--denoise off|light|medium|strong overrides the choice.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime import ToolError, ensure_project_venv, run  # noqa: E402
ensure_project_venv()

import numpy as np

PRESETS = {
    # integrated LUFS, true-peak ceiling dBTP
    "youtube":   {"lufs": -14.0, "tp": -1.0},
    "shorts":    {"lufs": -14.0, "tp": -1.0},
    "longform":  {"lufs": -16.0, "tp": -1.5},   # podcast-style long talks
    "broadcast": {"lufs": -23.0, "tp": -1.0},   # EBU R128
}
TONES = {
    # tonal EQ after compression: cut mud, add presence, a little air (or warmth)
    "neutral": "equalizer=f=250:t=q:w=1.2:g=-1.5,equalizer=f=3200:t=q:w=1.0:g=1.5",
    "clear":   "equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3200:t=q:w=1.0:g=2.5,highshelf=f=10000:g=2",
    "warm":    "lowshelf=f=150:g=1.5,equalizer=f=350:t=q:w=1.2:g=-1,equalizer=f=3000:t=q:w=1.0:g=1,highshelf=f=9000:g=-1",
}
# makeup is a LINEAR factor in ffmpeg (2 = +6 dB, which lifted the hiss with everything else); loudness is set later
COMPRESSOR = "acompressor=threshold=-20dB:ratio=3:attack=12:release=180:knee=4:makeup=1"
DEESSER = "deesser=i=0.35:m=0.5:f=0.5"
HIGHPASS = "highpass=f=80:poles=2"


def compressor(threshold_db: float = -20.0, ratio: float = 3.0, release_ms: float = 180.0) -> str:
    return f"acompressor=threshold={threshold_db}dB:ratio={ratio}:attack=12:release={release_ms}:knee=4:makeup=1"


def deesser(intensity: float = 0.35) -> str:
    return f"deesser=i={intensity}:m=0.5:f=0.5"


def highpass(hz: float = 80.0) -> str:
    return f"highpass=f={hz}:poles=2"
DENOISE_NR = {"light": 6, "medium": 10, "strong": 14}
PEAK_TARGET = -6.0   # gain staging: leave headroom before compression


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


def sample_peak(media: str) -> float:
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(media), "-vn", "-af", "volumedetect", "-f", "null", "-"])
    m = re.search(r"max_volume:\s+(-?[\d.]+) dB", p.stderr)
    return float(m.group(1)) if m else 0.0


def decode_pcm(media: str) -> np.ndarray:
    """16 kHz mono int16 samples."""
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


def floor_from_pcm(pcm: np.ndarray, rate: int = 16000) -> float:
    return round(float(np.percentile(frame_db(pcm, rate), 10)), 1)


def speech_from_pcm(pcm: np.ndarray, rate: int = 16000) -> float:
    return round(float(np.percentile(frame_db(pcm, rate), 90)), 1)


def snr_from_pcm(pcm: np.ndarray, rate: int = 16000) -> float:
    """Speech level (90th percentile frame) minus noise floor (10th): the number denoising should raise."""
    d = frame_db(pcm, rate)
    return round(float(np.percentile(d, 90) - np.percentile(d, 10)), 1)


def measure(media: str) -> dict:
    pcm = decode_pcm(media)
    return {**loudness(media), "sample_peak_dbfs": sample_peak(media), "noise_floor_dbfs": floor_from_pcm(pcm),
            "speech_dbfs": speech_from_pcm(pcm), "snr_db": snr_from_pcm(pcm)}


# ---------------------------------------------------------------- decisions (pure, tested)
def denoise_level(floor_db: float) -> str:
    if floor_db < -62:
        return "off"
    if floor_db < -50:
        return "light"
    if floor_db < -40:
        return "medium"
    return "strong"


NF_OFFSET = 12.0      # afftdn's nf sits this far above the broadband floor (it works per band)
NF_SPEECH_GAP = 15.0  # and never closer than this to the speech level, so quiet words are not treated as noise


def afftdn_floor(floor_db: float, speech_db: float) -> float:
    return round(min(-20.0, max(-80.0, min(floor_db + NF_OFFSET, speech_db - NF_SPEECH_GAP))), 1)


def denoise_filters(level: str, rnn_model: str | None, floor_db: float, speech_db: float) -> list[str]:
    """afftdn only works when told where the noise sits. Measured on test material: a fixed nf of -50 removed 1 dB of
    a -44 dB hiss; nf at floor+12 removed the full nr (6/10/14 dB) on white and pink noise, speech level unchanged."""
    if level in ("off", "none"):
        return []
    out = []
    if level in ("strong", "neural") and rnn_model:
        out.append(f"arnndn=m='{rnn_model}':mix=0.85")
    nf = afftdn_floor(floor_db, speech_db)
    nr = DENOISE_NR.get(level, 14)
    out.append(f"afftdn=nr={nr}:nf={nf}")
    return out


def find_deep_filter() -> str | None:
    for c in (
        os.environ.get("VIDEO_DEEPFILTER"),
        os.path.expanduser("~/.config/video-skills/bin/deep-filter"),
        os.path.expanduser("~/.config/video-skills/bin/deep-filter.exe"),
        os.path.expanduser("~/.local/bin/deep-filter"),
    ):
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def apply_deep_filter(src_media: str, tmp_dir: Path, atten_db: float = 32.0) -> str:
    df = find_deep_filter()
    if not df:
        raise ToolError("deep-filter binary not found in ~/.config/video-skills/bin/deep-filter or $VIDEO_DEEPFILTER")
    raw_wav = tmp_dir / "df_in.wav"
    out_dir = tmp_dir / "df_out"
    out_dir.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src_media), "-vn", "-ar", "48000",
         "-c:a", "pcm_s16le", str(raw_wav)])
    cmd = [df, "-D", "-a", str(atten_db), "-o", str(out_dir), str(raw_wav)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise ToolError(f"deep-filter failed: {res.stderr}")
    return str(out_dir / "df_in.wav")


def find_rnn_model(explicit: str | None) -> str | None:
    if explicit:
        return explicit if (os.path.isfile(explicit) and os.path.getsize(explicit) > 1024) else None
    for cand in ("sh.rnnn", "cb.rnnn", "mp.rnnn", "bd.rnnn"):
        p = os.path.expanduser(f"~/.config/video-skills/rnnoise/{cand}")
        if os.path.isfile(p) and os.path.getsize(p) > 1024:
            return p
    found = [f for f in sorted(glob.glob(os.path.expanduser("~/.config/video-skills/rnnoise/*.rnnn")))
             if os.path.getsize(f) > 1024]
    return found[0] if found else None


def expander(floor_db: float, speech_db: float) -> str:
    """Gentle downward expander so the pauses sit lower before compression narrows the range: 2:1, at most 10 dB.
    agate's detector reads lower than the 50 ms RMS floor, so the threshold sits 14 dB above it (at +8 it did
    nothing on test material; at +14 the pauses dropped ~5 dB), never closer than 12 dB to the speech level."""
    thr_db = min(floor_db + 14.0, speech_db - 12.0)
    return f"agate=threshold={10 ** (thr_db / 20):.5f}:ratio=2:range={10 ** (-10 / 20):.3f}:attack=5:release=150"


def gain_to(target: float, current: float) -> float:
    return round(target - current, 2)


# ---------------------------------------------------------------- rendering
def render(media: str, out: str, chain: list[str], music: str | None = None, duck_db: float = 18.0,
           music_db: float = -18.0) -> None:
    video = has_stream(media, "v") and Path(out).suffix.lower() in (".mp4", ".mov", ".mkv", ".m4v")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(media)]
    if music:
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        voice = ",".join(chain) if chain else "anull"
        thr = 10 ** (-duck_db / 20)
        fc = (f"[0:a]{voice},asplit=2[v][sc];[1:a]volume={music_db}dB,afade=t=in:d=1[bed];"
              f"[bed][sc]sidechaincompress=threshold={thr:.4f}:ratio=10:attack=15:release=350[duck];"
              f"[v][duck]amix=inputs=2:duration=first:normalize=0[a]")
        cmd += ["-filter_complex", fc, "-map", "[a]"]
    else:
        cmd += ["-map", "0:a:0", "-af", ",".join(chain) if chain else "anull"]
    if video:
        cmd += ["-map", "0:v:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                "-movflags", "+faststart"]
    else:
        cmd += ["-ar", "48000"]
        if Path(out).suffix.lower() == ".wav":
            cmd += ["-c:a", "pcm_s24le"]
    if music:
        cmd += ["-shortest"]
    cmd.append(str(out))
    run(cmd)


def clean(media: str, out: str, args) -> dict:
    # Caching check: Never re-clean if output already exists and is newer than source, unless --force
    if not getattr(args, "force", False) and os.path.isfile(out) and os.path.getsize(out) > 1024:
        if not os.path.exists(media) or os.path.getmtime(media) <= os.path.getmtime(out):
            print(f"✓ Reusing existing clean audio: {out} (use --force to re-clean)")
            m = measure(out)
            level = args.denoise if (args.denoise and args.denoise != "auto") else denoise_level(m["noise_floor_dbfs"])
            return {"mode": "clean", "denoise": level, "chain": ["cached"], "before": m, "after": m}

    before = measure(media)
    level = args.denoise if (args.denoise and args.denoise != "auto") else denoise_level(before["noise_floor_dbfs"])
    src = media
    tmp_clean = None
    if level == "neural" and find_deep_filter():
        tmp_clean = Path(tempfile.mkdtemp(prefix="audio-clean-df-"))
        src = apply_deep_filter(media, tmp_clean)
        active_level = "off"
    else:
        active_level = "strong" if level == "neural" else level
    g = gain_to(PEAK_TARGET, before["sample_peak_dbfs"])
    chain = [f"volume={g}dB", highpass(args.highpass),
             *denoise_filters(active_level, find_rnn_model(args.rnn_model), before["noise_floor_dbfs"] + g,
                              before["speech_dbfs"] + g)]
    render(src, out, chain)
    if tmp_clean and tmp_clean.exists():
        shutil.rmtree(tmp_clean, ignore_errors=True)
    return {"mode": "clean", "denoise": level, "chain": chain, "before": before, "after": measure(out)}


def master(media: str, out: str, args) -> dict:
    p = PRESETS[args.preset]
    before = measure(media)
    if args.denoise and args.denoise != "auto":
        level = args.denoise
    elif args.denoise == "auto" or before["noise_floor_dbfs"] >= -50.0:
        level = denoise_level(before["noise_floor_dbfs"])
    else:
        level = "off"
    tmp = Path(tempfile.mkdtemp(prefix="audio-chain-"))
    src = media
    if level == "neural" and find_deep_filter():
        src = apply_deep_filter(media, tmp)
        active_level = "off"
    else:
        active_level = "strong" if level == "neural" else level
    g = gain_to(PEAK_TARGET, before["sample_peak_dbfs"])
    pre = [f"volume={g}dB", highpass(args.highpass),
           *denoise_filters(active_level, find_rnn_model(args.rnn_model), before["noise_floor_dbfs"] + g,
                             before["speech_dbfs"] + g),
           expander(before["noise_floor_dbfs"] + g, before["speech_dbfs"] + g), deesser(args.deess),
           compressor(args.comp_threshold, args.comp_ratio, args.comp_release), TONES[args.tone]]
    stage = str(tmp / "stage.wav")
    render(src, stage, pre, music=args.music, duck_db=args.duck_db, music_db=args.music_db)
    # loudness: linear gain to target, then a limiter under the ceiling; verify the true peak, tighten once if over
    lufs = loudness(stage)["integrated_lufs"]
    ceiling = p["tp"] - 0.5
    for _ in range(3):
        gain = gain_to(p["lufs"], lufs)
        tail = [f"volume={gain}dB", f"alimiter=limit={10 ** (ceiling / 20):.4f}:attack=5:release=60:level=disabled"]
        final = str(tmp / "final.wav")
        render(stage, final, tail)
        got = loudness(final)
        if got["true_peak_dbtp"] is None or got["true_peak_dbtp"] <= p["tp"]:
            break
        ceiling -= 0.5
    # the limiter can shave a little loudness; one corrective nudge if we are more than 0.5 LU under
    if got["integrated_lufs"] is not None and p["lufs"] - got["integrated_lufs"] > 0.5:
        lufs -= (p["lufs"] - got["integrated_lufs"])
        gain = gain_to(p["lufs"], lufs)
        tail = [f"volume={gain}dB", f"alimiter=limit={10 ** (ceiling / 20):.4f}:attack=5:release=60:level=disabled"]
        render(stage, final, tail)
    # put it back on the picture (or write the audio file)
    if has_stream(media, "v") and Path(out).suffix.lower() in (".mp4", ".mov", ".mkv", ".m4v"):
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(media), "-i", final,
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
             "-shortest", "-movflags", "+faststart", str(out)])
    else:
        render(final, out, [])
    after = measure(out)
    ok = (after["integrated_lufs"] is not None and abs(after["integrated_lufs"] - p["lufs"]) <= 1.0
          and after["true_peak_dbtp"] is not None and after["true_peak_dbtp"] <= p["tp"] + 0.1)
    rep = {"mode": "master", "preset": args.preset, "target": p, "tone": args.tone, "denoise": level,
           "music": args.music, "chain": pre + tail, "before": before, "after": after, "pass": ok}
    if tmp and tmp.exists():
        shutil.rmtree(tmp, ignore_errors=True)
    return rep


def show(rep: dict) -> None:
    if rep.get("mode") is None:
        print(json.dumps(rep, indent=1)); return
    b, a = rep["before"], rep["after"]
    print(f"{rep['mode']}: denoise={rep['denoise']}" + (f"  preset={rep['preset']} target={rep['target']}" if rep['mode'] == 'master' else ""))
    for k in ("integrated_lufs", "true_peak_dbtp", "range_lu", "sample_peak_dbfs", "noise_floor_dbfs", "speech_dbfs", "snr_db"):
        print(f"  {k:18} {b.get(k)!s:>8} -> {a.get(k)!s:>8}")
    if "pass" in rep:
        print("PASS" if rep["pass"] else "FAIL: loudness or true peak off target (see numbers above)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["measure", "clean", "master"])
    ap.add_argument("media")
    ap.add_argument("--out")
    ap.add_argument("--preset", choices=sorted(PRESETS), default="youtube")
    ap.add_argument("--tone", choices=sorted(TONES), default="neutral")
    ap.add_argument("--denoise", choices=["auto", "off", "light", "medium", "strong", "neural"])
    ap.add_argument("--rnn-model", help="RNNoise .rnnn model for strong denoising")
    ap.add_argument("--music", help="music bed to duck under the voice (master only)")
    ap.add_argument("--duck-db", type=float, default=18.0, help="how far the bed drops under speech")
    ap.add_argument("--music-db", type=float, default=-18.0, help="bed level before ducking")
    ap.add_argument("--highpass", type=float, default=80.0, help="high-pass corner in Hz (100-120 for boomy rooms)")
    ap.add_argument("--deess", type=float, default=0.35, help="de-esser intensity 0-1")
    ap.add_argument("--comp-threshold", type=float, default=-20.0, help="compressor threshold dB")
    ap.add_argument("--comp-ratio", type=float, default=3.0, help="compressor ratio")
    ap.add_argument("--comp-release", type=float, default=180.0, help="compressor release ms (longer = less pumping)")
    ap.add_argument("--report", help="write the numbers as JSON here")
    ap.add_argument("--force", action="store_true", help="force re-processing even if output already exists")
    a = ap.parse_args()
    if a.mode != "measure" and not a.out:
        ap.error("--out is required for clean and master")
    rep = measure(a.media) if a.mode == "measure" else clean(a.media, a.out, a) if a.mode == "clean" \
        else master(a.media, a.out, a)
    show(rep)
    if a.report:
        Path(a.report).write_text(json.dumps(rep, indent=1))
    if rep.get("pass") is False:
        sys.exit(1)


if __name__ == "__main__":
    main()
