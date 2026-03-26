import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_TITLE = "AI Secure Data Intelligence Platform"
API_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# AI/LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
AI_ENABLED = bool(OPENAI_API_KEY)

# Detection Patterns
PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone": r"(?:\+1|\b)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b",
    "api_key": r"(?:api[_-]?key|apikey|api_secret|secret_key)['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9\-_]{20,})['\"]?",
    "password": r"(?:password|passwd|pwd)['\"]?\s*[:=]\s*['\"]?([^'\"\s]+)['\"]?",
    "token": r"(?:token|access_token|refresh_token)['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9\-_.]{20,})['\"]?",
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "private_key": r"-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----",
    "jwt": r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
    "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
}

# Risk Configuration
RISK_SCORES = {
    "email": 2,
    "phone": 2,
    "api_key": 8,
    "password": 10,
    "token": 8,
    "hardcoded_secret": 9,
    "stack_trace": 5,
    "sql_injection": 9,
    "credential": 9,
}

RISK_THRESHOLDS = {
    "low": 3,
    "medium": 6,
    "high": 8,
    "critical": 10,
}

# File Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".txt", ".log", ".pdf", ".doc", ".docx"}

# Log Analysis Configuration
LOG_LEVEL_PATTERNS = {
    "DEBUG": r"DEBUG",
    "INFO": r"INFO",
    "WARNING": r"WARN|WARNING",
    "ERROR": r"ERROR|ERR",
    "CRITICAL": r"CRITICAL|FATAL",
}

ANOMALY_DETECTORS = {
    "repeated_failures": r"failed|failure|error",
    "suspicious_ip": r"(?:\d{1,3}\.){3}\d{1,3}",
    "debug_mode": r"debug|verbose|trace",
}
