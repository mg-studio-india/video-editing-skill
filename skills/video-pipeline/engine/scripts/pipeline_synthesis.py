#!/usr/bin/env python3
"""pipeline_synthesis.py: source evidence, references, brand inputs and the review packet (REVIEW.md).

Everything here is measured or copied from the user's own files. Nothing is filled in from defaults: there is no
brand memo or style-guide template, and legacy MEMO.md / STYLE-GUIDE.md scaffolds are ignored by name.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mxf"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
PDF_SUFFIXES = {".pdf"}
BRAND_TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml"}
BRAND_ASSET_SUFFIXES = IMAGE_SUFFIXES | PDF_SUFFIXES | {".svg"}
# Old installs copied template files into every workspace; they describe nobody's brand, so they are never read.
IGNORED_BRAND_FILES = {"memo.md", "style-guide.md", "style_guide.md", "styleguide.md"}

SKILLS_DIR = Path(__file__).resolve().parents[3]
STYLES_DIR = SKILLS_DIR / "video-style" / "styles"


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pdf_review(pdf_path: Path, review_dir: Path, stem: str) -> dict:
    from pypdf import PdfReader
    import pypdfium2 as pdfium
    from PIL import Image, ImageDraw

    review_dir.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(str(pdf_path))
    extracted = "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()
    text_path = review_dir / f"{stem}.txt"
    text_path.write_text(extracted, encoding="utf-8")
    thumbnails = []
    with pdfium.PdfDocument(str(pdf_path)) as document:
        page_count = len(document)
        sample_count = min(page_count, 12)
        page_indexes = sorted({round(i * (page_count - 1) / max(sample_count - 1, 1))
                               for i in range(sample_count)}) if page_count else []
        resampling = getattr(Image, "Resampling", Image).LANCZOS
        for page_index in page_indexes:
            page = document[page_index]
            pw, ph = page.get_size()
            scale = min(0.55, 1200 / max(pw, ph)) if max(pw, ph) > 0 else 0.55
            bitmap = page.render(scale=scale)
            preview = bitmap.to_pil().convert("RGB").copy()
            bitmap.close()
            page.close()
            preview.thumbnail((340, 440), resampling)
            thumbnails.append((page_index + 1, preview))
    sheet_path = review_dir / f"{stem}-pages.jpg"
    if thumbnails:
        cw, ch, columns = 380, 490, 3
        rows = (len(thumbnails) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * cw, rows * ch), "#e9edf2")
        draw = ImageDraw.Draw(sheet)
        for item, (number, preview) in enumerate(thumbnails):
            x, y = (item % columns) * cw, (item // columns) * ch
            draw.text((x + 12, y + 8), f"Page {number}", fill="#17212b")
            sheet.paste(preview, (x + (cw - preview.width) // 2, y + 38))
        sheet.save(sheet_path, quality=88)
    return {"pages": len(reader.pages), "text_snapshot": str(text_path),
            "visual_contact_sheet": str(sheet_path) if thumbnails else None,
            "extraction_status": "text_extracted" if extracted else "no_selectable_text"}


# ---------------------------------------------------------------- references and brand
def collect_references(project_root: Path, explicit: list[str] | None, source_video: str, work: Path) -> list[dict]:
    refs = [Path(p).expanduser().resolve() for p in (explicit or [])]
    missing = [str(p) for p in refs if not p.is_file()]
    if missing:
        raise RuntimeError("Reference file(s) not found: " + ", ".join(missing))
    supported = VIDEO_SUFFIXES | IMAGE_SUFFIXES | PDF_SUFFIXES
    ref_dir = project_root / "references"
    if ref_dir.is_dir():
        refs.extend(p.resolve() for p in sorted(ref_dir.rglob("*"))
                    if p.is_file() and p.suffix.lower() in supported
                    and not any(part.startswith(".") for part in p.relative_to(ref_dir).parts))
    source = Path(source_video).resolve()
    out_dir = work / "references"
    out_dir.mkdir(parents=True, exist_ok=True)
    records, seen = [], set()
    watch = Path(__file__).with_name("watch.py")
    for ref in refs:
        if str(ref) in seen or ref == source:
            continue
        seen.add(str(ref))
        kind = "video" if ref.suffix.lower() in VIDEO_SUFFIXES else ("pdf" if ref.suffix.lower() in PDF_SUFFIXES else "image")
        rec = {"id": "reference-%02d" % (len(records) + 1), "path": str(ref), "sha256": hash_file(ref), "kind": kind}
        rdir = out_dir / rec["id"]
        rdir.mkdir(parents=True, exist_ok=True)
        if kind == "video":
            run = subprocess.run([sys.executable, str(watch), "ref", str(ref), "--intent",
                                  "Visual direction reference only; not source footage.", "--out-dir", str(rdir),
                                  "--fresh", "--no-transcript", "--no-hook", "--max-frames", "48"],
                                 capture_output=True, text=True)
            if run.returncode:
                raise RuntimeError("Could not analyse reference %s: %s" % (ref.name, (run.stderr or run.stdout)[-1200:]))
            rec.update({"analysis_dir": str(rdir), "status": "analysed (fill storyboard.md with video-watch)"})
        elif kind == "image":
            from PIL import Image
            with Image.open(ref) as img:
                rec.update({"dimensions": list(img.size), "status": "image; inspect it directly"})
        else:
            shutil.copyfile(ref, rdir / ref.name)
            rec.update({**_pdf_review(ref, rdir, ref.stem), "status": "pdf text extracted"})
        records.append(rec)
    (out_dir / "reference-index.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    return records


def find_brand_dir(project_root: Path) -> Path:
    """The project's own brand/ folder, else the workspace's (videos/<name> -> videos -> workspace)."""
    for base in [project_root, *list(project_root.parents)[:2]]:
        cand = base / "brand"
        if cand.is_dir() and any(p.is_file() and p.name.lower() not in IGNORED_BRAND_FILES and not p.name.startswith(".")
                                 for p in cand.rglob("*")):
            return cand
    return project_root / "brand"


def collect_brand(project_root: Path, work: Path) -> list[dict]:
    brand_dir = find_brand_dir(project_root)
    candidates = []
    if brand_dir.is_dir():
        candidates = [p for p in sorted(brand_dir.rglob("*")) if p.is_file()
                      and not any(part.startswith(".") for part in p.relative_to(brand_dir).parts)
                      and p.suffix.lower() in BRAND_TEXT_SUFFIXES | BRAND_ASSET_SUFFIXES
                      and p.name.lower() not in IGNORED_BRAND_FILES]
    entries = []
    for path in candidates:
        dst = work / "context" / "brand" / path.relative_to(brand_dir)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dst)
        entry = {"source": str(path.resolve()), "snapshot": str(dst), "sha256": hash_file(path),
                 "kind": "document" if path.suffix.lower() in BRAND_TEXT_SUFFIXES | PDF_SUFFIXES else "asset"}
        if path.suffix.lower() in PDF_SUFFIXES:
            entry.update(_pdf_review(path, dst.parent, dst.name))
        elif path.suffix.lower() in IMAGE_SUFFIXES:
            from PIL import Image
            with Image.open(path) as image:
                entry["dimensions"] = list(image.size)
        entries.append(entry)
    out = work / "context" / "brand-inputs.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    return entries


# ---------------------------------------------------------------- evidence
def speech_segments(words: list[dict]) -> list[dict]:
    segments, cur = [], []
    for w in words:
        s, e = float(w["start"]), float(w["end"])
        if cur and (s - float(cur[-1]["end"]) > 1.0 or s - float(cur[0]["start"]) > 10):
            segments.append(cur)
            cur = []
        cur.append(w)
    if cur:
        segments.append(cur)
    return [{"id": "speech-%03d" % (i + 1), "start": round(float(seg[0]["start"]), 3), "end": round(float(seg[-1]["end"]), 3),
             "text": " ".join(str(w.get("text") or w.get("w") or "") for w in seg).strip()}
            for i, seg in enumerate(segments)]


def to_flat(t: float, cut_map: dict) -> float | None:
    for seg in cut_map.get("segments", []):
        if seg["src_start"] - 1e-6 <= t <= seg["src_end"] + 1e-6:
            return round(seg["flat_start"] + (t - seg["src_start"]), 3)
    return None


def write_evidence(work: Path, meta: dict, flat_words: list[dict], visual: dict, cut_map: dict) -> dict:
    samples = []
    for item in visual.get("evidence_frames", []):
        samples.append({"id": item["id"], "source_time": item["timestamp"], "flat_time": to_flat(item["timestamp"], cut_map),
                        "shot": [item["shot_start"], item["shot_end"]], "frame": os.path.relpath(item["frame"], work)})
    evidence = {
        "schema": "video-source-evidence/2",
        "timeline": "flat (the active cut, including the end tail); source times are kept for frames",
        "source": {"path": meta["source_video"], "duration": meta["duration"], "width": meta["width"],
                   "height": meta["height"], "fps": meta["fps"]},
        "flat_duration": cut_map["flat_duration"], "content_duration": cut_map["content_duration"],
        "tail": cut_map["tail"],
        "speech_segments": speech_segments(flat_words),
        "visual_samples": samples,
        "detected_shots": visual.get("detected_shots", []),
        "notes": ["Speech segments use the flat (cut) timeline that captions and beats use.",
                  "A visual sample with flat_time null was cut out of the edit.",
                  "Scene detection marks visual change, not meaning; look at the frames."],
    }
    (work / "source-evidence.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    return evidence


# ---------------------------------------------------------------- styles and catalog
def default_styles() -> list[dict]:
    out = []
    for path in sorted(STYLES_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        out.append({"name": data.get("name", path.stem), "file": str(path), "summary": data.get("summary", "")})
    return out


def catalog_status(engine_dir: Path) -> dict:
    configured = os.environ.get("VIDEO_COMPOSITIONS", "").strip()
    comp_dir = Path(configured).expanduser() if configured else engine_dir / "compositions"
    index = comp_dir / "catalog.json"
    if not index.is_file():
        return {"index": str(index), "ok": False, "count": 0,
                "fix": "run: \"$PY\" \"$ENG/scripts/catalog.py\" build   (or video-skills setup)"}
    try:
        count = len(json.loads(index.read_text(encoding="utf-8")).get("items", []))
    except ValueError:
        count = 0
    return {"index": str(index), "ok": count > 0, "count": count}


# ---------------------------------------------------------------- review packet
def write_review(work: Path, project_root: Path, meta: dict, prompt: str, audio_report: dict, transcript: dict,
                 cut: dict, cut_map: dict, visual: dict, references: list[dict], brand: list[dict],
                 catalog: dict, ab_preview: str | None) -> Path:
    rel = lambda p: os.path.relpath(str(p), work) if p else "(missing)"
    words = transcript.get("words", [])
    sample = " ".join(str(w.get("text") or w.get("w")) for w in words[:60])
    b, a = audio_report.get("before", {}), audio_report.get("after", {})
    dn = audio_report.get("denoise")
    denoise_label = dn.get("label", "on") if isinstance(dn, dict) else (dn or "off")
    removed = [r for r in cut.get("removed", []) if not str(r.get("reason", "")).startswith("pause")]
    pauses = [r for r in cut.get("removed", []) if str(r.get("reason", "")).startswith("pause")]
    styles = default_styles()
    md = [f"# Review packet · {project_root.name}", "",
          f"Brief: {prompt or '(none given)'}", "",
          "## Source", "",
          f"- {meta['duration']:.2f}s · {meta['width']}×{meta['height']} · {meta['fps']} fps (constant frame rate copy)",
          f"- Contact sheet: `{rel(visual.get('contact_sheet_path'))}` · grade preview: `{rel(visual.get('grade_preview_path'))}`",
          "", "## Audio (pass 1 done: dereverb + DeepFilterNet, once)", "",
          f"- Noise floor {b.get('noise_floor_db')} → {a.get('noise_floor_db')} dB · SNR {b.get('snr_db')} → {a.get('snr_db')} dB"
          f" · denoise: {denoise_label}"
          f" · alignment correction {audio_report.get('lag_corrected_ms', 0)} ms",
          f"- Listen before approving: `{rel(ab_preview)}` (original, short gap, then the same lines cleaned)",
          "- Pass 2 (polish + loudness) runs once at render, on the voice only.",
          "", "## Transcript (Hinglish, Roman script)", "",
          f"- {len(words)} words · timing: {transcript.get('timing')} · model: {transcript.get('model')}"
          f" · removed as silent: {len(transcript.get('dropped_no_speech', []))}",
          f"- Opening: “{sample}…”",
          "- Fix misheard names with verify-words.py; corrections persist across re-runs.",
          "", "## Cut (active, tight, word-safe)", "",
          f"- {cut_map['content_duration']:.2f}s kept of {meta['duration']:.2f}s · {len(cut_map.get('segments', []))} segments"
          f" · + {cut_map['tail']:.2f}s tail with fade to black · total {cut_map['flat_duration']:.2f}s",
          f"- Removed: {len(removed)} ranges (retakes, restarts, fillers) · pauses shortened: {len(pauses)}",
          f"- Details: `CUT.md` · preview the cut: `hyperframes/input-video.mp4`",
          "", "## Style (choose one; nothing is applied until chosen)", ""]
    md += [f"- **{s['name']}**: {s['summary']}" for s in styles] or ["- (no default styles found)"]
    md += ["", "## HyperFrames catalog", "",
           (f"- {catalog['count']} blocks/components indexed at `{catalog['index']}` — search it before building anything custom."
            if catalog["ok"] else f"- Catalog index missing: {catalog.get('fix')}"),
           "", "## References", ""]
    md += [f"- {r['id']}: `{r['path']}` ({r['kind']}; {r['status']})" for r in references] or ["- None in `references/`."]
    md += ["", "## Brand", ""]
    md += [f"- `{e['source']}` ({e['kind']})" for e in brand] or ["- None in `brand/`. Use the chosen default style; do not invent brand rules."]
    md += ["", "## Next", "",
           "1. Research the topic (video-researcher) → `research/research.json` with sourced facts, graphics, sounds, b-roll.",
           "2. Draft `storyboard.json` (catalog blocks first) and `style.json` from the chosen style.",
           "3. Ask only what is still open: platform/aspect, style, cut OK?, captions, music.",
           "4. Present one review (this packet + storyboard), get approval, then `approve` and `assemble`."]
    path = work / "REVIEW.md"
    path.write_text("\n".join(md) + "\n", encoding="utf-8")
    return path
