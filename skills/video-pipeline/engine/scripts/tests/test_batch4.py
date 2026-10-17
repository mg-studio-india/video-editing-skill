"""generate (requests, cost gate, ledger), sfx-prep, audiocraft-gen (plan, licence), render (--raw finish), review."""
import importlib.util, json, os, subprocess, sys, unittest
from .helpers import SCRIPTS, ffmpeg, load, needs_ffmpeg, run, scratch, write


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, filename))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, SCRIPTS)
    spec.loader.exec_module(m)
    return m


G = module("generate_t", "generate.py")
AC = module("audiocraft_t", "audiocraft-gen.py")
RV = module("review_t", "review.py")


class Generate(unittest.TestCase):
    def test_requests(self):
        r = G.veo_request("a desk at dawn", "first.png", "last.png", "9:16", 8)
        self.assertEqual(r["config"]["aspect_ratio"], "9:16")
        self.assertEqual((r["image"], r["last_frame"]), ("first.png", "last.png"))
        self.assertIn("watermark", r["config"]["negative_prompt"])
        b = G.openrouter_image_body("google/x", "a cat", [])
        self.assertEqual(b["modalities"], ["image", "text"])
        self.assertIn("No text", G.image_prompt("a cat.", "9:16"))
        self.assertIn("identical", G.restyle_prompt("ink"))

    def test_models_are_configurable(self):
        os.environ["VEO_MODEL"] = "veo-9-test"
        try:
            self.assertEqual(G.veo_request("x", None, None, "16:9", 4)["model"], "veo-9-test")
        finally:
            del os.environ["VEO_MODEL"]

    def test_estimates_never_invent_a_price(self):
        ns = type("A", (), {"price_per_second": None, "price_per_image": None})()
        self.assertTrue(G.estimate("video", 8, ns).startswith("unknown"))
        ns.price_per_second = 0.5
        self.assertTrue(G.estimate("video", 8, ns).startswith("~4.00"))

    def test_restyle_is_off_unless_the_user_asked(self):
        r = run("generate.py", "restyle", "--clip", "x.mp4", "--style-prompt", "ink", "--out", "/tmp/never.mp4", "--dry-run")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("disabled by default", r.stderr)
        r2 = run("generate.py", "restyle", "--clip", "x.mp4", "--style-prompt", "ink", "--out", "/tmp/never.mp4",
                 "--dry-run", "--user-requested")
        self.assertEqual(r2.returncode, 0, r2.stderr)

    def test_nothing_is_spent_without_yes(self):
        d = scratch(self)
        out = os.path.join(d, "g", "shot.mp4")
        r = run("generate.py", "video", "--prompt", "x", "--out", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("add --yes", r.stdout)
        self.assertFalse(os.path.exists(out))
        self.assertFalse(os.path.exists(os.path.join(d, "g", "ledger.json")))

    def test_ledger_marks_ai_generated(self):
        d = scratch(self)
        G.ledger(os.path.join(d, "a.png"), {"mode": "image"})
        G.ledger(os.path.join(d, "b.png"), {"mode": "image"})
        led = load(os.path.join(d, "ledger.json"))
        self.assertEqual(len(led), 2)
        self.assertTrue(all(e["ai_generated"] for e in led))


HS = module("heygen_sound_t", "heygen-sound.py")
RA4 = module("resolve_anchors_t4", "resolve-anchors.py")


class HeyGenSound(unittest.TestCase):
    def test_request_dedupes_names_and_music_is_strict_retrieve(self):
        req = HS.build_request([{"name": "click"}, {"name": "pop"}, {"name": "click"}, {"id": "x"}], "calm lo-fi")
        self.assertEqual([l["sfx"] for l in req["lines"]], [["click"], ["pop"]])
        self.assertEqual(req["bgm"], {"mode": "retrieve", "query": "calm lo-fi"})
        self.assertEqual(HS.build_request([], None)["bgm"], {"mode": "none"})

    def test_results_written_into_the_plan(self):
        plan, missing = HS.apply_results({"sfx": [{"id": "a", "name": "click"}, {"id": "b", "name": "nope"}]},
                                         {"click": {"src": "sfx/click.wav", "dur": 0.3}})
        self.assertEqual(plan["sfx"][0], {"id": "a", "name": "click", "src": "sfx/click.wav", "dur": 0.3, "volume": 0.3})
        self.assertEqual(missing, ["nope"])

    def test_sound_cues_resolve_to_phrases(self):
        words = [{"text": "three", "start": 3.3, "end": 3.6}, {"text": "tools", "start": 3.6, "end": 4.0}]
        out, R = RA4.resolve({"sfx": [{"id": "c", "at": "@three tools"}, {"id": "d", "at": 1.5}]}, words, 10.0)
        self.assertEqual([s["at"] for s in out["sfx"]], [3.3, 1.5])

    def test_stage_skips_cues_without_file_time_or_inside(self):
        d = scratch(self)
        spec = write(os.path.join(d, "sb.json"), {"id": "s", "duration": 4, "video": "v.mp4", "beats": [], "sfx": [
            {"id": "ok", "src": "sfx/a.wav", "at": 1.0, "dur": 0.3}, {"id": "nofile", "at": 1.0},
            {"id": "late", "src": "sfx/b.wav", "at": 9.0}, {"id": "notime", "src": "sfx/c.wav", "at": "@gone"}]})
        r = run("stage.py", "--spec", spec, "--out", os.path.join(d, "p"),
                "--style", write(os.path.join(d, "s.json"), {"fonts": {"display": {"family": "X", "files": {}}}}))
        self.assertEqual(r.returncode, 0, r.stderr)
        html = open(os.path.join(d, "p", "index.html")).read()
        self.assertIn('id="ok"', html)
        for bad in ("nofile", "late", "notime"):
            self.assertNotIn('id="%s"' % bad, html)
            self.assertIn("sound %s" % bad, r.stdout)


class AudioCraft(unittest.TestCase):
    def test_plan_loops_long_beds(self):
        self.assertEqual(AC.plan("music", 20)["crossfade_loops"], 0)
        p = AC.plan("music", 60)
        self.assertEqual((p["generate_seconds"], p["crossfade_loops"]), (28.0, 2))
        self.assertIn("audiogen", AC.plan("sfx", 2)["model"])

    def test_refuses_without_licence_acknowledgement(self):
        r = run("audiocraft-gen.py", "music", "--prompt", "x", "--seconds", "5", "--out", "/tmp/never.wav")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("CC-BY-NC", r.stderr)


class Review(unittest.TestCase):
    def test_loudness_verdict(self):
        self.assertTrue(RV.loudness_verdict({"integrated_lufs": -14.3, "true_peak_dbtp": -1.2}, "shorts")[0])
        self.assertFalse(RV.loudness_verdict({"integrated_lufs": -18.0, "true_peak_dbtp": -1.2}, "shorts")[0])
        self.assertFalse(RV.loudness_verdict({"integrated_lufs": -14.0, "true_peak_dbtp": -0.2}, "shorts")[0])

    def test_moments_cover_beats_and_cuts(self):
        ts = RV.moments({"beats": [{"in": 1.0, "out": 3.0}]}, {"cuts": [5.0]}, 10.0)
        self.assertEqual(ts, [2.0, 4.95, 5.05])
        self.assertEqual(len(RV.moments(None, None, 10.0)), 5)


@needs_ffmpeg
class EndToEnd(unittest.TestCase):
    def test_sfx_prep_trims_quiet_leading_silence(self):
        d = scratch(self)
        src, out = os.path.join(d, "c.wav"), os.path.join(d, "c2.wav")
        ffmpeg("-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono:d=0.4", "-f", "lavfi", "-i", "sine=f=1200:d=0.15",
               "-filter_complex", "[1]volume=0.05[b];[0][b]concat=n=2:v=0:a=1", src)
        r = run("sfx-prep.py", src, out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("-> -3.0 dBFS", r.stdout)
        self.assertRegex(r.stdout, r": 0\.1[0-9]+ s")

    def test_render_finishes_a_raw_file_and_review_passes(self):
        d = scratch(self)
        raw = os.path.join(d, "raw.mp4")
        ffmpeg("-f", "lavfi", "-i", "testsrc2=s=1080x1920:d=3:r=30", "-f", "lavfi",
               "-i", "sine=f=180:d=3,volume='0.3*(0.5+0.5*sin(2*PI*1.3*t))':eval=frame",
               "-c:v", "libx264", "-b:v", "14M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", raw)
        out = os.path.join(d, "out", "p-v1.mp4")
        r = run("render.py", "--public", os.path.join(d, "none"), "--raw", raw, "--out", out, "--resolution", "portrait")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        tags = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_primaries",
                               "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip()
        self.assertEqual(tags, "bt709")
        rv = run("review.py", "--final", out, "--preset", "shorts", "--res", "1080x1920")
        self.assertEqual(rv.returncode, 0, rv.stdout + rv.stderr)
        self.assertTrue(os.path.isfile(os.path.join(d, "out", "p-v1-REVIEW.md")))


if __name__ == "__main__":
    unittest.main()
