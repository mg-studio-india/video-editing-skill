"""Configuration: environment > ~/.config/watch/.env > defaults."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

CONFIG_FILE = Path.home() / ".config" / "watch" / ".env"

DEFAULTS = {
    # whisper.cpp
    "WATCH_WHISPER_CPP_BIN": "",          # path to whisper-cli (auto-detected if empty)
    "WATCH_WHISPER_MODEL": "",            # path to a ggml model (auto-detected; the Hinglish model is preferred)
    "WATCH_WHISPER_LANG": "auto",         # auto: Hinglish model -> en token (Roman output); stock model -> hi, then romanised
    "WATCH_WHISPER_THREADS": "",          # default: min(8, cpu count)
    "WATCH_WHISPER_DTW": "auto",          # auto: DTW word timing preset from the model name; "off" disables it
    "WATCH_WHISPER_PROMPT": "",           # optional initial prompt: names and jargon only, never a topic sentence
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
# Hinglish first: a Whisper fine-tune that writes Hindi/English speech in Roman script, so the transcript says what
# was spoken (stock Whisper forced to English translates Hindi instead of transcribing it).
HINGLISH_MODEL = "ggml-apex-hinglish-q8_0.bin"
MODEL_NAMES = [HINGLISH_MODEL, "ggml-large-v3.bin", "ggml-large-v3-turbo.bin", "ggml-large-v2.bin"]
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
    for name in MODEL_NAMES:  # Hinglish model first, then large-v3
        for d in MODEL_DIRS:
            p = Path(d).expanduser() / name
            if p.is_file():
                return p
    return None


def is_hinglish_model(model: Path | str | None) -> bool:
    name = Path(str(model or "")).name.lower()
    return "hinglish" in name or "hi2hing" in name


def whisper_lang(cfg: dict[str, str], model: Path | str | None) -> str:
    """Decoder language. The Hinglish fine-tune emits Roman Hinglish under the `en` token (its documented usage).
    A stock model must decode Hindi as `hi` (faithful Devanagari, romanised afterwards): `en` would translate."""
    lang = (cfg.get("WATCH_WHISPER_LANG") or "auto").strip().lower()
    if lang in ("", "auto", "hinglish", "hi-latn"):
        return "en" if is_hinglish_model(model) else "hi"
    return lang


def dtw_preset(cfg: dict[str, str], model: Path | str | None) -> str | None:
    """whisper.cpp --dtw alignment-head preset for word timing; None when disabled or unknown."""
    value = (cfg.get("WATCH_WHISPER_DTW") or "auto").strip().lower()
    if value in ("off", "none", "0", "false"):
        return None
    if value != "auto":
        return value
    name = Path(str(model or "")).name.lower()
    if is_hinglish_model(name) or "turbo" in name:
        return "large.v3.turbo"      # the Hinglish Apex model is a large-v3-turbo fine-tune
    if "large-v3" in name:
        return "large.v3"
    if "large-v2" in name:
        return "large.v2"
    return None
