---
name: video-take-geometry
description: Reframes approved footage only when the selected aspect or intended composition requires it.
---

# Take geometry and reframing

Use this skill only when a new aspect, a user-selected layout, or a specific visible problem requires a framing change. Keep the source framing when it already fits. Do not add routine punch-ins, split screens, PiP, speaker mattes or movement to every shot.

```bash
ROOT="<user-selected-video-folder>"
W="$ROOT/.video-pipeline"
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
PY="${VIDEO_ENGINE_DIR:-$HOME/.config/video-skills/engine}/.venv/bin/python3"
```

## Review each shot

Read the selected framing and aspect in `resolved-spec.json`, then inspect the actual frames and `cut-map.json`. Note where the subject, product, hands, labels, screen text and other important details move. Face detection is a measurement aid; it does not decide the story or establish what an object is.

If the source aspect already suits delivery, keep it. For a different aspect, create a per-shot crop only where the full action remains visible. If a crop would lose useful product detail or context, preserve the full image using a restrained fit/background treatment or explain the trade-off for review. Do not invent a second visual to fill an unused region.

Use split screen or PiP only when the user selects it and both views have actual, relevant material. Use a matte only when requested, when the source edges are clean enough, and when a local tool can produce a usable result. Never cover the face, hands, product, or meaningful source text with captions or graphics.

## Produce and inspect a reframe

Keep derived video, crop maps and snapshots under `$W/hyperframes/` or `$W/review/`. Use the configured engine interpreter for pipeline scripts:

```bash
"$PY" "$ENG/scripts/reframe.py" --video "$W/hyperframes/input-video.mp4" \
  --aspect 9:16 --cut-map "$W/cut-map.json" \
  --out "$W/review/reframe-9x16.json" --render "$W/hyperframes/input-9x16.mp4"
```

Inspect the rendered contact sheet across every shot and every crop boundary. Reject any crop that clips a face, a product interaction, a label, or text needed to understand the footage. Rerun the plan and approval gate if the selected framing or cut changes.

Do not use fixed split ratios or safe margins for every platform. Use measured canvas dimensions and the user's delivery target. Do not invoke `npx` or fetch an unpinned tool during an edit. Keep all project work under `.video-pipeline/` and the verified final render under `Exports/`.
