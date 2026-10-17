# style.json fields

Sizes are fractions of the canvas WIDTH, positions fractions of the HEIGHT, so one style works at 9:16 and 16:9.
"Read by" says which builder uses the field; a field nobody reads is documentation only.

| Field | Default | Read by | Meaning |
|---|---|---|---|
| `name`, `source`, `status` | | people | where the look came from (reference files, date) and whether it is approved |
| `canvas` | `[1080,1920]` | people | the usual output size for this style (the storyboard's `canvas` decides the build) |
| `colors.text` | `#ffffff` | treatments, captions | main text colour |
| `colors.accent` | `#ffd400` | treatments, captions | emphasis words, markers, dividers, active caption word |
| `colors.accent2` | `#00e0ff` | (free for formats) | a second accent |
| `colors.money` | `#22e07a` | (free for formats) | money and stakes figures |
| `colors.dark` | `#0b0b0f` | split | background behind split-screen halves |
| `colors.paper`, `colors.paper_ink` | `#f4ecd8`, `#1d1a16` | drawer | the paper panel and its text |
| `fonts.display.family` | `Poppins` | all | the display family; must have a local file per weight |
| `fonts.display.files` | | stage, compose, captions | `{weight: path}`; paths absolute, relative to the style file, or `@engine/...` |
| `fonts.body` | | stage, compose | optional second family, same shape |
| `fonts.fallback` | | all | a family for a second script, stacked after display (`Inter` → `Noto Sans Devanagari`). Variable fonts: key the file by its weight range, `"100 900"` |
| `evidence` | | people | the basis of each value (observed / cross-post / production default) |
| `colors.band` | `#000000` | banner | the headline band's background |
| `safe_zone_px` | top 180, bottom 300 | format | platform UI margins to keep free of critical copy |
| `fonts.scripts` | `["latin"]` | people | scripts the font covers (`devanagari` for Hindi) |
| `caption_script` | | transcribe, captions | `latin`, `devanagari`, or `roman-hinglish` (needs a checked transliteration pass) |
| `text_stroke` | `0` | hero, card titles | dark outline as a fraction of the font size; ~0.045 keeps accents readable over bright footage |
| `captions.engine` | `builtin` | captions skill | `builtin`, or `catalog:<component>` (e.g. `catalog:caption-highlight`) |
| `captions.mode` | `pop` | builtin | `pop` (words pop in), `karaoke` (all shown, active word lit), `block` (whole group fades) |
| `captions.case` | `upper` | builtin | `upper` or `keep` |
| `captions.weight` | `800` | builtin | font weight |
| `captions.color`, `active_color`, `emphasis_color` | text, accent, accent | builtin | idle word, the word being spoken, emphasised words |
| `captions.emphasis_bg` | `""` | builtin | a block behind emphasised words (keeps a low-contrast accent readable) |
| `captions.max_emphasis` | none | builtin | at most this many emphasised words per group (business reels: 1) |
| `captions.pill_color` | `""` | builtin | a coloured block behind the active word instead of a colour change |
| `captions.stroke` | `0` | builtin | outline in px |
| `captions.portrait` / `.landscape` | | builtin, stage | `size`, `y`, `max_words`, `max_chars`, `low_y` (where captions go while a panel is up) per orientation |
| `captions.set` | `{}` | catalog | component constants to override, e.g. `{"COLOR_INACTIVE": "#5E5E5E"}` |
| `cards.bg`, `text`, `radius`, `border`, `title_color` | dark glass, accent title | cards | card list look |
| `motion.in`, `out`, `ease_in`, `ease_out` | 0.35, 0.25, power3.out, power2.in | hero, cards, banner, motion-graphics | entrance and exit timing |
| `motion.keyword`, `callout`, `punch`, `chart`, `rules` | | motion-graphics | further timings and the motion hierarchy in words |
| `camera.punch`, `creep`, `origin_*` | | take-geometry | zoom ranges and camera origin per orientation |
| `pacing` | | plan-storyboard | measured from references: seconds between visual changes, words per caption |
| `sound.default`, `allowed`, `never` | silence | sound-design | which sounds earn a place |
| `audio_preset` | `youtube` | audio | the loudness preset (`shorts` for reels) |
