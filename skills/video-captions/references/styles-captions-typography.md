# Caption & Typography Styles (catalog #21-#45)

Owned by `video-captions`. Part of the 225-style catalog: the full index, the entry schema and the owning file of every
style are in `video-plan-storyboard/references/style-catalog.md`. Entries are verbatim from the original master
(Section 2); cite a style by its number and name in `plan.md` / `storyboard.plan.json`.

_Videos where words are the main visual experience._

### 21. Caption-Edit
* **Visual & Spatial Composition**: The visual edit is entirely anchored around massive, stylized, center-weighted captions. Subtitle text is not a secondary aid; it is the primary visual engine of the video.
* **Narrative Intent & Best Fits**: Talking-head reels, short-form viral hooks, noisy social feeds where >70% of viewers watch with audio muted.
* **Anti-Patterns & Guardrails**: Captions overlapping speaker's chin or mouth. Captions displaying more than 4-5 words at a time (causes reading fatigue and loses rhythm).
* **Motion Physics & Temporal Dynamics**: Instant cuts on phrase groups (`duration: 0.18s-0.24s`), perfectly synchronized with speech audio phonemes.
* **Engine & Asset Requirements**: `video-captions` with transcript timestamp alignment; high-impact bold typography (`Poppins Black`, `Anton`), heavy drop-shadow/stroke.

### 22. Karaoke Captions
* **Visual & Spatial Composition**: Full spoken phrases displayed on screen simultaneously in neutral tint (`#B9B5AE` or white), with each individual word lighting up into bright vibrant accent color (`#FFD400` or `#00E0FF`) precisely as spoken.
* **Narrative Intent & Best Fits**: Rapid-fire explanations, educational monologues, rap/music lyric videos, maintaining viewer visual lock through reading anticipation.
* **Anti-Patterns & Guardrails**: Highlight color with poor contrast against backing video (< 3:1 contrast ratio). Highlight triggering out of sync with audio by >60ms.
* **Motion Physics & Temporal Dynamics**: Per-word color transition is instant or micro-flash (`duration: 0.08s`). Optional subtle scale punch (`scale: 1.0 -> 1.08 -> 1.0`) on active word.
* **Engine & Asset Requirements**: Whisper word-level timestamps (`start`, `end`); CSS span classes with color transition; audio-scrubbed verification.

### 23. Kinetic Typography
* **Visual & Spatial Composition**: Typographic elements that dynamically animate, scale, rotate, track, and rearrange themselves in direct physical expression of the emotional tone and rhythm of spoken words.
* **Narrative Intent & Best Fits**: Manifesto videos, high-energy commercial promos, punchy audio excerpts without footage, poetic storytelling.
* **Anti-Patterns & Guardrails**: Overly complex animations that render text illegible before the eye can decode it. Text must be readable before it transforms.
* **Motion Physics & Temporal Dynamics**: Words slam down (`scale: 1.8 -> 1.0`, `duration: 0.16s`, `ease: power4.out`), stretch horizontally on speed lines, or explode into fragments on aggressive audio hits.
* **Engine & Asset Requirements**: GSAP / Web Animations text splitting engine; SVG path morphing; transient impact whoosh and thud SFX.

### 24. Big-Text Hook
* **Visual & Spatial Composition**: Oversized, bold, all-caps headline dominating 40-60% of the upper screen area during the first 0.0s-3.0s of the video. Maximum 3-5 words with one punch-word highlighted.
* **Narrative Intent & Best Fits**: Stopping the social media scroll within the first 500ms; establishing high-stakes premise or irresistible curiosity gap.
* **Anti-Patterns & Guardrails**: Keeping the big-text hook on screen past 3.5 seconds (causes visual boredom). Hook text contradicting spoken opening line.
* **Motion Physics & Temporal Dynamics**: Enters frame at frame 0.0s with immediate visual slam or snappy slide down (`y: -50px -> 0`, `duration: 0.18s`). Exits cleanly via scale-fade.
* **Engine & Asset Requirements**: Heavyweight display font (`Syne 800`, `Montserrat 900`), solid black backing highlight pill or high-contrast outline (`paint-order: stroke fill`).

### 25. Wall-of-Text
* **Visual & Spatial Composition**: High-density screen filled with multiple lines of structured copy or excerpted document text, where rapid visual highlighters or kinetic focus bars isolate specific phrases while dimming the rest.
* **Narrative Intent & Best Fits**: Investigative legal breakdowns, contract reviews, scientific paper proof, establishing overwhelming evidence or exhaustive scale.
* **Anti-Patterns & Guardrails**: Leaving the wall of text unhighlighted, forcing the user to read fine print unaided. Always provide an immediate optical guide.
* **Motion Physics & Temporal Dynamics**: Background text appears at 35% opacity; yellow/green highlighter bar sweeps across critical sentence (`width: 0 -> 100%`, `duration: 0.35s`, `ease: power2.out`).
* **Engine & Asset Requirements**: Monospace or clean editorial serif typeface; highlighter overlay shader with multiply blend mode; document scan asset.

### 26. Sentence-by-Sentence Captions
* **Visual & Spatial Composition**: Natural phrase groups (3 to 6 words forming a complete grammatical clause) presented cleanly in a fixed reading box below the face.
* **Narrative Intent & Best Fits**: Thoughtful interviews, business insights, documentary narratives where word-by-word bouncing would feel too frantic or childish.
* **Anti-Patterns & Guardrails**: Sentences breaking awkwardly across grammatical boundaries (e.g., separating "in" and "London" across different cuts).
* **Motion Physics & Temporal Dynamics**: Smooth upward settle and fade-in (`opacity: 0 -> 1`, `y: +12px -> 0`, `duration: 0.22s`), holding until clause completion, quick fade-out (`0.14s`).
* **Engine & Asset Requirements**: NLP phrase chunker / transcript clause grouping; uniform line-height and bounding container.

### 27. Word-by-Word Pop Captions
* **Visual & Spatial Composition**: Only one single word (or at most two words) displayed on screen at any given instant, flashing in the exact visual center of the canvas.
* **Narrative Intent & Best Fits**: High-intensity, hyper-stimulating short-form reels (Alex Hormozi style) designed to force relentless visual fixation.
* **Anti-Patterns & Guardrails**: Using this for videos longer than 60 seconds (causes cognitive fatigue). Avoid in thoughtful, nuanced, or somber discussions.
* **Motion Physics & Temporal Dynamics**: Each word pops into existence on its exact audio onset (`scale: 0.85 -> 1.0`, `duration: 0.12s`, `ease: back.out(1.5)`). Zero lingering decay.
* **Engine & Asset Requirements**: Sub-frame accurate audio alignment (whisper phonemes); high-visibility contrasting font color (`#00FF66`, `#FFFF00`); thick 4px black text stroke.

### 28. Typewriter Text
* **Visual & Spatial Composition**: Characters appear sequentially one by one from left to right, accompanied by a blinking vertical terminal cursor (`|` or `_`).
* **Narrative Intent & Best Fits**: Quoting written diary entries, displaying technical code inputs, retro mystery reveals, establishing an intimate authorial voice.
* **Anti-Patterns & Guardrails**: Setting typewriter speed slower than speaking speed. Never make the audience wait for words to finish typing when voiceover is already ahead.
* **Motion Physics & Temporal Dynamics**: Linear stepped character reveal (`stagger: 0.03s-0.05s` per character). Cursor blinks at 2Hz frequency.
* **Engine & Asset Requirements**: Monospaced font (`Fira Code`, `JetBrains Mono`); mechanical keyboard clack SFX synchronized to character typing rate.

### 29. Minimal Subtitle Style
* **Visual & Spatial Composition**: Understated, elegant, cinema-standard subtitles. Centered at bottom (12% margin from edge), modest size (28-34px), white text with subtle translucent black backing bar or soft drop shadow.
* **Narrative Intent & Best Fits**: Independent films, foreign language translations, cinematic travel vlogs, prestigious documentaries where visual aesthetics must not be cheapened by loud social captions.
* **Anti-Patterns & Guardrails**: Do not use bold neon colors, heavy outlines, or bouncy kinetic animations. Maintain strict visual humility.
* **Motion Physics & Temporal Dynamics**: Gentle alpha crossfades between lines (`duration: 0.15s`). No scale, position, or rotation movement.
* **Engine & Asset Requirements**: Classic typographic standard (`Helvetica Neue`, `Inter`, `Futura Medium`); standard SRT/VTT parser pipeline.

### 30. Color-Coded Speaker Captions
* **Visual & Spatial Composition**: Captions dynamically change font color or container badge color depending on who is speaking (e.g., Host = Electric Blue, Guest = Amber Gold).
* **Narrative Intent & Best Fits**: Dual-speaker podcasts, debate clips, comedic skits where one actor plays multiple characters, multi-person panel discussions.
* **Anti-Patterns & Guardrails**: Using colors that look too similar (e.g., light blue vs cyan). Inconsistent speaker color assignment between scenes.
* **Motion Physics & Temporal Dynamics**: Color shifts immediately on audio speaker turn, paired with small speaker avatar icon or name tag appearing beside caption.
* **Engine & Asset Requirements**: Speaker diarization data in transcript; multi-token color palette; automated diarization track routing.

### 31. Emphasis-Word Zoom
* **Visual & Spatial Composition**: In a sentence caption, the single operative keyword scales up significantly (130-150% size), punches forward in Z-space, and shifts to a fiery accent color.
* **Narrative Intent & Best Fits**: Punctuating punchlines, financial statistics ("MILLIONS"), unexpected plot twists, verbal expressions of surprise or anger.
* **Anti-Patterns & Guardrails**: Emphasizing filler words ("and", "very", "so"). Limit to at most one emphasis word per 4 seconds of speech to preserve impact.
* **Motion Physics & Temporal Dynamics**: Zoom occurs on audio transient peak (`scale: 1.0 -> 1.45`, `duration: 0.14s`, `ease: back.out(2.0)`), followed by gradual settle.
* **Engine & Asset Requirements**: `video-captions` emphasis detection; camera micro-punch synchronizer; subtle sub-bass thump SFX (`kick-impact.wav`).

### 32. Scrolling Text
* **Visual & Spatial Composition**: Continuous horizontal ticker band along bottom edge (stock ticker / breaking news style) or vertical crawl (Star Wars opening crawl style).
* **Narrative Intent & Best Fits**: Live event streams, disclaimer legal copy, news updates, establishing epic backstories.
* **Anti-Patterns & Guardrails**: Scrolling faster than human reading comprehension speed. Avoid jerky frame-rate stutter; must be hardware-accelerated smooth 60fps scroll.
* **Motion Physics & Temporal Dynamics**: Constant linear velocity (`ease: none`). Pauses momentarily during key alert broadcasts.
* **Engine & Asset Requirements**: CSS `translateX` marquee loop; news-bar backing container; optional blinking "LIVE" or "UPDATE" red badge.

### 33. Oversized Editorial Headlines
* **Visual & Spatial Composition**: Sophisticated, high-fashion editorial layout featuring massive serif typography (`Playfair Display`, `Cormorant Garamond`) spanning edge-to-edge, partially masked by footage frames.
* **Narrative Intent & Best Fits**: Luxury brand spots, architectural documentaries, high-end lifestyle vlogs, artistic video essays.
* **Anti-Patterns & Guardrails**: Cramming multiple long sentences. Editorial headlines must be terse (1-3 words) with generous whitespace and breathing room.
* **Motion Physics & Temporal Dynamics**: Slow, majestic tracking expansion (`letter-spacing: 0.05em -> 0.15em`, `duration: 1.8s`, `ease: power1.out`), paired with gentle footage zoom.
* **Engine & Asset Requirements**: Premium display serif font files; ultra-fine stroke lines; ambient cinematic drone audio score.

### 34. Text-Message Conversation
* **Visual & Spatial Composition**: Realistic mobile messaging bubbles (iOS Blue / WhatsApp Green / SMS Gray) appearing alternately on screen inside or beside a smartphone frame.
* **Narrative Intent & Best Fits**: Storytelling depicting private chats, internet drama recaps, customer interaction re-enactments, suspenseful digital thrillers.
* **Anti-Patterns & Guardrails**: Showing massive blocks of text in one bubble. Messages must mimic authentic texting brevity with realistic typos/reactions.
* **Motion Physics & Temporal Dynamics**: Animated three-dot typing indicator appears for 0.8s, followed by message bubble popping up from bottom (`y: +20px -> 0`, `duration: 0.2s`).
* **Engine & Asset Requirements**: Native chat UI bubble components; authentic platform audio chimes (sent swoosh, received ding, keyboard tap clicks).

### 35. Fake Social-Media Comments
* **Visual & Spatial Composition**: Exact visual replicas of YouTube, TikTok, Instagram, or X (Twitter) comment cards with avatars, usernames, upvote counts, and comment text floating over footage.
* **Narrative Intent & Best Fits**: Addressing viewer questions, debunking hate comments, showing social proof and community consensus, humor inserts.
* **Anti-Patterns & Guardrails**: Blurry low-res screenshots taken from phones. Render crisp vector/SVG mockups with legible high-resolution typography.
* **Motion Physics & Temporal Dynamics**: Card scales in with a jaunty tilt (`rotation: -3deg`, `scale: 0.8 -> 1.0`, `duration: 0.25s`, `ease: back.out(1.4)`).
* **Engine & Asset Requirements**: Reusable social comment UI block; vector platform icons (thumbs up, heart, verified checkmark); light pop SFX.

### 36. Terminal / Code-Text Animation
* **Visual & Spatial Composition**: Monochromatic dark IDE or Linux shell window (`#0F141C`) with syntax-highlighted code lines executing, compiling, or being typed in real-time.
* **Narrative Intent & Best Fits**: Software engineering tutorials, cybersecurity stories, developer tool product launches, hacker aesthetic themes.
* **Anti-Patterns & Guardrails**: Code text too small to read on mobile screens (minimum 14pt relative font size). Overwhelming viewers with 50 lines of unformatted code.
* **Motion Physics & Temporal Dynamics**: Line-by-line syntax reveal with auto-scrolling terminal window. Terminal output commands generate instant execution blocks.
* **Engine & Asset Requirements**: Prism / Highlight.js syntax highlighting engine; monospace fonts (`Fira Code`, `JetBrains Mono`); subtle electric hum and keystroke sounds.

### 37. Handwritten Annotations
* **Visual & Spatial Composition**: Organic digital pen strokes, underlined phrases, circled words, corrective strikethroughs, and handwritten marginalia appearing over text or footage.
* **Narrative Intent & Best Fits**: Educational breakdowns, architectural audits, pointing out subtle visual easter eggs in footage, personalized human touch.
* **Anti-Patterns & Guardrails**: Sloppy illegible handwriting. Keep stroke thickness balanced so it accents rather than obscures underlying assets.
* **Motion Physics & Temporal Dynamics**: SVG stroke-dashoffset animation simulating the real-time velocity of a drawing hand (`duration: 0.4s-0.8s`, `ease: power2.inOut`).
* **Engine & Asset Requirements**: SVG vector paths with animated trim-path properties; marker/chalk writing sound effects (`chalkboard-stroke.wav`).

### 38. Marker-and-Doodle Captions
* **Visual & Spatial Composition**: Playful illustrated doodles (stars, question marks, lightning bolts, lightbulbs, squiggly arrows) drawn around active words in dynamic hand-drawn marker style.
* **Narrative Intent & Best Fits**: Casual creator vlogs, playful storytelling, creative design tutorials, high-energy entertainment shorts.
* **Anti-Patterns & Guardrails**: Distracting clutter around every single word. Reserve marker doodles exclusively for peak punchlines or conceptual hooks.
* **Motion Physics & Temporal Dynamics**: Two-frame or three-frame loop animated at 12fps (boiling effect) to create lively organic vibration.
* **Engine & Asset Requirements**: Custom animated SVG sticker library; bright marker yellow (`#FFE600`) and cyan (`#00F0FF`); squeaky marker SFX.

### 39. Quote-Card Typography
* **Visual & Spatial Composition**: Elegant full-frame or centered modal card featuring large decorative quotation marks (`“`), quote text in high-legibility italic type, and author attribution with portrait thumbnail.
* **Narrative Intent & Best Fits**: Book summaries, historical philosophy videos, podcast guest highlights, corporate customer testimonials.
* **Anti-Patterns & Guardrails**: Quotes exceeding 25 words on screen. Break lengthy quotes into sequential cards to preserve viewer engagement.
* **Motion Physics & Temporal Dynamics**: Card fades up with subtle scale (`scale: 0.95 -> 1.0`, `duration: 0.4s`), while quotation marks expand in background at 15% opacity.
* **Engine & Asset Requirements**: High-contrast card container (`#252525` on `#171717` dark background); serif quotation glyphs; subtle chime or bass bed.

### 40. Number-Counter Typography
* **Visual & Spatial Composition**: Prominently displayed numerical figure (financial figures, subscriber counts, stopwatch seconds, percentages) whose digits dynamically roll or count up at high speed.
* **Narrative Intent & Best Fits**: Revealing revenue milestones ("$0 to $1,000,000"), countdowns, performance benchmark comparisons, stat verification.
* **Anti-Patterns & Guardrails**: Counting up so slowly that pacing drags, or so fast that the final figure cannot be absorbed. Always hold on the final number for >=1.5s.
* **Motion Physics & Temporal Dynamics**: Rapid count with exponential deceleration (`ease: power4.out`, `duration: 1.2s`). Final digit settle accompanied by green scale flash.
* **Engine & Asset Requirements**: GSAP numerical tween formatting commas and currency symbols (`$`, `₹`, `%`); rapid mechanical ticking SFX resolving to cash register ring.

### 41. Three-Dimensional Typography
* **Visual & Spatial Composition**: Heavy typographic characters rendered with true physical 3D depth, bevels, realistic surface textures (chrome, stone, brushed metal, neon glass), casting shadows into the scene.
* **Narrative Intent & Best Fits**: Movie title sequences, AAA gaming trailers, blockbuster brand announcements, cinematic music videos.
* **Anti-Patterns & Guardrails**: Cheesy low-polygon 3D text that feels like 1990s WordArt. Must feature sophisticated lighting, ambient occlusion, and environment reflections.
* **Motion Physics & Temporal Dynamics**: 3D camera sweeps across the word geometry, with dynamic specular highlight gleam sliding across bevel edges (`duration: 1.5s`).
* **Engine & Asset Requirements**: Three.js / WebGL / Blender rendering pipeline; environment reflection maps; cinematic sub-bass boom SFX.

### 42. Text-Mask Reveal
* **Visual & Spatial Composition**: Video footage or secondary animation is visible *only* inside the geometric silhouettes of large bold letterforms, surrounded by solid black or white negative space.
* **Narrative Intent & Best Fits**: Cinematic title intros, location establishing shots, revealing a new environment through the project name.
* **Anti-Patterns & Guardrails**: Fine-line, lightweight fonts that show almost zero video inside the strokes. Use ultra-wide heavy type (`Impact`, `Druk Wide`, `Futura Bold`).
* **Motion Physics & Temporal Dynamics**: Letters expand rapidly toward camera (`scale: 1.0 -> 15.0`, `duration: 0.8s`, `ease: power3.in`), zooming through a letter opening to reveal full footage.
* **Engine & Asset Requirements**: CSS `background-clip: text` or SVG clip-path mask; sweeping whoosh transition audio.

### 43. Glitch Typography
* **Visual & Spatial Composition**: Digital transmission distortion: RGB color splitting (chromatic aberration), horizontal pixel displacement slices, scan lines, and temporary character scramble.
* **Narrative Intent & Best Fits**: Cyberpunk aesthetic, hacking themes, highlighting system failures, dystopian narratives, high-impact beat drops.
* **Anti-Patterns & Guardrails**: Endless continuous glitching that induces headaches. Glitches must be sharp, surgical bursts lasting 2 to 6 frames maximum.
* **Motion Physics & Temporal Dynamics**: Sudden erratic X-displacement (`±20px`), RGB channel separation (red channel offset left, blue offset right), resolving immediately to clean text.
* **Engine & Asset Requirements**: WebGL chromatic aberration shader; digital noise displacement map; analog static burst SFX (`digital-glitch-hit.wav`).

### 44. Text-on-B-Roll
* **Visual & Spatial Composition**: Clean, restrained typography positioned strategically in natural negative space (sky, dark wall, empty road) of high-production cinematic B-roll footage.
* **Narrative Intent & Best Fits**: Documentaries, travel films, luxury brand spots, video essays where footage and words coexist in visual harmony.
* **Anti-Patterns & Guardrails**: Placing text directly over busy, high-contrast visual details (e.g., checkered shirts, tree foliage) where letters become illegible.
* **Motion Physics & Temporal Dynamics**: Text tracks smoothly to camera movement using 2D/3D planar tracking, giving the impression of being anchored in physical space.
* **Engine & Asset Requirements**: Motion tracking metadata; soft vignette underlay; clean sans-serif type (`Inter SemiBold`).

### 45. Transcript-Following Highlight
* **Visual & Spatial Composition**: An interactive transcript or teleprompter-style list where a rectangular highlight block or glowing underline tracks down the page line-by-line in sync with speech.
* **Narrative Intent & Best Fits**: Language learning apps, audiobooks with video accompaniment, legal testimony reviews, dense academic lecture reviews.
* **Anti-Patterns & Guardrails**: Highlight falling behind audio cadence. Ensure smooth vertical scrolling so active line stays anchored at 45% screen height.
* **Motion Physics & Temporal Dynamics**: Continuous vertical auto-scroll (`ease: linear`) with subtle ease adjustments on paragraph transitions.
* **Engine & Asset Requirements**: Synchronized transcript parser; automated auto-scroll controller; calm ambient study room tone audio.
