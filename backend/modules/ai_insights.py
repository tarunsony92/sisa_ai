from typing import List, Dict, Optional
import json
from models.schemas import Finding, RiskLevel
from config import AI_ENABLED, OPENAI_API_KEY, LLM_MODEL


class AIInsights:
    """AI-powered insights generator using LLM."""
    
    def __init__(self):
        self.ai_enabled = AI_ENABLED
        if self.ai_enabled:
            try:
                import openai
                openai.api_key = OPENAI_API_KEY
                self.client = openai
            except ImportError:
                self.ai_enabled = False
    
    def generate_insights(self, content: str, findings: List[Finding], 
                         analysis_type: str = "log") -> List[str]:
        """
        Generate AI-powered insights based on findings.
        
        Args:
            content: Original content analyzed
            findings: List of security findings
            analysis_type: Type of analysis (log, text, file)
            
        Returns:
            List of insight strings
        """
        # If AI is not enabled, fall back to rule-based insights
        if not self.ai_enabled:
            return self._generate_rule_based_insights(findings, analysis_type)
        
        return self._generate_ai_insights(content, findings, analysis_type)
    
    def _generate_rule_based_insights(self, findings: List[Finding], 
                                      analysis_type: str) -> List[str]:
        """Generate insights using rule-based approach."""
        insights = []
        
        # Group findings by type
        finding_types = {}
        for finding in findings:
            if finding.type not in finding_types:
                finding_types[finding.type] = 0
            finding_types[finding.type] += 1
        
        # Generate insights based on findings
        if "password" in finding_types:
            insights.append("Sensitive credentials exposed in plain text")
        
        if "api_key" in finding_types:
            insights.append("API keys found in logs - rotate immediately")
        
        if "email" in finding_types and finding_types["email"] > 3:
            insights.append("Multiple email addresses exposed - potential data leak")
        
        if "stack_trace" in finding_types:
            insights.append("Stack traces reveal internal system details")
        
        if "sql_injection" in finding_types:
            insights.append("Potential SQL injection patterns detected")
        
        if "token" in finding_types:
            insights.append("Authentication tokens exposed - revoke and reissue")
        
        if finding_types.get("credential", 0) > 0:
            insights.append("Multiple credentials found - implement secret management")
        
        # General insights based on amount
        total_findings = len(findings)
        if total_findings > 10:
            insights.append(f"High concentration of sensitive data: {total_findings} items found")
        
        # Critical items
        critical_findings = [f for f in findings if f.risk == RiskLevel.CRITICAL]
        if critical_findings:
            insights.append(f"URGENT: {len(critical_findings)} critical security issues found")
        
        # High risk items
        high_findings = [f for f in findings if f.risk == RiskLevel.HIGH]
        if high_findings:
            insights.append(f"{len(high_findings)} high-risk items require attention")
        
        if not insights:
            insights.append("No significant security issues detected")
        
        return insights
    
    def _generate_ai_insights(self, content: str, findings: List[Finding], 
                             analysis_type: str) -> List[str]:
        """Generate insights using LLM."""
        try:
            findings_text = self._format_findings(findings)
            
            prompt = f"""Analyze the following {analysis_type} analysis and provide 3-5 key security insights.

Findings:
{findings_text}

Content Preview (first 500 chars):
{content[:500]}

Provide insights as a JSON array of strings. Focus on:
1. Immediate security threats
2. Compliance issues
3. Data exposure risks
4. Recommended actions
5. Overall risk assessment

Response format:
{{"insights": ["insight1", "insight2", ...]}}"""

            response = self.client.ChatCompletion.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a security expert analyzing logs and content for vulnerabilities."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            response_text = response['choices'][0]['message']['content']
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result.get("insights", self._generate_rule_based_insights(findings, analysis_type))
            
        except Exception as e:
            # Fallback to rule-based if AI fails
            print(f"AI insight generation failed: {e}")
        
        return self._generate_rule_based_insights(findings, analysis_type)
    
    def _format_findings(self, findings: List[Finding]) -> str:
        """Format findings for LLM consumption."""
        formatted = []
        for i, finding in enumerate(findings[:10], 1):  # Limit to 10 findings
            formatted.append(
                f"{i}. Type: {finding.type.value}, Risk: {finding.risk.value}, "
                f"Line: {finding.line}, Value: {finding.value or 'N/A'}"
            )
        return "\n".join(formatted)
    
    def generate_summary(self, findings: List[Finding], 
                        log_metadata: Optional[Dict] = None) -> str:
        """
        Generate a summary of the analysis.
        
        Args:
            findings: List of security findings
            log_metadata: Optional log metadata
            
        Returns:
            Summary string
        """
        if not findings:
            return "No security issues detected"
        
        # Count findings by type
        types_count = {}
        for finding in findings:
            types_count[finding.type.value] = types_count.get(finding.type.value, 0) + 1
        
        # Count by risk level
        risk_count = {}
        for finding in findings:
            risk_count[finding.risk.value] = risk_count.get(finding.risk.value, 0) + 1
        
        summary_parts = []
        
        # Build summary
        if risk_count.get("critical", 0) > 0:
            summary_parts.append(f"{risk_count['critical']} critical security issues")
        
        if risk_count.get("high", 0) > 0:
            summary_parts.append(f"{risk_count['high']} high-risk items")
        
        # Add specific threats
        threats = []
        if "password" in types_count:
            threats.append("passwords")
        if "api_key" in types_count or "aws_key" in types_count:
            threats.append("API keys")
        if "email" in types_count:
            threats.append("email addresses")
        if "stack_trace" in types_count:
            threats.append("system details in stack traces")
        
        if threats:
            summary_parts.append(f"Contains {', '.join(threats)}")
        
        if log_metadata and log_metadata.get("has_errors"):
            summary_parts.append("Multiple errors found")
        
        summary = " - ".join(summary_parts) if summary_parts else f"Found {len(findings)} security findings"
        
        return summary
