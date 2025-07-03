@echo off
echo ===================================
echo Water Intake Tracker Launcher
echo ===================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if required directories exist
if not exist "water_tracker" (
    echo ERROR: water_tracker directory not found.
    echo Make sure you're running this from the correct directory.
    echo.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking requirements...
pip show flask >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Some dependencies may be missing. Installing requirements...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install requirements.
        echo Please run 'pip install -r requirements.txt' manually.
        echo.
        pause
        exit /b 1
    )
)

REM Generate avatars if they don't exist
if not exist "water_tracker\static\images\avatars\avatar1.png" (
    echo Generating default avatars...
    python water_tracker/generate_simple_avatars.py
)

echo Starting Water Intake Tracker...
echo.
echo The application will be available at: http://127.0.0.1:8080
echo Press Ctrl+C to stop the server
echo.

python run.py

pause
