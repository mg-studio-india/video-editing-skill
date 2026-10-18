# Blueprint schema (`blueprint/1`)

One JSON file per blueprint in `blueprints/Bxx.json`. Measured values are from frame/audio analysis; font sizes were
solved for the local engine fonts; everything else is a description of the editing system. No source identity.

| Key | Content |
|---|---|
| `id` | `Bxx` |
| `format` | `type` (talking-head, podcast-clip, explainer-graphics, b-roll-voiceover, screen-demo, ugc-ad, skit, brand-promo, street-interview, mixed), `aspect`, `language`, `duration_class`, `people_on_screen` |
| `topic_class` | generic class (business advice, marketing, tech/AI tools, ...) |
| `caption_family` | giant-keyword, two-tier-script, stacked-kinetic, boxed-pill, karaoke-highlight, word-by-word-plain, phrase-plain, title-only, none, or `other:<name>` |
| `signature` | `one_line`, `unique_devices` (what is distinctive across the whole library), `why_it_works` |
| `hook` | type, first word / first cut (s), opening frame |
| `structure` | beats with `from_pct` / `to_pct` of runtime |
| `pacing` | pace, median shot, cuts/min, wpm, pauses/min, visual change interval |
| `elements` | `captions`, `background_text`, `motion_graphics`, `cards_lists`, `silhouettes_cutouts`, `broll_inserts`, `layout`, `camera`, `transitions`, `end_card`: each item `what` / `when` / `how` / `catalog` (style IDs) |
| `captions_spec`, `other_text_spec` | measured caption / text system: grouping, layout %, type tiers (closest local font, `verified_px` at 1080x1920, tracking, colour role), animation in frames |
| `style` | `palette_roles` (defaults for text / accent / surface / card), `fonts`, `look_intent` (words only) |
| `sound` | music (heuristic), SFX placements, loudness |
| `measured` | grade numbers (look reference only), layout shares (letterbox, split), sound heuristics (beat periodicity, cut-hit share) |
| `catalog_styles` | style IDs from `video-plan-storyboard/references/style-catalog.md` with their role here |
| `use_when`, `avoid_when` | conditions for choosing it |
| `match` | `tags`, `keywords`, `needs` (speaker footage, screen recordings, B-roll, brand assets) |
| `quality_score` | 1-5 fit as a business/creator reel reference |
| `brand_prompt` | paste-ready prompt against brand tokens, with a VERIFY step |
