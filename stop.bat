@echo off
title Stop Staff Payment Portal

cd /d "%~dp0"
python setup.py stop
pause
