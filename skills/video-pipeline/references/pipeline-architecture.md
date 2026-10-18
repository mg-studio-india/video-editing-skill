# Pipeline Execution Architecture & Style Rule Checklist

From the 225-style catalog appendix: how a chosen style flows through the skills, and the rules every builder and
reviewer enforces.


How the styles in this catalog are processed and rendered through the engine:

```mermaid
flowchart TD
    A["Raw Intake Footage & Transcript"] --> B["video-plan-storyboard (Gate 1)"]
    B -->|"Selects from 225 Styles Matrix"| C["plan.md & storyboard.plan.json"]
    C --> D["video-style (Gate 3: style.json)"]
    D --> E["video-take-geometry (Face Tracking & Mattes)"]
    D --> F["video-format (Layouts & Kit Blocks)"]
    D --> G["video-motion-graphics (GSAP Physics)"]
    D --> H["video-captions (Phoneme Sync & Styling)"]
    D --> I["video-audio (Mastering -14 LUFS & SFX)"]
    E & F & G & H & I --> J["HyperFrames Engine (Deterministic Build)"]
    J --> K["video-review-gate (Gate 5)"]
    K --> L["Final Delivered MP4"]
```

### Style Rule Checklist for Editors & Autonomous Agents:
1. **Never use the same treatment or visual device twice in a row**: Alternate between speaker framing, graphic cards, full-frame cutaways, and split screens.
2. **Respect the face**: Live-action speakers must never be covered by cards or headlines. Face sits anchored at ~38% canvas height in vertical reframing.
3. **Contrast floor**: Text and key assets must achieve a minimum 3:1 contrast ratio against underlying footage (enforce dark backing pills or text stroke).
4. **Phoneme-level lock**: All animated reveals, card lists, and caption highlights must align to speech phonemes within a ±40ms tolerance window.
5. **Acoustic priority**: Voice intelligibility always takes precedence. Background music must duck cleanly by 12-18dB during vocal activity.
