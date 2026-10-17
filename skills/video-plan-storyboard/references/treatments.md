# Treatments

A treatment is a visual way of presenting a stretch of the video. One video uses several; never the same one twice in a
row. Each entry: what it is, when it fits, when it does not, and what later skills must deliver. The look (colours,
type, motion feel) always comes from `video-style`; the build from `video-format` and `video-motion-graphics`.

| Treatment | What it is | Fits | Avoid when | Needs |
|---|---|---|---|---|
| **Split-screen** | Two pictures side by side (16:9) or stacked (9:16): the speaker and a screen, two people, before and after | the screen and the face both matter; a conversation; a comparison shown, not told | one side would be static for long; the screen text is too small to read at half size | `video-take-geometry`: a face-tracked 8:9 (side by side) or 9:8 (stacked) crop of each source; `video-format`: the layout and divider |
| **Paper-drawer** | A paper-textured panel slides in from an edge carrying text, images or a sketch, then slides out | a side note, a definition, a "by the way", a quote; a section intro with a hand-made feel | the copy is long (over ~12 words); the next beat is also a panel | `video-generate` (optional): a paper texture or a sketch via Gemini Flash; `video-motion-graphics`: the slide in/out and paper shadow |
| **Whiteout** | The picture blows out to white and comes back on the next shot | a hard section change, a time jump, "and then everything changed", a reveal | between two lines of the same thought; more than about once a minute; on a joke's landing (it kills the beat) | `video-format`: the transition timing (out ~0.25 s, hold 2 to 4 frames, back ~0.35 s); `video-audio`/`video-sound-design`: usually silence or a soft swell, never a whoosh on copy |
| **Caption-edit** | The words are the main visual: large, word-by-word or phrase-by-phrase captions, key words emphasised | Shorts; vlogs; a strong line with nothing better to show; watching muted | the screen already carries text the viewer must read | `video-captions`: word-exact timing from `transcript.json`, emphasis rules; `video-style`: caption type |
| **Layered-head** | Text or graphics placed behind the speaker, who stays in front (a subject matte) | a big number, a title, a single word that matters, while staying on camera | busy or moving backgrounds; hair or hands crossing the text constantly; a 1080p source with a soft edge | `video-take-geometry`: the subject matte (`npx hyperframes remove-background`); `video-format`/`video-motion-graphics`: the layer order inside the camera |
| **B-roll** | Full-frame footage that shows what is being said: the user's own clips, screen recordings, stock, or generated shots | a person, place, object or action named; proof (their screen); giving the face a rest | the cutaway would be generic decoration; generated footage would pose as proof | the insert list: `own-footage` → conform; `stock` → licence check and conform; `generate-video`/`generate-image` → gate 3, `video-generate`, `video-omni-restyle` |
| **Speaker layout** | The speaker's own video moves: **stack** (speaker in the top ~44%, a card below), **pip** (content full frame, speaker in a framed corner window), **hide** (a pure-graphic moment), back to full | evidence, documents, charts or a list that needs the space while the speaker stays present; business and explainer reels | the speaker's face carries the moment (an emotional line, a joke); more than one layout change every ~10 s | `video-format`: a `layout` beat (stage.py); `video-take-geometry`: the face position (`focus`) for the cropped video |
| **Card-list** | Items appear one by one on a card or as separate pills, each on its word | a counted list said aloud ("three things"), steps, deliverables, in hooks and Shorts | long-form bodies (make each item its own device instead); items over ~18 characters | `video-format`: list, bullets, pop-out or pills, with a check marker for done/to-do lists |

## Combining

- Layered-head + caption-edit: fine in a Short (text behind, captions in front) when they never overlap.
- Split-screen + caption-edit: captions go across the divider, never inside one half.
- Whiteout + paper-drawer: a whiteout can open a section whose first beat is a drawer, not the reverse.
- B-roll during card-list: no; the list needs the face or a calm background to read against.

## Writing a treatment into the plan

For each use: the phrase it starts on, the phrase it ends on (or a hold), the treatment, and one line of content.
"`@the hardest part` → whiteout into section 2", "`@three tools` → card-list: HyperFrames, whisper.cpp, Veo".
