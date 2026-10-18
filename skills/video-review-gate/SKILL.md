---
name: video-review-gate
description: Final quality gate on the rendered deliverable - checks structure, speech alignment, loudness, and frame sheets. Verifies CLI check report and renders, keeping composition fully editable via CLI tools, and automatically purges transient temp files. Owns Gate 6.
---

# Review Gate & Delivery (Final Quality Assurance)

Inspects the final deliverable from the viewer's perspective. Guarantees visual polish, acoustic fidelity, CLI composability, and complete temp file cleanup.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
F="$W/processed/<project>-v<N>.mp4"
```

---

> [!IMPORTANT]
> **Virtual Environment (STRICT)**: ALWAYS execute scripts using the project's virtual environment (`"$PROJECT/.venv/bin/python3"`). Never invoke system python.

Run verification on the rendered MP4 file:
```bash
"$PROJECT/.venv/bin/python3" "$ENG/scripts/review.py" --final "$F" --preset shorts --res 1080x1920 \
  --storyboard "$W/storyboard.json" --transcript "$W/transcript.json"
```

Must verify:
1. **Structure & Resolution:** Exact 1080x1920 vertical canvas, 12+ Mb/s bitrate, BT.709 color tags.
2. **Audio Loudness:** `-14.0 LUFS` integrated, `<= -1.0 dBTP` true peak.
3. **No Black Frames or Glitches:** 0 frame dropouts, 0 flash artifacts.
4. **Platform Safe Zones:** Text clear of bottom 320px and top 180px.

---

## 2. CLI Composition Inspection & Interactive Preview

Validate the HyperFrames composition using CLI tools without requiring the desktop GUI app:
```bash
npx hyperframes check "$W/hyperframes"
```
Optional interactive preview via local browser server (on user request):
```bash
npx hyperframes preview "$W/hyperframes"
```
Keeps the project 100% editable, composable, and verifiable via command line.

---

## 3. Automated Lifecycle Cleanup & Report Purge

Once verification and review are completed successfully and approved, purge all intermediate scratch files and temporary review reports:
```bash
"$PROJECT/.venv/bin/python3" "$ENG/scripts/clean-temp.py" "$W" --clean-reports
```
Purges intermediate WAVs, un-mastered raw renders, auto-editor dumps, verification reports (`*-VERIFY.md`), acoustic audits (`*-audio.json`), review summaries (`*-REVIEW.md`), and review contact sheets (`*-review-sheet.png`), leaving strictly the clean final deliverable (`processed/<project>-v<N>.mp4`) and the editable `hyperframes/` project files.
