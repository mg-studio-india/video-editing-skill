#!/usr/bin/env python3
"""audio-analyze.py: Identify acoustic parameters dynamically from input audio/video.

Scans the input file to detect:
  1. Channel topology & asymmetric mic selection (c0 vs c1 vs stereo)
  2. Optimal room-tone noise profiling window (quietest inter-phrase pause)
  3. Speaker fundamental pitch (F0), highpass cutoff, and warmth frequency
  4. Room resonance modes / standing waves (narrow peaks in 100-800 Hz)
  5. Calibrated leveling compressor threshold based on speech RMS
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

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

import numpy as np


def analyze_channels(media: str) -> dict:
    p = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "stream=channels,channel_layout,sample_rate", "-select_streams", "a:0",
        "-of", "json", media
    ], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return {"channels": 1, "filter": "anull", "strategy": "mono"}
    
    info = json.loads(p.stdout)["streams"][0]
    channels = int(info.get("channels", 1))
    if channels <= 1:
        return {"channels": 1, "filter": "anull", "strategy": "mono"}
    
    # Decode 15s of stereo to compare c0 vs c1
    p = subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", media,
        "-vn", "-c:a", "pcm_s16le", "-f", "s16le", "-ar", "48000", "-ac", "2", "-t", "15", "-"
    ], capture_output=True)
    if p.returncode != 0 or len(p.stdout) < 48000 * 4:
        return {"channels": channels, "filter": "pan=mono|c0=0.5*c0+0.5*c1", "strategy": "downmix"}
    
    audio = np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    c0 = audio[0::2]
    c1 = audio[1::2]
    rms0 = 20 * np.log10(np.sqrt(np.mean(c0**2)) + 1e-12)
    rms1 = 20 * np.log10(np.sqrt(np.mean(c1**2)) + 1e-12)
    
    # Check speech band energy (300 Hz - 3500 Hz)
    n = min(len(c0), 48000 * 10)
    f0 = np.abs(np.fft.rfft(c0[:n]))
    f1 = np.abs(np.fft.rfft(c1[:n]))
    freqs = np.fft.rfftfreq(n, 1 / 48000)
    speech_band = (freqs >= 300) & (freqs <= 3500)
    sp0 = 10 * np.log10(np.mean(f0[speech_band]**2) + 1e-12)
    sp1 = 10 * np.log10(np.mean(f1[speech_band]**2) + 1e-12)
    
    diff = rms0 - rms1
    if diff > 1.2 and sp0 > sp1:
        strategy = "c0_dominant"
        af = "pan=mono|c0=c0"
    elif diff < -1.2 and sp1 > sp0:
        strategy = "c1_dominant"
        af = "pan=mono|c0=c1"
    else:
        strategy = "balanced_stereo"
        af = "pan=mono|c0=0.5*c0+0.5*c1"
        
    return {
        "channels": channels,
        "c0_rms_dbfs": round(float(rms0), 1),
        "c1_rms_dbfs": round(float(rms1), 1),
        "strategy": strategy,
        "filter": af
    }


def analyze_acoustics(media: str, channel_filter: str) -> dict:
    # Decode up to 30s of mono audio at 48kHz
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", media, "-vn"]
    if channel_filter != "anull":
        cmd += ["-af", channel_filter]
    cmd += ["-c:a", "pcm_s16le", "-f", "s16le", "-ar", "48000", "-t", "30", "-"]
    
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0 or len(p.stdout) < 48000 * 2:
        return {}
    
    audio = np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    sr = 48000
    
    # 1. Quietest Room Tone Window Discovery (0.4s sliding window, 0.1s hop)
    win_len = int(0.4 * sr)
    hop_len = int(0.1 * sr)
    min_rms = 1.0
    best_start = 0.0
    for i in range(0, len(audio) - win_len, hop_len):
        chunk = audio[i:i + win_len]
        rms = float(np.sqrt(np.mean(chunk**2)))
        # Exclude digital silence (< -80 dBFS) which indicates muted input
        if 1e-4 < rms < min_rms:
            min_rms = rms
            best_start = i / sr
            
    noise_floor_db = round(20 * np.log10(min_rms + 1e-12), 1)
    
    # 2. Voice Fundamental (F0) & Voiced Dynamics
    frame_sz = 2048
    hop_sz = 1024
    f0_list = []
    voiced_rms = []
    fft_accum = np.zeros(frame_sz // 2 + 1)
    count = 0
    
    for i in range(0, len(audio) - frame_sz, hop_sz):
        chunk = audio[i:i + frame_sz]
        rms = float(np.sqrt(np.mean(chunk**2)))
        if rms > 0.025:  # Voiced frame threshold
            voiced_rms.append(rms)
            # Autocorrelation for pitch F0
            corr = np.correlate(chunk, chunk, mode="full")[frame_sz - 1:]
            # Search lag for 80 Hz to 320 Hz (lag 600 down to 150)
            corr_range = corr[150:600]
            if len(corr_range) > 0 and np.max(corr_range) > 0.3 * corr[0]:
                peak_lag = 150 + int(np.argmax(corr_range))
                pitch = sr / peak_lag
                f0_list.append(pitch)
            # Accumulate spectrum for resonance detection
            fft_accum += np.abs(np.fft.rfft(chunk * np.hanning(frame_sz)))
            count += 1
            
    median_f0 = float(np.median(f0_list)) if f0_list else 125.0
    speech_rms_db = round(float(20 * np.log10(np.percentile(voiced_rms, 90) + 1e-12)), 1) if voiced_rms else -20.0
    
    # Recommended Highpass & Warmth
    highpass_hz = int(max(75, min(100, round(median_f0 - 25, -1))))
    warmth_hz = int(round(median_f0))
    
    # 3. Room Mode / Standing Resonance Detection
    notches = []
    notch_filters = []
    if count > 5:
        avg_fft = fft_accum / count
        freqs = np.fft.rfftfreq(frame_sz, 1 / sr)
        mask = (freqs >= 120) & (freqs <= 750)
        sub_freqs = freqs[mask]
        sub_fft = 20 * np.log10(avg_fft[mask] + 1e-6)
        
        # Moving average envelope
        kernel_sz = 11
        smoothed = np.convolve(sub_fft, np.ones(kernel_sz) / kernel_sz, mode="same")
        diff = sub_fft - smoothed
        
        for idx in range(1, len(diff) - 1):
            # Peak standing > 2.8 dB above smoothed envelope
            if diff[idx] > 2.8 and diff[idx] > diff[idx - 1] and diff[idx] > diff[idx + 1]:
                freq_val = int(round(float(sub_freqs[idx])))
                # Prevent notching voice pitch fundamental
                if abs(freq_val - warmth_hz) > 25:
                    gain_val = round(-min(4.0, max(2.0, float(diff[idx]))), 1)
                    notches.append({"freq": freq_val, "standing_db": round(float(diff[idx]), 1), "gain": gain_val})
                    notch_filters.append(f"equalizer=f={freq_val}:t=q:w=3.5:g={gain_val}")
                    
    # 4. Compressor Threshold Calibration (speech RMS minus 4 dB headroom)
    comp_thresh_db = round(speech_rms_db - 4.0, 1)
    
    return {
        "noise_window": {"start": round(best_start, 2), "duration": 0.4, "floor_dbfs": noise_floor_db},
        "voice_pitch": {"f0_hz": round(median_f0, 1), "warmth_hz": warmth_hz, "highpass_hz": highpass_hz},
        "speech_level_dbfs": speech_rms_db,
        "comp_threshold_db": comp_thresh_db,
        "room_resonances": notches,
        "notch_filters": notch_filters
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("media", help="Path to input audio/video file")
    ap.add_argument("--json", action="store_true", help="Output pure JSON")
    args = ap.parse_args()
    
    media_path = Path(args.media)
    if not media_path.exists():
        sys.exit(f"Error: File not found: {args.media}")
        
    ch_info = analyze_channels(str(media_path))
    ac_info = analyze_acoustics(str(media_path), ch_info["filter"])
    
    report = {
        "media": str(media_path),
        "channel_analysis": ch_info,
        "acoustic_profile": ac_info
    }
    
    if args.json:
        print(json.dumps(report, indent=2))
        return
        
    print(f"=== Acoustic Profile for: {media_path.name} ===")
    print(f"Channels: {ch_info['channels']} ({ch_info.get('strategy', 'mono')}) -> Filter: {ch_info['filter']}")
    
    nw = ac_info.get("noise_window", {})
    print(f"Room Tone Floor: {nw.get('floor_dbfs', 'N/A')} dBFS (sampled at {nw.get('start', 0.0)}s for {nw.get('duration', 0.4)}s)")
    
    vp = ac_info.get("voice_pitch", {})
    print(f"Voice Fundamental (F0): {vp.get('f0_hz', 'N/A')} Hz -> Recommended Highpass: {vp.get('highpass_hz', 85)} Hz, Warmth: {vp.get('warmth_hz', 130)} Hz")
    
    print(f"Speech Level: {ac_info.get('speech_level_dbfs', 'N/A')} dBFS -> Calibrated Comp Threshold: {ac_info.get('comp_threshold_db', -18.0)} dB")
    
    res = ac_info.get("room_resonances", [])
    if res:
        res_strs = [f"{r['freq']} Hz ({r['standing_db']} dB spike -> notch {r['gain']} dB)" for r in res]
        print("Detected Room Resonances: " + ", ".join(res_strs))
        print("Notch Filters: " + ",".join(ac_info.get("notch_filters", [])))
    else:
        print("Detected Room Resonances: None (Clean acoustic space)")


if __name__ == "__main__":
    main()
