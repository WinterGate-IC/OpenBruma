# Build guide

## Overview
OpenBruma is built with `mkarchiso` inside an Arch Linux build VM.

## Steps
1. Download Arch ISO: `.\build\download-arch-iso.ps1`
2. Create build VM: `.\build\vbox-create-build-vm.ps1`
3. Boot build VM from Arch ISO, install Arch (or run archinstall).
4. Inside build VM:
   ```
   sudo pacman -S --needed git base-devel archiso ...
   git clone <repo> ~/OpenBruma   # or copy from shared folder
   cd ~/OpenBruma
   bash scripts/setup-build-vm.sh
   bash scripts/build-iso.sh
   ```
5. Copy resulting ISO from VM to host via shared folder `/mnt/openbruma-out`.
6. Test in test VM.

## Reproducibility
See docs/REPRODUCIBILITY.md.
