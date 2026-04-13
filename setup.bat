@echo off
title Staff Payment Portal Setup
color 0B

cd /d "%~dp0"

echo ========================================
echo   Staff Payment Portal - First Setup
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Install Python 3.10+ from https://python.org and re-run this file.
    pause
    exit /b 1
)

python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10+ is required.
    echo Your current python version is:
    python --version
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.
echo Running automatic environment setup and app start...
echo This will:
echo 1. Create .venv if missing
echo 2. Install backend requirements
echo 3. Start backend on port 8000
echo 4. Auto-create database and default admin
echo.

python setup.py start
if errorlevel 1 (
    echo.
    echo Setup failed. See error details above.
    echo If pip fails due to network, connect internet and run setup.bat again.
    pause
    exit /b 1
)

echo.
echo Setup complete.
echo Login URL: http://localhost:8000/login.html
echo Default admin: admin@staff.com / admin123
pause
