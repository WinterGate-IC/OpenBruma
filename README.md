# OpenBruma

OpenBruma is the official Linux OS of the **WinterGate Intelligence Collective**
(WinterGateIC) — a lightweight, full-desktop distribution built for lawful
OSINT, investigative work, defensive security research, and small servers.

It boots live from USB, installs to HDD/SSD with a **graphical installer
(Calamares)**, and ships a usable XFCE desktop out of the box.

## Base

OpenBruma is **Debian-based** (Debian 13 "trixie", x86_64), built with
`live-build`. It is **not** a from-scratch kernel or userspace build.

An earlier **Arch-based** prototype (built with `archiso`) is retained under
`archiso/` for reference. Arch does not support 32-bit x86 and does not ship
Calamares in its official repositories, which is why the current OS is built on
Debian.

## 32-bit support

The current OpenBruma x86_64 edition supports 64-bit hardware only. A future
**OpenBruma Legacy** edition (Debian i386 or Buildroot) is planned for older
32-bit machines.

## Features

- Debian 13 x86_64 base
- **Calamares graphical installer** with three modes:
  - **Guided** — erase the selected disk, minimal clicks
  - **Custom** — manual partitioning and advanced options
  - **USB / Virtual Machine** — guided install to a USB stick or a
    VirtualBox/VMware virtual disk
- XFCE desktop with a single neon top bar, LightDM autologin and a live
  (animated) default wallpaper
- Linux kernel 6.12 (Debian)
- NetworkManager with Wi-Fi applet and firmware for common wireless cards,
  Bluetooth (Blueman), PipeWire audio
- Firefox ESR (pinned next to the menu), Terminal and Files pinned on the bar
- Open-source Mesa/Xorg drivers and common redistributable firmware
- OSINT / investigative tooling: nmap, masscan, dnsrecon, gobuster, dirb,
  whois, dnsutils, traceroute, mtr, tcpdump, Wireshark/tshark, httrack,
  w3m/lynx, exiftool, mat2, binwalk, foremost, scalpel, SleuthKit,
  forensics-all, forensics-extra, john, hashcat, hydra
- **OSINT & Investigation menu**: Maigret, Holehe, Blackbird, Sherlock,
  h8mail, Social Analyzer, Toutatis, Instaloader, waymore, SploitScan
- **OPSEC menu**: AnonSurf (CLI + GUI), Tor Browser, Tor/Nyx, OnionShare,
  Proxychains, KeePassXC, BleachBit, MAT2, MAC Changer, secure-delete
- Python 3 with pip, venv and pipx (isolated `/opt/osint` toolbox)
- Partition/recovery: GParted, testdisk, gddrescue, smartmontools
- UEFI (with Secure Boot shim) and legacy BIOS boot
- VirtualBox/VMware/QEMU guest integration (tools, display resize, clipboard)
- OpenBruma / WinterGateIC branding

## Repository layout

```
OpenBruma/
  README.md
  LICENSE
  debian/           # live-build profile for the current Debian edition
    auto/config
    config/
      package-lists/
      includes.chroot/
      hooks/live/
    build.sh
  build/            # host helpers (VirtualBox VM creation, ISO download)
  archiso/          # legacy Arch prototype (reference)
  branding/         # logos, wallpapers
  installer/        # Arch/Calamares reference configs
  packages/         # package notes
  scripts/          # Arch build helpers (legacy)
  docs/             # documentation
  .github/workflows/# CI / reproducible build notes
  CHANGELOG.md
  SECURITY.md
```

## Build (Debian edition)

See `docs/DEBIAN.md`. Summary:

1. Prepare a Debian 13 environment with `live-build` and build tools.
2. Install build dependencies:
   `apt-get install live-build debootstrap squashfs-tools xorriso isolinux syslinux-common grub-efi-amd64-bin grub-pc-bin mtools dosfstools`
3. Copy this repo into the environment.
4. Run `REPO_DIR=/root/OpenBruma bash debian/build.sh`.
5. The ISO is written to `OUT_DIR` (default `/root/openbruma-debian-out`).

## Live credentials

- User: `openbruma` / `openbruma`
- Root: `root` / `openbruma`
- Passwordless `sudo` for the live user; `sudo` then works as usual.
- The live account, its sudoers entry and the autologin config are removed
  from the target system during installation (the root account stays).
- Extra accounts can be added after install with **Users and Groups**
  (`users-admin`), or from a root shell with `adduser`.
- Installers (application menu → System, plus desktop launchers):
  - **Install OpenBruma (Guided)** - Calamares with "erase disk" preselected.
  - **Install OpenBruma (Custom)** - Calamares with manual partitioning.
  - **Install OpenBruma (USB / Virtual Machine)** - guided install where the
    target device is picked explicitly (USB stick, VirtualBox/VMware disk).
  - From a terminal: `sudo /usr/local/bin/openbruma-install-guided`,
    `...-custom` or `...-removable`.

## Philosophy and boundaries

OpenBruma is built for lawful, documented, proportional investigative work.
It is not a hacking or vigilante toolkit. See `SECURITY.md` and the
WinterGateIC public notice for the collective's operating boundaries.

## License

Project scripts/configs/branding: MIT (see `LICENSE`). Bundled Debian packages
retain their own licenses; see `docs/LICENSES.md`. The WinterGateIC logo is a
copyrighted mark of WinterGate IC and is used here for official OpenBruma
builds only.
