<#
.SYNOPSIS
    Creates or updates a PowerShell module manifest file
.DESCRIPTION
    Advanced manifest creation with validation, dependency checking, and auto-population
.PARAMETER ModulePath
    Path to the module directory
.PARAMETER ModuleName
    Name of the module
.PARAMETER ManifestPath
    Explicit path to the manifest file
.PARAMETER ScanFunctions
    Automatically scan Public/ directory for functions
.PARAMETER ScanRequiredModules
    Scan module files for required dependencies
.EXAMPLE
    .\create_manifest.ps1 -ModulePath "./MyModule" -ScanFunctions
#>

#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateScript({
        if (-not (Test-Path $_)) {
            throw "Module path does not exist: $_"
        }
        $true
    })]
    [string]$ModulePath,
    
    [Parameter(Mandatory=$false)]
    [string]$ModuleName,
    
    [Parameter(Mandatory=$false)]
    [string]$ManifestPath,
    
    [Parameter(Mandatory=$false)]
    [switch]$ScanFunctions,
    
    [Parameter(Mandatory=$false)]
    [switch]$ScanRequiredModules,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$AdditionalData = @{},
    
    [Parameter(Mandatory=$false)]
    [switch]$Validate
)

function Get-ModuleFunctions {
    param(
        [string]$Path,
        [string]$Type = 'Public'
    )
    
    Write-Verbose "Scanning for $Type functions"
    
    $functionsPath = Join-Path $Path $Type
    
    if (-not (Test-Path $functionsPath)) {
        Write-Verbose "No $Type directory found"
        return @()
    }
    
    $functionFiles = Get-ChildItem -Path $functionsPath -Filter "*.ps1" -File
    $functions = @()
    
    foreach ($file in $functionFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        
        $matches = [regex]::Matches($content, 'function\s+([a-zA-Z][a-zA-Z0-9_-]*)\s*{')
        
        foreach ($match in $matches) {
            $functions += $match.Groups[1].Value
        }
    }
    
    Write-Verbose "Found $($functions.Count) $Type functions"
    return $functions
}

function Get-ModuleDependencies {
    param(
        [string]$Path
    )
    
    Write-Verbose "Scanning for module dependencies"
    
    $dependencies = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    
    $ps1Files = Get-ChildItem -Path $Path -Filter "*.ps1" -File -Recurse
    
    foreach ($file in $ps1Files) {
        $content = Get-Content -Path $file.FullName -Raw
        
        # Find Import-Module statements
        $importMatches = [regex]::Matches($content, 'Import-Module\s+-Name\s+[''"]?([a-zA-Z][a-zA-Z0-9.-]*)')
        foreach ($match in $importMatches) {
            $dependencies.Add($match.Groups[1].Value) | Out-Null
        }
        
        # Find #Requires statements
        $requireMatches = [regex]::Matches($content, '#Requires\s+-Modules\s+([a-zA-Z][a-zA-Z0-9.-]*)')
        foreach ($match in $requireMatches) {
            $dependencies.Add($match.Groups[1].Value) | Out-Null
        }
    }
    
    # Exclude the module itself
    if ($ModuleName) {
        $dependencies.Remove($ModuleName) | Out-Null
    }
    
    Write-Verbose "Found $($dependencies.Count) dependencies"
    return $dependencies
}

function New-ModuleManifestContent {
    param(
        [string]$Name,
        [string]$Path,
        [string[]]$PublicFunctions,
        [string[]]$Dependencies,
        [hashtable]$ExtraData
    )
    
    Write-Verbose "Creating manifest content"
    
    $guid = [System.Guid]::NewGuid().ToString()
    $year = Get-Date -Format "yyyy"
    
    # Check if manifest already exists
    $existingPath = Join-Path $Path "$Name.psd1"
    $existingManifest = $null
    
    if (Test-Path $existingPath) {
        try {
            $existingManifest = Import-PowerShellDataFile -Path $existingPath -ErrorAction Stop
            Write-Verbose "Found existing manifest"
        }
        catch {
            Write-Warning "Could not read existing manifest: $_"
        }
    }
    
    # Use existing values where available
    $author = $existingManifest?.Author ?? ""
    $company = $existingManifest?.CompanyName ?? ""
    $description = $existingManifest?.Description ?? "PowerShell module for $Name"
    $version = $existingManifest?.ModuleVersion ?? "1.0.0"
    $psVersion = $existingManifest?.PowerShellVersion ?? "5.1"
    
    $functionsExport = if ($PublicFunctions.Count -gt 0) {
        $PublicFunctions | ForEach-Object { "'$_'" }
        $PublicFunctions -join "', '"
    } else {
        "@()"
    }
    
    $requiredModules = if ($Dependencies.Count -gt 0) {
        $Dependencies | ForEach-Object { "'$_'" }
        $Dependencies -join "', '"
    } else {
        "@()"
    }
    
    $manifest = @"
# Module manifest for module '$Name'
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

@{

    # Script module or binary module file associated with this manifest.
    RootModule = '$Name.psm1'

    # Version number of this module.
    ModuleVersion = '$version'

    # Supported PSEditions
    CompatiblePSEditions = @('Desktop', 'Core')

    # ID used to uniquely identify this module
    GUID = '$guid'

    # Author of this module
    Author = '$author'

    # Company or vendor of this module
    CompanyName = '$company'

    # Copyright statement for this module
    Copyright = '(c) $year $author. All rights reserved.'

    # Description of the functionality provided by this module
    Description = '$description'

    # Minimum version of the PowerShell engine required by this module
    PowerShellVersion = '$psVersion'

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
    RequiredModules = @($requiredModules)

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
    FunctionsToExport = @($functionsExport)

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
    
    return $manifest
}

function Test-Manifest {
    param(
        [string]$Path
    )
    
    Write-Verbose "Validating manifest"
    
    try {
        $result = Test-ModuleManifest -Path $Path -ErrorAction Stop
        
        Write-Host "Manifest validation passed" -ForegroundColor Green
        Write-Host "  Module: $($result.Name)"
        Write-Host "  Version: $($result.Version)"
        Write-Host "  PowerShell: $($result.PowerShellVersion)"
        Write-Host "  Functions: $($result.ExportedFunctions.Count)"
        Write-Host "  Commands: $($result.ExportedCommands.Count)"
        
        return $true
    }
    catch {
        Write-Error "Manifest validation failed: $_"
        return $false
    }
}

try {
    Write-Verbose "Starting manifest creation"
    
    if ($ManifestPath) {
        $moduleDir = Split-Path $ManifestPath -Parent
        $moduleName = Split-Path $ManifestPath -Leaf -ErrorAction SilentlyContinue
        if ($moduleName -match '\.psd1$') {
            $moduleName = $moduleName -replace '\.psd1$', ''
        }
    }
    elseif ($ModulePath) {
        $moduleDir = $ModulePath
        $moduleName = Split-Path $ModulePath -Leaf
    }
    elseif ($ModuleName) {
        $moduleDir = "."
    }
    else {
        Write-Error "Must specify ModulePath, ModuleName, or ManifestPath"
        exit 1
    }
    
    $publicFunctions = @()
    $dependencies = @()
    
    if ($ScanFunctions) {
        $publicFunctions = Get-ModuleFunctions -Path $moduleDir -Type 'Public'
    }
    
    if ($ScanRequiredModules) {
        $dependencies = Get-ModuleDependencies -Path $moduleDir
    }
    
    $manifestContent = New-ModuleManifestContent -Name $moduleName -Path $moduleDir -PublicFunctions $publicFunctions -Dependencies $dependencies -ExtraData $AdditionalData
    
    if ($ManifestPath) {
        $outputPath = $ManifestPath
    }
    else {
        $outputPath = Join-Path $moduleDir "$moduleName.psd1"
    }
    
    if ($PSCmdlet.ShouldProcess($outputPath, "Create/update manifest")) {
        Set-Content -Path $outputPath -Value $manifestContent -Encoding UTF8
        Write-Host "Manifest created/updated: $outputPath"
        
        if ($publicFunctions.Count -gt 0) {
            Write-Host "Exported functions: $($publicFunctions -join ', ')"
        }
        
        if ($dependencies.Count -gt 0) {
            Write-Host "Required modules: $($dependencies -join ', ')"
        }
    }
    
    if ($Validate) {
        if (-not (Test-Manifest -Path $outputPath)) {
            exit 1
        }
    }
    
    Write-Verbose "Manifest creation completed"
}
catch {
    Write-Error "Manifest creation failed: $_"
    exit 1
}
finally {
    Write-Verbose "Create manifest script completed"
}

Export-ModuleMember -Function Get-ModuleFunctions, Get-ModuleDependencies
