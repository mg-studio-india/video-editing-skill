"""Speech analysis from the word-level transcript.

All pure functions over plain dicts, so they are easy to unit-test.
"""
from __future__ import annotations

import bisect
import re

PAUSE_MIN = 0.35   # gaps between words at least this long count as pauses

# Unambiguous disfluencies: safe to suggest cutting.
FILLERS_HARD = {"um", "uh", "uhm", "umm", "uhh", "er", "erm", "ah", "hmm", "mm", "mhm", "eh"}
# Phrases that are often fillers but sometimes meaningful: reported, never auto-cut.
FILLERS_SOFT = [("you", "know"), ("i", "mean"), ("kind", "of"), ("sort", "of")]


def norm(word: str) -> str:
    return re.sub(r"[^\w']+", "", word.lower())


def find_fillers(words: list[dict]) -> list[dict]:
    out: list[dict] = []
    n = [norm(w["w"]) for w in words]
    for i, w in enumerate(words):
        if n[i] in FILLERS_HARD:
            out.append({"kind": "hard", "text": w["w"], "start": w["start"], "end": w["end"],
                        "first": i, "last": i})
    for i in range(len(words) - 1):
        for a, b in FILLERS_SOFT:
            if n[i] == a and n[i + 1] == b:
                out.append({"kind": "soft", "text": f"{words[i]['w']} {words[i + 1]['w']}",
                            "start": words[i]["start"], "end": words[i + 1]["end"],
                            "first": i, "last": i + 1})
    return sorted(out, key=lambda f: f["start"])


def find_pauses(words: list[dict], min_gap: float = PAUSE_MIN) -> list[dict]:
    pauses = []
    for a, b in zip(words, words[1:]):
        gap = b["start"] - a["end"]
        if gap >= min_gap:
            pauses.append({"start": round(a["end"], 3), "end": round(b["start"], 3),
                           "duration": round(gap, 3)})
    return pauses


def speech_stats(words: list[dict], t0: float, t1: float) -> dict:
    """Pace, pauses, fillers and where speech begins/ends."""
    duration = max(0.0, t1 - t0)
    if not words:
        return {"has_speech": False}
    first, last = words[0]["start"], words[-1]["end"]
    span = max(0.001, last - first)
    pauses = find_pauses(words)
    fillers = find_fillers(words)
    hard = [f for f in fillers if f["kind"] == "hard"]
    soft = [f for f in fillers if f["kind"] == "soft"]
    minutes = duration / 60.0 if duration else span / 60.0
    return {
        "has_speech": True,
        "word_count": len(words),
        "time_to_first_word": round(first - t0, 2),
        "first_word_at": round(first, 2),
        "last_word_at": round(last, 2),
        "speaking_span": round(span, 2),
        "words_per_minute": round(len(words) / (span / 60.0), 1) if span >= 3 else None,
        "speech_coverage": round(sum(w["end"] - w["start"] for w in words) / duration, 3) if duration else None,
        "pause_count": len(pauses),
        "pauses_per_minute": round(len(pauses) / minutes, 1) if minutes else None,
        "longest_pause": max((p["duration"] for p in pauses), default=0.0),
        "filler_count": len(hard),
        "fillers_per_minute": round(len(hard) / minutes, 1) if minutes else None,
        "soft_filler_count": len(soft),
    }


def assign_words_to_shots(shots: list[dict], words: list[dict]) -> None:
    """Annotate each shot with the words spoken inside it (by word midpoint)."""
    mids = [(w["start"] + w["end"]) / 2 for w in words]
    for s in shots:
        lo = bisect.bisect_left(mids, s["start"])
        hi = bisect.bisect_left(mids, s["end"])
        chunk = words[lo:hi]
        s["text"] = " ".join(w["w"] for w in chunk)
        s["word_count"] = len(chunk)
        s["words_per_sec"] = round(len(chunk) / s["duration"], 2) if s["duration"] > 0 else 0.0


LEAD_WINDOW = 0.6   # speech starting up to this long before a cut reads as a J-cut lead
TRAIL_WINDOW = 0.6  # speech ending up to this long after a cut reads as an L-cut trail
EDGE = 0.03


def cut_alignment(shots: list[dict], segments: list[dict], silences: list[dict]) -> dict:
    """Classify how each cut relates to speech. Heuristic: judged from timing only,
    since we do not have separate audio and picture tracks.

      on_pause    cut falls between sentences or inside silence
      j_lead      the next sentence starts just BEFORE the cut (audio leads picture)
      l_trail     the current sentence ends just AFTER the cut (audio trails picture)
      mid_speech  cut lands in the middle of a sentence with neither pattern
    """
    counts = {"on_pause": 0, "j_lead": 0, "l_trail": 0, "mid_speech": 0}
    if not segments:
        return {"counts": counts, "total": 0, "has_speech": False}
    for s in shots[1:]:
        t = s["start"]
        inside = [g for g in segments if g["start"] < t < g["end"]]
        in_silence = any(z["start"] <= t <= z["end"] for z in silences)
        if not inside or in_silence:
            label = "on_pause"
        else:
            g = inside[0]
            if t - g["start"] <= LEAD_WINDOW and t - g["start"] > EDGE:
                label = "j_lead"
            elif g["end"] - t <= TRAIL_WINDOW and g["end"] - t > EDGE:
                label = "l_trail"
            else:
                label = "mid_speech"
        s["cut_audio"] = label
        counts[label] += 1
    return {"counts": counts, "total": sum(counts.values()), "has_speech": True}
