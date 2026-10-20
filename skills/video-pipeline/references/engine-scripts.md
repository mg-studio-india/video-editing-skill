# Engine scripts: ownership map

Generated from the skill docs, imports and tests. Scripts used by a single skill live in that skill's `scripts/` folder:
`video-audio` audio-analyze · `video-cut-audit` dead-air, hand-cut, tighten-cut, sliver, cutlist-to-edl + build-edl-review.mjs ·
`video-short-form` make-short · `video-style` palette · `video-transcribe` phrase-times, verify-words · `video-researcher`
research-scaffold · `video-review-gate` review · `video-motion-graphics` snap-beats · `video-sound-design` audiocraft-gen ·
`video-watch` screen-activity, teardown · `video-plan-storyboard` storyboard-md. Everything below stays in
`video-pipeline/engine/scripts/` because several skills or other scripts depend on it (or it is pipeline intake). Tests: one suite in `engine/tests` (`cd "$ENG" && python3 -m unittest discover -s tests -t .`).

**Status:** *shared library* = imported/called by other scripts, not run by skills directly · *multi-skill tool* = run by
two or more skills · *skill tool* = run by one skill but also used by other scripts (so it stays shared) · *pipeline intake* = run by
video-pipeline itself (multi-clip / multi-camera intake).

| Script | Status | Skills that run it | Used by scripts | Tested | Purpose |
|---|---|---|---|---|---|
| `apply-cut.py` | multi-skill tool | cut-audit, pipeline | make-short.py, patch-cut.py, stutter-scan.py, tighten-cut.py | yes | turn cut-list.json into a frame-accurate flat cut (one re-encode, dense keyframes, BT.709 tags). |
| `assemble.py` | multi-skill tool | motion-graphics, plan-storyboard, render | — | — | put finished segments in order and deliver one 4K master. Replaces iMovie. |
| `audio-chain.py` | multi-skill tool | audio, pipeline, render | render.py, spec-resolver.py | yes | voice processing in the right order, with ffmpeg only, measured before and after. |
| `broll-conform.py` | multi-skill tool | format, generate, omni-restyle | generate.py | yes | turn one AI b-roll result (a generated clip, or a still) into a cutaway the composer can use. |
| `parallel_pipeline.py` | multi-skill tool | pipeline, reference-match, cut-audit, plan-storyboard, render | — | yes | High-speed parallel video editing pipeline: parallel ingest, whisper.cpp ASR, dynamic color correction, preset matching, and master render. |
| `install-compositions.mjs` | multi-skill tool | format, pipeline | install.sh | yes | High-speed concurrent installer for all 447 HyperFrames catalog compositions into engine sandbox. |
| `captions.py` | multi-skill tool | captions, pipeline | compose.py, stage.py, treatments.py | yes | word-exact captions from the flat-cut transcript, two ways. |
| `clean-temp.py` | multi-skill tool | captions, pipeline, review-gate | — | — | Safely removes transient scratch files, intermediate audio stems, |
| `compose.py` | multi-skill tool | format, take-geometry | captions.py, snap-beats.py, stage.py, teardown.py … | yes | build public/index.html for a talking-head edit from a storyboard.json, using the proven |
| `generate.py` | multi-skill tool | generate, omni-restyle | — | yes | generated stills and clips, with a cost gate and a ledger. |
| `grade.py` | multi-skill tool | pipeline, plan-storyboard, reference-match, researcher, style | apply-cut.py, match.py, spec-resolver.py | yes | cinematic, high-retention color grading engine for creator videos. |
| `heygen-sound.py` | multi-skill tool | pipeline, sound-design | stage.py | yes | sound effects from local sound-palette and HeyGen's sound library, through HyperFrames' audio engine. |
| `reframe.py` | multi-skill tool | format, short-form, take-geometry | — | yes | crop a 16:9 shot to another aspect around the speaker's face, never a blind centre crop. |
| `render.py` | multi-skill tool | motion-graphics, render, sound-design | review.py, verify-render.py | yes | one command from a checked composition to a deliverable file, with no step skipped. |
| `resolve-anchors.py` | multi-skill tool | take-geometry, transcribe | make-short.py | yes | storyboard.plan.json (phrases) + transcript.json (flat cut) -> storyboard.json (seconds). |
| `stage.py` | multi-skill tool | format, plan-storyboard, take-geometry | captions.py, compose.py, treatments.py | yes | storyboard.json -> public/index.html for ANY canvas (9:16 Shorts and Reels, 1:1, 4:5, or 16:9). |
| `transcribe.py` | multi-skill tool | pipeline, transcribe | fix-words.py, review.py | yes | word-level transcript of a clip with whisper.cpp, in the shape every engine script reads. |
| `verify-render.py` | multi-skill tool | motion-graphics, render | render.py, review.py | yes | unattended checks on the RENDERED file, before it goes to the Renders folder. |
| `watch.py` | multi-skill tool | omni-restyle, pipeline, reference-match, take-geometry, transcribe, watch | measure_blueprint.py | yes | local video analysis for storyboarding references and planning edits. |
| `window-patch.py` | multi-skill tool | motion-graphics, render | — | — | make a render-ready copy of a composed project that covers only [T0, T1] of its timeline, so a |
| `frames.py` | skill tool | take-geometry | jump-frames.py, resolve-anchors.py, shots.py, storyboard.py … | yes | Shot detection (shots.py) already measured every cut. This module only decides |
| `gap-scan.py` | skill tool | pipeline | — | yes | coverage scan of a composition for long-form pacing. |
| `jump-frames.py` | skill tool | take-geometry | resolve-anchors.py | yes | the exact frame where each jump cut happens, measured from the picture. |
| `setup.py` | skill tool | transcribe | transcribe_cpp.py, watch.py | — | Preflight for the watch skill. Never installs anything and never touches the network. |
| `sfx-prep.py` | skill tool | sound-design | audiocraft-gen.py, heygen-sound.py | yes | make a sound effect land on its frame and sit at a known level. |
| `spec-resolver.py` | skill tool | pipeline | — | yes | Context-driven creative dimension extractor and missing-step resolver. |
| `stutter-scan.py` | skill tool | pipeline | patch-cut.py | — | second opinion on the paper cut, using a mechanical mistake finder. |
| `transcribe_cpp.py` | skill tool | transcribe | editplan.py, transcribe.py, watch.py | yes | Word timing recipe: `-ml 1 -sow` makes whisper.cpp emit one entry per word, |
| `treatments.py` | skill tool | format | captions.py, compose.py, stage.py | yes | Each builder takes a beat (resolved times) and a context, and returns (html, css, js_lines, placement): |
| `audio.py` | shared library | — | watch.py | yes | from __future__ import annotations |
| `beat-check.py` | shared library | — | compose.py | yes | transcript-sync gate for our compositions (Gate 0: every card lands on its spoken word). |
| `config.py` | shared library | — | setup.py, transcribe.py, transcribe_cpp.py, watch.py | yes | Everything here is a local path or a tuning number. There are no API keys in |
| `download.py` | shared library | — | watch.py | — | This is the only place the skill touches the network, and only to download the |
| `edge-audit.py` | shared library | — | dead-air.py | — | check every edge of a cut list by the AUDIO, not the transcript, and optionally fix it. |
| `editplan.py` | shared library | — | watch.py | yes | Outputs (all deterministic, all suggestions for Claude and the user to review): |
| `find-cut-candidates.mjs` | shared library | — | stutter-scan.py | — | Adapted from an MIT-licensed open-source HyperFrames starter kit; license and copyright notice: LICENSES/MIT-s |
| `fingerprint.py` | shared library | — | watch.py | yes | The numbers come from analysis.json (measured). The `qualitative` block is a |
| `fix-words.py` | shared library | — | transcribe.py, verify-words.py | yes | correct misheard words in a transcript without touching its timing, and remember the fix. |
| `hinglish.py` | shared library | — | captions.py, compose.py, fix-words.py, transcribe.py … | yes | Ensures that all transcriptions, captions, and on-screen text for Hindi/Hinglish |
| `memo.py` | shared library | — | spec-resolver.py | yes | Brand memory manager (brand/MEMO.md). |
| `pacing.py` | shared library | — | watch.py | yes | capped sample), so the numbers stay honest on fast-cut videos. |
| `paper-cut.py` | shared library | — | hand-cut.py, stutter-scan.py | — | decide what to remove from a raw talking-head recording. |
| `patch-cut.py` | shared library | — | apply-cut.py, dead-air.py | yes | small fixes to an existing cut-list.json without rebuilding it by hand. |
| `probe.py` | shared library | — | build_index.py, caption_probe.py, shots.py, watch.py | yes | from __future__ import annotations |
| `runtime.py` | shared library | — | audio-analyze.py, audio-chain.py, audio.py, captions.py … | yes | Stdlib only. Imported by every other script in this folder. |
| `shots.py` | shared library | — | frames.py, watch.py | yes | Why this is separate from frame extraction: cuts are measured across the |
| `speech.py` | shared library | — | editplan.py, watch.py | yes | All pure functions over plain dicts, so they are easy to unit-test. |
| `storyboard.py` | shared library | — | watch.py | yes | Everything measurable is filled in by code (timecodes, durations, transitions, |
| `ingest.py` | pipeline intake (video-pipeline, before Gate 2) | — | — | — | probe every clip in a raw/ folder, put them in order, and optionally join the talking-head |
| `sync-tracks.py` | pipeline intake (video-pipeline, before Gate 2) | — | — | — | find the time offset between two recordings of the same take (the camera file and the |
