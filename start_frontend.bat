@echo off
REM AI Secure Data Intelligence Platform - Frontend Startup Script
echo.
echo ====================================================
echo   AI Secure Data Intelligence Platform
echo   Starting Frontend Server
echo ====================================================
echo.

cd /d "%~dp0frontend"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

echo.
echo Frontend will be available at: http://localhost:3000
echo Backend should be running on: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

python -m http.server 3000

pause
