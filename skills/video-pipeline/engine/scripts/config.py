"""Configuration: environment > ~/.config/watch/.env > defaults."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

CONFIG_FILE = Path.home() / ".config" / "watch" / ".env"

DEFAULTS = {
    # whisper.cpp
    "WATCH_WHISPER_CPP_BIN": "",          # path to whisper-cli (auto-detected if empty)
    "WATCH_WHISPER_MODEL": "",            # path to ggml-large-v3.bin (auto-detected if empty)
    "WATCH_WHISPER_LANG": "auto",         # 'auto' or a code like 'en', 'hi'
    "WATCH_WHISPER_THREADS": "",          # default: min(8, cpu count)
    "WATCH_WHISPER_DTW": "",              # optional --dtw preset, e.g. large.v3 (see references/macos-setup.md)
    "WATCH_WHISPER_PROMPT": "",           # optional initial prompt: names, jargon
    # analysis
    "WATCH_SCENE_THRESHOLD": "0.20",      # ffmpeg scene score that counts as a cut
    "WATCH_CACHE_DIR": "~/.cache/watch",
}

# Where Homebrew / manual installs usually put things on macOS.
BIN_CANDIDATES = [
    "/opt/homebrew/bin/whisper-cli",
    "/usr/local/bin/whisper-cli",
    "~/whisper.cpp/build/bin/whisper-cli",
]
MODEL_NAMES = ["ggml-large-v3.bin", "ggml-large-v3-turbo.bin", "ggml-large-v2.bin"]
MODEL_DIRS = [
    "~/.cache/whisper.cpp",
    "~/whisper.cpp/models",
    "~/.local/share/whisper.cpp",
    "~/models/whisper",
    "/opt/homebrew/share/whisper-cpp/models",
    "/usr/local/share/whisper-cpp/models",
]


def read_env_file(path: Path = CONFIG_FILE) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (FileNotFoundError, OSError):
        return values
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if value[:1] in "\"'" and value.endswith(value[:1]) and len(value) >= 2:
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        values[key] = value
    return values


def load() -> dict[str, str]:
    file_values = read_env_file()
    cfg = {}
    for key, default in DEFAULTS.items():
        cfg[key] = os.environ.get(key, file_values.get(key, default)).strip()
    return cfg


def cache_root(cfg: dict[str, str] | None = None) -> Path:
    cfg = cfg or load()
    return Path(cfg["WATCH_CACHE_DIR"]).expanduser()


def find_whisper_bin(cfg: dict[str, str] | None = None) -> Path | None:
    cfg = cfg or load()
    explicit = cfg.get("WATCH_WHISPER_CPP_BIN", "")
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.is_file() else None
    for name in ("whisper-cli", "whisper-cpp"):
        found = shutil.which(name)
        if found:
            return Path(found)
    for cand in BIN_CANDIDATES:
        p = Path(cand).expanduser()
        if p.is_file():
            return p
    return None


def find_whisper_model(cfg: dict[str, str] | None = None) -> Path | None:
    cfg = cfg or load()
    explicit = cfg.get("WATCH_WHISPER_MODEL", "")
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.is_file() else None
    for name in MODEL_NAMES:  # large-v3 first
        for d in MODEL_DIRS:
            p = Path(d).expanduser() / name
            if p.is_file():
                return p
    return None
