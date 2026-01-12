<#
.SYNOPSIS
    Publishes PowerShell modules to the PowerShell Gallery
.DESCRIPTION
    Comprehensive module publishing with versioning, testing, and validation
.PARAMETER ModulePath
    Path to the module directory
.PARAMETER ApiKey
    PowerShell Gallery API key for publishing
.PARAMETER SkipTests
    Skip running tests before publishing
.PARAMETER Prerelease
    Publish as a prerelease version
.EXAMPLE
    .\publish_to_gallery.ps1 -ModulePath "./MyModule" -ApiKey "your-api-key"
#>

#Requires -Version 7.0
#Requires -Modules PowerShellGet, PSScriptAnalyzer

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [ValidateScript({
        if (-not (Test-Path $_)) {
            throw "Module path does not exist: $_"
        }
        if (-not (Test-Path (Join-Path $_ "$((Split-Path $_ -Leaf)).psd1"))) {
            throw "Module manifest not found in path: $_"
        }
        $true
    })]
    [string]$ModulePath,
    
    [Parameter(Mandatory=$true)]
    [string]$ApiKey,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests,
    
    [Parameter(Mandatory=$false)]
    [switch]$Prerelease,
    
    [Parameter(Mandatory=$false)]
    [string]$Repository = 'PSGallery',
    
    [Parameter(Mandatory=$false)]
    [switch]$Force,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

function Test-ModuleStructure {
    param(
        [string]$Path
    )
    
    Write-Verbose "Validating module structure"
    
    $moduleName = Split-Path $Path -Leaf
    $manifestPath = Join-Path $Path "$moduleName.psd1"
    $modulePath = Join-Path $Path "$moduleName.psm1"
    
    $issues = @()
    
    if (-not (Test-Path $manifestPath)) {
        $issues += "Module manifest not found: $manifestPath"
    }
    
    if (Test-Path $manifestPath) {
        $manifest = Test-ModuleManifest -Path $manifestPath -ErrorAction SilentlyContinue
        if (-not $manifest) {
            $issues += "Invalid module manifest: $manifestPath"
        }
        else {
            Write-Verbose "Module: $($manifest.Name) v$($manifest.Version)"
            
            if ($manifest.PowerShellVersion -lt 5.1) {
                $issues += "Minimum PowerShell version too old: $($manifest.PowerShellVersion)"
            }
        }
    }
    
    $publicFunctions = Join-Path $Path "Public"
    if (Test-Path $publicFunctions) {
        $functionFiles = Get-ChildItem -Path $publicFunctions -Filter "*.ps1" -File
        Write-Verbose "Found $($functionFiles.Count) public functions"
    }
    
    $privateFunctions = Join-Path $Path "Private"
    if (Test-Path $privateFunctions) {
        $privateFiles = Get-ChildItem -Path $privateFunctions -Filter "*.ps1" -File
        Write-Verbose "Found $($privateFiles.Count) private functions"
    }
    
    if ($issues.Count -gt 0) {
        Write-Warning "Module structure issues:"
        $issues | ForEach-Object { Write-Warning "  - $_" }
        return $false
    }
    
    Write-Verbose "Module structure validated"
    return $true
}

function Invoke-PSScriptAnalyzer {
    param(
        [string]$Path,
        [string]$ModuleName
    )
    
    Write-Verbose "Running PSScriptAnalyzer"
    
    try {
        $rules = @(
            'PSUseApprovedVerbs',
            'PSAvoidUsingCmdletAliases',
            'PSAvoidUsingWriteHost',
            'PSProvideCommentHelp',
            'PSAvoidSemicolons',
            'PSUseDeclaredVarsMoreThanAssignments'
        )
        
        $results = Invoke-ScriptAnalyzer -Path $Path -Recurse -Rules $rules -ErrorAction Stop
        
        if ($results) {
            Write-Host "`nScript Analyzer Results:"
            Write-Host "-------------------------"
            $results | Group-Object -Property RuleName | ForEach-Object {
                Write-Host "$($_.Name): $($_.Count) occurrence(s)" -ForegroundColor Yellow
                $_.Group | Select-Object -First 3 | ForEach-Object {
                    Write-Host "  - Line $($_.Line): $($_.Message)" -ForegroundColor Yellow
                }
            }
            
            $errorCount = ($results | Where-Object { $_.Severity -eq 'Error' }).Count
            if ($errorCount -gt 0) {
                Write-Error "Found $errorCount critical issues. Please fix before publishing."
                return $false
            }
        }
        else {
            Write-Host "No issues found by PSScriptAnalyzer" -ForegroundColor Green
        }
        
        return $true
    }
    catch {
        Write-Warning "PSScriptAnalyzer check failed: $_"
        return $false
    }
}

function Test-ModuleDependencies {
    param(
        [string]$Path
    )
    
    Write-Verbose "Checking module dependencies"
    
    $moduleName = Split-Path $Path -Leaf
    $manifestPath = Join-Path $Path "$moduleName.psd1"
    $manifestData = Import-PowerShellDataFile -Path $manifestPath
    
    if ($manifestData.RequiredModules) {
        Write-Host "`nRequired Modules:"
        Write-Host "----------------"
        
        foreach ($dep in $manifestData.RequiredModules) {
            $depName = if ($dep -is [string]) { $dep } else { $dep.ModuleName }
            $depVersion = if ($dep -is [hashtable]) { $dep.ModuleVersion } else { $dep.RequiredVersion }
            
            $installed = Get-Module -ListAvailable -Name $depName -ErrorAction SilentlyContinue
            
            if ($installed) {
                $latestVersion = ($installed | Sort-Object Version -Descending | Select-Object -First 1).Version
                Write-Host "  ✓ $depName (latest: $latestVersion)" -ForegroundColor Green
            }
            else {
                Write-Host "  ✗ $depName (not installed)" -ForegroundColor Red
            }
        }
    }
}

function Invoke-ModuleTests {
    param(
        [string]$Path
    )
    
    Write-Verbose "Running module tests"
    
    $testPath = Join-Path $Path "Tests"
    
    if (-not (Test-Path $testPath)) {
        Write-Warning "No tests found in: $testPath"
        return $true
    }
    
    try {
        $testResults = Invoke-Pester -Path $testPath -PassThru -ErrorAction Stop
        
        if ($testResults.FailedCount -gt 0) {
            Write-Host "`nTest Results: FAILED" -ForegroundColor Red
            Write-Host "Passed: $($testResults.PassedCount)"
            Write-Host "Failed: $($testResults.FailedCount)"
            
            $testResults.Failed | Select-Object -First 5 | ForEach-Object {
                Write-Host "  - $($_.Describe): $($_.Context) - $($_.Name)" -ForegroundColor Red
            }
            
            return $false
        }
        else {
            Write-Host "`nTest Results: PASSED" -ForegroundColor Green
            Write-Host "All $($testResults.PassedCount) tests passed"
            return $true
        }
    }
    catch {
        Write-Warning "Test execution failed: $_"
        return $false
    }
}

function Publish-ModuleToGallery {
    param(
        [string]$Path,
        [string]$Key,
        [string]$Repo,
        [bool]$IsPrerelease,
        [bool]$ForcePublish,
        [bool]$Simulate
    )
    
    Write-Verbose "Publishing module to $Repo"
    
    try {
        $params = @{
            Path = $Path
            NuGetApiKey = $Key
            Repository = $Repo
            ErrorAction = 'Stop'
        }
        
        if ($IsPrerelease) {
            $params.Prerelease = 'alpha'
        }
        
        if ($ForcePublish) {
            $params.Force = $true
        }
        
        if ($Simulate) {
            $params.WhatIf = $true
        }
        
        if ($PSCmdlet.ShouldProcess($Path, "Publish to $Repo")) {
            Publish-Module @params
            Write-Host "Module published successfully to $Repo" -ForegroundColor Green
        }
    }
    catch {
        Write-Error "Publishing failed: $_"
        throw
    }
}

try {
    Write-Verbose "Starting module publishing process"
    
    $moduleName = Split-Path $ModulePath -Leaf
    Write-Host "Publishing Module: $moduleName"
    Write-Host "Repository: $Repository"
    Write-Host "Path: $ModulePath"
    
    if (-not (Test-ModuleStructure -Path $ModulePath)) {
        exit 1
    }
    
    Test-ModuleDependencies -Path $ModulePath
    
    $analyzerPass = Invoke-PSScriptAnalyzer -Path $ModulePath -ModuleName $moduleName
    if (-not $analyzerPass) {
        Write-Warning "PSScriptAnalyzer found issues. Review and fix before publishing."
        if (-not $Force) {
            exit 1
        }
    }
    
    $testsPass = $true
    if (-not $SkipTests) {
        $testsPass = Invoke-ModuleTests -Path $ModulePath
        if (-not $testsPass) {
            Write-Error "Tests failed. Please fix before publishing."
            exit 1
        }
    }
    
    Publish-ModuleToGallery -Path $ModulePath -Key $ApiKey -Repo $Repository -IsPrerelease $Prerelease -ForcePublish $Force -Simulate $WhatIf
    
    Write-Verbose "Module publishing completed"
}
catch {
    Write-Error "Module publishing failed: $_"
    exit 1
}
finally {
    Write-Verbose "Module publishing script completed"
}

Export-ModuleMember -Function Test-ModuleStructure, Invoke-PSScriptAnalyzer
