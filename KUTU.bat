@echo off
title KUTU Agent
cd /d "%~dp0"

if not exist "venv" (
    echo Age setup.bat chalao! Prothom bar setup korte hobe.
    pause
    exit /b 1
)

REM App window khule - kalo console window asbe na (pythonw).
REM pythonw na thakle python diyei khulbe.
if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" kutu_gui.py
) else (
    start "" "venv\Scripts\python.exe" kutu_gui.py
)
