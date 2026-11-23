#!/usr/bin/env bash
# Run inside the OpenBruma build VM (Arch Linux).
# Installs build dependencies.
set -e
sudo pacman -Syu --noconfirm
sudo pacman -S --needed --noconfirm \
  git base-devel archiso \
  nano vim curl wget zstd squashfs-tools xorriso mtools dosfstools \
  edk2-ovmf ovmf \
  python python-pip
echo "Build dependencies installed."
