#!/usr/bin/env python3
"""match.py: rank the style blueprints against a user's video / image / concept and write an editing roadmap.

  match.py [--video FILE ...] [--image FILE ...] [--concept "text"] [--transcript transcript.json]
           [--tags a,b] [--format talking-head] [--language Hinglish] [--weights weights.json]
           [--top 5] [--out DIR] [--pick B07[,B21]]

Without --pick: prints the ranked blueprints with per-column scores and writes <out>/matches.json.
With --pick: also writes <out>/ROADMAP.md (elements, motion graphics, cut-outs, captions, background text, transitions,
camera, layout, sound, pacing, grade-from-footage, catalog style IDs, brand prompt) for the chosen blueprint(s).

Columns are weighted (references/weights.json) and re-normalised over the columns this input can show. "similar" in
the output means score >= similar_threshold: that is the trigger for the reference gate (see SKILL.md).
Nothing is uploaded; video analysis is ffprobe/ffmpeg + a Haar face count.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(os.path.dirname(HERE), "references")
STOP = set("a an the and or of to in on for with my our your is are be this that it as at by from video reel reels make "
           "want like style me i we you short shorts".split())


# ------------------------------------------------------------------ blueprints
def load_blueprints():
    out = []
    for p in sorted(glob.glob(os.path.join(REF, "blueprints", "B*.json"))):
        b = json.load(open(p))
        b["_path"] = os.path.relpath(p, os.path.dirname(REF))
        out.append(b)
    if not out:
        sys.exit("no blueprints in %s" % os.path.join(REF, "blueprints"))
    return out


SPEAKER_FORMATS = {"talking-head", "podcast-clip", "mixed", "street-interview"}
FORMAT_WORDS = [("podcast", "podcast-clip"), ("interview", "podcast-clip"), ("skit", "skit"), ("comedy", "skit"),
                ("meme", "skit"), ("selfie", "talking-head"), ("talking", "talking-head"), ("explainer", "explainer-graphics"),
                ("animation", "explainer-graphics"), ("demo", "screen-demo"), ("tutorial", "screen-demo"),
                ("screen", "screen-demo"), ("ugc", "ugc-ad"), ("ad", "ugc-ad"), ("promo", "brand-promo"),
                ("launch", "brand-promo"), ("broll", "b-roll-voiceover"), ("voiceover", "b-roll-voiceover")]
IDF = {}


def build_idf(bps):
    import math
    docs = [bp_text(b) for b in bps]
    df = {}
    for d in docs:
        for w in d:
            df[w] = df.get(w, 0) + 1
    IDF.update({w: math.log((1 + len(docs)) / (1 + c)) + 0.2 for w, c in df.items()})


def words(t):
    return [w for w in re.findall(r"[a-z0-9]+", (t or "").lower()) if w not in STOP and len(w) > 1]


def bp_text(b):
    s = b.get("signature", {})
    parts = [b.get("topic_class", ""), s.get("one_line", ""), " ".join(s.get("unique_devices", [])),
             " ".join(b.get("use_when", [])), " ".join(b.get("match", {}).get("keywords", [])),
             " ".join(t.replace("-", " ") for t in b.get("match", {}).get("tags", [])), b.get("format", {}).get("type", "")]
    return set(words(" ".join(parts)))


# ------------------------------------------------------------------ input analysis
def ffprobe(path):
    d = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
                                   "-of", "json", path], capture_output=True, text=True).stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = any(s.get("codec_type") == "audio" for s in d.get("streams", []))
    return float(d.get("format", {}).get("duration", 0) or 0), v.get("width"), v.get("height"), a


def aspect_label(w, h):
    if not w or not h:
        return None
    r = w / h
    for lab, val in (("9:16", 9 / 16), ("9:10", 0.9), ("1:1", 1.0), ("4:5", 0.8), ("16:9", 16 / 9)):
        if abs(r - val) < 0.04:
            return lab
    return "9:16" if r < 0.7 else ("16:9" if r > 1.3 else "1:1")


def duration_class(s):
    return "micro" if s < 15 else "short" if s <= 60 else "mid" if s <= 180 else "long"


def cuts(path, dur):
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-vf", "select='gt(scene,0.3)',showinfo", "-an", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ts = [float(m) for m in re.findall(r"pts_time:([0-9.]+)", out)]
    shots = [b - a for a, b in zip([0.0] + ts, ts + [dur])] if dur else []
    shots = sorted(s for s in shots if s > 0.05)
    med = shots[len(shots) // 2] if shots else dur
    return {"cuts_per_min": round(60 * len(ts) / dur, 1) if dur else 0, "median_shot_s": round(med, 2)}


def faces(path, is_video, dur):
    try:
        import cv2
    except ImportError:
        return None
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    counts = []
    times = [dur * k / 8 for k in range(1, 8)] if is_video else [0]
    for t in times:
        if is_video:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.2f" % t, "-i", path, "-frames:v", "1", "-f", "image2pipe",
                                  "-vcodec", "png", "-"], capture_output=True).stdout
            import numpy as np
            img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE) if raw else None
        else:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        s = 540 / max(img.shape)
        img = cv2.resize(img, None, fx=s, fy=s)
        counts.append(len(casc.detectMultiScale(img, 1.1, 5, minSize=(40, 40))))
    if not counts:
        return None
    m = sorted(counts)[len(counts) // 2]
    return "0" if m == 0 else ("1" if m == 1 else "2+")


def analyse(a):
    f = {"text": set(), "tags": set(t.strip().lower() for t in (a.tags or "").split(",") if t.strip())}
    f["text"] |= set(words(a.concept))
    f["text"] |= {w for t in f["tags"] for w in words(t.replace("-", " "))}
    if a.format:
        f["format_type"] = a.format
    if a.language:
        f["language"] = a.language
    for v in a.video or []:
        dur, w, h, has_audio = ffprobe(v)
        f.update({"aspect": aspect_label(w, h), "duration_class": duration_class(dur), "duration_s": dur})
        f["pacing"] = cuts(v, dur)
        f["people_on_screen"] = faces(v, True, dur)
        f.setdefault("needs", {})["speaker_footage"] = f["people_on_screen"] not in (None, "0")
        f["is_raw_take"] = f["pacing"]["cuts_per_min"] < 3          # an unedited take has (almost) no cuts
    for im in a.image or []:
        try:
            from PIL import Image
            w, h = Image.open(im).size
            f.setdefault("aspect", aspect_label(w, h))
        except Exception:
            pass
        f.setdefault("people_on_screen", faces(im, False, 0))
    if "format_type" not in f:
        txt = " ".join(sorted(f["text"]))
        guess = next((ft for kw, ft in FORMAT_WORDS if re.search(r"\b%s\b" % kw, (a.concept or "").lower())), None)
        if guess:
            f["format_type"] = guess
    if a.transcript and os.path.isfile(a.transcript):
        t = json.load(open(a.transcript))
        ws = t.get("words", t if isinstance(t, list) else [])
        txt = " ".join((w.get("text") or w.get("w") or "") for w in ws)
        f["text"] |= set(words(txt))
        lang = (t.get("language") or "").lower()
        if "language" not in f and lang:
            f["language"] = "Hinglish" if ("hi" in lang or "hinglish" in lang) else ("English" if lang.startswith("en") else None)
        if ws and f.get("duration_s"):
            f["wpm"] = 60 * len(ws) / max(1, f["duration_s"])
            spoken = sum(max(0.0, float(w.get("end", 0)) - float(w.get("start", 0))) for w in ws) / f["duration_s"]
            if "format_type" not in f and f.get("people_on_screen") in ("1", "2+") and spoken > 0.4:
                f["format_type"] = "talking-head" if f["people_on_screen"] == "1" else "podcast-clip"
                f["format_inferred"] = True
    return f


# ------------------------------------------------------------------ scoring
def col_scores(f, b):
    s = {}
    fm = b.get("format", {})
    if "format_type" in f:
        bt_ = fm.get("type")
        same = f["format_type"] == bt_
        close = {f["format_type"], bt_} <= SPEAKER_FORMATS or bt_ == "mixed"
        s["format_type"] = 1.0 if same else (0.6 if close else 0.0)
    if f.get("text") and IDF:
        bt = bp_text(b)
        q = {w for w in f["text"] if w in IDF}                  # words no blueprint uses carry no signal
        if q:
            s["concept_text"] = round(sum(IDF[w] for w in q & bt) / sum(IDF[w] for w in q), 3)
    if f.get("tags"):
        bt = set(b.get("match", {}).get("tags", []))
        s["tags"] = len(f["tags"] & bt) / len(f["tags"])
    if "needs" in f:
        need = b.get("match", {}).get("needs", {})
        have = f["needs"]
        ok = [1.0 if (not need.get(k) or have.get(k)) else 0.0 for k in ("speaker_footage", "screen_recordings", "broll", "brand_assets")]
        spk = 1.0 if bool(need.get("speaker_footage")) == bool(have.get("speaker_footage")) else 0.3
        s["needs_fit"] = 0.5 * spk + 0.5 * (sum(ok) / len(ok))
    if f.get("people_on_screen") is not None and fm.get("people_on_screen"):
        s["people_on_screen"] = 1.0 if f["people_on_screen"] == fm["people_on_screen"] else 0.3
    if f.get("language") and fm.get("language"):
        s["language"] = 1.0 if f["language"] == fm["language"] else (0.6 if {f["language"], fm["language"]} <= {"Hinglish", "Hindi"} else 0.2)
    if f.get("aspect") and fm.get("aspect"):
        s["aspect"] = 1.0 if f["aspect"] == fm["aspect"] else 0.3
    if f.get("duration_class") and fm.get("duration_class"):
        order = ["micro", "short", "mid", "long"]
        bd = fm["duration_class"].split(" ")[0]
        if bd in order:
            s["duration_class"] = max(0.0, 1 - 0.5 * abs(order.index(f["duration_class"]) - order.index(bd)))
    if f.get("pacing") and not f.get("is_raw_take"):        # only an edited input says anything about pacing
        p = b.get("pacing", {})
        if p.get("median_shot_s"):
            r = (f["pacing"]["median_shot_s"] + 0.3) / (p["median_shot_s"] + 0.3)
            s["pacing"] = max(0.0, 1 - abs(__import__("math").log(r)) / 1.2)
    return s


def score(f, b, W):
    cs = col_scores(f, b)
    cols = W["columns"]
    used = {k: v for k, v in cs.items() if cols.get(k, 0) > 0}
    tot = sum(cols[k] for k in used)
    base = sum(cols[k] * v for k, v in used.items()) / tot if tot else 0.0
    q = (b.get("quality_score", 3) - 3) / 2.0                    # -1 .. +1
    return round(max(0.0, min(1.0, base + W.get("quality_bonus", 0) * q)), 3), cs


# ------------------------------------------------------------------ roadmap
def fmt_items(items):
    out = []
    for it in items or []:
        if isinstance(it, dict):
            cat = ", ".join("#%s" % c for c in it.get("catalog", []) or [])
            out.append("- **%s** — %s%s%s" % (it.get("what", ""), it.get("how", ""), (" · when: " + it["when"]) if it.get("when") else "",
                                               (" · catalog " + cat) if cat else ""))
        else:
            out.append("- %s" % it)
    return out or ["- none in this blueprint"]


def roadmap(bps, f):
    L = ["# Roadmap from style blueprint%s %s" % ("s" if len(bps) > 1 else "", " + ".join(b["id"] for b in bps)), ""]
    for b in bps:
        s = b.get("signature", {})
        L += ["## %s · %s" % (b["id"], s.get("one_line", "")), "",
              "Blueprint: `%s` · format %s · %s · %s" % (b["_path"], b["format"].get("type"), b["format"].get("aspect"), b["format"].get("duration_class")), "",
              "**What makes it distinct (use these):**"] + ["- %s" % d for d in s.get("unique_devices", [])] + [""]
        L += ["### Structure", ""] + ["- %s %s-%s%% — %s" % (x.get("beat"), x.get("from_pct"), x.get("to_pct"), x.get("what")) for x in b.get("structure", [])] + [""]
        p = b.get("pacing", {})
        L += ["### Pacing", "", "- median shot %s s · %s cuts/min · visual change every ~%s s · %s wpm" % (
            p.get("median_shot_s"), p.get("cuts_per_min"), p.get("visual_change_every_s"), p.get("wpm")), ""]
        E = b.get("elements", {})
        for key, title in (("captions", "Captions"), ("background_text", "Background text / titles / cards"), ("motion_graphics", "Motion graphics"),
                           ("cards_lists", "Cards & lists"), ("silhouettes_cutouts", "Silhouettes & cut-outs"), ("broll_inserts", "B-roll & inserts"),
                           ("layout", "Layout"), ("camera", "Camera / punch-ins"), ("transitions", "Transitions"), ("end_card", "End card")):
            L += ["### %s" % title, ""] + fmt_items(E.get(key)) + [""]
        snd = b.get("sound", {})
        L += ["### Sound", "", "- music: %s" % snd.get("music")] + ["- sfx: %s" % x for x in snd.get("sfx", [])] + \
             ["- loudness target: -14 LUFS (platform), reference measured %s" % snd.get("loudness_lufs"), ""]
        st = b.get("style", {})
        L += ["### Style tokens (replace with the brand)", "", "- palette roles (defaults): %s" % json.dumps(st.get("palette_roles", {})),
              "- fonts: %s" % json.dumps(st.get("fonts", {})), ""]
        L += ["### Grade", "", "- **From this project's own footage** (video-style / grade.py), not from the blueprint. Target look: %s." % st.get("look_intent", "natural"), ""]
        L += ["### Catalog styles to cite in plan.md", ""] + ["- #%s %s — %s" % (c.get("id"), c.get("name"), c.get("role", "")) for c in b.get("catalog_styles", [])] + [""]
        L += ["### Needs", "", "- %s" % json.dumps(b.get("match", {}).get("needs", {})), "- avoid when: %s" % "; ".join(b.get("avoid_when", [])), ""]
        L += ["### Brand prompt", "", "```text", b.get("brand_prompt", ""), "```", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--video", action="append"); ap.add_argument("--image", action="append"); ap.add_argument("--concept")
    ap.add_argument("--transcript"); ap.add_argument("--tags"); ap.add_argument("--format"); ap.add_argument("--language")
    ap.add_argument("--weights", default=os.path.join(REF, "weights.json")); ap.add_argument("--top", type=int)
    ap.add_argument("--out", default="."); ap.add_argument("--pick")
    a = ap.parse_args()
    if not (a.video or a.image or a.concept or a.tags or a.transcript or a.format):
        sys.exit("give at least one of --video, --image, --concept, --transcript, --tags, --format")
    W = json.load(open(a.weights))
    bps = load_blueprints()
    build_idf(bps)
    f = analyse(a)
    ranked = sorted(((score(f, b, W), b) for b in bps), key=lambda x: -x[0][0])
    top = a.top or W.get("top_k", 5)
    thr = W.get("similar_threshold", 0.62)
    res = {"input": {k: (sorted(v) if isinstance(v, set) else v) for k, v in f.items() if k != "text"},
           "threshold": thr, "similar_found": ranked[0][0][0] >= thr,
           "matches": [{"id": b["id"], "score": sc, "similar": sc >= thr, "columns": cs, "one_line": b.get("signature", {}).get("one_line"),
                        "format": b.get("format"), "path": b["_path"]} for (sc, cs), b in ranked[:top]]}
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(os.path.join(a.out, "matches.json"), "w"), indent=1)
    for m in res["matches"]:
        print("%s %.2f %s  %s" % (m["id"], m["score"], "SIMILAR" if m["similar"] else "       ", m["one_line"]))
    print("similar_found: %s (threshold %.2f) -> %s" % (res["similar_found"], thr, os.path.join(a.out, "matches.json")))
    if a.pick:
        chosen = [b for b in bps if b["id"] in a.pick.split(",")]
        if not chosen:
            sys.exit("unknown blueprint id(s): %s" % a.pick)
        p = os.path.join(a.out, "ROADMAP.md")
        open(p, "w").write(roadmap(chosen, f))
        print("roadmap ->", p)


if __name__ == "__main__":
    main()
