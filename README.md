# s21u-emu

Turning a retired Samsung Galaxy S21 Ultra (Exynos 2100, Mali-G78) into a dedicated emulation handheld, and using it as a vehicle to learn Android systems work, native builds and app development.

The goal isn't to install some apps. It's to **measure, build from source and ship software**, and to document every decision along the way.

## Hardware

| Item | Value |
|---|---|
| Model | SM-G998B/DS (codename `p3s`) |
| SoC | Exynos 2100: 1x Cortex-X1, 3x Cortex-A78, 4x Cortex-A55 |
| GPU | Mali-G78 MP14 (no Adreno/Turnip drivers) |
| Host | Windows + WSL2 (Odin on Windows, builds in WSL2) |

## Emulators installed

| System | Emulator | Version | Source | Open source | Benchmarked |
|---|---|---|---|---|---|
| PSP | [PPSSPP](https://www.ppsspp.org) | 1.20.4 | ppsspp.org | ✅ GPL-2.0 | ✅ baseline |
| GameCube / Wii | [Dolphin](https://dolphin-emu.org) | 2609 | dolphin-emu.org | ✅ GPL-2.0+ | 🔄 in progress |
| PS1 | [DuckStation](https://github.com/stenzek/duckstation) | 0.1-8969 | Google Play (only official Android source) | ❌ Android app not public | ⏳ |
| PS2 | [ARMSX2](https://github.com/ARMSX2/ARMSX2) (PCSX2 ARM64 port) | 2.7.1 nightly | GitHub releases | ✅ GPL-3.0 | ⏳ |
| Nintendo DS | [melonDS Android](https://github.com/rafaelvcaetano/melonDS-android) | 2.0.1 | GitHub releases | ✅ GPL-3.0 | ⏳ |
| Original Xbox | X1 BOX | 1.2.5 | third-party | ❌ closed | ✖ excluded (not reproducible) |

Switch (Eden) is on hold until keys, firmware and games are dumped from my own console.

## Roadmap

| Phase | What | Status |
|---|---|---|
| 0 | Pre-flight: bootloader compatibility check | ✅ Done ([write-up](docs/phase-0-preflight.md)) |
| 1 | Unlock bootloader, flash [UN1CA](https://github.com/salvogiangri/UN1CA) (One UI 8), [Floppy2100](https://github.com/FlopKernel-Series/flop_exynos2100_kernel) kernel + KernelSU Next root | ✅ Done ([write-up](docs/phase-1-unlock-and-flash.md)) |
| 2 | Performance tuning for *sustained* FPS, with before/after benchmarks | 🔄 Baselines in progress ([plan](docs/phase-2-tuning.md) · [log](benchmarks/log.md)) |
| 3 | Android SDK/NDK toolchain; build RetroArch and Dolphin from source | ⏳ |
| 4 | Custom Kotlin + Jetpack Compose emulation launcher (separate repo) | ⏳ |
| 5 | (Stretch) Mali GPU driver research | ⏳ |

## Repo layout

```
docs/         Phase write-ups: decisions, steps, problems hit and fixes
benchmarks/   FPS / thermal logs and before/after tables
tools/        perflog.sh (on-device FPS/clock/thermal logger), summarize.py, plot_run.py (SVG charts)
build-notes/  Per-emulator build instructions and toolchain versions
```

## Why these choices

- **UN1CA over AOSP/LineageOS:** there's no stable AOSP build for `p3s`, and AOSP on Exynos tends to have camera/modem/GPU driver issues. UN1CA is a debloated One UI 8 build that keeps Samsung's vendor drivers and is actively maintained.
- **Sustained, not peak performance:** phones throttle. The tuning target is flat FPS over a 15-minute session, not a short benchmark spike.
- **Build from source:** understanding and reproducing the toolchain is the point, and it enables targeted compiler flags for the Exynos cores.

## Legal

Emulators are legal. This repo contains **no** games, BIOS files, firmware, keys or ROM images. All game data used for testing is dumped from hardware I own.
