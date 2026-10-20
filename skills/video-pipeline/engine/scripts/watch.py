#!/usr/bin/env python3
"""watch: local video analysis for storyboarding references and planning edits."""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import audio as audio_mod  # noqa: E402
import config  # noqa: E402
import download as download_mod  # noqa: E402
import editplan as ep  # noqa: E402
import fingerprint as fp_mod  # noqa: E402
import frames as frames_mod  # noqa: E402
import pacing as pacing_mod  # noqa: E402
import probe as probe_mod  # noqa: E402
import shots as shots_mod  # noqa: E402
import speech as speech_mod  # noqa: E402
import storyboard as sb_mod  # noqa: E402
import transcribe_cpp as asr  # noqa: E402
from runtime import (ToolError, configure_stdio, fmt_time, log, parse_time,  # noqa: E402
                     parse_time_list, read_json, write_json)

DEFAULT_FRAMES = {"ref": 60, "mine": 36, "focus": 16}


# ---------------------------------------------------------------- helpers
def resolve_source(source: str, cfg: dict) -> Path:
    if download_mod.is_url(source):
        return download_mod.download(source, config.cache_root(cfg) / "downloads")
    p = Path(source).expanduser()
    if not p.is_file():
        raise ToolError(f"File not found: {source}")
    return p.resolve()


def base_dir(video: Path, cfg: dict, out_dir: str | None) -> Path:
    if out_dir:
        return Path(out_dir).expanduser().resolve()
    st = video.stat()
    key = hashlib.sha1(f"{video}|{st.st_size}|{st.st_mtime_ns}".encode()).hexdigest()[:10]
    slug = re.sub(r"[^\w.-]+", "_", video.stem)[:40]
    return config.cache_root(cfg) / f"{slug}-{key}"


def resolve_range(args, duration: float) -> tuple[float, float, bool]:
    t0 = parse_time(args.start) or 0.0
    t1 = parse_time(args.end)
    if t1 is None or t1 > duration:
        t1 = duration
    if t0 < 0 or t0 >= t1:
        raise ToolError(f"Bad range: start {fmt_time(t0)} must be before end {fmt_time(t1)} "
                        f"(video is {fmt_time(duration)} long).")
    return t0, t1, (t0 <= 0.0 and t1 >= duration - 0.01)


def get_transcript(video: Path, meta: dict, base: Path, run_dir: Path, t0: float, t1: float,
                   full_range: bool, args, cfg: dict, warnings: list[str]) -> dict | None:
    if not meta["has_audio"]:
        warnings.append("no audio stream: nothing to transcribe")
        return None
    if args.no_transcript:
        return None
    full_path = base / "transcript.json"
    try:
        if full_path.is_file() and not args.fresh:
            full = read_json(full_path)
            tr = full if full_range else asr.filter_range(full, t0, t1)
            log("using cached transcript")
        else:
            tr = asr.transcribe(str(video), base, None if full_range else t0,
                                None if full_range else t1, cfg)
            if full_range:
                write_json(full_path, tr)
    except ToolError as exc:
        warnings.append(f"transcript unavailable: {exc}")
        return None
    write_json(run_dir / "transcript.json", tr)
    return tr


# ---------------------------------------------------------------- core analysis
def analyze(args, mode: str) -> dict:
    cfg = config.load()
    video = resolve_source(args.source, cfg)
    meta = probe_mod.probe(video)
    t0, t1, full_range = resolve_range(args, meta["duration"])
    base = base_dir(video, cfg, args.out_dir)
    base.mkdir(parents=True, exist_ok=True)
    run_dir = base / ("full" if full_range else f"range_{int(t0)}-{int(t1)}")
    run_dir.mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []
    rs, re_ = (t0 if t0 > 0 else None), (t1 if t1 < meta["duration"] - 0.01 else None)

    thr = float(args.scene_threshold) if args.scene_threshold else float(cfg["WATCH_SCENE_THRESHOLD"])
    log("detecting shots…")
    shots = shots_mod.build_shots(shots_mod.detect_cuts(str(video), rs, re_, thr), t0, t1)

    black, freeze = [], []
    try:
        bf = shots_mod.detect_black_freeze(str(video), rs, re_)
        black, freeze = bf["black"], shots_mod.close_open_freezes(bf["freeze"], t1)
    except ToolError as exc:
        warnings.append(f"black/freeze detection skipped: {exc}")

    audio = None
    silences: list[dict] = []
    if meta["has_audio"]:
        try:
            log("measuring audio…")
            silences = audio_mod.silences(str(video), rs, re_, total_duration=t1)
            audio = {"loudness": audio_mod.loudness(str(video), rs, re_), "silences": silences,
                     "silence_ratio": round(sum(s["duration"] for s in silences) / (t1 - t0), 3)}
        except ToolError as exc:
            warnings.append(f"audio analysis skipped: {exc}")

    tr = get_transcript(video, meta, base, run_dir, t0, t1, full_range, args, cfg, warnings)
    words = tr["words"] if tr else []
    speech = speech_mod.speech_stats(words, t0, t1) if tr else {"has_speech": False}
    cut_align = {}
    if tr:
        speech_mod.assign_words_to_shots(shots, words)
        cut_align = speech_mod.cut_alignment(shots, tr["segments"], silences)
    pacing = pacing_mod.compute_pacing(shots, t0, t1)

    sheets = hook_sheets = None
    frame_items: list[dict] = []
    hook_items: list[dict] = []
    if not args.no_frames:
        aspect = meta["aspect"] or (16 / 9)
        max_frames = args.max_frames or DEFAULT_FRAMES[mode]
        log("extracting frames…")
        items = frames_mod.pick_times(shots, t0, t1, max_frames, args.hook_seconds, parse_time_list(args.timestamps))
        items = frames_mod.extract_frames(str(video), items, run_dir / "frames", args.frame_width)
        if not args.no_dedup:
            items, _ = frames_mod.dedupe(items)
        frame_items = items
        sheets = frames_mod.make_sheets(items, run_dir / "sheets", aspect, "sheet")
        if not args.no_hook and args.hook_seconds > 0:
            hook_items = frames_mod.extract_frames(
                str(video),
                [{"t": t, "kind": "hook", "shot": None}
                 for t in frames_mod.hook_times(t0, t1, args.hook_seconds, args.hook_step)],
                run_dir / "hook", args.frame_width)
            hook_sheets = frames_mod.make_sheets(hook_items, run_dir / "sheets", aspect, "hook", with_shot=False)
        if sheets is None:
            warnings.append("Pillow not installed: showing individual frames instead of contact sheets "
                            "(python3 -m pip install pillow)")

    analysis = {
        "schema": "watch.analysis/1",
        "meta": meta,
        "range": {"start": round(t0, 3), "end": round(t1, 3), "duration": round(t1 - t0, 3), "full": full_range},
        "settings": {"scene_threshold": thr},
        "shots": shots,
        "pacing": pacing,
        "black": black,
        "freeze": freeze,
        "audio": audio,
        "speech": speech,
        "cut_alignment": cut_align,
        "transcript": ({"engine": tr["engine"], "model": tr["model"], "language": tr["language"],
                        "word_count": len(words), "sound_cues": len(tr["sound_cues"]),
                        "loops_collapsed": tr["loops_collapsed"]} if tr else None),
        "frames": {
            "frames": [{k: it.get(k) for k in ("t", "kind", "shot", "path")} for it in frame_items],
            "hook_frames": [{k: it.get(k) for k in ("t", "path")} for it in hook_items],
            "sheets": sheets, "hook_sheets": hook_sheets,
        },
        "warnings": warnings,
    }
    write_json(run_dir / "analysis.json", analysis)

    fp = fp_mod.build(analysis)
    fp_path = run_dir / "fingerprint.json"
    if fp_path.is_file() and not args.fresh:  # keep any qualitative fields Claude already filled in
        try:
            old = read_json(fp_path)
            if old.get("schema") == fp["schema"]:
                fp["qualitative"] = old.get("qualitative", fp["qualitative"])
        except (ValueError, OSError):
            pass
    write_json(fp_path, fp)

    return {"video": video, "meta": meta, "base": base, "run_dir": run_dir, "analysis": analysis,
            "transcript": tr, "sheets": sheets, "hook_sheets": hook_sheets,
            "frame_items": frame_items, "hook_items": hook_items, "fingerprint": fp,
            "range": (t0, t1), "warnings": warnings}


# ---------------------------------------------------------------- printing
def headline(res: dict, label: str) -> list[str]:
    m, a = res["meta"], res["analysis"]
    p, sp = a["pacing"], a["speech"]
    loud = (a.get("audio") or {}).get("loudness") or {}
    t0, t1 = res["range"]
    lines = [f"# watch · {label} · {m['filename']}",
             f"{fmt_time(t1 - t0)} analysed ({fmt_time(t0)}-{fmt_time(t1)}) · {m['width']}x{m['height']} "
             f"{m['orientation']} · {m['fps']} fps · audio: {'yes' if m['has_audio'] else 'no'}",
             f"Shots {p['shot_count']} · {p['cuts_per_minute']} cuts/min · median shot "
             f"{p['median_shot_length']}s ({p['pace']}) · soft transitions {int(p['soft_transition_share'] * 100)}%"]
    if sp.get("has_speech"):
        lines.append(f"Speech {sp['words_per_minute']} wpm · first word at {sp['time_to_first_word']}s · "
                     f"{sp['fillers_per_minute']} fillers/min · longest pause {sp['longest_pause']}s")
    if loud.get("integrated_lufs") is not None:
        lines.append(f"Loudness {loud['integrated_lufs']} LUFS · true peak {loud.get('true_peak_dbtp')} dBTP")
    tr = a["transcript"]
    lines.append(f"Transcript: {tr['engine']} {tr['model']} · {tr['language']} · {tr['word_count']} words"
                 if tr else "Transcript: none")
    return lines


def image_list(res: dict) -> list[str]:
    out = ["", "## Look at these images next (Read each, in order)"]
    hs, ss = res["hook_sheets"], res["sheets"]
    if hs:
        out.append("Hook sheets (every frame is labelled with its time):")
        out += [f"- {h['path']}" for h in hs]
    elif res["hook_items"]:
        out.append("Hook frames:")
        out += [f"- {i['path']}  ({fmt_time(i['t'], 1)})" for i in res["hook_items"]]
    if ss:
        out.append("Shot sheets (labels show #shot and time):")
        for s in ss:
            first, last = s["cells"][0], s["cells"][-1]
            out.append(f"- {s['path']}  (S{s['number']}: {first['label']} to {last['label']})")
    elif res["frame_items"]:
        out.append("Shot frames:")
        out += [f"- {i['path']}  (#{i['shot']} {fmt_time(i['t'], 1)})" for i in res["frame_items"]]
    return out


def warnings_block(warnings: list[str]) -> list[str]:
    return (["", "## Warnings"] + [f"- {w}" for w in warnings]) if warnings else []


# ---------------------------------------------------------------- commands
def cmd_ref(args) -> int:
    res = analyze(args, "ref")
    a, rd = res["analysis"], res["run_dir"]
    md = sb_mod.render(a, res["transcript"], args.intent, res["sheets"], res["hook_sheets"])
    sb_path = rd / "storyboard.md"
    note = ""
    if sb_path.exists() and not args.fresh:
        sb_path = rd / "storyboard.skeleton.md"
        note = " (existing storyboard.md kept; this is a fresh skeleton)"
    sb_path.write_text(md, encoding="utf-8")
    unfilled = len(sb_mod.lint(sb_path))

    out = headline(res, "ref") + image_list(res) + warnings_block(res["warnings"])
    out += ["", "## Files", f"- {sb_path}{note}  ({unfilled} lines still have ⟨fill⟩)",
            f"- {rd / 'fingerprint.json'}  (measured numbers filled; `qualitative` is yours to fill)",
            f"- {rd / 'analysis.json'}  (all shots, pacing, audio)",
            f"- {rd / 'transcript.json'}" if res["transcript"] else "- (no transcript)",
            "", "## Next",
            "1. Read the images above. 2. Fill every ⟨fill⟩ in the storyboard. 3. Fill fingerprint.json `qualitative`. "
            f"4. `python3 {Path(__file__).name} lint <file>` until clean."]
    print("\n".join(out))
    return 0


def cmd_mine(args) -> int:
    res = analyze(args, "mine")
    a, rd, tr, meta = res["analysis"], res["run_dir"], res["transcript"], res["meta"]
    t0, t1 = res["range"]
    ref_fp = read_json(Path(args.against)) if args.against else None

    flags = ep.qa_flags(a, ref_fp, args.target_lufs)
    rows = fp_mod.compare(ref_fp, res["fingerprint"]) if ref_fp else []

    opts = {"max_pause": args.max_pause, "keep_pause": args.keep_pause,
            "cut_fillers": not args.keep_fillers, "cut_retakes": not args.keep_retakes,
            "trim_ends": not args.no_trim_ends, "jump_cut_zoom": args.jump_cut_zoom}
    ref_cw = ((ref_fp or {}).get("qualitative", {}).get("caption_style") or {}).get("words_per_caption")
    opts["caption_words"] = args.caption_words or (int(ref_cw) if isinstance(ref_cw, (int, float)) else 3)

    words, segments = (tr["words"], tr["segments"]) if tr else ([], [])
    if not tr:
        res["warnings"].append("no transcript: rough cut keeps everything; fillers/pauses/retakes not analysed")
    keep, removed = ep.build_keep_ranges(words, segments, t0, t1, opts)
    stats = ep.cutlist_stats(keep, removed, t0, t1)
    style = {}
    if ref_fp:
        pc, sp = ref_fp.get("pacing", {}), ref_fp.get("speech", {})
        style = {"cuts_per_minute": pc.get("cuts_per_minute"), "median_shot_length": pc.get("median_shot_length"),
                 "hook_cuts_in_first_10s": (pc.get("hook") or {}).get("cuts_in_first_10s"),
                 "words_per_minute": sp.get("words_per_minute"),
                 "integrated_lufs": (ref_fp.get("audio") or {}).get("integrated_lufs")}
    plan = ep.make_edit_plan(meta, keep, words, opts, style)

    write_json(rd / "cutlist.json", {"keep": keep, "removed": removed, "stats": stats, "options": opts})
    write_json(rd / "edit-plan.json", plan)
    preview = None
    if args.preview:
        if tr:
            preview = ep.render_preview(str(res["video"]), keep, rd / "preview.mp4", meta["has_audio"])
        else:
            res["warnings"].append("preview skipped: needs a transcript to decide what to cut")

    report = ["# Mine report", "", *headline(res, "mine"), "", "## QA flags"]
    if flags:
        report += ["| Severity | Issue | Suggestion |", "|---|---|---|"]
        report += [f"| {f['severity']} | {f['issue']} | {f['suggestion']} |" for f in flags]
    else:
        report.append("No flags raised.")
    if rows:
        report += ["", "## Against the reference", fp_mod.compare_markdown(rows)]
    report += ["", "## Suggested tight cut (review before using)",
               f"- {stats['original_duration']}s → {stats['new_duration']}s "
               f"({int(stats['removed_share'] * 100)}% removed) in {stats['clip_count']} clips",
               f"- removed seconds by reason: {stats['removed_seconds_by_reason']}"]
    report += [f"- cut {fmt_time(r['start'], 1)}-{fmt_time(r['end'], 1)} ({'/'.join(r['reasons'])}) {r['text']}".rstrip()
               for r in removed[:25]]
    (rd / "mine-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    out = headline(res, "mine") + image_list(res) + warnings_block(res["warnings"])
    out += ["", "## QA flags (" + str(len(flags)) + ")"]
    out += [f"- [{f['severity']}] {f['issue']} → {f['suggestion']}" for f in flags[:12]] or ["- none"]
    if rows:
        out += ["", "## Against the reference", fp_mod.compare_markdown(rows)]
    out += ["", f"## Suggested tight cut: {stats['original_duration']}s → {stats['new_duration']}s "
            f"({int(stats['removed_share'] * 100)}% removed, {stats['clip_count']} clips)",
            "", "## Files", f"- {rd / 'mine-report.md'}", f"- {rd / 'cutlist.json'}", f"- {rd / 'edit-plan.json'}"]
    if preview:
        out.append(f"- {preview}  (quick preview of the tight cut)")
    print("\n".join(out))
    return 0


def cmd_focus(args) -> int:
    if args.start is None or args.end is None:
        raise ToolError("focus needs --start and --end (e.g. --start 0:12 --end 0:20).")
    cfg = config.load()
    video = resolve_source(args.source, cfg)
    meta = probe_mod.probe(video)
    t0, t1, full_range = resolve_range(args, meta["duration"])
    base = base_dir(video, cfg, args.out_dir)
    base.mkdir(parents=True, exist_ok=True)
    run_dir = base / f"focus_{int(t0)}-{int(t1)}"
    run_dir.mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []

    cuts = shots_mod.detect_cuts(str(video), t0, t1, float(cfg["WATCH_SCENE_THRESHOLD"]))
    tr = get_transcript(video, meta, base, run_dir, t0, t1, full_range, args, cfg, warnings)

    span = t1 - t0
    max_frames = args.max_frames or DEFAULT_FRAMES["focus"]
    step = args.step or max(0.5, span / max_frames)
    times = [round(t0 + i * step, 3) for i in range(int(span / step) + 1) if t0 + i * step <= t1]
    times = sorted(set(times + parse_time_list(args.timestamps)))[: max_frames + 8]
    items = frames_mod.extract_frames(str(video), [{"t": t, "kind": "focus", "shot": None} for t in times],
                                      run_dir / "frames", args.frame_width or 768)
    out = [f"# watch · focus · {meta['filename']}",
           f"{fmt_time(t0, 1)}-{fmt_time(t1, 1)} ({span:.1f}s) · {meta['width']}x{meta['height']} · {meta['fps']} fps",
           f"Cuts in range: " + (", ".join(fmt_time(c["t"], 2) for c in cuts) or "none")]
    if tr:
        out += ["", "## Words (with timing)"]
        for seg in tr["segments"]:
            ws = [w for w in tr["words"] if seg["start"] <= w["start"] <= seg["end"]]
            out.append(f"- [{fmt_time(seg['start'], 1)}] " + " ".join(f"{w['w']}@{w['start']:.1f}" for w in ws))
    out += ["", "## Look at these frames (Read each)"]
    out += [f"- {i['path']}  ({fmt_time(i['t'], 1)})" for i in items]
    out += warnings_block(warnings)
    print("\n".join(out))
    return 0


def cmd_compare(args) -> int:
    print(fp_mod.compare_markdown(fp_mod.compare(read_json(Path(args.reference)), read_json(Path(args.mine)))))
    return 0


def cmd_lint(args) -> int:
    path = Path(args.file)
    if not path.is_file():
        raise ToolError(f"File not found: {path}")
    if path.suffix.lower() == ".json":
        n = fp_mod.count_unfilled(read_json(path))
        print("fingerprint: all qualitative fields filled" if n == 0
              else f"fingerprint: {n} qualitative field(s) still null")
        return 0 if n == 0 else 1
    problems = sb_mod.lint(path)
    if problems:
        print(f"{len(problems)} line(s) still contain ⟨fill⟩:")
        print("\n".join(problems[:40]))
        if len(problems) > 40:
            print(f"... and {len(problems) - 40} more")
        return 1
    print("storyboard: no unfilled markers")
    return 0


def cmd_check(args) -> int:
    import setup as setup_mod
    sys.argv = ["setup.py"] + (["--json"] if args.json else [])
    return setup_mod.main()


# ---------------------------------------------------------------- CLI
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="watch.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, frames: bool = True):
        p.add_argument("source", help="video file path (or URL; needs yt-dlp)")
        p.add_argument("--start", help="range start: SS, MM:SS or HH:MM:SS")
        p.add_argument("--end", help="range end")
        p.add_argument("--out-dir", help="write artifacts here instead of the cache")
        p.add_argument("--fresh", action="store_true", help="ignore cached transcript, overwrite outputs")
        p.add_argument("--no-transcript", action="store_true", help="skip whisper.cpp")
        p.add_argument("--scene-threshold", help="cut sensitivity 0-1 (default 0.20; lower finds softer cuts)")
        p.add_argument("--timestamps", help="comma-separated moments to always capture, e.g. 0:12,1:30")
        p.add_argument("--max-frames", type=int, help="frame budget for contact sheets")
        p.add_argument("--frame-width", type=int, default=640 if frames else None)
        if frames:
            p.add_argument("--hook-seconds", type=float, default=10.0)
            p.add_argument("--hook-step", type=float, default=0.5)
            p.add_argument("--no-hook", action="store_true")
            p.add_argument("--no-frames", action="store_true")
            p.add_argument("--no-dedup", action="store_true")

    r = sub.add_parser("ref", help="storyboard + fingerprint of a reference video")
    common(r)
    r.add_argument("--intent", help="what you want from this reference, e.g. 'hook and caption style'")
    r.set_defaults(fn=cmd_ref)

    m = sub.add_parser("mine", help="QA + tight cut + edit plan for your own footage")
    common(m)
    m.add_argument("--against", help="reference fingerprint.json to compare with")
    m.add_argument("--max-pause", type=float, default=ep.DEFAULT_OPTS["max_pause"])
    m.add_argument("--keep-pause", type=float, default=ep.DEFAULT_OPTS["keep_pause"])
    m.add_argument("--keep-fillers", action="store_true", help="do not cut um/uh")
    m.add_argument("--keep-retakes", action="store_true", help="do not cut detected retakes")
    m.add_argument("--no-trim-ends", action="store_true", help="keep dead air before/after speech")
    m.add_argument("--caption-words", type=int, help="words per caption (default 3, or the reference's)")
    m.add_argument("--jump-cut-zoom", action="store_true", help="suggest alternating punch-ins on clips")
    m.add_argument("--target-lufs", type=float, help="loudness target (default: reference's, else -14)")
    m.add_argument("--preview", action="store_true", help="render a quick preview.mp4 of the tight cut")
    m.set_defaults(fn=cmd_mine)

    f = sub.add_parser("focus", help="dense frames + words for one moment")
    common(f, frames=False)
    f.add_argument("--step", type=float, help="seconds between frames")
    f.set_defaults(fn=cmd_focus, no_frames=False, hook_seconds=0, hook_step=0.5, no_hook=True, no_dedup=True)

    c = sub.add_parser("compare", help="compare two fingerprints")
    c.add_argument("reference")
    c.add_argument("mine")
    c.set_defaults(fn=cmd_compare)

    l = sub.add_parser("lint", help="fail while a storyboard/fingerprint has unfilled parts")
    l.add_argument("file")
    l.set_defaults(fn=cmd_lint)

    k = sub.add_parser("check", help="preflight")
    k.add_argument("--json", action="store_true")
    k.set_defaults(fn=cmd_check)
    return ap


def main() -> int:
    configure_stdio()
    args = build_parser().parse_args()
    try:
        return args.fn(args)
    except ToolError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
