# Changelog

## [0.2.0] - 2026-11-23

### Added
- **Debian 13 (trixie) edition** built with `live-build` — now the primary
  OpenBruma OS.
- **Calamares graphical installer** with OpenBruma branding (install to disk
  from the live desktop).
- XFCE desktop with LightDM autologin (live user `openbruma`).
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
