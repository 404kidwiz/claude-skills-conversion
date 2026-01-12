# PowerShell 5.1 Legacy Patterns

## Overview

This guide covers patterns and techniques specific to PowerShell 5.1 and Windows-only environments.

## Windows-Specific Patterns

### Windows Forms Integration

```powershell
Add-Type -AssemblyName System.Windows.Forms

$form = New-Object System.Windows.Forms.Form
$form.Text = "PowerShell 5.1 Form"
$form.Width = 400
$form.Height = 300

$button = New-Object System.Windows.Forms.Button
$button.Text = "Click Me"
$button.Location = New-Object System.Drawing.Point(100, 100)
$button.Add_Click({
    [System.Windows.Forms.MessageBox]::Show("Hello from PS 5.1!")
})

$form.Controls.Add($button)
$form.ShowDialog()
```

### WMI Queries (Legacy)

```powershell
# Query using Get-WmiObject
$os = Get-WmiObject -Class Win32_OperatingSystem
Write-Host "OS: $($os.Caption)"
Write-Host "Version: $($os.Version)"
Write-Host "Service Pack: $($os.ServicePackMajorVersion)"

# Query with WQL filter
$services = Get-WmiObject -Class Win32_Service -Filter "State='Running'"
```

### Active Directory Automation

```powershell
# Create user with properties
New-ADUser -SamAccountName "jdoe" `
            -UserPrincipalName "jdoe@corp.local" `
            -Name "John Doe" `
            -DisplayName "John Doe" `
            -Path "OU=Users,DC=corp,DC=local" `
            -Enabled $true `
            -ChangePasswordAtLogon $true `
            -AccountPassword (ConvertTo-SecureString "TempPass123!" -AsPlainText -Force)

# Query with filter
Get-ADUser -Filter * -Properties * | Where-Object { $_.Enabled -eq $false }

# Batch operations
$users = Import-Csv -Path "users.csv"
foreach ($user in $users) {
    New-ADUser @user
}
```

## Legacy Protocol Management

### Remoting with WinRM

```powershell
# Enable WinRM
Enable-PSRemoting -Force

# Test remoting connection
Test-WSMan -ComputerName "server01"

# Invoke command remotely
Invoke-Command -ComputerName "server01" -ScriptBlock {
    Get-Service | Where-Object { $_.Status -eq 'Running' }
}

# Enter remote session
Enter-PSSession -ComputerName "server01"
```

### Legacy COM Objects

```powershell
# Create COM object
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $true

$workbook = $excel.Workbooks.Add()
$worksheet = $workbook.Worksheets.Item(1)
$worksheet.Cells.Item(1,1).Value = "Hello"

# Clean up
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($worksheet) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($workbook) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
```

## Registry Operations

### Registry Manipulation

```powershell
# Create registry key
New-Item -Path "HKLM:\Software\MyApp" -Force

# Set registry value
Set-ItemProperty -Path "HKLM:\Software\MyApp" -Name "Version" -Value "1.0.0"

# Read registry value
Get-ItemProperty -Path "HKLM:\Software\MyApp" -Name "Version"

# Remove registry value
Remove-ItemProperty -Path "HKLM:\Software\MyApp" -Name "Version"

# Check if key exists
if (Test-Path "HKLM:\Software\MyApp") {
    Write-Host "Registry key exists"
}
```

### Registry Permissions

```powershell
# Get ACL
$acl = Get-Acl "HKLM:\Software\MyApp"

# Add access rule
$rule = New-Object System.Security.AccessControl.RegistryAccessRule(
    "DOMAIN\User",
    "FullControl",
    "Allow"
)

$acl.SetAccessRule($rule)
Set-Acl "HKLM:\Software\MyApp" $acl
```

## Windows Service Management

### Service Control

```powershell
# Get service status
Get-Service -Name "wuauserv"

# Start service
Start-Service -Name "wuauserv"

# Stop service
Stop-Service -Name "wuauserv" -Force

# Restart service
Restart-Service -Name "wuauserv"

# Set service startup type
Set-Service -Name "wuauserv" -StartupType Automatic
```

### Service Dependencies

```powershell
# Get service dependencies
Get-Service -Name "spooler" -RequiredServices

# Get dependent services
Get-Service -Name "Spooler" -DependentServices
```

## Event Log Integration

### Reading Event Logs

```powershell
# Get recent events
Get-EventLog -LogName System -Newest 10

# Filter by event ID
Get-EventLog -LogName Security -InstanceId 4624 -Newest 100

# Get specific time range
$startTime = (Get-Date).AddHours(-24)
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID = 4624
    StartTime = $startTime
}
```

### Writing to Event Logs

```powershell
# Create custom event source
New-EventLog -LogName "Application" -Source "MyScript"

# Write event
Write-EventLog -LogName "Application" `
               -Source "MyScript" `
               -EntryType Information `
               -EventId 1000 `
               -Message "Script completed successfully"
```

## Windows Server 2012/2016/2019 Specific

### Server Manager Integration

```powershell
# Import Server Manager module
Import-Module ServerManager

# Get Windows features
Get-WindowsFeature

# Install feature
Install-WindowsFeature -Name Web-Server -IncludeManagementTools

# Remove feature
Remove-WindowsFeature -Name Web-Server
```

### IIS Administration

```powershell
# Import IIS module
Import-Module WebAdministration

# Get websites
Get-Website

# Create website
New-Website -Name "MySite" `
             -PhysicalPath "C:\inetpub\wwwroot\mysite" `
             -Port 80

# Get application pools
Get-WebApplicationPool

# Start website
Start-Website -Name "MySite"
```

## Performance Counters

### Performance Monitoring

```powershell
# Get available counters
Get-Counter -ListSet "Processor"

# Get counter data
Get-Counter -Counter "\Processor(_Total)\% Processor Time"

# Continuous monitoring
while ($true) {
    $cpu = Get-Counter -Counter "\Processor(_Total)\% Processor Time"
    Write-Host "CPU: $($cpu.CounterSamples.CookedValue)%"
    Start-Sleep -Seconds 1
}
```

## Best Practices

1. Always check for Windows-specific features before use
2. Use `try/catch` for WMI/COM operations
3. Release COM objects properly
4. Test registry operations in a safe environment
5. Use verbose logging for troubleshooting
6. Validate user input before execution
7. Handle permissions gracefully

## Migration Notes

When migrating to PowerShell 7:

- Replace `Get-WmiObject` with `Get-CimInstance`
- Update Windows-specific APIs to cross-platform alternatives
- Use PowerShell 7 specific features where applicable
- Test all scripts in PS 7 environment
- Update module imports for PS 7 compatibility

## Resources

- [PowerShell 5.1 Documentation](https://docs.microsoft.com/en-us/powershell/scripting/whats-new/what-s-new-in-windows-powershell-50)
- [WMI Classes](https://docs.microsoft.com/en-us/windows/win32/wmisdk/wmi-classes)
- [Active Directory Module](https://docs.microsoft.com/en-us/powershell/module/activedirectory/)
