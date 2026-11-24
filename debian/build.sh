#!/bin/bash
# Build OpenBruma Debian edition ISO with live-build.
# Run inside a Debian chroot (bookworm) with live-build installed.
set -euo pipefail

REPO_DIR="${REPO_DIR:-/root/OpenBruma}"
BUILD_DIR="${BUILD_DIR:-/root/openbruma-debian-build}"
OUT_DIR="${OUT_DIR:-/root/openbruma-debian-out}"

if [ ! -d "$REPO_DIR/debian" ]; then
  echo "debian/ profile not found under $REPO_DIR" >&2
  exit 1
fi

mkdir -p "$BUILD_DIR" "$OUT_DIR"
cd "$BUILD_DIR"

# Copy live-build config
rm -rf config auto
cp -a "$REPO_DIR/debian/auto" .
cp -a "$REPO_DIR/debian/config" .

# Sync branding assets into includes.
# The wallpaper must be the current 4K generation, never the legacy gradient.
WALL_SRC="$REPO_DIR/branding/wallpapers/openbruma-neo-noir.png"
[ -f "$WALL_SRC" ] || WALL_SRC="$REPO_DIR/branding/openbruma-wallpaper.png"
if [ -f "$WALL_SRC" ]; then
  cp "$WALL_SRC" config/includes.chroot/usr/share/backgrounds/openbruma-wallpaper.png
  cp "$WALL_SRC" config/includes.chroot/usr/share/backgrounds/openbruma/openbruma-neo-noir.png 2>/dev/null || true
fi
cp "$REPO_DIR/branding/openbruma-logo.svg" config/includes.chroot/usr/share/pixmaps/ 2>/dev/null || true

# Run live-build
lb clean --purge || true
lb build 2>&1 | tee /tmp/openbruma-debian-build.log

# Collect ISO
ISO=$(ls -1 *.iso 2>/dev/null | head -1 || true)
if [ -z "$ISO" ]; then
  echo "No ISO produced; see /tmp/openbruma-debian-build.log" >&2
  exit 1
fi
cp "$ISO" "$OUT_DIR/"
cd "$OUT_DIR"
ls -lh
sha256sum *.iso
echo "DONE: $OUT_DIR/$ISO"
