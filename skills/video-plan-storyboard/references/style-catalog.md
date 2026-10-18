# Style Catalog · 225 styles

The single index of the video-editing style taxonomy. Each style's full entry (composition, intent, guardrails,
motion physics, engine requirements) lives in the skill that builds it — follow the `File` column. Pick styles here
at Gate 1; cite them as `#<ID> <Name>` in `plan.md` and `storyboard.plan.json`.

| Section | Owning file |
|---|---|
| 1. Layout & Composition Styles | `video-format/references/styles-layout-composition.md` |
| 2. Caption & Typography Styles | `video-captions/references/styles-captions-typography.md` |
| 3. Camera & Footage-Driven Styles | `video-take-geometry/references/styles-camera-footage.md` |
| 4. Animation, Transitions & Visual Effects Styles | `video-motion-graphics/references/styles-animation-transitions-vfx.md` |
| 5. Cards, Lists & Information Structures | `video-format/references/styles-cards-lists.md` |
| 6. Storytelling & Narrative Formats | `video-plan-storyboard/references/styles-storytelling.md` |
| 7. Editing Pace & Rhythm Formats | `video-cut-audit/references/styles-pace-rhythm.md` |
| 8. Audio-Led Formats | `video-sound-design/references/styles-audio-led.md` |
| 9. Commercial & Platform-Specific Formats | `video-plan-storyboard/references/styles-commercial-platform.md` |
| 10. Duration & delivery | `video-plan-storyboard/references/duration-delivery.md` |
| Appendix: canvas & safe zones | `video-take-geometry/references/canvas-safe-zones.md` |
| Appendix: pipeline & rule checklist | `video-pipeline/references/pipeline-architecture.md` |

This document establishes the official reference taxonomy and implementation standard for `video-editing-skill`. Every style is structured according to a deterministic 5-pillar architectural template compatible with HyperFrames, GSAP motion physics, and modern programmatic video rendering engines.

---

## The Universal Style Definition Template Specification

When any style from this catalog is called into a storyboard, script, or `plan.md`, it must conform to the following schema:

```yaml
Style Entry Schema:
  ID & Name: "[Number]. [Style Name]"
  Visual & Spatial Composition:
    Layer Stack: [root | behind | camera | front]
    Framing & Canvas Placement: [Safe-zone coordinates, crop ratios, padding]
    Visual Elements: [Footage, cards, text, badges, masks, background textures]
  Narrative Intent & Best Fits:
    Cognitive Role: [Hook retention, evidence delivery, pacing reset, emotional payoff]
    Optimal Format: [Shorts 9:16, YouTube 16:9, Explainer, Commercial]
  Anti-Patterns & Guardrails (Avoid When):
    Exclusions: [Clutter thresholds, collision with captions/face, overuse fatigue]
    Readability & Contrast Floor: [Minimum WCAG/HyperFrames contrast >= 3:1]
  Motion Physics & Temporal Dynamics:
    Timing: [Entrance duration, hold time, exit duration, stagger latency]
    Easing Curves: [power3.out, back.out(1.4), power2.in, damped harmonic]
  Engine & Asset Requirements:
    Pipeline Skills: [video-take-geometry, video-captions, video-format, video-motion-graphics, video-audio]
    Asset Dependencies: [Alpha mattes, SFX markers, SVG icons, color tokens]
```

## All styles

| # | Style | Best for | File |
|---|---|---|---|
| 1 | Split-Screen | Contrasting two perspectives, showing cause-and-effect simultaneously, displaying speaker and referenced screen in tandem without obscuring  | `video-format` · styles-layout-composition.md |
| 2 | Side-by-Side Comparison | Direct head-to-head benchmarking, software feature shootouts, price/quality comparisons | `video-format` · styles-layout-composition.md |
| 3 | Stacked Split-Screen | Reaction video to viral content, coding tutorial with presenter on top and terminal below, live physical unboxing with overhead camera below | `video-format` · styles-layout-composition.md |
| 4 | Picture-in-Picture (PiP) | Presenter guiding the viewer through complex gameplay, technical demos, UI walkthroughs, or slide decks while retaining personal connection | `video-format` · styles-layout-composition.md |
| 5 | Layered-Head (Subject Cutout) | High-production YouTube intros, hook sequences, striking proof numbers ("$100,000", "30 Days") | `video-format` · styles-layout-composition.md |
| 6 | Facecam Bubble | Casual software demos, Loom-style productivity walkthroughs, micro-commentary clips, educational coding courses | `video-format` · styles-layout-composition.md |
| 7 | Screen-Plus-Facecam | SaaS product walkthroughs, developer tutorials, financial model reviews, executive video memos | `video-format` · styles-layout-composition.md |
| 8 | Green-Screen Commentary | TikTok/Reels style news commentary, trend analysis, gossip/pop-culture breakdowns, critique of landing pages | `video-format` · styles-layout-composition.md |
| 9 | Duet / Reaction Layout | Viral reactions, peer reviews, comedy stitches, expert validation or debunking of common claims | `video-format` · styles-layout-composition.md |
| 10 | Picture-Frame | Curated art presentations, historical anecdotes, nostalgia themes, premium brand teasers | `video-format` · styles-layout-composition.md |
| 11 | Multi-Panel Grid | Multiverse comparisons, multi-camera sports action, customer testimonial mosaics, synchronized musical performances | `video-format` · styles-layout-composition.md |
| 12 | Dynamic Split-Screen | Conversational debates where speaking turns dictate screen territory; showing progress bar conversions; interactive reveals | `video-format` · styles-layout-composition.md |
| 13 | Layered Collage | Investigative deep-dives (Vox/Johnny Harris style), Gen-Z aesthetic explainers, complex case-study syntheses | `video-format` · styles-layout-composition.md |
| 14 | Paper-Drawer | Academic citations, "By the way" technical definitions, side notes, author quotes without interrupting primary video flow | `video-format` · styles-layout-composition.md |
| 15 | Scrapbook | Personal memoirs, travel retrospectives, company milestone celebrations, artistic creator stories | `video-format` · styles-layout-composition.md |
| 16 | Polaroid Stack | Photo retrospectives, rapid-fire portfolio showcasing, travel highlights, chronological team intros | `video-format` · styles-layout-composition.md |
| 17 | Floating Cards | Presenting software features, metrics, key bullet points, or product pricing tiers in high-tech corporate reels | `video-format` · styles-layout-composition.md |
| 18 | Over-the-Shoulder Screen | Collaborative discussions, coding reviews, strategic teardowns, establishing realistic working environments | `video-format` · styles-layout-composition.md |
| 19 | Device Mockup | Mobile app demonstrations, website launch promos, responsive design showcases, digital product marketing | `video-format` · styles-layout-composition.md |
| 20 | Foreground-Background Parallax | Immersive cinematic intros, storytelling documentaries, creating artificial depth from still photography (2.5D animation) | `video-format` · styles-layout-composition.md |
| 21 | Caption-Edit | Talking-head reels, short-form viral hooks, noisy social feeds where >70% of viewers watch with audio muted | `video-captions` · styles-captions-typography.md |
| 22 | Karaoke Captions | Rapid-fire explanations, educational monologues, rap/music lyric videos, maintaining viewer visual lock through reading anticipation | `video-captions` · styles-captions-typography.md |
| 23 | Kinetic Typography | Manifesto videos, high-energy commercial promos, punchy audio excerpts without footage, poetic storytelling | `video-captions` · styles-captions-typography.md |
| 24 | Big-Text Hook | Stopping the social media scroll within the first 500ms; establishing high-stakes premise or irresistible curiosity gap | `video-captions` · styles-captions-typography.md |
| 25 | Wall-of-Text | Investigative legal breakdowns, contract reviews, scientific paper proof, establishing overwhelming evidence or exhaustive scale | `video-captions` · styles-captions-typography.md |
| 26 | Sentence-by-Sentence Captions | Thoughtful interviews, business insights, documentary narratives where word-by-word bouncing would feel too frantic or childish | `video-captions` · styles-captions-typography.md |
| 27 | Word-by-Word Pop Captions | High-intensity, hyper-stimulating short-form reels (Alex Hormozi style) designed to force relentless visual fixation | `video-captions` · styles-captions-typography.md |
| 28 | Typewriter Text | Quoting written diary entries, displaying technical code inputs, retro mystery reveals, establishing an intimate authorial voice | `video-captions` · styles-captions-typography.md |
| 29 | Minimal Subtitle Style | Independent films, foreign language translations, cinematic travel vlogs, prestigious documentaries where visual aesthetics must not be chea | `video-captions` · styles-captions-typography.md |
| 30 | Color-Coded Speaker Captions | Dual-speaker podcasts, debate clips, comedic skits where one actor plays multiple characters, multi-person panel discussions | `video-captions` · styles-captions-typography.md |
| 31 | Emphasis-Word Zoom | Punctuating punchlines, financial statistics ("MILLIONS"), unexpected plot twists, verbal expressions of surprise or anger | `video-captions` · styles-captions-typography.md |
| 32 | Scrolling Text | Live event streams, disclaimer legal copy, news updates, establishing epic backstories | `video-captions` · styles-captions-typography.md |
| 33 | Oversized Editorial Headlines | Luxury brand spots, architectural documentaries, high-end lifestyle vlogs, artistic video essays | `video-captions` · styles-captions-typography.md |
| 34 | Text-Message Conversation | Storytelling depicting private chats, internet drama recaps, customer interaction re-enactments, suspenseful digital thrillers | `video-captions` · styles-captions-typography.md |
| 35 | Fake Social-Media Comments | Addressing viewer questions, debunking hate comments, showing social proof and community consensus, humor inserts | `video-captions` · styles-captions-typography.md |
| 36 | Terminal / Code-Text Animation | Software engineering tutorials, cybersecurity stories, developer tool product launches, hacker aesthetic themes | `video-captions` · styles-captions-typography.md |
| 37 | Handwritten Annotations | Educational breakdowns, architectural audits, pointing out subtle visual easter eggs in footage, personalized human touch | `video-captions` · styles-captions-typography.md |
| 38 | Marker-and-Doodle Captions | Casual creator vlogs, playful storytelling, creative design tutorials, high-energy entertainment shorts | `video-captions` · styles-captions-typography.md |
| 39 | Quote-Card Typography | Book summaries, historical philosophy videos, podcast guest highlights, corporate customer testimonials | `video-captions` · styles-captions-typography.md |
| 40 | Number-Counter Typography | Revealing revenue milestones ("$0 to $1,000,000"), countdowns, performance benchmark comparisons, stat verification | `video-captions` · styles-captions-typography.md |
| 41 | Three-Dimensional Typography | Movie title sequences, AAA gaming trailers, blockbuster brand announcements, cinematic music videos | `video-captions` · styles-captions-typography.md |
| 42 | Text-Mask Reveal | Cinematic title intros, location establishing shots, revealing a new environment through the project name | `video-captions` · styles-captions-typography.md |
| 43 | Glitch Typography | Cyberpunk aesthetic, hacking themes, highlighting system failures, dystopian narratives, high-impact beat drops | `video-captions` · styles-captions-typography.md |
| 44 | Text-on-B-Roll | Documentaries, travel films, luxury brand spots, video essays where footage and words coexist in visual harmony | `video-captions` · styles-captions-typography.md |
| 45 | Transcript-Following Highlight | Language learning apps, audiobooks with video accompaniment, legal testimony reviews, dense academic lecture reviews | `video-captions` · styles-captions-typography.md |
| 46 | Talking-Head | Authoritative teaching, expert opinions, editorial arguments, personal accountability, building trust and direct connection | `video-take-geometry` · styles-camera-footage.md |
| 47 | Vlog | Personal brand building, authentic day-in-the-life journeys, behind-the-curtain creator updates | `video-take-geometry` · styles-camera-footage.md |
| 48 | Walk-and-Talk | High-energy thought leadership, casual brainstorm sharing, establishing momentum and urgency in business topics | `video-take-geometry` · styles-camera-footage.md |
| 49 | Day-in-the-Life | Aspirational founder routines, engineer lifestyle showcases, productivity system demonstrations, recruitment culture reels | `video-take-geometry` · styles-camera-footage.md |
| 50 | Behind-the-Scenes (BTS) | Demystifying high-budget projects, celebrating team effort, establishing authenticity, teasing upcoming launches | `video-take-geometry` · styles-camera-footage.md |
| 51 | B-Roll Style | Elevating production value, sustaining visual engagement during complex voiceovers, showing proof of physical environments or objects | `video-take-geometry` · styles-camera-footage.md |
| 52 | Voiceover Plus B-Roll | Faceless YouTube channels, documentary essays, historical retrospectives, software overview explainers | `video-take-geometry` · styles-camera-footage.md |
| 53 | Cinematic Montage | Emotional video climaxes, athletic hype sequences, travel showreels, transformation reveals | `video-take-geometry` · styles-camera-footage.md |
| 54 | POV Video (Point-of-View) | Extreme sports, culinary cooking tutorials, unboxing, hands-on mechanical repairs, immersive experiential travel | `video-take-geometry` · styles-camera-footage.md |
| 55 | Hands-Only Demonstration | Crafting, digital illustration tutorials, watchmaking, recipe videos (Tasty style), physical product teardowns | `video-take-geometry` · styles-camera-footage.md |
| 56 | Interview Format | In-depth journalism, celebrity dialogues, executive leadership profiles, investigative cross-examinations | `video-take-geometry` · styles-camera-footage.md |
| 57 | Street Interview / Vox Pop | Social experiments, public opinion polls, viral trivia challenges, market research feedback reels | `video-take-geometry` · styles-camera-footage.md |
| 58 | Podcast Clip | Repurposing long-form audio podcasts into viral short-form social reels, highlighting provocative debate moments or vulnerable stories | `video-take-geometry` · styles-camera-footage.md |
| 59 | Reaction Video | Movie trailer reviews, music album first listens, comedy commentary, viral stunt breakdowns | `video-take-geometry` · styles-camera-footage.md |
| 60 | Commentary Over Source Footage | Sports play-by-play tactical breakdowns, political speech fact-checking, cinematography analysis, video game strategy guides | `video-take-geometry` · styles-camera-footage.md |
| 61 | UGC Selfie-Style Video (User-Generated Content) | High-converting TikTok/Instagram direct-response ads, skincare testimonials, app referral campaigns, peer-to-peer recommendations | `video-take-geometry` · styles-camera-footage.md |
| 62 | Screen-Recording Tutorial | Coding bootcamps, Photoshop/Figma masterclasses, SaaS onboarding guides, administrative workflows | `video-take-geometry` · styles-camera-footage.md |
| 63 | Live Demonstration | Proving product claims (e.g., indestructible phone case drop test, stain remover on white rug), high-stakes magic tricks, scientific experim | `video-take-geometry` · styles-camera-footage.md |
| 64 | Product Close-Up / Macro Shots | Luxury goods advertising, electronics reviews, culinary gourmet showcases, establishing bespoke craftsmanship | `video-take-geometry` · styles-camera-footage.md |
| 65 | Unboxing | New tech hardware releases, luxury unboxing experiences, subscription box reviews, consumer desire induction | `video-take-geometry` · styles-camera-footage.md |
| 66 | First-Person Experience | Theme park promos, sports brand campaigns, travel adventures, experiential virtual reality teasers | `video-take-geometry` · styles-camera-footage.md |
| 67 | Travel Diary | Tourism marketing, nomadic lifestyle chronicles, destination promotion, evocative lifestyle escapism | `video-take-geometry` · styles-camera-footage.md |
| 68 | Event Recap | Post-event marketing, ticket sales for next year's conference, sponsor thank-you reels, social celebrations | `video-take-geometry` · styles-camera-footage.md |
| 69 | Testimonial Interview | B2B case studies, social proof advertisements, healthcare patient stories, non-profit donor appeals | `video-take-geometry` · styles-camera-footage.md |
| 70 | Single-Take / One-Shot Video (Oner) | High-concept music videos, dramatic storytelling climaxes, studio facility tours, establishing virtuoso filmmaking skill | `video-take-geometry` · styles-camera-footage.md |
| 71 | Surveillance / Found-Footage Aesthetic | True-crime documentaries, investigative thrillers, paranormal mysteries, dramatic realism in fictional stories | `video-take-geometry` · styles-camera-footage.md |
| 72 | Archival-Footage Documentary | Historical retrospectives, retrospective corporate retrospectives, geopolitical essays, cultural retrospectives | `video-take-geometry` · styles-camera-footage.md |
| 73 | Silent Observational Video | Artisanal manufacturing, nature meditations, fine woodworking, culinary preparation, high-art showcases | `video-take-geometry` · styles-camera-footage.md |
| 74 | ASMR Close-Up Video | Sensory relaxation, stress relief, product tactile demonstration, viral TikTok odd-satisfaction feeds | `video-take-geometry` · styles-camera-footage.md |
| 75 | Time-Lapse / Hyperlapse | Conveying passage of time, structural construction milestones, bustling city energy, majestic natural transformations | `video-take-geometry` · styles-camera-footage.md |
| 76 | Paper-Cutout Animation | Whimsical storytelling, children's educational content, satirical political sketches (South Park / Terry Gilliam style), indie creative expl | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 77 | Whiteout | Paradigm shifts ("And then everything changed"), catastrophic failures, explosive revelations, transitioning between dark indoor scene and b | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 78 | Morph Transition | Explaining conceptual evolution, showing financial conversions (time is money), maintaining continuous visual flow without hard cuts | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 79 | Mask-Reveal Animation | Revealing hidden features, before-and-after comparisons, peeling back surface layers to reveal internal mechanisms | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 80 | Wipe and Slide Transitions | Fast-paced listicles, switching between distinct product features, energetic comedic shifts, retro sports recaps | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 81 | Motion-Graphics Explainer | B2B tech marketing, cryptographic security explainers, fintech workflow overviews, venture funding pitch videos | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 82 | Flat-Vector Animation | Scientific education, global demographics explainers, healthcare and biology tutorials, clean brand anthems | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 83 | Whiteboard Animation | Traditional corporate training, book summaries, educational psychology lectures, low-budget direct response marketing | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 84 | Stop-Motion Animation | Artisanal craft commercials, quirky holiday promos, music videos, creative DIY storytelling | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 85 | 2D Character Animation | Narrative moral fables, corporate customer persona journeys, humorous skits, brand mascot marketing | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 86 | 3D Product Animation | Hardware product launches (Apple keynote style), industrial design showcases, luxury watch unveilings | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 87 | Isometric Animation | Cloud architecture explainers, logistics and supply chain demos, city planning visualizations, game development teasers | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 88 | Kinetic-Shape Animation | Music visualizers, event opening titles, transitions between conceptual chapters, brand mood anthems | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 89 | Animated Infographic | Annual corporate reports, socio-economic journalism, climate change data presentations, market size analysis | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 90 | Data-Visualization Animation | Financial market analysis, crypto trading breakdowns, scientific research presentations, sports analytics | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 91 | Animated Map / Route | Geopolitical analysis, travel itineraries, historical military campaigns, corporate supply chain tracking | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 92 | Timeline Animation | Company history retrospectives, biographical profiles, product roadmap reveals, evolutionary history | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 93 | UI / Website Animation | SaaS feature launches, web design agency portfolios, e-commerce checkout walkthroughs | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 94 | App-Product Showcase | App Store preview videos, fintech mobile launch trailers, consumer app feature showcases | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 95 | Parallax Photo Animation (2.5D / Camera Projection) | Historical documentaries (Ken Burns upgraded), biographical retrospectives, true-crime storytelling, bringing dead archives to life | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 96 | Glitch / Digital-Distortion Aesthetic | Cyber-attacks, horror themes, internet mysteries, dramatic plot interruptions, high-energy music drops | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 97 | VHS / Retro-Camcorder Aesthetic | Nostalgia marketing, skate videos, indie horror aesthetics, flashback sequences, streetwear lookbooks | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 98 | Film-Grain / Analog Aesthetic | Cinematic narrative shorts, timeless brand commercials, high-fashion reels, indie music videos | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 99 | Light-Leak Transitions | Summer travel montages, romantic wedding films, indie music videos, nostalgic memory transitions | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 100 | Speed-Ramp Editing | Action sports (skateboard kickflip, snowboard jump), martial arts hits, automotive drifts, dance choreography | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 101 | Whip-Pan Transitions | High-energy vlog pacing (Casey Neistat style), comedic smash cuts, fast geographic relocations, energetic product tours | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 102 | Match-Cut Transitions | Illustrating thematic parallels, time jumps (a young girl blowing a birthday candle cuts to an elderly woman blowing a candle), cinematic vi | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 103 | Zoom-Through Transitions | High-impact portal travel, entering a character's mind or memory, transition from macro product view to lifestyle setting | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 104 | Spin Transitions | Fast-paced social reels, dance videos, disorienting plot twists, music video beat transitions | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 105 | White-Background Minimalist Motion Design | Premium consumer hardware, Swiss design explainers, medical technology, high-end SaaS apps (Apple/Linear aesthetic) | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 106 | Dark Cinematic Motion Design | Web3 platforms, cybersecurity software, luxury automotive spots, high-tier developer developer tools | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 107 | Liquid / Fluid-Motion Graphics | Beverage commercials, cosmetics and skincare promos, youth culture reels, creative agency branding | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 108 | Particle / Abstract-Motion Graphics | Artificial intelligence explainers, big data analytics, quantum computing, sci-fi world-building, concert visuals | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 109 | Paper-Texture / Editorial Animation | Long-form journalistic essays, cultural critiques, literary retrospectives, artistic fashion lookbooks | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 110 | Cutout-Subject Background Replacement | Explainer videos where the host walks through virtual charts, fantasy environments, or surreal brand dimensions | `video-motion-graphics` · styles-animation-transitions-vfx.md |
| 111 | Card-List | Numbered key takeaways ("3 tools you need"), service deliverables, summary recaps in hooks and Reels | `video-format` · styles-cards-lists.md |
| 112 | Top-N Ranking | Viral curiosity hooks ("Top 5 AI tools that will replace designers"), countdown lists, comparative benchmarking | `video-format` · styles-cards-lists.md |
| 113 | Checklist | SOP tutorials, daily routine breakdowns, audit criteria, process completion milestones | `video-format` · styles-cards-lists.md |
| 114 | Step-by-Step Tutorial | How-to educational videos, software setup guides, complex multi-stage technical workflows | `video-format` · styles-cards-lists.md |
| 115 | Myth-Versus-Fact | Educational debunking, contrarian business advice, nutrition/fitness corrections, challenging industry orthodoxy | `video-format` · styles-cards-lists.md |
| 116 | Pros-and-Cons Comparison | Unbiased product reviews, software buying guides, career decision analyses, investment risk assessments | `video-format` · styles-cards-lists.md |
| 117 | Before-and-After Reveal | Video color grading showcases, fitness body transformations, architectural renovations, audio remastering demos | `video-format` · styles-cards-lists.md |
| 118 | A-Versus-B Comparison | Product shootouts (e.g., "iPhone 16 Pro vs Samsung S25 Ultra", "React vs Svelte"), strategic debates | `video-format` · styles-cards-lists.md |
| 119 | Do-This-Not-That Format | Fitness exercise form guides, coding best practices, social etiquette tips, design critique reels | `video-format` · styles-cards-lists.md |
| 120 | Mistakes-and-Fixes | Debugging tutorials, rookie business mistakes, financial blunder retrospectives | `video-format` · styles-cards-lists.md |
| 121 | Tips-and-Tricks List | Productivity hacks, hidden software shortcuts, insider trade secrets, viral engagement reels | `video-format` · styles-cards-lists.md |
| 122 | FAQ Sequence | Customer objection handling, product launch Q&As, onboarding FAQs, clearing up community misconceptions | `video-format` · styles-cards-lists.md |
| 123 | Question-and-Answer Cards | Addressing community comments, client strategy consultations, AMA (Ask Me Anything) reels | `video-format` · styles-cards-lists.md |
| 124 | Decision-Tree Explainer | Diagnostic troubleshooting, choosing which software framework/tool to use, medical triage logic, financial investment branching | `video-format` · styles-cards-lists.md |
| 125 | Flowchart Animation | Business operations mapping, software algorithmic logic, supply chain walkthroughs | `video-format` · styles-cards-lists.md |
| 126 | Process Breakdown | Manufacturing processes, client onboarding lifecycles, creative project milestones | `video-format` · styles-cards-lists.md |
| 127 | Roadmap / Milestone Progression | Startup investor updates, open-source project roadmaps, corporate vision presentations | `video-format` · styles-cards-lists.md |
| 128 | Timeline of Events | Company founding histories, retrospective timelines of market crashes, geopolitical crises | `video-format` · styles-cards-lists.md |
| 129 | Ranking Leaderboard | Competition recaps, sales team leaderboards, stock performance rankings, benchmarking tests | `video-format` · styles-cards-lists.md |
| 130 | Stat-of-the-Day | Opening video hooks, memorable anchor facts, social media thought-leadership carousels | `video-format` · styles-cards-lists.md |
| 131 | Data Point / Chart Reveal | Revealing market turning points, pinpointing anomalies, scientific data proofs, financial earnings calls | `video-format` · styles-cards-lists.md |
| 132 | Interactive-Style Quiz | Educational engagement, viewer retention boosting, social media trivia reels, audience knowledge testing | `video-format` · styles-cards-lists.md |
| 133 | Guess-the-Answer Reveal | Mystery hooks, pricing guessing games, blind taste tests, history trivia | `video-format` · styles-cards-lists.md |
| 134 | Flashcard Sequence | Language learning reels, medical terminology study guides, rapid vocabulary expansion | `video-format` · styles-cards-lists.md |
| 135 | Quote-by-Quote Presentation | Pitch deck video intros, book launch trailers, customer advocacy reels, philosophical video essays | `video-format` · styles-cards-lists.md |
| 136 | Case-Study Breakdown | B2B enterprise sales reels, marketing agency client showcases, consulting pitch videos | `video-format` · styles-cards-lists.md |
| 137 | Review Scorecard | Consumer tech reviews, restaurant food ratings, movie critiques, automobile reviews | `video-format` · styles-cards-lists.md |
| 138 | Feature Matrix | Software pricing page walkthroughs, subscription tier recommendations, hardware model breakdowns | `video-format` · styles-cards-lists.md |
| 139 | Pros, Cons, Verdict | Concluding minutes of comprehensive consumer reviews, definitive buying advice | `video-format` · styles-cards-lists.md |
| 140 | Comparison Table Animation | Financial modeling, real estate deal breakdowns, cost-benefit calculations, salary comparisons | `video-format` · styles-cards-lists.md |
| 141 | Map-and-Marker Explainer | Franchise expansion updates, real estate investing overviews, geopolitical event tracking | `video-format` · styles-cards-lists.md |
| 142 | Animated Diagram | Deep technical explainers, medical surgery breakdowns, automotive engine mechanics, industrial design | `video-format` · styles-cards-lists.md |
| 143 | Glossary / Term Breakdown | Demystifying complex industry jargon, crypto/AI acronym explainers, educational language lessons | `video-format` · styles-cards-lists.md |
| 144 | One-Concept Explainer | Mental model breakdowns, foundational conceptual teaching, simplifying complex abstract theories | `video-format` · styles-cards-lists.md |
| 145 | Mini-Documentary | Deep investigative journalism, corporate rise-and-fall stories, scientific breakthroughs, cultural retrospectives (8-20 minutes) | `video-plan-storyboard` · styles-storytelling.md |
| 146 | Educational Explainer | Science, economics, engineering, and software masterclasses (Vox, Kurzgesagt, Veritasium style) | `video-plan-storyboard` · styles-storytelling.md |
| 147 | Teaser / Trailer | Building massive anticipation for an upcoming product launch, documentary premiere, course release, or long-form video | `video-plan-storyboard` · styles-storytelling.md |
| 148 | Hook → Problem → Solution → Call to Action (HPSC) | E-commerce product commercials, SaaS lead generation ads, customer acquisition campaigns | `video-plan-storyboard` · styles-storytelling.md |
| 149 | Problem → Agitation → Solution (PAS) | B2B enterprise software ads, health and wellness pain-relief products, high-ticket consulting offers | `video-plan-storyboard` · styles-storytelling.md |
| 150 | Story Arc: Setup → Conflict → Resolution | Founder memoirs, athletic comeback stories, customer transformation journeys, long-form YouTube essays | `video-plan-storyboard` · styles-storytelling.md |
| 151 | Mystery / Reveal | Secret project unveilings, magic/illusion breakdowns, true-crime investigations, celebrity guest appearances | `video-plan-storyboard` · styles-storytelling.md |
| 152 | Failure → Lesson → Improvement | Post-mortem business reviews, startup shutdown stories, personal growth reflections, coding disaster breakdowns | `video-plan-storyboard` · styles-storytelling.md |
| 153 | Transformation / Journey | Weight-loss transformations, learning a skill in 30 days, building a house, bootstrapping a business from zero to profitability | `video-plan-storyboard` · styles-storytelling.md |
| 154 | Personal Origin Story | Creator personal branding, author bio videos, establishing deep rapport and humble authority with an audience | `video-plan-storyboard` · styles-storytelling.md |
| 155 | Founder Story | Company about pages, investor pitch decks, recruitment anthems, premium brand heritage films | `video-plan-storyboard` · styles-storytelling.md |
| 156 | Customer Success Story | High-ticket B2B enterprise validation, testimonial advertising, closing enterprise procurement teams | `video-plan-storyboard` · styles-storytelling.md |
| 157 | Experiment / Challenge | Viral entertainment, empirical product testing, fitness/lifestyle challenges, software stress tests | `video-plan-storyboard` · styles-storytelling.md |
| 158 | Myth-Busting | Scientific education, debunking viral internet life hacks, automotive safety demonstrations (MythBusters style) | `video-plan-storyboard` · styles-storytelling.md |
| 159 | Contrarian Argument / Hot Take | Thought leadership disruption, viral LinkedIn/X video essays, sparking debate and passionate comment sections | `video-plan-storyboard` · styles-storytelling.md |
| 160 | Debunking / Fact-Check | Journalism, political commentary, consumer protection, health misinformation correction | `video-plan-storyboard` · styles-storytelling.md |
| 161 | Lessons Learned | Annual retrospectives, post-exit founder advice, career retrospectives, project post-mortems | `video-plan-storyboard` · styles-storytelling.md |
| 162 | Case Study → Evidence → Conclusion | Venture capital investment memos, scientific research dissemination, management consulting pitches | `video-plan-storyboard` · styles-storytelling.md |
| 163 | Prediction → Evidence → Outcome | Economic forecasts, technological trend analysis, sports draft predictions, futurism essays | `video-plan-storyboard` · styles-storytelling.md |
| 164 | News Brief | Daily tech industry updates, market opening bells, crypto news alerts, entertainment digests (60-120 seconds) | `video-plan-storyboard` · styles-storytelling.md |
| 165 | Trend Analysis | Consumer behavior reports, fashion trend breakdowns, marketing industry forecasts, cultural anthropology essays | `video-plan-storyboard` · styles-storytelling.md |
| 166 | Opinion / Commentary Essay | Film criticism, philosophical cultural analysis, political theory, modern art breakdowns | `video-plan-storyboard` · styles-storytelling.md |
| 167 | Narrative Voiceover Story | True-crime thrillers, bedtime stories, philosophical parables, inspirational brand anthems | `video-plan-storyboard` · styles-storytelling.md |
| 168 | Suspense / Countdown Reveal | Product drop count-downs, live event openers, escape room challenges, bomb-defusal or deadline thrillers | `video-plan-storyboard` · styles-storytelling.md |
| 169 | Open-Loop Storytelling with a Delayed Payoff | High-retention social reels, narrative entertainment vlogs, dramatic educational mysteries | `video-plan-storyboard` · styles-storytelling.md |
| 170 | Circular Storytelling (Looping Narrative) | TikTok/Reels algorithm optimization (viewers watch 1.5x to 2x without realizing the video restarted), artistic narrative loops | `video-plan-storyboard` · styles-storytelling.md |
| 171 | Episodic Series | Multi-part documentary series, serial fiction, educational multi-week courses, brand web-series | `video-plan-storyboard` · styles-storytelling.md |
| 172 | Compilation / Highlights Reel | Year-in-review recaps, sports season highlights, streamer funniest clips, festival retrospective reels | `video-plan-storyboard` · styles-storytelling.md |
| 173 | Jump-Cut Editing | YouTube talking-head videos, vlog monologues, high-speed tutorials, eliminating dead air to force relentless narrative velocity | `video-cut-audit` · styles-pace-rhythm.md |
| 174 | Rapid-Fire Cuts | Action trailers, sensory overload hooks, showing the sheer scale of options or chaos before presenting clarity | `video-cut-audit` · styles-pace-rhythm.md |
| 175 | Beat-Synced Editing | Music videos, sports highlight reels, high-fashion promos, commercial sizzles | `video-cut-audit` · styles-pace-rhythm.md |
| 176 | Slow-Cinematic Pacing | Prestige documentaries, luxury commercials, emotional drama climaxes, reflective philosophical video essays | `video-cut-audit` · styles-pace-rhythm.md |
| 177 | Montage Editing | Training routines (Rocky style), software building sprints, home renovations, studying for exams | `video-cut-audit` · styles-pace-rhythm.md |
| 178 | Real-Time Continuous Scene | Crisis negotiations, live cooking tests, high-stakes physical challenges, intimate emotional dialogues | `video-cut-audit` · styles-pace-rhythm.md |
| 179 | Speed-Ramp Montage | Automotive commercials, extreme sports reels, high-fashion runway recaps, dance reels | `video-cut-audit` · styles-pace-rhythm.md |
| 180 | Flash-Cut Editing | Psychological thrillers, horror teasers, trauma flashbacks, high-impact creative reveals | `video-cut-audit` · styles-pace-rhythm.md |
| 181 | Freeze-Frame Annotation | Sports tactical analysis, comedic character introductions (Guy Ritchie style), safety audits, tactical gaming breakdowns | `video-cut-audit` · styles-pace-rhythm.md |
| 182 | Replay / Instant Rewind | Comedy reels, sports bloopers, magic trick reveals, forensic analysis of subtle background details | `video-cut-audit` · styles-pace-rhythm.md |
| 183 | Countdown Structure | Highly structured listicles, countdown challenges, game show formats, urgency-driven product teardowns | `video-cut-audit` · styles-pace-rhythm.md |
| 184 | Seamless-Loop Video | TikTok/Reels algorithm gaming, hypnotic satisfaction reels, perpetual motion art | `video-cut-audit` · styles-pace-rhythm.md |
| 185 | Split-Screen Comparison Cuts | Multi-angle musical performances, dual-perspective dialogue scenes, showing before-and-after development simultaneously | `video-cut-audit` · styles-pace-rhythm.md |
| 186 | Rhythmic Transition Sequence | High-energy travel montages, commercial transitions between lifestyles, fashion transformations | `video-cut-audit` · styles-pace-rhythm.md |
| 187 | Long-Take Storytelling | Immersive corporate facility tours, high-drama narrative scenes, high-trust unedited demonstrations | `video-cut-audit` · styles-pace-rhythm.md |
| 188 | Voiceover-Led Storytelling | Historical video essays, true crime stories, philosophical parables, luxury brand narrative spots | `video-sound-design` · styles-audio-led.md |
| 189 | Podcast Audiogram with Animated Waveform | Repurposing audio-only podcast snippets for social feeds (X, LinkedIn, Instagram) without filming video | `video-sound-design` · styles-audio-led.md |
| 190 | Voiceover with Synchronized Subtitles | Poetry readings, motivational quotes, language learning pronunciation guides, soundbite social reels | `video-sound-design` · styles-audio-led.md |
| 191 | Music-Led Montage with Minimal Dialogue | Action sports hype reels, aesthetic travel films, festival after-movies, fitness lifestyle promos | `video-sound-design` · styles-audio-led.md |
| 192 | Sound-Effect-Led Reveal (SFX Punch) | Comedic punchlines, tech product reveals, cartoon slapstick, financial milestone celebrations | `video-sound-design` · styles-audio-led.md |
| 193 | ASMR / Sensory Audio | Sensory relaxation, consumer product tactile demos, stress-relief reels, culinary sizzle spots | `video-sound-design` · styles-audio-led.md |
| 194 | Sound-Reactive Motion Graphics | Electronic music visualizers, DJ set backdrops, high-tech brand anthems, crypto/AI intros | `video-sound-design` · styles-audio-led.md |
| 195 | Dialogue-First Interview Edit | Thought leadership podcasts, investigative journalism, documentary character studies | `video-sound-design` · styles-audio-led.md |
| 196 | Narrated Slideshow | Architectural project reviews, historical retrospectives, academic art history lectures | `video-sound-design` · styles-audio-led.md |
| 197 | No-Dialogue Cinematic Short | High-art film festivals, luxury perfume/fashion spots, emotional non-profit appeals | `video-sound-design` · styles-audio-led.md |
| 198 | Call-and-Response Dialogue | Comedic sketches, customer objection debunking, dual-host podcast banter, musical rap battles | `video-sound-design` · styles-audio-led.md |
| 199 | Music Drop / Beat-Drop Reveal | Product unveilings, festival hype videos, sports triumph moments, automotive reveals | `video-sound-design` · styles-audio-led.md |
| 200 | Before-and-After Sound Comparison | Audio plugin marketing, microphone reviews, acoustics treatment showcases, podcast production tutorials | `video-sound-design` · styles-audio-led.md |
| 201 | Product Advertisement | Paid Instagram/Facebook/TikTok ad campaigns, TV commercial spots, e-commerce conversion | `video-plan-storyboard` · styles-commercial-platform.md |
| 202 | Product Demo | Consideration-stage buyers, software product tours, hardware functionality proofs | `video-plan-storyboard` · styles-commercial-platform.md |
| 203 | Product Launch Announcement | Announcing major version updates (v2.0), brand new hardware lines, flagship SaaS platform releases | `video-plan-storyboard` · styles-commercial-platform.md |
| 204 | Brand Sizzle Reel | Agency capability showcases, investor pitch deck openers, conference exhibition booths | `video-plan-storyboard` · styles-commercial-platform.md |
| 205 | Brand Origin Film | "About Us" company page, brand heritage marketing, building premium luxury pricing power | `video-plan-storyboard` · styles-commercial-platform.md |
| 206 | Feature Announcement | Monthly SaaS product release notes, email newsletter video inserts, Twitter/X changelog updates | `video-plan-storyboard` · styles-commercial-platform.md |
| 207 | App Walkthrough | Post-signup customer onboarding, reducing user churn, user education, product documentation | `video-plan-storyboard` · styles-commercial-platform.md |
| 208 | Website-to-Video Showcase | Web design agency showcases, launching a new website, SaaS marketing without custom footage | `video-plan-storyboard` · styles-commercial-platform.md |
| 209 | Social Proof / Testimonial Montage | Retargeting ad campaigns, landing page social proof sections, overcoming customer purchase hesitation | `video-plan-storyboard` · styles-commercial-platform.md |
| 210 | Recruitment Video | Attracting elite engineering and executive talent, employer branding on LinkedIn, career portal hero video | `video-plan-storyboard` · styles-commercial-platform.md |
| 211 | Founder Pitch Video | Crowdfunding campaigns (Kickstarter/Wefunder), accelerator applications (Y Combinator), early-stage angel fundraising | `video-plan-storyboard` · styles-commercial-platform.md |
| 212 | Investor Pitch Explainer | Pre-meeting investor memo videos, LP update videos, virtual demo day presentations | `video-plan-storyboard` · styles-commercial-platform.md |
| 213 | Landing-Page Hero Video | Homepage conversion optimization, converting cold website traffic into free trial signups | `video-plan-storyboard` · styles-commercial-platform.md |
| 214 | Course Lesson | Online masterclasses, cohort-based courses, internal corporate employee training modules | `video-plan-storyboard` · styles-commercial-platform.md |
| 215 | Webinar Highlight | Social media audience building, driving registrations for upcoming live webinars | `video-plan-storyboard` · styles-commercial-platform.md |
| 216 | Conference or Event Promo | Selling early-bird conference tickets, attracting corporate event sponsors | `video-plan-storyboard` · styles-commercial-platform.md |
| 217 | Social-Media News Update | TikTok/Reels/Shorts daily news commentary, riding viral breaking news trends within hours of occurrence | `video-plan-storyboard` · styles-commercial-platform.md |
| 218 | Tutorial Series Intro | YouTube playlist openers, multi-part masterclass series branding | `video-plan-storyboard` · styles-commercial-platform.md |
| 219 | Customer Onboarding Video | SaaS day-1 retention, reducing initial user friction, increasing product activation rates | `video-plan-storyboard` · styles-commercial-platform.md |
| 220 | Comparison / Buying Guide | Affiliate marketing reviews, consumer purchase consultation, e-commerce gift guides | `video-plan-storyboard` · styles-commercial-platform.md |
| 221 | Unboxing and First Impressions | Consumer electronics launches, luxury goods, fashion sneakers, subscription boxes | `video-plan-storyboard` · styles-commercial-platform.md |
| 222 | Offer / Sale Announcement | Flash sales, holiday commercial promotions, seasonal e-commerce revenue spikes | `video-plan-storyboard` · styles-commercial-platform.md |
| 223 | FAQ / Objection-Handling Ad | Retargeting abandoned cart visitors, overcoming sales skepticism, boosting e-commerce checkout rates | `video-plan-storyboard` · styles-commercial-platform.md |
| 224 | Trailer for a Longer Video | Driving social traffic from TikTok/Reels/Shorts into long-form YouTube watch-time | `video-plan-storyboard` · styles-commercial-platform.md |
| 225 | Recap / Weekly Digest | Weekly newsletter video companions, community digests, fast-moving AI/tech updates | `video-plan-storyboard` · styles-commercial-platform.md |
