# Category Benchmarks & Format Playbooks

This reference document provides production-tested playbooks for 8 major content categories. When `video-researcher` analyzes a transcript, it identifies the best-fitting category and applies these benchmark parameters as the baseline for `research.json`.

---

## 1. Tech & AI SaaS Breakdowns
*Ideal for: AI tools, SaaS launches, framework releases, product updates, tech commentary.*

* **Audience:** Developers, technical founders, tech-curious creators, product managers.
* **Winning Hook Formula (0.0s - 3.0s):**
  - Confrontational or disruptive outcome: *"OpenAI just killed 50 startups with one update."* / *"Stop building backends in 2026."*
  - Synchronized visual: High-contrast headline banner (`lt-headline-banner`) + fast zoom-in on software UI + punchy whoosh SFX.
* **Visual Rhythm & Pacing:**
  - Cut Frequency: **1.4s - 2.0s** per visual change.
  - Alternating pattern: Talking head (fast punch-in) → Terminal / UI screen recording → Floating tech stack logo cloud → Animated code block.
* **Layout & Composition Styles:**
  - `Style 07: Screen-Plus-Facecam` or `Style 03: Stacked Split-Screen` (Speaker top 44%, clean screen demo bottom 56%).
  - `Style 05: Layered-Head` for big AI benchmark numbers (e.g. "1M Context" behind the speaker's shoulders).
* **Color Palette & Mood:**
  - Theme: **Electric Cyber / Obsidian Dark Mode**.
  - Background: `#090A0F`, Card Glass: `rgba(16, 20, 28, 0.82)`.
  - Punch Accent: `#00F0FF` (Cyan) or `#A6FF00` (Acid Lime), Contrast Border: `rgba(0, 240, 255, 0.3)`.
* **Typography Hierarchy:**
  - Primary Punch: `Poppins Black (900)` or `Anton Display`, All-Caps.
  - Accent / Tech Display: `JetBrains Mono (800)` or `Fira Code Bold`.
  - Body / Subtext: `Inter Bold (700)`.
* **Catalog Component Queries:**
  - `query "terminal code window dev"` -> `code-mockup-frame`, `terminal-window-glow`.
  - `query "stat counter callout pill"` -> `stat-callout-counter`.
  - `query "logo cloud grid showcase"` -> `logo-cloud-grid`.

---

## 2. Business, Finance & D2C Market Breakdowns
*Ideal for: Startup case studies, marketing breakdowns, revenue analyses, D2C stories (Raj Shamani, Nitin Joshi, Bypreneurs).*

* **Audience:** Entrepreneurs, investors, business students, ambitious professionals.
* **Winning Hook Formula (0.0s - 3.0s):**
  - The Hidden Number / Revenue Paradox: *"This 24-year-old made ₹12 Crore selling plain water."* / *"Why Zomato actually wanted Swiggy to win."*
  - Synchronized visual: Full-width black headline band with red emphasis word + animated ₹/$ revenue counter ticker + crisp cash-register or tape-stop sound.
* **Visual Rhythm & Pacing:**
  - Cut Frequency: **1.8s - 2.5s** per visual shift.
  - Rhythm: Face statement → Branded evidence document/tweet → Financial chart growth curve → Storefront/product footage.
* **Layout & Composition Styles:**
  - `Style 03: Stacked Split-Screen` (Speaker in top half, evidence receipts/graphs in bottom half).
  - `Style 45: Paper-Drawer Reveal` (Clean financial receipt or balance sheet slides from edge).
  - `Style 02: Side-by-Side Comparison` (Unit economics: Old Model vs New Model).
* **Color Palette & Mood:**
  - Theme: **High-Trust Authority / Financial Depth**.
  - Background: `#10141A` or Charcoal `#171717`.
  - Accent Punch: `#10B981` (High-Trust Emerald) or `#D9413A` (Muted Urgency Red).
  - Secondary Text: Warm Off-White `#F5F1EA`.
* **Typography Hierarchy:**
  - Primary Punch: `Inter ExtraBold (800)` or `Poppins Black (900)`.
  - Devanagari (if Hindi): `Noto Sans Devanagari (700)`.
  - Numerals: Tabular lining figures (`font-variant-numeric: tabular-nums`).
* **Catalog Component Queries:**
  - `query "lower third headline banner"` -> `lt-headline-banner`.
  - `query "metric badge callout pill"` -> `badge-pill-pill`, `stat-callout-counter`.
  - `query "comparison split table"` -> `comparison-split-card`.

---

## 3. Coding & Developer Tutorials
*Ideal for: Code walkthroughs, bug debugging, architecture explanations, Git workflows.*

* **Audience:** Junior to senior software engineers, bootcamp students.
* **Winning Hook Formula (0.0s - 3.0s):**
  - The Error or Elegant Fix: *"You've been using async/await completely wrong."* / *"How 3 lines of code replaced a 500-line microservice."*
  - Synchronized visual: Red error banner switching instantly to green checkmark + subtle keyboard clatter SFX.
* **Visual Rhythm & Pacing:**
  - Cut Frequency: **2.0s - 3.2s** (code needs slightly longer cognitive dwell time).
  - Rhythm: Problem statement → Red-highlighted buggy syntax → Side-by-side refactor → Verified benchmark output.
* **Layout & Composition Styles:**
  - `Style 07: Screen-Plus-Facecam` with zoomed code viewport (140% scale on active function).
  - `Style 06: Facecam Bubble` anchored to bottom right, never obscuring line numbers or imports.
* **Color Palette & Mood:**
  - Theme: **Monokai / Tokyo Night Dark**.
  - Background: `#1A1B26` (Tokyo Night Deep) or `#1E1E1E` (VS Code Dark).
  - Accent Punch: `#7AA2F7` (Electric Blue) and `#9ECE6A` (Syntax Green).
* **Typography Hierarchy:**
  - Primary Punch: `JetBrains Mono (800)` or `Geist Mono SemiBold`.
  - Body: `Inter (600)`.
* **Catalog Component Queries:**
  - `query "code diff comparison"` -> `code-diff-viewer`.
  - `query "feature pill list"` -> `feature-pill-card`.

---

## 4. Educational & Science Explainers
*Ideal for: Physics, psychology, history, mathematics, deep concept breakdowns (Veritasium, Cleo Abram, 3Blue1Brown).*

* **Audience:** Curious generalists, students, lifelong learners.
* **Winning Hook Formula (0.0s - 3.0s):**
  - Counter-Intuitive Truth: *"Light doesn't actually travel in a straight line."* / *"The math behind why you feel like you have no friends."*
  - Synchronized visual: Dynamic 3D simulation or abstract graphic + speaker looking up at the formula + mysterious ambient riser.
* **Visual Rhythm & Pacing:**
  - Cut Frequency: **2.2s - 3.5s**.
  - Pacing: Concept statement → Full-screen animated diagram (speaker voiceover) → Real-world historical photograph/B-roll → Return to speaker with hand-drawn marker callout.
* **Layout & Composition Styles:**
  - `Style 05: Layered-Head` with celestial/atomic animation floating behind speaker.
  - `Style 12: Full-Graphic Canvas` (Speaker drops out completely for 4-6 seconds to let the diagram breathe).
* **Color Palette & Mood:**
  - Theme: **Cosmic Deep Space / Editorial Precision**.
  - Background: Deep Navy `#0B0F19`, Surface: `#161F30`.
  - Accent Punch: Warm Gold `#FBBF24` or Nebula Violet `#8B5CF6`.
* **Typography Hierarchy:**
  - Primary Punch: `Syne ExtraBold (800)` or `Cabinet Grotesk`.
  - Body / Subtext: `Plus Jakarta Sans Medium (500)`.
* **Catalog Component Queries:**
  - `query "interactive graph chart"` -> `chart-line-animated`, `diagram-node-flow`.
  - `query "marker highlight paper"` -> `marker-draw-highlight`.

---

## 5. Productivity & Self-Improvement
*Ideal for: Time management, second brain systems, reading habits, discipline frameworks (Ali Abdaal style).*

* **Audience:** High-achieving knowledge workers, college students, founders.
* **Winning Hook Formula (0.0s - 3.0s):**
  - The System Revelation: *"I read 100 books a year without actually reading."* / *"The 2-minute rule that cured my ADHD paralysis."*
  - Synchronized visual: Clean desk aesthetic + paper-tear sticker popping on screen + soft typewriter click sound.
* **Visual Rhythm & Pacing:**
  - Cut Frequency: **2.0s - 2.8s**.
  - Rhythm: Warm desk to-camera talk → Minimal Notion/app window → Checklist tick-off animation → 3-step numbered card.
* **Layout & Composition Styles:**
  - `Style 45: Paper-Drawer / Sticky-Note Reveal`.
  - `Style 50: Numbered Card-List` (Items arrive one by one as spoken).
* **Color Palette & Mood:**
  - Theme: **Warm Linen & Minimalist Studio**.
  - Background: `#F8F6F2` (Warm Linen Light) or `#1F2022` (Soft Graphite Dark).
  - Accent Punch: Terracotta `#C85A32` or Forest Sage `#2E5A44`.
* **Typography Hierarchy:**
  - Primary Punch: `Fraunces Bold` or `Playfair Display (700)`.
  - Supporting Body: `Inter (500)`.
* **Catalog Component Queries:**
  - `query "checklist to-do task card"` -> `marker-checklist-card`.
  - `query "paper rip collage"` -> `torn-paper-rip`.

---

## 6. D2C, Fashion & E-Commerce Product Showcases
*Ideal for: Product unboxings, fashion hauls, gadget reviews, amazon finds.*

* **Audience:** Shoppers, lifestyle trend followers, Gen-Z / Millennials.
* **Winning Hook Formula (0.0s - 3.0s):**
  - Price-to-Value Shock: *"Everything in this luxury box was under ₹499."* / *"Never buy the Apple AirPods Max until you see this."*
  - Synchronized visual: Fast snap-scale pop on the product + price badge sticker + camera punch zoom + camera shutter SFX.
* **Visual Rhythm & Pacing:**
  - Cut Frequency: **1.2s - 1.8s** (ultra fast-paced, high retention).
  - Rhythm: Fast product try-on → Macro texture close-up → Price pill badge → Comparison wipe.
* **Layout & Composition Styles:**
  - `Style 01: Split-Screen` (Wearing item on left, price & specs card on right).
  - `Style 25: Scale-Pop Sticker` with rotating badge overlay.
* **Color Palette & Mood:**
  - Theme: **Commercial Warm Punch**.
  - Background: `#100E0D`, Accent Punch: Vibrant Gold `#FFD700` and Coral `#FF4D4D`.
* **Typography Hierarchy:**
  - Primary Punch: `Poppins Black (900)`, All-Caps, heavy text-stroke.
  - Accent: `Syne ExtraBold (800)`.
* **Catalog Component Queries:**
  - `query "product card feature showcase"` -> `mk-specs-list`, `feature-pill-card`.
  - `query "metric badge callout pill"` -> `stat-callout-counter`.
