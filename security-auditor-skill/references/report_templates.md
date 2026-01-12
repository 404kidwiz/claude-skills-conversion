# Security Report Templates

## Overview
Standardized templates for security audit reports, penetration test reports, and vulnerability assessments.

## Executive Summary Template

```markdown
# Security Assessment Report - Executive Summary

**Report ID:** SA-2024-001
**Assessment Date:** January 12, 2026
**Report Date:** January 12, 2026
**Prepared By:** Security Team
**Organization:** [Company Name]

## Overview
This document provides an executive summary of the security assessment conducted on [System/Application Name]. The assessment identified [X] vulnerabilities across [Y] categories.

## Risk Rating Summary

| Severity | Count | Risk Level |
|----------|-------|------------|
| Critical | X | Immediate Action Required |
| High     | Y | Urgent Action Required |
| Medium   | Z | Action Required |
| Low      | W | Monitor |

## Key Findings

1. **[Critical Finding Title]** - [Brief description]
   - Impact: [Business impact]
   - Affected Systems: [List]

2. **[High Finding Title]** - [Brief description]
   - Impact: [Business impact]
   - Affected Systems: [List]

## Executive Recommendations

1. **Immediate Actions (24-48 hours)**
   - Remediate critical vulnerabilities
   - Implement temporary mitigations
   - Notify stakeholders

2. **Short-term Actions (1-2 weeks)**
   - Address high severity issues
   - Update security controls
   - Conduct targeted training

3. **Long-term Actions (1-3 months)**
   - Implement security governance
   - Enhance monitoring capabilities
   - Regular security assessments

## Compliance Status

| Framework | Status | Notes |
|-----------|--------|-------|
| OWASP Top 10 | Compliant/Non-Compliant | [Notes] |
| PCI DSS | Compliant/Non-Compliant | [Notes] |
| GDPR | Compliant/Non-Compliant | [Notes] |
| SOC 2 | Compliant/Non-Compliant | [Notes] |

## Conclusion

[Summary of overall security posture and next steps]

---

## Approval

| Name | Title | Date | Signature |
|------|-------|------|-----------|
| [Name] | [Title] | [Date] | |
| [Name] | [Title] | [Date] | |
```

## Detailed Technical Report Template

```markdown
# Security Assessment Report - Technical Details

**Report ID:** SA-2024-001
**Assessment Type:** [Vulnerability Scan/Penetration Test/Code Review]
**Scope:** [Defined scope]
**Methodology:** [Tools and techniques used]

## Methodology

### Assessment Approach
- [ ] Vulnerability Scanning
- [ ] Manual Testing
- [ ] Configuration Review
- [ ] Source Code Review
- [ ] Architecture Review

### Tools Used
- [ ] OWASP ZAP
- [ ] Burp Suite
- [ ] Nessus/OpenVAS
- [ ] Nmap
- [ ] SQLMap
- [ ] Bandit
- [ ] Trivy
- [ ] Other: ______

## Detailed Findings

### Finding #1: [Finding Title]

**Severity:** Critical/High/Medium/Low  
**CVSS Score:** X.X  
**CWE ID:** CWE-XXX  
**Finding ID:** F-001

#### Description
[Detailed description of the vulnerability]

#### Affected Systems
- System: [System Name]
- URL/Path: [URL or file path]
- Location: [Specific location]

#### Technical Details
```
[Code snippet, configuration, or technical details]
```

#### Proof of Concept
```bash
[Commands or steps to reproduce]
```

#### Impact
- **Confidentiality:** [High/Medium/Low/None]
- **Integrity:** [High/Medium/Low/None]
- **Availability:** [High/Medium/Low/None]

#### Remediation

**Immediate Mitigation:**
```python/code/bash
[Temporary fix]
```

**Permanent Fix:**
```python/code/bash
[Permanent solution]
```

**Validation Steps:**
```bash
[Commands to verify remediation]
```

#### References
- [OWASP Link]
- [CVE Link]
- [Documentation Link]

---

### Finding #2: [Finding Title]
[Repeat structure for each finding]

## Vulnerability Summary by Category

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Injection | | | | | |
| Authentication | | | | | |
| Configuration | | | | | |
| Encryption | | | | | |
| Logging | | | | | |
| **Total** | | | | | |

## Appendix

### A. Scanned Assets
[Detailed list of all scanned systems, IPs, URLs]

### B. False Positives
[List any confirmed false positives]

### C. Testing Timeline
- Start Date: [Date]
- End Date: [Date]
- Total Duration: [Time]

### D. Scope Limitations
[Any limitations or exclusions from testing]

### E. Definitions
- **Critical:** Can be exploited to completely compromise system
- **High:** Can be exploited to compromise system with user interaction
- **Medium:** Limited impact, requires specific conditions
- **Low:** Minimal impact, difficult to exploit
```

## Penetration Test Report Template

```markdown
# Penetration Test Report

**Report ID:** PT-2024-001
**Test Type:** Black Box / Gray Box / White Box
**Test Window:** [Start Date] to [End Date]

## Executive Summary
[High-level overview of test results]

## Testing Scope

### In Scope
- IP Range: [X.X.X.X/X]
- Domains: [domain1.com, domain2.com]
- Applications: [App1, App2]
- User Accounts: [List provided credentials]

### Out of Scope
- Production systems (unless authorized)
- Third-party services
- Physical security

## Attack Narrative

### Phase 1: Reconnaissance
```
[Finding enumeration results]
```

### Phase 2: Vulnerability Assessment
```
[Identified vulnerabilities]
```

### Phase 3: Exploitation
```
[Successful exploit details]
```

### Phase 4: Post-Exploitation
```
[Achieved access level, data accessed]
```

## Exploited Vulnerabilities

### Vulnerability 1: [Name]
**Chain:** This vulnerability was exploited to gain initial access

**Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Result:**
```
[Command output or screenshot]
```

### Vulnerability 2: [Name]
[Repeat for each exploited vulnerability]

## Risk Assessment

### Risk Scoring Methodology
- **Likelihood:** (Very Low to Very High)
- **Impact:** (Very Low to Very High)
- **Risk Score:** Likelihood × Impact

### Top Risks

| Risk | Likelihood | Impact | Risk Score |
|------|------------|--------|------------|
| [Risk 1] | High | High | Very High |
| [Risk 2] | Medium | High | High |
| [Risk 3] | High | Medium | High |

## Recommendations (Prioritized)

### Priority 1 - Critical (Implement Immediately)
1. [Recommendation]
2. [Recommendation]

### Priority 2 - High (Implement Within 1 Week)
1. [Recommendation]
2. [Recommendation]

### Priority 3 - Medium (Implement Within 1 Month)
1. [Recommendation]
2. [Recommendation]

## Remediation Status

| Finding | Status | Date Completed | Notes |
|---------|--------|----------------|-------|
| [Finding 1] | Pending | | |
| [Finding 2] | Remediated | [Date] | Validated |
| [Finding 3] | Accepted Risk | | Reason: |

## Lessons Learned

1. What went well:
   - [List]

2. Areas for improvement:
   - [List]

3. Recommendations for future tests:
   - [List]

## Appendices

### Appendix A: Full Scan Results
[Raw scan outputs]

### Appendix B: Exploitation Scripts
[Any custom scripts used]

### Appendix C: Screenshots
[Relevant screenshots]
```

## Compliance Report Template

```markdown
# Compliance Assessment Report

**Standard:** [PCI DSS v4.0 / ISO 27001 / SOC 2 / HIPAA / GDPR]
**Assessment Period:** [Date Range]
**Organization:** [Company Name]

## Executive Summary

### Compliance Status
- **Overall Status:** [Compliant / Partially Compliant / Non-Compliant]
- **Compliance Score:** X%

### Critical Gaps
1. [Gap 1]
2. [Gap 2]

## Compliance by Control

| Control | Requirement | Status | Gap | Remediation |
|---------|-------------|--------|-----|-------------|
| [Control ID] | [Description] | Compliant/Non-Compliant | [Gap description] | [Action needed] |

## Detailed Findings

### Finding 1: Non-Compliance with [Control]
**Requirement:** [Specific requirement text]

**Current State:**
```
[Description of current implementation]
```

**Gap Analysis:**
- What's missing: [List]
- Why it's missing: [Reason]

**Recommendation:**
```bash/python
[Specific remediation steps]
```

**Evidence Required:**
- [ ]
- [ ]
- [ ]

### Finding 2: Partial Compliance with [Control]
[Repeat structure]

## Risk Assessment

### Non-Compliance Risks

| Control | Risk Level | Business Impact | Likelihood |
|---------|------------|----------------|------------|
| [Control 1] | High | [Impact] | High |
| [Control 2] | Medium | [Impact] | Medium |

## Remediation Plan

### Immediate Actions (30 days)
| Item | Owner | Due Date | Status |
|------|-------|----------|--------|
| [Action 1] | [Name] | [Date] | Pending |
| [Action 2] | [Name] | [Date] | Pending |

### Short-term Actions (60 days)
[Table format same as above]

### Long-term Actions (90 days)
[Table format same as above]

## Evidence Collection

### Evidence Repository
- Location: [Path/URL]
- Access: [Who has access]

### Required Evidence Matrix

| Control | Evidence Type | Collected? | Location |
|---------|---------------|------------|----------|
| [Control 1] | Screenshot | Yes | [Location] |
| [Control 1] | Log excerpt | Yes | [Location] |
| [Control 2] | Policy document | No | [Will collect by date] |

## Continuous Compliance Monitoring

### Automation
- [ ] Automated compliance checks implemented
- [ ] Continuous monitoring in place
- [ ] Alerting configured

### Schedule
- **Daily:** [What's monitored daily]
- **Weekly:** [What's checked weekly]
- **Monthly:** [What's reviewed monthly]
- **Quarterly:** [What's audited quarterly]

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| CISO | [Name] | [Date] | |
| Compliance Officer | [Name] | [Date] | |
| System Owner | [Name] | [Date] | |
| Auditor | [Name] | [Date] | |
```

## Code Review Security Report Template

```markdown
# Security Code Review Report

**Project:** [Project Name]
**Review Date:** [Date]
**Reviewer:** [Name]
**Branch/Commit:** [Branch name or commit hash]

## Summary

- **Total Files Reviewed:** X
- **Total Lines of Code:** Y
- **Security Findings:** Z
- **Code Quality Issues:** W

## Findings Summary

| Severity | Count | Files |
|----------|-------|-------|
| Critical | X | [List] |
| High     | Y | [List] |
| Medium   | Z | [List] |
| Low      | W | [List] |

## Detailed Findings

### Finding 1: [Title]

**File:** `src/module/file.py:Line`  
**Severity:** Critical  
**Category:** [Injection/Auth/etc]

**Vulnerable Code:**
```python
[Code snippet with issue]
```

**Issue Description:**
[Detailed explanation]

**Remediation:**
```python
[Fixed code]
```

**References:**
- [OWASP/CWE reference]

---

### Finding 2: [Title]
[Repeat for each finding]

## Security Best Practices Review

### Authentication & Authorization
- [ ] Password hashing implemented
- [ ] Session management secure
- [ ] Multi-factor authentication
- [ ] Proper authorization checks

### Input Validation
- [ ] All user inputs validated
- [ ] SQL injection protection
- [ ] XSS protection
- [ ] CSRF protection

### Cryptography
- [ ] Secure encryption algorithms
- [ ] Proper key management
- [ ] TLS/SSL enforced
- [ ] Random number generation

### Error Handling
- [ ] No sensitive data in errors
- [ ] Proper logging
- [ ] Secure exception handling
- [ ] Generic error messages

### Configuration
- [ ] Debug mode disabled
- [ ] Secure headers configured
- [ ] Hardcoded secrets removed
- [ ] Proper CORS configuration

## Recommendations

### Code Changes
1. [Specific code fix]
2. [Specific code fix]

### Process Improvements
1. [Process recommendation]
2. [Process recommendation]

### Tooling
1. [Tool recommendation]
2. [Tool recommendation]

## Next Steps

1. **Immediate:** [What to do now]
2. **Short-term:** [What to do this week]
3. **Long-term:** [What to do this month]
```

## Report Generation Script

```python
#!/usr/bin/env python3
"""
Security Report Generator
Generates standardized security reports from scan results
"""

import json
from datetime import datetime
from typing import Dict, List
import yaml

class SecurityReportGenerator:
    def __init__(self, findings: List[Dict]):
        self.findings = findings
        self.severity_order = ['critical', 'high', 'medium', 'low']
    
    def generate_summary(self) -> Dict:
        summary = {severity: 0 for severity in self.severity_order}
        
        for finding in self.findings:
            severity = finding.get('severity', 'low').lower()
            if severity in summary:
                summary[severity] += 1
        
        return summary
    
    def generate_executive_summary(self) -> str:
        summary = self.generate_summary()
        total = sum(summary.values())
        
        report = f"""
# Security Assessment Executive Summary

**Report Date:** {datetime.now().strftime('%Y-%m-%d')}

## Risk Rating Summary

| Severity | Count | Risk Level |
|----------|-------|------------|
| Critical | {summary['critical']} | Immediate Action Required |
| High     | {summary['high']} | Urgent Action Required |
| Medium   | {summary['medium']} | Action Required |
| Low      | {summary['low']} | Monitor |

**Total Findings:** {total}

## Top Critical Issues

"""
        critical_findings = [f for f in self.findings if f.get('severity') == 'critical']
        for i, finding in enumerate(critical_findings[:5], 1):
            report += f"{i}. **{finding.get('title', 'Unknown')}**\n"
            report += f"   - {finding.get('description', 'No description')}\n\n"
        
        return report
    
    def generate_detailed_report(self) -> str:
        report = "# Detailed Security Findings\n\n"
        
        for severity in self.severity_order:
            findings = [f for f in self.findings if f.get('severity') == severity]
            if findings:
                report += f"## {severity.upper()} Severity ({len(findings)})\n\n"
                
                for i, finding in enumerate(findings, 1):
                    report += f"### {i}. {finding.get('title', 'Unknown')}\n\n"
                    report += f"**ID:** {finding.get('id', 'N/A')}\n"
                    report += f"**Location:** {finding.get('file', 'N/A')}:{finding.get('line', 'N/A')}\n\n"
                    report += f"**Description:**\n{finding.get('description', 'No description')}\n\n"
                    
                    if finding.get('remediation'):
                        report += f"**Remediation:**\n```\n{finding['remediation']}\n```\n\n"
                    
                    if finding.get('references'):
                        report += f"**References:**\n"
                        for ref in finding['references']:
                            report += f"- {ref}\n"
                        report += "\n"
        
        return report
    
    def save_reports(self, output_dir: str):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        exec_summary = self.generate_executive_summary()
        with open(f'{output_dir}/executive_summary_{timestamp}.md', 'w') as f:
            f.write(exec_summary)
        
        detailed_report = self.generate_detailed_report()
        with open(f'{output_dir}/detailed_report_{timestamp}.md', 'w') as f:
            f.write(detailed_report)

if __name__ == '__main__':
    # Example usage
    findings = [
        {
            'id': 'VULN-001',
            'severity': 'critical',
            'title': 'SQL Injection',
            'description': 'SQL injection vulnerability in login function',
            'file': 'src/auth.py',
            'line': 45,
            'remediation': 'Use parameterized queries',
            'references': ['https://owasp.org/www-community/attacks/SQL_Injection']
        }
    ]
    
    generator = SecurityReportGenerator(findings)
    generator.save_reports('reports/')
```

## Email Notification Templates

```python
# Critical vulnerability notification
def send_critical_alert(finding):
    subject = f"CRITICAL: {finding['title']} - Immediate Action Required"
    body = f"""
A critical vulnerability has been identified:

**Title:** {finding['title']}
**Severity:** CRITICAL
**Location:** {finding['file']}:{finding['line']}
**Description:** {finding['description']}

**Recommended Action:**
{finding['remediation']}

Please acknowledge receipt of this alert.

--
Security Team
"""
    # Send email logic here
    pass

# Weekly security summary
def send_weekly_summary(findings):
    summary = {sev: len([f for f in findings if f['severity'] == sev]) 
               for sev in ['critical', 'high', 'medium', 'low']}
    
    subject = "Weekly Security Summary"
    body = f"""
Weekly Security Summary

Total Findings: {len(findings)}
Critical: {summary['critical']}
High: {summary['high']}
Medium: {summary['medium']}
Low: {summary['low']}

Please review the detailed report attached.

--
Security Team
"""
    # Send email logic here
    pass
```
