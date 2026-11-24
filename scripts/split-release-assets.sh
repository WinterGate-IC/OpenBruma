#!/bin/bash
# Split an OpenBruma ISO into 250 MB parts for GitHub Release upload and
# generate per-part and whole-file checksums.
#
#   ./scripts/split-release-assets.sh path/to/openbruma-amd64.hybrid.iso [outdir]
#
# GitHub's HTTP upload times out on multi-GB assets on slow links, so release
# builds are published as parts and reassembled by the user (docs/ISO-PARTS.md).
set -euo pipefail

ISO="${1:-}"
OUT="${2:-release-parts}"
PART_SIZE="250m"

if [ -z "$ISO" ] || [ ! -f "$ISO" ]; then
  echo "usage: $0 path/to/openbruma-amd64.hybrid.iso [outdir]" >&2
  exit 1
fi

mkdir -p "$OUT"
rm -f "$OUT"/openbruma-amd64.hybrid.iso.part-* "$OUT"/SHA256SUMS.parts

sha256sum "$ISO" | awk '{print $1"  openbruma-amd64.hybrid.iso"}' > "$OUT/SHA256SUMS.debian"
split -b "$PART_SIZE" -d -a 2 "$ISO" "$OUT/openbruma-amd64.hybrid.iso.part-"
cd "$OUT"
sha256sum openbruma-amd64.hybrid.iso.part-* > SHA256SUMS.parts

echo "parts:    $(ls -1 openbruma-amd64.hybrid.iso.part-* | wc -l)"
echo "checksums: SHA256SUMS.parts, SHA256SUMS.debian"
echo "iso sha256: $(cut -d' ' -f1 SHA256SUMS.debian)"
echo "reassemble: cat openbruma-amd64.hybrid.iso.part-* > openbruma-amd64.hybrid.iso"
