#!/usr/bin/env python3
"""fix-words.py: correct misheard words in a transcript without touching its timing, and remember the fix.

Whisper mishears names, products and jargon ("cap cut" for CapCut, "hyper frames" for HyperFrames, a Hindi name spelled
three ways). Every transcription pass after a cut would bring the same errors back, so corrections live in the project's
corrections.json ({"misheard phrase": "Correct form"}) and transcribe.py applies them on every pass automatically (and
feeds the correct forms to whisper as spelling hints).

Timing is kept: a phrase replaced word for word keeps each word's times; several words merged into one ("cap cut" ->
"CapCut") span from the first start to the last end; one word split into several shares its span evenly. Punctuation
attached to the original words is kept ("cut." -> "CapCut.").

Usage:
  python3 fix-words.py --transcript W/transcript.json --add "cap cut=CapCut" --add "hyper frames=HyperFrames"
      (adds to W/corrections.json next to the transcript, then applies it in place)
  python3 fix-words.py --transcript W/transcript.json            # re-apply W/corrections.json
  python3 fix-words.py --transcript W/transcript.json --dry-run  # show what would change
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

TOKEN = re.compile(r"[^\w']+", re.UNICODE)


def norm(s: str) -> list[str]:
    return [t for t in TOKEN.split(s.lower()) if t]


def _edges(text: str) -> tuple[str, str]:
    m = re.match(r"^(\W*)(.*?)(\W*)$", text, re.S | re.UNICODE)
    return (m.group(1), m.group(3)) if m else ("", "")


def apply(words: list[dict], corrections: dict[str, str]) -> tuple[list[dict], list[str]]:
    """Pure (tested). words: [{text|w, start, end}]. Returns new words and a list of human-readable changes."""
    rules = sorted(((norm(k), v.split()) for k, v in corrections.items() if norm(k) and v.strip()),
                   key=lambda r: -len(r[0]))                     # longest phrase first
    out, changes, i = [], [], 0
    toks = [norm(w.get("text") or w.get("w") or "") for w in words]
    while i < len(words):
        hit = None
        for phrase, repl in rules:
            m = len(phrase)
            if i + m <= len(words) and all(len(toks[i + k]) == 1 and toks[i + k][0] == phrase[k] for k in range(m)):
                hit = (m, repl)
                break
            if toks[i] == phrase:                                  # one word holding the whole phrase ("co-founder")
                hit = (1, repl)
                break
        if not hit:
            out.append(words[i]); i += 1
            continue
        m, repl = hit
        span = words[i:i + m]
        lead = _edges(span[0].get("text") or span[0].get("w") or "")[0]
        trail = _edges(span[-1].get("text") or span[-1].get("w") or "")[1]
        n = len(repl)
        if n == m:
            new = [{**w, "start": w["start"], "end": w["end"], "text": r, "w": r} for w, r in zip(span, repl)]
        else:
            s0, s1 = float(span[0]["start"]), float(span[-1]["end"])
            step = (s1 - s0) / n
            new = [{"start": round(s0 + k * step, 3), "end": round(s0 + (k + 1) * step, 3), "text": r, "w": r}
                   for k, r in enumerate(repl)]
        new[0]["text"] = new[0]["w"] = lead + new[0]["text"]
        new[-1]["text"] = new[-1]["w"] = new[-1]["text"] + trail
        changes.append("%.2f s: %r -> %r" % (float(span[0]["start"]), " ".join(w.get("text") or w.get("w") for w in span),
                                              " ".join(w["text"] for w in new)))
        out.extend(new)
        i += m
    return out, changes


def load_corrections(path: str) -> dict[str, str]:
    return json.load(open(path)) if path and os.path.isfile(path) else {}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--corrections", help="default: corrections.json next to the transcript")
    ap.add_argument("--add", action="append", default=[], metavar='"misheard=Correct"')
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cpath = a.corrections or os.path.join(os.path.dirname(os.path.abspath(a.transcript)), "corrections.json")
    corr = load_corrections(cpath)
    for spec in a.add:
        if "=" not in spec:
            sys.exit("--add needs misheard=Correct, got %r" % spec)
        k, v = spec.split("=", 1)
        corr[k.strip()] = v.strip()
    t = json.load(open(a.transcript))
    words = t["words"] if isinstance(t, dict) else t
    new, changes = apply(words, corr)
    for c in changes:
        print("  " + c)
    print("%d change(s) from %d correction(s)%s" % (len(changes), len(corr), " (dry run)" if a.dry_run else ""))
    if a.dry_run:
        return
    if a.add:
        json.dump(corr, open(cpath, "w"), indent=1, ensure_ascii=False)
        print("corrections saved: %s (applied on every transcription pass)" % cpath)
    if isinstance(t, dict):
        t["words"] = new
        t["corrections_applied"] = len(changes)
    else:
        t = new
    json.dump(t, open(a.transcript, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
