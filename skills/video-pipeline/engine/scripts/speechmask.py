"""speechmask.py: where speech actually is, measured from the waveform (10 ms frames).

Shared by the transcript clean-up, the cut builder and the cut check. ASR word times are estimates; the energy of the
cleaned voice is ground truth for "is someone talking here". Every cut edge must sit in a frame this module calls quiet.
"""
from __future__ import annotations

import subprocess

import numpy as np

RATE = 16000
HOP = 160            # 10 ms frames


class SpeechMask:
    def __init__(self, db: np.ndarray, threshold_db: float, floor_db: float, speech_db: float):
        self.db = db
        self.threshold_db = threshold_db
        self.floor_db = floor_db
        self.speech_db = speech_db
        raw = db > threshold_db
        # close 1-2 frame dips inside words (plosives, glottal stops) so one word is one voiced region
        win = np.ones(5, dtype=np.int32)
        dilated = np.convolve(raw.astype(np.int32), win, mode="same") > 0
        closed = np.convolve(dilated.astype(np.int32), win, mode="same") == len(win)
        self.voiced = closed | raw
        self.frames = len(db)

    # ---------------------------------------------------------------- time <-> frame
    def f(self, t: float) -> int:
        return int(min(max(0, round(t * 100)), max(0, self.frames - 1)))

    @staticmethod
    def t(frame: int) -> float:
        return frame / 100.0

    # ---------------------------------------------------------------- queries
    def voiced_fraction(self, start: float, end: float) -> float:
        a, b = self.f(start), self.f(end)
        if b <= a:
            return float(self.voiced[a]) if self.frames else 0.0
        return float(self.voiced[a:b].mean())

    def quiet_regions(self, start: float, end: float, min_len: float = 0.03) -> list[tuple[float, float]]:
        """Quiet (unvoiced) regions inside [start, end], as (t0, t1) pairs."""
        a, b = self.f(start), self.f(end)
        out, run0 = [], None
        for i in range(a, b + 1):
            q = i < self.frames and not self.voiced[i]
            if q and run0 is None:
                run0 = i
            elif not q and run0 is not None:
                if (i - run0) / 100.0 >= min_len:
                    out.append((self.t(run0), self.t(i)))
                run0 = None
        if run0 is not None and (b + 1 - run0) / 100.0 >= min_len:
            out.append((self.t(run0), self.t(b + 1)))
        return out

    def quietest(self, start: float, end: float) -> float:
        a, b = self.f(start), self.f(end)
        if b <= a:
            return self.t(a)
        return self.t(a + int(np.argmin(self.db[a:b])))

    def is_quiet(self, t: float) -> bool:
        return self.frames == 0 or not self.voiced[self.f(t)]

    def first_voiced(self, start: float, end: float) -> float | None:
        a, b = self.f(start), self.f(end)
        idx = np.flatnonzero(self.voiced[a:b])
        return self.t(a + int(idx[0])) if len(idx) else None

    def last_voiced_end(self, start: float, end: float) -> float | None:
        a, b = self.f(start), self.f(end)
        idx = np.flatnonzero(self.voiced[a:b])
        return self.t(a + int(idx[-1]) + 1) if len(idx) else None


def decode(media: str) -> np.ndarray:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(media), "-vn", "-ac", "1",
                        "-ar", str(RATE), "-f", "s16le", "-"], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg could not decode %s: %s" % (media, p.stderr.decode(errors="replace")[-400:]))
    return np.frombuffer(p.stdout, dtype=np.int16).astype(np.float64) / 32768.0


def build(media: str) -> SpeechMask:
    pcm = decode(media)
    n = len(pcm) // HOP
    if n == 0:
        return SpeechMask(np.array([-120.0]), 0.0, -120.0, -120.0)
    frames = pcm[: n * HOP].reshape(n, HOP)
    db = 20 * np.log10(np.maximum(np.sqrt((frames ** 2).mean(axis=1)), 1e-6))
    speech = float(np.percentile(db, 95))
    # Denoised audio can be digital silence between words (-120 dB); measure the floor no lower than 70 dB under speech
    floor = max(float(np.percentile(db, 10)), speech - 70.0)
    # Voiced = more than 10 dB over the room floor and within 40 dB of the speech level. Soft word endings stay voiced;
    # room tone, hiss residue and silence are quiet.
    threshold = max(floor + 10.0, speech - 40.0)
    return SpeechMask(db, threshold, floor, speech)
