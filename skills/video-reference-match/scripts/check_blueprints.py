#!/usr/bin/env python3
"""check_blueprints.py: schema + anonymity check of references/blueprints/B*.json (run after any edit)."""
import argparse
import glob
import json
import os
import re
import sys

REF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references")
ASPECTS = {"9:16", "16:9", "9:10", "10:9", "4:5", "5:4", "1:1", "4:3", "3:4", "21:9", "2:1", "1:2"}
KEYS = ["schema", "id", "format", "topic_class", "signature", "hook", "structure", "pacing", "elements", "style", "sound",
        "catalog_styles", "use_when", "avoid_when", "match", "quality_score", "brand_prompt"]
TRACES = [(r"\b(reel|rel)\s?\d+\b", "source id"), (r"\b(?!test\.)\w+\.(mp4|mov|MOV|m4v)\b", "video file name"),
          (r"(grid|anim|crop)_\d", "proof-frame path"), (r"\b(full|captions)/(sheets|frames|hook|grid)", "analysis path"),
          (r"https?://", "URL"), (r"\b\d{1,2}:\d{2}(\.\d+)?\b", "mm:ss timestamp"), (r"@(?!handle\b)[A-Za-z][\w.]{2,}", "@handle"),
          (r"\{\{BID\}\}", "unfilled {{BID}}"), (r'"src"\s*:', "src key")]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--deny")
    a = ap.parse_args()
    deny = [w.strip().lower() for w in open(a.deny)] if a.deny else []
    deny = [w for w in deny if w and not w.startswith("#")]
    probs, files = [], sorted(glob.glob(os.path.join(REF, "blueprints", "B*.json")))
    for p in files:
        bid = os.path.basename(p)[:-5]
        raw = open(p).read()
        try:
            b = json.loads(raw)
        except Exception as e:
            probs.append("%s: invalid JSON (%s)" % (bid, e)); continue
        for k in KEYS:
            if k not in b:
                probs.append("%s: missing key %s" % (bid, k))
        for rx, what in TRACES:
            for m in re.finditer(rx, raw):
                if what == "mm:ss timestamp" and m.group(0) in ASPECTS:
                    continue
                probs.append("%s: %s %r" % (bid, what, raw[max(0, m.start() - 30):m.end() + 10]))
        if "hard_cuts" in raw or '"duration_s"' in raw or '"word_count"' in raw:
            probs.append("%s: exact count/duration field (runtime can be rebuilt from it)" % bid)
        pc = b.get("pacing", {})
        if isinstance(pc.get("cuts_per_min"), float) and pc["cuts_per_min"] != int(pc["cuts_per_min"]):
            probs.append("%s: cuts_per_min must be a whole number" % bid)
        bp = (b.get("brand_prompt") or "").lower()
        if re.search(r"(contrast|saturation|temperature|exposure)\s*[:=]?\s*[+-]?0?\.\d", bp):
            probs.append("%s: brand prompt carries grade values (grade must come from the user's footage)" % bid)
        low = raw.lower()
        for w in deny:
            if re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(w), low):
                probs.append("%s: deny-listed word %r" % (bid, w))
    for x in probs:
        print(x)
    print("%d blueprints, %d problem(s)" % (len(files), len(probs)))
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
