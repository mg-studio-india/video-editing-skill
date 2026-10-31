---
name: video-review-gate
description: Reviews the final render, audio, captions, frames and editable HyperFrames project before delivery.
---

# Final review

```bash
ROOT="<user-selected-video-folder>"
W="$ROOT/.video-pipeline"
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
PY="$ENG/.venv/bin/python3"
F="$ROOT/Exports/<project>-v1.mp4"
```

Read the approved `storyboard.json` canvas and `resolved-spec.json` to determine the expected aspect, platform and audio target. Do not assume every project is a vertical Short.

Run the render review and keep its reports inside the hidden workspace:

```bash
"$PY" "${VIDEO_SKILLS:-$HOME/.agents/skills}/video-review-gate/scripts/review.py" \
  --final "$F" --preset <youtube|shorts|longform|broadcast> \
  --res <expected-WxH> --storyboard "$W/storyboard.json" \
  --transcript "$W/transcript.json" --report-dir "$W/review"
```

Inspect the generated review sheet and watch the complete export with sound. Check the source-led story, crop safety, graphic readability, caption wording/timing, audio transitions, echo/reverb residuals, clipping, black frames, and whether every added visual has a source or approved-asset basis. Do not call dereverb complete echo cancellation.

If the local HyperFrames CLI is installed, validate the editable project with its configured binary:

```bash
"$ENG/../node_modules/.bin/hyperframes" check "$W/hyperframes"
```

If that path is unavailable, use the already configured local engine binary path. Do not use `npx` or download a replacement during review. Keep reports and snapshots under `$W/review`; the user-facing `Exports/` folder should contain the deliverable.
