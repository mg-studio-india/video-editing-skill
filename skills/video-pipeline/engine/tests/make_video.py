"""Generate a small synthetic clip with KNOWN structure for tests.

Timeline (10s, 30fps, 640x360):
  0-2   red       (hard cut at 2)
  2-4   blue      (hard cut at 4)
  4-7   testsrc2  (moving pattern, hard cut at 7)
  7-8   black     (hard cut at 8)
  8-10  green
Audio: 440 Hz tone 0-3s, silence 3-5s, tone 5-8s, silence 8-10s.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SIZE = "640x360"
RATE = 30
KNOWN_CUTS = [2.0, 4.0, 7.0, 8.0]
DURATION = 10.0


def make(path: str | Path, with_audio: bool = True) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    srcs = [
        ("color=c=red:s=%s:d=2:r=%d" % (SIZE, RATE)),
        ("color=c=blue:s=%s:d=2:r=%d" % (SIZE, RATE)),
        ("testsrc2=s=%s:d=3:r=%d" % (SIZE, RATE)),
        ("color=c=black:s=%s:d=1:r=%d" % (SIZE, RATE)),
        ("color=c=green:s=%s:d=2:r=%d" % (SIZE, RATE)),
    ]
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for s in srcs:
        cmd += ["-f", "lavfi", "-i", s]
    n = len(srcs)
    graph = "".join(f"[{i}:v]format=yuv420p,setsar=1[v{i}];" for i in range(n))
    graph += "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]"
    maps = ["-map", "[v]"]
    if with_audio:
        audio_srcs = [
            "sine=frequency=440:duration=3", "anullsrc=r=16000:cl=mono:d=2",
            "sine=frequency=440:duration=3", "anullsrc=r=16000:cl=mono:d=2",
        ]
        for a in audio_srcs:
            cmd += ["-f", "lavfi", "-i", a]
        graph += ";" + "".join(f"[{n + j}:a]aresample=16000,aformat=channel_layouts=mono[a{j}];"
                               for j in range(4))
        graph += "".join(f"[a{j}]" for j in range(4)) + "concat=n=4:v=0:a=1[a]"
        maps += ["-map", "[a]"]
    cmd += ["-filter_complex", graph, *maps, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p"]
    if with_audio:
        cmd += ["-c:a", "aac"]
    cmd += [str(path)]
    subprocess.run(cmd, check=True, capture_output=True)
    return path


if __name__ == "__main__":
    out = make(sys.argv[1] if len(sys.argv) > 1 else "/tmp/watch_test.mp4")
    print(out)
