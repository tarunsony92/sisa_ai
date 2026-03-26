from typing import List, Dict, Tuple
from models.schemas import Finding, RiskLevel
from config import RISK_THRESHOLDS


class RiskEngine:
    """Risk assessment and scoring engine."""
    
    def __init__(self):
        self.risk_thresholds = RISK_THRESHOLDS
    
    def calculate_risk_score(self, findings: List[Finding]) -> Tuple[float, RiskLevel]:
        """
        Calculate overall risk score from findings.
        
        Args:
            findings: List of security findings
            
        Returns:
            Tuple of (risk_score, risk_level)
        """
        if not findings:
            return 0.0, RiskLevel.LOW
        
        # Calculate weighted score
        score = 0.0
        weights = {
            RiskLevel.CRITICAL: 3.0,
            RiskLevel.HIGH: 2.0,
            RiskLevel.MEDIUM: 1.0,
            RiskLevel.LOW: 0.5
        }
        
        for finding in findings:
            score += weights.get(finding.risk, 0)
        
        # Normalize score (0-10 scale)
        max_score = len(findings) * 3.0
        if max_score > 0:
            normalized_score = min(10.0, (score / max_score) * 10.0)
        else:
            normalized_score = 0.0
        
        risk_level = self._score_to_risk_level(normalized_score)
        
        return round(normalized_score, 2), risk_level
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score >= self.risk_thresholds["critical"]:
            return RiskLevel.CRITICAL
        elif score >= self.risk_thresholds["high"]:
            return RiskLevel.HIGH
        elif score >= self.risk_thresholds["medium"]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def get_risk_breakdown(self, findings: List[Finding]) -> Dict[str, int]:
        """Get breakdown of findings by risk level."""
        breakdown = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for finding in findings:
            breakdown[finding.risk.value] += 1
        
        return breakdown
    
    def identify_critical_threats(self, findings: List[Finding]) -> List[Finding]:
        """Identify critical threats that need immediate action."""
        critical = []
        
        critical_types = ["password", "api_key", "hardcoded_secret", "token"]
        
        for finding in findings:
            if finding.risk == RiskLevel.CRITICAL or finding.type.value in critical_types:
                critical.append(finding)
        
        return sorted(critical, key=lambda f: -(ord(f.risk.value)), reverse=False)
    
    def should_block_content(self, findings: List[Finding]) -> bool:
        """
        Determine if content should be blocked based on risk.
        
        Returns:
            True if content should be blocked
        """
        critical_findings = [f for f in findings if f.risk == RiskLevel.CRITICAL]
        return len(critical_findings) > 0
    
    def get_remediation_actions(self, findings: List[Finding]) -> List[str]:
        """
        Get recommended remediation actions.
        
        Args:
            findings: List of security findings
            
        Returns:
            List of recommended actions
        """
        actions = []
        action_set = set()
        
        for finding in findings:
            if finding.type.value == "password":
                action_set.add("Rotate all exposed passwords immediately")
            elif finding.type.value == "api_key":
                action_set.add("Revoke and regenerate exposed API keys")
            elif finding.type.value == "token":
                action_set.add("Revoke authentication tokens and log out affected users")
            elif finding.type.value == "hardcoded_secret":
                action_set.add("Remove hardcoded secrets and implement secret management")
            elif finding.type.value == "stack_trace":
                action_set.add("Configure logging to exclude stack traces in production")
            elif finding.type.value == "sql_injection":
                action_set.add("Implement parameterized queries and input validation")
            elif finding.type.value == "email":
                action_set.add("Review data retention policies and access controls")
            elif finding.type.value == "credential":
                action_set.add("Audit who has access to credentials")
        
        # Add general recommendations
        high_risk_count = len([f for f in findings if f.risk == RiskLevel.HIGH])
        if high_risk_count > 5:
            action_set.add("Conduct full security audit of logging infrastructure")
        
        if len(findings) > 20:
            action_set.add("Implement centralized secret management system")
            action_set.add("Enable log redaction for sensitive data patterns")
        
        return sorted(list(action_set))
    
    def calculate_mttr(self, findings: List[Finding]) -> Dict[str, int]:
        """
        Estimate Mean Time To Remediate (MTTR) in hours.
        
        Args:
            findings: List of security findings
            
        Returns:
            Dictionary with MTTR estimates by severity
        """
        estimate = {
            "critical": 0,  # Minutes for critical
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        mttr_weights = {
            "password": {"critical": 60, "high": 120, "medium": 240, "low": 480},
            "api_key": {"critical": 30, "high": 60, "medium": 120, "low": 240},
            "token": {"critical": 30, "high": 60, "medium": 120, "low": 240},
            "hardcoded_secret": {"critical": 120, "high": 240, "medium": 480, "low": 960},
            "stack_trace": {"critical": 60, "high": 120, "medium": 240, "low": 480},
            "sql_injection": {"critical": 120, "high": 240, "medium": 480, "low": 960},
        }
        
        for finding in findings:
            weights = mttr_weights.get(finding.type.value, 
                                      {"critical": 60, "high": 120, "medium": 240, "low": 480})
            estimate[finding.risk.value] += weights.get(finding.risk.value, 60)
        
        # Convert to hours
        return {
            k: max(1, round(v / 60)) for k, v in estimate.items()
        }
