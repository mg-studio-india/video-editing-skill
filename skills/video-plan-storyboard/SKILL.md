---
name: video-plan-storyboard
description: Builds a footage-led storyboard from inspected source evidence, project references and brand rules. Owns the creative review before assembly.
---

# Footage-led storyboard

The source determines the story. Do not start from a genre template, fixed beat count, or familiar advertising structure.

## Read the project evidence first

The main pipeline stores working files under `$ROOT/.video-pipeline/` so the user's source folder stays organized. Read:

- `source-evidence.json` and inspect the timestamped images in `preview/source-contact-sheet.jpg`.
- `transcript.json` and listen to the source around any line used as a quote, claim, or beat anchor.
- `references/reference-index.json`; inspect every supplied image and each video reference's separate `storyboard.md` and frames.
- `context/brand-inputs.json` and every listed brand memo/style guide before selecting fonts, colors, logos, claims, or graphic tone.
- `cut-proposal.json`, which is a suggestion only. `cut-list.json` remains full length until the user approves exact removals.

Never merge reference footage into source evidence. A reference demonstrates visual direction; it does not prove what happens in the user's footage or validate a product claim. Brand requirements constrain the reference style.

## Find the story in the material

Inspect the source contact sheet and focused frames around relevant speech or visual changes. Name what is actually visible or spoken. Scene detection only reports likely visual transitions; it does not identify objects, actions, intent, or product features.

Every proposed beat must cite one or more `source_refs` IDs from `source-evidence.json` and state the evidence that supports its content. Use real source ranges or verified transcript phrases. If the footage does not support a beat, leave it out. A storyboard may contain no graphic beats when the footage works best on its own.

Do not impose a hook, a set number of points, a verdict, or a call to action. Do not invent cards, metrics, logos, product features, quotes, sound cues, or b-roll. Do not split a product video into equal time quarters and label those quarters as product events. When dialogue is absent, preserve and shape the actual visual sequence; lack of speech is not a reason to remove footage.

## Ask for the missing decisions together

Read `QUESTIONNAIRE.md`. Ask only unanswered questions, in one compact interaction. Cover:

- what must stay and what may be cut;
- intended platform/aspect ratio, with source framing as the default;
- whether supplied references, an indexed style candidate, or an original footage-led direction should guide the look;
- framing that fits the actual shots;
- captions: retain the current simple phrase treatment, choose another, or disable;
- audio: denoise level, original sound only or user-supplied/licensed music/SFX. Dereverb remains strong as requested.

Do not ask again when the brief or saved brand guide already answers it. Record the user's decisions in `resolved-spec.json` under `user_answers` with these keys: `keep_cut`, `platform_aspect`, `direction`, `framing`, `captions`, and `sound`. If the brief specifies a decision, record it; if the user delegates it, record the delegation and chosen option. Do not apply an indexed style match without the user's choice. If there is no reference, use `reference-match/matches.json` to offer a few relevant choices; the user may delegate the choice.

## Make a source-specific storyboard

Write the approved creative plan to `storyboard.plan.json`, and the stage-ready version to `storyboard.json`. The stage-ready JSON uses the existing `stage.py` schema. Include:

- `id`, `duration`, `canvas`, `video`, and optional `captions`;
- `source_evidence_sha256`, copied from the current `storyboard.plan.json`;
- `beats`, which may be empty;
- for every authored beat: `id`, `type`, numeric `in` and `out`, `source_refs`, and only the content needed by that treatment;
- for a HyperFrames block: the local `src`, the exact internal `comp_id` declared by that file, `source_refs`, and validated variable values if the composition declares variables;
- `sfx` only when sound design was requested and each cue has a justified, approved time.
- An omitted `camera` field receives the pipeline's restrained centered push/pull (up to 1.022×); include authored camera operations or `"camera": []` when the footage calls for a different move or a static frame.

Keep the simple phrase caption treatment for a simple edit: bold Google Sans, about 60–80 px at a 1080-wide canvas, a subtle padded backing, and no shadows. A user-selected caption look or brand guide may override these defaults. Do not add a graphic merely to fill empty space. Use an existing HyperFrames composition or component only when its motion and visual purpose fit a real source moment. Mount only selected local catalog assets; never fetch an unpinned package or add an unrelated framework.

Every graphic word must be traceable to verified speech, a user-supplied asset, or the brand guide. Mark uncertain transcript words for review instead of turning them into claims. Respect logo clear space, required colors, type, and exclusions from the brand materials.

## Review and approval gate

Create `style.json` from `style-template.json`, the brand rules, and the resolved user direction. Record the chosen denoise level, audio preset, and optional project-local music path under `resolved-spec.json` → `audio`. Keep all review artifacts under the hidden workspace. Present one concise review containing the actual source contact sheet, relevant reference frames, brand constraints, proposed cut ranges, selected story beats, framing/aspect, caption treatment, and sound plan.

Do not assemble until the user approves. After approval, run:

```bash
"$PY" "$ENG/scripts/parallel_pipeline.py" approve --project "$ROOT" --user-approved --note "<approval summary>"
```

The approval command checks that every beat cites valid evidence IDs, beat times are in range, and kept cut ranges are valid. Then the main pipeline may assemble and render. If the user changes the plan, update the files and seek approval for the revised version.

The export goes to `$ROOT/Exports/`. Intermediate transcripts, contact sheets, reference analyses, audio files, HyperFrames files, and verification artifacts stay in `$ROOT/.video-pipeline/`.
