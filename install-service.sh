#!/usr/bin/env bash
set -euo pipefail

# KML Route Checker Bot - Install as Systemd Service

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="kml-route-checker"
SERVICE_USER="telebot"
SERVICE_GROUP="telebot"
SERVICE_HOME="$SCRIPT_DIR"

echo "========================================="
echo "📦 Installing $SERVICE_NAME as Systemd Service"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run as root (sudo)"
    exit 1
fi

# 1. Create service user if not exists
echo ""
echo "1️⃣  Creating service user..."
if id "$SERVICE_USER" &>/dev/null; then
    echo "✅ User $SERVICE_USER already exists"
else
    useradd --system --home "$SERVICE_HOME" --shell /bin/bash "$SERVICE_USER"
    echo "✅ Created user $SERVICE_USER"
fi

# 2. Set permissions
echo ""
echo "2️⃣  Setting permissions..."
mkdir -p "$SCRIPT_DIR/logs"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$SCRIPT_DIR"

# Make sure parent directories are traversable for the service user
PARENT_DIR="$SCRIPT_DIR"
while [ "$PARENT_DIR" != "/" ]; do
    chmod 755 "$PARENT_DIR" 2>/dev/null || true
    PARENT_DIR="$(dirname "$PARENT_DIR")"
done

chmod 755 "$SCRIPT_DIR"
chmod 755 "$SCRIPT_DIR/run.sh"
chmod 755 "$SCRIPT_DIR/setup.sh"
chmod 755 "$SCRIPT_DIR/install-service.sh"
chmod 755 "$SCRIPT_DIR/telegram-debug.sh"
chmod 755 "$SCRIPT_DIR/backup.sh"
chmod 750 "$SCRIPT_DIR/config.env" 2>/dev/null || true
chmod 750 "$SCRIPT_DIR/.venv" 2>/dev/null || true
chmod 755 "$SCRIPT_DIR/logs"
chmod 700 "$SCRIPT_DIR/.git" 2>/dev/null || true
echo "✅ Permissions set"

# 3. Create systemd service file
echo ""
echo "3️⃣  Creating systemd service..."
cat > "/etc/systemd/system/$SERVICE_NAME.service" <<EOF
[Unit]
Description=KML Route Checker Bot
After=network.target
Documentation=https://github.com/your-repo

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=$SCRIPT_DIR/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$SCRIPT_DIR/.venv/bin/python run.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created at /etc/systemd/system/$SERVICE_NAME.service"

# 4. Reload systemd
echo ""
echo "4️⃣  Reloading systemd..."
systemctl daemon-reload
echo "✅ Systemd reloaded"

# 5. Enable service
echo ""
echo "5️⃣  Enabling service..."
systemctl enable "$SERVICE_NAME"
echo "✅ Service enabled to start on boot"

echo ""
echo "========================================="
echo "✅ Installation completed!"
echo "========================================="
echo ""
echo "Service commands:"
echo "  Start:   sudo systemctl start $SERVICE_NAME"
echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
echo "  Status:  sudo systemctl status $SERVICE_NAME"
echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo "  Restart: sudo systemctl restart $SERVICE_NAME"
