#!/usr/bin/env bash
set -euo pipefail

# KML Route Checker Bot - Backup Script
# Usage: bash backup.sh [backup_dir]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${1:-.}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="kml-bot-backup_${TIMESTAMP}"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

echo "========================================="
echo "💾 KML Route Checker Bot - Backup"
echo "========================================="
echo "Backup timestamp: $TIMESTAMP"
echo "Backup location: $BACKUP_PATH"
echo ""

# Create backup directory
mkdir -p "$BACKUP_PATH"

# 1. Backup config (but not sensitive tokens)
echo "1️⃣  Backing up configuration..."
if [ -f "$SCRIPT_DIR/config.env" ]; then
    cp "$SCRIPT_DIR/config.env" "$BACKUP_PATH/config.env"
    # Mask tokens in backup
    sed -i 's/BOT_TOKEN=.*/BOT_TOKEN=***masked***/g' "$BACKUP_PATH/config.env"
    sed -i 's/DISCORD_TOKEN=.*/DISCORD_TOKEN=***masked***/g' "$BACKUP_PATH/config.env"
    echo "✅ Configuration backed up (tokens masked)"
fi

# 2. Backup data
echo ""
echo "2️⃣  Backing up data..."
if [ -d "$SCRIPT_DIR/data" ]; then
    cp -r "$SCRIPT_DIR/data" "$BACKUP_PATH/"
    echo "✅ Data directory backed up"
fi

# 3. Backup logs
echo ""
echo "3️⃣  Backing up logs..."
if [ -d "$SCRIPT_DIR/logs" ]; then
    cp -r "$SCRIPT_DIR/logs" "$BACKUP_PATH/" 2>/dev/null || true
    echo "✅ Logs backed up"
fi

# 4. Backup source code (exclude venv)
echo ""
echo "4️⃣  Backing up source code..."
rsync -a --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='.pytest_cache' --exclude='logs' --exclude='config.env' \
    "$SCRIPT_DIR"/{bot,core,utils,tests,*.py,*.sh,*.txt,*.md,*.yml,*.yaml,Dockerfile} \
    "$BACKUP_PATH/source/" 2>/dev/null || true
echo "✅ Source code backed up"

# 5. Create archive
echo ""
echo "5️⃣  Creating archive..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
ARCHIVE_SIZE=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)
rm -rf "$BACKUP_NAME"
echo "✅ Archive created: ${BACKUP_NAME}.tar.gz ($ARCHIVE_SIZE)"

echo ""
echo "========================================="
echo "✅ Backup completed!"
echo "========================================="
echo ""
echo "Archive: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "To restore:"
echo "  tar -xzf ${BACKUP_NAME}.tar.gz"
