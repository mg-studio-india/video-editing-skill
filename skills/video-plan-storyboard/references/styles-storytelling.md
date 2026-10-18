# Storytelling & Narrative Formats (catalog #145-#172)

Owned by `video-plan-storyboard`. Part of the 225-style catalog: the full index, the entry schema and the owning file of every
style are in `video-plan-storyboard/references/style-catalog.md`. Entries are verbatim from the original master
(Section 6); cite a style by its number and name in `plan.md` / `storyboard.plan.json`.

_These describe the structure of the story, regardless of whether the visuals use a talking head, B-roll, captions, or animation._

### 145. Mini-Documentary
* **Visual & Spatial Composition**: Highly cinematic multi-act narrative structure combining archival footage, expert talking-head interviews, atmospheric B-roll, custom motion graphics, and orchestral score.
* **Narrative Intent & Best Fits**: Deep investigative journalism, corporate rise-and-fall stories, scientific breakthroughs, cultural retrospectives (8-20 minutes).
* **Anti-Patterns & Guardrails**: Rushing through complex historical context without establishing emotional stakes. The narrative requires deliberate act breaks.
* **Motion Physics & Temporal Dynamics**: Dynamic cinematic pacing: thoughtful slow-burn exposition alternating with fast-paced montage crescendos.
* **Engine & Asset Requirements**: Multi-layer timeline structure; professional cinematic grade; multi-stems orchestral score; archival historical media.

### 146. Educational Explainer
* **Visual & Spatial Composition**: Concept-first pedagogical hierarchy: First principles definition -> Visual conceptual model -> Real-world case study -> Practical takeaway summary.
* **Narrative Intent & Best Fits**: Science, economics, engineering, and software masterclasses (Vox, Kurzgesagt, Veritasium style).
* **Anti-Patterns & Guardrails**: Talking at a high abstract level without grounding the theory in tangible, everyday physical examples.
* **Motion Physics & Temporal Dynamics**: Visual assets appear precisely as their spoken concept is vocalized; zero visual dead air or unillustrated speech.
* **Engine & Asset Requirements**: Vector motion graphic library; technical diagrams; clear voiceover stem; focused pedagogical sound design.

### 147. Teaser / Trailer
* **Visual & Spatial Composition**: High-intensity montage featuring rapid non-linear micro-scenes, unresolved dramatic questions, escalating orchestral risers, and bold title flashes.
* **Narrative Intent & Best Fits**: Building massive anticipation for an upcoming product launch, documentary premiere, course release, or long-form video.
* **Anti-Patterns & Guardrails**: Giving away the ultimate climax or resolution in the teaser. Withhold the answer to create an unbearable itch to watch.
* **Motion Physics & Temporal Dynamics**: Exponential cut acceleration (shots shorten from 2.0s -> 1.0s -> 0.5s -> 0.1s at climax), cutting to black on peak riser.
* **Engine & Asset Requirements**: Cinematic riser and sub-drop SFX; rapid flash frames; bold metallic 3D title logo.

### 148. Hook → Problem → Solution → Call to Action (HPSC)
* **Visual & Spatial Composition**: Standard high-converting direct-response advertising architecture: Act 1 (0-3s Hook) -> Act 2 (3-15s Agonizing Problem) -> Act 3 (15-45s Revolutionary Solution) -> Act 4 (45-60s Clear Frictionless CTA).
* **Narrative Intent & Best Fits**: E-commerce product commercials, SaaS lead generation ads, customer acquisition campaigns.
* **Anti-Patterns & Guardrails**: Burying the hook or introducing the product solution in the first 2 seconds before the problem pain is established.
* **Motion Physics & Temporal Dynamics**: Urgent opening pace, transitioning to clear, methodical demonstration pace during solution, ending on high-contrast static CTA card.
* **Engine & Asset Requirements**: Product mockup assets; problem pain-point stock clips; conversion CTA button component; upbeat promotional score.

### 149. Problem → Agitation → Solution (PAS)
* **Visual & Spatial Composition**: Dark, emotionally tense visual palette during Problem and Agitation phases, transitioning abruptly to bright, vibrant, clean visual palette when Solution is revealed.
* **Narrative Intent & Best Fits**: B2B enterprise software ads, health and wellness pain-relief products, high-ticket consulting offers.
* **Anti-Patterns & Guardrails**: Weak agitation. The agitation phase must vividly articulate the ongoing emotional, financial, and time cost of leaving the problem unsolved.
* **Motion Physics & Temporal Dynamics**: Dissonant, minor-key audio and jittery editing during agitation, resolving to harmonious major-key chord and smooth motion on solution.
* **Engine & Asset Requirements**: Dynamic color-grade shift (cold desaturated -> warm saturated); dissonant riser resolving to clean harmonic resolution.

### 150. Story Arc: Setup → Conflict → Resolution
* **Visual & Spatial Composition**: Classic 3-act dramatic structure: Act 1 establishes the baseline status quo; Act 2 introduces an inciting crisis and escalating struggle; Act 3 delivers hard-won triumph.
* **Narrative Intent & Best Fits**: Founder memoirs, athletic comeback stories, customer transformation journeys, long-form YouTube essays.
* **Anti-Patterns & Guardrails**: Flat conflict. Without genuine obstacle, stakes, and risk of failure, the final resolution feels unearned and hollow.
* **Motion Physics & Temporal Dynamics**: Classical narrative pacing: deliberate exposition, accelerating cuts during conflict climax, sustained breathing hold on resolution.
* **Engine & Asset Requirements**: Emotional orchestral/ambient soundtrack with distinct thematic cues for each of the three acts.

### 151. Mystery / Reveal
* **Visual & Spatial Composition**: Visuals withhold the central object or identity (silhouette lighting, cropped tight angles, obscured faces) while narration drops tantalizing clues, culminating in a dramatic full reveal.
* **Narrative Intent & Best Fits**: Secret project unveilings, magic/illusion breakdowns, true-crime investigations, celebrity guest appearances.
* **Anti-Patterns & Guardrails**: Teasing a mystery whose eventual payoff is disappointing or mundane. The reveal must match the build-up intensity.
* **Motion Physics & Temporal Dynamics**: Suspenseful drone note holding for extended duration, cutting abruptly to complete acoustic silence right before the explosive reveal.
* **Engine & Asset Requirements**: Shadow silhouette lighting; smoke/fog particle shader; dramatic spotlight reveal.

### 152. Failure → Lesson → Improvement
* **Visual & Spatial Composition**: Vulnerable, unvarnished visual aesthetic during the failure confession (candid camera, desaturated tones), shifting to structured educational cards for the lessons.
* **Narrative Intent & Best Fits**: Post-mortem business reviews, startup shutdown stories, personal growth reflections, coding disaster breakdowns.
* **Anti-Patterns & Guardrails**: Arrogant or defensive tone. True vulnerability and radical transparency are essential for audience connection and credibility.
* **Motion Physics & Temporal Dynamics**: Thoughtful, reflective pacing with pauses allowed to breathe; snappy card list animations for the structured improvement takeaways.
* **Engine & Asset Requirements**: Candid B-roll assets; financial chart downturn visualizations; somber piano bed shifting to inspiring progression.

### 153. Transformation / Journey
* **Visual & Spatial Composition**: Fast-paced chronological time progression tracking a visible physical, technical, or financial metamorphosis from day 1 to day 365.
* **Narrative Intent & Best Fits**: Weight-loss transformations, learning a skill in 30 days, building a house, bootstrapping a business from zero to profitability.
* **Anti-Patterns & Guardrails**: Showing only the start and the end while skipping the agonizing middle struggle. The journey *is* the story.
* **Motion Physics & Temporal Dynamics**: Consistent camera framing across hundreds of days (match-cut alignment), creating a seamless timelapse of human evolution.
* **Engine & Asset Requirements**: Timestamp calendar overlays; match-cut alignment guide; escalating motivational soundtrack.

### 154. Personal Origin Story
* **Visual & Spatial Composition**: Childhood photographs, humble early beginnings, home videos, early rejection letters, intercut with current professional accomplishments.
* **Narrative Intent & Best Fits**: Creator personal branding, author bio videos, establishing deep rapport and humble authority with an audience.
* **Anti-Patterns & Guardrails**: Boastful or self-aggrandizing framing. The focus must remain on the formative struggles and pivotal human choices.
* **Motion Physics & Temporal Dynamics**: Slow, affectionate Ken Burns zooms on vintage personal photographs; intimate acoustic guitar or piano bed.
* **Engine & Asset Requirements**: High-res scans of personal archives; photo album frame layout; warm analog color grade.

### 155. Founder Story
* **Visual & Spatial Composition**: Gritty garage/dorm-room early footage contrasted with modern bustling headquarters, patent sketches, whiteboard architecture sessions, and founder direct address.
* **Narrative Intent & Best Fits**: Company about pages, investor pitch decks, recruitment anthems, premium brand heritage films.
* **Anti-Patterns & Guardrails**: Corporate buzzword bingo. The story must focus on the singular obsession and stubborn thesis that birthed the product.
* **Motion Physics & Temporal Dynamics**: Forward-moving rhythmic drive; cuts synchronized to the momentum of company milestones.
* **Engine & Asset Requirements**: Startup archival screenshots; product prototype footage; inspiring cinematic corporate score.

### 156. Customer Success Story
* **Visual & Spatial Composition**: Documentary profile following a real customer at work in their own facility, discussing the bottleneck that used to threaten their livelihood before adopting the product.
* **Narrative Intent & Best Fits**: High-ticket B2B enterprise validation, testimonial advertising, closing enterprise procurement teams.
* **Anti-Patterns & Guardrails**: Scripted infomercial feel where the customer recites marketing taglines. Keep customer dialogue authentic and conversational.
* **Motion Physics & Temporal Dynamics**: Documentary handheld realism; clean animated metric badges verifying ROI statistics.
* **Engine & Asset Requirements**: On-location customer B-roll; verified metric callout graphics; professional lavalier audio master.

### 157. Experiment / Challenge
* **Visual & Spatial Composition**: High-stakes hypothesis-testing format: "I tried X for 30 days" or "Can an AI run my company for a week?". Includes daily video diaries, rule graphics, and live tracking metrics.
* **Narrative Intent & Best Fits**: Viral entertainment, empirical product testing, fitness/lifestyle challenges, software stress tests.
* **Anti-Patterns & Guardrails**: Abandoning the challenge midway without honest accountability. If the experiment fails, the failure itself is the content.
* **Motion Physics & Temporal Dynamics**: Day counter graphic flipping rapidly (`Day 1`, `Day 2`...); energetic vlog pacing with sudden crisis hurdles.
* **Engine & Asset Requirements**: Day counter calendar component; empirical tracking dashboard; dynamic sound design for rule violations.

### 158. Myth-Busting
* **Visual & Spatial Composition**: Experimental laboratory aesthetic: High-speed slow-motion cameras, physical stress tests, forensic data measurements, and industrial testing rigs disproving common beliefs.
* **Narrative Intent & Best Fits**: Scientific education, debunking viral internet life hacks, automotive safety demonstrations (MythBusters style).
* **Anti-Patterns & Guardrails**: Declaring a myth busted without rigorous experimental proof or control groups.
* **Motion Physics & Temporal Dynamics**: High-speed phantom slow-mo (1000fps) during the destructive physical test; bold "MYTH BUSTED" rubber stamp graphic.
* **Engine & Asset Requirements**: High-speed camera footage; scientific sensor readout HUD; explosive impact sound effects.

### 159. Contrarian Argument / Hot Take
* **Visual & Spatial Composition**: Unflinching, intense direct-to-camera eye contact. Minimalist background, high contrast lighting, zero distractions. Speaker challenges widely accepted dogma in opening second.
* **Narrative Intent & Best Fits**: Thought leadership disruption, viral LinkedIn/X video essays, sparking debate and passionate comment sections.
* **Anti-Patterns & Guardrails**: Being contrarian purely for clickbait without a defensible, airtight intellectual framework to back it up.
* **Motion Physics & Temporal Dynamics**: Hard jump cuts removing all conversational hesitations; punch-in zooms on operative thesis claims.
* **Engine & Asset Requirements**: `video-take-geometry` punch-in tracking; crisp vocal compression; minimal to zero music to force total focus on the spoken argument.

### 160. Debunking / Fact-Check
* **Visual & Spatial Composition**: Split screen showing the viral claim or misleading politician/influencer clip on one side, paired with verifiable source documents, public databases, and expert refutations on the other.
* **Narrative Intent & Best Fits**: Journalism, political commentary, consumer protection, health misinformation correction.
* **Anti-Patterns & Guardrails**: Partisan emotional shouting. The power of debunking comes from calm, clinical, unassailable documentary evidence.
* **Motion Physics & Temporal Dynamics**: Split-screen highlighter sweeps; false claim video freezes and turns red as fact document illuminates.
* **Engine & Asset Requirements**: Document zoom component; "CLAIM: FALSE" verification stamp; forensic keyboard and document rustle foley.

### 161. Lessons Learned
* **Visual & Spatial Composition**: Thoughtful post-event debrief. Speaker sits in calm study or workshop, presenting a structured numbered ledger of hard-won wisdom derived from an arduous venture.
* **Narrative Intent & Best Fits**: Annual retrospectives, post-exit founder advice, career retrospectives, project post-mortems.
* **Anti-Patterns & Guardrails**: Generic clichés ("Never give up"). Lessons must be counter-intuitive, highly specific, and battle-tested.
* **Motion Physics & Temporal Dynamics**: Deliberate, relaxed pacing; elegant animated lesson cards entering with smooth slide-fades.
* **Engine & Asset Requirements**: Glassmorphic lesson cards; warm studio lighting; reflective ambient music bed.

### 162. Case Study → Evidence → Conclusion
* **Visual & Spatial Composition**: Rigorous scientific/consulting structure: Quadrant 1 states the empirical premise; Quadrant 2 lays out the data tables and customer recordings; Quadrant 3 summarizes the strategic conclusion.
* **Narrative Intent & Best Fits**: Venture capital investment memos, scientific research dissemination, management consulting pitches.
* **Anti-Patterns & Guardrails**: Drawing sweeping conclusions that exceed the scope of the evidence presented.
* **Motion Physics & Temporal Dynamics**: Methodical, logical transitions; data tables highlight in synchronization with the spoken deduction.
* **Engine & Asset Requirements**: Data visualization components; executive summary card layout; clean corporate sound design.

### 163. Prediction → Evidence → Outcome
* **Visual & Spatial Composition**: Tri-part timeline narrative: Scene 1 shows past historical prediction; Scene 2 shows the unfolding trends and indicators; Scene 3 reveals the resulting future outcome.
* **Narrative Intent & Best Fits**: Economic forecasts, technological trend analysis, sports draft predictions, futurism essays.
* **Anti-Patterns & Guardrails**: Hiding past incorrect predictions. True credibility comes from scoring past prediction accuracy honestly.
* **Motion Physics & Temporal Dynamics**: Time-travel transitions linking historical footage, present data dashboards, and 3D conceptual futures.
* **Engine & Asset Requirements**: Historical timeline graphic; dynamic prediction score card; atmospheric sci-fi synth beds.

### 164. News Brief
* **Visual & Spatial Composition**: Modern broadcast studio format: Branded lower-third headline straps (`BREAKING NEWS`), upper corner live topic bug, side B-roll window, and rapid teleprompter delivery.
* **Narrative Intent & Best Fits**: Daily tech industry updates, market opening bells, crypto news alerts, entertainment digests (60-120 seconds).
* **Anti-Patterns & Guardrails**: Stale pacing or rambling introductions. The lead story must be stated in the first 3 seconds with zero pleasantries.
* **Motion Physics & Temporal Dynamics**: Urgent forward clip pacing; swift lower-third strap wipes and graphic ticker scrolling.
* **Engine & Asset Requirements**: News ticker graphics engine; lower-third headline straps; urgent orchestral news chime intro.

### 165. Trend Analysis
* **Visual & Spatial Composition**: Macro-perspective visual layout combining cultural social media screengrabs, Google search trend graphs, demographic maps, and expert commentary.
* **Narrative Intent & Best Fits**: Consumer behavior reports, fashion trend breakdowns, marketing industry forecasts, cultural anthropology essays.
* **Anti-Patterns & Guardrails**: Confusing a temporary viral fad with an enduring macro-trend. Contextualize the underlying structural driver.
* **Motion Physics & Temporal Dynamics**: Dynamic collage animation; multi-layered screenshot fanning; chart extrapolation animations.
* **Engine & Asset Requirements**: 3D screenshot fan component (`fan3d`); search trend chart animation; modern lo-fi hip hop beat.

### 166. Opinion / Commentary Essay
* **Visual & Spatial Composition**: Highly stylized video essay combining personal aesthetic flourishes, film clips, literary citations, and provocative cultural critique (Nerdwriter / Contrapoints style).
* **Narrative Intent & Best Fits**: Film criticism, philosophical cultural analysis, political theory, modern art breakdowns.
* **Anti-Patterns & Guardrails**: Monotonous voiceover delivery without emotional inflection. The essay must be an artistic performance in itself.
* **Motion Physics & Temporal Dynamics**: Thematic visual motifs recurring across scenes; graceful match cuts; poetic pacing pauses.
* **Engine & Asset Requirements**: High-end color grading; literary quote typography; bespoke cinematic musical curation.

### 167. Narrative Voiceover Story
* **Visual & Spatial Composition**: Fiction or narrative non-fiction storytelling where rich, evocative voiceover carries the entire emotional weight, supported by poetic cinematic imagery and foley.
* **Narrative Intent & Best Fits**: True-crime thrillers, bedtime stories, philosophical parables, inspirational brand anthems.
* **Anti-Patterns & Guardrails**: Music drowning out the voiceover or fighting the vocal frequencies. The voice must remain pristine and centered.
* **Motion Physics & Temporal Dynamics**: Visuals dissolve slowly; camera floats continuously through atmospheric environments.
* **Engine & Asset Requirements**: Master voiceover recording with close-mic intimacy; hyper-detailed environmental foley soundscapes.

### 168. Suspense / Countdown Reveal
* **Visual & Spatial Composition**: An ominous digital or mechanical countdown clock ticks toward zero in the corner or center of the screen, with each passing second ratcheting up visual tension.
* **Narrative Intent & Best Fits**: Product drop count-downs, live event openers, escape room challenges, bomb-defusal or deadline thrillers.
* **Anti-Patterns & Guardrails**: Fake artificial suspense where the clock hits zero and nothing happens. The payoff must be explosive.
* **Motion Physics & Temporal Dynamics**: Heartbeat pulse animation synchronized to clock ticks; lighting in scene subtly pulses red as zero approaches.
* **Engine & Asset Requirements**: Digital LED countdown timer component; ticking heartbeat audio loop; high-impact explosion/reveal riser.

### 169. Open-Loop Storytelling with a Delayed Payoff
* **Visual & Spatial Composition**: In the first 10 seconds, a dramatic, shocking, or bizarre event is shown without explanation. The video suddenly cuts away to the beginning ("How did I end up here?"), paying off the loop at the very end.
* **Narrative Intent & Best Fits**: High-retention social reels, narrative entertainment vlogs, dramatic educational mysteries.
* **Anti-Patterns & Guardrails**: Forgetting to pay off the loop at the end (enrages viewers). The resolution must directly connect to the opening frame.
* **Motion Physics & Temporal Dynamics**: Record-scratch freeze frame on the opening climax (`duration: 0.5s`), followed by rapid rewinding VHS tape animation.
* **Engine & Asset Requirements**: Rewind tape visual shader; record-scratch audio cue (`record-scratch-freeze.mp3`); chronological chapter tags.

### 170. Circular Storytelling (Looping Narrative)
* **Visual & Spatial Composition**: The final spoken sentence and visual camera move connect seamlessly with the very first spoken sentence and visual camera move of the video, creating an endless, infinite loop.
* **Narrative Intent & Best Fits**: TikTok/Reels algorithm optimization (viewers watch 1.5x to 2x without realizing the video restarted), artistic narrative loops.
* **Anti-Patterns & Guardrails**: Audible audio pops or visual stutter at the loop point. The seam must be mathematically imperceptible.
* **Motion Physics & Temporal Dynamics**: The outgoing shot matches the lighting, camera angle, and focal length of the opening shot exactly.
* **Engine & Asset Requirements**: Loop-point audio crossfade (20ms); frame-accurate script splicing; seamless video player integration.

### 171. Episodic Series
* **Visual & Spatial Composition**: Standardized opening signature bumper (2s), recurring series logo bug in corner, episodic chapter numbering (`Episode 4: The Heist`), and end-screen next-episode card.
* **Narrative Intent & Best Fits**: Multi-part documentary series, serial fiction, educational multi-week courses, brand web-series.
* **Anti-Patterns & Guardrails**: Making episodes too self-contained with zero cliffhangers, or making them so fragmented that standalone viewers are lost.
* **Motion Physics & Temporal Dynamics**: Consistent series pacing and recurring transition motifs that build brand familiarity.
* **Engine & Asset Requirements**: Episodic intro bumper asset; recurring series motion graphics template; next-episode clickable card.

### 172. Compilation / Highlights Reel
* **Visual & Spatial Composition**: High-speed anthology assembling the top 10-20 best moments, funniest fails, sickest goals, or biggest wins from dozens of hours of source footage into a concentrated dopamine hit.
* **Narrative Intent & Best Fits**: Year-in-review recaps, sports season highlights, streamer funniest clips, festival retrospective reels.
* **Anti-Patterns & Guardrails**: Including mediocre filler clips just to pad run-time. Cut ruthlessly—every single clip must be an A+ highlight.
* **Motion Physics & Temporal Dynamics**: Relentless high-speed beat cuts; energy escalates steadily toward the #1 grand finale clip.
* **Engine & Asset Requirements**: Multi-source footage conformer; high-energy electronic music bed; clip chapter identification tags.
