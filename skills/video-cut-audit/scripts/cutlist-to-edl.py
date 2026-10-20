#!/usr/bin/env python3
"""cutlist-to-edl.py: turn our cut-list.json into the EDL shape the cut review page reads, so the page can be built."""
import argparse, json

ap = argparse.ArgumentParser()
ap.add_argument("--cut-list", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

cl = json.load(open(args.cut_list))
dur = float(cl["source_duration"])
kept = sorted(cl["kept"], key=lambda s: s["start"])
reasons = {}
for r in cl.get("removed", []):
    reasons.setdefault((round(r["start"], 2)), []).append(r["reason"] + ((": " + r["text"][:60]) if r.get("text") else ""))

deletes, cursor = [], 0.0
for s in kept:
    if s["start"] > cursor + 0.001:
        why = [v for k, vs in reasons.items() if cursor - 0.05 <= k <= s["start"] for v in vs] or ["removed"]
        deletes.append({"start": round(cursor, 3), "end": round(s["start"], 3), "reasons": why[:4]})
    cursor = max(cursor, s["end"])
if cursor < dur - 0.001:
    deletes.append({"start": round(cursor, 3), "end": round(dur, 3), "reasons": ["tail"]})

removed = sum(d["end"] - d["start"] for d in deletes)
edl = {
    "agent": "cut-audit/paper-cut",
    "params": {"gap": "auto-editor -30dB", "headPad": 0.15, "tailPad": 0.45},
    "source_duration": dur,
    "edited_duration": round(dur - removed, 3),
    "removed": round(removed, 3),
    "delete_ranges": deletes,
    "keep_ranges": [{"start": s["start"], "end": s["end"]} for s in kept],
}
json.dump(edl, open(args.out, "w"), indent=1)
print("EDL: %d kept, %d cut ranges, removed %.1fs of %.1fs -> %s" % (len(kept), len(deletes), removed, dur, args.out))
