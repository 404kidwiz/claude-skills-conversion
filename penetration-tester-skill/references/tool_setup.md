# Penetration Testing Tool Setup Guide

## Overview
Comprehensive guide for setting up penetration testing tools on various platforms.

## Kali Linux Setup

### Basic Kali Installation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install recommended tools
sudo apt install -y \
    nmap \
    nikto \
    gobuster \
    dirb \
    hydra \
    john \
    hashcat \
    metasploit-framework \
    burpsuite \
    owasp-zap \
    sqlmap \
    aircrack-ng \
    wireshark \
    tcpdump \
    git \
    python3-pip
```

### Python Tools Installation

```bash
# Install Python tools
pip3 install \
    sublist3r \
    sqlmap \
    xsser \
    zap-cli \
    impacket \
    requests \
    beautifulsoup4 \
    scapy \
    paramiko
```

### Metasploit Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Initialize Metasploit database
sudo msfdb init

# Start Metasploit
msfconsole

# Update Metasploit
sudo apt install metasploit-framework
```

## Ubuntu/Debian Setup

### System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3 \
    python3-pip \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev
```

### Web Security Tools

```bash
# OWASP ZAP
sudo apt install zaproxy

# Burp Suite Community
sudo apt install burpsuite

# Nikto
sudo apt install nikto

# Nmap
sudo apt install nmap

# SQLMap
pip3 install sqlmap

# XSSer
sudo apt install xsser
```

### Network Security Tools

```bash
# Nmap
sudo apt install nmap

# Masscan
git clone https://github.com/robertdavidgraham/masscan.git
cd masscan
make
sudo make install

# Wireshark
sudo apt install wireshark

# Tcpdump
sudo apt install tcpdump
```

### Password Cracking Tools

```bash
# John the Ripper
sudo apt install john

# Hashcat
sudo apt install hashcat

# Hydra
sudo apt install hydra
```

### Wordlists

```bash
# Install SecLists
git clone https://github.com/danielmiessler/SecLists.git /usr/share/SecLists

# Install rockyou.txt
sudo apt install wordlists
# Or download
wget https://github.com/brannondorsey/naughty-strings/blob/master/naughty-strings.txt
```

## macOS Setup

### Package Manager Setup

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Update brew
brew update
```

### Tools Installation

```bash
# Security tools
brew install \
    nmap \
    wireshark \
    john \
    hashcat \
    hydra \
    burp-suite \
    zap

# Python tools
pip3 install \
    sqlmap \
    xsser \
    sublist3r \
    impacket \
    requests \
    scapy

# Additional tools
brew install --cask \
    wireshark \
    burp-suite \
    zap
```

## Windows Setup

### Chocolatey Setup

```powershell
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### Tools Installation

```powershell
# Install security tools
choco install \
    nmap \
    wireshark \
    burp-suite-free-edition \
    zap \
    putty \
    winscp \
    heidi-sql \
    sqlmap \
    python3 \
    git
```

### WSL2 for Linux Tools

```powershell
# Enable WSL2
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
wsl --set-default-version 2

# Install Ubuntu
wsl --install -d Ubuntu-20.04
```

## Cloud Platforms

### AWS Penetration Testing

```bash
# AWS CLI setup
pip3 install awscli
aws configure

# Install AWS security tools
pip3 install \
    aws-vault \
    scout2 \
    prowler \
    cloudmapper
```

### Azure Penetration Testing

```bash
# Azure CLI setup
pip3 install azure-cli
az login

# Install Azure security tools
pip3 install \
    azurite \
    azure-security-center
```

### GCP Penetration Testing

```bash
# GCP SDK setup
pip3 install google-cloud-sdk
gcloud init

# Install GCP security tools
pip3 install \
    cloud-forensics-utils \
    cloudsql-proxy
```

## Docker Security Tools

### Quick Start Container

```dockerfile
FROM kalilinux/kali-rolling:latest

RUN apt update && apt install -y \
    nmap \
    nikto \
    sqlmap \
    gobuster \
    hydra \
    john \
    hashcat \
    metasploit-framework \
    python3-pip

RUN pip3 install \
    sublist3r \
    xsser \
    impacket \
    scapy

WORKDIR /tools
CMD /bin/bash
```

### Docker Security Tools

```bash
# Run OWASP ZAP in Docker
docker run -u zap -p 8080:8080 -i owasp/zap2docker-stable zap-webswing.sh

# Run Trivy for vulnerability scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image myapp:latest

# Run OWASP Dependency Check
docker run --volume $(pwd):/dependency-check \
    owasp/dependency-check
```

## Tool-Specific Configuration

### OWASP ZAP Configuration

```bash
# Start ZAP
zap-cli quick-scan --self-contained --start-options '-config api.disablekey=true' http://localhost:8080

# ZAP API key
zap-cli api key

# Enable Spider
zap-cli spider http://target.com

# Enable Active Scan
zap-cli active-scan http://target.com

# Generate Report
zap-cli report -o zap_report.html -f html
```

### Burp Suite Configuration

```python
# Burp Suite API setup
# File: burp_config.py
from burp import IBurpExtender
from burp import IHttpListener

class BurpExtender(IBurpExtender, IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        
        callbacks.setExtensionName("Custom Extension")
        callbacks.registerHttpListener(self)
    
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        # Custom logic here
        pass
```

### Nmap Configuration

```bash
# Custom Nmap script
# File: custom_scan.nse
description = [[
  "Custom vulnerability scan"
]]

categories = {"default", "safe", "vuln"}

portrule = function(host, port)
  if port.protocol == "tcp" and port.state == "open" then
    return true
  end
  return false
end

action = function(host, port)
  return "Port is open: " .. port.number
end
```

### Metasploit Configuration

```bash
# Start Metasploit with database
msfdb init
msfconsole

# Configure automated exploitation
msf6 > use exploit/multi/handler
msf6 exploit(multi/handler) > set LHOST 192.168.1.100
msf6 exploit(multi/handler) > set LPORT 4444
msf6 exploit(multi/handler) > exploit -j

# Post-exploitation modules
msf6 > use post/linux/gather/enum_users
msf6 post(linux/gather/enum_users) > set SESSION 1
msf6 post(linux/gather/enum_users) > run
```

## Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc

# Tool paths
export PATH=$PATH:/opt/SecLists
export PATH=$PATH:/opt/metasploit-framework
export PATH=$PATH:/opt/owasp-zap

# Python virtual environment
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/local/bin/virtualenvwrapper.sh

# API keys (use environment variables, never hardcode)
export SHODAN_API_KEY="your_key_here"
export VIRUSTOTAL_API_KEY="your_key_here"
export XSSER_API_KEY="your_key_here"
```

## Wordlists

### Location and Installation

```bash
# SecLists
git clone https://github.com/danielmiessler/SecLists.git /usr/share/SecLists
sudo ln -s /usr/share/SecLists/ /usr/share/wordlists

# Rockyou.txt
sudo apt install wordlists
ln -s /usr/share/wordlists/rockyou.txt.gz /opt/rockyou.txt.gz
gunzip /opt/rockyou.txt.gz

# Custom wordlists
mkdir -p /opt/custom-wordlists
```

### Creating Custom Wordlists

```bash
# Cewl - Custom Word List Generator
cewl http://target.com -w target_words.txt -d 5

# Crunch - Generate custom wordlist
crunch 8 12 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ -o custom.txt

# Hydra with custom wordlist
hydra -l admin -P /opt/custom-wordlists/users.txt target.com http-post-form "/login:user=^USER^&pass=^PASS^"
```

## VPN and Proxy Configuration

### Proxychains

```bash
# Configure /etc/proxychains4.conf
proxychains
socks4 127.0.0.1 9050
socks5 127.0.0.1 9050

# Use with tools
proxychains nmap -sT -p 80,443 target.com
proxychains sqlmap -u http://target.com
```

### Tor Configuration

```bash
# Install Tor
sudo apt install tor

# Start Tor
sudo systemctl start tor

# Configure applications to use Tor
export http_proxy=http://127.0.0.1:9050
export https_proxy=http://127.0.0.1:9050
```

## Virtual Machine Setup

### VirtualBox PenTest Lab

```bash
# Create network
VBoxManage hostonlyif create
VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1 --netmask 255.255.255.0

# Start vulnerable VMs
VBoxManage startvm "metasploitable3" --type headless
VBoxManage startvm "dvwa" --type headless
```

### VMware PenTest Lab

```bash
# Network configuration
vmrun start "/path/to/VM.vmx" nogui

# Snapshot management
vmrun snapshot "/path/to/VM.vmx" take "Before Testing"
vmrun revertToSnapshot "/path/to/VM.vmx" "Before Testing"
```

## Documentation and Reporting

### Markdown Report Template

```markdown
# Penetration Test Report

**Date:** [Date]
**Tester:** [Name]
**Target:** [Target]

## Executive Summary
[High-level summary]

## Methodology
[Testing approach]

## Findings
[Detailed findings]

## Recommendations
[Remediation steps]

## Appendices
[Additional data]
```

### Automated Report Generation

```python
#!/usr/bin/env python3
"""
Generate penetration test reports
"""

def generate_report(findings, output_file):
    report = "# Penetration Test Report\n\n"
    
    for finding in findings:
        report += f"## {finding['title']}\n"
        report += f"**Severity:** {finding['severity']}\n"
        report += f"**Description:** {finding['description']}\n"
        report += f"**Remediation:** {finding['remediation']}\n\n"
    
    with open(output_file, 'w') as f:
        f.write(report)
```

## Updates and Maintenance

### Regular Updates

```bash
# Daily/Weekly update script
#!/bin/bash
# update_tools.sh

echo "Updating Kali Linux..."
sudo apt update && sudo apt upgrade -y

echo "Updating Metasploit..."
cd /opt/metasploit-framework
git pull
bundle install

echo "Updating SecLists..."
cd /usr/share/SecLists
git pull

echo "Updating Python tools..."
pip3 install --upgrade sqlmap xsser sublist3r

echo "Updating complete!"
```

### Backup and Restore

```bash
# Backup configurations
tar -czf pentest_configs_backup.tar.gz \
    ~/.zaproxy \
    ~/.config/BurpSuite \
    ~/.msf4 \
    /opt/custom-wordlists

# Restore
tar -xzf pentest_configs_backup.tar.gz -C /
```

## Troubleshooting

### Common Issues

```bash
# Permission denied
sudo chown -R $USER:$USER /tools

# Python module not found
pip3 install --user <module>

# Database connection failed
sudo systemctl start postgresql
sudo msfdb init

# Port already in use
sudo netstat -tlnp | grep :8080
sudo kill -9 <PID>
```

## References

- [Kali Tools](https://www.kali.org/tools-listing/)
- [OWASP ZAP](https://www.zaproxy.org/)
- [Metasploit Documentation](https://docs.metasploit.com/)
- [Nmap Reference](https://nmap.org/book/man.html)
