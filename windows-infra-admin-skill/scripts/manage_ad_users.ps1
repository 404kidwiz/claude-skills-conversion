# Active Directory User Management Script

<#
.SYNOPSIS
    Manages Active Directory users with comprehensive functionality

.DESCRIPTION
    This script provides functions for creating, updating, and managing Active Directory users
    with proper validation, error handling, and logging.

.PARAMETER Username
    The username for the AD user

.PARAMETER FirstName
    First name of the user

.PARAMETER LastName
    Last name of the user

.PARAMETER Email
    Email address of the user

.PARAMETER OU
    Organizational Unit path for the user

.PARAMETER Enabled
    Enable or disable the user account

.EXAMPLE
    .\manage_ad_users.ps1 -Action Create -Username "jdoe" -FirstName "John" -LastName "Doe" -Email "jdoe@example.com" -OU "OU=Users,DC=example,DC=com"
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Create', 'Update', 'Delete', 'Disable', 'Enable', 'List')]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [string]$Username,

    [Parameter(Mandatory=$false)]
    [string]$FirstName,

    [Parameter(Mandatory=$false)]
    [string]$LastName,

    [Parameter(Mandatory=$false)]
    [string]$Email,

    [Parameter(Mandatory=$false)]
    [string]$OU = "OU=Users,DC=example,DC=com",

    [Parameter(Mandatory=$false)]
    [bool]$Enabled = $true,

    [Parameter(Mandatory=$false)]
    [string]$LogPath = ".\ad_management.log"
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
        Write-Log "Active Directory module not available. Please install RSAT." -Level 'ERROR'
        return $false
    }
}

function Validate-Username {
    param([string]$Username)

    if ([string]::IsNullOrWhiteSpace($Username)) {
        throw "Username cannot be empty"
    }

    if ($Username -match '[\s\\/":|<>+=;,?*@]') {
        throw "Username contains invalid characters"
    }

    if ($Username.Length -gt 20) {
        throw "Username exceeds maximum length of 20 characters"
    }

    return $true
}

function Validate-Email {
    param([string]$Email)

    if ([string]::IsNullOrWhiteSpace($Email)) {
        return $false
    }

    $emailRegex = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return $Email -match $emailRegex
}

function New-ADUserAdvanced {
    param(
        [string]$Username,
        [string]$FirstName,
        [string]$LastName,
        [string]$Email,
        [string]$OU,
        [bool]$Enabled
    )

    Write-Log "Creating AD user: $Username" -Level 'INFO'

    Validate-Username -Username $Username

    $displayName = "$FirstName $LastName"
    $samAccountName = $Username

    $params = @{
        SamAccountName = $samAccountName
        UserPrincipalName = "$Username@$((Get-ADDomain).DNSRoot)"
        Name = $displayName
        GivenName = $FirstName
        Surname = $LastName
        DisplayName = $displayName
        Path = $OU
        Enabled = $false
        ChangePasswordAtLogon = $true
        PasswordNeverExpires = $false
    }

    if ($Email) {
        if (-not (Validate-Email -Email $Email)) {
            throw "Invalid email format: $Email"
        }
        $params.EmailAddress = $Email
    }

    try {
        New-ADUser @params
        Write-Log "User $Username created successfully" -Level 'INFO'

        if ($Enabled) {
            $tempPassword = ConvertTo-SecureString "TempPassword123!" -AsPlainText -Force
            Set-ADAccountPassword -Identity $Username -NewPassword $tempPassword -Reset
            Enable-ADAccount -Identity $Username
            Write-Log "User $Username enabled with temporary password" -Level 'INFO'
        }

        return @{
            Success = $true
            Username = $Username
            DN = (Get-ADUser $Username).DistinguishedName
        }
    }
    catch {
        Write-Log "Failed to create user $Username`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Update-ADUserAdvanced {
    param(
        [string]$Username,
        [string]$FirstName,
        [string]$LastName,
        [string]$Email
    )

    Write-Log "Updating AD user: $Username" -Level 'INFO'

    try {
        $user = Get-ADUser -Identity $Username -ErrorAction Stop

        $updateParams = @{}

        if ($FirstName) {
            $updateParams.GivenName = $FirstName
            $updateParams.DisplayName = "$FirstName $($user.Surname)"
        }

        if ($LastName) {
            $updateParams.Surname = $LastName
            $updateParams.DisplayName = "$($user.GivenName) $LastName"
        }

        if ($Email) {
            if (-not (Validate-Email -Email $Email)) {
                throw "Invalid email format: $Email"
            }
            $updateParams.EmailAddress = $Email
        }

        if ($updateParams.Count -gt 0) {
            Set-ADUser -Identity $Username @updateParams
            Write-Log "User $Username updated successfully" -Level 'INFO'
        }
        else {
            Write-Log "No updates provided for user $Username" -Level 'WARNING'
        }

        return @{
            Success = $true
            Username = $Username
        }
    }
    catch [Microsoft.ActiveDirectory.Management.ADIdentityNotFoundException] {
        Write-Log "User $Username not found" -Level 'ERROR'
        return @{
            Success = $false
            Error = "User not found"
        }
    }
    catch {
        Write-Log "Failed to update user $Username`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Remove-ADUserAdvanced {
    param([string]$Username)

    Write-Log "Deleting AD user: $Username" -Level 'INFO'

    try {
        Remove-ADUser -Identity $Username -Confirm:$false
        Write-Log "User $Username deleted successfully" -Level 'INFO'

        return @{
            Success = $true
            Username = $Username
        }
    }
    catch [Microsoft.ActiveDirectory.Management.ADIdentityNotFoundException] {
        Write-Log "User $Username not found" -Level 'ERROR'
        return @{
            Success = $false
            Error = "User not found"
        }
    }
    catch {
        Write-Log "Failed to delete user $Username`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Set-ADUserStatus {
    param(
        [string]$Username,
        [bool]$Enable
    )

    Write-Log "Setting user $Username status to $(if($Enable){'Enabled'}else{'Disabled'})" -Level 'INFO'

    try {
        if ($Enable) {
            Enable-ADAccount -Identity $Username
        }
        else {
            Disable-ADAccount -Identity $Username
        }

        Write-Log "User $Username status updated successfully" -Level 'INFO'

        return @{
            Success = $true
            Username = $Username
            Enabled = $Enable
        }
    }
    catch {
        Write-Log "Failed to update user status $Username`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Get-ADUserList {
    param(
        [string]$Filter = "*",
        [string]$SearchBase = (Get-ADDomain).DistinguishedName
    )

    Write-Log "Listing AD users with filter: $Filter" -Level 'INFO'

    try {
        $users = Get-ADUser -Filter $Filter -SearchBase $SearchBase -Properties EmailAddress, LastLogonDate, Enabled

        $userList = $users | ForEach-Object {
            [PSCustomObject]@{
                Username = $_.SamAccountName
                DisplayName = $_.DisplayName
                Email = $_.EmailAddress
                Enabled = $_.Enabled
                LastLogon = $_.LastLogonDate
                DN = $_.DistinguishedName
            }
        }

        return @{
            Success = $true
            Users = $userList
        }
    }
    catch {
        Write-Log "Failed to list users`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

$moduleAvailable = Test-ADModule
if (-not $moduleAvailable) {
    exit 1
}

switch ($Action) {
    'Create' {
        if (-not $Username -or -not $FirstName -or -not $LastName) {
            Write-Log "Username, FirstName, and LastName are required for Create action" -Level 'ERROR'
            exit 1
        }
        $result = New-ADUserAdvanced -Username $Username -FirstName $FirstName -LastName $LastName -Email $Email -OU $OU -Enabled $Enabled
    }
    'Update' {
        if (-not $Username) {
            Write-Log "Username is required for Update action" -Level 'ERROR'
            exit 1
        }
        $result = Update-ADUserAdvanced -Username $Username -FirstName $FirstName -LastName $LastName -Email $Email
    }
    'Delete' {
        if (-not $Username) {
            Write-Log "Username is required for Delete action" -Level 'ERROR'
            exit 1
        }
        $result = Remove-ADUserAdvanced -Username $Username
    }
    'Disable' {
        if (-not $Username) {
            Write-Log "Username is required for Disable action" -Level 'ERROR'
            exit 1
        }
        $result = Set-ADUserStatus -Username $Username -Enable $false
    }
    'Enable' {
        if (-not $Username) {
            Write-Log "Username is required for Enable action" -Level 'ERROR'
            exit 1
        }
        $result = Set-ADUserStatus -Username $Username -Enable $true
    }
    'List' {
        $result = Get-ADUserList
    }
}

if ($result.Success) {
    Write-Log "Operation completed successfully" -Level 'INFO'
    if ($result.Users) {
        $result.Users | Format-Table -AutoSize
    }
}
else {
    Write-Log "Operation failed: $($result.Error)" -Level 'ERROR'
    exit 1
}
