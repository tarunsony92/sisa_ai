#!/bin/bash
# AI Secure Data Intelligence Platform - Linux/Mac Startup Script

echo ""
echo "===================================================="
echo "   AI Secure Data Intelligence Platform"
echo "   Starting Backend Server"
echo "===================================================="
echo ""

cd "$(dirname "$0")/backend"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

# Install requirements if needed
echo "Checking dependencies..."
pip3 install -q -r requirements.txt

echo ""
echo "Starting server..."
echo "API will be available at: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
echo ""
echo "Frontend: Open frontend/index.html in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
