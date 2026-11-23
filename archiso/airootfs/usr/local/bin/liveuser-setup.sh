#!/bin/bash
# Live user setup for OpenBruma
set -e
useradd -m -G wheel,audio,video,optical,storage -s /bin/bash live 2>/dev/null || true
echo "live:live" | chpasswd
echo "root:root" | chpasswd
# autologin via lightdm
mkdir -p /etc/lightdm/lightdm.conf.d
cat > /etc/lightdm/lightdm.conf.d/50-openbruma-autologin.conf <<'EOF'
[Seat:*]
autologin-user=live
autologin-user-timeout=0
user-session=xfce
EOF
# enable services
systemctl enable NetworkManager
systemctl enable lightdm
systemctl enable pipewire pipewire-pulse wireplumber 2>/dev/null || true
