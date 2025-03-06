@echo off
setlocal EnableDelayedExpansion

title VoiceChat Over 9000 Setup
color 0A

echo ================================================
echo           VoiceChat Over 9000 Setup
echo                  Version 1.0
echo ================================================
echo.

:: Change to script directory
cd /d "%~dp0"

:: Check internet connectivity
echo [*] Checking internet connection...
ping -n 1 github.com >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] No internet connection detected.
    echo         Please check your connection and try again.
    goto :exit
)

:: Check for required tools with colorful feedback
call :check_dependency "winget" "winget --version" "Microsoft Store" "" "0"
if errorlevel 1 goto :exit

call :check_dependency "Python" "python --version" "Python.Python.3.12" "python" "1"
if errorlevel 1 goto :exit

call :check_dependency "Git" "git --version" "Git.Git" "git" "1" 
if errorlevel 1 goto :exit

call :check_dependency "FFmpeg" "ffmpeg -version" "Gyan.FFmpeg" "ffmpeg" "1"
if errorlevel 1 goto :exit

:: Update repository
echo.
echo [*] Updating repository from GitHub...
git pull || (
    color 0C
    echo [ERROR] Failed to update from GitHub.
    goto :exit
)

:: Check/create virtual environment
echo.
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv || (
        color 0C
        echo [ERROR] Failed to create virtual environment.
        goto :exit
    )
    echo [+] Virtual environment created successfully.
) else (
    echo [+] Virtual environment exists.
)

:: Check for .env file
echo.
if not exist ".env" (
    color 0E
    echo [!] OpenAI API key required
    echo     Create a .env file with the following content:
    echo.
    echo     OPENAI_API_KEY=your-api-key
    echo.
    set /p continue="Press Enter when ready to continue or Q to quit: "
    if /i "!continue!"=="Q" goto :exit
    color 0A
) else (
    echo [+] .env file exists.
)

:: Activate and update virtual environment
echo.
echo [*] Activating virtual environment...
call venv/Scripts/activate || (
    color 0C
    echo [ERROR] Failed to activate virtual environment.
    goto :exit
)

echo [*] Installing required packages...
pip install -r requirements.txt || (
    color 0C
    echo [ERROR] Failed to install required packages.
    goto :exit
)

:: Run the application
echo.
echo [*] Starting VoiceChat Over 9000...
echo ================================================
python main.py

echo.
echo ================================================
echo           VoiceChat Over 9000 closed
echo ================================================

:exit
echo.
pause
endlocal
exit /b

:: Function to check dependencies
:check_dependency
echo.
echo [*] Checking for %~1...
%~2 >nul 2>&1
if errorlevel 1 (
    if "%~5"=="0" (
        color 0C
        echo [ERROR] %~1 is required but not installed.
        echo         Please install from %~3.
        exit /b 1
    ) else (
        echo [X] %~1 not found. Install it? Y/N
        set /p user_choice=
        if /i "!user_choice!"=="Y" (
            echo [*] Installing %~1...
            winget install -e --id=%~3
            if errorlevel 1 (
                color 0C
                echo [ERROR] Failed to install %~1.
                exit /b 1
            )
            echo [+] %~1 installed successfully.
        ) else (
            color 0C
            echo [ERROR] %~1 is required to run this project.
            exit /b 1
        )
    )
) else (
    echo [+] %~1 is installed.
)
exit /b 0