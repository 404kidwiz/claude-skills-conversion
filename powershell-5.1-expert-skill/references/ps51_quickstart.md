# PowerShell 5.1 Expert - Quick Start Guide

## Overview

This skill provides expertise in Windows PowerShell 5.1, the legacy PowerShell version installed on Windows systems. Perfect for managing Windows Server 2012/2016/2019 environments.

## Prerequisites

- Windows operating system with PowerShell 5.1 installed
- Administrative privileges for system-level operations
- Active Directory module for AD operations (RSAT tools)

## Getting Started

### 1. Install Required Modules

```powershell
# Check PowerShell version
$PSVersionTable.PSVersion

# Install RSAT tools (if needed)
Install-WindowsFeature -Name RSAT-AD-PowerShell

# Import modules
Import-Module ActiveDirectory
Import-Module PSDesiredStateConfiguration
```

### 2. Basic AD User Management

```powershell
# Create a user
.\scripts\manage_legacy_ad.ps1 -Username "jdoe" -Action Create -OU "OU=Users,DC=corp,DC=local"

# Enable a user
.\scripts\manage_legacy_ad.ps1 -Username "jdoe" -Action Enable

# Disable a user
.\scripts\manage_legacy_ad.ps1 -Username "jdoe" -Action Disable
```

### 3. WMI/CIM Queries

```powershell
# Query system information
.\scripts\query_wmi.ps1 -QueryClass "Win32_OperatingSystem" -UseCIM

# Query with filter
.\scripts\query_wmi.ps1 -QueryClass "Win32_Processor" -PropertyFilter "Name"

# Query remote computer
.\scripts\query_wmi.ps1 -QueryClass "Win32_Service" -ComputerName "server01"
```

### 4. Deploy DSC Configuration

```powershell
# Compile and apply DSC
.\scripts\deploy_dsc.ps1 -ConfigurationName "WebServerConfig" -TargetNodes "web01","web02" -Mode Apply

# Test DSC compliance
.\scripts\deploy_dsc.ps1 -ConfigurationName "WebServerConfig" -TargetNodes "web01" -Mode Test
```

## Key Concepts

### Execution Policy

PowerShell 5.1 uses execution policies to control script execution:

```powershell
# View current policy
Get-ExecutionPolicy -List

# Set execution policy
Set-ExecutionPolicy -Scope LocalMachine -ExecutionPolicy RemoteSigned
```

### Module Management

```powershell
# List available modules
Get-Module -ListAvailable

# Import a module
Import-Module ActiveDirectory

# Get module commands
Get-Command -Module ActiveDirectory
```

## Common Patterns

### Error Handling

```powershell
try {
    # Your code here
    Get-ADUser -Identity "jdoe"
}
catch {
    Write-Error "Failed to retrieve user: $_"
}
finally {
    # Cleanup code
}
```

### Parameter Validation

```powershell
param(
    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [string]$Username,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('Enable', 'Disable', 'Delete')]
    [string]$Action
)
```

### Verbose Output

```powershell
[CmdletBinding()]
param()

begin {
    Write-Verbose "Starting operation"
}

process {
    Write-Verbose "Processing item: $_"
}

end {
    Write-Verbose "Operation complete"
}
```

## TypeScript Integration

```typescript
import PowerShell51Manager from './scripts/legacy_wrapper';

const ps51 = new PowerShell51Manager('./scripts');

// Manage AD users
await ps51.manageLegacyAD({
  username: 'jdoe',
  action: 'Create',
  ou: 'OU=Users,DC=corp,DC=local',
  groups: ['Developers', 'PowerUsers']
});

// Query WMI
await ps51.queryWMI({
  queryClass: 'Win32_Processor',
  useCIM: true
});
```

## Troubleshooting

### AD Module Not Found

```
Error: The term 'Get-ADUser' is not recognized
```

**Solution:** Install RSAT tools:
```powershell
Install-WindowsFeature -Name RSAT-AD-PowerShell
```

### WMI Access Denied

```
Error: Access denied
```

**Solution:** Run PowerShell as Administrator or use appropriate credentials.

### DSC Compilation Errors

```
Error: The term 'Configuration' is not recognized
```

**Solution:** Import DSC module:
```powershell
Import-Module PSDesiredStateConfiguration
```

## Best Practices

1. Always use `#Requires -Version 5.1` at the top of scripts
2. Implement try/catch/finally blocks for error handling
3. Use `Write-Verbose` for debugging information
4. Validate input parameters with validation attributes
5. Use `ShouldProcess` for destructive operations
6. Test scripts in a non-production environment first

## Next Steps

- Explore the `references/` directory for advanced patterns
- Review `legacy_patterns.md` for PowerShell 5.1 specific techniques
- Check `migration_guide.md` for upgrading to PowerShell 7

## Support

For issues or questions, refer to:
- Microsoft PowerShell 5.1 Documentation
- Windows Server Documentation
- Active Directory PowerShell Module Reference
