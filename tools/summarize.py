#!/usr/bin/env python3
"""Summarise a perflog.sh CSV into the numbers used in benchmarks/log.md.

Usage: python3 tools/summarize.py run.csv [--skip SECONDS]

--skip ignores the first N seconds (menus/loading) before the test scene starts.
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
    ap.add_argument("--skip", type=int, default=0, help="seconds to ignore at the start")
    args = ap.parse_args()

    with open(args.csv, newline="") as f:
        rows = [r for r in csv.DictReader(f) if int(r["t_s"]) >= args.skip]
    if not rows:
        raise SystemExit("no samples after --skip")

    fps = [float(r["fps"]) for r in rows]
    col = lambda name: [float(r[name]) for r in rows if r[name]]

    # Sustained performance: compare the first and last 3 minutes of the run.
    window = 180
    t0, t1 = int(rows[0]["t_s"]), int(rows[-1]["t_s"])
    first = [float(r["fps"]) for r in rows if int(r["t_s"]) < t0 + window]
    last = [float(r["fps"]) for r in rows if int(r["t_s"]) > t1 - window]

    print(f"duration        {t1 - t0} s ({len(rows)} samples)")
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
    print(f"avg big mhz     {statistics.fmean(col('cpu_big_mhz')):.0f}")
    print(f"avg gpu mhz     {statistics.fmean(col('gpu_mhz')):.0f}")


if __name__ == "__main__":
    main()
