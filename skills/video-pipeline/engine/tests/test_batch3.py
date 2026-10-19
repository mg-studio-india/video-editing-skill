"""captions (grouping, catalog injection), treatments (builders), stage.py (any canvas) and the compose.py hook.
These check structure and rules; the visual check is `npx hyperframes check` + snapshots, run by the skills."""
import importlib.util, json, os, re, subprocess, sys, unittest
from .helpers import SCRIPTS, script_path, load, run, scratch, write

sys.path.insert(0, SCRIPTS)
import captions as C      # noqa: E402
import treatments as T    # noqa: E402

ENGINE = os.path.dirname(SCRIPTS)
STYLE = {"colors": {"accent": "#ffd400"}, "text_stroke": 0.045,
         "fonts": {"display": {"family": "Poppins", "files": {"800": "@engine/assets/fonts/poppins/Poppins-ExtraBold.ttf"}}},
         "captions": {"mode": "pop", "case": "upper", "portrait": {"y": 0.66, "size": 0.074}, "landscape": {"y": 0.88, "size": 0.036}}}


def W(text, s, e):
    return {"text": text, "start": s, "end": e}


class Grouping(unittest.TestCase):
    def test_max_words_sentence_and_fillers(self):
        ws = [W("So", 0, .2), W("um", .25, .4), W("here", .45, .6), W("is", .62, .7), W("the", .72, .8), W("thing.", .82, 1.1),
              W("Next", 1.2, 1.4), W("one", 1.42, 1.6)]
        g = C.group(ws, max_words=3)
        self.assertEqual([[w["text"] for w in x["words"]] for x in g], [["So", "here", "is"], ["the", "thing"], ["Next", "one"]])

    def test_pause_and_cut_break_groups(self):
        ws = [W("a", 0, .2), W("b", .21, .4), W("c", .7, .9), W("d", .91, 1.1)]
        self.assertEqual(len(C.group(ws, max_words=5)), 2)                      # 0.3 s pause
        ws2 = [W("a", 0, .2), W("b", .21, .4), W("c", .41, .6)]
        self.assertEqual(len(C.group(ws2, cuts=[0.405], max_words=5)), 2)       # never across a jump cut

    def test_devanagari_danda_ends_a_sentence(self):
        ws = [W("यह", 0, .2), W("है।", .21, .4), W("अब", .41, .6)]
        self.assertEqual(len(C.group(ws, max_words=5)), 2)

    def test_numbers_and_listed_words_are_emphasised(self):
        g = C.group([W("lost", 0, .2), W("70%", .21, .5), W("viewers", .51, .8)], max_words=3, emphasis=["viewers"])
        self.assertEqual([w["em"] for w in g[0]["words"]], [False, True, True])

    def test_small_gaps_hold_instead_of_flicker(self):
        g = C.group([W("a.", 0, .3), W("b", .8, 1.0)], max_words=3)
        self.assertAlmostEqual(g[0]["end"], 0.78, places=2)


COMPONENT = """<html><head><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap" rel="stylesheet" />
<style>html,body{width:1920px;height:1080px}.g{bottom: 140px;font-family: "Montserrat", sans-serif;}</style></head>
<body><div data-composition-id="caption-x" data-start="0" data-duration="8" data-width="1920" data-height="1080"></div>
<script>var COLOR_INACTIVE = "#A6A6A6";
var WORDS = [ { text: "demo", start: 0.0, end: 0.3 } ];
var RAW_GROUPS = [ [0, 0] ];
var nextStart = 1 < 2 ? 0 : 8.0;</script></body></html>"""


class Inject(unittest.TestCase):
    def test_words_groups_canvas_length_font_and_overrides(self):
        g = C.group([W("one", 0, .3), W("two", .31, .6), W("three.", .61, .9), W("four", 1.5, 1.8)], max_words=3)
        html, notes = C.inject(COMPONENT, g, 1080, 1920, 12.5, y=0.66, font=("Poppins", "@font-face{}"),
                               sets={"COLOR_INACTIVE": "#5E5E5E"})
        self.assertNotIn("cdn.jsdelivr.net", html)
        self.assertNotIn("fonts.googleapis", html)
        self.assertIn('"text": "one"', html)
        self.assertIn("[[0, 2], [3, 3]]", html)
        self.assertIn('data-duration="12.500"', html)
        self.assertIn('data-width="1080"', html)
        self.assertIn("width:1080px;height:1920px", html)
        self.assertIn("bottom: 653px", html)
        self.assertIn(": 12.500;", html)
        self.assertIn('COLOR_INACTIVE = "#5E5E5E"', html)
        self.assertIn("font-family: 'Poppins', sans-serif;", html)

    def test_unknown_shape_is_refused(self):
        with self.assertRaises(SystemExit):
            C.inject("<html><script>var LINES = [];</script></html>", [], 1080, 1920, 5)


class Builders(unittest.TestCase):
    def ctx(self, w=1080, h=1920):
        return {"W": w, "H": h, "style": STYLE, "track": 10, "camera_sel": "#cam"}

    def test_every_type_builds_and_names_its_placement(self):
        beats = {"hero": {"text": "Big idea", "em": [1]}, "cards": {"items": [["A", 1.2], ["B", 1.6]], "title": "Two"},
                 "whiteout": {}, "drawer": {"title": "Note", "lines": ["one line"]},
                 "split": {"a": {"src": "a.mp4"}, "b": {"src": "b.mp4"}}, "behind": {"text": "70%"},
                 "clip": {"src": "broll/x.mp4", "label": "x"}, "block": {"comp_id": "x-post", "src": "compositions/x-post.html"},
                 "captions": {"groups": C.group([W("hi", 1, 1.3)])}}
        where = {}
        for t, extra in beats.items():
            b = {"type": t, "id": t + "1", "in": 1.0, "out": 3.0, **extra}
            html, css, js, place = T.build(b, self.ctx())
            self.assertIn('data-start="', html, t)
            where[t] = place
        self.assertEqual(where["behind"], "behind")
        self.assertEqual({where[t] for t in ("split", "clip", "block")}, {"root"})

    def test_hosts_are_never_tweened(self):
        for t, extra in {"hero": {"text": "x"}, "drawer": {"title": "x"}, "cards": {"items": [["a", 1.5]]}}.items():
            _, _, js, _ = T.build({"type": t, "id": "z", "in": 1, "out": 3, **extra}, self.ctx())
            self.assertFalse([l for l in js if "#host-" in l], t)

    def test_portrait_panels_sit_below_the_face(self):
        _, css, _, _ = T.build({"type": "drawer", "id": "d", "in": 1, "out": 3, "title": "x"}, self.ctx())
        top = int(re.search(r"top:(\d+)px", css).group(1))
        self.assertGreater(top / 1920, 0.45)

    def test_layered_head_text_is_marked_as_intentional_occlusion(self):
        html, _, _, _ = T.build({"type": "behind", "id": "b", "in": 1, "out": 3, "text": "70%"}, self.ctx())
        self.assertIn("data-layout-allow-occlusion", html)

    def test_engine_font_paths_resolve(self):
        self.assertTrue(os.path.isfile(T.resolve_font("@engine/assets/fonts/poppins/Poppins-Bold.ttf", "/nowhere")))


class Stage(unittest.TestCase):
    def test_vertical_page_with_camera_matte_captions_and_step_aside(self):
        d = scratch(self)
        pub = os.path.join(d, "public")
        write(os.path.join(pub, "transcript.json"), {"words": [W("one", .5, .8), W("two", .82, 1.1), W("three.", 1.12, 1.5),
                                                               W("four", 2.2, 2.5), W("five", 2.52, 2.9)]})
        spec = write(os.path.join(d, "storyboard.json"), {
            "id": "s1", "canvas": [1080, 1920], "duration": 4.0, "video": "in.mp4", "matte": "m.webm",
            "captions": {"source": "transcript.json"},
            "beats": [{"type": "behind", "id": "big", "text": "70%", "in": 0.4, "out": 1.6},
                      {"type": "drawer", "id": "dr", "title": "Note", "in": 2.0, "out": 3.5}],
            "camera": [["punch", 0.5, 1.1], ["set", 1.6, 1.0]]})
        st = write(os.path.join(d, "style.json"), STYLE)
        r = run("stage.py", "--spec", spec, "--out", pub, "--style", st)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        html = open(os.path.join(pub, "index.html")).read()
        self.assertIn('data-composition-id="s1"', html)
        self.assertIn('data-width="1080" data-height="1920"', html)
        self.assertIn('window.__timelines["s1"] = tl', html)
        self.assertIn("tl.to('#cam', { scale: 1.100, duration: 0.32", html)
        self.assertLess(html.index('id="host-big"'), html.index('id="matte"'))    # text sits under the matte
        self.assertIn("data-layout-allow-overflow", html)
        self.assertTrue(os.path.isfile(os.path.join(pub, "fonts", "Poppins-ExtraBold.ttf")))
        self.assertRegex(html, r'id="cg-1" style="top:\d+px"')                    # the group under the drawer stepped aside

    def test_overlapping_panels_warn(self):
        d = scratch(self)
        spec = write(os.path.join(d, "sb.json"), {"id": "s", "duration": 4, "video": "v.mp4", "beats": [
            {"type": "drawer", "id": "a", "title": "x", "in": 0.5, "out": 2.5},
            {"type": "cards", "id": "b", "items": [["x", 1.5]], "in": 1.5, "out": 3.0}]})
        r = run("stage.py", "--spec", spec, "--out", os.path.join(d, "p"), "--style", write(os.path.join(d, "s.json"), STYLE))
        self.assertIn("WARN: a and b are on screen together", r.stdout)

    def test_unresolved_beat_stops_the_build(self):
        d = scratch(self)
        spec = write(os.path.join(d, "sb.json"), {"id": "s", "duration": 4, "video": "v.mp4",
                                                  "beats": [{"type": "hero", "id": "h", "text": "x", "in": None, "out": None, "unresolved": True}]})
        r = run("stage.py", "--spec", spec, "--out", os.path.join(d, "p"), "--style", write(os.path.join(d, "s.json"), STYLE))
        self.assertNotEqual(r.returncode, 0)


class Palette(unittest.TestCase):
    def test_finds_the_accent_and_its_share(self):
        import numpy as np
        spec = importlib.util.spec_from_file_location("palette_t", script_path("palette.py"))
        P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
        px = np.concatenate([np.tile([255, 212, 0], (300, 1)), np.tile([20, 20, 20], (700, 1))]).astype(float)
        c, share = P.kmeans(px, 2)
        self.assertEqual(P.describe(c[0])["kind"], "near-black")
        self.assertAlmostEqual(float(share[1]), 0.3, places=2)
        self.assertEqual(P.describe(c[1])["hex"], "#FFD400")


class ComposeHook(unittest.TestCase):
    def test_compose_builds_treatments_on_16x9_and_warns_on_captions_with_lines(self):
        d = scratch(self)
        pub = os.path.join(d, "public")
        write(os.path.join(pub, "transcript.json"), {"words": [W("hello", .5, .9), W("there", .92, 1.3)]})
        spec = write(os.path.join(d, "sb.json"), {"id": "c1", "duration": 4.0, "video": "input-video.mp4",
                                                  "captions": {"source": "transcript.json"},
                                                  "beats": [{"type": "line", "id": "l1", "text": "Hi there", "in": 0.3, "out": 2.0, "anchor": "-"},
                                                            {"type": "whiteout", "id": "wo", "in": 2.2, "out": 2.9},
                                                            {"type": "cards", "id": "cd", "items": [["A", 3.0]], "in": 2.9, "out": 3.9}]})
        r = run("compose.py", "--spec", spec, "--out", pub, "--style", write(os.path.join(d, "s.json"), STYLE))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("WARN: captions and lower lines", r.stdout)
        html = open(os.path.join(pub, "index.html")).read()
        for needle in ('id="host-wo-h"', 'class="cards-cd"', 'id="cap-rail"', "font-family:'Poppins'"):
            self.assertIn(needle, html)


if __name__ == "__main__":
    unittest.main()
