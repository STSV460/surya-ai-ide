#!/usr/bin/env bash
# Copy shared surya-agent-core + surya-vscode-extension into a given fork.
# Usage: ./sync.sh "Surya AI Code Mac" | "Surya AI Code Windows" | "Surya AI Code Linux"
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FORK_DIR_NAME="${1:?fork dir name required}"
FORK="$ROOT/$FORK_DIR_NAME"
UPSTREAM="$FORK/upstream"
DEST_EXT="$UPSTREAM/extensions/surya-ai"
DEST_CORE="$DEST_EXT/agent-core"

[ -d "$UPSTREAM" ] || { echo "upstream missing in $FORK"; exit 1; }

echo ">> sync extension -> $DEST_EXT"
rm -rf "$DEST_EXT"
mkdir -p "$DEST_EXT"
rsync -a --delete \
  --exclude node_modules --exclude out --exclude .git \
  "$ROOT/surya-vscode-extension/" "$DEST_EXT/"

echo ">> sync agent-core -> $DEST_CORE"
mkdir -p "$DEST_CORE"
rsync -a --delete \
  --exclude __pycache__ --exclude .venv --exclude .git \
  "$ROOT/surya-agent-core/" "$DEST_CORE/"

echo ">> done"
