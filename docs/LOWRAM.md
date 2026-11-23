# Low-RAM profile

OpenBruma targets older 64-bit machines. For systems with limited RAM:

## Minimum tested
- 1 GB RAM (live boot may be slow; installer needs ~2 GB free disk)
- 2 GB RAM recommended for comfortable XFCE desktop

## Tuning steps
1. Use the `linux-lts` kernel (default).
2. Disable XFCE compositor: Settings -> Window Manager Tweaks -> Compositor -> off.
3. Enable zram: `systemctl enable --now systemd-zram-generator` (install `zram-generator`).
4. Remove unneeded packages: `pacman -Rns firefox` (replace with midori/links if desired).
5. Disable unused services: bluetooth, cups, avahi-daemon.
6. Use a lightweight file manager (thunar is already light).

## Documented test profile
- VM: 1 vCPU, 1024 MB RAM, 20 GB disk, UEFI.
- Expected: live boot reaches desktop within ~90s; installer completes.
