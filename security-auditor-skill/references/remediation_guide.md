# Security Remediation Guide

## Overview
Comprehensive guide for remediating common security vulnerabilities and implementing security best practices.

## Remediation Prioritization

### Severity-Based Prioritization
1. **Critical** - Immediate remediation (within 24 hours)
2. **High** - Urgent remediation (within 1 week)
3. **Medium** - Planned remediation (within 1 month)
4. **Low** - Backlog remediation (within 3 months)

### Risk-Based Approach
Consider:
- Exploitability (Ease of exploitation)
- Impact (Business damage)
- Asset value (Importance of affected system)
- Exposure (Public vs. internal)

## Common Vulnerability Remediations

### SQL Injection

**Detection:**
```sql
-- Vulnerable pattern (detected by scanners)
SELECT * FROM users WHERE id = $user_input
```

**Remediation:**
```python
# Using parameterized queries with SQLAlchemy
from sqlalchemy import text

def get_user(user_id):
    # Safe - parameterized query
    query = text("SELECT * FROM users WHERE id = :id")
    result = db.session.execute(query, {"id": user_id})
    return result.fetchone()

# Using psycopg2 with proper binding
import psycopg2

def get_user(user_id):
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    
    # Safe - parameterized query
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()

# Using ORM
from models import User

def get_user(user_id):
    # Safe - ORM handles escaping
    return User.query.filter_by(id=user_id).first()
```

**Validation:**
```bash
# Use SQLMap to test remediation
sqlmap -u "http://example.com/user?id=1" --level=5 --risk=3
```

### Cross-Site Scripting (XSS)

**Detection:**
```html
<!-- Vulnerable pattern -->
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
```

**Remediation:**
```python
# Input validation with bleach
import bleach

def sanitize_user_input(content):
    # Strip all HTML tags
    return bleach.clean(content, tags=[], strip=True)

# Whitelist approach with allowed tags
def sanitize_rich_text(content):
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a']
    allowed_attrs = {'a': ['href', 'title']}
    return bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

# Template escaping (automatically done in modern frameworks)
# Jinja2 example
from jinja2 import Environment, select_autoescape

env = Environment(
    autoescape=select_autoescape(['html', 'xml'])
)

# Output context-aware encoding
@app.route('/comment')
def show_comment(comment_text):
    return render_template('comment.html', comment=comment_text)
```

**HTTP Headers:**
```python
# Content Security Policy
@app.after_request
def add_csp_header(response):
    csp = "default-src 'self'; script-src 'self' https://trusted.cdn.com;"
    response.headers['Content-Security-Policy'] = csp
    return response
```

### Authentication Bypass

**Detection:**
```python
# Vulnerable pattern
if password == stored_password:  # Weak comparison
```

**Remediation:**
```python
# Secure password hashing
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )

# Secure login with rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and verify_password(password, user.password_hash):
        login_user(user)
        return redirect(url_for('dashboard'))
    
    # Use constant-time comparison to prevent timing attacks
    return 'Invalid credentials', 401
```

### Insecure Direct Object References (IDOR)

**Detection:**
```python
# Vulnerable pattern
@app.route('/documents/<doc_id>')
def get_document(doc_id):
    doc = Document.query.get(doc_id)
    return doc.content  # No authorization check
```

**Remediation:**
```python
# Add authorization checks
@app.route('/documents/<doc_id>')
@login_required
def get_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    # Authorization check
    if doc.owner_id != current_user.id:
        if not current_user.has_permission('read_all_documents'):
            abort(403)
    
    return doc.content

# Alternative: use UUID instead of sequential IDs
import uuid

# Document model
class Document(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Generate secure URLs
document_url = url_for('get_document', document_id=document.id)
```

### Hardcoded Credentials

**Detection:**
```python
# Vulnerable pattern
API_KEY = "sk_live_1234567890abcdef"
DB_PASSWORD = "admin123"
```

**Remediation:**
```python
# Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Use secret management for production
# AWS Secrets Manager example
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# HashiCorp Vault example
import hvac

client = hvac.Client(url='https://vault.example.com')
client.auth.approle.login(
    role_id=os.getenv('VAULT_ROLE_ID'),
    secret_id=os.getenv('VAULT_SECRET_ID')
)

secret = client.read_secret(path='secret/database')['data']['password']
```

### Insecure Deserialization

**Detection:**
```python
# Vulnerable pattern
import pickle

def load_data(data):
    return pickle.loads(data)  # Dangerous!
```

**Remediation:**
```python
# Use JSON instead of pickle
import json

def load_data(data):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        raise ValueError("Invalid data format")

# If pickle must be used, sign the data
import hmac
import hashlib
import pickle

def secure_serialize(data, secret_key):
    pickled = pickle.dumps(data)
    signature = hmac.new(secret_key.encode(), pickled, hashlib.sha256).digest()
    return signature + pickled

def secure_deserialize(data, secret_key):
    signature = data[:32]
    pickled = data[32:]
    
    expected_sig = hmac.new(secret_key.encode(), pickled, hashlib.sha256).digest()
    
    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("Invalid signature")
    
    return pickle.loads(pickled)
```

## Configuration Hardening

### Web Server Security

**Nginx:**
```nginx
# Disable server tokens
server_tokens off;

# Security headers
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
add_header Content-Security-Policy "default-src 'self'";

# SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers off;
```

**Apache:**
```apache
# Disable server signature
ServerSignature Off
ServerTokens Prod

# Security headers
Header always set X-Frame-Options "DENY"
Header always set X-Content-Type-Options "nosniff"
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"

# SSL configuration
SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
SSLCipherSuite HIGH:!aNULL:!MD5
```

### Database Security

**PostgreSQL:**
```sql
-- Remove default test database
DROP DATABASE IF EXISTS test;

-- Create users with least privilege
CREATE USER app_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Enable SSL
ALTER SYSTEM SET ssl = on;
```

**MySQL/MariaDB:**
```sql
-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';

-- Remove test database
DROP DATABASE IF EXISTS test;

-- Set password policy
SET GLOBAL validate_password.policy = STRONG;
SET GLOBAL validate_password.length = 12;

-- Enable SSL
ALTER USER 'root'@'localhost' REQUIRE SSL;
```

### System Hardening

**Ubuntu/Debian:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install and configure firewall
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable

# Disable root login via SSH
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Configure fail2ban
sudo apt install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

**RHEL/CentOS:**
```bash
# Update system
sudo yum update -y

# Configure firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld
sudo firewall-cmd --add-service=ssh --permanent
sudo firewall-cmd --reload

# Harden SSH
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

## Dependency Management

### Python
```bash
# Audit dependencies
pip-audit

# Update dependencies
pip install --upgrade package-name

# Use pip-tools for dependency pinning
pip install pip-tools
pip-compile requirements.in
```

### Node.js
```bash
# Audit dependencies
npm audit

# Fix vulnerabilities
npm audit fix

# Update packages
npm update package-name

# Use npm-check-updates
npx npm-check-updates -u
npm install
```

## Container Security

### Docker
```dockerfile
# Use minimal base image
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Don't run as root
# Don't include secrets in image
# Use multi-stage builds

# Scan image
# docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
#   aquasec/trivy:latest image myapp:latest
```

### Kubernetes
```yaml
# Security context
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

## Monitoring and Logging

### Security Event Logging
```python
import structlog

logger = structlog.get_logger()

# Log authentication events
def log_auth_attempt(username, success, ip_address):
    logger.info(
        "auth_attempt",
        username=username,
        success=success,
        ip_address=ip_address,
        timestamp=datetime.utcnow().isoformat()
    )

# Log sensitive operations
def log_data_access(user_id, resource_type, resource_id):
    logger.warning(
        "data_access",
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        timestamp=datetime.utcnow().isoformat()
    )
```

### Intrusion Detection
```bash
# Install OSSEC
sudo apt install ossec-hids-server

# Configure monitoring
# Monitor critical files
<syscheck>
  <directories check_all="yes">/etc,/usr/bin,/usr/sbin</directories>
</syscheck>

# Configure active response
<active-response>
  <command>host-deny</command>
  <location>local</location>
</active-response>
```

## Testing and Validation

### Automated Security Testing
```yaml
# GitHub Actions workflow
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r ./src
      
      - name: Run Safety
        run: |
          pip install safety
          safety check --json
      
      - name: Run Trivy
        run: |
          docker run --rm -v $PWD:/app aquasec/trivy config /app
```

### Penetration Testing
```bash
# OWASP ZAP automated scan
zap-cli quick-scan --self-contained --start-options '-config api.disablekey=true' http://localhost:8080

# Nmap vulnerability scan
nmap --script vuln -p- target.example.com

# Nikto web scanner
nikto -h http://target.example.com -C all
```

## Remediation Workflow

1. **Identify** - Detect vulnerabilities through scanning
2. **Prioritize** - Assess risk and business impact
3. **Remediate** - Apply fixes based on priority
4. **Validate** - Test that remediation is effective
5. **Document** - Record changes and evidence
6. **Monitor** - Watch for regressions and new issues

## Post-Remediation Validation

### Verification Checklist
- [ ] Vulnerability scanner shows no more findings
- [ ] Manual testing confirms fix is effective
- [ ] Application still functions correctly
- [ ] No performance degradation
- [ ] Security tests pass
- [ ] Documentation updated
- [ ] Team notified of changes

## Resources

- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [SANS Reading Room](https://www.sans.org/reading-room/)
