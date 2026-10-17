# Storyboard schema and vocabulary

Use short, consistent tags so storyboards from different references can be compared. Combine tags with `+` when needed (`CU+text`). Anything unusual can be described in a few words.

## Shot list columns

Pre-filled by the script (do not edit): `#`, `Time`, `Dur`, `In`, `Frame`, `Spoken`.

`In` combines the transition into the shot with how it lines up with speech: `cut·on_pause`, `cut·j_lead`, `cut·l_trail`, `cut·mid_speech`, `soft·…`, `start`. `Frame` is the contact-sheet cell (`S2·5`; a leading `~` means no frame of its own, so it is the nearest one).

### Framing
`ECU` extreme close-up · `CU` close-up · `MCU` medium close-up (chest up) · `MS` medium · `WS` wide · `OTS` over the shoulder · `POV` · `screen` screen recording · `insert` cutaway object/detail · `b-roll` · `graphic` full-screen graphic/animation · `split` split screen · `stock`

### Move
`static` · `handheld` · `push-in` · `pull-out` · `pan` · `tilt` · `track` · `whip` · `punch-in` (digital zoom jump) · `slow-zoom` · `screen-zoom` (zoom on a screen capture) · `parallax` · `speed-ramp`

### On-screen text
`none` · `caption` (spoken words) · `title` · `lower-third` · `label` (points at something) · `callout` (emphasis word/number) · `meme-text` · `UI` (text that belongs to a screen capture). Add placement and style if it matters: `caption(centre, 3 words, yellow key word)`.

### Audio
`VO` voice-over · `talk` on-camera speech · `music` · `sfx` (say which: whoosh, hit, riser) · `ambient` · `silence` · `music+duck` (music lowered under voice). Note `J-cut`/`L-cut` if you can see/hear it.

### Purpose
`hook` · `claim` · `setup` · `context` · `proof` · `demo` · `example` · `pattern-interrupt` · `reaction` · `transition` · `payoff` · `CTA` · `loop-back`. A shot may have two (`proof+demo`), but name the primary one first.

## Hook patterns (name the one that fits; say why it holds attention)

- **Bold claim / contrarian**: states something surprising in the first sentence.
- **Open loop**: poses a question or promise that the rest resolves.
- **Result first**: shows the finished outcome, then rewinds to how.
- **In medias res**: starts mid-action with no intro.
- **Pattern interrupt**: unexpected visual/sound change in the first 1-2 seconds.
- **Direct address**: speaks to a specific viewer ("If you edit on a phone…").
- **Curiosity gap visual**: something odd on screen that needs explaining.
- **Social proof / credential**: leads with a number, name or result.

Note what happens in the first 3 seconds visually, verbally, and in sound; strong hooks usually stack two of the three.

## Beat sheet template

| Beat | Time | What happens | Why it works |
|---|---|---|---|
| Hook | 00:00-00:03 | … | … |
| Setup | … | … | … |
| Build / proof | … | … | … |
| Payoff | … | … | … |
| CTA / loop | … | … | … |

Use as many beats as the video really has (4-8). Timecodes come from the shot list.

## Takeaways: what good looks like

Each one is a rule the user can apply tomorrow, grounded in a measured number or a timestamp.

Good: "New visual roughly every 1.8s (median shot 1.7s); never hold any shot longer than 4s."
Good: "First word lands at 0.3s; no lead-in. Captions are 3 words, centred, with the key word in yellow."
Weak: "Fast-paced, energetic editing." / "Good use of B-roll."

Include 5-8, ordered by how much they shape the viewer's experience: hook, pacing, caption/text style, audio mix, transitions, structure, then the rest.

## Merging rows

When consecutive shots do the same job (a rapid B-roll montage, a repeated cutaway rhythm), replace their rows with one row `#14-19` and put the count and combined time in `Time`/`Dur`. Keep every shot that does something different.
