<#
.SYNOPSIS
    Scaffolds a new PowerShell module with proper structure
.DESCRIPTION
    Creates a complete module structure with Public, Private, Tests, and Example directories
.PARAMETER ModuleName
    Name of the module to create
.PARAMETER Path
    Base path where module will be created
.PARAMETER Author
    Module author name
.PARAMETER Description
    Module description
.PARAMETER IncludeTests
    Include Pester test structure
.PARAMETER IncludeExamples
    Include example scripts directory
.EXAMPLE
    .\scaffold_module.ps1 -ModuleName "MyModule" -Path "./modules" -Author "John Doe"
#>

#Requires -Version 7.0

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [ValidatePattern('^[a-zA-Z][a-zA-Z0-9_-]*$')]
    [string]$ModuleName,
    
    [Parameter(Mandatory=$false)]
    [string]$Path = ".",
    
    [Parameter(Mandatory=$false)]
    [string]$Author,
    
    [Parameter(Mandatory=$false)]
    [string]$Description = "PowerShell module for $($ModuleName)",
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludeTests,
    
    [Parameter(Mandatory=$false)]
    [switch]$IncludeExamples,
    
    [Parameter(Mandatory=$false)]
    [string]$PowerShellVersion = "5.1",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

function Test-ModuleNaming {
    param(
        [string]$Name
    )
    
    Write-Verbose "Validating module name: $Name"
    
    $errors = @()
    
    if ($Name -match '\s') {
        $errors += "Module name cannot contain spaces"
    }
    
    if ($Name -match '^\d') {
        $errors += "Module name cannot start with a number"
    }
    
    if ($Name -match '[^a-zA-Z0-9_-]') {
        $errors += "Module name contains invalid characters"
    }
    
    if ($errors.Count -gt 0) {
        $errors | ForEach-Object { Write-Error $_ }
        return $false
    }
    
    Write-Verbose "Module name validated"
    return $true
}

function New-ModuleStructure {
    param(
        [string]$Name,
        [string]$BasePath,
        [bool]$CreateTests,
        [bool]$CreateExamples
    )
    
    Write-Verbose "Creating module structure"
    
    $modulePath = Join-Path $BasePath $Name
    
    if (Test-Path $modulePath) {
        if ($Force) {
            Remove-Item -Path $modulePath -Recurse -Force
            Write-Verbose "Removed existing module directory"
        }
        else {
            Write-Error "Module directory already exists: $modulePath"
            throw "Module exists"
        }
    }
    
    $directories = @(
        "$modulePath",
        "$modulePath/Public",
        "$modulePath/Private",
        "$modulePath/Classes",
        "$modulePath/Formats",
        "$modulePath/Types",
        "$modulePath/en-US"
    )
    
    if ($CreateTests) {
        $directories += "$modulePath/Tests"
        $directories += "$modulePath/Tests/Unit"
        $directories += "$modulePath/Tests/Integration"
    }
    
    if ($CreateExamples) {
        $directories += "$modulePath/Examples"
    }
    
    foreach ($dir in $directories) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
        Write-Verbose "Created directory: $dir"
    }
    
    return $modulePath
}

function New-ModuleManifestFile {
    param(
        [string]$Name,
        [string]$ModulePath,
        [string]$Auth,
        [string]$Desc,
        [string]$PSVersion
    )
    
    Write-Verbose "Creating module manifest"
    
    $guid = [System.Guid]::NewGuid().ToString()
    $year = Get-Date -Format "yyyy"
    
    $manifestPath = Join-Path $ModulePath "$Name.psd1"
    
    $manifestContent = @"
# Module manifest for module '$Name'
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

@{

    # Script module or binary module file associated with this manifest.
    RootModule = '$Name.psm1'

    # Version number of this module.
    ModuleVersion = '1.0.0'

    # Supported PSEditions
    CompatiblePSEditions = @('Desktop', 'Core')

    # ID used to uniquely identify this module
    GUID = '$guid'

    # Author of this module
    Author = '$Auth'

    # Company or vendor of this module
    CompanyName = ''

    # Copyright statement for this module
    Copyright = '(c) $year $Auth. All rights reserved.'

    # Description of the functionality provided by this module
    Description = '$Desc'

    # Minimum version of the PowerShell engine required by this module
    PowerShellVersion = '$PSVersion'

    # Name of the PowerShell host required by this module
    # PowerShellHostName = ''

    # Minimum version of the PowerShell host required by this module
    # PowerShellHostVersion = ''

    # Minimum version of Microsoft .NET Framework required by this module
    # DotNetFrameworkVersion = ''

    # Minimum version of the common language runtime (CLR) required by this module
    # ClrVersion = ''

    # Processor architecture (None, X86, Amd64) required by this module
    # ProcessorArchitecture = ''

    # Modules that must be imported into the global environment prior to importing this module
    # RequiredModules = @()

    # Assemblies that must be loaded prior to importing this module
    # RequiredAssemblies = @()

    # Script files (.ps1) that are run in the caller's environment prior to importing this module.
    # ScriptsToProcess = @()

    # Type files (.ps1xml) to be loaded when importing this module
    # TypesToProcess = @()

    # Format files (.ps1xml) to be loaded when importing this module
    # FormatsToProcess = @()

    # Modules to import as nested modules of the module specified in RootModule/ModuleToProcess
    # NestedModules = @()

    # Functions to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no functions to export.
    FunctionsToExport = @()

    # Cmdlets to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no cmdlets to export.
    CmdletsToExport = @()

    # Variables to export from this module
    VariablesToExport = @()

    # Aliases to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no aliases to export.
    AliasesToExport = @()

    # DSC resources to export from this module
    # DscResourcesToExport = @()

    # List of all modules packaged with this module
    # ModuleList = @()

    # List of all files packaged with this module
    # FileList = @()

    # Private data to pass to the module specified in RootModule/ModuleToProcess
    PrivateData = @{

        PSData = @{

            # Tags applied to this module. These help with module discovery in online galleries.
            Tags = @('PowerShell', 'Module')

            # A URL to the license for this module.
            # LicenseUri = ''

            # A URL to the main website for this project.
            # ProjectUri = ''

            # A URL to an icon representing this module.
            # IconUri = ''

            # ReleaseNotes of this module
            # ReleaseNotes = ''

            # Prerelease string of this module
            # Prerelease = ''

            # Flag to indicate whether the module requires explicit user acceptance for install/update/save
            # RequireLicenseAcceptance = $false

            # External dependent modules of this module
            # ExternalModuleDependencies = @()

        } # End of PSData hashtable

    } # End of PrivateData hashtable

    # HelpInfo URI of this module
    # HelpInfoURI = ''

    # Default prefix for commands exported from this module. Override the default prefix using Import-Module -Prefix.
    # DefaultCommandPrefix = ''

}
"@
    
    Set-Content -Path $manifestPath -Value $manifestContent -Encoding UTF8
    Write-Host "Created manifest: $manifestPath"
    
    return $manifestPath
}

function New-ModuleScriptFile {
    param(
        [string]$Name,
        [string]$ModulePath
    )
    
    Write-Verbose "Creating module script file"
    
    $scriptPath = Join-Path $ModulePath "$Name.psm1"
    
    $scriptContent = @"
# $Name module
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

$ErrorActionPreference = 'Stop'

# Load public functions
Get-ChildItem -Path `$PSScriptRoot\Public -Filter *.ps1 | ForEach-Object {
    . `$_.FullName
}

# Load private functions
Get-ChildItem -Path `$PSScriptRoot\Private -Filter *.ps1 | ForEach-Object {
    . `$_.FullName
}

# Export only public functions
$publicFunctions = Get-ChildItem -Path `$PSScriptRoot\Public -Filter *.ps1 | 
                   ForEach-Object { [System.IO.Path]::GetFileNameWithoutExtension(`$_.FullName) }

Export-ModuleMember -Function `$publicFunctions
"@
    
    Set-Content -Path $scriptPath -Value $scriptContent -Encoding UTF8
    Write-Host "Created module script: $scriptPath"
}

function New-TemplateFunction {
    param(
        [string]$ModulePath,
        [string]$FunctionName,
        [string]$Type = 'Public'
    )
    
    Write-Verbose "Creating template function: $FunctionName"
    
    $dirPath = Join-Path $ModulePath $Type
    $filePath = Join-Path $dirPath "$FunctionName.ps1"
    
    $template = @"
<#
.SYNOPSIS
    Brief description of $FunctionName
.DESCRIPTION
    Detailed description of $FunctionName
.PARAMETER Parameter1
    Description of Parameter1
.EXAMPLE
    $FunctionName -Parameter1 value
#>

function $FunctionName {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=`$true)]
        [ValidateNotNullOrEmpty()]
        [string]`$Parameter1
    )

    begin {
        Write-Verbose "Starting $FunctionName"
    }

    process {
        try {
            Write-Verbose "Processing $FunctionName"
            
            # Your logic here
            
            `$result = "Processed: `$Parameter1"
            return `$result
        }
        catch {
            Write-Error "Error in $FunctionName: `$_"
            throw
        }
    }

    end {
        Write-Verbose "Completing $FunctionName"
    }
}
"@
    
    Set-Content -Path $filePath -Value $template -Encoding UTF8
    Write-Verbose "Created function: $filePath"
}

function New-ReadmeFile {
    param(
        [string]$Name,
        [string]$ModulePath,
        [string]$Auth,
        [string]$Desc
    )
    
    Write-Verbose "Creating README file"
    
    $readmePath = Join-Path $ModulePath "README.md"
    
    $readmeContent = @"
# $Name

$Desc

## Installation

\`\`\`powershell
Install-Module -Name $Name
\`\`\`

## Usage

\`\`\`powershell
Import-Module $Name
Get-Command -Module $Name
\`\`\`

## Functions

- \`Get-Something\`: Retrieves something
- \`Set-Something\`: Sets something

## Examples

See the Examples directory for usage examples.

## Contributing

Contributions are welcome!

## License

Copyright (c) $(Get-Date -Format "yyyy") $Auth
"@
    
    Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8
    Write-Host "Created README: $readmePath"
}

try {
    Write-Verbose "Starting module scaffolding: $ModuleName"
    
    if (-not (Test-ModuleNaming -Name $ModuleName)) {
        exit 1
    }
    
    $modulePath = New-ModuleStructure -Name $ModuleName -BasePath $Path -CreateTests $IncludeTests -CreateExamples $IncludeExamples
    
    New-ModuleManifestFile -Name $ModuleName -ModulePath $modulePath -Auth $Author -Desc $Description -PSVersion $PowerShellVersion
    
    New-ModuleScriptFile -Name $ModuleName -ModulePath $modulePath
    
    New-TemplateFunction -ModulePath $modulePath -FunctionName "Get-$ModuleName" -Type 'Public'
    New-TemplateFunction -ModulePath $modulePath -FunctionName "Set-$ModuleName" -Type 'Public'
    
    if ($IncludeTests) {
        $testTemplate = @"
Describe '$ModuleName' {
    BeforeAll {
        Import-Module `$PSScriptRoot\..\$ModuleName.psd1
    }

    It 'Should import successfully' {
        `$module = Get-Module $ModuleName
        `$module | Should -Not -BeNullOrEmpty
    }

    It 'Should export functions' {
        `$functions = Get-Command -Module $ModuleName
        `$functions.Count | Should -BeGreaterThan 0
    }
}
"@
        $testPath = Join-Path $modulePath "Tests\$ModuleName.Tests.ps1"
        Set-Content -Path $testPath -Value $testTemplate -Encoding UTF8
        Write-Host "Created test file: $testPath"
    }
    
    New-ReadmeFile -Name $ModuleName -ModulePath $modulePath -Auth $Author -Desc $Description
    
    Write-Host "`nModule '$ModuleName' created successfully at: $modulePath"
    Write-Host "Next steps:"
    Write-Host "  1. Edit $ModuleName.psd1 to update module information"
    Write-Host "  2. Add functions to Public/ directory"
    Write-Host "  3. Add helper functions to Private/ directory"
    Write-Host "  4. Update FunctionsToExport in the manifest"
    
    Write-Verbose "Module scaffolding completed"
}
catch {
    Write-Error "Module scaffolding failed: $_"
    exit 1
}
finally {
    Write-Verbose "Scaffold module script completed"
}

Export-ModuleMember -Function New-ModuleStructure, New-TemplateFunction
