@echo off
echo ==============================
echo BUILD TELEGRAM KML BOT
echo ==============================

pyinstaller ^
  --onefile ^
  --name KML_Route_Checker ^
  --hidden-import=telegram ^
  --hidden-import=telegram.ext ^
  --hidden-import=core ^
  run.py

echo ==============================
echo BUILD DONE
pause
