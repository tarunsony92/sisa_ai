#!/bin/bash
# AI Secure Data Intelligence Platform - Frontend Startup Script

echo ""
echo "===================================================="
echo "   AI Secure Data Intelligence Platform"
echo "   Starting Frontend Server"
echo "===================================================="
echo ""

cd "$(dirname "$0")/frontend"

echo ""
echo "Frontend will be available at: http://localhost:3000"
echo "Backend should be running on: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m http.server 3000
