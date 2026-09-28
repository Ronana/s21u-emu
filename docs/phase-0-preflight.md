# Phase 0: Pre-flight bootloader check

**Date:** 2026-09-28

## Why this matters

Samsung firmware carries a **bootloader binary** (anti-rollback) number. A phone refuses firmware with a lower binary than it currently has, and trying to force it risks a brick. Before unlocking or flashing anything, I needed to know:

1. What binary the phone is on now.
2. What the custom ROM (UN1CA) expects.

## Reading the binary

The binary is the **5th character from the end** of the firmware build string (`1`-`9`, then `A` = 10, `B` = 11, …).

| | Build | Android | Binary |
|---|---|---|---|
| Phone (stock) | `G998BXXSBGXDH` | 14 (`UP1A`) | **B = 11** |
| Latest stock A15 | `G998BXXSJHZC2` | 15 | **J = 19** |

## What UN1CA requires

The official XDA thread for the G998B states that an **Android 15 bootloader is required** to avoid bugs. The UN1CA 3.0.7 changelog moved to `G998BXXSJHZC2`.

## Decision

The phone is *behind* the requirement. Moving up (11 → 19) is safe, and moving down is not. So before touching the bootloader:

1. Update to Android 15 using Samsung's **official OTA** (no Odin, no Knox trip, no wipe).
2. Re-check the build number.
3. Fallback if OTA doesn't reach A15: flash official Samsung firmware via Odin.

Note: this is one-way. Once on binary 19, the phone can never return to Android 14 firmware. That's acceptable for a dedicated device.

## Result

Official OTA completed on 2026-09-28. No Odin needed.

| | Build |
|---|---|
| Before | `UP1A.231005.007.G998BXXSBGXDH` (Android 14, binary B = 11) |
| After | `AP3A.240905.015.A2.G998BXXSJHZC2` (Android 15, binary **J = 19**) |

✅ **Pre-flight passed.** The phone matches UN1CA's bootloader requirement exactly, so Phase 1 can begin.
