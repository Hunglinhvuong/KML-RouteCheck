import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from bot.telegram_bot import main

if __name__ == "__main__":
    print("======================================")
    print("🚀 Starting KML Route Checker Bot")
    print("📂 Base directory:", PROJECT_ROOT)
    print("======================================")

    main()
