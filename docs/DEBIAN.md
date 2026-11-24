# Building OpenBruma (Debian edition)

## Requirements

- Debian 13 (trixie) amd64 environment (bare metal, VM, or WSL Debian).
- Root access.
- ~10 GB free disk, ~4 GB RAM recommended.
- Internet access to `deb.debian.org`.

## Install build tools

```sh
apt-get update
apt-get install -y live-build debootstrap squashfs-tools xorriso \
  isolinux syslinux-common syslinux-efi grub-efi-amd64-bin grub-pc-bin \
  mtools dosfstools parted gdisk rsync
```

Enable `contrib`, `non-free`, and `non-free-firmware` in apt sources for
firmware and Calamares settings packages.

## Build

```sh
cp -a /path/to/OpenBruma /root/OpenBruma
REPO_DIR=/root/OpenBruma \
BUILD_DIR=/root/openbruma-debian-build \
OUT_DIR=/root/openbruma-debian-out \
bash /root/OpenBruma/debian/build.sh
```

The script runs `lb clean --purge`, `lb build`, copies the resulting
`openbruma-amd64.hybrid.iso` to `OUT_DIR`, and prints its SHA-256.

## Configuration

- `debian/auto/config` — `lb config` options (distribution, bootloaders,
  live boot append, ISO label).
- `debian/config/package-lists/openbruma.list.chroot` — package list.
- `debian/config/includes.chroot/` — branding, Calamares branding, skel.
- `debian/config/hooks/live/0050-openbruma-live.hook.chroot` — live user,
  autologin, hostname, sudo, welcome, Calamares branding, installer wrappers,
  installed-system cleanup.

## Installers

Two launchers ship on the desktop and in the menu:

- `openbruma-install-guided` writes an `eraseDisk` partition profile to
  `/etc/calamares/modules/partition.conf` and starts Calamares.
- `openbruma-install-custom` writes a `manual` profile instead.

Both wrappers run through `pkexec`; a polkit rule allows the live user without
an extra password prompt. Running Calamares with `-c` is avoided because
Calamares 3.3 requires a full application-data directory (`qml/`) in that case.

## Boot modes

- BIOS: syslinux/isolinux via hybrid MBR.
- UEFI: GRUB EFI with Debian shim (Secure Boot support).

## Notes

- The build is performed on Debian; do not use Ubuntu for the final image.
- The ISO is a hybrid image and can be written to USB with `dd` (on Linux)
  or booted directly in a VM.
