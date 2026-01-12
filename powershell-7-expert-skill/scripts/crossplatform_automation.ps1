<#
.SYNOPSIS
    Cross-platform PowerShell 7+ automation script
.DESCRIPTION
    Modern PowerShell 7 automation with cross-platform support, REST APIs, and containers
.PARAMETER TargetOS
    Target operating system (Windows, Linux, macOS)
.PARAMETER Action
    Automation action to perform
.PARAMETER ApiEndpoint
    REST API endpoint URL
.PARAMETER ContainerImage
    Docker container image name
.EXAMPLE
    .\crossplatform_automation.ps1 -TargetOS Linux -Action Deploy -ApiEndpoint "https://api.example.com"
#>

#Requires -Version 7.0

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Windows', 'Linux', 'macOS')]
    [string]$TargetOS,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet('Deploy', 'Configure', 'Monitor', 'Backup')]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [uri]$ApiEndpoint,
    
    [Parameter(Mandatory=$false)]
    [string]$ContainerImage,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$ConfigurationData = @{},
    
    [Parameter(Mandatory=$false)]
    [switch]$DockerAvailable,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipContainerCheck
)

function Get-PlatformInfo {
    Write-Verbose "Getting platform information"
    
    $platform = @{
        OS = [System.Environment]::OSVersion.Platform
        IsWindows = $IsWindows
        IsLinux = $IsLinux
        IsMacOS = $IsMacOS
        PowerShellVersion = $PSVersionTable.PSVersion
        MachineName = $env:COMPUTERNAME ?? $env:HOSTNAME
        HomePath = $HOME
        TempPath = $env:TEMP ?? $env:TMPDIR
    }
    
    Write-Verbose "Platform: $($platform.OS), PowerShell: $($platform.PowerShellVersion)"
    return $platform
}

function Test-CrossPlatformPrerequisites {
    param(
        [string]$OS,
        [string]$Action,
        [bool]$CheckDocker,
        [bool]$SkipContainer
    )
    
    Write-Verbose "Checking prerequisites for $OS"
    
    $issues = @()
    
    switch ($OS) {
        'Windows' {
            if (-not $IsWindows) {
                $issues += "Not running on Windows"
            }
        }
        'Linux' {
            if (-not $IsLinux) {
                $issues += "Not running on Linux"
            }
        }
        'macOS' {
            if (-not $IsMacOS) {
                $issues += "Not running on macOS"
            }
        }
    }
    
    if ($CheckDocker -and -not $SkipContainer) {
        try {
            $dockerVersion = docker --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Verbose "Docker available: $dockerVersion"
            }
            else {
                $issues += "Docker not available"
            }
        }
        catch {
            $issues += "Docker check failed: $_"
        }
    }
    
    if ($issues.Count -gt 0) {
        Write-Warning "Prerequisites check issues:"
        $issues | ForEach-Object { Write-Warning "  - $_" }
        return $false
    }
    
    Write-Verbose "Prerequisites verified"
    return $true
}

function Invoke-RestApiRequest {
    param(
        [uri]$Endpoint,
        [string]$Method = 'GET',
        [hashtable]$Headers = @{},
        [object]$Body
    )
    
    Write-Verbose "Invoking REST API: $Method $Endpoint"
    
    try {
        $params = @{
            Method = $Method
            Uri = $Endpoint
            ErrorAction = 'Stop'
        }
        
        if ($Headers.Count -gt 0) {
            $params.Headers = $Headers
        }
        
        if ($Body) {
            $params.Body = $Body | ConvertTo-Json -Depth 10
            $params.ContentType = 'application/json'
        }
        
        $response = Invoke-RestMethod @params
        Write-Verbose "API request successful"
        return $response
    }
    catch {
        Write-Error "REST API request failed: $_"
        throw
    }
}

function Invoke-DockerOperation {
    param(
        [string]$Image,
        [string]$Operation = 'run',
        [hashtable]$Options = @{}
    )
    
    Write-Verbose "Executing Docker operation: $Operation on $Image"
    
    try {
        $dockerArgs = @($Operation, $Image)
        
        foreach ($key in $Options.Keys) {
            $value = $Options[$key]
            switch ($key) {
                'Ports' {
                    $value | ForEach-Object { $dockerArgs += "-p", $_ }
                }
                'Volumes' {
                    $value | ForEach-Object { $dockerArgs += "-v", $_ }
                }
                'Environment' {
                    $value.GetEnumerator() | ForEach-Object {
                        $dockerArgs += "-e", "$($_.Key)=$($_.Value)"
                    }
                }
                'Name' {
                    $dockerArgs += "--name", $value
                }
                'Detached' {
                    if ($value) { $dockerArgs += "-d" }
                }
            }
        }
        
        $result = docker @dockerArgs 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Verbose "Docker operation successful"
            return $result
        }
        else {
            Write-Error "Docker operation failed: $result"
            throw "Docker command failed"
        }
    }
    catch {
        Write-Error "Docker operation failed: $_"
        throw
    }
}

function Invoke-CrossPlatformDeploy {
    param(
        [string]$OS,
        [uri]$ApiEndpoint,
        [hashtable]$Config,
        [string]$ContainerImage
    )
    
    Write-Verbose "Executing deployment for $OS"
    
    try {
        $platform = Get-PlatformInfo
        
        Write-Host "Platform Information:"
        Write-Host "  OS: $($platform.OS)"
        Write-Host "  PowerShell: $($platform.PowerShellVersion)"
        Write-Host "  Machine: $($platform.MachineName)"
        
        if ($ApiEndpoint) {
            Write-Host "`nConfiguring via API..."
            $apiConfig = Invoke-RestApiRequest -Endpoint $ApiEndpoint -Method 'GET'
            Write-Host "API configuration received"
        }
        
        if ($ContainerImage -and $DockerAvailable) {
            Write-Host "`nDeploying container: $ContainerImage"
            
            $containerOptions = @{
                Name = "ps7-deploy-$([DateTime]::Now.ToString('yyyyMMddHHmmss'))"
                Detached = $true
                Environment = $Config
            }
            
            if ($PSCmdlet.ShouldProcess($ContainerImage, "Deploy container")) {
                $containerId = Invoke-DockerOperation -Image $ContainerImage -Operation 'run' -Options $containerOptions
                Write-Host "Container deployed: $containerId"
            }
        }
        
        Write-Host "`nDeployment completed successfully"
    }
    catch {
        Write-Error "Deployment failed: $_"
        throw
    }
}

function Invoke-CrossPlatformConfigure {
    param(
        [string]$OS,
        [hashtable]$Config
    )
    
    Write-Verbose "Configuring platform: $OS"
    
    try {
        Write-Host "Applying configuration..."
        
        $config.GetEnumerator() | ForEach-Object {
            $key = $_.Key
            $value = $_.Value
            
            Write-Verbose "Setting $key = $value"
            
            switch ($OS) {
                'Windows' {
                    [System.Environment]::SetEnvironmentVariable($key, $value, 'User')
                }
                'Linux' {
                    $envFile = "$HOME/.bashrc"
                    $envLine = "export $key=$value"
                    if (-not (Select-String -Path $envFile -Pattern $key -Quiet -ErrorAction SilentlyContinue)) {
                        Add-Content -Path $envFile -Value $envLine
                    }
                }
                'macOS' {
                    $envFile = "$HOME/.zshrc"
                    $envLine = "export $key=$value"
                    if (-not (Select-String -Path $envFile -Pattern $key -Quiet -ErrorAction SilentlyContinue)) {
                        Add-Content -Path $envFile -Value $envLine
                    }
                }
            }
        }
        
        Write-Host "Configuration applied successfully"
    }
    catch {
        Write-Error "Configuration failed: $_"
        throw
    }
}

try {
    Write-Verbose "Starting cross-platform automation: $Action on $TargetOS"
    
    if (-not (Test-CrossPlatformPrerequisites -OS $TargetOS -Action $Action -CheckDocker $DockerAvailable -SkipContainer $SkipContainerCheck)) {
        exit 1
    }
    
    switch ($Action) {
        'Deploy' {
            Invoke-CrossPlatformDeploy -OS $TargetOS -ApiEndpoint $ApiEndpoint -Config $ConfigurationData -ContainerImage $ContainerImage
        }
        
        'Configure' {
            Invoke-CrossPlatformConfigure -OS $TargetOS -Config $ConfigurationData
        }
        
        'Monitor' {
            Write-Host "Monitoring platform: $TargetOS"
            
            $metrics = @{
                Timestamp = [DateTime]::UtcNow
                Platform = Get-PlatformInfo
                System = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction SilentlyContinue
                Process = Get-Process -Id $PID
            }
            
            $metrics | Format-Table -AutoSize
        }
        
        'Backup' {
            Write-Host "Creating backup for: $TargetOS"
            
            $backupDir = Join-Path -Path $HOME -ChildPath "backups"
            $backupFile = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
            $backupPath = Join-Path -Path $backupDir -ChildPath $backupFile
            
            if (-not (Test-Path $backupDir)) {
                New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
            }
            
            Compress-Archive -Path "$HOME/Documents" -DestinationPath $backupPath -Force -ErrorAction Stop
            Write-Host "Backup created: $backupPath"
        }
    }
    
    Write-Verbose "Cross-platform automation completed"
}
catch {
    Write-Error "Automation failed: $_"
    exit 1
}
finally {
    Write-Verbose "Cross-platform automation script completed"
}

Export-ModuleMember -Function Get-PlatformInfo, Test-CrossPlatformPrerequisites, Invoke-RestApiRequest
