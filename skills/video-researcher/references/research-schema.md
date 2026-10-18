# Research Schema Specification (`research.json` & `research.md`)

This specification establishes the technical and creative contract for `video-researcher`. Every research pass must generate two synchronized output files in the project directory `$W`:
1. `$W/research.json`: Strict, machine-readable specification consumed by downstream agents (`video-plan-storyboard`, `video-style`, `video-format`, `video-motion-graphics`, and `video-pipeline`).
2. `$W/research.md`: Human-readable creative brief and intelligence summary that the creator can review in 2 minutes.

---

## 1. Machine-Readable Schema: `research.json`

> [!IMPORTANT]
> **Strict Anti-Hardcoding Contract**: All fields in `research.json` must be filled with real, verified findings discovered during the active session via web research or asset extraction. Placeholder links (`example.com`, fake YouTube/Instagram URLs) and arbitrary hardcoded color hexes are strictly forbidden. When a section is awaiting research, fields must be set to `null` or `[]`.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VideoResearchSpecification",
  "type": "object",
  "required": [
    "project_id",
    "timestamp",
    "category",
    "target_platform",
    "aspect_ratio",
    "topic_analysis",
    "entities_and_logos",
    "trending_benchmarks"
  ],
  "properties": {
    "project_id": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "category": {
      "type": "object",
      "required": ["primary_genre"],
      "properties": {
        "primary_genre": { "type": "string" },
        "niche": { "type": ["string", "null"] },
        "target_audience": { "type": ["string", "null"] },
        "tone": { "type": ["string", "null"] }
      }
    },
    "target_platform": { "type": "string", "enum": ["reels", "shorts", "tiktok", "youtube_longform"] },
    "aspect_ratio": { "type": "string", "enum": ["9:16", "16:9", "1:1", "4:5"] },
    "topic_analysis": {
      "type": "object",
      "required": ["summary", "core_claims", "verified_data_points", "key_takeaways"],
      "properties": {
        "summary": { "type": "string" },
        "core_claims": { "type": "array", "items": { "type": "string" } },
        "verified_data_points": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["claim", "verified_value", "source_url", "confidence"],
            "properties": {
              "claim": { "type": "string" },
              "verified_value": { "type": "string" },
              "source_url": { "type": ["string", "null"] },
              "confidence": { "type": "string", "enum": ["verified", "estimate", "unconfirmed"] }
            }
          }
        },
        "key_takeaways": { "type": "array", "items": { "type": "string" } }
      }
    },
    "entities_and_logos": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["entity_name", "slug", "status", "local_path", "format"],
        "properties": {
          "entity_name": { "type": "string" },
          "slug": { "type": "string" },
          "status": { "type": "string", "enum": ["resolved", "generated", "fallback", "missing"] },
          "local_path": { "type": "string", "example": "videos/my-project/assets/logos/google.svg" },
          "source_url": { "type": "string" },
          "format": { "type": "string", "enum": ["svg", "png"] },
          "brand_colors": {
            "type": "object",
            "properties": {
              "primary": { "type": "string", "example": "#4285F4" },
              "accent": { "type": "string", "example": "#34A853" },
              "dark_mode_optimized": { "type": "boolean" }
            }
          }
        }
      }
    },
    "trending_benchmarks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["title", "creator_channel", "url", "views", "hook_technique", "cut_pace_seconds", "why_it_worked"],
        "properties": {
          "title": { "type": "string" },
          "creator_channel": { "type": "string" },
          "url": { "type": "string" },
          "views": { "type": "string" },
          "hook_technique": { "type": "string" },
          "cut_pace_seconds": { "type": "number" },
          "why_it_worked": { "type": "string" },
          "visual_devices": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "recommended_format": {
      "type": ["object", "null"],
      "properties": {
        "layout_style_id": { "type": "string" },
        "layout_style_name": { "type": "string" },
        "canvas_framing": { "type": "string" },
        "target_cut_pace_sec": { "type": "number" },
        "hook_formula": { "type": "string" }
      }
    },
    "recommended_style": {
      "type": ["object", "null"],
      "properties": {
        "theme_preset": { "type": "string" },
        "palette": {
          "type": "object",
          "properties": {
            "background": { "type": "string", "example": "#090a0f" },
            "surface_glass": { "type": "string", "example": "rgba(16, 20, 28, 0.85)" },
            "text_primary": { "type": "string", "example": "#ffffff" },
            "accent_punch": { "type": "string", "example": "#00f0ff" },
            "accent_secondary": { "type": "string", "example": "#a6ff00" },
            "border_subtle": { "type": "string", "example": "rgba(0, 240, 255, 0.25)" }
          }
        },
        "typography": {
          "type": "object",
          "properties": {
            "primary_punch": { "type": "string", "example": "Poppins-Black (900)" },
            "accent_display": { "type": "string", "example": "Syne-ExtraBold (800)" },
            "body_support": { "type": "string", "example": "Inter-Bold (700)" },
            "stroke": { "type": "string", "example": "3px rgba(0,0,0,0.95)" }
          }
        },
        "motion_physics": {
          "type": "object",
          "properties": {
            "entrance_ease": { "type": "string", "example": "power3.out" },
            "pop_curve": { "type": "string", "example": "back.out(1.4)" },
            "damping": { "type": "number", "example": 14 },
            "stiffness": { "type": "number", "example": 180 },
            "tilt_angle_deg": { "type": "number", "example": -2.0 }
          }
        }
      }
    },
    "suggested_catalog_blocks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["catalog_query", "recommended_block", "beat_role"],
        "properties": {
          "catalog_query": { "type": "string" },
          "recommended_block": { "type": "string" },
          "beat_role": { "type": "string" }
        }
      }
    },
    "actionable_links": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["label", "url", "category"],
        "properties": {
          "label": { "type": "string" },
          "url": { "type": "string" },
          "category": { "type": "string", "enum": ["reference_video", "data_source", "asset", "documentation"] }
        }
      }
    }
  }
}
```

---

## 2. Human-Readable Specification: `research.md`

Every run must also write a clean, beautifully formatted `$W/research.md` file using this template:

```markdown
# Creative & Market Research Brief: <Project Name>

**Category:** <Category / Niche> · **Target Platform:** <Reels / Shorts / TikTok / YouTube> · **Aspect Ratio:** <9:16 / 16:9>
**Research Date:** <YYYY-MM-DD> · **Status:** Ready for Gate 0 Verification

---

## 1. Executive Topic Summary & Verified Data
<2-3 concise paragraphs breaking down the core concepts, talking points, and audience hook.>

### Verified Facts & Citations
- **<Claim 1>:** <Verified stat / number> — [Source Link](https://...)
- **<Claim 2>:** <Verified fact / date> — [Source Link](https://...)

---

## 2. Trending Category Benchmarks & Reference Videos
Top-performing reference videos in this specific niche demonstrating proven visual formats:

| Creator / Channel | Video Title & Link | Views | Cut Pace | Winning Hook / Technique |
|---|---|---|---|---|
| **<Creator 1>** | [<Title 1>](https://...) | 1.4M | 1.6s / cut | Pattern interrupt question + audio tape stop |
| **<Creator 2>** | [<Title 2>](https://...) | 820K | 2.1s / cut | High-contrast kinetic badge + proof UI demo |
| **<Creator 3>** | [<Title 3>](https://...) | 2.9M | 1.4s / cut | Layered-head 3D text behind subject |

### Key Creative Insights from Benchmarks:
1. **Hook Structure:** <What top performers do in 0-3s>
2. **Visual Rhythm:** <Visual change interval, B-roll density>
3. **Sound Design:** <SFX choices, whoosh/riser placement, music ducking>

---

## 3. Brand & Entity Assets (Resolved & Generated Logos)
All brands and tools identified in the transcript with vector assets saved to `$W/assets/logos/`:

| Entity | Status | Format | Brand Color | Local Asset Path | Source |
|---|---|---|---|---|---|
| **<Brand 1>** | Resolved | SVG | `#0066FF` | `assets/logos/<brand1>.svg` | [Official Link](https://...) |
| **<Brand 2>** | Resolved | SVG | `#FF4B4B` | `assets/logos/<brand2>.svg` | [Official Link](https://...) |
| **<Concept 3>** | Generated | SVG | `#10B981` | `assets/logos/<concept3>.svg` | HyperFrames Lockup |

---

## 4. Recommended Visual Layout & Master Style Direction
Directly mapped to the 225-Style Taxonomy in `video-plan-storyboard/references/style-catalog.md`:

- **Primary Layout:** **Style <ID>: <Style Name>** (e.g. *Style 03: Stacked Split-Screen*)
  - *Canvas Framing:* <Framing details>
  - *Cut Pace:* ~<X.X> seconds per visual beat
- **Color Theme:** **<Theme Preset>**
  - Background: `<Hex>` · Text: `<Hex>` · Punch Accent: `<Hex>` · Border: `<Hex>`
- **Typography:**
  - Punch Display: `<Font Family> <Weight>` (All-Caps, letter-spacing `<emometer>`)
  - Accent / Curiosity: `<Font Family> <Weight>`
  - Body & Support: `<Font Family> <Weight>`
- **Motion Physics:**
  - Entrance: `<ease>`, Damping: `<val>`, Stiffness: `<val>`, Tilt: `<deg>`

---

## 5. HyperFrames Catalog Action Plan
Pre-searched HyperFrames Registry components ready for installation:

| Beat Role | Catalog Search Query | Recommended Block ID | Visual Treatment |
|---|---|---|---|
| **Opening Hook Banner** | `lower third headline banner` | `lt-headline-banner` | Snappy high-contrast claim bar |
| **Product / Feature List** | `feature specs card list` | `mk-specs-list` | Staggered card entrance with icons |
| **Proof / Number Stat** | `stat counter callout pill` | `stat-callout-counter` | Count-up animated badge |
| **Hard Transition** | `flash transition white leak` | `flash-through-white` | 2-frame optical white flash |

---

## 6. Actionable Reference Links & Source Repository
- **Reference Reels & Competitors:**
  - [Link 1](https://...)
  - [Link 2](https://...)
- **Primary Data Sources & Articles:**
  - [Link 1](https://...)
  - [Link 2](https://...)
- **Brand Style Guides & Vector Assets:**
  - [Link 1](https://...)

---

### Creator Verification (Gate 0)
*Review the above research plan. Once approved, the pipeline advances to **Gate 1 (`video-plan-storyboard`)** where beats, cuts, and component choreography are locked.*
```
