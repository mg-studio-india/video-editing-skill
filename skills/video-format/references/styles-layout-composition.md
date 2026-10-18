# Layout & Composition Styles (catalog #1-#20)

Owned by `video-format`. Part of the 225-style catalog: the full index, the entry schema and the owning file of every
style are in `video-plan-storyboard/references/style-catalog.md`. Entries are verbatim from the original master
(Section 1); cite a style by its number and name in `plan.md` / `storyboard.plan.json`.

_How footage, text, speakers, and graphics are arranged on screen._

### 01. Split-Screen
* **Visual & Spatial Composition**: Two or more distinct video streams playing concurrently on a partitioned screen. In 16:9, divided vertically into dual 8:9 columns; in 9:16, stacked horizontally into dual 9:8 rows. Divided by a crisp 2-4px divider line (`#4A4845` or accent).
* **Narrative Intent & Best Fits**: Contrasting two perspectives, showing cause-and-effect simultaneously, displaying speaker and referenced screen in tandem without obscuring either.
* **Anti-Patterns & Guardrails**: Avoid when one pane remains static for >5 seconds or when text inside a pane drops below 24px legible scale. Captions must span across the divider or sit anchored at bottom, never duplicated inside panes.
* **Motion Physics & Temporal Dynamics**: Split divider animates in along the seam axis (`duration: 0.3s`, `ease: power2.out`). Panes enter via directional slide or simultaneous crossfade.
* **Engine & Asset Requirements**: `video-take-geometry` for face-tracked cropping; `video-format` for layout grid and divider rendering. Audio is locked to primary stream; secondary stream muted or -18dB ambient.

### 02. Side-by-Side Comparison
* **Visual & Spatial Composition**: Two symmetrical columns (50/50 width in 16:9, or side-by-side cards with pillarboxing in 9:16). Clear labels ("Option A" vs "Option B" or "Competitor" vs "Our Product") anchored at top header bands.
* **Narrative Intent & Best Fits**: Direct head-to-head benchmarking, software feature shootouts, price/quality comparisons. Provides immediate visual cognitive closure.
* **Anti-Patterns & Guardrails**: Avoid when differences are too subtle to spot visually without zoom-in callouts. Do not use asymmetric lighting that makes one side artificially unreadable unless intentional.
* **Motion Physics & Temporal Dynamics**: Both sides reveal synchronously or via quick ping-pong wipe (`0.25s`). Synchronized playback markers ensure key comparison events occur at identical timestamps.
* **Engine & Asset Requirements**: Dual video tracks synchronized on timeline; `video-format` badge components for category headers; stereo audio balanced to speaker commentary.

### 03. Stacked Split-Screen
* **Visual & Spatial Composition**: Two video frames stacked vertically (top 50% / bottom 50% or 44% top speaker / 56% bottom demonstration). Ideal native orientation for 9:16 vertical canvas.
* **Narrative Intent & Best Fits**: Reaction video to viral content, coding tutorial with presenter on top and terminal below, live physical unboxing with overhead camera below.
* **Anti-Patterns & Guardrails**: Avoid placing faces in the extreme top 15% (covered by platform UI) or bottom 25% (obscured by engagement buttons and captions).
* **Motion Physics & Temporal Dynamics**: Upper and lower viewports enter from top and bottom edges respectively, snapping at center divider with `back.out(1.2)` damping.
* **Engine & Asset Requirements**: `video-take-geometry` center-face framing on top track; bottom track conformed to 1080x960; central divider bar with optional glowing accent pulse.

### 04. Picture-in-Picture (PiP)
* **Visual & Spatial Composition**: Primary scene occupies 100% full-frame background. Secondary inset window (width: 28-36% of canvas, radius: 12-16px, border: 2px solid rgba(255,255,255,0.2), box-shadow: `0 8px 32px rgba(0,0,0,0.5)`) positioned in a corner.
* **Narrative Intent & Best Fits**: Presenter guiding the viewer through complex gameplay, technical demos, UI walkthroughs, or slide decks while retaining personal connection.
* **Anti-Patterns & Guardrails**: Never place the PiP window over critical UI elements, software menus, or primary focal points of the background video. Move corner dynamically if necessary.
* **Motion Physics & Temporal Dynamics**: PiP scales up from corner anchor point (`scale: 0 -> 1`, `duration: 0.35s`, `ease: back.out(1.4)`). Smooth repositioning tween (`duration: 0.4s`, `ease: power3.inOut`) when dodging background focal shifts.
* **Engine & Asset Requirements**: Inset frame mask, drop-shadow rendering, audio sidechain ducking to presenter voice.

### 05. Layered-Head (Subject Cutout)
* **Visual & Spatial Composition**: Speaker isolated via AI foreground rotoscoping/alpha-matting. Graphics, large typographic numbers, charts, or B-roll are sandwiched strictly *behind* the speaker's head/torso and *in front* of the background footage.
* **Narrative Intent & Best Fits**: High-production YouTube intros, hook sequences, striking proof numbers ("$100,000", "30 Days"). Creates intense cinematic depth.
* **Anti-Patterns & Guardrails**: Avoid if raw footage has low contrast edge boundaries, motion blur on hands that cross the face repeatedly, or frizzy hair artifacts from poor lighting.
* **Motion Physics & Temporal Dynamics**: Typography or graphics rise or scale up behind the subject (`y: +40px -> 0`, `opacity: 0 -> 1`, `duration: 0.28s`) while speaker remains seated/speaking naturally.
* **Engine & Asset Requirements**: `video-take-geometry` / `npx hyperframes remove-background` producing alpha silhouette; z-index layer stack: `[bg-media: 10] -> [graphics-behind: 20] -> [subject-cutout: 30] -> [captions-front: 40]`.

### 06. Facecam Bubble
* **Visual & Spatial Composition**: Circular (1:1 aspect ratio with `border-radius: 50%`) or rounded squircle speaker camera window floating over main footage. Diameter: 240px-320px in 1080p canvas.
* **Narrative Intent & Best Fits**: Casual software demos, Loom-style productivity walkthroughs, micro-commentary clips, educational coding courses.
* **Anti-Patterns & Guardrails**: Avoid small bubbles where speaker facial expressions are unreadable. Ensure speaker eye line points toward the screen action, not off-camera away from content.
* **Motion Physics & Temporal Dynamics**: Enters with spring overshoot (`scale: 0.2 -> 1.0`, `duration: 0.4s`, `ease: elastic.out(1, 0.75)`). Subtle breathing pulse on active speech.
* **Engine & Asset Requirements**: Radial clipping path, circular outline with brand gradient stroke, audio waveform ring reactive to speaker mic input.

### 07. Screen-Plus-Facecam
* **Visual & Spatial Composition**: Structured dual-layout optimizing desktop/browser recordings. Main screen scaled to 70-80% width with a dedicated sidebar or corner bracket housing the 16:9 presenter video.
* **Narrative Intent & Best Fits**: SaaS product walkthroughs, developer tutorials, financial model reviews, executive video memos.
* **Anti-Patterns & Guardrails**: Do not shrink screen recording so much that font sizes become unreadable. Zoom in on active UI zones while keeping facecam steady.
* **Motion Physics & Temporal Dynamics**: Dynamic viewport zoom on screen details (`100% -> 140%` push-in over `0.6s`) while facecam smoothly tucks into a minimized dock.
* **Engine & Asset Requirements**: Clean 4K screen capture asset; cursor smoothing filter; layout template with dark slate container backing (`#1A1D24`).

### 08. Green-Screen Commentary
* **Visual & Spatial Composition**: Full-body or waist-up presenter with chroma-keyed transparent background superimposed directly onto full-frame screenshots, news articles, tweets, or footage.
* **Narrative Intent & Best Fits**: TikTok/Reels style news commentary, trend analysis, gossip/pop-culture breakdowns, critique of landing pages.
* **Anti-Patterns & Guardrails**: Avoid green spill on clothing or hair. Presenter must actively gesture toward and interact with the background elements, not just stand statically in the center.
* **Motion Physics & Temporal Dynamics**: Presenter dynamically pans/slides left or right (`duration: 0.3s`) when background highlights change, maintaining visual balance.
* **Engine & Asset Requirements**: Clean chroma keying / HSV spill suppression; simulated lighting match between background luminance and presenter color temperature.

### 09. Duet / Reaction Layout
* **Visual & Spatial Composition**: Side-by-side or top-and-bottom split optimized for social duets. Creator occupies one pane expressing reactions (nodding, laughing, gasping); original video plays unaltered in adjacent pane.
* **Narrative Intent & Best Fits**: Viral reactions, peer reviews, comedy stitches, expert validation or debunking of common claims.
* **Anti-Patterns & Guardrails**: Avoid dead silence or expressionless staring from the reacting creator. If adding verbal commentary, duck the original audio cleanly.
* **Motion Physics & Temporal Dynamics**: Punch-ins on creator's face during peak comedic/dramatic beats (`scale: 115%`, `duration: 0.15s`).
* **Engine & Asset Requirements**: Time-aligned dual video tracks; audio balance prioritizing the active speaker; platform-compliant safe margins.

### 10. Picture-Frame
* **Visual & Spatial Composition**: Central footage displayed inside an ornate, vintage, or branded graphic frame border (e.g., gold gallery frame, retro TV bezel, sleek neo-brutalist border).
* **Narrative Intent & Best Fits**: Curated art presentations, historical anecdotes, nostalgia themes, premium brand teasers.
* **Anti-Patterns & Guardrails**: Avoid excessive frame width that constricts the inner video to under 75% of screen area. Keep frame textures subtle to prevent visual noise.
* **Motion Physics & Temporal Dynamics**: Frame remains static or participates in gentle 3D tilt while the inner video scales or plays. Inner footage reveals via frame-curtain wipe.
* **Engine & Asset Requirements**: High-resolution PNG/SVG frame asset with alpha viewport cutout; drop shadows inner and outer.

### 11. Multi-Panel Grid
* **Visual & Spatial Composition**: Synchronized matrix of 3, 4, 6, or 9 panels arranged in a balanced grid (e.g., 2x2, 3x3). Each panel shows a different angle, test subject, or data stream.
* **Narrative Intent & Best Fits**: Multiverse comparisons, multi-camera sports action, customer testimonial mosaics, synchronized musical performances.
* **Anti-Patterns & Guardrails**: High cognitive load. Never run rapid individual motion in all panels simultaneously without one highlighted "hero" panel.
* **Motion Physics & Temporal Dynamics**: Panels stagger into frame in sequence (`stagger: 0.08s`, `scale: 0.8 -> 1.0`, `ease: power2.out`). Active panel receives bright highlight border.
* **Engine & Asset Requirements**: Synchronized multi-track video composer; dynamic border highlight shader; audio downmixed to single master feed.

### 12. Dynamic Split-Screen
* **Visual & Spatial Composition**: Split-screen where the dividing boundary line dynamically moves, expands, rotates, or collapses based on narrative beats (e.g., left pane expands from 50% to 80% as subject explains detail).
* **Narrative Intent & Best Fits**: Conversational debates where speaking turns dictate screen territory; showing progress bar conversions; interactive reveals.
* **Anti-Patterns & Guardrails**: Jerky or unpredictable divider motion that causes motion sickness. Limit transitions to purposeful speaker shifts.
* **Motion Physics & Temporal Dynamics**: Divider position tweened using cubic Bezier (`duration: 0.5s`, `ease: cubic-bezier(0.25, 1, 0.5, 1)`). Viewports crop smoothly without stretching content.
* **Engine & Asset Requirements**: Real-time CSS flex/grid or canvas clipping path animation; responsive face-tracking anchor points.

### 13. Layered Collage
* **Visual & Spatial Composition**: Eclectic, textured composition featuring overlapping screenshots, torn paper cutouts, highlighter strips, stickers, arrows, and animated footage snippets on a textured background.
* **Narrative Intent & Best Fits**: Investigative deep-dives (Vox/Johnny Harris style), Gen-Z aesthetic explainers, complex case-study syntheses.
* **Anti-Patterns & Guardrails**: Visual anarchy without hierarchy. One element must clearly hold dominant scale (the primary focus) while supporting assets remain secondary.
* **Motion Physics & Temporal Dynamics**: Elements drop in with rotational jitter (`rotation: random(-6, 6)deg`, `scale: 0.9 -> 1.0`, `duration: 0.22s`, `stagger: 0.12s`).
* **Engine & Asset Requirements**: Asset library of paper rips, masking tape textures, drop shadows (`filter: drop-shadow(0 10px 20px rgba(0,0,0,0.35))`), SVG doodles.

### 14. Paper-Drawer
* **Visual & Spatial Composition**: A tactile, paper-textured compartment or folder tab that slides out smoothly from screen edge (left, right, or bottom) into the frame, revealing a note, definition, or formula.
* **Narrative Intent & Best Fits**: Academic citations, "By the way" technical definitions, side notes, author quotes without interrupting primary video flow.
* **Anti-Patterns & Guardrails**: Text on paper panel exceeding 12-15 words. Avoid leaving drawer open for >6 seconds after narration has moved on.
* **Motion Physics & Temporal Dynamics**: Slide-in (`x: -100% -> 0`, `duration: 0.32s`, `ease: power3.out`), subtle settle (`x: 0 -> -8px -> 0`), hold for speech duration, slide-out (`x: 0 -> -100%`, `duration: 0.24s`, `ease: power2.in`).
* **Engine & Asset Requirements**: High-res paper parchment texture (`#F4ECD8`), ink-black typography (`#1D1A16`), paper slide SFX (`whoosh-paper-friction.mp3`).

### 15. Scrapbook
* **Visual & Spatial Composition**: Analog scrapbook spread with photo prints taped down with semi-transparent scotch tape, handwritten cursive titles, push pins, and cardboard grain.
* **Narrative Intent & Best Fits**: Personal memoirs, travel retrospectives, company milestone celebrations, artistic creator stories.
* **Anti-Patterns & Guardrails**: Modern corporate UI elements clashing with analog textures. Maintain consistent physical lighting and shadow direction across all pinned items.
* **Motion Physics & Temporal Dynamics**: Stop-motion staggered entrance (step-based animation at 12fps) simulating physical hands pasting items down.
* **Engine & Asset Requirements**: Masking tape alphas, paper tear brushes, localized shadow shaders, analog acoustic sounds (tape rip, paper thud).

### 16. Polaroid Stack
* **Visual & Spatial Composition**: Classic white-bordered Polaroid instant photo frames stacked slightly offset on a desk or solid surface. Upper photo is viewed, then swept away to reveal the next.
* **Narrative Intent & Best Fits**: Photo retrospectives, rapid-fire portfolio showcasing, travel highlights, chronological team intros.
* **Anti-Patterns & Guardrails**: Stacks deeper than 4 items cause visual clutter. Avoid tiny photos where subjects are unrecognizable.
* **Motion Physics & Temporal Dynamics**: Top card flicks away with velocity and slight rotation (`x: +120%`, `rotation: 25deg`, `duration: 0.35s`, `ease: power2.inOut`). Lower card springs to focus.
* **Engine & Asset Requirements**: White Polaroid frame template with bottom label text, realistic card shuffle SFX (`foley-card-slide.wav`).

### 17. Floating Cards
* **Visual & Spatial Composition**: Modular rounded glassmorphic or dark-mode UI cards (`border-radius: 18px`, subtle gradient border) floating gracefully in 3D perspective space around the speaker or canvas center.
* **Narrative Intent & Best Fits**: Presenting software features, metrics, key bullet points, or product pricing tiers in high-tech corporate reels.
* **Anti-Patterns & Guardrails**: Cards covering the presenter's mouth or eyes. Cards lingering after spoken point finishes.
* **Motion Physics & Temporal Dynamics**: Smooth 3D tilt (`transform: perspective(1000px) rotateY(-8deg)`), gentle floating sinusoidal hover (`y: ±6px`, `period: 2.5s`).
* **Engine & Asset Requirements**: CSS 3D transforms, frosted glass backdrop filter (`blur(16px)`), luminous border gradients, subtle UI pop chime.

### 18. Over-the-Shoulder Screen
* **Visual & Spatial Composition**: Camera angle positioned behind/beside the presenter, showing their shoulder/profile in foreground while looking at a physical laptop, tablet, or virtual floating projection.
* **Narrative Intent & Best Fits**: Collaborative discussions, coding reviews, strategic teardowns, establishing realistic working environments.
* **Anti-Patterns & Guardrails**: Presenter's head obstructing more than 30% of the active screen area. Screen glare or reflection washing out display data.
* **Motion Physics & Temporal Dynamics**: Subtle handheld camera drift (`wiggle: 1.5%`) giving an authentic fly-on-the-wall observational feel.
* **Engine & Asset Requirements**: 4-point corner pin perspective projection of screen media onto physical monitor surface; ambient screen light casting onto presenter's shoulder.

### 19. Device Mockup
* **Visual & Spatial Composition**: High-fidelity 3D/vector render of an iPhone, MacBook Pro, iPad, or browser window centered on canvas with recorded UI cleanly composited inside screen bezels.
* **Narrative Intent & Best Fits**: Mobile app demonstrations, website launch promos, responsive design showcases, digital product marketing.
* **Anti-Patterns & Guardrails**: Low-resolution screen captures that look pixelated inside 4K device frames. Avoid static mockups; the content inside *must* scroll or interact.
* **Motion Physics & Temporal Dynamics**: Device floats in with smooth rotational tilt (`rotateX: 12deg`, `rotateY: -15deg -> 0deg`, `duration: 0.6s`, `ease: power3.out`). Scroll gestures inside device time-aligned to narration.
* **Engine & Asset Requirements**: Apple hardware vector models (clay/metallic variants), screen mask container, subtle glass reflection glare overlay.

### 20. Foreground-Background Parallax
* **Visual & Spatial Composition**: Multi-plane composition where foreground elements (foliage, cutout speaker, architectural pillars) move at a faster rate across camera than midground graphics and distant background.
* **Narrative Intent & Best Fits**: Immersive cinematic intros, storytelling documentaries, creating artificial depth from still photography (2.5D animation).
* **Anti-Patterns & Guardrails**: Exaggerated speed differentials that break physical optical laws or cause depth tearing artifacts.
* **Motion Physics & Temporal Dynamics**: Linear or smooth eased camera tracking across X/Z axes with speed ratios: FG = 1.0x, MG = 0.5x, BG = 0.15x.
* **Engine & Asset Requirements**: Photoshop layer separation of still assets (inpainted background plate); camera projection plane setup in 3D motion engine.
