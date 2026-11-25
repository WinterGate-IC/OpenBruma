# Changelog

## [0.3.0] - 2026-11-24

### Added
- **OpenBruma theme collection** generated with WinterGateIC's UmbraForge:
  8 branded 4K wallpapers (Neo-Noir, Electric Blue, Violet Forge, Ember,
  Cyber-Lime, Crimson Gate, Ghost Protocol, Aurora), matching login and GRUB art.
- **Three live (animated) wallpapers** — Aurora Drift, Data Rain and Ember
  Pulse — rendered with the official OpenBruma logo and dimmed so the desktop
  stays readable. They are opt-in (Application menu → System); the default is
  the static neon wallpaper, which is the most reliable option on virtual
  machines and older GPUs.
- **Neon desktop**: picom compositor with a per-theme window glow, gradient
  panel with accent line and active-window underline, and five switchable
  presets (Neo-Noir, Synthwave, Crimson, Cyber-Lime, Ghost) in *OpenBruma
  Themes*.
- **Official brand artwork**: the OpenBruma logo is the menu button and About
  icon; the WIC shield is used for the WIC Apps category and every WIC app
  entry.
- **Custom OpenBruma application menu** replacing Whisker: fully themed GTK
  launcher with Favorites, OSINT & Investigation, OPSEC, WIC Apps and standard
  categories, live search, keyboard navigation and a toggle-on-second-click
  behaviour.
- **Three installer modes**: Guided (erase disk), Custom (manual) and a new
  USB / Virtual Machine guided mode with explicit target selection.
- **OSINT & Investigation menu**: Maigret, Holehe, Blackbird, Sherlock, h8mail,
  Social Analyzer, Toutatis, Instaloader, waymore and SploitScan, installed in
  an isolated `/opt/osint` Python environment with CLI wrappers.
- **OPSEC menu**: AnonSurf (CLI and Qt GUI, Parrot packages), bundled Tor
  Browser, Tor/Nyx, OnionShare, Proxychains, KeePassXC, BleachBit, MAT2,
  MAC Changer and secure-delete.
- **Python toolchain**: python3, pip, venv and pipx.
- **Network**: NetworkManager manages all interfaces, Wi-Fi powersave tuned,
  radios unblocked at login, Blueman applet, firmware for Intel/Realtek/
  Atheros/Broadcom.
- **Virtual machine support**: open-vm-tools, spice-vdagent and qemu-guest-agent.
- **Root account** `root` / `openbruma`; live account lockout now also removes
  its polkit rule.
- **Extra account creation** through Users and Groups after install.

### Changed
- Top bar redesigned Kali-style: branded menu, pinned Firefox/Terminal/Files,
  divider lines, icon-only window list, tray, clock and session menu.
- Desktop icons are hidden by default so the live wallpaper is unobstructed;
  launchers live in the menu and on the top bar.
- Qt applications render dark (`QT_STYLE_OVERRIDE=Adwaita-Dark`).

### Fixed
- Removed Debian logo/title from the boot splash.
- Fixed wallpaper application across virtual monitor names.
- Fixed missing XFCE power-manager plugin.
- Fixed missing installer entries on the live desktop.
- Fixed the guided installer failing to start (missing qml application data).
- Fixed the Arch-style bootloader paths that would produce unbootable installs.
- **Rendering stability:** the desktop runs uncomposited by default (the most
  reliable choice on VirtualBox/VMware without 3D acceleration); picom is only
  started by the explicit *Enable Neon Window Glow* toggle. The packaged picom
  autostart, which competed with the window manager and caused black/flickering
  repaints, is removed.
- **Installer branding is now enforced at launch** instead of at image-build
  time. The Debian Calamares packaging replaces `/etc/calamares` during the
  build, which made the installer fall back to stock Debian branding (and the
  unstyled black content panel). The three launchers now apply the OpenBruma
  branding, module configs and live-account cleanup immediately before opening.
- **Calamares stylesheet trimmed** so a broad `QWidget` background can no
  longer paint over embedded pages/pickers.
- **Faster boot:** boot menus auto-select after 3 s (was 5 s) and services that
  are irrelevant on this desktop (ModemManager, CUPS, Avahi, saned,
  speech-dispatcher, colord) are masked.
- **Tray icons:** added the XFCE indicator plugin so NetworkManager and Blueman
  (StatusNotifier) icons appear next to the legacy tray.
- Terminal opens with a branded ASCII/OpenBruma + WIC banner and live system
  metrics; prompt glyph fixed.
- Removed duplicate NetworkManager/Blueman autostart entries.
- Pinned apps on the bar are now three separate launchers (XFCE collapsed a
  multi-item launcher into a dropdown).
- Safe binary-asset handling in the build tooling (no CRLF corruption of PNG/TTF).

## [0.2.0] - 2026-11-23
