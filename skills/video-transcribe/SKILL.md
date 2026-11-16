---
name: video-transcribe
description: Hinglish transcripts (Hindi and English as spoken, always in Roman script) with word timing snapped to the actual speech, so captions, cuts and graphics land on the right word. Use to check or fix a transcript, correct misheard names, find when a phrase is said, or transcribe any clip.
---

# Transcribe (Hinglish, in sync)

`video-pipeline analyze` already transcribes the cleaned voice once:
- `$W/transcript.source.json`: source timeline (the cut is built from it);
- `$W/hyperframes/transcript.json`: the same words on the cut timeline (captions, beats, research use it).

The flat transcript is mapped through the exact cut map, not re-transcribed, so captions show the words you reviewed
and stay in sync with the audio. Same variables as `video-pipeline`.

## How it stays faithful and in sync

- **Model:** a Whisper fine-tune that writes Hindi/English speech as Roman Hinglish (`ggml-apex-hinglish-q8_0.bin`).
  With a stock Whisper model the speech is decoded as Hindi and romanised, never forced to English (that translates).
- **No topic prompt.** A prompt sentence leaks into transcripts. Only names/jargon are passed (`--names` in analyze).
- **Timing:** DTW word alignment when the whisper-cli build supports it, then every word is snapped to the measured
  speech energy of the cleaned voice. Words with no speech under them (silence hallucinations) are dropped and listed
  in `dropped_no_speech`.

## Fix misheard words

```bash
V="$SK/video-transcribe/scripts/verify-words.py"
"$PY" "$V" --transcript "$W/transcript.source.json"                       # flags likely mishearings
"$PY" "$V" --transcript "$W/transcript.source.json" --add "zomato=Zomato"  # adds a correction
```

Corrections live in `$W/corrections.json` and are applied on every re-run without moving any times. After fixing,
run `"$PY" "$ENG/scripts/parallel_pipeline.py" recut --project "$ROOT"` so the flat transcript and captions update.
Never edit word times by hand.

## Find a phrase

`"$PY" "$SK/video-transcribe/scripts/phrase-times.py" --transcript "$W/hyperframes/transcript.json" "sabse bada"` →
flat time of each occurrence (`NOT FOUND` = cut out or misheard).

## Any other clip

```bash
"$PY" "$ENG/scripts/transcribe.py" <media> --out <transcript.json> [--names "..."] [--window 25]
```

`--window 25` splits long takes at silences (keeps retakes visible). Setup check: `"$PY" "$ENG/scripts/setup.py"`
shows the model (Hinglish or stock), whisper-cli and DTW support.
