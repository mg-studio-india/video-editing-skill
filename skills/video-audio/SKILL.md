---
name: video-audio
description: Cleans and masters project audio with measured local processing; strong dereverb is the pipeline default.
---

# Audio cleanup and mastering

Keep the original media untouched. The project pipeline uses strong dereverb, asks before adding music or sound effects, and keeps audio work under `.video-pipeline/`.

```bash
ROOT="<user-selected-video-folder>"
W="$ROOT/.video-pipeline"
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
ENGINE_ROOT="${VIDEO_ENGINE_DIR:-$HOME/.config/video-skills/engine}"
PY="$ENGINE_ROOT/.venv/bin/python3"
```

## Echo and reverb

Before transcription, the project pipeline passes the source audio through multichannel WPE dereverberation and a late-reverb suppression stage. It keeps the processed voice aligned with the source picture and uses that cleaned audio for speech recognition. At final render, the existing audio master runs twice in sequence: pass one processes the rendered mix, then pass two re-processes pass one's cleaned audio. The passes use lossless WAV intermediates; selected music is mixed once on pass one. The final AAC encode happens only after pass two.

This can reduce room tails and echoes, but it cannot guarantee their removal. Listen to the source and processed versions, check for metallic or watery artifacts and clipped word endings, and preserve the less-damaged version if processing harms speech. Do not claim complete echo cancellation or speaker isolation.

For a manual diagnostic pass, keep scratch outputs inside the project workspace:

```bash
"$PY" "${VIDEO_SKILLS:-$HOME/.agents/skills}/video-audio/tools/voice-clean.py" \
  "$W/raw/standard-input.mp4" --video "$W/raw/standard-input.mp4" \
  --out "$W/scratch/audio-clean-preview.mp4" --keep "$W/scratch/voice-clean" --no-deep-filter
```

The optional DeepFilterNet stage is separate from WPE and late-reverb suppression. The pipeline does not silently enable it in the transcription clean pass; denoising is a recorded user choice for the final master.

## Master and inspect

`audio-chain.py` measures the source, selects the chosen denoise level, applies strong dereverb by default, masters loudness and true peak for the selected delivery preset, and writes a JSON report. `render.py` runs it twice over the audio in sequence. It stores a combined `$W/` report plus per-pass reports and scratch audio; the final video is published only after render verification.

Use only the configured local tools. Do not add music, SFX or generated sound unless the user selected them. Keep every chosen music file inside `$ROOT/`, record its path in `resolved-spec.json`, and retain its source/license information with the project.
