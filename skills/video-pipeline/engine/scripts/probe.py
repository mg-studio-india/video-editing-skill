"""ffprobe wrapper: one flat dict describing the file."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime import ToolError, run


def _fraction(value: str | None) -> float:
    if not value or value == "0/0":
        return 0.0
    try:
        if "/" in value:
            num, den = value.split("/", 1)
            return float(num) / float(den) if float(den) else 0.0
        return float(value)
    except ValueError:
        return 0.0


def probe(path: str | Path) -> dict:
    path = Path(path).resolve()
    proc = run([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", "--", str(path),
    ])
    data = json.loads(proc.stdout or "{}")
    streams = data.get("streams", [])
    fmt = data.get("format", {})
    video = next((s for s in streams if s.get("codec_type") == "video"
                  and s.get("disposition", {}).get("attached_pic") != 1), None)
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    if video is None:
        raise ToolError(f"No video stream found in {path.name}.")

    width, height = int(video.get("width", 0)), int(video.get("height", 0))
    rotation = 0
    for sd in video.get("side_data_list", []) or []:
        if "rotation" in sd:
            rotation = int(sd["rotation"])
    rotation = int(video.get("tags", {}).get("rotate", rotation) or rotation)
    if abs(rotation) in (90, 270):  # report display orientation
        width, height = height, width

    duration = float(fmt.get("duration") or video.get("duration") or 0.0)
    fps = _fraction(video.get("avg_frame_rate")) or _fraction(video.get("r_frame_rate"))
    return {
        "path": str(path),
        "filename": path.name,
        "duration": round(duration, 3),
        "width": width,
        "height": height,
        "aspect": round(width / height, 4) if height else None,
        "orientation": "vertical" if height > width else ("square" if height == width else "horizontal"),
        "fps": round(fps, 3),
        "video_codec": video.get("codec_name"),
        "pix_fmt": video.get("pix_fmt"),
        "color_transfer": video.get("color_transfer"),
        "bit_rate": int(fmt.get("bit_rate") or 0),
        "size_bytes": int(fmt.get("size") or 0),
        "rotation": rotation,
        "has_audio": bool(audio),
        "audio": [
            {"codec": a.get("codec_name"), "channels": a.get("channels"),
             "sample_rate": int(a.get("sample_rate") or 0)}
            for a in audio
        ],
        "title": (fmt.get("tags") or {}).get("title"),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: probe.py <video>", file=sys.stderr)
        raise SystemExit(2)
    print(json.dumps(probe(sys.argv[1]), indent=2))
