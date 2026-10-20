# Style blueprint index · 50 blueprints

The default reference set for `video-reference-match`. Each blueprint is a brand-neutral, measured editing system (structure, pacing, captions, background text, motion graphics, cut-outs, layout, camera, transitions, sound) with a paste-ready brand prompt. Blueprints carry no source identity. Match a project with `scripts/match.py`; the gate in SKILL.md decides whether a blueprint is used.

Files: `blueprints/Bxx.json` (full blueprint) · `index.json` (one row per blueprint, what the matcher reads) · `PROMPTS.md` (all brand prompts) · `weights.json` (matching columns) · `blueprint-schema.md`.

## Targets across comparable talking-head blueprints

| Metric | Median |
|---|---|
| Median shot (s) | 3.15 |
| Cuts per minute | 13.5 |
| Words per minute | 210.0 |

Grade is never taken from a blueprint: it is built from the project's own footage; blueprints only state a look intent.

## Blueprints by caption family

### giant-keyword — small lead words + one huge accent-coloured key word per phrase

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B11](blueprints/B11.json) | podcast-clip 9:16 | Hinglish | short | 5 | `comparison-split`, `split-tilt-cards`, `card-resize`, `yt-lower-third`, `flash-through-white` | Interview recut with giant solid-accent key words, accent/second accent cut-out cards, and a 50/50 split montage swapping proof images every ~15 frames. |
| [B20](blueprints/B20.json) | podcast-clip 9:16 | English | short | 4 | `caption-gradient-fill`, `yt-lower-third`, `whip-pan-cut`, `waveform` | Two-person podcast clip cut on speaker changes, with stacked word-by-word captions: small white lead words over one giant glowing accent UPPERCASE keyword on the chest. |
| [B29](blueprints/B29.json) | podcast-clip 9:16 | Hinglish | short | 4 | `yt-lower-third`, `flash-through-white`, `whip-pan`, `confetti` | Two-camera podcast banter cut on every turn with reaction inserts, letterboxed B&W photo cutaways captioned in the bar, accent cut-out swap gag. |
| [B30](blueprints/B30.json) | b-roll-voiceover 9:16 | English | mid | 3 | `caption-neon-accent`, `animated-bar-chart`, `cta-close`, `transitions-light` | B-roll course ad: one shot and one accent key word per module, lead words justified above. |

### two-tier-script — two typographic tiers (caps line + script / handwritten completion)

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B02](blueprints/B02.json) | podcast-clip 9:10 | Hinglish | short | 4 | `yt-lower-third`, `lt-clean-bar`, `caption-editorial-emphasis`, `testimonial-card`, `waveform` | Podcast holds carried by word-by-word caps captions completed by a glowing accent script line. |

### stacked-kinetic — phrases stacked as kinetic typography

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B08](blueprints/B08.json) | podcast-clip 9:16 | English | short | 4 | `caption-gradient-fill`, `yt-lower-third`, `vignette`, `whip-pan-cut` | Slow two-camera interview carried by lower-left stacked word blocks: thin light words plus one heavy accent glowing key word; B&W cold open. |
| [B40](blueprints/B40.json) | mixed 9:16 | English | mid | 4 | `mesh-gradient-bg`, `caption-kinetic-slam`, `tilt-card`, `card-resize` | Keyed speaker over swapped backgrounds, zig-zag stacked captions with one gradient key line, illustrated phrase cards every few seconds. |
| [B32](blueprints/B32.json) | explainer-graphics 9:16 | English | short | 3 | `flowchart`, `conic-progress-ring`, `constellation-hub`, `device-frame-stage`, `data-chart` | Cream line-art explainer: face-pill cutout in evolving metaphor, blur-slide captions, 2x pink key. |
| [B44](blueprints/B44.json) | podcast-clip 9:16 | English | short | 3 | `comparison-split`, `yt-lower-third`, `caption-gradient-fill` | Zero-cut speaker-over-listener split; glowing three-tier seam captions with one accent key word. |

### boxed-pill — caption text on a solid or translucent box / pill

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B13](blueprints/B13.json) | podcast-clip 9:16 | English | short | 4 | `caption-pill-karaoke`, `yt-lower-third`, `badge-pop`, `cinematic-zoom` | Frenetic name-drop podcast: accent divider pills, second accent name titles, one shot per word. |
| [B19](blueprints/B19.json) | mixed 9:16 | Hinglish | mid | 4 | `browser-device-stage`, `app-showcase`, `agent-cursor`, `code-terminal-run`, `card-resize`, `split-tilt-cards` | Selfie talking head rotating with split face-card + UI mock-ups; UPPERCASE word-by-word captions with one white-boxed accent key phrase. |
| [B31](blueprints/B31.json) | talking-head 9:16 | English | long | 4 | `comparison-split`, `count-up`, `confetti`, `badge-pop` | Game-show versus format: boxed 1-2-word captions at 78 % height, two-size jump cuts, pixel-art P1-vs-P2 scoreboard and a score-comment CTA after every round. |
| [B48](blueprints/B48.json) | talking-head 9:16 | English | short | 3 | `ai-answer-rank`, `badge-pop`, `caption-pill-karaoke`, `marker-checklist-card` | One-take listicle: chest captions with hopping black word box, boxed hook title, stacking list pills. |

### karaoke-highlight — the spoken word is highlighted as it is said

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B36](blueprints/B36.json) | explainer-graphics 9:16 | English | short | 4 | `browser-device-stage`, `agent-cursor`, `cursor-annotate`, `flowchart-vertical`, `chart-story` | Zero-cut cream-canvas UI explainer; three-state grey-to-black karaoke line; result-first progress hook. |
| [B39](blueprints/B39.json) | talking-head 9:16 | English | micro | 3 | `caption-pill-karaoke`, `lower-third-bild`, `camera-shake` | One-take staged press-scrum announcement: top-band karaoke captions, spoken word accent, persistent CTA bar. |

### word-by-word-plain — words appear one at a time, no box, little emphasis

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B06](blueprints/B06.json) | talking-head 9:16 | English | mid | 4 | `x-post`, `reddit-post`, `comparison-split`, `testimonial-card`, `device-frame-stage` | Credibility sandwich: raw selfie hook, then third-party receipts letterboxed on black with word-by-word white captions below, then selfie close. |
| [B12](blueprints/B12.json) | mixed 9:16 | English | mid | 4 | `flowchart`, `constellation-hub`, `device-frame-stage`, `grid-card-assemble` | One evolving black dot-grid diagram above a rounded face card, single-word captions, italic-serif title word, full-face cuts for opinions. |
| [B23](blueprints/B23.json) | talking-head 16:9 | Hinglish | short | 3 | `flash-through-white`, `caption-kinetic-slam`, `lt-accent-underline` | Landscape walk-and-talk: one-word captions, flash-burst hook, corner titles with accent swash-italic word. |
| [B35](blueprints/B35.json) | talking-head 9:16 | English | long | 3 | `caption-highlight`, `lt-clean-bar`, `vignette` | Single locked-off standing take carried only by progressive word-by-word captions that fade in white on the chest; credential-stack hook and spoken numbered signposts. |
| [B27](blueprints/B27.json) | mixed 9:16 | English | mid | 2 | `before-after-wipe`, `comparison-split`, `split-tilt-cards`, `badge-pop` | Question-hook comparison test: front-loaded roll-call cuts, then repeated identical POV test rounds under a one-word-at-a-time uppercase white caption rail. |

### phrase-plain — whole phrase at once, plain text

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B26](blueprints/B26.json) | talking-head 9:16 | English | short | 4 | `ai-answer-rank`, `badge-pop`, `grid-card-assemble`, `card-resize` | Tier-list over one static shot: S-E board in the lower 40 %, icon cards pop to centre then drop into rows; persistent black-box title. |
| [B33](blueprints/B33.json) | talking-head 9:16 | Hinglish | short | 4 | `comparison-split`, `x-post`, `chart-story`, `count-up`, `card-resize`, `marker-checklist-card` | Selfie breakdown: top proof window over accent divider, plain captions, accelerating screenshot montage. |
| [B45](blueprints/B45.json) | mixed 9:16 | English | mid | 4 | `comparison-split`, `browser-device-stage`, `count-up`, `conic-progress-ring`, `chart-story` | Split-panel framework explainer: UI-mock proof for every claim, accent counting badges, numbered chapter card, chunk captions, accent-underlined italic-serif titles. |
| [B25](blueprints/B25.json) | talking-head 9:16 | English | short | 3 | `comparison-split`, `headline-slam`, `caption-highlight` | Low-effort repurposing template: near-square footage letterboxed in black 9:16, fixed two-line pain headline on top, plain two-line captions. |
| [B17](blueprints/B17.json) | podcast-clip 16:9 | English | micro | 2 | `whip-pan`, `yt-lower-third`, `caption-clip-wipe` | Micro question-to-answer clip: whip to guest, light lowercase captions beside the speaker. |

### other:editorial-build — editorial build

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B47](blueprints/B47.json) | podcast-clip 9:16 | English | short | 4 | `caption-editorial-emphasis`, `yt-lower-third`, `testimonial-proof-card`, `card-resize` | Editorial podcast layout: top-left word build, giant accent key phrases, rounded footage card. |

### other:meme-text — meme text

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B22](blueprints/B22.json) | skit 9:16 | English | micro | 1 | `x-post`, `caption-clip-wipe`, `vignette` | Phone meme: quoted ironic claim over deadpan selfie, then held three-line reality set-up. |
| [B24](blueprints/B24.json) | skit 9:16 | Hinglish | micro | 1 | `lt-dark-card`, `caption-pill-karaoke`, `confetti` | Office skit: small two-line set-up text over boss, dropped for a wordless gesture gag. |

### other:phrase-accent-word — phrase accent word

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B38](blueprints/B38.json) | talking-head 9:16 | English | short | 3 | `caption-blend-difference`, `lt-clean-bar`, `chart-story` | Static talking head; difference-blend white captions with one accent word; image cards above the head. |

### other:plain-serif-accent — plain serif accent

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B09](blueprints/B09.json) | talking-head 9:16 | English | short | 5 | `chat-thread`, `chat-message`, `count-up`, `chart-story`, `card-resize`, `lt-clean-bar` | Fast receipt-driven story: rolling gradient numerals, chat bubbles over chest, italic-serif caption accents. |

### other:role-labels — role labels

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B49](blueprints/B49.json) | skit 9:16 | Hinglish | micro | 1 | `lt-soft-pill`, `caption-pill-karaoke`, `confetti` | Single locked-off wide skit with accent role-label pills pinned above each head. |

### other:running-caption+keyword-cards — running caption+keyword cards

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B14](blueprints/B14.json) | ugc-ad 9:16 | English | short | 3 | `app-showcase`, `mk-specs-list`, `badge-pop`, `vfx-iphone-device`, `cta-close` | Frenetic one-feature-one-shot product ad: small lowercase wide-grotesque running captions that swap to huge stacked UPPERCASE keyword cards on each selling point. |

### other:subtitle-box — subtitle box

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B15](blueprints/B15.json) | street-interview 9:16 | English | mid | 3 | `lower-third-bild`, `lt-clean-bar`, `camera-shake` | Doorstep two-camera interview: small subtitles, top promise pill, broadcast lower third, keyword pill. |
| [B21](blueprints/B21.json) | skit 9:16 | English | short | 2 | `caption-pill-karaoke`, `whip-pan`, `camera-shake` | Handheld skit: text colour boxed film subtitles, whip-pan character handoffs, silent captionless punchline. |

### other:two-tier-highlight — two tier highlight

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B03](blueprints/B03.json) | podcast-clip 9:16 | Hinglish | mid | 4 | `count-up`, `apple-money-count`, `cinematic-zoom`, `yt-lower-third`, `whip-pan` | Podcast trailer: money-claim hook with punch-ins, white lead + bold accent Title-Case numbers staggered left, black-frame chapter breaks, pill captions on screens. |

### other:two-voice-colour — two voice colour

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B50](blueprints/B50.json) | mixed 9:16 | English | mid | 3 | `waveform`, `thread-message-stack`, `caption-highlight`, `card-resize` | Fly-on-the-wall call recording made readable by speaker-coded captions above the head: on-camera voice in white serif, off-camera voice in accent wide sans. |

### title-only — no speech captions; titles, labels or cards only

| ID | Format | Lang | Duration | Score | Linked HyperFrames Compositions | Signature |
|---|---|---|---|---|---|---|
| [B04](blueprints/B04.json) | mixed 16:9 | Hinglish | long | 3 | `flowchart`, `constellation-hub`, `mk-specs-list`, `card-resize`, `logo-brand-close` | Landscape course-launch pitch alternating moody low-key talking head with clean white-canvas motion graphics, ending in a struck-through price ladder and comment CTA. |
| [B10](blueprints/B10.json) | skit 9:16 | Hinglish | micro | 2 | `lt-dark-card`, `marker-highlight`, `caption-pill-karaoke` | Deadpan one-take office meme: boxed competitor-pain title, 'Meanwhile : us' pills, printed prop punchline. |
| [B16](blueprints/B16.json) | ugc-ad 9:16 | Hinglish | micro | 2 | `avatar-group-hover`, `headline-slam`, `fade-through` | Locked same-mark team lineup dissolving every ~42 frames under a fixed text colour serif Hinglish offer. |
| [B18](blueprints/B18.json) | ugc-ad 9:16 | none | micro | 2 | `comparison-split`, `headline-slam`, `cta-lockup` | Two event phone clips under one static text colour condensed 3-line ask overlay plus quoted credential. |
| [B34](blueprints/B34.json) | talking-head 9:16 | English | mid | 2 | `headline-slam`, `lt-clean-bar`, `marker-highlight` | Zero-cut single-take talking head carried by one persistent two-box header (light box topic over dark box value range); list withholds final item for DM CTA. |
| [B37](blueprints/B37.json) | brand-promo 9:16 | none | short | 2 | `flash-through-white`, `beat-freeze-cut`, `cinematic-zoom`, `logo-outro` | Music-led BTS event montage, flash transitions, no overlays until an outlined brand + contact card. |
| [B41](blueprints/B41.json) | ugc-ad 9:16 | none | short | 2 | `device-frame-stage`, `marker-checklist-card`, `confetti`, `cta-close` | Song-driven hiring reel told through props (screen, paper signs), logo bug, 3D zoom-blur logo sting. |
| [B42](blueprints/B42.json) | ugc-ad 9:16 | none | micro | 2 | `char-slam-explode`, `flash-through-white`, `beat-freeze-cut` | Still group shot under a colon-ended serif title, then a textless ~10-frame-per-clip highlight burst. |
| [B43](blueprints/B43.json) | brand-promo 9:16 | none | short | 2 | `char-slam-explode`, `colorama-wipe`, `morph-text`, `cta-close` | Music-only kinetic-type manifesto: one giant word per card flipping black/cream on the beat, accent punchline word, recurring 3D ball, logo hold. |
| [B01](blueprints/B01.json) | brand-promo 9:16 | none | micro | 1 | `instagram-follow`, `tiktok-follow`, `cta-close`, `char-slam-explode`, `colorama-wipe` | Footage-free one-word kinetic cards on flat colours: fill/outline stutter stack, mock follow-click end card. |
| [B05](blueprints/B05.json) | skit 9:16 | English | micro | 1 | `lt-bold-block`, `caption-clip-wipe`, `camera-shake`, `confetti` | Two-shot POV skit: persistent mid-frame label, rant, jump cut to polite phone voice. |
| [B07](blueprints/B07.json) | brand-promo 9:16 | none | micro | 1 | `yt-comment-card`, `caption-kinetic-slam`, `cta-lockup`, `mesh-gradient-bg` | Music-only save-bait: quoted viewer question, caps reply, dark note-screenshot list, framed monogram card. |
| [B28](blueprints/B28.json) | skit 9:16 | Hindi | micro | 1 | `lt-dark-card`, `caption-blend-difference`, `vignette` | Single moody office two-shot lip-sync under a persistent text colour condensed-serif headline. |
| [B46](blueprints/B46.json) | brand-promo 9:16 | none | micro | 1 | `colorama-wipe`, `char-slam-explode`, `logo-outro` | Type-only teaser: typeface swaps every 2-3 frames, accent/black inverting word cards, blurring stock reveal. |

## Tags

talking-head (14), podcast-clip (10), vertical (10), hinglish (9), no-captions (9), music-only (8), micro (8), split-screen (8), comment-cta (6), two-person (5), single-take (5), word-by-word (4), phone-footage (4), selfie (4), kinetic-typography (3), two-tier-captions (3), comedy (3), ugc (3), word-by-word-captions (3), interview (3), stacked-captions (3), logo-end-card (3), jump-cuts (3), skit (3), subject-cutout (3), dark-studio (3), comment-keyword-cta (3), handheld (3), serif-title (3), hiring (3), minimal-edit (3), event (3), ui-mockups (3), no-cta (3), single-shot (3), no-cuts (3), text-only (2), beat-synced (2), end-card (2), roman-hinglish-captions (2), trailer (2), pill-captions (2), progress-bar (2), english (2), workplace-humour (2), b-roll (2), colour-flash (2), fast-pace (2), versus (2), hinglish-text (2), giant-key-word (2), handle-end-card (2), rapid-cuts (2), face-card (2), one-word-captions (2), italic-serif-title (2), lead-magnet (2), lowercase-captions (2), subtitles (2), long-form (2)

