#!/usr/bin/env python3
"""apply-cut.py: cut-list.json -> frame-accurate flat cut, its lossless voice track, and cut-map.json.

* Picture and sound are trimmed at the same frame-snapped times. Edges snap OUTWARD (start down, end up) so a cut
  placed in silence can never move into a word.
* --audio takes the cleaned voice WAV (sample 0 = the first video frame); otherwise the input's own audio is used.
* --tail holds the last frame (and silence) for the fade to black; the fade itself is drawn by the composition.
* Writes <out>.mp4 (picture + AAC preview sound), --voice-out WAV (lossless, what the render masters) and cut-map.json.
"""
import argparse, json, math, os, subprocess, sys
from fractions import Fraction

ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True, help="CFR video (the ingest copy)")
ap.add_argument("--audio", help="cleaned voice WAV aligned to the first video frame (default: the input's audio)")
ap.add_argument("--cut-list", required=True)
ap.add_argument("--out", required=True, help="flat-cut video (e.g. .video-pipeline/hyperframes/input-video.mp4)")
ap.add_argument("--voice-out", help="lossless flat-cut voice WAV (default: voice.wav next to --out)")
ap.add_argument("--tail", type=float, default=0.0, help="seconds of held last frame + silence after the final word")
ap.add_argument("--crf", type=int, default=14, help="H.264 CRF (default: 14, visually lossless)")
ap.add_argument("--preset", default="medium", help="x264 preset (default: medium)")
ap.add_argument("--grade", help="grade preset from grade.py (e.g. enhanced-natural, dynamic)")
args = ap.parse_args()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grade  # noqa: E402  (also moves this process into the engine venv)


def probe(path, *entries):
    r = subprocess.run(["ffprobe", "-v", "error"] + [x for e in entries for x in ("-show_entries", e)] + ["-of", "json", path],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


# ---- source frame grid ---------------------------------------------------------------------------------
info = probe(args.input, "stream=codec_type,r_frame_rate,start_time", "format=start_time")
vs = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
if vs is None:
    sys.exit("no video stream in %s" % args.input)
rate = Fraction(vs.get("r_frame_rate", "30/1"))
if rate <= 0:
    rate = Fraction(30)
# Inside the filter graph the first video frame sits at (video start_time - format start_time).
origin = num(vs.get("start_time")) - num(info.get("format", {}).get("start_time"))
half = 0.5 / float(rate)
k_down = lambda t: max(0, int(math.floor((Fraction(t) - Fraction(origin)) * rate + Fraction(1, 10 ** 6))))
k_up = lambda t: int(math.ceil((Fraction(t) - Fraction(origin)) * rate - Fraction(1, 10 ** 6)))
at = lambda k: origin + float(Fraction(k) / rate)

cl = json.load(open(args.cut_list))
FADE = 0.012                 # click guard at every join; edges already sit in silence
use_wav = bool(args.audio)
a_in = "1:a" if use_wav else "0:a"
parts, chain, cut_map, skipped = [], [], [], []
flat = Fraction(0)
prev_k1 = -1
for s in cl["kept"]:
    k0, k1 = k_down(s["start"]), k_up(s["end"])
    k0 = max(k0, prev_k1)               # outward snapping never makes two kept ranges overlap
    if k1 <= k0:
        skipped.append(s); continue
    prev_k1 = k1
    i = len(parts)
    t0, t1 = at(k0), at(k1)
    d = float(Fraction(k1 - k0) / rate)
    a0, a1 = (t0 - origin, t1 - origin) if use_wav else (t0, t1)
    chain.append("[0:v]trim=start=%.6f:end=%.6f,setpts=PTS-STARTPTS[v%d]" % (max(0.0, t0 - half), t1 - half, i))
    chain.append("[%s]atrim=start=%.6f:end=%.6f,asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=%.3f,afade=t=out:st=%.6f:d=%.3f[a%d]"
                 % (a_in, max(0.0, a0), a1, FADE, max(0.0, d - FADE), FADE, i))
    parts.append("[v%d][a%d]" % (i, i))
    f0 = flat; flat += Fraction(k1 - k0) / rate
    cut_map.append({"flat_start": round(float(f0), 6), "flat_end": round(float(flat), 6),
                    "src_start": round(t0 - origin, 6), "src_end": round(t1 - origin, 6), "frames": k1 - k0})
if not parts:
    sys.exit("no kept segment is at least one frame long")

chain.append("".join(parts) + "concat=n=%d:v=1:a=1[v_cat][a_cat]" % len(parts))
tail = float(round(max(0.0, float(args.tail)) * float(rate))) / float(rate)    # a whole number of frames
v_tail = "tpad=stop_mode=clone:stop_duration=%.6f," % tail if tail > 0 else ""
a_tail = "apad=pad_dur=%.6f," % tail if tail > 0 else ""
vf = grade.get_filter_string(args.grade, input_video=args.input) if args.grade else grade.get_base_format_filter(args.input)
chain.append("[v_cat]%s%s[v]" % (v_tail, vf))
chain.append("[a_cat]%saformat=sample_rates=48000,asplit=2[a_m][a_w]" % a_tail)
chain.append("[a_m]aformat=sample_fmts=fltp[a_mp4]")
chain.append("[a_w]aformat=sample_fmts=s32[a_wav]")
fc = ";".join(chain)

voice_out = args.voice_out or os.path.join(os.path.dirname(os.path.abspath(args.out)), "voice.wav")
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
out_fps = "%d/%d" % (rate.numerator, rate.denominator)
gop = max(1, int(round(float(rate))))
cmd = ["ffmpeg", "-y", "-v", "error", "-i", args.input]
if use_wav:
    cmd += ["-i", args.audio]
cmd += ["-filter_complex", fc,
        "-map", "[v]", "-map", "[a_mp4]", "-r", out_fps, "-fps_mode", "cfr",
        "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf), "-g", str(gop), "-keyint_min", str(gop),
        "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-color_range", "tv", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart+write_colr", args.out,
        "-map", "[a_wav]", "-c:a", "pcm_s24le", "-ar", "48000", voice_out]
subprocess.run(cmd, check=True)

content_d = float(flat)
flat_d = round(content_d + tail, 6)
cut_map_path = os.path.join(os.path.dirname(os.path.abspath(args.cut_list)), "cut-map.json")
json.dump({"cuts": [c["flat_start"] for c in cut_map[1:]], "segments": cut_map,
           "content_duration": round(content_d, 6), "tail": round(tail, 6), "flat_duration": flat_d,
           "fps": out_fps, "source_fps": out_fps, "frame_origin": round(origin, 6),
           "video": os.path.abspath(args.out), "voice": os.path.abspath(voice_out),
           "audio_source": os.path.abspath(args.audio) if use_wav else "input"},
          open(cut_map_path, "w"), indent=1)
for s in skipped:
    print("skipped %.3f-%.3f: shorter than one frame" % (s["start"], s["end"]))
print("flat cut %.3fs (+%.2fs tail), %d segments, %d jump cuts, %s fps -> %s"
      % (content_d, tail, len(parts), len(parts) - 1, out_fps, args.out))

# ---- verify: picture, preview sound and voice WAV must all be as long as cut-map.json says --------------------
out = probe(args.out, "stream=codec_type,duration", "format=duration")
dur = {s.get("codec_type"): num(s.get("duration"), None) for s in out.get("streams", [])}
v, a = dur.get("video"), dur.get("audio")
w = num(probe(voice_out, "format=duration").get("format", {}).get("duration"), None)
frame = 1.0 / float(rate)
problems = []
if v is None or abs(v - flat_d) > frame + 0.002:
    problems.append("video %s s vs cut-map %.3f s (limit one frame)" % ("%.3f" % v if v is not None else "?", flat_d))
if v is None or a is None or abs(v - a) > frame + 0.025:
    problems.append("video %s s vs audio %s s (limit one frame + AAC padding)" % tuple("%.3f" % x if x is not None else "?" for x in (v, a)))
if w is None or abs(w - flat_d) > 0.005:
    problems.append("voice WAV %s s vs cut-map %.3f s (limit 5 ms)" % ("%.3f" % w if w is not None else "?", flat_d))
if problems:
    print("!!! DRIFT: %s. Do not build on this cut." % "; ".join(problems))
    sys.exit(2)
print("verified: video %.3f s, audio %.3f s, voice %.3f s = cut-map %.3f s" % (v, a, w, flat_d))
