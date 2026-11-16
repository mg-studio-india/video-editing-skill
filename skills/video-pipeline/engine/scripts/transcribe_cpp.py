"""Local Hinglish transcription with whisper.cpp (`whisper-cli`). Nothing leaves the machine.

Output is always Roman-script Hinglish (Hindi and English speech, English letters):
  * the default model is a Whisper fine-tune that writes Hinglish directly (decoder token `en`);
  * a stock model decodes Hindi as `hi` (never `en`, which translates instead of transcribing) and is romanised here.
No topic prompt is injected: a prompt leaks its words into the transcript. Word starts use DTW alignment when the
build supports it, and `refine_words` snaps every word to the measured speech energy so text, audio and picture agree.
"""
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
# flag -> number of values; dropped one at a time when a whisper-cli build does not know them
OPTIONAL_FLAGS = {"-np": 0, "--dtw": 1, "-nfa": 0, "-t": 1, "--prompt": 1}


# ---------------------------------------------------------------- audio extraction
def extract_wav(media: str, out_wav: Path, start: float | None = None, end: float | None = None) -> Path:
    """16 kHz mono PCM for whisper. No loudness normalisation: it changes nothing whisper needs and can lift noise."""
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    if start:
        cmd += ["-ss", f"{start:.3f}"]
    if start is not None and end is not None:
        cmd += ["-t", f"{max(0.0, end - start):.3f}"]
    elif end is not None:
        cmd += ["-t", f"{end:.3f}"]
    cmd += ["-i", str(Path(media).resolve()), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(out_wav)]
    run(cmd)
    return out_wav


# ---------------------------------------------------------------- running whisper-cli
def build_command(binary: Path, model: Path, wav: Path, out_prefix: Path, cfg: dict[str, str]) -> list[str]:
    lang = config.whisper_lang(cfg, model)
    cmd = [str(binary), "-m", str(model), "-f", str(wav), "-of", str(out_prefix),
           "-ojf", "-ml", "1", "-sow", "-l", lang, "-np"]
    threads = cfg.get("WATCH_WHISPER_THREADS") or str(min(8, os.cpu_count() or 4))
    cmd += ["-t", threads]
    preset = config.dtw_preset(cfg, model)
    if preset:
        # DTW needs the attention matrix, which the flash-attention path does not expose
        cmd += ["--dtw", preset, "-nfa"]
    prompt = (cfg.get("WATCH_WHISPER_PROMPT") or "").strip()
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
    for _ in range(len(OPTIONAL_FLAGS) + 2):
        proc = run(cmd, check=False)
        if proc.returncode == 0:
            return
        blob = (proc.stderr or "") + (proc.stdout or "")
        m = re.search(r"unknown argument:\s*(\S+)", blob)
        if m and m.group(1) == "-ojf" and "-ojf" in cmd:
            log("whisper-cli has no full JSON output; word starts fall back to segment offsets")
            cmd = [("-oj" if c == "-ojf" else c) for c in cmd]
            continue
        if m and m.group(1) in OPTIONAL_FLAGS and m.group(1) in cmd:
            log(f"whisper-cli does not support {m.group(1)}; retrying without it")
            cmd = _drop_flag(cmd, m.group(1))
            if m.group(1) == "--dtw":
                cmd = _drop_flag(cmd, "-nfa")
            continue
        if "--dtw" in cmd:
            # e.g. a build that lacks this DTW preset: keep going on segment timing (words are still energy-snapped)
            log("whisper-cli failed with DTW word timing; retrying without it: " + tail(blob, 300))
            cmd = _drop_flag(_drop_flag(cmd, "--dtw"), "-nfa")
            continue
        raise ToolError(f"whisper-cli failed (exit {proc.returncode}): {tail(blob)}")
    raise ToolError("whisper-cli kept rejecting flags; run setup.py to inspect your build.")


# ---------------------------------------------------------------- parsing
def _dtw_start(entry: dict) -> float | None:
    times = []
    for tok in entry.get("tokens") or []:
        text = str(tok.get("text", ""))
        t_dtw = tok.get("t_dtw")
        if text.startswith("[_") or t_dtw is None:
            continue
        try:
            t_dtw = float(t_dtw)
        except (TypeError, ValueError):
            continue
        if t_dtw >= 0:
            times.append(t_dtw / 100.0)          # whisper.cpp keeps token times in 10 ms units
    return min(times) if times else None


def parse_whisper_json(data: dict, offset: float = 0.0) -> dict:
    language = (data.get("result") or {}).get("language")
    words: list[dict] = []
    cues: list[dict] = []
    cur: dict | None = None
    dtw_hits = 0
    for entry in data.get("transcription", []):
        raw = entry.get("text", "")
        text = raw.strip()
        off = entry.get("offsets") or {}
        if not text or off.get("from") is None:
            continue
        start = off["from"] / 1000.0 + offset
        end = (off.get("to", off["from"])) / 1000.0 + offset
        dtw = _dtw_start(entry)
        if dtw is not None:
            dtw_hits += 1
            start = dtw + offset
            end = max(end, start + 0.02)
        if text.startswith("[_"):      # special tokens like [_BEG_]
            continue
        if NON_SPEECH_RE.match(text):
            if cur:
                words.append(cur)
                cur = None
            label = text.strip("[]()*♪ ").strip()
            if label.lower() not in IGNORED_CUES and label:
                cues.append({"text": hinglish.to_hinglish(label), "start": round(start, 3), "end": round(end, 3)})
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

    # Timing hygiene, keeping the spoken order: starts never go backwards, positive duration, no overlaps.
    for i in range(1, len(words)):
        words[i]["start"] = max(words[i]["start"], words[i - 1]["start"])
    for i, w in enumerate(words):
        w["end"] = max(w["end"], w["start"] + 0.02)
        if i + 1 < len(words) and w["end"] > words[i + 1]["start"]:
            w["end"] = max(w["start"] + 0.02, words[i + 1]["start"])
    for w in words:
        w["start"], w["end"] = round(w["start"], 3), round(w["end"], 3)
    words = hinglish.clean_transcript_words(words)
    return {"language": "hi-Latn", "decoder_language": language, "words": words, "sound_cues": cues,
            "timing": "dtw" if dtw_hits else "segment-offsets"}


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


def refine_words(words: list[dict], mask) -> tuple[list[dict], list[dict]]:
    """Snap word edges to measured speech and drop words spoken over silence (ASR hallucinations).

    Starts move to the onset of the voiced region they belong to; ends move to the last voiced frame before the next
    word. A word with no voiced frame anywhere near its span was never said and is returned in `dropped`.
    """
    out, dropped = [], []
    for i, w in enumerate(words):
        s, e = float(w["start"]), float(w["end"])
        nxt = float(words[i + 1]["start"]) if i + 1 < len(words) else e + 0.6
        prev_start = out[-1]["start"] if out else 0.0
        if mask.voiced_fraction(s - 0.08, max(e, s + 0.1) + 0.08) == 0.0:
            dropped.append({**w, "reason": "no speech energy under this word"})
            continue
        if mask.is_quiet(s):
            onset = mask.first_voiced(s, min(s + 0.25, max(nxt, s + 0.05)))
            if onset is not None:
                s = onset
        else:
            k = s
            lo = max(prev_start + 0.05, s - 0.12)
            while k - 0.01 >= lo and not mask.is_quiet(k - 0.01):
                k -= 0.01
            s = k
        end_bound = max(nxt, s + 0.05)
        last = mask.last_voiced_end(s, end_bound)
        e = last if last is not None else s + 0.08
        e = min(max(e, s + 0.04), end_bound)
        out.append({**w, "start": round(s, 3), "end": round(e, 3)})
    for a, b in zip(out, out[1:]):
        if a["end"] > b["start"]:
            a["end"] = round(max(a["start"] + 0.02, b["start"]), 3)
    return out, dropped


def words_to_segments(words: list[dict], gap: float = 0.8, max_words: int = 28) -> list[dict]:
    segments: list[dict] = []
    cur: list[dict] = []

    def flush() -> None:
        if cur:
            segments.append({"start": cur[0]["start"], "end": cur[-1]["end"],
                             "text": " ".join(w.get("w") or w.get("text", "") for w in cur)})
            cur.clear()

    for w in words:
        if cur and (w["start"] - cur[-1]["end"] > gap or len(cur) >= max_words):
            flush()
        cur.append(w)
        if re.search(r"[.!?…][\"')\]]*$", w.get("w") or w.get("text", "")):
            flush()
    flush()
    return segments


def build_transcript(parsed: dict, model_name: str, rng: tuple[float | None, float | None]) -> dict:
    words, removed = collapse_loops(parsed["words"])
    words = hinglish.clean_transcript_words(words)
    words = [{**w, "text": w["w"]} for w in words]
    return {
        "engine": "whisper.cpp",
        "model": model_name,
        "language": "hi-Latn",
        "script": "hinglish",
        "timing": parsed.get("timing"),
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
def transcribe(media: str, work_dir: Path, start: float | None = None,
               end: float | None = None, cfg: dict[str, str] | None = None) -> dict:
    cfg = cfg or config.load()
    binary = config.find_whisper_bin(cfg)
    model = config.find_whisper_model(cfg)
    if binary is None:
        raise ToolError("whisper-cli not found. On macOS: `brew install whisper-cpp`, or set WATCH_WHISPER_CPP_BIN.")
    if model is None:
        raise ToolError("whisper.cpp model not found. Re-run the video-skills setup (it downloads the Hinglish model "
                        f"{config.HINGLISH_MODEL}) or set WATCH_WHISPER_MODEL.")
    if not config.is_hinglish_model(model):
        log(f"note: {model.name} is a stock Whisper model; Hindi is decoded as Hindi and romanised. "
            f"Install {config.HINGLISH_MODEL} for natural Hinglish spelling.")
    work_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="watch-asr-", dir=str(work_dir)) as tmp:
        wav = extract_wav(media, Path(tmp) / "audio.wav", start, end)
        prefix = Path(tmp) / "out"
        log(f"transcribing with whisper.cpp ({model.name}); large models can take several minutes…")
        run_whisper(build_command(binary, model, wav, prefix, cfg))
        out_json = Path(str(prefix) + ".json")
        if not out_json.is_file():
            raise ToolError("whisper-cli finished but wrote no JSON; check the build supports -oj.")
        data = json.loads(out_json.read_text(encoding="utf-8", errors="replace"))
    parsed = parse_whisper_json(data, offset=start or 0.0)
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
    print(f"language={t['language']}  timing={t['timing']}  words={len(t['words'])}  segments={len(t['segments'])}  "
          f"loops_collapsed={t['loops_collapsed']}")
    for w in t["words"][:15]:
        print(f"  {fmt_time(w['start'], 2):>8}  {w['w']}")
