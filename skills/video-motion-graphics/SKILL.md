---
name: video-motion-graphics
description: Adds restrained, deterministic motion to approved, source-grounded HyperFrames compositions.
---

# Motion graphics and animation

Motion should clarify an actual moment in the footage or carry an approved message. Stillness is valid. Do not add counters, charts, badges, transitions, logos or kinetic text just to occupy space or increase pace.

## Ground every element

Before authoring, read the approved storyboard, source evidence, selected style and brand guidance. Every graphic beat must cite source evidence and match a real visual or verified spoken moment. A numeric graphic requires a verified source or a user-provided value. A product graphic must use an approved product asset and verified wording. Omit the graphic when its content cannot be grounded.

Prefer a suitable local HyperFrames composition or component. Inspect its local HTML, declared composition ID, variables and required assets. Use a component only through a supported parent composition. Record the selected block in the approved storyboard; the pipeline stages only the blocks listed there. Do not auto-apply blueprint links or alter unrelated beat structure.

## Animate for meaning

- Keep the motion style consistent with the footage and brand. Use restrained timing, scale and easing; no fixed spring, punch-in or stagger is required.
- Keep all animation seek-safe and deterministic. Tie it to the HyperFrames composition timeline; avoid `Math.random()`, timers, network assets and state that depends on playback history.
- Prefer transform and opacity animation where supported. Check that key frames render correctly when seeking directly to the beginning, middle and end of an animation.
- Preserve the existing simple phrase captions unless the user or brand guide selects another treatment.
- Do not animate unsupported claims or imply events, comparisons, product features or outcomes that are not visible or verified.

Keep project compositions and copied assets under `$ROOT/.video-pipeline/hyperframes/`. Use the configured local HyperFrames CLI and installed creative/animation guidance. Do not invoke `npx`, load a CDN, install Swift packages or fetch unpinned assets during an edit. Changes to direction or cut require a new review and user approval before rendering.
