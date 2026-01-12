<#
.SYNOPSIS
    Manages Active Directory users using legacy Windows PowerShell 5.1 patterns
.DESCRIPTION
    Comprehensive Active Directory user management with WMI fallback, suitable for
    Windows Server 2012/2016/2019 environments with PowerShell 5.1
.PARAMETER Username
    The username for the account operation
.PARAMETER Action
    Action to perform: Create, Enable, Disable, Delete, Unlock
.PARAMETER OrganizationalUnit
    Target OU path for user creation
.PARAMETER Groups
    Array of group names to add user to
.EXAMPLE
    .\manage_legacy_ad.ps1 -Username "jdoe" -Action Create -OU "OU=Users,DC=corp,DC=local"
#>

#Requires -Modules ActiveDirectory
#Requires -Version 5.1

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [string]$Username,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet('Create', 'Enable', 'Disable', 'Delete', 'Unlock')]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$OrganizationalUnit = "CN=Users,DC=corp,DC=local",
    
    [Parameter(Mandatory=$false)]
    [string[]]$Groups,
    
    [Parameter(Mandatory=$false)]
    [switch]$UseWMI
)

function Test-ADAvailability {
    try {
        $module = Get-Module -ListAvailable -Name ActiveDirectory
        if (-not $module) {
            Write-Warning "Active Directory module not found"
            return $false
        }
        return $true
    }
    catch {
        Write-Warning "AD module check failed: $_"
        return $false
    }
}

function Invoke-WMIFallback {
    param(
        [string]$User,
        [string]$Operation
    )
    
    Write-Verbose "Using WMI fallback for: $Operation"
    
    try {
        $query = "SELECT * FROM Win32_UserAccount WHERE Name = '$User'"
        $user = Get-WmiObject -Query $query -ErrorAction Stop
        
        switch ($Operation) {
            'Disable' {
                $user.Disabled = $true
                $user.Put() | Out-Null
                Write-Host "Disabled user $User via WMI"
            }
            'Enable' {
                $user.Disabled = $false
                $user.Put() | Out-Null
                Write-Host "Enabled user $User via WMI"
            }
            'Delete' {
                $user.Delete()
                Write-Host "Deleted user $User via WMI"
            }
            default {
                Write-Error "Operation $Operation not supported via WMI"
            }
        }
    }
    catch {
        Write-Error "WMI operation failed: $_"
        throw
    }
}

function New-LegacyADUser {
    param(
        [string]$User,
        [string]$OU,
        [string[]]$GroupList
    )
    
    try {
        $sam = $User
        $upn = "$User@corp.local"
        $displayName = $User -replace '([a-z])([A-Z])', '$1 $2'
        $displayName = (Get-Culture).TextInfo.ToTitleCase($displayName)
        
        $userParams = @{
            SamAccountName = $sam
            UserPrincipalName = $upn
            Name = $displayName
            DisplayName = $displayName
            Path = $OU
            Enabled = $true
            ChangePasswordAtLogon = $true
            AccountPassword = (ConvertTo-SecureString "TempP@ss123!" -AsPlainText -Force)
        }
        
        New-ADUser @userParams -ErrorAction Stop
        Write-Host "Created user: $User in $OU"
        
        foreach ($group in $GroupList) {
            try {
                Add-ADGroupMember -Identity $group -Members $sam -ErrorAction Stop
                Write-Verbose "Added $User to group: $group"
            }
            catch {
                Write-Warning "Failed to add to group $group : $_"
            }
        }
    }
    catch {
        Write-Error "Failed to create user: $_"
        throw
    }
}

try {
    Write-Verbose "Starting AD management operation: $Action for $Username"
    
    if ($UseWMI) {
        Invoke-WMIFallback -User $Username -Operation $Action
        exit 0
    }
    
    if (-not (Test-ADAvailability)) {
        Write-Warning "AD module unavailable, falling back to WMI"
        Invoke-WMIFallback -User $Username -Operation $Action
        exit 0
    }
    
    Import-Module ActiveDirectory -ErrorAction Stop
    
    switch ($Action) {
        'Create' {
            if ($PSCmdlet.ShouldProcess($Username, "Create AD user")) {
                New-LegacyADUser -User $Username -OU $OrganizationalUnit -GroupList $Groups
            }
        }
        
        'Enable' {
            if ($PSCmdlet.ShouldProcess($Username, "Enable AD user")) {
                Enable-ADAccount -Identity $Username -ErrorAction Stop
                Write-Host "Enabled user: $Username"
            }
        }
        
        'Disable' {
            if ($PSCmdlet.ShouldProcess($Username, "Disable AD user")) {
                Disable-ADAccount -Identity $Username -ErrorAction Stop
                Write-Host "Disabled user: $Username"
            }
        }
        
        'Delete' {
            if ($PSCmdlet.ShouldProcess($Username, "Delete AD user")) {
                Remove-ADUser -Identity $Username -Confirm:$false -ErrorAction Stop
                Write-Host "Deleted user: $Username"
            }
        }
        
        'Unlock' {
            if ($PSCmdlet.ShouldProcess($Username, "Unlock AD user")) {
                Unlock-ADAccount -Identity $Username -ErrorAction Stop
                Write-Host "Unlocked user: $Username"
            }
        }
    }
    
    Write-Verbose "Operation completed successfully"
}
catch {
    Write-Error "Script execution failed: $_"
    exit 1
}
finally {
    Write-Verbose "AD management script completed"
}

Export-ModuleMember -Function New-LegacyADUser, Invoke-WMIFallback
