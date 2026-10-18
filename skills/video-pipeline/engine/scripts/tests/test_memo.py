#!/usr/bin/env python3
"""Tests for memo.py brand memory manager."""
import os
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
import sys
sys.path.insert(0, str(SCRIPTS))
import memo  # noqa: E402


class TestMemo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.memo_path = Path(self.tmp.name) / "brand" / "MEMO.md"

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_creates_memo(self):
        f = memo.init_memo(self.memo_path, {"creator": "TestCreator", "instagram": "@testcreator"})
        self.assertTrue(f.is_file())
        text = f.read_text()
        self.assertIn("TestCreator", text)
        self.assertIn("@testcreator", text)
        self.assertIn("focus-blur-resolve", text)

    def test_parse_memo(self):
        memo.init_memo(self.memo_path, {"creator": "Vihan", "instagram": "@vihan_"})
        data = memo.parse_memo(self.memo_path)
        self.assertIn("identity_&_profiles", data)
        self.assertEqual(data["identity_&_profiles"].get("creator_/_channel"), "Vihan")
        self.assertEqual(data["identity_&_profiles"].get("instagram"), "@vihan_")

    def test_update_memo_field(self):
        memo.init_memo(self.memo_path)
        ok = memo.update_memo_field("Instagram", "@new_handle", self.memo_path)
        self.assertTrue(ok)
        data = memo.parse_memo(self.memo_path)
        self.assertEqual(data["identity_&_profiles"].get("instagram"), "@new_handle")


if __name__ == "__main__":
    unittest.main()
