<#
.SYNOPSIS
    Signs PowerShell modules and scripts with code signing certificates
.DESCRIPTION
    Authenticode signing with certificate management and timestamping
.PARAMETER Path
    Path to file(s) to sign
.PARAMETER Certificate
    Certificate thumbprint or file path
.PARAMETER TimestampServer
    Timestamp server URL
.PARAMETER Verify
    Verify signatures after signing
.EXAMPLE
    .\sign_module.ps1 -Path "./MyModule" -Certificate "ABC123..." -TimestampServer "http://timestamp.digicert.com"
#>

#Requires -Version 5.1

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [ValidateScript({
        if (-not (Test-Path $_)) {
            throw "Path does not exist: $_"
        }
        $true
    })]
    [string]$Path,
    
    [Parameter(Mandatory=$false)]
    [string]$Certificate,
    
    [Parameter(Mandatory=$false)]
    [string]$CertificatePath,
    
    [Parameter(Mandatory=$false)]
    [securestring]$CertificatePassword,
    
    [Parameter(Mandatory=$false)]
    [string]$TimestampServer = "http://timestamp.digicert.com",
    
    [Parameter(Mandatory=$false)]
    [switch]$Recurse,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verify,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

function Get-CodeSigningCertificates {
    Write-Verbose "Retrieving available code signing certificates"
    
    try {
        $certs = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert -ErrorAction Stop
        
        if (-not $certs) {
            Write-Warning "No code signing certificates found in CurrentUser store"
        }
        
        return $certs
    }
    catch {
        Write-Error "Failed to retrieve certificates: $_"
        return @()
    }
}

function Select-CodeSigningCertificate {
    param(
        [string]$Thumbprint,
        [string]$CertPath
    )
    
    Write-Verbose "Selecting code signing certificate"
    
    if ($Thumbprint) {
        try {
            $cert = Get-ChildItem -Path "Cert:\CurrentUser\My\$Thumbprint" -ErrorAction Stop
            
            if (-not $cert.EnhancedKeyUsageList -contains 'Code Signing') {
                Write-Error "Certificate is not valid for code signing"
                return $null
            }
            
            Write-Host "Using certificate: $($cert.Subject)" -ForegroundColor Green
            return $cert
        }
        catch {
            Write-Error "Certificate not found: $Thumbprint"
            return $null
        }
    }
    
    if ($CertPath) {
        try {
            $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
            
            if ($CertificatePassword) {
                $cert.Import($CertPath, $CertificatePassword, [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::DefaultKeySet)
            }
            else {
                $cert.Import($CertPath)
            }
            
            Write-Host "Using certificate from file: $CertPath" -ForegroundColor Green
            return $cert
        }
        catch {
            Write-Error "Failed to load certificate from file: $_"
            return $null
        }
    }
    
    # Auto-select first available certificate
    $certs = Get-CodeSigningCertificates
    
    if ($certs.Count -eq 1) {
        Write-Host "Auto-selecting certificate: $($certs[0].Subject)" -ForegroundColor Green
        return $certs[0]
    }
    elseif ($certs.Count -gt 1) {
        Write-Host "Multiple certificates found:" -ForegroundColor Cyan
        
        $certs | ForEach-Object {
            Write-Host "  [$($_.Thumbprint)] $($_.Subject)" -ForegroundColor Yellow
        }
        
        $selection = Read-Host "Select certificate by thumbprint"
        
        $selected = $certs | Where-Object { $_.Thumbprint -eq $selection }
        
        if ($selected) {
            return $selected
        }
        else {
            Write-Error "Invalid selection"
            return $null
        }
    }
    else {
        Write-Error "No code signing certificates available"
        return $null
    }
}

function Get-FilesToSign {
    param(
        [string]$BasePath,
        [bool]$Recursive
    )
    
    Write-Verbose "Finding files to sign"
    
    $files = @()
    
    if ((Get-Item $BasePath) -is [System.IO.DirectoryInfo]) {
        if ($Recursive) {
            $files = Get-ChildItem -Path $BasePath -Filter "*.ps1" -File -Recurse
            $files += Get-ChildItem -Path $BasePath -Filter "*.psm1" -File -Recurse
            $files += Get-ChildItem -Path $BasePath -Filter "*.psd1" -File -Recurse
        }
        else {
            $files = Get-ChildItem -Path $BasePath -Filter "*.ps*" -File
        }
    }
    else {
        $files = Get-Item $BasePath
    }
    
    $files = $files | Where-Object { $_.Extension -in @('.ps1', '.psm1', '.psd1') }
    
    Write-Host "Found $($files.Count) files to sign" -ForegroundColor Cyan
    return $files
}

function Sign-FileInternal {
    param(
        [System.IO.FileInfo]$File,
        [System.Security.Cryptography.X509Certificates.X509Certificate2]$Cert,
        [string]$TimestampUrl,
        [bool]$ForceSign
    )
    
    Write-Verbose "Signing file: $($File.Name)"
    
    try {
        # Check if already signed
        $signature = Get-AuthenticodeSignature -FilePath $File.FullName -ErrorAction SilentlyContinue
        
        if ($signature.Status -eq 'Valid' -and -not $ForceSign) {
            Write-Host "  → Already signed: $($File.Name)" -ForegroundColor Gray
            return $true
        }
        
        if ($PSCmdlet.ShouldProcess($File.FullName, "Sign with certificate $($Cert.Subject)")) {
            Set-AuthenticodeSignature -FilePath $File.FullName -Certificate $Cert -TimestampServer $TimestampUrl -Force:$ForceSign -ErrorAction Stop
            
            Write-Host "  ✓ Signed: $($File.Name)" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "  ✗ Failed: $($File.Name)" -ForegroundColor Red
        Write-Error "    $($_.Exception.Message)"
        return $false
    }
}

function Test-FileSignature {
    param(
        [System.IO.FileInfo]$File
    )
    
    Write-Verbose "Verifying signature: $($File.Name)"
    
    try {
        $signature = Get-AuthenticodeSignature -FilePath $File.FullName -ErrorAction Stop
        
        switch ($signature.Status) {
            'Valid' {
                Write-Host "  ✓ Valid: $($File.Name)" -ForegroundColor Green
                Write-Host "    Signer: $($signature.SignerCertificate.Subject)"
                Write-Host "    Date: $($signature.SignerCertificate.NotBefore) - $($signature.SignerCertificate.NotAfter)"
                return $true
            }
            'HashMismatch' {
                Write-Host "  ✗ Hash mismatch: $($File.Name)" -ForegroundColor Red
                return $false
            }
            'NotSigned' {
                Write-Host "  ⚠ Not signed: $($File.Name)" -ForegroundColor Yellow
                return $false
            }
            default {
                Write-Host "  ⚠ $($signature.Status): $($File.Name)" -ForegroundColor Yellow
                return $false
            }
        }
    }
    catch {
        Write-Error "Failed to verify signature for $($File.Name): $_"
        return $false
    }
}

function Generate-SigningReport {
    param(
        [System.IO.FileInfo[]]$Files,
        [hashtable]$Results
    )
    
    Write-Verbose "Generating signing report"
    
    $signedCount = ($Results.Values | Where-Object { $_ -eq $true }).Count
    $total = $Files.Count
    
    $reportPath = "SigningReport_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
    
    $report = @"
PowerShell Module Signing Report
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Summary
-------
Total Files: $total
Signed: $signedCount
Failed: $($total - $signedCount)

Details
-------

"@
    
    foreach ($file in $Files) {
        $status = if ($Results[$file.FullName]) { "✓ Signed" } else { "✗ Failed" }
        $report += "$status - $($file.FullName)`n"
    }
    
    $report += @"

Certificate Information
----------------------
Subject: $cert.Subject
Issuer: $cert.Issuer
Valid From: $cert.NotBefore
Valid To: $cert.NotAfter
Thumbprint: $cert.Thumbprint

"@
    
    Set-Content -Path $reportPath -Value $report -Encoding UTF8
    Write-Host "`nReport saved to: $reportPath"
}

try {
    Write-Verbose "Starting module signing process"
    
    $cert = Select-CodeSigningCertificate -Thumbprint $Certificate -CertPath $CertificatePath
    
    if (-not $cert) {
        exit 1
    }
    
    # Check certificate validity
    if ($cert.NotBefore -gt [DateTime]::Now) {
        Write-Error "Certificate is not yet valid"
        exit 1
    }
    
    if ($cert.NotAfter -lt [DateTime]::Now) {
        Write-Error "Certificate has expired"
        exit 1
    }
    
    $files = Get-FilesToSign -BasePath $Path -Recursive $Recurse
    
    if ($files.Count -eq 0) {
        Write-Host "No files to sign" -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "`nSigning files..." -ForegroundColor Cyan
    Write-Host "--------------------"
    
    $results = @{}
    
    foreach ($file in $files) {
        $success = Sign-FileInternal -File $file -Cert $cert -TimestampUrl $TimestampServer -ForceSign $Force
        $results[$file.FullName] = $success
    }
    
    if ($Verify) {
        Write-Host "`nVerifying signatures..." -ForegroundColor Cyan
        Write-Host "-----------------------"
        
        foreach ($file in $files) {
            Test-FileSignature -File $file
        }
    }
    
    $signedCount = ($results.Values | Where-Object { $_ -eq $true }).Count
    Write-Host "`nSigning Summary:" -ForegroundColor Cyan
    Write-Host "----------------"
    Write-Host "Total: $($files.Count)"
    Write-Host "Signed: $signedCount"
    Write-Host "Failed: $($files.Count - $signedCount)"
    
    if ($signedCount -eq $files.Count) {
        Write-Host "`n✓ All files signed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "`n⚠ Some files failed to sign" -ForegroundColor Yellow
    }
    
    Write-Verbose "Module signing completed"
}
catch {
    Write-Error "Module signing failed: $_"
    exit 1
}
finally {
    Write-Verbose "Sign module script completed"
}

Export-ModuleMember -Function Get-CodeSigningCertificates, Select-CodeSigningCertificate
