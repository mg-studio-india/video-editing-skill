"""Fetch a video from a URL with yt-dlp. OPTIONAL.

This is the only place the skill touches the network, and only to download the
video file you asked for. Analysis itself never uploads anything. If you would
rather stay fully offline, download the file yourself and pass its path.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from runtime import ToolError, log, run

URL_RE = re.compile(r"^https?://", re.IGNORECASE)
VIDEO_EXTS = (".mp4", ".mkv", ".webm", ".mov", ".m4v")


def is_url(value: str) -> bool:
    return bool(URL_RE.match(value.strip()))


def download(url: str, out_dir: Path, max_height: int = 1080) -> Path:
    if shutil.which("yt-dlp") is None:
        raise ToolError("yt-dlp is not installed. `brew install yt-dlp`, or download the file "
                        "yourself and pass its path.")
    out_dir.mkdir(parents=True, exist_ok=True)
    before = {p for p in out_dir.iterdir()} if out_dir.exists() else set()
    log("downloading video with yt-dlp (the only network step)…")
    run(["yt-dlp", "--no-playlist", "--no-progress", "--restrict-filenames",
         "-f", f"bv*[height<={max_height}]+ba/b[height<={max_height}]/b",
         "--merge-output-format", "mp4",
         "-o", str(out_dir / "%(id)s.%(ext)s"), "--", url], timeout=1800)
    new = [p for p in out_dir.iterdir() if p not in before and p.suffix.lower() in VIDEO_EXTS]
    if not new:  # re-download of an existing id: fall back to the newest video file
        new = [p for p in out_dir.iterdir() if p.suffix.lower() in VIDEO_EXTS]
    if not new:
        raise ToolError("yt-dlp finished but no video file was found.")
    return max(new, key=lambda p: p.stat().st_mtime)
