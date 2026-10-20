#!/usr/bin/env python3
"""reframe.py: crop a 16:9 shot to another aspect around the speaker's face, never a blind centre crop."""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runtime
runtime.ensure_project_venv()

import numpy as np

EYE_LINE = 0.38       # face centre at this fraction of the crop height from the top
DEAD_ZONE = 0.30      # follow: the face may move inside the middle 30% of the crop width without moving the crop
SMOOTH = 0.5          # follow: share of the distance past the dead zone closed per sample (0.25 lost a walking face)


# ---------------------------------------------------------------- probing and shots
def probe(video: str) -> dict:
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate:format=duration", "-of", "json", video],
                       capture_output=True, text=True, check=True)
    j = json.loads(p.stdout)
    s = j["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return {"w": int(s["width"]), "h": int(s["height"]), "fps": float(n) / float(d),
            "duration": float(j["format"]["duration"])}


def scene_cuts(video: str, threshold: float = 0.3) -> list[float]:
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf",
                        f"scale=320:-2,select='gt(scene,{threshold})',metadata=print:file=-", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    out = []
    for line in p.stdout.splitlines():
        if "pts_time:" in line:
            out.append(float(line.split("pts_time:")[1].split()[0]))
    return out


def shots_from(cuts: list[float], duration: float, min_gap: float = 0.25) -> list[tuple[float, float]]:
    pts = [0.0]
    for c in sorted(cuts):
        if min_gap < c < duration - min_gap and c - pts[-1] >= min_gap:
            pts.append(round(c, 3))
    pts.append(duration)
    return list(zip(pts[:-1], pts[1:]))


# ---------------------------------------------------------------- detection
def find_yunet(explicit: str | None) -> str | None:
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    found = sorted(glob.glob(os.path.expanduser("~/.config/video-skills/models/face_detection_yunet*.onnx")))
    return found[-1] if found else None


def detect(video: str, info: dict, every: float, yunet: str | None, subject: str) -> tuple[list, str]:
    import cv2
    dw = 640
    dh = int(round(info["h"] * dw / info["w"] / 2) * 2)
    scale = info["w"] / dw
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps=1/{every},scale={dw}:{dh}",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    if yunet:
        det = cv2.FaceDetectorYN.create(yunet, "", (dw, dh), 0.7)
        name = "yunet"
    else:
        if not hasattr(cv2, "CascadeClassifier"):
            sys.exit("this OpenCV (%s) has no Haar face detector (removed in OpenCV 5). Either install OpenCV 4: "
                     "pip install 'opencv-python-headless>=4.9,<5', or add the YuNet model (see --help) and pass --yunet."
                     % cv2.__version__)
        det = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))
        # local contrast (CLAHE), not global equalizeHist: with a large flat background, global equalisation
        # flattened the face and Haar found nothing at any scale; CLAHE found it and still helps in dim rooms
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        name = "haar"
    out, k, size = [], 0, dw * dh * 3
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        img = np.frombuffer(buf, np.uint8).reshape(dh, dw, 3)
        if yunet:
            _, faces = det.detect(img)
            boxes = [] if faces is None else [tuple(f[:4]) for f in faces]
        else:
            g = clahe.apply(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
            boxes = [tuple(b) for b in det.detectMultiScale(g, 1.1, 5, minSize=(dw // 40, dw // 40))]
        t = round(k * every, 3)
        if boxes:
            if subject == "left":
                b = min(boxes, key=lambda b: b[0])
            elif subject == "right":
                b = max(boxes, key=lambda b: b[0] + b[2])
            else:
                b = max(boxes, key=lambda b: b[2] * b[3])
            x, y, w, h = [float(v) * scale for v in b]
            out.append({"t": t, "cx": x + w / 2, "cy": y + h / 2, "fw": w, "fh": h})
        else:
            out.append({"t": t, "cx": None})
        k += 1
    p.wait()
    return out, name


# ---------------------------------------------------------------- planning (pure, tested)
def crop_size(src_w: int, src_h: int, aspect: float, zoom: float = 1.0) -> tuple[int, int]:
    ch = src_h / zoom
    cw = ch * aspect
    if cw > src_w / zoom:
        cw = src_w / zoom
        ch = cw / aspect
    return int(cw) // 2 * 2, int(ch) // 2 * 2


def place(cx: float, cy: float, cw: int, ch: int, src_w: int, src_h: int) -> tuple[int, int]:
    x = min(max(cx - cw / 2, 0), src_w - cw)
    y = min(max(cy - EYE_LINE * ch, 0), src_h - ch)
    return int(x) // 2 * 2, int(y) // 2 * 2


def plan(dets: list[dict], shots: list[tuple[float, float]], src_w: int, src_h: int, cw: int, ch: int,
         mode: str = "static") -> tuple[list[dict], list[dict]]:
    keys, report = [], []
    last = (src_w / 2, src_h / 2)
    for s0, s1 in shots:
        inside = [d for d in dets if s0 <= d["t"] < s1]
        found = [d for d in inside if d.get("cx") is not None]
        if found:
            mcx = float(np.median([d["cx"] for d in found]))
            mcy = float(np.median([d["cy"] for d in found]))
            last = (mcx, mcy)
        cx, cy = last
        x, y = place(cx, cy, cw, ch, src_w, src_h)
        report.append({"shot": [s0, s1], "samples": len(inside), "faces": len(found),
                       "fallback": "none" if found else ("previous shot" if keys else "centre")})
        keys.append({"t": round(s0, 3), "x": x, "y": y})
        if mode == "follow" and found:
            # start where the face is at the top of the shot (the median would start a walk mid-frame)
            head = found[:3]
            curx = float(np.mean([d["cx"] for d in head]))
            x0, _ = place(curx, cy, cw, ch, src_w, src_h)
            keys[-1]["x"] = x0
            for d in found:
                if d["t"] <= s0:
                    continue
                off = d["cx"] - curx
                if abs(off) > DEAD_ZONE * cw / 2:
                    curx += SMOOTH * (off - np.sign(off) * DEAD_ZONE * cw / 2)
                nx, _ = place(curx, cy, cw, ch, src_w, src_h)
                if nx != keys[-1]["x"]:
                    keys.append({"t": d["t"], "x": nx, "y": y})
    return keys, report


def per_frame(keys: list[dict], shots: list[tuple[float, float]], fps: float) -> list[dict]:
    starts = {round(s0, 3) for s0, _ in shots}
    out = []
    for a, b in zip(keys, keys[1:] + [None]):
        out.append(a)
        if b is None or round(b["t"], 3) in starts:
            continue
        n = int((b["t"] - a["t"]) * fps)
        for i in range(1, n):
            f = i / n
            out.append({"t": round(a["t"] + i / fps, 4), "x": int(a["x"] + f * (b["x"] - a["x"])) // 2 * 2, "y": a["y"]})
    return out


# ---------------------------------------------------------------- render
def render(video: str, keys: list[dict], cw: int, ch: int, out: str, size: str, workdir: str) -> None:
    cmds = os.path.join(workdir, "reframe-cmds.txt")
    with open(cmds, "w") as f:
        for k in keys:
            f.write(f"{k['t']:.4f} crop x {k['x']}, crop y {k['y']};\n")
    w, h = size.split("x")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    vf = f"sendcmd=f='{runtime.ff_filter_path(cmds)}',crop=w={cw}:h={ch}:x={keys[0]['x']}:y={keys[0]['y']},scale={w}:{h}:flags=lanczos,setsar=1"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video, "-vf", vf, "-c:v", "libx264", "-crf", "16",
                    "-preset", "fast", "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "copy", "-movflags", "+faststart", out], check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--video", required=True)
    ap.add_argument("--aspect", required=True, help="W:H, e.g. 9:16, 1:1, 4:5, 8:9, 9:8")
    ap.add_argument("--out", required=True, help="the crop plan JSON")
    ap.add_argument("--cut-map")
    ap.add_argument("--mode", choices=["static", "follow"], default="static")
    ap.add_argument("--zoom", type=float, default=1.0, help=">1 crops tighter")
    ap.add_argument("--subject", choices=["largest", "left", "right"], default="largest")
    ap.add_argument("--every", type=float, default=0.2, help="seconds between face samples")
    ap.add_argument("--yunet")
    ap.add_argument("--no-scenes", action="store_true", help="use only the cut-map's cuts")
    ap.add_argument("--render")
    ap.add_argument("--size", help="output WxH for --render (default from the aspect: 9:16 -> 1080x1920)")
    a = ap.parse_args()
    aw, ah = [float(x) for x in a.aspect.split(":")]
    info = probe(a.video)
    cuts = json.load(open(a.cut_map))["cuts"] if a.cut_map else []
    if not a.no_scenes:
        cuts += scene_cuts(a.video)
    shots = shots_from(cuts, info["duration"])
    cw, ch = crop_size(info["w"], info["h"], aw / ah, a.zoom)
    dets, detector = detect(a.video, info, a.every, find_yunet(a.yunet), a.subject)
    keys, report = plan(dets, shots, info["w"], info["h"], cw, ch, a.mode)
    if a.mode == "follow":
        keys = per_frame(keys, shots, info["fps"])
    hit = sum(r["faces"] for r in report)
    total = sum(r["samples"] for r in report)
    res = {"video": os.path.abspath(a.video), "aspect": a.aspect, "mode": a.mode, "detector": detector,
           "source": [info["w"], info["h"]], "crop": [cw, ch], "face_rate": round(hit / total, 3) if total else 0.0,
           "shots": report, "keys": keys}
    json.dump(res, open(a.out, "w"), indent=1)
    print(f"{a.aspect} crop {cw}x{ch} from {info['w']}x{info['h']}, {len(shots)} shots, detector {detector}, "
          f"faces in {hit}/{total} samples")
    for r in report:
        if r["fallback"] != "none":
            print(f"  shot {r['shot'][0]:.2f}-{r['shot'][1]:.2f}: no face, used the {r['fallback']} framing")
    if total and hit / total < 0.5:
        print("WARN: faces found in under half the samples; check the frames, try --yunet or --subject")
    if a.render:
        if a.size:
            size = a.size
        else:
            long_side = 1920
            size = f"{int(long_side * aw / ah) // 2 * 2}x{long_side}" if ah >= aw else f"{long_side}x{int(long_side * ah / aw) // 2 * 2}"
        render(a.video, keys, cw, ch, a.render, size, os.path.dirname(os.path.abspath(a.out)))
        print(f"-> {a.render} ({size})")


if __name__ == "__main__":
    main()
