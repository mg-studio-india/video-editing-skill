"""End-to-end test through the real CLI. Needs ffmpeg/ffprobe; whisper.cpp is faked so the
test is fast and runs anywhere. Run: python3 -m unittest discover -s tests"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(HERE))

FAKE_WHISPER = r'''#!/usr/bin/env python3
import json, sys
a = sys.argv[1:]
if "-h" in a:
    sys.stderr.write("--output-json --max-len --split-on-word --dtw --prompt\n"); sys.exit(0)
if "-np" in a:                      # pretend an older build: must be retried without it
    sys.stderr.write("error: unknown argument: -np\n"); sys.exit(1)
prefix = a[a.index("-of") + 1]
words = [("So",.5,.7),("today",.7,1.1),("I",1.1,1.2),("want",1.2,1.4),
         ("So",2.0,2.2),("today",2.2,2.6),("I",2.6,2.7),("want",2.7,2.9),("um",2.9,3.2),
         ("to",3.3,3.4),("show",3.4,3.8),("you",3.8,4.15),(".",4.15,4.2),
         ("Next",6.5,6.9),("step",6.9,7.4),(".",7.4,7.5)]
tr = [{"offsets": {"from": int(s*1000), "to": int(e*1000)}, "text": w if w == "." else " " + w} for w, s, e in words]
json.dump({"result": {"language": "en"}, "transcription": tr}, open(prefix + ".json", "w"))
'''


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg not installed")
class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from make_video import make
        cls.tmp = Path(tempfile.mkdtemp(prefix="watch-it-"))
        cls.video = make(cls.tmp / "clip.mp4")
        from tests.helpers import fake_exe
        fake = Path(fake_exe(str(cls.tmp / "whisper-cli"), FAKE_WHISPER))
        (cls.tmp / "ggml-large-v3.bin").write_bytes(b"")
        cls.env = {**os.environ, "WATCH_WHISPER_CPP_BIN": str(fake),
                   "WATCH_WHISPER_MODEL": str(cls.tmp / "ggml-large-v3.bin"),
                   "WATCH_CACHE_DIR": str(cls.tmp / "cache"), "HOME": str(cls.tmp / "home")}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_watch(self, *args, expect=0):
        p = subprocess.run([sys.executable, str(SCRIPTS / "watch.py"), *args], capture_output=True,
                           text=True, env=self.env)
        self.assertEqual(p.returncode, expect, p.stdout + p.stderr)
        return p

    def run_dir(self):
        return next((self.tmp / "cache").glob("clip-*")) / "full"

    def test_1_ref_pipeline(self):
        p = self.run_watch("ref", str(self.video), "--intent", "test")
        rd = self.run_dir()
        for name in ("analysis.json", "fingerprint.json", "storyboard.md", "transcript.json"):
            self.assertTrue((rd / name).is_file(), name)
        a = json.loads((rd / "analysis.json").read_text())
        self.assertEqual([round(s["start"], 1) for s in a["shots"]], [0.0, 2.0, 4.0, 7.0, 8.0])
        self.assertEqual(a["transcript"]["word_count"], 14)
        self.assertIn("hook_", p.stdout)
        self.assertTrue(list((rd / "sheets").glob("sheet_*.jpg")))
        # unfilled storyboard must fail lint, a filled copy must pass
        self.run_watch("lint", str(rd / "storyboard.md"), expect=1)
        filled = self.tmp / "filled.md"
        filled.write_text((rd / "storyboard.md").read_text().replace("⟨fill⟩", "ok"))
        self.run_watch("lint", str(filled))

    def test_2_second_run_keeps_filled_storyboard_and_uses_cache(self):
        rd = self.run_dir()
        sb = rd / "storyboard.md"
        sb.write_text("MY FILLED WORK")
        p = self.run_watch("ref", str(self.video))
        self.assertEqual(sb.read_text(), "MY FILLED WORK")
        self.assertTrue((rd / "storyboard.skeleton.md").is_file())
        self.assertIn("cached transcript", p.stderr)

    def test_3_mine_with_preview(self):
        rd = self.run_dir()
        p = self.run_watch("mine", str(self.video), "--against", str(rd / "fingerprint.json"), "--preview", "--no-hook")
        cut = json.loads((rd / "cutlist.json").read_text())
        self.assertEqual(cut["stats"]["clip_count"], len(cut["keep"]))
        reasons = {r for x in cut["removed"] for r in x["reasons"]}
        self.assertTrue({"retake", "filler", "pause"} <= reasons, reasons)
        plan = json.loads((rd / "edit-plan.json").read_text())
        self.assertEqual([t["type"] for t in plan["tracks"]], ["video", "audio", "captions"])
        self.assertTrue((rd / "preview.mp4").is_file())
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(rd / "preview.mp4")], capture_output=True, text=True)
        self.assertAlmostEqual(float(probe.stdout), plan["duration"], delta=0.3)
        self.assertIn("Against the reference", p.stdout)

    def test_4_focus(self):
        p = self.run_watch("focus", str(self.video), "--start", "1.5", "--end", "5")
        self.assertIn("Words (with timing)", p.stdout)
        self.assertIn("Cuts in range: 00:02.00, 00:04.00", p.stdout)

    def test_5_bad_input_is_a_clean_error(self):
        p = self.run_watch("ref", str(self.tmp / "missing.mp4"), expect=1)
        self.assertIn("File not found", p.stderr)
        p = self.run_watch("focus", str(self.video), expect=1)
        self.assertIn("--start and --end", p.stderr)


if __name__ == "__main__":
    unittest.main()
