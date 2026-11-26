#!/bin/bash
# Create a small, non-sensitive demo case and verify the sealed bundle.
# Run inside OpenBruma (or any Debian host with gocryptfs/gnupg installed).
set -eu
PASS="${BRUMA_DEMO_PASSPHRASE:-correct-horse-battery}"
WORK="${TMPDIR:-/tmp}/bruma-demo-artifact.txt"

echo "OpenBruma Case Capsule - demo" >"$WORK"

printf '%s\n%s\n' "$PASS" "$PASS" | bruma case new "Demo case - example.com" \
  --operator "demo operator" --scope "non-sensitive public example"
CID=$(bruma case list | awk '/\*/ {print $2}' | head -1)
[ -n "$CID" ] || CID=$(bruma case list | tail -1 | awk '{print $2}')

printf '%s\n' "$PASS" | bruma case open "$CID"
bruma evidence add "$WORK" --notes "harmless demo artifact"
bruma note "Demo note: chain verified after sealing"
bruma run -- whois example.com >/dev/null || true
printf '%s\n%s\n' "$PASS" "$PASS" | bruma case seal

BUNDLE=$(ls "$HOME"/OpenBruma-Cases/*-sealed-*.gpg "$HOME"/OpenBruma-Cases/*-sealed-*.age 2>/dev/null | tail -1)
printf '%s\n' "$PASS" | bruma case verify "$BUNDLE"
