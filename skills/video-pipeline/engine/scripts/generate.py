#!/usr/bin/env python3
"""generate.py: generated stills and clips, with a cost gate and a ledger."""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import runtime
runtime.ensure_project_venv()

DEFAULTS = {
    "VEO_MODEL": "veo-3.1-generate-preview",
    "GEMINI_IMAGE_MODEL": "gemini-2.5-flash-image",
    "OPENROUTER_IMAGE_MODEL": "google/gemini-2.5-flash-image",
}
OPENROUTER = "https://openrouter.ai/api/v1"
NEGATIVE = "text, captions, watermark, logo, extra people, distorted hands, fake user interface, readable screens"


def cfg(name: str) -> str:
    return os.environ.get(name) or DEFAULTS[name]


def google_key() -> str | None:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def estimate(kind: str, seconds: float, a) -> str:
    if kind == "video" and a.price_per_second:
        return "~%.2f (%.0f s x %.3f)" % (seconds * a.price_per_second, seconds, a.price_per_second)
    if kind == "image" and a.price_per_image:
        return "~%.3f per image" % a.price_per_image
    return "unknown: check the provider's current pricing and pass --price-per-%s" % ("second" if kind == "video" else "image")


def ledger(out: str, entry: dict) -> None:
    path = os.path.join(os.path.dirname(os.path.abspath(out)) or ".", "ledger.json")
    data = json.load(open(path)) if os.path.isfile(path) else []
    data.append({**entry, "at": dt.datetime.now().isoformat(timespec="seconds"), "ai_generated": True})
    json.dump(data, open(path, "w"), indent=1)


def mime(path: str) -> str:
    return "image/png" if path.lower().endswith(".png") else "image/jpeg"


# ---------------------------------------------------------------- request builders (pure, tested)
def image_prompt(prompt: str, aspect: str) -> str:
    return "%s. Aspect ratio %s. No text, no logos, no watermark." % (prompt.rstrip(". "), aspect)


def restyle_prompt(style: str) -> str:
    return ("Redraw this exact frame in the style: %s. Keep the composition, the people, their pose and expression, the "
            "camera angle and the framing identical; change only the rendering style. No text, no logos." % style)


def openrouter_image_body(model: str, prompt: str, refs: list[str]) -> dict:
    content = [{"type": "text", "text": prompt}]
    for r in refs:
        b = base64.b64encode(open(r, "rb").read()).decode() if os.path.isfile(r) else "<%s>" % r
        content.append({"type": "image_url", "image_url": {"url": "data:%s;base64,%s" % (mime(r), b)}})
    return {"model": model, "modalities": ["image", "text"], "messages": [{"role": "user", "content": content}]}


def veo_request(prompt: str, image: str | None, last: str | None, aspect: str, seconds: int) -> dict:
    return {"model": cfg("VEO_MODEL"), "prompt": prompt, "image": image, "last_frame": last,
            "config": {"aspect_ratio": aspect, "number_of_videos": 1, "duration_seconds": seconds,
                       "negative_prompt": NEGATIVE}}


# ---------------------------------------------------------------- providers
def gemini_image(prompt: str, refs: list[str], out: str) -> str:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=google_key())
    parts = [prompt] + [types.Part.from_bytes(data=open(r, "rb").read(), mime_type=mime(r)) for r in refs]
    resp = client.models.generate_content(model=cfg("GEMINI_IMAGE_MODEL"), contents=parts)
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            open(out, "wb").write(part.inline_data.data)
            return cfg("GEMINI_IMAGE_MODEL")
    raise RuntimeError("Gemini returned no image (it may have refused the prompt): %s" % (resp.text or "")[:300])


def http_json(url: str, body: dict | None, key: str) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
                                 method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def openrouter_image(prompt: str, refs: list[str], out: str) -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    model = cfg("OPENROUTER_IMAGE_MODEL")
    resp = http_json(OPENROUTER + "/chat/completions", openrouter_image_body(model, prompt, refs), key)
    imgs = (resp.get("choices") or [{}])[0].get("message", {}).get("images") or []
    if not imgs:
        raise RuntimeError("OpenRouter returned no image from %s" % model)
    url = imgs[0]["image_url"]["url"]
    open(out, "wb").write(base64.b64decode(url.split(",", 1)[1]))
    return model


def openrouter_video_models() -> list[str]:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return []
    data = http_json(OPENROUTER + "/models", None, key).get("data", [])
    return [m["id"] for m in data if "video" in ((m.get("architecture") or {}).get("output_modalities") or [])]


def veo_video(req: dict, out: str, poll: int = 10, timeout: int = 900) -> str:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=google_key())
    c = req["config"]
    conf = dict(aspect_ratio=c["aspect_ratio"], number_of_videos=1, negative_prompt=c["negative_prompt"],
                duration_seconds=c["duration_seconds"])
    if req.get("last_frame"):
        conf["last_frame"] = types.Image(image_bytes=open(req["last_frame"], "rb").read(), mime_type=mime(req["last_frame"]))
    kwargs = dict(model=req["model"], prompt=req["prompt"], config=types.GenerateVideosConfig(**conf))
    if req.get("image"):
        kwargs["image"] = types.Image(image_bytes=open(req["image"], "rb").read(), mime_type=mime(req["image"]))
    op = client.models.generate_videos(**kwargs)
    t0 = time.time()
    while not op.done:
        if time.time() - t0 > timeout:
            raise RuntimeError("Veo did not finish within %d s (operation %s)" % (timeout, getattr(op, "name", "?")))
        time.sleep(poll)
        op = client.operations.get(op)
    vids = (op.response.generated_videos if op.response else None) or []
    if not vids:
        raise RuntimeError("Veo returned no video (it may have refused the prompt or the image)")
    client.files.download(file=vids[0].video)
    vids[0].video.save(out)
    return req["model"]


# ---------------------------------------------------------------- modes
def do_image(a) -> None:
    prompt = image_prompt(a.prompt, a.aspect)
    plan = {"mode": "image", "prompt": prompt, "refs": a.ref, "out": a.out,
            "providers": [cfg("GEMINI_IMAGE_MODEL") + " (Gemini)", cfg("OPENROUTER_IMAGE_MODEL") + " (OpenRouter fallback)"],
            "estimate": estimate("image", 0, a)}
    if a.dry_run or not a.yes:
        print(json.dumps(plan, indent=1)); print("not generated: %s" % ("dry run" if a.dry_run else "add --yes after the user approves the cost (gate 3)"))
        if a.dry_run:
            print(json.dumps(openrouter_image_body(cfg("OPENROUTER_IMAGE_MODEL"), prompt, a.ref), indent=1)[:1500])
        return
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    errors = []
    for name, fn in (("gemini", gemini_image), ("openrouter", openrouter_image)):
        if name == "gemini" and not google_key():
            errors.append("gemini: GEMINI_API_KEY not set"); continue
        try:
            model = fn(prompt, a.ref, a.out)
            ledger(a.out, {"mode": "image", "provider": name, "model": model, "prompt": prompt, "inputs": a.ref, "outputs": [a.out]})
            print("%s -> %s (%s)" % (name, a.out, model)); return
        except Exception as e:      # noqa: BLE001 - every provider error is reported, then the next is tried
            errors.append("%s: %s" % (name, e))
    sys.exit("no image generated:\n  " + "\n  ".join(errors))


def run_video(req: dict, out: str, a, label: str, inputs: list[str]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    errors = []
    if google_key():
        try:
            model = veo_video(req, out)
            ledger(out, {"mode": label, "provider": "google", "model": model, "prompt": req["prompt"], "inputs": inputs,
                         "outputs": [out], "seconds": req["config"]["duration_seconds"]})
            print("veo -> %s (%s)" % (out, model)); return
        except Exception as e:      # noqa: BLE001
            errors.append("veo: %s" % e)
    else:
        errors.append("veo: GEMINI_API_KEY not set")
    try:
        vm = openrouter_video_models()
    except Exception as e:          # noqa: BLE001
        vm, _ = [], errors.append("openrouter: %s" % e)
    if vm:
        errors.append("openrouter lists video models %s, but this script does not know their request format; "
                      "read OpenRouter's docs for that model before wiring it (do not guess the API)" % ", ".join(vm[:5]))
    else:
        errors.append("openrouter: no video-output model available to this key")
    sys.exit("no video generated:\n  " + "\n  ".join(errors) +
             "\n  budget fallback: generate a still (mode image) and conform it with a slow push-in "
             "(broll-conform.py --in still.png --push 1.08)")


def do_video(a) -> None:
    req = veo_request(a.prompt, a.image, a.last, a.aspect, a.seconds)
    plan = {**req, "estimate": estimate("video", a.seconds, a), "fallback": "OpenRouter if it lists a video model"}
    if a.dry_run or not a.yes:
        print(json.dumps(plan, indent=1)); print("not generated: %s" % ("dry run" if a.dry_run else "add --yes after the user approves the cost (gate 3)"))
        return
    run_video(req, a.out, a, "video", [x for x in (a.image, a.last) if x])


def frame_at(clip: str, t: float | str, out: str) -> str:
    args = ["ffmpeg", "-y", "-v", "error"]
    args += (["-sseof", "-0.05"] if t == "end" else ["-ss", "%.3f" % float(t)])
    subprocess.run(args + ["-i", clip, "-frames:v", "1", out], check=True)
    return out


def do_restyle(a) -> None:
    base = os.path.splitext(a.out)[0]
    first, last = base + "-first.png", base + "-last.png"
    first_s, last_s = base + "-first-styled.png", base + "-last-styled.png"
    sp = restyle_prompt(a.style_prompt)
    motion = a.motion or "the same camera move and action as the source shot, natural motion, no cuts"
    req = veo_request("%s. Style: %s." % (motion, a.style_prompt), first_s, last_s if a.keep_end else None, a.aspect, a.seconds)
    plan = {"mode": "restyle", "clip": a.clip, "steps": [
        "extract the first%s frame" % (" and last" if a.keep_end else ""),
        "restyle %s with %s: %r" % ("both frames" if a.keep_end else "it", cfg("GEMINI_IMAGE_MODEL"), sp),
        "animate with %s from the restyled first frame%s: %r" % (cfg("VEO_MODEL"), " to the restyled last frame" if a.keep_end else "", req["prompt"]),
        "conform with broll-conform.py to the slot length"],
        "note": "motion is regenerated, not preserved", "estimate": {"images": estimate("image", 0, a), "video": estimate("video", a.seconds, a)}}
    if a.dry_run or not a.yes:
        print(json.dumps(plan, indent=1)); print("not generated: %s" % ("dry run" if a.dry_run else "add --yes after the user approves the cost (gate 3)"))
        return
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    frame_at(a.clip, 0.05, first)
    if a.keep_end:
        frame_at(a.clip, "end", last)
    for src, dst in [(first, first_s)] + ([(last, last_s)] if a.keep_end else []):
        ns = argparse.Namespace(**{**vars(a), "prompt": sp, "ref": [src], "out": dst})
        try:
            do_image_direct(ns)
        except SystemExit as e:
            sys.exit("restyle stopped at the still: %s" % e)
    print("check the restyled stills before paying for motion: %s" % ", ".join([first_s] + ([last_s] if a.keep_end else [])))
    if not a.confirm_stills:
        print("re-run with --confirm-stills once the stills look right (a bad still is a re-run, not a video)")
        return
    run_video(req, a.out, a, "restyle", [a.clip, first_s] + ([last_s] if a.keep_end else []))


def do_image_direct(a) -> None:
    errors = []
    for name, fn in (("gemini", gemini_image), ("openrouter", openrouter_image)):
        if name == "gemini" and not google_key():
            errors.append("gemini: no key"); continue
        try:
            model = fn(a.prompt, a.ref, a.out)
            ledger(a.out, {"mode": "restyle-still", "provider": name, "model": model, "prompt": a.prompt, "inputs": a.ref, "outputs": [a.out]})
            return
        except Exception as e:      # noqa: BLE001
            errors.append("%s: %s" % (name, e))
    raise SystemExit("; ".join(errors))


def do_models(a) -> None:
    if google_key():
        from google import genai
        client = genai.Client(api_key=google_key())          # keep a reference: an inline client is closed before use
        try:
            names = [m.name for m in client.models.list()]
        except Exception as e:      # noqa: BLE001
            sys.exit("google: could not list models (%s: %s). Check GEMINI_API_KEY and the network." % (type(e).__name__, str(e)[:200]))
        for want in ("VEO_MODEL", "GEMINI_IMAGE_MODEL"):
            hit = any(cfg(want) in n for n in names)
            print("%-20s %-36s %s" % (want, cfg(want), "available" if hit else "NOT FOUND: set %s to one of the listed models" % want))
        print("google models with 'veo' or 'image':", ", ".join(n for n in names if "veo" in n or "image" in n))
    else:
        print("google: GEMINI_API_KEY not set")
    if os.environ.get("OPENROUTER_API_KEY"):
        print("openrouter video-output models:", ", ".join(openrouter_video_models()) or "none")
    else:
        print("openrouter: OPENROUTER_API_KEY not set")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["image", "video", "restyle", "models"])
    ap.add_argument("--prompt")
    ap.add_argument("--ref", action="append", default=[], help="reference image(s) for image mode")
    ap.add_argument("--image", help="first frame for video mode")
    ap.add_argument("--last", help="last frame for video mode")
    ap.add_argument("--clip", help="source clip for restyle")
    ap.add_argument("--style-prompt")
    ap.add_argument("--motion", help="restyle: describe the source shot's camera move and action")
    ap.add_argument("--keep-end", action="store_true", help="restyle: also pin the last frame (Veo first+last frame)")
    ap.add_argument("--confirm-stills", action="store_true", help="restyle: the stills were checked; pay for motion")
    ap.add_argument("--out")
    ap.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"])
    ap.add_argument("--seconds", type=int, default=8)
    ap.add_argument("--price-per-second", type=float)
    ap.add_argument("--price-per-image", type=float)
    ap.add_argument("--yes", action="store_true", help="the user approved this cost (gate 3)")
    ap.add_argument("--user-requested", action="store_true",
                    help="restyle only: the user explicitly asked for a restyle (omni-restyle is off by default)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.mode == "models":
        return do_models(a)
    if not a.out:
        ap.error("--out is required")
    if a.mode == "image":
        if not a.prompt:
            ap.error("image needs --prompt")
        do_image(a)
    elif a.mode == "video":
        if not a.prompt:
            ap.error("video needs --prompt")
        do_video(a)
    else:
        if not a.user_requested:
            sys.exit("omni-restyle is disabled by default. Use it only when the user explicitly asks to restyle a clip, "
                     "then pass --user-requested.")
        if not (a.clip and a.style_prompt):
            ap.error("restyle needs --clip and --style-prompt")
        do_restyle(a)


if __name__ == "__main__":
    main()
