# Changelog

Every release of video-editing-skill. Update with `video-skills update`.

## [2.0.1] - 2026-11-16

- Installer: show live progress during step 5 (HyperFrames package install, Chrome check, skills suite update, composition downloads, and catalog indexing)
- video-skills: auto-purge retired 1.x skills from state and agent directories during update and doctor
- Environment check: fix importlib.util import and false-positive on FFmpeg -fps_mode
- macOS: recognize ffmpeg-full formula (supports zscale, tonemap and drawtext)

Skills changed: video-pipeline 2.0.0 -> 2.0.1

## [2.0.0] - 2026-11-16

- Simpler: 19 skills -> 9 (pipeline, watch, style, audio, transcribe, captions, researcher, plan-storyboard, generate); one approval gate; retired skills are removed on update
- Audio: two passes, each run once - WPE + DeepFilterNet (strength from measured noise, delay-compensated, alignment-checked) before transcription; voice-only polish + one master at render. No more triple dereverb / double denoise on the full mix (robotic, echoey voice)
- Sound effects and music are mixed after the voice is processed; one AAC encode; before/after preview at review
- Hinglish transcripts: Hinglish Whisper model by default (Roman script); stock models decode Hindi instead of being forced to English (which translated); no injected topic prompt; DTW word timing; words snapped to speech energy; silent hallucinations dropped
- Sync: constant-frame-rate ingest, source audio aligned to the first frame, transcript mapped through the exact cut map (no second transcription), A/V checks within one frame
- Cuts: tight by default and active at analysis; every edge placed in measured silence and snapped outward to frames, so words are never clipped; recut command for drops/restores
- Every video ends with a held frame and a fade to black (picture and audio)
- HyperFrames catalog first: install-time catalog index + catalog.py search/show; catalog blocks validated at approval
- Research feeds the edit: research.json facts with sources drive graphics, sounds and b-roll; beats may cite research-NNN
- Captions: Inter SemiBold, sentence case, white; only keywords highlight with a kinetic pop
- Four default styles; brand rules only from the user's own files; brand/MEMO.md and STYLE-GUIDE.md templates removed and ignored
- Installer: requirements installed from the package (not the workspace); workspace cleanup is opt-in and no longer touches .claude/AGENTS.md/.vscode; engine unit tests removed
- video-skills: a release that drops skills now retires their links (edited ones backed up first), cleans dangling agent-folder links and forgets them in its state, so the 10 merged 1.x skills stop loading and doctor stays clean; rollback restores them
- tools/test-package-manager.sh: (A) the sandboxed package-manager test (release, install, update/conflict, force, rollback, partial update, migration, prune, doctor, uninstall) now also covers a release that drops a skill; (B) environment verification before editing - skills, engine, FFmpeg filters, whisper DTW flags, Hinglish model, DeepFilterNet, HyperFrames + catalog index - with --fix to run the setup; (C) a full sample edit checked end to end. Installed as $VIDEO_ENGINE_DIR/test-package-manager.sh (B + C) and run with --quick at the end of setup

Skills changed: video-audio 1.1.1 -> 2.0.0, video-captions 1.1.1 -> 2.0.0, video-generate 1.1.1 -> 2.0.0, video-pipeline 1.1.1 -> 2.0.0, video-plan-storyboard 1.1.1 -> 2.0.0, video-researcher 1.1.1 -> 2.0.0, video-style 1.1.1 -> 2.0.0, video-transcribe 1.1.1 -> 2.0.0, video-watch 1.1.1 -> 2.0.0

Skills removed: video-cut-audit, video-format, video-motion-graphics, video-omni-restyle, video-reference-match, video-render, video-review-gate, video-short-form, video-sound-design, video-take-geometry

## [1.1.1] - 2026-11-08

- Fix audio processing and HyperFrames assembly
- Add pipeline synthesis and evidence collection
- Bundle Google Sans typography assets
- Streamline skill definitions and reference documentation

Skills changed: video-audio 1.1.0 -> 1.1.1, video-captions 1.1.0 -> 1.1.1, video-format 1.1.0 -> 1.1.1, video-generate 1.0.0 -> 1.1.1, video-motion-graphics 1.1.0 -> 1.1.1, video-pipeline 1.1.0 -> 1.1.1, video-plan-storyboard 1.1.0 -> 1.1.1, video-reference-match 1.1.0 -> 1.1.1, video-render 1.0.0 -> 1.1.1, video-researcher 1.1.0 -> 1.1.1, video-review-gate 1.1.0 -> 1.1.1, video-sound-design 1.1.0 -> 1.1.1, video-style 1.1.0 -> 1.1.1, video-take-geometry 1.1.0 -> 1.1.1, video-transcribe 1.1.0 -> 1.1.1, video-watch 1.1.0 -> 1.1.1

## [1.1.0] - 2026-10-20

- User references take precedence over style blueprints
- Bottom split-screen speaker layout (70%) with head-area focus crop
- Studio mesh illuminated gradient background for graphic card canvas
- HyperFrames composition library integration and installer indexing
- Minified runtime engine scripts

Skills changed: video-audio 1.0.3 -> 1.1.0, video-captions 1.0.0 -> 1.1.0, video-cut-audit 1.0.0 -> 1.1.0, video-format 1.0.0 -> 1.1.0, video-motion-graphics 1.0.0 -> 1.1.0, video-pipeline 1.0.3 -> 1.1.0, video-plan-storyboard 1.0.0 -> 1.1.0, video-reference-match 1.0.2 -> 1.1.0, video-researcher 1.0.0 -> 1.1.0, video-review-gate 1.0.0 -> 1.1.0, video-short-form 1.0.0 -> 1.1.0, video-sound-design 1.0.0 -> 1.1.0, video-style 1.0.0 -> 1.1.0, video-take-geometry 1.0.0 -> 1.1.0, video-transcribe 1.0.0 -> 1.1.0, video-watch 1.0.2 -> 1.1.0

## [1.0.5] - 2026-10-19

- Default creative workspace to current working directory unconditionally
- Uninstall removes .engine sandbox and cleans broken agent links

## [1.0.4] - 2026-10-19

- Windows: install.sh accepts C:/... paths from video-skills, so the workspace and skills folder are created in the right place
- CI runs on pull requests only and is verified on Windows, Ubuntu and macOS

## [1.0.3] - 2026-10-19

- README: install with the one-line installer; new Staying Up to Date section; system requirements match the installer
- Installer and skills point to 'video-skills setup' for re-running setup

Skills changed: video-audio 1.0.1 -> 1.0.3, video-pipeline 1.0.2 -> 1.0.3

## [1.0.2] - 2026-10-19

- Fix: skills no longer break when an agent folder links to ~/.agents/skills; video-skills update repairs them
- Every skill is verified after install; video-skills doctor checks each skill and agent folder
- Windows: FFmpeg filter paths fixed (RNNoise cleaning, reframing, teardown); verified in CI on Windows, Ubuntu, macOS
- README rewritten for creators

Skills changed: video-pipeline 1.0.1 -> 1.0.2, video-reference-match 1.0.0 -> 1.0.2, video-watch 1.0.0 -> 1.0.2

## [1.0.1] - 2026-10-19

- Linux: private Node.js 22 and prebuilt whisper.cpp installed automatically (no sudo); clear install hints per distro
- Windows: get.ps1 checks prerequisites with winget hints and uses Git Bash; .cmd launcher; Windows-safe paths and DeepFilterNet
- API keys in .env are always quoted safely; non-key input is refused
- New: video-skills setup re-runs the engine setup after a fix
- Fix: reframe.py crashed (missing import); HeyGen sign-in check no longer reports a false yes

Skills changed: video-audio 1.0.0 -> 1.0.1, video-pipeline 1.0.0 -> 1.0.1

## [1.0.0] - 2026-10-19

- One-line install (get.sh / get.ps1) and the video-skills package manager: check, update, per-skill update, rollback, conflict-safe edits
- 19 skills, including video-reference-match: 50 measured, anonymous style blueprints with a gated reference match at every project start
- 225-style catalog split into the skills that build each style
- Echo and noise cleanup (WPE dereverb + DeepFilterNet) in video-audio; single-skill scripts moved into their skills; one merged engine test suite

Skills changed: video-audio (new), video-captions (new), video-cut-audit (new), video-format (new), video-generate (new), video-motion-graphics (new), video-omni-restyle (new), video-pipeline (new), video-plan-storyboard (new), video-reference-match (new), video-render (new), video-researcher (new), video-review-gate (new), video-short-form (new), video-sound-design (new), video-style (new), video-take-geometry (new), video-transcribe (new), video-watch (new)
