---
name: video-reference-match
description: Separately analyzes supplied visual references and ranks the bundled style index against the project's source footage. Offers candidates without applying a style automatically.
---

# References and indexed styles

Reference files and the source video are different evidence. Never pass a reference video as another `--video` to the source matcher: the last input can overwrite the source duration, aspect, pacing and people measurements.

Project paths:

```bash
ROOT="<user-selected-video-folder>"
W="$ROOT/.video-pipeline"
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
PY="$ENG/.venv/bin/python3"
RM="${VIDEO_SKILLS:-$HOME/.agents/skills}/video-reference-match"
```

The pipeline scans only `$ROOT/references/` and explicit `--reference` inputs. It analyzes each reference video separately with `watch.py ref`, reads image dimensions, and extracts PDF text into the hidden review packet. Paths and hashes are recorded in `references/reference-index.json`. Inspect actual reference frames and extracted text before writing down layout, pacing, typography or motion observations. Do not treat the reference's product content, words or claims as facts about the user's footage.

With or without user references, rank the source footage against the bundled `references/index.json`:

```bash
"$PY" "$RM/scripts/match.py" --video "$W/raw/standard-input.mp4" \
  --transcript "$W/transcript.json" --top 5 --out "$W/reference-match"
```

The index file is canonical. `matches.json` records whether it was used or whether recovery from individual blueprint files was necessary and why. A missing/invalid index must be visible to the user and must not silently skip reference-free matching.

Offer a few good candidates and a custom direction option only when the user has not already decided. Do not apply a ranked blueprint without that choice. If the user supplied a reference, discuss its measured visual grammar first; blueprints can suggest local HyperFrames assets only when they fit the source and brand. Brand instructions take priority over style samples.

Use the distinctive parts of a selected blueprint only when source evidence supports them. Check `match.needs`, `avoid_when` and linked composition metadata. Do not force its structure, card copy, number of beats, CTA, grade, music, fonts, or palette into the edit. Map its useful visual qualities to actual source moments, cite source-evidence IDs in the storyboard, and omit unsupported devices.

Select and mount only a local HyperFrames composition that serves an approved beat. Verify its HTML path and internal `data-composition-id`. Do not apply every linked item by default, use `npx`, or fetch a replacement during the edit.
