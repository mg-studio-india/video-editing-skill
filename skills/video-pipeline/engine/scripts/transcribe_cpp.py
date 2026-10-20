"""Local transcription with whisper.cpp (`whisper-cli`). Nothing leaves the machine."""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path
import config
import hinglish
from runtime import ToolError, ensure_project_venv, fmt_time, log, parse_time, run, tail

ensure_project_venv()

NON_SPEECH_RE = re.compile(r"^[\[\(\*♪].*[\]\)\*♪]$")
IGNORED_CUES = {"blank_audio", "silence", "no speech", "inaudible"}
OPTIONAL_FLAGS = {"-np": 0, "--dtw": 1, "-t": 1, "--prompt": 1, "--carry-initial-prompt": 0}  # flag -> number of values

DEFAULT_HINGLISH_PROMPT = (
    "Namaste dosto. Aaj ke is video mein hum business, startup, clients, testimonials, previous work, "
    "college projects, deadlines, milestones, trust, connections aur net worth ke baare mein baat karenge."
)


# ---------------------------------------------------------------- audio extraction
def extract_wav(video: str, out_wav: Path, start: float | None = None,
                end: float | None = None) -> Path:
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    if start:
        cmd += ["-ss", f"{start:.3f}"]
    if start is not None and end is not None:
        cmd += ["-t", f"{max(0.0, end - start):.3f}"]
    elif end is not None:
        cmd += ["-t", f"{end:.3f}"]
    cmd += ["-i", str(Path(video).resolve()), "-vn",
            "-af", "highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ac", "1", "-ar", "16000",
            "-c:a", "pcm_s16le", str(out_wav)]
    run(cmd)
    return out_wav


# ---------------------------------------------------------------- running whisper-cli
def build_command(binary: Path, model: Path, wav: Path, out_prefix: Path,
                  cfg: dict[str, str]) -> list[str]:
    raw_lang = (cfg.get("WATCH_WHISPER_LANG") or "auto").strip().lower()
    # When transcribing Hindi/Hinglish speech, configuring Whisper to decode with the English token space ('-l', 'en')
    # and a conversational Hinglish prompt natively instructs Whisper to output spoken Hindi directly
    # in Latin alphabet (Hinglish). This eliminates Devanagari output directly at the Whisper decoder level.
    is_hinglish = raw_lang in ("hi", "hindi", "hinglish", "hi-latn") or cfg.get("WATCH_WHISPER_SCRIPT") == "hinglish"
    whisper_lang = "en" if is_hinglish else raw_lang

    cmd = [str(binary), "-m", str(model), "-f", str(wav), "-of", str(out_prefix),
           "-oj", "-ml", "1", "-sow", "-l", whisper_lang, "-np"]
    threads = cfg.get("WATCH_WHISPER_THREADS") or str(min(8, os.cpu_count() or 4))
    cmd += ["-t", threads]
    if cfg.get("WATCH_WHISPER_DTW"):
        cmd += ["--dtw", cfg["WATCH_WHISPER_DTW"]]

    prompt = cfg.get("WATCH_WHISPER_PROMPT") or ""
    if is_hinglish:
        cmd += ["--carry-initial-prompt"]
        if not prompt:
            prompt = DEFAULT_HINGLISH_PROMPT
        elif "namaste" not in prompt.lower() and "baat karenge" not in prompt.lower():
            prompt = (DEFAULT_HINGLISH_PROMPT + " " + prompt).strip()

    if prompt:
        cmd += ["--prompt", prompt]
    return cmd


def _drop_flag(cmd: list[str], flag: str) -> list[str]:
    out, i = [], 0
    while i < len(cmd):
        if cmd[i] == flag:
            i += 1 + OPTIONAL_FLAGS.get(flag, 0)
            continue
        out.append(cmd[i])
        i += 1
    return out


def run_whisper(cmd: list[str]) -> None:
    for _ in range(len(OPTIONAL_FLAGS) + 1):
        proc = run(cmd, check=False)
        if proc.returncode == 0:
            return
        blob = (proc.stderr or "") + (proc.stdout or "")
        m = re.search(r"unknown argument:\s*(\S+)", blob)
        if m and m.group(1) in OPTIONAL_FLAGS and m.group(1) in cmd:
            log(f"whisper-cli does not support {m.group(1)}; retrying without it")
            cmd = _drop_flag(cmd, m.group(1))
            continue
        raise ToolError(f"whisper-cli failed (exit {proc.returncode}): {tail(blob)}")
    raise ToolError("whisper-cli kept rejecting flags; run setup.py to inspect your build.")


# ---------------------------------------------------------------- parsing
def parse_whisper_json(data: dict, offset: float = 0.0) -> dict:
    language = (data.get("result") or {}).get("language")
    words: list[dict] = []
    cues: list[dict] = []
    cur: dict | None = None
    for entry in data.get("transcription", []):
        raw = entry.get("text", "")
        text = raw.strip()
        off = entry.get("offsets") or {}
        if not text or off.get("from") is None:
            continue
        start = off["from"] / 1000.0 + offset
        end = (off.get("to", off["from"])) / 1000.0 + offset
        if text.startswith("[_"):      # special tokens like [_BEG_]
            continue
        if NON_SPEECH_RE.match(text):
            if cur:
                words.append(cur)
                cur = None
            label = text.strip("[]()*♪ ").strip()
            if label.lower() not in IGNORED_CUES and label:
                label_cleaned = hinglish.to_hinglish(label)
                cues.append({"text": label_cleaned, "start": round(start, 3), "end": round(end, 3)})
            continue
        text_clean = hinglish.to_hinglish(text)
        if raw.startswith(" ") or cur is None:
            if cur:
                words.append(cur)
            cur = {"w": text_clean, "start": start, "end": end}
        else:                          # punctuation / word-piece continuing the previous word
            cur["w"] += text_clean
            cur["end"] = max(cur["end"], end)
    if cur:
        words.append(cur)

    # Timing hygiene: positive duration, no overlaps.
    for i, w in enumerate(words):
        w["end"] = max(w["end"], w["start"] + 0.02)
        if i + 1 < len(words) and w["end"] > words[i + 1]["start"]:
            w["end"] = max(w["start"] + 0.02, words[i + 1]["start"])
    for w in words:
        w["start"], w["end"] = round(w["start"], 3), round(w["end"], 3)
    words = hinglish.clean_transcript_words(words)
    if language == "hi":
        language = "hi-Latn"
    return {"language": language, "words": words, "sound_cues": cues}


def collapse_loops(words: list[dict]) -> tuple[list[dict], int]:
    norm = [re.sub(r"\W+", "", w["w"].lower()) for w in words]
    keep = [True] * len(words)
    removed = 0
    for n, min_rep in ((1, 5), (2, 4), (3, 4)):
        i = 0
        while i + n * min_rep <= len(words):
            gram = norm[i:i + n]
            if not all(gram):
                i += 1
                continue
            reps, j = 1, i + n
            while j + n <= len(words) and norm[j:j + n] == gram:
                reps += 1
                j += n
            if reps >= min_rep:
                for k in range(i + n, j):
                    if keep[k]:
                        keep[k] = False
                        removed += 1
                i = j
            else:
                i += 1
    return [w for w, k in zip(words, keep) if k], removed


def words_to_segments(words: list[dict], gap: float = 0.8, max_words: int = 28) -> list[dict]:
    segments: list[dict] = []
    cur: list[dict] = []

    def flush() -> None:
        if cur:
            segments.append({
                "start": cur[0]["start"], "end": cur[-1]["end"],
                "text": " ".join(w["w"] for w in cur),
            })
            cur.clear()

    for w in words:
        if cur and (w["start"] - cur[-1]["end"] > gap or len(cur) >= max_words):
            flush()
        cur.append(w)
        if re.search(r"[.!?…][\"')\]]*$", w["w"]):
            flush()
    flush()
    return segments


def build_transcript(parsed: dict, model_name: str, rng: tuple[float | None, float | None]) -> dict:
    words, removed = collapse_loops(parsed["words"])
    words = hinglish.clean_transcript_words(words)
    return {
        "engine": "whisper.cpp",
        "model": model_name,
        "language": parsed.get("language"),
        "script": "hinglish",
        "range": [rng[0], rng[1]] if rng != (None, None) else None,
        "words": words,
        "segments": words_to_segments(words),
        "sound_cues": parsed.get("sound_cues", []),
        "loops_collapsed": removed,
    }


def filter_range(transcript: dict, start: float | None, end: float | None) -> dict:
    lo = start if start is not None else float("-inf")
    hi = end if end is not None else float("inf")
    words = [w for w in transcript["words"] if w["end"] >= lo and w["start"] <= hi]
    out = dict(transcript)
    out["words"] = words
    out["segments"] = words_to_segments(words)
    out["sound_cues"] = [c for c in transcript.get("sound_cues", []) if c["end"] >= lo and c["start"] <= hi]
    out["range"] = [start, end]
    return out


# ---------------------------------------------------------------- public entry point
def transcribe(video: str, work_dir: Path, start: float | None = None,
               end: float | None = None, cfg: dict[str, str] | None = None) -> dict:
    cfg = cfg or config.load()
    binary = config.find_whisper_bin(cfg)
    model = config.find_whisper_model(cfg)
    if binary is None:
        raise ToolError("whisper-cli not found. On macOS: `brew install whisper-cpp` "
                        "(see references/macos-setup.md), or set WATCH_WHISPER_CPP_BIN.")
    if model is None:
        raise ToolError("whisper.cpp model not found. Download ggml-large-v3.bin and set "
                        "WATCH_WHISPER_MODEL (see references/macos-setup.md).")
    work_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="watch-asr-", dir=str(work_dir)) as tmp:
        wav = extract_wav(video, Path(tmp) / "audio.wav", start, end)
        prefix = Path(tmp) / "out"
        log(f"transcribing with whisper.cpp ({model.name}); large models can take several minutes…")
        run_whisper(build_command(binary, model, wav, prefix, cfg))
        out_json = Path(str(prefix) + ".json")
        if not out_json.is_file():
            raise ToolError("whisper-cli finished but wrote no JSON; check the build supports -oj.")
        data = json.loads(out_json.read_text(encoding="utf-8", errors="replace"))
    parsed = parse_whisper_json(data, offset=start or 0.0)
    raw_lang = (cfg.get("WATCH_WHISPER_LANG") or "auto").strip().lower()
    if raw_lang in ("hi", "hindi", "hinglish", "hi-latn") or parsed.get("language") == "hi":
        parsed["language"] = "hi-Latn"
    return build_transcript(parsed, model.name, (start, end))


if __name__ == "__main__":
    # Sanity check on your machine:  python3 transcribe_cpp.py clip.mp4 [--start 0 --end 20]
    import argparse
    ap = argparse.ArgumentParser(description="Transcribe a clip with whisper.cpp and show the first words.")
    ap.add_argument("media")
    ap.add_argument("--start")
    ap.add_argument("--end")
    a = ap.parse_args()
    t = transcribe(a.media, Path(tempfile.mkdtemp(prefix="watch-")), parse_time(a.start), parse_time(a.end))
    print(f"language={t['language']}  words={len(t['words'])}  segments={len(t['segments'])}  "
          f"sound_cues={len(t['sound_cues'])}  loops_collapsed={t['loops_collapsed']}")
    for w in t["words"][:15]:
        print(f"  {fmt_time(w['start'], 2):>8}  {w['w']}")
