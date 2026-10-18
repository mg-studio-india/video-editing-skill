# Brand prompts · 50 style blueprints

Each prompt applies one blueprint's editing system to **your** brand. Fill the BRAND TOKENS (colours, fonts, handle, logo) from the brand; every geometry, size and timing value stays as measured. Grade always comes from your own footage. To mix, take CAPTIONS from one prompt and OTHER TEXT from another. Sizes were solved for the fonts in `~/.agents/skills/video-pipeline/engine/assets/fonts`; if you swap a font, run the prompt's VERIFY step (`scripts/caption_probe.py`, expected values from `scripts/fit_font.py`) and adjust px until it passes.

## giant-keyword

_small lead words + one huge accent-coloured key word per phrase_

### B11 · podcast-clip · Hinglish · score 5

Interview recut with giant solid-accent key words, accent/second accent cut-out cards, and a 50/50 split montage swapping proof images every ~15 frames.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B11 (video-reference-match/references/blueprints/B11.json) to this brand.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: the solid {{ACCENT}} key word must stay >= 3:1 on the footage behind it, {{ACCENT_2}} headlines >= 4.5:1 on {{SURFACE}})
- {{TEXT}} lead captions - default #FFFFFF
- {{ACCENT}} giant key word - default purple #7404E6
- {{ACCENT_2}} card headlines + cut-out sticker outline - default lime #EFFA04 (statement-card text #F0F210)
- {{SURFACE}} flat card background - default purple #7D02FB
- {{CARD_BG}} end card - default white with a soft {{SURFACE}} radial glow
- {{FONT_DISPLAY}} key word + card headlines - default Inter 900 (Black)
- {{FONT_BODY}} lead captions - default Inter 600 (SemiBold)
- {{HANDLE}} - @handle on the end card ({{ACCENT}} bold)
- {{LOGO}} - profile photo / logo in the end-card circle

Canvas 1080x1920, 30 fps.

CAPTIONS
1. Latin script (Roman Hinglish for Hindi lines), as spoken; lead words sentence case, key word lowercase.
2. Lead line: 1-3 words, {{FONT_BODY}} 69-70 px, -0.01em, {{TEXT}}, no stroke/box, shadow 0 2px 8px rgba(0,0,0,.35). Each word fades in over 2 frames with ~1 % H upward drift as spoken. Alone: centred at ~49.5 % H.
3. Key word: ONE per sentence (the noun/verb that carries the idea), {{FONT_DISPLAY}} ~292 px, -0.03em, solid {{ACCENT}}, no shadow/stroke, centred, centre y 55-59 % (a 6-7-letter word fills ~78-86 % W). Entry: from ~40 % opacity and scale 0.85 -> 1.0 over 3 frames, 3-5 frames after the lead line, on or just before the spoken word. Hard cut out with the next caption.
4. Nested lockup: the lead line sits inside the key word's ascender band (overlapping the key's top by ~2 % H), over the longest run of x-height letters, aligned to that run's edge (right-aligned over a trailing run e.g. x 51.5-79.9 %, y 46.8-49.4 %; left-aligned over a leading run e.g. x 16.7-48.9 %, y 50.9-54.0 %).
5. Split shots: a single {{TEXT}} line centred on the divider (~50 % H), no key word.

OTHER TEXT / EDIT DEVICES
6. Hook: start mid-thought (first word within frame 1); first cut at frame ~19 to a cut-out headline card: solid {{SURFACE}} frame, {{ACCENT_2}} lowercase {{FONT_DISPLAY}} headline 'headline / here / words!' in 3 stacked lines top-left (x 10 %, y 7-33 %, ~6 % H per line, tight leading), subject cut out in greyscale with a ~8 px {{ACCENT_2}} sticker outline bottom-right overlapping the last line; ~40 frames. Reuse the card to introduce each new example.
7. Example montage: 50/50 split, example images in the top half swapping every 12-18 frames, one per 2-3-word caption chunk, speaker held in the bottom half (~15 images over two examples).
8. Statement card (~60 frames): solid {{SURFACE}}, {{ACCENT_2}} bold 'Headline here' in 3 centred lines at 42-55 % H, ~3.4 % H per line.
9. Final line: ~120 % tighter crop on the speaker with the last giant key word.
10. Source credit (if re-cutting someone's footage): platform icon + '/ Source name', white, ~1.3 % H, top-left at y 4 %.
11. End card (~75 frames): {{CARD_BG}}, {{LOGO}} circle on an {{ACCENT}} disc (~50 % W) at y 25-50 %, {{HANDLE}} below, two lavender pill buttons 'Like' / 'Share' at ~73 % H; Like presses and pops.

GRADE: Grade from the user's footage (video-style / grade.py); target look: high-contrast, saturated, warm, natural skin; graphics fully saturated.
SOUND: voice at about -14 LUFS; soft tick/pop on montage swaps; click + pop on the Like button; low bed under the end card.

VERIFY before rendering (px values were render-verified with Inter; if the brand font differs, adjust px until the numbers match):
a) Render test frames over a dark area: "a particular" ({{FONT_BODY}} 69 px {{TEXT}}) and "quality" / "things" ({{FONT_DISPLAY}} 292 px {{ACCENT}}).
b) Measure: python video-reference-match/scripts/caption_probe.py <test render or snapshot> --out <dir> --at <t> --box 0.1,0.44,0.9,0.66 --ink "{{TEXT}}:60,{{ACCENT}}:90" (tighten --box per line).
c) Required: "a particular" ink 3.2 % +-0.5 of H and 32.2 % +-2 of W; "quality" 14.61 % +-0.5 and 85.4 % +-2; "things" 14.69 % +-0.5 and 78.2 % +-2. For any other key word compute the expected ink with python video-reference-match/scripts/fit_font.py --font "<{{FONT_DISPLAY}}>" --word "<word>" at 292 px.
```

### B20 · podcast-clip · English · score 4

Two-person podcast clip cut on speaker changes, with stacked word-by-word captions: small white lead words over one giant glowing accent UPPERCASE keyword on the chest.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B20 (video-reference-match/references/blueprints/B20.json) to this brand.
Canvas 1080x1920, 30 fps. All positions are % of frame; px are at 1080x1920.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{ACCENT}} must stay >= 3:1 on the dark set and visibly brighter than skin; {{ACCENT_2}} is a lighter tint of {{ACCENT}} for the sheen)
- {{TEXT}}      lead / trailing words                    default #FFFFFF
- {{ACCENT}}    keyword fill and glow                    default #9EC43A (lime)
- {{ACCENT_2}}  diagonal sheen band across the keyword   default #B6D372
- {{SURFACE}}   black band below the picture / set       default #000000
- {{CARD_BG}}   none                                     default none
- {{FONT_DISPLAY}} keyword                               default Inter 900 (black-weight neo-grotesque, wide caps)
- {{FONT_BODY}}    lead / trailing words                 default Inter 700
- {{HANDLE}}    not shown (optional: add a guest name lower third only if the brand needs it)
- {{LOGO}}      not shown

CAPTIONS
1. English as spoken. Lead words in sentence case; the keyword in UPPERCASE. Drop commas, question marks and quotes; keep apostrophes.
2. Per phrase: 1-3 small lead words, then ONE keyword (the topic word: a strong noun or verb, about one every 60-90 frames), then 0-2 small trailing words. Max 3 lines. Phrases without a strong keyword show only the small white line (at ~60-62 % height).
3. Lead/trailing words: {{FONT_BODY}} at 54 px, tracking +0.05em, {{TEXT}}, no stroke, no box, faint soft glow.
4. Keyword: {{FONT_DISPLAY}} at 114 px (~2.1x the lead), tracking +0.03em, {{ACCENT}} with a lighter diagonal {{ACCENT_2}} sheen band across the middle letters, soft glow 0 0 40px of {{ACCENT}} at 35 % opacity, no stroke, no box.
5. Layout: stack tightly. The lead line sits directly on the keyword's cap height, left-aligned with its left edge; the trailing line goes under the keyword, indented (right-aligned to it when it fits). Keyword centre at 63.7 % of height (y ~1223 px); block roughly centred (x 42-50 %), nudged over the speaker's chest so it never covers the face.
6. Animation: build word by word; each word (small or keyword) hard-cuts in at full size and opacity on the audible word; placed words never move. No pop, scale, fade or colour sweep. The whole stack hard-cuts out when the next phrase starts or on a speaker cut. Leave pure reaction shots uncaptioned.

OTHER TEXT
7. None: no title, name lower thirds or logo bug. If the source is not 9:16, place the picture in the top ~83 % with {{SURFACE}} below.

EDIT DEVICES
8. Open mid-conversation on a question (first word in the first ~2 frames) and cut to the other person's laughing reaction within ~50 frames. Cut only on speaker change or reaction (median shot ~70 frames, J-leads, never mid-sentence). First shot a wider MS, later shots tighter MCUs; hold the quotable payoff in the longest shot; no CTA so it loops.

GRADE
9. Grade from the user's footage (video-style / grade.py); target look: crushed-black set, faces pop, cool teal rim light, warm skin; no heavy sharpening.

AUDIO
10. Low music bed under the conversation (optional); no SFX. Master to about -14.1 LUFS, true peak <= -1 dBTP.

VERIFY before rendering
a) Render a test frame with the stack "KEY WORD / MEET / with you" and one with "LOVE" as the keyword, over a dark area, and measure:
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.05,0.55,0.95,0.72 --ink "{{ACCENT}}:30,{{TEXT}}:60"
   Required at the default fonts: "MEET" ink 4.38 % ±0.5 of height and 30.6 % ±2 of width; "LOVE" 4.53 % and 28.5 % ±2; "with you" 2.66 % ±0.5 and 20.8 % ±2; keyword centre y 63.7 % ±0.5. With brand fonts, compute the expected ink with video-reference-match/scripts/fit_font.py ({{FONT_DISPLAY}} 114 px +0.03em; {{FONT_BODY}} 54 px +0.05em) and match within ±0.5 % H.
```

### B29 · podcast-clip · Hinglish · score 4

Two-camera podcast banter cut on every turn with reaction inserts, letterboxed B&W photo cutaways captioned in the bar, accent cut-out swap gag.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B29 (video-reference-match/references/blueprints/B29.json) to this brand.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: the solid {{ACCENT}} key word must stay >= 3:1 on the footage, {{ACCENT_2}} headline >= 4.5:1 on {{SURFACE}})
- {{TEXT}} captions - default #FFFFFF
- {{ACCENT}} giant payoff word - default purple #7B02FB
- {{ACCENT_2}} card headline + cut-out sticker outline - default yellow #F0F80A
- {{SURFACE}} flat card - default purple #7D00FE
- {{CARD_BG}} end card - default #FDFBFE with a soft lavender #E3C6F5 radial edge glow
- {{FONT_DISPLAY}} key word + card headline - default Inter 900 (Black)
- {{FONT_BODY}} captions - default Inter 600 (SemiBold)
- {{HANDLE}} - @handle on the end card ({{ACCENT}} bold, ink 3.2 % H)
- {{LOGO}} - profile photo / logo in the end-card circle

Canvas 1080x1920, 30 fps.

EDIT
1. Two-camera podcast: cut on every speaker change (J-lead into answers) and insert 9-15-frame listener reactions; target median shot ~38 frames.
2. Hook: first cut at ~6 % of runtime to a {{SURFACE}} card: {{ACCENT_2}} {{FONT_DISPLAY}} 2-line headline 'Headline here / second line!' left-aligned at x 5.6 % (y 13.1-19.6 % and 21.4-27.7 %, ~6.4 % H ink per line); below it a greyscale cut-out of person A with a ~8 px {{ACCENT_2}} sticker outline, hard-swapped to person B ~20 frames in (comparison gag); ~30 frames total.
3. Proof cutaways: B&W photos / archival clips letterboxed on black, ~12 frames per photo, one per 1-2-word caption chunk; the caption moves into the black bar.
4. One ~130 % punch-in on a one-word reaction (~9 frames), then cut to the listener's nod (~15 frames).

CAPTIONS
5. Latin script (Roman Hinglish as spoken), sentence case, punctuation kept; 1-3 words.
6. Line: {{FONT_BODY}} 58 px, -0.01em, {{TEXT}}, no stroke/box, shadow 0 2px 8px rgba(0,0,0,.35), one centred line, centre y 67 %. Words fade in over ~2 frames with a slight upward drift as spoken; hard cut out, 1-frame gap before the next caption.
7. Payoff word (rare, max one per sentence): {{FONT_DISPLAY}} ~274 px, -0.03em, solid {{ACCENT}}, centred, centre y 63.1 % (ink ~57.8-68.4 %); the lead words in {{FONT_BODY}} 68 px nested left-aligned over its first letters (x ~23-55 %, baseline ~57 %, overlapping the key's top). Key fades from 40 % and scales 0.85 -> 1 over 3 frames, ~2 frames after the last lead word.
8. Letterbox cutaways: the same caption centred in the top black bar at y 27.5 % (2-word line ink ~2.34 % H), or in the bar under the image.

OTHER TEXT
9. Source credit if re-cutting footage: platform icon + '/ Source name', white, top-left y 4.3 %.
10. End card (~66 frames, the last spoken word can sit on it): {{CARD_BG}}, {{LOGO}} circle on an {{ACCENT}} disc at y 24-46 %, x 24-75 %, {{HANDLE}} at y 54.3-57.4 %, two lavender pill buttons at y 69.5-75.7 % with labels at ~78.8 %; Like presses and pops.

GRADE: Grade from the user's footage (video-style / grade.py); target look: high-contrast, natural-saturation, warm natural skin; cutaways desaturated to B&W.
SOUND: two voices at about -14 LUFS (keep some dynamics); optional pop on the cut-out swap, tick on photo swaps, click + pop on the Like button.

VERIFY before rendering (px values were render-verified with Inter; if the brand font differs, adjust px until the numbers match):
a) Render test frames over a dark area: "Have you sat" ({{FONT_BODY}} 58 px), "most senior" ({{FONT_BODY}} 68 px) and "person" ({{FONT_DISPLAY}} 274 px {{ACCENT}}).
b) Measure: python video-reference-match/scripts/caption_probe.py <test render or snapshot> --out <dir> --at <t> --box 0.25,0.64,0.75,0.695 --ink "{{TEXT}}:60" (line); --box 0.2,0.535,0.58,0.574 --ink "{{TEXT}}:55" (lead); --box 0.05,0.565,0.95,0.7 --ink "{{ACCENT}}:90" (key).
c) Required: "Have you sat" ink 2.81 % +-0.5 of H and 31.1 % +-2 of W; "most senior" 2.5 % +-0.5 and 32.4 % +-2; "person" 10.62 % +-0.5 and 80.1 % +-2. For other words compute the expected ink with python video-reference-match/scripts/fit_font.py --font "<font>" --word "<word>" at the px above.
```

### B30 · b-roll-voiceover · English · score 3

B-roll course ad: one shot and one accent key word per module, lead words justified above.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B30 (video-reference-match/references/blueprints/B30.json) to this brand.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship — text and accent must stay >= 4.5:1 / >= 3:1 against what sits behind them on the footage):
- {{TEXT}}      default #FFFFFF (lead words, CTA heading)
- {{ACCENT}}    default #F2D805 (key words, bullets, phone number)
- {{ACCENT_2}}  default #CF9C5E (end-card descriptor box)
- {{SURFACE}}   default #000000 (end card / bottom gradient)
- {{CARD_BG}}   default #B18B63 (end-card headings)
- {{FONT_DISPLAY}} default Poppins 700 (Montserrat ExtraBold is closer)
- {{FONT_BODY}}    default Poppins 700; Playfair Display 700 for the CTA heading
- {{HANDLE}}    default @handle
- {{LOGO}}      default the brand's logo file (transparent PNG/SVG)
{{ACCENT}} must stay >= 3:1 on the footage even above the gradient; a dark brand colour needs a lighter tint for the key words.
Canvas 1080x1920, 30 fps.

CAPTIONS (keyword callouts, not full transcripts)
1. One callout per sentence, only on shots where the sentence has a clear topic phrase: 1-3 small lowercase lead-in words as spoken + ONE key word or 2-word phrase in Title Case (placeholder 'lead words here' + 'KEY WORD'). No punctuation, no emoji.
2. Key: {{FONT_DISPLAY}} at 128 px (fixed size, never fit-to-width; a 2-word phrase may run to ~87 % W), {{ACCENT}}, tracking -0.01 em, slight dark shadow 0 2px 6px rgba(0,0,0,.4), no stroke / box, centred at ~68 % H. Two-word phrases may stack as two lines, line 1 right-aligned to line 2.
3. Lead-in: {{FONT_DISPLAY}} at 57 px, {{TEXT}}, slight shadow, directly above the key word and JUSTIFIED to the key's width (first word flush left, last flush right, extra word spacing), centre ~62.3 % H.
4. Top variant (once, for the big claim): key phrase at the top (centre 19.4 %), small {{TEXT}} words UNDER it at 24.6 %, first flush left, last flush right.
5. Background: dark bottom gradient ({{SURFACE}} -> transparent from the bottom edge to ~55 % H) under the lower callouts.
6. Animation: each word appears as it is spoken — fade + blur + slight scale-down / upward settle over 3-4 frames; lead words first, key word last. Callouts hard-cut out with their shot. No idle motion.

OTHER TEXT (only where the script has a matching beat)
7. Bullet list (3 benefits): left-aligned {{ACCENT}} lines with ring bullets, bold geometric ~94 px, baseline pitch 5.5 % H, block x 12.8-89 %, y 62-76 %.
8. {{LOGO}} badge pop (~15-frame scale-in) at ~70 % H when the brand is first named; optional money-rain overlay (~75 frames) on a revenue / earnings line.
9. CTA: 'CONTACT US:' in {{TEXT}} bold serif caps (Playfair Display 700, 64 px, +0.02 em) centred at 65.6 %, phone number(s) in {{ACCENT}} serif below at 69.8 % (~77 % W).
10. End card (last ~114 frames): {{SURFACE}}; {{LOGO}} + brand name at 28-42 %; {{ACCENT_2}} box with white caps descriptor lines at 45-50 %; 'contact' / 'location' headings in {{CARD_BG}} caps with white caps details below (54-71 %).
11. Edit: B-roll for ~96 % of runtime, median ~73 frames per shot; in list sections one 50-70 frame shot per item; VO leads cuts (J-cuts); two light-leak flashes in the hook; screen footage gets slow push-ins. Limit the master to -1 dBTP.

GRADE
Grade from the user's footage (video-style / grade.py); target look: warm, saturated, golden light, high contrast, dark bottom vignette for text.

VERIFY before rendering
a) Render the lead word 'just' (in a lead line 'lead just here') over 'KEY WORD', and 'CONTACT US:', then measure:
   python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.12,0.655,0.88,0.71 --ink "{{ACCENT}}:60"
   python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.42,0.6,0.56,0.655 --ink "{{TEXT}}:40"
   python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.2,0.63,0.8,0.68 --ink "{{TEXT}}:50"
   Expected (±0.5 % H, ±2 % W): 'just' ~2.8 % H (estimated) / 11.7 % W; 'CONTACT US:' 2.66 % H / 39.6 % W at 64 px Playfair 700.
b) Key word: python3 video-reference-match/scripts/fit_font.py --font "Poppins 700" --word "<Key word without descenders>" --ink 5.16 --tracking -0.01 -> ~122-128 px with Poppins (128 px is the width-balanced value; Montserrat ExtraBold matches better). Lead words: --font "Poppins 700" --word "just" --width 11.7 -> ~57-66 px. Measure white over a dark area. (fit_font.py needs a target: --ink and/or --width; it returns the px that reproduces that ink for YOUR word plus the width it will read at that px. Requires Pillow.)
c) Positions within ±1 % H: lead centre 62.3 %, key centre 68 %, top-variant key 19.4 %, CTA heading 65.6 %, number line 69.8 %.
```

## two-tier-script

_two typographic tiers (caps line + script / handwritten completion)_

### B02 · podcast-clip · Hinglish · score 4

Podcast holds carried by word-by-word caps captions completed by a glowing accent script line.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B02 (video-reference-match/references/blueprints/B02.json) to this brand.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship — text and accent must stay >= 4.5:1 / >= 3:1 against what sits behind them on the footage):
- {{TEXT}}      default #EEE6E2 (warm white caps line; #FFFFFF before a warm grade)
- {{ACCENT}}    default #E5EB7A (pale lime script line + glow)
- {{ACCENT_2}}  default none
- {{SURFACE}}   default none (captions sit on footage)
- {{CARD_BG}}   default none
- {{FONT_DISPLAY}} default Poppins 800 (caps line)
- {{FONT_BODY}}    default a monoline connected script, e.g. Sacramento (completion line)
- {{HANDLE}}    default @handle
- {{LOGO}}      default the brand's logo file (transparent PNG/SVG)
The script line is thin: keep {{ACCENT}} light enough for >= 3:1 on the clothing behind it and keep its glow; if the brand accent is dark, use a light tint of it.
Canvas 1080x1920, 30 fps. The reference picture is 9:10 placed full-width (1080x1200 at y 360-1560); if your footage fills 9:16, keep the captions on the lower chest just below the mic (69 % / 74 % of the picture height).

CAPTIONS
1. Roman script as spoken (transliterate Devanagari). Split each phrase into two tiers: line 1 = first 1-5 words in UPPERCASE; line 2 = the completion (1-5 words) in lowercase script (placeholder 'LEAD WORDS' / 'key word here'). No punctuation, no emoji.
2. Line 1: {{FONT_DISPLAY}} at 57 px, tracking +0.04 em, {{TEXT}}, soft dark drop shadow 0 2px 6px rgba(0,0,0,.45), no stroke / box. Centred; ink centre at 62.0 % H. Max line width ~75 % W.
3. Line 2: {{FONT_BODY}}, lowercase, {{ACCENT}}, soft outer glow 0 0 8px {{ACCENT}} at ~60 % opacity, centred with its centre at 64.7 % H so the tall ascenders overlap the bottom of line 1. Start at ~66 px.
4. Reveal: lay out the full two-tier phrase first, then reveal it word by word IN PLACE. Each word fades 0->100 % over 5-8 frames (script words 6-10), no scale / slide, starting 2-8 frames after the word is spoken. Line 2 begins after line 1 is complete.
5. Exit: the whole block hard-cuts out at the phrase end; 2-3 empty frames before the next block. No idle motion.

OTHER TEXT
6. None: no titles, lower-thirds, {{LOGO}}, watermark or end card.
7. Edit: open with a ~15-frame zoom-blur into the first MCU with the first word on frame 1; hold 7-8 s shots; L-trail cut to a second angle mid-way; soft cut to a ~115 % crop for the final line.

GRADE
Grade from the user's footage (video-style / grade.py); target look: warm, creamy, high-key with bloom/glow and crisp sharpening, natural saturation.

VERIFY before rendering
a) Render 'FINANCIALLY' on line 1 and a two-word placeholder 'key word' on line 2, then measure:
   python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.25,0.59,0.75,0.635 --ink "{{TEXT}}:45"
   python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.15,0.625,0.85,0.68 --ink "{{ACCENT}}:60"
   Expected (±0.5 % H, ±2 % W): 'FINANCIALLY' ink 2.11 % H / 37.6 % W at 57 px Poppins 800 +0.04 em. Script line: ink ~3.05 % H for a two-word lowercase line; adjust px from 66 until it matches.
b) Any other caps word / font: python3 video-reference-match/scripts/fit_font.py --font "Poppins 800" --word "<WORD>" --upper --ink 2.11 --tracking 0.04 -> ~57 px. Measure over dark clothing, not the light set. (fit_font.py needs a target: --ink and/or --width; it returns the px that reproduces that ink for YOUR word plus the width it will read at that px. Requires Pillow.)
c) Positions within ±1 % H: line 1 centre 62.0 %, line 2 centre 64.7 %.
```

## stacked-kinetic

_phrases stacked as kinetic typography_

### B08 · podcast-clip · English · score 4

Slow two-camera interview carried by lower-left stacked word blocks: thin light words plus one heavy accent glowing key word; B&W cold open.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B08 (video-reference-match/references/blueprints/B08.json) to this brand.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: the {{ACCENT}} key word must stay >= 3:1 on the footage, with its dark glow behind it; thin {{TEXT}} words need a dark area behind them)
- {{TEXT}} light caption words - default #FFFFFF
- {{ACCENT}} key word - default blue #2E88FE, with a dark glow tinted from it (default indigo rgba(30,25,120,.6))
- {{ACCENT_2}} one-off key word for 'future / change' moments - default coral #FE664A
- {{SURFACE}} - none (footage)
- {{CARD_BG}} end card - default near-white #F6FDFF
- {{FONT_DISPLAY}} key word - default Poppins 800 (Plus Jakarta Sans ExtraBold is closer)
- {{FONT_BODY}} light words - default Inter 300 (Plus Jakarta Sans Light is closer)
- {{HANDLE}} - @handle (not shown in this blueprint; optional on the end card)
- {{LOGO}} - animated circular logo on the end card (~45 % W)

Canvas 1080x1920, 25 fps.

EDIT
1. Cold open (~100 frames): lift the strongest line from later in the interview, grade it black-and-white, no intro (first word within ~3 frames); then a ~12-frame pink-to-orange gradient flash into the colour question. Replay the line in colour where it really occurs.
2. Let takes run long (median shot ~200 frames); tighten slowly inside a long take (MCU -> CU, ~100 -> 125 %); break any take longer than ~375 frames with an L-cut to the listener. Soft dissolves (~8-12 frames) between speakers; tighten pauses under ~10 frames.
3. When the speaker names a concrete thing, composite matching footage into the bottom ~40 % of frame under the caption block for ~100 frames instead of cutting away.
4. End: ~75 frames {{CARD_BG}} card with {{LOGO}} animated, centred at 45-55 % H, no text.

CAPTIONS
5. Latin script, lowercase as spoken (capital only at the start of a thought), no punctuation, no emoji.
6. Blocks of 2-7 words over 2-4 stacked lines, left-aligned at x 12-13 %, ragged right, max width 81 %, first line top at y 65-66 %, band y 62-85 %; very tight leading (ascenders touch the descenders above); a short trailing line may indent under the end of the line above. Never cover the face (faces above 55 % H).
7. Light words: {{FONT_BODY}} 300, {{TEXT}}, no shadow/stroke/box; connective / first line 132 px, secondary lines 87 px. Each word fades in over 2 frames (half, then full) on its spoken word; no drift/scale.
8. Key word (0-1 per block, the word that carries the idea): {{FONT_DISPLAY}} 800, -0.02em, {{ACCENT}}, ~192 px on the main speaker (shrink long words to stay <= 81 % W), ~133 px on the host / listener; dark glow 0 12px 60px; hard-cut in, full size, 2-3 frames BEFORE the spoken word. In the B&W cold open it reads grey (#8C8C8C); use {{ACCENT_2}} once for a 'future / change' word.
9. Block grows downward line by line, existing lines never move; the whole block hard-cuts out ~3 frames before the next phrase.

GRADE: Grade from the user's footage (video-style / grade.py); target look: high-contrast, natural-saturation, neutral-warm skin, shallow depth of field; B&W for the cold open only.
SOUND: voice at about -14 LUFS over a low bed; whoosh/shimmer on the colour flash; no cut hits.

VERIFY before rendering (px values were render-verified with Inter / Poppins; with the closer Plus Jakarta Sans, re-fit px until the numbers match):
a) Render test frames over a dark area: "because" ({{FONT_BODY}} 300, 132 px), "online" and "frankly" ({{FONT_DISPLAY}} 800, ~192 px, {{ACCENT}}), "digital" ({{FONT_DISPLAY}} 800, 133 px), and "KEY WORD" in {{FONT_BODY}} 300 at 87 px.
b) Measure: python video-reference-match/scripts/caption_probe.py <test render or snapshot> --out <dir> --at <t> --box 0.1,0.62,0.95,0.86 --ink "{{TEXT}}:60,{{ACCENT}}:80" (tighten --box per line).
c) Required: "because" ink 5.47 % +-0.5 of H and 41.7 % +-2 of W; "online" 8.83 % +-0.5 and 53.8 % +-2; "frankly" 11.64 % +-0.5 and 60.3 % +-2 (Poppins misses one axis - prefer the closer face); "digital" 7.97 % +-0.5 and 37.6 % +-2. For the 87 px tier compute expected ink with python video-reference-match/scripts/fit_font.py --font "<{{FONT_BODY}}>" --word "KEY WORD".
```

### B40 · mixed · English · score 4

Keyed speaker over swapped backgrounds, zig-zag stacked captions with one gradient key line, illustrated phrase cards every few seconds.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B40 (video-reference-match/references/blueprints/B40.json) to this brand.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: white lines and the key gradient must stay >= 3:1 on the footage, card text >= 4.5:1 on {{SURFACE}})
- {{TEXT}} caption lines - default #FFFFFF
- {{ACCENT}} key-line gradient top colour - default #E65E79 (gradient tints to near-white at the baseline: #E65E79 -> #ED9AAE -> #F3C7D8)
- {{ACCENT_2}} hook / alternate key gradient - default #83AAE9 (-> #A8C4F4 -> #CEDBF8); a third key colour may follow the same recipe (default yellow #EFDE72 -> #F2E7A0)
- {{SURFACE}} phrase-card background - default lavender-grey #D2D2E0 (card text near-black #060609)
- {{CARD_BG}} CTA pill / PiP-card white - default #F6F5FD; button text default crimson #B7223A
- {{FONT_DISPLAY}} key line / hook / button - default Inter 800 (ExtraBold)
- {{FONT_BODY}} caption lines - default Inter 500 (Medium)
- {{HANDLE}} - @handle (not shown on screen in this blueprint; optional on the end card)
- {{LOGO}} - logo lockup for the end card and logo-proof cards

Canvas 1080x1920, 24 fps (23.976). All positions are % of frame.

CAPTIONS
1. Latin script, as spoken; sentence case for {{TEXT}} lines; key lines as spoken (lowercase; acronyms / brand names keep caps).
2. Grouping: split each clause into 1-2-word lines (max 3). Lines STACK: each new line appears under the previous one on its first spoken word, up to 4 lines; at the clause end (or a picture cut) the whole stack hard-cuts out and the next clause starts fresh. At most ONE key line per stack - the 1-2 words that carry the claim.
3. Lines: {{FONT_BODY}}, 89 px (stacked lines may vary 89-101 px), {{TEXT}}, tracking 0, no stroke, no box, tight dark drop shadow down-right (~3px 4px 6px rgba(0,0,0,.65), estimated).
4. Key line: {{FONT_DISPLAY}}, 100 px, vertical gradient top->bottom {{ACCENT}} -> mid tint -> near-white at the baseline. Rotate {{ACCENT_2}} (same recipe) for variety. Same shadow, no stroke.
5. Hook: the first 2 spoken words alone, {{FONT_DISPLAY}} 127 px, {{ACCENT_2}} gradient, centred, centre y 60.6 %, on screen for frames 1-24, then hard cut.
6. Layout: column x 18-78 %, band y 52-72 % (torso, below the chin). Zig-zag: alternate lines hug the column's left edge (x ~21 %) and right edge (x ~75 %); typical stack: line 1 left x 21-59 % centre y 54.7 %, line 2 (key) x 23-76 % y 59.7 %, line 3 right-aligned to 75 % y 63 %, line 4 right-aligned y ~69 %. Baseline pitch 4.3-5 % H (line-height 0.85-0.9). A lone line is centred at y 60-62 %.
7. Animation: each line blurs in (8 px -> 0, opacity 0 -> 1, sharp after 2-3 frames) while sliding up ~2.5 % H (~48 px), ease-out (power3.out) over 5-6 frames; lines already on screen stay still; line appears 0-4 frames after its first word; exit = hard cut of the whole stack; no idle motion, no karaoke.

OTHER TEXT / EDIT DEVICES
8. Opening: matte the speaker and swap the background to a glowing {{ACCENT_2}} rising-chart graphic by frame ~12 of shot 1; first cut at ~4 % of runtime.
9. Phrase cards (~45 % of runtime, 36-144 frames each, one every 72-144 frames on VO beats): full-screen flat/illustrated still on {{SURFACE}} or other pastel tones; the spoken phrase as 2-4 stacked lines (same zig-zag) in the upper third (y 18-35 %) or centre (y 40-55 %): 'Lead words' near-black {{FONT_BODY}}, 'KEY WORD' near-black {{FONT_DISPLAY}} ~94 px; inactive lines grey + blurred until spoken; soft ~6 px dark shadow; lines blur + fade in over ~7 frames with ~1 % H upward drift. Accent variant: one solid {{ACCENT}}-family line with a dark 3D extrusion shadow.
10. Turn marker: a ~7-frame shot at a new location, then a {{CARD_BG}} card with the speaker in a centred portrait window (x 25-77 %, y 22-74 %) under a two-line title ('Lead words' small / 'Headline here' bold) at y 13-17 %, in a dark brand colour.
11. Logo proof: rounded light-grey square (~35 % W) with a client wordmark, top-centre y 2-17 %, above the speaker's head.
12. CTA (last ~11 % of runtime): 'CTA line' in {{TEXT}} {{FONT_BODY}} ~100 px at centre y 60 % + a fully-rounded {{CARD_BG}} pill at x 28-77 %, y 77.3-84.2 % with italic {{FONT_DISPLAY}} caps 'CTA' (ink 2.3 % H) in the brand's dark accent and a white double down-chevron at y 86-89 %, ~108 frames; then ~55 silent frames of {{LOGO}} centred on white at ~70 % W.

GRADE: Grade from the user's footage (video-style / grade.py); target look: high-contrast, muted, warm, natural skin; pastel cards.
SOUND: voice only, compressed to about -14 LUFS; optional soft whoosh on zoom-blur entries only; silence under the end card.

VERIFY before rendering (px values were render-verified with Inter; if the brand font differs, adjust px until the ink numbers match):
a) Render test frames over a dark area: "They trust" ({{TEXT}}, {{FONT_BODY}} 89 px), "people who" (key gradient, {{FONT_DISPLAY}} 100 px), "KEY WORD" (hook, {{FONT_DISPLAY}} 127 px).
b) Measure: python video-reference-match/scripts/caption_probe.py <test render or snapshot> --out <dir> --at <t> --box 0.1,0.5,0.9,0.66 --ink "{{TEXT}}:45,{{ACCENT}}:70,{{ACCENT_2}}:60" (tighten --box to one line if lines overlap).
c) Required: "They trust" ink 4.14 % +-0.5 of H and 37.9 % +-2 of W; "people who" 4.45 % +-0.5 and 52.4 % +-2. For the hook word (or any other word) compute the expected ink with python video-reference-match/scripts/fit_font.py --font "<{{FONT_DISPLAY}}>" --word "KEY WORD" at 127 px and compare. Positions within +-1 % of H of the numbers above.
```

### B32 · explainer-graphics · English · score 3

Cream line-art explainer: face-pill cutout in evolving metaphor, blur-slide captions, 2x pink key.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B32 (video-reference-match/references/blueprints/B32.json) to this brand.
Canvas 1080x1920, 30 fps. Speaker footage desaturated; most of the piece on a light canvas with line art.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{ACCENT}} is the ONLY saturated colour and must stay >= 3:1 on {{SURFACE}} and on the desaturated footage; {{TEXT}} >= 7:1 on {{SURFACE}})
- {{TEXT}}: default #31302E on cream (white #FFFFFF on footage / dark sections)
- {{ACCENT}}: default #E23A78 (key words, face ring, pill borders, highlighted bar)
- {{ACCENT_2}}: default #AFAEAD (line art)
- {{SURFACE}}: default #FBF8F7 (cream canvas)
- {{CARD_BG}}: default #121212 (dark section behind the UI card)
- {{FONT_DISPLAY}}: default Inter 700 (key words)
- {{FONT_BODY}}: default Inter 500 (lead words)
- {{HANDLE}}: not on screen
- {{LOGO}}: none

CAPTIONS
1. Latin, as spoken, punctuation kept; sentence case (continuation blocks start lowercase); key words lowercase; no emoji.
2. Blocks of 2-8 words (~5), up to 4 lines, laid out centred in advance (does not re-centre while growing); 0-1 key word per block on its own line.
3. Lead: {{FONT_BODY}} at 77 px, tracking -0.02em, {{TEXT}}; key: {{FONT_DISPLAY}} at ~148-153 px (~2x lead, fixed size), tracking -0.03em, {{ACCENT}}. No stroke, shadow or box.
4. Hook state (first ~11 %, over footage): block top 65 % H, lines at 66.8 % / 71.2 %, key at 78.3 %, pitch 4.4 % H. Main state (canvas): first line centre 15.1 % H, key line 21.7-22.3 % (17.6 % when it opens the block), lines after key 24.5-28.9 %, lead pitch 4.9 % H, lead-to-key baseline pitch 8.3 % H; max width 78 % W, margins >= 11 % W.
5. Each word appears on its spoken word (0-3 frames early), sliding ~2 % W from the left with a 3-frame horizontal motion blur (smeared, light blur, sharp); no scale. Block exit: blur + fade + drift up ~1 % H over ~6 frames; the next block's first word lands ~1 frame later.

GRAPHICS AND EDIT DEVICES
6. Hook: desaturated footage, {{ACCENT}} oval ring (~1.5 % W stroke) around the face, faint white grid overlay; hard switch to {{SURFACE}} at ~11 %.
7. Speaker as a face pill / rounded-rect cutout 13-30 % W with a ~3 px {{ACCENT}} border, linked into one {{ACCENT_2}} line-art metaphor that changes state every sentence (break, branch, network, final {{ACCENT}} version). Change the graphic state every ~0.5-1.5 s.
8. Example beat (~14 % of runtime): motion-blur drop to {{CARD_BG}}; white rounded card x 9-91 %, y 41.5-82.5 % with a soft {{ACCENT}} glow; icon + 'Card title' + grey subtitle; 5 rows avatar + 'Name' + bar + counting %; the hero row's bar in {{ACCENT}}, others light grey; others fade out.
9. Transitions: graphic zoom-throughs and vertical motion-blur drops (~6-8 frames); one hard footage->canvas switch.
10. No lower-thirds, logos or emoji.

GRADE: Grade from the user's footage (video-style / grade.py); target look: near-B&W desaturated speaker, warm cream canvas, high-contrast text, one saturated accent.
SOUND: voice only, dense delivery (do not speed up artificially), -14 LUFS; soft whooshes on blur drops.

VERIFY
a) Render the key word "lose" at 148 px on line 2 of a block on {{SURFACE}} and measure:
   python video-reference-match/scripts/caption_probe.py <test_render> --out <dir> --at <t> --box 0.06,0.18,0.94,0.26 --ink "{{ACCENT}}:60"   (default ink #E23A78)
   Required: 5.62 % ±0.5 of H, 24.2 % ±2 of W. "no point" at 153 px: 7.5 % H, 49.2 % W (--box 0.06,0.10,0.94,0.215).
b) Lead: "everybody else is" at 77 px white over {{CARD_BG}}: --box 0.06,0.12,0.94,0.175 --ink "#FFFFFF:50" -> 3.75 % ±0.5 H, 51.9 % ±2 W.
c) Expected ink for any other word: video-reference-match/scripts/fit_font.py --font "{{FONT_BODY}}" --word <word> --tracking -0.02.
```

### B44 · podcast-clip · English · score 3

Zero-cut speaker-over-listener split; glowing three-tier seam captions with one accent key word.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B44 (video-reference-match/references/blueprints/B44.json) to this brand.
Canvas 1080x1920, 29.97/30 fps. Two-camera conversation as a 50/50 vertical split: speaker top, listener bottom, seam at 50 % H.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{ACCENT}} key word must stay >= 3:1 and be the brightest saturated element on the footage; thin {{TEXT}} lead words need a dark area behind them)
- {{TEXT}}: default #FFFFFF (lead and small words)
- {{ACCENT}}: default #EAB827 (key word + its glow)
- {{ACCENT_2}}: none
- {{SURFACE}}: none (footage)
- {{CARD_BG}}: none
- {{FONT_DISPLAY}}: default Poppins 900 (key word; Montserrat Black is the original feel)
- {{FONT_BODY}}: default Inter 300 (lead words; Montserrat Light preferred); small words Poppins 800
- {{HANDLE}}: not on screen
- {{LOGO}}: none

CAPTIONS (three-tier seam stack)
1. Latin, as spoken; lead words sentence case, key and small words lowercase; no punctuation except apostrophes; no emoji.
2. Per phrase: 1-3 lead words, 0-1 key word (the stressed word), 0-2 small follow-on words.
3. Lead: {{FONT_BODY}} at 65 px, {{TEXT}}, soft white glow 0 0 15px rgba(255,255,255,.55), centred at 45.1 % H.
4. Key: {{FONT_DISPLAY}} at 133 px, {{ACCENT}}, tracking -0.01em, soft halo 0 0 21px of {{ACCENT}} at 60 % opacity, centred ON the seam at 50.1-50.7 % H.
5. Small: Poppins 800 at 47 px, {{TEXT}}, soft glow, centred at 54.1 % H.
6. Motion (30 fps): lead words fade in ~3 frames with light blur on their words; key word blur+fade in over ~6 frames (no scale); small word fades in ~4 frames after the key; the stack clears with a left-to-right letter-by-letter fade over ~4 frames before the next phrase. No hard text cuts, no idle motion.

LAYOUT AND EDIT DEVICES
7. No picture cuts: keep the split for the whole piece. At ~60 % of runtime swap the top panel to a second voice/angle (cut inside the panel only).
8. No titles, lower-thirds, b-roll, punch-ins or end card.

GRADE: Grade from the user's footage (video-style / grade.py); target look: dark, warm, moody low-key, saturated warm walls, deep blacks, natural skin.
SOUND: voice only, trimmed to the first word (~4 frames), -14 LUFS (source sits slightly under, -14.6).

VERIFY
a) Render the key word "not" at 133 px on the seam and measure:
   python video-reference-match/scripts/caption_probe.py <test_render> --out <dir> --at <t> --box 0.3,0.47,0.7,0.54 --ink "{{ACCENT}}:70"   (default ink #EAB827)
   Required: 4.61 % ±0.5 of H, 21.5 % ±2 of W, centre y ~50.4 %.
b) Small word "person" at 47 px: --box 0.3,0.52,0.7,0.565 --ink "{{TEXT}}:60" -> 1.72 % ±0.5 H, 16.8 % ±2 W.
c) Lead line: render "KEY WORD" in {{FONT_BODY}} at 65 px at 45.1 % H; expected ink from video-reference-match/scripts/fit_font.py --font "{{FONT_BODY}}" --word <word> (a 3-word lowercase-ish line ~2.2 % H).
```

## boxed-pill

_caption text on a solid or translucent box / pill_

### B13 · podcast-clip · English · score 4

Frenetic name-drop podcast: accent divider pills, second accent name titles, one shot per word.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B13 (video-reference-match/references/blueprints/B13.json) to this brand.
Canvas 1080x1920, 25 fps. Two-camera podcast footage plus b-roll for every named example.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: white {{TEXT}} >= 4.5:1 on the {{ACCENT}} pill; {{ACCENT_2}} name titles >= 3:1 on the footage with their dark outline)
- {{TEXT}}: default #FFFFFF
- {{ACCENT}}: default #1590C5 (solid caption pill)
- {{ACCENT_2}}: default #EFA816 (name titles, gradient to a deeper orange)
- {{SURFACE}}: none (footage)
- {{CARD_BG}}: default #000000 (end card)
- {{FONT_DISPLAY}}: default Playfair Display 700 italic (name titles)
- {{FONT_BODY}}: default Inter 700 (pill captions)
- {{HANDLE}}: default @handle (end card)
- {{LOGO}}: optional on the mics/set; platform icon on the end card

CAPTIONS
1. Latin, as spoken, sentence case; keep commas, full stops, question marks; no emoji.
2. 2-4 words per phrase, one line; break at commas.
3. {{FONT_BODY}} at 58 px, {{TEXT}}, tracking -0.01em, thin dark outline ~1.5 px, on a solid {{ACCENT}} rounded pill 80 px tall, 18 px side padding, radius ~20 px; pill hugs the text.
4. Single shots: centred, centre y 66.8 % H (pill 64.7-68.8 %). 50/50 splits: centre y 49.8 %, exactly on the divider.
5. Hard swap of pill + text in one frame on the phrase's first word (+0 to +3 frames); no scale/fade/slide; hard cut out.
6. Hook b-roll variant (~5-7 % of runtime): plain {{TEXT}} line, Inter 500 74 px, tracking 0.04em, centred at 59.6 % H, unspoken words at 40 % opacity stepping to full on their word. Very first ~2 %: lead words on a translucent soft-edged warm box (~70 %), ~85 px.

OTHER TEXT AND EDIT DEVICES
7. Name titles (hook only): on the cut to each named person, 'Name Surname' in {{FONT_DISPLAY}} ~91 px, {{ACCENT_2}} with a slight vertical gradient to a deeper orange, thin dark outline, centred at 54-60 % H, up to ~85 % W.
8. Long answers: stacked 50/50 split (b-roll top, speaker bottom), swap the top image every ~4 s; optional translucent large white 'Name' label (55-60 % opacity) at y 34.5-40 % in the top panel.
9. Lists of examples: one b-roll shot per spoken word, ~10 frames each, cut mid-sentence on the noun, then back to the speaker. Pacing deliberately uneven: bursts vs long split holds.
10. Open with a ~1 s pull-out from a detail ECU into the split; first word within ~1 frame.
11. End card (last ~4 % of runtime, ~50 frames): {{CARD_BG}}, 'WATCH FULL VIDEO / ON [PLATFORM]' white bold caps ~72 px at centre y 24.6 %, episode thumbnail with white border x 15.5-84.5 %, y 37-60 % with the platform icon on its bottom edge, 'LINK IN BIO' ~70 px at 73.1 % H.

GRADE: Grade from the user's footage (video-style / grade.py); target look: warm tungsten studio, dark backgrounds, natural skin; leave inserted b-roll in its own look.
SOUND: low music bed (~6 dB under speech gaps), zero silence, -14.3 LUFS; occasional hits on cuts.

VERIFY
a) Render the pill caption "and she would be" on a split divider and measure:
   python video-reference-match/scripts/caption_probe.py <test_render> --out <dir> --at <t> --box 0.28,0.479,0.72,0.517 --ink "{{TEXT}}:70"   (default ink #FFFFFF)
   Required: 2.19 % ±0.5 of H, 42.5 % ±2 of W; pill (--box 0.2,0.47,0.8,0.535 --ink "{{ACCENT}}:60") 46.0 % W x 4.14 % H.
b) "The movies" at 66.8 %: --box 0.355,0.651,0.645,0.685 -> 2.11 % H, 27.8 % W.
c) Name title: render "KEY WORD" in {{FONT_DISPLAY}} ~91 px; expected ink for a real name from video-reference-match/scripts/fit_font.py --font "{{FONT_DISPLAY}}" --word <name>.
```

### B19 · mixed · Hinglish · score 4

Selfie talking head rotating with split face-card + UI mock-ups; UPPERCASE word-by-word captions with one white-boxed accent key phrase.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B19 (video-reference-match/references/blueprints/B19.json) to this brand.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{ACCENT}} text must stay >= 4.5:1 on its white box, captions >= 3:1 on the footage)
- {{TEXT}} caption text on footage - default #FFFFFF (navy #0B1327 on light layouts)
- {{ACCENT}} key-phrase text / headline key words / STEP tags - default royal blue #1F4FD6
- {{ACCENT_2}} hook title highlight bar - default lime #BDF806 (black text on it)
- {{SURFACE}} light UI background - default #EEF4FB with a faint dot grid; cards white with soft shadow
- {{CARD_BG}} dark-mode layout / end card - default navy #091E47 (key box inverts to an {{ACCENT}} box with a thin white outline and white text)
- {{FONT_DISPLAY}} captions, key box, headlines - default Inter 800 (ExtraBold)
- {{FONT_BODY}} UI mono labels - default JetBrains Mono, uppercase, letter-spaced, grey, ~1 % H
- {{HANDLE}} - @handle (end card, under the logo)
- {{LOGO}} - brand lockup on the navy end card

Canvas 1080x1920, 30 fps.

LAYOUT (rotate on almost every cut; only ~1 in 12 cuts keeps the same layout)
1. Full-face selfie MCU (~20 % of runtime, 48-117 frames per shot), static, no punch-ins.
2. Split (~36 %): rounded face card x 8-92 %, y 4-46 %; caption centred in the gap at y ~48-50 %; UI mock-up card from y ~56 % down on {{SURFACE}}.
3. Full-screen UI explainer (~44 %) on {{SURFACE}} (or {{CARD_BG}} for mechanism / CTA): headline at the top, centre y ~14 %, UI cards below with animated cursor, check marks, bar fills, link lines; blue 'STEP N · TOOL' mono tags at y ~64 %.

CAPTIONS
4. Latin script, UPPERCASE (English translation of Hinglish speech is fine). 1-6 words on ONE line, never wraps.
5. Caption: {{FONT_DISPLAY}} 46 px, {{TEXT}}, tracking 0, no stroke/box, faint shadow 0 2px 4px rgba(0,0,0,.35). Face shots: centred at y 75.9 %. Split shots: centred at y ~48-50 % (navy on light).
6. Reveal in place: typeset the full line centred first, then switch words on one by one at their final x (hard cut, no fade/scale), ~4-12 frames apart; hard cut out, then a 1-frame gap before the next caption.
7. Key phrase (one per sentence, the noun phrase that names the idea): small lead-in word in {{TEXT}} at y 75.9 %, then 5 frames later the key phrase in a solid white rounded box (r ~8 px, padding ~27 px L/R, ~24 px top, ~30 px bottom) at x 27.4-72.6 %, y 77.7-84.1 %, text {{ACCENT}} {{FONT_DISPLAY}} 88 px, tracking -0.04em, wiped left-to-right over 2 frames, no overshoot. On split layouts ~75 px. On {{CARD_BG}} layouts invert: {{ACCENT}} box, thin white outline, white text.
8. Explainer headline: {{FONT_DISPLAY}} 74-86 px, -0.04em, navy on {{SURFACE}} (key words {{ACCENT}}), centre y 13.7-14.3 %, revealed word by word in place.

OTHER TEXT / EDIT DEVICES
9. Hook frame 1: a white stat card proving the pain at the top + 'Headline here' in black heavy rounded type on an {{ACCENT_2}} bar at y 28-31 %; first cut at frame ~57 into an animated mock-up of the slow current method.
10. 'Stop doing this' beat: grey old-method button, {{ACCENT}} X drawing across, tilted 'OLD METHOD' tag, small handwritten aside.
11. Comparison: two stat cards 'small VS big' with large {{ACCENT}} / navy numerals; caveat as 'X ≠ Y' white and navy pills with an {{ACCENT}} ≠.
12. CTA (last ~19 %): locked framework card with padlock 'IN YOUR DM' (~280 frames), a comment bar (white pill, '+ KEYWORD', {{ACCENT}} 'Post') at y ~90 % typing the keyword, then {{CARD_BG}} end card with {{LOGO}}, {{HANDLE}} and an {{ACCENT}} 'Comment "KEYWORD"' pill (~78 frames).
13. Cuts: hard cuts only, on caption-phrase boundaries (mid-sentence is fine).

GRADE: Grade from the user's footage (video-style / grade.py); target look: high-contrast, muted, neutral-warm face footage set against cool off-white and navy graphics.
SOUND: voice at about -14 LUFS, optional low bed under voice and end card, optional click on cursor taps.

VERIFY before rendering (px values were render-verified with Inter; if the brand font differs, adjust px until the numbers match):
a) Render test frames: "EASY WAY" ({{ACCENT}} in the white box, 88 px, -0.04em), "BECAUSE" (navy headline, 74 px, -0.04em on {{SURFACE}}), and "KEY WORD" as a caption line (46 px {{TEXT}} over a dark area).
b) Measure: python video-reference-match/scripts/caption_probe.py <test render or snapshot> --out <dir> --at <t> --box 0.28,0.775,0.72,0.835 --ink "{{ACCENT}}:90" (key box); --box 0.15,0.11,0.85,0.165 --ink "#0B1327:80" (headline); --box 0.1,0.745,0.9,0.775 --ink "{{TEXT}}:60" (caption).
c) Required: "EASY WAY" ink 3.67 % +-0.5 of H and 40.1 % +-2 of W; "BECAUSE" 2.89 % +-0.5 and 30.4 % +-2; caption caps ink ~1.8 % H - compute the expected width of "KEY WORD" at 46 px with python video-reference-match/scripts/fit_font.py --font "<{{FONT_DISPLAY}}>" --word "KEY WORD". Box edges within +-1 % of the numbers above.
```

### B31 · talking-head · English · score 4

Game-show versus format: boxed 1-2-word captions at 78 % height, two-size jump cuts, pixel-art P1-vs-P2 scoreboard and a score-comment CTA after every round.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B31 (video-reference-match/references/blueprints/B31.json) to this brand.
Canvas 1080x1920, 30 fps. All positions are % of frame; px are at 1080x1920.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} must stay >= 4.5:1 on {{CARD_BG}} at 75 % opacity, {{ACCENT}} >= 3:1 on the footage behind the title)
- {{TEXT}}      caption text, large labels on dark layouts   default #FFFFFF
- {{ACCENT}}    hook question title                          default #F4F2B5 (pale yellow)
- {{ACCENT_2}}  stat result tag                              default #E3E3D7 (off-white)
- {{SURFACE}}   dark comparison / split layout               default #1D1C1A
- {{CARD_BG}}   caption box (at 75 % opacity)                default #2F2F2F
- {{FONT_DISPLAY}} hook title                                default Playfair Display 700 (bold high-contrast display serif)
- {{FONT_BODY}}    captions, labels, tags                    default Inter 700 (captions) / Inter 400 (tag)
- {{HANDLE}}    source credits on borrowed footage ("Source - @handle")
- {{LOGO}}      contender logos on labels and the scoreboard card

CAPTIONS
1. English as spoken, sentence case (capital only at a sentence start); keep commas, full stops, apostrophes; digits as transcribed.
2. 1-2 words per caption (mostly 2), one line, replaced as a unit; never more than one caption on screen.
3. Type: {{FONT_BODY}} 700 at 50 px, tracking 0, {{TEXT}}, no stroke, no shadow.
4. Box: rounded rectangle {{CARD_BG}} at 75 % opacity, 86 px tall, 25 px left/right padding, width hugging the text (resizes with each phrase), radius ~9 px.
5. Position: centred (x 540 px), box and text centre at 78.4 % of height (y ~1505 px), identical on talking-head, screen-recording and split shots.
6. Animation: hard cut in (text + resized box on one frame) ~6-7 frames after the phrase's first word starts; hard cut out on the next phrase. No fade, pop, slide, highlight or idle motion. Hide captions while a full-frame card is up.

OTHER TEXT
7. Hook title, first shot only (on from frame 0, hard-cut out with the first picture cut): 2-line question "<A> vs <B>: / Question here?" centred at the top, {{ACCENT}}, {{FONT_DISPLAY}} at ~86 px (line 1 ~84, line 2 ~89), soft dark drop shadow; block x 5.8-93.5 %, y 12.5-21.8 %, centre y 17.1 %, line gap 1.6 % H.
8. Scoreboard card (~94 frames, when introducing the contenders): full-frame pixel-art game card: "SCORE" ribbon, P1/P2 tabs, parchment panels with {{LOGO}} + 2-line contender name and a big pixel "0 / POINTS", a "VS" badge. 4-frame zoom settle on entry; logo wipes in left-to-right (3 frames), score fades in (4 frames), name reveals letter by letter (~6 frames); P2 fills the same way; no captions over it.
9. Contender label on every screen capture: {{LOGO}} + 2-line name; small dark grey at top centre (y ~8.5 %, ~1.1 % H per line) on light screens; large {{TEXT}} on a {{SURFACE}} comparison layout (block centre y ~17 %).
10. Stat tag when a result needs a number: e.g. "~N+ hours", {{ACCENT_2}}, {{FONT_BODY}} 400 at 59 px, centred at y 25.7 %.
11. Source credit on borrowed footage: "Source - {{HANDLE}}", tiny white sans (~0.7 % H), top-left at x 9 %, y 6 %.
12. No end card; CTAs are spoken.

EDIT DEVICES
13. Two-size jump cuts on the talking head: alternate MS and a ~130-150 % MCU/CU every 30-90 frames (median shot ~54 frames); cut on word boundaries.
14. Hook: question title + a short flash of finished results before any explanation. Re-hook at ~8 % of runtime by promising that the final round is the decider. After every round, a spoken score-comment CTA. Peak the cut rate (~39 cuts/min) in the decider round; slow to ~8 cuts/min for the closing opinion.
15. Same-prompt comparisons as top/bottom splits on {{SURFACE}}.

GRADE
16. Grade from the user's footage (video-style / grade.py); target look: warm, high-contrast, muted, lamp-lit home studio with natural skin and gentle contrast.

AUDIO
17. Light music bed under dense speech; soft whoosh/pop on cuts into screen captures (about a third of cuts), optional 8-bit blips on the scoreboard. Master to about -14.7 LUFS with true peak <= -1 dBTP.

VERIFY before rendering
a) Render a test frame with the caption "KEY WORD" in its box and measure:
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.25,0.75,0.75,0.82 --ink "{{TEXT}}:45"
b) Expected ink: video-reference-match/scripts/fit_font.py with {{FONT_BODY}} 700 at 50 px (reference ink height 1.88 % H for mixed-case words with ascenders, no descenders). Required: within ±0.5 % H; centre y 78.4 % ±0.5; box height 4.45 % H; colours equal to the tokens. Title: --box 0.05,0.12,0.95,0.22 --ink "{{ACCENT}}:60", expected ink ~3.9-4.0 % H per line at the default font.
```

### B48 · talking-head · English · score 3

One-take listicle: chest captions with hopping black word box, boxed hook title, stacking list pills.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B48 (video-reference-match/references/blueprints/B48.json) to this brand.
Canvas 1080x1920, 30 fps. Static single-take talking head; all visual change is text on the chest (61-77 % H).

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship: {{TEXT}} on {{ACCENT}} boxes >= 7:1, {{ACCENT}} boxes >= 3:1 against the clothing, {{ACCENT}} text on {{CARD_BG}} >= 7:1)
- {{TEXT}}: caption and pill text, default #FFFFFF
- {{ACCENT}}: active-word box, hook-title boxes, list pills, save-pill text, default #000000
- {{ACCENT_2}}: unused, default none
- {{SURFACE}}: unused, default none
- {{CARD_BG}}: save sticker pill fill, default #FFFFFF
- {{FONT_DISPLAY}}: default Poppins 700
- {{FONT_BODY}}: default Poppins 700
- {{HANDLE}}: not shown in the source; optional in the follow ask
- {{LOGO}}: not shown in the source

CAPTIONS
1. As spoken, sentence case; keep sentence-final full stops, drop commas.
2. Chunks of 1-4 words over 2 short lines (1-2 on line 1, 1-3 on line 2); a sentence-final word may stand alone ("KEY WORD."). Whole chunk hard-cuts in ~2 frames after its first word.
3. {{FONT_DISPLAY}} 55 px, {{TEXT}}, tracking 0, no stroke/shadow. Calibration: "connection" ink 2.27 % H / 29.3 % W; "recruitment" 2.27 % / 31.9 %.
4. Active word: sits in a {{ACCENT}} box, radius 6 px, padding 13 px left/right, 12 px top, 15 px bottom (~3.67 % H tall); text stays {{TEXT}}, same size. The box hard-jumps to each word on its start (0-2 frames); no box during short gaps.
5. Position: lines centred at x ~48 % W; line 1 ink 66.7-69.6 % H, line 2 70.2-73.1 % H (block centre ~70 %), tight line gap, below the chin.
6. Hard cuts only: no fade, pop, scale or idle motion.

OTHER TEXT
7. Hook title (frames 0-~83, replaces captions): hook sentence in 2 centred lines (x ~46 %), {{FONT_DISPLAY}} 57 px {{TEXT}} on merged {{ACCENT}} per-line boxes (~6 px rounded corners) spanning x 11.9-81.2 %, y 61.6-70.4 %; the one viewer word in CAPS; end with "..". Line ink ~2.97 % H; a ~24-character line spans ~63.5 % W.
8. Save sticker (frames ~31-73): {{CARD_BG}} rounded pill (radius ~9 px) x 17.9-70.7 %, y 71.1-76.5 %, 0.7 % H under the title; {{ACCENT}} {{FONT_BODY}} 56 px 3-word save prompt + green check emoji, left-aligned from x 20.1 %. Hard cut in/out, no pop.
9. List items (replace captions while items are named, ~29-48 % of runtime): {{ACCENT}} pills, radius ~6 px, {{TEXT}} {{FONT_BODY}} "N. Item", left-aligned, each hard-cut in under the previous ~2 frames after its item is spoken. Stack 1 (items 1-3): 53 px text, pills 5.1 % H, left edge x 23.4 %, rows 64.7-69.8 % and 71.1-76.2 %. Stack 2 (items 4-6): 40 px text, pills 3.7 % H, left edge x 33.1 %, row tops 61.6 / 66.0 / 71.2 %.

STRUCTURE: hook ~10 %, setup ~17 %, list ~21 %, why/proof ~24 %, comment-keyword CTA then follow ask ~28 %.
SOUND: voice only, no bed. Master to about -14.5 LUFS, true peak <= -1 dBTP.
GRADE: Grade from the user's footage (video-style / grade.py); target look: low-contrast, saturated, warm soft indoor light, natural skin.

VERIFY before rendering: render the calibration words and measure them:
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at <t_connection> --box 0.2,0.700,0.8,0.728 --ink "#FFFFFF:60"
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at <t_recruitment> --box 0.2,0.700,0.8,0.733 --ink "#FFFFFF:60"
"connection" must read ink 2.27 % +-0.5 of H and width 29.3 % +-2 of W; "recruitment" 2.27 % +-0.5 / 31.9 % +-2; the active box measured with --ink "#000000:25" over --box 0.2,0.64,0.8,0.75 must be 3.67 % +-0.5 tall. Swap --ink colours to {{TEXT}} / {{ACCENT}}. Expected ink for other words: video-reference-match/scripts/fit_font.py with {{FONT_DISPLAY}} at 55 px. Positions within +-1 % of frame height.
```

## karaoke-highlight

_the spoken word is highlighted as it is said_

### B36 · explainer-graphics · English · score 4

Zero-cut cream-canvas UI explainer; three-state grey-to-black karaoke line; result-first progress hook.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B36 (video-reference-match/references/blueprints/B36.json) to this brand.
Canvas 1080x1920, 30 fps. Speaker on a plain light canvas ({{SURFACE}}) in the bottom half, UI graphics in the top third.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: current-word {{TEXT}} must stay >= 7:1 on {{SURFACE}}, upcoming grey must stay visibly lighter than spoken grey, {{ACCENT}} box must keep >= 7:1 behind {{TEXT}})
- {{TEXT}}: default #161410 (current word, headline)
- {{ACCENT}}: default #FBD409 (headline key-word box, badges, cost callouts)
- {{ACCENT_2}}: default #9C968C (already-spoken words); upcoming words default #D1CCC2 (derive as a lighter tint of {{ACCENT_2}} toward {{SURFACE}})
- {{SURFACE}}: default #F1EDE3 (warm cream canvas behind speaker and graphics)
- {{CARD_BG}}: default #FFFFFF (UI cards, phone screens)
- {{FONT_DISPLAY}}: default Inter 700 (headline)
- {{FONT_BODY}}: default Poppins 800 (captions; Montserrat ExtraBold is the closer original)
- {{HANDLE}}: default @handle (comment/DM CTA cards)
- {{LOGO}}: optional, inside UI cards only; never a corner bug

CAPTIONS
1. Latin, as spoken, sentence case, no punctuation, no emoji.
2. One line of 3-5 words per phrase; never 2 lines.
3. {{FONT_BODY}} at 60 px, tracking 0, no stroke, no shadow, no box.
4. Three states: whole phrase visible from its start in the upcoming grey (default #D1CCC2); the word being spoken in {{TEXT}}; words already spoken in {{ACCENT_2}}.
5. Centred. Centre y 40.3 % H while the speaker is in frame (gap between top graphics and head); 69.5 % H when a graphic fills the frame.
6. Phrase hard-cuts in on its first word (first word already {{TEXT}}); highlight jumps to each next word within ±1 frame of its start as a 1-frame colour switch; hard cut to the next phrase; no idle motion.

OTHER TEXT AND EDIT DEVICES
7. Hook headline (first ~8 % of runtime, ~90 frames): 2 centred lines in {{FONT_DISPLAY}} 63 px, {{TEXT}}, tracking -0.01em, lines at 12.8-18.8 % H (centres 14.3 % / 17.3 %); {{ACCENT}} box (~3.75 % H tall, ~6 px radius) behind the one KEY WORD, text stays {{TEXT}}.
8. Result-first hook graphic: two {{CARD_BG}} rounded cards at x 7-46 % and 54-92 %, y 21-32 % ('what you pay for' -> 'your version'), a thin progress bar counting 2 % -> 100 % synced to the spoken promise, then a small {{ACCENT}} badge.
9. No hard cuts: the speaker slides out with one motion-blur whip (~6-8 frames) at ~8 % and returns for the claim and the CTA; for ~70 % of runtime full-screen UI mock-ups on {{SURFACE}} carry the story, a new element every ~1-2 s (slide/scale in, 8-12 frame ease-out, soft shadows).
10. When a cost or number is spoken, an {{ACCENT}} rounded callout with a bold {{TEXT}} number at ~x 42-76 %, y ~51-55 %.
11. CTA (last ~12 %): speaker returns; mock comment card with a keyword from {{HANDLE}} + DM card with a link animate in above the head.
12. No lower-thirds, no emoji, no end card.

GRADE: Grade from the user's footage (video-style / grade.py); target look: bright warm cream, low saturation, high-contrast black type, natural skin, soft vignette.
SOUND: voice-led, compressed, -14 LUFS, no music bed required; optional soft whoosh on the whip.

VERIFY
a) Render a test frame with a 4-word phrase whose current word is "with", centred at 40.3 % H, and measure:
   python video-reference-match/scripts/caption_probe.py <test_render> --out <dir> --at <t> --box 0.43,0.37,0.62,0.45 --ink "{{TEXT}}:60"   (default ink #161410)
   Required: "with" ink 2.5 % ±0.5 of H and 12.9 % ±2 of W; centre y 40.3 %. Second check: "sent" 2.11 % H, 12.5 % W.
b) Headline: render "KEY WORD" in {{FONT_DISPLAY}} at 63 px and measure with --box 0.15,0.12,0.85,0.158 --ink "{{TEXT}}:80"; expected ink for any word: video-reference-match/scripts/fit_font.py --font "{{FONT_DISPLAY}}" --word <word>.
c) If {{FONT_BODY}} is not Poppins 800, re-solve px with fit_font.py --font "{{FONT_BODY}}" --word with --ink 2.5 --width 12.9 and use that size.
```

### B39 · talking-head · English · score 3

One-take staged press-scrum announcement: top-band karaoke captions, spoken word accent, persistent CTA bar.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B39 (video-reference-match/references/blueprints/B39.json) to this brand.
Canvas 1080x1920, 30 fps. One continuous take; all editing is in the text layers.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship: {{ACCENT}} must stay >= 3:1 on the footage in the top band, {{ACCENT_2}} >= 7:1 on {{CARD_BG}})
- {{TEXT}}: already-spoken caption words, default #FFFFFF
- {{ACCENT}}: the word being spoken, default #FECC00
- {{ACCENT_2}}: CTA bar text, default #000000
- {{SURFACE}}: unused, default none
- {{CARD_BG}}: CTA bar fill, default #FDFDFD
- {{FONT_DISPLAY}}: captions, default Poppins 600
- {{FONT_BODY}}: CTA bar text, default Poppins 600
- {{HANDLE}}: contact on the CTA bar (email, site or "@handle")
- {{LOGO}}: not shown in the source

CAPTIONS
1. Script & case: as spoken; lowercase except the first word of the video and proper nouns. Drop all punctuation (keep '@' and '.' inside {{HANDLE}}).
2. Grouping: segments of 4-7 words over at most 2 lines. Lay out the WHOLE segment first (each line centred on x ~51 %, max line width 71 % W), then reveal its words word by word in their final slots; the first word is not re-centred alone. When the 2 lines are full, hard-cut to the next segment (breaks may fall mid-sentence). Leave the band empty during pauses longer than ~15 frames.
3. {{FONT_DISPLAY}} 56 px for every word (no size change on the active word), tracking 0, no stroke, no box, soft shadow 0 1px 4px rgba(0,0,0,.35). Calibration: "positions" ink 3.05 % H / 24.6 % W; "locations" 2.19 % / 24.3 %.
4. Colours: word being spoken {{ACCENT}}; spoken words {{TEXT}}; unspoken words hidden.
5. Position: upper fifth, block centred at ~20 % H: line 1 ink 16.7-19.7 %, line 2 20.5-23.4 % (baseline pitch 3.6 % H); a 1-line segment centred in the band (~20.5 %). Keep the face (~38-55 %) and the CTA bar (~73 %) clear.
6. Animation: hard cut per word on its transcript start (0 frames); the highlight hops to the new word and the previous word turns {{TEXT}} on the same frame; no fade, pop, slide or idle motion; segment change is a hard cut.

OTHER TEXT
7. Persistent CTA bar, whole video: {{CARD_BG}} rounded rectangle (radius ~6 px), x 17.2-78.5 %, y 72.1-74.2 % (2.1 % H); centred {{ACCENT_2}} text "Headline here <heart emoji> {{HANDLE}}" (~8 words) in {{FONT_BODY}} 26 px (a 5-letter word reads ~0.86 % H; full line spans x 18.3-77.4 %). Static, not tracked.

EDIT
8. Single unbroken take, no cuts or punch-ins. Stage the opening as a scene (e.g. hands with phones and a mic pushed toward the speaker from the foreground); first word within 2-3 frames. Beat split: hook ~19 %, claim ~35 %, invitation question ~11 %, CTA ~20 %, sign-off ~15 %.

SOUND: voice only (any bed must be inaudible, > 25 dB under speech). Master to about -14.5 LUFS, true peak <= -1 dBTP.
GRADE: Grade from the user's footage (video-style / grade.py); target look: natural office daylight, high-contrast but muted, slightly warm with cool overheads, neutral skin.

VERIFY before rendering: render the calibration words and measure them (yellow state):
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at <t_positions> --box 0.03,0.11,0.97,0.26 --ink "#FECC00:60"
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at <t_locations> --box 0.03,0.11,0.97,0.26 --ink "#FECC00:60"
"positions" must read ink 3.05 % +-0.5 of H and width 24.6 % +-2 of W; "locations" 2.19 % +-0.5 / 24.3 % +-2. Swap the --ink colour to {{ACCENT}}. Expected ink for any other word: video-reference-match/scripts/fit_font.py with {{FONT_DISPLAY}} at 56 px. Positions within +-1 % of frame height.
```

## word-by-word-plain

_words appear one at a time, no box, little emphasis_

### B06 · talking-head · English · score 4

Credibility sandwich: raw selfie hook, then third-party receipts letterboxed on black with word-by-word white captions below, then selfie close.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B06 (video-reference-match/references/blueprints/B06.json) to this brand.
Canvas 1080x1920, 30 fps. All positions are % of frame; px are at 1080x1920.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} must stay >= 4.5:1 on {{SURFACE}} and >= 3:1 on the footage)
- {{TEXT}}      captions                          default #FFFFFF
- {{ACCENT}}    none (this blueprint has no emphasis colour; do not add one)  default none
- {{ACCENT_2}}  none                              default none
- {{SURFACE}}   letterbox canvas behind inserts   default #050405 (near-black)
- {{CARD_BG}}   none                              default none
- {{FONT_DISPLAY}} captions                       default Poppins 500 (geometric sans medium)
- {{FONT_BODY}}    same as display                default Poppins 500
- {{HANDLE}}    not shown
- {{LOGO}}      not shown (only logos that are native to the b-roll)

CAPTIONS
1. English as spoken, sentence case (capital "I"); keep full stops, commas, apostrophes. No emoji, no highlight colour, no box.
2. Grouping: one clause per block, 1-6 words over at most 2 centred lines (~45 % of width max per line).
3. Type: {{FONT_DISPLAY}} at 57 px, {{TEXT}}, tracking 0, no stroke, no shadow, no box.
4. Position: block centred horizontally; line 1 centre at 79.0 % of height, line 2 at 82.4 % (line pitch 3.4 % ~ 65 px). Same position over selfie footage and over inserts.
5. Animation (30 fps): lay out the full block centred first, then reveal each word in its final slot on its spoken word (up to ~9 frames early is fine): fade in while rising ~1 % of height over 2 frames. No scale, no blur. The whole block hard-cuts out when the next clause starts. Partial lines look off-centre until complete; that is correct.

OTHER TEXT
6. No authored titles, lower thirds or end card. For receipts, place each screenshot / quote / press image full-width on a {{SURFACE}} 9:16 canvas (image band roughly y 6-77 %) for ~90-120 frames, untouched, with captions continuing below at ~79 %.

EDIT DEVICES
7. Shape: selfie hook (~13 % of runtime) -> insert block (~60 %: receipts on {{SURFACE}} + full-frame b-roll of the subject, a new visual every ~90-180 frames) -> one long selfie close (~28 %). Hard cuts only, no punch-ins.

GRADE
8. Grade from the user's footage (video-style / grade.py); target look: warm, high-contrast, natural saturation, daylight phone look; leave inserts in their native colours.

AUDIO
9. Calm unobtrusive music bed under the voice (optional); no SFX on cuts. Master to about -14.2 LUFS, true peak <= -1 dBTP.

VERIFY before rendering
a) Render a test frame with the caption "KEY WORD" on line 1 over {{SURFACE}} and the word "school." on line 2, then measure:
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.1,0.775,0.9,0.81 --ink "{{TEXT}}:50"
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.3,0.81,0.7,0.845 --ink "{{TEXT}}:50"
   Required: "school." ink 2.19 % ±0.5 of height and 18.3 % ±2 of width (at the default font); "KEY WORD" within ±0.5 % H of the value from video-reference-match/scripts/fit_font.py ({{FONT_DISPLAY}}, 57 px). Line centres within ±1 % of 79.0 / 82.4 %; colour equal to {{TEXT}}.
```

### B12 · mixed · English · score 4

One evolving black dot-grid diagram above a rounded face card, single-word captions, italic-serif title word, full-face cuts for opinions.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B12 (video-reference-match/references/blueprints/B12.json) to this brand.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} on {{SURFACE}} >= 7:1, {{ACCENT}} dots/bar >= 3:1 on {{SURFACE}}, white text on the {{ACCENT}} bar >= 4.5:1)
- {{TEXT}} captions, titles, years - default #FFFFFF
- {{ACCENT}} timeline dots, CTA bar - default red #B8070B (dots #AD1217)
- {{ACCENT_2}} view badges, final 'hero' nodes - default green #117210
- {{SURFACE}} graphic panel - default near-black #050505 with a faint dot grid
- {{CARD_BG}} light hook panel - default light grey #E0DFDF (text near-black #0A090A)
- {{FONT_DISPLAY}} accent word in titles / concept names - default italic old-style serif (Instrument Serif Italic or EB Garamond Italic; local stand-in Playfair Display 400 italic)
- {{FONT_BODY}} captions, titles, labels - default Inter 700 (Bold)
- {{HANDLE}} - @handle (optional, small under the CTA)
- {{LOGO}} - not required; optional small mark on the CTA panel

Canvas 1080x1920, 24 fps.

LAYOUT
1. Split for ~70 % of runtime: graphic panel y 0-70 % on {{SURFACE}}; speaker in a rounded face card x 6-94 %, y ~73-100 %, radius ~4 % W. Full-face CU/MCU for every opinion or aside (~30 %, 38-180 frames each), alternating crop sizes.
2. One diagram for the whole video: a horizontal timeline with {{ACCENT}} node dots and big {{TEXT}} bold labels (ink 3.59 % H, centre y 55.7 %) that scrolls with directional motion blur (~10-14 frames, power2.inOut); branches grow into a category tree of small black pills with thin white outlines; pan node to node as each is discussed; recap with the winners in {{ACCENT_2}}.
3. Example cards (rounded thumbnails, {{ACCENT_2}} count badges like '1.2M') pop in with back.out(1.4) over ~8 frames.

CAPTIONS
4. Latin script, as spoken, punctuation kept; exactly ONE word on screen at a time; hard 1-frame swap on each spoken word, no fade, no gap, no colour emphasis.
5. {{FONT_BODY}}, {{TEXT}}, tracking 0, no stroke/box, soft shadow 0 2px 6px rgba(0,0,0,.5). Splits: 58 px, centred, centre y 66.4 % (gap above the face card). Full-face: 68 px, centre y 63 %.

OTHER TEXT
6. Section title on every split: two centred Title Case lines 'Headline here / Second line here', {{FONT_BODY}} 52 px, -0.02em, {{TEXT}} (near-black on {{CARD_BG}}), line centres y 7.0 % and 9.8 %, width 50-62 % W; one or two key words swapped to {{FONT_DISPLAY}} at the same cap height. Title changes per section.
7. Concept name on the full-face shot after the hook: {{FONT_DISPLAY}} ~75 px (verify width), x ~18-54 %, centre y 63.5 %.
8. Hook frame 1: {{CARD_BG}} panel with the title and a 3x3 grid of example thumbnails popping in, count badges by frame ~36; first cut to full-face at ~3 % of runtime.
9. CTA (last ~8 %): 'Comment' {{FONT_BODY}} + '"KEYWORD"' {{FONT_DISPLAY}} (ink 3.36 % H, x 20-81 %, centre y 8 %), then 'To Get The Doc' {{TEXT}} bold (ink 2.89 % H) on a solid {{ACCENT}} bar x 20-80 %, y 10.5-14.5 %, over a grid of document-page thumbnails.

GRADE: Grade from the user's footage (video-style / grade.py); target look: dark low-key studio, high-contrast, muted, warm lamp bokeh, cool desaturated shadows.
SOUND: voice only at about -14 LUFS (keep true peak <= -1 dBTP); optional soft whoosh on timeline scrolls.

VERIFY before rendering (px values were render-verified with Inter; if the brand font differs, adjust px until the numbers match):
a) Render test frames over {{SURFACE}}: "education" ({{FONT_BODY}} 58 px), "video" ({{FONT_BODY}} 68 px), a two-line test title "Headline here" (52 px) and "KEY WORD" in {{FONT_DISPLAY}} at 75 px.
b) Measure: python video-reference-match/scripts/caption_probe.py <test render or snapshot> --out <dir> --at <t> --box 0.3,0.645,0.7,0.685 --ink "{{TEXT}}:60" (split caption); --box 0.3,0.605,0.7,0.65 (full-face caption); --box 0.15,0.055,0.85,0.083 (title line 1); --box 0.15,0.6,0.6,0.655 --ink "{{TEXT}}:70" (serif word).
c) Required: "education" ink 2.19 % +-0.5 of H and 24.6 % +-2 of W; "video" 2.58 % +-0.5 and 15.7 % +-2. For the title and serif word compute expected ink with python video-reference-match/scripts/fit_font.py --font "<font>" --word "<word>" at the px above (serif target cap-to-descender ink ~3.9 % H for a 1-word name).
```

### B23 · talking-head · Hinglish · score 3

Landscape walk-and-talk: one-word captions, flash-burst hook, corner titles with accent swash-italic word.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B23 (video-reference-match/references/blueprints/B23.json) to this brand.
Native canvas 1920x1080 at 30 fps (sizes below give the 16:9 px and the 1080x1920 px for a 9:16 reframe).

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} >= 4.5:1 on the chest; {{ACCENT}} gradient must stay >= 3:1 on the background behind the title, e.g. dark foliage or walls)
- {{TEXT}}: default #FFFFFF (captions, title sans line, end-card wordmark)
- {{ACCENT}}: default #F5D34C (gold gradient light stop)
- {{ACCENT_2}}: default #E0A820 (gold gradient deep stop)
- {{SURFACE}}: none (footage)
- {{CARD_BG}}: default #000000 (end card)
- {{FONT_DISPLAY}}: default Playfair Display 700 italic (a swash italic/script is closer)
- {{FONT_BODY}}: default Inter 500
- {{HANDLE}}: not used
- {{LOGO}}: monogram for the end card

CAPTIONS
1. Latin, as spoken, lowercase except 'I'; no punctuation, no emoji.
2. One word at a time: {{FONT_BODY}} at 43 px on 1920x1080 (76 px on 1080x1920), {{TEXT}}, no stroke, no shadow, no box, tracking 0; centred, centre y 55.7 % H (chest), same position over b-roll.
3. Hook only (first ~7 % of runtime): the opening sentence accumulates in ONE widely spaced line at ~55 % H; each word gets a fixed slot with ~3-5 % W gaps (16:9: x 15-80 %; 9:16: inside x 8-92 %); each word fades in over 2 frames.
4. Each word hard-cuts in 0-6 frames after its spoken start and out when the next starts; no idle motion.

CORNER TITLES (2-3 per minute, for the key phrase)
5. Two lines beside the head, never over the face. Line 1: {{FONT_BODY}} at 79 px on 16:9 (140 px on 9:16), {{TEXT}}, sentence case 'lead words', left edge 8.6 % W, y 17-23 % (9:16: left 8 % W, y 15-21 %). Line 2: the KEY WORD in {{FONT_DISPLAY}} at 170 px on 16:9 (302 px on 9:16), vertical gradient {{ACCENT}} -> {{ACCENT_2}}, starting ~3-9 % W further left and tucked under line 1 (y 25-36 %); any trailing word in the white sans.
6. Title words fade in one by one (~3 frames each, slight blur-in), hold 2-3 s, hard cut out.

EDIT DEVICES
7. Right after the first line: 4 b-roll shots of ~15 frames each (flash burst).
8. Alternate WS and MS (~130 %) every 1.5-3 s; intercut founder-at-work b-roll for ~25 % of runtime, 1-2.3 s per shot.
9. Twice per piece, a half-frame split wipe (b-roll | presenter) as the transition.
10. End card (last ~10 %): {{CARD_BG}}, {{LOGO}} monogram (~7 % W on 16:9, ~20 % W on 9:16) centred at 48 % H, letter-spaced caps brand name (~1.5 % H, tracking ~0.4em) at 54.5 % H. No lower-thirds, no emoji.

GRADE: Grade from the user's footage (video-style / grade.py); target look: natural daylight, moderate saturation, soft mid contrast, neutral-warm.
SOUND: calm music bed (~72 bpm) under the voice, carrying the end card; keep true peak below -1 dBTP; -14 LUFS.

VERIFY
a) Render the caption word "and" at 43 px on 1920x1080 (or 76 px on 1080x1920) over a dark area at 55.7 % H and measure:
   python video-reference-match/scripts/caption_probe.py <test_render> --out <dir> --at <t> --box 0.4,0.5,0.6,0.61 --ink "{{TEXT}}:60"   (default ink #FFFFFF)
   Required (16:9 frame): 2.65 % ±0.5 of H, 4.5 % ±2 of W; "processes" 2.79 % H, 13.0 % W.
b) Corner title: render "grow" in {{FONT_DISPLAY}} at 170 px (16:9) and measure with --ink "{{ACCENT}}:90": 11.0 % ±0.5 H, 22.2 % ±2 W.
c) Expected ink for any other word: video-reference-match/scripts/fit_font.py --font "{{FONT_BODY}}" --word <word> --canvas 1920x1080.
```

### B35 · talking-head · English · score 3

Single locked-off standing take carried only by progressive word-by-word captions that fade in white on the chest; credential-stack hook and spoken numbered signposts.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B35 (video-reference-match/references/blueprints/B35.json) to this brand.
Canvas 1080x1920, 30 fps. All positions are % of frame; px are at 1080x1920.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} must stay >= 4.5:1 on the speaker's top where it sits, with the thin dark outline)
- {{TEXT}}      caption words                          default #FFFFFF
- {{ACCENT}}    none (no highlight colour; the dim look is only the fade)  default none
- {{ACCENT_2}}  caption outline                        default near-black (#111111)
- {{SURFACE}}   none                                   default none
- {{CARD_BG}}   none                                   default none
- {{FONT_DISPLAY}} captions                            default Inter 800 (bold grotesque; alt Figtree Bold / Plus Jakarta Sans Bold)
- {{FONT_BODY}}    same as display                     default Inter 800
- {{HANDLE}}    not shown
- {{LOGO}}      not shown

CAPTIONS
1. English as spoken, sentence case (capital at a sentence start); keep commas, full stops, apostrophes.
2. Phrases of up to ~7 words over at most 2 centred lines, max line width ~55 % W (~595 px). Lay out the whole phrase first (line breaks and centring fixed), then reveal word by word as spoken; earlier words never move.
3. Type: {{FONT_DISPLAY}} at 50 px, line pitch 60 px, tracking 0, {{TEXT}}, thin {{ACCENT_2}} outline ~2 px (paint-order stroke or a 1 px 4-direction text-shadow), no blurred shadow, no box.
4. Position: centred; the first line's ink top fixed at 61.0 % of height (y ~1171 px): one line centres at 62.2 %, a second line grows downward (centre 63.7 %). Keep it on the speaker's chest / dark clothing.
5. Per-word animation: opacity 0 -> 0.11 -> 0.20 -> 0.30 -> 0.41 -> 0.57 -> 0.73 over 6 frames, then snap to 1.0 on frame 7 (ease-in); start 2-9 frames after the word's transcript start. No scale, slide or blur. When the phrase is complete, cut it out on one frame, leave the band empty ~4 frames, then start the next phrase.
6. No colour highlight and no idle motion.

OTHER TEXT
7. None: no title, lower third, sticker, CTA card or end card.

EDIT DEVICES
8. Keep one locked-off thigh-up take; trim only head and tail. Script shape: credential stack + failure twist in the first ~5 % of runtime, the question by ~10 %, then numbered points with spoken signposts every ~15-20 % of runtime, one-word sign-off. (For a faster cut, add a punch-in every ~90-150 frames without moving the caption position.)

GRADE
9. Grade from the user's footage (video-style / grade.py); target look: mid-contrast, muted, warm-leaning natural daylight; flat, ungraded feel.

AUDIO
10. Dry voice only, no music, no SFX; keep natural short pauses. Master to about -14.0 LUFS, true peak <= -1 dBTP.

VERIFY before rendering
a) Render a test frame with a fully built one-line caption "KEY WORD" over a dark area and measure:
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.2,0.585,0.8,0.67 --ink "{{TEXT}}:60"
b) Expected ink: video-reference-match/scripts/fit_font.py with {{FONT_DISPLAY}} at 50 px (reference: lines with descenders 2.42 % H, without 1.88 % H). Required: within ±0.5 % H; first-line ink top at 61.0 % ±0.5; colour equal to {{TEXT}}. Check a mid-fade frame: the word at frame 6 of its ramp must read at ~73 % opacity.
```

### B27 · mixed · English · score 2

Question-hook comparison test: front-loaded roll-call cuts, then repeated identical POV test rounds under a one-word-at-a-time uppercase white caption rail.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B27 (video-reference-match/references/blueprints/B27.json) to this brand.
Canvas 1080x1920, 30 fps. All positions are % of frame; px are at 1080x1920.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} must stay >= 3:1 on the footage at 68.5 % height, helped by the tight shadow)
- {{TEXT}}      caption words and pinned label          default #FFFFFF
- {{ACCENT}}    none (no emphasis colour; do not add one) default none
- {{ACCENT_2}}  none                                     default none
- {{SURFACE}}   none                                     default none
- {{CARD_BG}}   pinned-label square                       default #FFFFFF (same as {{TEXT}})
- {{FONT_DISPLAY}} caption words                         default Poppins 900 (heavy geometric caps; Montserrat Black slightly wider)
- {{FONT_BODY}}    pinned spec label                     default Poppins 700
- {{HANDLE}}    not shown
- {{LOGO}}      not shown (the label pins under the product's own logo)

CAPTIONS
1. English as spoken, ALL UPPERCASE. Strip commas, full stops and question marks; keep apostrophes (LET'S). Spell numbers as spoken (e.g. "10x" -> TEN, TIMES).
2. Exactly ONE word on screen at a time; every spoken word captioned (including THE, CAN, SO). Never two words, never two lines.
3. Type: {{FONT_DISPLAY}} at 42 px, letter-spacing +0.05em, {{TEXT}}, no stroke, no box, tight soft dark shadow 0 1px 6px rgba(0,0,0,.55).
4. Position: centred horizontally (x 540 px), vertical centre 68.5 % of height (y ~1315 px), the same spot in every shot.
5. Animation: hard cut in at full size and opacity 0-7 frames after the word's transcript start (never early); hard cut out when the next word replaces it. No fade, pop, scale, slide, highlight or idle motion.
6. Drop captions during 10-12-frame product roll-call inserts and on wordless pointing / establishing shots.

OTHER TEXT
7. Object-pinned spec label when the hero product is held to camera (~77 frames): a {{CARD_BG}} square (~45x45 px) then a short spec label ("Label here") in {{FONT_BODY}} ~39 px, {{TEXT}}, tracking 0.05em, no shadow, pinned just under the product's logo (reference: square x 37.5 %, text x 44-64 %, centre y 58.5 %) and tracked so it moves and scales with the object. Square grows from a dot at its bottom-left over 6 frames; characters appear right-to-left with very wide letter-spacing collapsing to normal over ~22 frames; exit: characters delete right-to-left while the square shrinks to a dot over ~9 frames, before the cut.
8. No title cards, lower thirds, stickers, CTA or end card.

EDIT DEVICES
9. Hook: yes/no stakes question in the first word; ~9 cuts in the first 300 frames, including a roll-call of each contender at 10-12 frames as it is named. Then relax to ~12 cuts/min.
10. Body: identical POV framing for every contender's round; cut on hand/device motion (motion blur hides the cut); voice continuous across cuts (J/L). Give the hero the longest take; end on an unresolved reaction, no CTA.

GRADE
11. Grade from the user's footage (video-style / grade.py); target look: warm, mid-contrast, natural saturation; moody LED-backlit intro, bright natural daylight for the test rounds.

AUDIO
12. Light continuous bed or ambience under the VO; a hit/whoosh on most hard cuts and every roll-call flash. Master to about -14.1 LUFS, true peak <= -1 dBTP.

VERIFY before rendering
a) Render a test frame with the caption "ACTUALLY" (and then "WORST") over a dark area and measure:
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.35,0.66,0.65,0.72 --ink "{{TEXT}}:45"
   Required at the default font: "ACTUALLY" ink 1.56 % ±0.5 of height and 23.2 % ±2 of width; "WORST" 1.56 % H, 15.0 % W; centre y 68.5 % ±0.5. With a brand font, compute the expected ink with video-reference-match/scripts/fit_font.py ({{FONT_DISPLAY}}, 42 px, +0.05em) and match it within ±0.5 % H.
```

## phrase-plain

_whole phrase at once, plain text_

### B26 · talking-head · English · score 4

Tier-list over one static shot: S-E board in the lower 40 %, icon cards pop to centre then drop into rows; persistent black-box title.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B26 (video-reference-match/references/blueprints/B26.json) to this brand.
Canvas 1080x1920, 30 fps (reference 29.97). All positions are % of frame; px are at 1080x1920.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} >= 7:1 on {{CARD_BG}}; the tier ramp must stay a clear hot-to-cool order from {{ACCENT}} (top tier) to {{ACCENT_2}} (bottom tier) with dark letters >= 4.5:1 on each tile)
- {{TEXT}}      captions, title text, icon cards       default #FFFFFF
- {{ACCENT}}    top-tier (S) label tile                default #FC7E7E (A #FEBD7E, B #FCDC7F, C #FCFC7F, D #BEFD7F interpolate)
- {{ACCENT_2}}  bottom-tier (E) label tile             default #80FE81
- {{SURFACE}}   tier board panel                       default #1A1A17
- {{CARD_BG}}   title box                              default #060606
- {{FONT_DISPLAY}} title                               default Inter 700 (tight neo-grotesque, -0.05em)
- {{FONT_BODY}}    captions, card labels               default Inter 600 (-0.05em)
- {{HANDLE}}    not shown
- {{LOGO}}      optional small mark inside the board's corner; item icons are the brand's own illustrations

CAPTIONS
1. English as spoken, sentence case as transcribed; keep full stops and other punctuation.
2. 1-2 words per caption, one line, replaced as a unit.
3. Type: {{FONT_BODY}} at 60 px, letter-spacing -0.05em (letters nearly touch), {{TEXT}}, no stroke, no box, faint shadow 0 2px 6px rgba(0,0,0,.25).
4. Position: centred, centre at 50.2 % of height (y ~964 px), in the gap between the chin and the board top (54.6 %). Same spot on the clean CTA shot.
5. Animation: hard cut in on the word (up to 2 frames early), hard cut out on the next caption. No fade, pop, slide, highlight or idle motion.

OTHER TEXT
6. Persistent title for the whole main shot: 2 centred lines ("Question Title / Goes Here?") in {{FONT_DISPLAY}} at 70 px, tracking -0.05em, {{TEXT}}, Title Case, on a solid {{CARD_BG}} square-cornered rectangle x 23-76 %, y 7.5-16.8 % (~18 px padding), line pitch 4.7 % H; on from frame 0, static, removed at the cut to the CTA shot.
7. Tier board: {{SURFACE}} rounded panel x 11.4-87.5 %, y 54.6-92.0 %, six equal rows separated by thin dark lines; left label column (to x 25.3 %) with flat tiles from {{ACCENT}} (S) through A/B/C/D to {{ACCENT_2}} (E), each with a small dark letter. Items are white rounded icon cards (~9.5 % W) with a tiny dark label, placed left to right in their row.
8. Card animation: rise from below the board into the centre at ~2x size with strong vertical motion blur over ~8 frames, hold until the tier is spoken, then shrink and fly into its row slot in 2-3 frames; next card every ~66 frames.
9. CTA: hard cut to the same framing with all graphics removed for the final ~7 %; captions only.

EDIT DEVICES
10. One static MCU for the main shot; no punch-ins. Script cadence: item, tier, reason of 6 words or fewer; include one or two spicy ratings; the last item gets the longest reason.

GRADE
11. Grade from the user's footage (video-style / grade.py); target look: warm, high-contrast, muted, lamp-lit, natural skin.

AUDIO
12. Voice only; soft pop on each card arrival and a short tick as it lands in its row. Master to about -14.1 LUFS, true peak <= -1 dBTP.

VERIFY before rendering
a) Render a test frame with the caption "in the" over a dark area (not a white shirt) and measure:
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.3,0.47,0.7,0.535 --ink "{{TEXT}}:20"
   Required at the default font: "in the" ink 2.34 % ±0.5 of height and 12.1 % ±2 of width; centre y 50.2 % ±0.5. With a brand font, compute the expected ink with video-reference-match/scripts/fit_font.py ({{FONT_BODY}}, 60 px, -0.05em).
b) Title: render "KEY WORD" on each line; expected ink 2.89 % H per caps-height line at the default font (or the fit_font.py value for {{FONT_DISPLAY}} at 70 px); box edges within ±1 %.
```

### B33 · talking-head · Hinglish · score 4

Selfie breakdown: top proof window over accent divider, plain captions, accelerating screenshot montage.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B33 (video-reference-match/references/blueprints/B33.json) to this brand.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship — text and accent must stay >= 4.5:1 / >= 3:1 against what sits behind them on the footage):
- {{TEXT}}      default #FFFFFF (captions)
- {{ACCENT}}    default #FDF677 (split divider bar)
- {{ACCENT_2}}  default #EBE97E (screenshot card border)
- {{SURFACE}}   default #EAEADE (light-grey panel behind screenshot cards)
- {{CARD_BG}}   default #DADEE4 (light-grey ground behind full-screen post captures)
- {{FONT_DISPLAY}} default Inter 600
- {{FONT_BODY}}    default Inter 600
- {{HANDLE}}    default @handle
- {{LOGO}}      default the brand's logo file (transparent PNG/SVG)
Divider and border are chrome, not text: keep them clearly visible (>= 3:1) against both the B-roll and the face below.
Canvas 1080x1920, 25 fps (scale frame counts if the project fps differs).

CAPTIONS
1. Roman script / English as spoken, sentence case (capitals at sentence starts and for names); full stops at sentence ends; numbers as digits. No emoji, no key-word colour.
2. One line of 2-4 words per caption, whole phrase at once; break at phrase / sentence boundaries.
3. Type: {{FONT_BODY}} at 65 px, {{TEXT}}, tracking +0.02 em, no stroke / box, soft drop shadow 0 2px 6px rgba(0,0,0,.5). Centred, ink centre at 80.3 % H, max ~66 % W. Same position on every layout.
4. Animation: none — hard cut on, hard cut off. Mid-sentence chunks replace each other directly; 4-5 empty frames between sentences; sentence-start captions may land ~8 frames after the spoken word.

OTHER TEXT / LAYOUT
5. Split screen while talking (~54 % of runtime): B-roll window 0-35 % H, talking head below, separated by a solid {{ACCENT}} bar 8 px tall at 35.1-35.5 % H. Swap the top visual every ~25-50 frames in the hook.
6. Screenshot proof: {{SURFACE}} panel in the top third with the screenshot framed by a ~6 px {{ACCENT_2}} border, x 7-95 %, y 6-27 %.
7. Post-capture montage (~65-91 % of runtime): full-screen {{CARD_BG}} with each capture in a rounded card (radius ~3 % W), x 7-93 %, y 7-90 %, original UI kept; 8-75 frames per card, accelerating; ~44 % short soft swaps. Captions stay on top at 80.3 %.
8. Payoff: back to full-frame face for the last ~9 % with a comment question. No {{LOGO}} or end card ({{HANDLE}} optional).

GRADE
Grade from the user's footage (video-style / grade.py); target look: high-contrast, natural-saturation, warm front-camera look.

VERIFY before rendering
a) Render a test caption 'KEY WORD here now' and measure: python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.08,0.765,0.92,0.835 --ink "{{TEXT}}:50"
b) python3 video-reference-match/scripts/fit_font.py --font "Inter 600" --word "<line with ascenders and descenders>" --ink 3.12 --tracking 0.02 -> ~64-65 px; a ~23-character 4-word line reads ~62 % W. Tolerance ±0.5 % H, ±2 % W; measure over dark clothing. (fit_font.py needs a target: --ink and/or --width; it returns the px that reproduces that ink for YOUR word plus the width it will read at that px. Requires Pillow.)
c) Positions within ±1 % H: caption centre 80.3 %, divider 35.1-35.5 %.
```

### B45 · mixed · English · score 4

Split-panel framework explainer: UI-mock proof for every claim, accent counting badges, numbered chapter card, chunk captions, accent-underlined italic-serif titles.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B45 (video-reference-match/references/blueprints/B45.json) to this brand.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} on {{SURFACE}} >= 7:1, white numbers on {{ACCENT}} badges >= 4.5:1, {{ACCENT}} underline >= 3:1 on {{SURFACE}})
- {{TEXT}} captions + titles - default #FFFFFF (near-black #0A0A0A on {{CARD_BG}} panels)
- {{ACCENT}} counter badges, step labels, active chapter bar, title underline - default red #B20F14
- {{ACCENT_2}} highlight ring / mechanism ring - default lime #C9DC32 (a green ring is fine)
- {{SURFACE}} graphic panel - default near-black #020202 with a faint grid
- {{CARD_BG}} alternate light panel + CTA card - default light grey #DDDCD9 with a dot grid
- {{FONT_DISPLAY}} italic accent word / coined term - default italic old-style serif (Instrument Serif Italic or EB Garamond Italic; local stand-in Playfair Display 400 italic)
- {{FONT_BODY}} captions, titles, labels - default Inter 800 (ExtraBold)
- {{HANDLE}} - @handle (profile-card mocks, optional)
- {{LOGO}} - optional, on the video-player mock in the CTA

Canvas 1080x1920, 24 fps.

LAYOUT
1. Split for ~77 % of runtime: animated graphic panel y 0-70 % on {{SURFACE}} (a few panels on {{CARD_BG}} for variety); speaker in a rounded face card x 5.5-94.5 %, y ~70.5-100 %, radius ~3 % W. Full-face MCU for ~23 % (14-113 frames each) for opinions and transitions; alternate faster (every 24-72 frames) in the middle of the longest step.
2. Proof for every claim as a UI mock-up in the panel: profile cards, video-player mocks with view counts, phone mock, thumbnail grids, funnel. Numbers sit in {{ACCENT}} rectangular badges with white bold digits that count up (power2.out over ~60-84 frames).
3. Chapter card at each step change: 'Framework name' with 01 / 02 / 03; the active step in a solid {{ACCENT}} bar.
4. Hook frame 1: title + avatar orbit with an {{ACCENT}} counter badge climbing ~10x in ~84 frames and a launch move; first full-face cut at ~3 % of runtime naming the method in {{FONT_DISPLAY}}.

CAPTIONS
5. Latin script, as spoken, punctuation kept, numbers as digits; 1-3-word meaning chunks, one line.
6. {{FONT_BODY}}, -0.02em, {{TEXT}}, no stroke/box, very soft shadow 0 2px 6px rgba(0,0,0,.5); centred at y 64.4 %; 54 px on splits, 68 px on full-face; near-black on {{CARD_BG}} panels.
7. Hard-cut chunk swaps ~2 frames after the chunk's first word, no gap, no emphasis colour.
8. Once, the coined term replaces the caption on a full-face shot in {{FONT_DISPLAY}} (~56-69 px, verify), centred at y 64.4 %.

OTHER TEXT
9. Section title on every split: 'Headline here' (line 1, {{FONT_BODY}} 58 px, centre y 10 %, x ~22-78 %) / 'Second line here' (line 2, ~15 % larger, y ~12-15.5 %, x ~17-84 %), last word of line 2 in {{FONT_DISPLAY}}, thin {{ACCENT}} underline at y ~15.6 % spanning line 2.
10. Recap: bar chart with the viewer's bar ('YOU') tallest.
11. CTA (last ~6 %): {{CARD_BG}} card, black 'Comment' + {{FONT_DISPLAY}} '"KEYWORD"' / 'To Get This Video' (2 centred lines, y ~11-19 %, x 15-84 %) above a video-player mock with {{LOGO}}/{{HANDLE}} in the channel row; caption continues in near-black.

GRADE: Grade from the user's footage (video-style / grade.py); target look: dark low-key studio, high-contrast, muted, warm bokeh, cool desaturated shadows.
SOUND: dense voice at about -14 LUFS; counter tick/roll under badges, soft whoosh on panel transitions.

VERIFY before rendering (px values were render-verified with Inter; if the brand font differs, adjust px until the numbers match):
a) Render test frames over {{SURFACE}}: "a personal brand" ({{FONT_BODY}} 54 px), "KEY WORD" as a full-face caption (68 px), a title line "Headline here" (58 px), and "KEY WORD" in {{FONT_DISPLAY}} (~56-69 px).
b) Measure: python video-reference-match/scripts/caption_probe.py <test render or snapshot> --out <dir> --at <t> --box 0.2,0.62,0.8,0.67 --ink "{{TEXT}}:60" (caption); --box 0.15,0.088,0.85,0.118 --ink "{{TEXT}}:70" (title line 1); --box 0.15,0.615,0.85,0.672 --ink "{{TEXT}}:70" (serif callout).
c) Required: "a personal brand" ink 2.58 % +-0.5 of H and 37.9 % +-2 of W. For the full-face caption, title and serif callout compute expected ink with python video-reference-match/scripts/fit_font.py --font "<font>" --word "<text>" at the px above (targets: full-face caption cap+descender ~3.4 % H, title line ~2.7 % H, serif ~3.4 % H).
```

### B25 · talking-head · English · score 3

Low-effort repurposing template: near-square footage letterboxed in black 9:16, fixed two-line pain headline on top, plain two-line captions.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B25 (video-reference-match/references/blueprints/B25.json) to this brand.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} on {{SURFACE}} >= 7:1, captions >= 4.5:1 on the footage with the shadow)
- {{TEXT}} headline + captions - default #FFFFFF
- {{ACCENT}} - default #FFFFFF (this blueprint has no colour emphasis; a brand accent may tint '!!' or one headline word at most)
- {{ACCENT_2}} - none
- {{SURFACE}} letterbox bars - default #000000
- {{CARD_BG}} - none
- {{FONT_DISPLAY}} headline - default Poppins 700 (Montserrat Bold is closer to the original width)
- {{FONT_BODY}} captions - default Poppins 500 (Montserrat SemiBold closer)
- {{HANDLE}} - @handle (optional, small in the empty bottom bar)
- {{LOGO}} - optional, small in the bottom bar

Canvas 1080x1920, 30 fps (29.97).

LAYOUT
1. {{SURFACE}} 9:16 canvas; the speaker footage scaled into a near-square (~1.09:1) window 1080x995 px at y 463-1457 px (24.1-75.9 % H), bars above and below.
2. Fixed headline for 100 % of runtime in the top bar: 2 centred lines 'Pain point headline / because of this!!', {{FONT_DISPLAY}} 64 px, {{TEXT}}, no shadow/box; line centres y 16.7 % (x ~11-89 %) and 20.8 % (x ~16-84 %).
3. Cuts move between camera angles (front MS, angled MS, tighter MCU) at a ~111-frame median shot length; allow one long hold for the core lesson; short dissolves or straight cuts on phrase boundaries; no punch-ins, no B-roll, no graphics.
4. End: last ~9 frames black with only the headline (loop-back).

CAPTIONS
5. Latin script, sentence case as spoken, profanity masked with asterisks.
6. 3-7 words per caption split over 2 lines (short line 1, longer line 2), {{FONT_BODY}} 47-48 px, {{TEXT}}, tracking 0, no stroke/box, soft shadow 0 2px 6px rgba(0,0,0,.5); centred, line centres y 61.3 % and 64.3 % (1177 px / 1235 px), i.e. the bottom quarter of the window.
7. Whole phrase hard-cuts in 0-4 frames after its first word and hard-cuts to the next phrase with no gap; no emphasis, no animation.

GRADE: Grade from the user's footage (video-style / grade.py); target look: high-contrast, muted, cool background with natural skin.
SOUND: voice only at about -14 LUFS; keep short breath pauses; no SFX.

VERIFY before rendering (px values were render-verified with Poppins; with Montserrat or another face, adjust px until the numbers match):
a) Render a test frame with the caption "When you" / "KEY WORD" and the headline "Headline here" over the black bar / a dark area.
b) Measure: python video-reference-match/scripts/caption_probe.py <test render or snapshot> --out <dir> --at <t> --box 0.25,0.595,0.75,0.627 --ink "{{TEXT}}:60" (caption line 1); --box 0.05,0.15,0.95,0.185 --ink "{{TEXT}}:60" (headline line 1).
c) Required: "When you" ink 2.27 % +-0.5 of H and 22.8 % +-2 of W. For the second caption line and the headline compute expected ink with python video-reference-match/scripts/fit_font.py --font "<font>" --word "<line>" at 47-48 px / 64 px (headline target ink ~3.3 % H).
```

### B17 · podcast-clip · English · score 2

Micro question-to-answer clip: whip to guest, light lowercase captions beside the speaker.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B17 (video-reference-match/references/blueprints/B17.json) to this brand.
Native canvas 1920x1080, 30 fps (for 1080x1920: reframe to the speaker, keep the same px, centre the caption at x 50 %, ~50 % H).

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: light-weight {{TEXT}} needs >= 7:1 on the dark area beside the speaker because it has no box)
- {{TEXT}}: default #FFFFFF
- {{ACCENT}}: none (no emphasis colour)
- {{ACCENT_2}}: none
- {{SURFACE}}: none (footage)
- {{CARD_BG}}: none
- {{FONT_DISPLAY}}: none
- {{FONT_BODY}}: default Inter 300 (Mulish Light / Nunito Sans Light closer)
- {{HANDLE}}: not on screen
- {{LOGO}}: none (optional branded microphones in shot)

CAPTIONS
1. Latin, as spoken, ALL lowercase (including sentence starts and 'i'); apostrophes kept; no other punctuation; no emoji.
2. 1-4 words per phrase (median ~3), one line; hold single words on slow speech.
3. {{FONT_BODY}} at 81 px on 1920x1080, {{TEXT}}, tracking 0, no stroke, no box, at most a very faint soft shadow.
4. 16:9: line centre x ~39 % W (in the empty space beside the speaker; ~44 % on a centred framing), centre y 50.5 %, line top 47 %, max width 41 % W. 9:16 reframe: centred x 50 %, ~50 % H, same px.
5. Hard cut in ~1 frame after the first word, hard cut out on the next phrase; captions continue through the whip and do not move with the punch-in.

EDIT DEVICES
6. Host asks the question in the first ~20 % of runtime; ~10-frame motion-blur whip to the guest; the answer follows immediately.
7. One soft ~110 % punch-in on the answer's second sentence; 3 shots total; end on the quotable line. No titles, lower-thirds, b-roll or end card.

GRADE: Grade from the user's footage (video-style / grade.py); target look: dark low-key, warm practicals, deep blacks, muted saturation, skin as the brightest element.
SOUND: voice only, -14 LUFS, true peak <= -1 dBTP (do not let peaks clip).

VERIFY
a) Render "KEY WORD" in lowercase-style light weight at 81 px on 1920x1080 at the caption position and measure:
   python video-reference-match/scripts/caption_probe.py <test_render> --out <dir> --at <t> --box 0.18,0.44,0.6,0.58 --ink "{{TEXT}}:70"   (default ink #FFFFFF)
   Expected ink for any phrase from video-reference-match/scripts/fit_font.py --font "{{FONT_BODY}}" --word "<phrase>" --canvas 1920x1080; a 4-word lowercase line with descenders should be ~7 % H and ~38 % W, a 2-word line ~5.6 % H.
b) Line centre ~39 % W, ~50.5 % H on 16:9.
```

## other:editorial-build

_editorial build_

### B47 · podcast-clip · English · score 4

Editorial podcast layout: top-left word build, giant accent key phrases, rounded footage card.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B47 (video-reference-match/references/blueprints/B47.json) to this brand.
Canvas 1080x1920, 30 fps. Off-white editorial canvas; footage lives in a card.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} >= 7:1 on {{SURFACE}}; {{ACCENT}} >= 4.5:1 on {{SURFACE}}; the preview grey {{ACCENT_2}} must read clearly lighter than {{TEXT}})
- {{TEXT}}: default #2F2E2C (running lines)
- {{ACCENT}}: default #C34479 (giant key phrases, list totals)
- {{ACCENT_2}}: default #CECBC7 (next-word preview grey)
- {{SURFACE}}: default #F3F1ED (off-white canvas)
- {{CARD_BG}}: default #000000 (proof inserts; running line turns white there)
- {{FONT_DISPLAY}}: default Inter 800 (key phrases)
- {{FONT_BODY}}: default Inter 600 (running lines)
- {{HANDLE}}: not on screen
- {{LOGO}}: optional, only inside the web-page proof inserts

CAPTIONS (editorial build)
1. Latin, as spoken, lowercase (sentence case after a full stop); no punctuation in running lines; no emoji.
2. Left-aligned block, left edge 7.6 % W, first line centre ~17.4 % H, line pitch 5.2 % H, max width 78 % W; 2-4 words per line, up to 4 lines; the block clears at each layout change.
3. {{FONT_BODY}} at 80 px, tracking -0.02em, no stroke/shadow/box. The NEXT word appears early in {{ACCENT_2}}; on its spoken word it turns {{TEXT}} and lands with a 1-frame horizontal motion blur sliding ~2 % W from the right.
4. One key phrase per ~8-10 s in {{FONT_DISPLAY}} at 166 px (smaller when sharing the top with the card), {{ACCENT}}, tracking -0.04em, always ending with a full stop, stacked directly under the dark lines on the same left edge; lands ~4 frames before its word with the same blur.
5. On {{CARD_BG}} inserts the running line turns white.

LAYOUT AND EDIT DEVICES
6. Footage in a rounded card x 7.5-92.5 %, y 45-93 %, radius ~24 px, soft drop shadow, on {{SURFACE}}.
7. Spoken numbers -> stat list replacing the card for ~3 s: rows of a big number (~5 % H) at x 7.5 % + label at x ~22 %; earlier rows mid-grey, the new total in {{ACCENT}} bold with a thin dark rule above it.
8. Proof inserts (~3-4 s): {{CARD_BG}} screen with the brand's web page / stat tiles under the running caption.
9. Every transition is a soft layout crossfade (~8-12 frames); no hard cuts, no punch-ins.
10. End on a text-only frame on {{SURFACE}}: lead line at 36 % H, the hook's KEY WORD phrase in {{ACCENT}} at 39.5-58 % H, left 8 %.

GRADE: Grade from the user's footage (video-style / grade.py); target look: muted warm studio footage with natural skin under a clean off-white, high-contrast editorial frame.
SOUND: voice-led and compressed; any bed at least ~20 dB under speech; -14 LUFS.

VERIFY
a) Render the running line "it's always been" at 80 px on {{SURFACE}} and measure:
   python video-reference-match/scripts/caption_probe.py <test_render> --out <dir> --at <t> --box 0.05,0.14,0.9,0.21 --ink "{{TEXT}}:60"   (default ink #2F2E2C)
   Required: 3.91 % ±0.5 of H, 50.0 % ±2 of W.
b) Key phrase: render "KEY WORD." in {{FONT_DISPLAY}} at 166 px with --ink "{{ACCENT}}:70"; expected ink from video-reference-match/scripts/fit_font.py --font "{{FONT_DISPLAY}}" --word <word> (a 9-letter lowercase word should be ~6.9 % H, ~66 % W).
c) If {{FONT_BODY}} is not Inter 600, re-solve with fit_font.py --font "{{FONT_BODY}}" --word "it's always been" --ink 3.91 --width 50.0 --tracking -0.02.
```

## other:meme-text

_meme text_

### B22 · skit · English · score 1

Phone meme: quoted ironic claim over deadpan selfie, then held three-line reality set-up.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B22 (video-reference-match/references/blueprints/B22.json) to this brand.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship — text and accent must stay >= 4.5:1 / >= 3:1 against what sits behind them on the footage):
- {{TEXT}}      default #FFFFFF (meme text)
- {{ACCENT}}    default #FFFFFF (no accent colour in this style; keep it white unless the brand insists)
- {{ACCENT_2}}  default none
- {{SURFACE}}   default none (text sits directly on footage)
- {{CARD_BG}}   default none
- {{FONT_DISPLAY}} default Poppins 500 (a lighter 300-400 geometric with single-storey a is closer)
- {{FONT_BODY}}    default same as display
- {{HANDLE}}    default @handle
- {{LOGO}}      default the brand's logo file (transparent PNG/SVG)
Text must stay >= 4.5:1 on the footage behind the 17-28 % band; pick shots with a darker upper third rather than adding a box.
Canvas 1080x1920, sizes are px at that canvas; frame counts at 30 fps.

CAPTIONS
1. No speech captions. The only text is two meme-text overlays in a native in-app text look.
2. Overlay 1 (ironic claim, over the hook shot, ~28 % of runtime): one line in curly double quotes, sentence case (placeholder '“Headline here”'), {{FONT_DISPLAY}} 54 px, {{TEXT}}, centred, ink centre at 26 % H.
3. Overlay 2 (the reality, from the first cut to the end, held across every following shot): 3 centred lines, sentence case, balanced breaks, ending in one native emoji (placeholder 'Set-up line here / lead words KEY WORD / closing words <emoji>'). Block 17-27.7 % H, line pitch 4.2 % H (line-height ~1.25), widest line ~53 % W.
4. Type: {{FONT_DISPLAY}} at 54 px, {{TEXT}}, tracking 0, no stroke / shadow / box; emoji at text size.
5. Animation: none. Overlay 1 on from frame 0; swapped for overlay 2 by hard cut exactly on the first shot cut; text never moves, fades or scales.

OTHER TEXT
6. None: no titles, {{LOGO}}, watermark or end card (add {{HANDLE}} only if the brand requires it, small, bottom-centre, outside the 17-28 % band).
7. Edit: 3-5 handheld phone shots, hard cuts on audio pauses, end on a quiet reaction shot (~25 % of runtime). Trend audio / music bed, no SFX.

GRADE
Grade from the user's footage (video-style / grade.py); target look: high-contrast, muted, warm; ungraded-phone daylight, natural skin.

VERIFY before rendering
a) Render overlay 1 and overlay 2 with the placeholders and measure:
   python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.2,0.235,0.8,0.28 --ink "{{TEXT}}:45"
   python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.15,0.16,0.85,0.30 --ink "{{TEXT}}:45"
b) python3 video-reference-match/scripts/fit_font.py --font "Poppins 500" --word "<your line>" --ink 2.97 -> ~54-55 px for a line with ascenders and descenders; widest set-up line must stay <= ~53 % W (read at_verified_px). Line tops ~4.2 % H apart. Measure over mid/dark background. (fit_font.py needs a target: --ink and/or --width; it returns the px that reproduces that ink for YOUR word plus the width it will read at that px. Requires Pillow.)
c) Positions within ±1 % H: overlay 1 centre 26 %, overlay 2 block 17-27.7 %.
```

### B24 · skit · Hinglish · score 1

Office skit: small two-line set-up text over boss, dropped for a wordless gesture gag.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B24 (video-reference-match/references/blueprints/B24.json) to this brand.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship — text and accent must stay >= 4.5:1 / >= 3:1 against what sits behind them on the footage):
- {{TEXT}}      default #FFFFFF (set-up text)
- {{ACCENT}}    default #FFFFFF (no accent in this style)
- {{ACCENT_2}}  default none
- {{SURFACE}}   default none
- {{CARD_BG}}   default none
- {{FONT_DISPLAY}} default Anton 400 (closer: a bold semi-condensed grotesque such as Barlow Semi Condensed SemiBold)
- {{FONT_BODY}}    default same
- {{HANDLE}}    default @handle
- {{LOGO}}      default the brand's logo file (transparent PNG/SVG)
The text is small and has no shadow: place it on a mid/dark wall area so it stays >= 4.5:1; never add a box.
Canvas 1080x1920, 30 fps.

CAPTIONS
1. No speech captions.

OTHER TEXT
2. Set-up text, first shot only: 2 centred lines of Roman Hinglish, sentence case — line 1 a situation line ending in a spaced hyphen, line 2 a short question (placeholder 'Headline here -' / 'KEY WORD here?'). {{FONT_DISPLAY}} ~41 px (line 2 ~42 px), {{TEXT}}, tracking -0.01 em, no stroke / shadow / box. Line 1 centre 18.4 % H, line 2 centre 21.2 % H (pitch 2.8 % H), block centre x ~50.6 %, on the empty wall above the head.
3. Timing: on from frame 0 with no animation; hard off ~4 frames before the first cut; the payoff shot has no text.
4. No {{LOGO}}, watermark or end card.
5. Edit: shot 1 = medium shot of the questioner (~22 % of runtime); hard cut mid-question to a static low over-the-shoulder wide held to the end; let a body crossing the lens close it.

GRADE
Grade from the user's footage (video-style / grade.py); target look: high-contrast, muted, neutral-warm; natural office light.

VERIFY before rendering
a) Render both lines with the placeholders and measure: python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.25,0.165,0.75,0.235 --ink "{{TEXT}}:50"
b) python3 video-reference-match/scripts/fit_font.py --font "Anton 400" --word "<line 2, lowercase with ascenders>" --ink 2.19 --tracking -0.01 -> ~41-42 px (the reference 3-word line 2 read 24.9 % W; line 1 of ~24 characters ~36 % W at ~40 px). Tolerance ±0.5 % H, ±2 % W. (fit_font.py needs a target: --ink and/or --width; it returns the px that reproduces that ink for YOUR word plus the width it will read at that px. Requires Pillow.)
c) Positions within ±1 % H: line 1 centre 18.4 %, line 2 centre 21.2 %.
```

## other:phrase-accent-word

_phrase accent word_

### B38 · talking-head · English · score 3

Static talking head; difference-blend white captions with one accent word; image cards above the head.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B38 (video-reference-match/references/blueprints/B38.json) to this brand.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship — text and accent must stay >= 4.5:1 / >= 3:1 against what sits behind them on the footage):
- {{TEXT}}      default #FFFFFF (caption white, rendered with a difference blend)
- {{ACCENT}}    default #E06A2C (key word / topic word orange)
- {{ACCENT_2}}  default none (not used)
- {{SURFACE}}   default #FDFDFD (end-card background)
- {{CARD_BG}}   default none (end-card text / icons are near-black #0C0C0C on {{SURFACE}})
- {{FONT_DISPLAY}} default Inter 800 (ExtraBold)
- {{FONT_BODY}}    default Inter 800 (ExtraBold)
- {{HANDLE}}    default @handle
- {{LOGO}}      default the brand's logo file (transparent PNG/SVG)
Accent must stay >= 3:1 on the footage behind the caption band; if the brand accent is dark, lift its lightness rather than changing the role.
Canvas 1080x1920, sizes below are px at that canvas; frame counts are at 25 fps (scale them if the project fps differs).

CAPTIONS
1. English as spoken, sentence case, keep commas / full stops at phrase ends. No emoji.
2. One phrase of 2-4 words per caption, ONE line, whole phrase at once. 0-1 key word per caption in {{ACCENT}}: the pain or outcome word; many captions have none.
3. Caption: {{FONT_BODY}} at 68 px, {{TEXT}}, tracking 0, no stroke / shadow / box, centred, ink centre at 80 % of height, max line width ~72 % W. Key word: same font, 68-69 px, {{ACCENT}}.
4. Put the caption layer in mix-blend-mode: difference (stays {{TEXT}} over dark clothing, inverts where hands pass under). Drop the blend if the caption band sits on light clothing.
5. Entry: slide up from +4 % H with motion blur and scale 1.1 -> 1.0, ease-out; sharp after 6 frames, settled by 10 (centre 84.8 -> 82.3 -> 81.4 -> 81.0 -> 80.8 % at +2/+4/+6/+8/+10 f). Previous caption hard-cuts out 0-1 frame before. Land each phrase on its first stressed word (<= 3 frames late). No idle motion.
6. Repeated-lead list beats: two-line lockup, lead words 114 px at centre 74.8 % over the shared noun ~62 px at 79.4 %, held while each list item drops in as a topic word (rule 8).

OTHER TEXT (only where the script has a matching beat)
7. Hook title (first ~7 % of runtime): series label in {{TEXT}} {{FONT_DISPLAY}} 103 px centred at 78.9 % H, slides up 2 % H with blur over 2 frames on the first word; '#N' pops in on the next line (centre 84.4 %, ~1.6x size, leading ~0.85) ~14 frames later.
8. Topic word: UPPERCASE {{FONT_DISPLAY}} 118-130 px (set per word, keep inside ~72 % W), {{ACCENT}}, centred at 22-23 % H above the head; drops in from ~1.5x scale, blurred and partly off the top edge, settles in ~6 frames exactly on its spoken word.
9. {{LOGO}} watermark top-right (x 76-92 %, y 5-10 %) from ~10 % of runtime to the end.
10. PIP image cards on the problem and outcome lines (75-150 frames each): rounded corners (~3 % W radius), x 3-97 %, y 5-35 %, scale-in with blur over ~8 frames; the face stays visible below.
11. Optional full-screen flat illustration (~110 frames) with a dark bottom gradient; captions continue in {{TEXT}} at 80 %.
12. Transitions: one zoom-blur punch-in to ~115 % (~12 frames) mid-claim and back out; a 5-frame light-leak flash before the CTA. Skip the hook dip-to-black.
13. End card (~50 frames, after an 8-frame dip to black): flat {{SURFACE}}, centred near-black geometric sans — headline at 25.9 % (ink 3.6 % H, ~76 % W), sub-line ~30 %, 'contact' line ~36 %, {{LOGO}} 44-62 %, follow prompt at 72.8 % (ink 2.4 % H), four rounded-square social icons ~78 %, website line ~82.5 %; 10-frame fade to black.

GRADE
Grade from the user's footage (video-style / grade.py); target look: high-contrast, muted, neutral-warm; natural clean skin.

VERIFY before rendering
a) Render a test caption 'KEY WORD problems' with 'problems' in {{ACCENT}}, the hook word 'Challenge' and the topic word 'RETENTION', then measure:
   python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.05,0.76,0.95,0.84 --ink "{{TEXT}}:60,{{ACCENT}}:55"
   python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.08,0.15,0.92,0.29 --ink "{{ACCENT}}:60"
   Expected (±0.5 % H, ±2 % W) with Inter 800: 'problems' 3.36 % H / 28.3 % W at 69 px; 'Challenge' 5.08 % H / 45.6 % W at 103 px; 'RETENTION' 4.69 % H / 61.0 % W at 118 px. Measure white text over a dark area only.
b) For other words or a non-Inter brand font: python3 video-reference-match/scripts/fit_font.py --font "<font weight>" --word "<word>" --ink <tier ink> [--upper] (caption 3.44 / key 3.36 / hook 5.08 / topic 4.69 --upper) -> use the returned px (Inter targets: caption 68, key 69, hook 103, topic 118-130, list lead 114 px) and expect at_verified_px.width_pct_of_W from the probe. (fit_font.py needs a target: --ink and/or --width; it returns the px that reproduces that ink for YOUR word plus the width it will read at that px. Requires Pillow.)
c) Positions within ±1 % H: caption ink centre 80 %, topic word 22-23 %, hook label 78.9 %, PIP card y 5-35 %.
```

## other:plain-serif-accent

_plain serif accent_

### B09 · talking-head · English · score 5

Fast receipt-driven story: rolling gradient numerals, chat bubbles over chest, italic-serif caption accents.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B09 (video-reference-match/references/blueprints/B09.json) to this brand.
Canvas 1080x1920, 25 fps. Seated speaker, plain saturated wall, dark top.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} >= 4.5:1 on the chest/shirt, numeral gradient top {{ACCENT}} must stay >= 3:1 on the footage and darken toward the shirt)
- {{TEXT}}: default #FFFFFF (captions, titles)
- {{ACCENT}}: default #0259BA (numeral gradient top; bottom = a 60 % darker shade, default #123153)
- {{ACCENT_2}}: default #7500FE (chat bubbles)
- {{SURFACE}}: default rgba(60,60,62,.6) grey pill behind captions on white screenshots
- {{CARD_BG}}: default #0A4C8A (square lower-third name box)
- {{FONT_DISPLAY}}: default Playfair Display italic (Instrument Serif Italic preferred) for accent words
- {{FONT_BODY}}: default Inter 600 (captions, numerals, titles)
- {{HANDLE}}: default @handle (chat bubble sender, screenshots)
- {{LOGO}}: not used on screen

CAPTIONS
1. Latin, as spoken, lowercase except 'I', proper nouns and sentence starts; keep hyphens; at most a full stop at a sentence end; no emoji.
2. One line of 2-3 words per phrase.
3. {{FONT_BODY}} at 69 px, {{TEXT}}, tracking -0.01em, very soft shadow 0 2px 8px rgba(0,0,0,.35), no stroke, no box. Centred, centre y 60.5 % H.
4. At most one accent word per line in {{FONT_DISPLAY}}, same cap height as the sans inline; standalone accent words over b-roll at 137 px, left-aligned at x 17 %, y 22-30 %.
5. Over white screenshots: same caption on a {{SURFACE}} pill (radius ~15 px, padding ~3 % W) at 60.7 % H.
6. Hard cut per phrase, from 2 frames before to 4 frames after the first word, or exactly on a shot cut; captions are applied before punch-ins so they scale ~1.15x with the shot.

NUMBERS (hook)
7. When the hook states counts: lead line centred at 57 % H; giant numeral in {{FONT_BODY}} 310 px centred at 59-71.5 % H with a vertical gradient {{ACCENT}} -> dark shade fading into the shirt; unit word in {{TEXT}} at ~73 % H revealed syllable by syllable with 2-frame fades. Roll like a slot counter: one digit per frame easing out (0 -> N over ~11 frames), count down for the next item.

OTHER TEXT AND EDIT DEVICES
8. Hook title over b-roll (~8-9 % of runtime): big ordinal/number in {{FONT_BODY}} 192 px, {{TEXT}} fading to transparent at the bottom, red/cyan chromatic fringes ~3 px, centred x ~46 %, y 17-25 %; a sans line in Inter 500 82 px at y 27-30 %; last word in {{FONT_DISPLAY}}; builds line by line with a chromatic flicker.
9. Lower-third after the hook (12-18 % of runtime, ~85 frames): 'Name Surname' Inter 700 69 px {{TEXT}} on a square {{CARD_BG}} box (x 28.5-70 %, y 72-76.5 %), 'Role, Company' Inter 500 42 px at 78.6 % H; box wipes in from the left.
10. Receipts: {{ACCENT_2}} rounded chat bubbles with small white text and a round avatar pop in over the chest; replies in white bubbles; then full-screen screenshots (~2 s each, slow zoom, key line highlighted) for ~30 % of runtime. Blur private names.
11. Cut rhythm: every ~1.9 s alternate locked-off MCU and a ~120 % CU punch-in; ~half the transitions are short blur/defocus soft cuts; let audio lead ~40 % of cuts (J-cut).
12. Optional: speaker cut-out composited over a thumbnail collage when scale is mentioned. No end card, no emoji.

GRADE: Grade from the user's footage (video-style / grade.py); target look: punchy contrast, cool saturated backdrop, warm natural skin, b-roll warmer and darker.
SOUND: voice-led, compressed, -14 LUFS; whoosh/hit on about half the hard cuts; tick per numeral digit; soft pop per chat bubble.

VERIFY
a) Render the caption "exclusively" on the grey pill at 60.7 % H and measure:
   python video-reference-match/scripts/caption_probe.py <test_render> --out <dir> --at <t> --box 0.2,0.57,0.8,0.64 --ink "{{TEXT}}:60"   (default ink #FFFFFF)
   Required: 3.28 % ±0.5 of H, 31.4 % ±2 of W.
b) Numeral "4" at 310 px: --box 0.35,0.55,0.65,0.75 --ink "{{ACCENT}}:90" -> ~11-12.5 % H, 18.8 % ±2 W.
c) Accent "to close" in the italic at 137 px: height 5.7 % ±0.5 H (height only).
d) Lower-third: render "KEY WORD" in Inter 700 69 px on the box, --box 0.29,0.73,0.69,0.77; expected ink for the brand's real name: video-reference-match/scripts/fit_font.py --font "Inter 700" --word <name>.
e) If {{FONT_BODY}} is not Inter 600, re-solve with fit_font.py --font "{{FONT_BODY}}" --word exclusively --ink 3.28 --width 31.4.
```

## other:role-labels

_role labels_

### B49 · skit · Hinglish · score 1

Single locked-off wide skit with accent role-label pills pinned above each head.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B49 (video-reference-match/references/blueprints/B49.json) to this brand.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship — text and accent must stay >= 4.5:1 / >= 3:1 against what sits behind them on the footage):
- {{TEXT}}      default #FFFFFF (label text)
- {{ACCENT}}    default #FA3551 (label pill fill)
- {{ACCENT_2}}  default none (optionally a second pill colour per role)
- {{SURFACE}}   default none
- {{CARD_BG}}   default #FA3551 (pill fill; same as accent)
- {{FONT_DISPLAY}} default Inter 800
- {{FONT_BODY}}    default Inter 800
- {{HANDLE}}    default @handle
- {{LOGO}}      default the brand's logo file (transparent PNG/SVG)
Pill text must stay >= 4.5:1 on {{CARD_BG}}; the pill itself needs >= 3:1 against the footage behind it (avoid pills that match the sky colour).
Canvas 1080x1920, 30 fps.

CAPTIONS
1. No captions.

OTHER TEXT
2. Two role labels, one per person, Title-case single word (placeholders 'ROLE A' / 'ROLE B' set as e.g. 'Brand' / 'Client'), {{FONT_DISPLAY}} at 57 px, {{TEXT}}, tracking 0, no stroke / shadow, on a solid {{CARD_BG}} rounded rectangle hugging the word (height 4.3-4.5 % H, corner radius ~20 % of its height, padding ~2.5 % W left/right, ~0.9 % H top/bottom).
3. Pin each pill just above its person's head: foreground person x 12.8-36.8 %, y 36.2-40.5 % (text centre 38.8 %); background person x 65.3-85.1 %, y 41.2-45.7 % (text centre 43.4 %). Further-back people get lower, smaller-looking positions.
4. Animation: none — both on from frame 0 to the last frame, screen-fixed (the camera is locked off). If the subjects move, track the pills to the heads instead.
5. No {{LOGO}}, titles or end card ({{HANDLE}} optional, small, bottom).
6. Edit: one locked-off wide, no cuts.

GRADE
Grade from the user's footage (video-style / grade.py); target look: high-contrast, muted, neutral-warm; natural golden-hour sky.

VERIFY before rendering
a) Render a pill with 'Client' and one with 'Agency' and measure: python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.6,0.40,0.9,0.47 --ink "{{TEXT}}:60"
   Expected (±0.5 % H, ±2 % W) with Inter 800 at 57 px: 'Client' ink 2.19 % H / 14.9 % W; 'Agency' ~19.2 % W.
b) Brand role words: python3 video-reference-match/scripts/fit_font.py --font "Inter 800" --word "<Word>" --ink 2.19 -> ~57 px for a Title-case word without descenders; size the pill around the returned width. (fit_font.py needs a target: --ink and/or --width; it returns the px that reproduces that ink for YOUR word plus the width it will read at that px. Requires Pillow.)
c) Positions within ±1 % H: pill A y 36.2-40.5 %, pill B y 41.2-45.7 %.
```

## other:running-caption+keyword-cards

_running caption+keyword cards_

### B14 · ugc-ad · English · score 3

Frenetic one-feature-one-shot product ad: small lowercase wide-grotesque running captions that swap to huge stacked UPPERCASE keyword cards on each selling point.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B14 (video-reference-match/references/blueprints/B14.json) to this brand.
Canvas 1080x1920, 30 fps. All positions are % of frame; px are at 1080x1920.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} must stay >= 3:1 on the footage at mid-frame; place cards over dark product surfaces)
- {{TEXT}}      running captions and keyword cards       default #FFFFFF
- {{ACCENT}}    full-frame flash colour                  default saturated yellow (not measured; use the brand's signature colour)
- {{ACCENT_2}}  light-leak tint                          default warm red (footage effect, low opacity)
- {{SURFACE}}   none                                     default none
- {{CARD_BG}}   none (cards have no box)                 default none
- {{FONT_DISPLAY}} keyword cards                         default Inter 800 (extra-bold neo-grotesque; alt Archivo Black)
- {{FONT_BODY}}    running captions                      default Syne 400 (wide regular grotesque; alt Archivo SemiExpanded)
- {{HANDLE}}    not shown
- {{LOGO}}      the product's own logo, filmed in macro for the final shot

CAPTIONS (two tiers, same centre point)
1. Running caption: English as spoken, ALL LOWERCASE, no full stops or commas (keep hyphens), 2-5 words, one line. {{FONT_BODY}} at 50 px, tracking 0, {{TEXT}}, no stroke, shadow or box. Centred at x 540 px, centre y 50.2 % (~964 px).
2. Keyword cards: ~5 per video (the hook claim, each headline feature, the product name) shown INSTEAD of the running line: UPPERCASE, 1-2 words per line, 2-4 lines, {{FONT_DISPLAY}} at 98 px, tracking -0.02em, line pitch 84 px (line-height ~0.86), {{TEXT}}, soft dark shadow 0 2px 10px rgba(0,0,0,.35), no box; block centred at x 540 px, y 50 %; widest line ~49 % W. Keep apostrophes and unit marks.
3. Animation: both tiers hard-cut in as a whole phrase ~7 frames after the phrase's first word, hard-cut out when the next phrase/card lands; the card replaces the running line on the same frame. Text carries across picture cuts. No fade, pop, slide, highlight or idle motion.

OTHER TEXT
4. Hook: the claim card from frame 0 over the speaker holding the product; end it with a 12-frame full-frame {{ACCENT}} light flash that washes the card out, then cut to the running caption.
5. End: the product name as the last keyword card over a slow push into a macro of {{LOGO}}.
6. No titles, lower thirds, stickers or separate end card.

EDIT DEVICES
7. One feature = one insert shown in the same second it is named (handheld macro, locked overhead top-down, in-use shot); median shot ~31 frames, never over ~90; ~60 cuts/min in the first ~150 frames, ~36 after. Cut on motion (swings, hands, zips). Prove the boldest claim live (wide demo + macro result). One low-opacity {{ACCENT_2}} light leak early in the body.

GRADE
8. Grade from the user's footage (video-style / grade.py); target look: cinematic warm-on-cool, tungsten practicals vs cool walls, deep blacks, slightly desaturated.

AUDIO
9. Continuous VO, no music bed; whoosh/hit on product swings and card swaps (~40 % of cuts), a riser or impact into the flash. Master to about -14.2 LUFS, true peak <= -1 dBTP.

VERIFY before rendering
a) Render a test frame with the card line "RESISTANT" and one with a running caption "key word", over a dark area, and measure:
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.2,0.40,0.8,0.60 --ink "{{TEXT}}:60"
   Required at the default font: "RESISTANT" ink 3.83 % ±0.5 of height and 49.3 % ±2 of width, centred at 50 % ±0.5. Running caption: expected ink from video-reference-match/scripts/fit_font.py ({{FONT_BODY}}, 50 px; reference 2.34 % H for lowercase lines with ascenders and descenders). With brand fonts, compute both with fit_font.py and match within ±0.5 % H.
```

## other:subtitle-box

_subtitle box_

### B15 · street-interview · English · score 3

Doorstep two-camera interview: small subtitles, top promise pill, broadcast lower third, keyword pill.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B15 (video-reference-match/references/blueprints/B15.json) to this brand.
Canvas 1080x1920, 25 fps. Two handheld cameras (host + guest), location sound.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{ACCENT}} key word >= 7:1 on the black pill; white subtitle >= 4.5:1 on its faint box over the footage; {{ACCENT_2}} tag >= 4.5:1 behind white text)
- {{TEXT}}: default #FFFFFF (subtitles, pill text)
- {{ACCENT}}: default #EEFB1F (title key word; CTA keyword #E8F582)
- {{ACCENT_2}}: default #2771B3 (lower-third role tag and offset bar)
- {{SURFACE}}: default #000000 (title and CTA pills); subtitle box rgba(0,0,0,.25)
- {{CARD_BG}}: default #FCFCFD (name box, logo tile)
- {{FONT_DISPLAY}}: default Playfair Display 400 (serif name and role)
- {{FONT_BODY}}: default Noto Sans 400/700 (subtitles, title pill)
- {{HANDLE}}: default @handle
- {{LOGO}}: company logo tile + sponsor logo pill

CAPTIONS (subtitles)
1. Latin, as spoken, sentence case with full punctuation (commas, full stops, ?, !, ellipsis when continuing); correct proper nouns; no emoji.
2. A sentence or clause per subtitle (1-10 words, ~6), up to 2 centred lines, max line width 57 % W (margins >= 20 % W).
3. {{FONT_BODY}} 400 at 38 px, {{TEXT}}, no stroke/shadow, on a translucent rgba(0,0,0,.25) box, padding ~1.5 % W, small radius.
4. Centre y 76.2 % H (2-line block ~75.5 %).
5. Hard cut in ~1 frame before the first word; hard cut out on the next subtitle.

OTHER TEXT AND EDIT DEVICES
6. Promise title pill (first ~10 % of runtime, static): {{SURFACE}} rounded box x 16-83 %, y 8-20.5 %, radius ~3 % W; line 1 'Headline here' {{FONT_BODY}} 400 65 px {{TEXT}} at 12.1 % H; line 2 with the KEY WORD in {{FONT_BODY}} 700 74 px {{ACCENT}} at 16.4 % H.
7. Lower third once at the name reveal (~11-14 % of runtime, ~75 frames): {{ACCENT_2}} tag x 16-60 %, y 59.4-62.3 % with small white serif 'Role, Company'; {{CARD_BG}} box x 15.5-77 %, y 62.7-67 % with black {{FONT_DISPLAY}} 'Name Surname' (~58 px) and an offset {{ACCENT_2}} bar; tag wipes L->R ~5 frames, role types on ~8 frames, name box wipes ~3 frames, name fades ~3 frames. {{LOGO}} on a white rounded tile x 35.8-64 %, y 79.4-90.2 %.
8. Sponsor (~60 % of runtime, ~150 frames): 'Link in Bio' white bold on a dark grey rounded pill at 13.6 % H (~5.8 % H tall); sponsor logo on a white rounded pill x 25.6-74.2 % at 67.5 % H (~7.3 % H tall).
9. CTA over the last ~8 % (during the payoff, not after): {{SURFACE}} rounded pill x 20-78 % at 67.4 % H (~6.2 % H tall): 'Comment' Inter 500 ~57 px white + '“KEYWORD”' Inter 700 ~59 px {{ACCENT}}.
10. Cold open: handheld approach with one whip (~6 frames), ~5 cuts in the first ~2 %; then cut host/guest on nearly every sentence (median ~1 s), easing to 20-45 cuts/min. One ~1 s emotional photo insert before the closing lesson. No punch-ins.

GRADE: Grade from the user's footage (video-style / grade.py); target look: natural, slightly warm, mid-high contrast, rich exterior greens, tungsten interiors.
SOUND: location dialogue up front, low bed (~5 dB under speech gaps), hits on ~half the cuts; -14 LUFS, true peak <= -2 dBTP.

VERIFY
a) Render a 7-word subtitle at 38 px at 76.2 % H over dark clothing and measure:
   python video-reference-match/scripts/caption_probe.py <test_render> --out <dir> --at <t> --box 0.15,0.735,0.85,0.785 --ink "{{TEXT}}:60"   (default ink #FFFFFF)
   Expected: ~1.95 % H for mixed-case words with ascenders/descenders and a '?'; compute the exact ink/width for your phrase with video-reference-match/scripts/fit_font.py --font "Noto Sans Devanagari 400" --word "<phrase>".
b) Title pill: render "KEY WORD" in {{FONT_BODY}} 700 at 74 px, --box 0.43,0.14,0.82,0.19 --ink "{{ACCENT}}:90"; compare with fit_font.py output for that word.
```

### B21 · skit · English · score 2

Handheld skit: text colour boxed film subtitles, whip-pan character handoffs, silent captionless punchline.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B21 (video-reference-match/references/blueprints/B21.json) to this brand.
Canvas 1080x1920, 30 fps. Multi-character handheld scene.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: subtitle {{TEXT}} must stay >= 4.5:1 against its box over both light walls and dark clothing)
- {{TEXT}}: default #F2C911 (subtitle yellow)
- {{ACCENT}}: default #F2C911 (same as text; no separate emphasis)
- {{ACCENT_2}}: none
- {{SURFACE}}: default rgba(0,0,0,.25) (subtitle box)
- {{CARD_BG}}: none
- {{FONT_DISPLAY}}: none (no titles)
- {{FONT_BODY}}: default Inter 700 (Arimo Bold for an Arial look)
- {{HANDLE}}: not on screen
- {{LOGO}}: none (the skit carries no branding on screen)

CAPTIONS
1. Latin, as spoken, sentence case like written dialogue; keep commas, full stops and question marks; no emoji.
2. 1-5 words per subtitle (a clause), one line, break at punctuation or natural pauses.
3. {{FONT_BODY}} at 48 px, {{TEXT}}, tracking 0, tight dark edge (text-shadow 0 0 2px rgba(0,0,0,.8)), on a {{SURFACE}} rectangle, radius ~4 px, padding ~13 px left/right and ~12 px top/bottom; the box hugs the line (~3 % H tall).
4. Centred, centre y 66 % H, the same position on every shot (does not follow the speaker).
5. Hard cut in on the first word of each phrase (within ~1 frame), hard cut out on the next phrase; no idle motion.
6. Turn captions OFF for the silent payoff (last ~17 % of runtime).

EDIT DEVICES
7. Open mid-conversation: first word inside ~4 frames, a name/role and a concrete number in the first line; no title card.
8. Handoffs between characters: ~half the cuts are horizontal whip pans (~6-8 frames motion blur); on most cuts start the next line before the picture changes (J-cut).
9. Median shot ~3 s; no punch-ins, no titles, no graphics, no b-roll.
10. Payoff: the last ~17 % of runtime as wordless wide reveal shots plus one deadpan reaction; grade the reveal cooler and darker than the rest.

GRADE: Grade from the user's footage (video-style / grade.py); target look: soft, muted warm beige interiors, then a cooler grey reveal.
SOUND: quiet bed or room tone under dialogue (gaps ~8 dB below speech), ambience through the reveal; -14 LUFS, true peak <= -1 dBTP.

VERIFY
a) Render "KEY WORD" as a subtitle at 48 px on its box at 66 % H and measure:
   python video-reference-match/scripts/caption_probe.py <test_render> --out <dir> --at <t> --box 0.3,0.63,0.7,0.69 --ink "{{TEXT}}:60"   (default ink #F2C911)
   Expected ink for it (and any other word) from video-reference-match/scripts/fit_font.py --font "{{FONT_BODY}}" --word "KEY WORD"; a short mixed-case phrase should land near 1.8-2.3 % H.
b) Box height ~3.0 % H, centred on 66 % H.
```

## other:two-tier-highlight

_two tier highlight_

### B03 · podcast-clip · Hinglish · score 4

Podcast trailer: money-claim hook with punch-ins, white lead + bold accent Title-Case numbers staggered left, black-frame chapter breaks, pill captions on screens.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B03 (video-reference-match/references/blueprints/B03.json) to this brand.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: the {{ACCENT}} key line must stay >= 3:1 on the footage (a light, high-luminance accent works best on dark sets); white pill text >= 7:1 on its box)
- {{TEXT}} lead captions + pill text - default #FFFFFF
- {{ACCENT}} key words / every number and money amount - default yellow #F8FF0D
- {{ACCENT_2}} - none
- {{SURFACE}} black chapter frames + pill box - default #000000 (pill ~rgba(20,20,20,.9))
- {{CARD_BG}} end card - default mauve-purple #6F4465
- {{FONT_DISPLAY}} key line - default Poppins 700
- {{FONT_BODY}} lead line + pill - default Poppins 500
- {{HANDLE}} - @handle (optional on the end card)
- {{LOGO}} - show logo on the end card; partner wordmark for the sponsor bug if any

Canvas 1080x1920, 25 fps.

EDIT
1. Hook (first ~17 %): the biggest money / number claim with checkable maths; first word within frame 1; punch-in (~115-130 %) or angle switch every ~38-75 frames.
2. Chapter breaks: 15-40 frames of pure {{SURFACE}} with audio continuing (J-cut) and only a pill caption on it.
3. Social proof (optional, keep under ~250 frames standalone): screen recordings of a previous video and its comments, laptop / TV B-roll, slow screen zoom/scroll.
4. Climax: shot / reverse-shot every 25-40 frames with numbers stacked as {{ACCENT}} callouts; end on an open-loop promise.
5. End card (~45 frames): solid {{CARD_BG}}, white {{LOGO}} (~20 % W) at ~33 % H, white 'x' at ~50 %, partner wordmark (~25 % W) at ~65 %, centred.
6. Sponsor bug (if any): 'POWERED BY' small white caps (~1.3 % H) + partner wordmark (~4 % H), bottom-right x 50-90 %, centre y ~89 %, throughout.

CAPTIONS
7. Latin script (Roman Hinglish where speech is Hindi); lead sentence case, key words Title Case; drop most punctuation, keep currency signs, thousands commas and '?'.
8. Lead line: 1-4 words, {{FONT_BODY}} 83 px, {{TEXT}}, word-spacing +0.3em (wide gaps), soft shadow 0 2px 6px rgba(0,0,0,.5), no box.
9. Key line(s): every number / money amount and the claim word, {{FONT_DISPLAY}} 122 px, {{ACCENT}}, same shadow; key line 1 centre ~67 %, key line 2 centre ~72.9 % (pitch ~5.9 % H) indented ~11 % W right of line 1.
10. Block: left-aligned, left edge x 7-22 % (keep it on the chest beside the mic), centre y 61-73 %, band y 58-76 %, max width 75 %; re-place the block when the camera angle changes.
11. Timing: every word hard-cuts on (1 frame, no scale/slide) 2-3 frames BEFORE it is spoken; the block hard-cuts out with 1-2 empty frames before the next.
12. Over screens, B-roll and black frames switch to pill captions: {{FONT_BODY}} 47 px {{TEXT}} in a near-black rounded pill (r ~18 px, padding ~4 % W / ~2 % H), centred at y ~80 %.

GRADE: Grade from the user's footage (video-style / grade.py); target look: high-contrast, natural-saturation, warm amber practicals on a dark background, natural skin.
SOUND: voice at about -14 LUFS over a bed that fills the montage; hits/whooshes on some hard cuts; bleep expletives.

VERIFY before rendering (px values were render-verified with Poppins; if the brand font differs, adjust px until the numbers match):
a) Render test frames over a dark area: "To" and "get" ({{FONT_BODY}} 83 px), "KEY WORD" ({{FONT_DISPLAY}} 122 px {{ACCENT}}), and "walk you through" in the pill (47 px).
b) Measure: python video-reference-match/scripts/caption_probe.py <test render or snapshot> --out <dir> --at <t> --box 0.05,0.58,0.95,0.76 --ink "{{TEXT}}:60,{{ACCENT}}:80" (tighten --box per word); --box 0.25,0.76,0.75,0.84 --ink "{{TEXT}}:60" (pill).
c) Required: "To" ink 3.59 % +-0.5 of H and 8.8 % +-2 of W; "get" 3.44 % +-0.5 and 12.1 % +-2; "walk you through" 2.5 % +-0.5 and 37.6 % +-2. For the key line compute expected ink with python video-reference-match/scripts/fit_font.py --font "<{{FONT_DISPLAY}}>" --word "KEY WORD" at 122 px (a 7-letter key word targets ~4.8 % H).
```

## other:two-voice-colour

_two voice colour_

### B50 · mixed · English · score 3

Fly-on-the-wall call recording made readable by speaker-coded captions above the head: on-camera voice in white serif, off-camera voice in accent wide sans.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B50 (video-reference-match/references/blueprints/B50.json) to this brand.
Canvas 1080x1920, 30 fps. All positions are % of frame; px are at 1080x1920.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} and {{ACCENT}} must each stay >= 3:1 on the footage behind the captions, and {{ACCENT_2}} >= 4.5:1 on the {{ACCENT}} bar)
- {{TEXT}}      on-camera voice captions, title          default #FFFFFF
- {{ACCENT}}    off-camera voice captions, outcome bar   default #EDF21C (yellow)
- {{ACCENT_2}}  text on the outcome bar and aside pill   default #000000
- {{SURFACE}}   not used                                 default none
- {{CARD_BG}}   aside pill fill                          default #FFFFFF
- {{FONT_DISPLAY}} on-camera voice, title, bar, pill     default Playfair Display 700/900 (bold high-contrast serif)
- {{FONT_BODY}}    off-camera voice                      default Syne 700 (heavy wide grotesque; Archivo ExtraBold Expanded is closer)
- {{HANDLE}}    not shown
- {{LOGO}}      not shown

CAPTIONS (two voices, colour-coded)
1. English as spoken, sentence case, commas/apostrophes kept; spell names and brand names correctly. No emoji in captions.
2. Grouping: 2-5 words per caption (about 3-4), one line, max line width 55 % W; the style switches whenever the speaker switches.
3. On-camera voice: {{FONT_DISPLAY}} 700 at 45 px, {{TEXT}}, no box, very soft dark shadow. Centred, sitting just above the subject's head: centre y 28.9 % in a wide high-angle shot, 26.1 % when punched in, ~16 % in a tight shot.
4. Off-camera / phone voice: {{FONT_BODY}} at 49 px, {{ACCENT}} with a thin ~1.5 px dark outline, centred at ~21 % of height (about 5 % above where the on-camera line sits when both show).
5. Animation: none. Each phrase appears by hard cut ~1 frame before its first word and is replaced by hard cut. No pop, fade or highlight.

OTHER TEXT
6. Result-first title for the first ~87 frames, over a 15-frame blur-to-sharp opening of the footage: 2-word title (e.g. "Headline here") in {{FONT_DISPLAY}} 900 at 99 px, {{TEXT}}, soft shadow, centred at 15.7 %; under it a solid {{ACCENT}} rounded bar x 11.4-88.5 %, y 19.5-25.1 % (radius ~2 % W) with the outcome in {{FONT_DISPLAY}} 900 at 56 px, {{ACCENT_2}}, ending in one emoji. Both hard-cut out together.
7. One candid aside, once, starting at ~22 % of runtime, held ~90 frames: {{CARD_BG}} rounded pill x 15-85 %, y 70.5-75.3 % with {{ACCENT_2}} heavy serif (~46 px) text in parentheses plus one laughing emoji.

EDIT DEVICES
8. Keep one high-angle static camera; jump-cut dead air between turns (about 5-6 cuts/min) and add one ~115 % punch-in section around 26-43 % of runtime. Leave real friction (rejection, objection) in.

GRADE
9. Grade from the user's footage (video-style / grade.py); target look: warm, mid-contrast, natural saturation, soft indoor daylight.

AUDIO
10. Voice only, no music bed or SFX. Master to about -14.4 LUFS, true peak <= -1 dBTP; lift the quieter phone-side voice.

VERIFY before rendering
a) Render a test frame with "KEY WORD" as an on-camera caption at 45 px centred at 26 % and as an off-camera caption at 49 px centred at 21 %, then measure:
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.25,0.24,0.75,0.285 --ink "{{TEXT}}:60"
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.05,0.19,0.95,0.235 --ink "{{ACCENT}}:80"
   Title: --box 0.25,0.13,0.75,0.185 --ink "{{TEXT}}:60"; bar text: --box 0.12,0.2,0.80,0.245 --ink "{{ACCENT_2}}:90".
b) Expected ink for any word: video-reference-match/scripts/fit_font.py with the token font and px above (reference ink heights: on-camera 2.19 % H, off-camera 2.03 % H, title 3.75 % H, bar 2.11 % H). Required: within ±0.5 % H of the fit_font.py value; positions within ±1 % of height; colours equal to the tokens.
```

## title-only

_no speech captions; titles, labels or cards only_

### B04 · mixed · Hinglish · score 3

Landscape course-launch pitch alternating moody low-key talking head with clean white-canvas motion graphics, ending in a struck-through price ladder and comment CTA.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B04 (video-reference-match/references/blueprints/B04.json) to this brand.
Canvas: the blueprint is native 16:9 (1920x1080, 30 fps). For a vertical 1080x1920 cut use the short-side rule: keep the same px, keep x centring, put lower-band callouts at ~80-85 % height and the title at ~50 %. All positions below are % of frame.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} and {{ACCENT}} must stay >= 4.5:1 on {{SURFACE}} / {{CARD_BG}}; graphics stay light while the talking head stays dark)
- {{TEXT}}      text on white graphics, product title     default #111111
- {{ACCENT}}    real-price text                           default #1D6E96 (teal-blue)
- {{ACCENT_2}}  strike line on wrong prices               default saturated red (not measured)
- {{SURFACE}}   graphic canvas                            default #F8F6F9 (near-white)
- {{CARD_BG}}   price pills, cards, windows               default #F8F9FC
- {{FONT_DISPLAY}} title, price, CTA                      default Inter 500 (medium neo-grotesque)
- {{FONT_BODY}}    labels, pills, cards                   default Inter 500
- {{HANDLE}}    shown inside profile-style proof cards ("@handle")
- {{LOGO}}      small logo badge in a corner of the curriculum split, and logo tiles in the hook graphic

CAPTIONS
1. Add NO running speech captions. All on-screen text is short callouts in {{FONT_DISPLAY}}, tracking 0.

OTHER TEXT (only where the script has a matching beat)
2. Product title over a collage: 2x3 grid of rounded image/product cards with a soft white radial glow in the middle; title in {{FONT_DISPLAY}} at 104 px, {{TEXT}}, centred at 50 % height (x ~28.7-71.2 % on 16:9).
3. Price ladder (one pill per spoken wrong guess, ~30 frames apart, left to right): {{CARD_BG}} rounded pills ~14.5 % W each, evenly across x 6-93 %, y 81-90 % (16:9) on a translucent dark band; on vertical stack 2-3 per row at ~80-86 %. Text dark #2A2A2A {{FONT_BODY}}; each pill crossed by a {{ACCENT_2}} diagonal strike from top-left to bottom-right that overshoots the pill.
4. Real price: one larger {{CARD_BG}} rounded pill (x 40-60 %, y 78.1-92.5 % on 16:9; centred at ~82 % on vertical), price in {{FONT_DISPLAY}} at 86 px, {{ACCENT}}; pops in (back.out(1.4), ~8 frames) with small sparkle particles.
5. CTA for the last ~150 frames: 'Comment "KEYWORD"' in {{FONT_DISPLAY}} at 83 px, #FFFFFF, centred at ~87 % (16:9) / ~85 % (vertical) on a faint frosted dark panel (x ~30-70 %, y ~81-93 %).
6. Hook graphic (~3-4 % of runtime): three logo tiles on {{SURFACE}} with a small label ("Label here") above a grey progress bar that fills over ~45 frames.

EDIT DEVICES
7. Pixel-glitch reveal (~10 frames) from the talking head into a collage ~45 frames in.
8. Social proof: 3 profile-style cards ({{HANDLE}}, counts) stack in on a white grid over ~180 frames.
9. Curriculum (~41-79 % of runtime): speaker in a rounded card on the left ~35 % W of a {{SURFACE}} canvas; thin vertical timeline with dot markers and grey 'Chapter 0X: Label' labels; a new chapter label + screen-recording window slides in on the right every ~120 frames (power3.out); {{LOGO}} badge in a corner.
10. Talking-head blocks: static MCU, dark low-key set; hard cuts back from graphics. In a short cut, punch in or add a callout at least every ~120-180 frames.

GRADE
11. Grade from the user's footage (video-style / grade.py); target look: high-contrast, muted, neutral-warm talking head (low-key, warm bokeh, natural skin) against clean bright graphics.

AUDIO
12. Voice only, no music bed. Soft whoosh/tick on graphic slide-ins (about a third of cuts), a small sparkle on the price pop. Master to about -14.4 LUFS, true peak <= -1 dBTP.

VERIFY before rendering (on 1080x1920; on 16:9 scale the box y-ranges with the canvas)
a) Render a test frame with 'Comment "KEY WORD"' over a dark area and a real-price pill with "KEY WORD", then measure:
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.05,0.82,0.95,0.88 --ink "#FFFFFF:40"
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.3,0.79,0.7,0.85 --ink "{{ACCENT}}:60"
b) Expected ink for any word: video-reference-match/scripts/fit_font.py with {{FONT_DISPLAY}} at the px above (reference ink heights on 1080x1920: CTA and price 3.28 % H, title 4.14 % H). Required: within ±0.5 % H of the fit_font.py value; positions within ±1 %; colours equal to the tokens.
```

### B10 · skit · Hinglish · score 2

Deadpan one-take office meme: boxed competitor-pain title, 'Meanwhile : us' pills, printed prop punchline.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B10 (video-reference-match/references/blueprints/B10.json) to this brand.
No speech captions: a one-take meme skit whose editing is two text layers plus a badge. Canvas 1080x1920, 30 fps.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship: {{TEXT}} and {{ACCENT}} >= 4.5:1 on {{SURFACE}} boxes; the pain phrase must stay a warning-type hue distinct from the brand colours)
- {{TEXT}}: title and 'Meanwhile' text, default #000000
- {{ACCENT}}: competitor pain phrase, default #E00006
- {{ACCENT_2}}: brand name word 1 on the pill, default #0C3248 (word 2 default #60261B)
- {{SURFACE}}: title boxes and pills, default #FFFFFF
- {{CARD_BG}}: unused, default none
- {{FONT_DISPLAY}}: default Poppins 800 italic
- {{FONT_BODY}}: default Poppins 800 italic
- {{HANDLE}}: not shown in the source
- {{LOGO}}: round badge top-right for the whole clip

TITLE
1. Copy: "Other <competitors>: <pain phrase> / <rest of line>" in the audience's register (source: Roman Hinglish), 2 lines, ~10 words, sentence case; the pain phrase in {{ACCENT}} ("Other brands: KEY WORD here / lead words here").
2. {{FONT_DISPLAY}} 58 px, tracking 0; text {{TEXT}}, key phrase {{ACCENT}}; no stroke or shadow.
3. Box: {{SURFACE}} behind each line, merged into one shape with ~10 px rounded corners (line 1 box x 9.3-90.1 %, line 2 box x 5.6-93.9 %, together y 15.8-25.7 %). Lines centred: line 1 ink 16.7-19.1 %, line 2 ink 20.8-23.8 % H (a ~31-character line spans ~83.9 % W at 3.0 % H).
4. Timing: on from frame 0 to the end, static.

OTHER TEXT
5. Turn pills at the joke's turn (~30 % of runtime), both hard-cut in together, static to the end: {{SURFACE}} pills (radius ~8 px) on the right. Pill 1 x 68.8-91.2 %, y 46.1-49.1 % with "Meanwhile :" in {{TEXT}} {{FONT_BODY}} 33 px; pill 2 x 66.4-93.5 %, y 50.9-53.8 % with the brand name, first word {{ACCENT_2}}, second word the brand's second colour. Gap 1.8 % H.
6. {{LOGO}} round badge top-right (x ~78-94 %, y ~5.5-14.5 %), static, whole clip. Deliver the punchline as a physical printed one-word prop ("KEY WORD !!") lifted to face height while both people point at it; no typed punchline.

EDIT
7. One locked medium two-shot, deadpan to camera, no cuts or zooms; keep the right side at 45-55 % H clear for the pills.

SOUND: a non-speech trend sound or comedic sting with gaps; optional pop on the pills. Master to about -14 LUFS, true peak <= -1 dBTP.
GRADE: Grade from the user's footage (video-style / grade.py); target look: high-contrast, muted, warm office light, neutral skin.

VERIFY before rendering: render the title and pills and measure:
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at 1.0 --box 0.05,0.2,0.95,0.24 --ink "#000000:90"
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at 3.0 --box 0.66,0.46,0.93,0.49 --ink "#000000:90"
Title line 2 (run the {{TEXT}} and {{ACCENT}} inks, e.g. --ink "#E00006:90", and combine): compute the expected ink for the brand's line with video-reference-match/scripts/fit_font.py at 58 px (a ~31-character line reads ~3.0 % H / 83.9 % W); "Meanwhile :" must read 1.33 % +-0.5 of H and 19.3 % +-2 of W. Box/pill positions within +-1 % of frame height.
```

### B16 · ugc-ad · Hinglish · score 2

Locked same-mark team lineup dissolving every ~42 frames under a fixed text colour serif Hinglish offer.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B16 (video-reference-match/references/blueprints/B16.json) to this brand.
This blueprint has NO speech captions: one fixed 2-line offer title over a locked-off same-mark team lineup. Canvas 1080x1920, 30 fps.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship: {{TEXT}} has no stroke or box, so it must stay >= 3:1 against the clothing/backdrop behind it; add a 2 px dark outline only if it drops below)
- {{TEXT}}: offer lines, default #FFDF00
- {{ACCENT}}: same as {{TEXT}} (no emphasis word in the source), default #FFDF00
- {{ACCENT_2}}: unused, default none
- {{SURFACE}}: unused (backdrop is the real location: one strong single-colour wall/facade), default none
- {{CARD_BG}}: unused, default none
- {{FONT_DISPLAY}}: condensed transitional serif, default Playfair Display 400 (Instrument Serif closer)
- {{FONT_BODY}}: same as {{FONT_DISPLAY}}
- {{HANDLE}}: not shown in the source
- {{LOGO}}: not shown in the source

TITLE
1. Copy: the offer in the audience's register (source: Roman-script Hinglish), 2 lines, ~5 + 3 words, sentence case, no punctuation ("Lead words here" / "KEY WORD").
2. {{FONT_DISPLAY}} in {{TEXT}}, tracking 0, no stroke/shadow/box. Line 1 76 px, line 2 88 px (~1.2x). Exact narrow look: Playfair 95 / 115 px with transform: scaleX(0.74), or Instrument Serif sized to the measured ink.
3. Layout: both lines centred; line 1 centre 52.0 % H (x 13-88 %, ink ~4.8 % H at ~24 characters), line 2 centre 57.7 % H (x 20-82 %, ink ~5.82 % H at ~17 characters), across the chest of a centred medium shot. Optional slight bulge warp.
4. Timing: on from frame 0 to the last frame, static, untouched by the dissolves.

EDIT
5. Locked camera, identical medium framing, one strong single-colour backdrop. 5 people on the same mark, ~42 frames each; swaps are ~6-frame cross-dissolves, the last change a hard cut. Each person: eyes closed / looking down, then eyes open + small smile within ~24 frames. No punch-ins, no end card.

SOUND: one trending/upbeat song, no voice, steady level. Master to about -14 LUFS, true peak <= -1 dBTP.
GRADE: Grade from the user's footage (video-style / grade.py); target look: mid-contrast, natural saturation, cool daylight with true skin.

VERIFY before rendering: render the two lines and measure:
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at 1.0 --box 0.08,0.48,0.92,0.545 --ink "#FFDF00:75"
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at 1.0 --box 0.08,0.548,0.92,0.61 --ink "#FFDF00:75"
Swap the --ink colour to {{TEXT}}. Compute the expected ink height/width of the brand's actual lines with video-reference-match/scripts/fit_font.py (76 / 88 px, or 95 / 115 px x scaleX 0.74); if height fits but width is too wide, apply the scaleX. Line centres within +-1 % of frame height of 52.0 / 57.7 %.
```

### B18 · ugc-ad · none · score 2

Two event phone clips under one static text colour condensed 3-line ask overlay plus quoted credential.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B18 (video-reference-match/references/blueprints/B18.json) to this brand.
This blueprint has NO speech captions: one static 3-line hook overlay plus a credential sub-line held over 1-2 phone clips. If the edit has speech, caption it with its own spec and keep this overlay as the only title. Canvas 1080x1920, 30 fps.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship: {{TEXT}} must stay >= 3:1 on the footage behind it, and {{ACCENT_2}} outline must be the darkest brand neutral so the text survives bright lights)
- {{TEXT}}: overlay and sub-line fill, default #FFCA00
- {{ACCENT}}: same as {{TEXT}} unless the brand wants one key word recoloured, default #FFCA00
- {{ACCENT_2}}: outline + halo, default #110503
- {{SURFACE}}: unused (no cards), default none
- {{CARD_BG}}: unused, default none
- {{FONT_DISPLAY}}: heavy condensed sans, default Anton 400 (original ~21 % narrower)
- {{FONT_BODY}}: credential sub-line, default Poppins 600
- {{HANDLE}}: not shown in the source; optional "@handle" can replace the credential sub-line
- {{LOGO}}: not shown in the source

OVERLAY
1. Copy: a 3-line audience + ask hook, ~8-10 words, broken long / short / long ("Headline here, lead words" / "KEY WORD" / "(short aside here)"). Sentence case; parentheses and curly quotes allowed.
2. {{FONT_DISPLAY}} in {{TEXT}}, tracking 0, 72 px (balanced). For the exact narrow look set Anton at ~85 px with transform: scaleX(0.79). Thin {{ACCENT_2}} outline ~3 px plus a faint {{ACCENT_2}} halo; no box.
3. Layout: centred; line centres at 41.0 %, 46.0 %, 52.2 % H (block 38.5-54.5 %); line 1 spans x 21.9-77.9 % (ink 5.08 % H), line 2 x 37.5-62.4 % (4.14 % H), line 3 x 21.2-78.5 % (4.3 % H). In the source the block sits over the face; if face-safe rules apply, move the whole block up to 18-34 % H keeping the same spacing.
4. Warp: slight bulge/arc (glyphs at the line ends a little smaller, leaning outward). Subtle; skip if unavailable.
5. Sub-line: ~3-word credential in quote marks, {{FONT_BODY}} 30 px, {{TEXT}} with a thin {{ACCENT_2}} outline, centred at 56.3 % H (x 33.5-62.5 %, ink ~1.41 % H).
6. Timing: both layers on screen from frame 0 to the last frame, completely static (no entry, exit or tracking), across every cut.

EDIT
7. Two clips: a low-angle selfie (~45 % of runtime, slow tilt down) then one hard cut to a handheld wide that proves the setting; reach the payoff view with an in-camera fast swing (~15 frames of motion blur) rather than an edit transition. No punch-ins, no end card.

SOUND: music only, steady bed (low loudness range); optional whoosh on the swing. Master to about -14 LUFS, true peak <= -1 dBTP.
GRADE: Grade from the user's footage (video-style / grade.py); target look: mid-contrast, natural saturation, neutral-warm night event light (cool stage whites, warm bulbs).

VERIFY before rendering: render the overlay with "KEY WORD" on line 2 at the stated px and measure:
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at 1.0 --box 0.15,0.499,0.85,0.546 --ink "#FFCA00:70"
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at 1.0 --box 0.15,0.439,0.85,0.482 --ink "#FFCA00:70"
Compute the expected ink height/width for the brand's actual lines with video-reference-match/scripts/fit_font.py ({{FONT_DISPLAY}} 72 px, or 85 px x scaleX 0.79); line 3 at the reference length should read ~4.3 % H, line 2 ~4.14 % H. Swap the --ink colour to {{TEXT}}. Line centres within +-1 % of frame height of 41.0 / 46.0 / 52.2 %.
```

### B34 · talking-head · English · score 2

Zero-cut single-take talking head carried by one persistent two-box header (light box topic over dark box value range); list withholds final item for DM CTA.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B34 (video-reference-match/references/blueprints/B34.json) to this brand.
Canvas 1080x1920, 30 fps. All positions are % of frame; px are at 1080x1920.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: header text must stay >= 4.5:1 on its own box, and the two boxes must read as light-over-dark)
- {{TEXT}}      line 1 text on the light box      default #101010
- {{ACCENT}}    line 2 box fill (dark bar)        default #010101
- {{ACCENT_2}}  line 2 text on the dark bar       default #FFFFFF
- {{SURFACE}}   not used (footage fills the frame) default none
- {{CARD_BG}}   line 1 box fill (light box)       default #FDFDFD
- {{FONT_DISPLAY}} header font                    default Poppins 500 (Poppins Light 300 / Jost Light if available; the look is a light geometric sans)
- {{FONT_BODY}}    same as display                default Poppins 500
- {{HANDLE}}    not shown on screen (spoken DM CTA only)
- {{LOGO}}      not used

CAPTIONS
1. Add NO running speech captions.

OTHER TEXT
2. One static 2-line header, on screen for 100 % of the runtime (frame 0 to last frame, no entry/exit animation):
   - Line 1 (topic, Title Case, e.g. "Headline here"): {{FONT_DISPLAY}} at 51 px, {{TEXT}}, centred on a square {{CARD_BG}} box spanning x 5.1-94.9 %, y 12.5-18.9 % (text centre y 16.0 %).
   - Line 2 (value / price range, Title Case, e.g. "(Range) Key Word"): same font at 51 px, {{ACCENT_2}}, centred on a square {{ACCENT}} box spanning x 10.1-87.5 %, y 19.8-25.6 % (text centre y 22.8 %), 0.9 % of height below the light box.
   - Each box is ~2-5 % W wider than its text on each side. No radius, stroke or shadow. Tracking 0em. Proof-read both lines.

EDIT DEVICES
3. Keep the take whole: no cuts, punch-ins, b-roll or transitions. Only trim the head/tail.
4. Structure: numbered promise in the first ~9 % of runtime; deliver all list items but the last; in the final ~4 % withhold the last ("best") item behind a spoken "DM me" CTA.

GRADE
5. Grade from the user's footage (video-style / grade.py); target look: cool, high-contrast, natural saturation, teal-leaning background against warm skin.

AUDIO
6. Master speech to about -15 LUFS integrated with true peak <= -1 dBTP. No SFX. An optional faint music bed sits ~17 dB under speech.

VERIFY before rendering
a) Render a test frame with the user's header text (or "KEY WORD" on both lines) at 51 px and measure (thin strokes: use a 2-px row threshold):
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.07,0.13,0.93,0.188 --ink "{{TEXT}}:90"
   python video-reference-match/scripts/caption_probe.py <test.mp4> --out <dir> --at <t> --box 0.11,0.2,0.86,0.255 --ink "{{ACCENT_2}}:90"
b) Expected ink for the actual words: video-reference-match/scripts/fit_font.py with {{FONT_DISPLAY}} at 51 px (reference ink height ~2.7-2.8 % of H for a Title Case line). Required: measured ink within ±0.5 % H of the fit_font.py value; box edges within ±1 % of the geometry above; colours equal to the tokens.
```

### B37 · brand-promo · none · score 2

Music-led BTS event montage, flash transitions, no overlays until an outlined brand + contact card.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B37 (video-reference-match/references/blueprints/B37.json) to this brand.
This blueprint has NO captions and NO overlays until the end card: a music-led phone BTS montage. Canvas 1080x1920, 30 fps.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship: {{ACCENT}} and {{ACCENT_2}} fills sit inside a {{TEXT}} outline, and the outlined lines must stay >= 3:1 against the dark/sky area of the last shot)
- {{TEXT}}: outline colour of both end-card lines, default #FFFFFF
- {{ACCENT}}: brand-name fill, default #E31E28
- {{ACCENT_2}}: contact-line fill, default #000000
- {{SURFACE}}: unused, default none
- {{CARD_BG}}: unused, default none
- {{FONT_DISPLAY}}: default Poppins 600
- {{FONT_BODY}}: default Poppins 600
- {{HANDLE}}: contact line (phone number or "@handle")
- {{LOGO}}: not overlaid; the brand must be visible in-shot (uniforms, signage, props)

EDIT
1. Open with a walk-to-camera of the lead person through the busiest part of the set (~13 % of runtime), music hitting on frame 0.
2. Then cut every ~42 frames (median shot 1.42), with two bursts of ~15-frame shots (48-60 cuts/min) at ~20-40 % and ~60-80 % of runtime on the music's hits; cut on musical phrases, not on lyrics.
3. ~62 % of changes soft: ~6-frame light-flash/flare or quick blend between locations; one ~6-frame white-out early (~24 %). No punch-ins; all motion handheld.
4. Order: walk-in -> prep / pattern interrupt -> scale proof (vehicles, stage, performers) -> people directing + happy client -> high wide.

CAPTIONS
5. None; do not caption song lyrics. No logo bug; let in-shot branding carry the brand 5+ times.

OTHER TEXT (end card, last shot only, ~38 frames)
6. Hard-cut in on the same frame as the final high wide, static, held to the last frame, over a dark/sky area.
7. Line 1, brand name, sentence case: {{FONT_DISPLAY}} 61 px, fill {{ACCENT}}, {{TEXT}} outline ~4 px, no shadow/box; centred, centre y 28.5 % H (x 25.8-72.6 % at ~14 characters, ink 2.97 % H).
8. Line 2, {{HANDLE}} / phone digits: {{FONT_BODY}} 73 px (~1.2x line 1), fill {{ACCENT_2}}, {{TEXT}} outline ~4 px; centred directly under line 1, centre y 31.8 % H (outline box 30.0-33.6 % H, ~37.6 % W for 10 digits).

SOUND: music with vocals at full level, no voiceover. Normalise to -14 LUFS and limit true peak to -1 dBTP (do not clip).
GRADE: Grade from the user's footage (video-style / grade.py); target look: mid-contrast, saturated, neutral-warm night event colour (rich uniforms, purple-blue stage light, warm practicals).

VERIFY before rendering: render a test end-card frame with "Brand name here" (or the real brand) and a 10-digit number, then measure:
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at <t_endcard> --box 0.22,0.255,0.78,0.30 --ink "#E31E28:80"
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at <t_endcard> --box 0.25,0.30,0.75,0.34 --ink "#FFFFFF:40"
Swap the --ink colours to {{ACCENT}} / {{TEXT}}. Compute the expected ink height/width of the brand's actual line with video-reference-match/scripts/fit_font.py at 61 px / 73 px; a 14-character line in Poppins 600 61 px should read ~2.97-3.2 % H; the 10-digit outline box ~3.67 % H / 37.6 % W. Positions within +-1 % of frame height.
```

### B41 · ugc-ad · none · score 2

Song-driven hiring reel told through props (screen, paper signs), logo bug, 3D zoom-blur logo sting.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B41 (video-reference-match/references/blueprints/B41.json) to this brand.
This blueprint has NO captions and NO typed text overlays: the message lives on props in the footage (screen headline, printed signs). Only a logo bug and a logo sting are added. Canvas 1080x1920, 30 fps.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship: {{TEXT}} bug must stay >= 3:1 on the top-right of every shot; {{ACCENT}} logo >= 4.5:1 on {{SURFACE}})
- {{TEXT}}: logo-mark bug colour, default #FFFFFF
- {{ACCENT}}: end-card logo colour, default #264378
- {{ACCENT_2}}: unused, default none
- {{SURFACE}}: end-card background, default #FFFFFF
- {{CARD_BG}}: unused, default none
- {{FONT_DISPLAY}}: prop-screen headline (made as a slide on the laptop, not overlaid), default Poppins 600 with the key word Poppins 800 slanted
- {{FONT_BODY}}: printed signs, any bold sans, default Poppins 700
- {{HANDLE}}: contact on the printed sheet (email / "@handle")
- {{LOGO}}: logo mark for the bug + full logo file for the sting

CAPTIONS
1. None. Do not caption song lyrics; add no typed overlays.

OTHER TEXT
2. Logo bug on every footage shot: {{LOGO}} mark in {{TEXT}}, top-right, x 79.3-90.4 % (~11 % W), y 5.9-11.3 %; static from frame 0 until the end card.
3. End card (last ~28 % of runtime): hard cut to {{SURFACE}}; full {{LOGO}} in {{ACCENT}} centred at x 19-80 %, y 41-60 % (centre ~52 % H). Reveal: logo pieces streak and rotate in with a radial zoom-blur over ~53 frames (power3.out), fully settled ~75 frames after the cut, then hold still to the end.

EDIT
4. Hook (~15 %): static wide, chair facing away in front of a branded wall spins round; the subject lifts a laptop to camera showing the headline on the music's first hit.
5. ~15 %: soft push-in onto the laptop screen (headline fills ~62 % W at ~47 % H, key word bold italic).
6. 28-72 %: handheld shots of staff holding/taping printed signs (2-3 role lines each, one sign per shot, ~60-210 frames per shot); finish with the contact sheet ({{HANDLE}}) pushed close to the lens for ~60 frames. 3 hard cuts timed to song phrases.

SOUND: one trending song with vocals at full level, no voiceover; optional whoosh under the zoom-blur reveal. Master to about -14 LUFS, true peak <= -1 dBTP.
GRADE: Grade from the user's footage (video-style / grade.py); target look: high-contrast, muted, cool office light with saturated brand-wall colour and a clean white end card.

VERIFY before rendering: snapshot one footage frame and one settled end-card frame. Measure the bug with
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at <t_footage> --box 0.75,0.03,0.95,0.14 --ink "#FFFFFF:40"
(box x 79.3-90.4 %, y 5.9-11.3 % within +-1 %), and the end-card logo with --box 0.1,0.3,0.9,0.7 --ink "<{{ACCENT}}>:60" (centre ~52 % H, spanning x 19-80 %). No other overlaid text may appear.
```

### B42 · ugc-ad · none · score 2

Still group shot under a colon-ended serif title, then a textless ~10-frame-per-clip highlight burst.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B42 (video-reference-match/references/blueprints/B42.json) to this brand.
This blueprint has NO captions: one 2-line title on a still opener, then a textless highlight burst. Canvas 1080x1920, 30 fps.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship: {{ACCENT}} must stay >= 3:1 on the sky/background behind the title; {{TEXT}} must sit on a non-white area)
- {{TEXT}}: lead-in line, default #FFFFFF
- {{ACCENT}}: key phrase, default #FF0021
- {{ACCENT_2}}: unused, default none
- {{SURFACE}}: unused (no cards), default none
- {{CARD_BG}}: unused, default none
- {{FONT_DISPLAY}}: key phrase brush italic, default Playfair Display 700 italic (Merienda 700 closer in feel)
- {{FONT_BODY}}: lead-in condensed serif, default Playfair Display 500 (Instrument Serif closer)
- {{HANDLE}}: not shown in the source
- {{LOGO}}: not shown in the source

OTHER TEXT (opener only)
1. First shot near-static, ~44 % of runtime, title in clean sky/background above the subjects' heads. Two centred lines, no stroke/shadow/box:
   a. Lead-in ("Lead words", ~12 characters): {{FONT_BODY}} 63 px, {{TEXT}}, centre y 23.8 % H (x 35-65 %, ink ~4.14 % H). With a condensed serif size it to that ink.
   b. Key phrase ending in " :" ("KEY WORD :"): {{FONT_DISPLAY}} 78 px, {{ACCENT}}, centre y 28.7 % H (x 18-82 %), 0.9 % H under line 1; first word regular weight, key word bold, same size (ink ~4.06 % H / 63.3 % W at ~17 characters).
2. Both lines on from frame 0, static, hard-cut out with the opener shot. No text in the burst.

EDIT
3. Burst: 16 clips of 6-13 frames (median ~10, ~110 cuts/min, peak ~190) on the music beats, 44 % as 2-3-frame blends and the rest hard cuts; order by intensity and end on the biggest visual so the loop restarts high. No punch-ins.

SOUND: short trend voice line or sting over the opener, then the music drop on the first burst cut. Master to about -14 LUFS, true peak <= -1 dBTP.
GRADE: Grade from the user's footage (video-style / grade.py); target look: warm, softly faded opener; burst clips kept saturated and natural.

VERIFY before rendering: render the title with the brand's lines (or "Lead words" / "KEY WORD :") and measure:
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at 1.0 --box 0.15,0.26,0.85,0.31 --ink "#FF0021:90"
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at 1.0 --box 0.3,0.205,0.7,0.26 --ink "#FFFFFF:35"
Swap the --ink colours to {{ACCENT}} / {{TEXT}}. Compute the expected ink of the actual lines with video-reference-match/scripts/fit_font.py (63 px {{FONT_BODY}}, 78 px {{FONT_DISPLAY}}); a ~17-character key phrase should read ~4.06 % H / 63.3 % W. Line centres within +-1 % of frame height of 23.8 / 28.7 %.
```

### B43 · brand-promo · none · score 2

Music-only kinetic-type manifesto: one giant word per card flipping black/cream on the beat, accent punchline word, recurring 3D ball, logo hold.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B43 (video-reference-match/references/blueprints/B43.json) to this brand.
This blueprint has NO speech captions: the kinetic type is the content. Cover only the text cards and edit devices below.

BRAND TOKENS (use the brand's colour/font for each role; keep the contrast relationship: {{TEXT}} on {{SURFACE}} and {{SURFACE}}-coloured text on {{CARD_BG}} >= 7:1, {{ACCENT}} on {{SURFACE}} >= 3:1)
- {{TEXT}} word-card ink on light cards - default near-black #09080A
- {{ACCENT}} punchline word / payoff line / recurring 3D object - default signal orange #FD5815
- {{ACCENT_2}} logo-hold field - default electric blue #1A39EF (render #162CB3-like)
- {{SURFACE}} light card - default warm cream #F0E7D2
- {{CARD_BG}} dark card - default near-black #0A090B
- {{FONT_DISPLAY}} word cards - default Inter 900 (geometric Black faces like Gilroy/Outfit are closer); manifesto - Poppins 900; held brand word - Anton 400
- {{FONT_BODY}} handle watermark - default JetBrains Mono
- {{HANDLE}} - @handle, tiny, top-left
- {{LOGO}} - the brand mark for the final hold (3D extruded tiles in {{SURFACE}} / {{ACCENT}} on {{ACCENT_2}})

Canvas 1080x1920, 30 fps. Music-only; cut to the beat.

1. Hook burst (first ~17 % of runtime): 8 one-word cards, a new card every 6-12 frames on the beat, background flipping {{CARD_BG}} <-> {{SURFACE}} on every cut. Word lowercase with punctuation, centred at y 50 %, {{FONT_DISPLAY}} ~324 px for a 5-letter word (ink 12.5 % H, ~70 % W; not fit-to-width - a 7-letter word ~236 px), tracking -0.03em, {{TEXT}} on {{SURFACE}} / {{SURFACE}} on {{CARD_BG}}; ONE punchline word in solid {{ACCENT}}. Entry over 2-4 frames: tracking collapse (spread letters -> normal) or scale 1.25 -> 1 with a 15 % H rise, power3.out, no overshoot. No shadow, stroke or box.
2. Recurring object: one glossy {{ACCENT}} 3D object in every early shot that interacts with the type (bounce, pendulum swing, knocks letters out, becomes a light source).
3. Manifesto (next ~23 %): {{SURFACE}} card, two centred UPPERCASE lines, Poppins 900 ~172 px, -0.06em, line centres y 35.4 % / 44.8 % (pitch 9.4 % H); line 1 {{TEXT}} holds while line 2 ('ANSWER.') swaps in {{ACCENT}} every ~15-24 frames; the pendulum ball knocks letters of the last line out with motion trails.
4. Slow section (next ~27 %): ~12-frame dark wipe, then the object glows and a {{SURFACE}} light cone sweeps across navy; only 2 shots.
5. Word over montage (next ~16 %): the brand word in Anton ~296 px, white, centred (y 49.9 %, x 14-86 %), hard dark shadow (0 6px 0 rgba(0,0,0,.6)), held still while ~10 full-screen 3D backgrounds hard-cut underneath every 6-12 frames.
6. Logo hold (last ~18 %, ~105 frames): {{LOGO}} assembled from extruded {{SURFACE}}/{{ACCENT}} tiles on {{ACCENT_2}}.
7. {{HANDLE}} tiny mono, top-left x 5 %, y ~13.5 %, ~1 % H, colour flipping with the card, until the montage.

GRADE: Grade from the user's footage (video-style / grade.py) if any footage is used; target look: high-contrast, natural-saturation, cool graphic palette with glossy soft-shadow 3D.
SOUND: music only, mastered to about -14 LUFS with true peak <= -1 dBTP; cuts on beats; optional impact on letter knock-outs and a riser into the montage.

VERIFY before rendering (px values were render-verified with local fonts; if the brand font differs, adjust px until the numbers match):
a) Render test frames: "don’t" ({{FONT_DISPLAY}} 324 px, -0.03em, {{TEXT}} on {{SURFACE}}), "MADE" (Poppins 900 177 px, -0.06em), and "KEY WORD" as the held brand word (Anton 296 px, white over a dark area).
b) Measure: python video-reference-match/scripts/caption_probe.py <test render or snapshot> --out <dir> --at <t> --box 0.1,0.41,0.9,0.6 --ink "{{TEXT}}:80" (word card); --box 0.2,0.3,0.8,0.395 --ink "{{TEXT}}:80" (manifesto line 1); --box 0.08,0.41,0.92,0.59 --ink "#FEFDFD:60" (held word).
c) Required: "don’t" ink 12.66 % +-0.5 of H and 70.0 % +-2 of W; "MADE" 6.48 % +-0.5 and 45.7 % +-2. For the held brand word compute the expected ink with python video-reference-match/scripts/fit_font.py --font "Anton 400" --word "<brand word>" at 296 px.
```

### B01 · brand-promo · none · score 1

Footage-free one-word kinetic cards on flat colours: fill/outline stutter stack, mock follow-click end card.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B01 (video-reference-match/references/blueprints/B01.json) to this brand.
This blueprint has NO speech captions: it is a footage-free kinetic title / follow-CTA sequence. If the edit has speech, caption it with its own spec; use this for the title cards and end card. Canvas 1080x1920, 30 fps.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship: text vs card >= 7:1, {{ACCENT}} >= 3:1 on {{CARD_BG}}, light cards stay light and the dark card stays dark)
- {{TEXT}}: text on light cards, default #000000 (white #FFFFFF on the dark card)
- {{ACCENT}}: the one key noun on the dark card, default #F7D328
- {{ACCENT_2}}: second light card (CTA card, end-card flashes), default #E4FEA3
- {{SURFACE}}: first light card (hook), default #B2F4B5
- {{CARD_BG}}: dark card, default #161616
- {{FONT_DISPLAY}}: default Anton 400 (look: Bebas Neue-like condensed caps)
- {{FONT_BODY}}: default Inter 700 (profile-row account name)
- {{HANDLE}}: account name on the mock profile row, default "@handle"
- {{LOGO}}: wordmark text or logo on the end card and the avatar circle image

TITLE CARDS
1. {{FONT_DISPLAY}}, ALL CAPS, one word per beat, no punctuation/emoji, tracking 0, no stroke/shadow/box on filled words.
2. Size: beat words 166 px (calibration "HEY" ink 7.19 % H x 21.2 % W; "SCROLLING" 7.34 % / 59.7 %; "PROMOTE" 7.58 % / 53.5 %). CTA word and wordmark 138 px ("FOLLOW" 6.17 % H / 36.9 % W). If {{FONT_DISPLAY}} is not Anton, re-solve px with VERIFY.
3. Position: every word horizontally centred, block centre 49.5-50 % H. Two-line blocks use fixed slots (line 1 centre 44.6 %, line 2 centre 55 %); line 1 does not move when line 2 lands (+8 frames).
4. Hook stack (first ~24 % of runtime): repeat the hook word in a 5-row stack, pitch 9.93 % H (gap 2.7 % H), row centres 29.7 / 39.6 / 49.5 / 59.5 / 69.4 %. Rows alternate FILL / OUTLINE / FILL / OUTLINE / FILL on {{SURFACE}}: fill rows {{TEXT}}, outline rows transparent with a white ~7-8 px stroke outside the glyph (same 166 px size). Build order: centre fill, outline above, outline below, fill above, fill below; each row hard-cuts in, one every 8-10 frames. Then hard-cut to a two-word imperative on the 2-line slots.
5. Dark card: {{CARD_BG}} with white text; function words as white outline stacks, the verb in white fill, the ONE key noun in {{ACCENT}}. One word every 9-10 frames, each hard-cutting in place of the previous; no fades, scale or idle motion.
6. Transitions: light -> dark is a left-to-right wipe of the new card over ~6 frames, text static under it. Key-noun exit: the word hard-cuts into a full-height column of ~11 copies (pitch ~3.4 % H) that scrolls up out of frame in ~6 frames (power2.in). Then hard cut to the {{ACCENT_2}} CTA card; the CTA verb lands 6 frames after the background.

OTHER TEXT / END CARD (last ~36 % of runtime)
7. {{LOGO}} wordmark (138 px, {{TEXT}}, centre 49.4 % H) on white; 1 frame later a profile row reveals from below in 2-3 frames: gradient avatar circle with {{LOGO}} (diameter 6.3 % W, x 25.5-31.8 %, centre y 56.8 %), {{HANDLE}} in {{FONT_BODY}} #343434 (cap height ~1.1 % H, x 33.8-48.8 %), white "Follow" pill with 1 px #BBBBBB outline (14.1 % W x 1.9 % H at x 60.3-74.4 %, y 55.8-57.7 %, radius ~3 px).
8. A hand cursor appears below the pill ~9 frames after the card, glides onto it in ~9 frames (power2.out), clicks ~33 frames later: the pill hard-switches to filled #343434 with white "Following". Background flashes {{ACCENT_2}} for ~7 frames twice before the click, then stays white to the end.

SOUND: music only, beat-driven; place word and row steps on beats; optional soft click on the cursor click. Master to about -14 LUFS, true peak <= -1 dBTP.
GRADE: Grade from the user's footage (video-style / grade.py); target look: flat graphic colour fields, high contrast, muted pastels against near-black (no footage in this blueprint, so only inserted footage would be graded).

VERIFY before rendering: render the calibration words and measure them:
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at <t_hook_stack> --box 0.1,0.2,0.9,0.8 --ink "#000000:30"
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at <t_cta_word> --box 0.1,0.2,0.9,0.8 --ink "#000000:30"
Filled "HEY" must read ink 7.19 % +-0.5 of H and width 21.2 % +-2 of W; "FOLLOW" 6.17 % +-0.5 / 36.9 % +-2. For the brand's own words, compute the expected ink with video-reference-match/scripts/fit_font.py at 166 px / 138 px in {{FONT_DISPLAY}}. Positions within +-1 % of frame height of the values above.
```

### B05 · skit · English · score 1

Two-shot POV skit: persistent mid-frame label, rant, jump cut to polite phone voice.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B05 (video-reference-match/references/blueprints/B05.json) to this brand.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship — text and accent must stay >= 4.5:1 / >= 3:1 against what sits behind them on the footage):
- {{TEXT}}      default #FFFFFF (POV label)
- {{ACCENT}}    default #FFFFFF (no accent in this style)
- {{ACCENT_2}}  default none
- {{SURFACE}}   default none
- {{CARD_BG}}   default none
- {{FONT_DISPLAY}} default Poppins 500
- {{FONT_BODY}}    default Poppins 500
- {{HANDLE}}    default @handle
- {{LOGO}}      default the brand's logo file (transparent PNG/SVG)
Label must stay >= 4.5:1 on the footage at mid-frame; if the subject wears white, add the faint shadow (0 1px 3px rgba(0,0,0,.25)) or darken clothing, never a box.
Canvas 1080x1920, 30 fps.

CAPTIONS
1. No speech captions.

OTHER TEXT
2. One persistent label from frame 0 to the last frame: 'POV:' in caps + a short lowercase premise (placeholder 'POV: headline here'), {{FONT_DISPLAY}} at 67 px, {{TEXT}}, tracking 0, very faint soft shadow, no stroke / box, one line centred at 49.8 % H (~81 % W for ~24 characters). No animation; unaffected by cuts.
3. No {{LOGO}}, watermark or end card ({{HANDLE}} only if required, small, outside the label band).
4. Edit: one propped-phone medium shot; frustrated beat first, then a soft jump cut at ~30 % of runtime to the polite/professional beat. No music required; keep the audio dynamic so the tone flip is audible.

GRADE
Grade from the user's footage (video-style / grade.py); target look: mid-contrast, natural-saturation, warm; natural indoor phone light.

VERIFY before rendering
a) Render the label and measure: python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.05,0.47,0.95,0.53 --ink "{{TEXT}}:60"
   Expected (±0.5 % H, ±2 % W) with Poppins 500 at 67 px: 'POV:' ink ~2.66 % H / ~14 % W; a ~24-character line ~81 % W.
b) python3 video-reference-match/scripts/fit_font.py --font "Poppins 500" --word "<your label>" --ink 3.44 -> ~64-67 px for a line with descenders; if at_verified_px width exceeds ~85 % W, shorten the premise rather than shrinking below ~60 px. (fit_font.py needs a target: --ink and/or --width; it returns the px that reproduces that ink for YOUR word plus the width it will read at that px. Requires Pillow.)
c) Position within ±1 % H: label centre 49.8 %.
```

### B07 · brand-promo · none · score 1

Music-only save-bait: quoted viewer question, caps reply, dark note-screenshot list, framed monogram card.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B07 (video-reference-match/references/blueprints/B07.json) to this brand.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship — text and accent must stay >= 4.5:1 / >= 3:1 against what sits behind them on the footage):
- {{TEXT}}      default #FFFFFF (title lines, end-card type and frame)
- {{ACCENT}}    default #71CAC3 (teal 'yes' heading)
- {{ACCENT_2}}  default unmeasured red/pink ('no' heading; use the brand's warning colour)
- {{SURFACE}}   default #000000 (dark-mode UI / end card)
- {{CARD_BG}}   default #0F2025 (dark-teal highlight band behind 'yes' headings)
- {{FONT_DISPLAY}} default Inter 400 (title lines); spaced bold geometric caps for the end-card wordmark
- {{FONT_BODY}}    default Inter 400
- {{HANDLE}}    default @handle
- {{LOGO}}      default the brand's logo file (transparent PNG/SVG)
Keep the highlight band dark and the heading text light (>= 4.5:1 inside the band).
Canvas 1080x1920, sizes are px at that canvas; frame counts at 30 fps.

CAPTIONS
1. No speech captions (music-only format). If the edit has speech, do not add a caption track unless asked.

OTHER TEXT
2. Hook question (frame 0 to the first cut, ~46 % of runtime): the audience's own question in curly double quotes, sentence case, one line, {{FONT_BODY}} at 43 px, {{TEXT}}, tracking 0, no stroke / shadow / box, centred, ink centre at 50 % H, ~68 % W. Screen-fixed while the footage slowly pushes in.
3. Answer line: UPPERCASE 2-3 word reassurance ending in '!!' (placeholder 'KEY WORD!!'), {{FONT_BODY}} 46 px, {{TEXT}}, centred at 57.3 % H. Hard cut in ~65 frames after the start; both lines hard-cut out with the shot cut.
4. Proof screens: real dark-mode phone note screenshots of the brand's list, {{SURFACE}} background, light-grey body text left-aligned at x 11 % (~3.8 % H line pitch); 'yes' headings in {{ACCENT}} on a {{CARD_BG}} highlight band, 'no' headings in {{ACCENT_2}} italic on a dark-red band with a cross emoji; a new page every ~30 frames by hard cut.
5. End card (~24 frames, hard cut in, static): {{SURFACE}}; thin 2 px {{TEXT}} frame (x 15-85 %, y 21-79 %); {{LOGO}} monogram at 28-37 %; brand name in bold geometric caps, ~0.3 em tracking (ink 1.72 % H, ~49 % W, centre 41 %); light spaced-caps sub-line below; short rule at ~53.5 %; small serif 'by' at ~63.5 %; founder / team name in spaced serif caps (Playfair Display, ink 1.95 % H, ~49 % W, centre 70.4 %).
6. Footage: one slow linear push-in (~110-115 %) across the first shot; hard cuts only; music-only bed, no SFX.

GRADE
Grade from the user's footage (video-style / grade.py); target look: low-contrast, muted, neutral-warm; dim warm studio, then pure-black UI.

VERIFY before rendering
a) Render the hook question and the answer line with neutral placeholders ('Headline here, is this a question?' and 'KEY WORD!!'), then measure:
   python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.1,0.475,0.9,0.52 --ink "{{TEXT}}:70"
   python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.3,0.55,0.7,0.6 --ink "{{TEXT}}:70"
b) python3 video-reference-match/scripts/fit_font.py --font "Inter 400" --word "<your question line>" --ink 1.95 -> ~39-43 px (keep 43 px if your line spans <= ~70 % W); answer: --word "<ANSWER>!!" --upper --ink 1.72 -> ~44-46 px. The returned width is what the probe should read. Measure over mid-grey or darker background. (fit_font.py needs a target: --ink and/or --width; it returns the px that reproduces that ink for YOUR word plus the width it will read at that px. Requires Pillow.)
c) Positions within ±1 % H: question centre 50.2 %, answer centre 57.3 %, end-card wordmark 41.1 %, founder line 70.4 %.
```

### B28 · skit · Hindi · score 1

Single moody office two-shot lip-sync under a persistent text colour condensed-serif headline.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B28 (video-reference-match/references/blueprints/B28.json) to this brand.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship — text and accent must stay >= 4.5:1 / >= 3:1 against what sits behind them on the footage):
- {{TEXT}}      default #F7D312 (headline yellow)
- {{ACCENT}}    default #F7D312 (same; single-colour style)
- {{ACCENT_2}}  default none
- {{SURFACE}}   default none (headline sits on a dark area of the footage)
- {{CARD_BG}}   default none
- {{FONT_DISPLAY}} default Instrument Serif Regular (condensed high-contrast serif); local fallback Playfair Display 500 at scaleX ~0.6
- {{FONT_BODY}}    default same
- {{HANDLE}}    default @handle
- {{LOGO}}      default the brand's logo file (transparent PNG/SVG)
The headline needs a dark band of footage behind it: {{TEXT}} must stay >= 4.5:1 there; a bright brand colour works, a dark one does not.
Canvas 1080x1920, 24 fps.

CAPTIONS
1. No captions (the audio is a dialogue / trend track).

OTHER TEXT
2. One persistent 2-line headline for the whole clip, sentence case, no full stop (placeholder 'Headline here, lead words' / 'KEY WORD here'). {{FONT_DISPLAY}} at ~80 px with line 2 slightly bigger, {{TEXT}}, tracking -0.01 em, no stroke / shadow / box.
3. Placement: band 14.2-25.2 % H on the empty dark wall / ceiling above the heads; line 1 cap top 15.0 %, baseline 19.4 %; line 2 baseline 25.2 % (baseline pitch ~5.8 % H, descenders touching ascenders); centred block, centre x ~46 %.
4. Animation: none — on from frame 0 to the last frame.
5. No {{LOGO}}, watermark or end card.
6. Edit: one locked-off two-shot, no cuts; let the audio carry the joke.

GRADE
Grade from the user's footage (video-style / grade.py); target look: moody low-key, warm skin, deep shadows, slight magenta/purple corner cast.

VERIFY before rendering
a) Render the headline with 'Another' on line 1 and measure: python3 video-reference-match/scripts/caption_probe.py <test-render> --out <dir> --at <t> --box 0.1,0.14,0.85,0.26 --ink "{{TEXT}}:60"
   Expected (±0.5 % H, ±2 % W): 'Another' ink 4.45 % H / 21.1 % W. Playfair cannot hit both (it is ~40 % too wide); with Instrument Serif solve the px for height, then check width.
b) Any word / font: python3 video-reference-match/scripts/fit_font.py --font "<font weight>" --word "<word>" --ink 4.45 --width 21.1 --tracking -0.01 gives the matching px for the calibration word; for other words pass --ink only. Re-check line 2 at ~5.0 % H for a 2-word line with ascenders. (fit_font.py needs a target: --ink and/or --width; it returns the px that reproduces that ink for YOUR word plus the width it will read at that px. Requires Pillow.)
c) Positions within ±1 % H: line 1 baseline 19.4 %, line 2 baseline 25.2 %.
```

### B46 · brand-promo · none · score 1

Type-only teaser: typeface swaps every 2-3 frames, accent/black inverting word cards, blurring stock reveal.

```text
Use /video-pipeline with /video-captions on videos/<project>. Apply style blueprint B46 (video-reference-match/references/blueprints/B46.json) to this brand.
This blueprint has NO speech captions: it is a text-only hype teaser plus one stock/venue shot. Canvas 1080x1920, 30 fps.

BRAND TOKENS (use the brand's colour for each role; keep the contrast relationship: {{ACCENT}} must stay >= 3:1 on {{CARD_BG}} and {{CARD_BG}} >= 3:1 on {{ACCENT}}; white text >= 4.5:1 on {{SURFACE}})
- {{TEXT}}: opener phrase and closing question, default #FFFFFF
- {{ACCENT}}: word-card colour (text on dark, background on the inverted card), default #AF0000
- {{ACCENT_2}}: unused, default none
- {{SURFACE}}: opener background, default #6C0101 (deep maroon)
- {{CARD_BG}}: dark word-card background, default #000000
- {{FONT_DISPLAY}}: heavy flared serif for the word cards and question, default Playfair Display 900 (a flared low-contrast display serif is closer)
- {{FONT_BODY}}: start face of the opener rotation, default Playfair Display 400
- {{HANDLE}}: not shown in the source; optional "@handle" small under the question
- {{LOGO}}: not shown in the source; optional small logo for the last 20 frames

TITLE CARDS
1. Font-swap opener (first 33 % of runtime, ~106 frames): flat {{SURFACE}}; a short two-word teaser line ("Headline here.") in {{TEXT}}, one line, centred at 50 % H. Every 2-3 frames hard-swap the line to a different typeface category; rotate ~12: Playfair Display 400 / 400 italic / 900, Inter 300 / 800, Anton 400, Syne 700, Poppins 500, DM Sans 700, JetBrains Mono 500, plus Caveat, Permanent Marker, Kalam, Orbitron; never the same face twice in a row. Start at {{FONT_BODY}} 40 px (ink 2.19 % H, width 23.1 % W) and grow continuously (~0.8 % scale per frame) to ink ~5.4 % H / ~45 % W (wide faces up to ~75 % W). No stroke, box or fade.
2. Escalation cards (33-69 % of runtime): 4 one-word ALL-CAPS comparative adjectives in {{FONT_DISPLAY}} at 129 px ("BIGGER" ink 5.31 % H / 46.5 % W; "GRANDER" 5.23 % / 59.6 %), centred at y 50 %. Each word twice: {{ACCENT}} text on {{CARD_BG}} for 10-13 frames, then {{CARD_BG}} text on {{ACCENT}} for 15-20 frames, identical size and position; text and background hard-cut on the same frame; no idle motion.
3. Closing question (last ~31 %, ~100 frames): hard cut to a full-frame stock or venue wide; 2 centred lines (ALL CAPS, three short words, keep '?'), {{TEXT}}, {{FONT_DISPLAY}} 87 px (first line of ~7 characters reads 3.52 % H / 35.4 % W), block centred at 50 % H, line gap ~1.6 % H. Entry: 1-frame pop (first frame 116 % scale, then 100 %), then a linear zoom to ~151 % by the last frame. Background blurs from sharp to heavy mostly over frames 5-29 after the cut (ease-out), softening slightly further to ~frame 80.

OTHER TEXT
4. None in the source. Optional brand sign-off: {{LOGO}} at 8 % W, centred at 88 % H, fades in over 6 frames in the last 20 frames.

SOUND: music only, a building trailer bed; optional impact on each inversion and a riser under the final zoom. Master to about -14 LUFS, true peak <= -1 dBTP.
GRADE: Grade from the user's footage (video-style / grade.py); target look: low-contrast, saturated, warm (deep red / maroon / black cards, golden stock wide).

VERIFY before rendering: render the calibration words and measure them:
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at <t_BIGGER_black> --box 0.15,0.45,0.85,0.55 --ink "#AF0000:90"
  video-reference-match/scripts/caption_probe.py <render-file> --out <dir> --at <t_GRANDER_red> --box 0.15,0.45,0.85,0.55 --ink "#000000:60"
"BIGGER" must read ink 5.31 % +-0.5 of H and width 46.5 % +-2 of W; "GRANDER" 5.23 % +-0.5 / 59.6 % +-2. Closing question: measure line 1 just after the pop with --box 0.15,0.40,0.85,0.60 --ink "#FFFFFF:45" before the background is bright behind it. For the brand's own words compute the expected ink with video-reference-match/scripts/fit_font.py at 129 px / 87 px in {{FONT_DISPLAY}} (swap the --ink colour to {{ACCENT}} / {{CARD_BG}} when the tokens change). Positions within +-1 % of frame height.
```

