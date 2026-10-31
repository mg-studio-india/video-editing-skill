# Creative prompts for video edits

Choose one prompt, replace the bracketed details, and start a fresh conversation for each project. Give the agent the folder that should own the edit. Put source footage in that folder's `raw/`, visual references in `references/`, and brand guides and assets in `brand/`.

Each prompt is a creative brief, not a prewritten storyboard. The video pipeline should inspect the footage, references, and brand materials; use the actual project evidence to shape the edit; and follow its review and approval gates. If no reference is supplied, it should offer a few relevant directions from the bundled style index and wait for your choice. References guide visual language, while the brand guide sets requirements. Keep the two separate from facts about the footage.

The pipeline should ask one concise batch of only unanswered decisions: what to keep or cut, platform and aspect ratio, creative direction, framing, captions, and sound. The current simple phrase captions and strong dereverb are defaults. Assembly waits for your approval. Project work stays in `.video-pipeline/`; verified exports go to `Exports/`.

## 1. Visual-first product showcase

For product footage with little or no dialogue. This prompt directly protects visual-only product footage from being cut just because it is silent.

```text
Edit the project `[PROJECT FOLDER]` as a visual-first product showcase using `[SOURCE CLIP OR raw/]` for `[PLATFORM / ASPECT, or ask me]`.

Inspect the full sequence, including quiet and silent sections, and build the edit around the product actions and details that are actually visible. Preserve the product demonstration and its meaningful sequence unless I approve specific removals. No dialogue is not a reason to delete a shot. Do not invent product features, benefits, claims, specs, testimonials, labels, or missing b-roll. Use supplied references only for visual direction and follow the brand guide. Keep negative space clean; use a local HyperFrames composition only if it serves a real, approved moment. Show me the evidence-based plan and proposed cuts, then wait for approval before assembly.
```

## 2. Product launch with presenter or voiceover

For a launch piece where speech and product footage both matter.

```text
Create a `[LENGTH, if known]` product launch edit in `[PROJECT FOLDER]` from `[SOURCE CLIP(S)]` for `[PLATFORM / ASPECT]`.

Let the presenter's verified words and the actual product footage determine the structure. Pair a spoken point with a product shot only when that shot genuinely illustrates it; do not imply an unshown capability or result. Keep useful product detail shots even when no one is speaking. Inspect the brand guide and references before proposing color, type, pacing, or motion. Do not force a hook, feature list, verdict, or CTA. Ask me about missing creative and technical choices together, then show a source-linked plan and wait for approval.
```

## 3. Talking-head explainer or lesson

For a single-speaker educational video, either full-length or as a short excerpt.

```text
Edit `[SOURCE CLIP]` in `[PROJECT FOLDER]` into a `[FULL EXPLAINER / SHORT EXCERPT]` for `[PLATFORM / ASPECT]`.

Preserve the speaker's intended meaning and enough context to understand each point. Use verified transcript wording; do not rewrite speech into claims, add unsupported statistics, or impose a fixed hook / numbered-points / verdict structure. Tighten only false starts and pauses that harm the flow, preserving natural emphasis and breaths. Keep the speaker as the visual focus. Add an overlay only when it clarifies a specific spoken idea and is supported by the footage or supplied materials. Follow the brand and any selected reference; keep current simple phrase captions unless I choose otherwise. Show proposed cuts before assembly.
```

## 4. Interview or podcast segment

For conversations where question, answer, and listener reaction depend on one another.

```text
Shape `[SOURCE CLIP(S)]` in `[PROJECT FOLDER]` into a `[LENGTH / PLATFORM / ASPECT]` interview or podcast edit.

Build around the strongest complete exchange supported by the recording. Preserve enough of each question and answer to keep its meaning; do not splice separate statements into a new claim or remove context to manufacture conflict. Use reaction shots and alternate angles only when they are present and belong at that moment. Keep conversational pauses when they carry emotion or turn-taking. Avoid decorative cards and invented speaker labels. Review the references and brand guide before choosing the visual treatment, then show me the selected passage and proposed cut for approval.
```

## 5. Tutorial or screen recording

For software demos, walkthroughs, and how-to videos where screen legibility is central.

```text
Turn `[SCREEN RECORDING AND OPTIONAL CAMERA CLIP]` in `[PROJECT FOLDER]` into a `[TUTORIAL / WALKTHROUGH]` for `[PLATFORM / ASPECT]`.

Keep the real interface, cursor actions, and step order legible. Base any callout on text or controls that are actually visible, and use the narration only for instructions that are actually spoken. Never fabricate interface states, results, values, or steps. Crop or zoom only when it improves readability without hiding context; use a split view only if both supplied views help explain the same moment. Preserve the brand's visual rules, keep the treatment restrained, and show me the proposed structure and any reframing before assembly.
```

## 6. Mini-documentary or founder profile

For an observational, personal, or documentary-style story.

```text
Edit `[SOURCE CLIPS]` in `[PROJECT FOLDER]` as a `[LENGTH]` mini-documentary about `[SUBJECT, if known]` for `[PLATFORM / ASPECT]`.

Find the narrative in what the footage and verified speech actually establish. Respect chronology when it matters; do not invent a turning point, motivation, stakes, or resolution. Use supplied archival or supporting footage only for what it shows, and distinguish it from the interview or present-day footage. Let meaningful pauses and visual moments breathe. Use references for visual grammar and the brand guide for constraints, without borrowing their claims or story structure. Present the evidence and proposed sequence before cutting.
```

## 7. Before-and-after or comparison demo

Use only when the source actually contains both states or both items being compared.

```text
Make a `[PLATFORM / ASPECT]` comparison edit from `[SOURCE CLIP(S)]` in `[PROJECT FOLDER]`, comparing `[ITEMS OR STATES, if established by the source]`.

First verify that both sides of the comparison are present and identifiable in the footage or supplied materials. Keep the comparison fair: align like with like where possible, preserve relevant context, and do not invent measurements, improvements, causes, or a winner. If the evidence does not support a clear comparison, tell me what is missing and propose a footage-led edit instead. Use split-screen, labels, or a local HyperFrames composition only if they make the actual comparison easier to understand. Show me the evidence and plan for approval.
```

## 8. Social cutdown from a longer video

For selecting a self-contained passage from a long source before reframing it for social.

```text
Find a `[DURATION]` cutdown in `[SOURCE VIDEO]` inside `[PROJECT FOLDER]` for `[PLATFORM / ASPECT]`.

Review the full source and suggest up to `[NUMBER]` self-contained passages with source timecodes, a short description of what each passage says or shows, and any context that would be lost. Do not cut yet. After I choose, preserve the chosen passage's meaning and continuity; do not stitch distant phrases into a new claim. Check every proposed crop against the actual frames so faces, hands, products, and important screen text remain visible. Keep current simple phrase captions unless I request another treatment. Wait for my selection and approval before assembly.
```

## 9. Silent or natural-sound montage

For visual sequences where speech is absent or should not drive the edit.

```text
Create a `[LENGTH / PLATFORM / ASPECT]` visual montage from `[SOURCE CLIP(S)]` in `[PROJECT FOLDER]`.

Use the actual images, movement, and changes in the source to find the rhythm. Preserve product demonstrations and other important visual actions even when they have no dialogue. Do not add voiceover, explanatory text, or a narrative the footage cannot support. Keep useful original sound; ask before adding supplied or licensed music or effects. Let a shot hold when its detail needs time, and avoid dividing the runtime into arbitrary equal sections. Show me the selected source moments and proposed order before assembly.
```

## 10. Reference-led brand film

For an edit where the user supplies an example video, image, or PDF brand guide.

```text
Create a `[FORMAT / LENGTH / PLATFORM / ASPECT]` edit in `[PROJECT FOLDER]` from `[SOURCE CLIP(S)]`, using `[REFERENCE FILES]` for visual direction and the supplied brand guide for brand rules.

Analyze the source and each reference separately. Describe the reference's usable visual language—such as pacing, framing, typography, color, or motion—then adapt only the parts that fit the actual footage and brand. Do not transfer reference copy, products, claims, logos, story beats, or layouts automatically. Make the brand guide's requirements and exclusions explicit in the proposal. Select local HyperFrames assets only when their purpose fits an approved source moment. Show the references, source evidence, and proposed treatment together; wait for my approval before assembly.
```

## Useful follow-up notes

Use these after reviewing a plan or preview:

```text
Keep `[time range / action]`; it is essential to the product demonstration. Remove only `[specific range]`.
```

```text
The crop at `[timecode]` hides `[face / hand / product detail / screen text]`. Preserve the full frame there and show me a revised preview.
```

```text
Keep the current simple phrase captions. Move them clear of `[specific visible detail]`; do not add other titles or cards.
```

```text
Use the selected reference for `[specific visual quality]` only. Keep the source's actual story and the brand guide's requirements.
```

```text
Keep strong dereverb, but compare the processed audio with the original around `[timecode]`. Use the cleaner-sounding version if the processing damages a word ending.
```
