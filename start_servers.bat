@echo off
echo Starting FastAPI server and Flask app...

REM Start FastAPI server in a new window
start cmd /k "cd /d %~dp0 && python run_fastapi.py"

REM Wait a moment for FastAPI to start
timeout /t 3 /nobreak > nul

REM Start Flask app in a new window
start cmd /k "cd /d %~dp0 && python run_app.py"

echo Both servers started!
echo FastAPI server running at http://localhost:8000
echo Flask app running at http://localhost:5000
echo.
echo Press any key to exit this window...
pause > nul
