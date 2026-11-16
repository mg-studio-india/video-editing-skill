#!/usr/bin/env python3
"""Preflight for the watch skill. Never installs anything and never touches the network."""
from __future__ import annotations

import argparse
import os
import json
import platform
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
from runtime import configure_stdio, run  # noqa: E402

MODEL_URL = "https://huggingface.co/gouravg8/gtm-hi2hing-ggml/resolve/main/ggml-apex-hinglish-q8_0.bin"


def _first_line(cmd: list[str]) -> str | None:
    try:
        out = run(cmd, check=False, timeout=15)
    except Exception:  # noqa: BLE001 - preflight must never crash
        return None
    text = (out.stdout or out.stderr or "").strip().splitlines()
    return text[0] if text else None


def whisper_capabilities(binary: Path) -> dict:
    try:
        proc = run([str(binary), "-h"], check=False, timeout=20)
    except Exception:  # noqa: BLE001
        return {"readable": False}
    text = (proc.stdout or "") + (proc.stderr or "")
    return {
        "readable": True,
        "output_json": "--output-json" in text or "-oj" in text,
        "word_split": "--split-on-word" in text and "--max-len" in text,
        "dtw": "--dtw" in text,
        "output_json_full": "--output-json-full" in text or "-ojf" in text,
        "no_flash_attn": "--no-flash-attn" in text or "-nfa" in text,
        "prompt": "--prompt" in text,
        "vad": "--vad" in text,
    }


def check() -> dict:
    cfg = config.load()
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    wbin, wmodel = config.find_whisper_bin(cfg), config.find_whisper_model(cfg)
    caps = whisper_capabilities(wbin) if wbin else {}
    try:
        import PIL  # noqa: F401
        pillow = True
    except ImportError:
        pillow = False
    try:
        import cv2  # noqa: F401
        opencv = True
    except ImportError:
        opencv = False
    try:
        import pypdf  # noqa: F401
        pdf_text = True
    except ImportError:
        pdf_text = False
    try:
        import pypdfium2  # noqa: F401
        pdf_preview = True
    except ImportError:
        pdf_preview = False
    deep_filter = next((c for c in (os.environ.get("VIDEO_DEEPFILTER"),
                                     os.path.expanduser("~/.config/video-skills/bin/deep-filter"),
                                     os.path.expanduser("~/.config/video-skills/bin/deep-filter.exe"),
                                     shutil.which("deep-filter")) if c and os.path.isfile(c)), None)
    try:
        from runtime import find_engine_dir
        catalog_index = find_engine_dir() / "compositions" / "catalog.json"
    except Exception:  # noqa: BLE001
        catalog_index = None
    ready = {
        "core": bool(ffmpeg and ffprobe),
        "transcript": bool(wbin and wmodel and caps.get("word_split", True)),
        "contact_sheets": pillow,
        "pipeline_visual": pillow and opencv,
        "pipeline_documents": pillow and pdf_text and pdf_preview,
        "urls": shutil.which("yt-dlp") is not None,
    }
    return {
        "platform": f"{platform.system()} {platform.machine()}",
        "ffmpeg": {"path": ffmpeg, "version": _first_line(["ffmpeg", "-version"]) if ffmpeg else None},
        "ffprobe": {"path": ffprobe},
        "whisper_cli": {"path": str(wbin) if wbin else None, "capabilities": caps},
        "whisper_model": str(wmodel) if wmodel else None,
        "hinglish_model": bool(wmodel and config.is_hinglish_model(wmodel)),
        "deep_filter": deep_filter,
        "catalog_index": str(catalog_index) if catalog_index and catalog_index.is_file() else None,
        "yt_dlp": shutil.which("yt-dlp"),
        "pillow": pillow,
        "opencv": opencv,
        "pypdf": pdf_text,
        "pypdfium2": pdf_preview,
        "config_file": str(config.CONFIG_FILE) + (" (exists)" if config.CONFIG_FILE.is_file() else " (absent)"),
        "ready": ready,
    }


def fixes(status: dict) -> list[str]:
    out = []
    if not status["ready"]["core"]:
        out.append("ffmpeg/ffprobe missing:  brew install ffmpeg")
    if not status["whisper_cli"]["path"]:
        out.append("whisper-cli missing:  brew install whisper-cpp   (or set WATCH_WHISPER_CPP_BIN)")
    elif status["whisper_cli"]["capabilities"].get("readable") and not status["whisper_cli"]["capabilities"].get("word_split"):
        out.append("whisper-cli lacks --split-on-word/--max-len: update it (brew upgrade whisper-cpp)")
    if not status["hinglish_model"]:
        out.append("Hinglish model missing:  mkdir -p ~/.cache/whisper.cpp && curl -L -o "
                   f"~/.cache/whisper.cpp/{config.HINGLISH_MODEL} {MODEL_URL}   (about 850 MB)")
    if not status["deep_filter"]:
        out.append("DeepFilterNet missing (audio pass 1 needs it): video-skills setup")
    if not status["catalog_index"]:
        out.append("HyperFrames catalog index missing: video-skills setup, or catalog.py build")
    if not status["pillow"] or not status["opencv"]:
        out.append("pipeline visual dependencies missing: install the configured engine requirements with video-skills setup")
    if not status["ready"]["pipeline_documents"]:
        out.append("PDF guide/reference support missing: install the configured engine requirements with video-skills setup")
    if not status["yt_dlp"]:
        out.append("optional, URLs:  brew install yt-dlp")
    return out


ENV_TEMPLATE = """# watch skill config (environment variables override this file)
# Paths are auto-detected on macOS/Homebrew; uncomment only to override.
#WATCH_WHISPER_CPP_BIN=/opt/homebrew/bin/whisper-cli
#WATCH_WHISPER_MODEL=~/.cache/whisper.cpp/ggml-apex-hinglish-q8_0.bin
# auto = Hinglish model -> Roman Hinglish; stock model -> Hindi decoding, romanised (never forced English)
#WATCH_WHISPER_LANG=auto
# Names and jargon only. A topic sentence here leaks into the transcript.
#WATCH_WHISPER_PROMPT=Zerodha, Nifty, HyperFrames
# auto picks the DTW word-timing preset from the model; off disables it
#WATCH_WHISPER_DTW=auto
#WATCH_SCENE_THRESHOLD=0.20
"""


def main() -> int:
    configure_stdio()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--init-config", action="store_true")
    args = ap.parse_args()

    if args.init_config:
        if config.CONFIG_FILE.exists():
            print(f"already exists: {config.CONFIG_FILE}")
        else:
            config.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            config.CONFIG_FILE.write_text(ENV_TEMPLATE, encoding="utf-8")
            print(f"wrote {config.CONFIG_FILE}")
        return 0

    status = check()
    if args.check:
        return 0 if status["ready"]["core"] else 2
    if args.json:
        print(json.dumps({**status, "fixes": fixes(status)}, indent=2))
        return 0 if status["ready"]["core"] else 2

    def mark(ok: bool) -> str:
        return "OK     " if ok else "MISSING"

    r = status["ready"]
    print(f"watch preflight · {status['platform']}")
    print(f"  {mark(r['core'])}  ffmpeg + ffprobe  {status['ffmpeg']['version'] or ''}")
    print(f"  {mark(bool(status['whisper_cli']['path']))}  whisper-cli       {status['whisper_cli']['path'] or ''}")
    print(f"  {mark(bool(status['whisper_model']))}  whisper model     {status['whisper_model'] or ''}"
          f"{'  (Hinglish)' if status['hinglish_model'] else '  (stock: install the Hinglish model)' if status['whisper_model'] else ''}")
    print(f"  {mark(bool(status['deep_filter']))}  DeepFilterNet     {status['deep_filter'] or ''}")
    print(f"  {mark(bool(status['catalog_index']))}  HyperFrames index {status['catalog_index'] or ''}")
    print(f"  {mark(r['contact_sheets'])}  Pillow (source contact sheets)")
    print(f"  {mark(r['pipeline_visual'])}  OpenCV (caption-safe face measurement)")
    print(f"  {mark(r['pipeline_documents'])}  pypdf + PDFium (brand/reference PDF text and visual sheets)")
    print(f"  {mark(r['urls'])}  yt-dlp (URL input, optional)")
    print(f"  config: {status['config_file']}")
    print(f"  transcript ready: {'yes' if r['transcript'] else 'NO (analysis still runs, without words)'}")
    todo = fixes(status)
    if todo:
        print("\nTo fix:")
        for line in todo:
            print(f"  - {line}")
    return 0 if r["core"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
