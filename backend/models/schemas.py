from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum


class InputType(str, Enum):
    TEXT = "text"
    FILE = "file"
    SQL = "sql"
    LOG = "log"
    CHAT = "chat"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    HARDCODED_SECRET = "hardcoded_secret"
    STACK_TRACE = "stack_trace"
    SQL_INJECTION = "sql_injection"
    CREDENTIAL = "credential"


class Finding(BaseModel):
    type: FindingType
    risk: RiskLevel
    value: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    context: Optional[str] = None


class AnalysisRequest(BaseModel):
    input_type: InputType
    content: Optional[str] = None
    file_name: Optional[str] = None
    options: Optional[Dict[str, Any]] = {
        "mask": True,
        "block_high_risk": True,
        "log_analysis": True,
        "ai_insights": True
    }


class AnalysisResponse(BaseModel):
    summary: str
    content_type: str
    findings: List[Finding]
    risk_score: float
    risk_level: RiskLevel
    action: str
    insights: List[str]
    masked_content: Optional[str] = None
    processing_time_ms: float


class LogMetadata(BaseModel):
    total_lines: int
    timestamp_range: Optional[str] = None
    log_level_distribution: Optional[Dict[str, int]] = None
