# Windows Infrastructure Patterns

Common patterns and best practices for Windows infrastructure administration.

## Active Directory Patterns

### OU Structure Design

```powershell
# Recommended OU hierarchy
$OUStructure = @(
    "DC=example,DC=com",
    "OU=Users,DC=example,DC=com",
    "OU=Groups,DC=example,DC=com",
    "OU=Computers,DC=example,DC=com",
    "OU=Servers,DC=example,DC=com",
    "OU=Workstations,DC=example,DC=com",
    "OU=Resources,DC=example,DC=com",
    "OU=SharedFolders,OU=Resources,DC=example,DC=com",
    "OU=Printers,OU=Resources,DC=example,DC=com"
)

# Create OU structure
foreach ($OU in $OUStructure) {
    $OUParts = $OU -split ',' | Where-Object { $_ -match '^OU=' }
    $currentPath = $OU
    $parentPath = ""

    foreach ($part in $OUParts) {
        $name = $part -replace '^OU=', ''
        if ($parentPath) {
            $currentPath = "OU=$name,$parentPath"
        } else {
            $currentPath = "OU=$name,DC=example,DC=com"
        }

        try {
            New-ADOrganizationalUnit -Name $name -Path $parentPath -ErrorAction Stop
        } catch {
            Write-Warning "OU $name already exists"
        }
        $parentPath = $currentPath
    }
}
```

### User Group Management Pattern

```powershell
function Add-UserToGroupSmart {
    param(
        [string]$Username,
        [string]$GroupName,
        [string]$Domain = "example.com"
    )

    try {
        $user = Get-ADUser -Identity $Username -ErrorAction Stop
        $group = Get-ADGroup -Identity $GroupName -ErrorAction Stop

        if ($user.DistinguishedName -in $group.Members) {
            Write-Warning "User $Username is already a member of $GroupName"
            return $false
        }

        Add-ADGroupMember -Identity $GroupName -Members $Username
        Write-Host "Added $Username to $GroupName"
        return $true
    }
    catch {
        Write-Error "Failed to add user to group: $($_.Exception.Message)"
        return $false
    }
}

# Bulk add users to group
$users = Get-Content "users.txt"
foreach ($user in $users) {
    Add-UserToGroupSmart -Username $user -GroupName "Department-IT"
}
```

### Computer Object Lifecycle

```powershell
# New computer onboarding
$computerName = "DESKTOP-001"
$OU = "OU=Workstations,DC=example,DC=com"

New-ADComputer -Name $computerName -Path $OU -Enabled $true

# Join specific groups
Add-ADGroupMember -Identity "Workstation-Standard" -Members $computerName
Add-ADGroupMember -Identity "WSUS-Clients" -Members $computerName

# Set description
Set-ADComputer -Identity $computerName -Description "Assigned to: John Doe (Finance)"

# Computer offboarding
$computerName = "DESKTOP-001"

# Disable and move to disabled OU
Disable-ADAccount -Identity $computerName
$disabledOU = "OU=Disabled Computers,DC=example,DC=com"
Move-ADObject -Identity (Get-ADComputer $computerName).DistinguishedName -TargetPath $disabledOU

# Remove from sensitive groups
$groups = (Get-ADComputer $computerName -Properties MemberOf).MemberOf
foreach ($group in $groups) {
    Remove-ADGroupMember -Identity $group -Members $computerName -Confirm:$false
}
```

## DNS Management Patterns

### DNS Zone Standardization

```powershell
# Standard DNS records for new domain
function Initialize-StandardDNSRecords {
    param(
        [string]$Domain,
        [string]$WebServerIP,
        [string]$MailServerIP,
        [string]$DNSServer
    )

    # A records
    @(
        @{Name="@"; IP=$WebServerIP; Desc="Domain Root"},
        @{Name="www"; IP=$WebServerIP; Desc="Web Server"},
        @{Name="mail"; IP=$MailServerIP; Desc="Mail Server"},
        @{Name="autodiscover"; IP=$MailServerIP; Desc="Exchange Autodiscover"}
    ) | ForEach-Object {
        Add-DnsServerResourceRecordA -Name $_.Name -ZoneName $Domain `
            -IPv4Address $_.IP -ComputerName $DNSServer -ErrorAction SilentlyContinue
        Write-Host "Created A record: $($_.Name).$Domain -> $($_.IP)"
    }

    # MX record
    Add-DnsServerResourceRecordMX -Name "@" -ZoneName $Domain `
        -MailExchange "mail.$Domain" -Preference 10 -ComputerName $DNSServer

    # SPF record
    $spfRecord = "v=spf1 include:_spf.google.com ~all"
    Add-DnsServerResourceRecordTxt -Name "@" -ZoneName $Domain `
        -DescriptiveText $spfRecord -ComputerName $DNSServer
}
```

### DNS Failover Pattern

```powershell
# Configure round-robin DNS for load balancing
function Set-DNSRoundRobin {
    param(
        [string]$Domain,
        [string]$RecordName,
        [string[]]$IPAddresses,
        [string]$DNSServer
    )

    # Remove existing records
    Get-DnsServerResourceRecord -Name $RecordName -ZoneName $Domain -ComputerName $DNSServer |
        Remove-DnsServerResourceRecord -ZoneName $Domain -ComputerName $DNSServer -Force

    # Add new records (one for each IP)
    foreach ($IP in $IPAddresses) {
        Add-DnsServerResourceRecordA -Name $RecordName -ZoneName $Domain `
            -IPv4Address $IP -ComputerName $DNSServer
    }
}

# Use multiple IPs for redundancy
Set-DNSRoundRobin -Domain "example.com" -RecordName "www" `
    -IPAddresses @("192.168.1.10", "192.168.1.11", "192.168.1.12") `
    -DNSServer "dc01.example.com"
```

### DNS Aging and Scavenging

```powershell
# Enable DNS scavenging to remove stale records
$zone = "example.com"
$server = "dc01.example.com"

# Configure scavenging on zone
Set-DnsServerZoneAging -Name $zone -ComputerName $server `
    -AgingEnabled $true `
    -NoRefreshInterval 7.00:00:00 `
    -RefreshInterval 7.00:00:00

# Enable scavenging on server
Set-DnsServerScavenging -ComputerName $server `
    -ScavengingState $true `
    -ScavengingInterval 7.00:00:00
```

## Group Policy Patterns

### GPO Naming Convention

```powershell
# Standard GPO naming: <Scope>-<Function>-<Environment>
$gpoTemplates = @(
    "SEC-Password-Policy-Prod",
    "SEC-Account-Lockout-Prod",
    "CFG-Desktop-Background-Prod",
    "CFG-Software-Deployment-Prod",
    "APP-Office-Deployment-Prod",
    "APP-Antivirus-Deployment-Prod"
)

foreach ($gpoName in $gpoTemplates) {
    New-GPO -Name $gpoName
}
```

### GPO Inheritance Control

```powershell
# Block inheritance at OU level
Set-GPInheritance -Target "OU=Computers,DC=example,DC=com" -IsBlocked Yes

# Enforce GPO at OU level (Block inheritance from above)
$gpo = Get-GPO -Name "Critical Security"
New-GPLink -Guid $gpo.Id -Target "OU=Servers,DC=example,DC=com" -Enforced Yes

# Remove block inheritance
Set-GPInheritance -Target "OU=Computers,DC=example,DC=com" -IsBlocked No
```

### WMI Filters for Conditional GPO Application

```powershell
# Create WMI filter for laptops
$wmiQuery = "SELECT * FROM Win32_ComputerSystem WHERE PCSystemType = 2"
$wmiFilterName = "Is Laptop"

$namespace = "root\cimv2"
$query = [Wmi]::CreateQuery("SELECT * FROM MSFT_SomFilter WHERE Name='$wmiFilterName'")

# Create filter
$wmiFilter = New-Object -TypeName Microsoft.GroupPolicy.WmiFilter
$wmiFilter.Name = $wmiFilterName
$wmiFilter.Namespace = $namespace
$wmiFilter.Query = $wmiQuery
$wmiFilter.Description = "Filter for laptop computers"

# Apply filter to GPO
$gpo = Get-GPO -Name "Laptop Security Policy"
Set-GPRegistryValue -Guid $gpo.Id -Key "HKLM\Software\Policies\Microsoft" `
    -ValueName "WmiFilter" -Type String -Value $wmiFilter.Name
```

### GPO Security Baseline Pattern

```powershell
function Apply-SecurityBaseline {
    param(
        [string]$GPOName,
        [string]$TargetOU
    )

    $gpo = New-GPO -Name $GPOName -Comment "Security baseline configuration"

    # Password policy
    $gpoPath = $gpo.Path
    $securitySettingsPath = "$gpoPath\Machine\Microsoft\Windows NT\SecEdit"

    # Create secedit.inf
    $infContent = @"
[Unicode]
Unicode=yes
[Version]
signature="`$CHICAGO`$"
Revision=1
[System Access]
MinimumPasswordLength = 12
PasswordComplexity = 1
PasswordHistorySize = 12
MaximumPasswordAge = 60
LockoutThreshold = 5
LockoutDuration = 15
LockoutObservationWindow = 15
"@

    $infFile = "$env:TEMP\security.inf"
    $infContent | Out-File -FilePath $infFile -Encoding Unicode

    # Apply to GPO
    secedit /configure /db secedit.sdb /cfg $infFile /areas SECURITYPOLICY

    # Link GPO
    New-GPLink -Guid $gpo.Id -Target $TargetOU -LinkEnabled Yes

    # Clean up
    Remove-Item $infFile -Force
}
```

## Security Patterns

### Privileged Account Management

```powershell
# Tier 0: Enterprise Admin, Domain Admin (rarely used, no internet access)
# Tier 1: Server Admins (manage servers)
# Tier 2: Helpdesk (manage user workstations)

function Create-AdminAccount {
    param(
        [string]$Username,
        [ValidateSet('Tier0', 'Tier1', 'Tier2')]
        [string]$AdminTier,
        [string]$FirstName,
        [string]$LastName
    )

    $OU = switch ($AdminTier) {
        'Tier0' { "OU=Tier0 Admins,OU=Admins,DC=example,DC=com" }
        'Tier1' { "OU=Tier1 Admins,OU=Admins,DC=example,DC=com" }
        'Tier2' { "OU=Tier2 Admins,OU=Admins,DC=example,DC=com" }
    }

    # Create admin account
    New-ADUser -SamAccountName $Username -GivenName $FirstName -Surname $LastName `
        -Name "$FirstName $LastName" -Path $OU -Enabled $false `
        -ChangePasswordAtLogon $true

    # Add to appropriate admin group
    $adminGroup = switch ($AdminTier) {
        'Tier0' { "Enterprise Admins" }
        'Tier1' { "Server Admins" }
        'Tier2' { "Helpdesk Admins" }
    }

    Add-ADGroupMember -Identity $adminGroup -Members $Username
}
```

### Account Lockout Monitoring

```powershell
# Monitor for account lockouts
function Get-AccountLockouts {
    param(
        [int]$Hours = 24
    )

    $startTime = (Get-Date).AddHours(-$Hours)

    Get-WinEvent -LogName Security -FilterXPath "*[System[EventID=4740]]" |
        Where-Object { $_.TimeCreated -gt $startTime } |
        ForEach-Object {
            $data = $_.Properties[0].Value
            $computer = $_.Properties[1].Value

            [PSCustomObject]@{
                Timestamp = $_.TimeCreated
                Account = $data
                LockedOnComputer = $computer
            }
        } | Format-Table -AutoSize
}
```

### Password Expiration Notifications

```powershell
function Send-PasswordExpirationAlerts {
    param(
        [int]$DaysWarning = 14
    )

    $maxPasswordAge = (Get-ADDefaultDomainPasswordPolicy).MaxPasswordAge.Days
    $warningDate = (Get-Date).AddDays($DaysWarning)

    Get-ADUser -Filter {Enabled -eq $true -and PasswordNeverExpires -eq $false} -Properties PasswordLastSet |
        Where-Object { $_.PasswordLastSet -and $_.PasswordLastSet.AddDays($maxPasswordAge) -le $warningDate } |
        ForEach-Object {
            $daysUntilExpire = ($_.PasswordLastSet.AddDays($maxPasswordAge) - (Get-Date)).Days

            Send-MailMessage -To "$($_.GivenName) <$($_.EmailAddress)>" `
                -From "IT Support <it@example.com>" `
                -Subject "Password expiring in $daysUntilExpire days" `
                -Body "Your password will expire in $daysUntilExpire days. Please change it soon." `
                -SmtpServer "smtp.example.com"
        }
}
```

## Backup and Recovery Patterns

### Automated AD Backup

```powershell
function Backup-ActiveDirectory {
    param(
        [string]$BackupPath = "\\backup\ADBackups"
    )

    $date = Get-Date -Format "yyyy-MM-dd"
    $backupFile = "$BackupPath\AD-$date.bak"

    # Use Windows Server Backup
    wbadmin start backup -backupTarget:$backupFile -include:"C:\Windows\NTDS" `
        -include:"C:\Windows\SYSVOL" -systemState -allCritical -quiet

    # Backup GPOs
    $gpoBackupPath = "$BackupPath\GPOs-$date"
    Get-GPO -All | ForEach-Object {
        Backup-GPO -Guid $_.Id -Path $gpoBackupPath
    }

    # Backup DNS zones
    $dnsBackupPath = "$BackupPath\DNS-$date"
    Get-DnsServerZone | ForEach-Object {
        Export-DnsServerZone -Name $_.ZoneName -FileName "$dnsBackupPath\$($_.ZoneName).dns"
    }

    Write-Host "Backup completed to $BackupPath"
}
```

### GPO Restoration

```powershell
function Restore-GPOFromBackup {
    param(
        [string]$BackupID,
        [string]$BackupPath,
        [switch]$OverwriteExisting
    )

    if ($OverwriteExisting) {
        Restore-GPO -BackupId $BackupID -Path $BackupPath
    }
    else {
        $backup = Get-GPOBackup -Path $BackupPath -Guid $BackupID
        $existingGPO = Get-GPO -Name $backup.DisplayName -ErrorAction SilentlyContinue

        if ($existingGPO) {
            Write-Warning "GPO $($backup.DisplayName) already exists"
            return
        }

        Restore-GPO -BackupId $BackupID -Path $BackupPath
    }
}
```

## Monitoring Patterns

### Event Log Monitoring

```powershell
function Get-SecurityEvents {
    param(
        [int]$EventID,
        [int]$Hours = 24,
        [string]$ComputerName = $env:COMPUTERNAME
    )

    $startTime = (Get-Date).AddHours(-$Hours)

    Get-WinEvent -ComputerName $ComputerName -LogName Security `
        -FilterXPath "*[System[EventID=$EventID]]" |
        Where-Object { $_.TimeCreated -gt $startTime } |
        Select-Object TimeCreated, Message | Format-Table -AutoSize
}

# Monitor failed logons
Get-SecurityEvents -EventID 4625 -Hours 24

# Monitor privileged group changes
Get-SecurityEvents -EventID 4728 -Hours 24
```

### System Health Check

```powershell
function Test-SystemHealth {
    param([string]$ComputerName = $env:COMPUTERNAME)

    $results = [PSCustomObject]@{}

    $results.AD = Test-ComputerSecureChannel -Server $env:USERDNSDOMAIN -ErrorAction SilentlyContinue
    $results.DNS = Resolve-DnsName $env:COMPUTERNAME -ErrorAction SilentlyContinue
    $results.Time = Get-WmiObject -Class Win32_OperatingSystem -ComputerName $ComputerName | Select-Object LocalDateTime

    $criticalServices = @("NetLogon", "DNS", "W32Time")
    foreach ($service in $criticalServices) {
        $serviceStatus = Get-Service -Name $service -ComputerName $ComputerName -ErrorAction SilentlyContinue
        $results | Add-Member -MemberType NoteProperty -Name $service -Value $serviceStatus.Status
    }

    return $results
}
```
