#!/bin/bash
set -e
export REPO_DIR=/root/OpenBruma
export OUT_DIR=/root/openbruma-out
export WORK_DIR=/tmp/openbruma-work
cd /root/OpenBruma
bash scripts/build-iso.sh
echo "BUILD DONE"
ls -lh /root/openbruma-out
