from typing import List, Dict, Optional
from models.schemas import Finding, RiskLevel, AnalysisRequest, AnalysisResponse


class PolicyEngine:
    """Policy enforcement engine for data handling and compliance."""
    
    def __init__(self):
        self.policies = self._initialize_policies()
    
    def _initialize_policies(self) -> Dict:
        """Initialize default security policies."""
        return {
            "data_masking": {
                "enabled": True,
                "patterns": ["password", "api_key", "token", "credential", "ssn", "credit_card"]
            },
            "block_rules": {
                "threshold": RiskLevel.CRITICAL,
                "enabled": True
            },
            "audit_logging": {
                "enabled": True,
                "log_sensitive_findings": False
            },
            "data_retention": {
                "retention_days": 30,
                "encrypt_at_rest": True
            },
            "access_control": {
                "require_authentication": True,
                "rate_limit": "100_per_minute"
            }
        }
    
    def apply_policies(self, response: AnalysisResponse, 
                      findings: List[Finding],
                      options: Optional[Dict] = None) -> AnalysisResponse:
        """
        Apply policies to analysis response.
        
        Args:
            response: Analysis response to process
            findings: List of security findings
            options: Optional policy overrides
            
        Returns:
            Modified analysis response
        """
        # Apply masking policy
        if self._should_mask(options):
            response = self._apply_masking(response)
        
        # Apply blocking policy
        if self._should_block(findings, options):
            response.action = "blocked"
        
        # Add policy metadata
        response = self._add_policy_metadata(response)
        
        return response
    
    def _should_mask(self, options: Optional[Dict] = None) -> bool:
        """Determine if data masking should be applied."""
        if options and "mask" in options:
            return options["mask"]
        return self.policies["data_masking"]["enabled"]
    
    def _should_block(self, findings: List[Finding], 
                     options: Optional[Dict] = None) -> bool:
        """Determine if content should be blocked."""
        if options and "block_high_risk" in options:
            if not options["block_high_risk"]:
                return False
        
        if not self.policies["block_rules"]["enabled"]:
            return False
        
        threshold = self.policies["block_rules"]["threshold"]
        
        for finding in findings:
            if finding.risk == RiskLevel.CRITICAL:
                return True
            if finding.risk == threshold:
                return True
        
        return False
    
    def _apply_masking(self, response: AnalysisResponse) -> AnalysisResponse:
        """Apply data masking to findings."""
        for finding in response.findings:
            if finding.type.value in self.policies["data_masking"]["patterns"]:
                finding.value = None  # Clear sensitive values
        
        return response
    
    def _add_policy_metadata(self, response: AnalysisResponse) -> AnalysisResponse:
        """Add policy compliance metadata to response."""
        # This would contain compliance information
        compliance = {
            "gdpr_compliant": not any(f.type.value == "email" for f in response.findings),
            "pci_compliant": not any(f.type.value == "credit_card" for f in response.findings),
            "hipaa_compliant": not any(f.type.value in ["ssn", "credential"] for f in response.findings)
        }
        
        return response
    
    def enforce_retention_policy(self, analysis_record: Dict) -> bool:
        """
        Check if record should be retained based on policy.
        
        Args:
            analysis_record: Analysis record to check
            
        Returns:
            True if should be retained
        """
        retention_days = self.policies["data_retention"]["retention_days"]
        # Implementation would check record age
        return True
    
    def check_rate_limit(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limit.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if allowed
        """
        # Implementation would track requests per client
        return True
    
    def get_compliance_report(self, findings: List[Finding]) -> Dict[str, bool]:
        """
        Generate compliance report for findings.
        
        Args:
            findings: List of security findings
            
        Returns:
            Dictionary of compliance status
        """
        return {
            "gdpr": self._check_gdpr_compliance(findings),
            "pci_dss": self._check_pci_compliance(findings),
            "hipaa": self._check_hipaa_compliance(findings),
            "sox": self._check_sox_compliance(findings),
            "iso27001": self._check_iso27001_compliance(findings)
        }
    
    def _check_gdpr_compliance(self, findings: List[Finding]) -> bool:
        """Check GDPR compliance (focuses on personal data)."""
        risky_types = ["email", "phone", "credential"]
        critical_findings = [f for f in findings 
                            if f.type.value in risky_types and 
                            f.risk == RiskLevel.CRITICAL]
        return len(critical_findings) == 0
    
    def _check_pci_compliance(self, findings: List[Finding]) -> bool:
        """Check PCI DSS compliance (payment card data)."""
        pci_risky = ["credit_card", "credential", "api_key"]
        critical_findings = [f for f in findings 
                            if f.type.value in pci_risky and 
                            f.risk in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        return len(critical_findings) == 0
    
    def _check_hipaa_compliance(self, findings: List[Finding]) -> bool:
        """Check HIPAA compliance (health data)."""
        hipaa_risky = ["ssn", "credential", "email"]
        critical_findings = [f for f in findings 
                            if f.type.value in hipaa_risky and 
                            f.risk == RiskLevel.CRITICAL]
        return len(critical_findings) == 0
    
    def _check_sox_compliance(self, findings: List[Finding]) -> bool:
        """Check SOX compliance (audit trails)."""
        # Focus on stack traces and error logs
        sox_risky = ["stack_trace", "api_key", "password"]
        critical_findings = [f for f in findings 
                            if f.type.value in sox_risky]
        return len(critical_findings) < 5
    
    def _check_iso27001_compliance(self, findings: List[Finding]) -> bool:
        """Check ISO 27001 compliance (information security)."""
        critical_findings = [f for f in findings if f.risk == RiskLevel.CRITICAL]
        return len(critical_findings) == 0
