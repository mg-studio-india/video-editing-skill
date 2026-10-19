"""transcribe.py (whisper.cpp in the engine's transcript shape) and audio-chain.py (the ordered voice chain)."""
import importlib.util, json, os, subprocess, sys, unittest
from .helpers import SCRIPTS, script_path, fake_exe, ffmpeg, load, needs_ffmpeg, run, scratch, write


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, script_path(filename))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, SCRIPTS)
    spec.loader.exec_module(m)
    return m


T = module("transcribe_mod", "transcribe.py")
A = module("audio_chain_mod", "audio-chain.py")

FAKE_WHISPER = r'''#!/usr/bin/env python3
import json, sys
a = sys.argv[1:]
prefix = a[a.index("-of") + 1]
prompt = a[a.index("--prompt") + 1] if "--prompt" in a else ""
words = [("So",.5,.7),("um",.7,.9),("today",.9,1.3),(".",1.3,1.35),("Next",2.0,2.4),("step",2.4,2.9)]
tr = [{"offsets": {"from": int(s*1000), "to": int(e*1000)}, "text": w if w == "." else " " + w} for w, s, e in words]
json.dump({"result": {"language": "en"}, "transcription": tr, "prompt_seen": prompt}, open(prefix + ".json", "w"))
open(prefix + ".prompt", "w").write(prompt)
'''


class Windows(unittest.TestCase):
    def test_short_file_is_one_window(self):
        self.assertEqual(T.plan_windows(20.0, [], 25), [(0.0, 20.0)])

    def test_splits_at_the_last_silence_in_the_back_half(self):
        quiet = [(5.0, 5.4), (18.0, 18.6), (21.0, 21.4), (44.0, 44.4)]
        self.assertEqual(T.plan_windows(60.0, quiet, 25), [(0.0, 21.2), (21.2, 44.2), (44.2, 60.0)])

    def test_hard_split_when_no_silence(self):
        self.assertEqual(T.plan_windows(55.0, [], 25), [(0.0, 25.0), (25.0, 50.0), (50.0, 55.0)])

    def test_merge_never_overlaps_at_a_seam(self):
        a = {"language": "en", "words": [{"w": "a", "start": 0.0, "end": 1.0}, {"w": "b", "start": 1.0, "end": 2.0}]}
        b = {"language": "en", "words": [{"w": "b", "start": 1.5, "end": 2.0}, {"w": "c", "start": 2.1, "end": 2.5}]}
        words, _, lang = T.merge([a, b])
        self.assertEqual([w["w"] for w in words], ["a", "b", "c"])
        self.assertEqual(lang, "en")

    def test_engine_shape_has_text_and_w(self):
        self.assertEqual(T.to_engine_shape([{"w": "hi", "start": 1.0, "end": 1.2}]),
                         [{"text": "hi", "w": "hi", "start": 1.0, "end": 1.2}])


@needs_ffmpeg
class TranscribeEndToEnd(unittest.TestCase):
    def test_writes_the_shape_the_cut_tools_read(self):
        d = scratch(self)
        fake = fake_exe(os.path.join(d, "whisper-cli"), FAKE_WHISPER)
        model = write(os.path.join(d, "ggml-large-v3.bin"), "")
        clip = os.path.join(d, "clip.wav")
        ffmpeg("-f", "lavfi", "-i", "sine=f=200:d=4", clip)
        env = {**os.environ, "WATCH_WHISPER_CPP_BIN": fake, "WATCH_WHISPER_MODEL": model, "HOME": d}
        out = os.path.join(d, "transcript.json")
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "transcribe.py"), clip, "--out", out],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        t = load(out)
        self.assertEqual(t["engine"], "whisper.cpp")
        self.assertEqual([w["text"] for w in t["words"]], ["So", "um", "today.", "Next", "step"])
        self.assertTrue(all("w" in w and "start" in w and "end" in w for w in t["words"]))
        # the cut tools read it: phrase-times finds a phrase in it
        p = run("phrase-times.py", "--transcript", out, "next step")
        self.assertIn("2.00-2.90", p.stdout, p.stdout + p.stderr)


class AudioDecisions(unittest.TestCase):
    def test_denoise_scales_with_the_floor(self):
        self.assertEqual([A.denoise_level(f) for f in (-80, -55, -45, -35)], ["off", "light", "medium", "strong"])

    def test_no_filter_when_off(self):
        self.assertEqual(A.denoise_filters("off", None, -70, -20), [])

    def test_afftdn_floor_sits_above_measured_floor_but_clear_of_speech(self):
        self.assertEqual(A.afftdn_floor(-44.0, -12.0), -32.0)     # floor + 12
        self.assertEqual(A.afftdn_floor(-30.0, -25.0), -40.0)     # capped 15 dB under speech
        self.assertEqual(A.afftdn_floor(-10.0, 0.0), -20.0)       # clamped

    def test_strong_uses_rnnoise_only_with_a_model(self):
        self.assertEqual(len(A.denoise_filters("strong", None, -35, -10)), 1)
        f = A.denoise_filters("strong", "/m/voice.rnnn", -35, -10)
        self.assertTrue(f[0].startswith("arnndn=") and "mix=0.85" in f[0] and f[1].startswith("afftdn="))

    def test_compressor_has_no_hidden_makeup(self):
        self.assertIn("makeup=1", A.compressor())                  # linear factor: 2 would be +6 dB on the hiss

    def test_floor_and_snr_from_pcm(self):
        import numpy as np
        rate = 16000
        quiet = (np.random.default_rng(1).standard_normal(rate) * 0.001 * 32768).astype(np.int16)
        loud = (np.sin(np.arange(rate * 4) * 2 * np.pi * 200 / rate) * 0.3 * 32768).astype(np.int16)
        pcm = np.concatenate([quiet, loud])
        self.assertLess(A.floor_from_pcm(pcm), -55)
        self.assertGreater(A.snr_from_pcm(pcm), 40)


@needs_ffmpeg
class AudioEndToEnd(unittest.TestCase):
    def make(self, d, hiss):
        out = os.path.join(d, "voice-%s.wav" % hiss)
        ffmpeg("-f", "lavfi", "-i", "sine=f=180:d=9,volume='0.6*(0.5+0.5*sin(2*PI*1.3*t))*gt(mod(t\\,3)\\,0.6)':eval=frame",
               "-f", "lavfi", "-i", "anoisesrc=c=white:a=%s:d=9" % hiss,
               "-filter_complex", "[0][1]amix=inputs=2:normalize=0,aformat=sample_rates=48000", out)
        return out

    def test_clean_leaves_a_clean_file_alone_and_denoises_a_noisy_one(self):
        d = scratch(self)
        for hiss, level in (("0.0003", "off"), ("0.02", "medium")):
            rep = os.path.join(d, "r.json")
            r = run("audio-chain.py", "clean", self.make(d, hiss), "--out", os.path.join(d, "c.wav"), "--report", rep)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            j = load(rep)
            self.assertEqual(j["denoise"], level)
            if level == "medium":
                self.assertGreater(j["after"]["snr_db"] - j["before"]["snr_db"], 4.0)

    def test_master_hits_target_and_keeps_the_picture(self):
        d = scratch(self)
        wav = self.make(d, "0.002")
        clip = os.path.join(d, "clip.mp4")
        ffmpeg("-f", "lavfi", "-i", "testsrc2=s=320x180:d=9:r=30", "-i", wav, "-c:v", "libx264", "-c:a", "aac",
               "-shortest", clip)
        bed = os.path.join(d, "bed.wav")
        ffmpeg("-f", "lavfi", "-i", "sine=f=440:d=9", bed)
        rep = os.path.join(d, "r.json")
        out = os.path.join(d, "master.mp4")
        r = run("audio-chain.py", "master", clip, "--out", out, "--music", bed, "--report", rep)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        j = load(rep)
        self.assertTrue(j["pass"])
        self.assertAlmostEqual(j["after"]["integrated_lufs"], -14.0, delta=1.0)
        self.assertLessEqual(j["after"]["true_peak_dbtp"], -0.9)
        streams = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", out],
                                 capture_output=True, text=True).stdout.split()
        self.assertEqual(sorted(streams), ["audio", "video"])

    def test_master_auto_denoises_noisy_source(self):
        d = scratch(self)
        wav = self.make(d, "0.03")  # noisy background (road/room hiss)
        clip = os.path.join(d, "noisy_clip.mp4")
        ffmpeg("-f", "lavfi", "-i", "testsrc2=s=320x180:d=4:r=30", "-i", wav, "-c:v", "libx264", "-c:a", "aac",
               "-shortest", clip)
        rep = os.path.join(d, "r.json")
        out = os.path.join(d, "master_noisy.mp4")
        r = run("audio-chain.py", "master", clip, "--out", out, "--report", rep)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        j = load(rep)
        self.assertIn(j["denoise"], ("medium", "strong"))
        self.assertTrue(j["pass"])

    def test_master_denoise_explicit_off(self):
        d = scratch(self)
        wav = self.make(d, "0.03")
        clip = os.path.join(d, "noisy_clip2.mp4")
        ffmpeg("-f", "lavfi", "-i", "testsrc2=s=320x180:d=4:r=30", "-i", wav, "-c:v", "libx264", "-c:a", "aac",
               "-shortest", clip)
        rep = os.path.join(d, "r.json")
        out = os.path.join(d, "master_off.mp4")
        r = run("audio-chain.py", "master", clip, "--out", out, "--denoise", "off", "--report", rep)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        j = load(rep)
        self.assertEqual(j["denoise"], "off")


if __name__ == "__main__":
    unittest.main()
