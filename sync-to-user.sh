#!/bin/bash

# Sync repo contents to ~/.claude
# Creates target directories if missing.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

if [ ! -d "$CLAUDE_DIR" ]; then
    echo "Error: ~/.claude does not exist." >&2
    exit 1
fi

sync_dir() {
    local src="$SCRIPT_DIR/$1"
    [ ! -d "$src" ] && return
    mkdir -p "$CLAUDE_DIR/$1"
    rsync -a --delete "$src/" "$CLAUDE_DIR/$1/"
    echo "  $1/"
}

sync_file() {
    local src="$SCRIPT_DIR/$1"
    [ ! -f "$src" ] && return
    cp "$src" "$CLAUDE_DIR/$1"
    echo "  $1"
}

echo "Syncing to $CLAUDE_DIR:"

sync_dir agents
sync_dir commands
sync_dir hooks
sync_dir skills
sync_dir ccline

sync_file CLAUDE.md
sync_file README.md
sync_file settings.json
sync_file minimal-config.json
sync_file powerline-config.json

echo "Done."
