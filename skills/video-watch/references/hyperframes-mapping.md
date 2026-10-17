# edit-plan.json → Hyperframes

Hyperframes renders a video from an HTML composition: elements are placed on a timeline with timing attributes, grouped on tracks, and rendered locally (headless browser plus ffmpeg). `edit-plan.json` is designed so that every clip, caption and overlay already carries `start` and `duration` in **seconds on the output timeline**, which is the information a composition needs.

**Verify first.** This file describes the mapping at the level of concepts. It deliberately does not hard-code Hyperframes attribute names, because they are defined by the Hyperframes project and may change. Before writing a composition:

1. If a Hyperframes skill or its docs are available in this session, read them first (the composition contract: timing attributes, clip classes, tracks, sub-compositions, how media elements are sourced).
2. If not, ask the user to install them (for example `npx skills add heygen-com/hyperframes`) or to paste a working sample composition, then mirror that sample exactly.
3. Never guess an attribute name. A wrong guess renders a silent blank video.

## Field by field

| `edit-plan.json` | Becomes, in the composition |
|---|---|
| `canvas.{width,height,fps}` | The composition's size and frame rate |
| `tracks[video].clips[]` | One video element per clip, playing the source starting at `source_in` for `duration`, placed at timeline `start`. Consecutive clips on the same track |
| `tracks[audio].clips[]` | The matching audio. If the video element carries the source audio, keep audio and video clips in lockstep (same `source_in`, `start`, `duration`) and do not double the sound |
| `tracks[captions].clips[]` | One caption element per entry at `start` for `duration`. `words[]` holds per-word timing (also in timeline seconds) for word-by-word highlight or pop-in animations |
| `zooms[]` | A scale animation on the referenced clip (e.g. 100% → `scale` over a few frames; a hard jump for a punch-in) |
| `transitions[]` | Overlapping clips with an animated transition, or a transition element across the boundary |
| `overlays[]` | Titles, lower thirds, callouts, B-roll: extra elements on higher tracks with their own `start`/`duration` |
| `music` | A music element on its own audio track. `target_lufs` and `duck_db` are for the final audio pass |
| `style_targets` | Not rendered. A reminder of the reference's numbers to check the result against |

## Suggested workflow

1. **Work on a copy.** Keep the original footage untouched; point the composition at the source path or a copy inside the project.
2. **Build the composition from `edit-plan.json`**, track by track: video, audio, captions, then zooms/transitions/overlays you decided on.
3. **Preview with Hyperframes' own tooling** before the full render and compare against the reference storyboard: hook timing, caption legibility, first word time.
4. **Render.**
5. **Verify the result with this skill.** Run `python3 "$ENG/scripts/watch.py" mine <rendered.mp4> --against <reference fingerprint.json> --no-hook` on the render and read the comparison table. It is the quickest honest check that you hit the reference's pacing and loudness.
6. **Final audio pass with ffmpeg if needed**: `ffmpeg -i out.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy final.mp4` (use the target from `music.target_lufs` or the reference).

## If seeking looks wrong

Browsers can be imprecise when seeking in long-GOP files. If frames look off, make a seek-friendly working copy and point the composition at that:

```
ffmpeg -i source.mp4 -c:v libx264 -g 30 -crf 18 -c:a aac -movflags +faststart working.mp4
```

Recompute nothing: the plan's times are in seconds and stay valid as long as the transcode keeps the same timeline (no trimming).

## Editing the plan

`edit-plan.json` is meant to be edited by you before it is turned into a composition. Typical edits: add `transitions` at cuts the reference treats as soft, add `overlays` where the storyboard shows on-screen text, add B-roll slots where the QA flags show dead air or long static shots, set `music.duck_db`, and put short human-readable reasons in `notes`.
