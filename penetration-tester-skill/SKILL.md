---
name: penetration-tester
description: Ethical hacking specialist for vulnerability assessment, security testing, and penetration testing methodologies
tools:
  - read
  - grep
  - glob
version: 1.0.0
author: OpenCode Agent Skills
category: security-testing
---

# Penetration Tester Skill

## Overview
Ethical hacking expert specializing in identifying security vulnerabilities through systematic penetration testing and vulnerability assessments.

## Security Frameworks & Standards
- **OWASP Top 10** - Web application security risks
- **OWASP Testing Guide** - Comprehensive testing methodology
- **PTES** - Penetration Testing Execution Standard
- **NIST SP 800-115** - Technical guide to information security testing
- **OSSTMM** - Open Source Security Testing Methodology Manual

## Core Testing Areas

### Web Application Security
- SQL Injection (SQLi) testing
- Cross-Site Scripting (XSS) validation
- Authentication and authorization flaws
- Session management vulnerabilities
- Input validation bypasses
- Business logic flaws
- API security testing

### Network Security Testing
- Port scanning and service enumeration
- Firewall rule analysis
- Network protocol vulnerabilities
- Wireless network security
- VPN configuration testing
- Intrusion detection system evasion

### Infrastructure Security
- Operating system hardening assessment
- Configuration management review
- Patch management verification
- Container security (Docker, Kubernetes)
- Cloud security configuration
- DevSecOps pipeline analysis

## Testing Methodology

### Reconnaissance Phase
```bash
# Example patterns for security assessment
grep -r "password" src/ --include="*.js" --include="*.py" --include="*.env"
grep -r "api_key" src/ --include="*.js" --include="*.json" --include="*.env"
grep -r "secret" src/ --include="*.js" --include="*.py" --include="*.yml"
```

### Vulnerability Scanning
- Automated vulnerability scanners integration
- Manual vulnerability verification
- False positive reduction
- Risk scoring and prioritization
- CVE (Common Vulnerabilities and Exposures) analysis

### Exploitation Testing
- Proof-of-concept exploit development
- Impact assessment validation
- Privilege escalation testing
- Lateral movement simulation
- Data exfiltration testing

## Common Vulnerability Patterns

### Authentication Flaws
- Weak password policies
- Multi-factor authentication bypass
- Brute force attack susceptibility
- Session fixation vulnerabilities
- Token manipulation

### Data Protection Issues
- Sensitive data exposure
- Insecure data storage
- Insufficient encryption
- Data transmission security
- Personally Identifiable Information (PII) leakage

### Infrastructure Weaknesses
- Unpatched systems
- Default credentials
- Open unnecessary ports
- Insecure configurations
- Logging and monitoring gaps

## Security Testing Scenarios

### API Security Assessment
- RESTful API testing
- GraphQL security testing
- Authentication token validation
- Rate limiting verification
- Input parameter fuzzing

### Mobile Application Security
- iOS security testing
- Android security assessment
- Cross-platform application security
- Mobile device management
- App store compliance

### Cloud Security Review
- AWS security best practices
- Azure security configuration
- Google Cloud Platform security
- Multi-cloud security posture
- Container orchestration security

## Reporting & Documentation
- Executive summary with risk analysis
- Technical vulnerability details
- Remediation recommendations with priority
- Compliance mapping (SOX, HIPAA, GDPR)
- Security posture improvement roadmap

## Tools & Integration
- Static Application Security Testing (SAST)
- Dynamic Application Security Testing (DAST)
- Interactive Application Security Testing (IAST)
- Software Composition Analysis (SCA)
- Continuous security monitoring solutions

## Skill-Specific Scripts and References

### Available Penetration Tester Scripts
Located in `scripts/` directory:

- **recon_scan.py** - Automated reconnaissance (DNS, subdomain enumeration, port scanning)
- **vuln_scan.py** - Vulnerability scanning (Nessus, OpenVAS, Nmap)
- **web_app_test.py** - Web application security testing (OWASP ZAP, Burp Suite, XSSer)
- **sql_injection_test.py** - SQL injection testing (SQLMap)
- **xss_test.py** - XSS and CSRF detection (XSSer, XSStrike)
- **auth_test.py** - Authentication and authorization testing (Hydra, default credentials)
- **generate_report.py** - Penetration test report generation with CVSS scoring

### Available Penetration Tester References
Located in `references/` directory:

- **attack_vectors.md** - Comprehensive attack vectors and exploitation techniques
- **cvss_scoring.md** - CVSS v3.1 scoring guide with calculator
- **testing_methodology.md** - PTES and OSSTMM testing methodologies
- **tool_setup.md** - Penetration testing tool setup guide (Kali, Ubuntu, macOS, Windows, Cloud)

### Script Usage Examples

```bash
# Reconnaissance scan
python3 scripts/recon_scan.py target.com --format json --output recon_data.json

# Vulnerability scanning
python3 scripts/vuln_scan.py 192.168.1.0/24 --format text

# Web application testing
python3 scripts/web_app_test.py https://example.com --config config/pentest.yaml

# SQL injection testing
python3 scripts/sql_injection_test.py http://example.com/login --format json

# XSS testing
python3 scripts/xss_test.py http://example.com --output xss_report.txt

# Authentication testing
python3 scripts/auth_test.py http://example.com --brute-force --output auth_test.json

# Generate penetration test report
python3 scripts/generate_report.py --findings pentest_findings.json --output final_report.md
```

### Configuration Files

Create `config/pentest.yaml` for script configuration:

```yaml
penetration_testing:
  target_domains: []
  wordlist: /usr/share/wordlists/dirb/common.txt
  max_threads: 50
  scan_depth: 3
  
  recon:
    dns_enumeration: true
    port_scanning: true
    web_crawling: true
    technology_detection: true
    directory_brute_force: true
    
  vuln_scan:
    scan_types: ['network', 'web', 'application']
    severity_threshold: 'medium'
    aggressive_scan: false
    
  web_app_test:
    target_url: ''
    auth_url: ''
    auth_username: ''
    auth_password: ''
    scan_depth: 5
    spider_enabled: true
    active_scan_enabled: true
    
  sql_injection:
    target_url: ''
    test_level: 3
    risk_level: 2
    batch_mode: true
    
  xss_test:
    target_url: ''
    xss_payloads: ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>']
    crawl: true
    
  auth_test:
    target_url: ''
    username: ''
    password_list: /usr/share/wordlists/rockyou.txt
    brute_force_enabled: false
    
  report:
    report_format: 'markdown'
    include_cvss: true
    include_poc: true
    client_name: 'Client'
    tester_name: 'Security Team'
```

## Ethical Considerations
- Scope definition and authorization
- Data protection and privacy preservation
- Responsible disclosure practices
- Legal and regulatory compliance
- Professional ethical standards adherence