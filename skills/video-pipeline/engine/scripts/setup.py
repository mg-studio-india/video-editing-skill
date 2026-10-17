#!/usr/bin/env python3
"""Preflight for the watch skill. Never installs anything and never touches the network.

  setup.py              human-readable report with the exact fix command for anything missing
  setup.py --json       machine-readable
  setup.py --check      silent; exit 0 if the core (ffmpeg + ffprobe) is present, 2 if not
  setup.py --init-config  write a commented ~/.config/watch/.env template if none exists
"""
from __future__ import annotations

import argparse
import json
import platform
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
from runtime import configure_stdio, run  # noqa: E402

MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin"


def _first_line(cmd: list[str]) -> str | None:
    try:
        out = run(cmd, check=False, timeout=15)
    except Exception:  # noqa: BLE001 - preflight must never crash
        return None
    text = (out.stdout or out.stderr or "").strip().splitlines()
    return text[0] if text else None


def whisper_capabilities(binary: Path) -> dict:
    """Read `whisper-cli -h` to learn which flags this build understands."""
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
    ready = {
        "core": bool(ffmpeg and ffprobe),
        "transcript": bool(wbin and wmodel and caps.get("word_split", True)),
        "contact_sheets": pillow,
        "urls": shutil.which("yt-dlp") is not None,
    }
    return {
        "platform": f"{platform.system()} {platform.machine()}",
        "ffmpeg": {"path": ffmpeg, "version": _first_line(["ffmpeg", "-version"]) if ffmpeg else None},
        "ffprobe": {"path": ffprobe},
        "whisper_cli": {"path": str(wbin) if wbin else None, "capabilities": caps},
        "whisper_model": str(wmodel) if wmodel else None,
        "yt_dlp": shutil.which("yt-dlp"),
        "pillow": pillow,
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
    if not status["whisper_model"]:
        out.append("large model missing:  mkdir -p ~/.cache/whisper.cpp && curl -L -o "
                   f"~/.cache/whisper.cpp/ggml-large-v3.bin {MODEL_URL}   (about 3 GB)")
    if not status["pillow"]:
        out.append("optional, contact sheets:  python3 -m pip install pillow")
    if not status["yt_dlp"]:
        out.append("optional, URLs:  brew install yt-dlp")
    return out


ENV_TEMPLATE = """# watch skill config (environment variables override this file)
# Paths are auto-detected on macOS/Homebrew; uncomment only to override.
#WATCH_WHISPER_CPP_BIN=/opt/homebrew/bin/whisper-cli
#WATCH_WHISPER_MODEL=~/.cache/whisper.cpp/ggml-large-v3.bin
#WATCH_WHISPER_LANG=auto
# Whisper tends to drop um/uh. A prompt containing them makes it keep them (useful for cut lists):
#WATCH_WHISPER_PROMPT=Um, uh, you know, I mean, like.
#WATCH_WHISPER_DTW=large.v3
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
    print(f"  {mark(bool(status['whisper_model']))}  whisper model     {status['whisper_model'] or ''}")
    print(f"  {mark(r['contact_sheets'])}  Pillow (contact sheets, optional)")
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
