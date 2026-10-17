"""Pure-logic tests (no ffmpeg or whisper needed). Run: python3 -m unittest discover -s tests"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import editplan as ep  # noqa: E402
import fingerprint as fp  # noqa: E402
import frames  # noqa: E402
import pacing  # noqa: E402
import shots as shots_mod  # noqa: E402
import speech  # noqa: E402
import storyboard as sb  # noqa: E402
import transcribe_cpp as asr  # noqa: E402
from runtime import fmt_time, parse_time, parse_time_list  # noqa: E402


def W(t, s, e):
    return {"w": t, "start": s, "end": e}


class TimeTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_time("90"), 90.0)
        self.assertEqual(parse_time("1:30"), 90.0)
        self.assertEqual(parse_time("1:01:01.5"), 3661.5)
        self.assertIsNone(parse_time(None))
        with self.assertRaises(ValueError):
            parse_time("a:b")

    def test_format(self):
        self.assertEqual(fmt_time(65), "01:05")
        self.assertEqual(fmt_time(65.34, 1), "01:05.3")
        self.assertEqual(fmt_time(3725), "01:02:05")

    def test_list(self):
        self.assertEqual(parse_time_list("0:12, 5,0:12"), [5.0, 12.0])


class ShotTests(unittest.TestCase):
    def test_build_shots_covers_range_without_gaps(self):
        cuts = [{"t": 2.0, "score": 0.9}, {"t": 4.0, "score": 0.25}, {"t": 4.05, "score": 0.9}]
        shots = shots_mod.build_shots(cuts, 0.0, 10.0)
        self.assertEqual([s["start"] for s in shots], [0.0, 2.0, 4.0])  # flicker at 4.05 ignored
        self.assertEqual(shots[-1]["end"], 10.0)
        self.assertEqual([s["transition_in"] for s in shots], ["start", "cut", "soft"])
        for a, b in zip(shots, shots[1:]):
            self.assertAlmostEqual(a["end"], b["start"])


class PacingTests(unittest.TestCase):
    def test_not_capped_by_frame_budget(self):
        # 300 cuts in 300s must report 60 cuts/min no matter how many frames we sample.
        cuts = [{"t": float(i), "score": 0.9} for i in range(1, 300)]
        shots = shots_mod.build_shots(cuts, 0.0, 300.0)
        p = pacing.compute_pacing(shots, 0.0, 300.0)
        self.assertEqual(p["shot_count"], 300)
        self.assertAlmostEqual(p["cuts_per_minute"], 59.8, places=1)
        self.assertEqual(p["pace"], "frenetic")

    def test_hook_counts(self):
        shots = shots_mod.build_shots([{"t": 1.0, "score": 1}, {"t": 2.0, "score": 1}, {"t": 8.0, "score": 1}], 0, 20)
        h = pacing.compute_pacing(shots, 0, 20)["hook"]
        self.assertEqual((h["cuts_in_first_3s"], h["cuts_in_first_10s"]), (2, 3))


class WhisperParseTests(unittest.TestCase):
    DATA = {"result": {"language": "en"}, "transcription": [
        {"offsets": {"from": 0, "to": 10}, "text": " [_BEG_]"},
        {"offsets": {"from": 100, "to": 500}, "text": " Hello"},
        {"offsets": {"from": 500, "to": 520}, "text": ","},
        {"offsets": {"from": 600, "to": 1000}, "text": " world"},
        {"offsets": {"from": 1000, "to": 1100}, "text": "."},
        {"offsets": {"from": 1500, "to": 2500}, "text": " [MUSIC]"},
        {"offsets": {"from": 2600, "to": 3000}, "text": " [BLANK_AUDIO]"},
        {"offsets": {"from": 3100, "to": 3400}, "text": " Thanks"},
    ]}

    def test_words_cues_and_offset(self):
        r = asr.parse_whisper_json(self.DATA, offset=2.0)
        self.assertEqual([w["w"] for w in r["words"]], ["Hello,", "world.", "Thanks"])
        self.assertAlmostEqual(r["words"][0]["start"], 2.1)
        self.assertEqual([c["text"] for c in r["sound_cues"]], ["MUSIC"])  # BLANK_AUDIO ignored
        self.assertEqual(r["language"], "en")

    def test_no_overlap_and_positive_duration(self):
        data = {"transcription": [{"offsets": {"from": 0, "to": 900}, "text": " a"},
                                  {"offsets": {"from": 500, "to": 500}, "text": " b"}]}
        ws = asr.parse_whisper_json(data)["words"]
        self.assertLessEqual(ws[0]["end"], ws[1]["start"])
        self.assertGreater(ws[1]["end"], ws[1]["start"])

    def test_collapse_loops(self):
        words = [W("Thank", i * 1.0, i * 1.0 + .5) if i % 2 == 0 else W("you.", i * 1.0, i * 1.0 + .5) for i in range(12)]
        out, removed = asr.collapse_loops(words)
        self.assertLess(len(out), 6)
        self.assertGreater(removed, 0)
        keep, removed = asr.collapse_loops([W("no", 0, .2), W("no", .3, .5), W("no", .6, .8)])
        self.assertEqual(removed, 0)  # short legitimate repetition untouched

    def test_segments_split_on_punctuation_and_pause(self):
        words = [W("Hi", 0, .3), W("there.", .3, .7), W("Next", .8, 1.1), W("bit", 3.0, 3.3)]
        segs = asr.words_to_segments(words)
        self.assertEqual([s["text"] for s in segs], ["Hi there.", "Next", "bit"])


class SpeechTests(unittest.TestCase):
    def test_fillers_and_pauses(self):
        words = [W("so", 0, .2), W("um", .3, .6), W("you", 2.0, 2.2), W("know", 2.2, 2.4), W("it", 2.5, 2.6)]
        f = speech.find_fillers(words)
        self.assertEqual([(x["kind"], x["text"]) for x in f], [("hard", "um"), ("soft", "you know")])
        self.assertEqual(len(speech.find_pauses(words)), 1)
        st = speech.speech_stats(words, 0, 10)
        self.assertEqual(st["filler_count"], 1)
        self.assertEqual(st["soft_filler_count"], 1)

    def test_cut_alignment_labels(self):
        shots = [{"id": 1, "start": 0, "end": 5}, {"id": 2, "start": 5, "end": 12},
                 {"id": 3, "start": 12, "end": 15}, {"id": 4, "start": 15, "end": 20}]
        segments = [{"start": 4.6, "end": 9.0, "text": "a"}, {"start": 9.5, "end": 15.3, "text": "b"}]
        res = speech.cut_alignment(shots, segments, [])
        self.assertEqual(shots[1]["cut_audio"], "j_lead")      # sentence began 0.4s before the cut at 5
        self.assertEqual(shots[2]["cut_audio"], "mid_speech")  # cut at 12 is deep inside sentence b
        self.assertEqual(shots[3]["cut_audio"], "l_trail")     # sentence b ends 0.3s after the cut at 15
        self.assertEqual(sum(res["counts"].values()), 3)

    def test_cut_on_pause(self):
        shots = [{"id": 1, "start": 0, "end": 5}, {"id": 2, "start": 5, "end": 10}]
        res = speech.cut_alignment(shots, [{"start": 0.5, "end": 3.0, "text": "a"}], [])
        self.assertEqual(shots[1]["cut_audio"], "on_pause")
        self.assertEqual(res["counts"]["on_pause"], 1)


class EditPlanTests(unittest.TestCase):
    WORDS = [W("So", .5, .7), W("today", .7, 1.1), W("I", 1.1, 1.2), W("want", 1.2, 1.4),
             W("So", 2.0, 2.2), W("today", 2.2, 2.6), W("I", 2.6, 2.7), W("want", 2.7, 2.9), W("um", 2.9, 3.2),
             W("to", 3.3, 3.4), W("show", 3.4, 3.8), W("you.", 3.8, 4.2), W("Next", 6.5, 6.9), W("step.", 6.9, 7.5)]

    def test_retake_filler_pause_removed(self):
        keep, removed = ep.build_keep_ranges(self.WORDS, asr.words_to_segments(self.WORDS), 0.0, 10.0)
        reasons = {r for x in removed for r in x["reasons"]}
        self.assertTrue({"retake", "filler", "pause", "lead-in", "tail"} <= reasons)
        stats = ep.cutlist_stats(keep, removed, 0.0, 10.0)
        self.assertLess(stats["new_duration"], 5.0)
        for a, b in zip(keep, keep[1:]):
            self.assertLess(a["out"], b["in"])

    def test_no_words_keeps_everything(self):
        keep, removed = ep.build_keep_ranges([], [], 0.0, 12.0)
        self.assertEqual(keep, [{"in": 0.0, "out": 12.0}])
        self.assertEqual(removed, [])

    def test_timeline_and_captions(self):
        keep = [{"in": 1.0, "out": 2.0}, {"in": 5.0, "out": 6.0}]
        tmap = ep.timeline_map(keep)
        self.assertEqual(ep.map_time(1.5, tmap), 0.5)
        self.assertEqual(ep.map_time(5.5, tmap), 1.5)
        self.assertIsNone(ep.map_time(3.0, tmap))
        words = [W("a", 1.1, 1.3), W("b", 1.4, 1.6), W("gone", 3.0, 3.2), W("c", 5.1, 5.3)]
        caps = ep.build_captions(words, tmap, 2)
        self.assertEqual([c["text"] for c in caps], ["a b", "c"])
        self.assertAlmostEqual(caps[1]["start"], 1.1)

    def test_edit_plan_shape(self):
        meta = {"path": "/x.mp4", "width": 1080, "height": 1920, "fps": 30}
        keep = [{"in": 0.0, "out": 2.0}, {"in": 4.0, "out": 5.0}]
        plan = ep.make_edit_plan(meta, keep, [], {"jump_cut_zoom": True})
        self.assertEqual(plan["duration"], 3.0)
        self.assertEqual([t["type"] for t in plan["tracks"]], ["video", "audio", "captions"])
        self.assertEqual(plan["tracks"][0]["clips"][1]["start"], 2.0)
        self.assertEqual(len(plan["zooms"]), 1)

    def test_qa_flags(self):
        analysis = {
            "meta": {"duration": 60.0}, "shots": [{"id": 1, "start": 0, "end": 30, "duration": 30}],
            "pacing": {"hook": {"first_shot_duration": 30, "cuts_in_first_10s": 0}},
            "speech": {"has_speech": True, "time_to_first_word": 3.0, "fillers_per_minute": 9, "words_per_minute": 100},
            "audio": {"silences": [{"start": 10, "end": 13, "duration": 3}],
                      "loudness": {"integrated_lufs": -26.0, "true_peak_dbtp": 0.5}},
            "black": [],
        }
        text = " ".join(f["issue"] for f in ep.qa_flags(analysis))
        for needle in ("Dead air", "First word", "filler", "Slow visual hook", "Long unbroken", "Loudness", "True peak"):
            self.assertIn(needle, text)


class FingerprintTests(unittest.TestCase):
    def _fp(self, cpm, lufs):
        return {"pacing": {"cuts_per_minute": cpm, "median_shot_length": 60 / cpm, "p90_shot_length": 3,
                           "hook": {"cuts_in_first_10s": 5, "first_shot_duration": 1.0}},
                "speech": {"time_to_first_word": .4, "words_per_minute": 170, "pauses_per_minute": 8,
                           "longest_pause": .8, "fillers_per_minute": 0},
                "audio": {"integrated_lufs": lufs, "silence_ratio": .03}, "cut_alignment": {"j_or_l_share": .3}}

    def test_compare_verdicts(self):
        rows = {r["metric"]: r for r in fp.compare(self._fp(30, -14), self._fp(10, -14))}
        self.assertEqual(rows["Cuts per minute"]["verdict"], "lower")
        self.assertEqual(rows["Integrated loudness"]["verdict"], "similar")

    def test_missing_metric_is_na(self):
        rows = fp.compare({"pacing": {}}, {"pacing": {}})
        self.assertTrue(all(r["verdict"] == "n/a" for r in rows))

    def test_unfilled_count(self):
        f = {"qualitative": {"a": None, "b": {"c": None, "d": "x"}}}
        self.assertEqual(fp.count_unfilled(f), 2)


class FramePickTests(unittest.TestCase):
    def _shots(self, n, dur=2.0):
        return [{"id": i + 1, "start": i * dur, "end": (i + 1) * dur, "duration": dur} for i in range(n)]

    def test_budget_respected_and_hook_protected(self):
        shots = self._shots(100)
        items = frames.pick_times(shots, 0, 200, budget=30, hook_seconds=10)
        self.assertLessEqual(len(items), 30)
        hook_shots = {i["shot"] for i in items if i["t"] < 10}
        self.assertEqual(hook_shots, {1, 2, 3, 4, 5})
        self.assertIn(100, {i["shot"] for i in items})  # last shot kept

    def test_pinned_cue_survives_budget(self):
        items = frames.pick_times(self._shots(100), 0, 200, budget=10, pinned=[123.4])
        self.assertTrue(any(i["kind"] == "cue" and abs(i["t"] - 123.4) < 1e-6 for i in items))

    def test_few_cuts_falls_back_to_uniform(self):
        items = frames.pick_times(self._shots(2, 100.0), 0, 200, budget=20)
        self.assertTrue(all(i["kind"] == "uniform" for i in items))
        self.assertGreaterEqual(len(items), 8)

    def test_long_shot_gets_extras_when_budget_allows(self):
        shots = self._shots(10)
        shots.append({"id": 11, "start": 20.0, "end": 50.0, "duration": 30.0})
        items = frames.pick_times(shots, 0, 50, budget=40)
        self.assertGreater(sum(1 for i in items if i["kind"] == "extra"), 0)


class StoryboardLintTests(unittest.TestCase):
    def test_lint_flags_markers_and_passes_when_clean(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.md"
            p.write_text("# T\n| 1 | " + sb.FILL + " |\n", encoding="utf-8")
            self.assertEqual(len(sb.lint(p)), 1)
            p.write_text("# T\n| 1 | close-up |\n", encoding="utf-8")
            self.assertEqual(sb.lint(p), [])

    def test_instruction_text_never_contains_marker(self):
        analysis = {"meta": {"filename": "a.mp4", "duration": 5, "width": 1, "height": 1, "orientation": "square",
                             "fps": 30}, "range": {"start": 0, "end": 5}, "pacing": {}, "shots": [], "speech": {},
                    "audio": {}}
        md = sb.render(analysis, None, None, None, None)
        header_lines = [l for l in md.splitlines() if l.startswith("Frame = ")]
        self.assertTrue(header_lines)
        self.assertNotIn(sb.FILL, header_lines[0])


if __name__ == "__main__":
    unittest.main()
