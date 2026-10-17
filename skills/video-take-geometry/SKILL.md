---
name: video-take-geometry
description: Framing decisions - face-safe zones, zooms and punch-ins, camera resets at jump cuts, subject matte for text behind the head, face-tracked reframing to 9:16, 1:1, 4:5 or split-screen halves. Use after every cut and when the user says "zoom in", "make it vertical", "reframe", "text behind me", "split screen", or a card covers their face.
---
# take-geometry

Measures where the speaker is, once per shot, and turns it into rules: where cards may go, how the camera moves, how to
crop for other aspects without losing the face.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"; S="$ENG/scripts"; W="videos/<project>"
```

## 1. Framing per shot

Shot changes: `ffmpeg -v error -i "$W/hyperframes/input-video.mp4" -vf "select='gt(scene,0.12)',metadata=print:file=-" -f null -`.
For each framing (watch sheets or `watch.py focus`) record in `project.json` → `geometry.framings`: face x and y range,
fixed objects (mic, lamp), card safe zone, camera origin. Known 16:9 framings:
- Sitting left: cards right of x 1000; origin `38% 0%`.
- Centred at a desk with a mic (mic head ~x 500-800, y 330-500): cards left of x 660; top-left clears the mic (an 840 px
  card at left 62 reached x 902 and covered the face); origin `52% 0%`.
- Tight, mic bottom-right: face x 750-1150. Cards top-right (left 1220, 640 px wide) or top-left (left 62, top 80, under
  ~720 px, above y 220); nothing bottom-left.

A card never covers the face: copy that does not fit becomes a lower line, not a smaller card. If the frame already says
it (a number held to the lens), do not add an overlay.

## 2. Camera

Top-anchored origin, always (`52% 0%` centred, `38% 0%` sitting left; vertical: on the face, e.g. `50% 30%`): a
centre-anchored zoom crops the head. Ops go in the plan's `"camera"` with phrase anchors.

| Move | Numbers |
|---|---|
| Punch-in on emphasis | 118-125%, 0.30-0.35 s, `power2.out` (style `camera.punch` overrides; business reels 106-112%) |
| Slow creep across a thought | 110-112% over 5-10 s, `power1.inOut`; release on the next cut |
| Zoom-out reveal | 110 → 100% over 0.5 s as a card enters |
| Every shot change | back to 100%; never carry a zoom across a cut |
| Budget | 3-5 moves per 40 s hook; long-form ~7 per 90 s |
| Limits | 1080p source 112% max; 4K 150% freely, 200% for a deliberate crash-in |

- Two moves in a row on one subject read as a glitch: one move, one symmetric ease.
- At 112% with a 52% origin a left-anchored element drags ~105 px left: compensate.
- Jump cuts stay naked unless the energy changes (pivot, joke, section start): fast punch (104 → 100% over 0.12 s),
  zoom-through, or micro whip; one or two per 40 s hook, at most one per 10 s long-form, never mid-word. On long
  camera-only stretches alternate 100% / 109% between jump cuts.

## 3. Resets on the exact jump frame

`cut-map.json` times are not frame-aligned (a reset at the listed time can show a one-frame double cut). Measure, then
let the resolver add the resets:
```bash
python3 "$S/jump-frames.py" --video "$W/hyperframes/input-video.mp4" --cut-map "$W/cut-map.json" --out "$W/jump-frames.json"
python3 "$S/resolve-anchors.py" --plan "$W/storyboard.plan.json" --transcript "$W/transcript.json" \
  --out "$W/storyboard.json" --jump-frames "$W/jump-frames.json"
```
`weak` cuts (same framing both sides): look at the frames before trusting.

## 4. Text behind the speaker (layered-head)

`npx hyperframes remove-background "$W/hyperframes/input-video.mp4" -o "$W/hyperframes/subject-matte.webm" --quality best`
(for one moment, matte a short `ffmpeg -ss -t` excerpt). Layer order inside the camera: footage → text → matte. Check
hair edges, crossing hands and soft 1080p edges in a snapshot; a poor matte means text beside the head, not behind.

## 5. Other aspects (Shorts, feed, split-screen)

```bash
python3 "$S/reframe.py" --video <flat or Short file> --aspect 9:16 --cut-map <its cut-map.json> \
  --out <dir>/reframe-9x16.json --render <dir>/hyperframes/input-9x16.mp4
```

| Need | `--aspect` | Output |
|---|---|---|
| Short / Reel / TikTok | `9:16` | 1080x1920 |
| Square / portrait feed | `1:1` / `4:5` | 1920x1920 / 1536x1920 (or `--size`) |
| Split half, side by side (16:9) / stacked (9:16) | `8:9` / `9:8` | 960x1080 / 1080x960 |

`static` (default): one crop per shot on the median face, for talking. `--mode follow`: dead zone + smoothing, never
gliding across a cut (kept a face crossing at ~275 px/s inside the crop). `--subject left|right` for two people;
`--zoom 1.3` tighter (from 1080p a 9:16 crop is only 606 px wide). It reports faces per shot and fallbacks; under half
the samples with a face, look at the frames; profiles and small faces improve with YuNet
(`face_detection_yunet_2023mar.onnx` from opencv_zoo, in `~/.config/video-skills/models/`). Needs
`pip install 'opencv-python-headless>=4.9,<5'` (OpenCV 5 removed the Haar detector). Screen recordings in a split get a
fixed ffmpeg `crop`, not face tracking. The reframed file becomes that composition's video.

Record framings, origins, matte windows and reframe plans (aspect, mode, face rate) in `project.json`; a new cut makes
`jump-frames.json` and every reframe stale.
