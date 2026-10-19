"""Unit tests for Hinglish transliteration and virtualenv enforcement."""
import os
import unittest
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "scripts"))   # engine/scripts
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import hinglish
import runtime


class TestHinglish(unittest.TestCase):
    def test_has_devanagari(self):
        self.assertTrue(hinglish.has_devanagari("नमस्ते"))
        self.assertTrue(hinglish.has_devanagari("hello दुनिया"))
        self.assertTrue(hinglish.has_devanagari("है।"))
        self.assertFalse(hinglish.has_devanagari("Hello world!"))
        self.assertFalse(hinglish.has_devanagari("Yeh ek startup hai."))

    def test_transliterate_common_words(self):
        self.assertEqual(hinglish.to_hinglish("यह"), "yeh")
        self.assertEqual(hinglish.to_hinglish("वह"), "woh")
        self.assertEqual(hinglish.to_hinglish("है"), "hai")
        self.assertEqual(hinglish.to_hinglish("हैं"), "hain")
        self.assertEqual(hinglish.to_hinglish("नहीं"), "nahi")
        self.assertEqual(hinglish.to_hinglish("भारत"), "bharat")
        self.assertEqual(hinglish.to_hinglish("करोड़"), "crore")
        self.assertEqual(hinglish.to_hinglish("लाख"), "lakh")
        self.assertEqual(hinglish.to_hinglish("हज़ार"), "hazaar")
        self.assertEqual(hinglish.to_hinglish("गाड़ी"), "gaadi")

    def test_transliterate_sentence_with_danda(self):
        result = hinglish.to_hinglish("यह भारत का सबसे बड़ा स्टार्टअप है।")
        self.assertFalse(hinglish.has_devanagari(result))
        self.assertTrue(result.endswith("."))

    def test_clean_transcript_words(self):
        words = [
            {"text": "यह", "start": 0.0, "end": 0.3},
            {"text": "startup", "start": 0.3, "end": 0.7},
            {"text": "है।", "start": 0.7, "end": 1.0},
        ]
        cleaned = hinglish.clean_transcript_words(words)
        for w in cleaned:
            self.assertFalse(hinglish.has_devanagari(w["text"]))
        self.assertEqual(cleaned[0]["text"], "yeh")
        self.assertEqual(cleaned[1]["text"], "startup")
        self.assertEqual(cleaned[2]["text"], "hai.")

    def test_clean_transcript_structure(self):
        transcript_data = {
            "lang": "hi",
            "text": "यह एक बड़ा बिज़नेस है।",
            "cues": [
                {"text": "यह एक बड़ा बिज़नेस है।", "start": 0.0, "end": 1.5}
            ],
            "words": [
                {"text": "यह", "start": 0.0, "end": 0.3},
                {"text": "एक", "start": 0.3, "end": 0.5},
                {"text": "बड़ा", "start": 0.5, "end": 0.8},
                {"text": "बिज़नेस", "start": 0.8, "end": 1.2},
                {"text": "है।", "start": 1.2, "end": 1.5},
            ]
        }
        cleaned = hinglish.clean_transcript(transcript_data)
        self.assertEqual(cleaned["lang"], "hi-Latn")
        self.assertEqual(cleaned["script"], "hinglish")
        self.assertFalse(hinglish.has_devanagari(cleaned["text"]))
        for c in cleaned["cues"]:
            self.assertFalse(hinglish.has_devanagari(c["text"]))
        for w in cleaned["words"]:
            self.assertFalse(hinglish.has_devanagari(w["text"]))


class TestVirtualEnvEnforcement(unittest.TestCase):
    def test_find_project_venv(self):
        venv = runtime.find_project_venv()
        self.assertIsNotNone(venv, "Project .venv should be discovered")
        self.assertTrue(os.path.isdir(venv))
        self.assertTrue(os.path.exists(os.path.join(venv, "bin", "python3")) or
                        os.path.exists(os.path.join(venv, "bin", "python")))

    def test_find_engine_dir(self):
        engine_dir = runtime.find_engine_dir()
        self.assertIsNotNone(engine_dir)
        self.assertTrue(str(engine_dir).endswith("engine") or str(engine_dir).endswith(".video-skills"))

    def test_windows_and_unix_python_resolution(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            # Test Windows Scripts layout
            win_scripts = tmp_p / "Scripts"
            win_scripts.mkdir()
            win_py = win_scripts / "python.exe"
            win_py.touch()
            self.assertEqual(runtime._find_python_in_venv(tmp_p), win_py)

            # Test Unix bin layout
            unix_bin = tmp_p / "bin"
            unix_bin.mkdir()
            unix_py = unix_bin / "python3"
            unix_py.touch()
            self.assertEqual(runtime._find_python_in_venv(tmp_p), unix_py)


if __name__ == "__main__":
    unittest.main()
