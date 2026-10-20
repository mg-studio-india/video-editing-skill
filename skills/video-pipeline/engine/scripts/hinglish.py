"""hinglish.py: Transliterates Devanagari Hindi text to Roman Hinglish."""
from __future__ import annotations

import re
from typing import Any

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

# Common spoken Hindi / Hinglish vocabulary dictionary for natural creator-standard spelling
COMMON_WORDS: dict[str, str] = {
    # Pronouns & demonstratives
    "यह": "yeh", "वह": "woh", "ये": "ye", "वो": "wo", "इस": "is", "उस": "us",
    "इन": "in", "उन": "un", "इसे": "ise", "उसे": "use", "इन्हें": "inhein", "उन्हें": "unhein",
    "मेरा": "mera", "मेरी": "meri", "मेरे": "mere", "हमारा": "hamara", "हमारी": "hamari", "हमारे": "hamare",
    "तुम्हारा": "tumhara", "तुम्हारी": "tumhari", "तुम्हारे": "tumhare", "आपका": "aapka", "आपकी": "aapki", "आपके": "aapke",
    "अपना": "apna", "अपनी": "apni", "अपने": "apne", "कोई": "koi", "कुछ": "kuch", "सब": "sab", "सभी": "sabhi",
    
    # Auxiliary verbs & tenses
    "है": "hai", "हैं": "hain", "था": "tha", "थी": "thi", "थे": "the",
    "हो": "ho", "हूं": "hoon", "हूँ": "hoon", "होगा": "hoga", "होगी": "hogi", "होंगे": "honge",
    "रहा": "raha", "रही": "rahi", "रहे": "rahe", "हुआ": "hua", "हुई": "hui", "हुए": "hue",

    # Interrogatives & conjunctions
    "क्या": "kya", "क्यों": "kyun", "कैसे": "kaise", "कैसा": "kaisa", "कैसी": "kaisi",
    "कहाँ": "kahan", "कहा": "kaha", "यहाँ": "yahan", "वहाँ": "wahan", "कब": "kab", "जब": "jab", "तब": "tab",
    "अगर": "agar", "मगर": "magar", "लेकिन": "lekin", "पर": "par", "और": "aur", "या": "ya",
    "भी": "bhi", "तो": "to", "नहीं": "nahi", "मत": "mat", "सिर्फ": "sirf", "सिर्फ़": "sirf",

    # Business, Finance & Numerics
    "करोड़": "crore", "करोड़": "crore", "लाख": "lakh", "हज़ार": "hazaar", "हजार": "hazaar", "सौ": "sau",
    "रुपये": "rupaye", "रुपया": "rupaya", "रुपए": "rupaye", "पैसा": "paisa", "पैसे": "paise",
    "मार्केट": "market", "बिजनेस": "business", "कंपनी": "company", "स्टार्टअप": "startup",
    "प्रोडक्ट": "product", "कस्टमर": "customer", "प्रॉफिट": "profit", "लॉस": "loss", "इन्वेस्टर": "investor",
    "फंडिंग": "funding", "शेयर": "share", "स्टॉक": "stock", "ग्रोथ": "growth", "सेल्स": "sales",

    # Common nouns & adjectives
    "भारत": "bharat", "इंडिया": "india", "देश": "desh", "गाड़ी": "gaadi", "गाड़ी": "gaadi", "कार": "car",
    "लोग": "log", "लोगों": "logon", "काम": "kaam", "बात": "baat", "बातों": "baaton", "समय": "samay", "वक्त": "waqt",
    "अच्छा": "achha", "अच्छी": "achhi", "अच्छे": "achhe", "बुरा": "bura", "बुरी": "buri", "बुरे": "bure",
    "बड़ा": "bada", "बड़ी": "badi", "बड़े": "bade", "छोटा": "chhota", "छोटी": "chhoti", "छोटे": "chhote",
    "नया": "naya", "नई": "nayi", "नए": "naye", "पुराना": "purana", "पहला": "pehla", "पहली": "pehli", "पहले": "pehle",
    "आज": "aaj", "कल": "kal", "अब": "ab", "बहुत": "bahut", "ज्यादा": "zyada", "कम": "kam",

    # Common verbs
    "करना": "karna", "कर": "kar", "करता": "karta", "करती": "karti", "करते": "karte", "किया": "kiya", "किए": "kiye", "की": "ki",
    "होना": "hona", "सकता": "sakta", "सकती": "sakti", "सकते": "sakte", "चाहिए": "chahiye",
    "देना": "dena", "दिया": "diya", "दिए": "diye", "लेना": "lena", "लिया": "liya", "लिए": "liye",
    "बोलना": "bolna", "बोला": "bola", "कहना": "kahna", "कहा": "kaha", "देखना": "dekhna", "देखा": "dekha",
    "सुनना": "sunna", "सुना": "suna", "जाना": "jaana", "गया": "gaya", "गई": "gayi", "गए": "gaye",
    "आना": "aana", "आया": "aaya", "आई": "aayi", "आए": "aaye", "चलना": "chalna", "चला": "chala",
    "बताओ": "batao", "समझो": "samjho", "सोचो": "socho", "फास्ट": "fast", "स्पीड": "speed"
}

VOWELS: dict[str, str] = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo",
    "ऋ": "ri", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au",
    "अं": "an", "अः": "ah", "ऑ": "o", "ऍ": "e"
}

MATRAS: dict[str, str] = {
    "ा": "a", "ि": "i", "ी": "ee", "ु": "u", "ू": "oo",
    "ृ": "ri", "े": "e", "ै": "ai", "ो": "o", "ौ": "au",
    "ॅ": "e", "ॉ": "o"
}

CONSONANTS: dict[str, str] = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ng",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "ny",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
    "क़": "q", "ख़": "kh", "ग़": "gh", "ज़": "z", "ड़": "d", "ढ़": "dh", "फ़": "f"
}

NUKTA_MAP: dict[str, str] = {
    "क": "क़", "ख": "ख़", "ग": "ग़", "ज": "ज़", "ड": "ड़", "ढ": "ढ़", "फ": "फ़"
}

SIGNS: dict[str, str] = {
    "ं": "n", "ँ": "n", "ः": "h"
}


def has_devanagari(text: str) -> bool:
    return bool(DEVANAGARI_RE.search(text))


def transliterate_token(token: str) -> str:
    if not has_devanagari(token):
        return token

    # Extract leading and trailing punctuation
    prefix_match = re.match(r"^[^\u0900-\u097f\w]+", token)
    suffix_match = re.search(r"[^\u0900-\u097f\w]+$", token)
    prefix = prefix_match.group(0) if prefix_match else ""
    suffix = suffix_match.group(0) if suffix_match else ""
    
    # Strip affixes for lookup
    core = token[len(prefix):len(token) - len(suffix)] if suffix else token[len(prefix):]
    
    # Replace Devanagari danda in suffix
    suffix = suffix.replace("।", ".").replace("॥", ".")
    prefix = prefix.replace("।", ".").replace("॥", ".")

    if not core:
        return prefix + suffix

    # Check common vocabulary dictionary
    if core in COMMON_WORDS:
        res = COMMON_WORDS[core]
        if token and token[0].isupper():
            res = res.capitalize()
        return prefix + res + suffix

    # Normalize nukta combinations
    chars: list[str] = []
    i = 0
    core_len = len(core)
    while i < core_len:
        c = core[i]
        if i + 1 < core_len and core[i + 1] == "़":
            chars.append(NUKTA_MAP.get(c, c))
            i += 2
        else:
            chars.append(c)
            i += 1

    out: list[str] = []
    n = len(chars)
    for idx, ch in enumerate(chars):
        next_ch = chars[idx + 1] if idx + 1 < n else None
        
        if ch in VOWELS:
            out.append(VOWELS[ch])
        elif ch in CONSONANTS:
            base = CONSONANTS[ch]
            out.append(base)
            # Apply vowel or schwa
            if next_ch == "्":
                pass  # Halant suppresses inherent vowel
            elif next_ch in MATRAS:
                pass  # Matra takes precedence over inherent vowel
            elif next_ch in VOWELS:
                pass
            elif next_ch is None or (next_ch not in CONSONANTS and next_ch not in SIGNS):
                # Word-final consonant: schwa deletion in modern Hindi (e.g. Bharat, not Bharata)
                pass
            elif next_ch in CONSONANTS:
                # Medial consonant: check if followed by consonant + matra (e.g. karna -> kar-na)
                next_next_ch = chars[idx + 2] if idx + 2 < n else None
                if next_next_ch in MATRAS:
                    pass  # Schwa deletion
                else:
                    out.append("a")
            elif next_ch in SIGNS:
                out.append("a")
        elif ch in MATRAS:
            out.append(MATRAS[ch])
        elif ch in SIGNS:
            out.append(SIGNS[ch])
        elif ch == "्":
            pass
        elif ch == "।":
            out.append(".")
        else:
            out.append(ch)

    res = "".join(out)
    return prefix + res + suffix


def to_hinglish(text: str) -> str:
    if not text or not has_devanagari(text):
        return text.replace("।", ".")

    # Split by whitespace while preserving delimiters
    tokens = re.split(r"(\s+)", text)
    result = []
    for token in tokens:
        if has_devanagari(token):
            result.append(transliterate_token(token))
        else:
            result.append(token.replace("।", "."))
    return "".join(result)


def clean_transcript_words(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned = []
    for w in words:
        item = dict(w)
        if "text" in item and has_devanagari(str(item["text"])):
            item["text"] = to_hinglish(str(item["text"]))
        if "w" in item and has_devanagari(str(item["w"])):
            item["w"] = to_hinglish(str(item["w"]))
        cleaned.append(item)
    return cleaned


def clean_transcript(data: dict[str, Any]) -> dict[str, Any]:
    out = dict(data)
    if "text" in out and isinstance(out["text"], str):
        out["text"] = to_hinglish(out["text"])

    if "words" in out and isinstance(out["words"], list):
        out["words"] = clean_transcript_words(out["words"])

    if "cues" in out and isinstance(out["cues"], list):
        new_cues = []
        for c in out["cues"]:
            cue = dict(c)
            if "text" in cue:
                cue["text"] = to_hinglish(str(cue["text"]))
            new_cues.append(cue)
        out["cues"] = new_cues

    if "segments" in out and isinstance(out["segments"], list):
        new_segs = []
        for s in out["segments"]:
            seg = dict(s)
            if "text" in seg:
                seg["text"] = to_hinglish(str(seg["text"]))
            new_segs.append(seg)
        out["segments"] = new_segs

    if "sound_cues" in out and isinstance(out["sound_cues"], list):
        new_cues = []
        for c in out["sound_cues"]:
            cue = dict(c)
            if "text" in cue:
                cue["text"] = to_hinglish(str(cue["text"]))
            new_cues.append(cue)
        out["sound_cues"] = new_cues

    # Mark transcript language as Hinglish if it was Hindi
    if out.get("language") == "hi":
        out["language"] = "hi-Latn"
    if out.get("lang") == "hi":
        out["lang"] = "hi-Latn"
    out["script"] = "hinglish"
    return out
