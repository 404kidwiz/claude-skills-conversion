# PowerShell Module Best Practices

## Overview

This guide outlines best practices for developing, testing, and distributing PowerShell modules.

## Code Quality

### PSScriptAnalyzer Rules

```powershell
# Install PSScriptAnalyzer
Install-Module PSScriptAnalyzer

# Run analysis on module
Invoke-ScriptAnalyzer -Path ".\MyModule" -Recurse

# Run specific rules
Invoke-ScriptAnalyzer -Path ".\MyModule" -Rules @(
    'PSUseApprovedVerbs',
    'PSAvoidUsingCmdletAliases',
    'PSProvideCommentHelp'
)

# Enable strict mode
$env:POWERSHELL_FORMAT_SETTINGS = @{
    Enable = $true
    Rules = @('PSUseCorrectCasing')
}
```

### Code Style Guidelines

#### Naming Conventions

```powershell
# Good: Approved verbs
Get-Item
Set-Item
New-Item
Remove-Item
Test-Item
Update-Item

# Bad: Non-approved verbs
Retrieve-Item
Modify-Item
Make-Item
Delete-Item
Check-Item
```

#### Variable Naming

```powershell
# Good: PascalCase for variables, camelCase for parameters
$ServerName
$ConfigurationData
param(
    [string]$serverName,
    [hashtable]$configData
)

# Bad: Inconsistent casing
$servername
$ConfigData
```

### Error Handling

#### Try-Catch-Finally Pattern

```powershell
function Invoke-Operation {
    [CmdletBinding()]
    param(
        [string]$Path
    )
    
    try {
        # Validate input
        if (-not (Test-Path $Path)) {
            throw "Path does not exist: $Path"
        }
        
        # Perform operation
        $result = Get-Content -Path $Path
        
        return $result
    }
    catch [System.IO.FileNotFoundException] {
        Write-Error "File not found: $Path"
        throw
    }
    catch {
        Write-Error "Unexpected error: $_"
        throw
    }
    finally {
        # Cleanup
        Write-Verbose "Operation completed"
    }
}
```

#### Custom Error Messages

```powershell
function Set-Configuration {
    [CmdletBinding()]
    param(
        [string]$Key,
        [string]$Value
    )
    
    try {
        Set-ItemProperty -Path "HKLM:\Software\MyApp" -Name $Key -Value $Value
    }
    catch {
        $errorId = "ConfigurationSetFailed"
        $category = [System.Management.Automation.ErrorCategory]::InvalidOperation
        $errorRecord = [System.Management.Automation.ErrorRecord]::new(
            $_.Exception,
            $errorId,
            $category,
            $Key
        )
        
        $PSCmdlet.WriteError($errorRecord)
    }
}
```

## Parameter Validation

### Built-in Validators

```powershell
param(
    # Validate not null or empty
    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [string]$Name,
    
    # Validate set of values
    [Parameter(Mandatory=$true)]
    [ValidateSet('Enable', 'Disable', 'Toggle')]
    [string]$Action,
    
    # Validate range
    [Parameter(Mandatory=$false)]
    [ValidateRange(1, 100)]
    [int]$Count,
    
    # Validate pattern
    [Parameter(Mandatory=$false)]
    [ValidatePattern('^[a-zA-Z0-9]+$')]
    [string]$Identifier,
    
    # Validate script
    [Parameter(Mandatory=$true)]
    [ValidateScript({
        if (-not (Test-Path $_)) {
            throw "Path does not exist: $_"
        }
        $true
    })]
    [string]$Path,
    
    # Validate length
    [Parameter(Mandatory=$false)]
    [ValidateLength(1, 50)]
    [string]$Description,
    
    # Validate credential
    [Parameter(Mandatory=$false)]
    [pscredential]$Credential
)
```

### Custom Validators

```powershell
function Validate-EmailAddress {
    param(
        [Parameter(Mandatory=$true)]
        [string]$EmailAddress
    )
    
    if ($EmailAddress -notmatch '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$') {
        throw "Invalid email address format"
    }
}

# Usage
param(
    [ValidateScript({
        try {
            Validate-EmailAddress -EmailAddress $_
        }
        catch {
            throw $_
        }
    })]
    [string]$Email
)
```

## Performance Optimization

### Pipeline Best Practices

```powershell
# Good: Use pipeline
Get-ChildItem | Where-Object Extension -eq '.txt' | ForEach-Object Name

# Bad: Use variables
$files = Get-ChildItem
$txtFiles = $files | Where-Object { $_.Extension -eq '.txt' }
$names = $txtFiles | ForEach-Object { $_.Name }
```

### Object Creation

```powershell
# Good: Use PSCustomObject
$object = [PSCustomObject]@{
    Name = "Test"
    Value = 123
}

# Better: Use OrderedDictionary for predictable properties
$object = [PSCustomObject][ordered]@{
    Name = "Test"
    Value = 123
}
```

### Avoid Unnecessary Operations

```powershell
# Bad: Repeated property access
if ($object.Property -eq 'value') {
    $result = $object.Property
}

# Good: Cache property access
$propertyValue = $object.Property
if ($propertyValue -eq 'value') {
    $result = $propertyValue
}
```

## Testing

### Test Organization

```
Tests/
├── Unit/
│   ├── Public/
│   │   ├── Get-Item.Tests.ps1
│   │   └── Set-Item.Tests.ps1
│   └── Private/
│       └── Helper-Function.Tests.ps1
├── Integration/
│   └── EndToEnd.Tests.ps1
└── Tests.ps1
```

### Test Structure

```powershell
Describe "Get-Item Unit Tests" {
    BeforeAll {
        Import-Module "$PSScriptRoot\..\..\MyModule.psd1"
    }
    
    Context "Parameter Validation" {
        It "Should accept valid name" {
            { Get-Item -Name "Test" } | Should -Not -Throw
        }
        
        It "Should reject empty name" {
            { Get-Item -Name "" } | Should -Throw
        }
    }
    
    Context "Output Validation" {
        It "Should return PSObject" {
            $result = Get-Item -Name "Test"
            $result | Should -BeOfType System.Management.Automation.PSObject
        }
        
        It "Should have Name property" {
            $result = Get-Item -Name "Test"
            $result.PSObject.Properties.Name | Should -Contain 'Name'
        }
    }
}
```

## Security

### Secure Strings

```powershell
# Read credential securely
$credential = Get-Credential
$password = $credential.Password | ConvertFrom-SecureString

# Create secure string
$secureString = Read-Host "Enter password" -AsSecureString

# Use in commands
Invoke-Command -ComputerName "server" -Credential $credential
```

### Execution Policy

```powershell
# Check execution policy
Get-ExecutionPolicy -List

# Set execution policy
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Signing Scripts

```powershell
# Sign script
Set-AuthenticodeSignature -FilePath ".\script.ps1" -Certificate $cert

# Verify signature
Get-AuthenticodeSignature -FilePath ".\script.ps1"
```

## Documentation

### Comment-Based Help

```powershell
<#
.SYNOPSIS
    Brief description of the function
.DESCRIPTION
    Detailed description of what the function does
.PARAMETER Parameter1
    Description of Parameter1
.PARAMETER Parameter2
    Description of Parameter2
.EXAMPLE
    PS C:\> Get-Item -Name "Test"
    Returns the item named "Test"
.EXAMPLE
    PS C:\> Get-Item -Id 123
    Returns the item with ID 123
.INPUTS
    String, Integer
.OUTPUTS
    System.Management.Automation.PSObject
.NOTES
    Additional information about the function
.LINK
    https://docs.example.com/get-item
#>
```

### External Documentation

1. **README.md**: Module overview and quick start
2. **CHANGELOG.md**: Version history and changes
3. **LICENSE**: License information
4. **CONTRIBUTING.md**: Contribution guidelines
5. **Examples/**: Usage examples

## Version Management

### Semantic Versioning

```
MAJOR.MINOR.PATCH

MAJOR: Incompatible API changes
MINOR: Backward-compatible functionality additions
PATCH: Backward-compatible bug fixes
```

### Module Manifest Version

```powershell
@{
    ModuleVersion = '1.2.3'
    # ...
}
```

### Release Process

1. Update version in manifest
2. Update CHANGELOG.md
3. Tag release in version control
4. Run tests
5. Publish to gallery
6. Create release notes

## Distribution

### PowerShell Gallery

```powershell
# Publish module
Publish-Module -Path ".\MyModule" -NuGetApiKey "your-api-key"

# Update module
Update-Module -Name MyModule

# Find module
Find-Module -Name MyModule
```

### Private Repository

```powershell
# Register private repository
Register-PSRepository -Name "MyRepo" -SourceLocation "https://myrepo.local/nuget"

# Publish to private repository
Publish-Module -Path ".\MyModule" -NuGetApiKey "your-api-key" -Repository MyRepo
```

## Troubleshooting

### Common Issues

**Issue:** Module not found after installation

**Solution:** Refresh module path
```powershell
Import-Module MyModule -Force
```

**Issue:** Functions not exported

**Solution:** Check FunctionsToExport in manifest
```powershell
Get-Module MyModule | Select-Object ExportedFunctions
```

**Issue:** Tests failing

**Solution:** Run Pester with verbose output
```powershell
Invoke-Pester -Path ".\Tests" -Verbose
```

## Resources

- [PSScriptAnalyzer Rules](https://github.com/PowerShell/PSScriptAnalyzer#rules)
- [Pester Documentation](https://pester.dev/docs/)
- [PowerShell Best Practices](https://docs.microsoft.com/en-us/powershell/scripting/dev-cross-plat/best-practices)
- [PowerShell Gallery Guidelines](https://docs.microsoft.com/en-us/powershell/gallery/psgallery/publishing-guidelines)
