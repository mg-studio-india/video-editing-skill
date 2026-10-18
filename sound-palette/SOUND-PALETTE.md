# Sound Palette & Dynamic Audio Craft

A production-grade acoustic palette and dynamic cutting framework located at `~/lmc/video-editing-skill/sound-palette`.

---

## 1. The Core Sound Philosophy: Silence Is the Baseline

Amateur videos cram non-stop whooshes, meme SFX, and intrusive background music onto every frame, creating acoustic fatigue. High-credibility business and creator breakdowns (e.g. Nitin Joshi, Markets with Jayant) adhere to a strict audio hierarchy:

```
[ 1. Dialogue / Voice ]   --> -14 LUFS | Warm, crisp, in-your-face presence (2.8k & 4.2k boost)
[ 2. Forensic Foley/SFX ] --> -3 dBFS Peak normalized | Mixed at 0.15 - 0.32 volume | Fills frequency notches
[ 3. Ambience / Bed ]     --> Ducked -16 dB to -19 dB under speech | Zero emotional exaggeration
```

1. **Voice is the focal hero:** Sound effects must never mask plosives or consonants (especially in rapid Hindi-English code-switching).
2. **SFX acts as an evidence stamp:** A sound only occurs when an on-screen element genuinely warrants acoustic physical feedback (a document sliding in, a mouse clicking an active input, or a bottom-line financial disclosure landing).
3. **Silence on standard cuts:** Standard jump cuts and phrase-by-phrase captions are **silent**. Reserving sound only for high-value beats increases their cognitive punch.

---

## 2. Dynamic Cut Padding (Per Style & Delivery Cadence)

> **Core Principle**: Cut padding is **never static**. Applying a fixed 100ms padding everywhere either makes rapid-fire hooks sluggish or chops the breath and resonance off serious, thoughtful disclosures. 
> 
> Cut padding dynamically adapts based on **Words Per Minute (WPM)**, **phonetic onset type**, and **narrative tension**.

### Dynamic Padding Matrix

| Narrative State / Style | Target WPM | Lead-In Padding | Trailing Tail | Crossfade | Narrative Intent |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Aggressive Hook** *(0-3s)* | 180+ | **35ms - 50ms** | **60ms - 80ms** | 8ms | Staccato, breathless curiosity tease. Zero dead time between sentences. |
| **Investigative Teardown** | 140-180 | **65ms - 85ms** | **95ms - 120ms** | 12ms | Forensic, data-first cadence (Nitin Joshi style). Preserves consonants ('P', 'T', 'K') without hesitation. |
| **Conversational Authority** | 110-140 | **100ms - 130ms** | **140ms - 175ms** | 15ms | Founder reflections and nuanced arguments. Retains natural natural breath and room tone decay. |
| **Dramatic Verdict / Pause** | Any | **80ms - 100ms** | **250ms - 350ms** | 20ms | Post-revelation silence. Lets the audience digest a shocking financial figure or lab result. |

### Acoustic Safety Guardrails
* **Vowel & Consonant Attack Protection:** Voiced stops (*b, d, g*) and voiceless stops (*p, t, k*) have an acoustic burst phase lasting 15-35ms. Snapping a cut exactly to the speech detection threshold clips this burst, making speech sound muffled or distorted.
* **Micro-Crossfades:** Every single audio cut slice MUST have a **10ms - 15ms linear crossfade** to avoid digital DC-offset clicks and pops at transition boundaries.

---

## 3. Curated Sound Palette Assets

All files in `./audio/` are pre-trimmed (leading silence stripped so the transient peak lands on frame 0) and peak-normalized to **-3.0 dBFS**.

| ID | File | Category | Mix Volume | Frequency Profile | Primary Trigger |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `click_soft` | [`click-soft.mp3`](./audio/click-soft.mp3) | UI Micro | `0.22` | High (3.5k-7k Hz) | Subtle toggle, card swipe, bullet check |
| `click_hard` | [`click-hard.mp3`](./audio/click-hard.mp3) | UI Micro | `0.28` | Mid-High (2.8k-6.5k Hz) | Active mouse cursor click on link/button |
| `pop_card` | [`pop.mp3`](./audio/pop.mp3) | Kinetic Pop | `0.32` | Mid (600-2.4k Hz) | Card entrance, badge pill, sticker pop |
| `impact_sub_drop` | [`impact-sub-drop.mp3`](./audio/impact-sub-drop.mp3) | Impact | `0.24` | Sub-Bass (40-120 Hz) | Core controversy reveal, shocking allegation |
| `impact_heavy` | [`impact-heavy.mp3`](./audio/impact-heavy.mp3) | Impact | `0.26` | Low-Mid (80-350 Hz) | Final verdict, conclusive bottom-line stat |
| `whoosh_fast` | [`whoosh-fast.mp3`](./audio/whoosh-fast.mp3) | Transition | `0.18` | Broad (800-4.5k Hz) | Swift lateral wipe, snap zoom reframe |
| `whoosh_cinematic` | [`whoosh-cinematic.mp3`](./audio/whoosh-cinematic.mp3) | Transition | `0.15` | Full spectrum | Major act shift (e.g. from problem to expose) |
| `riser_tension` | [`riser-tension.mp3`](./audio/riser-tension.mp3) | Riser | `0.14` | Rising (300-8k Hz) | Tension build leading into evidence proof |
| `ping_metric` | [`ping-metric.mp3`](./audio/ping-metric.mp3) | Indicator | `0.18` | High (2.2k-5.5k Hz) | Financial stat landing (₹/$/%), percentages |
| `chime_reveal` | [`chime-reveal.mp3`](./audio/chime-reveal.mp3) | Indicator | `0.16` | Mid-High (1.2k-4.8k Hz) | Key insight, solution, verified truth |
| `paper_slide` | [`paper-slide.mp3`](./audio/paper-slide.mp3) | Foley | `0.24` | Organic (1.5k-3.8k Hz) | Document slide, report entry, invoice |
| `paper_thud` | [`paper-thud.mp3`](./audio/paper-thud.mp3) | Foley | `0.28` | Low-Mid (90-500 Hz) | Evidence landing on desk, official filing |
| `camera_shutter` | [`camera-shutter.mp3`](./audio/camera-shutter.mp3) | Foley | `0.20` | High (2.5k-6k Hz) | Screenshot freeze, proof capture snapshot |
| `error_buzzer` | [`error-buzzer.mp3`](./audio/error-buzzer.mp3) | Indicator | `0.22` | Mid (400-1.2k Hz) | Debunked claim, failed test result flag |
| `glitch_digital` | [`glitch-digital.mp3`](./audio/glitch-digital.mp3) | Texture | `0.16` | High (1.8k-9k Hz) | Exposing PR illusion vs reality |
| `typing_tactile` | [`typing-tactile.mp3`](./audio/typing-tactile.mp3) | Foley | `0.18` | Tactile (2k-5k Hz) | Search bar input, code entry |
| `key_tap` | [`key-tap.mp3`](./audio/key-tap.mp3) | Foley | `0.22` | Tactile (1.8k-4.5k Hz) | Single Enter/Return key press |
| `notification_chime`| [`notification-chime.mp3`](./audio/notification-chime.mp3) | UI Micro | `0.18` | High (2k-6k Hz) | Chat bubble entry, message alert |
| `shimmer_accent` | [`shimmer-accent.mp3`](./audio/shimmer-accent.mp3) | Indicator | `0.14` | Ultra-High (4k-12k Hz) | Gold standard rule, premium highlight |

---

## 4. How to Anchor Sounds in Video Projects

In your `storyboard.plan.json` or timeline definition, anchor sound cues directly to spoken phrases:

```json
{
  "sfx": [
    {
      "id": "reveal_paper",
      "sound": "paper_slide",
      "at": "@lab report",
      "volume": 0.24
    },
    {
      "id": "drop_verdict",
      "sound": "impact_sub_drop",
      "at": "@SPF 15",
      "volume": 0.26
    },
    {
      "id": "revenue_metric",
      "sound": "ping_metric",
      "at": "@500 Crore",
      "volume": 0.18
    }
  ]
}
```

The composition audio engine resolves these IDs directly to `./audio/<file>` and guarantees sample-accurate sync on the cue's acoustic onset.
