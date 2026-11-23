# VM setup

## Build VM
- OS: Arch Linux x86_64
- vCPU: 4
- RAM: 8 GB (reduce to 2 vCPU / 6 GB if host constrained)
- Disk: 60 GB VDI
- Firmware: EFI (UEFI)
- Network: NAT
- Shared folders: OpenBrumaRepo -> /mnt/openbruma-repo, OpenBrumaOut -> /mnt/openbruma-out

## Test VM
- OS: Arch/Debian (any)
- vCPU: 2
- RAM: 4 GB
- Disk: 20 GB VDI
- Firmware: EFI (one VM) and BIOS (second VM)

## Host safety
- VMs are disposable. Delete after use.
- Never write to host physical disks.
