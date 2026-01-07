#!/usr/bin/env bash
set -euo pipefail

# Resolve script path
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ "$SOURCE" != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
# -----------------------------------------------------

VENV_DIR="$SCRIPT_DIR/.venv"
REQ_FILE="$SCRIPT_DIR/../requirements.txt"
ENTRYPOINT="$SCRIPT_DIR/../main.py"

# 1. Create venv if it doesn't exist
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating venv at $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
fi


if [[ -f "$REQ_FILE" ]]; then
  REQ_HASH_FILE="$VENV_DIR/.req.md5"
  CURR_HASH=$(md5sum "$REQ_FILE" | awk '{print $1}')
  STORED_HASH=$(cat "$REQ_HASH_FILE" 2>/dev/null || echo "")
  if [[ "$CURR_HASH" != "$STORED_HASH" ]]; then
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r "$REQ_FILE"
    echo "$CURR_HASH" > "$REQ_HASH_FILE"
  fi
fi

exec "$VENV_DIR/bin/python" "$ENTRYPOINT" "$@"
