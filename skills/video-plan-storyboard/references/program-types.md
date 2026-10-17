# Program types

The program type sets structure and pacing. A long-form video can contain a hook; a vlog can contain a talking
section; plan each part by its own rules.

## Contents
- Hook (the first 15 to 60 seconds of anything)
- Long-form (a talk over ~3 minutes)
- Vlog (story told through places and moments)
- Short (9:16, under 60 seconds)

## Hook

The hook earns the rest of the video. About 6 overlay moments per 37 s (about 10 overlays and 4.5 to 7.5 camera moves a
minute). Cards hold 3 to 7 s; past 7 s they need internal motion (items arriving, a count-up).

- **Motion from the first frame.** One pattern that worked: four short clips of the user's own work in cards around
  them, all playing at once, in 0.12 s apart from 0.35 s, out by 5.8 s; the title line lands about 1 s after the open.
- **Reaction hooks (news, launches):** the hook moves the whole time; everything named is on screen on its word. A
  count gets a montage ("more than 20 releases": a card every ~0.3 s with a small counter).
- **Hook patterns** to name in the plan: bold claim, open loop, result first, in medias res, pattern interrupt, direct
  address, curiosity-gap visual, social proof. Strong hooks stack two of picture, words and sound in the first 3 s.

## Long-form

- **One persistent world.** A long video is one space the camera moves through, not a stack of unrelated cards. Decide
  the spatial grammar first (left to right = toward the outcome, up = a person, down = the system).
- **The chapter fixture returns at every boundary** (a progress tag, a slot wall or a numbered deck). An open loop is
  planted in the hook as something visibly incomplete (empty slots, a ghosted stack) and filled on screen, never "we'll
  come back to this".
- **One element at full brightness at a time.** What is drawn stays, dimmed but legible; retire a finished prop fully.
  About 20 on-screen words per section, no sentences; everything reads in under 2 seconds.
- **Pacing:** no stretch without an overlay or camera move over 15 s in the first 90 s, 20 s after, 30 s ever; about 7
  overlays and 7 camera moves per 90 s. One card across a topic span (an item building midway) beats five flashes. Never
  divide a section evenly.
- **The face is not the default background.** Aim for 40% or more of a talking section as full-frame animation, the
  graphic alone on screen. An abstract explanation goes full-frame, not as a card over the face.
- **Variety over lists.** No list panel in a long-form body: each list becomes a device (pills on each phrase, a loop
  diagram, one device per number, a pipeline). Card-list is for hooks and Shorts, or for counted lists the user wants
  seen as a list.
- **Every person or job named gets footage of that person** (2.6 to 3.4 s, right after the job is described, before the
  answer is revealed).
- **An app named gets a designed window** of it; **a website named gets the real page**, held until the talk moves on.
- **Compose per section** (hook, each intro, each body section) and join with `assemble.py`: each stays within the
  render's overlay budget, and a note costs one section's render.

## Vlog

A vlog is a story told through places and moments, not a talk with pictures on top. The plan follows the story, and
the picture leads more than the words.

- **Structure:** a cold open (the best moment or the question of the day, 3 to 8 s) → setup (where, why, what is at
  stake today) → the journey (a sequence of moments, each a mini-scene with a beginning and a turn) → the moment (the
  peak the cold open promised) → reflection (to camera, shorter than you think) → out.
- **Footage first.** Plan from the watch sheets as much as the transcript: list the strongest shots, then hang the
  talk on them. A great 4-second shot with no words beats a card.
- **Natural sound is a beat.** Plan 1 to 2 s "sound breaths" where the place speaks (a door, waves, a crowd) between
  talking bits; they reset attention better than any graphic. Mark them in the plan; `video-audio` must not denoise them away.
- **Cut rhythm:** a new shot or angle every 3 to 6 s in the journey; jump cuts in to-camera bits are fine and expected.
  Pauses can run longer than in long-form when the picture carries them (dead-air limit up to ~0.7 s on reflective
  lines).
- **Text:** few cards. Captions carry the words (`caption-edit`), place names as small labels, a time or date stamp
  when the day's timeline matters. No list panels.
- **Music** carries the edit more than in any other type: plan where it changes (setup → journey → moment → reflection),
  and where it drops out for a sound breath or a punchline.
- **B-roll** is the user's own footage almost always; generation only for something that could not be filmed (the
  idea in their head, a map), never for "what happened".

## Short

A separate 1080x1920 composition, never a centre crop of the 16:9 (the `video-take-geometry` skill reframes on the face).

- A specific reason to stay in the first 3 seconds, which the Short pays off. One main open loop.
- One idea. It must make sense with no context: no "as I said earlier", no "in this video".
- Word-exact captions throughout, the key word emphasised (`video-captions`). Hero type 88 to 110 px, cards full width minus
  48 px, the caption block about 280 px from the bottom (clear of the platform's buttons).
- Something new every 1.5 to 3 s: a punch-in, a caption emphasis, a cutaway.
- End on the payoff or a line that loops back to the first frame. No outro, no "follow for more" card.
