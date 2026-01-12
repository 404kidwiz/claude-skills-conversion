# DNS Configuration and Management Script

<#
.SYNOPSIS
    Configures and manages DNS zones and records

.DESCRIPTION
    This script provides comprehensive DNS management functionality including
    zone creation, record management, and DNS health checks.

.PARAMETER Action
    The action to perform (CreateZone, CreateRecord, DeleteRecord, QueryDNS, TestDNS)

.PARAMETER ZoneName
    The DNS zone name

.PARAMETER RecordName
    The DNS record name

.PARAMETER RecordType
    The DNS record type (A, AAAA, CNAME, MX, NS, TXT, SRV)

.PARAMETER RecordData
    The data for the DNS record

.PARAMETER DNSServer
    The DNS server to manage (default: local)

.EXAMPLE
    .\configure_dns.ps1 -Action CreateZone -ZoneName "example.com"
.EXAMPLE
    .\configure_dns.ps1 -Action CreateRecord -ZoneName "example.com" -RecordName "www" -RecordType "A" -RecordData "192.168.1.10"
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('CreateZone', 'CreateRecord', 'DeleteRecord', 'QueryDNS', 'TestDNS', 'ListZones')]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [string]$ZoneName,

    [Parameter(Mandatory=$false)]
    [string]$RecordName,

    [Parameter(Mandatory=$false)]
    [ValidateSet('A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SRV', 'PTR')]
    [string]$RecordType,

    [Parameter(Mandatory=$false)]
    [string]$RecordData,

    [Parameter(Mandatory=$false)]
    [int]$Priority,

    [Parameter(Mandatory=$false)]
    [string]$DNSServer = $env:COMPUTERNAME,

    [Parameter(Mandatory=$false)]
    [string]$LogPath = ".\dns_management.log"
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet('INFO', 'WARNING', 'ERROR')]
        [string]$Level = 'INFO'
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    Write-Host $logEntry
    Add-Content -Path $LogPath -Value $logEntry
}

function Test-DNSServerAvailable {
    param([string]$Server)

    try {
        Test-Connection -ComputerName $Server -Count 1 -Quiet
    }
    catch {
        Write-Log "DNS server $Server is not reachable" -Level 'ERROR'
        return $false
    }
}

function Test-IPAddress {
    param([string]$IPAddress)

    return $IPAddress -match '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
}

function New-DNSZoneAdvanced {
    param(
        [string]$ZoneName,
        [string]$DNSServer
    )

    Write-Log "Creating DNS zone: $ZoneName" -Level 'INFO'

    if (-not (Test-DNSServerAvailable -Server $DNSServer)) {
        return @{
            Success = $false
            Error = "DNS server not reachable"
        }
    }

    try {
        Add-DnsServerPrimaryZone -Name $ZoneName -ComputerName $DNSServer -ReplicationScope Forest
        Write-Log "DNS zone $ZoneName created successfully" -Level 'INFO'

        return @{
            Success = $true
            ZoneName = $ZoneName
        }
    }
    catch {
        if ($_.Exception.Message -match 'zone already exists') {
            Write-Log "DNS zone $ZoneName already exists" -Level 'WARNING'
            return @{
                Success = $false
                Error = "Zone already exists"
            }
        }
        Write-Log "Failed to create DNS zone $ZoneName`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function New-DNSRecordAdvanced {
    param(
        [string]$ZoneName,
        [string]$RecordName,
        [string]$RecordType,
        [string]$RecordData,
        [int]$Priority,
        [string]$DNSServer
    )

    Write-Log "Creating DNS record: $RecordName.$ZoneName ($RecordType)" -Level 'INFO'

    if (-not (Test-DNSServerAvailable -Server $DNSServer)) {
        return @{
            Success = $false
            Error = "DNS server not reachable"
        }
    }

    try {
        $fullRecordName = if ($RecordName -eq $ZoneName -or $RecordName -eq '@') {
            $ZoneName
        }
        else {
            "$RecordName.$ZoneName"
        }

        switch ($RecordType) {
            'A' {
                if (-not (Test-IPAddress -IPAddress $RecordData)) {
                    throw "Invalid IP address format: $RecordData"
                }
                Add-DnsServerResourceRecordA -Name $RecordName -ZoneName $ZoneName -IPv4Address $RecordData -ComputerName $DNSServer
            }
            'AAAA' {
                Add-DnsServerResourceRecordAAAA -Name $RecordName -ZoneName $ZoneName -IPv6Address $RecordData -ComputerName $DNSServer
            }
            'CNAME' {
                Add-DnsServerResourceRecordCName -Name $RecordName -ZoneName $ZoneName -HostNameAlias $RecordData -ComputerName $DNSServer
            }
            'MX' {
                if (-not $Priority) {
                    throw "Priority is required for MX records"
                }
                Add-DnsServerResourceRecordMX -Name $RecordName -ZoneName $ZoneName -MailExchange $RecordData -Preference $Priority -ComputerName $DNSServer
            }
            'TXT' {
                Add-DnsServerResourceRecordTxt -Name $RecordName -ZoneName $ZoneName -DescriptiveText $RecordData -ComputerName $DNSServer
            }
            'SRV' {
                $service, $proto, $port = $RecordName -split '\.'
                Add-DnsServerResourceRecordSRV -Name "$service.$proto" -ZoneName $ZoneName -DomainName $RecordData -Port $port -Priority $Priority -ComputerName $DNSServer
            }
            default {
                throw "Unsupported record type: $RecordType"
            }
        }

        Write-Log "DNS record $fullRecordName created successfully" -Level 'INFO'

        return @{
            Success = $true
            RecordName = $fullRecordName
            RecordType = $RecordType
            RecordData = $RecordData
        }
    }
    catch {
        Write-Log "Failed to create DNS record $RecordName.$ZoneName`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Remove-DNSRecordAdvanced {
    param(
        [string]$ZoneName,
        [string]$RecordName,
        [string]$RecordType,
        [string]$DNSServer
    )

    Write-Log "Deleting DNS record: $RecordName.$ZoneName ($RecordType)" -Level 'INFO'

    try {
        $record = Get-DnsServerResourceRecord -ZoneName $ZoneName -Name $RecordName -ComputerName $DNSServer -ErrorAction Stop

        Remove-DnsServerResourceRecord -ZoneName $ZoneName -Name $RecordName -ComputerName $DNSServer -Force
        Write-Log "DNS record $RecordName.$ZoneName deleted successfully" -Level 'INFO'

        return @{
            Success = $true
            RecordName = "$RecordName.$ZoneName"
        }
    }
    catch {
        Write-Log "Failed to delete DNS record $RecordName.$ZoneName`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Get-DNSQuery {
    param(
        [string]$Name,
        [string]$Type = 'A',
        [string]$DNSServer = '8.8.8.8'
    )

    Write-Log "Querying DNS: $Name ($Type)" -Level 'INFO'

    try {
        $result = Resolve-DnsName -Name $Name -Type $Type -Server $DNSServer -ErrorAction Stop

        $records = $result | Where-Object { $_.Type -eq $Type } | ForEach-Object {
            [PSCustomObject]@{
                Name = $_.Name
                Type = $_.Type
                TTL = $_.TTL
                Data = $_.IPAddress ?? $_.NameHost ?? $_.StringsJoined
            }
        }

        return @{
            Success = $true
            Records = $records
        }
    }
    catch {
        Write-Log "DNS query failed for $Name`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Test-DNSHealth {
    param(
        [string]$Domain,
        [string]$DNSServer
    )

    Write-Log "Testing DNS health for: $Domain" -Level 'INFO'

    $tests = @()

    $tests += @{
        Test = "Resolve A Record"
        Success = (Resolve-DnsName -Name $Domain -Type A -Server $DNSServer -ErrorAction SilentlyContinue) -ne $null
    }

    $tests += @{
        Test = "Resolve NS Records"
        Success = (Resolve-DnsName -Name $Domain -Type NS -Server $DNSServer -ErrorAction SilentlyContinue) -ne $null
    }

    $tests += @{
        Test = "Resolve MX Records"
        Success = (Resolve-DnsName -Name $Domain -Type MX -Server $DNSServer -ErrorAction SilentlyContinue) -ne $null
    }

    $tests += @{
        Test = "DNS Server Response Time"
        Success = (Measure-Command { Resolve-DnsName -Name $Domain -Type A -Server $DNSServer }).TotalMilliseconds -lt 1000
    }

    $passedTests = ($tests | Where-Object { $_.Success }).Count
    $totalTests = $tests.Count

    Write-Log "DNS health test completed: $passedTests/$totalTests passed" -Level 'INFO'

    return @{
        Success = $true
        Tests = $tests
        Passed = $passedTests
        Total = $totalTests
    }
}

function Get-DNSZoneList {
    param([string]$DNSServer)

    Write-Log "Listing DNS zones on: $DNSServer" -Level 'INFO'

    try {
        $zones = Get-DnsServerZone -ComputerName $DNSServer

        $zoneList = $zones | ForEach-Object {
            [PSCustomObject]@{
                ZoneName = $_.ZoneName
                ZoneType = $_.ZoneType
                IsReverseLookupZone = $_.IsReverseLookupZone
                IsDsIntegrated = $_.IsDsIntegrated
                IsAutoCreated = $_.IsAutoCreated
            }
        }

        return @{
            Success = $true
            Zones = $zoneList
        }
    }
    catch {
        Write-Log "Failed to list DNS zones`: $($_.Exception.Message)" -Level 'ERROR'
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

switch ($Action) {
    'CreateZone' {
        if (-not $ZoneName) {
            Write-Log "ZoneName is required for CreateZone action" -Level 'ERROR'
            exit 1
        }
        $result = New-DNSZoneAdvanced -ZoneName $ZoneName -DNSServer $DNSServer
    }
    'CreateRecord' {
        if (-not $ZoneName -or -not $RecordName -or -not $RecordType -or -not $RecordData) {
            Write-Log "ZoneName, RecordName, RecordType, and RecordData are required for CreateRecord action" -Level 'ERROR'
            exit 1
        }
        $result = New-DNSRecordAdvanced -ZoneName $ZoneName -RecordName $RecordName -RecordType $RecordType -RecordData $RecordData -Priority $Priority -DNSServer $DNSServer
    }
    'DeleteRecord' {
        if (-not $ZoneName -or -not $RecordName -or -not $RecordType) {
            Write-Log "ZoneName, RecordName, and RecordType are required for DeleteRecord action" -Level 'ERROR'
            exit 1
        }
        $result = Remove-DNSRecordAdvanced -ZoneName $ZoneName -RecordName $RecordName -RecordType $RecordType -DNSServer $DNSServer
    }
    'QueryDNS' {
        if (-not $ZoneName) {
            Write-Log "ZoneName is required for QueryDNS action" -Level 'ERROR'
            exit 1
        }
        $result = Get-DNSQuery -Name $ZoneName -Type $RecordType
    }
    'TestDNS' {
        if (-not $ZoneName) {
            Write-Log "ZoneName is required for TestDNS action" -Level 'ERROR'
            exit 1
        }
        $result = Test-DNSHealth -Domain $ZoneName -DNSServer $DNSServer
    }
    'ListZones' {
        $result = Get-DNSZoneList -DNSServer $DNSServer
    }
}

if ($result.Success) {
    Write-Log "Operation completed successfully" -Level 'INFO'
    if ($result.Records) {
        $result.Records | Format-Table -AutoSize
    }
    elseif ($result.Zones) {
        $result.Zones | Format-Table -AutoSize
    }
    elseif ($result.Tests) {
        $result.Tests | Format-Table -AutoSize
    }
}
else {
    Write-Log "Operation failed: $($result.Error)" -Level 'ERROR'
    exit 1
}
