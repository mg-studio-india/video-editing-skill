#!/usr/bin/env python3
"""build_index.py: publish the style blueprints and regenerate the index files.

  build_index.py                      rebuild index.json, INDEX.md, PROMPTS.md from references/blueprints/B*.json
  build_index.py --ingest SRC_DIR     one-time import of SRC_DIR/*/blueprint.json: shuffled into B01..Bnn with an
                                      unstored random order, source ids stripped, {{BID}} filled, then rebuild

Edit a blueprint directly in references/blueprints/ and run the rebuild; check_blueprints.py must pass afterwards.
"""
import argparse
import glob
import json
import os
import random
import statistics as st
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(os.path.dirname(HERE), "references")
BP = os.path.join(REF, "blueprints")

FAMILY_DESC = {
    "giant-keyword": "small lead words + one huge accent-coloured key word per phrase",
    "two-tier-script": "two typographic tiers (caps line + script / handwritten completion)",
    "stacked-kinetic": "phrases stacked as kinetic typography",
    "boxed-pill": "caption text on a solid or translucent box / pill",
    "karaoke-highlight": "the spoken word is highlighted as it is said",
    "word-by-word-plain": "words appear one at a time, no box, little emphasis",
    "phrase-plain": "whole phrase at once, plain text",
    "title-only": "no speech captions; titles, labels or cards only",
    "none": "no on-screen text",
}


def ingest(src):
    files = sorted(glob.glob(os.path.join(src, "*", "blueprint.json")))
    rng = random.SystemRandom()
    rng.shuffle(files)
    os.makedirs(BP, exist_ok=True)
    for old in glob.glob(os.path.join(BP, "B*.json")):
        os.remove(old)
    for n, p in enumerate(files, 1):
        bid = "B%02d" % n
        b = json.load(open(p))
        spec = os.path.join(os.path.dirname(p), "caption-spec.json")
        if os.path.isfile(spec):
            b["caption_family"] = json.load(open(spec)).get("family")
        b.pop("src", None)
        txt = json.dumps(b, ensure_ascii=False).replace("{{BID}}", bid)
        b = json.loads(txt)
        b = {"id": bid, **{k: v for k, v in b.items() if k != "id"}}
        json.dump(b, open(os.path.join(BP, bid + ".json"), "w"), indent=1, ensure_ascii=False)
    print("ingested %d blueprints (random order, no mapping kept)" % len(files))


def fam_desc(f):
    return FAMILY_DESC.get(f or "", FAMILY_DESC.get((f or "").split(":")[0], (f or "").replace("other:", "").replace("-", " ")))


def rebuild():
    bps = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(BP, "B*.json")))]
    rows = []
    for b in bps:
        fm, p, s = b.get("format", {}), b.get("pacing", {}), b.get("signature", {})
        rows.append({"id": b["id"], "format": fm.get("type"), "aspect": fm.get("aspect"), "language": fm.get("language"),
                     "duration_class": fm.get("duration_class"), "people_on_screen": fm.get("people_on_screen"),
                     "topic_class": b.get("topic_class"), "caption_family": b.get("caption_family"),
                     "median_shot_s": p.get("median_shot_s"), "cuts_per_min": p.get("cuts_per_min"), "wpm": p.get("wpm"),
                     "look_intent": b.get("style", {}).get("look_intent"), "music": b.get("sound", {}).get("music"),
                     "signature": s.get("one_line"), "unique_devices": s.get("unique_devices", []),
                     "catalog_styles": [c.get("id") for c in b.get("catalog_styles", [])],
                     "tags": b.get("match", {}).get("tags", []), "needs": b.get("match", {}).get("needs", {}),
                     "quality_score": b.get("quality_score"), "file": "blueprints/%s.json" % b["id"]})
    json.dump({"schema": "blueprint-index/1", "count": len(rows), "blueprints": rows},
              open(os.path.join(REF, "index.json"), "w"), indent=1, ensure_ascii=False)

    def m(k, flt=None):
        v = [r[k] for r in rows if isinstance(r[k], (int, float)) and (flt is None or flt(r))]
        return round(st.median(v), 2) if v else None
    talk = lambda r: r["format"] in ("talking-head", "podcast-clip", "mixed") and (r["quality_score"] or 0) >= 3
    fams = defaultdict(list)
    for r in rows:
        fams[r["caption_family"] or "none"].append(r)
    L = ["# Style blueprint index · %d blueprints" % len(rows), "",
         "The default reference set for `video-reference-match`. Each blueprint is a brand-neutral, measured editing system "
         "(structure, pacing, captions, background text, motion graphics, cut-outs, layout, camera, transitions, sound) "
         "with a paste-ready brand prompt. Blueprints carry no source identity. Match a project with `scripts/match.py`; "
         "the gate in SKILL.md decides whether a blueprint is used.", "",
         "Files: `blueprints/Bxx.json` (full blueprint) · `index.json` (one row per blueprint, what the matcher reads) · "
         "`PROMPTS.md` (all brand prompts) · `weights.json` (matching columns) · `blueprint-schema.md`.", "",
         "## Targets across comparable talking-head blueprints", "",
         "| Metric | Median |", "|---|---|",
         "| Median shot (s) | %s |" % m("median_shot_s", talk), "| Cuts per minute | %s |" % m("cuts_per_min", talk),
         "| Words per minute | %s |" % m("wpm", talk), "", "Grade is never taken from a blueprint: it is built from the project's own footage; "
         "blueprints only state a look intent.", "", "## Blueprints by caption family", ""]
    order = list(FAMILY_DESC)
    for f in sorted(fams, key=lambda x: (order.index(x) if x in order else len(order) - 2.5, x)):
        L += ["### %s — %s" % (f, fam_desc(f)), "", "| ID | Format | Lang | Duration | Score | Signature |", "|---|---|---|---|---|---|"]
        for r in sorted(fams[f], key=lambda r: -(r["quality_score"] or 0)):
            L.append("| [%s](blueprints/%s.json) | %s %s | %s | %s | %s | %s |" % (r["id"], r["id"], r["format"], r["aspect"], r["language"],
                     (r["duration_class"] or "").split(" ")[0], r["quality_score"], (r["signature"] or "").replace("|", "/")))
        L.append("")
    tags = Counter(t for r in rows for t in r["tags"])
    L += ["## Tags", "", ", ".join("%s (%d)" % kv for kv in tags.most_common(60)), ""]
    open(os.path.join(REF, "INDEX.md"), "w").write("\n".join(L) + "\n")

    P = ["# Brand prompts · %d style blueprints" % len(rows), "",
         "Each prompt applies one blueprint's editing system to **your** brand. Fill the BRAND TOKENS (colours, fonts, "
         "handle, logo) from the brand; every geometry, size and timing value stays as measured. Grade always comes from "
         "your own footage. To mix, take CAPTIONS from one prompt and OTHER TEXT from another. Sizes were solved for the "
         "fonts in `~/.agents/skills/video-pipeline/engine/assets/fonts`; if you swap a font, run the prompt's VERIFY step "
         "(`scripts/caption_probe.py`, expected values from `scripts/fit_font.py`) and adjust px until it passes.", ""]
    for f in sorted(fams, key=lambda x: (order.index(x) if x in order else len(order) - 2.5, x)):
        P += ["## %s" % f, "", "_%s_" % fam_desc(f), ""]
        for r in sorted(fams[f], key=lambda r: -(r["quality_score"] or 0)):
            b = next(x for x in bps if x["id"] == r["id"])
            P += ["### %s · %s · %s · score %s" % (r["id"], r["format"], r["language"], r["quality_score"]), "",
                  r["signature"] or "", "", "```text", (b.get("brand_prompt") or "(no prompt)").strip(), "```", ""]
    open(os.path.join(REF, "PROMPTS.md"), "w").write("\n".join(P) + "\n")
    print("rebuilt index.json, INDEX.md, PROMPTS.md (%d blueprints)" % len(rows))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ingest")
    a = ap.parse_args()
    if a.ingest:
        ingest(a.ingest)
    rebuild()


if __name__ == "__main__":
    main()
