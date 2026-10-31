---
name: video-transcribe
description: Word-level transcription with whisper.cpp in the shape the cut, caption and timing tools read; resolves plan phrases to times after each cut. Use twice per edit (raw take, then flat cut) and when the user asks to transcribe, get word timestamps, or says words or timings are wrong.
---
# transcribe

Every cut, caption and animation lands on a word, so word timing is the foundation. whisper.cpp, locally, in one shape
every engine script reads (each word has `text`, `w`, `start`, `end`).

> [!IMPORTANT]
> **Virtual Environment (STRICT)**: Execute scripts with the configured video-engine virtual environment. Never install these dependencies into system Python.
> **Roman English decoding (STRICT)**: The pipeline always forces Whisper's `en` decoder and writes Roman-script output. Hindi is not a selectable pipeline language, and auto-detection is disabled because it can switch scripts. Verify uncertain names and code-switched words against the audio.

```bash
ROOT="<user-selected-video-folder>"
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"; W="$ROOT/.video-pipeline"
ENGINE_ROOT="${VIDEO_ENGINE_DIR:-$HOME/.config/video-skills/engine}"; PY="$ENGINE_ROOT/.venv/bin/python3"
"$PY" "$ENG/scripts/transcribe.py" <media> --out <transcript.json> [--window 25] [--lang en] [--prompt "names"] [--no-fillers]
```

**Pass 1, the raw take** (on the clean clip from `video-audio clean`):
`"$PY" "$ENG/scripts/transcribe.py" "$W/raw/<clip>-clean.mp4" --out "$W/transcript-raw.json" --window 25`. Use `--window 25` on takes over
~3 min or with many retakes: ~25 s windows split at silences keep each retake in view (whisper can skip a repeated
sentence and loop on silence; loops are collapsed, see `loops_collapsed`).

**Pass 2, the flat cut**, after every `apply-cut`:
```bash
ffmpeg -y -v error -i "$W/hyperframes/input-video.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$W/audio.wav"
"$PY" "$ENG/scripts/transcribe.py" "$W/hyperframes/input-video.mp4" --out "$W/transcript.json"
"$PY" "$ENG/scripts/resolve-anchors.py" --plan "$W/storyboard.plan.json" --transcript "$W/transcript.json" \
  --out "$W/storyboard.json" [--jump-frames "$W/jump-frames.json"]
```
Never reuse the raw transcript after a cut or shift times by hand: a stale transcript is the top cause of captions and
cards on the wrong word. Unresolved anchors are handled by `video-plan-storyboard`. One phrase by hand:
`"${VIDEO_SKILLS:-$HOME/.agents/skills}/video-transcribe/scripts/phrase-times.py" --transcript "$W/transcript.json" "three tools" [--after T]` (`NOT FOUND` = cut or misheard).

- **Word Verification & Corrections (STRICT):** Immediately after transcription, verify words with:
  `"$PY" "${VIDEO_SKILLS:-$HOME/.agents/skills}/video-transcribe/scripts/verify-words.py" --transcript "$W/transcript.json"`
  Review flagged phonetic distortions and apply high-confidence fixes with `--auto-fix`, or add project-specific names/jargon:
  `"$PY" "${VIDEO_SKILLS:-$HOME/.agents/skills}/video-transcribe/scripts/verify-words.py" --transcript "$W/transcript.json" --add "misheard=Correct"`
  All fixes are recorded in `$W/corrections.json` and automatically preserved across every future transcription pass without shifting audio timings. Never retype times by hand.
- **Fillers kept by default** (the cut tools need "um/uh" to find restarts); `--no-fillers` for a finished cut.
- **Names and jargon:** `--prompt "Claude, HyperFrames, Veo"` spells them right for captions and phrase lookups.
- **Language:** fixed to English decoding (`--lang en`); no Hindi or auto-detect option. Romanize uncertain non-English speech only when the audio supports the spelling, and mark low-confidence words for review.
- **Timing check** on a new setup: `"$PY" "$ENG/scripts/transcribe_cpp.py" <clip> --end 20`; times should rise and match
  the audio. Many identical times: set `WATCH_WHISPER_DTW=large.v3` and rerun.
- Starts come from the transcript, ends from the audio: `video-cut-audit` measures edges, so don't correct times here.

Record pass, file, words, language, windows and loops in `project.json`; after pass 2 mark caption and beat steps
`stale`. Install, model and config: `references/whisper-setup.md`.
