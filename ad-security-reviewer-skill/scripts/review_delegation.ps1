<#
.SYNOPSIS
    Reviews and analyzes Active Directory delegation configurations

.DESCRIPTION
    This script reviews AD delegation settings to identify excessive permissions,
    potential security risks, and unauthorized delegation.

.PARAMETER SearchBase
    The distinguished name of the OU to review (default: entire domain)

.PARAMETER MaxDepth
    Maximum depth to search in OU hierarchy (default: 10)

.PARAMETER ReportPath
    Path to save the delegation review report (default: .\delegation_review.html)

.EXAMPLE
    .\review_delegation.ps1 -SearchBase "OU=Users,DC=example,DC=com"
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SearchBase = (Get-ADDomain).DistinguishedName,

    [Parameter(Mandatory=$false)]
    [int]$MaxDepth = 10,

    [Parameter(Mandatory=$false)]
    [string]$ReportPath = ".\delegation_review.html",

    [Parameter(Mandatory=$false)]
    [string]$LogPath = ".\delegation_review.log"
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet('INFO', 'WARNING', 'ERROR')]
        [string]$Level = 'INFO'
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    Write-Host $logEntry
    Add-Content -Path $LogPath -Value $logEntry
}

function Test-ADModule {
    try {
        Import-Module ActiveDirectory -ErrorAction Stop
        return $true
    }
    catch {
        Write-Log "Active Directory module not available" -Level 'ERROR'
        return $false
    }
}

function Get-ADObjectDelegation {
    param(
        [string]$DistinguishedName
    )

    try {
        $acl = Get-Acl -Path ("AD:\\" + $DistinguishedName)
        $delegations = @()

        foreach ($ace in $acl.Access) {
            # Skip inherited permissions and system accounts
            if ($ace.IsInherited) { continue }
            if ($ace.IdentityReference -like "*S-1-5-32-*") { continue }
            if ($ace.IdentityReference -like "*BUILTIN*") { continue }

            # Check for delegation rights
            $delegationRights = @()
            if ($ace.ActiveDirectoryRights -match 'GenericAll|Write|ExtendedRight') {
                $delegationRights += 'Read/Write'
            }

            if ($delegationRights.Count -gt 0) {
                $identity = $ace.IdentityReference.Value

                # Resolve identity to get details
                $account = try {
                    if ($identity -match '^S-') {
                        Get-ADObject -Identity $identity -Properties objectClass,objectGUID
                    } else {
                        $identityParts = $identity -split '\\'
                        $accountName = $identityParts[-1]
                        $domain = if ($identityParts.Length -gt 1) { $identityParts[0] }

                        if ($domain) {
                            Get-ADUser -Filter { SamAccountName -eq $accountName } -Server $domain -ErrorAction SilentlyContinue
                        } else {
                            Get-ADUser -Filter { SamAccountName -eq $accountName } -ErrorAction SilentlyContinue
                        }
                    }
                }
                catch {
                    $null
                }

                $accountType = if ($account) {
                    $account.objectClass
                } else {
                    'Unknown'
                }

                $delegations += [PSCustomObject]@{
                    ObjectDN = $DistinguishedName
                    ObjectType = 'AD Object'
                    Trustee = $identity
                    TrusteeType = $accountType
                    Rights = $ace.ActiveDirectoryRights
                    AccessType = $ace.AccessControlType
                    Inherited = $ace.IsInherited
                    DelegationType = $delegationRights -join ', '
                }
            }
        }

        return $delegations
    }
    catch {
        Write-Log "Failed to get delegation for $DistinguishedName`: $($_.Exception.Message)" -Level 'ERROR'
        return @()
    }
}

function Get-OUDelegations {
    param(
        [string]$SearchBase,
        [int]$MaxDepth
    )

    $delegations = @()

    try {
        $ous = Get-ADOrganizationalUnit -Filter * -SearchBase $SearchBase -SearchScope Subtree -Server $env:USERDNSDOMAIN

        foreach ($ou in $ous) {
            Write-Log "Reviewing delegation for OU: $($ou.Name)" -Level 'INFO'

            $ouDelegations = Get-ADObjectDelegation -DistinguishedName $ou.DistinguishedName

            if ($ouDelegations.Count -gt 0) {
                $delegations += $ouDelegations
            }
        }
    }
    catch {
        Write-Log "Failed to get OU delegations`: $($_.Exception.Message)" -Level 'ERROR'
    }

    return $delegations
}

function Get-UserDelegations {
    param(
        [string]$SearchBase
    )

    $delegations = @()

    try {
        $users = Get-ADUser -Filter * -SearchBase $SearchBase -SearchScope Subtree -Server $env:USERDNSDOMAIN

        foreach ($user in $users) {
            Write-Log "Reviewing delegation for user: $($user.SamAccountName)" -Level 'INFO'

            $userDelegations = Get-ADObjectDelegation -DistinguishedName $user.DistinguishedName

            if ($userDelegations.Count -gt 0) {
                $delegations += $userDelegations
            }
        }
    }
    catch {
        Write-Log "Failed to get user delegations`: $($_.Exception.Message)" -Level 'ERROR'
    }

    return $delegations
}

function Get-GroupDelegations {
    param(
        [string]$SearchBase
    )

    $delegations = @()

    try {
        $groups = Get-ADGroup -Filter * -SearchBase $SearchBase -SearchScope Subtree -Server $env:USERDNSDOMAIN

        foreach ($group in $groups) {
            Write-Log "Reviewing delegation for group: $($group.Name)" -Level 'INFO'

            $groupDelegations = Get-ADObjectDelegation -DistinguishedName $group.DistinguishedName

            if ($groupDelegations.Count -gt 0) {
                $delegations += $groupDelegations
            }
        }
    }
    catch {
        Write-Log "Failed to get group delegations`: $($_.Exception.Message)" -Level 'ERROR'
    }

    return $delegations
}

function Test-DelegationSecurity {
    param(
        [PSCustomObject]$Delegation
    )

    $issues = @()

    # Check for GenericAll
    if ($Delegation.Rights -match 'GenericAll') {
        $issues += "Has GenericAll rights (full control)"
    }

    # Check for Write on privileged objects
    if ($Delegation.ObjectType -eq 'AD Object' -and $Delegation.Rights -match 'Write') {
        $issues += "Has Write rights on AD object"
    }

    # Check for external accounts
    if ($Delegation.Trustee -match '\\\\' -and $Delegation.Trustee -notmatch "^$($env:USERDOMAIN)\\") {
        $issues += "Delegated to external account"
    }

    # Check for delegation to unprivileged accounts
    if ($Delegation.TrusteeType -eq 'user') {
        try {
            $user = Get-ADUser -Filter { SamAccountName -eq $Delegation.Trustee.Split('\\')[-1] } -Server $env:USERDNSDOMAIN -Properties MemberOf

            # Check if user is in any privileged groups
            $privilegedGroups = $user.MemberOf | Where-Object {
                $_ -match 'Admin|Operator|Creator|Domain Controllers'
            }

            if ($privilegedGroups.Count -eq 0) {
                $issues += "Delegated to non-privileged account"
            }
        }
        catch {
            # Account not found
            $issues += "Delegated account not found"
        }
    }

    return $issues
}

function New-DelegationReport {
    param(
        [array]$Delegations,
        [array]$Findings
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Delegation Review Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th { background-color: #3498db; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        tr:hover { background-color: #f5f5f5; }
        .critical { color: #e74c3c; font-weight: bold; }
        .high { color: #e67e22; font-weight: bold; }
        .medium { color: #f39c12; }
        .low { color: #27ae60; }
        .summary { background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Delegation Review Report</h1>
    <p><strong>Generated:</strong> $timestamp</p>
    <p><strong>Search Base:</strong> $SearchBase</p>

    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Delegations:</strong> $($Delegations.Count)</p>
        <p><strong>Total Findings:</strong> $($Findings.Count)</p>
        <p><strong>Critical Issues:</strong> $($Findings | Where-Object { $_.Severity -eq 'Critical' }).Count</p>
        <p><strong>High Issues:</strong> $($Findings | Where-Object { $_.Severity -eq 'High' }).Count</p>
        <p><strong>Medium Issues:</strong> $($Findings | Where-Object { $_.Severity -eq 'Medium' }).Count</p>
    </div>

    <h2>Delegations</h2>
    <table>
        <tr>
            <th>Object</th>
            <th>Trustee</th>
            <th>Trustee Type</th>
            <th>Rights</th>
            <th>Access Type</th>
            <th>Issues</th>
        </tr>
"@

    foreach ($delegation in $Delegations) {
        $issues = Test-DelegationSecurity -Delegation $delegation
        $severity = if ($issues -match 'GenericAll') { 'critical' }
                    elseif ($issues -match 'Write|External|non-privileged') { 'high' }
                    elseif ($issues.Count -gt 0) { 'medium' }
                    else { 'low' }

        $html += @"
        <tr>
            <td>$($delegation.ObjectDN)</td>
            <td>$($delegation.Trustee)</td>
            <td>$($delegation.TrusteeType)</td>
            <td>$($delegation.Rights)</td>
            <td>$($delegation.AccessType)</td>
            <td class="$severity">$(if ($issues.Count -gt 0) { $issues -join ', ' } else { 'None' })</td>
        </tr>
"@
    }

    $html += @"
    </table>

    <h2>Detailed Findings</h2>
    <table>
        <tr>
            <th>Severity</th>
            <th>Category</th>
            <th>Issue</th>
            <th>Affected Resource</th>
            <th>Recommendation</th>
        </tr>
"@

    foreach ($finding in $Findings) {
        $html += @"
        <tr>
            <td class="$($finding.Severity.ToLower())">$($finding.Severity)</td>
            <td>$($finding.Category)</td>
            <td>$($finding.Issue)</td>
            <td>$($finding.AffectedResource)</td>
            <td>$($finding.Recommendation)</td>
        </tr>
"@
    }

    $html += @"
    </table>

    <h2>Recommendations</h2>
    <ol>
        <li>Review all delegation permissions and remove unnecessary grants</li>
        <li>Implement the principle of least privilege for delegations</li>
        <li>Regularly audit delegation permissions (quarterly)</li>
        <li>Avoid delegating GenericAll rights</li>
        <li>Use role-based access control instead of direct delegation</li>
        <li>Document all delegation permissions with business justification</li>
        <li>Monitor delegation usage with audit logs</li>
        <li>Consider using Privileged Access Management (PAM) for complex delegation scenarios</li>
    </ol>

</body>
</html>
"@

    return $html
}

if (-not (Test-ADModule)) {
    exit 1
}

Write-Log "Starting delegation review for: $SearchBase" -Level 'INFO'

$delegations = @()

# Get OU delegations
$ouDelegations = Get-OUDelegations -SearchBase $SearchBase
$delegations += $ouDelegations

# Get user delegations
$userDelegations = Get-UserDelegations -SearchBase $SearchBase
$delegations += $userDelegations

# Get group delegations
$groupDelegations = Get-GroupDelegations -SearchBase $SearchBase
$delegations += $groupDelegations

Write-Log "Found $($delegations.Count) delegation entries" -Level 'INFO'

$findings = @()

foreach ($delegation in $delegations) {
    $issues = Test-DelegationSecurity -Delegation $delegation

    foreach ($issue in $issues) {
        $severity = if ($issue -match 'GenericAll') { 'Critical' }
                    elseif ($issue -match 'Write|External|non-privileged') { 'High' }
                    else { 'Medium' }

        $findings += [PSCustomObject]@{
            Severity = $severity
            Category = 'Delegation Security'
            Issue = $issue
            AffectedResource = "$($delegation.ObjectDN) <- $($delegation.Trustee)"
            Recommendation = 'Review delegation permissions and apply least privilege principle'
        }
    }
}

Write-Log "Found $($findings.Count) total findings" -Level 'INFO'

# Generate report
$report = New-DelegationReport -Delegations $delegations -Findings $findings
$report | Out-File -FilePath $ReportPath -Encoding UTF8

Write-Log "Report generated: $ReportPath" -Level 'INFO'

Write-Host "`nDelegation Review Summary:" -ForegroundColor Cyan
Write-Host "  Delegations Reviewed: $($delegations.Count)" -ForegroundColor White
Write-Host "  Total Findings: $($findings.Count)" -ForegroundColor White
Write-Host "  Report Saved: $ReportPath" -ForegroundColor Green
