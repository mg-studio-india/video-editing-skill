#!/usr/bin/env python3
"""verify-words.py: Audit, verify, and correct mis-spelled or misheard words in transcripts."""
import argparse
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))


def _engine_scripts():
    env = os.environ.get("VIDEO_ENGINE")
    for c in ((os.path.join(env, "scripts") if env else ""), os.path.join(HERE, "..", "..", "video-pipeline", "engine", "scripts"),
              os.path.expanduser("~/.agents/skills/video-pipeline/engine/scripts")):
        if c and os.path.isfile(os.path.join(c, "runtime.py")):
            return os.path.abspath(c)
    raise SystemExit("video-pipeline engine not found: set VIDEO_ENGINE or install the skills side by side")


ENG = _engine_scripts()
sys.path.insert(0, ENG)
import runtime
runtime.ensure_project_venv()
import hinglish
import importlib.util

def _load_fw():
    spec = importlib.util.spec_from_file_location("fix_words", os.path.join(ENG, "fix-words.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

FW = _load_fw()

# High-confidence common phonetic and syllable-split fixes for Hinglish / Indian speech in Whisper
COMMON_HINGLISH_CORRECTIONS: dict[str, str] = {
    # Split auxiliary verb compounds
    "ho ga": "hoga",
    "ho gi": "hogi",
    "ho ge": "hoge",
    "ho li": "hongi",
    "kar ke": "karke",
    "dekh ke": "dekhke",
    "samajh ke": "samajhke",
    "jaan ke": "jaanke",
    "keh ke": "kehke",
    "bol ke": "bolke",

    # Common phonetic distortions in Whisper
    "sochow": "socho",
    "bade ho jai": "badi ho jaye",
    "bade jai": "badh jaye",
    "bech pa da": "bech paata",
    "bêch pa da": "bech paata",
    "one capuchin piece": "One cappuccino please",
    "one capuchin case": "One cappuccino please",
    "one capuchin": "one cappuccino",
    "hamaro": "hamara",
    "saktah": "sakta hai",
    "tuk": "tak",
    "wajahe": "wajah",
    "waze": "wajah",
    "siraf": "sirf",
    "nuxan": "nuksan",
    "nuqsaan": "nuksan",
    "fayta": "fayda",
    "faayta": "fayda",
    "rupi": "rupee",
    "vahin": "wahi",
    "laak": "lakh",
    "laag": "lakh",
    "carod": "crore",
    "corod": "crore",
    "per lena": "kar lena",
    "par lena": "kar lena",
    "rivinyo": "revenue",
    "rivinyon": "revenue",
    "bild karta": "build karta",
    "kise bejna": "kise bechna",
    "kya bejna": "kya bechna",
    "tumhen bejna": "tumhen bechna",
    "shoing d testimoriyals": "showing the testimonials",
    "testimoriyals": "testimonials",
    "phrom agar klaints": "from our clients",
    "agar klaints": "our clients",
    "yor previyas vark": "your previous work",
    "previyas vark": "previous work",
    "end projekt": "and project",
    "kolej projekt": "college project",
    "thainks hui beldar": "things we build",
}


def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def audit_transcript(words: list[dict]) -> list[dict]:
    candidates = []
    n = len(words)
    i = 0
    while i < n:
        w_cur = words[i].get("w") or words[i].get("text") or ""
        clean_cur = re.sub(r"[^\w']+", "", w_cur).lower()

        # Check 2-word and 3-word split phrases against COMMON_HINGLISH_CORRECTIONS
        matched_phrase = False
        for span_len in (3, 2):
            if i + span_len <= n:
                span_words = [words[i + k].get("w") or words[i + k].get("text") or "" for k in range(span_len)]
                span_clean = " ".join(re.sub(r"[^\w']+", "", w).lower() for w in span_words)
                if span_clean in COMMON_HINGLISH_CORRECTIONS:
                    s_orig = " ".join(span_words)
                    s_corr = COMMON_HINGLISH_CORRECTIONS[span_clean]
                    candidates.append({
                        "start": words[i]["start"],
                        "end": words[i + span_len - 1]["end"],
                        "original": s_orig,
                        "suggested": s_corr,
                        "reason": f"Common phonetic phrase split/mishearing ('{span_clean}')"
                    })
                    i += span_len
                    matched_phrase = True
                    break

        if matched_phrase:
            continue

        # Check single word against dictionary
        if clean_cur in COMMON_HINGLISH_CORRECTIONS:
            s_corr = COMMON_HINGLISH_CORRECTIONS[clean_cur]
            # Match title case if original was capitalized
            if w_cur and w_cur[0].isupper():
                s_corr = s_corr.capitalize()
            candidates.append({
                "start": words[i]["start"],
                "end": words[i]["end"],
                "original": w_cur,
                "suggested": s_corr,
                "reason": f"Known phonetic mishearing ('{clean_cur}')"
            })
            i += 1
            continue

        # Check for un-normalized diacritics / non-ASCII characters (e.g., 'bêch' -> 'bech')
        no_accents = strip_accents(w_cur)
        if no_accents != w_cur:
            candidates.append({
                "start": words[i]["start"],
                "end": words[i]["end"],
                "original": w_cur,
                "suggested": no_accents,
                "reason": "Unwanted diacritic / accent mark"
            })
            i += 1
            continue

        # Check for Devanagari characters leakage
        if hinglish.has_devanagari(w_cur):
            candidates.append({
                "start": words[i]["start"],
                "end": words[i]["end"],
                "original": w_cur,
                "suggested": hinglish.to_hinglish(w_cur),
                "reason": "Devanagari script character detected"
            })
            i += 1
            continue

        i += 1

    return candidates


def apply_candidates(transcript_path: str, candidates: list[dict], corrections_path: str) -> int:
    corr = FW.load_corrections(corrections_path)
    for c in candidates:
        orig = re.sub(r"[^\w\s']+", "", c["original"]).strip().lower()
        corr[orig] = c["suggested"]

    os.makedirs(os.path.dirname(os.path.abspath(corrections_path)), exist_ok=True)
    with open(corrections_path, "w", encoding="utf-8") as f:
        json.dump(corr, f, indent=1, ensure_ascii=False)

    t = json.load(open(transcript_path, encoding="utf-8"))
    words = t.get("words", []) if isinstance(t, dict) else t
    new_words, changes = FW.apply(words, corr)
    if isinstance(t, dict):
        t["words"] = new_words
        t["corrections_applied"] = len(changes)
        t = hinglish.clean_transcript(t)
    else:
        t = new_words

    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(t, f, indent=1, ensure_ascii=False)

    return len(changes)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--transcript", required=True, help="Path to transcript.json")
    ap.add_argument("--corrections", help="Path to corrections.json (default: next to transcript)")
    ap.add_argument("--auto-fix", action="store_true", help="Automatically apply suggested fixes")
    ap.add_argument("--add", action="append", default=[], help="Add manual correction 'misheard=Correct'")
    ap.add_argument("--force", action="store_true", help="Force re-audit even if already verified")
    a = ap.parse_args()

    cpath = a.corrections or os.path.join(os.path.dirname(os.path.abspath(a.transcript)), "corrections.json")
    t_path = os.path.abspath(a.transcript)
    if not os.path.isfile(t_path):
        sys.exit(f"Transcript file not found: {t_path}")

    data = json.load(open(t_path, encoding="utf-8"))
    words = data.get("words", []) if isinstance(data, dict) else data

    # Caching check: Skip if already verified and corrections.json exists, unless --force or --add
    if not a.force and not a.add and os.path.isfile(cpath) and data.get("words_verified", False):
        print(f"✓ Words already verified: {os.path.basename(t_path)} (cached in {os.path.basename(cpath)}, use --force to re-audit)")
        return

    # 1. Manual additions if specified
    if a.add:
        corr = FW.load_corrections(cpath)
        for spec in a.add:
            if "=" not in spec:
                sys.exit(f"--add requires 'misheard=Correct', got {spec!r}")
            k, v = spec.split("=", 1)
            corr[k.strip().lower()] = v.strip()
        with open(cpath, "w", encoding="utf-8") as f:
            json.dump(corr, f, indent=1, ensure_ascii=False)
        print(f"Added {len(a.add)} manual correction(s) to {cpath}")
        words, changes = FW.apply(words, corr)
        data["words"] = words
        data["corrections_applied"] = len(changes)
        with open(t_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
        print(f"Applied {len(changes)} total correction(s) in place to {t_path}")
        return

    # 2. Audit transcript
    candidates = audit_transcript(words)
    print(f"\nWord Verification Report for {os.path.basename(t_path)}:")
    print(f"Total words: {len(words)} | Suspect items flagged: {len(candidates)}")
    print("-" * 80)
    for c in candidates:
        print(f"[{c['start']:6.2f}s - {c['end']:6.2f}s] {c['original']:<25} -> {c['suggested']:<25} ({c['reason']})")
    print("-" * 80)

    if not candidates:
        print("All words verified cleanly. No common phonetic distortions found.")
        return

    if a.auto_fix:
        num_applied = apply_candidates(t_path, candidates, cpath)
        print(f"\nAuto-applied {num_applied} correction(s) to {t_path} and saved to {cpath}.")
    else:
        print("\nRun with --auto-fix to apply these corrections, or add custom ones via:")
        print(f'  python3 verify-words.py --transcript {t_path} --add "misheard=Correct"')


if __name__ == "__main__":
    main()
