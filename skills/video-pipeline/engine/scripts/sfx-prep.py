#!/usr/bin/env python3
"""sfx-prep.py: make a sound effect land on its frame and sit at a known level.

1. Trim the silence before the transient, so the audible peak (not the file start) lands on the cue.
2. Peak-normalise to -3 dBFS, so data-volume in the composition is the only mix control (library files differ up to
   10x in level; at one shared volume some vanish).
3. Optional fade-out and length cap, so a tail never runs past its data-duration.

Usage: python3 sfx-prep.py IN OUT [--peak -3] [--max 1.5] [--fade 0.05] [--threshold -40]
Prints the new length and peak, and the data-duration to use.
"""
import argparse, re, subprocess, sys


def peak_db(path):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"max_volume:\s+(-?[\d.]+) dB", p.stderr)
    return float(m.group(1)) if m else None


def duration(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--peak", type=float, default=-3.0)
    ap.add_argument("--max", type=float, default=0.0, help="cap the length in seconds (0 = keep)")
    ap.add_argument("--fade", type=float, default=0.05)
    ap.add_argument("--threshold", type=float, default=None,
                    help="dB that counts as the start of the sound (default: 30 dB under the file's own peak; a fixed "
                         "-40 dB trimmed quiet library files to nothing)")
    a = ap.parse_args()
    tmp = a.out + ".trim.wav"
    src_peak = peak_db(a.inp)
    if src_peak is None or src_peak < -90:
        sys.exit("no audible sound in %s" % a.inp)
    thr = a.threshold if a.threshold is not None else max(src_peak - 30.0, -70.0)
    chain = "silenceremove=start_periods=1:start_threshold=%gdB:start_silence=0.002" % thr
    if a.max > 0:
        chain += ",atrim=0:%g" % a.max
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.inp, "-af", chain, "-ar", "48000", tmp], check=True)
    d = duration(tmp)
    pk = peak_db(tmp)
    if pk is None or d <= 0:
        import os; os.path.exists(tmp) and os.remove(tmp)
        sys.exit("trimming at %.0f dB left nothing of %s; pass a lower --threshold" % (thr, a.inp))
    gain = a.peak - pk
    fade = ",afade=t=out:st=%.3f:d=%.3f" % (max(0.0, d - a.fade), a.fade) if a.fade > 0 and d > a.fade else ""
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "volume=%.2fdB%s" % (gain, fade), a.out], check=True)
    import os; os.remove(tmp)
    print("%s: %.3f s, peak %.1f -> %.1f dBFS; use data-duration=\"%.3f\"" % (a.out, duration(a.out), pk, peak_db(a.out), duration(a.out)))


if __name__ == "__main__":
    main()
