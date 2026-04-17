@echo off
:: ═══════════════════════════════════════════════════════
::  NOVA — Build Script
::  Run this file to create Nova.exe inside the dist/ folder
::  Double-click build.bat  OR  run it in Command Prompt
:: ═══════════════════════════════════════════════════════

title Building Nova...
color 0B
echo.
echo  ======================================================
echo    NOVA - Building .exe  (this takes 1-3 minutes)
echo  ======================================================
echo.

:: Step 1: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install from https://python.org
    pause
    exit /b 1
)
echo  [OK] Python found

:: Step 2: Install / upgrade dependencies
echo.
echo  [1/3] Installing dependencies...
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
echo  [OK] Dependencies installed

:: Step 3: Build with PyInstaller
echo.
echo  [2/3] Building Nova.exe with PyInstaller...
pyinstaller nova.spec --clean --noconfirm

:: Step 4: Check output
echo.
if exist "dist\Nova.exe" (
    echo  [3/3] SUCCESS!
    echo.
    echo  ======================================================
    echo    Nova.exe is ready inside the  dist\  folder
    echo    Share that single file with anyone on Windows!
    echo  ======================================================
    echo.
    explorer dist
) else (
    echo  [ERROR] Build failed. Check the output above for errors.
    echo  Common fix: run  pip install pyinstaller  then try again.
)

pause
