# Group Policy Management Script

<#
.SYNOPSIS
    Configures and manages Group Policy Objects (GPOs)

.DESCRIPTION
    This script provides comprehensive GPO management functionality including
    GPO creation, link management, backup, and restoration.

.PARAMETER Action
    The action to perform (CreateGPO, LinkGPO, BackupGPO, RestoreGPO, ApplySettings, ListGPOs)

.PARAMETER GPOName
    The name of the Group Policy Object

.PARAMETER Description
    Description for the GPO

.PARAMETER TargetOU
    The target Organizational Unit for linking the GPO

.PARAMETER BackupPath
    Path for GPO backup files

.PARAMETER GPOSettings
    Hashtable containing GPO settings to apply

.EXAMPLE
    .\setup_gpo.ps1 -Action CreateGPO -GPOName "Workstation Security" -Description "Security policies for workstations"
.EXAMPLE
    .\setup_gpo.ps1 -Action LinkGPO -GPOName "Workstation Security" -TargetOU "OU=Workstations,DC=example,DC=com"
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('CreateGPO', 'LinkGPO', 'UnlinkGPO', 'BackupGPO', 'RestoreGPO', 'ApplySettings', 'ListGPOs', 'ReportGPO')]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [string]$GPOName,

    [Parameter(Mandatory=$false)]
    [string]$Description,

    [Parameter(Mandatory=$false)]
    [string]$TargetOU,

    [Parameter(Mandatory=$false)]
    [string]$BackupPath = ".\GPOBackups",

    [Parameter(Mandatory=$false)]
    [hashtable]$GPOSettings,

    [Parameter(Mandatory=$false)]
    [string]$LogPath = ".\gpo_management.log"
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

function Test-GPOModule {
    try {
        Import-Module GroupPolicy -ErrorAction Stop
        return $true
    }
    catch {
        Write-Log "Group Policy module not available. Please install RSAT." -Level 'ERROR'
        return $false
    }
}

function New-GPOAdvanced {
    param(
        [string]$GPOName,
        [string]$Description
    )

    Write-Log "Creating GPO: $GPOName" -Level 'INFO'

    try {
        $existingGPO = Get-GPO -Name $GPOName -ErrorAction SilentlyContinue
        if ($existingGPO) {
            Write-Log "GPO $GPOName already exists" -Level 'WARNING'
            return @{
                Success = $false
                Error = "GPO already exists"
            }
        }

        $params = @{
            Name = $GPOName
        }

        if ($Description) {
            $params.Comment = $Description
        }

        New-GPO @params
        Write-Log "GPO $GPOName created successfully" -Level 'INFO'

        return @{
            Success = $true
            GPOName = $GPOName
            ID = (Get-GPO $GPOName).Id
        }
    }
    catch {
        Write-Log "Failed to create GPO $GPOName`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Set-GPOLinkAdvanced {
    param(
        [string]$GPOName,
        [string]$TargetOU,
        [bool]$Enforced = $false,
        [bool]$LinkEnabled = $true
    )

    Write-Log "Linking GPO $GPOName to OU: $TargetOU" -Level 'INFO'

    try {
        $gpo = Get-GPO -Name $GPOName -ErrorAction Stop
        New-GPLink -Guid $gpo.Id -Target $TargetOU -LinkEnabled $LinkEnabled -Enforced $Enforced
        Write-Log "GPO $GPOName linked successfully to $TargetOU" -Level 'INFO'

        return @{
            Success = $true
            GPOName = $GPOName
            TargetOU = $TargetOU
        }
    }
    catch [System.Management.Automation.CommandNotFoundException] {
        Write-Log "GPO $GPOName not found" -Level 'ERROR'
        return @{
            Success = $false
            Error = "GPO not found"
        }
    }
    catch {
        Write-Log "Failed to link GPO $GPOName`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Remove-GPOLinkAdvanced {
    param(
        [string]$GPOName,
        [string]$TargetOU
    )

    Write-Log "Unlinking GPO $GPOName from OU: $TargetOU" -Level 'INFO'

    try {
        $gpo = Get-GPO -Name $GPOName -ErrorAction Stop
        Remove-GPLink -Guid $gpo.Id -Target $TargetOU
        Write-Log "GPO $GPOName unlinked successfully from $TargetOU" -Level 'INFO'

        return @{
            Success = $true
            GPOName = $GPOName
            TargetOU = $TargetOU
        }
    }
    catch {
        Write-Log "Failed to unlink GPO $GPOName`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Backup-GPOAdvanced {
    param(
        [string]$GPOName,
        [string]$BackupPath
    )

    Write-Log "Backing up GPO: $GPOName to $BackupPath" -Level 'INFO'

    if (-not (Test-Path $BackupPath)) {
        New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    }

    try {
        $gpo = Get-GPO -Name $GPOName -ErrorAction Stop
        $backup = Backup-GPO -Guid $gpo.Id -Path $BackupPath

        Write-Log "GPO $GPOName backed up successfully" -Level 'INFO'

        return @{
            Success = $true
            GPOName = $GPOName
            BackupID = $backup.BackupId
            BackupPath = $BackupPath
        }
    }
    catch {
        Write-Log "Failed to backup GPO $GPOName`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Restore-GPOAdvanced {
    param(
        [string]$BackupID,
        [string]$BackupPath
    )

    Write-Log "Restoring GPO from backup: $BackupID" -Level 'INFO'

    try {
        Restore-GPO -BackupId $BackupID -Path $BackupPath
        Write-Log "GPO restored successfully" -Level 'INFO'

        return @{
            Success = $true
            BackupID = $BackupID
        }
    }
    catch {
        Write-Log "Failed to restore GPO`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Set-GPOSecuritySettings {
    param(
        [string]$GPOName,
        [hashtable]$Settings
    )

    Write-Log "Applying security settings to GPO: $GPOName" -Level 'INFO'

    try {
        $gpo = Get-GPO -Name $GPOName -ErrorAction Stop

        if ($Settings.PasswordPolicy) {
            $gpoPath = $gpo.Path
            $securitySettingsPath = "$gpoPath\Machine\Microsoft\Windows NT\SecEdit"

            $seceditContent = @"
[Unicode]
Unicode=yes
[Version]
signature="`$CHICAGO`$"
Revision=1
[System Access]
MinimumPasswordLength = $($Settings.PasswordPolicy.MinLength ?? 8)
PasswordComplexity = 1
PasswordHistorySize = $($Settings.PasswordPolicy.History ?? 24)
MaximumPasswordAge = $($Settings.PasswordPolicy.MaxAgeDays ?? 90)
"@

            if ($Settings.PasswordPolicy.MinLength) {
                $seceditContent += "`nMinimumPasswordLength = $($Settings.PasswordPolicy.MinLength)"
            }

            $seceditPath = "$env:TEMP\secedit.inf"
            $seceditContent | Out-File -FilePath $seceditPath -Encoding Unicode

            secedit /configure /db secedit.sdb /cfg $seceditPath /areas SECURITYPOLICY
            Remove-Item $seceditPath -Force
        }

        if ($Settings.AuditPolicy) {
            Write-Log "Configuring audit policy" -Level 'INFO'

            foreach ($auditSetting in $Settings.AuditPolicy.GetEnumerator()) {
                auditpol /set /subcategory:$($auditSetting.Key) /success:$($auditSetting.Value.Success) /failure:$($auditSetting.Value.Failure)
            }
        }

        if ($Settings.UserRights) {
            Write-Log "Configuring user rights" -Level 'INFO'

            foreach ($rightSetting in $Settings.UserRights.GetEnumerator()) {
                $users = $rightSetting.Value -join ','
                secedit /export /cfg $env:TEMP\export.inf
                (Get-Content $env:TEMP\export.inf) -replace "$($rightSetting.Key) = .*", "$($rightSetting.Key) = $users" | Set-Content $env:TEMP\export.inf
                secedit /configure /db secedit.sdb /cfg $env:TEMP\export.inf /areas USER_RIGHTS
                Remove-Item $env:TEMP\export.inf -Force
            }
        }

        Write-Log "GPO security settings applied successfully" -Level 'INFO'

        return @{
            Success = $true
            GPOName = $GPOName
        }
    }
    catch {
        Write-Log "Failed to apply GPO settings`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Get-GPOList {
    param(
        [string]$Domain = (Get-ADDomain).DNSRoot
    )

    Write-Log "Listing GPOs for domain: $Domain" -Level 'INFO'

    try {
        $gpos = Get-GPO -All -Domain $Domain

        $gpoList = $gpos | ForEach-Object {
            [PSCustomObject]@{
                DisplayName = $_.DisplayName
                ID = $_.Id
                CreationTime = $_.CreationTime
                ModificationTime = $_.ModificationTime
                GPOStatus = $_.GPOStatus
                Version = "$($_.Version.Computer) (Computer), $($_.Version.User) (User)"
            }
        }

        return @{
            Success = $true
            GPOs = $gpoList
        }
    }
    catch {
        Write-Log "Failed to list GPOs`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Get-GPOReport {
    param(
        [string]$GPOName,
        [string]$ReportPath
    )

    Write-Log "Generating GPO report for: $GPOName" -Level 'INFO'

    try {
        $gpo = Get-GPO -Name $GPOName -ErrorAction Stop

        if (-not $ReportPath) {
            $ReportPath = ".\GPO-Report-$GPOName-$(Get-Date -Format 'yyyyMMdd-HHmmss').html"
        }

        Get-GPOReport -Guid $gpo.Id -ReportType Html -Path $ReportPath

        Write-Log "GPO report generated: $ReportPath" -Level 'INFO'

        return @{
            Success = $true
            ReportPath = $ReportPath
        }
    }
    catch {
        Write-Log "Failed to generate GPO report`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

$moduleAvailable = Test-GPOModule
if (-not $moduleAvailable) {
    exit 1
}

switch ($Action) {
    'CreateGPO' {
        if (-not $GPOName) {
            Write-Log "GPOName is required for CreateGPO action" -Level 'ERROR'
            exit 1
        }
        $result = New-GPOAdvanced -GPOName $GPOName -Description $Description
    }
    'LinkGPO' {
        if (-not $GPOName -or -not $TargetOU) {
            Write-Log "GPOName and TargetOU are required for LinkGPO action" -Level 'ERROR'
            exit 1
        }
        $result = Set-GPOLinkAdvanced -GPOName $GPOName -TargetOU $TargetOU
    }
    'UnlinkGPO' {
        if (-not $GPOName -or -not $TargetOU) {
            Write-Log "GPOName and TargetOU are required for UnlinkGPO action" -Level 'ERROR'
            exit 1
        }
        $result = Remove-GPOLinkAdvanced -GPOName $GPOName -TargetOU $TargetOU
    }
    'BackupGPO' {
        if (-not $GPOName) {
            Write-Log "GPOName is required for BackupGPO action" -Level 'ERROR'
            exit 1
        }
        $result = Backup-GPOAdvanced -GPOName $GPOName -BackupPath $BackupPath
    }
    'RestoreGPO' {
        if (-not $GPOSettings -or -not $GPOSettings.BackupID) {
            Write-Log "BackupID is required for RestoreGPO action" -Level 'ERROR'
            exit 1
        }
        $result = Restore-GPOAdvanced -BackupID $GPOSettings.BackupID -BackupPath $BackupPath
    }
    'ApplySettings' {
        if (-not $GPOName -or -not $GPOSettings) {
            Write-Log "GPOName and GPOSettings are required for ApplySettings action" -Level 'ERROR'
            exit 1
        }
        $result = Set-GPOSecuritySettings -GPOName $GPOName -Settings $GPOSettings
    }
    'ListGPOs' {
        $result = Get-GPOList
    }
    'ReportGPO' {
        if (-not $GPOName) {
            Write-Log "GPOName is required for ReportGPO action" -Level 'ERROR'
            exit 1
        }
        $result = Get-GPOReport -GPOName $GPOName -ReportPath $GPOSettings?.ReportPath
    }
}

if ($result.Success) {
    Write-Log "Operation completed successfully" -Level 'INFO'
    if ($result.GPOs) {
        $result.GPOs | Format-Table -AutoSize
    }
}
else {
    Write-Log "Operation failed: $($result.Error)" -Level 'ERROR'
    exit 1
}
