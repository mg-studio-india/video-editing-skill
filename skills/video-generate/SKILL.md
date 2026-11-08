---
name: video-generate
description: Generates stills (Gemini Flash Image) and short video shots (Google Veo), OpenRouter as fallback, behind a cost approval, never as fake proof. Use for generate-image or generate-video inserts and when the user asks to "generate a shot / image of" something they have no footage for.
---
# generate

Generated shots cost money per second, and a fake that looks like evidence destroys trust: every shot is planned,
priced, approved, checked as a still, labelled and recorded.

This skill runs only when the user explicitly requests a generated shot or image. It is not the default source of missing b-roll for the project pipeline.

```bash
ROOT="<user-selected-video-folder>"
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"; S="$ENG/scripts"; W="$ROOT/.video-pipeline"
ENGINE_ROOT="${VIDEO_ENGINE_DIR:-$HOME/.config/video-skills/engine}"; HF="$ENGINE_ROOT/node_modules/.bin/hyperframes"
```

**What may be generated:** only the shot or image the user explicitly requested. Do not generate it as proof of a real event, product feature, result, dashboard, document, platform UI, testimonial or metric. Do not invent a missing source moment or fill unused screen space with generated footage. Keep generated assets clearly labelled in the project ledger.

**Tool order:** Use a brand asset or reference already supplied in the project first. If the user asks to retrieve a missing, non-evidentiary asset, use the configured local HyperFrames CLI (`"$HF" media-use resolve --type image|icon|logo ...`) and record its source.
Images: Gemini Flash Image (`GEMINI_IMAGE_MODEL`, default `gemini-2.5-flash-image`) → OpenRouter
(`OPENROUTER_IMAGE_MODEL`). Video: Veo (`VEO_MODEL`, default `veo-3.1-generate-preview`); OpenRouter only if it lists a
video model for the key and you have read that model's request format (the script won't guess). No video available:
a still with a slow push-in (`broll-conform.py --push 1.08`). Once per session `python3 "$S/generate.py" models`
confirms the model names exist (Google renames them; set the env vars if NOT FOUND). Keys: `GEMINI_API_KEY`,
`OPENROUTER_API_KEY`.

## The chain (each step a stop)

1. **Shot list** in `$W/BROLL.md` (insert id, anchor, scene line, outfit from the footage, camera move, length, aspect),
   approved with the plan.
2. **References** for shots of the speaker: 6-12 user photos (front, three-quarter, neutral and smiling, half-body) +
   2-3 footage frames (`ffmpeg -ss <t> -i "$W/hyperframes/input-video.mp4" -frames:v 1 ref-1.png`); the same set every shot.
3. **Gate 3:** run each command without `--yes`: it prints the plan and an estimate (pass `--price-per-second` /
   `--price-per-image` from the provider's current pricing; prices are never invented). Show the total; wait for a yes.
4. **Still first:** `generate.py image --prompt "<the person from the reference photos, same face and hair, wearing ..., <one action> in <a specific place>, <time of day> window light, 35mm, eye level, shallow depth of field, natural skin texture>" --ref ref-1.png --ref ref-2.png --aspect 9:16 --out "$W/broll/raw/gen-01.png" --yes`.
   Check face, hands, anything written; a bad still is a re-run, not a video.
5. **Motion:** `generate.py video --image "$W/broll/raw/gen-01.png" --prompt "slow push-in, she looks up from the laptop, natural motion, no cuts, no new people" --aspect 9:16 --seconds 8 --out "$W/broll/raw/gen-01.mp4" --yes`
   (camera + one small action; `--last` pins an end frame).
6. **Conform:** `broll-conform.py --in "$W/broll/raw/gen-01.mp4" --out "$W/hyperframes/broll/gen-01.mp4" --start 0.5 --dur <slot + 1> --grade`, read its sheet, then a `clip` beat on its anchor.

Restyling an existing clip is `video-omni-restyle`, off unless the user asks.

**Records:** every output goes to `ledger.json` with `"ai_generated": true`, provider, model, prompt, inputs; the user
marks the video as synthetic or altered content where platforms ask (list it in the delivery notes). A refusal is an
error naming the provider: change or drop the shot, never rephrase around safety; a refusal on a real person's likeness
is a stop.
