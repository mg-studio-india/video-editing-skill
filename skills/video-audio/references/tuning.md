# Audio tuning and troubleshooting

Change one variable at a time. Keep the original and compare short excerpts at matched playback loudness; a louder version can seem better even when it is more distorted. Save a new default only after repeated successful tests on the user's recordings.

| Symptom | Likely cause | Next test |
|---|---|---|
| Hiss/fan/AC still audible | Denoise too light, wrong model, or noise resembles speech | Increase denoise slightly or use the single default neural enhancer (Resemble Enhance); compare before/after. Do not install or stack a second neural model by default. |
| Voice sounds watery, metallic, swirly | Neural denoise too aggressive or model mismatch | Use a less aggressive setting, try denoise-only mode, or bypass enhancement. |
| Room echo remains | Ordinary denoising does not remove reverberation | First test the default Resemble Enhance output. If echo remains, document the limitation and A/B-test a dedicated dereverberation model only as a separate, deliberate follow-up—not as part of the default installation. Severe echo may not be fully removable. |
| Voice is thin | High-pass cutoff too high or excessive high-frequency processing | Lower the high-pass cutoff or bypass it, then A/B. |
| Voice is boomy/rumbling | Proximity effect, handling noise, HVAC rumble | Increase high-pass gradually; do not cut low frequencies if they contain wanted voice fundamentals. |
| Voice is boxy/muddy | Room/mic coloration, often low-mid buildup | Try a modest broad EQ cut only after listening; do not apply a fixed notch to all files. |
| S/T sounds sting or voice lisps | Harshness or overdone de-essing | Use less de-essing; avoid broad fixed cuts that remove intelligibility. |
| Quiet words get lost | Too much dynamic range or weak source | Gentle compression/automation; don't solve by excessive makeup gain. |
| Pauses get noisy after compression | Compression lifts the noise floor | Reduce compression/makeup; consider gentle expansion or clip automation. Confirm cleanup stage actually helped. |
| Voice pumps/breathes | Compressor settings too aggressive or release mismatch | Reduce compression and adjust release; listen to sentence endings. |
| Background voice remains | Denoiser/gate cannot reliably distinguish speakers | If this is a real requirement, add a dedicated speech-separation or target-speaker extraction model as an optional extra; do not install it for ordinary cleanup. Verify wanted words are preserved. |
| Background sound chopped abruptly | Gate/threshold too aggressive | Use gentler expansion/automation and preserve breaths/word tails. |
| Word buzzing / edge flutter / vowel sputtering | Downward expander / gate attack too fast (<10ms) or release too short (<80ms) modulating fundamental pitch cycles (100-160 Hz); excessive stacked treble boosts | Remove fast-attack gate; rely on RNNoise continuous neural masking (arnndn) and smooth optical leveling (attack 15-20ms, release >= 70-140ms, 3-4 dB soft knee); avoid stacking treble boosts on top of gates. |
| Output sounds louder but not clearer | Loudness bias | Loudness-match the A/B comparison. Fix clarity first, normalize last. |
| True peak exceeds ceiling | Peaks/clipping in source or inadequate final limiting | Check source for clipping, use a suitable true-peak-aware workflow, remeasure final output. |
| Loudness misses target | Wrong measurement stage, normalization not measured, or limiter overworking | Measure the final assembled mix and use a proper two-pass loudnorm workflow where needed. |
| Section joins jump in level | Sections processed independently | Assemble first, then master the completed mix once. |

## Rules

- Default installation includes FFmpeg and one neural speech enhancer (Resemble Enhance), not multiple neural model packages.
- Local open-source inference has no per-minute API charge; account for disk space, install/download time, CPU/GPU time, and electricity.

- Do not use EQ to pretend to remove broadband noise or room echo.
- Do not stack multiple denoisers or enhancement models without an A/B test demonstrating improvement.
- Do not raise loudness beyond the requested target to make a file seem better.
- Do not claim universal SNR thresholds such as 80 dB for real-world dialogue.
- Keep the cleanest, most natural version—not necessarily the most processed one.
- If a recurring setting helps the user's mic/room, update `SKILL.md` with the actual tested setting and describe the source conditions.
