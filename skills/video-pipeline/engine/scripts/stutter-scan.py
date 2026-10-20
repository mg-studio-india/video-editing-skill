#!/usr/bin/env python3
"""stutter-scan.py: second opinion on the paper cut, using a mechanical mistake finder."""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FINDER = os.path.join(HERE, "find-cut-candidates.mjs")

ap = argparse.ArgumentParser()
ap.add_argument("--transcript", required=True)
ap.add_argument("--out-dir", required=True)
args = ap.parse_args()
if not os.path.exists(FINDER):
    sys.exit("find-cut-candidates.mjs not found at %s (it ships next to this script)" % FINDER)

raw = json.load(open(args.transcript))
words = raw["words"] if isinstance(raw, dict) and "words" in raw else raw
words = [{"text": w["text"], "start": float(w["start"]), "end": float(w["end"]), "type": "word"} for w in words if w.get("text")]
os.makedirs(args.out_dir, exist_ok=True)
kit_json = os.path.join(args.out_dir, "flat-transcript.json")
json.dump({"language_code": "en", "audio_duration_secs": words[-1]["end"] if words else 0,
           "text": " ".join(w["text"] for w in words), "words": words}, open(kit_json, "w"))
sys.path.insert(0, HERE)
import runtime  # noqa: E402  (puts the engine's private Node 22 first when install.sh added one)
os.environ["PATH"] = os.pathsep.join(runtime.engine_path_dirs() + [os.environ.get("PATH", "")])
res = subprocess.run(["node", FINDER, kit_json, "--out-dir", args.out_dir], capture_output=True, text=True)
if res.returncode != 0:
    sys.exit(res.stderr)
summary = json.loads(res.stdout)
md = summary["outputs"]["md"]
print("candidates: %d %s -> %s" % (summary["candidates"], json.dumps(summary["counts"]), md))
print(open(md).read())
