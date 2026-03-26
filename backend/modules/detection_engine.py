import re
from typing import List, Tuple, Dict, Optional
from config import PATTERNS, RISK_SCORES
from models.schemas import Finding, FindingType, RiskLevel, RiskLevel as RiskLevelEnum


class DetectionEngine:
    """Regex-based pattern detection engine for sensitive data and security issues."""
    
    def __init__(self):
        self.patterns = PATTERNS
        self.risk_scores = RISK_SCORES
        self.compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Pre-compile regex patterns for better performance."""
        compiled = {}
        for name, pattern in self.patterns.items():
            try:
                compiled[name] = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            except re.error as e:
                print(f"Error compiling pattern {name}: {e}")
                compiled[name] = None
        return compiled
    
    def detect_in_text(self, content: str, line_offset: int = 0) -> List[Finding]:
        """
        Detect sensitive data and security issues in text content.
        
        Args:
            content: Text content to analyze
            line_offset: Starting line number
            
        Returns:
            List of findings
        """
        findings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=line_offset + 1):
            # Skip empty lines
            if not line.strip():
                continue
            
            for pattern_name, pattern in self.compiled_patterns.items():
                if pattern is None:
                    continue
                
                matches = pattern.finditer(line)
                for match in matches:
                    finding = self._create_finding(
                        pattern_name,
                        match,
                        line_num,
                        line
                    )
                    if finding:
                        findings.append(finding)
        
        return findings
    
    def _create_finding(self, pattern_name: str, match: re.Match, 
                       line_num: int, line: str) -> Optional[Finding]:
        """Create a Finding object from a regex match."""
        value = match.group(0)
        
        # Map pattern names to finding types
        type_mapping = {
            "email": FindingType.EMAIL,
            "phone": FindingType.PHONE,
            "api_key": FindingType.API_KEY,
            "password": FindingType.PASSWORD,
            "token": FindingType.TOKEN,
            "aws_key": FindingType.API_KEY,
            "private_key": FindingType.HARDCODED_SECRET,
            "jwt": FindingType.TOKEN,
            "credit_card": FindingType.CREDENTIAL,
            "ssn": FindingType.CREDENTIAL,
        }
        
        finding_type = type_mapping.get(pattern_name, FindingType.CREDENTIAL)
        risk_score = self.risk_scores.get(pattern_name, 5)
        risk_level = self._score_to_risk_level(risk_score)
        
        return Finding(
            type=finding_type,
            risk=risk_level,
            value=value if pattern_name in ["email", "phone"] else None,
            line=line_num,
            column=match.start() + 1,
            context=line[:100]  # First 100 chars as context
        )
    
    def _score_to_risk_level(self, score: int) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score >= 9:
            return RiskLevel.CRITICAL
        elif score >= 7:
            return RiskLevel.HIGH
        elif score >= 4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def mask_sensitive_content(self, content: str) -> str:
        """
        Mask sensitive data in content.
        
        Args:
            content: Text content to mask
            
        Returns:
            Masked content
        """
        masked = content
        
        # Mask emails
        masked = re.sub(
            self.patterns["email"],
            "[***@***.***]",
            masked,
            flags=re.IGNORECASE
        )
        
        # Mask phone numbers
        masked = re.sub(
            self.patterns["phone"],
            "[***-***-****]",
            masked,
            flags=re.IGNORECASE
        )
        
        # Mask API keys
        masked = re.sub(
            self.patterns["api_key"],
            r"api_key: [***MASKED***]",
            masked,
            flags=re.IGNORECASE
        )
        
        # Mask passwords
        masked = re.sub(
            self.patterns["password"],
            r"password: [***MASKED***]",
            masked,
            flags=re.IGNORECASE
        )
        
        # Mask tokens
        masked = re.sub(
            self.patterns["token"],
            r"token: [***MASKED***]",
            masked,
            flags=re.IGNORECASE
        )
        
        # Mask credit cards
        masked = re.sub(
            self.patterns["credit_card"],
            "[****-****-****-****]",
            masked
        )
        
        # Mask SSN
        masked = re.sub(
            self.patterns["ssn"],
            "[***-**-****]",
            masked
        )
        
        return masked
    
    def detect_sql_injection(self, content: str) -> List[Finding]:
        """Detect potential SQL injection patterns."""
        findings = []
        sql_patterns = [
            (r"(?:union|select|insert|update|delete|drop|create|alter)[\s\(]+", "SQL Injection"),
            (r"(?:or|and)\s+1\s*=\s*1", "SQL Logic"),
            (r"(?:--|#|/\*)", "SQL Comment"),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, start=1):
            for pattern, name in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(Finding(
                        type=FindingType.SQL_INJECTION,
                        risk=RiskLevel.HIGH,
                        line=line_num,
                        column=1,
                        context=line[:100]
                    ))
        
        return findings
    
    def detect_stack_traces(self, content: str) -> List[Finding]:
        """Detect stack traces which leak system information."""
        findings = []
        stack_trace_pattern = r"(?:at|File|line)\s+[a-zA-Z0-9._\/]+\.(?:java|py|js|ts):\d+"
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, start=1):
            if re.search(stack_trace_pattern, line, re.IGNORECASE):
                findings.append(Finding(
                    type=FindingType.STACK_TRACE,
                    risk=RiskLevel.MEDIUM,
                    line=line_num,
                    column=1,
                    context=line[:100]
                ))
        
        return findings
