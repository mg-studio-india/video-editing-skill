"""Shared bits for the tests: run a script the way the skill does, make scratch dirs, synthesise media.
Paths are relative to this file (SCRIPTS = engine/scripts next to this tests/ folder; scripts owned by a single skill
live in skills/<skill>/scripts/ and are found by script_path), so the tests run from any install location.

Run the whole suite from the engine folder:  python3 -m unittest discover -s tests -t ."""
import glob, json, os, shutil, subprocess, sys, tempfile, unittest

ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ENGINE, "scripts")
SKILLS = os.path.dirname(os.path.dirname(ENGINE))          # .../skills (video-pipeline/engine -> skills)


def script_path(name):
    """engine/scripts/<name>, else the one skill folder that owns it (skills/<skill>/scripts/<name>)."""
    p = os.path.join(SCRIPTS, name)
    if os.path.isfile(p):
        return p
    hits = glob.glob(os.path.join(SKILLS, "*", "scripts", name))
    if len(hits) == 1:
        return hits[0]
    raise FileNotFoundError("%s: %s" % (name, "not found" if not hits else "found in several skills: %s" % hits))
HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
needs_ffmpeg = unittest.skipUnless(HAS_FFMPEG, "ffmpeg / ffprobe not on PATH")


def run(script, *args):
    return subprocess.run([sys.executable, script_path(script)] + [str(a) for a in args], capture_output=True, text=True)


def scratch(test):
    d = tempfile.mkdtemp(prefix="yt-edit-test-")
    test.addCleanup(shutil.rmtree, d, True)
    return d


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text if isinstance(text, str) else json.dumps(text))
    return path


def read(path):
    with open(path) as f:
        return f.read()


def load(path):
    return json.loads(read(path))


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + list(args), check=True)


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-show_entries", "format=duration",
                        "-of", "json", path], capture_output=True, text=True, check=True)
    p = json.loads(r.stdout)
    return {s["codec_type"]: float(s["duration"]) for s in p["streams"]}, float(p["format"]["duration"])
