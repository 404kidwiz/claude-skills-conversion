<#
.SYNOPSIS
    Performs WMI and CIM queries with legacy PowerShell 5.1 compatibility
.DESCRIPTION
    Robust WMI/CIM query tool with fallback mechanisms and detailed logging
.PARAMETER QueryClass
    WMI class to query (e.g., Win32_OperatingSystem)
.PARAMETER PropertyFilter
    Property name to filter results
.PARAMETER FilterExpression
    WQL WHERE clause for filtering
.PARAMETER UseCIM
    Force use of CIM cmdlets instead of WMI
.EXAMPLE
    .\query_wmi.ps1 -QueryClass Win32_Processor -UseCIM
#>

#Requires -Version 5.1

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [string]$QueryClass,
    
    [Parameter(Mandatory=$false)]
    [string]$PropertyFilter,
    
    [Parameter(Mandatory=$false)]
    [string]$FilterExpression,
    
    [Parameter(Mandatory=$false)]
    [switch]$UseCIM,
    
    [Parameter(Mandatory=$false)]
    [string]$ComputerName = $env:COMPUTERNAME,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('Default', 'CimDSProtocol', 'Dcom', 'Wsman')]
    [string]$Protocol = 'Default',
    
    [Parameter(Mandatory=$false)]
    [int]$TimeoutSeconds = 30
)

function Test-WMIConnectivity {
    param(
        [string]$TargetComputer
    )
    
    try {
        $ping = Test-Connection -ComputerName $TargetComputer -Count 1 -Quiet -ErrorAction Stop
        return $ping
    }
    catch {
        Write-Warning "Ping test failed for $TargetComputer: $_"
        return $false
    }
}

function Get-WMIWithFallback {
    param(
        [string]$Class,
        [string]$Filter,
        [string]$Computer,
        [string]$Protocol
    )
    
    Write-Verbose "Attempting WMI query for $Class"
    
    try {
        $wmiParams = @{
            Class = $Class
            ComputerName = $Computer
            ErrorAction = 'Stop'
        }
        
        if ($Filter) {
            $wmiParams.Filter = $Filter
        }
        
        $result = Get-WmiObject @wmiParams
        Write-Verbose "WMI query successful"
        return $result
    }
    catch {
        Write-Warning "WMI query failed: $_"
        throw
    }
}

function Get-CIMWithSession {
    param(
        [string]$Class,
        [string]$Filter,
        [string]$Computer,
        [string]$Protocol,
        [int]$Timeout
    )
    
    Write-Verbose "Attempting CIM query for $Class using $Protocol protocol"
    
    $session = $null
    try {
        $sessionParams = @{
            ComputerName = $Computer
            ErrorAction = 'Stop'
        }
        
        if ($Protocol -ne 'Default') {
            $sessionParams.SessionOption = New-CimSessionOption -Protocol $Protocol
        }
        
        $session = New-CimSession @sessionParams
        
        $cimParams = @{
            ClassName = $Class
            CimSession = $session
            ErrorAction = 'Stop'
        }
        
        if ($Filter) {
            $cimParams.Filter = $Filter
        }
        
        $result = Get-CimInstance @cimParams
        Write-Verbose "CIM query successful"
        return $result
    }
    catch {
        Write-Warning "CIM query failed: $_"
        throw
    }
    finally {
        if ($session) {
            Remove-CimSession -CimSession $session -ErrorAction SilentlyContinue
        }
    }
}

function Format-WMIOutput {
    param(
        [object]$InputObject,
        [string]$PropertyFilter
    )
    
    if (-not $InputObject) {
        return @()
    }
    
    if ($PropertyFilter) {
        $results = $InputObject | Select-Object -Property $PropertyFilter -ErrorAction SilentlyContinue
        return $results
    }
    
    $properties = $InputObject | Get-Member -MemberType Properties | 
                  Select-Object -ExpandProperty Name
    
    $results = $InputObject | Select-Object -Property $properties
    return $results
}

try {
    Write-Verbose "Starting WMI/CIM query for class: $QueryClass"
    
    if (-not (Test-WMIConnectivity -TargetComputer $ComputerName)) {
        Write-Error "Cannot reach computer: $ComputerName"
        exit 1
    }
    
    $results = $null
    
    if ($UseCIM -or $Protocol -ne 'Default') {
        try {
            $results = Get-CIMWithSession -Class $QueryClass `
                                          -Filter $FilterExpression `
                                          -Computer $ComputerName `
                                          -Protocol $Protocol `
                                          -Timeout $TimeoutSeconds
        }
        catch {
            Write-Warning "CIM query failed, attempting WMI fallback"
            $results = Get-WMIWithFallback -Class $QueryClass `
                                          -Filter $FilterExpression `
                                          -Computer $ComputerName
        }
    }
    else {
        $results = Get-WMIWithFallback -Class $QueryClass `
                                      -Filter $FilterExpression `
                                      -Computer $ComputerName
    }
    
    if ($results) {
        $formatted = Format-WMIOutput -InputObject $results -PropertyFilter $PropertyFilter
        
        Write-Host "`nQuery Results:"
        Write-Host "----------------"
        $formatted | Format-Table -AutoSize -Wrap
        
        Write-Host "`nStatistics:"
        Write-Host "-----------"
        Write-Host "Total records: $($results.Count)"
        
        Write-Verbose "Query completed successfully"
        return $formatted
    }
    else {
        Write-Warning "No results found for query class: $QueryClass"
    }
}
catch {
    Write-Error "WMI/CIM query execution failed: $_"
    exit 1
}
finally {
    Write-Verbose "WMI/CIM query script completed"
}

Export-ModuleMember -Function Get-WMIWithFallback, Get-CIMWithSession
