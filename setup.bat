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

REM ---- Icon + Desktop shortcut (v3) ----
REM Ekhane kichu fail holeo setup theme jabe na - shortcut
REM charao KUTU.bat double-click korlei app khulbe.
echo [3/3] Icon ar Desktop shortcut banano hocche...
python -c "import base64,os,importlib.util; s=importlib.util.find_spec('icon_data'); open('kutu.png','wb').write(base64.b64decode(__import__('icon_data').PNG_B64)) if s and not os.path.exists('kutu.png') else None" 2>nul
python -c "import os; from PIL import Image; Image.open('kutu.png').save('kutu.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]) if os.path.exists('kutu.png') else None" 2>nul
powershell -NoProfile -Command "$d=[Environment]::GetFolderPath('Desktop'); $w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut($d+'\KUTU Agent.lnk'); $s.TargetPath='%~dp0KUTU.bat'; $s.WorkingDirectory='%~dp0'; if (Test-Path '%~dp0kutu.ico') { $s.IconLocation='%~dp0kutu.ico' }; $s.Description='KUTU Agent'; $s.Save()" 2>nul
echo (Shortcut na holeo somossa nai - KUTU.bat double-click korlei cholbe)

echo.
echo ===================================================
echo    SETUP SESH!
echo ===================================================
echo.
echo Ekhon ekta kaj baki:
echo   1. aistudio.google.com theke FREE Gemini API key nao
echo   2. ei folder er ".env" file ta Notepad diye kholo
echo   3. GEMINI_API_KEY= er pore key ta paste kore Save koro
echo   4. tarpor Desktop er "KUTU Agent" shortcut (ba ei folder er KUTU.bat) double-click korlei KUTU chalu!
echo      (Kalo console e dekhte chaile run.bat diyeo chalano jay)
echo.
pause
