---
name: video-generate
description: Generates a still (Gemini Flash Image) or short shot (Google Veo; OpenRouter fallback) for b-roll the research calls for when no catalog block or sourced image can show it - priced and approved first, labelled as AI-generated, never passed off as real evidence. Use only when the user agrees to a generated shot.
---

# Generated b-roll (paid, opt-in)

Order of preference for b-roll (`video-researcher` → `broll`): a HyperFrames catalog block built from a sourced fact
→ a real image with source and licence → a generated shot (this skill). Generated shots cost money per second and
must never look like proof of a real event, product, UI, document, dashboard, metric or testimonial.

```bash
S="$ENG/scripts"      # ENG, PY, W, ROOT as in video-pipeline
```

1. **Plan** each shot in `$W/research/research.json` → `broll` (`kind: "generated"`, `at_speech`, the fact it
   illustrates, one-line scene, camera move, length, aspect). Show the list with the storyboard.
2. **Price:** run the command without `--yes`: it prints the plan and an estimate (pass `--price-per-second` /
   `--price-per-image` from the provider's current pricing; never invent prices). Wait for the user's yes.
3. **Still first:** `"$PY" "$S/generate.py" image --prompt "<scene>, natural light, 35mm, no text" --aspect 9:16
   --out "$W/research/broll/gen-01.png" --yes`. Check hands, faces, any lettering; a bad still is re-run, not animated.
4. **Motion** (optional): `"$PY" "$S/generate.py" video --image "$W/research/broll/gen-01.png" --prompt "slow push-in,
   natural motion, no cuts" --aspect 9:16 --seconds 6 --out "$W/research/broll/gen-01.mp4" --yes`. No video model:
   use the still with a slow push (`broll-conform.py --push 1.08`).
5. **Conform:** `"$PY" "$S/broll-conform.py" --in "$W/research/broll/gen-01.mp4" --out "$W/hyperframes/broll/gen-01.mp4"
   --start 0.3 --dur <slot + 0.5> --grade`, then a storyboard beat `{"type": "clip", "src": "broll/gen-01.mp4", ...,
   "refs": ["research-00N"]}`.

Models: `GEMINI_IMAGE_MODEL` (default `gemini-2.5-flash-image`), `VEO_MODEL` (default `veo-3.1-generate-preview`),
`OPENROUTER_IMAGE_MODEL`; keys `GEMINI_API_KEY`, `OPENROUTER_API_KEY`. `"$PY" "$S/generate.py" models` confirms the
names once per session. Every output is logged in `ledger.json` with `"ai_generated": true`; tell the user to mark the
video as containing AI-generated content where the platform asks. A provider refusal is final for that shot; a
refusal involving a real person's likeness is a stop.
