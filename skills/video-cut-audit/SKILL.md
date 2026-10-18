---
name: video-cut-audit
description: Executes frame-accurate, story-driven cuts anchored to the approved storyboard. Eliminates stutters, false starts, and background speech while protecting word boundaries with acoustic safety padding. Owns Gate 4.
---

# Cut Audit (Precision Story-Driven Editing)

> **Styles:** Editing pace & rhythm styles #173-187 of the 225-style catalog: `references/styles-pace-rhythm.md`.

A bad cut ruins good footage. The cut must be **anchored to the narrative storyboard approved at Gate 3**, maintaining narrative flow, eliminating dead air, and ensuring zero clipped syllables.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## 1. Dynamic Cutting & Pacing Rules

1. **Dynamic Style-Aware Cut Padding:**
   - Cut padding is **dynamic per video style, tempo (WPM), and narrative tension**, rather than fixed static offsets:
     - **Aggressive Hook / Fast-Paced Reel (180+ WPM):** `35ms - 50ms` lead-in, `60ms - 80ms` trailing tail. Eliminates conversational drag while preserving punch.
     - **Investigative Teardown / Forensic Breakdown (140-180 WPM):** `65ms - 85ms` lead-in, `95ms - 120ms` trailing tail. Balances fast information density with crystal-clear consonant articulation.
     - **Conversational Authority / Interview (110-140 WPM):** `100ms - 130ms` lead-in, `140ms - 175ms` trailing tail. Preserves natural breathing cadence and acoustic room resonance.
     - **Dramatic Verdict / Pause:** `80ms - 100ms` lead-in, `250ms - 350ms` trailing tail. Gives punchlines or shocking revelations room to breathe.
   - Never snap a cut directly to the speech detection threshold: doing so chops the initial acoustic burst of consonants (like 'P', 'T', 'K') and clips word endings.
2. **Audio Micro-Fades:**
   - Apply an **8ms - 15ms linear audio crossfade** at every edit boundary to eliminate digital clicks and DC-offset pops.
3. **Keep the Best Take (Retake Logic):**
   - When a creator repeats a sentence or phrase, keep the **last clean, confident take**, discarding false starts and stumbles.
4. **Dialogue vs. Non-Speaking Action:**
   - If footage contains visual actions (try-ons, demonstrations, reactions), cut each action at a natural motion inflection point (e.g. at the apex of a turn or smile).
   - Strip all ambient room chatter and non-creator speech during visual b-roll/cutaway shots.

---

## 2. Gate 2: Interactive Cut Review

Before applying the permanent cut or encoding video:
1. Generate `PAPER-CUT.md` listing:
   - Total original duration vs. proposed cut duration.
   - Exact timestamps of kept segments.
   - Clean transcript of what the cut video will actually say.
   - Non-speaking action segments identified for B-roll or try-ons.
2. Present `PAPER-CUT.md` to the user:
   > *"Here is the exact cut map. Intro dialogue: 0.0s - 19.1s. Dress 1 try-on: 6.0s. Dress 2 try-on: 6.0s. Dress 3 try-on: 6.0s. Outro: 1.4s. Total duration: 38.5s. Does this pacing work for you?"*
3. Apply the cut only after user approval.
