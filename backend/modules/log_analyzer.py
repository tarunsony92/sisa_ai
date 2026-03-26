import re
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime
from models.schemas import Finding, RiskLevel
from .detection_engine import DetectionEngine


class LogAnalyzer:
    """Specialized log file analyzer for security threats and anomalies."""
    
    def __init__(self):
        self.detection_engine = DetectionEngine()
        self.log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    def analyze_log(self, content: str) -> Dict:
        """
        Comprehensive log analysis.
        
        Args:
            content: Log file content
            
        Returns:
            Dictionary with analysis results
        """
        lines = content.split('\n')
        
        # Detect sensitive data and security issues
        findings = self.detection_engine.detect_in_text(content)
        findings.extend(self.detection_engine.detect_stack_traces(content))
        findings.extend(self.detection_engine.detect_sql_injection(content))
        
        # Extract log metadata
        metadata = self._extract_metadata(lines)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(lines)
        
        # Detect repeated patterns (brute force, suspicious activity)
        repeated_patterns = self._detect_repeated_patterns(lines)
        
        return {
            "findings": findings,
            "metadata": metadata,
            "anomalies": anomalies,
            "repeated_patterns": repeated_patterns,
            "audit_trail": self._extract_audit_trail(lines)
        }
    
    def _extract_metadata(self, lines: List[str]) -> Dict:
        """Extract metadata from log lines."""
        metadata = {
            "total_lines": len(lines),
            "log_level_distribution": defaultdict(int),
            "timestamp_range": None,
            "unique_hosts": set(),
            "unique_users": set(),
            "has_errors": False,
            "has_warnings": False
        }
        
        timestamps = []
        
        for line in lines:
            if not line.strip():
                continue
            
            # Count log levels
            for level in self.log_levels:
                if re.search(rf"\b{level}\b", line, re.IGNORECASE):
                    metadata["log_level_distribution"][level] += 1
                    if level in ["ERROR", "CRITICAL"]:
                        metadata["has_errors"] = True
                    if level == "WARNING":
                        metadata["has_warnings"] = True
                    break
            
            # Extract hosts/IPs
            ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
            metadata["unique_hosts"].update(ips)
            
            # Extract usernames
            users = re.findall(r'(?:user|username|uid)[\s=]+([a-zA-Z0-9_]+)', line, re.IGNORECASE)
            metadata["unique_users"].update(users)
            
            # Extract timestamps
            timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', line)
            if timestamp_match:
                timestamps.append(timestamp_match.group(0))
        
        # Set timestamp range
        if timestamps:
            metadata["timestamp_range"] = f"{timestamps[0]} to {timestamps[-1]}"
        
        metadata["unique_hosts"] = list(metadata["unique_hosts"])
        metadata["unique_users"] = list(metadata["unique_users"])
        metadata["log_level_distribution"] = dict(metadata["log_level_distribution"])
        
        return metadata
    
    def _detect_anomalies(self, lines: List[str]) -> List[str]:
        """Detect suspicious patterns and anomalies."""
        anomalies = []
        
        for line_num, line in enumerate(lines, start=1):
            # Detect multiple failed login attempts in close proximity
            if re.search(r"(authentication\s+fail|login\s+fail|invalid\s+cred|unauthorized)", 
                        line, re.IGNORECASE):
                anomalies.append(f"Line {line_num}: Failed authentication attempt")
            
            # Detect debug/verbose mode leaks
            if re.search(r"debug\s*[:=]\s*true|verbose|trace|stacktrace", line, re.IGNORECASE):
                anomalies.append(f"Line {line_num}: Debug information leaked")
            
            # Detect suspicious commands (rm, chmod, etc.)
            if re.search(r"\b(rm\s+-rf|chmod\s+777|sudo|su\s+root)\b", line, re.IGNORECASE):
                anomalies.append(f"Line {line_num}: Suspicious system command detected")
            
            # Detect connection attempts to unusual ports
            if re.search(r"(?:connection|connect)\s+.*:(\d+)", line):
                match = re.search(r":(\d+)", line)
                if match:
                    port = int(match.group(1))
                    if port > 10000 or port in [4444, 5555, 9999]:
                        anomalies.append(f"Line {line_num}: Suspicious port ({port}) connection")
            
            # Detect permission denied
            if re.search(r"permission\s+denied", line, re.IGNORECASE):
                anomalies.append(f"Line {line_num}: Permission denied error")
        
        return anomalies
    
    def _detect_repeated_patterns(self, lines: List[str]) -> Dict:
        """Detect repeated patterns that might indicate brute force or scanning."""
        patterns = defaultdict(int)
        error_count = 0
        
        for line in lines:
            # Count error patterns
            if re.search(r"(error|fail|denied|unauthorized)", line, re.IGNORECASE):
                error_count += 1
            
            # Extract and count IP addresses
            ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
            for ip in ips:
                patterns[f"IP: {ip}"] += 1
        
        # Flag suspicious activity
        suspicious = {}
        for pattern, count in patterns.items():
            if count > 5:  # More than 5 occurrences
                suspicious[pattern] = count
        
        return {
            "error_frequency": error_count,
            "suspicious_repetitions": suspicious,
            "brute_force_risk": "HIGH" if error_count > len(lines) * 0.3 else "LOW"
        }
    
    def _extract_audit_trail(self, lines: List[str]) -> List[Dict]:
        """Extract important audit trail events."""
        audit_events = []
        
        # Extract login/logout events
        for line_num, line in enumerate(lines, start=1):
            for event in ["login", "logout", "authentication", "authorization", 
                         "permission", "access", "failed", "error"]:
                if re.search(rf"\b{event}\b", line, re.IGNORECASE):
                    # Extract timestamp
                    timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', line)
                    timestamp = timestamp_match.group(0) if timestamp_match else "N/A"
                    
                    # Extract user if present
                    user_match = re.search(r'(?:user|username)[\s=]+([a-zA-Z0-9_]+)', line, re.IGNORECASE)
                    user = user_match.group(1) if user_match else "Unknown"
                    
                    audit_events.append({
                        "line": line_num,
                        "timestamp": timestamp,
                        "event": event.upper(),
                        "user": user,
                        "severity": "HIGH" if "fail" in line.lower() or "error" in line.lower() else "MEDIUM"
                    })
        
        return audit_events
    
    def calculate_log_risk_score(self, analysis: Dict) -> Tuple[float, RiskLevel]:
        """
        Calculate risk score based on log analysis.
        
        Returns:
            Tuple of (risk_score, risk_level)
        """
        score = 0
        
        # Add score for findings
        for finding in analysis["findings"]:
            if finding.risk == RiskLevel.CRITICAL:
                score += 3
            elif finding.risk == RiskLevel.HIGH:
                score += 2
            elif finding.risk == RiskLevel.MEDIUM:
                score += 1
        
        # Add score for anomalies
        score += len(analysis["anomalies"]) * 1.5
        
        # Add score for repeated patterns
        if analysis["repeated_patterns"]["brute_force_risk"] == "HIGH":
            score += 2
        
        # Normalize score to 0-10
        max_possible_score = len(analysis["findings"]) * 3 + len(analysis["anomalies"]) * 1.5 + 2
        if max_possible_score > 0:
            normalized_score = min(10, (score / max_possible_score) * 10)
        else:
            normalized_score = 0
        
        # Determine risk level
        if normalized_score >= 9:
            risk_level = RiskLevel.CRITICAL
        elif normalized_score >= 7:
            risk_level = RiskLevel.HIGH
        elif normalized_score >= 4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return round(normalized_score, 2), risk_level
