#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f "config.env" ]; then
  echo "❌ config.env not found"
  exit 1
fi

echo "=== Telegram Bot Debug ==="
echo "1. Checking config.env..."
grep -E 'BOT_TOKEN|ALLOWED_CHAT_IDS' config.env || true

echo ""
echo "2. Testing bot import..."
./.venv/bin/python - <<'PY'
import os
from bot.telegram_bot import BOT_TOKEN, ALLOWED_CHAT_IDS, ALLOW_ALL_CHATS
print('BOT_TOKEN_OK', bool(BOT_TOKEN))
print('ALLOWED_CHAT_IDS', ALLOWED_CHAT_IDS)
print('ALLOW_ALL_CHATS', ALLOW_ALL_CHATS)
PY

echo ""
echo "3. Starting bot in foreground (Ctrl+C to stop)"
exec ./.venv/bin/python run.py
