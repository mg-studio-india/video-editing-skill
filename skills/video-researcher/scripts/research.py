#!/usr/bin/env python3
"""research.py: scaffold and check the topic research that feeds graphics, sounds and b-roll.

  research.py init  --project ROOT [--topic "..."]   writes .video-pipeline/research/research.json + RESEARCH.md
  research.py check --project ROOT                    validates ids, sources and links before the storyboard uses them

`init` lists what the speaker actually says that research can support: numbers, money, years, names and claims,
each tied to its speech-NNN id on the cut timeline. The agent then searches the web and fills `facts` (each with a
source URL), and plans `motion` (HyperFrames catalog blocks), `sounds` and `broll` from those facts. Storyboard beats
cite `research-NNN` ids; the approval gate rejects a research id without a source URL.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

NUMBER = re.compile(r"(\d[\d,.]*\s*(%|percent|crore|cr|lakh|lac|million|billion|thousand|hazaar|k|x)?|₹|\$|rs\.?)", re.I)
YEAR = re.compile(r"\b(19|20)\d{2}\b")
MONEY = re.compile(r"\b(crore|lakh|lac|rupees?|rupaye|paise|dollars?|funding|valuation|revenue|profit|loss|ipo|market cap)\b", re.I)
CLAIM = re.compile(r"\b(sabse|most|largest|biggest|first|only|record|number one|no\. ?1|top|fastest|cheapest|world|india)\b", re.I)


def workspace(project: str) -> Path:
    p = Path(project).expanduser().resolve()
    return p if p.name == ".video-pipeline" else p / ".video-pipeline"


def cmd_init(a) -> int:
    work = workspace(a.project)
    ev = json.loads((work / "source-evidence.json").read_text(encoding="utf-8"))
    out_dir = work / "research"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "research.json"
    # re-running after a recut refreshes the question list; facts, motion, sounds and b-roll are kept
    old = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    questions = []
    for seg in ev.get("speech_segments", []):
        text = seg["text"]
        why = []
        if NUMBER.search(text) or YEAR.search(text):
            why.append("number/date")
        if MONEY.search(text):
            why.append("money")
        if CLAIM.search(text):
            why.append("claim")
        caps = sorted({w for w in re.findall(r"\b[A-Z][a-zA-Z0-9&.-]{2,}\b", text)} - {"I", "The", "And", "But"})
        if caps:
            why.append("names: " + ", ".join(caps[:6]))
        if why:
            questions.append({"speech_ref": seg["id"], "at": [seg["start"], seg["end"]], "text": text, "why": why})
    data = {
        "topic": a.topic or old.get("topic") or "",
        "created": old.get("created") or datetime.date.today().isoformat(),
        "questions": questions,
        "facts": old.get("facts", []),
        "motion": old.get("motion", []),
        "sounds": old.get("sounds", []),
        "broll": old.get("broll", []),
        "schema": {
            "facts": {"id": "research-001", "claim": "what is true, in one line", "source_url": "https://...",
                      "source_name": "publisher", "published": "YYYY-MM-DD", "accessed": "YYYY-MM-DD",
                      "speech_refs": ["speech-004"], "on_screen": "short text a graphic may show"},
            "motion": {"id": "m1", "at_speech": "speech-004", "facts": ["research-001"], "catalog": "<catalog item name>",
                       "vars": {}, "why": "what the viewer should understand"},
            "sounds": {"id": "s1", "at_speech": "speech-004", "palette": "ping-metric", "why": "number lands"},
            "broll": {"id": "r1", "at_speech": "speech-006", "facts": ["research-002"],
                      "kind": "catalog-block | image | generated", "asset": "path or catalog name",
                      "source_url": "for images: where it came from", "license": "for images"},
        },
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [f"# Research · {data['topic'] or '(topic from the brief)'}", "",
             "Moments in the cut that research can support (fill `facts` in research.json, with a URL each):", ""]
    for q in questions:
        lines.append(f"- **{q['speech_ref']}** ({q['at'][0]:.1f}s) {', '.join(q['why'])}: “{q['text'][:160]}”")
    if not questions:
        lines.append("- No numbers, names or claims detected; research the topic itself for context graphics.")
    (out_dir / "RESEARCH.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(questions)} research moments -> {path}")
    return 0


def cmd_check(a) -> int:
    work = workspace(a.project)
    path = work / "research" / "research.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    ev = json.loads((work / "source-evidence.json").read_text(encoding="utf-8"))
    speech = {s["id"] for s in ev.get("speech_segments", [])}
    problems, facts = [], {}
    for f in data.get("facts", []):
        fid = str(f.get("id", ""))
        if not re.fullmatch(r"research-\d{3}", fid):
            problems.append(f"fact id {fid!r} must look like research-001")
        if not re.match(r"https?://", str(f.get("source_url", ""))):
            problems.append(f"{fid}: needs a source_url (http/https)")
        if not str(f.get("claim", "")).strip():
            problems.append(f"{fid}: needs a claim")
        for ref in f.get("speech_refs", []):
            if ref not in speech:
                problems.append(f"{fid}: speech ref {ref} is not in the current cut")
        facts[fid] = f
    for kind in ("motion", "sounds", "broll"):
        for item in data.get(kind, []):
            iid = item.get("id", "?")
            if item.get("at_speech") and item["at_speech"] not in speech:
                problems.append(f"{kind} {iid}: at_speech {item['at_speech']} is not in the current cut")
            for fid in item.get("facts", []):
                if fid not in facts:
                    problems.append(f"{kind} {iid}: unknown fact {fid}")
            if kind == "broll" and item.get("kind") == "image" and not (item.get("source_url") and item.get("license")):
                problems.append(f"broll {iid}: an image needs source_url and license")
    print(f"{len(facts)} facts, {len(data.get('motion', []))} motion, {len(data.get('sounds', []))} sounds, "
          f"{len(data.get('broll', []))} b-roll")
    for p in problems:
        print("  - " + p)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 0 if not problems else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    i.add_argument("--project", required=True)
    i.add_argument("--topic")
    i.set_defaults(f=cmd_init)
    c = sub.add_parser("check")
    c.add_argument("--project", required=True)
    c.set_defaults(f=cmd_check)
    a = ap.parse_args()
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
