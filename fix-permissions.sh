#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_USER="${1:-telebot}"

if [ "$EUID" -ne 0 ]; then
  echo "❌ Run with sudo"
  exit 1
fi

echo "Fixing permissions for $SCRIPT_DIR"
mkdir -p "$SCRIPT_DIR/logs"
chown -R "$SERVICE_USER:$SERVICE_USER" "$SCRIPT_DIR"

PARENT_DIR="$SCRIPT_DIR"
while [ "$PARENT_DIR" != "/" ]; do
  chmod 755 "$PARENT_DIR" 2>/dev/null || true
  PARENT_DIR="$(dirname "$PARENT_DIR")"
done

chmod 755 "$SCRIPT_DIR"
chmod 755 "$SCRIPT_DIR"/*.sh 2>/dev/null || true
chmod 755 "$SCRIPT_DIR/logs"
chmod 750 "$SCRIPT_DIR/config.env" 2>/dev/null || true
chmod 750 "$SCRIPT_DIR/.venv" 2>/dev/null || true
chmod 700 "$SCRIPT_DIR/.git" 2>/dev/null || true

echo "✅ Permissions fixed"
