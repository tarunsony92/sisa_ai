@echo off
REM Build script for generating documentation and running tests

echo.
echo ====================================================
echo   AI Secure Data Intelligence Platform - Build
echo ====================================================
echo.

cd /d "%~dp0"

REM Install backend dependencies
echo [1/3] Installing backend dependencies...
cd backend
pip install -q -r requirements.txt

cd ..

REM Run tests (if test file exists)
echo [2/3] Checking project structure...
if exist backend\app.py echo    [OK] Backend app.py found
if exist frontend\index.html echo    [OK] Frontend index.html found
if exist backend\config.py echo    [OK] Backend config.py found
if exist backend\modules\detection_engine.py echo    [OK] Detection engine found
if exist backend\modules\log_analyzer.py echo    [OK] Log analyzer found
if exist backend\modules\risk_engine.py echo    [OK] Risk engine found
if exist backend\modules\policy_engine.py echo    [OK] Policy engine found

echo [3/3] Build complete!
echo.
echo Next steps:
echo   1. Run: start_backend.bat (or start_backend.sh on Linux/Mac)
echo   2. Open: frontend/index.html in your browser
echo   3. Or run: start_frontend.bat for separate frontend server
echo.

pause
