@echo off
REM This script installs Python and required packages for the project.

REM Check if winget is installed
winget --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo winget is not installed. Please install it manually.
    exit /b
)

REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed. Installing Python...
    REM Install Python using winget
    winget install -e --id Python.Python
)

REM Check Git
git --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Git is not installed. Please install it manually.
    exit /b
)

REM Check if ffmpeg is installed
ffmpeg -version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ffmpeg is not installed. Installing ffmpeg...
    REM Install ffmpeg using winget
    winget install -e --id=Gyan.FFmpeg
)

REM Check if venv exists
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
) ELSE (
    echo Virtual environment exists.
)

REM Activate the virtual environment
CALL venv\Scripts\activate

REM Install requirements
echo Installing requirements...
python -m pip install -r requirements.txt

REM Update git
echo Updating git...
git pull

REM Run main.py
python main.py