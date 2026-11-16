---
name: video-style
description: Sets the look of an edit - picks one of the default styles (or one matched to the user's references), applies the user's own brand files, fixes and grades the raw footage, and sets the delivery format (aspect, reframe, resolution). Writes style.json. Use after video-pipeline analyze and when the user asks about colour, grade, look, format or aspect.
---

# Style, grade and format

Same variables as `video-pipeline`. Styles live in `$SK/video-style/styles/`:

| style | for |
|---|---|
| `clean-creator` (default) | talking-head reels and explainers: measured colour correction, white captions, yellow keyword pop |
| `business-explainer` | money, markets, startups (Hinglish): gold/green, charts, counters, headlines, maps |
| `tech-minimal` | tech, product, tutorials: true colour, cyan, UI/code blocks, calm motion |
| `cinematic-story` | stories, vlogs, founders: warm grade, serif titles, few graphics, slow motion |

Each style sets colours, fonts, caption look, card look, motion timing, `color_grade`, `audio_tone`, the HyperFrames
catalog tags to prefer/avoid, and a small sound palette.

## 1. Pick the style

- User references in `references/` lead: run `video-watch` on them, then pick the closest default style and adjust
  only what the references clearly show (accent colour, caption weight/case, motion pace, how often graphics appear).
  Measure colours with `"$PY" "$SK/video-style/scripts/palette.py"` on reference frames; never guess hex values.
- No references: offer the 2-3 styles that fit the brief and footage, with a one-line reason each; the user picks.
- Brand files (`$ROOT/brand/`, else the workspace `brand/`; snapshot list in `$W/context/brand-inputs.json`) override
  the style where they say something. With no brand files, the style is the whole look. Never invent brand values; never read `MEMO.md`/`STYLE-GUIDE.md`.

Write `$W/style.json` = the chosen style file, with brand/reference overrides applied. Keep its keys (the renderer
reads them). Fonts must be files that exist (`@engine/assets/fonts/...` or the user's own files).

## 2. Fix and grade the footage

`analyze` already converted the source to constant frame rate SDR (HDR is tone-mapped) and measured a neutral
correction: compare frames in `$W/preview/grade-preview.jpg`.

- `color_grade` in `style.json`: `dynamic` (measured: fixes white balance, exposure, contrast; the safe default),
  `enhanced-natural`, `vibrant-enhanced`, `neutral-true`. Choose by looking at skin tones and whites in the preview.
- To compare every preset on one real frame:
  `"$PY" "$ENG/scripts/grade.py" preview --input "$W/raw/source-video.mp4" --at <seconds> --out "$W/preview/grade-compare.jpg"`.
- The grade is applied once, at assemble, together with the cut.

## 3. Format

- Aspect: `storyboard.json` → `canvas` (`[1080,1920]` 9:16, `[1080,1080]` 1:1, `[1920,1080]` 16:9).
- If the canvas aspect differs from the footage, add `"reframe": {"aspect": "9:16", "mode": "static"}` (face-aware crop
  per shot; `follow` tracks the face; `center` = plain centre crop). Check the result in the render sheet: no
  cropped faces, hands, products or on-screen text.
- Resolution: 1080-wide by default; `"resolution": "4k"` in the storyboard for UHD.
- Audio delivery: `resolved-spec.json` → `audio.preset` (`shorts`/`youtube` −14 LUFS, `longform` −16, `broadcast` −23)
  and `audio.tone` (`neutral`, `clear`, `warm`; the style's `audio_tone` is a good default).

Summarise for the user: style chosen and why, brand rules applied, grade, aspect/reframe, caption look.
