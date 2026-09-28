#!/usr/bin/env python3
"""Summarise a perflog.sh CSV into the numbers used in benchmarks/log.md.

Usage: python3 tools/summarize.py run.csv [--skip SECONDS] [--until SECONDS]

--skip ignores samples before N seconds (cool-down, menus, loading).
--until ignores samples after N seconds (exiting the game, plugging back in).
"""
import argparse
import csv
import statistics


def pct_low(values, pct):
    """Average of the lowest `pct`% of samples (e.g. 1% / 5% lows)."""
    ordered = sorted(values)
    n = max(1, round(len(ordered) * pct / 100))
    return statistics.fmean(ordered[:n])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--skip", type=int, default=0, help="ignore samples before this time (s)")
    ap.add_argument("--until", type=int, default=None, help="ignore samples after this time (s)")
    args = ap.parse_args()

    with open(args.csv, newline="") as f:
        rows = [
            r for r in csv.DictReader(f)
            if int(r["t_s"]) >= args.skip and (args.until is None or int(r["t_s"]) <= args.until)
        ]
    if not rows:
        raise SystemExit("no samples after --skip")

    # game_fps = the emulator's own surface (current logger); older logs only have
    # "fps" (whole-screen compositions), which is valid for PPSSPP but not Dolphin.
    fps_col = "game_fps" if "game_fps" in rows[0] else "fps"
    fps = [float(r[fps_col]) for r in rows]
    col = lambda name: [float(r[name]) for r in rows if r[name]]

    # Sustained performance: compare the first and last 3 minutes of the run.
    window = 180
    t0, t1 = int(rows[0]["t_s"]), int(rows[-1]["t_s"])
    first = [float(r[fps_col]) for r in rows if int(r["t_s"]) < t0 + window]
    last = [float(r[fps_col]) for r in rows if int(r["t_s"]) > t1 - window]

    print(f"duration        {t1 - t0} s ({len(rows)} samples, fps source: {fps_col})")
    print(f"avg fps         {statistics.fmean(fps):.1f}")
    print(f"5% low fps      {pct_low(fps, 5):.1f}")
    print(f"1% low fps      {pct_low(fps, 1):.1f}")
    print(f"first 3 min fps {statistics.fmean(first):.1f}")
    print(f"last 3 min fps  {statistics.fmean(last):.1f}")
    if statistics.fmean(first) > 0:
        print(f"sustain ratio   {statistics.fmean(last) / statistics.fmean(first) * 100:.0f}%  (last/first)")
    for name in ("temp_big_c", "temp_mid_c", "temp_gpu_c", "temp_batt_c"):
        vals = col(name)
        print(f"peak {name[5:-2]:<9} {max(vals):.1f} °C")
    # Clock sustain: throttling can show up in clocks before it shows up in FPS.
    def window_mean(name, lo, hi):
        vals = [float(r[name]) for r in rows if r[name] and lo <= int(r["t_s"]) <= hi]
        return statistics.fmean(vals) if vals else float("nan")

    for name, label in (("cpu_big_mhz", "X1"), ("cpu_mid_mhz", "A78"), ("gpu_mhz", "GPU")):
        a = window_mean(name, t0, t0 + window)
        b = window_mean(name, t1 - window, t1)
        print(f"{label:<4}mhz first/last {a:.0f} -> {b:.0f}  ({b / a * 100:.0f}%)")
    print(f"avg gpu busy    {statistics.fmean(col('gpu_busy_pct')):.0f}%")
    batt = col("batt_pct")
    print(f"battery used    {batt[0] - batt[-1]:.0f}%")


if __name__ == "__main__":
    main()
