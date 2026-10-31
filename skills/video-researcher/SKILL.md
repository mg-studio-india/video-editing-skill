---
name: video-researcher
description: Performs source-cited external fact research only when the user requests it for a video project.
---

# Video research

This is an optional factual research step. The project pipeline does not require internet research to create a footage-led edit. Do not run this skill to invent a hook, trend-based story, format menu, brand identity or visual proof.

Use it when the user asks to verify a factual claim, research a named subject, or find a specific external source. Keep results in `$ROOT/.video-pipeline/research/` so the project folder stays organized.

## Evidence rules

- Prefer primary sources and provide direct links for every external fact that may appear in the edit.
- Record the source, publication/update date and the exact claim it supports. Separate sourced facts, attributed statements and inference.
- If reliable evidence is missing or contradictory, mark the claim unresolved and leave it out of on-screen copy.
- User footage remains the only evidence of what happens in the source video. External research and reference videos do not prove the product's appearance, use or performance.
- Never infer customer counts, revenue, market share, conversion, testimonials, UI, product features or outcomes from a visual reference.
- Do not source a logo for every spoken entity. Use the user's supplied brand assets; retrieve another asset only after the user asks and record its source and license.

## Creative boundaries

Do not require a research gate before storyboarding. Do not present generic format menus, viral hook formulas, fixed beat structures, benchmark-derived pacing targets or recording requests unless the user asks for them. Reference matches are optional visual suggestions, and the project index can supply candidates without external trend research.

When research is approved, give the user a short summary and cited source list. Let the user decide whether verified facts belong in the approved storyboard. Keep the storyboard grounded in source evidence and the selected brand/reference direction. Use only local HyperFrames assets already installed in the configured engine; do not use `npx`, fetch assets automatically, or install another framework during an edit.
