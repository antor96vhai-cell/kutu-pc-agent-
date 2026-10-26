@echo off
title KUTU PC Agent
cd /d "%~dp0"

if not exist "venv" (
    echo Age setup.bat chalao! Prothom bar setup korte hobe.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python agent.py

echo.
echo KUTU bondho hoye geche.
pause
