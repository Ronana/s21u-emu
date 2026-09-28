# Phase 2: Tuning for sustained performance

Goal: flat, full-speed gameplay over a 10-minute session, not a peak-benchmark number. Every change is measured against a baseline with [`tools/perflog.sh`](../tools/perflog.sh), one variable at a time. Results go in [`benchmarks/log.md`](../benchmarks/log.md).

## What the baselines say

| Emulator | Bottleneck | Evidence | Tuning goal |
|---|---|---|---|
| PPSSPP (Midnight Club, 4×) | Neither: runs locked at 60 | FPS 100% sustained; clocks drop to ~75% by the end; 76 °C | Same 60 FPS, cooler and on less power |
| Dolphin (TimeSplitters, 2×) | **CPU** | GPU ~34% busy; X1 held at 1.56 GHz from ~5 min; 80 °C; game slows down (emulation < 100%) | Full speed for longer; remove shader stutter |

## Dolphin test plan

Based on Dolphin's official [performance guide](https://dolphin-emu.org/docs/guides/performance-guide/), filtered for a **CPU-bound phone with a Mali GPU that has spare headroom**. Each test changes **one** setting from the baseline; the winners are then combined into a tuned profile and re-measured.

**Baseline:** Vulkan · 2× internal resolution · 60 Hz · Specialized shaders (default) · warm shader cache · all hacks at defaults.

| # | Change | Why it should help here | Risk / what to watch |
|---|---|---|---|
| 0 | Check **Dual Core** is on (default) | Splits the CPU and GPU emulation threads | Only a verification, not a test |
| 1 | **GPU Texture Decoding: on** | Moves texture decoding from the CPU to the idle GPU; the guide says it helps weaker CPUs most | Incompatible with Arbitrary Mipmap Detection |
| 2 | **Texture Cache: Fast** | Less CPU time spent checking textures | Missing text or other graphical glitches |
| 3 | **Shader compilation: Hybrid Ubershaders** | Targets the fire-effect stutter; the GPU has headroom to spare for ubershaders | More GPU load. The guide's Vulkan warning is about NVIDIA, not Mali |
| 3b | **Compile Shaders Before Starting: on** (with Specialized) | Builds cached shaders at boot so explosions and fire don't hitch mid-game | Longer game boot time |
| 4 | **Skip EFB Access from CPU: on** | Big speed-up if the game reads back the screen | Breaks games that use screen reads for game logic; watch aiming and pickups |
| 5 | **Internal resolution 1×** (control test) | *Shouldn't* help if we really are CPU-bound; this checks our diagnosis | Lower image quality |
| 6 | **Emulated CPU Clock Override: 80–85%** | The guide's "most powerful tool" for weak devices: the game does less work per frame | Changes the game's own timing and can break games, so test last |

**Not touched** (per the guide): CPU Emulation Engine (already the fastest option), DSP (HLE is already fastest), Ignore Format Changes (negligible gain), Disable EFB VRAM Copies / Manual Texture Sampling (slower).

**TimeSplitters-specific note:** explosive action (e.g. plasma-grenade chain reactions) is the heaviest CPU load, so every run should include a few big explosions at similar points. Tests 2, 3b, 4 and 6 also match community tips for this game.

Metrics per run: game FPS (avg, 1% low), first-vs-last 3 min, X1/A78/GPU clock sustain, peak temperatures, plus notes on stutter, slow motion and visual glitches.

## After the Dolphin settings

1. Floppy2100 kernel tuning: CPU undervolting and thermal offsets (official Floppy guides). This is where PPSSPP's "same FPS, less heat" goal gets tested.
2. UN1CA's "Pause USB charging when gaming" (bypass charging) for docked play.
3. Clip-on cooler, as the final variable.
4. Before/after summary table.
