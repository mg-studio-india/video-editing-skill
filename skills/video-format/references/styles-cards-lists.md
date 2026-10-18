# Cards, Lists & Information Structures (catalog #111-#144)

Owned by `video-format`. Part of the 225-style catalog: the full index, the entry schema and the owning file of every
style are in `video-plan-storyboard/references/style-catalog.md`. Entries are verbatim from the original master
(Section 5); cite a style by its number and name in `plan.md` / `storyboard.plan.json`.

_Especially useful for educational content, business explainers, and social video series._

### 111. Card-List
* **Visual & Spatial Composition**: Structured modular UI cards (dark slate `#252525`, radius 14px, thin border `#4A4845`) stacked vertically or appearing sequentially below the speaker's face (from ~52% canvas height down).
* **Narrative Intent & Best Fits**: Numbered key takeaways ("3 tools you need"), service deliverables, summary recaps in hooks and Reels.
* **Anti-Patterns & Guardrails**: Stacking more than 4 cards on screen at once (leads to claustrophobia and covers face). Keep card text under 18 characters.
* **Motion Physics & Temporal Dynamics**: Each card slides up and settles (`y: +24px -> 0`, `duration: 0.22s`, `ease: power3.out`) exactly as its corresponding word is spoken.
* **Engine & Asset Requirements**: `video-format` card component; numbered badge icons; subtle mechanical latch sound on each card entry.

### 112. Top-N Ranking
* **Visual & Spatial Composition**: Dramatic hierarchical list counting down from #N to #1 (or up from #1 to #N). Features prominent metallic or colored ordinal number badges (`#5`, `#4`, etc.) and ranking leaderboards.
* **Narrative Intent & Best Fits**: Viral curiosity hooks ("Top 5 AI tools that will replace designers"), countdown lists, comparative benchmarking.
* **Anti-Patterns & Guardrails**: Rushing through lower ranks too fast without context, or spending 2 minutes on #5 and 10 seconds on #1.
* **Motion Physics & Temporal Dynamics**: Number badge slams down with heavy impact, followed by card expansion; previous ranks shrink or stack upward.
* **Engine & Asset Requirements**: High-visibility number badge component; ascending riser pitch or heavy bass thud for each rank reveal.

### 113. Checklist
* **Visual & Spatial Composition**: Vertical task list where round or square checkbox markers beside each item dynamically populate with a drawn green checkmark (`✔`) or red strike upon completion.
* **Narrative Intent & Best Fits**: SOP tutorials, daily routine breakdowns, audit criteria, process completion milestones.
* **Anti-Patterns & Guardrails**: Pre-filling all checkmarks before the speaker mentions them. Checkmarks must activate in strict lockstep with spoken affirmation.
* **Motion Physics & Temporal Dynamics**: SVG stroke-dashoffset checkmark draws across path (`duration: 0.18s`), accompanied by subtle green card glow pulse.
* **Engine & Asset Requirements**: SVG path draw component; tactile "ding" or pen scribble checkmark audio cue (`check-mark-done.wav`).

### 114. Step-by-Step Tutorial
* **Visual & Spatial Composition**: Numbered procedural stages ("Step 1: Ingest", "Step 2: Conform", "Step 3: Render") anchored by a continuous progress stepper bar spanning the top or side of canvas.
* **Narrative Intent & Best Fits**: How-to educational videos, software setup guides, complex multi-stage technical workflows.
* **Anti-Patterns & Guardrails**: Jumping steps or introducing sub-steps without updating the visible step indicator counter.
* **Motion Physics & Temporal Dynamics**: Active step card expands and illuminates; completed steps collapse to compact badge pills with dimmed opacity (40%).
* **Engine & Asset Requirements**: Multi-step state machine component; step progression tracker; clean transition whoosh between steps.

### 115. Myth-Versus-Fact
* **Visual & Spatial Composition**: Split layout or sequential flip-card format. Stage 1 presents the common misconception with a red "MYTH" badge; Stage 2 slashes through the myth and reveals the verified "FACT" in emerald green.
* **Narrative Intent & Best Fits**: Educational debunking, contrarian business advice, nutrition/fitness corrections, challenging industry orthodoxy.
* **Anti-Patterns & Guardrails**: Making the myth look visually identical to the fact, confusing viewers who skim without sound. Visual polarities must be extreme.
* **Motion Physics & Temporal Dynamics**: Heavy red diagonal strike-line or "BUSTED" stamp slams across the myth (`duration: 0.15s`), followed by card 3D flip to fact.
* **Engine & Asset Requirements**: Dual-state flip card; rubber stamp slam sound effect (`stamp-slam.wav`); triumphant fact chime.

### 116. Pros-and-Cons Comparison
* **Visual & Spatial Composition**: Two distinct columns or opposing cards: Emerald Green theme for "Pros / Advantages" (plus icons), Coral Red theme for "Cons / Limitations" (minus icons).
* **Narrative Intent & Best Fits**: Unbiased product reviews, software buying guides, career decision analyses, investment risk assessments.
* **Anti-Patterns & Guardrails**: Unbalanced visual weight (e.g., 5 pros vs 1 con filling same card height). Keep typography and spacing symmetric.
* **Motion Physics & Temporal Dynamics**: Pros cascade in on left (`stagger: 0.1s`), pause, then cons cascade on right, giving equal perceptual consideration.
* **Engine & Asset Requirements**: Dual-column responsive grid container; custom plus/minus vector glyphs; soft balance scale audio cue.

### 117. Before-and-After Reveal
* **Visual & Spatial Composition**: Interactive visual slider line splitting the canvas, dragging across to reveal the dramatic transformation between the untreated "Before" and fully optimized "After".
* **Narrative Intent & Best Fits**: Video color grading showcases, fitness body transformations, architectural renovations, audio remastering demos.
* **Anti-Patterns & Guardrails**: "Before" state deliberately degraded or darkened with dishonest lighting to exaggerate the "After". Maintain fair lighting baselines.
* **Motion Physics & Temporal Dynamics**: Central slider bar wipes smoothly from left to right (`duration: 1.2s`, `ease: power2.inOut`), holding at 50% split.
* **Engine & Asset Requirements**: Dual-canvas wipe mask; slider handle graphic with interactive arrows; smooth linear servo motor hum SFX.

### 118. A-Versus-B Comparison
* **Visual & Spatial Composition**: Head-to-head clash layout with "VS" lightning badge centered between two distinct competitor products, strategies, or creator styles.
* **Narrative Intent & Best Fits**: Product shootouts (e.g., "iPhone 16 Pro vs Samsung S25 Ultra", "React vs Svelte"), strategic debates.
* **Anti-Patterns & Guardrails**: Cluttered multi-attribute tables shown all at once. Isolate one battle dimension at a time (Speed, Battery, Cost).
* **Motion Physics & Temporal Dynamics**: The two contenders smash into center frame from opposite edges (`x: -100% -> -10%`, `x: +100% -> +10%`), meeting at the "VS" spark.
* **Engine & Asset Requirements**: Collision impact shader; sparks/dust particle burst; metallic impact clang audio.

### 119. Do-This-Not-That Format
* **Visual & Spatial Composition**: Dual-pane comparison explicitly categorizing behavioral actions: Top/Left highlighted with red "DON'T" (incorrect technique), Bottom/Right highlighted with green "DO THIS" (optimal technique).
* **Narrative Intent & Best Fits**: Fitness exercise form guides, coding best practices, social etiquette tips, design critique reels.
* **Anti-Patterns & Guardrails**: Showing only the mistake without demonstrating the exact physiological or programmatic correction clearly.
* **Motion Physics & Temporal Dynamics**: "Don't" video plays first with red warning buzzer, freezes on the error, then camera pans/cuts to "Do This" with green checkmark.
* **Engine & Asset Requirements**: Red/Green banner badges; error buzzer SFX followed by pleasant positive confirmation chime.

### 120. Mistakes-and-Fixes
* **Visual & Spatial Composition**: Narrative problem-solution card pair. Top half highlights the painful error with a warning triangle; bottom card expands with the concrete code/action fix.
* **Narrative Intent & Best Fits**: Debugging tutorials, rookie business mistakes, financial blunder retrospectives.
* **Anti-Patterns & Guardrails**: Spending 90% of video on the mistake and rushing the fix in 2 seconds. The fix must be clearly actionable and documented.
* **Motion Physics & Temporal Dynamics**: Error card shakes slightly (`shakeX: ±8px`, `duration: 0.2s`), then resolves as solution card slides smoothly into place.
* **Engine & Asset Requirements**: Warning icon vector; solution code snippet container; tension swell resolving to relief chord.

### 121. Tips-and-Tricks List
* **Visual & Spatial Composition**: Rapid-fire micro-cards anchored by lightbulb or lightning badges, delivering bite-sized, high-utility hacks in rapid succession.
* **Narrative Intent & Best Fits**: Productivity hacks, hidden software shortcuts, insider trade secrets, viral engagement reels.
* **Anti-Patterns & Guardrails**: Clickbait "tricks" that are basic, common-sense knowledge. Every tip must offer genuine novel utility.
* **Motion Physics & Temporal Dynamics**: High-speed entrance (`scale: 0.8 -> 1.0`, `duration: 0.18s`, `ease: back.out(1.4)`), holding for 2.5s, rapid flick exit.
* **Engine & Asset Requirements**: Lightbulb spark animation; crisp pop sound for each tip reveal.

### 122. FAQ Sequence
* **Visual & Spatial Composition**: Accordion-style UI card structure: the frequently asked question appears in bold header text, followed by the accordion smoothly expanding downward to reveal the clear answer.
* **Narrative Intent & Best Fits**: Customer objection handling, product launch Q&As, onboarding FAQs, clearing up community misconceptions.
* **Anti-Patterns & Guardrails**: Rambling answers. Force answers into crisp 1-2 sentence cards or bullet summaries.
* **Motion Physics & Temporal Dynamics**: Accordion height tween (`height: 0 -> auto`, `duration: 0.3s`, `ease: power3.out`); chevron arrow rotates 180 degrees.
* **Engine & Asset Requirements**: Smooth CSS height-interpolation container; UI toggle click sound.

### 123. Question-and-Answer Cards
* **Visual & Spatial Composition**: Clean dialogue-card layout where a prominent question card from a viewer/customer is positioned at top, while the creator delivers the spoken breakdown below.
* **Narrative Intent & Best Fits**: Addressing community comments, client strategy consultations, AMA (Ask Me Anything) reels.
* **Anti-Patterns & Guardrails**: Obscuring the speaker's eyes with the question card. Position question card in top 15% header band or safe margin.
* **Motion Physics & Temporal Dynamics**: Card glides in from top edge (`y: -100% -> 0`), holds during introduction, and minimizes into a compact chip.
* **Engine & Asset Requirements**: Social avatar badge, question mark badge, gentle floating card shadow.

### 124. Decision-Tree Explainer
* **Visual & Spatial Composition**: Branching logic diagram ("If A -> Go to B; If not -> Go to C") with animated routing lines guiding the viewer through complex choices.
* **Narrative Intent & Best Fits**: Diagnostic troubleshooting, choosing which software framework/tool to use, medical triage logic, financial investment branching.
* **Anti-Patterns & Guardrails**: Sprawling decision trees with 20 tiny unreadable nodes. Zoom in dynamically to follow the single active branch path.
* **Motion Physics & Temporal Dynamics**: Glowing pulse travels down connecting lines, illuminating choice nodes sequentially as they are evaluated.
* **Engine & Asset Requirements**: SVG path network engine; dynamic node highlight states; electrical pulse SFX.

### 125. Flowchart Animation
* **Visual & Spatial Composition**: Kinetic flowchart featuring standard geometric symbols (ovals for start/end, rectangles for processes, diamonds for decisions) linked by directional arrows.
* **Narrative Intent & Best Fits**: Business operations mapping, software algorithmic logic, supply chain walkthroughs.
* **Anti-Patterns & Guardrails**: Static dense diagrams pasted from Lucidchart. Every node must animate into existence dynamically as the speaker narrates.
* **Motion Physics & Temporal Dynamics**: Sequential node pop-ins (`scale: 0 -> 1.0`, `duration: 0.2s`); directional flow dashes moving continuously along arrows.
* **Engine & Asset Requirements**: Vector flowchart node library; directional animated SVG stroke paths; soft chime on node arrival.

### 126. Process Breakdown
* **Visual & Spatial Composition**: Linear chronological pipeline diagram (3 to 5 discrete stages) spanning horizontally or vertically, highlighting the active stage while dimming completed ones.
* **Narrative Intent & Best Fits**: Manufacturing processes, client onboarding lifecycles, creative project milestones.
* **Anti-Patterns & Guardrails**: Showing stages without duration or output expectations. Clarify what each stage produces.
* **Motion Physics & Temporal Dynamics**: Active stage pulses with subtle ambient glow; camera tracks laterally to follow pipeline progression.
* **Engine & Asset Requirements**: Pipeline stage container; glow shader; smooth stage-transition sound design.

### 127. Roadmap / Milestone Progression
* **Visual & Spatial Composition**: Strategic timeline showing quarterly milestones (Q1, Q2, Q3, Q4) with progress bars, status badges ("Shipped", "In Progress", "Planned"), and feature cards.
* **Narrative Intent & Best Fits**: Startup investor updates, open-source project roadmaps, corporate vision presentations.
* **Anti-Patterns & Guardrails**: Over-promising with dozens of tiny unreadable feature tags. Focus on top 2 critical deliverables per milestone.
* **Motion Physics & Temporal Dynamics**: Progress bar fills smoothly across milestones (`width: 0 -> 75%`, `duration: 1.0s`, `ease: power2.out`).
* **Engine & Asset Requirements**: Horizontal roadmap container; milestone pin graphics; ascending chime progression.

### 128. Timeline of Events
* **Visual & Spatial Composition**: Chronological historical ruler with year markers (`1995`, `2004`, `2026`) and vertical connector lines tying dates to archival photographs or headline cutaways.
* **Narrative Intent & Best Fits**: Company founding histories, retrospective timelines of market crashes, geopolitical crises.
* **Anti-Patterns & Guardrails**: Non-linear jumps without visual warning. Maintain consistent time-distance scale along axis.
* **Motion Physics & Temporal Dynamics**: High-speed camera sweep across years with numbers blurring by, braking smoothly at target milestone date.
* **Engine & Asset Requirements**: Infinite ruler scroll component; tick mark audio clatter (`clock-wheel.wav`).

### 129. Ranking Leaderboard
* **Visual & Spatial Composition**: Dynamic scoreboard table where rows animate and physically swap positions upward or downward based on score changes, metrics, or revenue.
* **Narrative Intent & Best Fits**: Competition recaps, sales team leaderboards, stock performance rankings, benchmarking tests.
* **Anti-Patterns & Guardrails**: Rows jumping instantly without smooth positional tweening, confusing the eye as to who moved where.
* **Motion Physics & Temporal Dynamics**: FLIP (First, Last, Invert, Play) smooth vertical position swapping (`duration: 0.4s`, `ease: power3.inOut`).
* **Engine & Asset Requirements**: Dynamic list reordering engine; green upward arrow for risers, red downward for fallers; arcade score SFX.

### 130. Stat-of-the-Day
* **Visual & Spatial Composition**: Minimalist, high-impact hero card featuring one colossal statistic ("87%", "4.2x", "$1.4B") with a concise 1-line explanatory subtitle below.
* **Narrative Intent & Best Fits**: Opening video hooks, memorable anchor facts, social media thought-leadership carousels.
* **Anti-Patterns & Guardrails**: Diluting impact by adding 3 other supporting statistics on the same card. Keep it singular and undeniable.
* **Motion Physics & Temporal Dynamics**: Stat digit counts up or slams down (`duration: 0.25s`), followed by subtle breathing glow.
* **Engine & Asset Requirements**: High-impact numeral display font; bold accent color (`#FFD400` or `#00E0FF`); sub-bass impact thud.

### 131. Data Point / Chart Reveal
* **Visual & Spatial Composition**: Focus zooms in on an expansive data chart, darkening 90% of the graphic while a circular spotlight or magnifying callout isolates the single critical inflection point.
* **Narrative Intent & Best Fits**: Revealing market turning points, pinpointing anomalies, scientific data proofs, financial earnings calls.
* **Anti-Patterns & Guardrails**: Pointing at a chart without drawing a clear marker or circle around the exact spoken data point.
* **Motion Physics & Temporal Dynamics**: Vignette mask dims surrounding canvas (`opacity: 0 -> 0.75`), while spotlight circle pulses around the data node.
* **Engine & Asset Requirements**: SVG chart masking shader; callout pointer line with text pill; gentle focus chime.

### 132. Interactive-Style Quiz
* **Visual & Spatial Composition**: Broadcast game-show layout: a trivia question appears at top, with 4 selectable multiple-choice cards (A, B, C, D) below, paired with a ticking countdown timer bar.
* **Narrative Intent & Best Fits**: Educational engagement, viewer retention boosting, social media trivia reels, audience knowledge testing.
* **Anti-Patterns & Guardrails**: Revealing the answer instantly before the viewer has 2 seconds to process the choices.
* **Motion Physics & Temporal Dynamics**: Countdown bar depletes across 3.0 seconds; winning card flashes bright green with checkmark while incorrect cards dim to gray.
* **Engine & Asset Requirements**: Quiz card state engine; tension clock ticking SFX (`quiz-tick-loop.wav`); correct answer ding or wrong buzzer.

### 133. Guess-the-Answer Reveal
* **Visual & Spatial Composition**: Mystery card with blurred text or a giant question mark badge (`?`). Narration prompts the viewer to guess, followed by the blur clearing to reveal the answer.
* **Narrative Intent & Best Fits**: Mystery hooks, pricing guessing games, blind taste tests, history trivia.
* **Anti-Patterns & Guardrails**: Leaving the question mark unresolved. Deliver an immediate, gratifying visual payoff.
* **Motion Physics & Temporal Dynamics**: Question mark spins and pops out of existence (`scale: 1.0 -> 0`, `duration: 0.2s`), followed by rapid un-blur of text (`blur: 16px -> 0`).
* **Engine & Asset Requirements**: CSS Gaussian blur filter animation; tension riser sound resolving to brass reveal fanfare.

### 134. Flashcard Sequence
* **Visual & Spatial Composition**: Rapid-fire double-sided flashcard: Front side displays foreign word, technical term, or formula; card rapidly flips on Y-axis to reveal definition/translation on back.
* **Narrative Intent & Best Fits**: Language learning reels, medical terminology study guides, rapid vocabulary expansion.
* **Anti-Patterns & Guardrails**: Slow sluggish 3D card flips that drag pacing down. Card flip must be snappy and crisp (<0.25s).
* **Motion Physics & Temporal Dynamics**: 3D card flip (`transform: rotateY(180deg)`, `duration: 0.22s`, `ease: power2.inOut`).
* **Engine & Asset Requirements**: CSS 3D preserve-3d card container; realistic card flick / snap sound effect.

### 135. Quote-by-Quote Presentation
* **Visual & Spatial Composition**: A curated sequence of prominent testimonials or historical quotes fading in and out sequentially against a dark, elegant textured backdrop.
* **Narrative Intent & Best Fits**: Pitch deck video intros, book launch trailers, customer advocacy reels, philosophical video essays.
* **Anti-Patterns & Guardrails**: Displaying quote cards for too short a time to read. Rule of thumb: display time = (word count / 3) + 1.0 second.
* **Motion Physics & Temporal Dynamics**: Smooth crossfade transitions with slow subtle scale drift (`scale: 0.98 -> 1.02` over 4s).
* **Engine & Asset Requirements**: Elegant serif typography pairing; subtle paper or dust particle overlay; warm ambient piano bed.

### 136. Case-Study Breakdown
* **Visual & Spatial Composition**: Structured executive dashboard card layout divided into 3 standardized quadrants: **Client Challenge** -> **Solution Deployed** -> **Quantified Results** (+340% ROI).
* **Narrative Intent & Best Fits**: B2B enterprise sales reels, marketing agency client showcases, consulting pitch videos.
* **Anti-Patterns & Guardrails**: Focusing entirely on the solution while skipping the pain of the challenge. Contrast is what sells.
* **Motion Physics & Temporal Dynamics**: Quadrants highlight sequentially in narrative order; the final "Results" metric explodes with green accent fire.
* **Engine & Asset Requirements**: Multi-pane dashboard component; metric counter animation; celebratory success chime.

### 137. Review Scorecard
* **Visual & Spatial Composition**: Product evaluation scorecard showing rated categories (Design, Battery, Performance, Value) with animated 1-to-5 star ratings or 1-to-10 slider scores, culminating in an overall score badge.
* **Narrative Intent & Best Fits**: Consumer tech reviews, restaurant food ratings, movie critiques, automobile reviews.
* **Anti-Patterns & Guardrails**: Showing static pre-filled score bars. Bars must fill up progressively to build suspense toward final score.
* **Motion Physics & Temporal Dynamics**: Star icons fill sequentially with gold gleam; final master score stamp drops with heavy impact.
* **Engine & Asset Requirements**: Rating star SVG component; score gauge slider; star pop audio cues and heavy gavel stamp.

### 138. Feature Matrix
* **Visual & Spatial Composition**: High-density grid comparison comparing 3-4 product tiers (Free, Pro, Enterprise) across specific feature rows with checkmarks, cross marks, and numerical limits.
* **Narrative Intent & Best Fits**: Software pricing page walkthroughs, subscription tier recommendations, hardware model breakdowns.
* **Anti-Patterns & Guardrails**: Matrix text so small it requires a magnifying glass on mobile screens. Zoom in and highlight the single row being discussed.
* **Motion Physics & Temporal Dynamics**: Spotlight bar pans down table to highlight the specific active feature row (`duration: 0.3s`).
* **Engine & Asset Requirements**: Responsive table component; row focus shader; subtle row selection click SFX.

### 139. Pros, Cons, Verdict
* **Visual & Spatial Composition**: Three-phase narrative summary sequence: Card 1 highlights top 3 Pros; Card 2 highlights top 2 Cons; Card 3 takes over full frame with the definitive "FINAL VERDICT: BUY / SKIP".
* **Narrative Intent & Best Fits**: Concluding minutes of comprehensive consumer reviews, definitive buying advice.
* **Anti-Patterns & Guardrails**: A weak, non-committal verdict ("It depends on what you like"). Audiences demand definitive recommendations.
* **Motion Physics & Temporal Dynamics**: Final verdict card slams into center screen with camera screen shake (`duration: 0.18s`).
* **Engine & Asset Requirements**: High-contrast verdict badge; bold color token (Buy = Neon Green, Pass = Crimson Red); heavy cinematic hit.

### 140. Comparison Table Animation
* **Visual & Spatial Composition**: An interactive spreadsheet or financial matrix where values, columns, and rows dynamically sort, reorder, filter, and calculate totals in real-time.
* **Narrative Intent & Best Fits**: Financial modeling, real estate deal breakdowns, cost-benefit calculations, salary comparisons.
* **Anti-Patterns & Guardrails**: Unanimated static Excel screenshots. The numbers must calculate dynamically to convey living financial models.
* **Motion Physics & Temporal Dynamics**: Highlight beam sweeps across row; summary total cell rolls numbers to final sum.
* **Engine & Asset Requirements**: Interactive HTML table engine; number calculation script; digital calculator beep audio.

### 141. Map-and-Marker Explainer
* **Visual & Spatial Composition**: Regional or country map with custom branded pin markers highlighting store locations, battle sites, real estate properties, or demographic clusters.
* **Narrative Intent & Best Fits**: Franchise expansion updates, real estate investing overviews, geopolitical event tracking.
* **Anti-Patterns & Guardrails**: Pin markers clustering so densely that individual locations become an unreadable blob. Implement cluster grouping badges.
* **Motion Physics & Temporal Dynamics**: Pins drop from top with physical gravity and elastic bounce (`duration: 0.4s`, `ease: bounce.out`).
* **Engine & Asset Requirements**: Vector map SVG engine; pin drop physics script; rubber pop or map thud sound effects.

### 142. Animated Diagram
* **Visual & Spatial Composition**: Technical engineering blueprint, anatomical biological illustration, or architectural cross-section with animated callout leader lines linking labels to parts.
* **Narrative Intent & Best Fits**: Deep technical explainers, medical surgery breakdowns, automotive engine mechanics, industrial design.
* **Anti-Patterns & Guardrails**: Crossed leader lines that confuse what label belongs to what part. Leader lines must follow clean orthogonal 45/90 degree paths.
* **Motion Physics & Temporal Dynamics**: Leader lines draw out from component anchor (`duration: 0.25s`), ending in a circular dot and expanding text pill.
* **Engine & Asset Requirements**: SVG animated leader line component; technical blueprint background grid; subtle laser draw sound effect.

### 143. Glossary / Term Breakdown
* **Visual & Spatial Composition**: Dictionary-style editorial card: Term in bold primary font, phonetic pronunciation guide (`/ˈsiːkwəl/`), grammatical part of speech (`noun`), and concise 12-word plain-English definition.
* **Narrative Intent & Best Fits**: Demystifying complex industry jargon, crypto/AI acronym explainers, educational language lessons.
* **Anti-Patterns & Guardrails**: Academic definitions filled with secondary jargon. Define terms in simple, vivid, concrete terms.
* **Motion Physics & Temporal Dynamics**: Card slides smoothly in from side edge, holds for pronunciation audio, and retracts cleanly.
* **Engine & Asset Requirements**: Clean dictionary layout typography; phonetic symbol font support; soft page turn audio cue.

### 144. One-Concept Explainer
* **Visual & Spatial Composition**: Dedicated full-frame thematic visual metaphor (e.g., an iceberg representing conscious vs unconscious mind, or water pipes representing electrical voltage/current).
* **Narrative Intent & Best Fits**: Mental model breakdowns, foundational conceptual teaching, simplifying complex abstract theories.
* **Anti-Patterns & Guardrails**: Mixing multiple competing metaphors in the same scene. Pick one strong visual metaphor and explore it thoroughly.
* **Motion Physics & Temporal Dynamics**: The visual metaphor builds layer by layer in synchronization with speaker's progressive explanation.
* **Engine & Asset Requirements**: Custom vector illustration metaphor asset; fluid motion graphic engine; calming ambient educational soundscape.
