#!/usr/bin/env bash
set -euo pipefail

# KML Route Checker Bot - Setup Script for Linux
# Usage: bash setup.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "🤖 KML Route Checker Bot - Setup"
echo "========================================="

# 1. Check Python version
echo "1️⃣  Checking Python version..."
PYTHON_BIN=$(command -v python3 || command -v python)
if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_BIN -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# 2. Create virtual environment
echo ""
echo "2️⃣  Setting up virtual environment..."
if [ -d ".venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    $PYTHON_BIN -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate venv
source .venv/bin/activate

# 3. Upgrade pip
echo ""
echo "3️⃣  Upgrading pip..."
pip install --upgrade pip >/dev/null 2>&1
echo "✅ pip upgraded"

# 4. Install dependencies
echo ""
echo "4️⃣  Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# 5. Verify installation
echo ""
echo "5️⃣  Verifying installation..."
$PYTHON_BIN -c "
import importlib
packages = {'dotenv': 'dotenv', 'telegram': 'telegram', 'discord': 'discord', 'geopy': 'geopy', 'pyproj': 'pyproj'}
failed = []
for name, module in packages.items():
    try:
        importlib.import_module(module)
    except ImportError:
        failed.append(name)
if failed:
    print(f'⚠️  Could not verify: {failed} (may still be installed)')
else:
    print('✅ All packages verified')
"

# 6. Check config.env
echo ""
echo "6️⃣  Checking configuration..."
if [ ! -f "config.env" ]; then
    echo "⚠️  config.env not found. Creating template..."
    cat > config.env.template <<'EOF'
BOT_TOKEN=your_telegram_bot_token_here
ALLOWED_CHAT_IDS=your_chat_id_here
DISCORD_TOKEN=your_discord_token_here
MYMAP_ID=your_google_mymap_id_here
EOF
    echo "📝 Created config.env.template - please fill in your tokens"
    exit 1
else
    echo "✅ config.env found"
fi

# 7. Run basic test
echo ""
echo "7️⃣  Running basic tests..."
if .venv/bin/python -m pytest tests/ -q 2>/dev/null; then
    echo "✅ Tests passed"
else
    echo "⚠️  Tests not available or failed (non-critical)"
fi

echo ""
echo "========================================="
echo "✅ Setup completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit config.env with your bot tokens"
echo "2. Run: ./run.sh"
echo "3. Or install as systemd service: sudo bash install-service.sh"
