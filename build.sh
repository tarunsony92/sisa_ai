#!/bin/bash
# Build script for generating documentation and running tests

echo ""
echo "===================================================="
echo "   AI Secure Data Intelligence Platform - Build"
echo "===================================================="
echo ""

cd "$(dirname "$0")"

# Install backend dependencies
echo "[1/3] Installing backend dependencies..."
cd backend
pip3 install -q -r requirements.txt
cd ..

# Check project structure
echo "[2/3] Checking project structure..."
[ -f backend/app.py ] && echo "    [OK] Backend app.py found"
[ -f frontend/index.html ] && echo "    [OK] Frontend index.html found"
[ -f backend/config.py ] && echo "    [OK] Backend config.py found"
[ -f backend/modules/detection_engine.py ] && echo "    [OK] Detection engine found"
[ -f backend/modules/log_analyzer.py ] && echo "    [OK] Log analyzer found"
[ -f backend/modules/risk_engine.py ] && echo "    [OK] Risk engine found"
[ -f backend/modules/policy_engine.py ] && echo "    [OK] Policy engine found"

echo "[3/3] Build complete!"
echo ""
echo "Next steps:"
echo "   1. Run: ./start_backend.sh"
echo "   2. Open: frontend/index.html in your browser"
echo "   3. Or run: ./start_frontend.sh for separate frontend server"
echo ""
