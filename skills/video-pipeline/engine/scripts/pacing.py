"""Editorial pacing metrics, computed from the FULL shot list (never from a
frame-capped sample), so the numbers stay honest on fast-cut videos."""
from __future__ import annotations

import json
import statistics
import sys


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = (len(ordered) - 1) * pct / 100.0
    lo, hi = int(k), min(int(k) + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def pace_label(median_shot: float) -> str:
    if median_shot < 1.2:
        return "frenetic"
    if median_shot < 2.5:
        return "fast"
    if median_shot < 5.0:
        return "moderate"
    if median_shot < 10.0:
        return "slow"
    return "very slow / mostly static"


def compute_pacing(shots: list[dict], t0: float, t1: float,
                   window: float | None = None) -> dict:
    duration = max(0.0, t1 - t0)
    if not shots or duration <= 0:
        return {"shot_count": 0, "cut_count": 0, "cuts_per_minute": 0.0}
    durs = [s["duration"] for s in shots]
    cut_times = [s["start"] for s in shots[1:]]
    cuts = len(cut_times)
    median = statistics.median(durs)

    window = window or max(5.0, round(duration / 12.0))
    curve = []
    w0 = t0
    while w0 < t1 - 1e-6:
        w1 = min(t1, w0 + window)
        n = sum(1 for t in cut_times if w0 <= t < w1)
        curve.append({"start": round(w0, 1), "end": round(w1, 1),
                      "cuts": n, "cuts_per_minute": round(n / ((w1 - w0) / 60.0), 1)})
        w0 = w1

    longest = max(shots, key=lambda s: s["duration"])
    shortest = min(shots, key=lambda s: s["duration"])
    soft = sum(1 for s in shots[1:] if s["transition_in"] == "soft")
    return {
        "shot_count": len(shots),
        "cut_count": cuts,
        "cuts_per_minute": round(cuts / (duration / 60.0), 2),
        "mean_shot_length": round(statistics.mean(durs), 2),
        "median_shot_length": round(median, 2),
        "p10_shot_length": round(percentile(durs, 10), 2),
        "p90_shot_length": round(percentile(durs, 90), 2),
        "shortest_shot": {"id": shortest["id"], "duration": shortest["duration"]},
        "longest_shot": {"id": longest["id"], "duration": longest["duration"]},
        "soft_transition_share": round(soft / cuts, 2) if cuts else 0.0,
        "pace": pace_label(median),
        "curve_window_seconds": window,
        "curve": curve,
        "hook": {
            "first_shot_duration": shots[0]["duration"],
            "cuts_in_first_3s": sum(1 for t in cut_times if t - t0 < 3.0),
            "cuts_in_first_10s": sum(1 for t in cut_times if t - t0 < 10.0),
        },
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: pacing.py <duration-seconds> <cut-time> [<cut-time> ...]", file=sys.stderr)
        raise SystemExit(2)
    dur = float(sys.argv[1])
    cuts = sorted(float(x) for x in sys.argv[2:])
    bounds = [0.0] + cuts + [dur]
    demo = [{"id": i + 1, "start": bounds[i], "end": bounds[i + 1],
             "duration": bounds[i + 1] - bounds[i],
             "transition_in": "start" if i == 0 else "cut"} for i in range(len(bounds) - 1)]
    print(json.dumps(compute_pacing(demo, 0.0, dur), indent=2))
