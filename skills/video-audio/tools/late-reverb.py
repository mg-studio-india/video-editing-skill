#!/usr/bin/env python3
"""late-reverb.py IN.wav OUT.wav [--rt60 0.5] [--td 0.05] [--floor-db -10]
Single-channel late-reverberation suppression (Lebart et al. 2001 / Habets 2007 statistical model):
late-reverb PSD = exp(-2*delta*Td) * PSD(t - Td), delta = 3 ln10 / RT60; spectral gain = max(1 - late/PSD, floor),
smoothed over time so it never 'warbles'. Early reflections (< Td) are left alone, which keeps the voice natural."""
import argparse, numpy as np, soundfile as sf
from scipy.signal import stft, istft
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--rt60", type=float, default=0.5); ap.add_argument("--td", type=float, default=0.05)
ap.add_argument("--floor-db", type=float, default=-10.0); ap.add_argument("--over", type=float, default=1.0)
a = ap.parse_args()
x, sr = sf.read(a.inp, dtype="float64")
if x.ndim > 1: x = x.mean(1)
n, hop = 1024, 256
f, t, X = stft(x, sr, nperseg=n, noverlap=n - hop)
P = np.abs(X) ** 2
# recursive PSD smoothing
Ps = np.empty_like(P); Ps[:, 0] = P[:, 0]
for k in range(1, P.shape[1]): Ps[:, k] = 0.6 * Ps[:, k - 1] + 0.4 * P[:, k]
delta = 3 * np.log(10) / a.rt60
D = max(1, int(round(a.td * sr / hop)))
late = np.zeros_like(Ps); late[:, D:] = np.exp(-2 * delta * a.td) * Ps[:, :-D]
G = np.maximum(1 - a.over * late / np.maximum(Ps, 1e-12), 10 ** (a.floor_db / 20))
for k in range(1, G.shape[1]): G[:, k] = 0.55 * G[:, k] + 0.45 * G[:, k - 1]   # temporal smoothing: no musical noise
_, y = istft(X * G, sr, nperseg=n, noverlap=n - hop)
y = y[: len(x)]
sf.write(a.out, (y / max(1e-9, np.abs(y).max()) * 0.7).astype(np.float32), sr, subtype="FLOAT")
print("wrote", a.out)
