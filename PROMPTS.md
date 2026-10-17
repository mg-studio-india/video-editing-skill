# The Prompts to Type

Copy them and change the parts in [brackets]. Plain words work at every step; these are just the shapes that get the
right skill moving first time. Start every new video in a new thread.

## Setup

> Run the video-pipeline setup check and fix anything it finds.

Then start a new thread.

## Start an Edit (Context & Format First)

**Context-driven edit (Recommended - agent analyzes transcript, proposes formats, and discusses every step):**

> Watch and transcribe videos/[project]/raw/[clip].mp4. Analyze the content context, propose 3-4 suitable video formats from the 225-Style Taxonomy, and let's discuss visuals, cuts, pacing, b-roll, color grading, and captions before storyboarding.

**Suggesting additional content to record:**

> What additional b-roll or demonstrations should I record to make videos/[project] significantly better?

**Several clips or multi-take footage:**

> Analyze the clips in videos/[project]/raw/. Propose the best narrative structure, suggest any missing b-roll I should film, and let's align on the video format.

**Face camera plus a screen recording:**

> Edit videos/[project]/raw/[face].mp4 with the screen recording [screen].mov. Use split-screen when I'm demoing, full screen when the screen matters.

**Shorts from a longer video:**

> Find the best 3 to 5 Shorts in videos/[project] and show me the list before cutting anything.

---

## At the Verification Gates

The edit stops at key verification points and waits for your confirmation.

**Gate 0: Research & Reference Direction (`video-researcher`)**
Review topic facts, logos, and market benchmarks:

> Approved. The Stacked Split-Screen layout and electric cyber palette look great. Use the second reference reel's hook style.
> Change the logo for [tool]: use their dark mode icon. Focus the hook on [specific insight].

**Gate 0.5: Pre-Storyboarding Collaborative Alignment**
Discuss all dimensions before locking the storyboard:

> Let's go with the Clean Authority Talking-Head format. Keep the headroom clean (no floating boxes over my head). Let's use 1.8s cuts, smooth light leak transitions, and the Commercial Clean color grade. I'll record a 5-second b-roll clip of the app to insert at 0:20.

**Gate 1: Storyboard & Technical Matrix (`video-plan-storyboard`)**
Review the hook, visual scenes, and scene order:

> Approved. Change one thing: replace the card list at "[phrase]" with a full-frame b-roll cutaway.
> Make the hook punchier: cut directly to the claim at "[phrase]".

**Gate 2: Flat Cut & Color Grade (`video-cut-audit` & `grade.py`)**
Inspect cut pacing and choose the color grade:

> Show me the color grading preview comparison sheet for this video.
> Use the Commercial Clean color grade. The cuts feel great; keep the 200ms breath after "[phrase]".

**Gate 3: Theme, Typography & Surface Palette (`video-style`)**

> The Poppins Black + Syne pairing looks sharp. Make the accent color emerald green (#10B981) and use frosted glass cards in the lower third.

**Gate 4: Caption Sample (`video-captions`)**

> Captions look good. Keep the natural phrase flow mode with smooth active word highlighting. No single orphan words.

**Gate 5: Final Review & Master (`video-review-gate`)**

> At 0:14 the caption covers my chin. At 0:31 the cards come in late. The music is too loud after 0:50.
> Everything looks clean and polished. Deliver the final master!

---

## Color Grading & Visuals

**Preview color grades:**

> Run grade.py preview on videos/[project] and show me the comparison contact sheet.

**Apply specific grade:**

> Apply the Cinematic Warm color grade with +10% contrast.

**HyperFrames Catalog components:**

> Search HyperFrames catalog for animated metric counters and feature pill cards for videos/[project].

---

## Make it Learn

After every round of notes that should apply to future videos:

> Save this to the skill.

Or be specific:

> Save this to the skill: never place floating checklist cards over the speaker's forehead; keep all cards in the lower third.
