#!/usr/bin/env bash
# Immediate one-shot synchronization of conversation & InfinityFree code to GitHub
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

chmod +x "$SCRIPT_DIR/sync/sync_daemon.py"
python3 "$SCRIPT_DIR/sync/sync_daemon.py" --once
