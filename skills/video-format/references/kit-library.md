# The kit's 16:9 format library (compose.py)

Ported from the forked kit. These formats are built by `compose.py` on a 1920x1080 talking-head composition, in the kit's glass look (`video-style/styles/kit-look.json`). The JSON shape of each type is in compose.py's docstring. Your seven treatments are in `treatment-beats.md`.

Vary the formats; never the same device twice in a row. `*` = built and snapshot-tested but used in fewer real
deliveries: read its first real snapshot with extra care and name it at Checkpoint B. The composer builds every format
with a type below (the JSON shapes are in compose.py's docstring); the specs give the numbers to check a snapshot
against, and to hand-build the rest.

| # | Format | Use for | Composer type |
|---|---|---|---|
| 1 | Big number behind the head | money and stakes figures | hand-built |
| 2 | Lower line | **any single line of copy, the default** | `line` |
| 3a | Glass card | lists, deliverables | `list` |
| 3b | Extended-left bullets | the same, for variety | `bullets` |
| 3c* | Glass pop-out | a short titled list when 3a and 3b were just used | `popout` |
| 4a | Logo card | naming a tool; the default for a list of tools | `logo` |
| 4b | Full-screen site cutaway | a site introduced as the subject, a glance under 3 s | `site` |
| 4c* | 3D floating browser | a site you talk about, held longer, or that scrolls | `browser3d` |
| 4d* | 3D screenshot fan | two or three screenshots at once: posts, wins, app screens | `fan3d` |
| 5 | Punchline chip | jokes, pattern interrupts | `chip` |
| 6 | Flow diagram | a long process with a detail line per step | hand-built |
| 7 | Ascending staircase | steps where each one earns the next | hand-built |
| 8 | Funnel | volume narrowing toward money | hand-built |
| 9 | Chapter tag | naming the section you just entered | `tag` |
| 9b | Progress tag | the same with N pips, on a numbered series | `tag` with `n`, `of` |
| 9c* | Slot wall | the video's parts as sockets, planted empty in the hook | `wall` |
| 10 | Success stamp | the moment something works | hand-built |
| 11 | Description pointer | "link in the description" | `pointer` |
| 12 | Key-word highlight | long form only: two or three key words | hand-built |
| 13 | Prompt window | reading out a prompt you give an AI | hand-built |
| 13b | AI chat window | the chat app itself: images drop in, the prompt types, the answer lands | `formats/claude_chat.py` |
| 14 | Subscribe bar | the ask, mid-video | hand-built |
| 16 | Shimmer sweep | a hero line | `"shimmer": true` on `line` |
| 17 | Vignette + grain | the awkward beat after a joke | `vignette` |
| 18 | Article cutaway with highlighter | one headline or quote from a page | hand-built |
| 18b | Doc read | two or three passages from one page, the rest out of focus | `doc` |
| 19 | Photo card | a named person | hand-built |
| 20 | Full-frame video cutaway | footage that needs hand work | hand-built |
| 20b | Before/after wipe | inside an image cutaway: the before becomes the after | hand-built |
| 20c | Clip | a full-frame cutaway: your screen, archive, stock, AI B-roll | `clip` |
| 21 | Logo swap plate | "X versus Y" | hand-built |
| 23 | Tutorial layout | screen + face in one glass composition | not built yet |
| 24* | Stat tiles | two to four numbers that belong together | `stats` |
| 25* | Growth card | one number that grew, with its shape | `growth` |
| 25m* | Chart morph | the growth bars turn into the trend line | `"morph": true` on `growth` |
| 26* | Bar comparison | "this takes X, that takes Y" | `bars` |
| 27* | Pipeline | three to five steps lit one by one | `pipeline` |
| 28* | Hub | one idea and the parts it is made of | `hub` |
| 29* | Equation | "A + B = C" said as one line | `equation` |
| 30* | Flowing paths | one thing becoming several, then one result | `flow` |
| 31* | Dashboard zoom | proof from a real dashboard: find one number, lift it out | `dashzoom` |
| 32* | Glass focus | walking through a table one row at a time | `lens` |
| 33* | Search → results | "I searched for X" | `search` |
| 34* | Magnetic dock | three or more tools named in a row | `dock` |
| 35* | Masked title | a full-frame chapter card | `masktitle` |
| 36* | Button → player | "watch this video", mid-video | `player` |
| 37* | Image reveal | a still opening behind slats | `image` |
| 38* | Exploded layers | what an app or a stack is made of | `layers` |
| 39 | World camera | a system you walk through: push in, pull back to reveal, travel | `world` |
| 40 | Numbered deck | the full-frame opener of each part of a numbered video | `deck` |
| 41 | Pills around the head | two to six short labels while you stay on camera | `pills` |
| 42 | Chat (bubbles, window, phone) | a conversation | `chat` |
| - | Check marker* | done and to-do lists: a check draws on each item | `"marker": "check"` on `list`, `bullets`, `popout` |
| - | Thumbnail grid | your own thumbnails; the cursor clicks one | `grid` |
| - | Coded scenes | money, catalog, room, plate, profile: B-roll with no stock | `scene` |

### When two formats compete

Pick the one that fits what you are saying. Tied: the one used least so far in this video (compose.py prints the
counts). Still tied: the one used least in your last video.

| You are... | Candidates | Pick |
|---|---|---|
| naming one tool | 4a, 34 | 4a; three or more tools in a row: 34 |
| showing a website | 4b, 4c | 4b for a glance under 3 s; 4c when you talk about it or it scrolls |
| giving numbers | 1, 24, 25 | 1 for one stakes figure; 24 for two to four that belong together; 25 when it grew and the shape matters (25m when the trend is the point) |
| explaining a process | 6, 7, 8, 27, 30 | 7 each step earns the next; 8 volume narrows to money; 30 one thing becomes several; 27 a quick sequence; 6 a long one |
| comparing | 26, 32, 21 | 26 for sizes (time, money); 32 for values read off a table; 21 for tool versus tool |
| listing | 3a, 3b, 3c, 41, check marker | never the same device twice in a row; the check marker for done or to-do; long form: no list panels |
| opening a section | 9, 9b, 9c, 35, 40 | 9c on a video with a spine; 40 for two to four numbered parts; 9b on a numbered series; 35 for a long break; 9 otherwise |
| showing an image or footage | 19, 20c, 37 | 19 for a named person; 20c for moving footage (20 when it needs hand work); 37 for a still |
| showing screenshots | 4d, 31, 4c | 31 when one number on it is the point; 4d for two or three; 4c for one site |
| typing | 13, 13b, 33 | 13 or 13b for a prompt to an AI (13b when the app itself matters); 33 for a search |
| saying one line | 2, 29, 5 | 29 only for an "A + B = C" line; 5 for a punchline; 2 otherwise |
| showing parts of a whole | 28, 38, 39 | 38 for layers of a product or stack; 28 for parts of an idea; 39 when the camera should move between them |
| naming a few short things on camera | 3a, 41 | 41 for labels of one to three words around you; 3a when you count a list |
| a conversation | 13, 42 | 42 for people talking; 13 for a prompt to an AI |
| reading from a page | 18, 18b | 18 for one headline; 18b for two or three passages |
| pointing to another video | 36 | mid-video only; at the end the YouTube end screen does the job |

### Copy on screen

- **2. Lower line (the default).** Any single line of copy, never in a card: bottom-centre, no box, always centred,
  ~100 to 104 px/700, letter-spacing -.015em, white with the key phrase cyan (amber for money). Words rise in staggered
  ~0.055 s (opacity 0→1, y 26→0, `power2.out`), never typed; animate `opacity`, not `display`, so the line never shifts.
  One span per word from `data-text` at load, container `font-size:0` (or whitespace doubles the gaps). Holds 5 to 7 s.
- **5. Punchline chip.** `rgba(17,17,17,.45)` glass, blur 18 px, radius 16, 64 to 76 px/700, the emphasis word solid
  magenta, bottom-centre 80 px up.
- **12. Key-word highlight (long form only).** A navy `#0005EE` block behind a word as you say it, white text, a glow;
  two or three words, never a sentence (word-by-word captions are for Shorts). ~78 px/700, bottom-centre, radius 14.
- **16. Shimmer sweep.** A cyan band crosses a hero line (`background-position` on a `background-clip:text` gradient),
  two passes of ~1.5 s; set the pre-sweep position inline or the words stay unpainted until the sweep.
- **29. Equation\*.** A glass strip bottom-centre (or `top`), 76 px terms rising on their words, `+` and `=` white at
  .6, the result cyan (`"em"`) or magenta (`"pay"`). Laid out from frame one so it never shifts; it takes the lower
  line's slot, never both.
- **41. Pills around the head.** Two to six glass pills (42 px icon + label, 88 px tall), each on its word: `sides`
  (alternating columns from `top` 290, clear of your face), `left`, `right` or `row` (bottom centre). `tone: "cyan"` for
  the one that matters, `"amber"` + `"mark": "x"` for a risk or a wrong answer. One to three words each; hidden until its
  word (glass that has not arrived blurs the footage).

### Cards and lists

Every light glass card uses one recipe:

```css
background: rgba(255,255,255,.18); backdrop-filter: blur(30px) saturate(1.25);
border: 3px solid rgba(255,255,255,.58); border-radius: 26px; box-shadow: 0 24px 80px rgba(0,0,0,.38);
```

- **3a. Glass card.** 600 px, monochrome (colour lives in the lower line): eyebrow 30 px/700 white at .92, items 64 to
  72 px/700 with white dots and no sub-text (each item stands alone: "Invite teammates", not "Invite feature" plus an
  explainer). Items start `display:none` and appear on their word, so the card grows with the list. Every text gets a
  dark `text-shadow`: at 18% white the card follows the footage behind it (a cyan eyebrow measured 2.4:1).
- **3b. Extended-left bullets.** `#video-wrap` pushes to scale 1.18, x 150 (0.75 s `power2.inOut`, origin `50% 0%`;
  back in 0.65 s), and the 173 px overhang covers the shift. Scrim `linear-gradient(90deg, rgba(0,0,0,.97) 0%,
  rgba(0,0,0,.82) 34%, rgba(0,0,0,.45) 46%, transparent 60%)`; items 68 px/700 at left 96, top 318, cyan dots, no card.
- **3c. Glass pop-out\*.** The 3b move with a glass panel at left 72, top 230 (40 px title, 62 px items, 560 to 820 px
  wide) that leaves 0.7 s before the release so the camera returns onto clean footage. Never zoom from `0% 50%`: it
  crops the head.
- **Check marker\*.** A 44 px ring per item; a beat after the item lands it fills cyan and a dark check draws in 0.3 s.
  Done and to-do lists only, not plain nouns.
- **1. Big number behind the head.** Full digits (`$207,000,000`, never `$207M`) so your head covers about one glyph in
  twelve. White, solid, never a gradient: ~230 px/700 + `-webkit-text-stroke: 5px`, centred at `top:17%`, counting up
  with `toLocaleString('en-US')` (~1.4 s `power2.out`). Inside `#video-zoom`: footage → number → matte. Supporting copy
  in front at the bottom, ~94 px/700, the key phrase amber. (The linter's `text_occluded` is the point here.)
  - Short figures lose digits behind a centred head: write the unit inline (`$1,000 A MONTH`, 200 px, left-anchored at
    150), or put the figure beside the head (170 to 200 px, no matte, 60 px clear of its edge measured on a frame).
  - **Counter split around the head:** a 190 px white number right-anchored so its last digit tucks ~24 px behind the
    hair (the head measured from the matte), a 120 px cyan unit 8 px clear on the other side (a tucked "/" vanishes),
    `font-variant-numeric: tabular-nums`. The count runs from the money word to the END of the amount word
    (`power2.out`, a 6% bump, a cha-ching at 0.07 on the landing); the unit enters on its word. Matte only that window
    (`ffmpeg -ss -t` → `remove-background --quality best`, `data-media-start="0"`); mark the text
    `data-layout-allow-occlusion`.
  - **Pixelated logo teaser:** mosaic a 480 px logo to 5x5 (`scale=5:5,scale=480:480:flags=neighbor`; 4x4 for a
    letterform logo, which still reads at 5x5), revealed in steps: blocks 48, 24, 12, clean, 0.1 s each.
- **24. Stat tiles\*.** Numbers 112 px (92 stacked) counting up in full digits over 1.1 s, 34 px labels; `layout: "row"`
  (full frame, a 76 px title) or `"stack"` (a column at `tl`/`tr`); `em_tiles` turns a number cyan. Only numbers you can
  source get a tile.
- **25. Growth card\*.** 600 px at `tr`/`tl`: the number counting up cyan at 120 px, then bars rising (the last one cyan)
  and a glowing white line drawing over them to a dot (`count_at`, `bars_at`, `line_at`). Once per video at most.
  **25m** (`"morph": true`): the bars thin to stems (1.1 s, 0.16 s apart) while a smooth Catmull-Rom line draws through
  their tops in 1.4 s at an even speed, then an optional `badge`.

### Sections

- **9. Chapter tag.** A pill top-right: a live cyan dot + 34 px/700 label, light glass, held ~5 s then dropped (one that
  stayed 76 s read as static), on its own `data-track-index` (`overlapping_clips_same_track` otherwise). **9b** (`n`,
  `of`) adds N pips (done, now, next) for the first ~5 s of each segment; the viewer sees the slots fill.
- **9c. Slot wall\*.** A glass strip top centre, one 264x74 slot per part: empty, dashed and numbered in the hook
  (`filled: 0`); at each section the live slot fills cyan with its name on the word (`filled`, `now`, `fill_at`; spent
  slots .56); at the recap (`recap: true`) every slot lights and a cyan thread draws under them. It replaces the progress
  tag on a video with a spine; never both in one section.
- **40. Numbered deck.** Two to four 380x520 glass cards (italic number, 112 px icon, a 40 px title of five words or
  fewer) under a `head` ("3 PREDICTIONS"). `now: 1`: the row arrives, the camera pushes in on card 1 (1.5x, 1.1 s), the
  others drop to .38; `now: k` slides from card k-1 to k (1.0 s); `recap_at` pulls back to the row. It returns at every
  part boundary; never with a progress tag in one section.
- **35. Masked title\*.** A letter-spaced eyebrow ("PART 2"), the word as a thin white outline filling solid from the
  bottom (1.5 s `power3.inOut`, with a cyan edge line and a small handle), then a 64 px sub line rising from behind a
  mask. `size` 220 px by default. Never over your face.

### Tools, sites and screenshots

- **4a. Logo card.** Logo only, no name (you say it): a 380 px glass plate, the logo ~264 px tall (150 px was "quite a
  bit too small"), `tl` at a desk, `tr` on a tight shot, one pop. **21. Logo swap plate:** one plate; the first logo
  slides out (x → -50) on the second name and the second slides in (x 50 → 0), one pop on the swap.
- **34. Magnetic dock\*.** White 114 px app tiles in a glass dock; the oversized cursor walks to each tool on its word,
  the tile under it swells to 1.75 on a smooth falloff and a tooltip names it. One driver tween, so any frame renders
  the same.
- **4b. Site cutaway** (`site`). The homepage fills the frame ~3 s: a 62 px chrome bar, traffic-light dots, the bare
  domain in a 21 px URL pill, no copy, a drift 1.00 → 1.06. From a real `npx hyperframes capture` (optional `scroll`).
- **4c. 3D floating browser\*.** A full-page capture in a 1340x830 window rising in already turned (rotateY 27→15°,
  rotateX 16→7°, z -420→0, 1.0 s `power3.out`), then a slow camera orbit toward it while the page scrolls (`scroll`, in
  displayed px); one sheen; `near` picks the edge closer to camera, `callout` rings a spot. No flip: the tilt only settles.
- **4d. 3D screenshot fan\*.** Two or three images in depth (the middle 30 px forward at 1.05, the sides turned 16° and
  70 px back) rising 0.14 s apart, the fan orbiting rotateY 5 → -5; `focus` brings one forward (z 160, 1.12) while the
  rest drop to .4. `"frame"`: card (560x700, default), `"phone"` (330x700) or `"browser"` with `domains`, `fit`
  (`"width"` = a long page from its top, `"contain"` = a whole post) and `scroll` (`{index, at, by, dur}`).
- **Screenshots are browser windows showing the page, never crops of video frames.** Posts come from X's official embed
  (see "Sourcing assets"). When a live page blocks headless capture, read its text in the browser, rebuild the long page
  in HTML with the site's fonts, then `"<Chrome binary>" --headless=new --force-device-scale-factor=2
  --window-size=760,2600 --screenshot`.
- **31. Dashboard zoom\*.** Your real analytics screenshot (one 16:9 screen; give `"size": [w, h]`): at `find_at` the
  camera pushes to `focus` (a rect in image px, zoom capped at 3.2x) and cyan brackets find it; at `lift_at` the tile
  lifts into a 760x420 glass card with leader lines back, then the number counts up with a delta chip and a sparkline.
  Real numbers only, read off the screenshot.
- **32. Glass focus\*.** A 1200 px card of up to six rows, all out of focus (a static blur); a glass lens glides to each
  row in `stops` on its word (0.6 s `power3.inOut`), sharp inside at 54 px with the value cyan. The lens's copy moves the
  opposite way to line up, and its glass is nearly opaque so the row never doubles.
- **33. Search → results\*.** A pill opens from 520 to 1200 px (0.55 s); from `type_at` the query types at `cps` (16) with
  a cyan caret; two to four result rows drop in. `"sound": true` adds typing for exactly the typing time.

### Explainers (full frame)

Every full-frame scene sits on an ambient three-radial brand wash plus a 96 px grid at .28, never flat black.

- **6. Flow diagram.** A rail 1840 px wide at left 40: N nodes of 320 px, 56 px gaps, a 44 px arrow centred in each
  (five nodes: lefts 0/376/752/1128/1504, arrows 326/702/1078/1454; recompute for another N). A node: a cyan number
  badge, a hand-drawn SVG glyph, a 30 px/700 two-line title, chips for specifics. One beat per spoken step (~6.4 s
  apart): the shaft draws (scaleX 0→1, origin `0% 50%`), the head fades, the node lands (y 34→0, scale .965→1), then a
  44 px detail line under the rail. Cyan for mechanical steps, amber for urgency, a magenta payoff banner once the rail
  dims to .5. No `drawSVG` (not in `gsap.min.js`).
- **7. Ascending staircase** ("therefore" where the flow says "then"). Treads 300x200, each +356 px right and -112 px up
  (lefts 60/416/772/1128/1484, tops 670/558/446/334/222), fixed height so the risers meet them. Risers span only the gap,
  (L+300, T+100) → (L+356, T-12), drawn with a dash sweep (`getTotalLength()`, `strokeDashoffset`). Treads arrive from
  below-left, the previous drops to .42, all return to .85 at the end; the last magenta, the rest cyan.
- **8. Funnel.** SVG polygons, not `clip-path` (borders do not follow it): bands 180 px tall, 14 px apart, narrowing 90 px
  a side: `200,280 920,280 830,460 290,460` / `290,474 830,474 740,654 380,654` / `380,668 740,668 660,848 460,848`.
  Cyan (reach) → amber (warming) → magenta (money); metrics count up inside the bands, text at left 1010. Every metric box
  shares one `left` on the centre axis (following the taper put boxes 45 and 90 px off). Done stages dim (band .5, panel
  .66, never lower or contrast fails).
- **27. Pipeline\*.** Three to five 290 px glass nodes; each lands on its word as a cyan light runs the connector, lit
  cyan while the previous settles white; `payoff: true` lands magenta. The fast version of 6.
- **28. Hub\*.** The idea in a 300 px glass circle with a cyan ring closing (`ring_at`), two to six parts arriving at the
  ends of spokes; `resolve_at` dims them to .56 and lights the centre ("all of that is really this").
- **30. Flowing paths\*.** An input pill left, two to four outputs, an optional result right, joined by S-curves and dim
  (.42) from frame one. A packet of light runs each path (0.9 s) and the pill lights on its word; at `result.at` light
  runs from every output 0.14 s apart and the result lands magenta; a second wave keeps it moving (`"repeat": false`).
- **38. Exploded layers\*.** One flat card tilts (rotateY -30, rotateX 16) at `split_at` and separates into two to four
  layers in depth (1.4 s, 0.22 s apart), labels on their layers, then a slow orbit.
- **26. Bar comparison\*.** A 76 px title, two to four rows of label (46 px) and bar, each on its word, growing 0.5 to
  0.9 s; the longest stops at 80% of the track; your row (`hi`) cyan with a glow, the rest white.
- **39. World camera.** One canvas in home-frame px (1920x1080 = zoom 1; nodes may sit off screen, or on a ring with
  `"polar": [cx, cy, r, deg]`). Node kinds: `card` (300 px: number, icon, 42 px label, 26 px sub), `pill`, `orb`, `hex`,
  `stat` (a 118 px number counting up + a cyan bar; `to` moves both on after the first count), `text`, `img`. Each node
  arrives on its word (glass stays hidden until then), can `lit` (cyan or `lit_color`), `dim` (.56; spent .33) and take
  amber `alerts`; `links` draw in 0.5 s and `run` sends a light along; `rings`, `window`, `dock` add circles, a window, a
  row of logos. `cam` = `[t, x, y, zoom, dur]`, one gesture each (`power2.inOut`, 1.0 s); a move that starts before the
  last ends fails the build. Open close on the thing you name (zoom 1.5 to 1.8), pull back to 0.8 to 1.0 as you say what
  it connects to, push to the next. Text 32 px or more at the zoom it is read at (the composer warns over 3.2).

### Cutaways and pages

- **18. Article cutaway with highlighter.** Full screen while you read from a page, cut in where your eyes drop (in a
  cut, the jump cut). Rebuild the page in HTML (real headline, byline, date, hero image, the site's own font): headless
  Chrome hits consent walls, and a rebuild makes the highlighter exact. Headline words get an amber block each
  (`rgba(255,185,4,.66)`, scaleX 0→1) stroked in one pass as the page appears (0.14 s a word, 0.035 s stagger), then a
  zoom into the headline for the rest of the read (1.0 → 1.42, `power1.inOut`), clipped under the 62 px chrome bar.
  Hard cuts in and out.
- **18b. Doc read.** The page rebuilt from the real kicker, title, date and paragraphs (a mark that is not verbatim fails
  the build; `"theme": "dark"` for dark pages, which get an amber underline). 0.35 s before each mark's word the camera
  glides to it at `zoom` (1.3), and on the word it is stroked in one pass; `focus` blurs the rest (a static copy; only
  opacity moves). Highlight on "highlight", zoom on "zoom": a mark can take its own `"zoom"` and `"move": false`.
- **19. Photo card.** Light glass 420 px wide, top-left: a 372 px square photo (radius 16), name 40 px/700, role 26 px.
  In on the name (x -40 → 0), gone ~1.8 s later.
- **20. Full-frame video cutaway** (hand-built). Your own screen recording first, public-domain archive for a metaphor
  second, then nothing. The `<video>` is a direct child of the root (`class="cutaway-video clip"`, its own timing
  attributes, `muted`, `z-index:20`); inside a timed wrapper it fails lint and shows the wrong frames.
  `object-fit:contain` does not paint its letterbox: `pad` to 16:9 with ffmpeg. Crop recordings to the window, re-encode
  like the footage (30 fps, dense keyframes, no audio), hard cuts, drift 1.0 → 1.04, 2 to 4 s; it hides a jump cut.
- **20b. Before/after wipe.** Two layers in a 1600x900 plate; the opaque after layer goes from `clip-path: inset(0px
  1600px 0px 0px)` to `inset(0px 0px 0px 0px)` (px on both ends so it interpolates) while a 5 px cyan line rides the
  edge, 0.65 to 1.1 s on the verb.
- **20c. Clip** (`clip`). Format 20 in the composer (muted, root level, z 20, drift, hard cuts, `anchor` on your words)
  for screen, archive, stock and AI B-roll conformed by `broll-conform.py`; an optional `label` or checklist (`items`).
- **37. Image reveal\*.** An image behind seven dark slats that close to their centres on `reveal_at` (1.1 s, 0.12 s
  apart), then a push 1.00 → 1.06; `"close": true` shuts them before the cut back. Stills only.
- **13. Prompt window.** A dark window, the prompt typing in as you read it (a cyan mic glyph and "Dictated" if you
  dictate). Characters start `display:none`, never `opacity:0`, or the caret parks at the finished width.
- **42. Chat.** Messages one by one: yours (`me`) cyan with dark text, theirs (`them`) white. `float` (up to five bubbles
  beside you), `window` (a dark app window that grows with the thread and scrolls once full) or `phone`. No anchor unless
  you read a message out. A client message is your example or a real one with permission, never made up.
- **36. Button → player\*.** A glass "Watch this next" pill grows into a 600x444 player at `morph_at` (1.1 s), the play
  icon travelling into the thumbnail; the real thumbnail, title and length fill in and the scrubber moves.
- **Thumbnail grid** (`grid`). Six of your thumbnails in a 3x2 grid; the oversized cursor clicks one (`click_index`,
  `click_at`) and the rest dim. Get them with `yt-dlp --flat-playlist -j <channel url>` and
  `https://i.ytimg.com/vi/<id>/maxresdefault.jpg`.
- **Coded scenes** (`scene`, no stock): `money` (amber $ chips drop on the word, never a digit), `catalog` (frames fill,
  one shine), `room` (furniture drops into a line-art room), `plate` (a phone with a plate: sweep, sparkles, steam),
  `profile` (the avatar gets its ring on "headshot"); `steps` time each kind, `label*` keys add the caption.

### Accents and asks

- **10. Success stamp.** A cyan circle with a dark check, a 62 px/700 label, glass with a cyan border, scale .86 → 1
  `back.out(2)` ~0.45 s (the house's one overshoot), bottom-left, ~5 s, on your own word ("boom", "it worked"), never on
  a read of the screen.
- **11. Description pointer** (`pointer`). A glass bar at bottom 34, "Everything is linked in the description" (cyan on
  the link phrase), three chevrons cascading beneath (0.14 s stagger, ~0.78 s cycle) on a finite loop, never `repeat:-1`.
- **14. Subscribe bar.** A pill glass bar: your channel mark in a dark avatar circle, the name 42 px/700, a 22 px/500
  tagline, a YouTube-red `#FF0000` pill 30 px/700 pulsing a finite 3 times (scale 1.08). Away from your head, under
  ~720 px wide.
- **17. Vignette + grain** (`vignette`). Radial darkening and fine grain: a beat, not a look (the pause after a dad joke).
- **23. Tutorial layout (not built yet).** The screen as a rounded plate, your face in a rounded crop bottom-right (a
  360x540 corner, right and bottom 48, radius 32; full to corner in 0.6 s `power3.inOut`, 0.3 s before the word),
  switched with `tl.set`, never a class toggle (not seek-safe).

### Rejected in the kit's own channel

These were rejected for the original creator's look. Two of them do **not** apply to this system: the paper drawer
("paper-and-tape dressing") and the whiteout ("flash cut") are wanted treatments here, built by `treatments.py`.

- Freeze-frame and paper-and-tape dressing; an outro or end card; a "Next video" pill at the end (the YouTube end screen
  does that job); payment or system notification banners.
- Typing with a trailing caret for lower lines; word-by-word highlighter pacing on an article (one stroke, then zoom).
- The flash cut on a return (two white blinks read as a mistake): for energy use the fast punch, or leave the cut naked.
- Dark blue `#0005EE` for highlighted words (it disappears on dark footage); magenta outside the chip and payoffs.
- Bounces, elastic type, spring stacks, particle logos, idle wobble; generic stock of a smiling founder at a laptop.

