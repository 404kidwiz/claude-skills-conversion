# PowerShell Module Development Guide

## Overview

This guide covers best practices for developing PowerShell modules, including structure, packaging, and distribution.

## Module Structure

### Standard Module Layout

```
MyModule/
├── MyModule.psd1          # Module manifest
├── MyModule.psm1          # Module script
├── Public/                # Public functions
│   ├── Get-Item.ps1
│   ├── Set-Item.ps1
│   └── Remove-Item.ps1
├── Private/               # Private helper functions
│   ├── Helper-Function.ps1
│   └── Utility-Function.ps1
├── Classes/               # PowerShell classes
│   └── MyClass.ps1
├── Formats/               # Format specifications
│   └── MyModule.format.ps1xml
├── Types/                 # Type extensions
│   └── MyModule.types.ps1xml
├── Tests/                 # Pester tests
│   ├── Unit/
│   │   └── Get-Item.Tests.ps1
│   └── Integration/
│       └── Integration.Tests.ps1
├── Examples/              # Example scripts
│   └── Basic-Usage.ps1
├── en-US/                 # Help files
│   └── about_MyModule.help.txt
├── README.md              # Module documentation
└── LICENSE                # License file
```

## Module Manifest

### Creating a Manifest

```powershell
# MyModule.psd1
@{
    RootModule = 'MyModule.psm1'
    ModuleVersion = '1.0.0'
    GUID = '12345678-1234-1234-1234-123456789012'
    Author = 'Your Name'
    CompanyName = 'Your Company'
    Copyright = '(c) 2024 Your Company'
    Description = 'Description of your module'
    PowerShellVersion = '5.1'
    CompatiblePSEditions = @('Desktop', 'Core')
    FunctionsToExport = @('Get-Item', 'Set-Item', 'Remove-Item')
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
    RequiredModules = @()
    Tags = @('PowerShell', 'Module')
    ProjectUri = 'https://github.com/yourusername/MyModule'
    LicenseUri = 'https://github.com/yourusername/MyModule/blob/main/LICENSE'
    ReleaseNotes = 'Initial release'
}
```

### Best Practices for Manifests

1. Use semantic versioning (MAJOR.MINOR.PATCH)
2. Export only public functions (avoid wildcards)
3. Include comprehensive metadata
4. Specify minimum PowerShell version
5. Add tags for discoverability
6. Include project and license URLs
7. Set CompatiblePSEditions for cross-platform support

## Module Script

### Basic Module Script

```powershell
# MyModule.psm1
$ErrorActionPreference = 'Stop'

# Load public functions
Get-ChildItem -Path "$PSScriptRoot\Public" -Filter "*.ps1" | ForEach-Object {
    . $_.FullName
}

# Load private functions
Get-ChildItem -Path "$PSScriptRoot\Private" -Filter "*.ps1" | ForEach-Object {
    . $_.FullName
}

# Export only public functions
$publicFunctions = Get-ChildItem -Path "$PSScriptRoot\Public" -Filter "*.ps1" | 
                   ForEach-Object { [System.IO.Path]::GetFileNameWithoutExtension($_.FullName) }

Export-ModuleMember -Function $publicFunctions
```

## Public Functions

### Function Template

```powershell
# Public/Get-Item.ps1
<#
.SYNOPSIS
    Retrieves items from the system
.DESCRIPTION
    Detailed description of the Get-Item function
.PARAMETER Name
    The name of the item to retrieve
.PARAMETER Id
    The ID of the item to retrieve
.EXAMPLE
    Get-Item -Name "MyItem"
.EXAMPLE
    Get-Item -Id 123
.INPUTS
    None
.OUTPUTS
    System.Management.Automation.PSObject
.NOTES
    Additional information
#>

function Get-Item {
    [CmdletBinding(DefaultParameterSetName='Name')]
    param(
        [Parameter(Mandatory=$true, ParameterSetName='Name')]
        [ValidateNotNullOrEmpty()]
        [string]$Name,
        
        [Parameter(Mandatory=$true, ParameterSetName='Id')]
        [ValidateRange(1, [int]::MaxValue)]
        [int]$Id,
        
        [Parameter(Mandatory=$false)]
        [switch]$IncludeDetails
    )
    
    begin {
        Write-Verbose "Starting Get-Item"
    }
    
    process {
        try {
            Write-Verbose "Processing request"
            
            # Implementation
            $result = [PSCustomObject]@{
                Name = $Name
                Id = $Id
                Details = if ($IncludeDetails) { "Detailed information" } else { $null }
            }
            
            return $result
        }
        catch {
            Write-Error "Error in Get-Item: $_"
            throw
        }
    }
    
    end {
        Write-Verbose "Completing Get-Item"
    }
}
```

### Best Practices for Functions

1. Always use `CmdletBinding()`
2. Include comprehensive comment-based help
3. Use parameter validation
4. Implement proper error handling
5. Use verbose output for debugging
6. Follow PowerShell verb-noun naming
7. Keep functions focused and single-purpose
8. Return objects, not text

## Private Functions

### Helper Function Example

```powershell
# Private/Helper-Function.ps1
function Invoke-ApiCall {
    [CmdletBinding()]
    param(
        [string]$Endpoint,
        [string]$Method = 'GET',
        [hashtable]$Headers = @{}
    )
    
    try {
        $params = @{
            Uri = $Endpoint
            Method = $Method
            Headers = $Headers
            ErrorAction = 'Stop'
        }
        
        return Invoke-RestMethod @params
    }
    catch {
        Write-Error "API call failed: $_"
        throw
    }
}
```

## Classes

### PowerShell Classes

```powershell
# Classes/MyClass.ps1
class MyClass {
    [string]$Name
    [int]$Id
    [bool]$Active
    
    # Constructor
    MyClass([string]$name, [int]$id) {
        $this.Name = $name
        $this.Id = $id
        $this.Active = $true
    }
    
    # Method
    [void] Activate() {
        $this.Active = $true
    }
    
    [void] Deactivate() {
        $this.Active = $false
    }
    
    [string] ToString() {
        return "$($this.Name) ($($this.Id))"
    }
}
```

## Format Specifications

### Custom Formats

```xml
<!-- Formats/MyModule.format.ps1xml -->
<Configuration>
    <ViewDefinitions>
        <View>
            <Name>MyModuleItem</Name>
            <ViewSelectedBy>
                <TypeName>MyModule.Item</TypeName>
            </ViewSelectedBy>
            <TableControl>
                <TableRowEntries>
                    <TableRowEntry>
                        <TableColumnItems>
                            <TableColumnItem>
                                <PropertyName>Id</PropertyName>
                            </TableColumnItem>
                            <TableColumnItem>
                                <PropertyName>Name</PropertyName>
                            </TableColumnItem>
                            <TableColumnItem>
                                <PropertyName>Active</PropertyName>
                            </TableColumnItem>
                        </TableColumnItems>
                    </TableRowEntry>
                </TableRowEntries>
            </TableControl>
        </View>
    </ViewDefinitions>
</Configuration>
```

## Type Extensions

### Adding Type Members

```xml
<!-- Types/MyModule.types.ps1xml -->
<Types>
    <Type>
        <Name>MyModule.Item</Name>
        <Members>
            <ScriptMethod>
                <Name>ToJson</Name>
                <ScriptBlock>
                    $this | ConvertTo-Json -Depth 10
                </ScriptBlock>
            </ScriptMethod>
        </Members>
    </Type>
</Types>
```

## Packaging

### Creating NuGet Package

```powershell
# Update module manifest version
$manifestPath = "MyModule.psd1"
Update-ModuleManifest -Path $manifestPath -ModuleVersion "1.1.0"

# Build module
# Ensure all files are in place

# Test module
Import-Module ".\MyModule.psd1"
Get-Command -Module MyModule

# Create NuGet package
# The module directory is ready for distribution
```

### Using PowerShellGet

```powershell
# Publish to PowerShell Gallery
Publish-Module -Path ".\MyModule" -NuGetApiKey "your-api-key" -Repository PSGallery

# Install from PowerShell Gallery
Install-Module -Name MyModule

# Update module
Update-Module -Name MyModule
```

## Testing

### Pester Tests

```powershell
# Tests/Unit/Get-Item.Tests.ps1
Describe "Get-Item" {
    BeforeAll {
        Import-Module "$PSScriptRoot\..\..\MyModule.psd1"
    }
    
    It "Should import successfully" {
        $module = Get-Module MyModule
        $module | Should -Not -BeNullOrEmpty
    }
    
    It "Should export functions" {
        $functions = Get-Command -Module MyModule
        $functions.Count | Should -BeGreaterThan 0
    }
    
    It "Should retrieve item by name" {
        $result = Get-Item -Name "Test"
        $result.Name | Should -Be "Test"
    }
    
    It "Should throw error for invalid name" {
        { Get-Item -Name "" } | Should -Throw
    }
}
```

## Documentation

### About Topics

```text
# en-US/about_MyModule.help.txt
TOPIC
    about_MyModule

SHORT DESCRIPTION
    A brief description of the MyModule module

LONG DESCRIPTION
    Detailed description of what the module does

EXAMPLES
    Example 1: Basic usage
    PS C:\> Get-Item -Name "Test"

NOTES
    Additional notes and references
```

## Best Practices Summary

1. **Structure**: Follow standard module layout
2. **Manifest**: Use semantic versioning, export only needed members
3. **Functions**: Include comment-based help, use parameter validation
4. **Testing**: Write comprehensive Pester tests
5. **Documentation**: Include README, about topics, and examples
6. **Version Control**: Use Git for source control
7. **CI/CD**: Implement automated testing and deployment
8. **Dependencies**: Specify and manage dependencies correctly
9. **Error Handling**: Implement robust error handling
10. **Performance**: Optimize for performance and resource usage

## Resources

- [PowerShell Module Development](https://docs.microsoft.com/en-us/powershell/scripting/developer/module/how-to-write-a-powershell-module)
- [Pester Testing Framework](https://pester.dev/)
- [PowerShellGet](https://docs.microsoft.com/en-us/powershell/module/powershellget/)
- [PSScriptAnalyzer](https://github.com/PowerShell/PSScriptAnalyzer)
