# Audio-Led Formats (catalog #188-#200)

Owned by `video-sound-design`. Part of the 225-style catalog: the full index, the entry schema and the owning file of every
style are in `video-plan-storyboard/references/style-catalog.md`. Entries are verbatim from the original master
(Section 8); cite a style by its number and name in `plan.md` / `storyboard.plan.json`.

_Where the acoustic track forms the primary creative and editorial spine._

### 188. Voiceover-Led Storytelling
* **Visual & Spatial Composition**: Rich, intimate voiceover recording mixed prominently front-and-center. Visuals serve as evocative visual wallpaper accompanying the spoken word.
* **Narrative Intent & Best Fits**: Historical video essays, true crime stories, philosophical parables, luxury brand narrative spots.
* **Anti-Patterns & Guardrails**: Low-quality microphone audio with room echo or background computer fan noise. Vocal recording must be dry, close, and treated.
* **Motion Physics & Temporal Dynamics**: Visual cuts follow natural vocal pauses, allowing poetic cadence to dictate edit timing.
* **Engine & Asset Requirements**: High-end vocal chain (FET compressor, EQ, de-esser); -14 LUFS vocal master; ambient atmospheric drone score.

### 189. Podcast Audiogram with Animated Waveform
* **Visual & Spatial Composition**: Static podcast cover art or guest photograph paired with a kinetic, pulsing audio waveform bar visualizer, speaker name tag, and animated captions.
* **Narrative Intent & Best Fits**: Repurposing audio-only podcast snippets for social feeds (X, LinkedIn, Instagram) without filming video.
* **Anti-Patterns & Guardrails**: Generic boring static wave bars that don't match the actual voice frequencies. Waveform must react to live audio spectrum.
* **Motion Physics & Temporal Dynamics**: Real-time FFT frequency bars bouncing dynamically with vocal amplitude (`60fps canvas render`).
* **Engine & Asset Requirements**: Web Audio API / FFT spectrum analyzer; dynamic SVG waveform component; high-legibility social caption box.

### 190. Voiceover with Synchronized Subtitles
* **Visual & Spatial Composition**: Minimalist dark background or slow ambient B-roll, with the visual focus dominated by high-precision karaoke or sentence captions lighting up in lockstep with the voice.
* **Narrative Intent & Best Fits**: Poetry readings, motivational quotes, language learning pronunciation guides, soundbite social reels.
* **Anti-Patterns & Guardrails**: Captions drifting out of sync with audio by >50ms. Requires phoneme-accurate alignment.
* **Motion Physics & Temporal Dynamics**: Word-highlight transitions trigger with instantaneous zero-latency optical response.
* **Engine & Asset Requirements**: Whisper word-level timestamps; clean typography tokens; subtle vocal reverb tail.

### 191. Music-Led Montage with Minimal Dialogue
* **Visual & Spatial Composition**: Music track volume at full commercial loudness (0dB reference, ducking disabled). Visual scenes edited with surgical rhythmic precision to melody, hooks, and drum patterns.
* **Narrative Intent & Best Fits**: Action sports hype reels, aesthetic travel films, festival after-movies, fitness lifestyle promos.
* **Anti-Patterns & Guardrails**: Choosing generic elevator royalty-free music. The track must have genuine artistic character, dynamic build-ups, and emotional drops.
* **Motion Physics & Temporal Dynamics**: Cuts accelerate during drum fills; visual slow-motion matches melodic bridge; explosive cuts on drops.
* **Engine & Asset Requirements**: High-energy mastered music track; transient hit markers; sub-bass impact audio reinforcement.

### 192. Sound-Effect-Led Reveal (SFX Punch)
* **Visual & Spatial Composition**: A visual element (card, logo, stat, character) appears on screen accompanied by an exaggerated, hyper-realistic, multi-layered sound effect that commands attention.
* **Narrative Intent & Best Fits**: Comedic punchlines, tech product reveals, cartoon slapstick, financial milestone celebrations.
* **Anti-Patterns & Guardrails**: Generic, repetitive stock whooshes on every single graphic. Curate bespoke, unexpected foley sounds (whip-crack, anvil drop, arcade bell).
* **Motion Physics & Temporal Dynamics**: Visual impact frame lands exactly on the transient acoustic peak of the SFX (zero frame offset).
* **Engine & Asset Requirements**: High-resolution foley library (96kHz/24bit); transient-aligned timeline markers; spatial stereo panning.

### 193. ASMR / Sensory Audio
* **Visual & Spatial Composition**: Macro visual framing paired with hyper-amplified, pristine acoustic sound: gentle whispering, fingernail tapping, crinkling foil, soap cutting.
* **Narrative Intent & Best Fits**: Sensory relaxation, consumer product tactile demos, stress-relief reels, culinary sizzle spots.
* **Anti-Patterns & Guardrails**: Any background noise floor, hiss, or accidental harsh peaks. Heavy multiband limiting and high-pass filtering required.
* **Motion Physics & Temporal Dynamics**: Hypnotic, slow, rhythmic physical movements matching the gentle acoustic cadence.
* **Engine & Asset Requirements**: Binaural 3D stereo microphone capture; ultra-low-noise preamps; macro close-up video feed.

### 194. Sound-Reactive Motion Graphics
* **Visual & Spatial Composition**: Abstract 2D/3D motion graphics where scale, position, color, turbulence, and particle emissions are driven programmatically by audio frequency bands (bass = scale, treble = particles).
* **Narrative Intent & Best Fits**: Electronic music visualizers, DJ set backdrops, high-tech brand anthems, crypto/AI intros.
* **Anti-Patterns & Guardrails**: Cluttered chaotic reactivity that looks like a broken visualizer. Map specific geometric properties to isolated frequency bands.
* **Motion Physics & Temporal Dynamics**: Instantaneous attack with smooth exponential decay curves (`decay: 0.15s`) preventing visual jitter.
* **Engine & Asset Requirements**: WebGL audio analyzer pipeline; frequency band isolator (low/mid/high); dynamic shader uniforms.

### 195. Dialogue-First Interview Edit
* **Visual & Spatial Composition**: Conversational audio edited seamlessly to remove all verbal stumbles and long pauses while preserving natural conversational flow, using J-cuts and L-cuts to show listener reactions.
* **Narrative Intent & Best Fits**: Thought leadership podcasts, investigative journalism, documentary character studies.
* **Anti-Patterns & Guardrails**: Mechanical cut pacing that sounds like robots talking without emotional breathing room.
* **Motion Physics & Temporal Dynamics**: J-cut: dialogue of incoming speaker begins 0.5s before the camera cuts to them, smoothing the visual transition.
* **Engine & Asset Requirements**: Multi-track dialogue leveler (speech loudness matching); room-tone fill loops to cover silence gaps; multi-cam switcher.

### 196. Narrated Slideshow
* **Visual & Spatial Composition**: Curated high-resolution still photographs or design slides transitioning smoothly while an authoritative narrator explains the historical or strategic significance of each image.
* **Narrative Intent & Best Fits**: Architectural project reviews, historical retrospectives, academic art history lectures.
* **Anti-Patterns & Guardrails**: Low-resolution images with harsh digital pixelation. Apply subtle, slow Ken Burns pan-and-scan to every still image.
* **Motion Physics & Temporal Dynamics**: Slow, elegant camera drift across image details (`scale: 1.0 -> 1.06` over 5s); gentle cross-dissolves.
* **Engine & Asset Requirements**: High-res still assets; pan-and-scan camera projection; warm acoustic storytelling score.

### 197. No-Dialogue Cinematic Short
* **Visual & Spatial Composition**: Pure visual storytelling relying exclusively on actor physical expression, cinematic lighting, environmental foley, and an expressive musical score.
* **Narrative Intent & Best Fits**: High-art film festivals, luxury perfume/fashion spots, emotional non-profit appeals.
* **Anti-Patterns & Guardrails**: Confusing, impenetrable plotlines. Visual actions and character motivations must be crystal clear without spoken guidance.
* **Motion Physics & Temporal Dynamics**: Cinematic 24fps motion; cuts dictated entirely by physical actor movements and musical dynamics.
* **Engine & Asset Requirements**: Cinema camera footage (ARRI/RED); pristine multi-layered foley bed; custom composed score.

### 198. Call-and-Response Dialogue
* **Visual & Spatial Composition**: Fast-paced dialogue editing between two speakers or vocal lines (e.g., Question -> Instant Answer), bouncing rhythmically back and forth like a tennis match.
* **Narrative Intent & Best Fits**: Comedic sketches, customer objection debunking, dual-host podcast banter, musical rap battles.
* **Anti-Patterns & Guardrails**: Linger time on a speaker who has already finished talking. Cut instantly to the responder on their first syllable.
* **Motion Physics & Temporal Dynamics**: Rapid alternating cuts with zero gap; subtle camera pan matching vocal direction.
* **Engine & Asset Requirements**: Dual-speaker diarization; automated dialog switching script; stereo voice panning (Speaker A left 15%, Speaker B right 15%).

### 199. Music Drop / Beat-Drop Reveal
* **Visual & Spatial Composition**: Music builds up with accelerating snare rolls and rising pitch risers while visuals grow darker or blurrier; at the beat drop, the screen explodes into vibrant full color and action.
* **Narrative Intent & Best Fits**: Product unveilings, festival hype videos, sports triumph moments, automotive reveals.
* **Anti-Patterns & Guardrails**: Dropping the beat without a corresponding visual climax. The visual reveal must be the most spectacular shot of the entire video.
* **Motion Physics & Temporal Dynamics**: 1 to 2 frames of total blackness or whiteout right on the drop, followed by explosive high-framerate action.
* **Engine & Asset Requirements**: Mastered EDM/rock music track with pronounced drop; camera screen shake shader; sub-bass impact audio hit.

### 200. Before-and-After Sound Comparison
* **Visual & Spatial Composition**: Visual display showing audio waveform and plugin racks: Section 1 plays raw, untreated audio (thin, noisy, reverberant); Section 2 toggles plugin to reveal fully mastered broadcast audio.
* **Narrative Intent & Best Fits**: Audio plugin marketing, microphone reviews, acoustics treatment showcases, podcast production tutorials.
* **Anti-Patterns & Guardrails**: Normalizing the raw audio so quietly that the comparison is rigged. Provide fair peak-volume matching so tonal differences are honest.
* **Motion Physics & Temporal Dynamics**: An animated bypass toggle switch flips on screen (`OFF -> ON`), accompanied by instantaneous acoustic transformation.
* **Engine & Asset Requirements**: Dual audio stems (raw and processed); interactive UI bypass switch graphic; visual spectrum analyzer overlay.
