---
name: video-captions
description: Sets the captions - simple semi-bold phrases in sentence case, white, with only the keywords highlighted in the accent colour and a small kinetic pop as they are spoken; always Roman-script Hinglish, word-timed to the cut. Use when choosing caption keywords or changing the caption look.
---

# Captions

Default look (every default style): **Inter SemiBold (600), sentence case, white, soft shadow, 2-4 word phrases**
that follow the speech. Only **keywords** change: they turn the accent colour with a quick pop (scale 1 → 1.12 → 1)
on the exact word. Hinglish is always Roman script. Timing comes from the flat transcript, so captions match the audio.

## Choose the keywords

In `$W/storyboard.json`:

```json
"captions": {"source": "transcript.json", "keywords": ["crore", "IPO", "sabse bada", "profit"]}
```

- Pick the words that carry the point: numbers, names, the claim, the payoff. Short phrases are fine ("sabse bada").
- At most one keyword lights up per caption phrase (`max_emphasis: 1`); a number is highlighted automatically.
- Spell keywords exactly as the transcript does (fix misheard words with `video-transcribe` first).
- No keywords at all = plain white captions.

## Adjust the look (only when the user asks)

`style.json` → `captions`:

| key | default | options |
|---|---|---|
| `mode` | `keywords` | `phrase` (every word lights up while spoken), `pop` (words pop in) |
| `highlight` | `color` | `marker` (accent bar sweeps behind the keyword, dark text) |
| `weight` | 600 | any weight of the caption font (Inter is variable 100-900) |
| `case` | `keep` | `upper` |
| `size` | 0.062 of width (portrait) | fraction of width, or pixels |
| `y` | below the chin / 0.72 | fraction of height for the caption line |
| `plate_color` | none | e.g. `rgba(8,10,14,.38)` for a subtle backing |
| `emphasis_color` | style accent | any colour |
| `max_emphasis` | 1 | keywords lit per phrase |

Turn captions off with `"captions": null`. A HyperFrames catalog caption component is also allowed: add it as a
`block` beat (`catalog.py search caption`); the pipeline injects the words and keywords into it.

Check after render: phrases readable at phone size, never over the face or a graphic's text, keywords landing on the
spoken word.
