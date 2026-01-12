<#
.SYNOPSIS
    Sets up PowerShell constrained language mode for security
.DESCRIPTION
    Configures constrained language mode with system lockdown and audit logging
.PARAMETER Mode
    Constrained mode type (FullLanguage, ConstrainedLanguage, Restricted, NoLanguage)
.PARAMETER SystemLockdown
    Apply system-wide lockdown via group policy
.PARAMETER AuditOnly
    Audit without enforcing restrictions
.EXAMPLE
    .\setup_constrained_mode.ps1 -Mode ConstrainedLanguage -SystemLockdown
#>

#Requires -Version 5.1

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('FullLanguage', 'ConstrainedLanguage', 'Restricted', 'NoLanguage')]
    [string]$Mode,
    
    [Parameter(Mandatory=$false)]
    [switch]$SystemLockdown,
    
    [Parameter(Mandatory=$false)]
    [switch]$AuditOnly,
    
    [Parameter(Mandatory=$false)]
    [switch]$EnableScriptBlockLogging,
    
    [Parameter(Mandatory=$false)]
    [switch]$EnableModuleLogging,
    
    [Parameter(Mandatory=$false)]
    [switch]$EnableTranscription,
    
    [Parameter(Mandatory=$false)]
    [string]$TranscriptionPath,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$AllowedCommands = @{}
)

function Get-PowerShellLanguageMode {
    Write-Verbose "Getting current language mode"
    
    $mode = $ExecutionContext.SessionState.LanguageMode
    Write-Host "Current Language Mode: $mode" -ForegroundColor Cyan
    return $mode
}

function Set-ConstrainedLanguageMode {
    param(
        [string]$TargetMode
    )
    
    Write-Verbose "Setting language mode to: $TargetMode"
    
    try {
        if ($PSCmdlet.ShouldProcess("PowerShell Session", "Set language mode to $TargetMode")) {
            $ExecutionContext.SessionState.LanguageMode = [System.Management.Automation.PSLanguageMode]::$TargetMode
            Write-Host "Language mode set to: $TargetMode" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Error "Failed to set language mode: $_"
        return $false
    }
}

function Test-ConstrainedModeCompliance {
    param(
        [string]$RequiredMode
    )
    
    Write-Verbose "Testing constrained mode compliance"
    
    $currentMode = Get-PowerShellLanguageMode
    $isCompliant = $currentMode -eq $RequiredMode
    
    Write-Host "`nCompliance Check:" -ForegroundColor Cyan
    Write-Host "----------------"
    
    if ($isCompliant) {
        Write-Host "✓ Compliant: Language mode is $RequiredMode" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Non-Compliant: Current mode is $currentMode, expected $RequiredMode" -ForegroundColor Red
    }
    
    # Test restricted operations
    Write-Host "`nTesting restricted operations..."
    
    $tests = @(
        @{ Name = "Add-Type"; Command = { Add-Type -TypeDefinition 'public class Test { }' } }
        @{ Name = "New-Object"; Command = { New-Object System.Net.WebClient } }
        @{ Name = "Get-WmiObject"; Command = { Get-WmiObject Win32_Process } }
    )
    
    $results = @()
    
    foreach ($test in $tests) {
        try {
            & $test.Command 2>$null | Out-Null
            $results += [PSCustomObject]@{
                Test = $test.Name
                Result = "Allowed"
                Compliant = $false
            }
        }
        catch {
            $results += [PSCustomObject]@{
                Test = $test.Name
                Result = "Blocked"
                Compliant = $true
            }
        }
    }
    
    $results | Format-Table -AutoSize
    
    return $isCompliant
}

function Set-SystemLockdownPolicy {
    param(
        [string]$TargetMode
    )
    
    Write-Verbose "Configuring system-wide lockdown"
    
    try {
        $registryPath = "HKLM:\SOFTWARE\Microsoft\PowerShell\1\ShellIds"
        
        if (-not (Test-Path $registryPath)) {
            New-Item -Path $registryPath -Force | Out-Null
        }
        
        Set-ItemProperty -Path $registryPath -Name "ConsoleSessionConfigurationName" -Value $TargetMode -Force -ErrorAction Stop
        Set-ItemProperty -Path $registryPath -Name "ScriptExecution" -Value "Enable" -Force -ErrorAction Stop
        
        Write-Host "System lockdown policy configured" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to configure system lockdown: $_"
        return $false
    }
}

function Enable-ScriptBlockLoggingInternal {
    Write-Verbose "Enabling script block logging"
    
    try {
        # Enable script block logging via registry
        $registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
        
        if (-not (Test-Path $registryPath)) {
            New-Item -Path $registryPath -Force | Out-Null
        }
        
        Set-ItemProperty -Path $registryPath -Name "EnableScriptBlockLogging" -Value 1 -Force -ErrorAction Stop
        Set-ItemProperty -Path $registryPath -Name "EnableScriptBlockInvocationLogging" -Value 1 -Force -ErrorAction Stop
        
        Write-Host "Script block logging enabled" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to enable script block logging: $_"
        return $false
    }
}

function Enable-ModuleLoggingInternal {
    Write-Verbose "Enabling module logging"
    
    try {
        $registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging"
        
        if (-not (Test-Path $registryPath)) {
            New-Item -Path $registryPath -Force | Out-Null
        }
        
        Set-ItemProperty -Path $registryPath -Name "EnableModuleLogging" -Value 1 -Force -ErrorAction Stop
        
        $moduleNamesPath = Join-Path $registryPath "ModuleNames"
        if (-not (Test-Path $moduleNamesPath)) {
            New-Item -Path $moduleNamesPath -Force | Out-Null
        }
        
        # Log all modules
        Set-ItemProperty -Path $moduleNamesPath -Name "*" -Value "*" -Force -ErrorAction Stop
        
        Write-Host "Module logging enabled" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to enable module logging: $_"
        return $false
    }
}

function Enable-TranscriptionInternal {
    param(
        [string]$Path
    )
    
    Write-Verbose "Enabling PowerShell transcription"
    
    try {
        $registryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription"
        
        if (-not (Test-Path $registryPath)) {
            New-Item -Path $registryPath -Force | Out-Null
        }
        
        $transcriptionPath = if ($Path) { $Path } else { Join-Path $env:ProgramData "PowerShellTranscripts" }
        
        Set-ItemProperty -Path $registryPath -Name "EnableTranscripting" -Value 1 -Force -ErrorAction Stop
        Set-ItemProperty -Path $registryPath -Name "EnableInvocationHeader" -Value 1 -Force -ErrorAction Stop
        Set-ItemProperty -Path $registryPath -Name "OutputDirectory" -Value $transcriptionPath -Force -ErrorAction Stop
        
        Write-Host "PowerShell transcription enabled" -ForegroundColor Green
        Write-Host "Transcripts will be saved to: $transcriptionPath"
        
        return $true
    }
    catch {
        Write-Error "Failed to enable transcription: $_"
        return $false
    }
}

function Get-SecurityConfiguration {
    Write-Verbose "Retrieving security configuration"
    
    $config = @{
        LanguageMode = Get-PowerShellLanguageMode
        ScriptBlockLogging = $false
        ModuleLogging = $false
        Transcription = $false
    }
    
    # Check script block logging
    $sbLoggingPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
    if (Test-Path $sbLoggingPath) {
        $sbLogging = Get-ItemProperty -Path $sbLoggingPath -ErrorAction SilentlyContinue
        $config.ScriptBlockLogging = if ($sbLogging.EnableScriptBlockLogging -eq 1) { $true } else { $false }
    }
    
    # Check module logging
    $modLoggingPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging"
    if (Test-Path $modLoggingPath) {
        $modLogging = Get-ItemProperty -Path $modLoggingPath -ErrorAction SilentlyContinue
        $config.ModuleLogging = if ($modLogging.EnableModuleLogging -eq 1) { $true } else { $false }
    }
    
    # Check transcription
    $transcriptionPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription"
    if (Test-Path $transcriptionPath) {
        $transcription = Get-ItemProperty -Path $transcriptionPath -ErrorAction SilentlyContinue
        $config.Transcription = if ($transcription.EnableTranscripting -eq 1) { $true } else { $false }
    }
    
    Write-Host "`nSecurity Configuration:" -ForegroundColor Cyan
    Write-Host "---------------------"
    Write-Host "Language Mode: $($config.LanguageMode)"
    Write-Host "Script Block Logging: $(if ($config.ScriptBlockLogging) { 'Enabled' } else { 'Disabled' })"
    Write-Host "Module Logging: $(if ($config.ModuleLogging) { 'Enabled' } else { 'Disabled' })"
    Write-Host "Transcription: $(if ($config.Transcription) { 'Enabled' } else { 'Disabled' })"
    
    return $config
}

try {
    Write-Verbose "Starting constrained mode setup: $Mode"
    
    $currentMode = Get-PowerShellLanguageMode
    
    if ($AuditOnly) {
        Write-Host "`nAuditing current configuration..." -ForegroundColor Cyan
        $config = Get-SecurityConfiguration
        $compliant = Test-ConstrainedModeCompliance -RequiredMode $Mode
        exit (if ($compliant) { 0 } else { 1 })
    }
    
    # Enable additional security features
    if ($EnableScriptBlockLogging) {
        Enable-ScriptBlockLoggingInternal
    }
    
    if ($EnableModuleLogging) {
        Enable-ModuleLoggingInternal
    }
    
    if ($EnableTranscription) {
        Enable-TranscriptionInternal -Path $TranscriptionPath
    }
    
    # Set constrained mode
    $success = Set-ConstrainedLanguageMode -TargetMode $Mode
    
    if (-not $success) {
        exit 1
    }
    
    # Apply system-wide lockdown if requested
    if ($SystemLockdown) {
        Write-Host "`nApplying system-wide lockdown..." -ForegroundColor Cyan
        $lockdownSuccess = Set-SystemLockdownPolicy -TargetMode $Mode
        
        if (-not $lockdownSuccess) {
            Write-Warning "System lockdown failed, but session mode was set"
        }
    }
    
    # Verify configuration
    Write-Host "`nVerifying configuration..." -ForegroundColor Cyan
    $config = Get-SecurityConfiguration
    $compliant = Test-ConstrainedModeCompliance -RequiredMode $Mode
    
    if (-not $compliant) {
        Write-Error "Configuration verification failed"
        exit 1
    }
    
    Write-Verbose "Constrained mode setup completed"
}
catch {
    Write-Error "Constrained mode setup failed: $_"
    exit 1
}
finally {
    Write-Verbose "Setup constrained mode script completed"
}

Export-ModuleMember -Function Get-PowerShellLanguageMode, Set-ConstrainedLanguageMode
