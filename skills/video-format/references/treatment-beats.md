# Treatment beats (treatments.py, built by stage.py on any canvas and by compose.py on 16:9)

Times (`in`, `out`, item times) come from the resolver; in the plan, write `anchor` phrases instead. Positions are
fractions of the height, sizes fractions of the width, so the same beat works at 9:16 and 16:9.

| Type | Fields | Portrait default placement | Notes |
|---|---|---|---|
| `layout` | `mode`: stack / pip / hide / full, `corner` (pip: tl / tr / bl / br), `size` (pip width, fraction), `focus` [x%, y%], `transition` (0.6 s) | stack: speaker top 44%; pip: 32% wide top-left under the top bar | the speaker's own video moves (stage.py only); back to full at `out` unless the next layout follows within one transition |
| `banner` | `text`, `em`, `y`, `size`, `bg`, `weight` | y 0.095, a full-width band under the top bar | headline claim, uppercase, one accent word (business reels) |
| `hero` | `text`, `em` (word indexes), `y`, `size`, `anim`: rise / slam / fade | y 0.15, above the head | big statement text; outline from `text_stroke` |
| `cards` | `title`, `items` [[text, t], ...], `marker`: num / dot / check, `y`, `pos` (16:9: tl / tr / center) | y 0.52, under the face | items enter on their words, alternating sides |
| `whiteout` | `peak` 0.25, `hold` 0.10, `back` 0.35 | full frame | opacity only (seek-safe); richer: catalog `flash-through-white`, `editorial-flash-overlay` |
| `drawer` | `edge`: left / right / bottom, `title`, `em`, `lines`, `img`, `w`, `y`, `rotate` | y 0.52, under the face | paper texture, tape strip, slides in and back out |
| `split` | `layout`: sbs / stack, `a` and `b`: {`src`, `focus` [x%, y%], `media_start`}, `gap`, `divider` | stacked halves | sources muted; the base video's sound plays. `focus` from `reframe.py --aspect 9:8` (stacked) or `8:9` (side by side) |
| `behind` | `text`, `em`, `y`, `size`, `color` | y 0.26-0.32, behind the head | needs the storyboard's `matte`; occlusion is intentional (marked for check) |
| `clip` | `src`, `media_start`, `focus`, `label` | full frame | B-roll; in compose.py the kit's own `clip` (20c) is used instead |
| `block` | `comp_id`, `src`, `w`, `h`, `x`, `y`, `z`, `vars` | as given | any registry block or injected caption style, mounted as a sub-composition |

Storyboard keys stage.py adds: `canvas` [W, H], `matte`, `origin`, `video-captions` {source, max_words, emphasis}, `sfx`
[{id, src, at, dur, volume}].

Example (a 9:16 Short):

```json
{"id": "short01", "canvas": [1080, 1920], "duration": "auto", "video": "input-9x16.mp4", "matte": "subject-matte.webm",
 "origin": "50% 30%", "captions": {"source": "transcript.json", "max_words": 3},
 "beats": [
  {"type": "hero", "id": "hook", "text": "Stop losing viewers", "em": [2], "anchor": "-", "in": 0.1, "out": 2.2},
  {"type": "behind", "id": "big70", "text": "70%", "anchor": "70%", "hold": 2.2},
  {"type": "whiteout", "id": "wo1", "anchor": "fix one thing", "lead": 0.3, "hold": 0.8},
  {"type": "drawer", "id": "tip", "edge": "left", "title": "Your first frame", "em": [2],
   "lines": ["decides the next 3 seconds"], "anchor": "your first frame", "hold": 1.5},
  {"type": "cards", "id": "tools", "title": "3 tools", "anchor": "three tools",
   "items": [["CapCut", "@", "capcut"], ["Canva", "@", "canva"], ["HyperFrames", "@", "hyperframes"]]}],
 "camera": [["punch", "@most creators", 1.10]]}
```
