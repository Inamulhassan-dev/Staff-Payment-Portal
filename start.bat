@echo off
title Staff Payment Portal
color 0A

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

python setup.py start
if errorlevel 1 (
    echo.
    echo Setup failed. Check error above.
    pause
    exit /b 1
)
