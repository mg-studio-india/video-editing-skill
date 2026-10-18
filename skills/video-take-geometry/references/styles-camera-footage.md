# Camera & Footage-Driven Styles (catalog #46-#75)

Owned by `video-take-geometry`. Part of the 225-style catalog: the full index, the entry schema and the owning file of every
style are in `video-plan-storyboard/references/style-catalog.md`. Entries are verbatim from the original master
(Section 3); cite a style by its number and name in `plan.md` / `storyboard.plan.json`.

_How a real person, location, product, or activity is filmed and presented._

### 46. Talking-Head
* **Visual & Spatial Composition**: Direct-to-camera address. Subject framed centrally or along rule-of-thirds grid line (waist-up or bust shot). Eyes aligned at 65-70% vertical height. Shallow depth of field (blurred background).
* **Narrative Intent & Best Fits**: Authoritative teaching, expert opinions, editorial arguments, personal accountability, building trust and direct connection.
* **Anti-Patterns & Guardrails**: Unbroken static shot running >10s without optical reset (causes gaze fatigue). Camera positioned below eye-level (unflattering upward nostril angle).
* **Motion Physics & Temporal Dynamics**: Periodic punch-in reframe (106-112% scale) on thesis statements or emotional shifts; instant reset to 100% at scene cuts.
* **Engine & Asset Requirements**: Face-tracking focal lock; natural color balance; studio vocal audio (-14 LUFS, crisp broadcast compression).

### 47. Vlog
* **Visual & Spatial Composition**: Dynamic first-person and third-person hybrid footage captured on handheld cameras or mobile rigs. Natural lighting, fluid camera movement, real-world acoustic environments.
* **Narrative Intent & Best Fits**: Personal brand building, authentic day-in-the-life journeys, behind-the-curtain creator updates.
* **Anti-Patterns & Guardrails**: Shaky cam that causes vertigo. Heavy artificial motion graphics that destroy the raw, organic intimacy of the format.
* **Motion Physics & Temporal Dynamics**: Micro-camera jitters preserved; cuts occur naturally on physical action (door opening, stepping into a car, sitting down).
* **Engine & Asset Requirements**: Handheld stabilization filter (gyro smoothing); directional shotgun mic audio mixed with ambient environmental soundbeds.

### 48. Walk-and-Talk
* **Visual & Spatial Composition**: Presenter walking through an urban, office, or natural setting while speaking directly to a retreating forward gimbal camera or selfie stick.
* **Narrative Intent & Best Fits**: High-energy thought leadership, casual brainstorm sharing, establishing momentum and urgency in business topics.
* **Anti-Patterns & Guardrails**: Presenter losing breath or puffing audio into microphone. Extreme background noise (traffic sirens) drowning out vocal intelligibility.
* **Motion Physics & Temporal Dynamics**: Steady forward tracking motion with slight vertical rhythmic bob matching footstep cadence.
* **Engine & Asset Requirements**: Lavalier mic with physical wind muff; AI voice isolation / spectral denoise; dynamic gimbal horizon lock.

### 49. Day-in-the-Life
* **Visual & Spatial Composition**: Chronological sequence documenting daily routine from morning to night. Incorporates time-stamps (`06:30 AM`), atmospheric lighting shifts, and varied activities.
* **Narrative Intent & Best Fits**: Aspirational founder routines, engineer lifestyle showcases, productivity system demonstrations, recruitment culture reels.
* **Anti-Patterns & Guardrails**: Tedious real-time pacing. Routine tasks (making coffee, commuting) must be compressed into snappy micro-beats (1.5s-3s).
* **Motion Physics & Temporal Dynamics**: Time-lapse accelerations between distinct lifestyle chapters; rhythmic jump cuts on repetitive actions.
* **Engine & Asset Requirements**: Dynamic clock/time badge overlay; acoustic sound design (alarm beep, kettle whistle, subway transit).

### 50. Behind-the-Scenes (BTS)
* **Visual & Spatial Composition**: Fly-on-the-wall observational angles showing the unpolished reality behind a polished production: lighting rigs, teleprompters, makeup, failed takes, crew banter.
* **Narrative Intent & Best Fits**: Demystifying high-budget projects, celebrating team effort, establishing authenticity, teasing upcoming launches.
* **Anti-Patterns & Guardrails**: Fabricated or staged "candid" moments that feel fake to savvy audiences. Keep color grading neutral and unvarnished.
* **Motion Physics & Temporal Dynamics**: Whip-pans and rack-focus transitions between primary actors and production monitors.
* **Engine & Asset Requirements**: Multi-cam setup with dedicated roving camera; raw, un-sweetened room audio capturing laughter and off-mic remarks.

### 51. B-Roll Style
* **Visual & Spatial Composition**: High-production contextual cutaway footage (slow-motion details, environment establishing shots, macro textures) that visually manifests spoken narration.
* **Narrative Intent & Best Fits**: Elevating production value, sustaining visual engagement during complex voiceovers, showing proof of physical environments or objects.
* **Anti-Patterns & Guardrails**: Generic stock footage that feels corporate and detached (e.g., random business handshake). Footage must be specific and authentic to the topic.
* **Motion Physics & Temporal Dynamics**: Butter-smooth slow-motion (60fps/120fps conformed to 24fps timeline) with constant directional slide or gimbal push.
* **Engine & Asset Requirements**: High-bitrate 4K footage; speed-ramp transitions; subtle whoosh SFX on shot entrances.

### 52. Voiceover Plus B-Roll
* **Visual & Spatial Composition**: Continuous, polished voiceover narration running as the audio spine, while the visual timeline is composed entirely of curated B-roll clips changing every 2-4 seconds.
* **Narrative Intent & Best Fits**: Faceless YouTube channels, documentary essays, historical retrospectives, software overview explainers.
* **Anti-Patterns & Guardrails**: Visual cutaways disconnected from spoken concepts. Every visual cut must have a direct conceptual anchor in the voiceover transcript.
* **Motion Physics & Temporal Dynamics**: Cuts land on vocal stressed syllables or musical downbeats; visual momentum flows consistently in one screen direction (left to right).
* **Engine & Asset Requirements**: Master voiceover track conformed to -14 LUFS; intelligent transcript-to-shot matching database; rich ambient SFX beds.

### 53. Cinematic Montage
* **Visual & Spatial Composition**: Rhythmically edited sequence of visually striking shots, synchronized precisely to a swelling musical soundtrack, often without spoken dialogue.
* **Narrative Intent & Best Fits**: Emotional video climaxes, athletic hype sequences, travel showreels, transformation reveals.
* **Anti-Patterns & Guardrails**: Random shots without narrative progression. The montage must follow an emotional arc (tension building to euphoria/resolution).
* **Motion Physics & Temporal Dynamics**: Beat-synced cuts with progressive tempo acceleration; speed ramps ramping into action impacts.
* **Engine & Asset Requirements**: High dynamic range color grade (LUT); transient audio hit points; cinematic sub-drops and riser sound effects.

### 54. POV Video (Point-of-View)
* **Visual & Spatial Composition**: Camera mounted to creator's chest, helmet, or forehead, showing the world exactly as the creator sees it (hands entering frame, direct eye-level perspective).
* **Narrative Intent & Best Fits**: Extreme sports, culinary cooking tutorials, unboxing, hands-on mechanical repairs, immersive experiential travel.
* **Anti-Patterns & Guardrails**: Camera angled too low (filming floor) or too high (filming ceiling). Hands must remain centered in active working zone.
* **Motion Physics & Temporal Dynamics**: Rock-steady horizon stabilization; natural head-turn panning physics matching human ocular tracking.
* **Engine & Asset Requirements**: Action camera / binaural microphone setup capturing immersive stereo spatial audio.

### 55. Hands-Only Demonstration
* **Visual & Spatial Composition**: Overhead top-down "flat lay" camera angle or tight 45-degree angle focused exclusively on hands manipulating tools, sketchbooks, cards, or culinary ingredients on a clean surface.
* **Narrative Intent & Best Fits**: Crafting, digital illustration tutorials, watchmaking, recipe videos (Tasty style), physical product teardowns.
* **Anti-Patterns & Guardrails**: Cluttered work surfaces with distracting shadows. Use soft, diffused, shadowless overhead ring lighting.
* **Motion Physics & Temporal Dynamics**: Precise, deliberate hand choreography; speed ramps across repetitive mechanical operations.
* **Engine & Asset Requirements**: Overhead boom arm mount; clean non-reflective work mat; hyper-detailed ASMR foley sound recording.

### 56. Interview Format
* **Visual & Spatial Composition**: Classic multi-camera setup. Wide two-shot establishing scene, alternating with tight medium close-ups of interviewer and subject adhering to the 180-degree cinematic rule.
* **Narrative Intent & Best Fits**: In-depth journalism, celebrity dialogues, executive leadership profiles, investigative cross-examinations.
* **Anti-Patterns & Guardrails**: Cutting to the speaking person after they have already started their sentence (late cut). Cut on the question prompt or show reaction shots.
* **Motion Physics & Temporal Dynamics**: Subtle handheld float or slow motorized slider drift; natural conversational cuts allowing emotional pauses to breathe.
* **Engine & Asset Requirements**: Multi-cam synchronized timeline; discrete lavalier/boom audio tracks per speaker; cross-camera color matching.

### 57. Street Interview / Vox Pop
* **Visual & Spatial Composition**: Handheld roving camera, handheld microphone thrust toward random pedestrians on public streets. Dynamic, slightly chaotic framing capturing raw ambient bustle.
* **Narrative Intent & Best Fits**: Social experiments, public opinion polls, viral trivia challenges, market research feedback reels.
* **Anti-Patterns & Guardrails**: Terrible audio where city traffic drowns out pedestrian answers. Always use a tight cardioid or dynamic handheld microphone (`Shure SM58`).
* **Motion Physics & Temporal Dynamics**: Rapid snap-zooms on pedestrian facial expressions, sudden whip-pans between interviewer and respondent.
* **Engine & Asset Requirements**: Broadcast handheld mic with custom logo flag; rapid noise reduction filter; playful sound effects for wrong/funny answers.

### 58. Podcast Clip
* **Visual & Spatial Composition**: Studio video recording of podcast conversation. Prominently features studio microphones (`Shure SM7B` on boom arms), acoustic wall baffles, headphones, and branded neon signs.
* **Narrative Intent & Best Fits**: Repurposing long-form audio podcasts into viral short-form social reels, highlighting provocative debate moments or vulnerable stories.
* **Anti-Patterns & Guardrails**: Wide shots that make speakers look distant on vertical mobile screens. Re-crop dynamically to vertical 9:16 solo close-ups for each speaker.
* **Motion Physics & Temporal Dynamics**: Automated audio-activated camera switching (camera switches automatically to speaker when vocal threshold breaks).
* **Engine & Asset Requirements**: Multi-track podcast DAW stems; `video-take-geometry` facial tracking to center speaker in 9:16 crop; animated waveform overlay.

### 59. Reaction Video
* **Visual & Spatial Composition**: Creator seated with headphones on, viewing external media displayed via PiP or split-screen. Creator facial expressions, vocal gasps, pauses, and breakdowns take center stage.
* **Narrative Intent & Best Fits**: Movie trailer reviews, music album first listens, comedy commentary, viral stunt breakdowns.
* **Anti-Patterns & Guardrails**: Pausing the source media every 2 seconds for trivial remarks, or staying dead silent for 30 seconds straight without reacting.
* **Motion Physics & Temporal Dynamics**: Zoom-in punch on creator's eyes/mouth during dramatic plot revelations; audio ducking of source video during creator speech.
* **Engine & Asset Requirements**: Synchronized source recording track; auto-ducking sidechain compressor; expressive creator lighting.

### 60. Commentary Over Source Footage
* **Visual & Spatial Composition**: Full-screen playback of third-party footage, news broadcasts, or archival clips, accompanied by an authoritative spoken analytical voiceover, interspersed with graphic highlight overlays.
* **Narrative Intent & Best Fits**: Sports play-by-play tactical breakdowns, political speech fact-checking, cinematography analysis, video game strategy guides.
* **Anti-Patterns & Guardrails**: Copyright infringement risk from uninterrupted source playback. Must provide substantial transformative commentary, freeze frames, and telestrator overlays.
* **Motion Physics & Temporal Dynamics**: Slow-motion playback during technical micro-movements, freeze frames paired with kinetic telestrator arrows.
* **Engine & Asset Requirements**: Telestrator drawing engine; slow-motion frame interpolation; clear audio ducking.

### 61. UGC Selfie-Style Video (User-Generated Content)
* **Visual & Spatial Composition**: Front-facing smartphone camera held at arm's length by creator in authentic home/bedroom environment. Casual attire, unpolished natural backdrop, direct eye contact with lens.
* **Narrative Intent & Best Fits**: High-converting TikTok/Instagram direct-response ads, skincare testimonials, app referral campaigns, peer-to-peer recommendations.
* **Anti-Patterns & Guardrails**: Looking too cinematic, corporate, or over-produced. The entire power of UGC lies in looking like a message from a trusted friend, not an ad agency.
* **Motion Physics & Temporal Dynamics**: Natural walking/talking arm micro-shake; quick, unedited feeling jump-cuts between spoken thoughts.
* **Engine & Asset Requirements**: Raw native smartphone color profile; direct uncompressed audio; platform native captions font (`TikTok Sans`).

### 62. Screen-Recording Tutorial
* **Visual & Spatial Composition**: Full-resolution computer desktop capture featuring clean mouse cursor movements, active application windows, keyboard shortcut visualizer HUD, and optional corner webcam.
* **Narrative Intent & Best Fits**: Coding bootcamps, Photoshop/Figma masterclasses, SaaS onboarding guides, administrative workflows.
* **Anti-Patterns & Guardrails**: Tiny illegible text. Editor must programmatically crop and zoom into active UI menus and text fields as they are discussed.
* **Motion Physics & Temporal Dynamics**: Smooth cursor smoothing (removing erratic mouse jitter); dynamic camera pan-and-zoom following the cursor locus.
* **Engine & Asset Requirements**: 4K screen capture; keystroke HUD overlay; subtle cursor highlight halo and click ripple animations.

### 63. Live Demonstration
* **Visual & Spatial Composition**: Continuous real-time camera capture showing a physical or scientific experiment, recipe, machine operation, or athletic feat with zero hidden cuts or deceitful camera tricks.
* **Narrative Intent & Best Fits**: Proving product claims (e.g., indestructible phone case drop test, stain remover on white rug), high-stakes magic tricks, scientific experiments.
* **Anti-Patterns & Guardrails**: Any visible cut or jump during the critical climax moment destroys viewer trust. Must feature a continuous visible timekeeper/stopwatch in frame.
* **Motion Physics & Temporal Dynamics**: Uninterrupted real-time playback speed; camera slowly zooms in as tension peaks to prove authenticity.
* **Engine & Asset Requirements**: High-framerate camera recording to provide slow-motion instant replays after the live demonstration succeeds.

### 64. Product Close-Up / Macro Shots
* **Visual & Spatial Composition**: Extreme macro lens capture (1:1 magnification ratio) highlighting minute details: carbon fiber weaves, stitching on leather, bevelled metal edges, water droplets on glass.
* **Narrative Intent & Best Fits**: Luxury goods advertising, electronics reviews, culinary gourmet showcases, establishing bespoke craftsmanship.
* **Anti-Patterns & Guardrails**: Dust specs, fingerprints, or chromatic fringing on product surfaces. Requires clean macro lighting and spotless product prep.
* **Motion Physics & Temporal Dynamics**: Motorized macro rail slide (`0.5mm/sec`), slow focus racks moving across product contours.
* **Engine & Asset Requirements**: Macro lens footage; focus-stacking capability; delicate high-frequency foley SFX (metallic clicks, leather creak).

### 65. Unboxing
* **Visual & Spatial Composition**: Dual-camera view (overhead flat-lay plus 45-degree angle). The pristine product packaging is introduced, seals sliced, lid lifted, accessories revealed, and protective films peeled.
* **Narrative Intent & Best Fits**: New tech hardware releases, luxury unboxing experiences, subscription box reviews, consumer desire induction.
* **Anti-Patterns & Guardrails**: Spending 5 minutes struggling to open tape off-camera. Keep package handling deft, confident, and rapid.
* **Motion Physics & Temporal Dynamics**: Slow-motion close-ups on plastic peel moments; snappy rhythmic cuts on component reveals.
* **Engine & Asset Requirements**: Crystal-clear ASMR audio capturing box slide friction, tape slice, and screen peel sounds.

### 66. First-Person Experience
* **Visual & Spatial Composition**: Ultra-wide immersive field of view (action cam or VR 180 capture) placing the viewer directly inside high-adrenaline situations (skydiving, rollercoaster, concert mosh pit).
* **Narrative Intent & Best Fits**: Theme park promos, sports brand campaigns, travel adventures, experiential virtual reality teasers.
* **Anti-Patterns & Guardrails**: Jarring un-stabilized camera shake that causes nausea. Use horizon-lock gyro stabilization algorithms.
* **Motion Physics & Temporal Dynamics**: Dynamic motion blur on rapid lateral head turns; speed changes accentuating acceleration forces.
* **Engine & Asset Requirements**: Wide-angle lens distortion correction; binaural 3D spatial audio recording.

### 67. Travel Diary
* **Visual & Spatial Composition**: Poetic blend of landscape panoramas, architectural golden-hour footage, cultural street scenes, local culinary delights, and reflective voiceover reflections.
* **Narrative Intent & Best Fits**: Tourism marketing, nomadic lifestyle chronicles, destination promotion, evocative lifestyle escapism.
* **Anti-Patterns & Guardrails**: Generic travel montage without personal emotional stakes or local cultural context.
* **Motion Physics & Temporal Dynamics**: Sweeping drone hyperlapses; match-cuts connecting footsteps across different global landmarks.
* **Engine & Asset Requirements**: Warm cinematic color grade; location title geo-tag overlays; authentic cultural music soundtrack.

### 68. Event Recap
* **Visual & Spatial Composition**: High-octane montage encapsulating a multi-day conference, festival, hackathon, or wedding into a punchy 60-90 second visual highlights reel.
* **Narrative Intent & Best Fits**: Post-event marketing, ticket sales for next year's conference, sponsor thank-you reels, social celebrations.
* **Anti-Patterns & Guardrails**: Boring footage of attendees staring at slides in dark auditoriums. Focus on smiling faces, energetic applause, networking, and stage keynotes.
* **Motion Physics & Temporal Dynamics**: Fast-paced beat-synced cuts with whip-pan and light-leak transitions linking distinct event segments.
* **Engine & Asset Requirements**: Multi-cam footage ingest; energetic electronic/indie-rock bed; lower-third speaker identification tags.

### 69. Testimonial Interview
* **Visual & Spatial Composition**: Warm, authentic close-up framing of a real customer or client in their natural environment (office, home). Eyes directed slightly off-camera toward an unseen conversational interviewer.
* **Narrative Intent & Best Fits**: B2B case studies, social proof advertisements, healthcare patient stories, non-profit donor appeals.
* **Anti-Patterns & Guardrails**: Scripted, robotic delivery where the customer sounds like they are reading legal talking points. Edit around genuine emotional cadence.
* **Motion Physics & Temporal Dynamics**: Gentle slow push-in during poignant vulnerable statements (`scale: 100% -> 108%` over 12 seconds).
* **Engine & Asset Requirements**: High-fidelity lavalier recording; documentary-style subtle string/piano musical bed; proof metric lower-thirds.

### 70. Single-Take / One-Shot Video (Oner)
* **Visual & Spatial Composition**: The entire video or significant narrative section is executed in one continuous, unbroken camera take without visible cuts, choreographing actors and camera through multiple rooms.
* **Narrative Intent & Best Fits**: High-concept music videos, dramatic storytelling climaxes, studio facility tours, establishing virtuoso filmmaking skill.
* **Anti-Patterns & Guardrails**: Long stretches where the camera stares at a blank wall or actors stumble on lines. Requires rigorous rehearsal and lighting cues.
* **Motion Physics & Temporal Dynamics**: Continuous fluid Steadicam / gimbal motion with dynamic pacing shifting from fast sprints to intimate pauses.
* **Engine & Asset Requirements**: Steadicam / Ronin stabilizer; wireless video transmission; concealed hidden whip-pan cut points (for emergency safety).

### 71. Surveillance / Found-Footage Aesthetic
* **Visual & Spatial Composition**: Simulated closed-circuit TV (CCTV), police bodycam, or dashboard camera look. High-angle wide lens, digital timecode stamps (`REC ● 2026-10-17 11:45:00`), timestamp overlays, low-bitrate compression.
* **Narrative Intent & Best Fits**: True-crime documentaries, investigative thrillers, paranormal mysteries, dramatic realism in fictional stories.
* **Anti-Patterns & Guardrails**: Looking too pristine and modern. Must accurately mimic camera lens distortion, chromatic fringing, interlaced scanning, and night-vision infrared glare.
* **Motion Physics & Temporal Dynamics**: Static fixed security camera mount or jerky mechanical pan-tilt-zoom (PTZ) stepped movements.
* **Engine & Asset Requirements**: CCTV overlay UI template; interlacing scanline shader; low-fidelity bandpass audio filter (telephone voice).

### 72. Archival-Footage Documentary
* **Visual & Spatial Composition**: Historical black-and-white or aged 16mm/35mm footage, public domain newsreels, declassified government documents, and historical photographs treated with slow pan-and-scan.
* **Narrative Intent & Best Fits**: Historical retrospectives, retrospective corporate retrospectives, geopolitical essays, cultural retrospectives.
* **Anti-Patterns & Guardrails**: Inaccurate aspect ratio stretching (e.g., stretching historical 4:3 archive into 16:9). Pillarbox with textured borders instead.
* **Motion Physics & Temporal Dynamics**: Classic Ken Burns effect (slow organic pan and zoom across photograph details); authentic film projector gate jitter.
* **Engine & Asset Requirements**: Film dust, scratches, and grain emulation; archival transfer color-timing; vintage audio hiss and crackle bed.

### 73. Silent Observational Video
* **Visual & Spatial Composition**: Pure visual cinema without spoken voiceover, talking heads, or intrusive text. The camera observes a master craftsman, natural landscape, or industrial process in meditative stillness.
* **Narrative Intent & Best Fits**: Artisanal manufacturing, nature meditations, fine woodworking, culinary preparation, high-art showcases.
* **Anti-Patterns & Guardrails**: Rushing cuts. Shots must hold long enough for the viewer's eye to explore textures and subtleties (5s-12s per shot).
* **Motion Physics & Temporal Dynamics**: Locked-off tripod shots or imperceptible motorized slider drift. Cuts occur on physical action completions.
* **Engine & Asset Requirements**: Pristine 4K/8K resolution; high dynamic range color grade; hyper-realistic pristine field audio recording.

### 74. ASMR Close-Up Video
* **Visual & Spatial Composition**: Intimate macro framing emphasizing repetitive, delicate physical tactile interactions (whispering, tapping nails on glass, slicing soap, crunching kinetic sand).
* **Narrative Intent & Best Fits**: Sensory relaxation, stress relief, product tactile demonstration, viral TikTok odd-satisfaction feeds.
* **Anti-Patterns & Guardrails**: Sudden loud noises or harsh abrasive peaks that shatter the sensory trance. Every sound must be soft, clean, and close.
* **Motion Physics & Temporal Dynamics**: Rhythmic, hypnotic, unhurried physical gestures. Cuts are seamless crossfades or gentle match-cuts.
* **Engine & Asset Requirements**: Ultra-sensitive binaural dummy-head microphone recording; zero background noise floor; ultra-detailed macro lens.

### 75. Time-Lapse / Hyperlapse
* **Visual & Spatial Composition**: Massive temporal acceleration. Time-lapse captures hours/days from a fixed camera (clouds billowing over skyscrapers, sun setting); hyperlapse tracks camera through miles of space while accelerating time.
* **Narrative Intent & Best Fits**: Conveying passage of time, structural construction milestones, bustling city energy, majestic natural transformations.
* **Anti-Patterns & Guardrails**: Jittery hyperlapse paths. Camera path must be meticulously smoothed using frame-to-frame feature tracking.
* **Motion Physics & Temporal Dynamics**: Continuous forward velocity with light-trail motion blur on moving vehicles and pedestrians (slow shutter interval).
* **Engine & Asset Requirements**: Intervalometer camera capture; frame stabilization / warping algorithms; ambient swelling drone score.
