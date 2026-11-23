# Packages

This directory documents package selection for OpenBruma.

- `../archiso/packages.x86_64` is the authoritative build-time package list.
- `packages-minimal.md` describes a low-RAM profile.

## Low-RAM profile (documented)

For machines with <= 2 GB RAM, after install remove heavy optional packages:
- firefox -> use a lighter browser (e.g. midori) or text browser
- disable compositor in XFCE
- use `linux-lts` (already default)
- disable unnecessary services: bluetooth, cups if not needed
- use zram swap

See docs/LOWRAM.md.
