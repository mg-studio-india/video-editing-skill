#!/usr/bin/env python3
"""The video pipeline: analyze -> (recut) -> approve -> assemble.

analyze   ingest (constant frame rate), audio pass 1 (dereverb + DeepFilterNet, once), Hinglish transcript snapped to
          the speech energy, the tight word-safe cut (active), the flat cut with a fade-out tail, flat-time transcript,
          frames/contact sheet/grade preview, references, brand files and REVIEW.md.
recut     change the cut (drop/restore ranges, pause length, tail) and rebuild the flat cut and its transcript.
approve   record the user's approval after checking the storyboard, cut, style, research and catalog blocks.
assemble  grade, optional reframe, stage the composition (captions, catalog blocks, SFX, fade), render, audio
          pass 2, verify, publish Exports/<project>-vN.mp4.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from html.parser import HTMLParser
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runtime  # noqa: E402
runtime.ensure_project_venv()
import grade  # noqa: E402
import pipeline_synthesis as synth  # noqa: E402

SKILLS = Path(HERE).parents[2]
VOICE_CLEAN = SKILLS / "video-audio" / "tools" / "voice-clean.py"
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mxf"}
STANDARD_FPS = (24, 25, 30, 50, 60)
DEFAULT_TAIL = 1.5
DEFAULT_FADE = 1.0


def sh(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def py(script: str, *args) -> None:
    sh([sys.executable, os.path.join(HERE, script), *args])


def read_json(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path: Path, data) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def workspace(project: str) -> tuple[Path, Path]:
    p = Path(project).expanduser().resolve()
    if p.name == ".video-pipeline":
        return p.parent, p
    return p, p / ".video-pipeline"


# ---------------------------------------------------------------- ingest
def probe(path: str) -> dict:
    data = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                      "stream=codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,start_time,"
                                      "pix_fmt,color_transfer,color_primaries:format=duration,start_time",
                                      "-of", "json", path], capture_output=True, text=True, check=True).stdout)
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    if v is None:
        raise RuntimeError(f"No video stream in {path}")

    def rate(text):
        try:
            n, d = map(float, str(text).split("/"))
            return n / d if d else 0.0
        except ValueError:
            return 0.0
    return {"video": v, "audio": a, "duration": float(data.get("format", {}).get("duration") or 0.0),
            "r_rate": rate(v.get("r_frame_rate")), "avg_rate": rate(v.get("avg_frame_rate")),
            "width": int(v.get("width") or 0), "height": int(v.get("height") or 0)}


def rotation_of(path: str) -> int:
    """Display rotation of the first video stream (phones store landscape frames + a rotation matrix)."""
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream_side_data=rotation:stream_tags=rotate", "-of", "json", path], capture_output=True, text=True)
    try:
        st = (json.loads(p.stdout or "{}").get("streams") or [{}])[0]
    except ValueError:
        return 0
    for sd in st.get("side_data_list") or []:
        if sd.get("rotation") not in (None, ""):
            try:
                return int(float(sd["rotation"])) % 360
            except (TypeError, ValueError):
                pass
    try:
        return int(float((st.get("tags") or {}).get("rotate", 0))) % 360
    except (TypeError, ValueError):
        return 0


def target_fps(info: dict) -> int:
    fps = info["avg_rate"] or info["r_rate"] or 30.0
    return min(STANDARD_FPS, key=lambda s: abs(s - fps)) if abs(min(STANDARD_FPS, key=lambda s: abs(s - fps)) - fps) <= 1.5 \
        else int(round(fps))


def ingest(source: str, work: Path) -> dict:
    """Constant-frame-rate, SDR, video-only copy + 48 kHz source audio whose sample 0 is the first video frame."""
    raw = work / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    video_out, wav_out, sig_path = raw / "source-video.mp4", work / "audio" / "source.wav", raw / "source.json"
    st = Path(source).stat()
    sig = {"path": str(Path(source).resolve()), "size": st.st_size, "mtime_ns": st.st_mtime_ns, "version": 2}
    info = probe(source)
    fps = target_fps(info)
    if read_json(sig_path) == sig and video_out.is_file() and wav_out.is_file():
        print("  [ingest] reusing the constant-frame-rate copy")
    else:
        v = info["video"]
        hdr = "arib-std-b67" in str(v.get("color_transfer")) or "smpte2084" in str(v.get("color_transfer")) \
            or "bt2020" in str(v.get("color_primaries"))
        cfr = info["r_rate"] > 0 and abs(info["r_rate"] - info["avg_rate"]) / info["r_rate"] < 0.001 and \
            abs(info["r_rate"] - fps) < 0.01
        rotated = rotation_of(source) != 0          # re-encoding applies the rotation; a stream copy would not
        copyable = cfr and not hdr and not rotated and v.get("codec_name") in ("h264", "hevc") and v.get("pix_fmt") == "yuv420p"
        if copyable:
            print(f"  [ingest] source is already {fps} fps constant frame rate SDR; copying the picture")
            sh(["ffmpeg", "-y", "-v", "error", "-i", source, "-map", "0:v:0", "-c:v", "copy", "-an",
                "-movflags", "+faststart", video_out])
        else:
            why = "HDR -> SDR, " if hdr else ""
            print(f"  [ingest] {why}converting to {fps} fps constant frame rate (variable-rate phone video drifts)")
            vf = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,"
                  "format=yuv420p" if hdr else "format=yuv420p")
            if hdr and "zscale" not in subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout:
                vf = "colorspace=all=bt709:iprimaries=bt2020:ispace=bt2020nc:itrc=bt2020-10:format=yuv420p"
            sh(["ffmpeg", "-y", "-v", "error", "-i", source, "-map", "0:v:0", "-vf", vf, "-fps_mode", "cfr", "-r", str(fps),
                "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-g", str(fps), "-pix_fmt", "yuv420p",
                "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
                "-an", "-movflags", "+faststart+write_colr", video_out])
        wav_out.parent.mkdir(parents=True, exist_ok=True)
        if info["audio"] is not None:
            # sample 0 of the WAV = the first video frame: shift by the audio/video start offset
            offset = float(info["audio"].get("start_time") or 0) - float(info["video"].get("start_time") or 0)
            af = "adelay=%d:all=1" % round(offset * 1000) if offset > 0.0005 else (
                "atrim=start=%.6f,asetpts=PTS-STARTPTS" % -offset if offset < -0.0005 else "anull")
            sh(["ffmpeg", "-y", "-v", "error", "-i", source, "-map", "0:a:0", "-af", af + ",aresample=48000",
                "-t", "%.6f" % info["duration"], "-c:a", "pcm_f32le", wav_out])
        else:
            sh(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "%.6f" % info["duration"],
                "-c:a", "pcm_f32le", wav_out])
        write_json(sig_path, sig)
    out = probe(str(video_out))
    return {"video": str(video_out), "wav": str(wav_out), "has_audio": info["audio"] is not None,
            "width": out["width"], "height": out["height"], "fps": fps, "duration": out["duration"] or info["duration"],
            "source_video": str(Path(source).resolve())}


# ---------------------------------------------------------------- audio pass 1 + transcript
def audio_track(meta: dict, work: Path, args) -> dict:
    t0 = time.time()
    voice = work / "audio" / "voice-clean.wav"
    report_path = work / "audio" / "voice-clean.json"
    if meta["has_audio"]:
        print("  [audio] pass 1: dereverb + DeepFilterNet (once, lossless)")
        sh([sys.executable, VOICE_CLEAN, meta["wav"], "--out", voice, "--report", report_path,
            "--dereverb", args.dereverb, "--denoise", args.denoise])
    else:
        shutil.copyfile(meta["wav"], voice)
        write_json(report_path, {"pass": 1, "denoise": "off", "note": "source has no audio"})
    report = read_json(report_path, {})
    ab = ab_preview(meta["wav"], str(voice), work / "preview" / "audio-before-after.wav") if meta["has_audio"] else None

    transcript_path = work / "transcript.source.json"
    if meta["has_audio"]:
        print("  [audio] Hinglish transcript (whisper.cpp), snapped to the speech energy")
        args_t = [sys.executable, os.path.join(HERE, "transcribe.py"), str(voice), "--out", str(transcript_path), "--force"]
        if (work / "corrections.json").is_file():
            args_t += ["--fix", str(work / "corrections.json")]
        if args.names:
            args_t += ["--prompt", args.names]
        sh(args_t)
    else:
        write_json(transcript_path, {"language": "hi-Latn", "script": "hinglish", "words": [], "note": "no audio"})
    print(f"  [audio] done in {time.time() - t0:.1f}s")
    return {"voice": str(voice), "report": report, "transcript": str(transcript_path), "ab": ab}


def ab_preview(raw_wav: str, clean_wav: str, out: Path) -> str | None:
    """10 s of the original, a short gap, then the same 10 s cleaned, from the busiest stretch of speech."""
    import numpy as np
    import soundfile as sf
    try:
        x, rate = sf.read(clean_wav, dtype="float64")
        if x.ndim > 1:
            x = x.mean(axis=1)
        win = int(10 * rate)
        if len(x) <= win:
            start = 0
        else:
            env = np.convolve(np.abs(x[::480]), np.ones(1000) / 1000, mode="valid")
            start = int(np.argmax(env)) * 480 if len(env) else 0
            start = max(0, min(len(x) - win, start))
        t0 = start / rate
        out.parent.mkdir(parents=True, exist_ok=True)
        sh(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % t0, "-t", "10", "-i", raw_wav, "-ss", "%.3f" % t0, "-t", "10",
            "-i", clean_wav, "-f", "lavfi", "-t", "0.7", "-i", "anullsrc=r=48000:cl=mono", "-filter_complex",
            "[0:a]aresample=48000,aformat=channel_layouts=mono,loudnorm=I=-18:TP=-2,aresample=48000[r];"
            "[1:a]aresample=48000,aformat=channel_layouts=mono,loudnorm=I=-18:TP=-2,aresample=48000[c];"
            "[r][2:a][c]concat=n=3:v=0:a=1[a]", "-map", "[a]", "-c:a", "pcm_s16le", out])
        return str(out)
    except Exception as exc:  # noqa: BLE001 - a missing preview never blocks the edit
        print(f"  [audio] before/after preview skipped: {exc}")
        return None


# ---------------------------------------------------------------- visual analysis
def visual_track(meta: dict, work: Path) -> dict:
    t0 = time.time()
    video, duration = meta["video"], meta["duration"]
    preview = work / "preview"
    preview.mkdir(parents=True, exist_ok=True)
    run = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-vf", "select='gt(scene,0.28)',showinfo", "-an",
                          "-f", "null", "-"], capture_output=True, text=True)
    cuts = sorted({float(x) for x in re.findall(r"pts_time:([0-9.]+)", run.stderr) if 0.15 < float(x) < duration - 0.15})
    bounds = [0.0]
    for c in cuts:
        if c - bounds[-1] >= 0.45:
            bounds.append(c)
    bounds.append(duration)
    shots = [{"start": round(a, 3), "end": round(b, 3)} for a, b in zip(bounds, bounds[1:]) if b - a >= 0.15] \
        or [{"start": 0.0, "end": round(duration, 3)}]
    picks = list(enumerate(shots)) if len(shots) <= 48 else \
        [(i, shots[i]) for i in sorted({round(k * (len(shots) - 1) / 47) for k in range(48)})]
    frames = []
    for idx, shot in picks:
        ts = round((shot["start"] + shot["end"]) / 2, 3)
        f = preview / f"source-{idx + 1:03d}.jpg"
        grade.extract_frame(video, ts, str(f))
        frames.append({"id": f"visual-{idx + 1:03d}", "timestamp": ts, "shot_start": shot["start"],
                       "shot_end": shot["end"], "frame": str(f)})
    sheet = preview / "source-contact-sheet.jpg"
    try:
        from PIL import Image, ImageDraw
        cw, ch, lh, cols = 320, 220, 30, 4
        rows = (len(frames) + cols - 1) // cols
        img = Image.new("RGB", (cols * cw, rows * (ch + lh)), "#202124")
        draw = ImageDraw.Draw(img)
        for i, it in enumerate(frames):
            fr = Image.open(it["frame"]).convert("RGB")
            fr.thumbnail((cw, ch))
            x, y = (i % cols) * cw, (i // cols) * (ch + lh)
            img.paste(fr, (x + (cw - fr.width) // 2, y + (ch - fr.height) // 2))
            draw.text((x + 8, y + ch + 5), f"{it['id']} · {it['timestamp']:.2f}s", fill="white")
        img.save(sheet, quality=88)
    except Exception as exc:  # noqa: BLE001
        print(f"  [visual] contact sheet unavailable: {exc}")
        sheet = None
    stamps = [round(duration * p, 2) for p in (0.15, 0.38, 0.62, 0.85)]
    dyn = grade.calculate_dynamic_color_correction(video, timestamps=stamps)
    write_json(preview / "dynamic-grade.json", dyn)
    grade_sheet = preview / "grade-preview.jpg"
    grade.generate_frame_correction_sheet(video, str(grade_sheet), timestamps=stamps, preset="dynamic")
    chin_y = None
    try:
        import cv2
        img = cv2.imread(frames[len(frames) // 2]["frame"])
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml").detectMultiScale(gray, 1.2, 5)
            if len(faces):
                fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
                chin_y = round((fy + fh * 1.15) / img.shape[0], 3)
    except Exception:  # noqa: BLE001
        pass
    print(f"  [visual] {len(shots)} shots, {len(frames)} frames, chin y={chin_y} in {time.time() - t0:.1f}s")
    return {"evidence_frames": frames, "detected_shots": shots, "contact_sheet_path": str(sheet) if sheet else None,
            "grade_preview_path": str(grade_sheet), "dyn_color": dyn, "chin_y": chin_y}


# ---------------------------------------------------------------- cut
def map_words(words: list[dict], cut_map: dict) -> list[dict]:
    """Source-time words -> flat timeline through the exact cut-map (cuts sit in silence, so words never straddle)."""
    out = []
    segs = cut_map.get("segments", [])
    for w in words:
        s, e = float(w["start"]), float(w["end"])
        mid = (s + e) / 2
        seg = next((g for g in segs if g["src_start"] - 1e-6 <= mid <= g["src_end"] + 1e-6), None)
        if seg is None:
            continue
        shift = seg["flat_start"] - seg["src_start"]
        fs = max(seg["flat_start"], s + shift)
        fe = min(seg["flat_end"], e + shift)
        if fe - fs < 0.02:
            continue
        out.append({**w, "start": round(fs, 3), "end": round(fe, 3), "src_start": round(s, 3)})
    return out


def build_cut(work: Path, meta: dict, voice: str, args) -> tuple[dict, dict, list[dict]]:
    cmd = ["--transcript", str(work / "transcript.source.json"), "--audio", voice, "--duration", "%.3f" % meta["duration"],
           "--out-dir", str(work), "--max-pause", str(args.max_pause)]
    for r in args.drop or []:
        cmd += ["--drop", r]
    for r in args.restore or []:
        cmd += ["--restore", r]
    if args.keep_retakes:
        cmd.append("--keep-retakes")
    if args.keep_fillers:
        cmd.append("--keep-fillers")
    py("cut.py", *cmd)
    hyper = work / "hyperframes"
    hyper.mkdir(parents=True, exist_ok=True)
    py("apply-cut.py", "--input", meta["video"], "--audio", voice, "--cut-list", str(work / "cut-list.json"),
       "--out", str(hyper / "input-video.mp4"), "--voice-out", str(hyper / "voice.wav"), "--tail", str(args.tail),
       "--preset", "fast")
    cut = read_json(work / "cut-list.json")
    cut_map = read_json(work / "cut-map.json")
    src = read_json(work / "transcript.source.json", {})
    flat_words = map_words(src.get("words", []), cut_map)
    flat = {**{k: v for k, v in src.items() if k not in ("words", "segments", "dropped_no_speech")},
            "timeline": "flat", "duration": cut_map["flat_duration"], "words": flat_words}
    write_json(hyper / "transcript.json", flat)
    write_json(work / "transcript.json", flat)
    return cut, cut_map, flat_words


def scaffold_storyboard(work: Path, project: str, meta: dict, cut_map: dict, visual: dict, keep_existing: bool) -> None:
    path = work / "storyboard.json"
    sb = read_json(path, {}) if keep_existing else {}
    w, h = meta["width"], meta["height"]
    sb.setdefault("id", re.sub(r"[^A-Za-z0-9_-]+", "-", project).strip("-") or "edit")
    sb.setdefault("canvas", [1080, 1920] if h > w else ([1920, 1080] if w > h else [1080, 1080]))
    sb["fps"] = int(round(eval_fraction(cut_map.get("fps", "30/1"))))
    sb["duration"] = cut_map["flat_duration"]
    sb.setdefault("video", "input-video.mp4")
    sb.setdefault("captions", {"source": "transcript.json", "keywords": []})
    end = dict(sb.get("end") or {})
    end["fade"] = round(min(float(end.get("fade", DEFAULT_FADE)), cut_map["tail"]), 3) if cut_map["tail"] > 0 else 0.0
    sb["end"] = end
    if visual.get("chin_y") is not None:
        sb.setdefault("chin_y", visual["chin_y"])
    sb.setdefault("beats", [])
    sb.setdefault("sfx", [])
    sb["source_evidence_sha256"] = synth.hash_file(work / "source-evidence.json")
    write_json(path, sb)


def eval_fraction(text: str) -> float:
    try:
        n, d = str(text).split("/")
        return float(n) / float(d)
    except ValueError:
        return float(text)


# ---------------------------------------------------------------- commands
def cmd_analyze(args):
    t_start = time.time()
    project_root = Path(args.project).expanduser().resolve()
    project_root.mkdir(parents=True, exist_ok=True)
    work = project_root / ".video-pipeline"
    work.mkdir(parents=True, exist_ok=True)
    src = Path(args.input).expanduser().resolve()
    if src.is_dir():
        root = src / "raw" if (src / "raw").is_dir() else src
        skip = {".video-pipeline", "Exports", "references", "brand"}
        found = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXT
                       and not (skip & set(p.relative_to(root).parts))
                       and not any(part.startswith(".") for part in p.relative_to(root).parts))
        if len(found) != 1:
            names = "\n".join(f"  - {p}" for p in found[:30]) or "  (none)"
            raise RuntimeError(f"Choose one source video; found {len(found)}:\n{names}")
        src = found[0]
    if not src.is_file() or src.suffix.lower() not in VIDEO_EXT:
        raise RuntimeError(f"Input must be a video file or a folder with exactly one: {src}")

    print("[1/5] ingest")
    meta = ingest(str(src), work)
    print(f"  {meta['width']}x{meta['height']} · {meta['fps']} fps CFR · {meta['duration']:.2f}s")

    print("[2/5] audio pass 1 + Hinglish transcript  ||  frames, shots, grade preview")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        fa = pool.submit(audio_track, meta, work, args)
        fv = pool.submit(visual_track, meta, work)
        audio, visual = fa.result(), fv.result()

    print("[3/5] tight word-safe cut (active) + flat cut with %.1fs fade-out tail" % args.tail)
    cut, cut_map, flat_words = build_cut(work, meta, audio["voice"], args)

    print("[4/5] references, brand files, evidence")
    refs = synth.collect_references(project_root, args.reference, meta["source_video"], work)
    brand = synth.collect_brand(project_root, work)
    synth.write_evidence(work, meta, flat_words, visual, cut_map)
    catalog = synth.catalog_status(runtime.find_engine_dir())

    print("[5/5] review packet")
    scaffold_storyboard(work, project_root.name, meta, cut_map, visual, keep_existing=False)
    style_template = {"color_grade": "dynamic", "dynamic_color_params": visual["dyn_color"].get("params", {}),
                      "note": "copy a default style from video-style/styles into style.json, then apply brand files"}
    write_json(work / "style-template.json", style_template)
    write_json(work / "meta.json", {**meta, "project_root": str(project_root)})
    write_json(work / "gates.json", {"plan": {"status": "waiting", "reason": "new analysis"}})
    write_json(work / "project.json", {
        "schema": "video-pipeline-project/2", "project": project_root.name, "brief": args.prompt,
        "source": meta["source_video"], "workspace": ".video-pipeline", "exports": "Exports/",
        "steps": {"analysis": "done", "research": "todo", "storyboard": "todo", "approval": "waiting", "assembly": "todo"}})
    review = synth.write_review(work, project_root, meta, args.prompt, audio["report"],
                                read_json(audio["transcript"], {}), cut, cut_map, visual, refs, brand, catalog, audio["ab"])
    print("=" * 70)
    print(f"ANALYSIS DONE in {time.time() - t_start:.1f}s -> {review}")
    print(f"  cut: {cut_map['content_duration']:.2f}s kept of {meta['duration']:.2f}s (+{cut_map['tail']:.1f}s tail)")
    print(f"  audio before/after: {audio['ab']}")
    print(f"  catalog: {catalog['count']} items" if catalog["ok"] else f"  catalog: MISSING ({catalog.get('fix')})")
    print("=" * 70)


def cmd_recut(args):
    project_root, work = workspace(args.project)
    meta = read_json(work / "meta.json")
    if not meta:
        raise RuntimeError("Run analyze first.")
    old = read_json(work / "cut-list.json", {}).get("params", {})
    for key in ("max_pause",):
        if getattr(args, key) is None:
            setattr(args, key, old.get(key, 0.28))
    if args.tail is None:
        args.tail = read_json(work / "cut-map.json", {}).get("tail", DEFAULT_TAIL)
    if not args.reset:
        args.drop = list(old.get("drop", [])) + list(args.drop or [])
        args.restore = list(old.get("restore", [])) + list(args.restore or [])
        args.keep_retakes = args.keep_retakes or bool(old.get("keep_retakes"))
        args.keep_fillers = args.keep_fillers or bool(old.get("keep_fillers"))
    voice = str(work / "audio" / "voice-clean.wav")
    cut, cut_map, flat_words = build_cut(work, meta, voice, args)
    evidence = read_json(work / "source-evidence.json", {})
    visual = {"evidence_frames": [{"id": s["id"], "timestamp": s["source_time"], "shot_start": s["shot"][0],
                                   "shot_end": s["shot"][1], "frame": str(work / s["frame"])}
                                  for s in evidence.get("visual_samples", [])],
              "detected_shots": evidence.get("detected_shots", [])}
    synth.write_evidence(work, meta, flat_words, visual, cut_map)
    scaffold_storyboard(work, project_root.name, meta, cut_map, {"chin_y": None}, keep_existing=True)
    write_json(work / "gates.json", {"plan": {"status": "waiting", "reason": "cut changed"}})
    print(f"recut: {cut_map['content_duration']:.2f}s kept (+{cut_map['tail']:.1f}s tail). Beat and SFX times in "
          "storyboard.json are on the old timeline: re-check them against hyperframes/transcript.json.")


# ---------------------------------------------------------------- catalog blocks
class _Meta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.variables = set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("data-composition-id"):
            self.ids.add(attrs["data-composition-id"])
        if attrs.get("data-composition-variables"):
            try:
                value = json.loads(attrs["data-composition-variables"])
                self.variables += [x.get("id") for x in value if isinstance(x, dict) and x.get("id")]
            except ValueError:
                pass


def catalog_dir() -> Path:
    configured = os.environ.get("VIDEO_COMPOSITIONS", "").strip()
    return (Path(configured).expanduser() if configured else runtime.find_engine_dir() / "compositions").resolve()


def selected_blocks(storyboard: dict) -> list[tuple[Path, Path]]:
    base = catalog_dir()
    out = []
    for beat in storyboard.get("beats", []):
        if beat.get("type") != "block":
            continue
        rel = Path(str(beat.get("src", "")).replace("\\", "/").removeprefix("compositions/"))
        if not str(rel) or rel.is_absolute() or ".." in rel.parts:
            raise RuntimeError(f"Unsafe catalog path in beat {beat.get('id')}: {beat.get('src')!r}")
        html = base / rel
        if not html.is_file():
            raise RuntimeError(f"Beat {beat.get('id')}: {rel} is not in the local HyperFrames catalog ({base}). "
                               "Search it with catalog.py search.")
        meta = _Meta()
        meta.feed(html.read_text(encoding="utf-8"))
        if str(beat.get("comp_id", "")) not in meta.ids:
            raise RuntimeError(f"Beat {beat.get('id')}: {rel.name} declares {sorted(meta.ids)}, not {beat.get('comp_id')!r}")
        unknown = sorted(set(beat.get("vars") or {}) - set(meta.variables))
        if unknown:
            raise RuntimeError(f"Beat {beat.get('id')}: {rel.name} has no variables {', '.join(unknown)}")
        out.append((html, rel))
    return out


ASSET_RE = re.compile(r"""(?:src|href)\s*=\s*["']([^"'#?]+)["']|url\(\s*["']?([^"')#?]+)["']?\s*\)""")


def stage_blocks(hyper: Path, storyboard: dict) -> None:
    """Copy only the chosen blocks (and the local files they reference) into the project's composition folder."""
    for html, rel in selected_blocks(storyboard):
        dest = hyper / "compositions" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        text = html.read_text(encoding="utf-8")
        for m in ASSET_RE.finditer(text):
            ref = (m.group(1) or m.group(2) or "").strip()
            if not ref or re.match(r"^(https?:|data:|//|/)", ref):
                continue
            src = (html.parent / ref).resolve()
            if src.is_file() and src.is_relative_to(catalog_dir()):
                target = (dest.parent / ref).resolve()
                if target.is_relative_to(hyper.resolve()):
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, target)
        if "caption" in html.name and (hyper / "transcript.json").is_file():
            import captions
            words = captions.load_words(str(hyper / "transcript.json"))
            cut_map = read_json(hyper.parent / "cut-map.json", {})
            cap = storyboard.get("captions") or {}
            groups = captions.group(words, cut_map.get("cuts", []), emphasis=list(cap.get("keywords", [])))
            canvas = storyboard.get("canvas", [1080, 1920])
            text, _ = captions.inject(text, groups, canvas[0], canvas[1], float(storyboard.get("duration", 0.0)))
        dest.write_text(text, encoding="utf-8")


def sfx_source(src: str, project_root: Path, work: Path) -> Path:
    raw = Path(src).expanduser()
    cands = [raw] if raw.is_absolute() else [work / "hyperframes" / raw, project_root / raw,
                                            SKILLS / "sound-palette" / "audio" / raw.name,
                                            SKILLS.parent / "sound-palette" / "audio" / raw.name,
                                            runtime.find_engine_dir() / "sound-palette" / "audio" / raw.name,
                                            work / "research" / "sounds" / raw.name]
    for c in cands:
        if c.is_file():
            return c.resolve()
    raise RuntimeError(f"Sound effect not found: {src} (use the sound palette, a project file, or research/sounds/)")


# ---------------------------------------------------------------- approval
def fingerprint(work: Path, project_root: Path) -> dict:
    names = ["resolved-spec.json", "storyboard.json", "style.json", "cut-list.json", "cut-map.json",
             "source-evidence.json", "references/reference-index.json", "context/brand-inputs.json"]
    if (work / "research" / "research.json").is_file():
        names.append("research/research.json")
    out = {}
    for name in names:
        p = work / name
        if not p.is_file():
            raise RuntimeError(f"Approval input is missing: {p}")
        out[name] = synth.hash_file(p)
    sb = read_json(work / "storyboard.json", {})
    for html, rel in selected_blocks(sb):
        out[f"block:{rel.as_posix()}"] = synth.hash_file(html)
    for cue in sb.get("sfx", []):
        out[f"sfx:{cue.get('id')}"] = synth.hash_file(sfx_source(str(cue.get("src", "")), project_root, work))
    return out


def refs_of(item: dict) -> list:
    return list(item.get("refs") or item.get("source_refs") or [])


def cmd_approve(args):
    project_root, work = workspace(args.project)
    if not args.user_approved:
        raise RuntimeError("Run approve only after the user explicitly approved the plan (--user-approved).")
    spec = read_json(work / "resolved-spec.json")
    sb = read_json(work / "storyboard.json")
    style = read_json(work / "style.json")
    cut_map = read_json(work / "cut-map.json")
    evidence = read_json(work / "source-evidence.json")
    for name, value in (("resolved-spec.json", spec), ("storyboard.json", sb), ("style.json", style),
                        ("cut-map.json", cut_map), ("source-evidence.json", evidence)):
        if not value:
            raise RuntimeError(f"{name} is missing or unreadable in {work}")
    answers = spec.get("user_answers") or {}
    missing = [k for k in ("platform_aspect", "style", "cut") if not answers.get(k)]
    if missing:
        raise RuntimeError("resolved-spec.json user_answers must record: " + ", ".join(missing))
    canvas = sb.get("canvas")
    if not (isinstance(canvas, list) and len(canvas) == 2 and all(isinstance(x, (int, float)) and x > 0 for x in canvas)):
        raise RuntimeError("storyboard.json needs canvas [width, height].")
    m = re.findall(r"(\d+(?:\.\d+)?)\s*[:/]\s*(\d+(?:\.\d+)?)", str(answers.get("platform_aspect")))
    if len(m) == 1 and abs(float(m[0][0]) / float(m[0][1]) - canvas[0] / canvas[1]) > 0.015:
        raise RuntimeError("storyboard canvas does not match the chosen aspect ratio.")
    meta = read_json(work / "meta.json", {})
    src_ratio = meta.get("width", 1) / max(1, meta.get("height", 1))
    if abs(src_ratio - canvas[0] / canvas[1]) > 0.02 and not sb.get("reframe"):
        raise RuntimeError("The canvas aspect differs from the footage: add \"reframe\": {\"aspect\": \"W:H\"} "
                           "(face-tracked crop) or {\"mode\": \"center\"} to storyboard.json.")
    D = float(sb.get("duration", -1))
    if abs(D - float(cut_map["flat_duration"])) > 0.05:
        raise RuntimeError(f"storyboard duration {D} must equal the cut ({cut_map['flat_duration']}s incl. tail). "
                           "Run recut or fix the storyboard.")
    if sb.get("source_evidence_sha256") != synth.hash_file(work / "source-evidence.json"):
        raise RuntimeError("storyboard.json was built for an older analysis/cut; update source_evidence_sha256 and beat times.")
    valid = {x["id"] for x in evidence.get("speech_segments", [])} | \
            {x["id"] for x in evidence.get("visual_samples", []) if x.get("flat_time") is not None}
    research = read_json(work / "research" / "research.json", {}) or {}
    for fact in research.get("facts", []):
        if re.fullmatch(r"research-\d{3}", str(fact.get("id", ""))) and re.match(r"https?://", str(fact.get("source_url", ""))):
            valid.add(fact["id"])
    ids = set()
    for kind, items in (("beat", sb.get("beats", [])), ("sfx", sb.get("sfx", []))):
        for it in items:
            iid = str(it.get("id", ""))
            if not re.fullmatch(r"[A-Za-z0-9_-]+", iid) or iid in ids:
                raise RuntimeError(f"Every {kind} needs a unique simple id (got {iid!r}).")
            ids.add(iid)
            refs = refs_of(it)
            bad = [r for r in refs if r not in valid]
            if not refs or bad:
                raise RuntimeError(f"{kind} {iid}: refs must cite speech-/visual- ids from source-evidence.json or "
                                   f"research-NNN facts with a source_url (bad: {bad or 'none given'}).")
            t0 = it.get("in", it.get("at"))
            t1 = it.get("out", (t0 or 0) + float(it.get("dur", 0.5)))
            if not isinstance(t0, (int, float)) or not isinstance(t1, (int, float)) or t0 < 0 or t1 <= t0 or t1 > D + 0.05:
                raise RuntimeError(f"{kind} {iid} has an invalid time range on the flat timeline (0-{D:.2f}s).")
    selected_blocks(sb)
    for cue in sb.get("sfx", []):
        sfx_source(str(cue.get("src", "")), project_root, work)
    music = (spec.get("audio") or {}).get("music_path")
    if music:
        mp = (project_root / music).resolve() if not Path(music).is_absolute() else Path(music).resolve()
        if not mp.is_file() or not mp.is_relative_to(project_root):
            raise RuntimeError("Music must be a file inside the project folder.")
    gate = {"plan": {"status": "approved", "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "note": args.note,
                     "fingerprint": fingerprint(work, project_root)}}
    write_json(work / "gates.json", gate)
    state = read_json(work / "project.json", {})
    state.setdefault("steps", {}).update({"approval": "done", "assembly": "ready"})
    write_json(work / "project.json", state)
    print(f"Approved. Assembly is enabled for {project_root}.")


# ---------------------------------------------------------------- assemble
def next_export(exports: Path, name: str) -> Path:
    pat = re.compile(rf"^{re.escape(name)}-v(\d+)\.mp4$", re.IGNORECASE)
    nums = [int(m.group(1)) for p in exports.iterdir() if (m := pat.match(p.name))]
    return exports / f"{name}-v{max(nums, default=0) + 1}.mp4"


def cmd_assemble(args):
    t_start = time.time()
    project_root, work = workspace(args.project)
    gate = read_json(work / "gates.json", {})
    if gate.get("plan", {}).get("status") != "approved":
        raise RuntimeError("Not approved. Review the plan with the user, then run approve.")
    if gate["plan"].get("fingerprint") != fingerprint(work, project_root):
        raise RuntimeError("Something changed after approval (storyboard, style, cut, research, spec or a chosen file). "
                           "Show the change to the user and approve again.")
    meta = read_json(work / "meta.json")
    sb = read_json(work / "storyboard.json")
    style = read_json(work / "style.json")
    spec = read_json(work / "resolved-spec.json")
    hyper = work / "hyperframes"
    cut_before = read_json(work / "cut-map.json")

    print("[1/4] graded flat cut")
    preset = args.grade or style.get("color_grade") or "enhanced-natural"
    py("apply-cut.py", "--input", meta["video"], "--audio", str(work / "audio" / "voice-clean.wav"),
       "--cut-list", str(work / "cut-list.json"), "--out", str(hyper / "input-video.mp4"),
       "--voice-out", str(hyper / "voice.wav"), "--tail", str(cut_before["tail"]), "--grade", preset)
    cut_map = read_json(work / "cut-map.json")
    if abs(cut_map["flat_duration"] - cut_before["flat_duration"]) > 0.002:
        raise RuntimeError("The graded cut does not match the approved timeline; stop and re-run analyze.")

    stage = json.loads(json.dumps(sb))
    stage["fps"] = int(round(eval_fraction(cut_map.get("fps", "30/1"))))
    # The composition's picture carries no sound at all, so the voice can never be mixed twice (that is an echo).
    # input-video.mp4 keeps its sound as the review preview; the render masters hyperframes/voice.wav instead.
    sh(["ffmpeg", "-y", "-v", "error", "-i", hyper / "input-video.mp4", "-map", "0:v:0", "-c", "copy", "-an",
        "-movflags", "+faststart", hyper / "base.mp4"])
    stage["video"] = "base.mp4"
    for beat in stage.get("beats", []):
        if beat.get("type") == "block":          # blocks are staged under compositions/; the host page loads them there
            rel = str(beat.get("src", "")).replace("\\", "/").removeprefix("compositions/")
            beat["src"] = "compositions/" + rel
    reframe = sb.get("reframe") or {}
    if reframe.get("aspect") and reframe.get("mode", "static") != "center":
        print("[1b] face-aware reframe to %s" % reframe["aspect"])
        out_name = "base-%s.mp4" % reframe["aspect"].replace(":", "x")
        canvas = sb["canvas"]
        py("reframe.py", "--video", str(hyper / "base.mp4"), "--aspect", reframe["aspect"],
           "--cut-map", str(work / "cut-map.json"), "--out", str(work / "review" / "reframe.json"),
           "--render", str(hyper / out_name), "--size", f"{int(canvas[0])}x{int(canvas[1])}",
           "--mode", reframe.get("mode", "static"))
        stage["video"] = out_name

    print("[2/4] stage composition (captions, catalog blocks, SFX, fade)")
    for cue in stage.get("sfx", []):
        src = sfx_source(str(cue.get("src", "")), project_root, work)
        dest = hyper / "sfx" / f"{synth.hash_file(src)[:12]}-{src.name}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        cue["src"] = f"sfx/{dest.name}"
        cue.setdefault("dur", 1.0)
    stage_blocks(hyper, stage)
    write_json(hyper / "storyboard-stage.json", stage)
    py("stage.py", "--spec", str(hyper / "storyboard-stage.json"), "--style", str(work / "style.json"),
       "--cut-map", str(work / "cut-map.json"), "--out", str(hyper))

    print("[3/4] render + audio pass 2 + verify")
    canvas = sb["canvas"]
    orient = "landscape" if canvas[0] > canvas[1] else ("square" if canvas[0] == canvas[1] else "portrait")
    resolution = orient + ("-4k" if str(sb.get("resolution", "")).lower() in ("4k", "uhd") else "")
    audio = spec.get("audio") or {}
    preset_audio = audio.get("preset") or style.get("audio_preset") or ("youtube" if orient == "landscape" else "shorts")
    out = work / "scratch" / "publish" / f"master-{time.time_ns()}.mp4"
    cmd = [sys.executable, os.path.join(HERE, "render.py"), "--public", str(hyper), "--out", str(out),
           "--voice", str(hyper / "voice.wav"), "--resolution", resolution, "--audio-preset", preset_audio,
           "--tone", audio.get("tone", "neutral"), "--fade-out", str((sb.get("end") or {}).get("fade", 0.0)),
           "--scratch-dir", str(work / "scratch" / "render")]
    if audio.get("music_path"):
        mp = Path(audio["music_path"])
        cmd += ["--music", str(mp if mp.is_absolute() else project_root / mp), "--music-db", str(audio.get("music_db", -20))]
    if args.gpu:
        cmd.append("--gpu")
    sh(cmd)

    print("[4/4] publish")
    exports = project_root / "Exports"
    exports.mkdir(parents=True, exist_ok=True)
    final = next_export(exports, project_root.name)
    os.replace(out, final)
    review = work / "review"
    review.mkdir(parents=True, exist_ok=True)
    for f in (work / "scratch" / "render").glob(out.stem + "-*"):
        if f.suffix in (".md", ".json"):
            shutil.copyfile(f, review / f.name.replace(out.stem, final.stem))
    sheet = work / "scratch" / "render" / "render-sheet.png"
    if sheet.is_file():
        shutil.copyfile(sheet, review / f"{final.stem}-render-sheet.png")
    state = read_json(work / "project.json", {})
    state.setdefault("steps", {})["assembly"] = "done"
    state["last_export"] = str(final.relative_to(project_root))
    write_json(work / "project.json", state)
    print("=" * 70)
    print(f"DONE in {time.time() - t_start:.1f}s -> {final}")
    print(f"  checks: {review}/{final.stem}-VERIFY.md · frames: {review}/{final.stem}-render-sheet.png")
    print("=" * 70)


def main():
    ap = argparse.ArgumentParser(description="Video pipeline: analyze -> recut -> approve -> assemble")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze", help="ingest, clean audio, transcript, tight cut, evidence and REVIEW.md")
    a.add_argument("--input", required=True, help="source video, or a folder holding exactly one")
    a.add_argument("--project", required=True, help="the user's project folder (work goes to .video-pipeline/)")
    a.add_argument("--prompt", default="", help="the user's brief")
    a.add_argument("--reference", action="append", help="extra reference file (references/ is scanned too)")
    a.add_argument("--names", default="", help="names/jargon to spell right, e.g. \"Zerodha, Nifty, HyperFrames\"")
    a.add_argument("--dereverb", choices=["off", "light", "normal", "strong"], default="normal")
    a.add_argument("--denoise", choices=["auto", "off", "light", "medium", "strong", "maximum"], default="auto")
    a.add_argument("--max-pause", type=float, default=0.28, help="longest pause kept inside speech")
    a.add_argument("--tail", type=float, default=DEFAULT_TAIL, help="held end + fade to black, seconds")
    a.add_argument("--drop", action="append", help="remove source range START-END")
    a.add_argument("--restore", action="append", help="keep source range START-END")
    a.add_argument("--keep-retakes", action="store_true")
    a.add_argument("--keep-fillers", action="store_true")
    r = sub.add_parser("recut", help="change the cut and rebuild the flat cut + transcript")
    r.add_argument("--project", required=True)
    r.add_argument("--drop", action="append", help="remove source range START-END (added to earlier drops)")
    r.add_argument("--restore", action="append", help="keep source range START-END")
    r.add_argument("--max-pause", type=float)
    r.add_argument("--tail", type=float)
    r.add_argument("--keep-retakes", action="store_true")
    r.add_argument("--keep-fillers", action="store_true")
    r.add_argument("--reset", action="store_true", help="forget earlier drop/restore decisions")
    p = sub.add_parser("approve", help="record the user's approval")
    p.add_argument("--project", required=True)
    p.add_argument("--user-approved", action="store_true")
    p.add_argument("--note", default="User approved the plan.")
    s = sub.add_parser("assemble", help="grade, stage, render, master, verify, export")
    s.add_argument("--project", required=True)
    s.add_argument("--grade", help="override style.json color_grade")
    s.add_argument("--gpu", action="store_true")
    args = ap.parse_args()
    try:
        {"analyze": cmd_analyze, "recut": cmd_recut, "approve": cmd_approve, "assemble": cmd_assemble}[args.cmd](args)
    except subprocess.CalledProcessError as exc:
        print(f"pipeline stage failed (exit {exc.returncode}): {' '.join(map(str, exc.cmd))}", file=sys.stderr)
        raise SystemExit(exc.returncode or 1)
    except (RuntimeError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"pipeline error: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
