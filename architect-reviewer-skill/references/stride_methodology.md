# STRIDE Threat Modeling Methodology

## Overview
STRIDE is a threat modeling framework developed by Microsoft to identify security threats in system design.

## STRIDE Categories

### Spoofing (S)

**Definition:** Impersonation of something or someone

**Examples:**
- Spoofed user authentication
- Fake API endpoints
- Email spoofing
- Man-in-the-middle attacks

**Detection:**
```python
# Check for weak authentication
def check_spoofing_risks(auth_mechanism):
    risks = []
    
    if not auth_mechanism.get('mfa_enabled'):
        risks.append('No multi-factor authentication')
    
    if auth_mechanism.get('type') == 'basic':
        risks.append('Basic authentication (use HTTPS with strong auth)')
    
    return risks
```

**Mitigations:**
- Strong authentication (passwords, certificates, biometrics)
- Multi-factor authentication (MFA)
- Certificate pinning
- HTTPS/TLS with valid certificates
- Session management best practices

### Tampering (T)

**Definition:** Modification of data or code

**Examples:**
- Data injection attacks
- Man-in-the-middle modification
- Code injection
- Parameter tampering

**Detection:**
```python
# Check for integrity protection
def check_tampering_protection(data_handling):
    risks = []
    
    if not data_handling.get('digital_signatures'):
        risks.append('No digital signatures for data integrity')
    
    if not data_handling.get('hash_verification'):
        risks.append('No hash verification for data integrity')
    
    return risks
```

**Mitigations:**
- Digital signatures
- Hash verification (SHA-256, SHA-3)
- Checksums
- Access controls on data
- Secure communication channels (TLS)
- Code signing

### Repudiation (R)

**Definition:** Users deny performing actions

**Examples:**
- Denial of transaction
- Audit log tampering
- Non-repudiation failures

**Detection:**
```python
# Check for audit logging
def check_repudiation_prevention(logging_config):
    risks = []
    
    if not logging_config.get('audit_trail'):
        risks.append('No audit trail implemented')
    
    if not logging_config.get('immutable_logs'):
        risks.append('Audit logs can be modified')
    
    return risks
```

**Mitigations:**
- Comprehensive audit logging
- Immutable audit logs
- Digital signatures on logs
- Non-repudiation services
- User activity tracking
- Time synchronization

### Information Disclosure (I)

**Definition:** Exposure of information to unauthorized parties

**Examples:**
- Data leakage
- Unencrypted sensitive data
- Exposed APIs
- Unsecured databases

**Detection:**
```python
# Check for data protection
def check_information_disclosure_risks(data_protection):
    risks = []
    
    if not data_protection.get('encryption_at_rest'):
        risks.append('Data not encrypted at rest')
    
    if not data_protection.get('encryption_in_transit'):
        risks.append('Data not encrypted in transit')
    
    return risks
```

**Mitigations:**
- Encryption (AES-256 for rest, TLS for transit)
- Access controls and least privilege
- Data masking/anonymization
- Secure API design
- Data classification
- Secure disposal

### Denial of Service (D)

**Definition:** Denial of service or access

**Examples:**
- DDoS attacks
- Resource exhaustion
- Application crashes
- Network flooding

**Detection:**
```python
# Check for DoS protections
def check_dos_protections(infra_config):
    risks = []
    
    if not infra_config.get('rate_limiting'):
        risks.append('No rate limiting configured')
    
    if not infra_config.get('load_balancing'):
        risks.append('No load balancing for high availability')
    
    return risks
```

**Mitigations:**
- Rate limiting
- Throttling
- Load balancing
- Redundancy (multi-AZ, multi-region)
- Auto-scaling
- DDoS protection services
- Circuit breakers

### Elevation of Privilege (E)

**Definition:** Gaining higher privileges than authorized

**Examples:**
- Privilege escalation attacks
- Horizontal/vertical privilege escalation
- Broken access control
- Admin interface exposure

**Detection:**
```python
# Check for privilege controls
def check_privilege_controls(auth_config):
    risks = []
    
    if not auth_config.get('least_privilege'):
        risks.append('Least privilege principle not enforced')
    
    if not auth_config.get('role_based_access'):
        risks.append('No role-based access control')
    
    return risks
```

**Mitigations:**
- Principle of least privilege
- Role-based access control (RBAC)
- Privilege separation
- Secure session management
- Regular privilege audits
- Input validation

## Threat Modeling Process

### Step 1: Decompose System

**Identify Elements:**
- Data stores (databases, file systems)
- Data flows (API calls, message queues)
- Processes (services, functions)
- External entities (users, third-party services)

**Diagram Elements:**
```
[User] --(HTTP)--> [Load Balancer] --(HTTP)--> [Web Server]
Web Server --(SQL)--> [Database]
Web Server --(gRPC)--> [Microservice A]
Microservice A --(Kafka)--> [Microservice B]
```

### Step 2: Apply STRIDE

**For Each Element:**
1. Can it be spoofed?
2. Can it be tampered with?
3. Can it repudiate?
4. Can information be disclosed?
5. Can it be denied service?
6. Can privileges be elevated?

**Example Table:**

| Element | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | Elevation |
|---------|------------|------------|---------------|------------------|------|------------|
| Login Form | Yes | No | Yes | Yes | Yes | Yes |
| Database | Yes | Yes | No | Yes | Yes | Yes |
| API Gateway | Yes | Yes | Yes | Yes | Yes | Yes |

### Step 3: Analyze Threats

**Threat Analysis Framework:**
```python
def analyze_threat(threat, likelihood, impact):
    """
    likelihood: low, medium, high
    impact: low, medium, high
    """
    risk_matrix = {
        ('low', 'low'): 'low',
        ('low', 'medium'): 'medium',
        ('low', 'high'): 'high',
        ('medium', 'low'): 'medium',
        ('medium', 'medium'): 'high',
        ('medium', 'high'): 'critical',
        ('high', 'low'): 'high',
        ('high', 'medium'): 'critical',
        ('high', 'high'): 'critical'
    }
    
    return risk_matrix[(likelihood, impact)]
```

### Step 4: Document Findings

**Threat Documentation Template:**
```markdown
## Threat: [Title]

**STRIDE Category:** [Spoofing/Tampering/etc]
**Target:** [Element/Component]
**Likelihood:** [Low/Medium/High]
**Impact:** [Low/Medium/High]
**Risk:** [Calculated Risk]

### Description
[Detailed description of the threat]

### Scenario
[Attack scenario description]

### Mitigation
[Recommended mitigations]

### Verification
[How to verify the mitigation works]
```

## Practical Examples

### Web Application STRIDE Analysis

**System Components:**
1. User Browser
2. Web Server (NGINX)
3. Application Server (Node.js)
4. Database (PostgreSQL)
5. Redis Cache

**Threat Analysis:**

#### User Browser
- **Spoofing:** Phishing attacks
- **Tampering:** Browser extensions
- **Repudiation:** User actions
- **Info Disclosure:** Stored credentials
- **DoS:** Browser freeze
- **Elevation:** N/A

#### Web Server
- **Spoofing:** DNS spoofing
- **Tampering:** Config tampering
- **Repudiation:** Access logs
- **Info Disclosure:** Headers leak
- **DoS:** Resource exhaustion
- **Elevation:** N/A

#### Application Server
- **Spoofing:** Session hijacking
- **Tampering:** Request tampering
- **Repudiation:** Action logs
- **Info Disclosure:** Error messages
- **DoS:** Memory exhaustion
- **Elevation:** Privilege escalation

#### Database
- **Spoofing:** SQL injection
- **Tampering:** Data corruption
- **Repudiation:** Transaction logs
- **Info Disclosure:** Data leaks
- **DoS:** Query overload
- **Elevation:** Admin escalation

### API Gateway STRIDE Analysis

**Components:**
1. API Gateway
2. Microservices
3. Message Queue
4. Event Bus

**Key Threats:**

#### API Gateway
| Threat | Description | Mitigation |
|---------|-------------|------------|
| Spoofing | Fake API tokens | JWT validation, OAuth 2.0 |
| Tampering | Request modification | Message signing |
| Repudiation | Request denial | Request logging |
| Info Disclosure | API key leaks | Secure storage |
| DoS | Rate limit bypass | Throttling, WAF |
| Elevation | Token privilege escalation | Token scopes |

#### Microservice Communication
| Threat | Description | Mitigation |
|---------|-------------|------------|
| Spoofing | Service impersonation | mTLS |
| Tampering | Message tampering | Encryption |
| Repudiation | Message denial | Audit logging |
| Info Disclosure | Data leakage | Encryption |
| DoS | Queue overflow | Backpressure |
| Elevation | Service takeover | Least privilege |

## Tools and Automation

### Microsoft Threat Modeling Tool
- GUI-based threat modeling
- STRIDE automatically applied
- Diagram visualization
- Export to multiple formats

### OWASP Threat Dragon
- Web-based threat modeling
- Collaborative modeling
- STRIDE and DREAD models
- Integration with other tools

### PyTM (Python Threat Modeling)
```python
#!/usr/bin/env python3
from pytm import TM, Actor, Server, Datastore, Dataflow

tm = TM("Threat Model")
tm.description = "Simple Web App"

user = Actor("User", tm)
webapp = Server("Web Application", tm)
db = Datastore("Database", tm)

user_to_webapp = Dataflow(user, webapp, "User Input")
webapp_to_db = Dataflow(webapp, db, "SQL Query")

tm.process()
```

### Custom STRIDE Script

```python
#!/usr/bin/env python3
import yaml
import json

class STRIDEThreatModeler:
    def __init__(self, system_design):
        self.design = system_design
        self.threats = []
    
    def model_threats(self):
        for component in self.design.get('components', []):
            self._check_spoofing(component)
            self._check_tampering(component)
            self._check_repudiation(component)
            self._check_info_disclosure(component)
            self._check_dos(component)
            self._check_elevation(component)
        
        return self.threats
    
    def _check_spoofing(self, component):
        if not component.get('auth_required'):
            self.threats.append({
                'component': component['name'],
                'category': 'Spoofing',
                'severity': 'high',
                'description': 'No authentication required'
            })
    
    # ... other methods ...

if __name__ == '__main__':
    design = {
        'components': [
            {'name': 'API', 'auth_required': True},
            {'name': 'Database', 'auth_required': False}
        ]
    }
    
    modeler = STRIDEThreatModeler(design)
    threats = modeler.model_threats()
    print(json.dumps(threats, indent=2))
```

## Best Practices

1. **Start Early:** Threat model during design, not after implementation
2. **Iterate:** Regularly update threat models as system evolves
3. **Prioritize:** Focus on high-risk, high-impact threats
4. **Document:** Keep detailed threat documentation
5. **Verify:** Test mitigations to ensure they work
6. **Involve Team:** Include security, development, and ops teams

## Common Mistakes

1. **Only Threat Modeling Implementation:** Model during design
2. **Ignoring Business Logic:** Consider non-technical threats
3. **Not Updating:** Keep models current with system changes
4. **Missing Components:** Ensure all elements are included
5. **Overlooking External Dependencies:** Include third-party services

## References

- [Microsoft STRIDE](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling)
- [OWASP Threat Modeling](https://owasp.org/www-community/threat_modeling)
- [Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
