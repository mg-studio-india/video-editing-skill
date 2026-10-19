"""resolve-anchors (plan phrases -> times), make-short (word-snapped Shorts), jump-frames (exact cut frames),
reframe (face-tracked crops)."""
import importlib.util, json, os, shutil, subprocess, sys, unittest
import numpy as np
from .helpers import SCRIPTS, script_path, ffmpeg, load, needs_ffmpeg, run, scratch, write


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, script_path(filename))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, SCRIPTS)
    spec.loader.exec_module(m)
    return m


RA = module("resolve_anchors_t", "resolve-anchors.py")
MS = module("make_short_t", "make-short.py")
JF = module("jump_frames_t", "jump-frames.py")
RF = module("reframe_t", "reframe.py")

WORDS = [("You", .5, .7), ("clicked", .7, 1.0), ("on", 1.0, 1.1), ("a", 1.1, 1.2), ("thumbnail.", 1.2, 1.8),
         ("There", 3.0, 3.2), ("are", 3.2, 3.3), ("three", 3.3, 3.6), ("tools:", 3.6, 4.0), ("candles,", 4.5, 5.0),
         ("soap", 5.5, 5.9), ("and", 6.0, 6.1), ("t-shirts.", 6.3, 6.9), ("Follow", 9.0, 9.3), ("@mkbhd", 9.3, 9.9),
         ("on", 10.0, 10.1), ("YouTube.", 10.1, 10.6), ("Three", 12.0, 12.3), ("tools", 12.3, 12.7), ("again.", 12.7, 13.2)]
TW = [{"text": w, "w": w, "start": s, "end": e} for w, s, e in WORDS]


class ResolveAnchors(unittest.TestCase):
    def go(self, plan, duration=15.0):
        return RA.resolve(plan, TW, duration)

    def test_beat_enters_a_lead_before_its_phrase_and_holds_by_type(self):
        out, R = self.go({"beats": [{"type": "line", "id": "l1", "anchor": "clicked on a thumbnail"}]})
        self.assertEqual((out["beats"][0]["in"], out["beats"][0]["out"]), (0.5, 5.5))
        self.assertEqual(R.problems, [])

    def test_list_items_time_themselves_and_the_list_ends_after_the_last(self):
        out, _ = self.go({"beats": [{"type": "list", "id": "ls", "anchor": "three tools",
                                     "items": [["Candles", "@"], ["Soap"], ["T-shirts", "@", "t shirts"]]}]})
        b = out["beats"][0]
        self.assertEqual([i[1] for i in b["items"]], [4.5, 5.5, 6.3])
        self.assertEqual(b["out"], 8.8)

    def test_repeated_phrase_follows_plan_order_and_after(self):
        out, _ = self.go({"beats": [{"type": "line", "id": "a", "anchor": "three tools"},
                                    {"type": "line", "id": "b", "anchor": "three tools", "after": "@follow"}]})
        self.assertEqual([b["in"] for b in out["beats"]], [3.1, 11.8])

    def test_handle_in_text_is_not_an_anchor(self):
        out, R = self.go({"beats": [{"type": "chip", "id": "c", "text": "@mkbhd", "anchor": "follow", "out": "@youtube"}],
                          "loops": [{"question": "@ which?", "planted": "@three tools", "payoff": "@again"}]})
        self.assertEqual(out["beats"][0]["text"], "@mkbhd")
        self.assertEqual(out["beats"][0]["out"], 10.6)               # an out-phrase means its end
        self.assertEqual(out["loops"][0], {"question": "@ which?", "planted": 3.3, "payoff": 12.7})
        self.assertEqual(R.problems, [])

    def test_camera_ops_and_end_suffix(self):
        out, _ = self.go({"camera": [["punch", "@three tools", 1.18], ["set", "@youtube:end", 1.0], ["release", 14.0, 0.5]]})
        self.assertEqual(out["camera"], [["punch", 3.3, 1.18], ["set", 10.6, 1.0], ["release", 14.0, 0.5]])

    def test_missing_phrase_is_reported_not_guessed(self):
        out, R = self.go({"beats": [{"type": "logo", "id": "x", "anchor": "never said this"}]})
        self.assertTrue(out["beats"][0]["unresolved"])
        self.assertIsNone(out["beats"][0]["in"])
        self.assertEqual(len(R.problems), 1)

    def test_out_never_passes_the_end(self):
        out, _ = self.go({"beats": [{"type": "line", "id": "z", "anchor": "again", "hold": 9}]}, duration=14.0)
        self.assertEqual(out["beats"][0]["out"], 14.0)

    def test_camera_resets_at_every_jump_unless_the_plan_has_one(self):
        cam = RA.add_resets([["punch", 3.3, 1.18], ["set", 7.997, 1.0]], [{"set_at": 5.497}, {"set_at": 8.0}])
        self.assertEqual(cam, [["punch", 3.3, 1.18], ["set", 5.497, 1.0], ["set", 7.997, 1.0]])

    def test_cli_exit_code(self):
        d = scratch(self)
        tr = write(os.path.join(d, "transcript.json"), {"words": TW, "duration": 15.0})
        good = write(os.path.join(d, "p1.json"), {"duration": "auto", "beats": [{"type": "line", "id": "a", "anchor": "follow"}]})
        bad = write(os.path.join(d, "p2.json"), {"beats": [{"type": "line", "id": "a", "anchor": "nope"}]})
        self.assertEqual(run("resolve-anchors.py", "--plan", good, "--transcript", tr, "--out", os.path.join(d, "o.json")).returncode, 0)
        self.assertEqual(load(os.path.join(d, "o.json"))["duration"], 15.0)
        self.assertEqual(run("resolve-anchors.py", "--plan", bad, "--transcript", tr, "--out", os.path.join(d, "o.json")).returncode, 1)


class ShortSnap(unittest.TestCase):
    def test_snaps_to_whole_words_with_lead_and_tail(self):
        self.assertEqual(MS.snap(2.9, 7.0, TW, 15.0), (2.92, 7.05))

    def test_never_bleeds_into_neighbours(self):
        tight = [{"start": 1.0, "end": 1.5}, {"start": 1.52, "end": 2.0}, {"start": 2.05, "end": 2.5}]
        self.assertEqual(MS.snap(1.5, 2.02, tight, 3.0), (1.5, 2.05))


class JumpFrames(unittest.TestCase):
    def test_finds_the_real_frame_near_a_listed_cut(self):
        diffs = np.full(120, 1.0); diffs[62] = 40.0; diffs[90] = 1.3
        r = JF.locate([2.04, 3.0], diffs, 30)
        self.assertEqual((r[0]["frame"], r[0]["offset_frames"], r[0]["set_at"]), (62, 1, 2.064))
        self.assertGreater(r[0]["confidence"], 10)
        self.assertLess(r[1]["confidence"], 2.0)                      # same framing on both sides: weak


class ReframePlan(unittest.TestCase):
    def test_crop_sizes(self):
        self.assertEqual(RF.crop_size(1920, 1080, 9 / 16), (606, 1080))
        self.assertEqual(RF.crop_size(1920, 1080, 8 / 9), (960, 1080))
        self.assertEqual(RF.crop_size(3840, 2160, 1.0, 1.5), (1440, 1440))

    def test_static_centres_each_shot_on_its_face_and_reuses_the_last_without_one(self):
        dets = [{"t": t / 10, "cx": 400.0, "cy": 500.0, "fw": 200, "fh": 200} for t in range(0, 30)]
        dets += [{"t": 3 + t / 10, "cx": 1500.0, "cy": 500.0, "fw": 200, "fh": 200} for t in range(0, 30)]
        dets += [{"t": 6 + t / 10, "cx": None} for t in range(0, 30)]
        keys, rep = RF.plan(dets, [(0, 3), (3, 6), (6, 9)], 1920, 1080, 606, 1080)
        self.assertEqual([k["x"] + 303 for k in keys], [399, 1499, 1499])
        self.assertEqual(rep[2]["fallback"], "previous shot")

    def test_crop_is_clamped_to_the_frame(self):
        self.assertEqual(RF.place(50, 300, 606, 1080, 1920, 1080), (0, 0))
        self.assertEqual(RF.place(1900, 300, 606, 1080, 1920, 1080)[0], 1314)

    def test_follow_jumps_at_cuts_and_glides_inside(self):
        keys = [{"t": 0.0, "x": 100, "y": 0}, {"t": 1.0, "x": 160, "y": 0}, {"t": 2.0, "x": 900, "y": 0}]
        f = RF.per_frame(keys, [(0, 2.0), (2.0, 4.0)], 30)
        inside = [k["x"] for k in f if 0 < k["t"] < 1.0]
        self.assertTrue(inside and all(100 <= x <= 160 for x in inside))
        self.assertFalse([k for k in f if 1.0 < k["t"] < 2.0])        # no glide into the next shot


@needs_ffmpeg
class ShortEndToEnd(unittest.TestCase):
    def test_make_short_then_measure_its_jump(self):
        d = scratch(self)
        flat = os.path.join(d, "flat.mp4")
        ffmpeg("-f", "lavfi", "-i", "color=c=red:s=320x180:d=7:r=30", "-f", "lavfi", "-i", "color=c=blue:s=320x180:d=8:r=30",
               "-f", "lavfi", "-i", "sine=f=200:d=15", "-filter_complex", "[0][1]concat=n=2:v=1:a=0[v]", "-map", "[v]",
               "-map", "2:a", "-c:v", "libx264", "-g", "30", "-c:a", "aac", "-shortest", flat)
        tr = write(os.path.join(d, "transcript.json"), {"words": TW})
        out = os.path.join(d, "shorts", "01")
        r = run("make-short.py", "--flat", flat, "--transcript", tr, "--out-dir", out,
                "--range", "@there are..@t-shirts", "--range", "12.0-13.2")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        s = load(os.path.join(out, "short.json"))
        self.assertEqual([(k["start"], k["end"]) for k in s["ranges_flat"]], [(2.92, 7.05), (11.92, 13.35)])
        self.assertTrue(s["text"].startswith("There are three tools"))
        cm = load(os.path.join(out, "cut-map.json"))
        self.assertEqual(len(cm["cuts"]), 1)
        j = run("jump-frames.py", "--video", os.path.join(out, "public", "input-video.mp4"),
                "--cut-map", os.path.join(out, "cut-map.json"), "--out", os.path.join(out, "jf.json"))
        self.assertEqual(j.returncode, 0, j.stdout + j.stderr)
        jf = load(os.path.join(out, "jf.json"))["jumps"]
        # red ends at 7.0 in the source, the first range keeps 2.92-7.05: the picture turns blue ~0.05 s before the
        # join and again at the join (blue -> blue is invisible), so a real jump sits within a few frames of the cut
        self.assertEqual(len(jf), 1)
        self.assertLessEqual(abs(jf[0]["offset_frames"]), 4)


@needs_ffmpeg
class ReframeEndToEnd(unittest.TestCase):
    def test_no_face_falls_back_to_centre_and_renders_vertical(self):
        d = scratch(self)
        v = os.path.join(d, "v.mp4")
        ffmpeg("-f", "lavfi", "-i", "color=c=gray:s=640x360:d=2:r=30", "-f", "lavfi", "-i", "sine=d=2",
               "-c:v", "libx264", "-c:a", "aac", "-shortest", v)
        r = run("reframe.py", "--video", v, "--aspect", "9:16", "--out", os.path.join(d, "p.json"),
                "--render", os.path.join(d, "o.mp4"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("WARN", r.stdout)
        p = load(os.path.join(d, "p.json"))
        self.assertAlmostEqual(p["keys"][0]["x"] + p["crop"][0] // 2, 320, delta=2)   # x is kept even for the encoder
        wh = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                             "-of", "csv=p=0", os.path.join(d, "o.mp4")], capture_output=True, text=True).stdout.strip()
        self.assertEqual(wh, "1080,1920")


if __name__ == "__main__":
    unittest.main()
