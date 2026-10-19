#!/usr/bin/env python3
"""voice-clean.py: dereverb (WPE, multi-mic) + neural denoise (DeepFilterNet) ahead of the audio-chain.

  voice-clean.py SRC_MEDIA --video VIDEO_FOR_PICTURE --out OUT.mp4 [--taps 18] [--delay 3] [--atten 32]

1. decode the source audio as 48 kHz float, keeping both iPhone mics (WPE uses the spatial diversity)
2. WPE dereverberation (nara_wpe): predicts and subtracts the late reverb tail per frequency band
2b. statistical late-reverb suppression (tools/late-reverb.py, RT60 0.5 s, -10 dB floor): ~7 dB less tail into pauses
3. DeepFilterNet3 (deep-filter binary, installed by install.sh into ~/.config/video-skills/bin): broadband/white-noise suppression with an attenuation limit so
   the voice keeps its natural texture (no watery artifacts)
4. 80 Hz high-pass and gain staging to -3 dBFS peak, muxed back onto the picture (stream copy)
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from nara_wpe.utils import istft, stft
from nara_wpe.wpe import wpe

def find_deep_filter() -> Path:
    """$VIDEO_DEEPFILTER, then the install.sh location, then next to this script."""
    import os
    for c in (os.environ.get("VIDEO_DEEPFILTER"), os.path.expanduser("~/.config/video-skills/bin/deep-filter"),
              os.path.expanduser("~/.config/video-skills/bin/deep-filter.exe"),
              str(Path(__file__).resolve().parent / "deep-filter")):
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return Path(c)
    raise SystemExit("deep-filter not found: run install.sh (it downloads DeepFilterNet into ~/.config/video-skills/bin) "
                     "or set VIDEO_DEEPFILTER")


DF = None


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--video", required=True, help="file whose picture is kept (stream copy)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--taps", type=int, default=18)
    ap.add_argument("--delay", type=int, default=3)
    ap.add_argument("--size", type=int, default=2048)
    ap.add_argument("--shift", type=int, default=512)
    ap.add_argument("--atten", type=float, default=32.0, help="DeepFilterNet attenuation limit dB")
    ap.add_argument("--rt60", type=float, default=0.5, help="late-reverb model RT60 (s)")
    ap.add_argument("--floor-db", type=float, default=-10.0, help="late-reverb gain floor (dB)")
    ap.add_argument("--keep", help="directory to keep the intermediate WAVs in")
    ap.add_argument("--reuse", action="store_true", help="reuse derev.wav in --keep (skip WPE)")
    a = ap.parse_args()

    tmp = Path(a.keep or tempfile.mkdtemp(prefix="voice-clean-"))
    tmp.mkdir(parents=True, exist_ok=True)
    raw = tmp / "stereo.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", a.src, "-map", "0:a:0", "-ac", "2", "-ar", "48000",
         "-c:a", "pcm_f32le", str(raw)])

    derev = tmp / "derev.wav"
    if derev.exists() and a.reuse:
        print("reusing", derev)
    else:
        wpe_stage(raw, derev, a)
    lr = tmp / "late.wav"
    run([sys.executable, str(Path(__file__).resolve().parent / "late-reverb.py"), str(derev), str(lr),
         "--rt60", str(a.rt60), "--floor-db", str(a.floor_db)])
    dfo = tmp / "df"
    if dfo.exists():
        shutil.rmtree(dfo)
    run([str(find_deep_filter()), "-D", "-a", str(a.atten), "-o", str(dfo), str(lr)])
    den = dfo / "late.wav"
    finish(a, den)


def wpe_stage(raw: Path, derev: Path, a) -> None:
    y, sr = sf.read(raw, dtype="float64", always_2d=True)       # (samples, ch)
    y = y.T                                                    # (ch, samples)
    Y = stft(y, size=a.size, shift=a.shift).transpose(2, 0, 1)  # (F, D, T)
    Z = wpe(Y, taps=a.taps, delay=a.delay, iterations=3, statistics_mode="full").transpose(1, 2, 0)
    z = istft(Z, size=a.size, shift=a.shift)[:, : y.shape[1]]
    mono = z.mean(axis=0)
    mono /= max(1e-9, np.abs(mono).max()) / 0.7                 # headroom for the DNN
    sf.write(derev, mono.astype(np.float32), sr, subtype="FLOAT")


def finish(a, den: Path) -> None:
    # normalise the peak to -3 dBFS so later stages see consistent levels
    peak = float(np.abs(sf.read(den, dtype="float64")[0]).max())
    g = 20 * np.log10(10 ** (-3 / 20) / max(peak, 1e-9))
    run(["ffmpeg", "-y", "-v", "error", "-i", a.video, "-i", str(den), "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-af", f"highpass=f=80:poles=2,volume={g:.2f}dB", "-c:a", "aac", "-b:a", "320k",
         "-ar", "48000", "-ac", "1", "-movflags", "+faststart", a.out])
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
