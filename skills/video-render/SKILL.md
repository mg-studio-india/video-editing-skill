---
name: video-render
description: Renders an approved project through the video-pipeline, verifies the master, and publishes a versioned export.
---

# Render and export

Use the project-scoped pipeline entry point so approval, selected audio settings, render verification and export publishing stay connected.

```bash
ROOT="<user-selected-video-folder>"
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
ENGINE_ROOT="${VIDEO_ENGINE_DIR:-$HOME/.config/video-skills/engine}"
PY="$ENGINE_ROOT/.venv/bin/python3"
W="$ROOT/.video-pipeline"
```

## Before rendering

- Confirm the user approved the current storyboard, cut, framing, captions, brand treatment and sound choices.
- Confirm `$W/gates.json` contains a current approval fingerprint. Editing the plan, cut, style, source evidence, references or brand inputs requires review and approval again.
- Review the source contact sheet, relevant reference and brand previews, selected HyperFrames composition and prior render notes.
- Keep the chosen aspect and audio preset from `resolved-spec.json`; strong dereverb is the default.

## Render

```bash
"$PY" "$ENG/scripts/parallel_pipeline.py" assemble --project "$ROOT" --dereverb strong
```

The pipeline stages only selected local HyperFrames compositions, renders under `.video-pipeline/scratch/`, runs its output verification, and publishes the next `$ROOT/Exports/<project>-vN.mp4` only after success. It retains earlier exports. Keep the audio report, verification report and HyperFrames project under the hidden workspace.

If a render fails, read the stage error and its report, fix that cause, then rerun the approved project. If the change affects content, timing, framing or treatment, update the plan and record user approval again first. Use only the configured local HyperFrames CLI; do not invoke `npx` or fetch an unpinned package during rendering.
