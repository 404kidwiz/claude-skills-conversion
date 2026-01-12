# Security Frameworks and Standards

## Overview
Comprehensive reference for major security frameworks, standards, and methodologies used in security auditing and compliance.

## OWASP (Open Web Application Security Project)

### OWASP Testing Guide
- **Purpose:** Comprehensive web application security testing methodology
- **Scope:** 4 categories, 13 controls
- **Key Areas:**
  - Information Gathering
  - Configuration and Deployment Management
  - Identity Management Testing
  - Input Validation Testing
- **Link:** https://owasp.org/www-project-web-security-testing-guide/

### OWASP ASVS (Application Security Verification Standard)
- **Purpose:** Security requirements and controls for applications
- **Scope:** 14 requirements areas
- **Verification Levels:**
  - Level 1: Basic security controls
  - Level 2: Standard security controls
  - Level 3: Advanced security controls
- **Link:** https://owasp.org/www-project-application-security-verification-standard/

### OWASP MASVS (Mobile Application Security Verification Standard)
- **Purpose:** Mobile app security requirements
- **Scope:** 8 areas including data storage, cryptography, authentication
- **Link:** https://owasp.org/www-project-mobile-app-security/

## NIST (National Institute of Standards and Technology)

### NIST SP 800-53 - Security and Privacy Controls
- **Purpose:** Security and privacy controls for federal information systems
- **Families:** 18 control families including:
  - Access Control (AC)
  - System and Communications Protection (SC)
  - Security Assessment and Authorization (CA)
  - Incident Response (IR)
- **Control Baselines:** Low, Moderate, High
- **Link:** https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final

### NIST SP 800-115 - Technical Guide to Information Security Testing
- **Purpose:** Technical guidance for security testing and assessment
- **Key Techniques:**
  - Discovery
  - Vulnerability scanning
  - Penetration testing
  - Red teaming
- **Link:** https://csrc.nist.gov/publications/detail/sp/800-115/final

### NIST Cybersecurity Framework (CSF)
- **Functions:**
  1. Identify
  2. Protect
  3. Detect
  4. Respond
  5. Recover
- **Categories:** 23 categories across functions
- **Tiers:** Partial, Risk Informed, Repeatable, Adaptive
- **Link:** https://www.nist.gov/cyberframework

## CIS (Center for Internet Security)

### CIS Controls
- **Purpose:** Prioritized set of actions for cybersecurity defense
- **Version:** CIS Controls v8
- **Implementation Groups:**
  - IG1: Basic cyber hygiene
  - IG2: Essential cyber hygiene
  - IG3: Advanced cyber hygiene
- **Key Controls:**
  - Inventory and Control of Enterprise Assets
  - Inventory and Control of Software Assets
  - Data Protection
  - Secure Configuration of Enterprise Assets
  - Account Management
- **Link:** https://www.cisecurity.org/controls/cis-controls-list

### CIS Benchmarks
- **Purpose:** Configuration guidelines for secure system setup
- **Platforms:** 100+ platforms including:
  - Windows, Linux, macOS
  - Cloud providers (AWS, Azure, GCP)
  - Databases
  - Network devices
- **Download:** https://www.cisecurity.org/cis-benchmarks

## ISO (International Organization for Standardization)

### ISO 27001 - Information Security Management
- **Purpose:** Requirements for establishing, implementing, maintaining ISMS
- **Annex A:** 114 controls in 14 categories
- **Certification:** Third-party audit available
- **Link:** https://www.iso.org/standard/27001

### ISO 27002 - Information Security Controls
- **Purpose:** Code of practice for information security controls
- **Structure:** 93 controls in 4 themes:
  - Organizational
  - People
  - Physical
  - Technological
- **Link:** https://www.iso.org/standard/82875

### ISO 22301 - Business Continuity
- **Purpose:** Requirements for business continuity management
- **Key Elements:**
  - Risk assessment
  - Business impact analysis
  - Business continuity strategy
  - Testing and exercising
- **Link:** https://www.iso.org/standard/75106

## PCI DSS (Payment Card Industry Data Security Standard)

### PCI DSS v4.0
- **Purpose:** Security standards for organizations handling cardholder data
- **12 Requirements:**
  1. Install and maintain network security controls
  2. Apply secure configurations to all system components
  3. Protect stored account data
  4. Protect cardholder data in transit
  5. Protect all systems from malware
  6. Develop and maintain secure systems and software
  7. Restrict access to system components and cardholder data
  8. Identify users and authenticate access
  9. Restrict physical access to cardholder data
  10. Log and monitor access to system components
  11. Test security systems and processes regularly
  12. Support information security with organizational policies
- **Validation:** Self-Assessment Questionnaire (SAQ) or ROC
- **Link:** https://www.pcisecuritystandards.org/

## HIPAA (Health Insurance Portability and Accountability Act)

### HIPAA Security Rule
- **Purpose:** Protect electronic protected health information (ePHI)
- **Administrative Safeguards:**
  - Security management process
  - Assigned security responsibility
  - Workforce security
  - Information access management
  - Security awareness and training
  - Security incident procedures
  - Contingency plan
  - Evaluation
  - Business associate contracts
- **Physical Safeguards:**
  - Facility access controls
  - Workstation use
  - Workstation security
  - Device and media controls
- **Technical Safeguards:**
  - Access control
  - Audit controls
  - Integrity controls
  - Transmission security
- **Link:** https://www.hhs.gov/hipaa/

## GDPR (General Data Protection Regulation)

### Key Requirements
- **Purpose:** Protect personal data of EU citizens
- **Principles:**
  1. Lawfulness, fairness, and transparency
  2. Purpose limitation
  3. Data minimization
  4. Accuracy
  5. Storage limitation
  6. Integrity and confidentiality
  7. Accountability
- **Rights:**
  - Right to be informed
  - Right of access
  - Right to rectification
  - Right to erasure
  - Right to restrict processing
  - Right to data portability
  - Right to object
  - Rights in relation to automated decision making
- **Link:** https://gdpr.eu/

## SOC 2 (System and Organization Controls)

### SOC 2 Type 1 and Type 2
- **Purpose:** Security, availability, processing integrity, confidentiality, privacy
- **Trust Services Criteria (TSC):**
  1. Security
  2. Availability
  3. Processing Integrity
  4. Confidentiality
  5. Privacy
- **Common Criteria:**
  - Control Environment
  - Communication and Information
  - Risk Assessment
  - Monitoring Activities
  - Control Activities
- **Link:** https://www.aicpa.org/soc4so

## Security Assessment Methodologies

### PTES (Penetration Testing Execution Standard)
- **Phases:**
  1. Pre-engagement Interactions
  2. Intelligence Gathering
  3. Threat Modeling
  4. Vulnerability Analysis
  5. Exploitation
  6. Post-Exploitation
  7. Reporting
- **Link:** http://www.pentest-standard.org/

### OSSTMM (Open Source Security Testing Methodology Manual)
- **Security Test Modules:**
  1. Human Security
  2. Physical Security
  3. Wireless Security
  4. Telecommunications Security
  5. Data Networks Security
  6. Data Communications Security
  7. Applications Security
- **Link:** https://www.isecom.org/

### STRIDE Threat Modeling
- **Categories:**
  - **S**poofing
  - **T**ampering
  - **R**epudiation
  - **I**nformation Disclosure
  - **D**enial of Service
  - **E**levation of Privilege
- **Link:** https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats

## Vulnerability Scoring

### CVSS (Common Vulnerability Scoring System)
- **Version:** CVSS v3.1
- **Metrics:**
  - Attack Vector (AV)
  - Attack Complexity (AC)
  - Privileges Required (PR)
  - User Interaction (UI)
  - Scope (S)
  - Confidentiality (C)
  - Integrity (I)
  - Availability (A)
- **Severity:**
  - 0.0: None
  - 0.1-3.9: Low
  - 4.0-6.9: Medium
  - 7.0-8.9: High
  - 9.0-10.0: Critical
- **Link:** https://www.first.org/cvss/

## Cloud Security Standards

### CSA STAR (Cloud Security Alliance Security Trust Assurance and Risk)
- **Purpose:** Cloud security assurance and certification
- **Components:**
  - CCM (Cloud Controls Matrix)
  - CAIQ (Consensus Assessments Initiative Questionnaire)
- **Link:** https://cloudsecurityalliance.org/star/

### ISO 27017 - Cloud Security
- **Purpose:** Cloud-specific information security controls
- **Controls:** 37 cloud-specific controls
- **Link:** https://www.iso.org/standard/43757

## DevSecOps Standards

### SAMM (Software Assurance Maturity Model)
- **Business Functions:**
  1. Governance
  2. Design
  3. Implementation
  4. Verification
  5. Operations
- **Security Practices:** 12 practices across functions
- **Maturity Levels:** 0-3
- **Link:** https://owaspsamm.org/

### BSIMM (Building Security In Maturity Model)
- **Domains:** 12 domains including:
  - Governance
  - Intelligence
  - SSDL Touchpoints
  - Deployment
  - Operations
- **Activities:** 119 activities
- **Link:** https://www.bsimm.com/

## Quick Reference

### Framework Selection Guide

| Organization/Type | Recommended Framework(s) |
|-------------------|-------------------------|
| Web Applications | OWASP Top 10, OWASP ASVS |
| Financial/Card Data | PCI DSS |
| Healthcare | HIPAA Security Rule |
| EU Data Processing | GDPR |
| Cloud Infrastructure | CIS Controls, ISO 27017 |
| Government (US) | NIST CSF, NIST SP 800-53 |
| Compliance Certification | ISO 27001, SOC 2 |
| DevSecOps | SAMM, BSIMM |

### Common Compliance Matrix

| Framework | Focus Area | Industry |
|-----------|------------|----------|
| OWASP ASVS | Application Security | All |
| NIST SP 800-53 | Federal Systems | Government |
| ISO 27001 | Information Security | All |
| PCI DSS | Payment Data | Financial |
| HIPAA | Health Data | Healthcare |
| GDPR | Personal Data | EU Operations |
| SOC 2 | Security Controls | SaaS/Cloud |
| CIS Controls | Security Controls | All |

## Implementation Tips

1. **Start with Risk Assessment:** Identify assets, threats, and risks first
2. **Baseline with CIS:** Use CIS Benchmarks for configuration hardening
3. **Map Controls:** Understand how controls map across frameworks
4. **Automate Where Possible:** Use tools for continuous compliance
5. **Document Everything:** Maintain evidence for audits
6. **Regular Reviews:** Update as threats and requirements evolve
7. **Training:** Ensure teams understand relevant frameworks
