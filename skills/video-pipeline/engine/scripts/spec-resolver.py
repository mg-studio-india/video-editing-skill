#!/usr/bin/env python3
"""spec-resolver.py: Context-driven creative dimension extractor and missing-step resolver."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runtime  # noqa: E402
runtime.ensure_project_venv()
import memo  # noqa: E402


# -----------------------------------------------------------------------------
# Master Data Catalogs (Up to 10 Curated Items Per Dimension)
# -----------------------------------------------------------------------------

MASTER_DIMENSIONS = {
    "format_layout": {
        "name": "Format & Multi-Layout Dynamism",
        "description": "Aspect ratio and dynamic A-roll choreography across narrative beats",
        "options": {
            "multi-dynamic": "Choreographed Multi-Layout (Hook full -> Corner PiP / Split View -> Cutout -> Outro)",
            "split-screen": "40/60 Split View (Presenter left/top + 60% dedicated visual data/article canvas)",
            "corner-pip": "Corner PiP Minimization (Presenter in ~30% squircle floating window, open canvas)",
            "speaker-cutout": "Speaker Matte Cutout (Presenter silhouette extracted over dark/gradient canvas)",
            "stacked-split": "Stacked 9:16 Layout (Presenter top 40% + terminal/demo graphics bottom 60%)",
            "screen-plus-facecam": "Screen-Plus-Facecam (75% desktop screen recording + presenter sidebar/dock)",
            "layered-head": "Layered-Head 3D Depth (Speaker cutout with kinetic text/numbers behind the head)",
            "side-by-side": "Side-by-Side Comparison (Dual 50/50 columns benchmarking options with category badges)",
            "facecam-bubble": "Floating Facecam Bubble (280px circular speaker bubble floating over main screen)",
            "full-camera": "Full Camera A-roll (Full-screen talking head with dynamic camera punch-ins)",
        },
    },
    "sounds_audio_bed": {
        "name": "Sounds, SFX & Music Bed",
        "description": "Acoustic punctuation (tactile clicks, whooshes, paper tears) and background music bed",
        "options": {
            "tactile-creator": "Curated Tactile SFX (Tactile whooshes on cuts, paper tears on articles, clicks on data, pops on punches)",
            "upbeat-lofi": "Upbeat Lofi Music Bed (-18dB ducked under dialogue, 85-95 BPM chillhop groove)",
            "corporate-modern-synth": "Modern Tech / Corporate Synth Bed (-18dB ducked under dialogue, 110-120 BPM driving pulse)",
            "ambient-documentary": "Ambient Documentary Bed (Minimalist sub-bass and warm organic acoustic pads)",
            "dramatic-cinematic": "Dramatic Cinematic Bed (Risers, tension pulses, and orchestral impacts)",
            "tech-minimal-electronic": "Minimal Tech Electronic (Crisp glitch accents, subtle sub-bass, clean clicks)",
            "hiphop-boom-bap": "Punchy Boom-Bap Groove (Head-nodding drums, vinyl crackle, active rhythm)",
            "acoustic-warm-folk": "Acoustic Warm Guitar (Organic fingerpicked guitar bed, friendly and authentic)",
            "dark-investigative": "Dark Investigative Drone (Deep minor drones, ticking clocks, forensic tension)",
            "dialogue-only-minimal": "Minimal SFX & Dialogue Only (No music bed, tactile micro-clicks on visuals)",
        },
    },
    "caption_style": {
        "name": "Caption Styling & Typography",
        "description": "Kinetic caption animation, typographical hierarchy, and punch highlighting",
        "options": {
            "weight-shift": "Weight-Shift Kinetic (Font weight shifts dynamically from 400 to Black 900 on active word with punch scale-pop)",
            "caption-highlight": "Caption-Highlight Fluid (Fluid fluorescent highlight sweep across phrase with badge punch words)",
            "badged-pill": "Badged Punch Pills (Keywords encased in vibrant high-contrast rounded pills)",
            "layered-head": "Big Background Figures & Layered Head (Large typographic figures & hero text in backdrop behind speaker)",
            "focus-blur-resolve": "Focus-Blur-Resolve (Active word in sharp focus, inactive blurred 3px, punch words in badge pills)",
            "punch-word": "Punch Word Scale-Pop (Natural conversational phrase with 0.90->1.06->1.00 keyword pop)",
            "karaoke-glow": "Fluid Karaoke Glow (Full phrase anchored with progressive color wipe and soft neon glow)",
            "dual-font-editorial": "Editorial Dual-Font (Grotesque sans body paired with expressive display serif on punch words)",
            "minimal-underline": "Clean Minimalist (Heavy sans with animated accent underline tracking keyword)",
            "kinetic-slam": "Kinetic Slam (High-impact keyword slam with camera shake and physical momentum)",
        },
    },
    "color_grading": {
        "name": "Color Grading Preset & Tone Formula",
        "description": "Cinema 3-way color grading profile and tone curve from grade.py",
        "options": {
            "kodak-portra-warm": "Kodak Portra Warm (Golden skin tones, soft highlight rolloff, lifted film blacks, organic S-curve)",
            "hollywood-teal-orange": "Hollywood Teal & Orange (Teal shadow split, warm amber midtones/highlights, punchy cinema contrast)",
            "vox-documentary": "Vox Documentary (Deep true blacks, crisp micro-clarity, 5600K neutral daylight, high contrast)",
            "magnates-gold": "Magnates Gold (Luxury wealth breakdown, amber-gold midtone bias, rich contrast with deep true blacks)",
            "fuji-pro-cinematic": "Fuji Pro Cinematic (Fuji Eterna pastel tones, emerald shadow nuance, natural documentary skin)",
            "modern-tech": "Modern Tech (Clean 5800K daylight, deep blacks, high clarity, vivid saturated tech accents)",
            "moody-film": "Moody Film (Analog 35mm print curve, softened highlights, lifted deep blacks, warm shadows, fine grain)",
            "vibrant-pop": "Vibrant Pop (High-energy social feed look, rich color saturation, dynamic contrast punch, warm skin tones)",
            "nordic-cold": "Nordic Cold (Desaturated Scandinavian drama look, cool blue shadows, muted mids, soft silvery highlights)",
            "studio-clean-balanced": "Studio Clean Balanced (Precision Rec.709 balanced studio correction, phone sensor cast removal)",
        },
    },
    "graphics_elements": {
        "name": "Motion Graphics & Visual Elements",
        "description": "Visual treatments and registry blocks occupying the empty canvas space",
        "options": {
            "researcher-articles": "Researcher Article Clippings (Journal/newspaper tear-out with animated fluorescent highlighter pen)",
            "kinetic-data-charts": "Kinetic Data Charts (Animated bar charts scaleY: 0->1, growth curves, metric counters)",
            "3d-isometric-cards": "3D Isometric Depth Cards (Tilted mockup cards perspective 1000px with soft ambient shadow)",
            "social-proof-mockups": "Social Proof & Post Mockups (Tweet cards, verified creator profiles, Reddit comment pop)",
            "specs-feature-drawer": "Specs & Feature Cards (Lower-third staggered cards with spring overshoot)",
            "map-route-travel": "Animated Route & Pin Map (Geo zoom-in, glowing path connection, location callout)",
            "code-terminal-window": "Interactive Code Terminal (Typing syntax highlighter with macOS window chrome)",
            "device-browser-scroll": "Framed Browser Scroll (Smooth seek-safe webpage scroll with cursor clicks)",
            "stat-counter-pop": "Live Metric Counter (Spring-pop counter ticking from 0 to final statistic claim)",
            "split-divider-badge": "Accent Divider & Topic Badges (Glowing vertical divider line with category badge)",
        },
    },
    "audio_processing": {
        "name": "Audio Processing & Noise Filtering",
        "description": "Noise suppression model and dialogue clarity processing from audio-chain.py",
        "options": {
            "neural-heavy": "Neural DeepFilterNet3 Heavy (Surgical suppression for heavy road, car, traffic rumble, engine noise)",
            "neural-indoor": "Neural DeepFilterNet3 / RNNoise Indoor (Active suppression for indoor AC hum, room reverb, fan noise, reflections)",
            "auto-adaptive": "Adaptive Auto (Measures SNR & room noise profile and applies calibrated filtering)",
            "dereverb-wpe": "WPE Neural Dereverberation (Suppresses harsh room echo and hollow acoustics)",
            "transparent-eq-gate": "Transparent Highpass & Gate (80Hz rumble cut + gentle transparent noise gate)",
            "multiband-deess": "Surgical Multiband De-Esser (Tames harsh sibilance 5-8 kHz while preserving air)",
            "broadcast-leveler": "Broadcast Master Leveler (EBU R128 target -14.0 LUFS with -1.0 dBTP ceiling)",
            "studio-clean-off": "Off / Studio Clean (No suppression filter applied, pristine studio acoustics)",
        },
    },
}


# -----------------------------------------------------------------------------
# Context-Driven Detection Engine
# -----------------------------------------------------------------------------

def detect_video_context(
    prompt: str = "",
    transcript_text: str = "",
    metadata: dict | None = None
) -> dict:
    combined = f"{prompt} {transcript_text}".lower()
    meta = metadata or {}

    context: dict[str, str] = {
        "genre": "creator-explainer",
        "pace": "medium",
        "primary_asset_type": "talking-head",
        "recommended_format": "multi-dynamic",
        "recommended_caption": "weight-shift",
        "recommended_grade": "kodak-portra-warm",
        "recommended_audio": "neural-heavy" if re.search(r"\b(road|car|traffic|vehicle|engine|street|outdoor)\b", combined) else "neural-indoor",
    }

    # 1. Format Detection based on Context
    if re.search(r"\b(code|terminal|developer|ide|software|github|api|programming|screen demo|screencast|browser|walkthrough)\b", combined):
        context["genre"] = "technical-walkthrough"
        context["recommended_format"] = "screen-plus-facecam"
        context["recommended_grade"] = "modern-tech"
        context["recommended_caption"] = "caption-highlight"
    elif re.search(r"\b(finance|revenue|report|market|stocks|investigative|teardown|forensic|newspaper|article|journal|data)\b", combined):
        context["genre"] = "investigative-teardown"
        context["recommended_format"] = "split-screen"
        context["recommended_grade"] = "vox-documentary"
        context["recommended_caption"] = "weight-shift"
    elif re.search(r"\b(unboxing|product launch|device|hardware|gadget|physical demo)\b", combined):
        context["genre"] = "product-showcase"
        context["recommended_format"] = "corner-pip"
        context["recommended_grade"] = "commercial-clean"
    elif re.search(r"\b(wealth|billionaire|luxury|magnates|business empire|monopoly)\b", combined):
        context["genre"] = "business-empire"
        context["recommended_format"] = "layered-head"
        context["recommended_grade"] = "magnates-gold"
        context["recommended_caption"] = "weight-shift"
    elif re.search(r"\b(reaction|reacting|reviewing|duet|commentary on)\b", combined):
        context["genre"] = "reaction-commentary"
        context["recommended_format"] = "stacked-split"
    elif re.search(r"\b(comparison|versus|vs|head to head|shootout|better than)\b", combined):
        context["genre"] = "comparison-benchmark"
        context["recommended_format"] = "side-by-side"
    elif re.search(r"\b(fast|viral|hook|retention|story|storytelling|reel|tiktok|short)\b", combined):
        context["genre"] = "high-retention-reel"
        context["recommended_format"] = "multi-dynamic"
        context["recommended_caption"] = "caption-highlight"
    elif re.search(r"\b(keynote|lecture|monologue|speech|presentation)\b", combined):
        context["genre"] = "keynote-speech"
        context["recommended_format"] = "full-camera"

    # 2. Caption Pacing & Backdrops
    # If user hasn't mentioned big figures in the background or large text, default is weight-shift or highlight with punch words
    if re.search(r"\b(big figure|big figures|large text|text behind|backdrop text|behind speaker|layered head)\b", combined):
        context["recommended_caption"] = "layered-head"
    else:
        wpm = meta.get("wpm", 145)
        if wpm >= 170 or re.search(r"\b(rapid|fast|energetic|intense)\b", combined):
            context["pace"] = "fast"
            context["recommended_caption"] = "caption-highlight"
        else:
            context["recommended_caption"] = "weight-shift"

    return context


# -----------------------------------------------------------------------------
# Extraction Engine
# -----------------------------------------------------------------------------

def extract_prompt_specs(prompt: str) -> dict[str, dict]:
    p = prompt.lower()
    extracted: dict[str, dict] = {}

    # 1. Format / Multi-Layout Dynamism
    layout_matches = []
    if re.search(r"\b(multi[- ]?dynamic|dynamic layout|multi[- ]?layout|vox style|magnates)\b", p):
        layout_matches.append(("multi-dynamic", "Multi-layout dynamism (Hook full -> PiP/Split -> Cutout)"))
    elif re.search(r"\b(split[- ]?screen|split view|split|40/60 split)\b", p):
        layout_matches.append(("split-screen", "Split-screen / 40-60 partitioned view"))
    elif re.search(r"\b(corner[- ]?pip|pip|picture[- ]in[- ]picture|floating (window|squircle)|minimi[zs]e( to corner)?)\b", p):
        layout_matches.append(("corner-pip", "Corner PiP minimization"))
    elif re.search(r"\b(speaker[- ]?cutout|cutout|matte|silhouette|background removal|transparent bg)\b", p):
        layout_matches.append(("speaker-cutout", "Speaker cutout / alpha matte over canvas"))
    elif re.search(r"\b(screen[- ]plus[- ]facecam|screen demo|screencast|browser layout)\b", p):
        layout_matches.append(("screen-plus-facecam", "Screen-plus-facecam desktop recording"))
    elif re.search(r"\b(layered[- ]head|3d depth|text behind head)\b", p):
        layout_matches.append(("layered-head", "Layered-head 3D depth cutout"))
    elif re.search(r"\b(side[- ]by[- ]side|comparison layout|vs layout)\b", p):
        layout_matches.append(("side-by-side", "Side-by-side comparison layout"))
    elif re.search(r"\b(facecam[- ]bubble|bubble camera|circular camera)\b", p):
        layout_matches.append(("facecam-bubble", "Floating facecam bubble"))
    elif re.search(r"\b(stacked[- ]?split|stacked|top bottom)\b", p):
        layout_matches.append(("stacked-split", "Stacked split layout"))
    elif re.search(r"\b(full[- ]?camera|full[- ]?screen|talking head only)\b", p):
        layout_matches.append(("full-camera", "Full camera talking head"))

    aspect_match = ""
    if re.search(r"\b(9:16|vertical|reel|reels|short|shorts|tiktok)\b", p):
        aspect_match = "9:16 Vertical"
    elif re.search(r"\b(16:9|landscape|horizontal|youtube long)\b", p):
        aspect_match = "16:9 Landscape"
    elif re.search(r"\b(1:1|square)\b", p):
        aspect_match = "1:1 Square"
    elif re.search(r"\b(4:5|social portrait)\b", p):
        aspect_match = "4:5 Portrait"

    res_match = ""
    if re.search(r"\b(uhd|4k|ultra[- ]?hd|2160p|2160x3840|3840x2160)\b", p):
        res_match = "UHD 4K"
    elif re.search(r"\b(1080p|fhd|full[- ]?hd|standard res(olution)?)\b", p):
        res_match = "1080p"

    if layout_matches or aspect_match or res_match:
        key = layout_matches[0][0] if layout_matches else "multi-dynamic"
        desc = layout_matches[0][1] if layout_matches else "Standard layout"
        if aspect_match:
            desc = f"{aspect_match} ({desc})"
        if res_match:
            desc = f"{desc} [{res_match}]"
        extracted["format_layout"] = {"key": key, "raw": desc}

    # 2. Sounds, SFX & Music Bed
    sfx_matches = []
    if re.search(r"\b(tactile|whoosh|whooshes|sound effect|sound effects|sfx|paper tear|paper slide|sub[- ]?bass|camera shutter|sound design|audio cues?)\b|\b(click|clicks|pop|pops)\s+(sound|sfx|effect|cue|on cuts|on punches)\b", p):
        sfx_matches.append("Tactile SFX cues")
    if re.search(r"\b(lofi|lo-fi|chillhop)\b", p):
        sfx_matches.append("Upbeat Lofi bed")
    elif re.search(r"\b(synth|electronic|tech music|corporate synth)\b", p):
        sfx_matches.append("Corporate Modern Synth bed")
    elif re.search(r"\b(ambient|documentary|minimal bed)\b", p):
        sfx_matches.append("Ambient Documentary bed")
    elif re.search(r"\b(cinematic|dramatic|orchestral|epic)\b", p):
        sfx_matches.append("Dramatic Cinematic bed")
    elif re.search(r"\b(no music|dialogue only|without music|silent bed)\b", p):
        sfx_matches.append("Dialogue only (no music)")

    if sfx_matches:
        extracted["sounds_audio_bed"] = {
            "key": "tactile-creator" if "Tactile SFX cues" in sfx_matches else "upbeat-lofi",
            "raw": ", ".join(sfx_matches)
        }

    # 3. Caption Styling & Typography (Must be explicitly specified or asked from user)
    cap_matches = []
    if re.search(r"\b(big figure|big figures|large text|text behind|backdrop text|behind speaker|layered head)\b", p):
        cap_matches.append(("layered-head", "Big background figures & layered text behind speaker"))
    elif re.search(r"\b(weight[- ]?shift|font weight shift|kinetic weight)\b", p):
        cap_matches.append(("weight-shift", "Weight-shift kinetic with punch words"))
    elif re.search(r"\b(caption[- ]?highlight|highlight caption|fluid highlight)\b", p):
        cap_matches.append(("caption-highlight", "Caption-highlight fluid sweep with punch words"))
    elif re.search(r"\b(badged?[- ]?pill|badge pill|pill badge)\b", p):
        cap_matches.append(("badged-pill", "Badged punch pills"))
    elif re.search(r"\b(focus[- ]?blur|focus blur|focus[- ]?blur[- ]?resolve)\b", p):
        cap_matches.append(("focus-blur-resolve", "Focus-blur-resolve with punch words"))
    elif re.search(r"\b(punch[- ]?word|scale[- ]?pop|pop word)\b", p):
        cap_matches.append(("punch-word", "Punch-word scale pop"))
    elif re.search(r"\b(karaoke|fluid wipe|word wipe)\b", p):
        cap_matches.append(("karaoke-glow", "Fluid karaoke wipe"))
    elif re.search(r"\b(editorial[- ]?dual|dual[- ]?font|grotesque and serif)\b", p):
        cap_matches.append(("dual-font-editorial", "Editorial dual-font grotesque/serif"))
    elif re.search(r"\b(minimal[- ]?underline|accent underline)\b", p):
        cap_matches.append(("minimal-underline", "Clean minimalist with accent underline"))
    elif re.search(r"\b(kinetic[- ]?slam|slam caption)\b", p):
        cap_matches.append(("kinetic-slam", "Kinetic slam keywords"))
    # NOTE: Generic words like 'captions' or 'subtitles' without style do NOT match here, ensuring the user is explicitly asked!

    if re.search(r"\b(poppins|anton|inter|syne|montserrat)\b", p):
        font = re.findall(r"\b(poppins|anton|inter|syne|montserrat)\b", p)[0].capitalize()
        if cap_matches:
            k, d = cap_matches[0]
            cap_matches[0] = (k, f"{d} [{font}]")
        else:
            cap_matches.append(("weight-shift", f"Weight-shift captions [{font}]"))

    if cap_matches:
        extracted["caption_style"] = {"key": cap_matches[0][0], "raw": cap_matches[0][1]}

    # 4. Color Grading Preset
    grade_matches = []
    if re.search(r"\b(kodak[- ]?portra|portra|warm grade|golden skin)\b", p):
        grade_matches.append(("kodak-portra-warm", "Kodak Portra Warm preset"))
    elif re.search(r"\b(teal[- ]?orange|hollywood|blockbuster)\b", p):
        grade_matches.append(("hollywood-teal-orange", "Hollywood Teal & Orange preset"))
    elif re.search(r"\b(vox[- ]?documentary|vox grade|investigative grade)\b", p):
        grade_matches.append(("vox-documentary", "Vox Documentary preset"))
    elif re.search(r"\b(magnates[- ]?gold|luxury grade|gold grade)\b", p):
        grade_matches.append(("magnates-gold", "Magnates Gold preset"))
    elif re.search(r"\b(fuji[- ]?pro|fuji eterna|eterna|pastel grade)\b", p):
        grade_matches.append(("fuji-pro-cinematic", "Fuji Pro Cinematic preset"))
    elif re.search(r"\b(modern[- ]?tech|modern tech|cool grade|tech grade)\b", p):
        grade_matches.append(("modern-tech", "Modern Tech preset"))
    elif re.search(r"\b(moody[- ]?film|moody film|film look|analog film|grain)\b", p):
        grade_matches.append(("moody-film", "Moody Film preset"))
    elif re.search(r"\b(vibrant[- ]?pop|vibrant pop|vibrant|pop colors)\b", p):
        grade_matches.append(("vibrant-pop", "Vibrant Pop preset"))
    elif re.search(r"\b(nordic[- ]?cold|nordic|cyan shadows)\b", p):
        grade_matches.append(("nordic-cold", "Nordic Cold preset"))
    elif re.search(r"\b(studio[- ]?clean|neutral correct|rec709|commercial clean)\b", p):
        grade_matches.append(("studio-clean-balanced", "Studio Clean Balanced preset"))
    elif re.search(r"\b(color grad(e|ing)|grading)\b", p):
        grade_matches.append(("kodak-portra-warm", "Cinematic color grade"))

    if grade_matches:
        extracted["color_grading"] = {"key": grade_matches[0][0], "raw": grade_matches[0][1]}

    # 5. Motion Graphics & Visual Elements
    gfx_matches = []
    if re.search(r"\b(article|newspaper|journal|headline|highlight|highlighter pen|paper rip|clipping)\b", p):
        gfx_matches.append(("researcher-articles", "Researcher article clippings & highlighter sweeps"))
    elif re.search(r"\b(chart|charts|graph|graphs|bar chart|growth curve|metrics? counter|data viz)\b", p):
        gfx_matches.append(("kinetic-data-charts", "Kinetic data charts & growth curves"))
    elif re.search(r"\b(3d|isometric|depth card|mockup|floating card)\b", p):
        gfx_matches.append(("3d-isometric-cards", "3D isometric depth cards & mockups"))
    elif re.search(r"\b(tweet|tweet card|reddit|social proof|verified badge|social card)\b", p):
        gfx_matches.append(("social-proof-mockups", "Social proof & post mockups"))
    elif re.search(r"\b(specs|feature card|feature drawer|lower third|motion graphics?|kinetic elements?)\b", p):
        gfx_matches.append(("specs-feature-drawer", "Kinetic specs & feature cards"))
    elif re.search(r"\b(map|route|pin|travel route)\b", p):
        gfx_matches.append(("map-route-travel", "Animated route map & location pin"))
    elif re.search(r"\b(terminal|code window|typing code)\b", p):
        gfx_matches.append(("code-terminal-window", "Interactive code terminal window"))

    if gfx_matches:
        extracted["graphics_elements"] = {"key": gfx_matches[0][0], "raw": gfx_matches[0][1]}

    # 6. Audio Processing & Noise Filtering (Active denoise for both indoor and outdoor)
    audio_matches = []
    if re.search(r"\b(road|car|traffic|vehicle|engine|street|outdoor)\b", p):
        audio_matches.append(("neural-heavy", "Neural DeepFilterNet3 (Heavy road/traffic rumble)"))
    elif re.search(r"\b(indoor|ac hum|fan noise|air condition(er|ing)|room reverb|echo|reflections?)\b", p):
        audio_matches.append(("neural-indoor", "Neural DeepFilterNet3 (Indoor AC/fan/reverb denoise)"))
    elif re.search(r"\b(deep[- ]?filter|neural denoise|neural suppression|heavy noise)\b", p):
        audio_matches.append(("neural-heavy", "Neural DeepFilterNet3 suppression"))
    elif re.search(r"\b(rnnoise|background voice|chatter|room noise)\b", p):
        audio_matches.append(("rnnoise-standard", "RNNoise standard neural denoiser"))
    elif re.search(r"\b(dereverb|room echo|echo removal)\b", p):
        audio_matches.append(("dereverb-wpe", "WPE Neural Dereverberation"))
    elif re.search(r"\b(denoise|filter noise|noise filter|noise suppression|clean audio)\b", p):
        audio_matches.append(("auto-adaptive", "Adaptive audio noise filtering"))
    elif re.search(r"\b(studio clean|no filter|raw audio|no denoise)\b", p):
        audio_matches.append(("studio-clean-off", "Off / Studio clean acoustics"))

    if audio_matches:
        extracted["audio_processing"] = {"key": audio_matches[0][0], "raw": audio_matches[0][1]}

    return extracted


def audit_specifications(
    prompt: str,
    memo_path: Path | str | None = None,
    transcript_text: str = "",
    metadata: dict | None = None
) -> dict:
    extracted = extract_prompt_specs(prompt)
    context = detect_video_context(prompt, transcript_text, metadata)
    brand_memo = memo.parse_memo(memo_path) if memo_path else {}

    audit: dict[str, dict] = {}
    missing_count = 0

    for dim_key, dim_meta in MASTER_DIMENSIONS.items():
        # Context-dependent dynamic auto default
        if dim_key == "format_layout":
            auto_key = context["recommended_format"]
            auto_default = f"{auto_key} ({dim_meta['options'].get(auto_key, 'Context-matched layout')})"
        elif dim_key == "caption_style":
            auto_key = context["recommended_caption"]
            auto_default = f"{auto_key} ({dim_meta['options'].get(auto_key, 'Kinetic with punch words')})"
        elif dim_key == "color_grading":
            auto_key = context["recommended_grade"]
            auto_default = f"{auto_key} ({dim_meta['options'].get(auto_key, 'Cinema tone grade')})"
        elif dim_key == "audio_processing":
            auto_key = context["recommended_audio"]
            auto_default = f"{auto_key} ({dim_meta['options'].get(auto_key, 'Noise filtering')})"
        elif dim_key == "graphics_elements":
            auto_key = "researcher-articles" if context["genre"] == "investigative-teardown" else "kinetic-data-charts"
            auto_default = f"{auto_key} ({dim_meta['options'].get(auto_key, 'Visual elements')})"
        else:
            auto_key = "tactile-creator"
            auto_default = f"{auto_key} + upbeat-lofi (-18dB ducked under dialogue)"

        if dim_key in extracted:
            audit[dim_key] = {
                "status": "PROVIDED_IN_PROMPT",
                "name": dim_meta["name"],
                "value": extracted[dim_key]["raw"],
                "chosen_key": extracted[dim_key]["key"],
                "source": "prompt",
                "master_options": dim_meta["options"],
                "auto_default": auto_default,
                "auto_key": auto_key,
            }
        else:
            # Check brand memory for fallback
            memo_val = None
            if brand_memo:
                if dim_key == "caption_style" and "primary_caption_engine" in brand_memo.get("typography_&_captions", {}):
                    memo_val = brand_memo["typography_&_captions"]["primary_caption_engine"]
                elif dim_key == "color_grading" and "color_grading_preset" in brand_memo.get("color_palette_&_grading", {}):
                    memo_val = brand_memo["color_palette_&_grading"]["color_grading_preset"]
                elif dim_key == "audio_processing" and "noise_suppression" in brand_memo.get("audio_&_voice_master", {}):
                    memo_val = brand_memo["audio_&_voice_master"]["noise_suppression"]

            if memo_val:
                audit[dim_key] = {
                    "status": "PROVIDED_IN_BRAND_MEMO",
                    "name": dim_meta["name"],
                    "value": memo_val,
                    "chosen_key": auto_key,
                    "source": "brand/MEMO.md",
                    "master_options": dim_meta["options"],
                    "auto_default": auto_default,
                    "auto_key": auto_key,
                }
            else:
                missing_count += 1
                audit[dim_key] = {
                    "status": "MISSING",
                    "name": dim_meta["name"],
                    "value": None,
                    "chosen_key": None,
                    "source": None,
                    "master_options": dim_meta["options"],
                    "auto_default": auto_default,
                    "auto_key": auto_key,
                }

    return {
        "prompt": prompt,
        "context": context,
        "missing_count": missing_count,
        "total_dimensions": len(MASTER_DIMENSIONS),
        "dimensions": audit,
    }


# -----------------------------------------------------------------------------
# Quality Flags & Settings Proactive Check
# -----------------------------------------------------------------------------

def generate_quality_flags_check(context: dict, audit: dict) -> list[dict]:
    checks = []

    # 1. Noise Suppression: Active for indoor (HVAC hum, room reverb, fan noise) as well as outdoor (traffic, vehicle rumble)
    checks.append({
        "flag": "--denoise neural",
        "setting": "DeepFilterNet3 Neural Suppression (Active for Indoor & Outdoor)",
        "benefit": "Active for indoor (AC hum, room reverb, fan noise) and outdoor (traffic, vehicle rumble) without robotic voice artifacts.",
        "recommended": True,
    })

    # 2. Face-Tracking Reframe: Active for vertical delivery (9:16 Reels/Shorts)
    fmt = audit.get("dimensions", {}).get("format_layout", {})
    fmt_str = (fmt.get("value") or fmt.get("auto_default") or "").lower()
    prompt_str = audit.get("prompt", "").lower()
    is_vertical = any(k in fmt_str for k in ("9:16", "vertical", "reel", "short", "tiktok", "portrait")) or any(k in prompt_str for k in ("9:16", "vertical", "reel", "short", "tiktok"))
    checks.append({
        "flag": "--reframe yunet",
        "setting": "YuNet AI Face-Tracking Reframe (Active for Vertical Delivery)",
        "benefit": "Active for 9:16 vertical delivery: dynamically tracks presenter face and locks eye/chin safe zones.",
        "recommended": is_vertical,
    })

    # 3. Ultra HD (UHD / 4K) Delivery Resolution
    checks.append({
        "flag": "--resolution uhd",
        "setting": "Ultra HD 4K Mastering (2160x3840 vertical / 3840x2160 horizontal)",
        "benefit": "Renders pristine 4K UHD masters, razor-sharp SVG vector graphics, micro-typography, and high-retention details with zero compression blur.",
        "recommended": True,
    })

    return checks


# -----------------------------------------------------------------------------
# Interactive Reporting & Question Generation (Max 10 Options)
# -----------------------------------------------------------------------------

def format_interactive_summary(spec_audit: dict) -> str:
    ctx = spec_audit.get("context", {})
    lines = [
        "# 📋 Gate 1: Creative Dimensions & Context-Driven Specification",
        "",
        f"**User Prompt:** *\"{spec_audit.get('prompt', '').strip()}\"*",
        f"**Detected Content Context:** `{ctx.get('genre', 'creator-video')}` | Pace: `{ctx.get('pace', 'medium')}` | Pacing Caption: `{ctx.get('recommended_caption', 'weight-shift')}`",
        "",
        "| Creative Dimension | Status | Value / Source | Context-Derived Auto Default |",
        "|---|---|---|---|",
    ]

    for dim_key, item in spec_audit["dimensions"].items():
        name = item["name"]
        st = item["status"]
        if st == "PROVIDED_IN_PROMPT":
            badge = "✅ Provided in Prompt"
            val = f"`{item['value']}`"
        elif st == "PROVIDED_IN_BRAND_MEMO":
            badge = "📌 Brand Memory (`MEMO.md`)"
            val = f"`{item['value']}`"
        else:
            badge = "⚠️ **MISSING** (Action Required)"
            val = "*Needs User Selection*"

        auto = f"`{item['auto_default']}`"
        lines.append(f"| **{name}** | {badge} | {val} | {auto} |")

    lines.append("")
    flags = generate_quality_flags_check(ctx, spec_audit)
    if flags:
        lines.append("### ⚡ Recommended Output Enhancement Flags:")
        for fl in flags:
            rec_tag = "**[Recommended Active]**" if fl["recommended"] else "[Optional]"
            lines.append(f"- {rec_tag} `{fl['flag']}`: **{fl['setting']}** — *{fl['benefit']}*")
        lines.append("")

    if spec_audit["missing_count"] > 0:
        lines.append(f"> [!IMPORTANT]")
        lines.append(f"> **{spec_audit['missing_count']} dimension(s) were not specified in your prompt.**")
        lines.append(f"> Please select your preference for each missing dimension below, or choose **(Recommended) Auto-Orchestrate** to automatically apply the context-derived configuration.")
    else:
        lines.append("> [!TIP]")
        lines.append("> All 6 creative dimensions are fully specified and ready for production.")

    return "\n".join(lines)


def format_ask_questions(spec_audit: dict, max_options: int = 10) -> list[dict]:
    questions = []

    for dim_key, item in spec_audit["dimensions"].items():
        if item["status"] != "MISSING":
            continue

        name = item["name"]
        auto_val = item["auto_default"]
        options = [
            f"(Recommended) Choose automatically based on video context & brand memory ({auto_val})"
        ]

        # Add explicit options from master data catalog up to max_options (including option 1)
        remaining_slots = max_options - len(options)
        for opt_key, opt_desc in list(item["master_options"].items())[:remaining_slots]:
            options.append(f"{opt_desc}")

        questions.append({
            "dimension": dim_key,
            "question": f"Which {name} would you like to use for this video?",
            "is_multi_select": False,
            "options": options[:max_options],
        })

    return questions


def resolve_specs(
    prompt: str,
    user_choices: dict[str, str] | None = None,
    auto_apply_missing: bool = False,
    memo_path: Path | str | None = None,
    transcript_text: str = "",
    out_path: Path | str | None = None
) -> dict:
    audit = audit_specifications(prompt, memo_path, transcript_text)
    user_choices = user_choices or {}
    resolved: dict[str, dict] = {}

    for dim_key, item in audit["dimensions"].items():
        if item["status"] in ("PROVIDED_IN_PROMPT", "PROVIDED_IN_BRAND_MEMO") and dim_key not in user_choices:
            resolved[dim_key] = {
                "key": item["chosen_key"] or item["auto_key"],
                "description": item["value"],
                "source": item["source"],
            }
        elif dim_key in user_choices:
            choice = user_choices[dim_key]
            if "Choose automatically" in choice or choice.lower() == "auto":
                resolved[dim_key] = {
                    "key": item["auto_key"],
                    "description": item["auto_default"],
                    "source": "context_auto_orchestrated",
                }
            else:
                matched_key = item["auto_key"]
                for k, desc in item["master_options"].items():
                    if k in choice.lower() or choice.lower() in desc.lower():
                        matched_key = k
                        break
                resolved[dim_key] = {
                    "key": matched_key,
                    "description": choice,
                    "source": "user_explicit_selection",
                }
        elif auto_apply_missing:
            resolved[dim_key] = {
                "key": item["auto_key"],
                "description": item["auto_default"],
                "source": "context_auto_orchestrated",
            }
        else:
            resolved[dim_key] = {
                "key": item["auto_key"],
                "description": item["auto_default"],
                "source": "context_auto_fallback",
            }

    final_payload = {
        "prompt": prompt,
        "context": audit["context"],
        "resolved_dimensions": resolved,
        "master_dimensions_count": len(resolved),
    }

    if out_path:
        out_file = Path(out_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(final_payload, indent=2), encoding="utf-8")

    return final_payload


# -----------------------------------------------------------------------------
# CLI Entrypoint
# -----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd")

    p_audit = sub.add_parser("audit", help="Extract specifications and identify missing steps")
    p_audit.add_argument("--prompt", required=True, help="User prompt text")
    p_audit.add_argument("--transcript", default="", help="Transcript text or path to transcript.json")
    p_audit.add_argument("--memo", help="Path to brand/MEMO.md")
    p_audit.add_argument("--json", action="store_true", help="Output audit result as JSON")
    p_audit.add_argument("--questions", action="store_true", help="Output structured ask_question payloads (max 10)")

    p_resolve = sub.add_parser("resolve", help="Resolve specifications and write resolved-spec.json")
    p_resolve.add_argument("--prompt", required=True, help="User prompt text")
    p_resolve.add_argument("--transcript", default="", help="Transcript text or path to transcript.json")
    p_resolve.add_argument("--choices", help="JSON string of user choices per dimension")
    p_resolve.add_argument("--auto-missing", action="store_true", help="Auto-resolve any missing dimensions")
    p_resolve.add_argument("--memo", help="Path to brand/MEMO.md")
    p_resolve.add_argument("--out", help="Path to write resolved-spec.json")

    a = ap.parse_args()

    tr_text = ""
    if hasattr(a, "transcript") and a.transcript:
        if os.path.isfile(a.transcript):
            try:
                td = json.load(open(a.transcript))
                tr_text = td.get("text", "") or " ".join(w.get("text", "") for w in td.get("words", []))
            except Exception:
                tr_text = open(a.transcript).read()
        else:
            tr_text = a.transcript

    if a.cmd == "audit":
        audit = audit_specifications(a.prompt, a.memo, tr_text)
        if a.json:
            print(json.dumps(audit, indent=2))
        elif a.questions:
            qs = format_ask_questions(audit, max_options=10)
            print(json.dumps(qs, indent=2))
        else:
            print(format_interactive_summary(audit))
            if audit["missing_count"] > 0:
                print("\n### ❓ Missing Steps for User Resolution:\n")
                qs = format_ask_questions(audit, max_options=10)
                for i, q in enumerate(qs, 1):
                    print(f"**{i}. {q['question']}** (Max {len(q['options'])} options)")
                    for opt in q["options"]:
                        print(f"   - {opt}")
                    print()
    elif a.cmd == "resolve":
        choices = json.loads(a.choices) if a.choices else {}
        res = resolve_specs(a.prompt, choices, a.auto_missing, a.memo, tr_text, a.out)
        print(json.dumps(res, indent=2))
        if a.out:
            print(f"\nSaved resolved specification to: {a.out}")
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
