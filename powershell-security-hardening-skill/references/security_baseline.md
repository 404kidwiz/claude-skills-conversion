# PowerShell Security Baseline

## Overview

This guide establishes security baselines for PowerShell environments, including execution policies, constrained language mode, and logging.

## Security Checklist

### Execution Policy

- [ ] Set appropriate execution policy (RemoteSigned recommended)
- [ ] Enforce execution policy across all scopes
- [ ] Regularly audit execution policy compliance
- [ ] Use Group Policy for enterprise-wide enforcement

### Constrained Language Mode

- [ ] Enable constrained language mode for production
- [ ] Test in non-production environment first
- [ ] Document restricted operations
- [ ] Monitor for bypass attempts

### Script Block Logging

- [ ] Enable script block logging
- [ ] Enable invocation header logging
- [ ] Configure log retention policies
- [ ] Regularly review script block logs

### Module Logging

- [ ] Enable module logging
- [ ] Specify modules to log
- [ ] Monitor module usage
- [ ] Alert on suspicious module activity

### Transcription

- [ ] Enable PowerShell transcription
- [ ] Set appropriate transcription path
- [ ] Configure secure storage for transcripts
- [ ] Implement transcript retention policy

## Execution Policy Configuration

### Recommended Settings

```powershell
# Set RemoteSigned for LocalMachine scope
Set-ExecutionPolicy -Scope LocalMachine -ExecutionPolicy RemoteSigned

# Set Restricted for Process scope
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Restricted

# Verify settings
Get-ExecutionPolicy -List
```

### Group Policy Enforcement

```
Computer Configuration → Administrative Templates →
Windows Components → Windows PowerShell

Turn on Script Execution:
- Enabled
- Execution Policy: Allow only signed scripts

```

## Constrained Language Mode

### Enabling Constrained Mode

```powershell
# Set constrained language mode
$ExecutionContext.SessionState.LanguageMode = "ConstrainedLanguage"

# Verify
$ExecutionContext.SessionState.LanguageMode
```

### System-Wide Enforcement

```powershell
# Set system-wide constrained mode
$registryPath = "HKLM:\SOFTWARE\Microsoft\PowerShell\1\ShellIds"
Set-ItemProperty -Path $registryPath -Name "ConsoleSessionConfigurationName" -Value "ConstrainedLanguage"
```

### Testing Constrained Mode

```powershell
# Test restricted operations
try {
    Add-Type -TypeDefinition 'public class Test { }'
    Write-Host "✗ Type creation allowed (NOT SECURE)" -ForegroundColor Red
}
catch {
    Write-Host "✓ Type creation blocked (SECURE)" -ForegroundColor Green
}

try {
    New-Object System.Net.WebClient
    Write-Host "✗ Object creation allowed (NOT SECURE)" -ForegroundColor Red
}
catch {
    Write-Host "✓ Object creation blocked (SECURE)" -ForegroundColor Green
}
```

## Script Block Logging

### Enabling Script Block Logging

```powershell
# Enable script block logging
$registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"

if (-not (Test-Path $registryPath)) {
    New-Item -Path $registryPath -Force
}

Set-ItemProperty -Path $registryPath -Name "EnableScriptBlockLogging" -Value 1 -Force
Set-ItemProperty -Path $registryPath -Name "EnableScriptBlockInvocationLogging" -Value 1 -Force
```

### Analyzing Script Block Logs

```powershell
# Query script block events
$events = Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" `
                      -FilterXPath "*[System[(EventID=4104)]]" `
                      -MaxEvents 100

# Analyze patterns
foreach ($event in $events) {
    $message = $event.Message
    
    if ($message -match "ScriptBlock ID: ([0-9a-f-]+)") {
        $scriptBlockId = $matches[1]
        Write-Host "Script Block ID: $scriptBlockId"
    }
}
```

### Detecting Suspicious Activity

```powershell
function Find-SuspiciousScripts {
    $suspiciousPatterns = @(
        'System.Reflection.Assembly',
        'System.Net.WebClient',
        'Invoke-Expression',
        'DownloadString',
        'IEX'
    )
    
    $events = Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" `
                          -FilterXPath "*[System[(EventID=4104)]]"
    
    foreach ($event in $events) {
        $message = $event.Message
        
        foreach ($pattern in $suspiciousPatterns) {
            if ($message -match $pattern) {
                Write-Host "Suspicious pattern detected: $pattern" -ForegroundColor Red
                Write-Host "Time: $($event.TimeCreated)"
                Write-Host "User: $($event.Properties[4].Value)"
                Write-Host "Message: $($message -split "`n")[0]"
                Write-Host ""
            }
        }
    }
}
```

## Module Logging

### Enabling Module Logging

```powershell
# Enable module logging
$registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging"

if (-not (Test-Path $registryPath)) {
    New-Item -Path $registryPath -Force
}

Set-ItemProperty -Path $registryPath -Name "EnableModuleLogging" -Value 1 -Force

# Specify modules to log
$moduleNamesPath = Join-Path $registryPath "ModuleNames"
if (-not (Test-Path $moduleNamesPath)) {
    New-Item -Path $moduleNamesPath -Force
}

Set-ItemProperty -Path $moduleNamesPath -Name "*" -Value "*" -Force
```

### Monitoring Module Usage

```powershell
function Get-ModuleUsage {
    $events = Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" `
                          -FilterXPath "*[System[(EventID=4103)]]"
    
    $moduleUsage = @{}
    
    foreach ($event in $events) {
        $moduleName = $event.Properties[0].Value
        
        if ($moduleUsage.ContainsKey($moduleName)) {
            $moduleUsage[$moduleName]++
        }
        else {
            $moduleUsage[$moduleName] = 1
        }
    }
    
    $moduleUsage.GetEnumerator() | 
        Sort-Object -Property Value -Descending | 
        Format-Table -AutoSize
}
```

## Transcription

### Enabling Transcription

```powershell
# Enable transcription
$registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription"

if (-not (Test-Path $registryPath)) {
    New-Item -Path $registryPath -Force
}

$transcriptionPath = "C:\Logs\PowerShellTranscripts"
if (-not (Test-Path $transcriptionPath)) {
    New-Item -Path $transcriptionPath -ItemType Directory -Force
}

Set-ItemProperty -Path $registryPath -Name "EnableTranscripting" -Value 1 -Force
Set-ItemProperty -Path $registryPath -Name "EnableInvocationHeader" -Value 1 -Force
Set-ItemProperty -Path $registryPath -Name "OutputDirectory" -Value $transcriptionPath -Force
```

### Configuring Transcription

```powershell
# Start transcription manually
Start-Transcript -Path "C:\Logs\transcript_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

# Stop transcription
Stop-Transcript

# Enable transcription for all sessions
$PSDefaultParameterValues['Start-Transcript:IncludeInvocationHeader'] = $true
```

## Just Enough Administration (JEA)

### Creating JEA Session Configuration

```powershell
# Create role capability file
$roleParams = @{
    Path = ".\AdminRole.psrc"
    VisibleCmdlets = "Get-Service", "Restart-Service"
    VisibleFunctions = "Get-SystemInfo"
    VisibleExternalCommands = "C:\Windows\System32\whoami.exe"
}

New-PSRoleCapabilityFile @roleParams

# Create session configuration file
$sessionParams = @{
    Path = ".\JEAConfig.pssc"
    SessionType = "RestrictedRemoteServer"
    RunAsVirtualAccount = $true
    RoleDefinitions = @{
        "CONTOSO\\JEA_Admins" = @{
            RoleCapabilityFiles = @(".\\AdminRole.psrc")
        }
    }
    TranscriptDirectory = "C:\\Transcripts"
}

New-PSSessionConfigurationFile @sessionParams

# Register session configuration
Register-PSSessionConfiguration -Path ".\JEAConfig.pssc" -Name "JEA" -Force
```

## Code Signing

### Signing Scripts

```powershell
# Get code signing certificate
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1

# Sign script
Set-AuthenticodeSignature -FilePath ".\script.ps1" -Certificate $cert -TimestampServer "http://timestamp.digicert.com"

# Verify signature
Get-AuthenticodeSignature -FilePath ".\script.ps1"
```

### Enforcing Signed Scripts

```powershell
# Require signed scripts only
Set-ExecutionPolicy -Scope LocalMachine -ExecutionPolicy AllSigned

# Test compliance
Get-AuthenticodeSignature -FilePath ".\script.ps1" | Select-Object Status
```

## Monitoring and Alerting

### PowerShell Security Events

```powershell
# Key event IDs to monitor
$securityEventIds = @{
    ScriptBlockExecution = 4104
    ModuleInvocation = 4103
    ModuleLogging = 4103
    PipelineExecution = 4104
    ScriptBlockLogging = 4104
}

# Query events
foreach ($eventId in $securityEventIds.Values) {
    $events = Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" `
                          -FilterXPath "*[System[(EventID=$eventId)]]" `
                          -MaxEvents 50
    
    Write-Host "Event ID $eventId: $($events.Count) events"
}
```

### Alert Configuration

```powershell
# Create scheduled task for monitoring
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\Scripts\Monitor-PowerShell.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "3:00 AM"

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "PowerShell Security Monitor" -Description "Monitor PowerShell security events"
```

## Compliance Scanning

### Security Compliance Check

```powershell
function Test-PowerShellSecurityCompliance {
    $compliance = @{
        ExecutionPolicy = $false
        ScriptBlockLogging = $false
        ModuleLogging = $false
        Transcription = $false
        ConstrainedMode = $false
    }
    
    # Check execution policy
    $policy = Get-ExecutionPolicy -Scope LocalMachine
    if ($policy -in @('RemoteSigned', 'AllSigned')) {
        $compliance.ExecutionPolicy = $true
    }
    
    # Check script block logging
    $sbLogging = (Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -ErrorAction SilentlyContinue).EnableScriptBlockLogging
    if ($sbLogging -eq 1) {
        $compliance.ScriptBlockLogging = $true
    }
    
    # Check module logging
    $modLogging = (Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging" -ErrorAction SilentlyContinue).EnableModuleLogging
    if ($modLogging -eq 1) {
        $compliance.ModuleLogging = $true
    }
    
    # Check transcription
    $transcription = (Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription" -ErrorAction SilentlyContinue).EnableTranscripting
    if ($transcription -eq 1) {
        $compliance.Transcription = $true
    }
    
    # Check constrained mode
    $mode = $ExecutionContext.SessionState.LanguageMode
    if ($mode -eq 'ConstrainedLanguage') {
        $compliance.ConstrainedMode = $true
    }
    
    # Display results
    $compliance.GetEnumerator() | ForEach-Object {
        $status = if ($_.Value) { "✓" } else { "✗" }
        $color = if ($_.Value) { "Green" } else { "Red" }
        Write-Host "$status $($_.Name)" -ForegroundColor $color
    }
    
    return $compliance
}
```

## Best Practices

1. **Defense in Depth**: Layer multiple security controls
2. **Regular Audits**: Review security logs regularly
3. **Test Changes**: Test security changes in non-production
4. **Document**: Document all security configurations
5. **Monitor**: Implement continuous monitoring
6. **Alert**: Set up alerts for suspicious activity
7. **Update**: Keep PowerShell and systems updated
8. **Train**: Train staff on PowerShell security

## Resources

- [PowerShell Security Documentation](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/wsman-credentials-in-security-descriptions)
- [Script Block Logging](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_script_block_logging)
- [JEA Documentation](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/jea/overview)
