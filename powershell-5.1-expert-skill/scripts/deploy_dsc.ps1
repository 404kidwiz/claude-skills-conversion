<#
.SYNOPSIS
    Deploys DSC configurations for Windows Server legacy environments
.DESCRIPTION
    PowerShell Desired State Configuration deployment tool with PS 5.1 patterns
.PARAMETER ConfigurationName
    Name of the DSC configuration to deploy
.PARAMETER TargetNodes
    Target computer names or node names
.PARAMETER ConfigurationPath
    Path to the DSC configuration script
.EXAMPLE
    .\deploy_dsc.ps1 -ConfigurationName "WebServerConfig" -TargetNodes "web01","web02"
#>

#Requires -Modules PSDesiredStateConfiguration
#Requires -Version 5.1

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [string]$ConfigurationName,
    
    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [string[]]$TargetNodes,
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigurationPath = ".\$ConfigurationName.ps1",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('Apply', 'Test', 'Publish')]
    [string]$Mode = 'Apply',
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\DSCOutput",
    
    [Parameter(Mandatory=$false)]
    [switch]$Wait,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

function Test-DSCPrerequisites {
    Write-Verbose "Checking DSC prerequisites"
    
    try {
        if (-not (Get-Module -ListAvailable -Name PSDesiredStateConfiguration)) {
            Write-Error "DSC module not available"
            return $false
        }
        
        if (-not (Test-Path $ConfigurationPath)) {
            Write-Error "Configuration file not found: $ConfigurationPath"
            return $false
        }
        
        Write-Verbose "DSC prerequisites verified"
        return $true
    }
    catch {
        Write-Error "Prerequisite check failed: $_"
        return $false
    }
}

function Initialize-DSCEnvironment {
    param(
        [string]$Path
    )
    
    Write-Verbose "Initializing DSC environment at: $Path"
    
    try {
        if (-not (Test-Path $Path)) {
            New-Item -Path $Path -ItemType Directory -Force | Out-Null
            Write-Verbose "Created DSC output directory"
        }
    }
    catch {
        Write-Error "Failed to initialize DSC environment: $_"
        throw
    }
}

function Invoke-DSCConfiguration {
    param(
        [string]$ConfigPath,
        [string]$ConfigName,
        [string]$OutPath,
        [string[]]$Nodes
    )
    
    Write-Verbose "Loading DSC configuration from: $ConfigPath"
    
    try {
        . $ConfigPath
        
        if (-not (Get-Command -Name $ConfigName -ErrorAction SilentlyContinue)) {
            Write-Error "Configuration $ConfigName not found in script"
            throw "Configuration not found"
        }
        
        Write-Verbose "Compiling DSC configuration for nodes: $($Nodes -join ', ')"
        
        $configParams = @{
            ConfigurationName = $ConfigName
            OutputPath = $OutPath
        }
        
        if ($Nodes) {
            $configParams.NodeName = $Nodes
        }
        
        & $ConfigName @configParams
        
        Write-Host "DSC configuration compiled successfully"
        Write-Host "MOF files generated in: $OutPath"
        
        return $true
    }
    catch {
        Write-Error "DSC configuration compilation failed: $_"
        throw
    }
}

function Invoke-DSCApply {
    param(
        [string[]]$Nodes,
        [string]$Path,
        [bool]$WaitFlag
    )
    
    Write-Verbose "Applying DSC configuration"
    
    try {
        foreach ($node in $Nodes) {
            $mofPath = Join-Path -Path $Path -ChildPath "$node.mof"
            
            if (-not (Test-Path $mofPath)) {
                Write-Warning "MOF file not found for node: $node"
                continue
            }
            
            Write-Host "Applying DSC to: $node"
            
            $job = Start-DscConfiguration -Path $Path -ComputerName $node -Force -ErrorAction Stop
            
            if ($WaitFlag) {
                Wait-Job -Job $job -Timeout 600 | Out-Null
                Receive-Job -Job $job
                
                $testResult = Test-DscConfiguration -ComputerName $node
                if ($testResult.InDesiredState) {
                    Write-Host "DSC applied successfully to $node"
                }
                else {
                    Write-Warning "DSC not in desired state on $node"
                }
            }
            else {
                Write-Host "DSC job started for $node (running in background)"
            }
        }
    }
    catch {
        Write-Error "DSC apply failed: $_"
        throw
    }
}

function Invoke-DSCTest {
    param(
        [string[]]$Nodes
    )
    
    Write-Verbose "Testing DSC configuration"
    
    try {
        foreach ($node in $Nodes) {
            Write-Host "Testing DSC on: $node"
            
            $result = Test-DscConfiguration -ComputerName $node -ErrorAction Stop
            
            if ($result.InDesiredState) {
                Write-Host "  ✓ Node $node is in desired state" -ForegroundColor Green
            }
            else {
                Write-Host "  ✗ Node $node is NOT in desired state" -ForegroundColor Red
                
                $resourcesNotInDesiredState = Get-DscConfigurationStatus -CimSession $node | 
                                              Where-Object { $_.Status -ne 'Success' }
                
                if ($resourcesNotInDesiredState) {
                    Write-Host "  Resources not in desired state:"
                    $resourcesNotInDesiredState | ForEach-Object {
                        Write-Host "    - $($_.ResourceID): $($_.Status)"
                    }
                }
            }
        }
    }
    catch {
        Write-Error "DSC test failed: $_"
        throw
    }
}

try {
    Write-Verbose "Starting DSC deployment: $ConfigurationName"
    
    if (-not (Test-DSCPrerequisites)) {
        exit 1
    }
    
    Initialize-DSCEnvironment -Path $OutputPath
    
    if ($PSCmdlet.ShouldProcess($ConfigurationName, "Compile DSC configuration")) {
        Invoke-DSCConfiguration -ConfigPath $ConfigurationPath `
                                -ConfigName $ConfigurationName `
                                -OutPath $OutputPath `
                                -Nodes $TargetNodes
    }
    
    switch ($Mode) {
        'Apply' {
            if ($PSCmdlet.ShouldProcess($TargetNodes, "Apply DSC configuration")) {
                Invoke-DSCApply -Nodes $TargetNodes -Path $OutputPath -WaitFlag:$Wait
            }
        }
        
        'Test' {
            Invoke-DSCTest -Nodes $TargetNodes
        }
        
        'Publish' {
            Write-Host "Configuration published to: $OutputPath"
            Write-Host "Use -Mode Apply to deploy to target nodes"
        }
    }
    
    Write-Verbose "DSC deployment completed"
}
catch {
    Write-Error "DSC deployment failed: $_"
    exit 1
}
finally {
    Write-Verbose "DSC deployment script completed"
}

Export-ModuleMember -Function Invoke-DSCConfiguration, Invoke-DSCApply
