# Testing

## Live boot
- Boot ISO in test VM (UEFI and BIOS).
- Verify desktop (XFCE) loads, network connects, audio works.

## Install
- Run Calamares or archinstall.
- Install to virtual disk.
- Reboot without ISO; verify installed system boots.

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
