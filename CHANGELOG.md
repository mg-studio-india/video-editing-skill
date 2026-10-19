# Changelog

Every release of video-editing-skill. Update with `video-skills update`.

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
