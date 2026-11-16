#!/usr/bin/env python3
"""cut.py: the tight, word-safe cut.

Which words stay comes from the transcript (paper-cut.py drops restarts, retakes and false starts; isolated fillers
and anything the plan drops go too). Where each cut lands comes from the cleaned voice: every edge is placed inside
a measured quiet gap between two words, with a short lead-in and tail, so no word is ever clipped. Long pauses inside
kept speech shrink to --max-pause. The result is the active cut-list.json plus CUT.md for review.

  cut.py --transcript T.json --audio voice-clean.wav --duration 81.2 --out-dir W [--drop 12.4-15.0] [--restore 30-33]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runtime  # noqa: E402
runtime.ensure_project_venv()
import speechmask  # noqa: E402

FILLERS = {"um", "umm", "uh", "uhh", "uhm", "hmm", "hm", "mm", "mmm", "er", "erm", "ah", "aa", "aaa"}


def parse_range(text: str) -> tuple[float, float]:
    m = re.fullmatch(r"\s*([\d.]+)\s*-\s*([\d.]+)\s*", text)
    if not m or float(m.group(2)) <= float(m.group(1)):
        raise SystemExit("bad range %r (use START-END in source seconds, e.g. 12.4-15.0)" % text)
    return float(m.group(1)), float(m.group(2))


def word_text(w: dict) -> str:
    return str(w.get("text") or w.get("w") or "").strip()


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9']", "", t.lower())


def gap_region(mask, a: dict, b: dict) -> tuple[float, float]:
    """The quiet stretch that separates word a from word b (zero length when the words run together)."""
    asr0, asr1 = float(a["end"]), float(b["start"])
    lo, hi = float(a["start"]) + 0.03, float(b["end"]) - 0.03
    lo2, hi2 = max(lo, min(asr0, asr1) - 0.30), min(hi, max(asr0, asr1) + 0.30)
    regions = mask.quiet_regions(lo2, hi2) if hi2 > lo2 else []
    if regions:
        c0, c1 = min(asr0, asr1) - 0.05, max(asr0, asr1) + 0.05
        mid = (asr0 + asr1) / 2

        def score(r):
            overlap = max(0.0, min(r[1], c1) - max(r[0], c0))
            return (overlap, -abs((r[0] + r[1]) / 2 - mid))
        return max(regions, key=score)
    t = mask.quietest(min(asr0, asr1) - 0.06, max(asr0, asr1) + 0.06)
    return (t, t)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--transcript", required=True, help="source-time word transcript (refined to speech energy)")
    ap.add_argument("--audio", required=True, help="cleaned voice WAV aligned to the source picture")
    ap.add_argument("--duration", type=float, required=True, help="source duration in seconds")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--drop", action="append", default=[], help="remove words inside START-END (source seconds)")
    ap.add_argument("--restore", action="append", default=[], help="keep words inside START-END even if marked as retakes")
    ap.add_argument("--keep-retakes", action="store_true", help="do not remove restarts, retakes and false starts")
    ap.add_argument("--keep-fillers", action="store_true", help="keep isolated um/uh/hmm")
    ap.add_argument("--max-pause", type=float, default=0.28, help="longest pause kept inside speech (s)")
    ap.add_argument("--lead", type=float, default=0.06, help="silence kept before a word after a cut (s)")
    ap.add_argument("--tail", type=float, default=0.10, help="silence kept after a word before a cut (s)")
    ap.add_argument("--head", type=float, default=0.12, help="lead-in before the very first word (s)")
    a = ap.parse_args()

    data = json.load(open(a.transcript, encoding="utf-8"))
    words = [w for w in (data["words"] if isinstance(data, dict) else data) if word_text(w)]
    os.makedirs(a.out_dir, exist_ok=True)
    out_list = os.path.join(a.out_dir, "cut-list.json")
    if not words:
        full = {"source_duration": a.duration, "kept": [{"start": 0.0, "end": round(a.duration, 3)}],
                "kept_seconds": round(a.duration, 3), "removed": [], "kept_word_indices": [],
                "status": "proposed", "note": "no recognised speech: the full picture is kept"}
        json.dump(full, open(out_list, "w"), indent=1)
        open(os.path.join(a.out_dir, "CUT.md"), "w").write("# Cut\n\nNo speech recognised; the full source is kept.\n")
        print("no words: full source kept (%.2fs)" % a.duration)
        return

    n = len(words)
    keep = [True] * n
    reasons: dict[int, str] = {}

    # 1. restarts, retakes, false starts (transcript logic)
    if not a.keep_retakes:
        with tempfile.TemporaryDirectory(prefix="paper-cut-") as tmp:
            subprocess.run([sys.executable, os.path.join(HERE, "paper-cut.py"), "--transcript", a.transcript,
                            "--duration", str(a.duration), "--out-dir", tmp], check=True, stdout=subprocess.DEVNULL)
            pc = json.load(open(os.path.join(tmp, "cut-list.json")))
        kept_idx = set(pc.get("kept_word_indices", range(n)))
        pc_removed = [r for r in pc.get("removed", []) if not str(r.get("reason", "")).startswith("silence")]
        for i in range(n):
            if i not in kept_idx:
                keep[i] = False
                mid = (float(words[i]["start"]) + float(words[i]["end"])) / 2
                hit = next((r for r in pc_removed if r["start"] - 0.05 <= mid <= r["end"] + 0.05), None)
                reasons[i] = (hit or {}).get("reason", "retake / restart")

    mask = speechmask.build(a.audio)

    # 2. isolated fillers (a pause on both sides, so removing them leaves a clean join)
    if not a.keep_fillers:
        for i, w in enumerate(words):
            if keep[i] and norm(word_text(w)) in FILLERS:
                before = float(w["start"]) - (float(words[i - 1]["end"]) if i else 0.0)
                after = (float(words[i + 1]["start"]) if i + 1 < n else a.duration) - float(w["end"])
                if before >= 0.12 and after >= 0.12:
                    keep[i] = False
                    reasons[i] = "filler"

    # 3. plan decisions
    for text in a.drop:
        r0, r1 = parse_range(text)
        for i, w in enumerate(words):
            if r0 <= (float(w["start"]) + float(w["end"])) / 2 <= r1:
                keep[i] = False
                reasons[i] = "dropped by plan (%s)" % text
    for text in a.restore:
        r0, r1 = parse_range(text)
        for i, w in enumerate(words):
            if r0 <= (float(w["start"]) + float(w["end"])) / 2 <= r1:
                keep[i] = True
                reasons.pop(i, None)
    if not any(keep):
        raise SystemExit("every word would be removed; check --drop ranges")

    # 4. edges from the waveform
    gaps = [gap_region(mask, words[j], words[j + 1]) for j in range(n - 1)]
    onset0 = mask.first_voiced(max(0.0, float(words[0]["start"]) - 0.3), float(words[0]["end"])) or float(words[0]["start"])
    head_region = (0.0, onset0)
    off_last = mask.last_voiced_end(float(words[-1]["start"]), min(a.duration, float(words[-1]["end"]) + 0.4)) \
        or float(words[-1]["end"])
    tail_region = (off_last, a.duration)

    segments, shortened, tight = [], [], []
    cur = None
    for j in range(n):
        if not keep[j]:
            continue
        if cur is None:
            region = head_region if j == 0 else gaps[j - 1]
            pad = a.head if j == 0 else a.lead
            cur = max(region[0], region[1] - pad)
            if region[1] - region[0] < 0.005 and j > 0:
                tight.append(round(cur, 3))
        if j == n - 1 or not keep[j + 1]:
            region = tail_region if j == n - 1 else gaps[j]
            end = min(region[1], region[0] + a.tail)
            if region[1] - region[0] < 0.005 and j < n - 1:
                tight.append(round(end, 3))
            segments.append([cur, end])
            cur = None
        else:
            region = gaps[j]
            if region[1] - region[0] > a.max_pause:
                keep_left = a.max_pause * 0.55
                c0, c1 = region[0] + keep_left, region[1] - (a.max_pause - keep_left)
                if c1 - c0 >= 0.06:
                    segments.append([cur, c0])
                    shortened.append({"start": round(c0, 3), "end": round(c1, 3), "reason": "pause %.2fs -> %.2fs"
                                      % (region[1] - region[0], a.max_pause), "text": ""})
                    cur = c1

    merged = []
    for s0, s1 in sorted(segments):
        s0, s1 = max(0.0, s0), min(a.duration, s1)
        if s1 - s0 < 0.05:
            continue
        if merged and s0 - merged[-1][1] < 0.04:
            merged[-1][1] = max(merged[-1][1], s1)
        else:
            merged.append([s0, s1])
    kept = [{"start": round(s0, 3), "end": round(s1, 3)} for s0, s1 in merged]

    removed = []
    i = 0
    while i < n:
        if keep[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and not keep[j + 1] and reasons.get(j + 1) == reasons.get(i):
            j += 1
        removed.append({"start": round(float(words[i]["start"]), 3), "end": round(float(words[j]["end"]), 3),
                        "reason": reasons.get(i, "removed"), "text": " ".join(word_text(w) for w in words[i:j + 1])})
        i = j + 1
    removed += shortened
    removed.sort(key=lambda r: r["start"])

    kept_seconds = round(sum(k["end"] - k["start"] for k in kept), 3)
    out = {"source_duration": round(a.duration, 3), "kept": kept, "kept_seconds": kept_seconds, "removed": removed,
           "kept_word_indices": [i for i in range(n) if keep[i]], "tight_joins": tight,
           "params": {"max_pause": a.max_pause, "lead": a.lead, "tail": a.tail, "head": a.head,
                      "drop": a.drop, "restore": a.restore, "keep_retakes": a.keep_retakes,
                      "keep_fillers": a.keep_fillers, "quiet_threshold_db": round(mask.threshold_db, 1)},
           "status": "proposed"}
    json.dump(out, open(out_list, "w"), indent=1)

    lines = ["# Cut", "",
             "Source %.1fs -> %.1fs kept in %d segments (%d jump cuts). Every edge sits in measured silence; pauses inside "
             "speech are capped at %.2fs." % (a.duration, kept_seconds, len(kept), max(0, len(kept) - 1), a.max_pause), ""]
    if tight:
        lines += ["Joins with no silence between words (listen to these): " + ", ".join("%.2fs" % t for t in tight), ""]
    lines += ["## What stays", ""]
    para, last_end = [], None
    for i, w in enumerate(words):
        if not keep[i]:
            continue
        if last_end is not None and float(w["start"]) - last_end > 1.2 and para:
            lines.append(" ".join(para)); para = []
        para.append(word_text(w))
        last_end = float(w["end"])
    if para:
        lines.append(" ".join(para))
    lines += ["", "## Removed", ""]
    lines += ["- %.2f-%.2fs [%s] %s" % (r["start"], r["end"], r["reason"], ("~~%s~~" % r["text"]) if r["text"] else "")
              for r in removed] or ["Nothing removed."]
    open(os.path.join(a.out_dir, "CUT.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("kept %.2fs of %.2fs in %d segments; %d word ranges removed; %d pauses shortened; %d tight joins -> %s"
          % (kept_seconds, a.duration, len(kept), len(removed) - len(shortened), len(shortened), len(tight), out_list))


if __name__ == "__main__":
    main()
