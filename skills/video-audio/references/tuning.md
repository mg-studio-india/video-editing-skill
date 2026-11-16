# Audio tuning by symptom

Change one thing at a time and compare loudness-matched excerpts (`preview/audio-before-after.wav` is matched).
Louder always sounds "better"; judge clarity, not level.

| Symptom | Cause | Fix |
|---|---|---|
| Hiss, fan, AC, traffic remain | DeepFilterNet strength too low for this room | `analyze --denoise strong`, then `maximum` |
| Watery, metallic, "underwater" voice | Denoise too strong for a fairly clean recording | `analyze --denoise medium` or `light` |
| Room echo remains | Long reverb tail | `analyze --dereverb strong`; very live rooms cannot be fully fixed |
| Voice thin or boxy after cleaning | Dereverb removing body | `analyze --dereverb light` or `off` |
| Robotic or phasey voice | Audio processed twice (old pipeline) or an external tool stacked on top | Use only the pipeline's two passes; never run another denoiser on `voice-clean.wav` |
| Boomy / rumble | Handling noise, proximity effect | Pass 1 high-pass is 70 Hz, pass 2 80 Hz; mention mic placement for next time |
| Harsh S sounds | Bright mic | `audio.tone: "warm"` |
| Muffled | Dull mic or heavy denoise | `audio.tone: "clear"`; try a lighter `--denoise` |
| Music fights the voice | Bed too loud | lower `audio.music_db` (e.g. −24) |
| Loudness off target | Very short or very sparse speech | Read `review/<name>-audio.json`; integrated loudness needs a few seconds of speech |
| Words and lips out of sync | Should not happen (CFR ingest, sample-aligned cleaning) | Check `audio/voice-clean.json` `lag_corrected_ms` and `apply-cut.py`'s verify line; report it |

Rules: one denoiser (DeepFilterNet), one dereverb (WPE), each once. No gates, no spectral subtraction, no second pass.
Do not raise loudness above the delivery target. Keep the most natural version, not the most processed one.
