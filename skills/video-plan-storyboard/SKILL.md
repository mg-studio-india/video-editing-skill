---
name: video-plan-storyboard
description: Writes storyboard.json for an analysed project - HyperFrames catalog blocks first, placed on the cut's timeline from the transcript and the research, plus caption keywords, sound cues, reframe and the fade-out ending. Use after video-pipeline analyze and video-researcher, before approval.
---

# Storyboard (HyperFrames catalog first)

The storyboard is the edit's plan on the **flat timeline** (the active cut, including the end tail). Times come from
`$W/hyperframes/transcript.json` and the `speech-NNN` segments in `$W/source-evidence.json`. Same variables as
`video-pipeline` (`ROOT`, `W`, `ENG`, `PY`).

## 1. Find the moments

Read the flat transcript, `research/research.json` (`motion`, `broll`, `sounds` plans) and the chosen style
(`style.json` → `catalog.prefer_tags`). A graphic earns its place when it makes a spoken point clearer: a number
landing, a name, a list, a comparison, a before/after, a step, a quote, a place. Aim for a visual change every few
seconds in short-form, without covering the speaker's face on every line.

## 2. Pick from the HyperFrames catalog

```bash
"$PY" "$ENG/scripts/catalog.py" search <words>            # e.g. chart, counter, headline, lower third, map, logo
"$PY" "$ENG/scripts/catalog.py" search --tag <tag>        # tags from the style's prefer_tags
"$PY" "$ENG/scripts/catalog.py" show <name>               # file, comp_id, variables, and a ready beat snippet
```

Use a catalog block for every graphic, title, b-roll card and transition it covers; open the HTML to check what it
draws and which variables it takes. Only when nothing fits, use a built-in treatment (`hero`, `banner`, `cards`,
`drawer`, `split`, `whiteout`, `clip`) and say why in the beat's `why`.

## 3. Write `$W/storyboard.json`

`analyze` wrote a scaffold (canvas, fps, duration, video, captions, end). Fill it in:

```json
{
  "id": "my-reel", "canvas": [1080, 1920], "fps": 30, "duration": 58.34, "video": "input-video.mp4",
  "reframe": {"aspect": "9:16", "mode": "static"},
  "captions": {"source": "transcript.json", "keywords": ["crore", "IPO", "profit"]},
  "end": {"fade": 1.0},
  "beats": [
    {"id": "b1", "type": "block", "src": "<catalog src>", "comp_id": "<catalog comp_id>",
     "vars": {"title": "₹2,000 crore IPO"}, "in": 4.20, "out": 7.10,
     "refs": ["speech-002", "research-001"], "why": "the number he says, sourced"}
  ],
  "sfx": [{"id": "s1", "src": "ping-metric.mp3", "at": 4.25, "dur": 0.8, "volume": 0.3, "refs": ["speech-002"]}]
}
```

- `refs` on every beat and SFX: `speech-NNN` / `visual-NNN` from `source-evidence.json`, or `research-NNN` facts
  (with a source URL). On-screen text = the speaker's words or the fact's `on_screen` text, nothing else.
- `in`/`out`/`at` are flat-timeline seconds inside `0 … duration`. Start a graphic on the word it illustrates.
- `reframe` only when the canvas aspect differs from the footage: `static`/`follow` = face-aware crop,
  `center` = plain centre crop. `resolution: "4k"` renders UHD.
- SFX come from the sound palette (`sound-palette/audio/*.mp3`), a project file, or `research/sounds/`. One cue per
  graphic at most; nothing on top of every caption; volume 0.2-0.4.
- Omit `camera` for the default slow push/pull; `"camera": []` keeps the frame still.
- Leave `captions.keywords` short: the words that carry the point (see `video-captions`).

After a `recut`, beat times are stale: re-time them against the new `hyperframes/transcript.json`.

## 4. Review

Present the storyboard as a short table (time · what appears · catalog block · text · source) with the cut summary,
style and sounds. Approval and assembly are `video-pipeline` steps 5-6.
