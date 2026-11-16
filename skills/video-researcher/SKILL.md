---
name: video-researcher
description: Researches the video's topic and the speaker's claims on the web, then plans the motion graphics, sounds and b-roll that complement it (each tied to a sourced fact and a moment in the cut). Use after video-pipeline analyze, before the storyboard, or when the user asks to research, fact-check or add b-roll.
---

# Research → graphics, sounds, b-roll

Research makes the edit richer without inventing anything: every number, name, headline or image on screen comes from
a source you can link. Same variables as `video-pipeline`; `R="$SK/video-researcher/scripts/research.py"`.

## 1. Find what to research

```bash
"$PY" "$R" init --project "$ROOT" --topic "<topic from the brief>"
```

Writes `$W/research/research.json` and `RESEARCH.md`: the moments in the cut that carry numbers, money, dates,
names or claims, each with its `speech-NNN` id. Read the full flat transcript too: the topic itself deserves context
(what the company is, when it happened, how big it is).

## 2. Research on the web

Search for each moment and for the topic. Prefer primary sources (company filings, official sites, government data,
reputable news). For each confirmed fact add to `facts`:

```json
{"id": "research-001", "claim": "Zomato's FY24 revenue was ₹12,114 crore", "source_url": "https://...",
 "source_name": "Zomato annual report", "published": "2024-05-13", "accessed": "2026-11-15",
 "speech_refs": ["speech-004"], "on_screen": "FY24 revenue: ₹12,114 Cr"}
```

If sources disagree or nothing reliable exists, do not add the fact; note it for the user. If the speaker's number is
wrong, tell the user instead of silently "fixing" it on screen.

## 3. Plan what the viewer sees and hears

From the facts, fill the plans the storyboard will use:

- `motion`: HyperFrames catalog blocks (search with `catalog.py search`) for numbers, charts, headlines, maps,
  timelines, logos, quotes: `{"id", "at_speech", "facts": [...], "catalog": "<name>", "vars": {...}, "why"}`.
- `broll`: visuals that show what is being talked about: first a catalog block built from the facts (headline card,
  stat card, map, logo wall); then a real image with `source_url` + `license` (saved in `$W/research/broll/`);
  a generated shot only through `video-generate` with the user's OK (it costs money).
- `sounds`: cues from the style's palette (`sound-palette/audio/`) that land a moment: a ping for a number, a paper
  slide for a headline, a whoosh for a section turn. Few and purposeful.

```bash
"$PY" "$R" check --project "$ROOT"      # ids, URLs, image licences, speech refs still in the cut
```

Give the user a short summary: facts used (with links), what each graphic shows, and anything unverified.
