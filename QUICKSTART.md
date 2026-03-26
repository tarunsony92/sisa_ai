# AI Secure Data Intelligence Platform - Quick Start Guide

## Installation & Setup

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Backend Server
```bash
python app.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Open Frontend
Open the frontend in your browser:
- File path: `frontend/index.html`
- Or serve it: `cd frontend && python -m http.server 3000`

Visit: `http://localhost:3000` (or `http://localhost:8000` if accessing through API)

## Testing the Platform

### Test 1: Analyze Sample Code with Sensitive Data
1. Go to "Text Analysis" tab
2. Paste this code:
```
password=admin123
api_key=sk-prod-xyz789
email=admin@company.com
```
3. Click "Analyze"

### Test 2: Upload Sample Log
1. Go to "File Upload" tab
2. Select `example_data/sample.log`
3. Click "Upload & Analyze"

### Test 3: SQL Injection Detection
1. Go to "Text Analysis" tab
2. Select "SQL Code" from dropdown
3. Paste:
```sql
SELECT * FROM users WHERE id = 1 OR 1=1; DROP TABLE users;
```
4. Click "Analyze"

## Features Overview

### 🔍 Detection Engine
- Finds passwords, API keys, tokens, emails, phone numbers
- Detects SQL injection patterns
- Identifies stack traces and debug information
- Extracts credit cards and SSN

### 📊 Log Analyzer
- Parses log files line-by-line
- Extracts log levels and timestamps
- Detects anomalies and patterns
- Identifies brute force attempts
- Generates security audit trail

### ⚠️ Risk Engine
- Calculates numerical risk scores (0-10)
- Assigns risk levels: CRITICAL, HIGH, MEDIUM, LOW
- Provides remediation time estimates
- Identifies critical threats

### 🛡️ Policy Engine
- GDPR compliance checking
- PCI-DSS validation
- HIPAA compliance
- SOX audit trail
- ISO-27001 security controls

### 🤖 AI Insights (Optional)
- When API key configured: intelligent recommendations
- Otherwise: rule-based insights
- Both modes generate actionable guidance

## API Quick Reference

### Health Check
```bash
curl http://localhost:8000/health
```

### Analyze Text
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "password=secret123",
    "options": {"mask": true}
  }'
```

### Upload File
```bash
curl -X POST http://localhost:8000/analyze/file \
  -F "file=@example_data/sample.log"
```

## Troubleshooting

### Error: "Port already in use"
Change port in `.env`:
```env
PORT=8001
```

### Error: "CORS Origin not allowed"
CORS is enabled for all origins in development mode. For production, configure in `backend/app.py`:
```python
allow_origins=["https://yourdomain.com"]
```

### API not responding
Ensure backend is running:
```bash
python backend/app.py
```

## Configuration

Edit `backend/config.py` to:
- Add custom detection patterns
- Adjust risk score thresholds
- Enable/disable AI features
- Change file size limits
- Modify compliance rules

## Project Structure Summary

```
sisaai/
├── backend/
│   ├── app.py (Main API server)
│   ├── config.py (Settings & patterns)
│   ├── models/schemas.py (Data models)
│   └── modules/ (Detection, analysis, risk engines)
├── frontend/
│   ├── index.html (Web interface)
│   └── static/ (CSS & JavaScript)
├── example_data/sample.log (Test log file)
└── README.md (Full documentation)
```

## Key Modules

1. **detection_engine.py**: Regex-based pattern matching
2. **log_analyzer.py**: Log-specific analysis
3. **risk_engine.py**: Risk scoring and assessment
4. **policy_engine.py**: Compliance checking
5. **ai_insights.py**: Intelligent recommendations

## Demo Scenarios

### Scenario 1: Database Leak
Input log with exposed credentials and database connections:
```log
2026-03-10 10:00:01 db_connection: postgresql://root:P@ssw0rd@db.com
2026-03-10 10:00:02 api_key=sk-prod-xyz789
```
Expected: CRITICAL risk, multiple findings, masking applied

### Scenario 2: Brute Force Attack
Input log with repeated failed login attempts:
```log
2026-03-10 10:01:01 Login failed for user: attacker@evil.com
2026-03-10 10:01:02 Login failed for user: attacker@evil.com
2026-03-10 10:01:03 Login failed for user: attacker@evil.com
```
Expected: Anomaly detected, brute force warning

### Scenario 3: Stack Trace Leak
Input log with stack traces:
```log
ERROR at UserService.java:156
  at proxy method (Unknown Source)
```
Expected: MEDIUM risk, debug info leakage detected

## Next Steps

1. ✅ Review example outputs
2. ✅ Test with your log files
3. ✅ Configure AI insights (optional)
4. ✅ Deploy to production
5. ✅ Integrate with your systems

## Performance Tips

- Large logs (>10MB): Use batch processing
- Real-time analysis: Use streaming endpoint
- Custom patterns: Add to config.py
- Caching: Implement Redis for repeated analyses

---

**Happy analyzing! 🔐**
