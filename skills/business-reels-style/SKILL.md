---
name: business-reels-style
description: Use when authoring or restyling short-form business, creator, interview, finance, entrepreneurship, D2C, or marketing videos in HyperFrames and you need an evidence-aware visual and motion direction informed by Raj Shamani, Nitin Joshi, Markets with Jayant, Bypreneurs, D2C by Nikhil, and Marketing with Govind.
---
# Business Creator Reels Style

Vertical reels that communicate a business idea fast, keep the speaker credible, make evidence legible, and hold one
coherent rhythm. A **composite production style** informed by public traces of six channels (Raj Shamani, Nitin Joshi,
Markets with Jayant, Bypreneurs, D2C by Nikhil, Marketing with Govind). It is one specific style option within the
broader 225-Style Taxonomy (`video-editing-styles-master.md`), not a blanket default for every video. Video format and
layout must always be determined dynamically in consultation with the user based on transcript context. It is a style
layer on top of the HyperFrames skills, never a replacement for them.

References: `references/accounts.md` (per-account evidence, lessons, unknowns) · `references/templates.md` (motion
patterns, edit templates A-D) · `references/research-audit.md` (sources) · `references/original-guide.md` (this skill's
full original text).

## Evidence contract: never pretend to have seen what was not inspected

Label every material style claim, and never upgrade a label because a choice seems plausible:

| Label | Meaning |
|---|---|
| VIDEO-FRAME VERIFIED | a frame of the exact account's Reel was directly inspected |
| PUBLIC CROSS-POST FRAME | a public frame associated with the creator; not proven a Reel or a top performer |
| POST/TEXT VERIFIED | the post, caption or transcript was readable; the moving image was not inspected |
| PROFILE/METRICS ONLY | metadata or aggregate metrics; says nothing about visuals |
| UNVERIFIED | no suitable evidence; do not fill gaps with genre stereotypes |
| PRODUCTION DEFAULT | a choice for this deliverable, not a fact about a reference |

In notes use Observed / Repeated (2+ independent posts) / Interpretation / Production default / Unknown. A single
screenshot is never a recurring brand rule.

**"Top / viral / trending"** only with a platform view or play count, its capture date, confirmation the metric is
views, and a stated sample ("top 5 of 20 accessible Reels from the last 90 days"); compare raw views with posting age.
Otherwise say "accessible examples". High views do not prove a colour, font or pacing caused them. The current research
did **not** support a top-Reel ranking for all six accounts, and most visual details are unverified
(`references/accounts.md`).

## When not to use

Not as proof of any creator's native brand; not to imitate a creator's voice, face or identity; never to invent
sources, statistics, screenshots, quotes, logos or branded UI. If one account is requested, do not blend in the others
without permission. If exact account-faithful extraction is required and only metadata exists, say what cannot be
verified and ask for screen recordings, downloaded videos or frame captures.

## Workflow

1. **HyperFrames context first:** `/hyperframes` (routing), `/hyperframes-core` (before composition HTML),
   `/hyperframes-creative`, `/hyperframes-animation`, and the media skill before external images, logos, video or music.
   Never invent HyperFrames attributes or APIs; keep everything deterministic and seek-safe.
2. **Audit the evidence** for each account: the exact profile; candidate Reels with views and dates; the Reel itself,
   not its tile or transcript. Per Reel inspect: first 0-2 s (hook, first shot, text, framing, sound entrance), setup,
   middle (cut rhythm, B-roll, captions, callouts, charts), the proof reveal, the ending, the audio. Record findings
   separately from interpretation; if a Reel cannot be played, say so and report no motion, font, palette or pacing.
3. **Design brief before code:** goal and audience, source assets and rights, canvas, palette and fonts (each labelled),
   speaker and evidence layout, captions, motion and timings, transitions and sound, safe zones, sources and qualifiers,
   known deviations. A six-channel composite is stated as a designed synthesis.
4. **Build, render, verify:** readable with motion off first; motion after hierarchy and timing work in a still; render
   and inspect opening, middle, reveal and ending; run the HyperFrames check; inspect the real output for collisions,
   clipped captions, wrong fonts, drift, seek issues, missing media, audio peaks, unreadable sources. Report verified vs
   unverified.

## Composite direction (production defaults)

**Principle: editorial credibility first, high-energy emphasis second.** Story and evidence carry attention; type and
motion strengthen emphasis but never make ordinary claims look like facts or hide missing evidence.

- **Palette (defaults, not sampled):** bg `#171717`, surface `#252525`, text `#F5F1EA`, muted `#B9B5AE`, accent `#D9413A`,
  line `#4A4845`. Red is a starting accent (one red word in one Raj-associated cross-post frame); white text on
  cinematic footage was seen in one Bypreneurs-associated image. No neon or other "signature" hue without a brand guide
  or measured frame; replace defaults with sampled or approved colours for a specific creator or client; keep natural
  skin tones.
- **Type (defaults):** bold sans (Inter 700-800 or installed equivalent) for display; Inter 500-700 for captions; a
  tested Devanagari font (Noto Sans Devanagari) for Hindi, checked in the actual render; lining numerals, units and
  qualifiers kept; at most two families.
- **Geometry (1080x1920 starting values):** headline 1-4 concise lines; side margin 80-100 px; top 180 px and bottom
  300 px free of critical copy until the platform UI is checked; at most two information zones per frame; never cover
  eyes, mouth, product identifiers, chart labels or the key passage of a document; check legibility at phone size.
- **Shot hierarchy:** person-led (speaker focal, text supports) · evidence-led (document, chart or product focal;
  speaker as voice or a readable picture-in-picture) · concept-led (diagram or number, quiet background) ·
  contrast-led (two comparable states, aligned text, factual comparison). No B-roll just to hide a jump cut.

## Motion (production defaults, not measured)

Primary: hard cuts, clean reframes, phrase-synchronised text. Secondary: subtle scale, short slide or fade callouts,
simple chart builds, relevant B-roll. Rare: whips, big zooms, shake, glitch, full-screen kinetic type, dramatic hits,
only when meaning supports them. Avoid: perpetual motion, random decoration, bounce on every caption, transitions on
every cut, effects that obscure facts.

| Element | Duration | Behaviour / constraint |
|---|---:|---|
| Headline reveal | 180-280 ms | opacity + short vertical settle; no long title-card intro before the hook |
| Keyword emphasis | 100-180 ms | subtle scale, weight or accent; one key phrase at a time |
| Callout / label | 220-360 ms | opacity + short directional move; stays attached to its referent |
| Camera punch-in | 220-350 ms | modest; motivated by a meaningful assertion or reaction |
| Chart build | 350-800 ms | sequential, only when data order matters |
| Scene transition | 150-300 ms | brief dissolve or slide; default to a hard cut |
| End signature | 200-400 ms | brief; never delays the conclusion |

Use the shortest animation that communicates the change. Patterns (claim → evidence → implication; text split across a
contrast; speaker-led hook) are in `references/templates.md`.

## Captions, overlays, evidence, sound

- Captions match the audio exactly (negations, qualifiers, names, numbers); natural phrase groups over word-by-word
  bouncing for complex explanations; at most one highlighted key phrase per caption beat, not by colour alone; no
  headline repeating the caption sentence unless intended; Hindi and Hinglish proofread by hand.
- Source labels stay separate from the editorial headline. No fake comment UI, view counts, engagement counters, news
  banners or platform interface. Creator names or logos only from supplied or verified assets.
- Keep the source's time period, metric definition, unit and denominator; cite on screen where possible (long citations
  in the caption or notes); distinguish documented fact, attributed allegation, opinion and inference; mark illustrative
  charts; never invent revenue, valuation, conversion, market share, CAC, ROAS, customer counts or returns; no stock or
  unrelated screenshot as evidence about a named company; show a document only when it supports the claim and is
  readable long enough; state gaps instead of hiding them.
- Sound (defaults): voice first, cleaned without harshness or gating artifacts; music ducked under speech, no scoring
  that implies unsupported certainty; an accent only when a reveal needs it; nothing masking consonants (Hindi-English
  code-switching especially); check loudness, peaks, phase and tails; licensed audio only.

Templates (full steps in `references/templates.md`): **A** founder/podcast moment 15-45 s · **B** business/market case
study 30-90 s or longer if needed (the accessible Jayant sample ran 144.4 s) · **C** D2C/marketing education 15-45 s ·
**D** contrast/retention edit.

## Checklist

- **Before:** correct account and Reel; "top" status supported or the video called an example; inspection level
  documented; one-line beat sheet (claim, context, evidence, ending); rights checked for every asset; observed vs
  interpretation vs default separated.
- **During:** a meaningful first frame, no intro; one obvious hierarchy; proofread captions; motion only on meaningful
  change; B-roll and charts relevant and labelled; one deliberate accent; nothing fabricated; HyperFrames rules followed.
- **Before delivery:** render inspected at 0%, 10-20%, middle, reveal, ending and dense moments; phone-size readability;
  safe zones on the target platform; no clipping, reflow, missing assets, flash frames or unsupported fonts; voice
  intelligible, no spikes or masked words; every claim verified and attributed; handoff written.

## Handoff (always)

**Deliverable** (runtime, canvas, format) · **Style basis** (accounts and inspected URLs) · **Observed details** (only
what inspected frames, audio or text support) · **Production defaults** (palette, fonts, timings, layout not observed)
· **Unverified items** (missing access, uncertain ranking, unknown metrics) · **Verification** (renders reviewed,
checks run, known defects). Never write "matches all six channels" or "based on the top trending Reel of each account"
unless the audit truly supports it.
