---
name: video-pipeline
description: Edits a talking or product video end to end - studio-clean audio, Hinglish transcript, tight word-safe cut, research-backed HyperFrames graphics, keyword captions, fade-out ending - with one approval before render. The entry point for every edit; start here for "edit this video", "make a reel/short/YouTube video from this footage".
---

# Video pipeline

One project folder, one flow, one approval. `$ROOT` is the video's own folder (e.g. `videos/my-reel`, footage in
`raw/`, optional `references/`). Brand files come from `$ROOT/brand/` or, if absent, the workspace `brand/`.
Originals stay untouched; working files go to `$ROOT/.video-pipeline/` (`$W`); results go to
`$ROOT/Exports/<project>-vN.mp4`.

```bash
ROOT="<project folder>"; W="$ROOT/.video-pipeline"
SK="${VIDEO_SKILLS:-$HOME/.agents/skills}"; ENG="$SK/video-pipeline/engine"
for PY in "$VIDEO_ENGINE_PYTHON" "$HOME/.video-skills/engine/.venv/bin/python3" \
          "$HOME/.config/video-skills/engine/.venv/bin/python3" "$HOME/.video-skills/engine/.venv/Scripts/python.exe"; do
  [ -n "$PY" ] && [ -x "$PY" ] && break; done
P="$ENG/scripts/parallel_pipeline.py"
```

## Rules that keep the output good

- **Nothing is assumed.** Brand rules come only from files the user put in a `brand/` folder. If there are none, the
  look is the default style the user picks (`video-style`). There is no memo or style-guide template; old
  `MEMO.md` / `STYLE-GUIDE.md` files are ignored. Do not invent colours, handles, CTAs, logos or claims.
- **Every on-screen word is sourced:** the speaker's own words (transcript) or a researched fact with a URL.
- **HyperFrames catalog first.** Every graphic, title, lower third, chart, transition or caption treatment is
  searched in the local catalog (`catalog.py search`) before anything custom is built.
- **Audio is cleaned once.** Pass 1 (dereverb + DeepFilterNet) runs in `analyze`; pass 2 (polish + loudness) runs in
  `assemble`. Never add another denoise/dereverb step; to change strength, re-run `analyze` with `--denoise`/`--dereverb`.
- **Transcript is Hinglish in Roman script**, always: Hindi and English as spoken, English letters.
- **Cuts are tight but never inside a word**, and every video ends with a held frame that fades to black.

## 0. Check the environment (first edit of a session)

```bash
bash "${VIDEO_ENGINE_DIR:-$HOME/.video-skills/engine}/test-package-manager.sh" --quick      # ~10 s
```

It verifies the skills, engine, FFmpeg filters, whisper flags, the Hinglish model, DeepFilterNet, HyperFrames and the
catalog index. On FAIL, run it with `--fix` (re-runs setup) and do not start the edit until it says READY. After an
install or update, run it once without `--quick`: it renders a sample edit end to end and checks the result.

## 1. Analyze

```bash
"$PY" "$P" analyze --input "$ROOT/<video or folder>" --project "$ROOT" --prompt "<the user's brief>" \
  [--names "Zerodha, Nifty"] [--reference "$ROOT/references/<file>"]
```

In one run: constant-frame-rate copy (so picture, sound and words never drift), audio pass 1, Hinglish transcript
snapped to the measured speech, the **tight cut, active by default** (retakes, restarts, isolated fillers out; pauses
≤ 0.28 s; every edge in silence), the flat cut `hyperframes/input-video.mp4` with a 1.5 s fade-out tail, the
flat-time transcript, contact sheet, grade preview, references, brand files and `$W/REVIEW.md`. If the folder holds
several videos, ask which one.

## 2. Review the material

Read `$W/REVIEW.md`, look at `preview/source-contact-sheet.jpg` and `preview/grade-preview.jpg`, read `CUT.md`.
- `video-watch` for every reference video/image in `references/` (what to borrow: pacing, layout, type, motion).
- `video-transcribe` to fix misheard names (corrections persist; never retype times).
- `video-style` to pick one default style (or match the references) and set the grade and aspect.
- Tell the user to listen to `preview/audio-before-after.wav`.

## 3. Research

`video-researcher`: research the topic and the speaker's claims on the web, then plan the motion graphics, sounds and
b-roll that make the video clearer. Output: `$W/research/research.json` (facts with URLs → graphics, sounds, b-roll).

## 4. Storyboard

`video-plan-storyboard`: write `$W/storyboard.json` on the cut's timeline — catalog blocks for the researched
graphics and b-roll, caption keywords (`video-captions`), sound cues, reframe if the aspect changes.

## 5. Ask once, then approve

Ask only what is still open, in one message: platform/aspect, style, is the cut OK (anything to keep or drop?),
caption keywords look, music (a file in the project, or none). Record answers in `$W/resolved-spec.json`:

```json
{"user_answers": {"platform_aspect": "9:16 Instagram Reel", "style": "business-explainer", "cut": "tight cut approved",
                  "captions": "keywords", "sound": "palette SFX, no music"},
 "audio": {"preset": "shorts", "tone": "neutral", "music_path": null, "music_db": -20}}
```

Cut changes: `"$PY" "$P" recut --project "$ROOT" --drop 41.2-47.9 --restore 12.0-15.5 [--max-pause 0.35] [--tail 2]`
(source seconds from `transcript.source.json`/`CUT.md`), then re-time beats against `hyperframes/transcript.json`.

Present one review: the cut summary, the style, each beat (time, catalog block, text, source), sounds, music. After the
user approves:

```bash
"$PY" "$P" approve --project "$ROOT" --user-approved --note "<what was approved>"
```

The gate checks the answers, canvas vs footage aspect (reframe needed?), timeline length, every beat/SFX reference
(speech-/visual- ids or `research-NNN` facts with a URL), catalog blocks (file, composition id, variables) and files.

## 6. Assemble and check

```bash
"$PY" "$P" assemble --project "$ROOT"
```

Grade → optional face-aware reframe → stage (captions, catalog blocks, SFX, fade to black) → HyperFrames render →
audio pass 2 (voice polish, effects, music ducked, −14 LUFS / −1 dBTP, fade) → verify → `Exports/<project>-vN.mp4`.
Open `$W/review/<name>-VERIFY.md` and `<name>-render-sheet.png`; watch the export with sound before calling it done.
Any change after approval (storyboard, style, cut, research, spec) needs a new approval.

## Boundaries

- Use only the local engine, FFmpeg, whisper.cpp, DeepFilterNet and the installed HyperFrames CLI/catalog. No `npx`,
  CDN assets or ad-hoc installs during an edit.
- Keep user files untouched; never delete intermediates unless asked.
- You cannot hear audio: report the measured numbers, and ask the user to listen to the before/after and the export.
