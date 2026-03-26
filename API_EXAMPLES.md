# API Curl Examples

## Health Check
```bash
curl http://localhost:8000/health
```

---

## Text Analysis Examples

### Example 1: Detect Passwords
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "User login: admin Password: super_secret_123"
  }'
```

### Example 2: Detect API Keys
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "API Key: sk-prod-8c7f2eXkR9qL4mN7hJpQvYw2sXyZ3bE8"
  }'
```

### Example 3: Detect Emails & Phones
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "Contact: john@example.com or (555) 123-4567"
  }'
```

### Example 4: Detect Multiple Issues
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "Admin: admin@company.com, Password: P@ssw0rd123!, API: sk-prod-xyz789"
  }'
```

### Example 5: With Options
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "password=admin123",
    "options": {
      "mask": true,
      "block_high_risk": true,
      "log_analysis": true,
      "ai_insights": true
    }
  }'
```

---

## Log Analysis Examples

### Example 1: Log Content
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "log",
    "content": "2026-03-10 10:00:01 INFO User login: admin@company.com\n2026-03-10 10:00:02 ERROR password=secret123\n2026-03-10 10:00:03 WARNING api_key=sk-prod-xyz"
  }'
```

### Example 2: Log with Errors
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "log",
    "content": "2026-03-10 10:00:01 ERROR NullPointerException at service.java:45\n  at proxy method (Unknown Source)\n  at main thread (Unknown Source)"
  }'
```

### Example 3: Brute Force Detection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "log",
    "content": "2026-03-10 10:01:01 ERROR Login failed from 192.168.1.100\n2026-03-10 10:01:02 ERROR Login failed from 192.168.1.100\n2026-03-10 10:01:03 ERROR Login failed from 192.168.1.100\n2026-03-10 10:01:04 ERROR Login failed from 192.168.1.100\n2026-03-10 10:01:05 ERROR Login failed from 192.168.1.100"
  }'
```

---

## SQL Analysis Examples

### Example 1: SQL Injection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "sql",
    "content": "SELECT * FROM users WHERE id = 1 OR 1=1; DROP TABLE users;"
  }'
```

### Example 2: Union-based Injection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "sql",
    "content": "SELECT id, name FROM users UNION SELECT username, password FROM admins;"
  }'
```

### Example 3: Time-based Injection
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "sql",
    "content": "SELECT * FROM users WHERE id = 1 AND SLEEP(5);"
  }'
```

---

## File Upload Examples

### Example 1: Upload TXT File
```bash
curl -X POST http://localhost:8000/analyze/file \
  -F "file=@test.txt"
```

### Example 2: Upload LOG File
```bash
curl -X POST http://localhost:8000/analyze/file \
  -F "file=@application.log"
```

### Example 3: Upload Sample
```bash
curl -X POST http://localhost:8000/analyze/file \
  -F "file=@example_data/sample.log"
```

---

## Batch Analysis Examples

### Example 1: Batch with Multiple Items
```bash
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '[
    {
      "input_type": "text",
      "content": "password=secret123"
    },
    {
      "input_type": "text",
      "content": "api_key=sk-prod-xyz"
    },
    {
      "input_type": "text",
      "content": "admin@company.com"
    }
  ]'
```

### Example 2: Batch Logs
```bash
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '[
    {
      "input_type": "log",
      "content": "2026-03-10 10:00:01 password=secret"
    },
    {
      "input_type": "log",
      "content": "2026-03-10 10:00:02 ERROR stack trace here"
    }
  ]'
```

---

## Metadata Endpoints

### Get Finding Types
```bash
curl http://localhost:8000/findings/types
```

Response:
```json
{
  "types": [
    "email",
    "phone",
    "api_key",
    "password",
    "token",
    "hardcoded_secret",
    "stack_trace",
    "sql_injection",
    "credential"
  ]
}
```

### Get Risk Levels
```bash
curl http://localhost:8000/risk/levels
```

Response:
```json
{
  "levels": ["low", "medium", "high", "critical"],
  "definitions": {
    "low": "Minimal security impact",
    "medium": "Moderate security concern",
    "high": "Significant security risk",
    "critical": "Immediate action required"
  }
}
```

### Get Compliance Report
```bash
curl http://localhost:8000/compliance/report
```

---

## Advanced Examples

### Example 1: Complex Log Analysis with Masking
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "log",
    "content": "2026-03-10 10:00:01 User: admin@company.com Password: admin123 Token: eyJhbGc...",
    "options": {
      "mask": true,
      "block_high_risk": false,
      "log_analysis": true,
      "ai_insights": true
    }
  }'
```

### Example 2: High-Risk Content Blocking
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "database_password=prod123 api_key=sk-prod-xyz credit_card=4532-1488-0343-6467",
    "options": {
      "block_high_risk": true
    }
  }'
```

### Example 3: SQL with Credentials
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "sql",
    "content": "CONNECT TO database AS root PASSWORD \"secret123\"; SELECT * FROM users WHERE id = 1 OR 1=1;"
  }'
```

---

## Response Format Examples

### Successful Analysis
```json
{
  "summary": "Content contains sensitive credentials",
  "content_type": "text",
  "findings": [
    {
      "type": "password",
      "risk": "critical",
      "line": 1,
      "value": null,
      "column": 25,
      "context": "password=admin123"
    }
  ],
  "risk_score": 10.0,
  "risk_level": "critical",
  "action": "blocked",
  "insights": [
    "Password found in plain text",
    "Implement credential management system"
  ],
  "masked_content": "password=[***MASKED***]",
  "processing_time_ms": 45.23
}
```

### Error Response
```json
{
  "error": "Content cannot be empty",
  "timestamp": "2026-03-26T14:32:15.123456"
}
```

---

## Testing with PowerShell

### PowerShell Example 1
```powershell
$body = @{
    input_type = "text"
    content = "password=secret123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/analyze" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### PowerShell Example 2
```powershell
$file = "C:\path\to\file.log"
$form = @{ file = Get-Item $file }

Invoke-WebRequest -Uri "http://localhost:8000/analyze/file" `
  -Method POST `
  -Form $form
```

---

## Testing with Python

### Python Example 1
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "input_type": "text",
        "content": "password=admin123"
    }
)

print(response.json())
```

### Python Example 2
```python
import requests

with open("sample.log", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/analyze/file",
        files=files
    )

print(response.json())
```

---

## Common curl Options

```bash
# Save response to file
curl ... -o output.json

# Include response headers
curl ... -i

# Show detailed request/response
curl ... -v

# Set authentication
curl ... -H "Authorization: Bearer token"

# Set timeout
curl ... --max-time 30

# Follow redirects
curl ... -L

# Pretty print JSON (requires jq)
curl ... | jq .
```

---

**Ready to test? Start the backend and run these examples! 🚀**
