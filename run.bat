@echo off
REM This script installs Python and required packages for the project.

REM Change directory to the project folder
cd %~dp0

REM Check if winget is installed
winget --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo winget is not installed. Consider installing winget from the Microsoft Store.
    exit /b
)

REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed. Install Python? y/n
    set /p choice=
    IF /I "%choice%" EQU "y" (
        REM Install Python using winget
        echo Installing Python...
        winget install -e --id=Python.Python.3.12
    ) ELSE (
        echo Python is required to run this project.
        exit /b
    )
)


REM Check Git
git --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Git is not installed. Install Git? y/n
    set /p choice=
    IF /I "%choice%" EQU "y" (
        REM Install Git using winget
        echo Installing Git...
        winget install -e --id=Git.Git
    ) ELSE (
        echo Git is required to run this project.
        exit /b
    )
)

REM Update the repository
echo Updating the repository from GitHub...
git pull

REM Check if ffmpeg is installed
ffmpeg -version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ffmpeg is not installed. Install ffmpeg? y/n
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

REM Check for .env file
IF NOT EXIST ".env" (
    echo Obtain OpenAI API key and create a .env file with the following content:
    echo OPENAI_API_KEY=your-api-key
    pause
) ELSE (
    echo .env file exists...
)

REM Activate the virtual environment
echo Activating virtual environment...
CALL venv\Scripts\activate

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt



REM Clear the screen
pause
cls

REM Run main.py
python main.py

REM Pause before closing
pause
