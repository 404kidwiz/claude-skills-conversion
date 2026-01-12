<#
.SYNOPSIS
    Configures PowerShell script block logging for security monitoring
.DESCRIPTION
    Enables and configures script block logging with event log integration
.PARAMETER Enable
    Enable script block logging
.PARAMETER LogInvocation
    Enable invocation header logging
.PARAMETER EventLog
    Write to Windows Event Log
.PARAMETER CustomPath
    Custom log file path
.EXAMPLE
    .\configure_script_block_logging.ps1 -Enable -LogInvocation -EventLog
#>

#Requires -Version 5.1

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$false)]
    [switch]$Enable,
    
    [Parameter(Mandatory=$false)]
    [switch]$Disable,
    
    [Parameter(Mandatory=$false)]
    [switch]$LogInvocation,
    
    [Parameter(Mandatory=$false)]
    [switch]$EventLog,
    
    [Parameter(Mandatory=$false)]
    [string]$CustomPath,
    
    [Parameter(Mandatory=$false)]
    [int]$MaxLogSizeMB = 100,
    
    [Parameter(Mandatory=$false)]
    [int]$RetentionDays = 30,
    
    [Parameter(Mandatory=$false)]
    [switch]$TestLogging
)

function Test-ScriptBlockLoggingStatus {
    Write-Verbose "Testing script block logging status"
    
    $status = @{
        Enabled = $false
        InvocationLogging = $false
        RegistryPath = $null
        EventLog = $false
    }
    
    $registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
    
    if (Test-Path $registryPath) {
        $properties = Get-ItemProperty -Path $registryPath -ErrorAction SilentlyContinue
        
        if ($properties.EnableScriptBlockLogging -eq 1) {
            $status.Enabled = $true
        }
        
        if ($properties.EnableScriptBlockInvocationLogging -eq 1) {
            $status.InvocationLogging = $true
        }
        
        $status.RegistryPath = $registryPath
    }
    
    # Check event log
    try {
        $eventLog = Get-WinEvent -ListLog "Microsoft-Windows-PowerShell/Operational" -ErrorAction SilentlyContinue
        if ($eventLog.IsEnabled) {
            $status.EventLog = $true
        }
    }
    catch {
        $status.EventLog = $false
    }
    
    return $status
}

function Enable-ScriptBlockLoggingInternal {
    param(
        [bool]$IncludeInvocation,
        [string]$LogPath
    )
    
    Write-Verbose "Enabling script block logging"
    
    try {
        $registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
        
        if (-not (Test-Path $registryPath)) {
            New-Item -Path $registryPath -Force | Out-Null
            Write-Verbose "Created registry path"
        }
        
        Set-ItemProperty -Path $registryPath -Name "EnableScriptBlockLogging" -Value 1 -Force -ErrorAction Stop
        
        if ($IncludeInvocation) {
            Set-ItemProperty -Path $registryPath -Name "EnableScriptBlockInvocationLogging" -Value 1 -Force -ErrorAction Stop
        }
        
        if ($LogPath) {
            Set-ItemProperty -Path $registryPath -Name "ScriptBlockLoggingPath" -Value $LogPath -Force -ErrorAction Stop
        }
        
        Write-Host "Script block logging enabled" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to enable script block logging: $_"
        return $false
    }
}

function Disable-ScriptBlockLoggingInternal {
    Write-Verbose "Disabling script block logging"
    
    try {
        $registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
        
        if (Test-Path $registryPath) {
            if ($PSCmdlet.ShouldProcess("Script Block Logging", "Disable")) {
                Set-ItemProperty -Path $registryPath -Name "EnableScriptBlockLogging" -Value 0 -Force -ErrorAction Stop
                Set-ItemProperty -Path $registryPath -Name "EnableScriptBlockInvocationLogging" -Value 0 -Force -ErrorAction Stop
                
                Write-Host "Script block logging disabled" -ForegroundColor Yellow
            }
            return $true
        }
        else {
            Write-Host "Script block logging not configured" -ForegroundColor Gray
            return $true
        }
    }
    catch {
        Write-Error "Failed to disable script block logging: $_"
        return $false
    }
}

function Configure-EventLogSettings {
    param(
        [int]$MaxSize,
        [int]$RetentionDays
    )
    
    Write-Verbose "Configuring event log settings"
    
    try {
        $logName = "Microsoft-Windows-PowerShell/Operational"
        $log = Get-WinEvent -ListLog $logName -ErrorAction Stop
        
        $log.MaximumSizeInBytes = $MaxSize * 1MB
        $log.IsEnabled = $true
        
        Write-Host "Event log configured" -ForegroundColor Green
        Write-Host "  Log: $logName"
        Write-Host "  Max Size: $MaxSize MB"
        
        return $true
    }
    catch {
        Write-Error "Failed to configure event log: $_"
        return $false
    }
}

function Invoke-ScriptBlockLoggingTest {
    Write-Verbose "Testing script block logging"
    
    Write-Host "`nRunning test script..." -ForegroundColor Cyan
    
    $testScript = {
        # This should be logged
        $testVar = "Test Value"
        Write-Host "Test complete"
        
        # Function definition - should be logged
        function Test-Function {
            param($Param1)
            return $Param1
        }
        
        # Invoke function - should be logged
        Test-Function -Param1 "Test"
    }
    
    # Execute test script
    try {
        & $testScript 2>&1 | Out-Null
        Write-Host "Test script executed" -ForegroundColor Green
    }
    catch {
        Write-Warning "Test script execution failed: $_"
    }
    
    Write-Host "`nChecking event logs..." -ForegroundColor Cyan
    
    # Wait a moment for logging
    Start-Sleep -Seconds 2
    
    try {
        $events = Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" `
                              -FilterXPath "*[System[(EventID=4104)]]" `
                              -MaxEvents 10 `
                              -ErrorAction SilentlyContinue
        
        if ($events) {
            Write-Host "`nRecent script block events (Event ID 4104):" -ForegroundColor Green
            Write-Host "--------------------------------------------"
            
            foreach ($event in $events | Select-Object -First 5) {
                $time = $event.TimeCreated
                $message = ($event.Message -split "`n")[0]
                
                Write-Host "[$time] $message"
            }
            
            Write-Host "`n✓ Script block logging is working" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "✗ No script block events found" -ForegroundColor Yellow
            Write-Host "This may indicate logging is not yet active or no events have occurred"
            return $false
        }
    }
    catch {
        Write-Warning "Could not retrieve event logs: $_"
        return $false
    }
}

function Get-ScriptBlockLogSummary {
    Write-Verbose "Retrieving script block log summary"
    
    try {
        $last24Hours = (Get-Date).AddHours(-24)
        
        $events = Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" `
                              -FilterXPath "*[System[(EventID=4104) and TimeCreated[@SystemTime > '$($last24Hours.ToUniversalTime():s)']]]" `
                              -ErrorAction SilentlyContinue
        
        $summary = @{
            TotalEvents = if ($events) { $events.Count } else { 0 }
            TimeRange = "Last 24 hours"
            EventTypes = @{}
        }
        
        if ($events) {
            # Analyze event types
            foreach ($event in $events) {
                $message = $event.Message
                
                if ($message -match "Script Block text:") {
                    $summary.EventTypes['ScriptDefinition']++
                }
                elseif ($message -match "CommandInvocation") {
                    $summary.EventTypes['CommandInvocation']++
                }
                elseif ($message -match "VariableReference") {
                    $summary.EventTypes['VariableReference']++
                }
            }
        }
        
        Write-Host "`nScript Block Log Summary:" -ForegroundColor Cyan
        Write-Host "-------------------------"
        Write-Host "Total Events: $($summary.TotalEvents)"
        Write-Host "Time Range: $($summary.TimeRange)"
        Write-Host ""
        Write-Host "Event Types:"
        foreach ($type in $summary.EventTypes.Keys) {
            Write-Host "  $type`: $($summary.EventTypes[$type])"
        }
        
        return $summary
    }
    catch {
        Write-Error "Failed to retrieve log summary: $_"
        return $null
    }
}

try {
    Write-Verbose "Starting script block logging configuration"
    
    if ($Enable -and $Disable) {
        Write-Error "Cannot enable and disable simultaneously"
        exit 1
    }
    
    if (-not $Enable -and -not $Disable -and -not $TestLogging) {
        # Default: show status
        $status = Test-ScriptBlockLoggingStatus
        
        Write-Host "`nScript Block Logging Status:" -ForegroundColor Cyan
        Write-Host "-----------------------------"
        Write-Host "Enabled: $(if ($status.Enabled) { 'Yes' } else { 'No' })"
        Write-Host "Invocation Logging: $(if ($status.InvocationLogging) { 'Yes' } else { 'No' })"
        Write-Host "Event Log: $(if ($status.EventLog) { 'Yes' } else { 'No' })"
        
        if ($status.RegistryPath) {
            Write-Host "Registry Path: $($status.RegistryPath)"
        }
        
        Get-ScriptBlockLogSummary | Out-Null
        
        exit 0
    }
    
    if ($Enable) {
        $success = Enable-ScriptBlockLoggingInternal -IncludeInvocation $LogInvocation -LogPath $CustomPath
        
        if (-not $success) {
            exit 1
        }
        
        if ($EventLog) {
            Configure-EventLogSettings -MaxSize $MaxLogSizeMB -RetentionDays $RetentionDays
        }
    }
    
    if ($Disable) {
        $success = Disable-ScriptBlockLoggingInternal
        
        if (-not $success) {
            exit 1
        }
    }
    
    if ($TestLogging) {
        Invoke-ScriptBlockLoggingTest
    }
    
    Write-Verbose "Script block logging configuration completed"
}
catch {
    Write-Error "Script block logging configuration failed: $_"
    exit 1
}
finally {
    Write-Verbose "Configure script block logging script completed"
}

Export-ModuleMember -Function Test-ScriptBlockLoggingStatus, Enable-ScriptBlockLoggingInternal
