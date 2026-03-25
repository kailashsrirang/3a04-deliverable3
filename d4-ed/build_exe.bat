@echo off
echo ==========================================
echo       SCEMAS Auto-Build Script
echo ==========================================

echo.
echo [1/4] Building React Frontend...
cd frontend
:: We use 'call' here so the batch script doesn't exit after npm finishes
call npm run build
cd ..

echo.
echo [2/4] Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist SCEMAS.spec del SCEMAS.spec

echo.
echo [3/4] Packaging Application into EXE...
:: Running PyInstaller
python -m PyInstaller --name SCEMAS --onefile --add-data "frontend/dist;dist" app.py

echo.
echo ==========================================
echo [4/4] Build Complete! 
echo Check the 'dist' folder for SCEMAS.exe
echo ==========================================
pause