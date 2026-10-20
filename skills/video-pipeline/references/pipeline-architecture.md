# Pipeline Execution Architecture & Style Rule Checklist

From the 225-style catalog appendix: how a chosen style flows through the skills, and the rules every builder and
reviewer enforces.


How the styles and presets are processed and rendered through the engine:

```mermaid
flowchart TD
    RAW["Raw Footage (HDR/HLG or SDR)"] --> STD["Standard Ingest (SDR Rec.709 H.265 @ 60fps)"]
    
    subgraph P1 ["Phase 1: Ingest, Parallel Analysis & Matching (~20s)"]
        STD --> WA["Audio Worker: 80Hz rumble cut + EBU R128 loudnorm + whisper.cpp ASR"]
        STD --> WV["Visual Worker: Probe 60fps + 4 Keyframes + Dynamic Frame Color Correction"]
        WA & WV --> VCA["video-cut-audit: Tight Paper Cut (paper-cut.py --tight)"]
        VCA --> VRM["video-reference-match: Rank top 3 presets from 50 creator blueprints (match.py)"]
    end
    
    subgraph P2 ["Phase 2: User Direction & Storyboard Gate"]
        VRM --> ASK{"ask_question (Gate Q)<br>Did user specify preferences in prompt?"}
        ASK -->|No| PROMPT["Prompt User: Select Preset, Multi-Layout & Proof Elements"]
        ASK -->|Yes| VPS
        PROMPT --> VPS["video-plan-storyboard (Gate S)<br>Generate STORYBOARD.md, grade-preview.jpg, Keyframes"]
        VPS --> GATE_S{"Gate S: User Review & Approval"}
    end
    
    subgraph P3 ["Phase 3: Assembly, Motion Scenes & Master Render (~50s)"]
        GATE_S -->|Approved| AC["apply-cut.py (Tight Cut + Dynamic Grade in Rec.709)"]
        AC --> P2T["Pass 2 Transcribe (Direct Word Sync on Conformed Cut)"]
        P2T --> STG["stage.py (take-geometry + motion-graphics + sound-design + captions)<br>- Studio Mesh Canvas (No Black Backgrounds)<br>- Squircle PiP / Rounded Top Card<br>- Active HyperFrames Motion Scenes<br>- Vibrant Single-Row Captions<br>- Subtle SFX (-20dB)"]
        STG --> RND["render.py & video-review-gate (60fps BT.709 Master, -14.4 LUFS, Programmatic QA)"]
        RND --> DELIV["Deliverable: processed/<project>-v1.mp4<br>(Temp folders preview/, hyperframes/, audio_processing/ preserved)"]
    end
```

### Style Rule Checklist for Editors & Autonomous Agents:
1. **Never use the same treatment or visual device twice in a row**: Alternate between speaker framing, graphic cards, full-frame cutaways, and split screens.
2. **Respect the face**: Live-action speakers must never be covered by cards or headlines. Face sits anchored at ~38% canvas height in vertical reframing.
3. **Contrast floor**: Text and key assets must achieve a minimum 3:1 contrast ratio against underlying footage (enforce dark backing pills or text stroke).
4. **Phoneme-level lock**: All animated reveals, card lists, and caption highlights must align to speech phonemes within a ±40ms tolerance window.
5. **Acoustic priority**: Voice intelligibility always takes precedence. Background music must duck cleanly by 12-18dB during vocal activity.
