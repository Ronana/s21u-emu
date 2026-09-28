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

## Step 6: Post-install checks

The UN1CA build shows in *About phone*; Wi-Fi, mobile data, calls, camera, Bluetooth audio and fingerprint all work. RAM confirmed as **12 GB**.

## Step 7: Choosing a kernel: VoidKernel → Floppy2100

The original plan was **VoidKernel**. Checking its [GitHub releases](https://github.com/any444v/android_kernel_samsung_universal2100/releases) showed the last release and commit were in **June 2025**, and it was only tested on One UI 7.

Switched to **[Floppy2100](https://github.com/FlopKernel-Series/flop_exynos2100_kernel)**:

- Actively maintained (commits in the last week, v1.1.2 released 2026-05-30)
- Supports Android 12–16 on One UI and AOSP; v1.1.2 fixes a UN1CA-specific bug, so it's used on this ROM
- Ships KernelSU Next + SuSFS builds, with SHA-256 digests on every asset
- Has official undervolting and thermal-offset guides, which matter for Phase 2's sustained-FPS goal

Requirement: **RAM Plus must be disabled**.

Before flashing, I read the zip's `anykernel.sh`: it supports `p3s` on Android 11–16 and writes only **`boot`** (kernel swap) and **`vendor_boot`**.

## Step 8: Backup and flash (2026-09-28)

1. Disabled RAM Plus.
2. In TWRP, backed up `boot`, `vendor_boot` and `dtbo` to the PC with `adb shell dd … of=/tmp/*.img` + `adb pull`. I checked the image headers (`ANDROID!`, `VNDRBOOT`, DTBO magic) and sizes (64/64/8 MB). TWRP can't decrypt internal storage, so pulling the images to the PC was the way to back them up.
3. TWRP → Advanced → **ADB Sideload** → `adb sideload Floppy_v1.1.2-KSUNext-SUSFS-exynos2100-20260530-1437.zip` (SHA-256 verified).
4. Rebooted into the system successfully.

## Step 9: Root and verification

- Installed **KernelSU Next v3.2.0** (the manager version Floppy v1.1.2 pairs with; SHA-256 verified) via `adb install`.
- Granted root to the Shell in the Superuser tab.

```
$ adb shell uname -r
5.4.302-Floppy-v1.1.2-KN-release
$ adb shell su -c id
uid=0(root) gid=0(root) groups=0(root) context=u:r:ksu:s0
```

- Developer options → **OEM unlocking** is still greyed out with *"Bootloader is already unlocked"*.

✅ **Phase 1 complete.**

## Final state

| Component | Version |
|---|---|
| Bootloader / modem | `G998BXXSJHZC2` / `G998BXXSJHZA6` (unlocked) |
| Recovery | TWRP 3.7.1_12-0 (xfwdrev) |
| ROM | UN1CA 3.2.0 (One UI 8, Android 16) |
| Kernel | Floppy2100 v1.1.2 (Linux 5.4.302) |
| Root | KernelSU Next v3.2.0 + SuSFS |
