# Licenses

OpenBruma aggregates third-party software. Each package retains its own
license.

## Project code
- OpenBruma's own scripts, configs, branding: MIT (see LICENSE).

## Base system
- Arch Linux packages: various (GPL, MIT, BSD, Apache, etc.)
- Kernel: GPL-2.0
- systemd: LGPL-2.1+

## Firmware
- `linux-firmware`: contains firmware blobs with varied redistribution
  terms. Review before redistributing modified images. Only include blobs
  whose terms permit redistribution.

## Desktop
- XFCE: GPL/LGPL
- GTK: LGPL

## Installer
- Calamares: GPL-3.0
- archinstall: GPL-3.0

## No proprietary drivers
- Proprietary NVIDIA/AMD drivers are not included by default. Open-source
  Mesa drivers are used.

## Compliance
- Source for GPL components is available via Arch repositories and upstream
  projects. OpenBruma provides build scripts and package lists to reproduce.
