#!/usr/bin/env python3
"""resolve-anchors.py: storyboard.plan.json (phrases) + transcript.json (flat cut) -> storyboard.json (seconds).

The plan is written before the cut, so it names phrases, not times. This fills every time from the flat-cut
transcript, and is re-run after every new cut: the plan file is the source, storyboard.json is derived.

What it resolves
  beats[]          "anchor": the phrase. "in" missing or "auto" -> anchor start - lead (default 0.20 s, or the beat's
                   "lead"). "out" missing or "auto" -> in + hold (the beat's "hold", else a default for its type).
                   "after": "@phrase" or seconds picks a later occurrence of a phrase said more than once.
  items[]          list/bullet items [text, time, anchor]: a missing or "@" time -> start of the anchor (or the text).
  "@phrase"        in a time field (in, out, pop, planted, payoff, *_at...) or a camera op: the phrase's start;
                   "@phrase:end" its end. Text fields are never resolved, so "@handle" copy stays as written.
  sfx[].at         "@phrase" -> the phrase's start ("@phrase:end" its end): sound cues land on words too.
  "duration"       "auto" -> cut-map.json flat_duration (next to the transcript) or the last word's end.

Phrases are searched in order: each beat looks from shortly before the previous beat's anchor, so a phrase said twice
resolves to the occurrence that fits the plan's order. Unresolved anchors are reported, the beat is marked
"unresolved": true with null times, and the exit code is 1: fix the plan (a shorter phrase, an "after") or tell the user
the line was cut.

  --jump-frames    adds ["set", t, 1.0] at every measured jump cut (take-geometry), so no zoom crosses a cut.

Usage:
  python3 resolve-anchors.py --plan W/storyboard.plan.json --transcript W/transcript.json --out W/storyboard.json \
      [--jump-frames W/jump-frames.json]
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys

LEAD = 0.20
HOLD = {"line": 5.0, "chip": 3.0, "logo": 3.0, "pills": 5.0, "tag": 5.0, "clip": 3.0, "image": 3.5, "site": 3.0}
HOLD_DEFAULT = 4.0
LIST_TAIL = 2.5
TIME_KEYS = {"at", "in", "out", "pop", "planted", "payoff", "count_at", "bars_at", "line_at", "split_at", "recap_at",
             "fill_at", "type_t0", "type_t1", "send", "think_end"}


def norm(s: str) -> list[str]:
    return re.sub(r"[^a-z0-9' ]+", " ", s.lower()).split()


class Words:
    def __init__(self, words: list[dict]):
        self.toks: list[tuple[str, float, float]] = []
        for w in words:
            parts = norm(w.get("text") or w.get("w") or "")
            for p in parts:
                self.toks.append((p, float(w["start"]), float(w["end"])))

    def find(self, phrase: str, after: float = -1.0) -> tuple[float, float] | None:
        p = norm(phrase)
        if not p:
            return None
        n = len(p)
        for i in range(len(self.toks) - n + 1):
            if self.toks[i][1] < after:
                continue
            if all(self.toks[i + k][0] == p[k] for k in range(n)):
                return self.toks[i][1], self.toks[i + n - 1][2]
        return None


def parse_ref(value) -> tuple[str, str] | None:
    """'@three tools' -> ('three tools', 'start'); '@three tools:end' -> ('three tools', 'end')."""
    if not isinstance(value, str) or not value.startswith("@") or len(value) < 2:
        return None
    body = value[1:]
    if body.endswith(":end"):
        return body[:-4].strip(), "end"
    return body.strip(), "start"


class Resolver:
    def __init__(self, words: Words, duration: float):
        self.w = words
        self.duration = duration
        self.problems: list[str] = []
        self.rows: list[tuple] = []

    def ref(self, value, after: float, where: str):
        r = parse_ref(value)
        if r is None:
            return value
        hit = self.w.find(r[0], after)
        if hit is None:
            self.problems.append(f"{where}: phrase not found: {r[0]!r}")
            return None
        return round(hit[0] if r[1] == "start" else hit[1], 3)

    def walk(self, node, after: float, where: str, timed: bool = False):
        """Resolve '@phrase' strings, but only in time fields (TIME_KEYS) and camera ops, so on-screen text that
        starts with '@' (a social handle) is never mistaken for an anchor."""
        if isinstance(node, dict):
            return {k: self.walk(v, after, f"{where}.{k}", timed or k in TIME_KEYS) for k, v in node.items()}
        if isinstance(node, list):
            out, cur = [], after
            for i, v in enumerate(node):
                r = self.walk(v, cur, f"{where}[{i}]", timed)
                if timed and isinstance(v, str) and parse_ref(v) and isinstance(r, (int, float)):
                    cur = r - 1.0
                elif isinstance(v, list) and isinstance(r, list) and len(r) > 1 and isinstance(r[1], (int, float)):
                    cur = r[1] - 1.0
                out.append(r)
            return out
        if timed and isinstance(node, str):
            return self.ref(node, after, where)
        return node

    def beat(self, b: dict, cursor: float) -> tuple[dict, float]:
        b = copy.deepcopy(b)
        bid = b.get("id", "?")
        after = cursor
        if "after" in b:
            a = b.pop("after")
            a = self.ref(a, -1.0, f"beat {bid} after") if isinstance(a, str) else a
            if isinstance(a, (int, float)):
                after = float(a)
        anchor = b.get("anchor")
        start = end = None
        if anchor and anchor != "-":
            hit = self.w.find(anchor, after)
            if hit is None:
                self.problems.append(f"beat {bid}: anchor not found: {anchor!r}")
                b["unresolved"] = True
                b["in"] = b["out"] = None
                self.rows.append((bid, anchor, None, None, "NOT FOUND"))
                return b, cursor
            start, end = hit
        lead = float(b.pop("lead", LEAD))
        hold = b.pop("hold", None)
        if b.get("in") in (None, "auto"):
            if start is None:
                self.problems.append(f"beat {bid}: no anchor and no 'in'")
                b["unresolved"] = True
                self.rows.append((bid, anchor, None, None, "NO TIME"))
                return b, cursor
            b["in"] = round(max(0.0, start - lead), 3)
        else:
            b["in"] = self.ref(b["in"], after, f"beat {bid} in")
        ref_t = start if start is not None else (b["in"] or after)
        if isinstance(b.get("items"), list):
            items, icur = [], ref_t - 0.5
            for k, it in enumerate(b["items"]):
                it = list(it)
                if len(it) < 2 or it[1] in (None, "@", "auto"):
                    phrase = it[2] if len(it) > 2 and it[2] not in (None, "-") else it[0]
                    hit = self.w.find(phrase, icur)
                    if hit is None:
                        self.problems.append(f"beat {bid} item {k}: phrase not found: {phrase!r}")
                        t = None
                    else:
                        t = round(hit[0], 3)
                        icur = hit[0]
                    it = [it[0], t] + it[2:]
                items.append(it)
            b["items"] = items
        if b.get("out") in (None, "auto"):
            if b.get("items") and all(isinstance(i[1], (int, float)) for i in b["items"]):
                b["out"] = round(max(i[1] for i in b["items"]) + LIST_TAIL, 3)
            else:
                b["out"] = round(b["in"] + float(hold if hold is not None else HOLD.get(b.get("type"), HOLD_DEFAULT)), 3)
        else:
            parsed = parse_ref(b["out"])
            if parsed and parsed[1] == "start" and not b["out"].endswith(":start"):
                b["out"] = "@" + parsed[0] + ":end"      # an out-phrase means "when that phrase ends"
            b["out"] = self.ref(b["out"], ref_t - 0.5, f"beat {bid} out")
        for k in list(b):
            if k in ("in", "out", "items", "anchor", "id", "type"):
                continue
            b[k] = self.walk(b[k], ref_t - 0.5, f"beat {bid}.{k}", k in TIME_KEYS)
        if isinstance(b.get("out"), (int, float)):
            b["out"] = round(min(b["out"], self.duration), 3)
        self.rows.append((bid, anchor, b.get("in"), b.get("out"), "ok"))
        return b, (start - 2.0 if start is not None else cursor)


def resolve(plan: dict, words: list[dict], duration: float) -> tuple[dict, Resolver]:
    R = Resolver(Words(words), duration)
    out = {}
    for k, v in plan.items():
        if k == "beats":
            beats, cur = [], -1.0
            for b in v:
                rb, cur = R.beat(b, cur)
                beats.append(rb)
            out["beats"] = beats
        elif k == "duration":
            out[k] = round(duration, 3) if v in (None, "auto") else v
        elif k == "camera":
            out[k] = R.walk(v, -1.0, k, timed=True)
        elif k == "sfx":                     # sound cues: "at": "@phrase" lands on the phrase's first word
            out[k] = R.walk(v, -1.0, k)
        elif k in ("loops", "tag", "tags"):
            out[k] = R.walk(v, -1.0, k)
        else:
            out[k] = v
    return out, R


def add_resets(camera: list, jumps: list[dict]) -> list:
    """Pure (tested): a ["set", t, 1.0] at every measured jump frame, so no zoom is carried across a cut. Skips a jump
    when the plan already has an op within 0.05 s of it. Returns the ops sorted by time."""
    ops = [list(c) for c in camera or []]
    have = [c[1] for c in ops if len(c) > 1 and isinstance(c[1], (int, float))]
    for j in jumps:
        t = j.get("set_at")
        if isinstance(t, (int, float)) and not any(abs(t - h) < 0.05 for h in have):
            ops.append(["set", round(t, 3), 1.0])
    return sorted(ops, key=lambda c: c[1] if len(c) > 1 and isinstance(c[1], (int, float)) else 1e9)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plan", required=True)
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cut-map", help="default: cut-map.json next to the transcript")
    ap.add_argument("--jump-frames", help="jump-frames.json from jump-frames.py: adds a camera reset at every jump cut")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    t = json.load(open(a.transcript))
    words = t["words"] if isinstance(t, dict) else t
    cm = a.cut_map or os.path.join(os.path.dirname(os.path.abspath(a.transcript)), "cut-map.json")
    if os.path.isfile(cm):
        duration = float(json.load(open(cm))["flat_duration"])
    else:
        duration = float((t.get("duration") if isinstance(t, dict) else None) or (words[-1]["end"] if words else 0))
    if isinstance(plan.get("duration"), (int, float)):
        duration = min(duration, float(plan["duration"]))      # an explicit plan length wins: nothing may run past it
    out, R = resolve(plan, words, duration)
    if a.jump_frames:
        jumps = json.load(open(a.jump_frames))["jumps"]
        out["camera"] = add_resets(out.get("camera", []), jumps)
        print(f"camera: {len(jumps)} jump cuts, resets added where the plan had none")
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"{'beat':14} {'in':>8} {'out':>8}  anchor")
    for bid, anchor, i, o, st in R.rows:
        fi = f"{i:8.2f}" if isinstance(i, (int, float)) else f"{'-':>8}"
        fo = f"{o:8.2f}" if isinstance(o, (int, float)) else f"{'-':>8}"
        print(f"{bid:14} {fi} {fo}  {anchor!r}" + ("" if st == "ok" else f"   <- {st}"))
    print(f"-> {a.out} (duration {out.get('duration')})")
    if R.problems:
        print("\nUNRESOLVED (fix the plan: a shorter phrase, an 'after', or the line was cut):")
        for p in R.problems:
            print("  " + p)
        sys.exit(1)


if __name__ == "__main__":
    main()
