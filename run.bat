@echo off
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

REM Check if venv exists
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
) ELSE (
    echo Virtual environment exists.
)

REM Activate the virtual environment
CALL venv\Scripts\activate

REM Check if requirements are installed
python -c "
try:
    import PyAudio, dotenv, colorama, pydub, openai
    print('All requirements are installed.')
except ImportError:
    print('Installing requirements...')
    import subprocess
    subprocess.check_call(['python', '-m', 'pip', 'install', '-r', 'requirements.txt'])
"

pause
cls

REM Run main.py
python main.py