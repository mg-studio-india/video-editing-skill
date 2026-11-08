# Project folder and state

The project boundary is the folder the user selected. Original media, references and brand guidance stay where they are. Generated pipeline files are grouped in one hidden workspace, and final renders are grouped in `Exports/`.

```text
$ROOT/                              user-selected video folder
  <source media>                    untouched user input
  references/                       optional user reference images/videos
  brand/                            optional MEMO.md and STYLE-GUIDE.md
                                    brand text, PDF guides and visual assets are indexed
  .video-pipeline/                  all generated analysis and edit files
    project.json                    project state and gate records
    raw/                            standardized working copy of selected source
    preview/                        timestamped evidence frames and contact sheet
    audio_processing/               cleaned audio, ASR files and reports
    references/                     separate reference analyses and index
    context/brand/                  hidden copies of guides/assets and extracted PDF text
    reference-match/                indexed style candidates
    source-evidence.json             evidence IDs for visual shots and speech ranges
    QUESTIONNAIRE.md                 unanswered creative decisions
    resolved-spec.json               recorded user decisions
    cut-proposal.json                optional transcript cut suggestion
    cut-list.json                    active kept ranges; full source until approval
    storyboard.plan.json             source-anchored creative plan
    storyboard.json                  approved stage-ready edit
    style-template.json              current simple-caption defaults and measured grade
    style.json                       approved brand-aware style values
    hyperframes/                     editable project composition and selected HyperFrames blocks
    scratch/                         disposable render/audio work
    review/                           QA sheets and reports
  Exports/                           versioned final renders only (published after verification)
```

The engine, Python packages, HyperFrames CLI and full composition catalog are installed once in the user's shared engine. FFmpeg is provided by the system, and Whisper's model is stored in the shared user cache. The pipeline copies only the blocks selected for this edit into the project's hidden workspace; HyperFrames requires those files to stay inside its project root.

Do not copy or move the user's original footage into the workspace. `meta.json` records the selected source path and the standardized analysis copy. If the input folder contains multiple supported videos, ask the user which one to edit.

## State and gates

Keep `project.json` compact: source paths, key outputs, current approval gate, and selected direction. The authoritative detailed files remain separate (`resolved-spec.json`, `cut-list.json`, `storyboard.json`, `style.json`).

The cut remains full length until the user approves specific kept ranges. The storyboard is not considered approved until `parallel_pipeline.py approve --user-approved` validates that:

- the user decisions are recorded;
- every authored beat cites valid source evidence IDs;
- every beat has a valid time range;
- kept source ranges are ordered, non-overlapping, and inside the source duration.

Any change to the cut or storyboard after approval clears the approval gate and requires a new review. Assembly must reject a missing or stale gate.
