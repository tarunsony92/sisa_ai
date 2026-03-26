from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import os
from datetime import datetime
from typing import Optional
import mimetypes

from config import API_TITLE, API_VERSION, DEBUG, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from models.schemas import (
    AnalysisRequest, AnalysisResponse, InputType, RiskLevel, Finding
)
from modules.detection_engine import DetectionEngine
from modules.log_analyzer import LogAnalyzer
from modules.risk_engine import RiskEngine
from modules.policy_engine import PolicyEngine
from modules.ai_insights import AIInsights


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="Advanced AI-powered security analysis platform"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
detection_engine = DetectionEngine()
log_analyzer = LogAnalyzer()
risk_engine = RiskEngine()
policy_engine = PolicyEngine()
ai_insights = AIInsights()


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "status": "operational",
        "service": API_TITLE,
        "version": API_VERSION,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """
    Analyze input content for security threats.
    
    Supports:
    - Text input (raw text)
    - File analysis (TXT, LOG)
    - SQL code analysis
    - Chat logs
    """
    start_time = time.time()
    
    try:
        # Validate input
        if not request.content or not request.content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        
        # Process based on input type
        if request.input_type == InputType.LOG:
            findings, error = await _analyze_log(request.content)
        elif request.input_type == InputType.TEXT:
            findings, error = await _analyze_text(request.content)
        elif request.input_type == InputType.SQL:
            findings, error = await _analyze_sql(request.content)
        else:
            findings, error = await _analyze_text(request.content)
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        # Calculate risk score
        risk_score, risk_level = risk_engine.calculate_risk_score(findings)
        
        # Generate summary
        summary = ai_insights.generate_summary(findings)
        
        # Generate AI insights
        insights = ai_insights.generate_insights(
            request.content[:1000],
            findings,
            request.input_type.value
        )
        
        # Determine action
        action = "blocked" if risk_engine.should_block_content(findings) else "passed"
        if request.options and request.options.get("mask"):
            action = "masked"
        
        # Mask content if requested
        masked_content = None
        if request.options and request.options.get("mask"):
            masked_content = detection_engine.mask_sensitive_content(request.content)
        
        # Build response
        response = AnalysisResponse(
            summary=summary,
            content_type=request.input_type.value,
            findings=findings,
            risk_score=risk_score,
            risk_level=risk_level,
            action=action,
            insights=insights,
            masked_content=masked_content,
            processing_time_ms=round((time.time() - start_time) * 1000, 2)
        )
        
        # Apply policies
        response = policy_engine.apply_policies(response, findings, request.options)
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 2)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/analyze/file")
async def analyze_file(file: UploadFile = File(...)):
    """
    Analyze uploaded file.
    
    Supported formats:
    - .txt
    - .log
    - .pdf (converted to text)
    - .doc/.docx (converted to text)
    """
    start_time = time.time()
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed: {ALLOWED_EXTENSIONS}"
            )
        
        # Read file content
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {MAX_FILE_SIZE} bytes"
            )
        
        # Decode content
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            text_content = content.decode('latin-1')
        
        # Determine analysis type
        if file_ext in [".log"]:
            input_type = InputType.LOG
        else:
            input_type = InputType.TEXT
        
        # Create analysis request
        analysis_request = AnalysisRequest(
            input_type=input_type,
            content=text_content,
            file_name=file.filename
        )
        
        # Analyze
        return await analyze(analysis_request)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File analysis failed: {str(e)}"
        )


@app.post("/analyze/batch")
async def analyze_batch(requests: list[AnalysisRequest]):
    """
    Analyze multiple requests in batch.
    """
    results = []
    
    for request in requests:
        try:
            result = await analyze(request)
            results.append(result)
        except HTTPException as e:
            results.append({
                "error": e.detail,
                "input_type": request.input_type
            })
    
    return {
        "total": len(requests),
        "successful": len([r for r in results if "error" not in r]),
        "results": results
    }


@app.get("/findings/types")
def get_finding_types():
    """Get list of supported finding types."""
    return {
        "types": [f.value for f in FindingType]
    }


@app.get("/risk/levels")
def get_risk_levels():
    """Get risk level definitions."""
    return {
        "levels": [r.value for r in RiskLevel],
        "definitions": {
            "low": "Minimal security impact",
            "medium": "Moderate security concern",
            "high": "Significant security risk",
            "critical": "Immediate action required"
        }
    }


@app.get("/compliance/report")
def get_compliance_report(findings: Optional[str] = None):
    """Get compliance status report."""
    # This would be enhanced with actual data
    return {
        "frameworks": [
            "GDPR",
            "PCI-DSS",
            "HIPAA",
            "SOX",
            "ISO-27001"
        ],
        "status": "compliant"
    }


# Helper functions
async def _analyze_text(content: str) -> tuple:
    """Analyze plain text input."""
    try:
        findings = detection_engine.detect_in_text(content)
        return findings, None
    except Exception as e:
        return [], str(e)


async def _analyze_log(content: str) -> tuple:
    """Analyze log file."""
    try:
        analysis = log_analyzer.analyze_log(content)
        findings = analysis["findings"]
        return findings, None
    except Exception as e:
        return [], str(e)


async def _analyze_sql(content: str) -> tuple:
    """Analyze SQL code."""
    try:
        findings = []
        findings.extend(detection_engine.detect_in_text(content))
        findings.extend(detection_engine.detect_sql_injection(content))
        return findings, None
    except Exception as e:
        return [], str(e)


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG
    )
