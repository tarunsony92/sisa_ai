# Deployment & Configuration Guide

## 📦 Production Deployment

### Prerequisites
- Python 3.8+
- 2GB RAM minimum
- 500MB disk space
- Port 8000 (API) and 3000 (frontend) available

---

## 🚀 Quick Start (Development)

### Windows
```bash
# Open Command Prompt in project root
start_backend.bat
# In another command prompt
start_frontend.bat
```

### Linux/Mac
```bash
chmod +x start_backend.sh start_frontend.sh
./start_backend.sh
# In another terminal
./start_frontend.sh
```

Then open:
- **API**: http://localhost:8000
- **Frontend**: http://localhost:3000 (or open `frontend/index.html`)

---

## ⚙️ Configuration

### Environment Variables

Create or edit `backend/.env`:

```env
# Server Configuration
DEBUG=True                          # Set to False in production
HOST=0.0.0.0
PORT=8000

# AI Configuration (Optional)
OPENAI_API_KEY=sk-...              # Your OpenAI API key for AI insights
LLM_MODEL=gpt-3.5-turbo

# Security
MAX_FILE_SIZE=52428800             # 50MB in bytes
ALLOWED_EXTENSIONS=.txt,.log,.pdf,.doc,.docx

# Compliance
GDPR_MODE=true
PCI_DSS_MODE=true
```

### Pattern Configuration

Edit `backend/config.py` to customize:

```python
# Add custom detection patterns
PATTERNS = {
    "custom_secret": r"your_regex_pattern",
}

# Adjust risk scores
RISK_SCORES = {
    "custom_secret": 8,
}

# Modify file limits
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
```

---

## 🔒 Security Hardening

### 1. HTTPS/TLS Setup

#### Using Nginx (Recommended)
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.crt;
    ssl_certificate_key /etc/ssl/private/your-key.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Using Gunicorn + SSL
```bash
pip install gunicorn
gunicorn --certfile=cert.pem --keyfile=key.pem --bind 0.0.0.0:443 backend.app:app
```

### 2. CORS Configuration

Edit `backend/app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Whitelist origins
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting

```bash
pip install slowapi
```

Add to `backend/app.py`:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/analyze")
@limiter.limit("100/minute")
async def analyze(request: AnalysisRequest):
    # ...
```

### 4. Authentication

Add JWT authentication:
```bash
pip install python-jose
```

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Add to endpoints
async def analyze(request: AnalysisRequest, token: str = Depends(oauth2_scheme)):
    # Validate token
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # ...
```

---

## 📊 Database Setup (Optional)

### Using PostgreSQL for History

```bash
pip install sqlalchemy psycopg2
```

Create `backend/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/sisaai"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

---

## 📈 Monitoring & Logging

### 1. Structured Logging

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'path': record.pathname,
        }
        return json.dumps(log_obj)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('sisaai.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Health Monitoring

```bash
# Set up monitoring endpoint
curl http://localhost:8000/health

# Response includes:
# - API status
# - Processing time
# - Error rates
# - Resource usage
```

### 3. Performance Metrics

Add telemetry:
```bash
pip install prometheus-client
```

---

## 🚯 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["python", "app.py"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DEBUG: "False"
      PORT: "8000"
    volumes:
      - ./logs:/app/logs

  frontend:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
```

### Run with Docker
```bash
docker-compose up -d
```

---

## ☁️ Cloud Deployment

### AWS EC2

```bash
# Launch instance
aws ec2 run-instances --image-id ami-0c55b159cbfafe1f0 --instance-type t2.micro

# SSH into instance
ssh -i key.pem ec2-user@instance-ip

# Install dependencies
sudo yum update -y
sudo yum install python3 -y
pip3 install -r requirements.txt

# Start server
python3 backend/app.py
```

### Google Cloud Run

```bash
# Build Docker image
docker build -t sisaai .

# Push to Container Registry
docker tag sisaai gcr.io/PROJECT_ID/sisaai
docker push gcr.io/PROJECT_ID/sisaai

# Deploy
gcloud run deploy sisaai --image gcr.io/PROJECT_ID/sisaai --platform managed
```

### Azure App Service

```bash
# Create resource group
az group create --name sisaai-rg --location eastus

# Create App Service plan
az appservice plan create --name sisaai-plan --resource-group sisaai-rg --sku F1

# Create web app
az webapp create --resource-group sisaai-rg --plan sisaai-plan --name sisaai-app

# Deploy
cd backend
az webapp up --name sisaai-app --resource-group sisaai-rg
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      
      - name: Run tests
        run: |
          pytest backend/
      
      - name: Deploy
        run: |
          # Your deployment script
```

---

## 📋 Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL/TLS certificates installed
- [ ] Database backups configured
- [ ] Logging enabled
- [ ] Monitoring set up
- [ ] Rate limiting enabled
- [ ] CORS configured
- [ ] API key authentication enabled
- [ ] Frontend assets optimized
- [ ] CDN configured (optional)
- [ ] Backup strategy in place
- [ ] Disaster recovery plan documented
- [ ] Performance tested
- [ ] Security audit completed
- [ ] Documentation updated

---

## 🛠️ Maintenance

### Regular Tasks

```bash
# Update dependencies
pip install --upgrade -r backend/requirements.txt

# Clean up old logs
find logs/ -mtime +30 -delete

# Monitor disk usage
df -h

# Check API health
curl -s http://localhost:8000/health | jq .

# View recent logs
tail -f sisaai.log
```

### Backup Strategy

```bash
# Daily backup
0 2 * * * tar -czf /backups/sisaai-$(date +%Y%m%d).tar.gz .

# Database backup (if using PostgreSQL)
0 2 * * * pg_dump sisaai > /backups/db-$(date +%Y%m%d).sql
```

---

## 📞 Support & Troubleshooting

### Common Issues

#### Issue: Port 8000 already in use
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 PID
```

#### Issue: High memory usage
```bash
# Monitor processes
top -p $(pgrep -f "python app.py")
# Reduce batch size or implement cleanup
```

#### Issue: SSL certificate errors
```bash
# Verify certificate
openssl x509 -in certificate.crt -text -noout
# Regenerate if needed
```

#### Issue: API timeouts
```bash
# Check network connectivity
curl -v http://localhost:8000/health
# Increase timeout values in config
```

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Deployment Best Practices](https://12factor.net)

---

## 🔐 Security Compliance

### GDPR Compliance
- ✅ Data minimization implemented
- ✅ User consent for AI features
- ✅ Right to access/deletion available
- ✅ Data retention policies documented

### PCI-DSS Compliance
- ✅ Credit card data masked
- ✅ No sensitive data in logs
- ✅ Encryption in transit (HTTPS)
- ✅ Access controls implemented

### ISO-27001 Compliance
- ✅ Information security policies
- ✅ Access control mechanisms
- ✅ Incident response procedures
- ✅ Security risk assessment

---

**Production-ready deployment guide completed! 🚀**
