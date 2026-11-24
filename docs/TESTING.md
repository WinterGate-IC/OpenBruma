# Testing

## Live boot
- Boot ISO in test VM (UEFI and BIOS).
- Verify desktop (XFCE) loads, network connects, audio works.

## Install
- Run the guided installer from the desktop or the application menu
  (or `sudo /usr/local/bin/openbruma-install-guided`).
- Install to a virtual disk.
- Reboot without ISO; verify the installed system boots to the LightDM
  greeter (autologin is removed on purpose) and that the new user can log in.
- Confirm the live account was removed: `id openbruma` should fail and
  `/etc/sudoers.d/openbruma` should not exist.

## Live user and security
- The live session logs in automatically as `openbruma` (password
  `openbruma`, passwordless sudo) for installer convenience.
- Calamares runs `shellprocess@livecleanup` so none of that survives into an
  installed system.

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
