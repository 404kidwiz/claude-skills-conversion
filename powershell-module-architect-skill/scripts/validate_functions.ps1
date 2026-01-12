<#
.SYNOPSIS
    Validates PowerShell module functions against best practices
.DESCRIPTION
    Performs comprehensive validation including syntax, parameter validation, help documentation
.PARAMETER ModulePath
    Path to the module directory
.PARAMETER StrictMode
    Enable strict validation (fail on warnings)
.PARAMETER CheckPSScriptAnalyzer
    Run PSScriptAnalyzer rules
.PARAMETER CheckHelp
    Verify help documentation completeness
.EXAMPLE
    .\validate_functions.ps1 -ModulePath "./MyModule" -StrictMode
#>

#Requires -Version 7.0
#Requires -Modules PSScriptAnalyzer

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateScript({
        if (-not (Test-Path $_)) {
            throw "Module path does not exist: $_"
        }
        $true
    })]
    [string]$ModulePath,
    
    [Parameter(Mandatory=$false)]
    [switch]$StrictMode,
    
    [Parameter(Mandatory=$false)]
    [switch]$CheckPSScriptAnalyzer,
    
    [Parameter(Mandatory=$false)]
    [switch]$CheckHelp,
    
    [Parameter(Mandatory=$false)]
    [switch]$CheckSyntax,
    
    [Parameter(Mandatory=$false)]
    [string[]]$ExcludeRules,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$FunctionWhitelist = @{}
)

function Test-FunctionSyntax {
    param(
        [string]$Path
    )
    
    Write-Verbose "Checking function syntax"
    
    $errors = @()
    $ps1Files = Get-ChildItem -Path $Path -Filter "*.ps1" -File -Recurse
    
    foreach ($file in $ps1Files) {
        try {
            $ast = [System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$null, [ref]$errors)
            
            if ($errors.Count -gt 0) {
                Write-Warning "Syntax errors in $($file.Name):"
                foreach ($err in $errors) {
                    Write-Warning "  Line $($err.Extent.StartLineNumber): $($err.Message)"
                    $errors += [PSCustomObject]@{
                        File = $file.Name
                        Line = $err.Extent.StartLineNumber
                        Message = $err.Message
                        Type = 'Syntax'
                    }
                }
            }
        }
        catch {
            Write-Warning "Could not parse $($file.Name): $_"
        }
    }
    
    return $errors
}

function Test-FunctionHelp {
    param(
        [string]$Path
    )
    
    Write-Verbose "Checking function help documentation"
    
    $missingHelp = @()
    $incompleteHelp = @()
    
    $publicPath = Join-Path $Path "Public"
    
    if (-not (Test-Path $publicPath)) {
        Write-Verbose "No Public directory found"
        return @()
    }
    
    $functionFiles = Get-ChildItem -Path $publicPath -Filter "*.ps1" -File
    
    foreach ($file in $functionFiles) {
        $content = Get-Content -Path $file.FullName -Raw
        $functionName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
        
        # Check for comment-based help
        $hasHelp = $content -match '<#\.(?:SYNOPSIS|DESCRIPTION)'
        
        if (-not $hasHelp) {
            $missingHelp += [PSCustomObject]@{
                Function = $functionName
                File = $file.Name
                Issue = "No comment-based help found"
            }
            Write-Warning "Missing help in $functionName"
            continue
        }
        
        # Check for required help sections
        $requiredSections = @('SYNOPSIS', 'DESCRIPTION', 'PARAMETER', 'EXAMPLE')
        $missingSections = @()
        
        foreach ($section in $requiredSections) {
            if ($content -notmatch "\.\s*$section") {
                $missingSections += $section
            }
        }
        
        if ($missingSections.Count -gt 0) {
            $incompleteHelp += [PSCustomObject]@{
                Function = $functionName
                File = $file.Name
                Issue = "Missing sections: $($missingSections -join ', ')"
            }
            Write-Warning "Incomplete help in $functionName: $($missingSections -join ', ')"
        }
    }
    
    return @($missingHelp + $incompleteHelp)
}

function Test-FunctionParameters {
    param(
        [string]$Path
    )
    
    Write-Verbose "Checking function parameters"
    
    $issues = @()
    $publicPath = Join-Path $Path "Public"
    
    if (-not (Test-Path $publicPath)) {
        return @()
    }
    
    $functionFiles = Get-ChildItem -Path $publicPath -Filter "*.ps1" -File
    
    foreach ($file in $functionFiles) {
        try {
            $tokens = $null
            $parseErrors = $null
            $ast = [System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$parseErrors)
            
            $functionDefinitions = $ast.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $true)
            
            foreach ($func in $functionDefinitions) {
                $functionName = $func.Name
                $params = $func.Body.ParamBlock?.Parameters.Parameters
                
                if (-not $params) {
                    continue
                }
                
                foreach ($param in $params) {
                    $paramName = $param.Name.VariablePath.UserPath
                    
                    # Check for parameter validation
                    $hasValidation = $param.Attributes | Where-Object { 
                        $_.TypeName.FullName -in @(
                            'ValidateNotNullOrEmpty',
                            'ValidateSet',
                            'ValidateRange',
                            'ValidatePattern',
                            'ValidateScript',
                            'ValidateLength'
                        )
                    }
                    
                    # Check for mandatory parameters without validation
                    $isMandatory = $param.Attributes | Where-Object { $_ -is [System.Management.Automation.Language.ParameterAttribute] -and $_.Mandatory }
                    
                    if ($isMandatory -and -not $hasValidation) {
                        $issues += [PSCustomObject]@{
                            Function = $functionName
                            Parameter = $paramName
                            File = $file.Name
                            Issue = "Mandatory parameter without validation"
                        }
                    }
                    
                    # Check for generic parameter types
                    $type = $param.StaticType?.FullName ?? $param.Attributes.TypeConstraint?.TypeName?.FullName ?? "object"
                    
                    if ($type -eq 'object' -or $type -eq 'System.Object') {
                        $issues += [PSCustomObject]@{
                            Function = $functionName
                            Parameter = $paramName
                            File = $file.Name
                            Issue = "Generic parameter type (object)"
                        }
                    }
                }
            }
        }
        catch {
            Write-Warning "Could not parse $($file.Name) for parameters: $_"
        }
    }
    
    return $issues
}

function Invoke-ScriptAnalyzerCheck {
    param(
        [string]$Path,
        [string[]]$ExcludedRules,
        [hashtable]$Whitelist
    )
    
    Write-Verbose "Running PSScriptAnalyzer"
    
    try {
        $allRules = Get-ScriptAnalyzerRule
        
        $rulesToRun = $allRules.RuleName
        if ($ExcludedRules.Count -gt 0) {
            $rulesToRun = $rulesToRun | Where-Object { $_ -notin $ExcludedRules }
        }
        
        $results = Invoke-ScriptAnalyzer -Path $Path -Recurse -Rules $rulesToRun -ErrorAction Stop
        
        $filteredResults = @()
        
        foreach ($result in $results) {
            $ruleName = $result.RuleName
            $fileName = Split-Path $result.ScriptPath -Leaf
            
            if ($Whitelist.ContainsKey($fileName) -and $Whitelist[$fileName] -contains $ruleName) {
                continue
            }
            
            $filteredResults += $result
        }
        
        Write-Host "`nPSScriptAnalyzer Results:"
        Write-Host "-------------------------"
        
        if ($filteredResults.Count -eq 0) {
            Write-Host "No issues found" -ForegroundColor Green
        }
        else {
            $filteredResults | Group-Object -Property RuleName | ForEach-Object {
                Write-Host "`n$($_.Name): $($_.Count) occurrence(s)" -ForegroundColor Yellow
                
                $_.Group | Select-Object -First 3 | ForEach-Object {
                    $file = Split-Path $_.ScriptPath -Leaf
                    Write-Host "  - $file:$($_.Line): $($_.Message)" -ForegroundColor Yellow
                }
            }
        }
        
        return $filteredResults
    }
    catch {
        Write-Error "PSScriptAnalyzer check failed: $_"
        return @()
    }
}

function Invoke-ModuleValidation {
    param(
        [string]$Path,
        [bool]$Strict,
        [bool]$CheckAnalyzer,
        [bool]$CheckHelpDocs,
        [bool]$CheckCodeSyntax,
        [string[]]$Exclude,
        [hashtable]$Whitelist
    )
    
    Write-Host "`n=== Module Validation Report ==="
    Write-Host "Module: $Path"
    Write-Host "Strict Mode: $Strict"
    Write-Host "==================================="
    
    $allIssues = @()
    
    if ($CheckCodeSyntax) {
        Write-Host "`n[1] Syntax Check..."
        $syntaxErrors = Test-FunctionSyntax -Path $Path
        $allIssues += $syntaxErrors
    }
    
    if ($CheckHelpDocs) {
        Write-Host "`n[2] Help Documentation Check..."
        $helpIssues = Test-FunctionHelp -Path $Path
        $allIssues += $helpIssues
    }
    
    $paramIssues = Test-FunctionParameters -Path $Path
    $allIssues += $paramIssues
    
    if ($CheckAnalyzer) {
        Write-Host "`n[3] PSScriptAnalyzer Check..."
        $analyzerIssues = Invoke-ScriptAnalyzerCheck -Path $Path -ExcludedRules $Exclude -Whitelist $Whitelist
        $allIssues += $analyzerIssues
    }
    
    Write-Host "`n=== Summary ==="
    Write-Host "Total issues found: $($allIssues.Count)"
    
    $errorCount = if ($analyzerIssues) { ($analyzerIssues | Where-Object { $_.Severity -eq 'Error' }).Count } else { 0 }
    $warningCount = $allIssues.Count - $errorCount
    
    Write-Host "Errors: $errorCount"
    Write-Host "Warnings: $warningCount"
    
    if ($Strict -and $allIssues.Count -gt 0) {
        Write-Host "`nValidation FAILED (Strict mode enabled)" -ForegroundColor Red
        exit 1
    }
    elseif ($errorCount -gt 0) {
        Write-Host "`nValidation FAILED (Errors found)" -ForegroundColor Red
        exit 1
    }
    else {
        Write-Host "`nValidation PASSED" -ForegroundColor Green
        return $true
    }
}

try {
    Write-Verbose "Starting function validation"
    
    $result = Invoke-ModuleValidation -Path $ModulePath -Strict $StrictMode -CheckAnalyzer $CheckPSScriptAnalyzer -CheckHelpDocs $CheckHelp -CheckCodeSyntax $CheckSyntax -Exclude $ExcludeRules -Whitelist $FunctionWhitelist
    
    Write-Verbose "Function validation completed"
    exit 0
}
catch {
    Write-Error "Function validation failed: $_"
    exit 1
}
finally {
    Write-Verbose "Validate functions script completed"
}

Export-ModuleMember -Function Test-FunctionSyntax, Test-FunctionHelp, Test-FunctionParameters
