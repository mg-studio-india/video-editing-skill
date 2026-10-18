"""Shared helpers: time parsing/formatting, a safe subprocess wrapper, JSON I/O.

Stdlib only. Imported by every other script in this folder.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


class ToolError(RuntimeError):
    """A command-line tool failed. The message is safe to show the user."""


def _find_python_in_venv(venv: Path) -> Path | None:
    """Find python binary inside a virtual environment across Unix and Windows."""
    for cand in (
        venv / "bin" / "python3",
        venv / "bin" / "python",
        venv / "Scripts" / "python.exe",
        venv / "Scripts" / "python",
    ):
        if cand.is_file():
            return cand
    return None


def find_engine_dir() -> Path:
    """Find the global or sandboxed video-skills engine directory across OSes (macOS, Linux, Windows)."""
    # 1. Explicit environment variable
    env_dir = os.environ.get("VIDEO_ENGINE_DIR")
    if env_dir and Path(env_dir).is_dir():
        return Path(env_dir)

    # 2. Project-level isolated sandbox (.engine/)
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        cand = parent / ".engine"
        if cand.is_dir():
            return cand

    # 3. Global user engine sandbox (~/.video-skills/engine)
    global_dir = Path.home() / ".video-skills" / "engine"
    if global_dir.is_dir():
        return global_dir

    # 4. Standard XDG / config engine path (~/.config/video-skills/engine)
    config_engine = Path.home() / ".config" / "video-skills" / "engine"
    if config_engine.is_dir():
        return config_engine

    # 5. Fallback default
    return Path.home() / ".video-skills" / "engine"


def find_project_venv() -> Path | None:
    """Find the virtual environment (.venv) directory across OSes (macOS, Linux, Windows).
    Supports:
      - Active VIRTUAL_ENV / sys.prefix
      - Global Engine Sandbox: ~/.video-skills/engine/.venv
      - Project Isolated Sandbox: .engine/.venv
      - Workspace local: .venv
    """
    # 1. Active virtual environment from VIRTUAL_ENV env var
    venv_env = os.environ.get("VIRTUAL_ENV")
    if venv_env and Path(venv_env).is_dir():
        if _find_python_in_venv(Path(venv_env)):
            return Path(venv_env)

    # 2. Check if current sys.prefix is a venv
    if sys.prefix != sys.base_prefix:
        if _find_python_in_venv(Path(sys.prefix)):
            return Path(sys.prefix)

    # 3. Project Isolated Sandbox: .engine/.venv (CWD and parents)
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        cand = parent / ".engine" / ".venv"
        if cand.is_dir() and _find_python_in_venv(cand):
            return cand

    # 4. Global Engine Sandbox: ~/.video-skills/engine/.venv or ~/.config/video-skills/engine/.venv
    engine_venv = find_engine_dir() / ".venv"
    if engine_venv.is_dir() and _find_python_in_venv(engine_venv):
        return engine_venv

    global_cands = [
        Path.home() / ".video-skills" / "engine" / ".venv",
        Path.home() / ".config" / "video-skills" / "engine" / ".venv",
        Path.home() / ".local" / "share" / "video-engine" / ".venv",
    ]
    for g in global_cands:
        if g.is_dir() and _find_python_in_venv(g):
            return g

    # 5. Check CWD and parent directories for .venv
    for parent in [cwd] + list(cwd.parents):
        cand = parent / ".venv"
        if cand.is_dir() and _find_python_in_venv(cand):
            return cand

    # 6. Check relative to this file's hierarchy
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / ".venv"
        if cand.is_dir() and _find_python_in_venv(cand):
            return cand
        cand_engine = parent / ".engine" / ".venv"
        if cand_engine.is_dir() and _find_python_in_venv(cand_engine):
            return cand_engine
        sib = parent / "video-editing" / ".venv"
        if sib.is_dir() and _find_python_in_venv(sib):
            return sib

    # 7. Check sibling and parent video-editing directories if any
    for parent in here.parents:
        sib = parent / ".venv"
        if sib.is_dir() and _find_python_in_venv(sib):
            return sib

    return None



def get_project_venv_python() -> str:
    """Return the absolute path to the virtual environment python executable.
    Cross-platform: supports Unix (bin/python3, bin/python) and Windows (Scripts/python.exe, Scripts/python).
    """
    venv = find_project_venv()
    if not venv:
        raise ToolError(
            "Video editing virtual environment (.venv) not found.\n"
            "Checked locations across macOS, Linux, and Windows:\n"
            f"  - Project Sandbox: {Path.cwd() / '.engine' / '.venv'}\n"
            f"  - Global Engine: {find_engine_dir() / '.venv'}\n"
            f"  - Active VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV')}\n"
            "Please initialize the engine via install.sh or configure VIDEO_ENGINE_DIR."
        )
    py = _find_python_in_venv(venv)
    if not py:
        raise ToolError(f"Virtual environment at {venv} is missing python binary (bin/python3 or Scripts/python.exe).")
    return str(py.absolute())


def load_global_env() -> None:
    """Load API keys from global engine ~/.config/video-skills/.env and ~/.video-skills/engine/.env."""
    for cand in (
        Path.home() / ".config" / "video-skills" / ".env",
        find_engine_dir() / ".env",
        Path.cwd() / ".engine" / ".env",
        Path.cwd() / ".env",
    ):
        if cand.is_file():
            try:
                for line in cand.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v
            except Exception:
                pass


def ensure_project_venv() -> None:
    """Enforce that the current process is running inside the virtual environment.
    If running under system Python, automatically re-executes using the engine .venv python.
    Also ensures engine node_modules/.bin is prepended to PATH for HyperFrames CLI.
    """
    load_global_env()
    venv_py = get_project_venv_python()
    venv_dir = str(Path(venv_py).parent.parent.absolute())

    # Prepend engine node_modules/.bin and venv bin/Scripts to PATH
    engine_node_bin = str(find_engine_dir() / "node_modules" / ".bin")
    venv_bin = str(Path(venv_py).parent)

    # Check if we are already running inside this virtual environment
    if sys.prefix != sys.base_prefix and Path(sys.prefix).absolute() == Path(venv_dir).absolute():
        if Path(engine_node_bin).is_dir() and engine_node_bin not in os.environ.get("PATH", ""):
            os.environ["PATH"] = f"{engine_node_bin}{os.pathsep}{os.environ.get('PATH', '')}"
        return

    # Check loop prevention marker
    if os.environ.get("_SKILL_VENV_ENFORCED") == venv_py:
        return

    env = dict(os.environ)
    env["VIRTUAL_ENV"] = venv_dir
    current_path = env.get("PATH", "")
    new_path_parts = [venv_bin]
    if Path(engine_node_bin).is_dir():
        new_path_parts.append(engine_node_bin)
    new_path_parts.append(current_path)
    env["PATH"] = os.pathsep.join(new_path_parts)
    env["_SKILL_VENV_ENFORCED"] = venv_py
    os.execve(venv_py, [venv_py] + sys.argv, env)



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
