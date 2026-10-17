# The project file and the working folder

## Folder layout

One folder per video, `videos/<project-id>/` (or `<project-id>/`, called `$W`). Every skill writes only inside it.

```
$W/
  project.json            the state of the edit (below)
  style.json, STYLE-GUIDE.md   the look (style skill); every builder reads style.json
  raw/                    MANDATORY: contains all user raw clips, footage, screen recordings, and mic audio.
                          All editing skills MUST strictly adhere to this folder for raw data.
  processed/              MANDATORY: version-controlled final renders:
                          <project-id>-v1.mp4, <project-id>-v2.mp4.
                          (Temporary verification and review reports *-VERIFY.md, *-audio.json,
                          *-REVIEW.md, and *-review-sheet.png are generated during Gate 5 review
                          and automatically purged upon successful review approval).
  hyperframes/            MANDATORY: HyperFrames composition files, fully editable via CLI tools:
                          index.html, compositions/ (catalog blocks, captions), sfx/, img/, fonts/, vendor/,
                          and input-video.mp4 (conformed flat cut)
  watch/                  watch output for this project (sheets, fingerprint.json, storyboard.md)
  transcript-raw.json     words on the raw timeline (cut-audit reads it)
  plan.md                 the plan the user approves at gate 1
  storyboard.plan.json    the beats, anchored to phrases (the source: edit this one)
  storyboard.json         the same beats resolved to flat-cut times (regenerated after every cut; never hand-edit)
  cut-list.json           what is kept, on the raw timeline
  PAPER-CUT.md            the cut as text, for gate 2
  cut-map.json            every jump cut in the flat cut
  jump-frames.json        the measured frame of each jump cut (camera resets land on it)
  transcript.json         words on the flat-cut timeline (everything after the cut reads this)
  audio.wav               16 kHz mono of the flat cut
  broll/raw/  broll/      generated and stock clips, before and after conforming
  shorts/<n>/             one folder per Short, the same layout inside (short.json: its ranges and text)
  snaps/                  snapshot sheets
  music/                  the music bed; sound-ledger.json lists every sound and its source
```

## project.json

```json
{
  "project": "ai-tools-review",
  "created": "2026-10-15",
  "program": "long-form",
  "treatments": ["layered-head", "card-list", "b-roll"],
  "aspects": ["16:9"],
  "audio_preset": "youtube",
  "omni_restyle": false,
  "style": "default",
  "sources": [{"file": "raw/C0001.MP4", "role": "face"}, {"file": "raw/screen.mov", "role": "screen"}],
  "steps": {
    "watch":        {"status": "done", "at": "2026-10-15T10:02", "outputs": ["watch/fingerprint.json"]},
    "audio_clean":  {"status": "done", "outputs": ["raw/C0001-clean.mp4"], "notes": "denoise=medium, SNR 18->25 dB"},
    "transcribe":   {"status": "done", "outputs": ["transcript-raw.json"]},
    "plan":         {"status": "waiting", "outputs": ["plan.md", "storyboard.json"]},
    "cut":          {"status": "todo"}
  },
  "gates": {"plan": null, "cut": null, "cost": [], "final": null},
  "tool_fallbacks": [{"step": "generate", "used": "openrouter", "why": "Veo refused a scene with a screen"}],
  "versions": [{"v": 1, "file": "processed/ai-tools-review-v1.mp4", "notes_received": 3}],
  "geometry": {"framings": [{"shots": "all", "face_x": [760, 1160], "safe": "cards right of x 1220", "origin": "52% 0%"}],
               "reframes": [{"file": "shorts/01/reframe-9x16.json", "aspect": "9:16", "mode": "static", "face_rate": 0.96}]},
  "shorts": [{"dir": "shorts/01", "ranges": ["@the real reason..@nobody tells you"], "seconds": 48.6, "status": "todo"}],
  "open_notes": [{"at": "0:22", "note": "text too small", "owner": "format"}]
}
```

- `program`: `hook`, `long-form`, `vlog` or `short`. It sets pacing and structure.
- `treatments`: any of `split-screen`, `paper-drawer`, `whiteout`, `caption-edit`, `layered-head`, `b-roll`,
  `card-list`. One video can use several.
- `status`: `todo`, `running`, `waiting` (at a gate), `done`, or `stale` (an earlier step changed after this ran).
- `gates`: `null` until the user answers, then `{"answer": "approved", "at": "..."}` or their note. `cost` is a list,
  one entry per paid run, with the amount quoted.

## What goes stale when

A step's outputs feed every step after it. When a step re-runs, mark the steps that read its outputs `stale`:

| Re-run | Marks stale |
|---|---|
| audio clean | transcribe and everything after |
| cut | the flat-cut transcript, jump frames, the resolved storyboard, reframes, Shorts, captions, motion-graphics, render, master, review |
| plan | format, motion-graphics, captions, sound-design, render onward (not the cut) |
| style | format, motion-graphics, captions (catalog captions are re-injected), render onward |
| any visual step | render, master, review |
| sound-design | render, master, review |

Re-run only what is stale.
