#!/usr/bin/env python3
"""Tests for spec-resolver.py context-driven creative dimension extractor and missing step resolver."""
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"          # engine/scripts (tests/ sits next to it)
import sys
sys.path.insert(0, str(SCRIPTS))
import importlib.util
spec = importlib.util.spec_from_file_location("spec_resolver", SCRIPTS / "spec-resolver.py")
spec_resolver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spec_resolver)

spec_grade = importlib.util.spec_from_file_location("grade", SCRIPTS / "grade.py")
grade = importlib.util.module_from_spec(spec_grade)
spec_grade.loader.exec_module(grade)

import memo  # noqa: E402


class TestSpecResolver(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.memo_path = Path(self.tmp.name) / "brand" / "MEMO.md"
        memo.init_memo(self.memo_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_extract_prompt_specs_full(self):
        prompt = (
            "Edit this into a 9:16 vertical reel with 40/60 split screen view. "
            "Use Kodak Portra warm color grading, weight-shift captions with Poppins font, "
            "whoosh sfx on cuts, researcher article clippings with highlighter pen sweeps, "
            "and filter out heavy road traffic noise."
        )
        extracted = spec_resolver.extract_prompt_specs(prompt)

        self.assertIn("format_layout", extracted)
        self.assertEqual(extracted["format_layout"]["key"], "split-screen")

        self.assertIn("color_grading", extracted)
        self.assertEqual(extracted["color_grading"]["key"], "kodak-portra-warm")

        self.assertIn("caption_style", extracted)
        self.assertEqual(extracted["caption_style"]["key"], "weight-shift")

        self.assertIn("sounds_audio_bed", extracted)

        self.assertIn("graphics_elements", extracted)
        self.assertEqual(extracted["graphics_elements"]["key"], "researcher-articles")

        self.assertIn("audio_processing", extracted)
        self.assertEqual(extracted["audio_processing"]["key"], "neural-heavy")

    def test_context_driven_format_recommendations(self):
        # 1. Technical software demo -> screen-plus-facecam
        ctx_tech = spec_resolver.detect_video_context(
            prompt="Software walkthrough demonstrating GitHub API integration in the terminal"
        )
        self.assertEqual(ctx_tech["recommended_format"], "screen-plus-facecam")

        # 2. Investigative market report -> split-screen
        ctx_investigative = spec_resolver.detect_video_context(
            prompt="Financial investigation and forensic teardown of quarterly revenue report"
        )
        self.assertEqual(ctx_investigative["recommended_format"], "split-screen")

        # 3. High-retention viral reel -> multi-dynamic
        ctx_viral = spec_resolver.detect_video_context(
            prompt="High energy viral storytelling reel with dynamic cuts"
        )
        self.assertEqual(ctx_viral["recommended_format"], "multi-dynamic")

        # 4. Product unboxing -> corner-pip
        ctx_product = spec_resolver.detect_video_context(
            prompt="Unboxing new hardware device and showing physical demo"
        )
        self.assertEqual(ctx_product["recommended_format"], "corner-pip")

    def test_default_caption_style_is_weight_shift_or_highlight(self):
        # Conversational speech pace -> weight-shift with punch words
        ctx_normal = spec_resolver.detect_video_context(
            prompt="A relaxed conversational discussion about business strategy"
        )
        self.assertIn(ctx_normal["recommended_caption"], ("weight-shift", "caption-highlight"))

        # Fast rapid speech pace -> caption-highlight with punch words
        ctx_fast = spec_resolver.detect_video_context(
            prompt="Fast intense energetic hook sequence with rapid pace"
        )
        self.assertIn(ctx_fast["recommended_caption"], ("weight-shift", "caption-highlight"))

    def test_audit_specifications_missing_detection(self):
        # Prompt only specifies format and color grade
        prompt = "Make a 9:16 vertical short with vibrant pop colors."
        audit = spec_resolver.audit_specifications(prompt, memo_path=None)

        self.assertEqual(audit["dimensions"]["format_layout"]["status"], "PROVIDED_IN_PROMPT")
        self.assertEqual(audit["dimensions"]["color_grading"]["status"], "PROVIDED_IN_PROMPT")
        self.assertEqual(audit["dimensions"]["sounds_audio_bed"]["status"], "MISSING")
        self.assertEqual(audit["dimensions"]["caption_style"]["status"], "MISSING")
        self.assertEqual(audit["dimensions"]["graphics_elements"]["status"], "MISSING")
        self.assertEqual(audit["dimensions"]["audio_processing"]["status"], "MISSING")
        self.assertEqual(audit["missing_count"], 4)

    def test_format_ask_questions_max_10_and_auto_first(self):
        prompt = "Create a reel with lofi background music."
        audit = spec_resolver.audit_specifications(prompt, memo_path=None)
        questions = spec_resolver.format_ask_questions(audit, max_options=10)

        self.assertTrue(len(questions) > 0)
        for q in questions:
            self.assertTrue(len(q["options"]) >= 2)
            self.assertLessEqual(len(q["options"]), 10)
            # The FIRST option must explicitly be the recommended automatic choice
            first_option = q["options"][0]
            self.assertTrue(first_option.startswith("(Recommended) Choose automatically based on video context & brand memory"))

    def test_grade_py_formula_and_presets(self):
        # Verify 3-way tone formula calculates shadows, midtones, highlights, contrast, saturation
        vf_formula = grade.build_tone_formula(
            shadows=0.03,
            midtones=1.08,
            highlights=-0.04,
            contrast=1.14,
            saturation=1.12,
            temperature=6300,
            sharpness=0.6
        )
        self.assertIn("colorlevels=", vf_formula)
        self.assertIn("colortemperature=temperature=6300", vf_formula)
        self.assertIn("eq=gamma=1.08:gamma_weight=0.5:contrast=1.14:saturation=1.12", vf_formula)
        self.assertIn("unsharp=3:3:0.6", vf_formula)

        # Verify 10 presets exist
        self.assertGreaterEqual(len(grade.PRESET_FILTERS), 10)
        self.assertIn("kodak-portra-warm", grade.PRESET_FILTERS)
        self.assertIn("hollywood-teal-orange", grade.PRESET_FILTERS)
        self.assertIn("vox-documentary", grade.PRESET_FILTERS)
        self.assertIn("magnates-gold", grade.PRESET_FILTERS)
        self.assertIn("fuji-pro-cinematic", grade.PRESET_FILTERS)

    def test_resolve_specs_with_auto_and_explicit_choices(self):
        prompt = "Edit my video with Kodak Portra warm grade."
        out_file = Path(self.tmp.name) / "resolved-spec.json"

        user_choices = {
            "caption_style": "(Recommended) Choose automatically based on video context & brand memory",
            "format_layout": "Corner PiP Minimization (Presenter in ~30% squircle floating window, open canvas)"
        }

        res = spec_resolver.resolve_specs(
            prompt=prompt,
            user_choices=user_choices,
            auto_apply_missing=True,
            memo_path=self.memo_path,
            out_path=out_file
        )

        self.assertTrue(out_file.is_file())
        saved = json.loads(out_file.read_text())

        # format_layout was explicitly chosen as corner-pip
        self.assertEqual(saved["resolved_dimensions"]["format_layout"]["key"], "corner-pip")
        self.assertEqual(saved["resolved_dimensions"]["format_layout"]["source"], "user_explicit_selection")

        # color_grading was in prompt
        self.assertEqual(saved["resolved_dimensions"]["color_grading"]["key"], "kodak-portra-warm")
        self.assertEqual(saved["resolved_dimensions"]["color_grading"]["source"], "prompt")

        # caption_style was auto-chosen to weight-shift or caption-highlight
        self.assertIn(saved["resolved_dimensions"]["caption_style"]["key"], ("weight-shift", "caption-highlight"))
        self.assertEqual(saved["resolved_dimensions"]["caption_style"]["source"], "context_auto_orchestrated")

    def test_format_interactive_summary(self):
        prompt = "Reel with 40/60 split view and neural noise suppression"
        audit = spec_resolver.audit_specifications(prompt, memo_path=None)
        summary = spec_resolver.format_interactive_summary(audit)

        self.assertIn("# 📋 Gate 1: Creative Dimensions & Context-Driven Specification", summary)
        self.assertIn("40/60 split view", summary)
        self.assertIn("neural noise suppression", summary)
        self.assertIn("Recommended Output Enhancement Flags", summary)

    def test_indoor_denoise_active_and_quality_flags(self):
        # Indoor prompt without road noise
        ctx_indoor = spec_resolver.detect_video_context(
            prompt="Record an indoor desk interview in a home studio"
        )
        self.assertEqual(ctx_indoor["recommended_audio"], "neural-indoor")

        audit = spec_resolver.audit_specifications("Indoor studio interview", memo_path=None)
        flags = spec_resolver.generate_quality_flags_check(ctx_indoor, audit)

        denoise_flag = next(f for f in flags if f["flag"] == "--denoise neural")
        self.assertTrue(denoise_flag["recommended"])
        self.assertIn("Indoor", denoise_flag["setting"])

    def test_reframe_yunet_active_for_vertical_delivery(self):
        # 1. Vertical Reel -> Reframe YuNet is recommended
        audit_vert = spec_resolver.audit_specifications("Create a 9:16 vertical reel", memo_path=None)
        ctx_vert = spec_resolver.detect_video_context("Create a 9:16 vertical reel")
        flags_vert = spec_resolver.generate_quality_flags_check(ctx_vert, audit_vert)
        reframe_vert = next(f for f in flags_vert if f["flag"] == "--reframe yunet")
        self.assertTrue(reframe_vert["recommended"])

        # 2. Horizontal 16:9 -> Reframe YuNet is NOT recommended
        audit_horiz = spec_resolver.audit_specifications("Create a 16:9 landscape documentary", memo_path=None)
        ctx_horiz = spec_resolver.detect_video_context("Create a 16:9 landscape documentary")
        flags_horiz = spec_resolver.generate_quality_flags_check(ctx_horiz, audit_horiz)
        reframe_horiz = next(f for f in flags_horiz if f["flag"] == "--reframe yunet")
        self.assertFalse(reframe_horiz["recommended"])

    def test_resolution_uhd(self):
        audit = spec_resolver.audit_specifications("Create a 4K UHD reel", memo_path=None)
        ctx = spec_resolver.detect_video_context("Create a 4K UHD reel")
        flags = spec_resolver.generate_quality_flags_check(ctx, audit)
        res_flag = next(f for f in flags if f["flag"] == "--resolution uhd")
        self.assertTrue(res_flag["recommended"])
        self.assertIn("4K", res_flag["setting"])

        extracted = spec_resolver.extract_prompt_specs("Make a vertical reel in UHD 4K")
        self.assertIn("UHD 4K", extracted["format_layout"]["raw"])

    def test_caption_engine_asked_unless_explicit_or_big_figures(self):
        # Generic 'add captions' does NOT match a style, so status is MISSING (user must be asked)
        prompt_generic = "Create a reel and add captions"
        extracted_generic = spec_resolver.extract_prompt_specs(prompt_generic)
        self.assertNotIn("caption_style", extracted_generic)

        audit_generic = spec_resolver.audit_specifications(prompt_generic, memo_path=None)
        self.assertEqual(audit_generic["dimensions"]["caption_style"]["status"], "MISSING")

        # Explicit 'big figures in the background' matches layered-head
        prompt_big_fig = "Make a reel with big figures in the background behind speaker"
        extracted_big_fig = spec_resolver.extract_prompt_specs(prompt_big_fig)
        self.assertIn("caption_style", extracted_big_fig)
        self.assertEqual(extracted_big_fig["caption_style"]["key"], "layered-head")

        ctx_big_fig = spec_resolver.detect_video_context(prompt_big_fig)
        self.assertEqual(ctx_big_fig["recommended_caption"], "layered-head")


if __name__ == "__main__":
    unittest.main()
