#!/usr/bin/env python3
"""Evidence collection and review packet generation for the video pipeline."""
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


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
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
            page_width, page_height = page.get_size()
            largest_side = max(page_width, page_height)
            scale = min(0.55, 1200 / largest_side) if largest_side > 0 else 0.55
            bitmap = page.render(scale=scale)
            preview = bitmap.to_pil().convert("RGB").copy()
            bitmap.close()
            page.close()
            preview.thumbnail((340, 440), resampling)
            thumbnails.append((page_index + 1, preview))

    sheet_path = review_dir / f"{stem}-pages.jpg"
    if thumbnails:
        cell_width, cell_height, columns = 380, 490, 3
        rows = (len(thumbnails) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), "#e9edf2")
        draw = ImageDraw.Draw(sheet)
        for item, (page_number, preview) in enumerate(thumbnails):
            x = (item % columns) * cell_width
            y = (item // columns) * cell_height
            draw.text((x + 12, y + 8), f"Page {page_number}", fill="#17212b")
            left = x + (cell_width - preview.width) // 2
            sheet.paste(preview, (left, y + 38))
        sheet.save(sheet_path, quality=88)

    return {"pages": len(reader.pages), "preview_pages": [index + 1 for index in page_indexes],
            "text_snapshot": str(text_path),
            "visual_contact_sheet": str(sheet_path) if thumbnails else None,
            "extraction_status": "text_extracted" if extracted else "no_selectable_text"}


def _project_references(project_root: Path, explicit_refs: list[str] | None, source_video: str) -> list[Path]:
    refs = [Path(p).expanduser().resolve() for p in (explicit_refs or [])]
    missing = [str(path) for path in refs if not path.is_file()]
    if missing:
        raise RuntimeError("Explicit reference file(s) not found: " + ", ".join(missing))
    supported = VIDEO_SUFFIXES | IMAGE_SUFFIXES | PDF_SUFFIXES
    unsupported = [str(path) for path in refs if path.is_file() and path.suffix.lower() not in supported]
    if unsupported:
        raise RuntimeError("Unsupported reference file type(s): " + ", ".join(unsupported))
    ref_dir = project_root / "references"
    if ref_dir.is_dir():
        refs.extend(p.resolve() for p in ref_dir.rglob("*")
                    if p.is_file() and p.suffix.lower() in supported
                    and not any(part.startswith(".") for part in p.relative_to(ref_dir).parts))
    source = Path(source_video).resolve()
    result, seen = [], set()
    for path in refs:
        key = str(path)
        if key not in seen and path.is_file() and path.resolve() != source:
            seen.add(key)
            result.append(path)
    return result


def _brand_inputs(project_root: Path, work_dir: Path) -> list[dict]:
    candidates = []
    brand_dir = project_root / "brand"
    if brand_dir.is_dir():
        candidates.extend(path for path in brand_dir.rglob("*") if path.is_file()
                          and not any(part.startswith(".") or part in {"node_modules", "__pycache__"}
                                      for part in path.relative_to(brand_dir).parts)
                          and path.suffix.lower() in BRAND_TEXT_SUFFIXES | BRAND_ASSET_SUFFIXES)
    root_brand_names = {"memo.md", "brand.md", "style-guide.md", "brand-guide.md", "brand-style-guide.md",
                        "style-guide.txt", "brand-style-guide.pdf", "brand-guide.pdf",
                        "logo.svg", "logo.png", "logo.jpg", "logo.jpeg", "logo.webp"}
    candidates.extend(path for path in project_root.iterdir() if path.is_file()
                      and (path.name.lower() in root_brand_names
                           or (path.suffix.lower() == ".pdf" and
                               any(word in path.stem.lower() for word in ("brand", "style", "guide")))
                           or (path.suffix.lower() in IMAGE_SUFFIXES | {".svg"} and
                               any(word in path.stem.lower() for word in ("brand", "logo")))))

    entries, seen = [], set()
    for path in sorted(candidates, key=lambda item: str(item).lower()):
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if path.is_relative_to(brand_dir):
            relative = Path("source") / path.relative_to(brand_dir)
        else:
            relative = Path("source") / path.name
        dst = work_dir / "context" / "brand" / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dst)
        entry = {"source": str(resolved), "snapshot": str(dst), "sha256": _hash_file(path),
                 "kind": "document" if path.suffix.lower() in BRAND_TEXT_SUFFIXES | PDF_SUFFIXES else "visual_asset"}
        suffix = path.suffix.lower()
        if suffix in BRAND_TEXT_SUFFIXES:
            entry["text_snapshot"] = str(dst)
        elif suffix in PDF_SUFFIXES:
            try:
                entry.update(_pdf_review(path, dst.parent, dst.name))
            except Exception as exc:
                raise RuntimeError(f"Could not read brand guide PDF {path}: {exc}") from exc
        elif suffix in IMAGE_SUFFIXES:
            try:
                from PIL import Image
                with Image.open(path) as image:
                    entry.update({"dimensions": list(image.size), "mode": image.mode})
            except Exception as exc:
                raise RuntimeError(f"Could not read brand image asset {path}: {exc}") from exc
        entries.append(entry)
    return entries


def _transcript_evidence(words: list[dict]) -> list[dict]:
    segments, current = [], []
    for word in words:
        try:
            start, end = float(word.get("start", 0)), float(word.get("end", 0))
        except (TypeError, ValueError):
            continue
        if end <= start:
            continue
        if current and (start - float(current[-1]["end"]) > 1.25 or start - float(current[0]["start"]) > 12):
            segments.append(current)
            current = []
        current.append({"start": start, "end": end, "text": str(word.get("text") or word.get("w") or "").strip()})
    if current:
        segments.append(current)
    return [{"id": f"speech-{i + 1:03d}", "start": round(seg[0]["start"], 3),
             "end": round(seg[-1]["end"], 3), "text": " ".join(w["text"] for w in seg).strip()}
            for i, seg in enumerate(segments) if any(w["text"] for w in seg)]


def synthesize_storyboard_and_cuts(raw_video: str, project_dir: str, meta: dict,
                                  audio_res: dict, visual_res: dict,
                                  ref_inputs: list[str] | None = None, prompt: str = "") -> dict:
    import time
    t0 = time.time()
    out_dir = Path(project_dir).resolve()
    project_root = out_dir.parent if out_dir.name == ".video-pipeline" else out_dir
    transcript_path = Path(audio_res["transcript_path"])
    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    words = transcript.get("words", [])
    duration = float(meta["duration"])

    # Keep the full source as the active cut until the user approves specific removals.
    full_cut = {"source_duration": duration, "kept_seconds": round(duration, 3),
                "kept": [{"start": 0.0, "end": round(duration, 3)}], "removed": [],
                "status": "awaiting_user_cut_review"}
    (out_dir / "cut-list.json").write_text(json.dumps(full_cut, indent=2), encoding="utf-8")
    proposal_dir = out_dir / "cut-proposal"
    proposal_dir.mkdir(parents=True, exist_ok=True)
    if words:
        print("  [Synthesis] Creating a transcript cut proposal; full source remains active pending review...")
        subprocess.run([sys.executable, str(Path(__file__).with_name("paper-cut.py")),
                        "--transcript", str(transcript_path), "--duration", str(duration),
                        "--out-dir", str(proposal_dir), "--tight"], check=True)
        cut_proposal = json.loads((proposal_dir / "cut-list.json").read_text(encoding="utf-8"))
    else:
        cut_proposal = {**full_cut, "status": "no_recognized_dialogue_full_picture_preserved"}
    (out_dir / "cut-proposal.json").write_text(json.dumps(cut_proposal, indent=2), encoding="utf-8")
    (out_dir / "PAPER-CUT.md").write_text(
        "# Cut proposal\n\n"
        f"Source duration: {duration:.2f}s. Active cut: full source preserved.\n\n"
        "A transcript-based proposal is available in `cut-proposal.json`. It has not been applied.\n",
        encoding="utf-8")

    source_path = str(meta.get("source_video", raw_video))
    references = _project_references(project_root, ref_inputs, source_path)
    refs_dir = out_dir / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)
    reference_records = []
    watch_script = Path(__file__).with_name("watch.py")
    for index, ref in enumerate(references, start=1):
        suffix = ref.suffix.lower()
        kind = "video" if suffix in VIDEO_SUFFIXES else ("pdf" if suffix in PDF_SUFFIXES else "image")
        record = {"id": f"reference-{index:02d}", "path": str(ref), "sha256": _hash_file(ref),
                  "kind": kind}
        ref_out = refs_dir / record["id"]
        ref_out.mkdir(parents=True, exist_ok=True)
        if kind == "video":
            cmd = [sys.executable, str(watch_script), "ref", str(ref), "--intent",
                   "Visual direction reference only; do not treat this as source footage.",
                   "--out-dir", str(ref_out), "--fresh", "--no-transcript", "--no-hook", "--max-frames", "48"]
            run = subprocess.run(cmd, capture_output=True, text=True)
            if run.returncode:
                error = (run.stderr or run.stdout).strip()[-1200:]
                raise RuntimeError(f"Could not analyze supplied reference {ref.name}: {error}")
            record.update({"analysis_dir": str(ref_out), "analysis_status": "complete"})
        elif kind == "image":
            try:
                from PIL import Image
                with Image.open(ref) as img:
                    record.update({"dimensions": list(img.size), "mode": img.mode,
                                   "analysis_status": "image_available_for_visual_review"})
            except Exception as exc:
                raise RuntimeError(f"Could not read supplied reference image {ref}: {exc}")
        else:
            try:
                snapshot = ref_out / ref.name
                shutil.copyfile(ref, snapshot)
                pdf_review = _pdf_review(ref, ref_out, ref.stem)
                record.update({"snapshot": str(snapshot), **pdf_review,
                               "analysis_status": pdf_review["extraction_status"]})
            except Exception as exc:
                raise RuntimeError(f"Could not read PDF reference {ref}: {exc}") from exc
        reference_records.append(record)
    (refs_dir / "reference-index.json").write_text(json.dumps(reference_records, indent=2), encoding="utf-8")

    brand_records = _brand_inputs(project_root, out_dir)
    brand_index = out_dir / "context" / "brand-inputs.json"
    brand_index.parent.mkdir(parents=True, exist_ok=True)
    brand_index.write_text(json.dumps(brand_records, indent=2), encoding="utf-8")

    # Source-only matching prevents reference footage from overwriting source properties.
    matched_presets = []
    match_script = Path(__file__).parents[3] / "video-reference-match" / "scripts" / "match.py"
    if not match_script.is_file():
        raise RuntimeError(f"Bundled style matcher is missing: {match_script}")
    match_dir = out_dir / "reference-match"
    subprocess.run([sys.executable, str(match_script), "--video", raw_video, "--transcript",
                    str(transcript_path), "--top", "5", "--out", str(match_dir)], check=True)
    matches_json = match_dir / "matches.json"
    if not matches_json.is_file():
        raise RuntimeError("Style matcher completed without writing reference-match/matches.json.")
    matched_presets = json.loads(matches_json.read_text(encoding="utf-8")).get("matches", [])

    visual_evidence = [{**item, "frame": os.path.relpath(item["frame"], out_dir)}
                       for item in visual_res.get("evidence_frames", [])]
    source_evidence = {
        "schema": "video-source-evidence/1",
        "source": {"path": source_path, "analysis_video": raw_video, "duration": duration,
                   "width": meta["width"], "height": meta["height"], "fps": meta["fps"]},
        "visual_samples": visual_evidence,
        "detected_shots": visual_res.get("detected_shots", []),
        "speech_segments": _transcript_evidence(words),
        "limitations": ["Scene detection marks visual change, not semantic events.",
                        "Speech is ASR output and must be checked against audio before quoting.",
                        "A frame sample alone does not establish a product feature, claim, or user intent."]
    }
    (out_dir / "source-evidence.json").write_text(json.dumps(source_evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    storyboard_plan = {"schema": "video-storyboard-plan/2", "id": project_root.name,
                       "source_evidence": "source-evidence.json",
                       "source_evidence_sha256": _hash_file(out_dir / "source-evidence.json"), "duration": duration,
                       "source_canvas": [meta["width"], meta["height"]], "beats": [],
                       "status": "needs_user_direction_and_source-grounded_storyboard"}
    plan_path = out_dir / "storyboard.plan.json"
    plan_path.write_text(json.dumps(storyboard_plan, indent=2), encoding="utf-8")

    dyn_color = visual_res.get("dyn_color", {})
    style_template = {
        "color_grade": "dynamic", "dynamic_color_params": dyn_color.get("params", {}),
        "fonts": {
            "display": {"family": "Poppins", "files": {
                "700": "@engine/assets/fonts/poppins/Poppins-Bold.ttf",
                "800": "@engine/assets/fonts/poppins/Poppins-ExtraBold.ttf"}},
            "body": {"family": "Inter", "files": {
                "100 900": "@engine/assets/fonts/inter/Inter-Variable.ttf"}},
            "captions": {"family": "Google Sans", "files": {
                "700": "@engine/assets/fonts/google-sans/GoogleSans-700-latin.woff2"}}
        },
        "captions": {"family": "Google Sans", "mode": "phrase", "y": visual_res["caption_y"], "size": 0.064,
                     "landscape": {"size": 0.036}, "weight": 700, "max_words": 3, "color": "#ffffff",
                     "active_color": "#ffe600", "emphasis_color": "#ffe600", "inactive_color": "#ffffff",
                     "plate_color": "rgba(8,10,14,.38)", "plate_border": "rgba(255,255,255,.09)",
                     "padding_x": 0.30, "padding_y": 0.12, "plate_radius": 0.24, "shadow": "none"},
        "brand_inputs": [os.path.relpath(x["snapshot"], out_dir) for x in brand_records],
        "status": "draft; apply brand requirements and approved user direction before assembly"
    }
    (out_dir / "style-template.json").write_text(json.dumps(style_template, indent=2), encoding="utf-8")

    question_path = out_dir / "QUESTIONNAIRE.md"
    question_path.write_text("\n".join([
        "# Direction questions", "",
        "Ask only what the user's brief and brand guide have not already answered. Bundle into one concise interaction.", "",
        "1. Which footage must stay, and what can be cut? The full picture is preserved until approved.",
        "2. What platform/aspect ratio should the export use? Recommend source framing when unspecified.",
        "3. Should supplied references lead, should the user choose an indexed style match, or should the direction be original and footage-led?",
        "4. Which framing fits the actual shots: preserve full frame, reframe, or a specifically requested split/PiP treatment?",
        "5. Keep the current simple phrase captions, use another treatment, or turn captions off?",
        "6. For noise, choose denoise level (off/auto/light/medium/strong); keep original sound only or add supplied/licensed music/SFX? Dereverb is set to strong as requested.", "",
        "Do not infer a product story or remove visual-only footage because speech is absent."
    ]) + "\n", encoding="utf-8")

    (out_dir / "meta.json").write_text(json.dumps({**meta, "raw_video": raw_video,
        "source_video": source_path, "project_root": str(project_root), "workspace": str(out_dir)}, indent=2), encoding="utf-8")
    gate_data = {"plan": {"status": "waiting", "reason": "new analysis requires a new creative review"}}
    (out_dir / "gates.json").write_text(json.dumps(gate_data, indent=2), encoding="utf-8")
    try:
        source_ref = os.path.relpath(source_path, project_root)
        if source_ref.startswith(".."):
            source_ref = source_path
    except ValueError:
        source_ref = source_path
    project_state = {
        "schema": "video-pipeline-project/1", "project": project_root.name,
        "creative_brief": prompt,
        "source": {"path": source_ref, "analysis_copy": "raw/standard-input.mp4",
                   "duration": duration, "width": meta["width"], "height": meta["height"], "fps": meta["fps"]},
        "workspace": ".video-pipeline", "exports": "Exports/",
        "steps": {"analysis": {"status": "done", "outputs": ["source-evidence.json", "STORYBOARD.md"]},
                  "direction": {"status": "waiting", "outputs": ["resolved-spec.json", "storyboard.json", "style.json"]},
                  "assembly": {"status": "todo"}},
        "gates": {"plan": {"status": "waiting"}}
    }
    (out_dir / "project.json").write_text(json.dumps(project_state, indent=2), encoding="utf-8")

    ref_lines = []
    for record in reference_records:
        line = f"- `{record['path']}` ({record['kind']}; {record['analysis_status']})"
        if record.get("text_snapshot"):
            line += f" · extracted text: `{os.path.relpath(record['text_snapshot'], out_dir)}`"
        if record.get("visual_contact_sheet"):
            line += f" · page previews: `{os.path.relpath(record['visual_contact_sheet'], out_dir)}`"
        if record.get("pages") is not None:
            line += f" · {record['pages']} pages"
        if record.get("preview_pages"):
            line += " · visual preview pages " + ", ".join(str(number) for number in record["preview_pages"])
        ref_lines.append(line)
    brand_lines = []
    for record in brand_records:
        line = f"- `{record['source']}` (snapshot: `{os.path.relpath(record['snapshot'], out_dir)}`)"
        if record.get("text_snapshot") and record["text_snapshot"] != record["snapshot"]:
            line += f" · extracted text: `{os.path.relpath(record['text_snapshot'], out_dir)}`"
        if record.get("visual_contact_sheet"):
            line += f" · page previews: `{os.path.relpath(record['visual_contact_sheet'], out_dir)}`"
        if record.get("extraction_status"):
            line += f" · {record['extraction_status']}"
        if record.get("preview_pages"):
            line += " · visual preview pages " + ", ".join(str(number) for number in record["preview_pages"])
        brand_lines.append(line)
    match_lines = [f"- {m.get('id')}: {m.get('one_line', '')} (score {m.get('score', 0):.2f})" for m in matched_presets[:5]]
    contact_sheet = visual_res.get("contact_sheet_path")
    contact_rel = os.path.relpath(contact_sheet, out_dir) if contact_sheet else None
    md = [f"# Source review · {project_root.name}", "",
          "Analysis is complete. No narrative beats, product claims, CTA, layout or sound effects have been invented.", "",
          "## Source", "", f"- Duration: {duration:.2f}s · {meta['width']}×{meta['height']} · {meta['fps']} fps",
          f"- Recognized words: {audio_res['words_count']}",
          f"- Working cut: full source preserved · proposed removals: {len(cut_proposal.get('removed', []))} (not applied)",
          "- Evidence: `source-evidence.json` · storyboard scaffold: `storyboard.plan.json`", "",
          "## Visual evidence", "",
          f"![Timestamped source contact sheet]({contact_rel})" if contact_rel else "Contact sheet unavailable; see `source-evidence.json` for individual frames.", "",
          f"Detected {len(visual_res.get('detected_shots', []))} shot ranges. Scene detection identifies visual changes only; inspect frames before naming events or designing graphics.", "",
          "## References", "", *(ref_lines or ["No project references found in this folder's `references/` directory."]), "",
          "Video reference footage is analyzed separately from source footage.", "",
          "## Brand guidance", "", *(brand_lines or ["No recognized brand guide or brand asset was found in the project folder."]), "",
          "Read each listed text snapshot and inspect every listed visual asset before choosing colors, fonts, logos, or graphic tone. Brand rules constrain the selected reference direction.", "",
          "## Indexed style candidates", "", *(match_lines or ["No candidates were returned; inspect the index status in `reference-match/matches.json`."]), "",
          "These are suggestions only; do not apply one without user direction.", "",
          "## Review files", "", "- `QUESTIONNAIRE.md` — ask only unanswered direction questions.",
          "- `cut-proposal.json` — optional dialogue-led cut suggestion; not active.",
          "- `style-template.json` — current simple caption defaults and measured grade; apply brand rules before approval.",
          "- `source-evidence.json` — source-linked IDs required by every storyboard beat.", "",
          "Every proposed beat must cite one or more `visual_samples` or `speech_segments` IDs. If no source moment supports it, omit it. For product and visual-only footage, preserve the full picture unless the user approves specific removals."]
    storyboard_md = out_dir / "STORYBOARD.md"
    storyboard_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"  [Synthesis] Source evidence and review packet written to {storyboard_md}")
    return {"storyboard_md": str(storyboard_md), "storyboard_json": str(plan_path),
            "kept_duration": duration, "dropped_duration": 0.0, "elapsed": time.time() - t0}
