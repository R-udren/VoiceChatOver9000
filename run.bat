@echo off
REM This script installs Python and required packages for the project.

REM Add shortcut to Desktop
echo Create shortcut to Desktop? (y/n)
set /p choice=
IF /I "%choice%" EQU "y" (
    echo Creating shortcut...
    mklink "C:\Users\%USERNAME%\Desktop\AI-Conversation.lnk" "%~dp0%~n0.bat"
)

REM Check if winget is installed
winget --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo winget is not installed. Consider installing winget from the Microsoft Store.
    exit /b
)

REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed. Install Python? (y/n)
    set /p choice=
    IF /I "%choice%" EQU "y" (
        REM Install Python using winget
        echo Installing Python...
        winget install -e --id=Python.Python
    ) ELSE (
        echo Python is required to run this project.
        exit /b
)

REM Check Git
git --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Git is not installed. Install Git? (y/n)
    set /p choice=
    IF /I "%choice%" EQU "y" (
        REM Install Git using winget
        echo Installing Git...
        winget install -e --id=Git.Git
    ) ELSE (
        echo Git is required to run this project.
        exit /b
)

REM Check if ffmpeg is installed
ffmpeg -version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ffmpeg is not installed. Install ffmpeg? (y/n)
    set /p choice=
    IF /I "%choice%" EQU "y" (
        REM Install ffmpeg using winget
        echo Installing ffmpeg...
        winget install -e --id=Gyan.FFmpeg
    ) ELSE (
        echo ffmpeg is required to run this project.
        exit /b
    )
)

REM Check if venv exists
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
) ELSE (
    echo Virtual environment exists.
)

REM Activate the virtual environment
echo Activating virtual environment...
CALL venv\Scripts\activate

REM Install requirements
echo Installing requirements...
python -m pip install -r requirements.txt

REM Update git
echo Updating git...
git pull

REM Pause and clear the screen
pause
cls

REM Run main.py
python main.py