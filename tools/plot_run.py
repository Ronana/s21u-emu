#!/usr/bin/env python3
"""Plot a perflog.sh CSV as an SVG: FPS, temperatures and clocks over time.

Usage: python3 tools/plot_run.py run.csv out.svg [--skip S] [--until S] [--title TEXT]

Dependency-free (standard library only). Three stacked panels share the time axis;
each panel has its own single y-axis (no dual axes).
"""
import argparse
import csv
from xml.sax.saxutils import escape

# Reference categorical palette, first three slots (validated all-pairs, light mode).
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"

W, PANEL_H, GAP = 900, 170, 46
LEFT, RIGHT, TOP = 64, 92, 56
PLOT_W = W - LEFT - RIGHT

PANELS = [
    ("Frames per second (game)", "fps", [("game_fps", "FPS")]),
    ("Temperature (°C)", "°C", [("temp_big_c", "X1 (BIG)"), ("temp_mid_c", "A78 (MID)"), ("temp_gpu_c", "GPU")]),
    ("Clock speed (MHz)", "MHz", [("cpu_big_mhz", "X1"), ("cpu_mid_mhz", "A78"), ("gpu_mhz", "GPU")]),
]


def nice_max(v):
    for step in (10, 20, 25, 50, 100, 250, 500, 1000):
        if v <= step * 5:
            return step * -(-v // step), step
    return v, v / 5


def smooth(values, k=3):
    """Centred moving average to tame 2 s sampling noise (k samples each side)."""
    out = []
    for i in range(len(values)):
        win = values[max(0, i - k): i + k + 1]
        out.append(sum(win) / len(win))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("out")
    ap.add_argument("--skip", type=int, default=0)
    ap.add_argument("--until", type=int, default=None)
    ap.add_argument("--title", default="")
    args = ap.parse_args()

    with open(args.csv, newline="") as f:
        rows = [
            r for r in csv.DictReader(f)
            if int(r["t_s"]) >= args.skip and (args.until is None or int(r["t_s"]) <= args.until)
        ]
    if "game_fps" not in rows[0]:  # older logs: whole-screen composition rate
        for r in rows:
            r["game_fps"] = r["fps"]
    t0 = int(rows[0]["t_s"])
    ts = [(int(r["t_s"]) - t0) / 60 for r in rows]  # minutes since test start
    t_max = ts[-1]

    height = TOP + len(PANELS) * (PANEL_H + GAP) + 10
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
        f'font-family="-apple-system, Segoe UI, Roboto, sans-serif">',
        f'<rect width="100%" height="100%" fill="{SURFACE}"/>',
        f'<text x="{LEFT}" y="30" font-size="17" font-weight="600" fill="{TEXT}">{escape(args.title)}</text>',
    ]

    x = lambda t: LEFT + t / t_max * PLOT_W

    for p, (title, unit, series) in enumerate(PANELS):
        top = TOP + p * (PANEL_H + GAP) + 18
        data = {col: smooth([float(r[col] or 0) for r in rows]) for col, _ in series}
        ymax, step = nice_max(max(max(v) for v in data.values()) * 1.05)
        y = lambda v: top + PANEL_H - v / ymax * PANEL_H

        svg.append(f'<text x="{LEFT}" y="{top - 8}" font-size="13" font-weight="600" fill="{TEXT}">{title}</text>')
        tick = 0
        while tick <= ymax + 1e-9:  # recessive grid + y labels
            svg.append(f'<line x1="{LEFT}" x2="{LEFT + PLOT_W}" y1="{y(tick):.1f}" y2="{y(tick):.1f}" stroke="{GRID}" stroke-width="1"/>')
            svg.append(f'<text x="{LEFT - 8}" y="{y(tick) + 4:.1f}" font-size="11" fill="{TEXT_2}" text-anchor="end">{tick:g}</text>')
            tick += step
        for m in range(0, int(t_max) + 1, 2 if t_max > 12 else 1):  # x ticks (minutes)
            svg.append(f'<text x="{x(m):.1f}" y="{top + PANEL_H + 16}" font-size="11" fill="{TEXT_2}" text-anchor="middle">{m} min</text>')

        # Lines, then direct labels at the line ends (nudged apart so they never collide).
        ends = []
        for i, (col, label) in enumerate(series):
            pts = " ".join(f"{x(t):.1f},{y(v):.1f}" for t, v in zip(ts, data[col]))
            svg.append(f'<polyline points="{pts}" fill="none" stroke="{SERIES[i]}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
            ends.append([y(data[col][-1]), label, SERIES[i]])
        ends.sort()
        for j in range(1, len(ends)):
            ends[j][0] = max(ends[j][0], ends[j - 1][0] + 14)
        for ly, label, color in ends:
            svg.append(f'<circle cx="{LEFT + PLOT_W + 8}" cy="{ly - 4:.1f}" r="4" fill="{color}"/>')
            svg.append(f'<text x="{LEFT + PLOT_W + 16}" y="{ly:.1f}" font-size="11" fill="{TEXT}">{escape(label)}</text>')

    svg.append("</svg>")
    with open(args.out, "w") as f:
        f.write("\n".join(svg))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
