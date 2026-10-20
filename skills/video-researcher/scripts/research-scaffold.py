#!/usr/bin/env python3
"""research-scaffold.py: Scaffolds research workspace, extracts entities & metrics dynamically,"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# Standard English stop words to filter false positive proper nouns
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your",
    "yours", "yourself", "yourselves", "okay", "right", "wait", "look", "listen", "actually",
    "basically", "literally", "totally", "really", "already", "always", "never", "sometimes",
    "hello", "hey", "today", "tomorrow", "yesterday", "first", "second", "third", "one", "two"
}

CATEGORY_SIGNATURES = {
    "Tech & AI SaaS": ["ai", "model", "llm", "software", "api", "database", "backend", "cloud", "saas", "app", "gpu", "neural"],
    "Coding & Developer Tools": ["code", "coding", "developer", "function", "javascript", "python", "typescript", "git", "terminal", "bug", "syntax"],
    "Business, Finance & D2C": ["revenue", "profit", "crore", "dollar", "valuation", "customer", "sales", "brand", "marketing", "founder", "startup", "investor"],
    "Educational & Science Explainers": ["physics", "math", "history", "science", "formula", "experiment", "brain", "universe", "theory", "why", "study"],
    "Productivity & Self-Improvement": ["habit", "routine", "focus", "book", "discipline", "notion", "adhd", "work", "morning", "time", "reading"],
    "D2C, Fashion & E-Commerce": ["haul", "unboxing", "review", "price", "amazon", "fabric", "wear", "shoes", "quality", "outfit", "brand"],
    "Fitness & Health": ["workout", "muscle", "diet", "protein", "training", "fat", "gym", "body", "health", "sleep", "recovery"],
    "Commentary & Pop Culture": ["trend", "drama", "creator", "youtube", "tiktok", "news", "viral", "exposed", "internet", "story"]
}


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def extract_colors_from_svg(svg_path: Path) -> dict[str, str | None]:
    if not svg_path.exists():
        return {"primary": None, "accent": None}

    try:
        content = svg_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"primary": None, "accent": None}

    # Extract all hex codes
    hex_candidates = re.findall(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b', content)
    
    # Extract rgb(r,g,b)
    rgb_candidates = re.findall(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', content)
    for r, g, b in rgb_candidates:
        hex_candidates.append(f"#{int(r):02x}{int(g):02x}{int(b):02x}")

    # Standardize and filter out pure white, pure black, and subtle transparent grays
    filtered_colors: list[str] = []
    for h in hex_candidates:
        if len(h) == 4:
            h = f"#{h[1]*2}{h[2]*2}{h[3]*2}"
        h_upper = h.upper()
        # Filter neutral black/white/transparent extremes
        if h_upper in {"#FFFFFF", "#000000", "#111111", "#222222", "#EEEEEE", "#F0F0F0"}:
            continue
        filtered_colors.append(h_upper)

    if not filtered_colors:
        return {"primary": None, "accent": None}

    # Count occurrences to find dominant colors
    from collections import Counter
    counts = Counter(filtered_colors)
    most_common = [c for c, _ in counts.most_common(2)]

    primary = most_common[0] if len(most_common) > 0 else None
    accent = most_common[1] if len(most_common) > 1 else None
    return {"primary": primary, "accent": accent}


def extract_colors_from_image(image_path: Path) -> dict[str, str | None]:
    if not image_path.exists():
        return {"primary": None, "accent": None}

    try:
        from PIL import Image
        import numpy as np

        im = Image.open(image_path).convert("RGBA")
        im.thumbnail((120, 120))
        data = np.array(im)
        
        # Only inspect non-transparent pixels
        alpha = data[:, :, 3]
        opaque = data[alpha > 128][:, :3]
        if len(opaque) == 0:
            return {"primary": None, "accent": None}

        # Filter out near-black (mean < 30) and near-white (mean > 235)
        means = opaque.mean(axis=1)
        valid = opaque[(means > 35) & (means < 235)]
        if len(valid) == 0:
            valid = opaque

        # Simple color quantization
        valid = (valid // 32) * 32
        unique, counts = np.unique(valid, axis=0, return_counts=True)
        sorted_indices = np.argsort(-counts)

        primary = None
        accent = None
        if len(sorted_indices) > 0:
            c1 = unique[sorted_indices[0]]
            primary = f"#{c1[0]:02X}{c1[1]:02X}{c1[2]:02X}"
        if len(sorted_indices) > 1:
            c2 = unique[sorted_indices[1]]
            accent = f"#{c2[0]:02X}{c2[1]:02X}{c2[2]:02X}"

        return {"primary": primary, "accent": accent}
    except Exception:
        return {"primary": None, "accent": None}


def extract_dynamic_entities(text: str) -> list[str]:
    found = set()

    # 1. Domain names and web handles (e.g., github.com, supabase.io, v0.dev)
    domains = re.findall(r'\b[a-zA-Z0-9\-]+\.(?:com|org|ai|io|dev|app|net|co|in|so)\b', text, re.IGNORECASE)
    for d in domains:
        name = d.split('.')[0]
        if len(name) > 1:
            found.add(name.capitalize())

    # 2. PascalCase / camelCase tokens (e.g. Next.js, TensorFlow, whisperCpp, ChatGPT)
    pascal = re.findall(r'\b[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)+\b', text)
    for p in pascal:
        if not re.match(r'^\d', p) and len(p) > 2:
            found.add(p)

    camel = re.findall(r'\b[a-z]+[A-Z0-9][a-zA-Z0-9]*\b', text)
    for c in camel:
        if c.lower() not in STOPWORDS and len(c) > 2:
            found.add(c)

    # 3. Uppercase acronyms (e.g. AWS, GCP, LLM, API, D2C, SaaS, SDK, UI)
    acronyms = re.findall(r'\b[A-Z]{2,6}\b', text)
    for a in acronyms:
        if a.lower() not in STOPWORDS and a not in {"THE", "AND", "FOR", "NOT", "BUT", "ALL", "NOW", "YES"}:
            found.add(a)

    # 4. Multi-word and single-word Proper Nouns (Capitalized words not at sentence boundaries or recurring)
    # Match capitalized phrases: e.g. "Linear", "Supabase", "Raj Shamani"
    capitalized_words = re.findall(r'\b[A-Z][a-z0-9_\-]{2,25}\b', text)
    from collections import Counter
    word_counts = Counter(capitalized_words)

    for word, count in word_counts.items():
        w_lower = word.lower()
        if w_lower in STOPWORDS:
            continue
        # If it appears more than once or is longer than 3 characters
        if count >= 1 and len(word) >= 3:
            found.add(word)

    # Clean and deduplicate (avoid substring redundancy)
    sorted_entities = sorted(list(found), key=lambda x: (len(x), x))
    filtered = []
    for e in sorted_entities:
        if not any(e.lower() != o.lower() and e.lower() in o.lower() for o in sorted_entities):
            filtered.append(e)

    return sorted(filtered, key=lambda x: text.find(x) if text.find(x) != -1 else 9999)[:20]


def extract_dynamic_metrics(text: str) -> list[str]:
    pattern = re.compile(
        r'(?:'
        r'[\$₹€£]\s*[0-9]+(?:[\.,][0-9]+)?(?:\s*(?:k|m|b|crore|lakh|billion|million|trillion))?'
        r'|[0-9]+(?:[\.,][0-9]+)?%'
        r'|[0-9]+(?:\.[0-9]+)?\s*x\b'
        r'|[0-9]+(?:[\.,][0-9]+)?\s*(?:seconds|minutes|hours|days|weeks|months|years|fps|users|downloads|subscribers|views|stars)'
        r')',
        re.IGNORECASE
    )
    matches = pattern.findall(text)
    seen = set()
    deduped = []
    for m in matches:
        clean = m.strip()
        if clean.lower() not in seen:
            seen.add(clean.lower())
            deduped.append(clean)
    return deduped[:15]


def infer_dynamic_category(text: str) -> str | None:
    text_lower = text.lower()
    scores: dict[str, int] = {}
    for category, keywords in CATEGORY_SIGNATURES.items():
        score = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))
        if score > 0:
            scores[category] = score

    if not scores:
        return None
    return max(scores, key=lambda k: scores[k])


def resolve_logo_asset(entity: str, slug: str, logos_dir: Path) -> dict:
    svg_path = logos_dir / f"{slug}.svg"
    png_path = logos_dir / f"{slug}.png"

    # 1. Existing local files
    if svg_path.exists():
        colors = extract_colors_from_svg(svg_path)
        return {
            "entity_name": entity,
            "slug": slug,
            "status": "resolved",
            "local_path": str(svg_path),
            "format": "svg",
            "brand_colors": colors
        }
    if png_path.exists():
        colors = extract_colors_from_image(png_path)
        return {
            "entity_name": entity,
            "slug": slug,
            "status": "resolved",
            "local_path": str(png_path),
            "format": "png",
            "brand_colors": colors
        }

    # 2. Dynamic CDN lookup via SimpleIcons (clean slug without special chars)
    clean_slug = re.sub(r'[^a-z0-9]', '', slug)
    if clean_slug:
        cdn_url = f"https://cdn.simpleicons.org/{clean_slug}"
        try:
            req = urllib.request.Request(cdn_url, headers={'User-Agent': 'AntigravityVideoResearcher/1.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    content = resp.read()
                    if b"<svg" in content:
                        svg_path.write_bytes(content)
                        colors = extract_colors_from_svg(svg_path)
                        return {
                            "entity_name": entity,
                            "slug": slug,
                            "status": "resolved",
                            "local_path": str(svg_path),
                            "source_url": cdn_url,
                            "format": "svg",
                            "brand_colors": colors
                        }
        except Exception:
            pass

    # 3. Unresolved: return clean record with None colors (no hardcoded fake values)
    return {
        "entity_name": entity,
        "slug": slug,
        "status": "missing",
        "local_path": str(svg_path),
        "source_url": None,
        "format": "svg",
        "brand_colors": {"primary": None, "accent": None}
    }


def parse_transcript_content(path_or_str: str) -> tuple[str, list[dict]]:
    p = Path(path_or_str)
    if not p.exists():
        return path_or_str, []

    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        words: list[str] = []
        timed_words: list[dict] = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "text" in item:
                    words.append(item["text"])
                    timed_words.append(item)
                elif isinstance(item, str):
                    words.append(item)
        elif isinstance(data, dict):
            if "words" in data and isinstance(data["words"], list):
                for item in data["words"]:
                    if isinstance(item, dict) and "text" in item:
                        words.append(item["text"])
                        timed_words.append(item)
            elif "text" in data and isinstance(data["text"], str):
                words = data["text"].split()
        return " ".join(words), timed_words
    except Exception:
        content = p.read_text(encoding="utf-8", errors="ignore")
        return content, []


def main():
    parser = argparse.ArgumentParser(description="Dynamically scaffold video research schema without hardcoded values.")
    parser.add_argument("--project", "-p", required=True, help="Path to project directory (e.g. videos/my-project)")
    parser.add_argument("--transcript", "-t", help="Path to transcript.json or transcript-raw.json")
    parser.add_argument("--topic", help="Topic or script outline text")
    parser.add_argument("--platform", default=None, choices=["reels", "shorts", "tiktok", "youtube_longform"])
    parser.add_argument("--genre", default=None, help="Explicit genre override (if omitted, inferred dynamically)")
    parser.add_argument("--aspect-ratio", default=None, choices=["9:16", "16:9", "1:1", "4:5"])
    args = parser.parse_args()

    project_dir = Path(args.project).resolve()
    logos_dir = project_dir / "assets" / "logos"
    logos_dir.mkdir(parents=True, exist_ok=True)

    full_text = ""
    if args.transcript:
        full_text, _ = parse_transcript_content(args.transcript)
    elif args.topic:
        full_text = args.topic

    # Dynamic extraction
    entities = extract_dynamic_entities(full_text) if full_text else []
    metrics = extract_dynamic_metrics(full_text) if full_text else []
    inferred_genre = args.genre or infer_dynamic_category(full_text) or "Unclassified"

    # Target platform and aspect ratio
    platform = args.platform or ("reels" if "reel" in project_dir.name.lower() or "short" in project_dir.name.lower() else "reels")
    aspect_ratio = args.aspect_ratio or ("9:16" if platform in ["reels", "shorts", "tiktok"] else "16:9")

    # Resolve logos dynamically without fake colors
    resolved_entities = []
    for entity in entities:
        slug = slugify(entity)
        if not slug:
            continue
        res = resolve_logo_asset(entity, slug, logos_dir)
        resolved_entities.append(res)

    project_name = project_dir.name
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Dynamic verified data points from transcript (no fake URLs or placeholder claims)
    initial_data_points = []
    for m in metrics:
        initial_data_points.append({
            "claim": f"Mentioned in transcript: {m}",
            "verified_value": m,
            "source_url": None,
            "confidence": "unconfirmed"
        })

    # Scaffold research.json: ONLY verified or null fields (NO hardcoded fake URLs or mock benchmarks)
    research_json_data = {
        "project_id": project_name,
        "timestamp": now_iso,
        "category": {
            "primary_genre": inferred_genre,
            "niche": None,
            "target_audience": None,
            "tone": None
        },
        "target_platform": platform,
        "aspect_ratio": aspect_ratio,
        "topic_analysis": {
            "summary": full_text[:400].strip() if full_text else "",
            "core_claims": [],
            "verified_data_points": initial_data_points,
            "key_takeaways": []
        },
        "entities_and_logos": resolved_entities,
        # Strictly empty until the researcher agent executes real search_web queries:
        "trending_benchmarks": [],
        "recommended_format": None,
        "recommended_style": None,
        "suggested_catalog_blocks": [],
        "actionable_links": []
    }

    out_json_path = project_dir / "research.json"
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(research_json_data, f, indent=2)

    # Scaffold clean research.md
    md_content = f"""# Creative & Market Research Brief: {project_name}

**Category:** {inferred_genre} · **Target Platform:** {platform.capitalize()} · **Aspect Ratio:** {aspect_ratio}
**Research Timestamp:** {now_iso} · **Status:** Scaffolding complete; awaiting agent live research pass

---

## 1. Executive Topic Summary & Verified Data
{research_json_data['topic_analysis']['summary'] if research_json_data['topic_analysis']['summary'] else "_Pending transcript analysis and topic research._"}

### Metrics & Data Points Found in Transcript
"""
    if initial_data_points:
        for dp in initial_data_points:
            md_content += f"- **{dp['verified_value']}**: `{dp['claim']}` (Verification pending)\n"
    else:
        md_content += "_No quantitative metrics detected in transcript._\n"

    md_content += """
---

## 2. Trending Category Benchmarks & Reference Videos
_To be populated by video-researcher via live search_web queries. No placeholder URLs are permitted._

| Creator / Channel | Video Title & Link | Views | Cut Pace | Winning Hook / Technique |
|---|---|---|---|---|
| _Pending live search_ | _Pending live search_ | _Pending_ | _Pending_ | _Pending_ |

---

## 3. Brand & Entity Assets (Resolved & Generated Logos)
All brands and tools identified in the transcript with vector assets saved to `assets/logos/`:

| Entity | Status | Format | Brand Colors | Local Asset Path | Source |
|---|---|---|---|---|---|
"""
    if resolved_entities:
        for e in resolved_entities:
            c_str = f"P: {e['brand_colors']['primary']}, A: {e['brand_colors']['accent']}" if e['brand_colors']['primary'] else "Pending extraction"
            source_str = f"[Link]({e['source_url']})" if e.get('source_url') else "Local / Search needed"
            md_content += f"| **{e['entity_name']}** | `{e['status'].upper()}` | {e['format']} | `{c_str}` | `{e['local_path']}` | {source_str} |\n"
    else:
        md_content += "| _None detected_ | - | - | - | - | - |\n"

    md_content += """
---

## 4. Recommended Visual Layout & Master Style Direction
_Awaiting video-researcher synthesis against `video-plan-storyboard/references/style-catalog.md` based on active category benchmarks._

- **Primary Layout:** _Pending agent analysis_
- **Color Theme:** _Pending extraction from verified logo assets & brand requirements_
- **Typography Pairing:** _Pending niche benchmark match_
- **Motion Physics:** _Pending niche benchmark match_

---

## 5. HyperFrames Catalog Action Plan
_Awaiting narrative beat mapping._

---

## 6. Actionable Reference Links & Source Repository
_To be populated with real, verified citations from the research pass._

---

### Creator Verification (Gate 0)
_Review the research plan once populated with live internet findings. Downstream agents proceed to **Gate 1 (`video-plan-storyboard`)** only after approval._
"""

    out_md_path = project_dir / "research.md"
    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    resolved_count = sum(1 for e in resolved_entities if e["status"] == "resolved")
    print(f"Scaffolded research workspace in {project_dir}:")
    print(f"  - Config: {out_json_path}")
    print(f"  - Brief: {out_md_path}")
    print(f"  - Category inferred: {inferred_genre}")
    print(f"  - Dynamic entities extracted: {len(entities)}")
    print(f"  - Logos resolved: {resolved_count}/{len(entities)}")


if __name__ == "__main__":
    main()
