# Architecture Security Checklist

## Overview
Comprehensive security checklist for reviewing software architecture and design.

## General Security Principles

### Security by Design
- [ ] Security is considered from the beginning
- [ ] Threat modeling conducted during design phase
- [ ] Security requirements documented
- [ ] Security testing included in development lifecycle
- [ ] Regular security reviews scheduled

### Defense in Depth
- [ ] Multiple layers of security controls
- [ ] No single point of failure in security
- [ ] Defense at network, application, and data levels
- [ ] Redundant security measures
- [ ] Fail-safe mechanisms

### Principle of Least Privilege
- [ ] Users have minimum necessary permissions
- [ ] Services run with minimal privileges
- [ ] Third-party integrations scoped properly
- [ ] Admin privileges separated from user privileges
- [ ] Regular privilege audits conducted

## Authentication and Authorization

### Authentication Design
- [ ] Strong password policies enforced
- [ ] Password hashing with bcrypt, Argon2, or scrypt
- [ ] Multi-factor authentication (MFA) implemented
- [ ] Session management secure (timeout, rotation)
- [ ] Secure password reset mechanism
- [ ] Account lockout after failed attempts
- [ ] CAPTCHA for sensitive operations
- [ ] OAuth 2.0 / OpenID Connect for social login
- [ ] JWT tokens properly signed and validated
- [ ] Refresh token mechanism implemented

### Authorization Design
- [ ] Role-based access control (RBAC)
- [ ] Attribute-based access control (ABAC) if needed
- [ ] Authorization checks on all endpoints
- [ ] Admin interfaces protected
- [ ] API access properly scoped
- [ ] Database access restricted
- [ ] Server access controlled
- [ ] Third-party access limited and monitored

### Identity Management
- [ ] Centralized identity management
- [ ] Single sign-on (SSO) where appropriate
- [ ] User lifecycle management (onboarding/offboarding)
- [ ] Identity federation considered
- [ ] User consent for data processing
- [ ] Right to erasure implemented

## Data Protection

### Data Classification
- [ ] Data properly classified (public, internal, confidential, restricted)
- [ ] Classification labels documented
- [ ] Handling procedures for each classification
- [ ] Retention policies defined
- [ ] Disposal procedures secure

### Encryption
- [ ] Data encrypted at rest (AES-256)
- [ ] Data encrypted in transit (TLS 1.2+)
- [ ] Encryption keys properly managed
- [ ] Key rotation policy in place
- [ ] Hardware security modules (HSM) for critical keys
- [ ] Encryption disabled for non-sensitive data where appropriate

### Data Storage
- [ ] Sensitive data isolated
- [ ] Database access controlled
- [ ] Backup encryption implemented
- [ ] Data masking for non-production
- [ ] Secure deletion procedures
- [ ] Data minimization principles followed

## Network Security

### Network Architecture
- [ ] Network segmentation implemented
- [ ] DMZ for public-facing services
- [ ] Private subnets for internal services
- [ ] VPC/VNet isolation
- [ ] Network access control lists (ACLs)
- [ ] Software-defined networking controls

### Firewall Configuration
- [ ] Default-deny firewall rules
- [ ] Only necessary ports open
- [ ] Inbound and outbound filtering
- [ ] Web Application Firewall (WAF) deployed
- [ ] DDoS protection enabled
- [ ] Regular firewall rule reviews

### Secure Communication
- [ ] HTTPS/TLS enforced for all services
- [ ] Valid certificates from trusted CAs
- [ ] HSTS enabled
- [ ] Certificate pinning where appropriate
- [ ] Internal services use mTLS
- [ ] API gateways enforce security policies

## Application Security

### Input Validation
- [ ] All user inputs validated
- [ ] Input sanitization implemented
- [ ] Type checking enforced
- [ ] Length limits on inputs
- [ ] Whitelist validation preferred over blacklist
- [ ] File upload restrictions (type, size, content)

### Output Encoding
- [ ] HTML output encoded
- [ ] JavaScript output encoded
- [ ] URL encoding where needed
- [ ] JSON output properly formatted
- [ ] No sensitive data in error messages
- [ ] Generic error messages to users

### Secure Coding
- [ ] Parameterized queries for database access
- [ ] Prepared statements used
- [ ] ORM for database operations
- [ ] No eval() or similar dangerous functions
- [ ] No hardcoded credentials
- [ ] Dependency vulnerability scanning

### API Security
- [ ] API versioning implemented
- [ ] Rate limiting configured
- [ ] API key authentication
- [ ] OAuth 2.0 / JWT for authentication
- [ ] API documentation security reviewed
- [ ] API gateway for centralized controls
- [ ] CORS properly configured

## Infrastructure Security

### Cloud Security
- [ ] Cloud security groups properly configured
- [ ] IAM roles with least privilege
- [ ] Encryption at rest enabled for cloud storage
- [ ] Cloud security services enabled (GuardDuty, etc.)
- [ ] Cloud configuration compliance checked
- [ ] Multi-factor authentication for cloud console

### Container Security
- [ ] Minimal base images used
- [ ] Containers run as non-root user
- [ ] Read-only root filesystem where possible
- [ ] Resource limits configured
- [ ] Container image scanning
- [ ] Kubernetes security policies (PodSecurityPolicy)
- [ ] Secrets management for containers

### Server Hardening
- [ ] Operating system updated regularly
- [ ] Unnecessary services disabled
- [ ] Secure SSH configuration
- [ ] Host-based firewalls
- [ ] Intrusion detection/prevention systems
- [ ] File integrity monitoring
- [ ] Log monitoring enabled

## Logging and Monitoring

### Logging
- [ ] Comprehensive logging implemented
- [ ] Security events logged
- [ ] Log format standardized
- [ ] Log rotation configured
- [ ] Secure log storage (encrypted, access-controlled)
- [ ] Logs backed up regularly
- [ ] No sensitive data in logs

### Monitoring
- [ ] Real-time security monitoring
- [ ] Alerting for suspicious activities
- [ ] Performance monitoring
- [ ] Anomaly detection
- [ ] Uptime monitoring
- [ ] Network traffic monitoring

### Incident Response
- [ ] Incident response plan documented
- [ ] Response team identified
- [ ] Escalation procedures defined
- [ ] Communication plan in place
- [ ] Post-incident reviews conducted
- [ ] Lessons learned documented

## Compliance and Governance

### Regulatory Compliance
- [ ] GDPR requirements addressed
- [ ] PCI DSS requirements met (if applicable)
- [ ] HIPAA requirements met (if applicable)
- [ ] SOC 2 controls implemented (if applicable)
- [ ] Industry-specific compliance verified
- [ ] Regular compliance audits scheduled

### Privacy
- [ ] Privacy policy published
- [ ] Consent management implemented
- [ ] Data subject rights supported
- [ ] Cookie banners compliant
- [ ] Data processing agreements in place
- [ ] Privacy impact assessments conducted

### Security Governance
- [ ] Security policies documented
- [ ] Security standards defined
- [ ] Security procedures established
- [ ] Security training provided
- [ ] Security awareness programs
- [ ] Regular security reviews

## DevSecOps

### Secure CI/CD
- [ ] Code review process
- [ ] Automated security testing in CI/CD
- [ ] Secret scanning for commits
- [ ] Dependency vulnerability scanning
- [ ] Container image scanning
- [ ] Infrastructure as code security checks
- [ ] Rollback procedures

### Deployment Security
- [ ] Production deployment approvals
- [ ] Blue/green deployments
- [ ] Canary releases
- [ ] Post-deployment verification
- [ ] Change management process
- [ ] Deployment documentation

## Third-Party and Vendor Security

### Vendor Management
- [ ] Vendor security assessments conducted
- [ ] Contracts include security requirements
- [ ] SLAs include security metrics
- [ ] Vendor access monitored
- [ ] Regular vendor reviews

### Supply Chain Security
- [ ] Dependency vetting process
- [ ] SBOM (Software Bill of Materials) maintained
- [ ] Vulnerability monitoring for dependencies
- [ ] Alternative vendors identified
- [ ] Supply chain incident response plan

## Physical Security

### Access Control
- [ ] Physical access controls implemented
- [ ] Badge/card systems used
- [ ] Visitor management
- [ ] Secure area designation
- [ ] Access logs maintained

### Equipment Security
- [ ] Server rooms locked
- [ ] Workstation security policies
- [ ] Mobile device management
- [ ] Laptop encryption required
- [ ] Secure disposal procedures

## Business Continuity

### Disaster Recovery
- [ ] Disaster recovery plan documented
- [ ] Backup strategy implemented
- [ ] Offsite backups
- [ ] Backup encryption
- [ ] Regular backup testing
- [ ] RTO and RPO defined

### High Availability
- [ ] Redundant infrastructure
- [ ] Load balancing
- [ ] Geographic distribution
- [ ] Failover procedures tested
- [ ] Performance under load verified

## Risk Management

### Risk Assessment
- [ ] Risk identification process
- [ ] Risk analysis methodology
- [ ] Risk scoring system
- [ ] Risk treatment decisions
- [ ] Risk register maintained
- [ ] Regular risk reviews

### Security Testing
- [ ] Regular penetration testing
- [ ] Vulnerability scanning schedule
- [ ] Code security reviews
- [ ] Application security testing
- [ ] Red team exercises
- [ ] Third-party security assessments

## Documentation

### Security Documentation
- [ ] Architecture documentation
- [ ] Security controls documented
- [ ] Incident response procedures
- [ ] Playbooks for common incidents
- [ ] Contact information documented
- [ ] Regular documentation updates

### Knowledge Sharing
- [ ] Security knowledge base
- [ ] Training materials available
- [ ] Threat intelligence sharing
- [ ] Industry threat feeds monitored
- [ ] Security community participation

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls)
- [Cloud Security Alliance](https://cloudsecurityalliance.org/)
