# Testing Guide

## Unit Testing Setup

### Python Test Requirements
```bash
pip install pytest pytest-cov
```

## Testing the Application

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-26T14:32:15.123456"
}
```

---

## 2. Detection Engine Tests

### Test: Email Detection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "Contact me at admin@company.com"
  }'
```

**Expected:** 1 finding with type "email", risk "low"

### Test: Password Detection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "password=admin123"
  }'
```

**Expected:** 1 finding with type "password", risk "critical"

### Test: API Key Detection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "api_key = sk-prod-xyz789abc123def456ghij"
  }'
```

**Expected:** 1 finding with type "api_key", risk "high"

### Test: Credit Card Detection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "CC: 4532-1488-0343-6467"
  }'
```

**Expected:** 1 finding with type detected, risk "high"

---

## 3. Log Analyzer Tests

### Test: Log File Upload
```bash
curl -X POST http://localhost:8000/analyze/file \
  -F "file=@example_data/sample.log"
```

**Expected:** Multiple findings from the sample log file

### Test: Brute Force Detection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "log",
    "content": "2026-03-10 10:01:01 Login failed\n2026-03-10 10:01:02 Login failed\n2026-03-10 10:01:03 Login failed\n2026-03-10 10:01:04 Login failed\n2026-03-10 10:01:05 Login failed"
  }'
```

**Expected:** Anomaly detected for repeated failures

### Test: Stack Trace Detection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "log",
    "content": "ERROR at UserService.java:156\n  at proxy method (Unknown Source)"
  }'
```

**Expected:** Finding with type "stack_trace", risk "medium"

---

## 4. Risk Engine Tests

### Test: Risk Scoring - Low Risk
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "admin@company.com"
  }'
```

**Expected:** risk_score < 3, risk_level "low"

### Test: Risk Scoring - High Risk
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "password=secret123\napi_key=sk-prod-xyz\napikey: sk-another-key"
  }'
```

**Expected:** risk_score >= 7, risk_level "high"

### Test: Risk Scoring - Critical
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "password=admin123\npassword=root123\npassword=secret456\napi_key=sk-prod-xyz\napi_key=sk-backup-ijk"
  }'
```

**Expected:** risk_score >= 9, risk_level "critical"

---

## 5. Policy Engine Tests

### Test: Data Masking
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "admin@company.com password=secret123",
    "options": {"mask": true}
  }'
```

**Expected:** masked_content should show [***@***.***] and [***MASKED***]

### Test: Blocking High Risk
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "password=critical_secret",
    "options": {"block_high_risk": true}
  }'
```

**Expected:** action "blocked" for critical findings

---

## 6. SQL Injection Detection

### Test: Basic SQL Injection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "sql",
    "content": "SELECT * FROM users WHERE id = 1 OR 1=1;"
  }'
```

**Expected:** Finding with type "sql_injection", risk "high"

### Test: Union-Based Injection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "sql",
    "content": "SELECT * FROM users UNION SELECT * FROM admins;"
  }'
```

**Expected:** SQL injection finding detected

---

## 7. Batch Processing Tests

### Batch Analysis
```bash
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '[
    {
      "input_type": "text",
      "content": "password=secret"
    },
    {
      "input_type": "text",
      "content": "api_key=sk-prod-xyz"
    }
  ]'
```

**Expected:** Array of 2 analysis results

---

## 8. File Upload Tests

### Test: TXT File
```bash
echo "password=admin123" > test.txt
curl -X POST http://localhost:8000/analyze/file \
  -F "file=@test.txt"
```

**Expected:** Successful analysis with password finding

### Test: Large File (>50MB)
```bash
dd if=/dev/zero bs=1M count=60 of=large_file.txt
curl -X POST http://localhost:8000/analyze/file \
  -F "file=@large_file.txt"
```

**Expected:** 413 Payload Too Large error

### Test: Invalid File Type
```bash
curl -X POST http://localhost:8000/analyze/file \
  -F "file=@script.exe"
```

**Expected:** 400 Bad Request, unsupported file type

---

## 9. API Metadata Tests

### Get Finding Types
```bash
curl http://localhost:8000/findings/types
```

**Expected:** JSON array of supported finding types

### Get Risk Levels
```bash
curl http://localhost:8000/risk/levels
```

**Expected:** Risk level definitions and scoring ranges

### Compliance Report
```bash
curl http://localhost:8000/compliance/report
```

**Expected:** List of supported compliance frameworks

---

## 10. Performance Tests

### Speed Test - Small Content
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "password=test"
  }' | grep processing_time_ms
```

**Expected:** processing_time_ms < 100ms

### Speed Test - Large Content
```bash
# Create a 1MB log file and analyze
python -c "print('\n'.join(['2026-03-10 10:00:0' + str(i % 10) + ' (INFO) entry' for i in range(10000)]))" > large_log.log

curl -X POST http://localhost:8000/analyze/file \
  -F "file=@large_log.log" | grep processing_time_ms
```

**Expected:** processing_time_ms < 500ms for 1MB file

---

## Frontend Testing Scenarios

### Scenario 1: Basic Text Analysis
1. Open frontend/index.html
2. Paste code: `password=admin123`
3. Click Analyze
4. Verify findings displayed
5. Check masking option works

### Scenario 2: File Upload
1. Navigate to "File Upload" tab
2. Drag `example_data/sample.log` into upload area
3. Click "Upload & Analyze"
4. Verify results display
5. Check log analysis details

### Scenario 3: Log Analysis
1. Paste multiline log content
2. Select "Log File" type
3. Analyze
4. Verify log metadata extraction
5. Check anomaly detection

### Scenario 4: Risk Assessment
1. Paste content with multiple findings
2. Verify risk score calculation
3. Check risk level badge
4. Review recommendations

### Scenario 5: Compliance Check
1. Analyze file with credit cards
2. Check PCI-DSS compliance status
3. Analyze with emails
4. Check GDPR compliance status

---

## Automated Testing

### Create test_suite.py

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✓ Health check passed")

def test_password_detection():
    payload = {
        "input_type": "text",
        "content": "password=admin123"
    }
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["findings"]) > 0
    assert data["findings"][0]["type"] == "password"
    print("✓ Password detection passed")

def test_api_key_detection():
    payload = {
        "input_type": "text",
        "content": "api_key=sk-prod-xyz789"
    }
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["findings"]) > 0
    print("✓ API key detection passed")

def test_masking():
    payload = {
        "input_type": "text",
        "content": "admin@company.com",
        "options": {"mask": true}
    }
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["masked_content"] is not None
    assert "***@***.*" in data["masked_content"] or "[***@***.***]" in data["masked_content"]
    print("✓ Masking test passed")

if __name__ == "__main__":
    test_health()
    test_password_detection()
    test_api_key_detection()
    test_masking()
    print("\nAll tests passed! ✓")
```

### Run tests:
```bash
cd backend
python ../test_suite.py
```

---

## Performance Benchmarks

| Test | Expected | Your Result |
|------|----------|-------------|
| Health check | <50ms | _____ |
| Small text (10 bytes) | <100ms | _____ |
| Medium text (1KB) | <150ms | _____ |
| Large log (1MB) | <500ms | _____ |
| Batch (10 items) | <1000ms | _____ |

---

## Common Issues & Solutions

### Issue: "Connection refused"
**Solution:** Ensure backend is running on port 8000

### Issue: "CORS error"
**Solution:** CORS is enabled. If error persists, check browser console for details

### Issue: "File upload fails"
**Solution:** Check file size (max 50MB) and format (.txt, .log, .pdf, .doc, .docx)

### Issue: "No findings detected"
**Solution:** Content might not match patterns. Check pattern definitions in config.py

### Issue: "Slow performance"
**Solution:** Check for large files, consider batch processing for multiple items

---

## Checklist

- [ ] Health check passes
- [ ] Email detection works
- [ ] Password detection works
- [ ] API key detection works
- [ ] Credit card detection works
- [ ] SQL injection detection works
- [ ] Stack trace detection works
- [ ] Log file analysis works
- [ ] Risk scoring works
- [ ] Masking works
- [ ] File uploads work
- [ ] Batch processing works
- [ ] Frontend displays results
- [ ] Performance is acceptable

---

**Happy Testing! 🧪**
