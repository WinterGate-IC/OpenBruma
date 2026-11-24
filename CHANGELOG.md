# Changelog

## [0.3.0] - 2026-11-24

### Added
- **OpenBruma theme collection** generated with WinterGateIC's UmbraForge:
  8 branded 4K wallpapers (Neo-Noir, Electric Blue, Violet Forge, Ember,
  Cyber-Lime, Crimson Gate, Ghost Protocol, Aurora), matching login and GRUB art.
- **Custom GRUB theme** (Orbitron / Share Tech Mono, neo-noir palette) and
  branded BIOS/UEFI splash images.
- **Custom terminal**: XFCE terminal profile (Share Tech Mono, WIC palette),
  branded prompt, fastfetch banner and OSINT aliases.
- **WIC Apps menu**: dedicated application-menu category for UmbraForge,
  VoiceForge, Ominis OSINT, Coeus OSINT ToolBox and the WIC portal.
- **Dark desktop by default**: Arc-Dark GTK, Papirus-Dark icons, dark XFWM.
- Single top panel (bottom dock removed), Whisker menu, systray/NetworkManager,
  PulseAudio applet, clock and session controls.
- **Performance tuning**: zram swap, earlyoom with installer-safe rules,
  tuned openbruma profile, preload, irqbalance, sysctl/limits for large
  browser/tool workloads.
- OpenBruma-branded boot menu labels and 5-second auto-boot.

### Fixed
- Removed Debian logo/title from the boot splash.
- Fixed wallpaper application across virtual monitor names.
- Fixed missing XFCE power-manager plugin.
- Safe binary-asset handling in the build tooling (no CRLF corruption of PNG/TTF).

## [0.2.0] - 2026-11-23
