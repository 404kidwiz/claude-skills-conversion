# Desired State Configuration (DSC) Patterns

## Overview

Desired State Configuration (DSC) is a management platform in PowerShell that enables deploying and managing configuration data for software services and managing the environment in which these services run.

## Basic DSC Configuration

### Simple Configuration

```powershell
# Simple Web Server Configuration
Configuration WebServerConfig {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ComputerName,
        
        [Parameter(Mandatory=$true)]
        [string]$WebsitePath
    )
    
    Node $ComputerName {
        WindowsFeature WebServer {
            Ensure = 'Present'
            Name = 'Web-Server'
        }
        
        File WebsiteContent {
            Ensure = 'Present'
            Type = 'Directory'
            DestinationPath = $WebsitePath
        }
        
        File DefaultPage {
            Ensure = 'Present'
            Type = 'File'
            DestinationPath = Join-Path $WebsitePath 'index.html'
            Contents = '<h1>Hello from DSC!</h1>'
        }
    }
}

# Compile configuration
WebServerConfig -ComputerName 'web01' -WebsitePath 'C:\inetpub\wwwroot'
```

## Advanced DSC Patterns

### Composite Resources

```powershell
# Composite DSC Resource
Configuration CompositeWebsite {
    Import-DscResource -ModuleName PSDesiredStateConfiguration
    
    Node web01 {
        # Install web platform
        WindowsFeature WebServer {
            Ensure = 'Present'
            Name = 'Web-Server'
            IncludeAllSubFeature = $true
        }
        
        # Configure IIS
        Script ConfigureIIS {
            GetScript = {
                @{
                    Result = (Get-Website 'Default Web Site' -ErrorAction SilentlyContinue) -ne $null
                }
            }
            TestScript = {
                (Get-Website 'Default Web Site' -ErrorAction SilentlyContinue) -ne $null
            }
            SetScript = {
                # Configuration logic
            }
        }
    }
}
```

### Configuration Data

```powershell
# Configuration Data
$configData = @{
    AllNodes = @(
        @{
            NodeName = 'web01'
            Role = 'WebServer'
            WebsitePath = 'C:\inetpub\wwwroot'
        },
        @{
            NodeName = 'web02'
            Role = 'WebServer'
            WebsitePath = 'C:\inetpub\wwwroot'
        },
        @{
            NodeName = 'db01'
            Role = 'Database'
            SqlInstance = 'MSSQLSERVER'
        }
    )
}

# Configuration using data
Configuration RoleBasedConfig {
    Node $AllNodes.NodeName {
        switch ($Node.Role) {
            'WebServer' {
                WindowsFeature WebServer {
                    Ensure = 'Present'
                    Name = 'Web-Server'
                }
                
                File Website {
                    Ensure = 'Present'
                    Type = 'Directory'
                    DestinationPath = $Node.WebsitePath
                }
            }
            
            'Database' {
                WindowsFeature SQLServer {
                    Ensure = 'Present'
                    Name = 'SQL-Server'
                }
            }
        }
    }
}

RoleBasedConfig -ConfigurationData $configData
```

### Partial Configurations

```powershell
# Configuration 1: IIS
Configuration IISConfig {
    Node web01 {
        WindowsFeature WebServer {
            Ensure = 'Present'
            Name = 'Web-Server'
        }
    }
}

# Configuration 2: Security
Configuration SecurityConfig {
    Node web01 {
        WindowsFeature Firewall {
            Ensure = 'Present'
            Name = 'Web-Server'
        }
    }
}

# Apply partial configurations
# Compile
IISConfig -OutputPath C:\DSC\IIS
SecurityConfig -OutputPath C:\DSC\Security

# Apply
Start-DscConfiguration -Path C:\DSC\IIS -ComputerName web01 -Wait -Verbose
Start-DscConfiguration -Path C:\DSC\Security -ComputerName web01 -Wait -Verbose
```

## DSC Resources

### Built-in Resources

```powershell
# File resource
File ExampleFile {
    Ensure = 'Present'
    Type = 'File'
    DestinationPath = 'C:\Temp\example.txt'
    Contents = 'Example content'
    Force = $true
}

# Registry resource
Registry ExampleRegistry {
    Ensure = 'Present'
    Key = 'HKLM:\SOFTWARE\Example'
    ValueName = 'Setting'
    ValueData = 'Value'
    ValueType = 'String'
}

# Service resource
Service ExampleService {
    Name = 'wuauserv'
    StartupType = 'Automatic'
    State = 'Running'
}

# WindowsFeature resource
WindowsFeature IIS {
    Ensure = 'Present'
    Name = 'Web-Server'
    IncludeAllSubFeature = $true
}

# Script resource
Script CustomScript {
    GetScript = {
        @{
            Result = (Test-Path 'C:\Temp\checkfile.txt')
        }
    }
    TestScript = {
        Test-Path 'C:\Temp\checkfile.txt'
    }
    SetScript = {
        'Created by DSC' | Out-File 'C:\Temp\checkfile.txt'
    }
}
```

### Custom DSC Resources

```powershell
# Custom resource schema (schema.mof)
[ClassVersion("1.0.0"), FriendlyName("CustomFile")]
class CustomFile : OMI_BaseResource
{
    [Key, Description("Path to file")] String Path;
    [Write, Description("File content")] String Content;
    [Write, Description("Ensure")] String Ensure;
};

# Resource implementation (CustomFile.psm1)
function Get-TargetResource {
    param (
        [string]$Path
    )
    
    if (Test-Path $Path) {
        return @{
            Path = $Path
            Content = Get-Content $Path -Raw
            Ensure = 'Present'
        }
    }
    else {
        return @{
            Path = $Path
            Content = $null
            Ensure = 'Absent'
        }
    }
}

function Set-TargetResource {
    param (
        [string]$Path,
        [string]$Content,
        [string]$Ensure
    )
    
    if ($Ensure -eq 'Present') {
        $Content | Out-File $Path -Encoding UTF8
    }
    else {
        Remove-Item $Path -Force
    }
}

function Test-TargetResource {
    param (
        [string]$Path,
        [string]$Content,
        [string]$Ensure
    )
    
    if (-not (Test-Path $Path)) {
        return $Ensure -eq 'Absent'
    }
    
    $actualContent = Get-Content $Path -Raw
    return $actualContent -eq $Content
}
```

## DSC Pull Server

### Setup Pull Server

```powershell
# Install DSC Service
Configuration PullServer {
    param(
        [string]$NodeName = 'localhost'
    )
    
    Node $NodeName {
        WindowsFeature DSCService {
            Ensure = 'Present'
            Name = 'DSC-Service'
        }
        
        File DSCModulePath {
            Ensure = 'Present'
            Type = 'Directory'
            DestinationPath = 'C:\Program Files\WindowsPowerShell\DscService\Modules'
        }
        
        File DSCConfigurationPath {
            Ensure = 'Present'
            Type = 'Directory'
            DestinationPath = 'C:\Program Files\WindowsPowerShell\DscService\Configuration'
        }
    }
}

PullServer

# Configure LCM
[DscLocalConfigurationManager()]
Configuration SetLCM {
    Node localhost {
        Settings {
            RefreshMode = 'Pull'
            ConfigurationID = '12345678-1234-1234-1234-123456789012'
        }
        
        ConfigurationRepositoryWeb PullSrv {
            ServerURL = 'http://pullserver:8080/PSDSCPullServer.svc'
            AllowUnsecureConnection = $true
        }
    }
}

SetLCM
```

## JEA (Just Enough Administration)

### JEA Configuration

```powershell
# Create JEA Session Configuration
$sessionConfig = @{
    Path = ".\JEAConfig.pssc"
    SessionType = "RestrictedRemoteServer"
    RunAsVirtualAccount = $true
    RoleDefinitions = @{
        "CONTOSO\\JEA_Admins" = @{
            RoleCapabilityFiles = @(".\\AdminRole.psrc")
        }
    }
    TranscriptDirectory = "C:\\Transcripts"
}

New-PSSessionConfigurationFile @sessionConfig

# Register session configuration
Register-PSSessionConfiguration -Path ".\JEAConfig.pssc" -Name "JEA" -Force
```

### Role Capability

```powershell
# Create role capability file
$roleParams = @{
    Path = ".\\AdminRole.psrc"
    VisibleCmdlets = "Get-Service", "Restart-Service", "Get-Process"
    VisibleFunctions = "Get-SystemInfo"
    VisibleExternalCommands = "C:\\Windows\\System32\\whoami.exe"
    ModulesToImport = "ActiveDirectory"
}

New-PSRoleCapabilityFile @roleParams
```

## Testing DSC

### Test Configuration

```powershell
# Test configuration compliance
Test-DscConfiguration -ComputerName web01

# Get DSC configuration status
Get-DscConfigurationStatus -CimSession web01

# Test specific resource
Invoke-DscResource -Name File -Method Test -ModuleName PSDesiredStateConfiguration -Property @{
    DestinationPath = 'C:\Temp\test.txt'
    Ensure = 'Present'
}
```

## Best Practices

1. Use declarative language (describe state, not procedure)
2. Separate configuration from data
3. Use idempotent resources
4. Implement proper error handling
5. Test configurations before deployment
6. Use version control for DSC configurations
7. Document custom resources thoroughly
8. Monitor DSC compliance regularly

## Troubleshooting

### Configuration Compilation Errors

**Error:** Invalid MOF file

**Solution:** Check syntax and resource parameters in configuration script

### LCM Issues

**Error:** LCM is in a disabled state

**Solution:** Enable LCM and set refresh mode
```powershell
Set-DscLocalConfigurationManager -Enabled $true
```

### Resource Failures

**Error:** Resource execution failed

**Solution:** Check resource logs and verify prerequisites

## Resources

- [DSC Documentation](https://docs.microsoft.com/en-us/powershell/dsc/overview)
- [DSC Resources](https://docs.microsoft.com/en-us/powershell/dsc/resources/resources)
- [JEA Documentation](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/jea/overview)
