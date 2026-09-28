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

## Step 3: Choosing and verifying the files

| File | Source | Verification |
|---|---|---|
| `twrp-3.7.1_12-0-p3s.tar` | Linked from UN1CA XDA Post #2 → GitHub release by **xfwdrev** (UN1CA's p3s maintainer) | SHA-256 matches GitHub asset digest `f4007273…445e` |
| `vbmeta_disabler.tar` | XDA "TWRP Android 15 p3s" thread | Inspected: single 4 KB `vbmeta.img`, AVB header, flags = 2 (verification disabled), no descriptors |
| `UN1CA_3.2.0-84de569d_20260912_p3s-sign.zip` | Official UN1CA 3.2.0 release (gofile) | MD5 + SHA1 match the official GitHub release notes |
| Odin 3.14.4 / ADB 37.0.1 | odindownload.com repack / Google | Contents inspected; ADB is official |

What I learned from reading UN1CA's p3s installer (`target/p3s/installer/*.edify`):

- It **aborts on afaneh92's TWRP builds** (`E3000`), so the maintainer's recovery build is required.
- It **aborts unless the bootloader is `G998BXXSJHZC2`** (`E3003`).
- When the device is already on `G998BXXSJHZC2`, it **skips all bootloader/modem/vbmeta writes**. That's why a vbmeta disabler has to be flashed separately alongside the recovery.
- A shortcut: the maintainer ships an Odin-flashable TWRP 3.7.1 `.tar`, so the XDA thread's two-stage TWRP 3.7.0 → 3.7.1 route isn't needed.

## Step 4: Flash TWRP with Odin (2026-09-28)

- Odin options: **Auto Reboot OFF**
- **AP:** `twrp-3.7.1_12-0-p3s.tar` → recovery partition
- **USERDATA:** `vbmeta_disabler.tar` → vbmeta partition
- Result: **PASS**. Then **Vol Down + Side** until black → immediately **Vol Up + Side** → booted straight into TWRP (so stock Android never got the chance to restore stock recovery).

## Step 5: Flash UN1CA 3.2.0 (2026-09-28)

1. TWRP: **Format Data** → reboot to recovery.
2. From Windows: `adb push UN1CA_…_p3s-sign.zip /sdcard/`
3. TWRP: **Install** → zip → swipe.
4. **Format Data** again (first install, per UN1CA's guide) → **Reboot → System**.

**Result:** ✅ Booted into the One UI 8 setup screen.

**Problem hit:** `adb push` of the 6.3 GB zip dropped partway with `no response: Broken pipe` and the device vanished from `adb devices`. Things tried: disabling MTP in TWRP, turning off TWRP's screen timeout, reconnecting on a direct PC port, `adb kill-server`, and deleting the partial file before retrying. A likely cause to check next time: if `/data` isn't mounted after a format, `/sdcard` lives in RAM and a large push fills it. `adb sideload` avoids needing storage at all.

## Next

Root (Magisk / KernelSU) → VoidKernel → verify (`uname -r`, OEM unlock still on).
