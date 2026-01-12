---
name: compliance-auditor
description: Specialized auditor for SOC2, HIPAA, GDPR, and regulatory compliance frameworks across industries
tools:
  - read
  - grep
  - glob
version: 1.0.0
author: OpenCode Agent Skills
category: compliance-auditing
---

# Compliance Auditor Skill

## Overview
Expert in regulatory compliance auditing, specializing in SOC2, HIPAA, GDPR, and industry-specific compliance frameworks with gap analysis and remediation guidance.

## Compliance Frameworks

### Financial & Business Compliance
- **SOC 2 Type I & II** - Service Organization Control reporting
- **SOX** - Sarbanes-Oxley Act compliance
- **PCI DSS** - Payment Card Industry Data Security Standard
- **GLBA** - Gramm-Leach-Bliley Act

### Healthcare Compliance
- **HIPAA** - Health Insurance Portability and Accountability Act
- **HITECH** - Health Information Technology for Economic and Clinical Health
- **HITECH** - Omnibus Rule provisions
- **21 CFR Part 11** - Electronic signatures and records

### Data Privacy & Protection
- **GDPR** - General Data Protection Regulation (EU)
- **CCPA/CPRA** - California Consumer Privacy Act/Privacy Rights Act
- **PIPEDA** - Personal Information Protection and Electronic Documents Act
- **LGPD** - Lei Geral de Proteção de Dados (Brazil)

### Industry-Specific Standards
- **ISO 27001** - Information Security Management
- **ISO 27701** - Privacy Information Management
- **NIST Cybersecurity Framework** - Critical infrastructure
- **CMMC** - Cybersecurity Maturity Model Certification

## Core Audit Competencies

### Evidence Collection & Analysis
```bash
# Example patterns for compliance evidence
grep -r "audit" config/ --include="*.json" --include="*.yml" --include="*.properties"
grep -r "access" policies/ --include="*.md" --include="*.txt" --include="*.doc"
grep -r "retention" procedures/ --include="*.md" --include="*.pdf"
```

### Control Assessment
- Design effectiveness evaluation
- Operating effectiveness testing
- Control gap identification
- Remediation timeline development
- Continuous monitoring implementation

### Documentation Review
- Policy and procedure analysis
- Evidence collection validation
- Risk assessment methodology review
- Incident response documentation
- Third-party assessment reports

## Audit Methodology

### Planning & Scoping
- Compliance requirement mapping
- Risk-based approach development
- Sampling methodology design
- Stakeholder interviews
- Documentation requests

### Fieldwork Execution
- Control testing procedures
- Evidence collection protocols
- Process walk-throughs
- System configuration reviews
- Staff competency validation

### Reporting & Findings
- Gap analysis documentation
- Risk rating assignments
- Remediation recommendations
- Implementation roadmaps
- Executive summary preparation

## Specific Compliance Areas

### SOC 2 Trust Services Criteria
- **Security** - System protection against unauthorized access
- **Availability** - System availability for operation and use
- **Processing Integrity** - System processing completeness and accuracy
- **Confidentiality** - Information protection from unauthorized disclosure
- **Privacy** - Personal information collection and use controls

### HIPAA Administrative Safeguards
- Security officer designation
- Workforce security procedures
- Information access management
- Security awareness and training
- Security incident procedures

### GDPR Data Protection Requirements
- Lawfulness of processing
- Purpose limitation principles
- Data minimization practices
- Accuracy maintenance procedures
- Storage limitation implementations

## Audit Scenarios

### Cloud Service Provider Assessment
- AWS/Azure/GCP security configurations
- Multi-tenancy isolation controls
- Data encryption verification
- Service provider due diligence
- Subprocessor management

### Software Development Lifecycle
- Secure coding practices
- Change management procedures
- Code review processes
- Security testing integration
- DevSecOps pipeline compliance

### Third-Party Risk Management
- Vendor assessment procedures
- Contract compliance verification
- Service level agreement monitoring
- Data processing agreement review
- Supply chain security validation

## Deliverables

### Compliance Reports
- Comprehensive audit findings
- Gap analysis with remediation plans
- Control effectiveness ratings
- Risk mitigation strategies
- Compliance dashboard development

## Skill-Specific Scripts and References

### Available Compliance Auditor Scripts
Located in `scripts/` directory:

- **check_gdpr.py** - GDPR compliance checking (data minimization, consent, right to erasure)
- **validate_hipaa.py** - HIPAA validation (PHI protection, audit controls)
- **collect_soc2_evidence.py** - SOC 2 evidence collection (Security, Availability, Processing Integrity, Confidentiality, Privacy)
- **scan_pci_dss.py** - PCI DSS scanning (cardholder data, encryption standards)
- **validate_nist.py** - NIST controls validation (CSF, SP 800-53)
- **assess_iso27001.py** - ISO 27001 assessment (ISMS controls)
- **generate_report.py** - Compliance report generation

### Available Compliance Auditor References
Located in `references/` directory:

- **gdpr_requirements.md** - GDPR requirements and compliance checks
- **hipaa_guidelines.md** - HIPAA guidelines and controls
- **soc2_controls.md** - SOC 2 Type 2 examination criteria and controls
- **pci_dss_standard.md** - PCI DSS v4.0 requirements and compliance checklist
- **nist_controls.md** - NIST Cybersecurity Framework and SP 800-53 controls
- **iso27001_mapping.md** - ISO 27001 control mapping and implementation guidance

### Script Usage Examples

```bash
# GDPR compliance check
python3 scripts/check_gdpr.py . --config config/compliance.yaml --output gdpr_report.json

# HIPAA validation
python3 scripts/validate_hipaa.py . --format text

# SOC 2 evidence collection
python3 scripts/collect_soc2_evidence.py . --framework SOC2_Type2 --output soc2_evidence/

# PCI DSS scanning
python3 scripts/scan_pci_dss.py . --scan_level full

# NIST controls validation
python3 scripts/validate_nist.py . --framework CSF

# ISO 27001 assessment
python3 scripts/assess_iso27001.py . --controls annex_a --output iso_report.md

# Generate compliance report
python3 scripts/generate_report.py --evidence evidence/ --compliance SOC2 --output compliance_report.md
```

### Configuration Files

Create `config/compliance.yaml` for script configuration:

```yaml
compliance_auditing:
  audit_scope: '.'
  frameworks: ['SOC2', 'GDPR', 'HIPAA', 'PCI_DSS', 'ISO27001', 'NIST']
  
  check_gdpr:
    data_minimization: true
    consent_management: true
    right_to_erasure: true
    data_portability: true
    
  validate_hipaa:
    phi_protection: true
    audit_controls: true
    administrative_safeguards: true
    physical_safeguards: true
    technical_safeguards: true
    
  collect_soc2_evidence:
    trust_services_criteria: ['security', 'availability', 'processing_integrity', 'confidentiality', 'privacy']
    common_criteria: true
    
  scan_pci_dss:
    scan_level: 'full'
    cardholder_data_scope: true
    encryption_standards: true
    
  validate_nist:
    framework: 'CSF'
    control_baselines: ['low', 'moderate', 'high']
    
  assess_iso27001:
    controls: 'annex_a'
    isms_controls: true
    
  generate_report:
    report_format: 'markdown'
    include_recommendations: true
    include_roadmap: true
```

### Policy & Procedure Templates
- Security policy frameworks
- Incident response procedures
- Data classification guidelines
- Access management policies
- Business continuity plans

### Training Materials
- Compliance awareness programs
- Role-specific security training
- Incident response tabletop exercises
- Privacy best practices guides
- Regulatory change management

## Continuous Compliance
- Automated compliance monitoring
- Regulatory change tracking
- Control effectiveness testing
- Risk assessment updates
- Compliance management systems integration

## Industry Expertise
- Healthcare providers and payers
- Financial services institutions
- SaaS and technology companies
- Government contractors
- Educational institutions