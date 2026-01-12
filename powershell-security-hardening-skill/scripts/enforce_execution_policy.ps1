<#
.SYNOPSIS
    Enforces PowerShell execution policy across the system
.DESCRIPTION
    Sets and validates PowerShell execution policy with scope and verification
.PARAMETER Scope
    Execution policy scope (MachinePolicy, UserPolicy, Process, CurrentUser, LocalMachine)
.PARAMETER Policy
    Execution policy type
.PARAMETER Validate
    Verify the policy was applied correctly
.EXAMPLE
    .\enforce_execution_policy.ps1 -Scope LocalMachine -Policy RemoteSigned -Validate
#>

#Requires -Version 5.1

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('MachinePolicy', 'UserPolicy', 'Process', 'CurrentUser', 'LocalMachine')]
    [string]$Scope,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet('Restricted', 'AllSigned', 'RemoteSigned', 'Unrestricted', 'Bypass', 'Undefined')]
    [string]$Policy,
    
    [Parameter(Mandatory=$false)]
    [switch]$Validate,
    
    [Parameter(Mandatory=$false)]
    [switch]$Audit,
    
    [Parameter(Mandatory=$false)]
    [switch]$LogCompliance
)

function Get-ExecutionPolicyReport {
    Write-Verbose "Retrieving execution policy report"
    
    $scopes = @('MachinePolicy', 'UserPolicy', 'Process', 'CurrentUser', 'LocalMachine')
    $report = @{}
    
    foreach ($scope in $scopes) {
        try {
            $policy = Get-ExecutionPolicy -Scope $scope -ErrorAction Stop
            $report[$scope] = $policy
            Write-Verbose "Scope $scope: $policy"
        }
        catch {
            Write-Warning "Could not retrieve policy for scope: $scope"
            $report[$scope] = 'Error'
        }
    }
    
    return $report
}

function Test-ExecutionPolicyCompliance {
    param(
        [hashtable]$Policies,
        [string]$RequiredScope,
        [string]$RequiredPolicy
    )
    
    Write-Verbose "Testing execution policy compliance"
    
    $effectivePolicy = Get-ExecutionPolicy
    
    Write-Host "`nExecution Policy Report:" -ForegroundColor Cyan
    Write-Host "-------------------------"
    
    foreach ($scope in $Policies.Keys) {
        $policy = $Policies[$scope]
        $isEffective = $false
        
        # Check if this is the effective policy
        $effectiveScopes = @('MachinePolicy', 'UserPolicy', 'Process', 'CurrentUser', 'LocalMachine')
        for ($i = 0; $i -lt $effectiveScopes.Count; $i++) {
            $testScope = $effectiveScopes[$i]
            if ($testScope -eq $scope -and $Policies[$testScope] -ne 'Undefined') {
                $isEffective = $true
                break
            }
            if ($testScope -eq $scope) {
                break
            }
        }
        
        $effectiveMarker = if ($isEffective) { " (Effective)" } else { "" }
        $color = if ($isEffective) { "Green" } else { "Gray" }
        
        Write-Host "$scope`: $policy$effectiveMarker" -ForegroundColor $color
    }
    
    Write-Host "`nEffective Policy: $effectivePolicy" -ForegroundColor Yellow
    
    $compliant = $false
    
    if ($Policies[$RequiredScope] -eq $RequiredPolicy) {
        Write-Host "`n✓ Compliant: $RequiredScope is set to $RequiredPolicy" -ForegroundColor Green
        $compliant = $true
    }
    else {
        Write-Host "`n✗ Non-Compliant: $RequiredScope is $($Policies[$RequiredScope]), expected $RequiredPolicy" -ForegroundColor Red
    }
    
    return $compliant
}

function Set-SecureExecutionPolicy {
    param(
        [string]$TargetScope,
        [string]$TargetPolicy
    )
    
    Write-Verbose "Setting execution policy: $TargetScope -> $TargetPolicy"
    
    # Security check: verify we're not making things less secure
    $currentPolicies = Get-ExecutionPolicyReport
    
    $securePolicies = @('Restricted', 'AllSigned', 'RemoteSigned')
    $insecurePolicies = @('Unrestricted', 'Bypass')
    
    if ($currentPolicies[$TargetScope] -in $securePolicies -and $TargetPolicy -in $insecurePolicies) {
        Write-Warning "Attempting to relax security settings for $TargetScope"
        Write-Warning "Current: $($currentPolicies[$TargetScope]), Requested: $TargetPolicy"
        
        $confirm = Read-Host "Are you sure you want to make this change? (Yes/No)"
        if ($confirm -ne 'Yes') {
            Write-Host "Operation cancelled"
            return $false
        }
    }
    
    try {
        if ($PSCmdlet.ShouldProcess($TargetScope, "Set execution policy to $TargetPolicy")) {
            Set-ExecutionPolicy -Scope $TargetScope -ExecutionPolicy $TargetPolicy -Force -ErrorAction Stop
            Write-Host "Execution policy set successfully" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Error "Failed to set execution policy: $_"
        return $false
    }
}

function Test-ScriptSigning {
    param(
        [string]$ScriptPath
    )
    
    Write-Verbose "Testing script signing"
    
    try {
        $authenticode = Get-AuthenticodeSignature -FilePath $ScriptPath -ErrorAction Stop
        
        $status = $authenticode.Status
        
        switch ($status) {
            'Valid' {
                Write-Host "✓ Script is signed and valid" -ForegroundColor Green
                Write-Host "  Signer: $($authenticode.SignerCertificate.Subject)"
                return $true
            }
            'Unknown' {
                Write-Host "⚠ Script signature status unknown" -ForegroundColor Yellow
                return $false
            }
            'HashMismatch' {
                Write-Host "✗ Script has been modified since signing" -ForegroundColor Red
                return $false
            }
            'NotSigned' {
                Write-Host "✗ Script is not signed" -ForegroundColor Red
                return $false
            }
            default {
                Write-Host "⚠ Script signing error: $status" -ForegroundColor Yellow
                return $false
            }
        }
    }
    catch {
        Write-Error "Could not verify script signing: $_"
        return $false
    }
}

function Get-ExecutionPolicyViolations {
    Write-Verbose "Scanning for execution policy violations"
    
    $violations = @()
    
    # Check common script locations
    $scriptPaths = @(
        "$HOME\Documents\WindowsPowerShell",
        "$HOME\Documents\PowerShell",
        $env:PSModulePath -split ';'
    )
    
    foreach ($path in $scriptPaths) {
        if (Test-Path $path) {
            $scripts = Get-ChildItem -Path $path -Filter "*.ps1" -File -Recurse -ErrorAction SilentlyContinue
            
            foreach ($script in $scripts) {
                $authenticode = Get-AuthenticodeSignature -FilePath $script.FullName -ErrorAction SilentlyContinue
                
                if ($authenticode.Status -eq 'NotSigned') {
                    $violations += [PSCustomObject]@{
                        Path = $script.FullName
                        Issue = "Unsigned script"
                        Status = $authenticode.Status
                    }
                }
                elseif ($authenticode.Status -eq 'HashMismatch') {
                    $violations += [PSCustomObject]@{
                        Path = $script.FullName
                        Issue = "Modified signed script"
                        Status = $authenticode.Status
                    }
                }
            }
        }
    }
    
    return $violations
}

function Export-ComplianceReport {
    param(
        [bool]$Compliant,
        [hashtable]$Policies,
        [object[]]$Violations,
        [string]$OutputPath
    )
    
    Write-Verbose "Exporting compliance report"
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    $report = @"
# PowerShell Execution Policy Compliance Report
Generated: $timestamp

## Summary
Compliance Status: $(if ($Compliant) { "PASS" } else { "FAIL" })
Policy Scope: $Scope
Required Policy: $Policy

## Current Execution Policies

"@
    
    foreach ($policyKey in $Policies.Keys) {
        $report += "- **$policyKey**: $($Policies[$policyKey])`n"
    }
    
    $report += @"

## Security Assessment

**Effective Policy**: $(Get-ExecutionPolicy)

**Compliance**: $(if ($Compliant) { "✓ Compliant" } else { "✗ Non-Compliant" })

"@
    
    if ($Violations.Count -gt 0) {
        $report += @"

## Violations Found: $($Violations.Count)

"@
        
        foreach ($violation in $Violations) {
            $report += @"

- **Path**: $($violation.Path)
  - **Issue**: $($violation.Issue)
  - **Status**: $($violation.Status)

"@
        }
    }
    else {
        $report += @"

## No violations detected

"@
    }
    
    $report += @"

## Recommendations

1. Regularly audit execution policies
2. Sign all production scripts
3. Use Group Policy for enterprise-wide enforcement
4. Monitor script block logs for suspicious activity
5. Implement Just Enough Administration (JEA) for delegation

---

End of Report
"@
    
    if ($OutputPath) {
        Set-Content -Path $OutputPath -Value $report -Encoding UTF8
        Write-Host "Compliance report exported to: $OutputPath"
    }
    
    return $report
}

try {
    Write-Verbose "Starting execution policy enforcement: $Scope -> $Policy"
    
    $currentPolicies = Get-ExecutionPolicyReport
    
    if ($Audit) {
        Write-Host "`nAuditing execution policies..." -ForegroundColor Cyan
        $compliant = Test-ExecutionPolicyCompliance -Policies $currentPolicies -RequiredScope $Scope -RequiredPolicy $Policy
        
        $violations = Get-ExecutionPolicyViolations
        
        if ($LogCompliance) {
            $reportPath = "ExecutionPolicy_Compliance_$(Get-Date -Format 'yyyyMMdd').md"
            Export-ComplianceReport -Compliant $compliant -Policies $currentPolicies -Violations $violations -OutputPath $reportPath
        }
        
        exit (if ($compliant) { 0 } else { 1 })
    }
    
    $success = Set-SecureExecutionPolicy -TargetScope $Scope -TargetPolicy $Policy
    
    if (-not $success) {
        exit 1
    }
    
    if ($Validate) {
        Write-Host "`nVerifying execution policy..." -ForegroundColor Cyan
        Start-Sleep -Seconds 1
        
        $newPolicies = Get-ExecutionPolicyReport
        $verified = Test-ExecutionPolicyCompliance -Policies $newPolicies -RequiredScope $Scope -RequiredPolicy $Policy
        
        if (-not $verified) {
            Write-Error "Execution policy verification failed"
            exit 1
        }
    }
    
    Write-Verbose "Execution policy enforcement completed"
}
catch {
    Write-Error "Execution policy enforcement failed: $_"
    exit 1
}
finally {
    Write-Verbose "Enforce execution policy script completed"
}

Export-ModuleMember -Function Get-ExecutionPolicyReport, Test-ExecutionPolicyCompliance
