---
name: video-transcribe
description: Word-level transcription with whisper.cpp in the shape the cut, caption and timing tools read; resolves plan phrases to times after each cut. Use twice per edit (raw take, then flat cut) and when the user asks to transcribe, get word timestamps, or says words or timings are wrong.
---
# transcribe

Every cut, caption and animation lands on a word, so word timing is the foundation. whisper.cpp, locally, in one shape
every engine script reads (each word has `text`, `w`, `start`, `end`).

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"; W="videos/<project>"
python3 "$ENG/scripts/transcribe.py" <media> --out <transcript.json> [--window 25] [--lang en] [--prompt "names"] [--no-fillers]
```

**Pass 1, the raw take** (on the clean clip from `video-audio clean`):
`transcribe.py "$W/raw/<clip>-clean.mp4" --out "$W/transcript-raw.json" --window 25`. Use `--window 25` on takes over
~3 min or with many retakes: ~25 s windows split at silences keep each retake in view (whisper can skip a repeated
sentence and loop on silence; loops are collapsed, see `loops_collapsed`).

**Pass 2, the flat cut**, after every `apply-cut`:
```bash
ffmpeg -y -v error -i "$W/hyperframes/input-video.mp4" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$W/audio.wav"
python3 "$ENG/scripts/transcribe.py" "$W/hyperframes/input-video.mp4" --out "$W/transcript.json"
python3 "$ENG/scripts/resolve-anchors.py" --plan "$W/storyboard.plan.json" --transcript "$W/transcript.json" \
  --out "$W/storyboard.json" [--jump-frames "$W/jump-frames.json"]
```
Never reuse the raw transcript after a cut or shift times by hand: a stale transcript is the top cause of captions and
cards on the wrong word. Unresolved anchors are handled by `video-plan-storyboard`. One phrase by hand:
`phrase-times.py --transcript "$W/transcript.json" "three tools" [--after T]` (`NOT FOUND` = cut or misheard).

- **Correct misheard words, keep the timing.** After pass 1 read the transcript for names, products, jargon and
  homophones whisper got wrong (Hindi names and mixed-language lines especially), and record each fix once:
  `python3 "$ENG/scripts/fix-words.py" --transcript "$W/transcript-raw.json" --add "cap cut=CapCut" --add "hyper frames=HyperFrames"`.
  Fixes go to `$W/corrections.json` and `transcribe.py` reapplies them on every later pass (the flat cut, Shorts) and
  passes the correct spellings to whisper as hints. Merged words span the originals; split words share their span;
  punctuation is kept. Never retype times by hand.
- **Fillers kept by default** (the cut tools need "um/uh" to find restarts); `--no-fillers` for a finished cut.
- **Names and jargon:** `--prompt "Claude, HyperFrames, Veo"` spells them right for captions and phrase lookups.
- **Language:** one per file; force with `--lang` (`en`, `hi`) for mixed speech or a wrong guess (default from
  `WATCH_WHISPER_LANG`). Read the first transcript of a new language setup before relying on it.
- **Timing check** on a new setup: `python3 "$ENG/scripts/transcribe_cpp.py" <clip> --end 20`; times should rise and match
  the audio. Many identical times: set `WATCH_WHISPER_DTW=large.v3` and rerun.
- Starts come from the transcript, ends from the audio: `video-cut-audit` measures edges, so don't correct times here.

Record pass, file, words, language, windows and loops in `project.json`; after pass 2 mark caption and beat steps
`stale`. Install, model and config: `references/whisper-setup.md`.
