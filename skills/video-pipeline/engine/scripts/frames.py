"""Frames for Claude to look at."""
from __future__ import annotations

import math
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from runtime import ToolError, fmt_time, log, run

MIN_SHOTS_FOR_SCENE = 6    # fewer cuts than this => treat as static/long-take footage
REP_FRACTION = 0.35        # representative frame sits this far into a shot...
REP_MAX_OFFSET = 1.5       # ...but never later than this many seconds after the cut
LONG_SHOT = 6.0            # shots longer than this get extra frames
LONG_SHOT_STEP = 4.0       # ...one every this many seconds
DEDUP_THUMB = 16
DEDUP_THRESHOLD = 2.0


# ---------------------------------------------------------------- choosing moments
def pick_times(shots: list[dict], t0: float, t1: float, budget: int,
               hook_seconds: float = 10.0, pinned: list[float] | None = None) -> list[dict]:
    pinned = [p for p in (pinned or []) if t0 <= p <= t1]
    budget = max(1, budget)
    items: list[dict] = []

    if len(shots) >= MIN_SHOTS_FOR_SCENE:
        base = []
        for s in shots:
            off = min(max(s["duration"] * REP_FRACTION, 0.05), REP_MAX_OFFSET)
            t = min(s["start"] + off, max(s["start"], s["end"] - 0.04))
            base.append({"t": round(t, 3), "kind": "shot", "shot": s["id"]})

        reserve = max(0, len(pinned))
        cap = max(1, budget - reserve)
        if len(base) > cap:
            protected = [b for i, b in enumerate(base)
                         if b["t"] < t0 + hook_seconds or i in (0, len(base) - 1)]
            rest = [b for b in base if b not in protected]
            room = cap - len(protected)
            if room <= 0:
                step = max(1, math.ceil(len(protected) / cap))
                base = protected[::step][:cap]
            else:
                idx = {round(i * (len(rest) - 1) / max(1, room - 1)) for i in range(room)} if rest else set()
                base = sorted(protected + [rest[i] for i in sorted(idx)], key=lambda b: b["t"])
        items = list(base)

        remaining = cap - len(items)
        if remaining > 0:
            extras = []
            for s in shots:
                if s["duration"] > LONG_SHOT:
                    t = s["start"] + min(max(s["duration"] * REP_FRACTION, 0.05), REP_MAX_OFFSET) + LONG_SHOT_STEP
                    while t < s["end"] - 1.0:
                        extras.append({"t": round(t, 3), "kind": "extra", "shot": s["id"], "_pri": s["duration"]})
                        t += LONG_SHOT_STEP
            extras.sort(key=lambda e: -e["_pri"])
            for e in extras[:remaining]:
                e.pop("_pri")
                items.append(e)
    else:
        span = t1 - t0
        n = min(max(1, budget - len(pinned)), max(8, int(span / 6)))
        for i in range(n):
            t = t0 + (i + 0.5) * span / n
            items.append({"t": round(t, 3), "kind": "uniform", "shot": _shot_at(shots, t)})

    for p in pinned:  # cue frames always win; drop a neighbour closer than 0.25s
        items = [i for i in items if abs(i["t"] - p) >= 0.25]
        items.append({"t": round(p, 3), "kind": "cue", "shot": _shot_at(shots, p)})
    return sorted(items, key=lambda i: i["t"])


def _shot_at(shots: list[dict], t: float) -> int | None:
    for s in shots:
        if s["start"] <= t < s["end"] or (s is shots[-1] and t <= s["end"]):
            return s["id"]
    return None


def hook_times(t0: float, t1: float, hook_seconds: float, step: float) -> list[float]:
    end = min(t1, t0 + hook_seconds)
    times, t = [], t0
    while t < end - 1e-6:
        times.append(round(t, 3))
        t += step
    return times


# ---------------------------------------------------------------- extraction
def _extract_one(video: str, t: float, out: Path, width: int) -> bool:
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}",
           "-i", video, "-an", "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", "3", str(out)]
    try:
        run(cmd)
    except ToolError as exc:
        log(f"frame at {fmt_time(t, 1)} failed: {exc}")
        return False
    return out.is_file() and out.stat().st_size > 0


def extract_frames(video: str, items: list[dict], out_dir: Path, width: int = 640,
                   workers: int = 4) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.jpg"):
        old.unlink()
    video = str(Path(video).resolve())
    jobs = []
    for i, item in enumerate(items):
        item["path"] = str(out_dir / f"f{i + 1:03d}_{item['t']:.2f}s.jpg")
        jobs.append((item, Path(item["path"])))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda j: _extract_one(video, j[0]["t"], j[1], width), jobs))
    return [it for it, ok in zip(items, results) if ok]


def dedupe(items: list[dict], threshold: float = DEDUP_THRESHOLD) -> tuple[list[dict], int]:
    try:
        from PIL import Image
    except ImportError:
        return items, 0

    def thumb(path: str) -> bytes:
        with Image.open(path) as im:
            return im.convert("L").resize((DEDUP_THUMB, DEDUP_THUMB)).tobytes()

    kept: list[dict] = []
    last: bytes | None = None
    dropped = 0
    for it in items:
        if it["kind"] not in ("extra", "uniform"):
            kept.append(it)
            last = thumb(it["path"])
            continue
        cur = thumb(it["path"])
        if last is not None:
            diff = sum(abs(a - b) for a, b in zip(cur, last)) / len(cur)
            if diff < threshold:
                Path(it["path"]).unlink(missing_ok=True)
                dropped += 1
                continue
        kept.append(it)
        last = cur
    return kept, dropped


# ---------------------------------------------------------------- contact sheets
def sheet_layout(aspect: float) -> tuple[int, int, int]:
    if aspect >= 1.4:
        return 4, 3, 320
    if aspect >= 0.9:
        return 5, 3, 288
    return 6, 3, 240


def label_for(item: dict, with_shot: bool = True) -> str:
    stamp = fmt_time(item["t"], 1)
    star = "* " if item.get("kind") == "cue" else ""
    if with_shot and item.get("shot") is not None:
        return f"{star}#{item['shot']} {stamp}"
    return f"{star}{stamp}"


def make_sheets(items: list[dict], out_dir: Path, aspect: float, prefix: str = "sheet",
                with_shot: bool = True) -> list[dict] | None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    if not items:
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob(f"{prefix}_*.jpg"):
        old.unlink()

    cols, rows, cell_w = sheet_layout(aspect)
    cell_h = max(1, round(cell_w / aspect)) if aspect else cell_w
    per = cols * rows
    gap = 4
    try:
        font = ImageFont.load_default(size=15)
    except TypeError:  # older Pillow
        font = ImageFont.load_default()

    sheets = []
    for sheet_no, start in enumerate(range(0, len(items), per), 1):
        chunk = items[start:start + per]
        used_rows = math.ceil(len(chunk) / cols)
        canvas = Image.new("RGB", (cols * cell_w + (cols + 1) * gap, used_rows * cell_h + (used_rows + 1) * gap),
                           (24, 24, 24))
        draw = ImageDraw.Draw(canvas)
        cells = []
        for n, item in enumerate(chunk):
            r, c = divmod(n, cols)
            x, y = gap + c * (cell_w + gap), gap + r * (cell_h + gap)
            with Image.open(item["path"]) as im:
                canvas.paste(im.convert("RGB").resize((cell_w, cell_h)), (x, y))
            text = label_for(item, with_shot)
            box = draw.textbbox((0, 0), text, font=font)
            draw.rectangle((x, y, x + box[2] + 10, y + box[3] + 8), fill=(0, 0, 0))
            draw.text((x + 5, y + 2), text, fill=(255, 255, 255), font=font)
            cells.append({"cell": n + 1, "t": item["t"], "shot": item.get("shot"),
                          "kind": item.get("kind"), "label": text})
        path = out_dir / f"{prefix}_{sheet_no:02d}.jpg"
        canvas.save(path, quality=82)
        sheets.append({"path": str(path), "number": sheet_no, "cols": cols, "rows": used_rows, "cells": cells})
    return sheets


def cell_ref(sheets: list[dict] | None, prefix: str, shot_id: int, shot: dict | None = None) -> str:
    best = None
    for sh in sheets or []:
        for c in sh["cells"]:
            if c["shot"] == shot_id:
                return f"{prefix}{sh['number']}·{c['cell']}"
            if shot is not None:
                mid = (shot["start"] + shot["end"]) / 2
                d = abs(c["t"] - mid)
                if best is None or d < best[0]:
                    best = (d, f"~{prefix}{sh['number']}·{c['cell']}")
    return best[1] if best else ""
