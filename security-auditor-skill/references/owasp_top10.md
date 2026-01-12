# OWASP Top 10 Security Risks

## Overview
The OWASP Top 10 represents the most critical web application security risks. This reference provides detection patterns and remediation strategies for each.

## OWASP Top 10 (2021)

### 1. Broken Access Control (A01:2021)

**Description:** Restrictions on what authenticated users are allowed to do are not properly enforced.

**Detection Patterns:**
- Missing authorization checks on sensitive endpoints
- IDOR (Insecure Direct Object References)
- Bypassing access control checks via URL manipulation
- CORS misconfigurations allowing unauthorized access

**Remediation:**
```python
# Secure pattern - always verify authorization
from functools import wraps

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/documents/<doc_id>')
@require_permission('read_document')
def get_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.owner_id != current_user.id:
        abort(403)
    return jsonify(doc.to_dict())
```

**Tools:** OWASP ZAP, Burp Suite, manual code review

### 2. Cryptographic Failures (A02:2021)

**Description:** Cryptography is often incorrectly implemented, leading to exposure of sensitive data.

**Detection Patterns:**
- Weak encryption algorithms (DES, MD5, SHA1)
- Hardcoded encryption keys
- Missing TLS/SSL
- Storing passwords in plaintext

**Remediation:**
```python
# Secure encryption pattern
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

def generate_key(password: bytes, salt: bytes = None) -> bytes:
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def encrypt_data(data: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()

# Password hashing with bcrypt
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

**Tools:** OpenSSL, bcrypt, cryptography library, SSL Labs

### 3. Injection (A03:2021)

**Description:** User-supplied data is not validated, filtered, or sanitized by the application.

**Detection Patterns:**
- SQL injection
- NoSQL injection
- OS command injection
- LDAP injection
- XPath injection

**Remediation:**
```python
# Secure database queries - use parameterized queries
import psycopg2
from psycopg2 import sql

def get_user_by_id(user_id: int):
    conn = psycopg2.connect("dbname=test user=postgres")
    cursor = conn.cursor()
    
    # Safe - parameterized query
    query = sql.SQL("SELECT * FROM users WHERE id = {}").format(
        sql.Literal(user_id)
    )
    cursor.execute(query)
    return cursor.fetchall()

# Using SQLAlchemy with ORM
from sqlalchemy.orm import Session
from sqlalchemy import text

def get_user_by_email(email: str, session: Session):
    # Safe - ORM handles escaping
    return session.query(User).filter(User.email == email).first()

# Using SQLAlchemy Core with bind parameters
def get_users_by_name(name: str):
    stmt = text("SELECT * FROM users WHERE name = :name")
    result = session.execute(stmt, {"name": name})
    return result.fetchall()

# Safe command execution with shlex
import shlex
import subprocess

def safe_exec_command(command_parts: list):
    # Validate and escape command parts
    safe_parts = []
    for part in command_parts:
        safe_parts.append(shlex.quote(part))
    
    return subprocess.run(' '.join(safe_parts), shell=False, check=True)
```

**Tools:** SQLMap, OWASP ZAP, Burp Suite, static analysis tools

### 4. Insecure Design (A04:2021)

**Description:** Design flaws lead to security vulnerabilities that cannot be fixed by implementation alone.

**Detection Patterns:**
- Missing threat modeling
- Insecure business logic
- No rate limiting
- Missing secure defaults
- Trusting client-side controls

**Remediation:**
```python
# Rate limiting implementation
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/login')
@limiter.limit("5 per minute")
def login():
    pass

# Input validation with Pydantic
from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=12, max_length=128)
    username: constr(min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
    
    class Config:
        extra = 'forbid'

# Secure defaults configuration
DEFAULT_SECURITY_CONFIG = {
    'password_min_length': 12,
    'session_timeout': 3600,
    'max_login_attempts': 5,
    'enable_csrf': True,
    'require_https': True
}
```

**Tools:** Threat modeling tools, design review checklists, security by design principles

### 5. Security Misconfiguration (A05:2021)

**Description:** Insecure default configurations, incomplete configurations, open cloud storage, misconfigured HTTP headers.

**Detection Patterns:**
- Default credentials
- Debug mode enabled
- Verbose error messages
- Missing security headers
- Unnecessary services running

**Remediation:**
```python
# Flask security configuration
app = Flask(__name__)
app.config.update({
    'DEBUG': False,
    'TESTING': False,
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax',
    'PERMANENT_SESSION_LIFETIME': timedelta(hours=1)
})

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Disable verbose errors in production
if not app.debug:
    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({'error': 'Internal server error'}), 500
```

**Tools:** Nmap, SSL Labs, security headers checker, configuration linters

### 6. Vulnerable and Outdated Components (A06:2021)

**Description:** Using libraries with known vulnerabilities or failing to update components.

**Detection Patterns:**
- Outdated dependencies
- Known CVEs in dependencies
- Abandoned libraries
- Using alpha/beta versions in production

**Remediation:**
```bash
# Python - pip-audit
pip install pip-audit
pip-audit

# Node.js - npm audit
npm audit
npm audit fix

# Using Dependabot for GitHub
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"

# Poetry dependency management
poetry update
poetry show --tree
```

**Tools:** OWASP Dependency Check, Snyk, npm audit, pip-audit, WhiteSource

### 7. Identification and Authentication Failures (A07:2021)

**Description:** Confirmation of the user's identity, authentication, and session management is compromised.

**Detection Patterns:**
- Weak password policies
- Credential stuffing
- Session fixation
- Brute force attacks
- Multi-factor authentication bypass

**Remediation:**
```python
# Secure authentication with Flask-Login
from flask_login import LoginManager, UserMixin
from flask_bcrypt import Bcrypt

login_manager = LoginManager()
bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    user = User.query.filter_by(email=email).first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return 'Invalid credentials', 401

# Rate limiting for authentication
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per 10 minutes")
def login():
    pass

# Secure session management
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
```

**Tools:** OWASP ZAP, Burp Suite, MFA solutions, password policy tools

### 8. Software and Data Integrity Failures (A08:2021)

**Description:** Code and infrastructure that does not protect against integrity violations.

**Detection Patterns:**
- Unsigned code/packages
- Auto-update without integrity checks
- CI/CD pipeline vulnerabilities
- Deserialization attacks

**Remediation:**
```python
# Verify package signatures
import hashlib
import json

def verify_package_integrity(package_path: str, checksums: dict) -> bool:
    with open(package_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    
    expected_hash = checksums.get(package_path)
    return file_hash == expected_hash

# Safe deserialization
import json

def safe_deserialize(data: str):
    # Use JSON instead of pickle for security
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON data") from e

# CI/CD security checks
# .github/workflows/security-checks.yml
name: Security Checks
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run security scan
        run: |
          pip install bandit
          bandit -r ./src
```

**Tools:** GPG, checksum verification, SLSA framework, Sigstore

### 9. Security Logging and Monitoring Failures (A09:2021)

**Description:** Logging, detecting, escalating, and responding to active breaches is not effective.

**Detection Patterns:**
- Insufficient logging
- No intrusion detection
- Missing audit trails
- Logs stored without protection

**Remediation:**
```python
# Secure logging with structlog
import structlog
import logging

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Log security events
@app.before_request
def log_request():
    log_data = {
        'method': request.method,
        'path': request.path,
        'ip': request.remote_addr,
        'user_agent': request.user_agent.string
    }
    
    if current_user.is_authenticated:
        log_data['user_id'] = current_user.id
    
    logger.info("api_request", **log_data)

# Alerting on security events
def log_security_event(event_type: str, details: dict):
    log_entry = {
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat(),
        'severity': 'high',
        **details
    }
    
    logger.warning("security_event", **log_entry)
    
    # Send alert (example with Sentry)
    # capture_message(f"Security event: {event_type}", extra=log_entry)
```

**Tools:** ELK Stack, Splunk, Graylog, SIEM solutions, AWS CloudTrail

### 10. Server-Side Request Forgery (A10:2021)

**Description:** Server-side request forgery occurs when a web application is fetching a remote resource without validating the user-supplied URL.

**Detection Patterns:**
- Fetching arbitrary URLs
- SSRF in file upload features
- Metadata service access
- Internal network scanning

**Remediation:**
```python
# Validate and sanitize URLs
from urllib.parse import urlparse
import ipaddress

ALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']

def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        
        if parsed.scheme not in ['http', 'https']:
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False
        
        # Block internal IP addresses
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
        
        # Allow only whitelisted domains
        if hostname not in ALLOWED_DOMAINS:
            return False
        
        return True
    except (ValueError, TypeError):
        return False

@app.route('/api/fetch')
def fetch_url():
    url = request.args.get('url')
    
    if not is_valid_url(url):
        return 'Invalid URL', 400
    
    # Use httpx with timeout and size limits
    import httpx
    with httpx.Client(timeout=10, max_redirects=3) as client:
        response = client.get(url, follow_redirects=True)
        return response.content

# Alternative: Use allowlist approach
ALLOWED_URLS = {
    'user_profile': 'https://api.example.com/v1/users/{id}',
    'product_info': 'https://api.example.com/v1/products/{id}'
}

def fetch_allowed_resource(resource_type: str, resource_id: str):
    template = ALLOWED_URLS.get(resource_type)
    if not template:
        raise ValueError(f"Unknown resource type: {resource_type}")
    
    url = template.format(id=resource_id)
    # Fetch URL...
```

**Tools:** OWASP SSRF Testing Guide, Burp Suite, custom validation scripts

## Additional OWASP Resources

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)

## Quick Reference Checklist

- [ ] Input validation on all user inputs
- [ ] Parameterized queries for database access
- [ ] Proper authentication and session management
- [ ] Authorization checks on all sensitive operations
- [ ] Secure cryptographic implementations
- [ ] Error handling without information disclosure
- [ ] Security headers configured
- [ ] Dependency vulnerability scanning
- [ ] Logging and monitoring in place
- [ ] Regular security testing and code reviews
