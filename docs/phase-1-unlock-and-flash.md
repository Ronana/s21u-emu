# Phase 1: Unlock bootloader and flash UN1CA

## Step 1: Pre-unlock checks (2026-09-28)

Download Mode status (Vol Up + Vol Down while plugging in USB, then a short Vol Up press):

| Field | Value | Meaning |
|---|---|---|
| OEM LOCK | ON | Bootloader locked (expected before unlock) |
| KG STATE | Completed | No Knox Guard restriction; `Prenormal`/`Checking` would block custom binaries |
| FRP LOCK | (not shown) | Normal on newer bootloaders |
| CURRENT BINARY | Samsung Official | Stock firmware |

Developer options → **OEM unlocking** was ON after the Android 15 OTA.

## Step 2: Bootloader unlock (2026-09-28)

1. Power off, hold **Vol Up + Vol Down**, plug in USB → Warning screen.
2. **Long-press Vol Up** → "Unlock bootloader?" → **Vol Up** to confirm.
3. The device factory-reset itself and rebooted.

**Result:** ✅ Developer options → OEM unlocking is greyed out with *"Bootloader is already unlocked"*.

Consequences (accepted): data wiped; Knox e-fuse tripped permanently (Samsung Pay/Wallet, Secure Folder no longer work); a "bootloader unlocked" warning shows on every boot.

**Gotcha:** after the status check, the phone stays on *"Downloading… Do not turn off target"*. That's just Download Mode idling while it waits for a PC tool. Exit with **Vol Down + Side key** (~7–10 s).

## Step 3: Custom recovery

_Next: select the recovery build recommended for UN1CA on `p3s` (Android 15 bootloader) and flash it with Odin._
