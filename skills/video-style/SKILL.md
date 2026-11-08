---
name: video-style
description: Applies the user's selected visual direction and brand rules to the pipeline style file.
---

# Video style

Set visual treatment from the approved direction, inspected footage, supplied references and brand guide. This skill styles the edit; it does not invent the story, add beats or decide what the footage means.

```bash
ROOT="<user-selected-video-folder>"
W="$ROOT/.video-pipeline"
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
PY="$ENG/.venv/bin/python3"
```

## Inputs and precedence

Read `resolved-spec.json`, `style-template.json`, the current source contact sheet and the approved `storyboard.json`. Read every brand file listed by `context/brand-inputs.json`; for PDFs, review both extracted text and the page contact sheet. Inspect the user-selected reference material and any chosen local HyperFrames treatment.

Apply explicit brand requirements first, then the user's selected direction and reference, then source-measured correction. Keep brand facts, reference observations and source observations distinct. Do not infer brand colors from footage, fabricate brand tokens, or copy claims and logos from a reference video.

## Style decisions

- Preserve the existing simple phrase-caption treatment for a simple edit unless the user or brand guide selects a change.
- Use only fonts and assets available in the configured engine or supplied by the user. Record the actual font files and selected colors in `style.json`.
- Use `grade.py`'s measured preview as a neutral correction starting point. Apply a stronger look only when the approved reference or brand direction supports it; inspect skin, product color and highlights in the preview.
- Set layout, graphic tone and motion only for treatments already present in the approved storyboard. Do not add cards, accent colors, a CTA, a new type hierarchy or motion effects just to make the file feel styled.
- Keep current audio choices in `resolved-spec.json` → `audio`; strong dereverb is already selected by the pipeline.

Create `style.json` from the stage-ready `style-template.json` and the decisions already saved by the pipeline. Keep the file compatible with `stage.py`; do not add fields that its renderer does not support. Ask only an unanswered question from `QUESTIONNAIRE.md`, and do not repeat a decision already in the brief or brand guide.

Present a concise style summary with the brand rules applied, caption treatment, framing and any selected HyperFrames block. Keep previews and working files in `$W/`; final renders belong in `$ROOT/Exports/`. Rendering still requires the pipeline approval gate.
