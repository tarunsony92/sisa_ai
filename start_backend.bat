@echo off
REM AI Secure Data Intelligence Platform - Windows Startup Script
echo.
echo ====================================================
echo   AI Secure Data Intelligence Platform
echo   Starting Backend Server
echo ====================================================
echo.

cd /d "%~dp0backend"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

REM Install requirements if needed
echo Checking dependencies...
pip install -q -r requirements.txt

echo.
echo Starting server...
echo API will be available at: http://localhost:8000
echo Health check: http://localhost:8000/health
echo.
echo Frontend: Open ../frontend/index.html in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
