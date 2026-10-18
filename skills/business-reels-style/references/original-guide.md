---
name: business-reels-style
description: Use when authoring or restyling short-form business, creator, interview, finance, entrepreneurship, D2C, or marketing videos in HyperFrames and you need an evidence-aware visual and motion direction informed by Raj Shamani, Nitin Joshi, Markets with Jayant, Bypreneurs, D2C by Nikhil, and Marketing with Govind.
---

# Business Creator Reels Style

## Mission

Create short-form vertical videos that communicate a business idea quickly, preserve the speaker's credibility, make evidence legible, and give each edit a coherent visual rhythm. This is a **composite production style**, informed by publicly accessible traces of six reference channels; it is not a claim that the six channels share one brand system.

Use this skill as a style layer alongside the installed HyperFrames skills. It does not replace the core renderer or its animation/runtime instructions.

## Evidence contract: never pretend to have seen what was not inspected

The user specifically requested that the styling be extracted from top-trending videos and that nothing be assumed. Treat the strength of evidence as a requirement, not a footnote.

### Evidence levels

Use the following labels in analysis notes and handoff documents:

- **VIDEO-FRAME VERIFIED** — a frame or screen recording from the exact account's Reel was directly visible and inspected.
- **PUBLIC CROSS-POST FRAME** — a frame from a public post/cross-post associated with the creator was inspected, but it is not proven to be an Instagram Reel or a top-performing item.
- **POST/TEXT VERIFIED** — the specific public post, caption, or transcript was readable, but the moving image was not fully inspectable.
- **PROFILE/METRICS ONLY** — public profile metadata or aggregate performance estimates were available; visual execution was not verified.
- **UNVERIFIED** — no suitable evidence was found. Do not fill gaps with genre stereotypes.
- **PRODUCTION DEFAULT** — a proposed implementation choice for the requested deliverable. It is not an observed fact about a reference account.

Never upgrade evidence from one level to another because a design choice seems plausible.

### “Top trending” selection rule

Do not call a Reel “top”, “viral”, “best-performing”, or “trending” unless evidence supports that classification.

1. Prefer a platform-visible view/play count for each candidate Reel and record the capture date.
2. Confirm that the metric means views/plays rather than likes, comments, or a third-party grid count. Third-party indexes often display multiple unlabeled numbers.
3. When comparing posts from different dates, report raw views and posting age. Where it is useful and enough dates are available, add an explicit normalized comparison; never silently equate a 2-day-old post and a 2-year-old post.
4. For an account-wide “top” ranking, establish the sample scope (for example, “top 5 among 20 accessible Reels posted in the last 90 days”). Do not imply exhaustive account coverage if it is not exhaustive.
5. If counts, dates, or ranking scope cannot be confirmed, call the sample “accessible examples” or “candidate high performers,” not “the top videos.”
6. A high view count does not itself prove that a particular color, font, transition, or pacing choice caused performance.

### Account-level evidence state for the current research pass

The research audit in `references/research-audit.md` is part of this skill. It lists sources, known limitations, and account-by-account verification status. At the time this package was written, **the evidence did not support a definitive top-Reel ranking for every one of the six accounts**. Do not write that all six accounts' top videos were fully watched. Treat this skill as an evidence-aware first-pass synthesis and upgrade it after direct frame review.

## When to use

Use this skill when:

- building a vertical Reel/Short about business, entrepreneurship, consumer brands, market analysis, marketing, or founder stories;
- turning a talking-head or podcast excerpt into a short-form video;
- mixing narration with source-backed screenshots, data, product footage, charts, or B-roll;
- creating a consistent style system across a recurring series while keeping evidence and speaker authenticity intact;
- comparing or auditing style from the six named references.

## When not to use

- Do not use this as proof of the exact native brand guideline for any one creator.
- Do not use it to imitate a specific creator's voice, face, or identity. It is about general editorial techniques and visual grammar, not impersonation.
- Do not invent source material, financial statistics, screenshots, quotes, logos, or branded UI.
- Do not use the composite palette or typography as an assertion about the original channels.
- If the user requires exact account-faithful style extraction and only metadata is available, state what cannot be verified and ask for screen recordings, downloaded sample videos, or frame captures before claiming the result is exact.

## Required workflow

### 1. Load the HyperFrames implementation context

Before producing a composition:

1. Read the installed `/hyperframes` skill and follow its routing instructions.
2. Read `/hyperframes-core` before implementing a composition.
3. Read `/hyperframes-creative` for composition and design-spec guidance.
4. Read `/hyperframes-animation` before choosing animation syntax, easing, sequencing, or seeking behavior.
5. Read any relevant asset/media-use skill before adding externally sourced images, logos, video, or music.
6. Treat this file as the visual direction layer, not as a substitute for the runtime, timing, rendering, or asset policies in those skills.

Do not invent HyperFrames attributes or animation APIs from memory. Use only the implementation syntax documented by the installed skills and current project examples. Ensure animations are deterministic and remain correct when the render timeline seeks directly to any time.

### 2. Audit the available reference evidence

For each requested account:

1. Open the exact profile, not a look-alike account.
2. Identify candidate Reels using available view/play counts and posting dates.
3. Record Reel URL, date, captured views, likes/comments if available, duration, and the selection method.
4. Open the candidate Reel itself and inspect the actual video, not only its profile tile, title, caption, transcript, or third-party thumbnail.
5. Inspect the opening, representative middle moments, major transitions, final beat, captions, graphics, and audio.
6. Record frame-level findings in the audit table below; separate direct observation from interpretation.
7. If the Reel cannot be played, say so. Do not report motion, exact frame layout, font, palette, cut frequency, or sound design that the evidence did not reveal.

Use this minimum inspection checklist per Reel:

- First 0-2 seconds: hook format, first shot, on-screen text, speaker framing, sound entrance.
- Early setup: context and visual hierarchy.
- Middle: cut rhythm, angle changes, B-roll frequency, caption behavior, callouts, charts, screenshots, and overlays.
- Reveal or proof: how a number, claim, company, product, or source is shown.
- Ending: conclusion, loop, question, CTA, or abrupt end.
- Audio: voice treatment, music, transitions, sound effects, pauses, and relative loudness.
- Technical details only when directly measurable: duration, aspect ratio, frame rate, shot lengths, text placement, and colors.

### 3. Create a fact/interpretation/default ledger

Every material style claim should be assigned one of these labels:

| Label | Meaning | Permitted phrasing |
|---|---|---|
| Observed | Directly seen/heard in the specific Reel | “In the inspected sample, the hook uses…” |
| Repeated | Seen in at least two independently inspected posts from the same account | “Across the inspected samples…” |
| Interpretation | A reasonable explanation for a choice, not directly stated by the creator | “This may function as…” |
| Production default | A choice being proposed for this new deliverable | “Use this starting preset…” |
| Unknown | Not available or not measurable | “Not verified from the available source.” |

Do not turn an interpretation into an observation. Do not call a single screenshot a recurring brand rule.

### 4. Write the design brief before coding

Create a compact design spec before writing the composition:

- editorial goal and audience;
- exact source assets and rights/provenance;
- vertical canvas and delivery constraints;
- palette and font choices, each labeled observed or production default;
- speaker and evidence layout;
- caption system;
- motion behavior and timings;
- transitions and sound rules;
- safe zones;
- sources and factual qualifiers;
- known deviations from reference evidence.

If the work is a composite of all six channels, state that the system is a designed synthesis. If the user asks for one account specifically, do not blend the other accounts in without permission.

### 5. Build, render, and verify

1. Make the essential composition readable with motion disabled.
2. Add motion only after hierarchy and timing work in a static frame.
3. Implement all time-based behavior using the documented HyperFrames primitives.
4. Keep all motion deterministic, seek-safe, and within the scene's timeline.
5. Render a preview and inspect opening, middle, reveal, and ending frames.
6. Run the project's documented check/lint command (use the installed HyperFrames command rather than guessing if it differs by version).
7. Inspect the actual rendered output for text collisions, clipped captions, wrong fonts, layout drift, seek issues, missing media, audio peaks, and unreadable sources.
8. Report what was verified and what remains unverified in the handoff.

## Evidence-based synthesis from the six reference accounts

This section is deliberately narrower than a generic creator-video playbook. Only the evidence in the accompanying research audit supports the account-specific observations below.

### Raj Shamani — storytelling/podcast reference

**Evidence status:** one public cross-post frame was inspected; third-party analytics pages expose aggregate view estimates, but the exact highest-viewed Instagram Reel and its moving edit were not confirmed.

**Observed in the cross-post frame:** a podcast/interview setting, speaker-led framing, a black top banner, bold uppercase white text, and one red-emphasized word. The frame appears associated with Raj Shamani's public content, but it is not proven to be the top Instagram Reel.

**Permitted design lesson:** test a direct claim in a high-contrast headline band, and reserve a single accent color for one key word. Maintain the speaker as the primary visual. Label this as an inspiration derived from a cross-post frame, not as a full account style rule.

**Not verified:** precise font family, native Instagram Reel color values, typical crop scale, cuts per minute, caption timing, sound effects, transitions, or the most-viewed Reel's full structure.

### Nitin Joshi — direct-to-camera/business reference

**Evidence status:** public profile metadata, a third-party video thumbnail, post text, and aggregate/third-party Reels metrics were found; a full top-performing Reel could not be verified frame by frame.

**Observed in a public video thumbnail:** direct-to-camera delivery, a casual indoor setting, speaker prominent in the shot, and a small account label in the lower-left region. The thumbnail is not enough to infer the full animation system or prove that the clip was the account's best performer.

**Permitted design lesson:** a straightforward speaker-led frame can be the base layer; add graphics only when they clarify the business point. Treat the lower-left bug as a sample detail, not a mandatory rule.

**Not verified:** repeated composition across Reels, exact typography, transition behavior, color grade, pacing, or highest-viewed clip structure.

### Markets with Jayant — evidence-led explanation reference

**Evidence status:** one specific public Reel transcript/page was accessible with an explicit play count (136.5K plays as shown by that source), date, and duration (144.4 seconds). Its position as the account's all-time or current top Reel was not established. The page includes a transcript, not a complete directly inspected video.

**Verified content structure in this sample's transcript:** a strong opinionated opening, case/context setup, an explanation of the relevant entity/rule, an evidence or document reveal, rhetorical questions, a change/reveal, and a prompt encouraging viewers to verify the claim. This describes the transcript structure only; it does not prove how each stage was animated on screen.

**Permitted design lesson:** for analysis content, structure narration as claim → context → evidence → implication → invitation to verify. Clearly distinguish confirmed facts from allegations or interpretation. Attribute source documents and show the relevant passage only when the actual document is available and checked.

**Not verified:** exact font, colors, chart style, B-roll treatment, caption animation, cut frequency, audio bed, or full visual execution of this Reel.

### Bypreneurs — cinematic-text reference

**Evidence status:** public profile data and one accessible image from the profile were inspected; the image's content type and whether it belongs to the highest-performing Reel were not proven. Third-party profile tiles contain “2m” and “1m” labels, but the labels were not explicitly defined as view counts in the accessible source.

**Observed in the available image:** two contrasting visual panels, warm/low-key footage stills, bold white sentence fragments, simple line breaks, and a small BYPR/catchphrase signature. It contrasts an older person in a home setting with a younger person in an elevator, with the text split between the two scenes. It is not verified as a Reel frame from a top-performing item.

**Permitted design lesson:** use the scene itself to carry part of the meaning; use short white text fragments that read as one thought across sequential images. Ensure that the cut between scenes adds meaning rather than acting as decoration.

**Not verified:** the actual motion between the panels, typeface, exact color grade, recurring logo behavior, music, and high-performing Reel ranking.

### D2C by Nikhil — D2C-growth reference

**Evidence status:** profile-analysis metadata identifies the account and describes its D2C/growth focus; aggregate metrics were available. No individual Instagram Reel frame or reliable ranked top Reel was confirmed in this research pass.

**Verified at profile/metadata level:** account positioning relates to D2C marketing, brand scaling, Meta ads, and growth systems. This supports choosing relevant subject matter, but it does not establish its visual design language.

**Permitted design lesson:** when creating a D2C case study, make the actual business mechanic visible—e.g., product, funnel stage, ad example, unit economics, or retention loop—only when grounded in the source material. Do not attribute a specific chart/animation template to this account without footage.

**Not verified:** color palette, fonts, caption placement, shooting setup, camera movement, transitions, audio signature, or the highest-viewed Instagram Reel.

### Marketing with Govind — marketing education reference

**Evidence status:** a public analytics page identified the account and showed aggregate metrics. No exact top Reel or inspectable video frame was confirmed in this research pass. Similar-name creators should not be substituted.

**Verified at profile/metadata level:** account naming and profile index point to digital marketing education. This does not verify its actual visual or motion choices.

**Permitted design lesson:** for a marketing education deliverable, make each tactic easy to apply and distinguish example, explanation, and action. This is a production design decision, not a claim about the account's native style.

**Not verified:** palette, typography, caption animation, B-roll system, transition style, sound design, exact Reel ranking, or top-performing video's structure.

## Composite style direction for a new video

Use this only when the brief asks for a combined style inspired by the six channels. It is a **production synthesis**, not the native brand system of any source account.

### Creative principle

**Editorial credibility first; high-energy emphasis second.** The story and evidence should carry attention. Typography and movement may strengthen emphasis but must not make ordinary claims look like facts or disguise missing evidence.

### Palette tokens

The account sample is too limited to claim a shared palette across the six references. The following tokens are editable **production defaults** for a neutral, cinematic starting point. They are not color-picked values from the accounts.

```css
:root {
  --bcr-bg: #171717;          /* production default: charcoal */
  --bcr-surface: #252525;     /* production default: raised panel */
  --bcr-text: #F5F1EA;        /* production default: warm white */
  --bcr-muted: #B9B5AE;       /* production default: secondary text */
  --bcr-accent: #D9413A;      /* production default: muted red accent */
  --bcr-line: #4A4845;        /* production default: divider */
}
```

- Red is a reasonable *starting* accent because a red-emphasized word was visible in one Raj-associated cross-post frame; `#D9413A` is a design token, not an exact sampled color.
- White text on cinematic footage was visible in one Bypreneurs-associated image. That does not prove all its posts use this treatment.
- Do not introduce neon lime, bright blue, or any other “signature” hue without a supplied brand guide or a measured frame sample.
- When editing a specific creator's video or a client brand, replace these defaults with sampled/approved colors and record the source.
- Preserve natural skin tones. Do not apply a universal dark grade to every asset.

### Typography tokens

No exact font family was verified for the reference samples. Use these as **implementation defaults only**, and test language support:

- Display: a bold sans serif with good condensed/compact options; candidate default is `Inter` 700-800 or a project-installed equivalent.
- Captions/body: `Inter` 500-700 or the closest installed readable sans serif.
- Hindi/Devanagari: choose a tested Devanagari-compatible font such as `Noto Sans Devanagari`; confirm glyphs and shaping in the actual render.
- Numbers: use lining numerals and consistent formatting; never strip units or contextual qualifiers.
- Avoid using more than two font families within a single deliverable unless a documented brand guide requires it.

### Screen geometry

The values below are starting values for a 1080 × 1920 vertical canvas, not measured reference-account settings:

- Primary headline: generally 1-4 concise lines; prioritize word wrapping and reading speed over a fixed pixel size.
- Side margin: start around 80-100 px and test in the actual platform interface.
- Keep the top 180 px and bottom 300 px relatively free of critical copy until the target platform UI has been checked.
- Use two main information zones at most in a typical frame: speaker/footage plus captions, or chart plus data label.
- Never cover eyes, mouth, product identifiers, chart labels, or the key passage in a source document.
- Use large enough body text to remain legible on a phone; review at actual size, not only in a desktop preview.

### Shot and frame hierarchy

Use a hierarchy that matches the content:

1. **Person-led:** speaker is the focal point; the hook/caption supports, not competes with, the face.
2. **Evidence-led:** source document, chart, product, or company visual is focal; speaker can become voiceover or a secondary picture-in-picture only if it remains readable.
3. **Concept-led:** diagram, sequence, or number is focal; keep the background quiet.
4. **Contrast-led:** two scenes or two states are compared; align their text treatment and make the comparison factual and immediately clear.

Avoid adding B-roll solely to hide a jump cut if it is unrelated to the spoken topic.

## Motion specification

The exact motion behavior of most account samples was not measurable. Every timing below is an **editable production default**, not a claim about any creator's actual edit.

### Motion hierarchy

- **Primary:** editorial hard cuts, clean reframes, and phrase-synchronized text reveals.
- **Secondary:** subtle scale changes, short slide/fade callouts, simple chart builds, and relevant B-roll cuts.
- **Rare:** whip transitions, large zooms, shake, glitch, kinetic full-screen type, or dramatic sound hits. Use only when the meaning supports it.
- **Avoid:** perpetual motion, random animated decorations, bounce on every caption, transitions on every cut, and effects that obscure facts.

### Starting animation timings

Use these as an initial timing vocabulary and adjust after rendering:

| Element | Starting duration | Behavior | Constraint |
|---|---:|---|---|
| Headline reveal | 180-280 ms | opacity plus a short vertical settle | No long title-card intro before the content hook |
| Keyword emphasis | 100-180 ms | subtle scale/weight/accent change | One key phrase at a time |
| Callout/label | 220-360 ms | opacity plus short directional movement | Keep the label attached to its referent |
| Camera punch-in | 220-350 ms | modest crop/scale change | Motivate it with a meaningful assertion or reaction |
| Chart build | 350-800 ms | sequential reveal or draw | Use only when the data order is meaningful |
| Scene transition | 150-300 ms when not a hard cut | brief dissolve/slide | Default to a clean hard cut if an effect adds no meaning |
| End signature | 200-400 ms | simple settle/fade | Keep it brief; do not let it delay the conclusion |

These are not hard requirements. Preserve the cadence and usability of the speech; use the shortest animation that clearly communicates the change.

### Motion pattern: claim → evidence → implication

For an analysis Reel:

1. Open on the claim, question, or important outcome. Do not open with a logo unless explicitly required.
2. Establish the entity, timeframe, and relevant context.
3. Introduce evidence one meaningful element at a time.
4. Reveal the inference only after the evidence is visible or adequately explained.
5. End with the implication, a clearly framed question, or an invitation to check the underlying source.

This structure is supported by the accessible Markets with Jayant transcript sample; it is an editorial pattern, not a claim about the clip's precise animation.

### Motion pattern: text split across visual contrast

When making a scene-pair or visual comparison:

1. Let the first frame introduce the first state with a short text fragment.
2. Cut to a genuinely contrasting or explanatory second state.
3. Complete the thought with aligned typography and comparable readability.
4. Keep the copy semantically continuous; do not imply a causal relationship that the evidence does not support.

This is inspired by the two-panel Bypreneurs-associated image in the audit; actual moving transition behavior was not verified.

### Motion pattern: speaker-led hook

1. Start the speaker audio at the actual hook or a clean pickup from it.
2. Use a clean medium close-up or close-up from the source footage; do not simulate a second camera angle with an excessive crop.
3. Reveal the hook phrase with the speaker's statement rather than a disconnected title animation.
4. Use a modest punch-in only on a high-value beat, if the source resolution allows it.
5. Return to a stable frame for longer explanation or dense language.

This is a proposed production preset informed by publicly visible speaker-led samples, not a verified universal behavior of the channels.

## Captions, headlines, and overlays

- Subtitle phrasing should match the audio exactly, including negation, qualifiers, names, and numbers.
- Prefer natural phrase groups to word-by-word bouncing for complex explanations.
- Highlight one key phrase per caption beat at most. Use weight, background, or one accent color; do not rely on color alone to communicate meaning.
- Do not let a headline restate the same full sentence shown in captions unless the duplication is intentionally part of the creative.
- Keep source labels separate from the editorial headline. A claim and its evidence should not look like one unqualified sentence when they are not.
- Do not add fake social-media comment UI, fabricated view counts, invented engagement counters, false news banners, or counterfeit platform interface elements.
- If a creator name, logo, or handle is shown, use a supplied/verified asset or a text treatment that does not pretend to be the original logo.
- For Hindi/Hinglish copy, proofread mixed-script captions and line breaks manually.

## Evidence, charts, and business claims

The Markets with Jayant sample reinforces a particularly important rule for business content: the story can be forceful without presenting unverified allegations as settled facts.

- Preserve the source's exact time period, metric definition, unit, and denominator.
- Cite primary/credible sources on screen when possible; put longer citations or URLs in an accompanying caption/reference note.
- Distinguish documented fact, attributed allegation, opinion, and inference with clear wording.
- If a chart is illustrative, mark it “illustrative” and disclose assumptions.
- Never invent revenue, valuation, conversion-rate, market-share, CAC, ROAS, customer-count, or return figures.
- Do not use a stock image or unrelated company screenshot as if it were primary evidence about a named company.
- If you show a report/screenshot, ensure that the displayed portion supports the spoken claim and is readable long enough to verify.
- If the evidence is incomplete, say so on screen or narratively instead of concealing the gap with editing.

## Sound design

No consistent music/SFX style could be verified across all six channels from this research pass. Use the following only as production defaults:

- Voice/dialogue is the priority. Clean noise and uneven levels without making the voice harsh or unnaturally gated.
- Duck any music beneath speech. Avoid emotional scoring that implies a certainty or drama unsupported by the content.
- Add a sound accent only when a visual reveal needs reinforcement; a silent reveal is often sufficient.
- Keep cuts and SFX from masking consonants, especially for Hindi and English code-switching.
- Check loudness, peaks, phase, and beginning/end tails in the rendered file. Follow the project's delivery spec if one is supplied.
- Use only music and sound effects permitted by the asset license and destination platform.

## Edit templates

Use these as reusable *content structures*, not as claims that any account always uses them.

### Template A — founder/podcast moment (15-45 seconds)

1. Hook (0-2s): strongest complete statement, not an out-of-context fragment.
2. Context (2-6s): identify the speaker/topic if unclear.
3. Story/argument: retain the cause-and-effect chain; remove dead time, not essential nuance.
4. Support: one or two relevant captions or real supporting visuals.
5. Resolution: preserve the full point; avoid an arbitrary end-card interrupting the sentence.

### Template B — business/market case study (30-90 seconds, or longer if needed)

1. Claim/question.
2. Entity + timeframe.
3. Background and primary-source context.
4. Evidence or mechanism, shown in digestible steps.
5. Implication or limitations.
6. Source prompt / conclusion.

Do not force a 90-second maximum if the information requires longer and the user has not specified a runtime. The accessible Markets with Jayant example was 144.4 seconds, so longer explanation is possible in this reference set.

### Template C — D2C/marketing education (15-45 seconds)

1. Name the problem/outcome.
2. State the relevant framework in plain language.
3. Explain one step at a time with a concrete, sourced example.
4. Show the metric/action the audience should inspect.
5. Summarize the usable lesson without making unsupported promises.

### Template D — contrast/retention edit

1. Introduce state A.
2. Introduce a genuinely comparable state B.
3. Make the contrast legible using aligned text or matched framing.
4. Explain what the contrast does—and does not—prove.
5. End with a conclusion that follows from the evidence.

## Production checklist

### Before editing

- [ ] Correct account and exact source Reel identified.
- [ ] “Top-performing” status supported by view/play counts and a defined comparison set, or the video is labeled as an example rather than a top Reel.
- [ ] Source footage/frame inspection level documented.
- [ ] Core claim, context, evidence, and ending captured in a one-line beat sheet.
- [ ] Rights/provenance checked for photos, product images, reports, logos, music, and screenshots.
- [ ] Every observed style claim is separated from interpretation and production defaults.

### During editing

- [ ] The first frame has a meaningful hook; no unnecessary intro.
- [ ] Speaker, text, and evidence have one obvious visual hierarchy.
- [ ] Captions are faithful and manually proofread.
- [ ] Motion emphasizes a meaningful change, not every word.
- [ ] B-roll or charts are relevant and factually labeled.
- [ ] Accent color is used deliberately and consistently.
- [ ] No platform UI, metrics, quotation, or source is fabricated.
- [ ] Required HyperFrames runtime/animation instructions followed; timeline behavior is deterministic and seek-safe.

### Before delivery

- [ ] Render inspected at 0%, 10-20%, middle, reveal, ending, and any dense text/chart moments.
- [ ] Phone-size readability checked.
- [ ] Safe zones validated against the target publishing surface.
- [ ] No clipping, reflow, missing assets, frame flashes, or unsupported fonts.
- [ ] Voice is intelligible; no loudness spikes or masked words.
- [ ] Every business/statistical claim is verified and appropriately attributed.
- [ ] Handoff names measured facts, selected production defaults, and outstanding unknowns.

## Required handoff format

Include this short handoff whenever the skill is used:

- **Deliverable:** runtime, canvas, format.
- **Style basis:** which accounts and inspected sample URLs informed it.
- **Observed details:** only facts directly supported by inspected frames/audio/text.
- **Production defaults:** any chosen palette, fonts, timings, or layout values not directly observed.
- **Unverified items:** missing video access, uncertain ranking, unknown metrics, or unmeasured styles.
- **Verification:** renders reviewed, tests/checks run, and any known defects.

Do not state “matches all six channels” or “based on the top trending Reel of each account” unless the evidence audit truly supports those claims.
