# PowerShell 7 Expert - Quick Start Guide

## Overview

This skill provides expertise in PowerShell 7+, the modern cross-platform version of PowerShell. Includes REST API automation, container support, and cloud integration.

## Prerequisites

- PowerShell 7.0 or later installed
- Cross-platform support (Windows, Linux, macOS)
- Internet access for REST API calls (optional)

## Getting Started

### 1. Install PowerShell 7

#### Windows
```powershell
# Using winget
winget install Microsoft.PowerShell

# Or download from GitHub
# https://github.com/PowerShell/PowerShell/releases
```

#### Linux (Ubuntu)
```bash
# Download and install
wget https://github.com/PowerShell/PowerShell/releases/download/v7.4.0/powershell_7.4.0-1.deb_amd64.deb
sudo dpkg -i powershell_7.4.0-1.deb_amd64.deb
```

#### macOS
```bash
# Using Homebrew
brew install powershell
```

### 2. Verify Installation

```powershell
# Check version
$PSVersionTable.PSVersion

# Check platform
if ($IsWindows) { Write-Host "Running on Windows" }
if ($IsLinux) { Write-Host "Running on Linux" }
if ($IsMacOS) { Write-Host "Running on macOS" }
```

### 3. Cross-Platform Automation

```powershell
# Run cross-platform deployment
.\scripts\crossplatform_automation.ps1 -TargetOS Linux -Action Deploy -ApiEndpoint "https://api.example.com"

# Configure platform
.\scripts\crossplatform_automation.ps1 -TargetOS Windows -Action Configure -ConfigurationData @{
    Setting1 = "Value1"
    Setting2 = "Value2"
}

# Monitor platform
.\scripts\crossplatform_automation.ps1 -TargetOS macOS -Action Monitor
```

### 4. REST API Consumption

```powershell
# Basic GET request
.\scripts\rest_api_consumer.ps1 -Uri "https://api.github.com/user" -Method GET

# With authentication
.\scripts\rest_api_consumer.ps1 `
    -Uri "https://api.example.com/data" `
    -Method POST `
    -AuthType Bearer `
    -Token "your-token-here" `
    -Body @{
        name = "Test"
        value = 123
    }

# With retry logic
.\scripts\rest_api_consumer.ps1 `
    -Uri "https://api.example.com/data" `
    -Method GET `
    -MaxRetries 5 `
    -RetryDelaySeconds 2
```

### 5. Publish to PowerShell Gallery

```powershell
# Publish module
.\scripts\publish_to_gallery.ps1 `
    -ModulePath "./MyModule" `
    -ApiKey "your-api-key" `
    -SkipTests:$false

# Publish as prerelease
.\scripts\publish_to_gallery.ps1 `
    -ModulePath "./MyModule" `
    -ApiKey "your-api-key" `
    -Prerelease
```

## Modern PowerShell 7 Features

### Ternary Operator

```powershell
# Old way
$result = if ($condition) { "yes" } else { "no" }

# New way
$result = $condition ? "yes" : "no"
```

### Null-Coalescing Operator

```powershell
# Old way
if ($null -eq $value) {
    $value = "default"
}

# New way
$value = $value ?? "default"
```

### Pipeline Chain Operators

```powershell
# Old way
Get-ChildItem | Where-Object { $_.Extension -eq '.txt' }

# New way
Get-ChildItem | Where-Object Extension -eq '.txt'

# Chain operators
Get-ChildItem | Where-Object Extension -eq '.txt' | ForEach-Object FullName
```

### Foreach Method

```powershell
# Old way
1..5 | ForEach-Object { Write-Host $_ }

# New way
1..5.ForEach({ Write-Host $_ })
```

### Where Method

```powershell
# Old way
$numbers = 1..100
$even = $numbers | Where-Object { $_ % 2 -eq 0 }

# New way
$numbers = 1..100
$even = $numbers.Where({ $_ % 2 -eq 0 })
```

## Container Support

### Docker Integration

```powershell
# Check Docker availability
docker --version

# Run container
docker run -d --name ps7-container -p 8080:80 nginx

# List containers
docker ps

# Stop container
docker stop ps7-container

# Remove container
docker rm ps7-container
```

### PowerShell in Containers

```powershell
# Run PowerShell in container
docker run --rm -it mcr.microsoft.com/powershell:latest

# Mount local directory
docker run --rm -it -v ${PWD}:/data mcr.microsoft.com/powershell:latest

# Run script in container
docker run --rm -v ${PWD}:/data mcr.microsoft.com/powershell:latest pwsh -File /data/script.ps1
```

## TypeScript Integration

```typescript
import PowerShell7Manager from './scripts/ps7_wrapper';

const ps7 = new PowerShell7Manager('./scripts');

// Cross-platform automation
await ps7.crossPlatformAutomation({
  targetOS: 'Linux',
  action: 'Deploy',
  apiEndpoint: 'https://api.example.com',
  containerImage: 'nginx:latest',
  configurationData: {
    ENV: 'production'
  }
});

// REST API call
await ps7.consumeRestApi({
  uri: 'https://api.github.com/user',
  method: 'GET',
  authType: 'Bearer',
  token: 'github-token',
  maxRetries: 3
});

// Publish module
await ps7.publishToGallery({
  modulePath: './MyModule',
  apiKey: 'psgallery-api-key',
  skipTests: false
});
```

## Best Practices

1. Use `#Requires -Version 7.0` for PS 7 specific scripts
2. Check platform compatibility with `$IsWindows`, `$IsLinux`, `$IsMacOS`
3. Use forward slashes `/` for cross-platform paths
4. Implement proper error handling and logging
5. Use PSScriptAnalyzer for code quality
6. Write comprehensive tests with Pester
7. Document all exported functions
8. Use semantic versioning for modules

## Troubleshooting

### PowerShell 7 Not Found

**Error:** pwsh: command not found

**Solution:** Install PowerShell 7 from the official repository

### Cross-Platform Path Issues

**Error:** File not found due to path separators

**Solution:** Use `Join-Path` or forward slashes `/` for paths

### REST API Errors

**Error:** API request failed with status code 401

**Solution:** Check authentication credentials and token validity

### Module Import Failures

**Error:** Could not load file or assembly

**Solution:** Check module dependencies and .NET version requirements

## Next Steps

- Explore the `references/` directory for advanced topics
- Review `modern_ps_guide.md` for PowerShell 7 best practices
- Check `dsc_patterns.md` for Desired State Configuration
- Learn about JEA (Just Enough Administration)

## Support

For issues or questions, refer to:
- [PowerShell 7 Documentation](https://docs.microsoft.com/en-us/powershell/scripting/whats-new/what-s-new-in-powershell-70)
- [PowerShell GitHub Repository](https://github.com/PowerShell/PowerShell)
- [PowerShell Community](https://github.com/PowerShell/PowerShell/discussions)
