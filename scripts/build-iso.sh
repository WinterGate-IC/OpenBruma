#!/usr/bin/env bash
# Build OpenBruma ISO with mkarchiso.
# Run inside the build VM from the repo root.
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/OpenBruma}"
PROFILE_DIR="$REPO_DIR/archiso"
OUT_DIR="${OUT_DIR:-$HOME/openbruma-out}"
WORK_DIR="${WORK_DIR:-/tmp/openbruma-work}"

if [ ! -d "$PROFILE_DIR" ]; then
  echo "Profile dir not found: $PROFILE_DIR" >&2
  exit 1
fi

mkdir -p "$OUT_DIR" "$WORK_DIR"
rm -rf "$WORK_DIR"/*

# Sync installer configs into airootfs
mkdir -p "$PROFILE_DIR/airootfs/usr/share/openbruma/calamares"
cp -r "$REPO_DIR/installer/calamares/"* "$PROFILE_DIR/airootfs/usr/share/openbruma/calamares/" 2>/dev/null || true
cp "$REPO_DIR/installer/archinstall/openbruma.json" "$PROFILE_DIR/airootfs/usr/share/openbruma/archinstall.json" 2>/dev/null || true

# Sync branding
cp "$REPO_DIR/branding/openbruma-wallpaper.png" "$PROFILE_DIR/airootfs/usr/share/backgrounds/" 2>/dev/null || true

sudo mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$PROFILE_DIR"

echo "ISO built in $OUT_DIR"
ls -lh "$OUT_DIR"
sha256sum "$OUT_DIR"/*.iso
