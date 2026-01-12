# PowerShell Migration Guide (5.1 → 7)

## Overview

This guide helps you migrate scripts and modules from Windows PowerShell 5.1 to PowerShell 7+.

## Key Differences

### Platform Support

| Feature | PowerShell 5.1 | PowerShell 7 |
|---------|----------------|---------------|
| Windows Support | Full | Full |
| Linux Support | No | Yes |
| macOS Support | No | Yes |
| ARM64 Support | Limited | Yes |
| Package Manager | MSI, MSIx | MSI, MSIx, ZIP, Linux packages |

### Command Changes

| PowerShell 5.1 | PowerShell 7 | Notes |
|-----------------|---------------|-------|
| `Get-WmiObject` | `Get-CimInstance` | CIM preferred |
| `Invoke-WmiMethod` | `Invoke-CimMethod` | CIM preferred |
| `Register-WmiEvent` | `Register-CimIndicationEvent` | CIM preferred |
| `Remove-WmiObject` | `Remove-CimInstance` | CIM preferred |

## Step-by-Step Migration

### 1. Update Syntax

#### Array Subexpression

**PowerShell 5.1:**
```powershell
$array = @()
$array += "Item1"
$array += "Item2"
```

**PowerShell 7:**
```powershell
$array = @("Item1", "Item2")
# Or use pipeline
$array = @("Item1", "Item2")
```

#### Null-Coalescing

**PowerShell 5.1:**
```powershell
if ($null -eq $value) {
    $value = "default"
}
```

**PowerShell 7:**
```powershell
$value = $value ?? "default"
```

#### Null-Conditional Assignment

**PowerShell 5.1:**
```powershell
if ($object -ne $null) {
    $object.Property = "value"
}
```

**PowerShell 7:**
```powershell
$object?.Property = "value"
```

### 2. Replace WMI with CIM

**PowerShell 5.1:**
```powershell
$process = Get-WmiObject -Class Win32_Process -Filter "Name='notepad.exe'"
```

**PowerShell 7:**
```powershell
$process = Get-CimInstance -ClassName Win32_Process -Filter "Name='notepad.exe'"
```

**PowerShell 5.1:**
```powershell
$wmi = Get-WmiObject -Class Win32_OperatingSystem
Invoke-WmiMethod -InputObject $wmi -Name "Win32Shutdown" -ArgumentList @()
```

**PowerShell 7:**
```powershell
$cim = Get-CimInstance -ClassName Win32_OperatingSystem
Invoke-CimMethod -InputObject $cim -MethodName "Win32Shutdown" -Arguments @{}
```

### 3. Update Platform-Specific Code

**PowerShell 5.1 (Windows-only):**
```powershell
# Use Windows-specific APIs
Add-Type -AssemblyName System.Windows.Forms
```

**PowerShell 7 (Cross-platform):**
```powershell
# Check platform first
if ($IsWindows) {
    Add-Type -AssemblyName System.Windows.Forms
} elseif ($IsLinux) {
    # Use Linux-specific APIs
} elseif ($IsMacOS) {
    # Use macOS-specific APIs
}
```

### 4. Modernize Error Handling

**PowerShell 5.1:**
```powershell
try {
    Get-Item "nonexistent"
}
catch {
    Write-Error $_
}
```

**PowerShell 7:**
```powershell
try {
    Get-Item "nonexistent"
}
catch [System.Management.Automation.ItemNotFoundException] {
    Write-Warning "Item not found"
}
catch {
    Write-Error $_
}
```

### 5. Update Parameter Validation

**PowerShell 5.1:**
```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Path
)
```

**PowerShell 7:**
```powershell
param(
    [Parameter(Mandatory=$true)]
    [ValidateScript({
        if (-not (Test-Path $_)) {
            throw "Path does not exist: $_"
        }
        $true
    })]
    [string]$Path
)
```

## Module Migration

### Update Module Manifest

**PowerShell 5.1:**
```powershell
@{
    ModuleVersion = '1.0.0'
    PowerShellVersion = '5.1'
    CompatiblePSEditions = @('Desktop')
    # ...
}
```

**PowerShell 7:**
```powershell
@{
    ModuleVersion = '1.0.0'
    PowerShellVersion = '5.1'
    CompatiblePSEditions = @('Desktop', 'Core')
    # ...
}
```

### Update #Requires Statements

**PowerShell 5.1:**
```powershell
#Requires -Version 5.1
#Requires -Modules ActiveDirectory
```

**PowerShell 7:**
```powershell
#Requires -Version 7.0
#Requires -Modules @{ ModuleName='ActiveDirectory'; ModuleVersion='1.0.0.0' }
```

## Breaking Changes

### Removed Features

1. **PowerShell Workflow** - Not available in PowerShell 7
2. **PowerShell Snap-ins** - Use modules instead
3. **Some Windows-specific APIs** - May not work on Linux/macOS

### Behavioral Changes

1. **Case sensitivity** - PowerShell 7 on Linux is case-sensitive
2. **File paths** - Use forward slashes `/` for cross-platform compatibility
3. **Culture settings** - Default to en-US, may differ on different OS

## Testing Checklist

Before deploying PowerShell 7 scripts:

- [ ] Test on Windows
- [ ] Test on Linux (if applicable)
- [ ] Test on macOS (if applicable)
- [ ] Verify all WMI calls converted to CIM
- [ ] Check Windows-specific APIs
- [ ] Test file path handling
- [ ] Verify module compatibility
- [ ] Test error handling
- [ ] Validate parameter types

## Example Migration

### Before (PowerShell 5.1)

```powershell
# Get-Service.ps1
[CmdletBinding()]
param(
    [string]$ComputerName = $env:COMPUTERNAME
)

$services = Get-WmiObject -Class Win32_Service -ComputerName $ComputerName

foreach ($service in $services) {
    $status = switch ($service.State) {
        'Running' { [System.ConsoleColor]::Green }
        'Stopped' { [System.ConsoleColor]::Red }
        default { [System.ConsoleColor]::Yellow }
    }
    
    Write-Host "$($service.Name) - $($service.State)" -ForegroundColor $status
}
```

### After (PowerShell 7)

```powershell
# Get-Service.ps1
#Requires -Version 7.0

[CmdletBinding()]
param(
    [string]$ComputerName = $env:COMPUTERNAME
)

$services = Get-CimInstance -ClassName Win32_Service -ComputerName $ComputerName

foreach ($service in $services) {
    $status = switch ($service.State) {
        'Running' { 'Green' }
        'Stopped' { 'Red' }
        default { 'Yellow' }
    }
    
    Write-Host "$($service.Name) - $($service.State)" -ForegroundColor $status
}
```

## Troubleshooting

### Common Issues

**Issue:** Script fails on Linux with case sensitivity errors

**Solution:** Use consistent casing for variable and function names

**Issue:** WMI cmdlets not found

**Solution:** Replace with CIM cmdlets

**Issue:** Windows-specific APIs not available

**Solution:** Add platform checks or use cross-platform alternatives

## Additional Resources

- [PowerShell 7 Release Notes](https://docs.microsoft.com/en-us/powershell/scripting/whats-new/what-s-new-in-powershell-70)
- [PowerShell 7 Compatibility](https://docs.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell)
- [About_PS_ISE](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_ps_ise)
