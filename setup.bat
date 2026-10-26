@echo off
title KUTU PC Agent - Setup
echo ===================================================
echo    KUTU PC AGENT - SETUP
echo    Prothom bar setup hote ektu somoy lagbe.
echo ===================================================
echo.

REM ---- Python ache kina check ----
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python pawa jay ni!
    echo Python install koro: https://www.python.org/downloads/
    echo Install er somoy "Add python.exe to PATH" box e obosshoi tick dio.
    echo Tarpor abar setup.bat chalao.
    pause
    exit /b 1
)

REM ---- Virtual environment banano ----
if not exist "venv" (
    echo [1/3] Virtual environment banano hocche...
    python -m venv venv
)

REM ---- Library install ----
echo [2/3] Library install hocche... (internet lagbe, ektu wait koro)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [WARNING] Kichu library install hoy ni.
    echo Bises kore PyAudio fail hole README r Troubleshooting ongsho dekho.
    echo.
)

REM ---- .env file banano ----
if not exist ".env" (
    echo [3/3] .env file banano hocche...
    copy .env.example .env >nul
)

echo.
echo ===================================================
echo    SETUP SESH!
echo ===================================================
echo.
echo Ekhon ekta kaj baki:
echo   1. aistudio.google.com theke FREE Gemini API key nao
echo   2. ei folder er ".env" file ta Notepad diye kholo
echo   3. GEMINI_API_KEY= er pore key ta paste kore Save koro
echo   4. tarpor "run.bat" double-click korlei KUTU chalu!
echo.
pause
