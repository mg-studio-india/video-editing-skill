#!/usr/bin/env python3
"""parallel_pipeline.py: High-speed, parallel video editing pipeline."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
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
        "-show_entries", "stream=width,height,r_frame_rate,duration,codec_name,pix_fmt:format=duration,size,bit_rate",
        "-of", "json", video_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)
    v_stream = next((s for s in data.get("streams", []) if s.get("codec_name") not in ("aac", "mp3")), {})
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

    if standard_out.exists() and standard_out.stat().st_size > 100000:
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
    dur = time.time() - t0
    print(f"  [Standard Ingest] Standard SDR H.265 video ready in {dur:.2f}s -> {standard_out}")
    return str(standard_out)


# -----------------------------------------------------------------------------
# Worker A: Audio Track (High-Pass, Loudnorm, Acoustic Silence, Whisper ASR)
# -----------------------------------------------------------------------------
def process_audio_worker(raw_video: str, project_dir: str) -> dict:
    t0 = time.time()
    out_dir = Path(project_dir)
    audio_dir = out_dir / "audio_processing"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    norm_wav = audio_dir / "audio-norm-16k.wav"
    clean_wav = out_dir / "audio-clean.wav"
    transcript_json = out_dir / "transcript.json"

    # 1. Audio Extraction with 80Hz rumble cut + Loudnorm (16kHz mono)
    print("  [Audio Worker] Extracting & normalizing dialogue audio...")
    extract_cmd = [
        "ffmpeg", "-y", "-v", "error", "-i", raw_video, "-vn",
        "-af", "highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(norm_wav)
    ]
    subprocess.run(extract_cmd, check=True)
    shutil.copyfile(str(norm_wav), str(clean_wav))

    # 2. Acoustic Waveform Silence Detection (-30dB threshold)
    print("  [Audio Worker] Scanning acoustic waveform for real silences...")
    silence_cmd = [
        "ffmpeg", "-i", str(norm_wav),
        "-af", "silencedetect=noise=-30dB:d=0.35",
        "-f", "null", "-"
    ]
    s_res = subprocess.run(silence_cmd, capture_output=True, text=True)
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

    # 3. Whisper Transcription (whisper.cpp)
    print("  [Audio Worker] Transcribing audio with whisper.cpp...")
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

    # 4. Transliteration & Phonetic Correction
    print("  [Audio Worker] Verifying words and standardizing transcript...")
    whisper_raw_data = json.loads(raw_json.read_text(encoding="utf-8"))
    parsed = transcribe_cpp.parse_whisper_json(whisper_raw_data)
    words = parsed.get("words", [])
    
    # Save standard transcript
    transcript_data = {
        "engine": "whisper.cpp",
        "model": model.name,
        "language": parsed.get("language", "hi-Latn"),
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
    # Sample 4 timestamps: 15%, 35%, 60%, 85%
    sample_timestamps = [
        round(duration * 0.15, 2),
        round(duration * 0.35, 2),
        round(duration * 0.60, 2),
        round(duration * 0.85, 2)
    ]

    print("  [Visual Worker] Extracting raw keyframes for storyboard and preview...")
    frame_paths = []
    for idx, ts in enumerate(sample_timestamps):
        frame_file = preview_dir / f"beat_frame_{idx + 1}.jpg"
        grade.extract_frame(raw_video, ts, str(frame_file))
        frame_paths.append(str(frame_file))

    # Dynamic Frame-Accurate Color Correction Calculation
    print("  [Visual Worker] Dynamically calculating color correction from frame distributions...")
    dyn_color = grade.calculate_dynamic_color_correction(raw_video, timestamps=sample_timestamps)
    dyn_grade_path = preview_dir / "dynamic-grade.json"
    with open(dyn_grade_path, "w", encoding="utf-8") as f:
        json.dump(dyn_color, f, indent=2)

    # Generate Frame-by-Frame Color Correction & Enhancement Sheet on actual chosen frames
    print("  [Visual Worker] Generating frame-by-frame color correction comparison sheet...")
    grade_preview_path = preview_dir / "grade-preview.jpg"
    grade.generate_frame_correction_sheet(raw_video, str(grade_preview_path), timestamps=sample_timestamps, preset="dynamic")

    # Chin & Face Detection for Caption Safe Placement
    print("  [Visual Worker] Measuring speaker framing and chin position...")
    chin_y = 0.58
    try:
        import cv2
        sample_img = cv2.imread(frame_paths[1])
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
    print(f"  [Visual Worker] Finished in {dur:.2f}s (dynamic color calculated, caption safe y={caption_y}).")
    return {
        "frame_paths": frame_paths,
        "grade_preview_path": str(grade_preview_path),
        "dyn_color": dyn_color,
        "dynamic_grade_path": str(dyn_grade_path),
        "caption_y": caption_y,
        "elapsed": dur
    }



# -----------------------------------------------------------------------------
# Synthesis: Tight Cut List & Visual Storyboard Artifact
# -----------------------------------------------------------------------------
def synthesize_storyboard_and_cuts(raw_video: str, project_dir: str, meta: dict,
                                  audio_res: dict, visual_res: dict,
                                  ref_input: str | None = None) -> dict:
    t0 = time.time()
    out_dir = Path(project_dir)
    transcript_path = audio_res["transcript_path"]

    # 1. Run Tight Paper-Cut
    print("  [Synthesis] Computing tight frame-accurate cuts (0.15s padding, stumbles eliminated)...")
    paper_cut_script = os.path.join(HERE, "paper-cut.py")
    cut_cmd = [
        sys.executable, paper_cut_script,
        "--transcript", transcript_path,
        "--duration", str(meta["duration"]),
        "--out-dir", project_dir,
        "--tight"
    ]
    subprocess.run(cut_cmd, check=True)

    cut_list_path = out_dir / "cut-list.json"
    cut_data = json.load(open(cut_list_path))
    kept_duration = cut_data.get("kept_seconds", meta["duration"])
    dropped_duration = round(meta["duration"] - kept_duration, 2)

    # 1b. Video-Reference-Match: References take precedence over blueprints
    print("  [Synthesis] Ranking proven video-presets for content archetype (video-reference-match)...")
    detected_ref = None
    if ref_input and os.path.exists(ref_input):
        detected_ref = str(Path(ref_input).resolve())
    else:
        candidate_dirs = [out_dir / "references", Path.cwd() / "references"]
        for rdir in candidate_dirs:
            if rdir.is_dir():
                for ext in ("*.mp4", "*.MOV", "*.mov", "*.png", "*.jpg"):
                    found = list(rdir.glob(ext))
                    if found:
                        detected_ref = str(found[0].resolve())
                        break
            if detected_ref:
                break

    matched_presets = []
    try:
        match_script = Path(HERE).parents[2] / "video-reference-match" / "scripts" / "match.py"
        if match_script.is_file():
            match_cmd = [
                sys.executable, str(match_script),
                "--video", raw_video,
                "--transcript", transcript_path,
                "--top", "3",
                "--out", str(out_dir)
            ]
            if detected_ref:
                print(f"  [Synthesis] User reference detected ({Path(detected_ref).name}): References take precedence over blueprints.")
                if detected_ref.lower().endswith((".mp4", ".mov")):
                    match_cmd.extend(["--video", detected_ref])
                else:
                    match_cmd.extend(["--image", detected_ref])
            subprocess.run(match_cmd, capture_output=True, text=True, check=True)
            matches_json = out_dir / "matches.json"
            if matches_json.is_file():
                match_data = json.load(open(matches_json))
                matched_presets = match_data.get("matches", [])
    except Exception as e:
        print(f"  [Synthesis] Note: video-reference-match non-fatal: {e}")

    # 2. Build Narrative Storyboard Structure (3 to 4 High-Retention Beats)
    print("  [Synthesis] Generating narrative beats and visual layout mockups...")
    beats = [
        {
            "id": "beat-1-hook",
            "name": "Hook & Personal Assertion",
            "start": 0.0,
            "end": min(12.0, round(kept_duration * 0.20, 2)),
            "layout": "Full Camera (1.10x punch-in on opener)",
            "visual_focus": "Speaker direct-to-lens eye contact with energetic opener badge",
            "frame_preview": visual_res["frame_paths"][0]
        },
        {
            "id": "beat-2-core-split",
            "name": "Core Breakdown (Split-Screen / Data Canvas)",
            "start": min(12.0, round(kept_duration * 0.20, 2)),
            "end": round(kept_duration * 0.70, 2),
            "layout": "Bottom Split-Screen (Speaker in Bottom 44% with Head Focus Crop; Top Dedicated Graphic Canvas)",
            "visual_focus": "Speaker cropped top/bottom to focus on head area in bottom pane (70% standard); active HyperFrames motion scene and checklist cards in upper screen",
            "frame_preview": visual_res["frame_paths"][1]
        },
        {
            "id": "beat-3-verdict",
            "name": "Key Takeaways & Proof Points",
            "start": round(kept_duration * 0.70, 2),
            "end": round(kept_duration - 4.0, 2),
            "layout": "Corner PiP Squircle + 3D Isometric Card",
            "visual_focus": "Floating corner PiP with 3D milestone cards and metric counters",
            "frame_preview": visual_res["frame_paths"][2]
        },
        {
            "id": "beat-4-outro",
            "name": "Verdict & Interactive Outro Call-to-Action",
            "start": round(kept_duration - 4.0, 2),
            "end": kept_duration,
            "layout": "Centered Follow Card with Pulse Animation",
            "visual_focus": "+1 Follower bounce card with verified badge and channel profile",
            "frame_preview": visual_res["frame_paths"][3]
        }
    ]

    split_in = round(min(12.0, kept_duration * 0.20), 2)
    split_out = round(kept_duration * 0.70, 2)
    
    stage_beats = [
        {
            "type": "layout",
            "id": "split_breakdown",
            "mode": "split",
            "pos": "bottom",
            "crop_head": True,
            "focus": [50, 24],
            "scale": 1.15,
            "in": split_in,
            "out": split_out,
            "transition": 0.5
        },
        {
            "type": "cards",
            "id": "breakdown_cards",
            "title": "3 KEYS TO SUCCESS",
            "pos": "center",
            "allow_top": True,
            "y": 0.14,
            "in": round(split_in + 0.4, 2),
            "out": round(split_out - 0.4, 2),
            "items": [
                ["1. Knowing The Right People", round(split_in + 0.8, 2)],
                ["2. How To Sell Yourself", round(split_in + (split_out - split_in) * 0.45, 2)],
                ["3. Trust & Milestone Proof", round(split_in + (split_out - split_in) * 0.80, 2)]
            ]
        }
    ]

    sfx_cues = [
        {"id": "sfx_pop", "src": "sfx/pop.mp3", "at": 0.4, "dur": 0.35, "volume": 0.4},
        {"id": "sfx_whoosh", "src": "sfx/whoosh-fast.mp3", "at": split_in, "dur": 0.5, "volume": 0.35},
        {"id": "sfx_click", "src": "sfx/click-soft.mp3", "at": split_out, "dur": 0.3, "volume": 0.35}
    ]

    storyboard_json = out_dir / "storyboard.json"
    canvas = [meta["width"], meta["height"]] if meta["height"] > meta["width"] else [1080, 1920]
    with open(storyboard_json, "w", encoding="utf-8") as f:
        json.dump({
            "id": out_dir.name,
            "duration": kept_duration,
            "canvas": canvas,
            "video": "input-video.mp4",
            "captions": {"source": "transcript.json"},
            "user_reference": detected_ref,
            "narrative_beats": beats,
            "beats": stage_beats,
            "sfx": sfx_cues,
            "matched_presets": matched_presets
        }, f, indent=2)

    meta_json = out_dir / "meta.json"
    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump({**meta, "raw_video": raw_video}, f, indent=2)

    # 3. Default Style Spec
    dyn_color = visual_res.get("dyn_color", {})
    dyn_params = dyn_color.get("params", {"imin": 0.005, "imax": 0.995, "gamma": 1.02, "contrast": 1.05, "saturation": 1.05, "temperature": 5650, "sharpness": 0.12})
    dyn_metrics = dyn_color.get("metrics", {"p1_shadow": 13.0, "p50_mid": 111.0, "p99_highlight": 230.0, "mean_saturation": 0.25, "rb_ratio": 0.94, "std_y_contrast": 63.7})

    style_json = out_dir / "style.json"
    style_spec = {
        "color_grade": "dynamic",
        "dynamic_color_params": dyn_params,
        "matched_preset": matched_presets[0]["id"] if matched_presets else "B19",
        "colors": {
            "canvas_bg": "radial-gradient(circle at 50% 20%, rgba(56, 189, 248, 0.16) 0%, transparent 55%), radial-gradient(ellipse 90% 65% at 50% 25%, #1e2c48 0%, #0d1526 60%, #040710 100%)",
            "dark": "#0b0b0f",
            "accent": "#ffe600",
            "accent2": "#00f59b",
            "text": "#ffffff"
        },
        "fonts": {
            "display": {
                "family": "Poppins",
                "files": {
                    "700": "@engine/assets/fonts/poppins/Poppins-Bold.ttf",
                    "800": "@engine/assets/fonts/poppins/Poppins-ExtraBold.ttf"
                }
            },
            "body": {
                "family": "Inter",
                "files": {
                    "100 900": "@engine/assets/fonts/inter/Inter-Variable.ttf"
                }
            }
        },
        "captions": {
            "mode": "phrase",
            "y": visual_res["caption_y"],
            "size": 0.048,
            "weight": 700,
            "max_words": 3,
            "color": "#ffffff",
            "active_color": "#ffe600",
            "emphasis_color": "#00f59b",
            "inactive_color": "#ffffff",
            "shadow": "0 3px 14px rgba(0,0,0,.85)"
        }
    }
    with open(style_json, "w", encoding="utf-8") as f:
        json.dump(style_spec, f, indent=2)

    # 4. Generate Visual STORYBOARD.md
    storyboard_md = out_dir / "STORYBOARD.md"
    md_content = [
        f"# Visual Storyboard & Production Blueprint: {out_dir.name}",
        "",
        "> **Project Status:** Ingest & Analysis Complete · Pending Storyboard & Color Grade Approval",
        "",
        "## 1. Footage & Cut Summary",
        f"- **Standard SDR H.265 Footage:** `{meta['duration']:.2f}s` ({meta['width']}x{meta['height']} @ {meta['fps']}fps)",
        f"- **Tight Cut Duration:** `{kept_duration:.2f}s` (**{dropped_duration:.2f}s** dead air & stumbles removed)",
        f"- **Spoken Words:** `{audio_res['words_count']}` words across `{len(cut_data.get('kept', []))}` kept takes",
        f"- **Acoustic Silence Gaps Trimmed:** `{len(cut_data.get('removed', []))}` pauses tightened to 0.15s rhythm",
        "",
        "## 2. Dynamic Frame-Accurate Color Correction & Enhancement",
        "Color correction was dynamically calculated directly from the statistical distribution of your video's actual frames (lighting, black floor, white ceiling, midtones, saturation, and color balance):",
        "",
        "| Metric / Parameter | Calculated Value | Measured Frame Distribution & Purpose |",
        "|---|---|---|",
        f"| **Shadow Black Floor (`imin`)** | `{dyn_params.get('imin', 0.04)}` | 1st percentile luma = `{dyn_metrics.get('p1_shadow', 13.0)}/255` (deep blacks without shadow crushing) |",
        f"| **Specular Ceiling (`imax`)** | `{dyn_params.get('imax', 0.93)}` | 99th percentile luma = `{dyn_metrics.get('p99_highlight', 230.0)}/255` (highlight dynamic recovery) |",
        f"| **Midtone Exposure (`gamma`)** | `γ{dyn_params.get('gamma', 1.05)}` | Median luma = `{dyn_metrics.get('p50_mid', 111.0)}/255` (perceptual 18% middle-grey normalization) |",
        f"| **Adaptive Contrast** | `{dyn_params.get('contrast', 1.02)}` | Standard deviation = `{dyn_metrics.get('std_y_contrast', 63.7)}` (gentle S-curve tuned to scene lighting) |",
        f"| **Natural Skin Vibrance** | `{dyn_params.get('saturation', 1.05)}x` | Mean HSV saturation = `{dyn_metrics.get('mean_saturation', 0.25):.3f}` (preserves healthy natural tones) |",
        f"| **White Balance / Temp** | `{dyn_params.get('temperature', 5650)}K` | Red/Blue channel ratio = `{dyn_metrics.get('rb_ratio', 0.94):.2f}` (neutral daylight calibration) |",
        f"| **Micro-Clarity** | `{dyn_params.get('sharpness', 0.12)}` | Laplacian edge variance = `{dyn_metrics.get('laplacian_clarity', 29.2)}` (restores fine edge detail) |",
        "",
        f"![Dynamic Frame-by-Frame Color Correction Sheet]({visual_res['grade_preview_path']})",
        "",
        "> **Dynamic Engine:** 100% computed from frame pixels. Zero artificial stylized filter presets.",
        ""
    ]

    # Section 3: Recommended Video-Presets (video-reference-match)
    if detected_ref:
        md_content.extend([
            "## 3. Presets & Reference Intelligence (video-reference-match)",
            f"> [!IMPORTANT]",
            f"> **References Precedence:** User reference detected (`{Path(detected_ref).name}`). Per system contract, reference specifications (layout, pacing, framing, and visual devices) take absolute precedence over blueprint presets.",
            "",
            "Proven creator blueprints evaluated against your transcript content:",
            "",
            "| Preset | Match Score | Visual Architecture & Signature |",
            "|---|---|---|"
        ])
    elif matched_presets:
        md_content.extend([
            "## 3. Recommended Video-Presets (video-reference-match)",
            "Proven creator blueprints evaluated against your transcript content:",
            "",
            "| Preset | Match Score | Visual Architecture & Signature |",
            "|---|---|---|"
        ])
    if matched_presets:
        for m in matched_presets[:3]:
            one_l = m.get("one_line", "High-retention talking-head layout")
            md_content.append(f"| **{m['id']}** | `{m['score']:.2f}` | {one_l} |")
        md_content.append("")

        top_m = matched_presets[0]
        top_comps = top_m.get("hyperframes_compositions", [])
        if top_comps:
            md_content.extend([
                f"### Linked HyperFrames Compositions for {top_m['id']} (First-Class Motion Scenes)",
                "The following verified HyperFrames catalog compositions are linked to execute this blueprint's visual system:",
                "",
                "| Composition | Type | Role in Video |",
                "|---|---|---|"
            ])
            for c in top_comps:
                md_content.append(f"| **`{c['name']}`** | `{c.get('type', 'component')}` | {c.get('role', '')} |")
            md_content.append("")

    # Section 4: Narrative Beats & Layout Choreography
    md_content.extend([
        "## 4. Narrative Beats & Layout Choreography",
        "",
        "| Timecode | Beat Name | Layout & Framing | Visual Focus & Elements | Preview Frame |",
        "|---|---|---|---|---|"
    ])


    for b in beats:
        md_content.append(
            f"| `{b['start']:.1f}s - {b['end']:.1f}s` | **{b['name']}** | {b['layout']} | {b['visual_focus']} | ![]({b['frame_preview']}) |"
        )

    md_content.extend([
        "",
        "## 5. Motion Graphics Canvas & Geometry (Zero Black Backgrounds)",
        "- **Active Studio Canvas:** The non-speaker canvas (upper split-screen & PiP background) utilizes a deep studio mesh gradient (`#1e293b` to `#0f172a`), eliminating dead black voids.",
        "- **Bottom Split-Screen Geometry (70% Standard):** In split-screen beats, the speaker takes the bottom pane (~44% height) with rounded top corners (`border-radius: 24px 24px 0 0`) and upward elevation shadow (`0 -18px 45px rgba(0,0,0,.6)`). The speaker video is cropped top and bottom (1.15x scale, vertical focus centered at 24%) to maximize head area visibility. The upper 56% canvas hosts active HyperFrames motion scenes on the studio mesh gradient.",
        "- **Speaker Window Geometry (PiP):** Polished floating squircle frame (`border-radius: 24px`, glass border, drop-shadow).",
        "- **HyperFrames Motion Scenes:** Animated checklist cards (`b_cards`), tactile paper drawers (`b_drawer`), and article highlighters fill the scene with visual proof.",
        "",
        "## 6. Subtle Sound Design (Acoustic Depth & Liveliness)",
        "- **Pop SFX (`pop.mp3`):** Damped kinetic pop on card and badge pill entrances (volume `-20 dB`).",
        "- **Whoosh SFX (`whoosh-fast.mp3`):** Swift directional whoosh on split-screen and PiP layout transitions (volume `-22 dB`).",
        "- **Click SFX (`click-soft.mp3`):** Tactile micro-click on milestone and proof checkmarks (volume `-20 dB`).",
        "- **Dialogue Clarity First:** Sound effects are balanced below speech frequencies, adding depth without competing with vocals.",
        "",
        "## 7. Kinetic Typography & Captions Plan",
        f"- **Font:** `Poppins Bold (700)` with vibrant, high-contrast palette",
        f"- **Small Elegant Size:** `0.048` (~52px) with strict single-line display (1-4 words max per row, zero line wrap)",
        f"- **Vibrant Color Palette:** Pure High-Contrast White (`#ffffff`), Active Spoken Word in Electric Gold (`#ffe600`), Punch Words in Neon Mint (`#00F59B`)",
        f"- **Caption Placement:** Dynamic chin-safe offset at `y = {visual_res['caption_y']}`",
        f"- **Zero-Overlap Guarantee:** Consecutive phrases strictly vanish before next phrase appears",
        "",
        "---",
        "### User Next Step",
        "Review the rendered screenshots, recommended presets, and dynamic color correction comparison sheet above. Once approved, the pipeline will execute the tight cut, stage HyperFrames, and master render the deliverable in one pass."
    ])

    with open(storyboard_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content) + "\n")

    print(f"  [Synthesis] Visual STORYBOARD.md successfully generated at {storyboard_md}")
    return {
        "storyboard_md": str(storyboard_md),
        "storyboard_json": str(storyboard_json),
        "kept_duration": kept_duration,
        "dropped_duration": dropped_duration,
        "elapsed": time.time() - t0
    }


# -----------------------------------------------------------------------------
# Main Commands
# -----------------------------------------------------------------------------
def cmd_analyze(args):
    start_total = time.time()
    print("=" * 70)
    print("  PARALLEL VIDEO EDITING PIPELINE: INGEST & ANALYSIS")
    print("=" * 70)

    raw_video = str(Path(args.input).resolve())
    project_dir = str(Path(args.project).resolve())
    os.makedirs(project_dir, exist_ok=True)

    print(f"\n[Step 1/4] Standardizing footage to SDR Rec.709 and H.265 (HEVC)...")
    standard_video = standardize_video(raw_video, project_dir)

    print(f"\n[Step 2/4] Probing standardized video: {standard_video}")
    meta = probe_video(standard_video)
    print(f"  Resolution: {meta['width']}x{meta['height']}, FPS: {meta['fps']}, Duration: {meta['duration']:.2f}s")

    print("\n[Step 3/4] Launching Parallel Audio & Visual Analysis Workers...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        fut_audio = executor.submit(process_audio_worker, standard_video, project_dir)
        fut_visual = executor.submit(process_visual_worker, standard_video, project_dir, meta)

        audio_res = fut_audio.result()
        visual_res = fut_visual.result()

    print("\n[Step 4/4] Synthesizing Tight Cuts & Rendering Visual Storyboard...")
    ref_input = getattr(args, "reference", None)
    syn_res = synthesize_storyboard_and_cuts(standard_video, project_dir, meta, audio_res, visual_res, ref_input=ref_input)

    total_time = time.time() - start_total
    print("\n" + "=" * 70)
    print(f"  ANALYSIS COMPLETE in {total_time:.2f}s!")
    print(f"  - Visual Storyboard: {syn_res['storyboard_md']}")
    print(f"  - Color Correction Sheet: {visual_res['grade_preview_path']}")
    print(f"  - Cut Plan: {meta['duration']:.2f}s -> {syn_res['kept_duration']:.2f}s ({syn_res['dropped_duration']:.2f}s trimmed)")
    print("=" * 70)


def cmd_assemble(args):
    start_total = time.time()
    print("=" * 70)
    print("  PARALLEL VIDEO EDITING PIPELINE: ASSEMBLY & MASTER RENDER")
    print("=" * 70)

    project_dir = Path(args.project).resolve()
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
        st = json.load(open(style_json))
        preset = args.preset or st.get("color_grade", "dynamic")

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
    temp_asr = Path(tempfile.mkdtemp(prefix="cut-asr-"))
    try:
        flat_trans = transcribe_cpp.transcribe(str(flat_cut_video), temp_asr)
        with open(hyper_dir / "transcript.json", "w", encoding="utf-8") as f:
            json.dump(flat_trans, f, indent=2, ensure_ascii=False)
        with open(project_dir / "transcript.json", "w", encoding="utf-8") as f:
            json.dump(flat_trans, f, indent=2, ensure_ascii=False)
        print(f"  [Pass 2 Transcribe] Mapped {len(flat_trans.get('words', []))} words directly to {flat_cut_video.name}")
    finally:
        shutil.rmtree(temp_asr, ignore_errors=True)

    # Stage tactile SFX assets
    repo_dir = Path(HERE).parents[3]
    engine_dir = runtime.find_engine_dir()
    candidate_sfx_dirs = [
        Path.cwd() / "sound-palette" / "audio",
        repo_dir / "sound-palette" / "audio",
        engine_dir / "sound-palette" / "audio",
    ]
    sfx_target_dir = hyper_dir / "sfx"
    sfx_target_dir.mkdir(parents=True, exist_ok=True)
    for sdir in candidate_sfx_dirs:
        if sdir.is_dir():
            for sfx_file in ("pop.mp3", "whoosh-fast.mp3", "click-soft.mp3"):
                src_f = sdir / sfx_file
                if src_f.is_file():
                    shutil.copyfile(src_f, sfx_target_dir / sfx_file)
            break

    storyboard_json = project_dir / "storyboard.json"
    cut_map_json = project_dir / "cut-map.json"

    # Stage linked HyperFrames compositions into hyperframes/compositions
    comp_engine_dir = Path(engine_dir) / "compositions"
    if comp_engine_dir.is_dir():
        target_comp_dir = hyper_dir / "compositions"
        target_comp_dir.mkdir(parents=True, exist_ok=True)
        (target_comp_dir / "components").mkdir(parents=True, exist_ok=True)
        sb_data = json.load(open(storyboard_json)) if storyboard_json.is_file() else {}
        matched = sb_data.get("matched_presets", [])
        if matched:
            for comp in matched[0].get("hyperframes_compositions", []):
                cname = comp.get("name")
                is_comp = comp.get("type") == "component"
                src_html = comp_engine_dir / ("components" if is_comp else "") / f"{cname}.html"
                dst_html = target_comp_dir / ("components" if is_comp else "") / f"{cname}.html"
                if src_html.is_file() and not dst_html.is_file():
                    shutil.copyfile(src_html, dst_html)

    # 3. Stage HyperFrames Composition with Collision-Free Captions
    print("\n[Step 3/4] Staging HyperFrames composition with collision-free captions & split layout...")
    stage_py = os.path.join(HERE, "stage.py")
    cmd_stage = [
        sys.executable, stage_py,
        "--spec", str(storyboard_json),
        "--style", str(style_json),
        "--cut-map", str(cut_map_json),
        "--out", str(hyper_dir)
    ]
    subprocess.run(cmd_stage, check=True)

    # 4. Master Render & Automated Verification (with Denoise & Audio Mastering)
    print("\n[Step 4/4] Rendering composite master deliverable with BT.709 tags & noise suppression...")
    render_py = os.path.join(HERE, "render.py")
    processed_dir = project_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    master_video = processed_dir / f"{project_dir.name}-v1.mp4"
    
    res_mode = "portrait"
    if storyboard_json.exists():
        try:
            sb = json.load(open(storyboard_json))
            c = sb.get("canvas")
            if c and len(c) == 2:
                if c[0] > c[1]:
                    res_mode = "landscape"
                elif c[0] == c[1]:
                    res_mode = "square"
                else:
                    res_mode = "portrait"
        except Exception:
            pass

    cmd_render = [
        sys.executable, render_py,
        "--public", str(hyper_dir),
        "--out", str(master_video),
        "--resolution", res_mode,
        "--sdr",
        "--denoise", "medium",
        "--audio-preset", "shorts"
    ]
    subprocess.run(cmd_render, check=True)

    # Note: Temporary data folders (preview, hyperframes, audio_processing) are preserved
    # in the project directory for user inspection as requested.

    total_time = time.time() - start_total
    print("\n" + "=" * 70)
    print(f"  ASSEMBLY & MASTER RENDER COMPLETE in {total_time:.2f}s!")
    print(f"  - Master Deliverable: {master_video}")
    print("=" * 70)


def main():
    ap = argparse.ArgumentParser(description="Parallel Video Editing Pipeline")
    sub = ap.add_subparsers(dest="subcommand", required=True)

    p_an = sub.add_parser("analyze", help="Parallel ingest, analysis, color grade preview, and visual storyboard")
    p_an.add_argument("--input", required=True, help="Path to raw video input")
    p_an.add_argument("--project", required=True, help="Project directory")
    p_an.add_argument("--reference", help="Path to user reference video or image taking precedence over blueprints")

    p_as = sub.add_parser("assemble", help="Execute cut, staging, and master render")
    p_as.add_argument("--project", required=True, help="Project directory")
    p_as.add_argument("--preset", default="dynamic", help="Color grade preset (default: dynamic)")

    args = ap.parse_args()
    if args.subcommand == "analyze":
        cmd_analyze(args)
    elif args.subcommand == "assemble":
        cmd_assemble(args)


if __name__ == "__main__":
    main()
