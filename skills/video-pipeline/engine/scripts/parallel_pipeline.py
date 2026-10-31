#!/usr/bin/env python3
"""Project-scoped video pipeline with evidence collection, approval gates and HyperFrames assembly."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
from html.parser import HTMLParser
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runtime
runtime.ensure_project_venv()
import grade
import transcribe_cpp


def probe_video(video_path: str) -> dict:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=codec_type,width,height,r_frame_rate,duration,codec_name,pix_fmt:format=duration,size,bit_rate",
        "-of", "json", video_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)
    v_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    fmt = data.get("format", {})
    
    fps_raw = v_stream.get("r_frame_rate", "30/1")
    try:
        num, den = map(int, fps_raw.split("/"))
        fps = round(num / den, 2) if den else 30.0
    except Exception:
        fps = 30.0

    dur = float(fmt.get("duration") or v_stream.get("duration") or 0.0)
    w = int(v_stream.get("width") or 1080)
    h = int(v_stream.get("height") or 1920)
    
    return {
        "width": w,
        "height": h,
        "fps": fps,
        "duration": dur,
        "pix_fmt": v_stream.get("pix_fmt", "yuv420p"),
        "bitrate": int(fmt.get("bit_rate") or 0)
    }


def standardize_video(input_video: str, project_dir: str) -> str:
    p_dir = Path(project_dir)
    raw_dir = p_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    standard_out = raw_dir / "standard-input.mp4"
    source = Path(input_video).resolve()
    source_stat = source.stat()
    signature = {"path": str(source), "size": source_stat.st_size, "mtime_ns": source_stat.st_mtime_ns}
    signature_path = raw_dir / "standard-input.source.json"
    try:
        cached_signature = json.loads(signature_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cached_signature = None
    if standard_out.exists() and standard_out.stat().st_size > 100000 and cached_signature == signature:
        print(f"  [Standard Ingest] Reusing existing standardized SDR H.265 video: {standard_out}")
        return str(standard_out)

    probe_cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,color_transfer,color_primaries,pix_fmt",
        "-of", "json", input_video
    ]
    try:
        r = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        data = json.loads(r.stdout)
        s = data.get("streams", [{}])[0]
        codec = s.get("codec_name", "").lower()
        trc = s.get("color_transfer", "").lower()
        pri = s.get("color_primaries", "").lower()
        pix_fmt = s.get("pix_fmt", "").lower()
    except Exception:
        codec, trc, pri, pix_fmt = "", "", "", ""

    is_hdr = "arib-std-b67" in trc or "bt2020" in pri or "smpte2084" in trc or "10le" in pix_fmt
    is_h265 = codec in ("hevc", "h265")

    if not is_hdr and is_h265 and pix_fmt == "yuv420p" and "bt709" in pri:
        print(f"  [Standard Ingest] Input video is already standard SDR BT.709 and H.265.")
        if Path(input_video).resolve() != standard_out.resolve():
            shutil.copyfile(input_video, standard_out)
        signature_path.write_text(json.dumps(signature, indent=2), encoding="utf-8")
        return str(standard_out)

    print(f"  [Standard Ingest] Converting raw footage to standard SDR BT.709 and H.265 (HEVC)...")
    t0 = time.time()
    vf = "colorspace=all=bt709:iprimaries=bt2020:ispace=bt2020nc:itrc=bt2020-10:format=yuv420p" if is_hdr else "format=yuv420p"
    conv_cmd = [
        "ffmpeg", "-y", "-i", input_video,
        "-vf", vf,
        "-c:v", "libx265", "-crf", "18", "-preset", "fast", "-tag:v", "hvc1",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
        "-c:a", "aac", "-b:a", "256k",
        str(standard_out)
    ]
    subprocess.run(conv_cmd, check=True)
    signature_path.write_text(json.dumps(signature, indent=2), encoding="utf-8")
    dur = time.time() - t0
    print(f"  [Standard Ingest] Standard SDR H.265 video ready in {dur:.2f}s -> {standard_out}")
    return str(standard_out)


# -----------------------------------------------------------------------------
# Worker A: Audio Track (strong dereverb, denoise, level, acoustic silence, Whisper ASR)
# -----------------------------------------------------------------------------
def process_audio_worker(raw_video: str, project_dir: str) -> dict:
    t0 = time.time()
    out_dir = Path(project_dir)
    audio_dir = out_dir / "audio_processing"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    norm_wav = audio_dir / "audio-norm-16k.wav"
    clean_wav = out_dir / "audio-clean.wav"
    transcript_json = out_dir / "transcript.json"

    audio_probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0",
                                  "-show_entries", "stream=index", "-of", "json", raw_video],
                                 capture_output=True, text=True, check=True)
    has_audio = bool(json.loads(audio_probe.stdout).get("streams"))
    if has_audio:
        # WPE uses the source's stereo channels before the stronger mono late-reverb pass.
        # This cleaned picture copy becomes the edit source, so the same voice reaches ASR and render.
        print("  [Audio Worker] Applying WPE and strong late-reverb reduction before transcription...")
        clean_video = audio_dir / "audio-cleaned.mp4"
        voice_clean = Path(HERE).parents[2] / "video-audio" / "tools" / "voice-clean.py"
        if not voice_clean.is_file():
            raise RuntimeError(f"WPE voice-clean stage is missing: {voice_clean}")
        subprocess.run([sys.executable, str(voice_clean), raw_video, "--video", raw_video,
                        "--out", str(clean_video), "--keep", str(out_dir / "scratch" / "voice-clean"),
                        "--no-deep-filter"], check=True)
        extract_clean = ["ffmpeg", "-y", "-v", "error", "-i", str(clean_video), "-vn",
                         "-c:a", "pcm_s24le", str(clean_wav)]
        subprocess.run(extract_clean, check=True)
        normalize_cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(clean_wav),
                         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ac", "1", "-ar", "16000",
                         "-c:a", "pcm_s16le", str(norm_wav)]
        subprocess.run(normalize_cmd, check=True)
    else:
        print("  [Audio Worker] Source has no audio stream; preserving video and skipping ASR.")
        silent_cmd = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono",
                      "-t", str(meta_duration := probe_video(raw_video)["duration"]),
                      "-c:a", "pcm_s16le", str(norm_wav)]
        subprocess.run(silent_cmd, check=True)
        shutil.copyfile(norm_wav, clean_wav)

    # 2. Acoustic Waveform Silence Detection (-30dB threshold)
    print("  [Audio Worker] Scanning acoustic waveform for real silences...")
    silence_cmd = [
        "ffmpeg", "-i", str(norm_wav),
        "-af", "silencedetect=noise=-30dB:d=0.35",
        "-f", "null", "-"
    ]
    s_res = subprocess.run(silence_cmd, capture_output=True, text=True, check=True)
    silences = []
    current_silence_start = None
    for line in s_res.stderr.splitlines():
        if "silence_start:" in line:
            m = re.search(r"silence_start:\s*([\d\.]+)", line)
            if m:
                current_silence_start = float(m.group(1))
        elif "silence_end:" in line and current_silence_start is not None:
            m = re.search(r"silence_end:\s*([\d\.]+)\s*\|\s*silence_duration:\s*([\d\.]+)", line)
            if m:
                silences.append({
                    "start": current_silence_start,
                    "end": float(m.group(1)),
                    "duration": float(m.group(2))
                })
                current_silence_start = None

    # 3. Whisper transcription (Roman-script English decode only)
    model = None
    if has_audio:
        print("  [Audio Worker] Transcribing processed audio with whisper.cpp...")
        import config
        cfg = config.load()
        whisper_bin = config.find_whisper_bin(cfg)
        model = config.find_whisper_model(cfg)
        if not whisper_bin or not model:
            raise RuntimeError("whisper.cpp binary or model not found. Run setup.py.")
        out_prefix = audio_dir / "whisper_raw"
        cmd = transcribe_cpp.build_command(whisper_bin, model, norm_wav, out_prefix, cfg)
        transcribe_cpp.run_whisper(cmd)
        raw_json = Path(str(out_prefix) + ".json")
        if not raw_json.exists():
            raise RuntimeError(f"Whisper output {raw_json} not generated.")
        whisper_raw_data = json.loads(raw_json.read_text(encoding="utf-8"))
        parsed = transcribe_cpp.parse_whisper_json(whisper_raw_data)
        words = parsed.get("words", [])
    else:
        parsed = {"language": "en", "words": []}
        words = []
    
    # Save standard transcript
    transcript_data = {
        "engine": "whisper.cpp" if model else "none; source has no audio stream",
        "model": model.name if model else None,
        "language": parsed.get("language", "en"),
        "words": words
    }
    with open(transcript_json, "w", encoding="utf-8") as f:
        json.dump(transcript_data, f, indent=2, ensure_ascii=False)

    dur = time.time() - t0
    print(f"  [Audio Worker] Finished in {dur:.2f}s ({len(words)} words, {len(silences)} acoustic pauses).")
    return {
        "words_count": len(words),
        "silences": silences,
        "transcript_path": str(transcript_json),
        "clean_audio_path": str(clean_wav),
        "clean_video_path": str(clean_video) if has_audio else None,
        "elapsed": dur
    }


# -----------------------------------------------------------------------------
# Worker B: Visual Track (Keyframes, Frame Color Correction, Chin Framing)
# -----------------------------------------------------------------------------
def process_visual_worker(raw_video: str, project_dir: str, meta: dict) -> dict:
    t0 = time.time()
    out_dir = Path(project_dir)
    preview_dir = out_dir / "preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    duration = meta["duration"]
    print("  [Visual Worker] Detecting shot boundaries and building a source contact sheet...")
    scene_cmd = [
        "ffmpeg", "-hide_banner", "-i", raw_video, "-vf",
        "select='gt(scene,0.28)',showinfo", "-an", "-f", "null", "-"
    ]
    scene_run = subprocess.run(scene_cmd, capture_output=True, text=True)
    if scene_run.returncode:
        raise RuntimeError(f"FFmpeg scene analysis failed: {scene_run.stderr[-1200:]}")
    cut_times = sorted({float(x) for x in re.findall(r"pts_time:([0-9]+(?:\.[0-9]+)?)", scene_run.stderr)
                        if 0.15 < float(x) < duration - 0.15})
    bounds = [0.0]
    for cut in cut_times:
        if cut - bounds[-1] >= 0.45:
            bounds.append(cut)
    if duration - bounds[-1] < 0.15 and len(bounds) > 1:
        bounds.pop()
    bounds.append(float(duration))
    shots = [{"start": round(a, 3), "end": round(b, 3)}
             for a, b in zip(bounds, bounds[1:]) if b - a >= 0.15]
    if not shots:
        shots = [{"start": 0.0, "end": round(float(duration), 3)}]

    # Keep the evidence sheet readable on long, high-cut footage. Selected samples remain
    # tied to real shot intervals; the full detected cut list is still recorded below.
    max_samples = 48
    if len(shots) <= max_samples:
        selected = list(enumerate(shots))
    else:
        indexes = sorted({round(i * (len(shots) - 1) / (max_samples - 1)) for i in range(max_samples)})
        selected = [(i, shots[i]) for i in indexes]
    evidence_frames = []
    grade_timestamps = [round(duration * p, 2) for p in (0.15, 0.38, 0.62, 0.85) if duration * p < duration]
    for idx, shot in selected:
        ts = round((shot["start"] + shot["end"]) / 2, 3)
        frame_file = preview_dir / f"source-{idx + 1:03d}.jpg"
        grade.extract_frame(raw_video, ts, str(frame_file))
        evidence_frames.append({"id": f"visual-{idx + 1:03d}", "timestamp": ts,
                               "shot_start": shot["start"], "shot_end": shot["end"],
                               "frame": str(frame_file)})

    # PIL is a declared engine dependency. If image decoding fails, individual frames
    # remain available and the failure is reported in the evidence packet.
    contact_sheet = preview_dir / "source-contact-sheet.jpg"
    try:
        from PIL import Image, ImageDraw, ImageFont
        cell_w, cell_h, label_h, columns = 320, 220, 30, 4
        rows = (len(evidence_frames) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * cell_w, rows * (cell_h + label_h)), "#202124")
        draw = ImageDraw.Draw(sheet)
        for i, item in enumerate(evidence_frames):
            frame = Image.open(item["frame"]).convert("RGB")
            frame.thumbnail((cell_w, cell_h))
            x, y = (i % columns) * cell_w, (i // columns) * (cell_h + label_h)
            sheet.paste(frame, (x + (cell_w - frame.width) // 2, y + (cell_h - frame.height) // 2))
            draw.text((x + 8, y + cell_h + 5),
                      f"{item['id']} · {item['timestamp']:.2f}s · shot {item['shot_start']:.2f}-{item['shot_end']:.2f}s",
                      fill="white")
        sheet.save(contact_sheet, quality=88)
    except Exception as exc:
        contact_sheet = None
        print(f"  [Visual Worker] Contact sheet unavailable; individual frames retained: {exc}")

    # Dynamic Frame-Accurate Color Correction Calculation
    print("  [Visual Worker] Dynamically calculating color correction from frame distributions...")
    dyn_color = grade.calculate_dynamic_color_correction(raw_video, timestamps=grade_timestamps)
    dyn_grade_path = preview_dir / "dynamic-grade.json"
    with open(dyn_grade_path, "w", encoding="utf-8") as f:
        json.dump(dyn_color, f, indent=2)

    # Generate Frame-by-Frame Color Correction & Enhancement Sheet on actual chosen frames
    print("  [Visual Worker] Generating frame-by-frame color correction comparison sheet...")
    grade_preview_path = preview_dir / "grade-preview.jpg"
    grade.generate_frame_correction_sheet(raw_video, str(grade_preview_path), timestamps=grade_timestamps, preset="dynamic")

    # Chin & Face Detection for Caption Safe Placement
    print("  [Visual Worker] Measuring speaker framing and chin position...")
    chin_y = 0.58
    try:
        import cv2
        sample_img = cv2.imread(evidence_frames[len(evidence_frames) // 2]["frame"])
        if sample_img is not None:
            gray = cv2.cvtColor(sample_img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
            if len(faces) > 0:
                fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
                chin_y = round((fy + fh * 1.15) / sample_img.shape[0], 3)
    except Exception:
        pass

    caption_y = min(0.86, max(0.65, chin_y + 0.12))

    dur = time.time() - t0
    print(f"  [Visual Worker] Finished in {dur:.2f}s ({len(shots)} detected shots, "
          f"{len(evidence_frames)} visual samples, caption safe y={caption_y}).")
    return {
        "evidence_frames": evidence_frames,
        "contact_sheet_path": str(contact_sheet) if contact_sheet else None,
        "shot_boundaries": bounds,
        "detected_shots": shots,
        "grade_preview_path": str(grade_preview_path),
        "dyn_color": dyn_color,
        "dynamic_grade_path": str(dyn_grade_path),
        "caption_y": caption_y,
        "elapsed": dur
    }



# -----------------------------------------------------------------------------
# Synthesis: source evidence, cut proposal, references and review artifacts
# -----------------------------------------------------------------------------
from pipeline_synthesis import synthesize_storyboard_and_cuts


# -----------------------------------------------------------------------------
# Main Commands
# -----------------------------------------------------------------------------
def cmd_analyze(args):
    start_total = time.time()
    print("=" * 70)
    print("  PARALLEL VIDEO EDITING PIPELINE: INGEST & ANALYSIS")
    print("=" * 70)

    try:
        import PIL  # noqa: F401
        import cv2  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("Pillow and OpenCV are required in the configured engine environment; run the video-skills setup to install engine/requirements.txt.") from exc

    project_root = Path(args.project).expanduser().resolve()
    project_root.mkdir(parents=True, exist_ok=True)
    input_path = Path(args.input).expanduser().resolve()
    if input_path.is_dir():
        search_root = input_path / "raw" if (input_path / "raw").is_dir() else input_path
        excluded = {".video-pipeline", "Exports", "references", "brand", ".git"}
        candidates = sorted(p for p in search_root.rglob("*")
                           if p.is_file() and p.suffix.lower() in {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mxf"}
                           and not (excluded & set(p.relative_to(search_root).parts))
                           and not any(part.startswith(".") for part in p.relative_to(search_root).parts))
        if len(candidates) != 1:
            names = "\n".join(f"  - {p.relative_to(input_path)}" for p in candidates[:30]) or "  (no supported videos found)"
            raise RuntimeError(f"Choose one source video from {input_path}; found {len(candidates)} candidates:\n{names}")
        input_path = candidates[0]
    if not input_path.is_file() or input_path.suffix.lower() not in {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mxf"}:
        raise RuntimeError(f"Input must be a supported video file or a folder containing exactly one: {input_path}")
    raw_video = str(input_path)
    project_dir = project_root / ".video-pipeline"
    project_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[Step 1/4] Standardizing footage to SDR Rec.709 and H.265 (HEVC)...")
    standard_video = standardize_video(raw_video, project_dir)

    print(f"\n[Step 2/4] Probing standardized video: {standard_video}")
    meta = probe_video(standard_video)
    meta["source_video"] = raw_video
    print(f"  Resolution: {meta['width']}x{meta['height']}, FPS: {meta['fps']}, Duration: {meta['duration']:.2f}s")

    print("\n[Step 3/4] Launching Parallel Audio & Visual Analysis Workers...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        fut_audio = executor.submit(process_audio_worker, standard_video, project_dir)
        fut_visual = executor.submit(process_visual_worker, standard_video, project_dir, meta)

        audio_res = fut_audio.result()
        visual_res = fut_visual.result()

    print("\n[Step 4/4] Building source evidence and review packet...")
    edit_video = audio_res.get("clean_video_path") or standard_video
    meta["raw_video"] = edit_video
    ref_input = getattr(args, "reference", None)
    syn_res = synthesize_storyboard_and_cuts(edit_video, project_dir, meta, audio_res, visual_res,
                                             ref_inputs=ref_input, prompt=getattr(args, "prompt", ""))

    total_time = time.time() - start_total
    print("\n" + "=" * 70)
    print(f"  ANALYSIS COMPLETE in {total_time:.2f}s!")
    print(f"  - Visual Storyboard: {syn_res['storyboard_md']}")
    print(f"  - Color Correction Sheet: {visual_res['grade_preview_path']}")
    print(f"  - Active Cut: full source preserved pending review ({meta['duration']:.2f}s)")
    print(f"  - Private work files: {project_dir}")
    print("=" * 70)


def _project_workspace(project: Path) -> tuple[Path, Path]:
    project = project.expanduser().resolve()
    if project.name == ".video-pipeline":
        return project.parent, project
    return project, project / ".video-pipeline"


def _approval_fingerprint(work_dir: Path) -> dict:
    files = ("resolved-spec.json", "storyboard.plan.json", "storyboard.json", "style.json",
             "cut-list.json", "source-evidence.json", "references/reference-index.json",
             "context/brand-inputs.json", "reference-match/matches.json")
    result = {}
    for name in files:
        path = work_dir / name
        if not path.is_file():
            raise RuntimeError(f"Approval input is missing: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        result[name] = digest

    # The review packet records hashes for the original project materials. Verify
    # those source files too, so replacing a reference or brand guide after review
    # cannot leave the approval gate looking current.
    external_inputs = (
        ("references/reference-index.json", "path"),
        ("context/brand-inputs.json", "source"),
    )
    for index_name, path_key in external_inputs:
        index_path = work_dir / index_name
        try:
            records = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Could not read approval input index {index_path}: {exc}") from exc
        for record in records:
            source = Path(record[path_key]).expanduser()
            if not source.is_file():
                raise RuntimeError(f"Reviewed project input is missing: {source}")
            source_hash = hashlib.sha256()
            with source.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    source_hash.update(chunk)
            digest = source_hash.hexdigest()
            if digest != record.get("sha256"):
                raise RuntimeError(f"Reviewed project input changed since analysis: {source}")
            result[f"{index_name}:{record.get('id', source.name)}"] = digest

    project_root, _ = _project_workspace(work_dir)
    storyboard = json.loads((work_dir / "storyboard.json").read_text(encoding="utf-8"))
    for html_path, relative in _validate_selected_blocks(storyboard):
        for asset in sorted(path for path in html_path.parent.rglob("*") if path.is_file()):
            digest = hashlib.sha256(asset.read_bytes()).hexdigest()
            asset_key = asset.relative_to(html_path.parent).as_posix()
            result[f"composition:{relative.as_posix()}:{asset_key}"] = digest
    for cue in storyboard.get("sfx", []):
        source = _resolve_sfx_source(str(cue.get("src", "")), project_root, work_dir)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        result[f"sfx:{cue.get('id', source.name)}"] = digest
    return result


def _next_export_path(exports_dir: Path, project_name: str) -> Path:
    pattern = re.compile(rf"^{re.escape(project_name)}-v(\d+)\.mp4$", re.IGNORECASE)
    versions = []
    for path in exports_dir.iterdir():
        match = pattern.match(path.name)
        if match:
            versions.append(int(match.group(1)))
    return exports_dir / f"{project_name}-v{max(versions, default=0) + 1}.mp4"


class _CompositionMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.variables = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("data-composition-id"):
            self.ids.add(attrs["data-composition-id"])
        encoded = attrs.get("data-composition-variables")
        if encoded:
            try:
                value = json.loads(encoded)
                if isinstance(value, list):
                    self.variables.extend(x.get("id") for x in value if isinstance(x, dict) and x.get("id"))
            except ValueError:
                pass


def _composition_catalog_dir() -> Path:
    configured = os.environ.get("VIDEO_COMPOSITIONS", "").strip()
    return (Path(configured).expanduser() if configured else runtime.find_engine_dir() / "compositions").resolve()


def _validate_selected_blocks(storyboard: dict) -> list[tuple[Path, Path]]:
    engine_dir = _composition_catalog_dir()
    selected = []
    for beat in storyboard.get("beats", []):
        if beat.get("type") != "block":
            continue
        src_value = str(beat.get("src", ""))
        relative = Path(src_value.replace("\\", "/").removeprefix("compositions/"))
        if not src_value or relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"Unsafe HyperFrames composition path: {src_value!r}")
        source_html = engine_dir / relative
        if not source_html.is_file():
            raise RuntimeError(f"Selected HyperFrames composition is missing from the configured local registry: {source_html}")
        parser = _CompositionMetadata()
        parser.feed(source_html.read_text(encoding="utf-8"))
        comp_id = str(beat.get("comp_id", ""))
        if comp_id not in parser.ids:
            raise RuntimeError(f"Composition {source_html.name} does not declare internal id {comp_id!r}.")
        variables = beat.get("vars", {})
        if not isinstance(variables, dict):
            raise RuntimeError(f"HyperFrames variables for beat {beat.get('id')} must be an object.")
        unknown = sorted(set(variables) - set(parser.variables))
        if unknown:
            raise RuntimeError(f"Composition {source_html.name} does not declare variables: {', '.join(unknown)}")
        selected.append((source_html, relative))
    return selected


def _stage_selected_compositions(hyper_dir: Path, storyboard: dict) -> None:
    selected = _validate_selected_blocks(storyboard)
    if not selected:
        return
    target_comp_dir = hyper_dir / "compositions"
    target_comp_dir.mkdir(parents=True, exist_ok=True)
    for source_html, relative in selected:
        destination_dir = target_comp_dir / relative.parent
        destination_dir.mkdir(parents=True, exist_ok=True)
        if relative.parent != Path("."):
            shutil.copytree(source_html.parent, destination_dir, dirs_exist_ok=True)
        else:
            shutil.copyfile(source_html, target_comp_dir / relative)


def _resolve_sfx_source(src_value: str, project_root: Path, work_dir: Path) -> Path:
    raw = Path(src_value).expanduser()
    candidates = []
    if raw.is_absolute():
        candidates.append(raw.resolve())
    else:
        candidates.extend([(work_dir / "hyperframes" / raw).resolve(), (project_root / raw).resolve()])
        name = raw.name
        repo_root = Path(HERE).parents[3]
        engine_dir = runtime.find_engine_dir()
        candidates.extend([repo_root / "sound-palette" / "audio" / name,
                           engine_dir / "sound-palette" / "audio" / name])
    for candidate in candidates:
        if not candidate.is_file():
            continue
        if candidate.is_relative_to(project_root) or candidate.is_relative_to(runtime.find_engine_dir()) or candidate.is_relative_to(Path(HERE).parents[3]):
            return candidate
    raise RuntimeError(f"SFX asset is missing or outside the project/local pipeline assets: {src_value}")


def _stage_sfx_assets(storyboard: dict, project_root: Path, work_dir: Path, hyper_dir: Path) -> dict:
    staged = json.loads(json.dumps(storyboard))
    sfx_dir = hyper_dir / "sfx"
    for cue in staged.get("sfx", []):
        source = _resolve_sfx_source(str(cue.get("src", "")), project_root, work_dir)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
        dest_name = f"{digest}-{source.name}"
        sfx_dir.mkdir(parents=True, exist_ok=True)
        destination = sfx_dir / dest_name
        if source.resolve() != destination.resolve():
            shutil.copyfile(source, destination)
        cue["src"] = f"sfx/{dest_name}"
    return staged


def cmd_approve(args):
    project_root, work_dir = _project_workspace(Path(args.project))
    if not args.user_approved:
        raise RuntimeError("Approval was not recorded. Run this command only after the user explicitly approves the plan and cut.")
    required = [work_dir / "resolved-spec.json", work_dir / "storyboard.plan.json", work_dir / "storyboard.json",
                work_dir / "style.json", work_dir / "cut-list.json", work_dir / "source-evidence.json",
                work_dir / "references" / "reference-index.json", work_dir / "context" / "brand-inputs.json",
                work_dir / "reference-match" / "matches.json"]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise RuntimeError("Cannot approve; required review files are missing:\n  " + "\n  ".join(missing))

    evidence = json.loads((work_dir / "source-evidence.json").read_text(encoding="utf-8"))
    spec = json.loads((work_dir / "resolved-spec.json").read_text(encoding="utf-8"))
    storyboard = json.loads((work_dir / "storyboard.json").read_text(encoding="utf-8"))
    cut = json.loads((work_dir / "cut-list.json").read_text(encoding="utf-8"))
    evidence_hash = hashlib.sha256((work_dir / "source-evidence.json").read_bytes()).hexdigest()
    plan = json.loads((work_dir / "storyboard.plan.json").read_text(encoding="utf-8"))
    if plan.get("source_evidence_sha256") != evidence_hash:
        raise RuntimeError("storyboard.plan.json is stale; rebuild the plan from the current source-evidence.json.")
    if storyboard.get("source_evidence_sha256") != evidence_hash:
        raise RuntimeError("storyboard.json must cite the current source_evidence_sha256 from source-evidence.json.")
    _validate_selected_blocks(storyboard)
    canvas = storyboard.get("canvas")
    if (not isinstance(canvas, list) or len(canvas) != 2
            or any(not isinstance(side, (int, float)) or isinstance(side, bool) or side <= 0 for side in canvas)):
        raise RuntimeError("storyboard.json needs a positive numeric [width, height] canvas matching the approved delivery aspect.")
    platform_answer = str(spec.get("user_answers", {}).get("platform_aspect", ""))
    ratio_matches = re.findall(r"(\d+(?:\.\d+)?)\s*[:/]\s*(\d+(?:\.\d+)?)", platform_answer)
    if len(ratio_matches) == 1:
        requested_ratio = float(ratio_matches[0][0]) / float(ratio_matches[0][1])
        canvas_ratio = float(canvas[0]) / float(canvas[1])
        if abs(requested_ratio - canvas_ratio) > 0.015:
            raise RuntimeError("storyboard.json canvas does not match the user's selected platform aspect ratio.")
    duration = float(evidence["source"]["duration"])
    if not isinstance(spec.get("user_answers"), dict) or not spec["user_answers"]:
        raise RuntimeError("resolved-spec.json must record the user's answers in a non-empty user_answers object.")
    required_answers = {"keep_cut", "platform_aspect", "direction", "framing", "captions", "sound"}
    unanswered = sorted(required_answers - set(spec["user_answers"]))
    if unanswered:
        raise RuntimeError("resolved-spec.json must record these decisions, including explicit defaults/delegation: "
                           + ", ".join(unanswered))
    audio_spec = spec.get("audio", {})
    if audio_spec.get("preset") and audio_spec["preset"] not in {"youtube", "shorts", "longform", "broadcast"}:
        raise RuntimeError("resolved-spec.json audio.preset must be youtube, shorts, longform, or broadcast.")
    if audio_spec.get("denoise") and audio_spec["denoise"] not in {"auto", "off", "light", "medium", "strong", "neural"}:
        raise RuntimeError("resolved-spec.json audio.denoise has an unsupported value.")
    music_path = audio_spec.get("music_path")
    if music_path:
        music_file = Path(music_path).expanduser()
        if not music_file.is_absolute():
            music_file = project_root / music_file
        music_file = music_file.resolve()
        try:
            music_file.relative_to(project_root)
        except ValueError:
            raise RuntimeError("Selected music must be inside the user-selected project folder.")
        if not music_file.is_file():
            raise RuntimeError(f"Selected music file does not exist: {music_file}")
    if not isinstance(storyboard.get("beats"), list):
        raise RuntimeError("storyboard.json must contain a beats array; use an empty array for a source-only edit.")
    valid_refs = {x["id"] for x in evidence.get("visual_samples", [])} | {x["id"] for x in evidence.get("speech_segments", [])}
    evidence_ranges = {}
    for item in evidence.get("visual_samples", []) + evidence.get("speech_segments", []):
        timestamp = item.get("timestamp", 0)
        start = float(item.get("shot_start", item.get("start", timestamp)))
        end = float(item.get("shot_end", item.get("end", timestamp)))
        evidence_ranges[item["id"]] = (start, end)
    for beat in storyboard["beats"]:
        if not isinstance(beat, dict):
            raise RuntimeError("Every storyboard beat must be an object.")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", str(beat.get("id", ""))):
            raise RuntimeError("Every beat needs a simple id using letters, numbers, underscores or hyphens.")
        refs = beat.get("source_refs", [])
        if not refs or any(ref not in valid_refs for ref in refs):
            raise RuntimeError(f"Beat {beat.get('id', '(unnamed)')} needs valid source_refs from source-evidence.json.")
        for key in ("in", "out"):
            if not isinstance(beat.get(key), (int, float)):
                raise RuntimeError(f"Beat {beat.get('id')} needs numeric {key} time in the approved edit timeline.")
        if beat["in"] < 0 or beat["out"] <= beat["in"] or beat["out"] > float(storyboard.get("duration", duration)) + 0.05:
            raise RuntimeError(f"Beat {beat.get('id')} has an invalid time range.")
    for cue in storyboard.get("sfx", []):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", str(cue.get("id", ""))):
            raise RuntimeError("Every SFX cue needs a simple id using letters, numbers, underscores or hyphens.")
        if not cue.get("source_refs") or any(ref not in valid_refs for ref in cue["source_refs"]):
            raise RuntimeError(f"SFX cue {cue.get('id')} needs valid source_refs from source-evidence.json.")
        if not isinstance(cue.get("at"), (int, float)) or not isinstance(cue.get("dur", 1.0), (int, float)):
            raise RuntimeError(f"SFX cue {cue.get('id')} needs numeric at and dur values.")
        if cue["at"] < 0 or cue["at"] >= float(storyboard.get("duration", duration)) or cue.get("dur", 1.0) <= 0:
            raise RuntimeError(f"SFX cue {cue.get('id')} has an invalid time range.")
        _resolve_sfx_source(str(cue.get("src", "")), project_root, work_dir)
    kept = cut.get("kept", [])
    if not kept:
        raise RuntimeError("The approved cut must keep at least one source range.")
    if abs(float(cut.get("source_duration", -1)) - duration) > 0.05:
        raise RuntimeError("cut-list.json source_duration does not match the analyzed source duration.")
    last_end = -1.0
    for segment in sorted(kept, key=lambda s: float(s.get("start", -1))):
        start, end = float(segment.get("start", -1)), float(segment.get("end", -1))
        if start < 0 or end <= start or end > duration + 0.05 or start < last_end - 0.001:
            raise RuntimeError("cut-list.json has an invalid, overlapping, or out-of-source kept range.")
        last_end = end
    for beat in storyboard["beats"]:
        for ref in beat.get("source_refs", []):
            source_start, source_end = evidence_ranges[ref]
            if not any(max(source_start, float(segment["start"])) <= min(source_end, float(segment["end"]))
                       for segment in kept):
                raise RuntimeError(f"Beat {beat.get('id')} cites {ref}, which is outside the approved kept ranges.")
    for cue in storyboard.get("sfx", []):
        for ref in cue.get("source_refs", []):
            source_start, source_end = evidence_ranges[ref]
            if not any(max(source_start, float(segment["start"])) <= min(source_end, float(segment["end"]))
                       for segment in kept):
                raise RuntimeError(f"SFX cue {cue.get('id')} cites {ref}, which is outside the approved kept ranges.")
    expected_duration = sum(float(segment["end"]) - float(segment["start"]) for segment in kept)
    if abs(float(cut.get("kept_seconds", -1)) - expected_duration) > 0.05:
        raise RuntimeError("cut-list.json kept_seconds does not match its kept ranges.")
    if abs(float(storyboard.get("duration", -1)) - expected_duration) > 0.05:
        raise RuntimeError("storyboard.json duration must match the total approved kept duration.")

    gate = {"plan": {"status": "approved", "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                     "approval_note": args.note, "source_evidence": "source-evidence.json",
                     "fingerprint": _approval_fingerprint(work_dir)}}
    gate_path = work_dir / "gates.json"
    gate_path.write_text(json.dumps(gate, indent=2), encoding="utf-8")
    state_path = work_dir / "project.json"
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state.setdefault("gates", {})["plan"] = gate["plan"]
        state.setdefault("steps", {}).setdefault("direction", {})["status"] = "done"
        state["steps"]["assembly"] = {"status": "ready"}
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(f"Plan and cut approval recorded for {project_root}. Assembly is now enabled.")


def cmd_assemble(args):
    start_total = time.time()
    print("=" * 70)
    print("  PARALLEL VIDEO EDITING PIPELINE: ASSEMBLY & MASTER RENDER")
    print("=" * 70)

    project_root, project_dir = _project_workspace(Path(args.project))
    gate_path = project_dir / "gates.json"
    gate = json.loads(gate_path.read_text(encoding="utf-8")) if gate_path.is_file() else {}
    if gate.get("plan", {}).get("status") != "approved":
        raise RuntimeError("Assembly is gated. Review the source, brand, references, questions, storyboard and cut; then run the approve command after user approval.")
    current_fingerprint = _approval_fingerprint(project_dir)
    if gate.get("plan", {}).get("fingerprint") != current_fingerprint:
        raise RuntimeError("The approved plan, cut, style, spec, source evidence, brand inputs, or references changed after approval. Review the changes and record a new approval.")
    cut_list = project_dir / "cut-list.json"
    raw_video = None
    if (project_dir / "meta.json").exists():
        try:
            m = json.load(open(project_dir / "meta.json"))
            raw_video = m.get("raw_video")
        except Exception:
            pass
    if not raw_video or not os.path.exists(raw_video):
        raw_files = list((project_dir / "raw").glob("*.MOV")) + list((project_dir / "raw").glob("*.mp4"))
        if not raw_files:
            raise RuntimeError(f"No raw video found in {project_dir}/raw/ or meta.json")
        raw_video = str(raw_files[0])

    hyper_dir = project_dir / "hyperframes"
    hyper_dir.mkdir(parents=True, exist_ok=True)
    flat_cut_video = hyper_dir / "input-video.mp4"

    preset = args.preset
    style_json = project_dir / "style.json"
    if style_json.exists():
        st = json.loads(style_json.read_text(encoding="utf-8"))
        preset = preset or st.get("color_grade", "dynamic")
    preset = preset or "dynamic"

    # 1. Apply Cut & Graded Flat Video
    print(f"\n[Step 1/4] Applying frame-accurate cut & {preset} color correction...")
    apply_cut_py = os.path.join(HERE, "apply-cut.py")
    cmd_cut = [
        sys.executable, apply_cut_py,
        "--input", raw_video,
        "--cut-list", str(cut_list),
        "--out", str(flat_cut_video),
        "--grade", preset
    ]
    subprocess.run(cmd_cut, check=True)

    # 2. Pass 2 Transcribe: Align Exact Word Timestamps to Flat Cut Video
    print("\n[Step 2/4] Transcribing flat cut audio for frame-exact caption sync...")
    temp_asr = project_dir / "scratch" / "cut-asr"
    temp_asr.mkdir(parents=True, exist_ok=True)
    try:
        flat_trans = transcribe_cpp.transcribe(str(flat_cut_video), temp_asr)
        with open(hyper_dir / "transcript.json", "w", encoding="utf-8") as f:
            json.dump(flat_trans, f, indent=2, ensure_ascii=False)
        with open(project_dir / "transcript.json", "w", encoding="utf-8") as f:
            json.dump(flat_trans, f, indent=2, ensure_ascii=False)
        print(f"  [Pass 2 Transcribe] Mapped {len(flat_trans.get('words', []))} words directly to {flat_cut_video.name}")
    finally:
        shutil.rmtree(temp_asr, ignore_errors=True)

    storyboard_json = project_dir / "storyboard.json"
    cut_map_json = project_dir / "cut-map.json"
    stage_spec_path = hyper_dir / "storyboard-stage.json"
    storyboard_data = json.loads(storyboard_json.read_text(encoding="utf-8"))
    stage_spec = _stage_sfx_assets(storyboard_data, project_root, project_dir, hyper_dir)
    stage_spec_path.write_text(json.dumps(stage_spec, indent=2, ensure_ascii=False), encoding="utf-8")

    # Stage only SFX explicitly present in the approved storyboard.
    engine_dir = runtime.find_engine_dir()

    # HyperFrames requires bundled assets to remain inside the project root. Resolve
    # blocks from the one shared catalog, then stage only the blocks this edit uses.
    _stage_selected_compositions(hyper_dir, storyboard_data)

    # 3. Stage HyperFrames Composition with Collision-Free Captions
    print("\n[Step 3/4] Staging approved HyperFrames beats and caption treatment...")
    stage_py = os.path.join(HERE, "stage.py")
    cmd_stage = [
        sys.executable, stage_py,
        "--spec", str(stage_spec_path),
        "--style", str(style_json),
        "--cut-map", str(cut_map_json),
        "--out", str(hyper_dir)
    ]
    subprocess.run(cmd_stage, check=True)

    # 4. Master Render & Automated Verification (with Denoise & Audio Mastering)
    print("\n[Step 4/4] Rendering the approved edit with BT.709 tags and selected audio processing...")
    render_py = os.path.join(HERE, "render.py")
    processed_dir = project_root / "Exports"
    processed_dir.mkdir(parents=True, exist_ok=True)
    render_output = project_dir / "scratch" / "publish" / f"master-{time.time_ns()}.mp4"
    
    sb = json.loads(storyboard_json.read_text(encoding="utf-8"))
    canvas = sb["canvas"]
    res_mode = "landscape" if canvas[0] > canvas[1] else ("square" if canvas[0] == canvas[1] else "portrait")

    cmd_render = [
        sys.executable, render_py,
        "--public", str(hyper_dir),
        "--out", str(render_output),
        "--scratch-dir", str(project_dir / "scratch" / "render"),
        "--resolution", res_mode,
        "--sdr",
        "--denoise", "auto",
        "--dereverb", args.dereverb,
        "--audio-preset", "shorts"
    ]
    resolved_spec = json.loads((project_dir / "resolved-spec.json").read_text(encoding="utf-8"))
    audio_spec = resolved_spec.get("audio", {})
    cmd_render[cmd_render.index("auto")] = audio_spec.get("denoise", "auto")
    chosen_preset = audio_spec.get("preset")
    if not chosen_preset:
        platform = str(resolved_spec.get("user_answers", {}).get("platform_aspect", "")).lower()
        chosen_preset = "broadcast" if "broadcast" in platform else (
            "longform" if "long" in platform or "podcast" in platform else
            "youtube" if "youtube" in platform and "short" not in platform else "shorts")
    cmd_render[cmd_render.index("shorts")] = chosen_preset
    if audio_spec.get("music_path"):
        music_file = Path(audio_spec["music_path"]).expanduser()
        if not music_file.is_absolute():
            music_file = project_root / music_file
        music_file = music_file.resolve()
        try:
            music_file.relative_to(project_root)
        except ValueError:
            raise RuntimeError("Selected music must be inside the user-selected project folder.")
        cmd_render.extend(["--music", str(music_file)])
    subprocess.run(cmd_render, check=True)

    if not render_output.is_file() or render_output.stat().st_size == 0:
        raise RuntimeError(f"Render completed without producing a usable master file: {render_output}")
    master_video = _next_export_path(processed_dir, project_root.name)
    while master_video.exists():
        master_video = _next_export_path(processed_dir, project_root.name)
    os.replace(render_output, master_video)

    state_path = project_dir / "project.json"
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state.setdefault("steps", {})["assembly"] = {"status": "done", "output": str(master_video.relative_to(project_root))}
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    total_time = time.time() - start_total
    print("\n" + "=" * 70)
    print(f"  ASSEMBLY & MASTER RENDER COMPLETE in {total_time:.2f}s!")
    print(f"  - Master Deliverable: {master_video}")
    print("=" * 70)


def main():
    ap = argparse.ArgumentParser(description="Parallel Video Editing Pipeline")
    sub = ap.add_subparsers(dest="subcommand", required=True)

    p_an = sub.add_parser("analyze", help="Ingest, parallel analysis, source evidence, references, and review packet")
    p_an.add_argument("--input", required=True, help="Source video, or a folder containing exactly one supported video")
    p_an.add_argument("--project", required=True, help="User project folder; pipeline work is stored in its hidden .video-pipeline folder")
    p_an.add_argument("--reference", action="append", help="Reference video or image; may be repeated, project/references is also scanned")
    p_an.add_argument("--prompt", default="", help="User's creative brief; carried into the project review")

    p_ap = sub.add_parser("approve", help="Record approval after the user has approved the storyboard and cut")
    p_ap.add_argument("--project", required=True, help="User project folder")
    p_ap.add_argument("--user-approved", action="store_true", help="Required acknowledgement that the user approved the plan")
    p_ap.add_argument("--note", default="User approved storyboard, brand treatment and cut.", help="Approval record note")

    p_as = sub.add_parser("assemble", help="Execute cut, staging, and master render")
    p_as.add_argument("--project", required=True, help="Project directory")
    p_as.add_argument("--preset", default=None, help="Override the grade selected in style.json")
    p_as.add_argument("--dereverb", choices=["off", "light", "medium", "strong"], default="strong",
                      help="late-reflection reduction strength for the audio master")

    args = ap.parse_args()
    try:
        if args.subcommand == "analyze":
            cmd_analyze(args)
        elif args.subcommand == "approve":
            cmd_approve(args)
        elif args.subcommand == "assemble":
            cmd_assemble(args)
    except subprocess.CalledProcessError as exc:
        print(f"pipeline stage failed with exit code {exc.returncode}: {exc.cmd}", file=sys.stderr)
        raise SystemExit(exc.returncode or 1)
    except (RuntimeError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"pipeline error: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
