# Testing

## Live boot
- Boot ISO in test VM (UEFI and BIOS).
- Verify desktop (XFCE) loads, network connects, audio works.
- Live wallpaper plays (Aurora Drift) and stays dim/behind the panel.
- Top bar: OpenBruma logo menu, pinned Firefox/Terminal/Files, dividers,
  tray (network/Bluetooth/audio/power), clock, session menu.
- Open a window and confirm the neon glow (picom) is visible.
- Switch presets in *OpenBruma Themes* and confirm wallpaper/glow change.
- Check menus: OSINT & Investigation, OPSEC, WIC Apps (with WIC shield icons).
- Launch a few tools (`maigret --help`, `anonsurf --help`, Tor Browser).
- Ctrl+Alt+T opens a terminal.

## Install
- Run each installer mode: Guided, Custom, USB / Virtual Machine.
- Install to a virtual disk.
- Reboot without ISO; verify the installed system boots to the LightDM
  greeter (autologin is removed on purpose) and that the new user can log in.
- Confirm the live account was removed: `id openbruma` should fail and
  `/etc/sudoers.d/openbruma` should not exist.
- Confirm root login works with `root` / `openbruma`.

## Live user and security
- The live session logs in automatically as `openbruma` (password
  `openbruma`, passwordless sudo) for installer convenience.
- Calamares runs `shellprocess@livecleanup` so none of that survives into an
  installed system, and `openbruma` is a forbidden install username.

## Low-RAM profile
- Test with 1-2 GB RAM VM; document results.

## Checklist
- [ ] UEFI live boot
- [ ] BIOS live boot
- [ ] UEFI install + reboot
- [ ] BIOS install + reboot
- [ ] Network (DHCP)
- [ ] Audio (PipeWire)
- [ ] Low-RAM profile
