#!/usr/bin/env python3
"""voice-clean.py: audio pass 1 of 2. Restore the voice once, losslessly, before anything else reads it.

  source WAV -> WPE dereverb (linear prediction, no spectral gating) -> DeepFilterNet3 (neural denoise, delay
  compensated) -> 70 Hz high-pass -> alignment check against the source -> voice-clean.wav (48 kHz, 24-bit, mono)

Pass 2 (audio-chain.py master) only polishes and levels this file; it never denoises or dereverbs again. Stacking
dereverb and denoise passes is what made voices sound robotic, so this file is the only place they happen.

The DeepFilterNet strength adapts to the measured noise: a quiet room gets a light touch (natural tone kept), a
noisy one gets the full model plus its post-filter. The output is sample-aligned with the source picture: any lag
found by cross-correlation is removed, and the length is matched to the sample.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

RATE = 48000


# ---------------------------------------------------------------- tools
def find_deep_filter() -> Path | None:
    for c in (os.environ.get("VIDEO_DEEPFILTER"),
              os.path.expanduser("~/.config/video-skills/bin/deep-filter"),
              os.path.expanduser("~/.config/video-skills/bin/deep-filter.exe"),
              os.path.expanduser("~/.local/bin/deep-filter"),
              shutil.which("deep-filter")):
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return Path(c)
    return None


def df_flags(binary: Path) -> set[str]:
    try:
        text = subprocess.run([str(binary), "--help"], capture_output=True, text=True, timeout=30)
        blob = (text.stdout or "") + (text.stderr or "")
    except Exception:  # noqa: BLE001 - a missing help text only disables optional flags
        blob = ""
    return {flag for flag in ("--compensate-delay", "--atten-lim", "--pf", "--output-dir", "--out-dir") if flag in blob}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------- measuring
def frame_db(x: np.ndarray, rate: int = RATE) -> np.ndarray:
    n = rate // 100
    frames = len(x) // n
    if frames == 0:
        return np.array([-120.0])
    y = x[: frames * n].reshape(frames, n)
    return 20 * np.log10(np.maximum(np.sqrt((y ** 2).mean(axis=1)), 1e-7))


def levels(x: np.ndarray) -> dict:
    d = frame_db(x)
    floor, speech = float(np.percentile(d, 10)), float(np.percentile(d, 95))
    return {"noise_floor_db": round(floor, 1), "speech_db": round(speech, 1), "snr_db": round(speech - floor, 1)}


def choose_strength(snr_db: float) -> dict:
    """DeepFilterNet attenuation limit (dB) and post-filter from the measured SNR: effective on noise, gentle on voice."""
    if snr_db >= 42:
        return {"atten_db": 14, "post_filter": False, "label": "light (quiet room)"}
    if snr_db >= 32:
        return {"atten_db": 20, "post_filter": False, "label": "medium"}
    if snr_db >= 22:
        return {"atten_db": 28, "post_filter": True, "label": "strong"}
    return {"atten_db": 36, "post_filter": True, "label": "maximum (very noisy)"}


def lag_samples(ref: np.ndarray, test: np.ndarray, rate: int = RATE, max_lag_s: float = 0.25) -> int:
    """Lag of `test` relative to `ref` (positive = test is late), from the loudest 20 s of speech."""
    n = len(ref)
    if n < rate:
        return 0
    win = min(n, 20 * rate)
    env = np.convolve(np.abs(ref), np.ones(rate) / rate, mode="valid")
    start = int(np.argmax(env)) - win // 2 if len(env) else 0
    start = max(0, min(n - win, start))
    a = ref[start:start + win] - ref[start:start + win].mean()
    b = test[start:start + win] - test[start:start + win].mean()
    size = 1 << int(np.ceil(np.log2(2 * win)))
    corr = np.fft.irfft(np.fft.rfft(b, size) * np.conj(np.fft.rfft(a, size)), size)
    m = int(max_lag_s * rate)
    corr = np.concatenate([corr[-m:], corr[: m + 1]])
    return int(np.argmax(corr)) - m


def shift(x: np.ndarray, lag: int) -> np.ndarray:
    if lag > 0:        # late: drop the first samples
        return np.concatenate([x[lag:], np.zeros(lag)])
    if lag < 0:        # early: pad the start
        return np.concatenate([np.zeros(-lag), x[:lag]])
    return x


# ---------------------------------------------------------------- stages
def wpe_stage(y: np.ndarray, strength: str, chunk_s: float = 90.0, overlap_s: float = 1.0) -> np.ndarray:
    """Weighted prediction error dereverb. Removes late reflections by linear prediction, so it does not add the
    swirly 'musical noise' of spectral subtraction. y: (channels, samples) -> (channels, samples).

    10.7 ms hop, 32 ms prediction delay (direct sound and early reflections are kept, so the voice keeps its body),
    tail model of 64-170 ms by strength. Long takes are processed in overlapping chunks to bound memory."""
    from nara_wpe.utils import istft, stft
    from nara_wpe.wpe import wpe
    taps = {"light": 6, "normal": 10, "strong": 16}[strength]
    size, hop = 2048, 512

    def one(seg: np.ndarray) -> np.ndarray:
        Y = stft(seg, size=size, shift=hop).transpose(2, 0, 1)      # (F, D, T)
        Z = wpe(Y, taps=taps, delay=3, iterations=3, statistics_mode="full").transpose(1, 2, 0)
        return istft(Z, size=size, shift=hop)[:, : seg.shape[1]]

    n = y.shape[1]
    chunk, ov = int(chunk_s * RATE), int(overlap_s * RATE)
    if n <= chunk + ov:
        return one(y)
    out = np.zeros_like(y)
    weight = np.zeros(n)
    start = 0
    while start < n:
        end = min(n, start + chunk + ov)
        seg = one(y[:, start:end])
        w = np.ones(end - start)
        if start > 0:
            w[:ov] = np.linspace(0.0, 1.0, ov)
        if end < n:
            w[-ov:] = np.minimum(w[-ov:], np.linspace(1.0, 0.0, ov))
        out[:, start:end] += seg * w
        weight[start:end] += w
        if end >= n:
            break
        start = end - ov
    return out / np.maximum(weight, 1e-9)


def deep_filter(binary: Path, flags: set[str], wav_in: Path, out_dir: Path, strength: dict) -> Path:
    cmd = [str(binary)]
    if "--compensate-delay" in flags:
        cmd.append("-D")
    if "--atten-lim" in flags:
        cmd += ["-a", str(strength["atten_db"])]
    if strength["post_filter"] and "--pf" in flags:
        cmd.append("--pf")
    cmd += ["-o", str(out_dir), str(wav_in)]
    run(cmd)
    out = out_dir / wav_in.name
    if not out.is_file():
        raise RuntimeError("DeepFilterNet wrote no output for %s" % wav_in)
    return out


def file_sig(path: str) -> str:
    st = os.stat(path)
    return hashlib.sha256(("%s|%d|%d" % (os.path.abspath(path), st.st_size, st.st_mtime_ns)).encode()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("src", help="source audio (WAV aligned to the first video frame, or any media file)")
    ap.add_argument("--out", required=True, help="voice-clean.wav to write (48 kHz, 24-bit, mono)")
    ap.add_argument("--report", help="JSON report (default: <out>.json)")
    ap.add_argument("--dereverb", choices=["off", "light", "normal", "strong"], default="normal",
                    help="WPE strength (default normal)")
    ap.add_argument("--denoise", choices=["auto", "off", "light", "medium", "strong", "maximum"], default="auto",
                    help="DeepFilterNet strength; auto picks it from the measured noise (default)")
    ap.add_argument("--work", help="folder for intermediates (default: a temp folder)")
    ap.add_argument("--force", action="store_true", help="re-clean even if a matching output exists")
    a = ap.parse_args()

    report_path = Path(a.report or (str(Path(a.out).with_suffix("")) + ".json"))
    sig = {"source": file_sig(a.src), "dereverb": a.dereverb, "denoise": a.denoise, "version": 2}
    if not a.force and Path(a.out).is_file() and report_path.is_file():
        try:
            old = json.loads(report_path.read_text(encoding="utf-8"))
            if old.get("signature") == sig:
                print("reusing cleaned voice %s (same source and settings)" % a.out)
                return
        except (OSError, ValueError):
            pass

    work = Path(a.work or tempfile.mkdtemp(prefix="voice-clean-"))
    work.mkdir(parents=True, exist_ok=True)
    raw = work / "source-48k.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", a.src, "-map", "0:a:0", "-ar", str(RATE), "-c:a", "pcm_f32le", str(raw)])
    x, rate = sf.read(raw, dtype="float64", always_2d=True)          # (samples, channels)
    ref = x.mean(axis=1)
    before = levels(ref)

    y = x.T
    if a.dereverb != "off":
        y = wpe_stage(y, a.dereverb)
    mono = y.mean(axis=0)
    peak = float(np.abs(mono).max()) or 1.0
    mono = mono * (0.7 / peak)                                     # headroom for the network
    stage = work / "voice-dereverb.wav"
    sf.write(stage, mono.astype(np.float32), RATE, subtype="PCM_16")  # the format deep-filter is known to read

    strength = choose_strength(before["snr_db"])
    if a.denoise != "auto":
        strength = {"off": None, "light": {"atten_db": 14, "post_filter": False, "label": "light"},
                    "medium": {"atten_db": 20, "post_filter": False, "label": "medium"},
                    "strong": {"atten_db": 28, "post_filter": True, "label": "strong"},
                    "maximum": {"atten_db": 36, "post_filter": True, "label": "maximum"}}[a.denoise]
    df_used, flags = None, set()
    if strength:
        binary = find_deep_filter()
        if binary is None:
            raise SystemExit("DeepFilterNet (deep-filter) is not installed. Run `video-skills setup`, or pass "
                             "--denoise off to continue without denoising.")
        flags = df_flags(binary)
        df_out = deep_filter(binary, flags, stage, work / "df", strength)
        cleaned, _ = sf.read(df_out, dtype="float64", always_2d=True)
        cleaned = cleaned.mean(axis=1)
        df_used = {"binary": str(binary), "flags": sorted(flags), **strength}
    else:
        cleaned = mono

    # alignment: same length, no lag against the source
    cleaned = cleaned[: len(ref)] if len(cleaned) >= len(ref) else np.concatenate([cleaned, np.zeros(len(ref) - len(cleaned))])
    lag = lag_samples(ref, cleaned)
    if abs(lag) > int(0.0005 * RATE):
        cleaned = shift(cleaned, lag)

    # 70 Hz high-pass (rumble, handling noise) in float, then -3 dBFS peak
    hp = work / "voice-hp.wav"
    pre_hp = work / "voice-aligned.wav"
    sf.write(pre_hp, cleaned.astype(np.float32), RATE, subtype="FLOAT")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(pre_hp), "-af", "highpass=f=70:poles=2", "-c:a", "pcm_f32le", str(hp)])
    final, _ = sf.read(hp, dtype="float64")
    final = final[: len(ref)] if len(final) >= len(ref) else np.concatenate([final, np.zeros(len(ref) - len(final))])
    final *= (10 ** (-3 / 20)) / max(float(np.abs(final).max()), 1e-9)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sf.write(a.out, final.astype(np.float32), RATE, subtype="PCM_24")

    after = levels(final)
    report = {"pass": 1, "signature": sig, "source": os.path.abspath(a.src), "output": os.path.abspath(a.out),
              "samples": len(final), "rate": RATE, "dereverb": a.dereverb, "denoise": df_used or "off",
              "lag_corrected_ms": round(1000.0 * lag / RATE, 2) if abs(lag) > int(0.0005 * RATE) else 0.0,
              "before": before, "after": after}
    report_path.write_text(json.dumps(report, indent=1), encoding="utf-8")
    if not a.work:
        shutil.rmtree(work, ignore_errors=True)
    print("pass 1: dereverb=%s, denoise=%s, SNR %.1f -> %.1f dB, lag %+.2f ms -> %s"
          % (a.dereverb, (df_used or {}).get("label", "off"), before["snr_db"], after["snr_db"],
             report["lag_corrected_ms"], a.out))


if __name__ == "__main__":
    main()
