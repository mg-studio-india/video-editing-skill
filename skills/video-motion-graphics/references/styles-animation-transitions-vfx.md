# Animation, Transitions & Visual Effects Styles (catalog #76-#110)

Owned by `video-motion-graphics`. Part of the 225-style catalog: the full index, the entry schema and the owning file of every
style are in `video-plan-storyboard/references/style-catalog.md`. Entries are verbatim from the original master
(Section 4); cite a style by its number and name in `plan.md` / `storyboard.plan.json`.

_The visual treatment and movement used to communicate the story._

### 76. Paper-Cutout Animation
* **Visual & Spatial Composition**: Tactile visual world composed of layered physical paper shapes, torn edges, cardboard textures, and cutout photographic elements casting soft drop shadows onto one another.
* **Narrative Intent & Best Fits**: Whimsical storytelling, children's educational content, satirical political sketches (South Park / Terry Gilliam style), indie creative explainers.
* **Anti-Patterns & Guardrails**: Smooth digital 60fps tweens that ruin the physical handcrafted illusion. Animate strictly at 12fps (on twos).
* **Motion Physics & Temporal Dynamics**: Stepped keyframe interpolation (`step-end`), physical pivot-joint rotations with slight rotational overshoot.
* **Engine & Asset Requirements**: Textured paper asset library; drop-shadow offset shader; paper rustling and folding sound design.

### 77. Whiteout
* **Visual & Spatial Composition**: Screen instantly blows out to pure 100% blinding solid white (`#FFFFFF`), holds momentarily, and reveals a completely new visual scene, location, or timeline as it decays.
* **Narrative Intent & Best Fits**: Paradigm shifts ("And then everything changed"), catastrophic failures, explosive revelations, transitioning between dark indoor scene and bright daylight exterior.
* **Anti-Patterns & Guardrails**: Using more than once in a short video; blinding the viewer needlessly between ordinary talking points; pairing with aggressive high-pitch whoosh.
* **Motion Physics & Temporal Dynamics**: Rapid flash to white (`duration: 0.18s-0.24s`), hold for 2-4 frames (0.08s), smooth logarithmic decay back to new scene (`duration: 0.35s`).
* **Engine & Asset Requirements**: Full-screen white overlay host; soft warm swell or momentary acoustic silence on the white peak.

### 78. Morph Transition
* **Visual & Spatial Composition**: One distinct vector shape, icon, or visual composition smoothly and continuously deforms and re-interpolates its vector paths into a completely different object (e.g., a coffee cup deforms into an hourglass).
* **Narrative Intent & Best Fits**: Explaining conceptual evolution, showing financial conversions (time is money), maintaining continuous visual flow without hard cuts.
* **Anti-Patterns & Guardrails**: Morphing objects with drastically mismatched path node counts, causing chaotic tangling of vertices. Clean path mapping required.
* **Motion Physics & Temporal Dynamics**: Fluid vector spline interpolation (`duration: 0.6s-0.9s`, `ease: cubic-bezier(0.65, 0, 0.35, 1)`).
* **Engine & Asset Requirements**: SVG path morphing engine (GSAP MorphSVGPlugin); organic liquid chime sound effects.

### 79. Mask-Reveal Animation
* **Visual & Spatial Composition**: Content is uncovered dynamically by an animated geometric mask (circle, diagonal wipe, sliding rectangle) or organic brush stroke traveling across the canvas.
* **Narrative Intent & Best Fits**: Revealing hidden features, before-and-after comparisons, peeling back surface layers to reveal internal mechanisms.
* **Anti-Patterns & Guardrails**: Sloppy mask edges that clip important typography. Mask edges should feature subtle feathering (2-6px blur).
* **Motion Physics & Temporal Dynamics**: Mask scales or sweeps across frame (`duration: 0.4s`, `ease: power3.out`), revealing underlying content.
* **Engine & Asset Requirements**: CSS `clip-path` / SVG `clipPath` definitions; soft whoosh reveal SFX.

### 80. Wipe and Slide Transitions
* **Visual & Spatial Composition**: Incoming scene sweeps across the frame from an edge (left, right, top, bottom), pushing the outgoing scene off-screen or covering it like a physical card.
* **Narrative Intent & Best Fits**: Fast-paced listicles, switching between distinct product features, energetic comedic shifts, retro sports recaps.
* **Anti-Patterns & Guardrails**: Generic default corporate PowerPoint slide transitions. Must use snappy velocity curves with physical motion blur.
* **Motion Physics & Temporal Dynamics**: Swift lateral translate (`x: -100% -> 0`, `duration: 0.28s`, `ease: power3.out`) with directional motion blur trail.
* **Engine & Asset Requirements**: Dual-host transition manager; directional blur shader; crisp mechanical slide audio cue.

### 81. Motion-Graphics Explainer
* **Visual & Spatial Composition**: Fully vector-animated world combining kinetic icons, typography, geometric layouts, and character vignettes to visualize abstract software or financial systems.
* **Narrative Intent & Best Fits**: B2B tech marketing, cryptographic security explainers, fintech workflow overviews, venture funding pitch videos.
* **Anti-Patterns & Guardrails**: Pointless geometric animation that adds no educational clarity. Every animated movement must illustrate a functional concept.
* **Motion Physics & Temporal Dynamics**: Interlocking mechanical choreography; elements assemble seamlessly with damped harmonic spring physics.
* **Engine & Asset Requirements**: HyperFrames / Lottie / GSAP composition runtime; curated corporate color palette; multi-layered micro-sound design.

### 82. Flat-Vector Animation
* **Visual & Spatial Composition**: Clean, modern 2D aesthetic characterized by bold flat colors, solid geometric silhouettes, zero gradients, and high contrast (Kurzgesagt / Google Material style).
* **Narrative Intent & Best Fits**: Scientific education, global demographics explainers, healthcare and biology tutorials, clean brand anthems.
* **Anti-Patterns & Guardrails**: Overly simplistic kindergarten shapes that feel juvenile for serious adult corporate topics. Maintain sophisticated design proportion.
* **Motion Physics & Temporal Dynamics**: Crisp geometric scale and rotation tweens (`ease: power2.inOut`); characters moving along smooth spline curves.
* **Engine & Asset Requirements**: Optimized SVG vector assets; flat color tokens; cheerful organic acoustic and synth sound beds.

### 83. Whiteboard Animation
* **Visual & Spatial Composition**: High-speed simulated hand holding a dry-erase marker sketching black-and-white cartoon doodles, icons, and diagrams onto an expansive white dry-erase board.
* **Narrative Intent & Best Fits**: Traditional corporate training, book summaries, educational psychology lectures, low-budget direct response marketing.
* **Anti-Patterns & Guardrails**: Fake static hand floating awkwardly without realistic wrist articulation. Animate stroke drawing with true path following.
* **Motion Physics & Temporal Dynamics**: Drawing path stroke-dash offset animated in sync with high-speed squeaky marker foley sound.
* **Engine & Asset Requirements**: Animated hand sprite; vector line path tracer; authentic dry-erase squeak and dry cloth erase foley.

### 84. Stop-Motion Animation
* **Visual & Spatial Composition**: Physical tangible objects (clay, Lego bricks, paper cutouts, puppets) photographed frame-by-frame, creating a charming, slightly jerky, handcrafted motion texture.
* **Narrative Intent & Best Fits**: Artisanal craft commercials, quirky holiday promos, music videos, creative DIY storytelling.
* **Anti-Patterns & Guardrails**: Smoothing the frame-rate with AI optical flow (destroys the soul of stop-motion). Render strictly at 12fps or 15fps.
* **Motion Physics & Temporal Dynamics**: Step-based linear motion (`step-start`), slight physical variations in lighting and surface fingerprint impressions between frames.
* **Engine & Asset Requirements**: Frame-by-frame image sequence pipeline; tactile acoustic sound effects (wood clicks, clay squish).

### 85. 2D Character Animation
* **Visual & Spatial Composition**: Illustrated character rigs (walk cycles, expressive facial lip-sync, gesture comedy) acting out scripted narrative scenarios in colorful illustrated scenes.
* **Narrative Intent & Best Fits**: Narrative moral fables, corporate customer persona journeys, humorous skits, brand mascot marketing.
* **Anti-Patterns & Guardrails**: Stiff "puppet" joint rotation where characters look like robotic wooden cutouts. Incorporate squash and stretch principles.
* **Motion Physics & Temporal Dynamics**: Classic 12 principles of animation: anticipation, squash and stretch, follow-through, secondary action.
* **Engine & Asset Requirements**: Rive / Spine / After Effects rigged vector characters; phonetic lip-sync mapping; character voiceover tracks.

### 86. 3D Product Animation
* **Visual & Spatial Composition**: Photorealistic CAD/3D render of physical product (smartphone, watch, sneaker, vehicle) rotating in an ethereal studio vacuum with studio light reflections sweeping across curves.
* **Narrative Intent & Best Fits**: Hardware product launches (Apple keynote style), industrial design showcases, luxury watch unveilings.
* **Anti-Patterns & Guardrails**: Unrealistic plastic shaders or low-poly jagged edges. Requires ray-traced global illumination and accurate physical materials.
* **Motion Physics & Temporal Dynamics**: Majestic slow-motion 3D camera orbits, exploding parts diagram separating components into 3D space (`duration: 1.5s`).
* **Engine & Asset Requirements**: Cinema 4D / Blender / Three.js 3D models; high-res PBR textures; cinematic bass swells and metallic gleam SFX.

### 87. Isometric Animation
* **Visual & Spatial Composition**: Orthographic 3D projection (fixed 30-degree isometric angle) displaying micro-worlds, architectural cross-sections, server rooms, or city grids with no perspective vanishing point.
* **Narrative Intent & Best Fits**: Cloud architecture explainers, logistics and supply chain demos, city planning visualizations, game development teasers.
* **Anti-Patterns & Guardrails**: Mixing true perspective assets with isometric grids (breaks spatial illusion). Keep projection strictly axonometric.
* **Motion Physics & Temporal Dynamics**: Isometric cubes and conveyor belts operating in synchronized perpetual motion loops.
* **Engine & Asset Requirements**: Isometric grid vector/3D engine; precise 30-degree angle transforms; clockwork ambient sound design.

### 88. Kinetic-Shape Animation
* **Visual & Spatial Composition**: Abstract geometric shapes (circles, squares, toruses, squiggles) pulsing, colliding, and rearranging to visual rhythms, setting mood without literal characters.
* **Narrative Intent & Best Fits**: Music visualizers, event opening titles, transitions between conceptual chapters, brand mood anthems.
* **Anti-Patterns & Guardrails**: Chaos without underlying geometric harmony. Align shapes to strict underlying Swiss graphic design grids.
* **Motion Physics & Temporal Dynamics**: Heavy elastic springs (`damping: 10`, `stiffness: 150`), rhythmic expansion and contraction to drum transients.
* **Engine & Asset Requirements**: WebGL / Canvas2D shape particle system; tight audio-reactive beat markers.

### 89. Animated Infographic
* **Visual & Spatial Composition**: High-density statistical information presented cleanly: percentage dials filling, demographic human icon grids lighting up, flow arrows routing capital.
* **Narrative Intent & Best Fits**: Annual corporate reports, socio-economic journalism, climate change data presentations, market size analysis.
* **Anti-Patterns & Guardrails**: Cramming too many metrics on screen simultaneously. Highlight one metric at a time, dimming historical data.
* **Motion Physics & Temporal Dynamics**: Radial gauge sweeps (`angle: 0 -> 270deg`, `duration: 0.8s`, `ease: power3.out`), numerical counters rolling concurrently.
* **Engine & Asset Requirements**: Dynamic chart rendering components; SVG dial masks; digital ascending chime SFX.

### 90. Data-Visualization Animation
* **Visual & Spatial Composition**: Dynamic animated bar charts, multi-line trend graphs, scatter plots, candlestick trading charts, and heatmaps updating in real-time.
* **Narrative Intent & Best Fits**: Financial market analysis, crypto trading breakdowns, scientific research presentations, sports analytics.
* **Anti-Patterns & Guardrails**: Showing axes without clear numerical units and labels. Viewers must instantly understand what X and Y represent.
* **Motion Physics & Temporal Dynamics**: Bars grow upward sequentially (`stagger: 0.08s`, `scaleY: 0 -> 1`); trend lines draw via animated stroke (`stroke-dashoffset`).
* **Engine & Asset Requirements**: D3.js / Chart.js integration; financial ticker audio clatter; highlighted milestone flash.

### 91. Animated Map / Route
* **Visual & Spatial Composition**: Satellite or clean vector geographic map. Camera swoops down to terrain, glowing route line traces path between cities, and 3D map pin drops with impact.
* **Narrative Intent & Best Fits**: Geopolitical analysis, travel itineraries, historical military campaigns, corporate supply chain tracking.
* **Anti-Patterns & Guardrails**: Cluttered maps with thousands of irrelevant town names. Clean map tiles to show only relevant narrative topography.
* **Motion Physics & Temporal Dynamics**: Smooth 3D camera pitch and yaw following the advancing route head (`ease: power2.inOut`).
* **Engine & Asset Requirements**: Mapbox / Vector GIS tiles; SVG route tracer; deep thud sound on pin drop (`pin-drop-impact.wav`).

### 92. Timeline Animation
* **Visual & Spatial Composition**: Horizontal or vertical chronological axis with milestone nodes, dates, and connected photo/text cards lighting up in sequence as camera travels down the line.
* **Narrative Intent & Best Fits**: Company history retrospectives, biographical profiles, product roadmap reveals, evolutionary history.
* **Anti-Patterns & Guardrails**: Jumping erratically back and forth in time without clear chronological visual anchors.
* **Motion Physics & Temporal Dynamics**: Camera glides smoothly along timeline track, pausing and snapping to each node (`duration: 0.5s`, `ease: power3.out`).
* **Engine & Asset Requirements**: Linear progression rail component; milestone pop badges; mechanical click on each date hit.

### 93. UI / Website Animation
* **Visual & Spatial Composition**: Clean browser viewport showing high-fidelity website interface. Virtual mouse cursor glides across links, clicks buttons, triggers dropdown menus, and scrolls page content.
* **Narrative Intent & Best Fits**: SaaS feature launches, web design agency portfolios, e-commerce checkout walkthroughs.
* **Anti-Patterns & Guardrails**: Jagged manual screen scrolling. Must use silky smooth programmatic programmatic scroll with authentic easing.
* **Motion Physics & Temporal Dynamics**: Natural Bézier cursor pathing with slight overshoot on hover target; subtle button scale depression on click (`scale: 0.96`).
* **Engine & Asset Requirements**: HTML/CSS DOM capture or Figma export; virtual cursor component; crisp mouse click SFX (`mouse-click-clean.wav`).

### 94. App-Product Showcase
* **Visual & Spatial Composition**: Sleek smartphone frame suspended in 3D space, running a high-speed tour through a mobile app's primary UI flows (swiping cards, biometric login, instant payment confirmation).
* **Narrative Intent & Best Fits**: App Store preview videos, fintech mobile launch trailers, consumer app feature showcases.
* **Anti-Patterns & Guardrails**: Showing complex settings menus. Focus on the single magical core action that provides immediate user value.
* **Motion Physics & Temporal Dynamics**: Touch ripple animations at thumb contact points; snappy tab bar transitions (`duration: 0.22s`).
* **Engine & Asset Requirements**: High-res iOS/Android UI mockups; haptic click and chime foley; 3D device tilt animations.

### 95. Parallax Photo Animation (2.5D / Camera Projection)
* **Visual & Spatial Composition**: A vintage or historic still photograph brought to life: subject cut out from background, background hole inpainted, and virtual 3D camera pushed through scene.
* **Narrative Intent & Best Fits**: Historical documentaries (Ken Burns upgraded), biographical retrospectives, true-crime storytelling, bringing dead archives to life.
* **Anti-Patterns & Guardrails**: Excessive camera angle deviation that exposes planar cardboard cutouts. Keep camera travel subtle and frontal.
* **Motion Physics & Temporal Dynamics**: Slow, majestic forward camera push (`Z: 0 -> 200px` over 5s) with subtle dust particle drift floating in air.
* **Engine & Asset Requirements**: AI inpainting plate generator; multi-plane depth projection; atmospheric ambient drone audio.

### 96. Glitch / Digital-Distortion Aesthetic
* **Visual & Spatial Composition**: Visual corruption simulation: CRT horizontal tearing, pixel sorting, RGB color fringing, block compression artifacts, and digital dropout flashes.
* **Narrative Intent & Best Fits**: Cyber-attacks, horror themes, internet mysteries, dramatic plot interruptions, high-energy music drops.
* **Anti-Patterns & Guardrails**: Indiscriminate continuous use that degrades viewer retention. Reserve for 2-6 frame bursts at key shock moments.
* **Motion Physics & Temporal Dynamics**: Random stepped displacement (`x: ±40px`, `frame-rate: 24fps`), instant snap-back to clean footage.
* **Engine & Asset Requirements**: WebGL displacement glitch shader; electrical crackle, radio static, and tape crunch sound effects.

### 97. VHS / Retro-Camcorder Aesthetic
* **Visual & Spatial Composition**: Authentic 1980s/1990s home video look: 4:3 aspect ratio, tracking noise static bar rolling at bottom, glowing green timestamp (`PLAY ▶ 12:04 AM OCT 17 1994`), tape saturation.
* **Narrative Intent & Best Fits**: Nostalgia marketing, skate videos, indie horror aesthetics, flashback sequences, streetwear lookbooks.
* **Anti-Patterns & Guardrails**: Fake cheesy overlays that just slap a static PNG over HD video. Must simulate authentic low-pass color smearing and edge ghosting.
* **Motion Physics & Temporal Dynamics**: Subtle tape flutter jitter (vertical frame wobble); periodic tracking noise roll.
* **Engine & Asset Requirements**: NTSC/PAL composite video shader emulation; tape hiss, head-drum hum, and rewind whine sound design.

### 98. Film-Grain / Analog Aesthetic
* **Visual & Spatial Composition**: Warm cinematic film emulation: organic 16mm or 35mm celluloid silver halide grain, gentle halation around bright light sources, gate weave, and soft highlight rolloff.
* **Narrative Intent & Best Fits**: Cinematic narrative shorts, timeless brand commercials, high-fashion reels, indie music videos.
* **Anti-Patterns & Guardrails**: Digital monochromatic noise masquerading as organic grain. True film grain is multi-chromatic and concentrated in midtones.
* **Motion Physics & Temporal Dynamics**: Dynamic 24fps film grain overlay scanned from authentic Kodak film stock.
* **Engine & Asset Requirements**: Authentic 35mm grain plate overlay (Overlay / Soft Light blend mode); halation bloom shader; subtle analog warmth grade.

### 99. Light-Leak Transitions
* **Visual & Spatial Composition**: Warm vintage optical phenomenon where stray sunlight leaks into the film camera chamber, washing the frame in glowing orange, golden, and magenta flare bursts.
* **Narrative Intent & Best Fits**: Summer travel montages, romantic wedding films, indie music videos, nostalgic memory transitions.
* **Anti-Patterns & Guardrails**: Heavy neon light leaks that blow out facial details completely. Position light leaks to enter from frame corners.
* **Motion Physics & Temporal Dynamics**: Light flare blooms to 80% luminance at the cut seam (`0.2s`), carrying the eye smoothly into the next shot.
* **Engine & Asset Requirements**: 4K optical light leak overlay footage (Screen blend mode); gentle warm breath/swell audio cue.

### 100. Speed-Ramp Editing
* **Visual & Spatial Composition**: Footage playback velocity shifts dynamically within a single continuous shot: real-time -> super slow-motion (20% speed) at peak action -> hyper-fast whip speed (400%) out.
* **Narrative Intent & Best Fits**: Action sports (skateboard kickflip, snowboard jump), martial arts hits, automotive drifts, dance choreography.
* **Anti-Patterns & Guardrails**: Ramping footage that was filmed at standard 24fps/30fps (causes hideous stuttering frames). Source *must* be filmed at 60fps/120fps/240fps.
* **Motion Physics & Temporal Dynamics**: Bezier curve velocity mapping: smooth deceleration into slow-mo apex, exponential acceleration out.
* **Engine & Asset Requirements**: High-framerate source video; optical flow motion estimation; pitch-corrected audio or pitch-diving whoosh SFX.

### 101. Whip-Pan Transitions
* **Visual & Spatial Composition**: Camera violently jerks or pans horizontally (or vertically) at high speed, creating extreme directional motion blur that seamlessly conceals a cut to a new scene.
* **Narrative Intent & Best Fits**: High-energy vlog pacing (Casey Neistat style), comedic smash cuts, fast geographic relocations, energetic product tours.
* **Anti-Patterns & Guardrails**: Directional mismatch (whipping right in shot A, but incoming shot B whips in from the left). Movement direction must match exactly.
* **Motion Physics & Temporal Dynamics**: Exponential acceleration into blur (duration: 4-6 frames), instant deceleration into stable framing of shot B.
* **Engine & Asset Requirements**: Directional blur filter; authentic high-speed camera whip whoosh SFX (`whip-pan-swish.wav`).

### 102. Match-Cut Transitions
* **Visual & Spatial Composition**: Two completely different scenes are spliced together across a cut where a prominent object, visual silhouette, or physical movement in shot A aligns precisely with shot B.
* **Narrative Intent & Best Fits**: Illustrating thematic parallels, time jumps (a young girl blowing a birthday candle cuts to an elderly woman blowing a candle), cinematic visual poetry.
* **Anti-Patterns & Guardrails**: Sloppy alignment. The two matched subjects must occupy the exact same pixel coordinates and focal scale on canvas.
* **Motion Physics & Temporal Dynamics**: Instant hard cut on exact frame of spatial alignment. Audio of shot B can lead by 2 frames (J-cut) for seamlessness.
* **Engine & Asset Requirements**: Onion-skinning frame comparison during edit; matching focal length lenses; resonant sound bridge connecting both shots.

### 103. Zoom-Through Transitions
* **Visual & Spatial Composition**: Camera rapidly zooms directly into an open aperture (a keyhole, a window, a coffee cup rim, an eye pupil), piercing through the dark void to emerge inside a completely new scene.
* **Narrative Intent & Best Fits**: High-impact portal travel, entering a character's mind or memory, transition from macro product view to lifestyle setting.
* **Anti-Patterns & Guardrails**: Centering the zoom on a flat, textured wall with no natural opening (feels like a digital camera crash rather than a portal).
* **Motion Physics & Temporal Dynamics**: Exponential zoom acceleration (`scale: 1.0 -> 20.0`, `duration: 0.5s`, `ease: power3.in`), bursting outward into shot B.
* **Engine & Asset Requirements**: Central circular mask; motion blur zoom radial shader; deep whoosh portal sound effect.

### 104. Spin Transitions
* **Visual & Spatial Composition**: The entire canvas rapidly spins 180 or 360 degrees on its Z-axis with intense radial blur, resolving into the next scene upon completion of rotation.
* **Narrative Intent & Best Fits**: Fast-paced social reels, dance videos, disorienting plot twists, music video beat transitions.
* **Anti-Patterns & Guardrails**: Overuse causing viewer nausea. Never use more than twice in an entire edit; keep rotational duration ultra-brief (<0.3s).
* **Motion Physics & Temporal Dynamics**: 360-degree rotation (`rotation: 0 -> 360deg`, `scale: 1.0 -> 0.85 -> 1.0`, `duration: 0.28s`, `ease: power2.inOut`).
* **Engine & Asset Requirements**: Radial motion blur filter; rotational canvas transform; centrifugal whoosh sound design.

### 105. White-Background Minimalist Motion Design
* **Visual & Spatial Composition**: Pristine, clinical, high-key white or light-gray canvas (`#FAFAFA`) populated by immaculate typography, subtle dark gray hairline borders, and hyper-refined micro-interactions.
* **Narrative Intent & Best Fits**: Premium consumer hardware, Swiss design explainers, medical technology, high-end SaaS apps (Apple/Linear aesthetic).
* **Anti-Patterns & Guardrails**: Cluttered colorful elements that break the disciplined monochromatic aesthetic. Accent color restricted to at most one brand hue.
* **Motion Physics & Temporal Dynamics**: Subtly damped harmonic springs (`mass: 0.8`, `stiffness: 220`), effortless micro-translations with zero overshoot.
* **Engine & Asset Requirements**: Ultra-clean vector graphics; soft diffuse ambient occlusion drop shadows; subtle ceramic tap/click sound design.

### 106. Dark Cinematic Motion Design
* **Visual & Spatial Composition**: Moody, deep charcoal/slate canvas (`#0B0D12`) with luminous neon or metallic accent glows, frosted glass cards, and dramatic directional volumetric lighting.
* **Narrative Intent & Best Fits**: Web3 platforms, cybersecurity software, luxury automotive spots, high-tier developer developer tools.
* **Anti-Patterns & Guardrails**: Muddy, washed-out gray tones. True black floor (`#050608`) combined with disciplined localized specular highlights.
* **Motion Physics & Temporal Dynamics**: Smooth, weighty, authoritative motion curves (`power3.out`); glowing lines drawing across dark surfaces.
* **Engine & Asset Requirements**: Frosted glass CSS shaders (`backdrop-filter: blur(20px)`); ambient colored rim light glows; deep cinematic sub-bass drones.

### 107. Liquid / Fluid-Motion Graphics
* **Visual & Spatial Composition**: Organic, viscous fluid shapes that melt, drip, coalesce, splash, and morph with realistic surface tension and bubble dynamics.
* **Narrative Intent & Best Fits**: Beverage commercials, cosmetics and skincare promos, youth culture reels, creative agency branding.
* **Anti-Patterns & Guardrails**: Stiff vector approximations that look like melting plastic. Fluid dynamics must reflect realistic liquid physics and viscosity.
* **Motion Physics & Temporal Dynamics**: Organic surface tension calculations; droplet detachment with spring recoil physics.
* **Engine & Asset Requirements**: 2D metaball shader or 3D fluid simulation (Blender Mantaflow); water splash and bubble foley.

### 108. Particle / Abstract-Motion Graphics
* **Visual & Spatial Composition**: Swarms of thousands of microscopic glowing particle nodes floating in 3D space, flocking together to form text, logos, or holographic human forms.
* **Narrative Intent & Best Fits**: Artificial intelligence explainers, big data analytics, quantum computing, sci-fi world-building, concert visuals.
* **Anti-Patterns & Guardrails**: Heavy frame-rate drops from unoptimized particle counts. Particles must maintain rock-solid 60fps rendering.
* **Motion Physics & Temporal Dynamics**: Curl noise turbulence fields directing particle velocity; magnetic attraction toward target mesh vertices.
* **Engine & Asset Requirements**: GPU WebGL particle shaders; ambient electrical shimmer and resonant harmonic chord sound design.

### 109. Paper-Texture / Editorial Animation
* **Visual & Spatial Composition**: High-end magazine spread brought to life: grainy newsprint paper textures, halftone dot print screens, CMYK color offset, and classic serif typographic layouts.
* **Narrative Intent & Best Fits**: Long-form journalistic essays, cultural critiques, literary retrospectives, artistic fashion lookbooks.
* **Anti-Patterns & Guardrails**: Slick digital gradients clashing with vintage print textures. Everything must look printed on a physical printing press.
* **Motion Physics & Temporal Dynamics**: Snappy, slightly stepped animation mimicking page turns and stamping ink presses onto paper.
* **Engine & Asset Requirements**: High-resolution scanned paper textures; halftone raster shaders; paper rustle and printing press thud SFX.

### 110. Cutout-Subject Background Replacement
* **Visual & Spatial Composition**: Live-action human presenter rotoscoped out from their real background and composited seamlessly into an entirely animated 2D/3D surreal or branded vector world.
* **Narrative Intent & Best Fits**: Explainer videos where the host walks through virtual charts, fantasy environments, or surreal brand dimensions.
* **Anti-Patterns & Guardrails**: Harsh, glowing green fringing around subject edges. Alpha matte must be eroded and choked slightly, with edge-wrap color blending.
* **Motion Physics & Temporal Dynamics**: Host remains anchored to a virtual ground plane, with virtual camera moves synchronized to real camera perspective.
* **Engine & Asset Requirements**: AI background matting (`video-take-geometry`); edge-wrap light spill shader; matched ambient lighting and shadows.
