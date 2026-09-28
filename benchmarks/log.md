# Benchmark log

## Method

- One test game per emulator, **15-minute** session, same scene each run.
- Record: average FPS, 1% low FPS (if available), peak temperature, ambient temperature, charging state, cooler on/off.
- Change **one variable per run**.
- Record with [`tools/perflog.sh`](../tools/perflog.sh) and summarise with [`tools/summarize.py`](../tools/summarize.py).

### Recording a run

```bash
# once: copy the logger to the phone
adb push tools/perflog.sh /data/local/tmp/perflog.sh

# start logging (15 min, 2 s samples), then launch the game
adb shell 'su -c "sh /data/local/tmp/perflog.sh 900 2 /sdcard/perflog/<emulator>-<run>.csv"'

# afterwards: pull and summarise (skip the first ~60 s of menus/loading)
adb pull /sdcard/perflog/<emulator>-<run>.csv benchmarks/raw/
python3 tools/summarize.py benchmarks/raw/<emulator>-<run>.csv --skip 60
```

The logger samples SurfaceFlinger's composited-frame counter (FPS), CPU cluster clocks (A55/A78/X1), GPU clock and load, the `BIG`/`MID`/`LITTLE`/`G3D`/battery temperatures, and battery state. The summary reports average FPS, 1%/5% lows, first-3-min vs last-3-min FPS (the **sustain ratio**, which is the number Phase 2 is trying to improve), and peak temperatures.

**Device state at baseline:** UN1CA 3.2.0, Floppy2100 v1.1.2 (`energy_step` governor, stock clocks: A55 2.21 GHz / A78 2.81 GHz / X1 2.91 GHz, GPU 858 MHz), display FHD+ 1080×2400 @ 120 Hz, RAM Plus off, no cooler.

## Runs

| Date | Emulator (version) | Game / scene | Settings | Tuning profile | Avg FPS | 1% low | Sustain ratio | Peak CPU °C | Peak GPU °C | Ambient °C | Cooler | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Before / after summary

_Filled in at the end of Phase 2._
