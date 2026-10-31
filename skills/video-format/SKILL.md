---
name: video-format
description: Chooses evidence-led framing and local HyperFrames compositions for approved source footage.
---

# Video format and layout

Layout serves the footage, the user's brief, the selected platform and brand rules. The source framing is the default. A catalog style, composition, split screen, PiP, card or crop is never applied just to make the edit feel busier.

```bash
ROOT="<user-selected-video-folder>"
W="$ROOT/.video-pipeline"
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
ENGINE_ROOT="${VIDEO_ENGINE_DIR:-$HOME/.config/video-skills/engine}"
HF="$ENGINE_ROOT/node_modules/.bin/hyperframes"
```

## Review before choosing a layout

Read the approved `storyboard.json`, `style.json`, `resolved-spec.json`, source evidence, selected references and brand inputs in `$W`. Inspect the actual frames at every proposed layout change. Keep source facts, reference style observations and brand requirements separate.

Use the user's platform/aspect answer. When the user delegates, preserve source framing unless the footage or delivery format gives a clear reason to reframe. Check that any crop keeps the product, hands, face, screen content and relevant on-screen text visible throughout the shot. If a crop loses meaningful content, preserve the full frame or ask about a fit treatment.

Do not assume the video opens with a hook, contains a presenter, has empty canvas that needs filling, or needs a final card. Keep silent product footage and its actual sequence intact. Do not invent stats, claims, interfaces, article text, logos, or product features. Negative space can remain empty when that reads cleanly.

## Select local HyperFrames assets

Prefer an existing local HyperFrames composition or component when its purpose fits an approved, source-supported beat and the brand guide allows its treatment. Inspect the local HTML, its internal `data-composition-id`, declared variables and any required assets before proposing it. Components that depend on a parent composition must be used through that supported composition.

Record a selected composition in the approved storyboard with its local `src`, exact `comp_id`, source evidence references and valid variable values. The pipeline stages only explicitly selected blocks and validates their metadata. It does not stage every match or apply a whole style blueprint automatically. If no local asset fits, use the existing footage and caption treatment; do not fetch a replacement during the edit.

## Frame and brand checks

- Use the measured canvas and user-selected platform safe areas; do not impose one fixed margin or split ratio on every aspect.
- Keep captions legible without covering the action, product details, faces or important source text.
- Apply colors, fonts, logo clear space and required/excluded elements from the reviewed brand guide.
- Keep all custom composition files and copied assets in `$W/hyperframes/`; preserve the installed engine catalog.
- Use the bundled HyperFrames creative, core, registry and animation guidance for valid composition structure and seek-safe animation.

Use only the configured local HyperFrames CLI when a CLI inspection is needed:

```bash
"$HF" check "$W/hyperframes"
```

Do not use `npx`, CDN assets, Swift Package Manager or unpinned frameworks. Render only after the plan and cut pass the pipeline's user-approval gate. Keep the deliverable in `$ROOT/Exports/` and all project work in `$W/`.
