# Changelog

## [0.2.0] - 2026-11-23

### Added
- **Debian 13 (trixie) edition** built with `live-build` — now the primary
  OpenBruma OS.
- **Two Calamares graphical installers:**
  - **Guided** — auto-selects "erase disk", minimal clicks.
  - **Custom** — manual partitioning and advanced options.
- Fully branded Calamares: WinterGateIC logo, dark blue stylesheet, custom
  QML slideshow, OpenBruma strings.
- Branded Plymouth boot splash, LightDM greeter theme, `/etc/issue`,
  `/etc/motd`, XFCE wallpaper, and desktop installer icons.
- OSINT / investigative toolchain: nmap, masscan, dnsrecon, gobuster, dirb,
  whois, dnsutils, traceroute, mtr, tcpdump, Wireshark/tshark, httrack,
  w3m, lynx, exiftool, mat2, binwalk, foremost, scalpel, SleuthKit,
  forensics-all, forensics-extra, john, hashcat, hydra.
- Firefox ESR, Thunderbird, LibreOffice, GParted, testdisk, gddrescue.
- PipeWire audio, NetworkManager, common redistributable firmware.
- UEFI (shim Secure Boot) + BIOS boot.
- WinterGateIC/OpenBruma branding, wallpaper, and installer logo.

### Changed
- Project is now clearly presented as Debian-based.
- Arch (`archiso`) profile retained as a legacy prototype.

### Known limitations
- x86_64 only; no 32-bit support in this edition.
- Visual desktop/audio checks still need a manual pass on real hardware.

## [0.1.0] - 2026-11-23

### Added
- Initial Arch-based OpenBruma repository and archiso profile.
- XFCE, linux-lts, PipeWire, NetworkManager, UEFI + BIOS boot.
- archinstall fallback (Calamares unavailable in Arch official repos).
