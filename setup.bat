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
REM Ager bar setup majhkhane fail hole venv er vitore adha-install
REM library thakte pare. Sofol setup er marker (venv\.kutu-ok) na
REM thakle purono venv ta muche ekdom notun kore banano hoy.
if exist "venv" (
    if not exist "venv\.kutu-ok" (
        echo [INFO] Ager adha-setup er venv pawa geche - muche notun kore banacchi...
        rmdir /s /q venv
    )
)
if not exist "venv" (
    echo [1/3] Virtual environment banano hocche...
    python -m venv venv
)

REM ---- Library install ----
echo [2/3] Library install hocche... (internet lagbe, ektu wait koro)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip

REM Step A: requirements.txt er sob library ready-made wheel theke
pip install --only-binary :all: -r requirements.txt
if errorlevel 1 (
    echo.
    echo [WARNING] Kichu library install hoy ni.
    echo Uporer error ta dekho, ar README r Troubleshooting ongsho dekho.
    echo Tarpor abar setup.bat chalao.
    echo.
    pause
    exit /b 1
)

REM Step B: PyAutoGUI r kono wheel nai - eta sdist thekei install hoy.
REM Chinta nai, eta pure Python, compile kichu lage na.
echo [2/3] PyAutoGUI install hocche... (eta alada step)
pip install pyautogui
if errorlevel 1 (
    echo.
    echo [WARNING] PyAutoGUI install hoy ni.
    echo Internet connection check kore abar setup.bat chalao.
    echo.
    pause
    exit /b 1
)

REM ---- Sob library sotti sotti kaj kore kina verify ----
echo [2/3] Library gula check hocche...
python -c "import pyautogui, sounddevice, soundfile, speech_recognition, edge_tts, google.generativeai, dotenv, PIL"
if errorlevel 1 (
    echo.
    echo [WARNING] Library install holeo kichu ekta thik moto kaj korche na.
    echo Uporer error ta dekho, ar README r Troubleshooting ongsho dekho.
    echo Tarpor abar setup.bat chalao.
    echo.
    pause
    exit /b 1
)
echo ok> venv\.kutu-ok

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
