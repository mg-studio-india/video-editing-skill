"""Shared helpers: time parsing/formatting, a safe subprocess wrapper, JSON I/O.

Stdlib only. Imported by every other script in this folder.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


class ToolError(RuntimeError):
    """A command-line tool failed. The message is safe to show the user."""


def configure_stdio() -> None:
    """Call once at script entry so non-ASCII titles never crash the console."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="backslashreplace")
            except (OSError, ValueError):
                pass


def tail(text: str | bytes | None, limit: int = 1500) -> str:
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    return (text or "").strip()[-limit:]


def run(cmd: list[str], *, timeout: float | None = None, check: bool = True,
        cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run a command, capturing text output. Never uses a shell.

    Raises ToolError with the tail of stderr on failure (when check=True), so
    the agent sees the real reason instead of a bare traceback.
    """
    try:
        proc = subprocess.run(
            [str(c) for c in cmd], capture_output=True, encoding="utf-8",
            errors="replace", timeout=timeout, cwd=cwd,
        )
    except FileNotFoundError:
        raise ToolError(f"Cannot run '{cmd[0]}': executable not found.") from None
    except subprocess.TimeoutExpired as exc:
        raise ToolError(f"'{cmd[0]}' timed out after {timeout}s: {tail(exc.stderr)}") from None
    except OSError as exc:
        raise ToolError(f"Cannot run '{cmd[0]}' ({type(exc).__name__}).") from None
    if check and proc.returncode != 0:
        raise ToolError(f"'{Path(str(cmd[0])).name}' failed (exit {proc.returncode}): {tail(proc.stderr)}")
    return proc


def parse_time(value) -> float | None:
    """Accept SS, MM:SS, HH:MM:SS (fractions allowed). None passes through."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    parts = str(value).strip().split(":")
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"Bad time '{value}'. Use SS, MM:SS or HH:MM:SS.")
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        raise ValueError(f"Bad time '{value}'. Use SS, MM:SS or HH:MM:SS.") from None
    total = 0.0
    for n in nums:
        total = total * 60 + n
    return total


def fmt_time(seconds: float, decimals: int = 0) -> str:
    """MM:SS (or HH:MM:SS), optionally with decimals: 01:05.3"""
    seconds = max(0.0, float(seconds))
    if decimals:
        whole = int(seconds)
        frac = f"{seconds - whole:.{decimals}f}"[1:]  # '.3'
    else:
        whole = int(round(seconds))
        frac = ""
    h, rem = divmod(whole, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}{frac}" if h else f"{m:02d}:{s:02d}{frac}"


def parse_time_list(value: str | None) -> list[float]:
    if not value:
        return []
    return sorted({parse_time(v) for v in value.split(",") if v.strip()})


def write_json(path: Path, obj) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def log(msg: str) -> None:
    print(f"[watch] {msg}", file=sys.stderr, flush=True)
