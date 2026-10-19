"""Speaker-video layouts (stack / pip / hide) and project transcript corrections (fix-words + transcribe --fix)."""
import importlib.util, json, os, subprocess, sys, unittest
from .helpers import SCRIPTS, script_path, ffmpeg, load, needs_ffmpeg, run, scratch, write

sys.path.insert(0, SCRIPTS)
import treatments as T  # noqa: E402


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, script_path(filename))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


FW = module("fix_words_t", "fix-words.py")
W = lambda t, s, e: {"text": t, "w": t, "start": s, "end": e}


class Layouts(unittest.TestCase):
    def test_boxes(self):
        self.assertEqual(T.layout_box("stack", 1080, 1920), (0, 0, 1080, 845))
        x, y, w, h = T.layout_box("pip", 1080, 1920)
        self.assertEqual((x, w, h), (43, 346, 461))
        self.assertGreaterEqual(y, 180)                              # under the platform's top bar
        x, y, w, h = T.layout_box("pip", 1920, 1080)
        self.assertGreater(x, 1920 / 2); self.assertGreater(y, 1080 / 2)     # landscape: bottom-right
        self.assertEqual(T.layout_box("hide", 1080, 1920), (0, 0, 1080, 1920))
        with self.assertRaises(SystemExit):
            T.layout_box("zoomy", 1080, 1920)

    def lay(self, *spans):
        return [{"type": "layout", "id": "L%d" % i, "mode": m, "in": a, "out": b} for i, (m, a, b) in enumerate(spans)]

    def test_returns_to_full_only_when_there_is_room(self):
        js = T.layout_js(self.lay(("stack", 1.0, 3.0), ("pip", 3.2, 5.0)), 1080, 1920, {})
        returns = [l for l in js if "width: 1080, height: 1920" in l]
        self.assertEqual(len(returns), 1)                            # only after the last one: 3.2 - 3.0 < transition
        self.assertIn("5.000", returns[0])
        js2 = T.layout_js(self.lay(("stack", 1.0, 3.0), ("pip", 5.0, 6.0)), 1080, 1920, {})
        self.assertEqual(len([l for l in js2 if "width: 1080, height: 1920" in l]), 2)

    def test_pip_floats_above_full_frame_content_and_hide_fades(self):
        js = T.layout_js(self.lay(("pip", 1.0, 2.0), ("hide", 3.0, 4.0)), 1080, 1920, {})
        self.assertTrue(any("zIndex: 35" in l and "1.000" in l for l in js))
        self.assertTrue(any("opacity: 0" in l and "3.000" in l for l in js))
        self.assertEqual(T.layout_overlaps(self.lay(("stack", 1, 3), ("pip", 2.5, 4))), ["L0 and L1 overlap"])

    def test_stage_builds_layouts(self):
        d = scratch(self)
        spec = write(os.path.join(d, "sb.json"), {"id": "s", "canvas": [1080, 1920], "duration": 6, "video": "v.mp4",
                     "beats": [{"type": "layout", "id": "L1", "mode": "stack", "in": 1, "out": 3},
                               {"type": "cards", "id": "c", "items": [["a", 1.5]], "in": 1.2, "out": 2.8}]})
        r = run("stage.py", "--spec", spec, "--out", os.path.join(d, "p"),
                "--style", write(os.path.join(d, "s.json"), {"fonts": {"display": {"family": "X", "files": {}}}}))
        self.assertEqual(r.returncode, 0, r.stderr)
        html = open(os.path.join(d, "p", "index.html")).read()
        self.assertIn("#cam-wrap { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;", html)
        self.assertIn("tl.to('#cam-wrap', { x: 0, y: 0, width: 1080, height: 845", html)


class Corrections(unittest.TestCase):
    def test_merge_split_rename_keep_timing_and_punctuation(self):
        words = [W("Use", 0, .2), W("cap", .2, .4), W("cut.", .4, .7), W("Then", 1, 1.2), W("co-founder", 2, 2.6)]
        new, ch = FW.apply(words, {"cap cut": "CapCut", "then": "and then", "co-founder": "cofounder"})
        self.assertEqual([(w["text"], w["start"], w["end"]) for w in new],
                         [("Use", 0, .2), ("CapCut.", .2, .7), ("and", 1.0, 1.1), ("then", 1.1, 1.2), ("cofounder", 2, 2.6)])
        self.assertTrue(all(w["w"] == w["text"] for w in new))
        self.assertEqual(len(ch), 3)

    def test_no_partial_matches(self):
        new, ch = FW.apply([W("capital", 0, 1), W("cuts", 1, 2)], {"cap cut": "CapCut", "cap": "CAP"})
        self.assertEqual([w["text"] for w in new], ["capital", "cuts"]); self.assertEqual(ch, [])

    def test_cli_saves_and_reapplies(self):
        d = scratch(self)
        tp = write(os.path.join(d, "transcript.json"), {"words": [W("hyper", 0, .3), W("frames", .3, .6)]})
        r = run("fix-words.py", "--transcript", tp, "--add", "hyper frames=HyperFrames")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(load(os.path.join(d, "corrections.json")), {"hyper frames": "HyperFrames"})
        self.assertEqual([w["text"] for w in load(tp)["words"]], ["HyperFrames"])


FAKE_WHISPER = r'''#!/usr/bin/env python3
import json, sys
a = sys.argv[1:]
prefix = a[a.index("-of") + 1]
open(prefix + ".prompt", "w").write(a[a.index("--prompt") + 1] if "--prompt" in a else "")
words = [("Try",.5,.7),("cap",.7,.9),("cut",.9,1.2),("today.",1.2,1.6)]
tr = [{"offsets": {"from": int(s*1000), "to": int(e*1000)}, "text": " " + w} for w, s, e in words]
json.dump({"result": {"language": "en"}, "transcription": tr}, open(prefix + ".json", "w"))
'''


@needs_ffmpeg
class TranscribeAppliesCorrections(unittest.TestCase):
    def test_every_pass_applies_project_corrections(self):
        d = scratch(self)
        fake = write(os.path.join(d, "whisper-cli"), FAKE_WHISPER); os.chmod(fake, 0o755)
        model = write(os.path.join(d, "ggml-large-v3.bin"), "")
        clip = os.path.join(d, "clip.wav"); ffmpeg("-f", "lavfi", "-i", "sine=f=200:d=2", clip)
        write(os.path.join(d, "corrections.json"), {"cap cut": "CapCut"})
        env = {**os.environ, "WATCH_WHISPER_CPP_BIN": fake, "WATCH_WHISPER_MODEL": model, "HOME": d}
        out = os.path.join(d, "transcript.json")
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "transcribe.py"), clip, "--out", out],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        t = load(out)
        self.assertEqual([w["text"] for w in t["words"]], ["Try", "CapCut", "today."])
        self.assertEqual((t["words"][1]["start"], t["words"][1]["end"]), (0.7, 1.2))
        self.assertEqual(t["corrections_applied"], 1)


if __name__ == "__main__":
    unittest.main()
