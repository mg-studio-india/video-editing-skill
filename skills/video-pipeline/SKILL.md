---
name: video-pipeline
description: Runs a project-scoped, source-grounded video editing pipeline with reference and brand review, explicit user direction, HyperFrames assembly, and organized exports.
---

# Video pipeline

The user-selected folder is the project boundary. Keep original inputs and guides in place, put all pipeline working files in its hidden `.video-pipeline/` directory, and write only final exports to `Exports/`.

```bash
ROOT="<user-selected-video-folder>"
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
ENGINE_ROOT="${VIDEO_ENGINE_DIR:-$HOME/.video-skills/engine}"
[ -d "$ENGINE_ROOT" ] || ENGINE_ROOT="$HOME/.config/video-skills/engine"
PY="${VIDEO_ENGINE_PYTHON:-}"
if [ -z "$PY" ]; then
  for candidate in "$ENGINE_ROOT/.venv/bin/python3" "$ENGINE_ROOT/.venv/bin/python" "$ENGINE_ROOT/.venv/Scripts/python.exe"; do
    if [ -x "$candidate" ]; then PY="$candidate"; break; fi
  done
fi
```

## 1. Analyze inside the selected project

Before running, confirm the configured engine environment has `Pillow`, `opencv-python-headless`, `pypdf`, and `pypdfium2` from `engine/requirements.txt`. Use the project `.venv`/engine interpreter; do not install into system Python.

Run analysis with the user's selected folder. If it contains one supported video, `--input` may be that folder; if it contains more than one source video, ask which clip(s) to edit rather than picking one silently. Project references are read only from `$ROOT/references/` or explicit `--reference` paths; video, image and PDF references are supported. Brand text, PDF guides and visual assets are read from `$ROOT/brand/` plus recognized root-level brand-guide files.

```bash
"$PY" "$ENG/scripts/parallel_pipeline.py" analyze \
  --input "$ROOT/<source-video-or-folder>" \
  --project "$ROOT" \
  --prompt "<the user's creative brief>" \
  [--reference "$ROOT/references/<reference-file>"]
```

Repeat `--reference` for multiple explicit references. The analyzer also finds supported media in the project's `references/` folder. It analyzes reference videos separately from the source, reads image references, extracts searchable text from PDF references and brand guides into the hidden review packet, snapshots brand assets, and uses the bundled `video-reference-match/references/index.json` when ranking styles. A missing or malformed index is reported and can recover from the bundled blueprint files; never silently skip the index.

Analysis creates timestamped source frames/contact sheets, shot ranges, transcript evidence, a non-active cut proposal, a simple caption template, and a review questionnaire in `.video-pipeline/`. Shot detection marks visual changes; it does not interpret events. No story beats, product claims, split layouts, CTA cards, or sound effects are generated automatically. The active cut preserves the entire source timeline.

## 2. Read source, references and brand rules

Apply `video-plan-storyboard` to inspect `source-evidence.json`, the actual source contact sheet and relevant focused frames, the transcript, every supplied reference, and every listed brand input. Keep source facts, reference style observations, and brand requirements distinct.

The selected creative direction must explain what the footage itself supports. Each proposed beat needs valid source evidence IDs. Use only verified transcript wording for on-screen claims. If a graphic does not clarify an actual source moment, omit it. Product and silent footage remain intact unless the user approves specific removals.

No-reference projects still use the style index to offer a few relevant choices. A match is a suggestion, not automatic direction. A supplied reference is analyzed independently and leads only after the user chooses it; brand requirements still apply.

Ask one compact batch of only the unanswered questions from `QUESTIONNAIRE.md`: footage to keep/cut, platform/aspect, reference or original direction, framing for the actual shots, caption choice, and audio denoise/music/SFX. Default simple phrase captions use bold Google Sans at roughly 60–80 px on a 1080-wide canvas, with a subtle padded backing and no shadows. Apply the supplied brand guide or selected caption treatment when it calls for a different look. Strong dereverb is already selected. Save answers in `resolved-spec.json` → `user_answers` using keys `keep_cut`, `platform_aspect`, `direction`, `framing`, `captions`, and `sound`; carry the answers into `storyboard.plan.json`, `storyboard.json`, and `style.json`. Record concrete audio choices in `resolved-spec.json` → `audio`. Copy the current evidence file's SHA-256 into `storyboard.json` as `source_evidence_sha256`.

## 3. Present and approve the plan

Before assembly, show a concise review of the source evidence, relevant reference frames, brand constraints, selected footage and cuts, framing/aspect, captions, and requested sound. Keep the working documents and analysis files in the hidden folder so the project root stays uncluttered.

Do not assemble or render until the user approves. After explicit approval, record the gate:

```bash
"$PY" "$ENG/scripts/parallel_pipeline.py" approve \
  --project "$ROOT" --user-approved --note "<approval summary>"
```

The gate rejects missing direction answers, unsupported beat references, out-of-range beat times, and invalid kept ranges. Use an empty `beats` array when no extra graphic treatment is appropriate.

## 4. Assemble and render

```bash
"$PY" "$ENG/scripts/parallel_pipeline.py" assemble \
  --project "$ROOT" --dereverb strong
```

The assembly uses the approved cut, transcribes the conformed edit for caption sync, validates every selected HyperFrames block against the shared catalog and its internal composition ID, then stages only the selected blocks inside the project. HyperFrames requires bundled assets to remain inside its project root, so the shared catalog itself stays in the engine while the small set used by this edit is copied into `.video-pipeline/hyperframes/compositions`. Missing local HyperFrames/GSAP assets fail with a setup error; the pipeline must not fall back to `npx`, CDN assets, Swift Package Manager, or another unrequested framework.

The render applies strong late-reflection reduction and the selected denoising/master chain. Dereverberation can reduce room tails but cannot guarantee removal of every echo; the generated audio report records the processing result. Do not claim full echo cancellation.

When `storyboard.json` omits `camera`, HyperFrames adds a centered, gentle push/pull between 1.000× and 1.022×. An authored camera plan takes precedence; use `"camera": []` to keep the frame still. No subject tracking or inferred focal points are added.

Each successful render is published as the next `$ROOT/Exports/<project>-vN.mp4`; the final file is moved there only after render verification completes. Transcripts, audio, review sheets, HyperFrames sources, and render intermediates stay under `$ROOT/.video-pipeline/`.

## Execution boundaries

- Keep work within this video-editing pipeline and the selected project folder.
- Reuse the user's shared engine, FFmpeg on `PATH`, Whisper binary/model cache, and HyperFrames catalog across projects. Never install or copy those shared tools into each video folder. Keep analysis and project-specific render assets in that project's `.video-pipeline/`; keep originals in place and final videos in `Exports/`.
- Python invokes FFmpeg, ffprobe, Whisper, HyperFrames, and pipeline stages with argument arrays through `subprocess`; this keeps media tools composable and file paths safe. Use shell only to launch the pipeline commands shown above.
- Use local, configured pipeline dependencies. Do not improvise package managers, frameworks, or network installs during an edit.
- Keep user inputs untouched. Do not delete intermediates without an explicit cleanup request.
- Do not run assembly when the recorded approval gate is missing or stale.
