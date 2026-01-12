<#
.SYNOPSIS
    Audits privileged group memberships in Active Directory

.DESCRIPTION
    This script audits privileged AD groups to identify excessive memberships,
    inactive privileged accounts, and potential security risks.

.PARAMETER Domain
    The domain to audit (default: current domain)

.PARAMETER Threshold
    Number of members considered excessive (default: 10)

.PARAMETER InactiveDays
    Number of days of inactivity to flag (default: 90)

.PARAMETER ReportPath
    Path to save the audit report (default: .\privileged_groups_audit.html)

.EXAMPLE
    .\audit_privileged_groups.ps1 -Domain "example.com" -Threshold 5
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Domain = (Get-ADDomain).DNSRoot,

    [Parameter(Mandatory=$false)]
    [int]$Threshold = 10,

    [Parameter(Mandatory=$false)]
    [int]$InactiveDays = 90,

    [Parameter(Mandatory=$false)]
    [string]$ReportPath = ".\privileged_groups_audit.html",

    [Parameter(Mandatory=$false)]
    [string]$LogPath = ".\audit_log.log"
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

function Get-PrivilegedGroups {
    param(
        [string]$Domain
    )

    $privilegedGroups = @(
        "Enterprise Admins",
        "Domain Admins",
        "Schema Admins",
        "Administrators",
        "Account Operators",
        "Backup Operators",
        "Domain Controllers",
        "Group Policy Creator Owners"
    )

    $groups = @()

    foreach ($groupName in $privilegedGroups) {
        try {
            $group = Get-ADGroup -Filter { Name -eq $groupName } -Server $Domain -ErrorAction Stop

            if ($group) {
                $groups += [PSCustomObject]@{
                    Name = $group.Name
                    SID = $group.SID.Value
                    DistinguishedName = $group.DistinguishedName
                    MemberCount = (Get-ADGroupMember -Identity $group -Server $Domain).Count
                    IsCritical = $groupName -match 'Enterprise|Domain|Schema|Administrators'
                }
            }
        }
        catch {
            Write-Log "Group $groupName not found in domain $Domain" -Level 'WARNING'
        }
    }

    return $groups
}

function Get-PrivilegedGroupMembers {
    param(
        [string]$GroupName,
        [string]$Domain
    )

    try {
        $group = Get-ADGroup -Filter { Name -eq $GroupName } -Server $Domain

        if (-not $group) {
            return @()
        }

        $members = Get-ADGroupMember -Identity $group -Recursive -Server $Domain |
            ForEach-Object {
                $user = Get-ADUser -Identity $_ -Server $Domain -Properties LastLogonDate,PasswordLastSet,Enabled,AccountExpirationDate

                $inactiveDays = if ($user.LastLogonDate) {
                    (Get-Date) - $user.LastLogonDate
                } else {
                    [TimeSpan]::MaxValue
                }

                $passwordAge = (Get-Date) - $user.PasswordLastSet

                [PSCustomObject]@{
                    Username = $user.SamAccountName
                    DisplayName = $user.DisplayName
                    Email = $user.EmailAddress
                    LastLogonDate = $user.LastLogonDate
                    DaysInactive = $inactiveDays.Days
                    PasswordAgeDays = $passwordAge.Days
                    Enabled = $user.Enabled
                    AccountExpires = $user.AccountExpirationDate
                    DistinguishedName = $user.DistinguishedName
                }
            }

        return $members
    }
    catch {
        Write-Log "Failed to get members for group $GroupName`: $($_.Exception.Message)" -Level 'ERROR'
        return @()
    }
}

function Test-PrivilegedAccountSecurity {
    param(
        [string]$Username,
        [string]$Domain
    )

    $issues = @()

    try {
        $user = Get-ADUser -Identity $Username -Server $Domain -Properties LastLogonDate,PasswordLastSet,Enabled

        if (-not $user.Enabled) {
            $issues += "Account is disabled"
        }

        $inactiveDays = if ($user.LastLogonDate) {
            (Get-Date) - $user.LastLogonDate
        } else {
            [TimeSpan]::MaxValue
        }

        if ($inactiveDays.Days -gt $InactiveDays) {
            $issues += "Account inactive for $($inactiveDays.Days) days"
        }

        $passwordAge = (Get-Date) - $user.PasswordLastSet
        if ($passwordAge.Days -gt 365) {
            $issues += "Password not changed for $($passwordAge.Days) days"
        }

        $groups = Get-ADPrincipalGroupMembership -Identity $Username -Server $Domain
        $privilegedCount = @($groups | Where-Object { $_.Name -match 'Admin|Operator|Creator' }).Count

        if ($privilegedCount -gt 3) {
            $issues += "Member of $privilegedCount privileged groups"
        }
    }
    catch {
        $issues += "Failed to retrieve user details: $($_.Exception.Message)"
    }

    return $issues
}

function Get-GroupDelegation {
    param(
        [string]$GroupName,
        [string]$Domain
    )

    try {
        $group = Get-ADGroup -Identity $GroupName -Server $Domain

        # Check for delegation permissions
        $delegation = Get-Acl -Path ("AD:\\" + $group.DistinguishedName) |
            Select-Object -ExpandProperty Access |
            Where-Object {
                $_.IdentityReference -notlike "*S-1-5-32*" -and
                $_.IdentityReference -notlike "*BUILTIN*"
            }

        if ($delegation) {
            return $delegation | ForEach-Object {
                [PSCustomObject]@{
                    Identity = $_.IdentityReference.Value
                    Rights = $_.ActiveDirectoryRights
                    AccessType = $_.AccessControlType
                    Inherited = $_.IsInherited
                }
            }
        }

        return @()
    }
    catch {
        return @()
    }
}

function New-AuditReport {
    param(
        [array]$Groups,
        [array]$Findings
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Privileged Groups Audit Report</title>
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
    <h1>Privileged Groups Audit Report</h1>
    <p><strong>Generated:</strong> $timestamp</p>
    <p><strong>Domain:</strong> $Domain</p>

    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Privileged Groups:</strong> $($Groups.Count)</p>
        <p><strong>Total Findings:</strong> $($Findings.Count)</p>
        <p><strong>Critical Issues:</strong> $($Findings | Where-Object { $_.Severity -eq 'Critical' }).Count</p>
        <p><strong>High Issues:</strong> $($Findings | Where-Object { $_.Severity -eq 'High' }).Count</p>
        <p><strong>Medium Issues:</strong> $($Findings | Where-Object { $_.Severity -eq 'Medium' }).Count</p>
    </div>

    <h2>Privileged Groups</h2>
    <table>
        <tr>
            <th>Group Name</th>
            <th>Members</th>
            <th>Severity</th>
            <th>Issues</th>
        </tr>
"@

    foreach ($group in $Groups) {
        $severity = if ($group.IsCritical) { 'critical' } elseif ($group.MemberCount -gt $Threshold) { 'high' } else { 'low' }

        $issues = @()
        if ($group.MemberCount -gt $Threshold) {
            $issues += "Exceeds member threshold ($Threshold)"
        }
        if ($group.IsCritical) {
            $issues += "Critical privileged group"
        }

        $html += @"
        <tr>
            <td>$($group.Name)</td>
            <td>$($group.MemberCount)</td>
            <td class="$severity">$severity.ToUpper()</td>
            <td>$(if ($issues) { $issues -join ', ' } else { 'None' })</td>
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
        <li>Review all privileged group memberships and remove unnecessary members</li>
        <li>Implement regular reviews of privileged access (quarterly)</li>
        <li>Enable Just-In-Time (JIT) access for privileged roles</li>
        <li>Use Privileged Identity Management (PIM) for Azure AD</li>
        <li>Monitor privileged account activity with audit logs</li>
        <li>Implement separation of duties where possible</li>
        <li>Enforce MFA for all privileged accounts</li>
        <li>Establish account lifecycle policies for privileged accounts</li>
    </ol>

</body>
</html>
"@

    return $html
}

if (-not (Test-ADModule)) {
    exit 1
}

Write-Log "Starting privileged groups audit for domain: $Domain" -Level 'INFO'

$groups = Get-PrivilegedGroups -Domain $Domain

Write-Log "Found $($groups.Count) privileged groups" -Level 'INFO'

$findings = @()

foreach ($group in $groups) {
    Write-Log "Auditing group: $($group.Name)" -Level 'INFO'

    # Check if group exceeds threshold
    if ($group.MemberCount -gt $Threshold) {
        $findings += [PSCustomObject]@{
            Severity = 'High'
            Category = 'Excessive Membership'
            Issue = "Group has $($group.MemberCount) members (threshold: $Threshold)"
            AffectedResource = $group.Name
            Recommendation = 'Review and remove unnecessary members from this group'
        }
    }

    # Check for inactive members
    $members = Get-PrivilegedGroupMembers -GroupName $group.Name -Domain $Domain

    foreach ($member in $members) {
        if ($member.DaysInactive -gt $InactiveDays) {
            $findings += [PSCustomObject]@{
                Severity = 'Medium'
                Category = 'Inactive Account'
                Issue = "User $($member.Username) inactive for $($member.DaysInactive) days"
                AffectedResource = "$($group.Name) - $($member.Username)"
                Recommendation = 'Review and disable or remove inactive privileged accounts'
            }
        }

        # Check for security issues
        $issues = Test-PrivilegedAccountSecurity -Username $member.Username -Domain $Domain

        foreach ($issue in $issues) {
            $findings += [PSCustomObject]@{
                Severity = 'Medium'
                Category = 'Account Security'
                Issue = $issue
                AffectedResource = "$($group.Name) - $($member.Username)"
                Recommendation = 'Review account security settings and activity'
            }
        }
    }

    # Check for delegation
    $delegation = Get-GroupDelegation -GroupName $group.Name -Domain $Domain

    if ($delegation) {
        foreach ($delegationItem in $delegation) {
            $findings += [PSCustomObject]@{
                Severity = 'High'
                Category = 'Delegation'
                Issue = "Group has delegation permissions for $($delegationItem.Identity)"
                AffectedResource = $group.Name
                Recommendation = 'Review and restrict delegation permissions on this group'
            }
        }
    }
}

Write-Log "Found $($findings.Count) total findings" -Level 'INFO'

# Generate report
$report = New-AuditReport -Groups $groups -Findings $findings
$report | Out-File -FilePath $ReportPath -Encoding UTF8

Write-Log "Report generated: $ReportPath" -Level 'INFO'

Write-Host "`nAudit Summary:" -ForegroundColor Cyan
Write-Host "  Groups Audited: $($groups.Count)" -ForegroundColor White
Write-Host "  Total Findings: $($findings.Count)" -ForegroundColor White
Write-Host "  Report Saved: $ReportPath" -ForegroundColor Green
