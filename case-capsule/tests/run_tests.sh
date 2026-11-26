#!/bin/bash
# Acceptance tests for Case Capsule (run as a normal user, HOME is disposable).
set -u
BRUMA="python3 /mnt/c/Users/zerop/OpenBruma/case-capsule/bruma.py"
PASS="correct-horse-battery"
WRONG="definitely-not-the-passphrase"
export HOME="${HOME:-/root/bruma-test-home}"
rm -rf "$HOME/.local/share/bruma" "$HOME/.local/state/bruma" "$HOME/OpenBruma-Cases" /tmp/bruma-*
mkdir -p "$HOME"

pass() { echo "PASS: $*"; }
fail() { echo "FAIL: $*"; FAILED=1; }
FAILED=0

echo "=== 1. create/open/run/seal ==="
echo "First test case" > /tmp/evidence-test.txt
printf '%s\n%s\n' "$PASS" "$PASS" | $BRUMA case new "Test case" --operator tester --scope "local test" >/tmp/t1.log 2>&1 \
  && pass "case new" || { fail "case new"; cat /tmp/t1.log; }
CID=$(grep -o 'Created case [^ ]*' /tmp/t1.log | awk '{print $3}')
[ -n "$CID" ] && pass "case id $CID" || fail "case id"
printf '%s\n' "$PASS" | $BRUMA case open "$CID" >>/tmp/t1.log 2>&1 && pass "case open" || { fail "case open"; tail -3 /tmp/t1.log; }
$BRUMA case status >>/tmp/t1.log 2>&1 && pass "case status" || fail "status"
$BRUMA evidence add /tmp/evidence-test.txt >>/tmp/t1.log 2>&1 && pass "evidence" || fail "evidence"
$BRUMA note "observed example.com DNS" >>/tmp/t1.log 2>&1 && pass "note" || fail "note"
$BRUMA run -- whois example.com >/tmp/whois.out 2>/tmp/whois.err && pass "bruma run whois" || fail "bruma run whois"
grep -qi "domain name" /tmp/whois.out && pass "whois output captured" || fail "whois output"
$BRUMA case status >>/tmp/t1.log 2>&1
grep -q "Chain:    OK" /tmp/t1.log && pass "chain ok before seal" || fail "chain before seal"
printf '%s\n%s\n' "$PASS" "$PASS" | $BRUMA case seal >>/tmp/t1.log 2>&1 && pass "seal" || { fail "seal"; tail -4 /tmp/t1.log; }

echo "=== 2. verify bundle ==="
BUNDLE=$(ls "$HOME"/OpenBruma-Cases/*.age "$HOME"/OpenBruma-Cases/*.gpg 2>/dev/null | head -1)
[ -n "$BUNDLE" ] && pass "bundle exists" || fail "bundle missing"
printf '%s\n' "$PASS" | $BRUMA case verify "$BUNDLE" >/tmp/verify.log 2>&1
grep -q "Verify: PASS" /tmp/verify.log && pass "verify passes" || { fail "verify failed"; cat /tmp/verify.log; }

echo "=== 3. wrong passphrase ==="
printf '%s\n' "$WRONG" | $BRUMA case open "$CID" >/tmp/wrong.log 2>&1
grep -qi "cannot open case\|wrong passphrase\|failed" /tmp/wrong.log && pass "wrong passphrase refused" || fail "wrong passphrase accepted"
$BRUMA case close >/dev/null 2>&1

echo "=== 4. tamper detection ==="
printf '%s\n%s\n' "$PASS" "$PASS" | $BRUMA case new "Tamper case" --operator tester >/tmp/t2.log 2>&1
CID2=$(grep -o 'Created case [^ ]*' /tmp/t2.log | awk '{print $3}')
printf '%s\n' "$PASS" | $BRUMA case open "$CID2" >/dev/null 2>&1
$BRUMA note "original note" >/dev/null 2>&1
ROOT=$(python3 - "$CID2" <<'PY'
import json, os, sys
sid = sys.argv[1]
root = os.path.expanduser("~/.local/share/bruma/cases/%s/mnt/case.db" % sid)
print(root)
PY
)
sqlite3 "$HOME/.local/share/bruma/cases/$CID2/mnt/case.db" "UPDATE events SET payload='{\"text\":\"tampered\"}' WHERE type='note';"
$BRUMA case status >/tmp/status2.log 2>&1
grep -q "Chain:    BROKEN" /tmp/status2.log && pass "tamper detected" || { fail "tamper not detected"; cat /tmp/status2.log; }
printf '%s\n%s\n' "$PASS" "$PASS" | $BRUMA case seal >/tmp/seal2.log 2>&1
grep -qi "refusing to seal" /tmp/seal2.log && pass "seal refused on broken chain" || fail "seal allowed on broken chain"
$BRUMA case close >/dev/null 2>&1

echo "=== 5. no plaintext after seal ==="
if find "$HOME/.local/share/bruma" -name 'case.db' 2>/dev/null | grep -q .; then
  fail "plaintext case.db left behind"
else
  pass "no plaintext database left"
fi
find /tmp -maxdepth 1 -name 'bruma-*' 2>/dev/null | grep -q . && fail "temp dirs left in /tmp" || pass "no temp dirs in /tmp"

echo "=== 6. normal terminal unaffected ==="
if command -v maigret >/dev/null 2>&1; then
  if [ "$(command -v maigret)" = "$HOME/.local/share/bruma/cases/$CID/mnt/.bruma/bin/maigret" ]; then
    fail "wrapper leaked outside case shell"
  fi
fi
pass "no global PATH interception (only case shell/bruma run)"

echo
if [ "$FAILED" = 0 ]; then echo "ALL TESTS PASSED"; else echo "SOME TESTS FAILED"; exit 1; fi
