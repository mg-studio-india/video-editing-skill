#!/usr/bin/env python3
"""audiocraft-gen.py: music beds (MusicGen) and sound effects (AudioGen) generated locally with Meta's AudioCraft.

LICENCE: AudioCraft's code is MIT, but Meta released the pretrained MusicGen and AudioGen WEIGHTS under CC-BY-NC 4.0
(non-commercial). For a monetised channel or client work, prefer HyperFrames' media library / HeyGen music, Google
Lyria, or a licensed library first (the sound-design skill's order). This script refuses to run without
--non-commercial-ok, which records that the user read this.

Usage:
  python3 audiocraft-gen.py music --prompt "calm lo-fi, soft keys, 90 bpm" --seconds 45 --out W/music/bed.wav --non-commercial-ok
  python3 audiocraft-gen.py sfx   --prompt "single soft mouse click" --seconds 1.5 --out W/sfx/click.wav --non-commercial-ok
  ... --dry-run   prints the plan without loading a model
Music longer than one generation (~30 s) is one seed clip crossfade-looped to length (no seams mid-phrase), then
faded out. SFX should then go through sfx-prep.py. Each output is recorded in <out dir>/ledger.json.

Install once (a separate virtual environment is wise; it pulls torch):  python3 -m pip install audiocraft
"""
import argparse, datetime as dt, json, os, subprocess, sys

MODELS = {"music": os.environ.get("MUSICGEN_MODEL", "facebook/musicgen-small"),
          "sfx": os.environ.get("AUDIOGEN_MODEL", "facebook/audiogen-medium")}
MAX_GEN = 28.0


def plan(kind, seconds):
    """Pure (tested): how many generated seconds and how the target length is reached."""
    gen = min(seconds, MAX_GEN)
    loops = 0 if seconds <= MAX_GEN else int((seconds - gen) // (gen - 2.0)) + 1
    return {"model": MODELS[kind], "generate_seconds": round(gen, 2), "crossfade_loops": loops, "target_seconds": seconds}


def loop_to(src, dst, target, xfade=2.0):
    cur = src
    n = 0
    while True:
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cur],
                                 capture_output=True, text=True).stdout.strip())
        if d >= target:
            break
        nxt = "%s.loop%d.wav" % (dst, n)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", cur, "-i", src, "-filter_complex",
                        "acrossfade=d=%g:c1=tri:c2=tri" % xfade, nxt], check=True)
        cur, n = nxt, n + 1
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", cur, "-af",
                    "atrim=0:%g,afade=t=out:st=%g:d=2" % (target, max(0.0, target - 2.0)), dst], check=True)
    for i in range(n):
        os.remove("%s.loop%d.wav" % (dst, i))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("kind", choices=["music", "sfx"])
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--seconds", type=float, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--non-commercial-ok", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    p = plan(a.kind, a.seconds)
    if a.dry_run:
        print(json.dumps({**p, "prompt": a.prompt, "out": a.out}, indent=1)); return
    if not a.non_commercial_ok:
        sys.exit("refusing: MusicGen/AudioGen weights are CC-BY-NC 4.0 (non-commercial). Use HyperFrames' library, Lyria "
                 "or a licensed track for commercial work, or pass --non-commercial-ok after the user accepts the licence.")
    import torch
    from audiocraft.data.audio import audio_write
    from audiocraft.models import AudioGen, MusicGen
    torch.manual_seed(a.seed)
    model = (MusicGen if a.kind == "music" else AudioGen).get_pretrained(p["model"])
    model.set_generation_params(duration=p["generate_seconds"])
    wav = model.generate([a.prompt])
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    stem = os.path.splitext(a.out)[0] + ".seed"
    audio_write(stem, wav[0].cpu(), model.sample_rate, strategy="loudness", loudness_compressor=True)
    seed_file = stem + ".wav"
    if a.seconds > p["generate_seconds"]:
        loop_to(seed_file, a.out, a.seconds)
        os.remove(seed_file)
    else:
        os.replace(seed_file, a.out)
    led = os.path.join(os.path.dirname(os.path.abspath(a.out)), "ledger.json")
    data = json.load(open(led)) if os.path.isfile(led) else []
    data.append({"tool": "audiocraft", "kind": a.kind, "model": p["model"], "prompt": a.prompt, "seed": a.seed,
                 "seconds": a.seconds, "out": a.out, "licence": "CC-BY-NC 4.0 weights", "at": dt.datetime.now().isoformat(timespec="seconds")})
    json.dump(data, open(led, "w"), indent=1)
    print("%s: %s, %.1f s (%s)" % (a.out, a.kind, a.seconds, p["model"]))


if __name__ == "__main__":
    main()
