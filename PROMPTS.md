# Prompts

Put the clip in `videos/<name>/raw/` and optional look references in `videos/<name>/references/`. Optional brand
files (logo, colours, fonts, guide) go in the workspace `brand/` (shared by every video) or `videos/<name>/brand/`.
Start a fresh conversation per video. The agent analyses, researches, storyboards, asks you
what is still open in one message, waits for your approval, then renders to `videos/<name>/Exports/`.

Defaults you do not need to ask for: studio-clean audio (two passes, once each), Hinglish transcript in Roman script,
a tight cut that never clips a word, research-backed graphics from the HyperFrames catalog, semi-bold captions with
highlighted keywords, and a fade to black at the end.

## Talking-head reel (Hinglish)

```text
Edit videos/[name] into a 9:16 Instagram Reel. Research the topic and the numbers I mention, and add graphics and
b-roll that explain them. Use the [business-explainer / clean-creator] style. Show me the plan before rendering.
```

## Explainer for YouTube

```text
Make a 16:9 YouTube video from videos/[name]. Keep the full explanation but cut retakes and dead air. Research [topic]
for charts, headlines and maps that support what I say. Light background music from music/[file] under the voice.
```

## Short from a long recording

```text
From videos/[name], suggest 3 self-contained 30-60 s moments for Shorts with their timecodes. After I pick one, cut
it tight, reframe to 9:16 on my face, and edit it like a reel.
```

## Tutorial / screen recording

```text
Turn videos/[name] into a [9:16 / 16:9] tutorial. Keep every step and keep the screen readable; zoom or call out only
what is actually on screen. Use the tech-minimal style.
```

## Product or story video

```text
Edit videos/[name] as a [product showcase / founder story] for [platform]. Keep the silent product shots. Use the
references in references/ for the look. No claims that I do not say or that research cannot source.
```

## Match a reference

```text
Watch references/[file] and tell me what makes it work (pacing, captions, graphics, sound). Then edit videos/[name]
in that style, keeping my brand files in brand/.
```

## Useful follow-ups

```text
Keep 0:41-0:48, it matters. Drop the part where I talk about [x].
```
```text
The voice still has echo / sounds watery - re-clean it stronger / lighter and show me the before-after.
```
```text
Highlight these words in the captions: [crore, IPO, profit]. Captions a bit bigger.
```
```text
That number on screen at 0:23 - show me the source. Replace the chart with a counter block from the catalog.
```
```text
End with a longer fade (2 s).
```
