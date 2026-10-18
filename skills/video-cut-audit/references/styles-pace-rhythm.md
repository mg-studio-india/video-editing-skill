# Editing Pace & Rhythm Formats (catalog #173-#187)

Owned by `video-cut-audit`. Part of the 225-style catalog: the full index, the entry schema and the owning file of every
style are in `video-plan-storyboard/references/style-catalog.md`. Entries are verbatim from the original master
(Section 7); cite a style by its number and name in `plan.md` / `storyboard.plan.json`.

_These are editing approaches that can be combined with almost any style above._

### 173. Jump-Cut Editing
* **Visual & Spatial Composition**: Consecutive cuts within the same continuous camera shot where tiny slices of time (pauses, filler words "um", breaths) are surgically excised, causing the subject to "jump" slightly in frame.
* **Narrative Intent & Best Fits**: YouTube talking-head videos, vlog monologues, high-speed tutorials, eliminating dead air to force relentless narrative velocity.
* **Anti-Patterns & Guardrails**: Cutting mid-consonant, creating clipping clicks. Jump cuts must preserve complete phonetic word boundaries with 20ms acoustic crossfades.
* **Motion Physics & Temporal Dynamics**: Instant 1-frame hard cuts; micro-punches (105% scale) on alternating cuts to make the jump intentional and dynamic rather than accidental.
* **Engine & Asset Requirements**: `video-cut-audit` with acoustic zero-crossing splice detection; zero-frame latency rendering.

### 174. Rapid-Fire Cuts
* **Visual & Spatial Composition**: Ultra-fast montage where shot duration drops to 8-18 frames (0.3s to 0.75s per cut), assaulting the viewer with a whirlwind barrage of contextual visuals.
* **Narrative Intent & Best Fits**: Action trailers, sensory overload hooks, showing the sheer scale of options or chaos before presenting clarity.
* **Anti-Patterns & Guardrails**: Sustaining rapid-fire cuts for >5 seconds without an optical breather. Follow a rapid-fire sequence with a stable, held hero shot.
* **Motion Physics & Temporal Dynamics**: Consistent screen center-weighting so viewer eyes don't have to dart across the screen between cuts.
* **Engine & Asset Requirements**: High-density timeline conformer; audio riser building in sync with cut frequency.

### 175. Beat-Synced Editing
* **Visual & Spatial Composition**: Every single visual cut, camera reframe, text reveal, and motion graphic entrance lands with mathematical precision on the musical transients (drum kicks, snares, bass drops).
* **Narrative Intent & Best Fits**: Music videos, sports highlight reels, high-fashion promos, commercial sizzles.
* **Anti-Patterns & Guardrails**: Editing on every single sixteenth note (causes visual chaos). Choose specific musical rhythm layers (e.g., cuts on kicks, text pops on snares).
* **Motion Physics & Temporal Dynamics**: Frame-accurate alignment with detected musical transients; micro-camera scale punch (`scale: 1.04 -> 1.0`) on kick drum hits.
* **Engine & Asset Requirements**: Audio transient detection engine; musical tempo BPM grid snap; dynamic timeline sync script.

### 176. Slow-Cinematic Pacing
* **Visual & Spatial Composition**: Expansive, unhurried shots held for 4 to 12 seconds each. Gentle camera glides, locked tripods, natural environmental movement (wind, waves, smoke).
* **Narrative Intent & Best Fits**: Prestige documentaries, luxury commercials, emotional drama climaxes, reflective philosophical video essays.
* **Anti-Patterns & Guardrails**: Mistaking boring, static footage for "cinematic". Every long shot must contain rich internal movement, lighting shifts, or micro-action.
* **Motion Physics & Temporal Dynamics**: Silky smooth motorized slider or Steadicam motion (`ease: linear`); deliberate dissolves and crossfades (`duration: 0.8s`).
* **Engine & Asset Requirements**: 4K/8K pristine footage; wide focal length lenses; rich ambient room-tone soundscapes.

### 177. Montage Editing
* **Visual & Spatial Composition**: Classical Soviet-style or Hollywood training montage: compressing days, weeks, or years of physical preparation into a 60-second narrative progression.
* **Narrative Intent & Best Fits**: Training routines (Rocky style), software building sprints, home renovations, studying for exams.
* **Anti-Patterns & Guardrails**: Showing repetitive actions that look identical. Each shot in the montage must demonstrate measurable progression toward the goal.
* **Motion Physics & Temporal Dynamics**: Progressively accelerating cut tempo; seamless musical overlay binding disparate geographic locations together.
* **Engine & Asset Requirements**: Diverse multi-location B-roll; energetic montage score; dynamic progress tags.

### 178. Real-Time Continuous Scene
* **Visual & Spatial Composition**: An event presented in strict 1:1 real time without time compression, slow motion, or ellipses, preserving raw authentic tension.
* **Narrative Intent & Best Fits**: Crisis negotiations, live cooking tests, high-stakes physical challenges, intimate emotional dialogues.
* **Anti-Patterns & Guardrails**: Allowing dead air with zero narrative tension. If real-time action slows down, the dialogue or stakes must escalate to compensate.
* **Motion Physics & Temporal Dynamics**: Naturalistic handheld or steady tracking; continuous unbroken audio bed.
* **Engine & Asset Requirements**: Uninterrupted master camera roll; synchronized boom audio.

### 179. Speed-Ramp Montage
* **Visual & Spatial Composition**: Sequence of 5-10 shots where every shot enters at 300% speed, slows down to 24% slow motion at the peak aesthetic moment, and accelerates back to 300% out.
* **Narrative Intent & Best Fits**: Automotive commercials, extreme sports reels, high-fashion runway recaps, dance reels.
* **Anti-Patterns & Guardrails**: Inconsistent ramp curves between shots. Establish a signature speed-ramp rhythm and apply it uniformly across the sequence.
* **Motion Physics & Temporal Dynamics**: S-curve velocity interpolation; whoosh audio on fast ramps, pitch-warped slow-motion audio on holds.
* **Engine & Asset Requirements**: High-framerate (120fps/240fps) capture; optical flow motion blur; dynamic pitch-shift audio processor.

### 180. Flash-Cut Editing
* **Visual & Spatial Composition**: Subliminal, momentary 1-frame or 2-frame visual insertions (a shocking image, a terrifying face, a mathematical clue) flashed into the middle of an ordinary scene.
* **Narrative Intent & Best Fits**: Psychological thrillers, horror teasers, trauma flashbacks, high-impact creative reveals.
* **Anti-Patterns & Guardrails**: Over-flashing that causes epileptic discomfort or feels like an editing glitch. Keep flash-cuts rare and purposeful.
* **Motion Physics & Temporal Dynamics**: Single-frame duration (41ms at 24fps); accompanied by high-transient electrical zap or gunshot SFX.
* **Engine & Asset Requirements**: Single-frame video splice; transient audio spike; high-contrast black-and-white or inverted frame.

### 181. Freeze-Frame Annotation
* **Visual & Spatial Composition**: Video suddenly freezes on an action frame (turning into a still image), accompanied by animated pen scribbles, spotlight arrows, stat badges, and voiceover breakdown.
* **Narrative Intent & Best Fits**: Sports tactical analysis, comedic character introductions (Guy Ritchie style), safety audits, tactical gaming breakdowns.
* **Anti-Patterns & Guardrails**: Freezing on an awkward, blurry, or unflattering face frame. Select a sharp, expressive, perfectly composed frame to freeze.
* **Motion Physics & Temporal Dynamics**: Motion halts instantly (`playbackRate: 0.0`); background desaturates slightly while foreground annotations pop with spring overshoot.
* **Engine & Asset Requirements**: Single-frame hold buffer; animated SVG telestrator brushes; record-scratch or freeze-camera shutter SFX.

### 182. Replay / Instant Rewind
* **Visual & Spatial Composition**: A surprising or hilarious event occurs, followed by an immediate visual rewind effect (video reverses at 400% speed with VHS tracking static) to replay the moment in slow motion.
* **Narrative Intent & Best Fits**: Comedy reels, sports bloopers, magic trick reveals, forensic analysis of subtle background details.
* **Anti-Patterns & Guardrails**: Replaying a moment that was mundane or clear on first watch. Replay only moments that warrant deeper scrutiny.
* **Motion Physics & Temporal Dynamics**: Reverse playback at 4x speed (`duration: 0.4s`), followed by forward replay at 50% slow-mo with zoom-in.
* **Engine & Asset Requirements**: Reverse video buffer; VHS rewind scanline overlay; tape rewind squeal audio (`vhs-rewind.wav`).

### 183. Countdown Structure
* **Visual & Spatial Composition**: The entire editing architecture is governed by an explicit decreasing counter (e.g., "10, 9, 8... 1"), where each number represents a dedicated section with strict time limits.
* **Narrative Intent & Best Fits**: Highly structured listicles, countdown challenges, game show formats, urgency-driven product teardowns.
* **Anti-Patterns & Guardrails**: Breaking the countdown rhythm or skipping numbers without an explicit comedic reason.
* **Motion Physics & Temporal Dynamics**: Number changes occur on rigid periodic intervals; audio riser builds in frequency as the counter approaches zero.
* **Engine & Asset Requirements**: Graphic countdown HUD component; tick audio cues; climactic resolution sound design.

### 184. Seamless-Loop Video
* **Visual & Spatial Composition**: Video engineered so the final frame visually and acoustically matches the opening frame with zero seam, causing social platforms to loop playback infinitely.
* **Narrative Intent & Best Fits**: TikTok/Reels algorithm gaming, hypnotic satisfaction reels, perpetual motion art.
* **Anti-Patterns & Guardrails**: Audible clicks, jump cuts, or grammatical sentences that feel cut off at the loop seam. The sentence must flow grammatically into the start.
* **Motion Physics & Temporal Dynamics**: Final camera move matches the opening camera move in vector and velocity (e.g., pan right out -> pan right in).
* **Engine & Asset Requirements**: Sub-frame audio alignment; 20ms audio crossfade; frame match-cut verification.

### 185. Split-Screen Comparison Cuts
* **Visual & Spatial Composition**: Split screen where both sides cut simultaneously between complementary takes, showing synchronized angles of the same action.
* **Narrative Intent & Best Fits**: Multi-angle musical performances, dual-perspective dialogue scenes, showing before-and-after development simultaneously.
* **Anti-Patterns & Guardrails**: Desynchronized action timing where one pane finishes the move 1 second before the other. Keep actions synchronized.
* **Motion Physics & Temporal Dynamics**: Simultaneous hard cuts across all screen partitions on exact musical downbeats.
* **Engine & Asset Requirements**: Multi-cam synchronized timeline; dual video render hosts; shared audio mix.

### 186. Rhythmic Transition Sequence
* **Visual & Spatial Composition**: A choreographed series of 4-6 rapid transitions (whip-pan right, whip-pan down, zoom-through, wipe right) chained together in rhythmic succession to transport the viewer across scenes.
* **Narrative Intent & Best Fits**: High-energy travel montages, commercial transitions between lifestyles, fashion transformations.
* **Anti-Patterns & Guardrails**: Transitions that feel detached from the music. Every transition impulse must land on a musical drum hit.
* **Motion Physics & Temporal Dynamics**: Consistent momentum chaining: the momentum of transition 1 feeds into transition 2 without stopping.
* **Engine & Asset Requirements**: Chained transition manager; directional blur shaders; synchronized percussion sound design.

### 187. Long-Take Storytelling
* **Visual & Spatial Composition**: Extended unbroken sequence (60s to 3 minutes+) where the camera fluidly follows actors through dynamic choreography, lighting shifts, and spatial changes without cutting.
* **Narrative Intent & Best Fits**: Immersive corporate facility tours, high-drama narrative scenes, high-trust unedited demonstrations.
* **Anti-Patterns & Guardrails**: Camera drifting aimlessly into empty corners. The camera must actively participate as a character, anticipating actor actions.
* **Motion Physics & Temporal Dynamics**: Smooth Steadicam / gimbal floating; dynamic blocking shifts between wide environmental shots and intimate close-ups.
* **Engine & Asset Requirements**: Steadicam / Ronin rig; wireless follow-focus system; boom mic operator choreography.
