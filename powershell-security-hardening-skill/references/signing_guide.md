# PowerShell Code Signing Guide

## Overview

This guide covers code signing for PowerShell scripts and modules using Authenticode digital signatures.

## Prerequisites

- Code signing certificate (personal or organizational)
- Windows operating system
- PowerShell 5.1 or later

## Obtaining a Code Signing Certificate

### Internal Certificate Authority

```powershell
# Request code signing certificate from internal CA
# Contact your PKI team for process
# Typical requirements:
# - Code Signing usage extension
# - Basic constraints not critical
# - Key usage: Digital Signature
```

### Public Certificate Authority

```
# Recommended providers:
- DigiCert
- Sectigo
- GlobalSign
- Certum

# Certificate requirements:
- Code Signing certificate (Code Signing)
- Timestamping server access
```

## Certificate Management

### Installing Certificate

```powershell
# Import certificate
$pfxPath = "C:\Certificates\codesign.pfx"
$password = ConvertTo-SecureString "password" -AsPlainText -Force
$cert = Import-PfxCertificate -FilePath $pfxPath -Password $password -CertStoreLocation Cert:\CurrentUser\My

# Verify installation
Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert
```

### Checking Certificate

```powershell
# Get certificate details
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1

$cert | Format-List Subject, Issuer, NotBefore, NotAfter, Thumbprint, EnhancedKeyUsageList

# Check certificate validity
if ($cert.NotBefore -gt [DateTime]::Now) {
    Write-Error "Certificate is not yet valid"
}

if ($cert.NotAfter -lt [DateTime]::Now) {
    Write-Error "Certificate has expired"
}
```

## Signing Scripts

### Basic Script Signing

```powershell
# Get code signing certificate
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1

# Sign script
Set-AuthenticodeSignature -FilePath ".\script.ps1" -Certificate $cert

# Verify signature
Get-AuthenticodeSignature -FilePath ".\script.ps1"
```

### Signing with Timestamp

```powershell
# Sign with timestamp server
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1
$timestampServer = "http://timestamp.digicert.com"

Set-AuthenticodeSignature -FilePath ".\script.ps1" -Certificate $cert -TimestampServer $timestampServer

# Verify timestamp
$signature = Get-AuthenticodeSignature -FilePath ".\script.ps1"
$signature | Format-List Status, SignerCertificate, TimeStamperCertificate
```

### Batch Signing

```powershell
# Sign all PowerShell scripts in directory
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1
$scripts = Get-ChildItem -Path ".\" -Filter "*.ps1" -Recurse

foreach ($script in $scripts) {
    Write-Host "Signing: $($script.FullName)"
    Set-AuthenticodeSignature -FilePath $script.FullName -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
    
    # Verify
    $signature = Get-AuthenticodeSignature -FilePath $script.FullName
    if ($signature.Status -eq 'Valid') {
        Write-Host "  ✓ Signed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Signing failed: $($signature.Status)" -ForegroundColor Red
    }
}
```

## Signing Modules

### Module Signing

```powershell
# Sign entire module
$modulePath = "C:\Modules\MyModule"
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1

# Sign all module files
$files = Get-ChildItem -Path $modulePath -Filter "*.ps*" -File

foreach ($file in $files) {
    Write-Host "Signing: $($file.Name)"
    Set-AuthenticodeSignature -FilePath $file.FullName -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
}

# Verify all files
Get-AuthenticodeSignature -Path "$modulePath\*.ps1"
```

### Module Manifest Signing

```powershell
# Sign module manifest specifically
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1

Set-AuthenticodeSignature -FilePath "C:\Modules\MyModule\MyModule.psd1" -Certificate $cert

# Verify signature can be checked during module import
$signature = Get-AuthenticodeSignature -FilePath "C:\Modules\MyModule\MyModule.psd1"
$signature.Status
```

## Verifying Signatures

### Checking Signature Status

```powershell
# Check single file
$signature = Get-AuthenticodeSignature -FilePath ".\script.ps1"

# Status values: Valid, HashMismatch, NotSigned, NotSupportedFile, UnknownError
switch ($signature.Status) {
    'Valid' { Write-Host "Script is signed and valid" -ForegroundColor Green }
    'HashMismatch' { Write-Host "Script has been modified since signing" -ForegroundColor Red }
    'NotSigned' { Write-Host "Script is not signed" -ForegroundColor Yellow }
    default { Write-Host "Signature status: $($signature.Status)" -ForegroundColor Yellow }
}

# Display signer information
if ($signature.Status -eq 'Valid') {
    Write-Host "Signer: $($signature.SignerCertificate.Subject)"
    Write-Host "Issuer: $($signature.SignerCertificate.Issuer)"
    Write-Host "Valid from: $($signature.SignerCertificate.NotBefore)"
    Write-Host "Valid to: $($signature.SignerCertificate.NotAfter)"
}
```

### Batch Verification

```powershell
# Verify all scripts in directory
$scripts = Get-ChildItem -Path ".\" -Filter "*.ps1" -File

$report = @()

foreach ($script in $scripts) {
    $signature = Get-AuthenticodeSignature -FilePath $script.FullName
    
    $report += [PSCustomObject]@{
        File = $script.Name
        Status = $signature.Status
        Signer = if ($signature.Status -eq 'Valid') { $signature.SignerCertificate.Subject } else { "N/A" }
    }
}

# Display report
$report | Format-Table -AutoSize
```

### Automated Verification

```powershell
# Verify scripts before execution
function Invoke-SignedScript {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ScriptPath
    )
    
    # Check if file exists
    if (-not (Test-Path $ScriptPath)) {
        Write-Error "Script not found: $ScriptPath"
        return
    }
    
    # Verify signature
    $signature = Get-AuthenticodeSignature -FilePath $ScriptPath
    
    switch ($signature.Status) {
        'Valid' {
            Write-Host "Script is signed and valid" -ForegroundColor Green
            # Execute script
            & $ScriptPath @args
        }
        'NotSigned' {
            Write-Warning "Script is not signed: $ScriptPath"
            $continue = Read-Host "Continue anyway? (y/n)"
            if ($continue -eq 'y') {
                & $ScriptPath @args
            }
        }
        'HashMismatch' {
            Write-Error "Script has been modified since signing: $ScriptPath"
            Write-Error "Execution blocked"
        }
        default {
            Write-Error "Invalid signature: $($signature.Status)"
            Write-Error "Execution blocked"
        }
    }
}
```

## Timestamping

### Timestamp Servers

```
# Public timestamp servers:
- http://timestamp.digicert.com
- http://timestamp.sectigo.com
- http://timestamp.globalsign.com/scripts/timstamp.dll
- http://timestamp.comodoca.com/authenticode
```

### Using Timestamps

```powershell
# Sign with timestamp
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1

Set-AuthenticodeSignature -FilePath ".\script.ps1" `
                        -Certificate $cert `
                        -TimestampServer "http://timestamp.digicert.com"

# Verify timestamp
$signature = Get-AuthenticodeSignature -FilePath ".\script.ps1"

if ($signature.TimeStamperCertificate) {
    Write-Host "Timestamp added by: $($signature.TimeStamperCertificate.Issuer)"
    Write-Host "Timestamp URL: $($signature.TimeStamperCertificate.Subject)"
}
else {
    Write-Host "No timestamp found" -ForegroundColor Yellow
}
```

## Best Practices

### Signing Workflow

```powershell
# Recommended signing workflow
1. Develop and test scripts
2. Review and validate all changes
3. Sign scripts in staging environment
4. Test signed scripts
5. Deploy to production

# Automated signing script
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1
$timestampServer = "http://timestamp.digicert.com"

$scripts = Get-ChildItem -Path ".\Scripts" -Filter "*.ps1"

foreach ($script in $scripts) {
    Write-Host "Signing: $($script.Name)"
    Set-AuthenticodeSignature -FilePath $script.FullName -Certificate $cert -TimestampServer $timestampServer -Force
    
    $signature = Get-AuthenticodeSignature -FilePath $script.FullName
    if ($signature.Status -ne 'Valid') {
        Write-Error "Signing failed: $($script.Name)"
    }
}
```

### Certificate Management

```powershell
# Monitor certificate expiration
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1
$daysUntilExpiration = ($cert.NotAfter - [DateTime]::Now).Days

Write-Host "Certificate expires in: $daysUntilExpiration days"

# Set up alert if expiring soon
if ($daysUntilExpiration -lt 30) {
    Write-Warning "Certificate expiring soon! Renew or replace certificate."
}

# Automated backup
function Backup-Certificate {
    $cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1
    $backupPath = "C:\Backups\certificates\codesign_$(Get-Date -Format 'yyyyMMdd').pfx"
    
    Export-PfxCertificate -Cert $cert -FilePath $backupPath -ChainOption BuildChain
    
    Write-Host "Certificate backed up to: $backupPath"
}
```

### Security Considerations

```powershell
# 1. Protect private keys
# - Use hardware security module (HSM) for production
# - Store certificates securely
# - Limit certificate access to authorized users

# 2. Use timestamps
# - Ensures signatures remain valid after certificate expiration
# - Required for some compliance frameworks

# 3. Regularly verify signatures
# - Check signature status periodically
# - Monitor for script modifications

# 4. Use code signing in execution policy
Set-ExecutionPolicy -Scope LocalMachine -ExecutionPolicy AllSigned

# 5. Document signing process
# - Maintain signing procedure documentation
# - Track certificate lifecycle
# - Audit signed files
```

## Troubleshooting

### Common Issues

**Issue:** Certificate not found

```powershell
# Check certificate store
Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object { $_.EnhancedKeyUsageList -contains 'Code Signing' }

# Solution: Import certificate
Import-PfxCertificate -FilePath "certificate.pfx" -CertStoreLocation Cert:\CurrentUser\My
```

**Issue:** Signing fails with access denied

```powershell
# Solution: Run PowerShell as Administrator
# Code signing requires administrative privileges
```

**Issue:** Timestamp server unavailable

```powershell
# Solution: Use alternative timestamp server
$timestampServers = @(
    "http://timestamp.digicert.com",
    "http://timestamp.sectigo.com",
    "http://timestamp.globalsign.com/scripts/timstamp.dll"
)

foreach ($server in $timestampServers) {
    try {
        Set-AuthenticodeSignature -FilePath ".\script.ps1" -Certificate $cert -TimestampServer $server
        Write-Host "Timestamp added using: $server"
        break
    }
    catch {
        Write-Warning "Failed with $server, trying next..."
    }
}
```

## Resources

- [Authenticode Documentation](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)
- [Code Signing Best Practices](https://docs.microsoft.com/en-us/windows/win32/seccrypto/code-signing-best-practices)
- [Timestamp Services](https://docs.microsoft.com/en-us/windows/win32/seccrypto/timestamp-authorization)
