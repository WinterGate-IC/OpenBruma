# OpenBruma

OpenBruma is a lightweight, full-desktop Linux distribution aimed at older
64-bit machines and small servers. It boots live from USB, installs to
HDD/SSD, and ships a usable XFCE desktop out of the box.

## Base

OpenBruma is **Arch-based**. It is built with `archiso` on top of the Arch
Linux package set and repositories. It is **not** a from-scratch kernel or
userspace build, and it does not ship its own package manager or init
system beyond what Arch provides (pacman + systemd).

## 32-bit support

The Arch edition of OpenBruma supports **x86_64 only**. Arch Linux does not
support 32-bit x86, and OpenBruma does not pretend otherwise. If 32-bit
legacy hardware must be supported, plan a separate **OpenBruma Legacy**
edition based on Debian i386 or Buildroot. That edition is out of scope for
this repository.

## Features (v1)

- Arch Linux x86_64 base
- XFCE desktop (low resource use)
- `linux-lts` kernel by default, with `linux` (standard) available
- Calamares installer when achievable, otherwise `archinstall` + docs
- NetworkManager, PipeWire, common firmware, Mesa, Xorg, fonts
- Browser, terminal, archive tools, partition tools, recovery tools
- OpenBruma branding (wallpaper, GRUB/systemd-boot theme, hostname)
- UEFI and legacy BIOS boot

## Repository layout

```
OpenBruma/
  README.md
  LICENSE
  build/            # build orchestration (host + VM)
  archiso/          # archiso profile (profiledef.sh, packages, airootfs)
  branding/         # logos, wallpapers, themes
  installer/        # Calamares / archinstall configuration
  packages/         # package lists and package notes
  scripts/          # helper scripts (run inside build VM)
  docs/             # documentation
  .github/workflows/# CI / reproducible build notes
  CHANGELOG.md
  SECURITY.md
```

## Quick start (build)

See `docs/BUILD.md`. Summary:

1. Install Arch Linux in a VirtualBox VM (build VM).
2. Inside the VM, install build deps: `git base-devel archiso ...`.
3. Clone/copy this repo into the VM.
4. Run `scripts/build-iso.sh`.
5. Test the resulting ISO in a second VM.

## Safety

- Only disposable VirtualBox VMs are used for building/testing.
- Never run `dd` against a Windows physical disk.
- No secrets, keys, or private data are committed.
- No proprietary firmware/drivers unless redistribution is clearly allowed.

## License

See `LICENSE`. OpenBruma aggregates packages under their own licenses
(GPL, MIT, BSD, etc.). License obligations are documented in
`docs/LICENSES.md`.
