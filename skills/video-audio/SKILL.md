---
name: video-audio
description: Makes the voice sound clean and studio-polished in two passes run once each - pass 1 removes room echo and noise (WPE + DeepFilterNet) before transcription, pass 2 polishes, mixes effects/music and masters loudness at render. Use for "voice is echoey/noisy/robotic", "clean the audio", loudness or music questions.
---

# Audio: two passes, once each

```
pass 1 (analyze)   source -> WPE dereverb -> DeepFilterNet3 (strength from measured noise) -> 70 Hz high-pass
                   -> alignment check -> audio/voice-clean.wav (lossless; the edit, the transcript and the cut use it)
pass 2 (assemble)  flat-cut voice -> 80 Hz high-pass, gentle EQ, de-ess, 2.5:1 compression
                   + sound effects (untouched) + music (ducked under the voice)
                   -> loudness to target -> true-peak limiter -> fade over the tail -> one AAC encode
```

Why it sounds natural: denoise and dereverb happen exactly once, on the voice alone, losslessly. Re-running them,
spectral "late reverb" subtraction, gates and stacked passes are what made voices robotic and are gone. Sound effects
never go through voice processing. Same variables as `video-pipeline`.

## Pass 1 strength

`analyze` measures the signal-to-noise ratio and picks DeepFilterNet's strength: quiet room → light (natural tone),
fan/traffic → strong with post-filter. Check `$W/audio/voice-clean.json` (noise floor and SNR before/after) and ask
the user to listen to `$W/preview/audio-before-after.wav` (same lines, original then cleaned, loudness-matched).

| User hears | Re-run analyze with |
|---|---|
| hiss/fan/traffic still there | `--denoise strong` (or `maximum`) |
| voice thin, watery, "underwater" | `--denoise light` or `medium` |
| room echo still there | `--dereverb strong` |
| voice dull or boxy after cleaning | `--dereverb light` |
| clean studio recording | `--denoise light --dereverb off` |

Re-running `analyze` rebuilds the transcript and cut from the new audio. Severe echo cannot be fully removed; say so.

## Pass 2 and delivery

`$W/resolved-spec.json` → `audio`: `preset` (`shorts`/`youtube` −14 LUFS, `longform` −16, `broadcast` −23; true peak
−1 dBTP), `tone` (`neutral`, `clear` = more presence, `warm` = fuller), `music_path` (a file inside the project) and
`music_db` (default −20, ducked further under speech). The render report `$W/review/<name>-audio.json` has the
measured result.

Measure any file: `"$PY" "$ENG/scripts/audio-chain.py" measure <media>`. Manual pass 1 on a file:
`"$PY" "$SK/video-audio/tools/voice-clean.py" <media> --out <clean.wav> [--denoise strong] [--dereverb strong]`.
Troubleshooting by symptom: `references/tuning.md`. You cannot hear the result: report numbers and ask the user to
listen.
