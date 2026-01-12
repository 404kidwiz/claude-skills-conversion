<#
.SYNOPSIS
    Consumes REST APIs with PowerShell 7+ modern features
.DESCRIPTION
    Advanced REST API client with authentication, retry logic, and error handling
.PARAMETER Uri
    REST API endpoint URI
.PARAMETER Method
    HTTP method (GET, POST, PUT, DELETE, PATCH)
.PARAMETER Body
    Request body data
.PARAMETER AuthType
    Authentication type (None, Bearer, Basic, OAuth)
.PARAMETER Credential
    PSCredential for Basic authentication
.PARAMETER Token
    Bearer token or OAuth token
.PARAMETER Headers
    Additional HTTP headers
.EXAMPLE
    .\rest_api_consumer.ps1 -Uri "https://api.github.com/user" -Method GET -Token $token
#>

#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [uri]$Uri,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS')]
    [string]$Method = 'GET',
    
    [Parameter(Mandatory=$false)]
    [object]$Body,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('None', 'Bearer', 'Basic', 'OAuth', 'ApiKey')]
    [string]$AuthType = 'None',
    
    [Parameter(Mandatory=$false)]
    [pscredential]$Credential,
    
    [Parameter(Mandatory=$false)]
    [string]$Token,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$Headers = @{},
    
    [Parameter(Mandatory=$false)]
    [string]$ApiKey,
    
    [Parameter(Mandatory=$false)]
    [string]$ApiKeyName = 'X-API-Key',
    
    [Parameter(Mandatory=$false)]
    [int]$TimeoutSeconds = 30,
    
    [Parameter(Mandatory=$false)]
    [int]$MaxRetries = 3,
    
    [Parameter(Mandatory=$false)]
    [int]$RetryDelaySeconds = 2,
    
    [Parameter(Mandatory=$false)]
    [switch]$FollowRedirects,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipCertificateCheck
)

function New-ApiHeaders {
    param(
        [hashtable]$CustomHeaders,
        [string]$AuthType,
        [string]$Token,
        [pscredential]$Credential,
        [string]$ApiKey,
        [string]$ApiKeyName
    )
    
    $headers = [System.Collections.Generic.Dictionary[string, string]]::new()
    
    if ($CustomHeaders) {
        foreach ($key in $CustomHeaders.Keys) {
            $headers[$key] = $CustomHeaders[$key]
        }
    }
    
    switch ($AuthType) {
        'Bearer' {
            if ($Token) {
                $headers['Authorization'] = "Bearer $Token"
            }
        }
        
        'Basic' {
            if ($Credential) {
                $encodedCreds = [System.Convert]::ToBase64String(
                    [System.Text.Encoding]::ASCII.GetBytes("$($Credential.UserName):$($Credential.GetNetworkCredential().Password)")
                )
                $headers['Authorization'] = "Basic $encodedCreds"
            }
        }
        
        'ApiKey' {
            if ($ApiKey) {
                $headers[$ApiKeyName] = $ApiKey
            }
        }
    }
    
    $headers['Accept'] = 'application/json'
    return $headers
}

function Invoke-ApiRequestWithRetry {
    param(
        [uri]$Endpoint,
        [string]$HttpMethod,
        [object]$RequestBody,
        [hashtable]$RequestHeaders,
        [int]$Timeout,
        [int]$Retries,
        [int]$RetryDelay,
        [bool]$FollowRedirect,
        [bool]$SkipCertCheck
    )
    
    $attempt = 0
    $lastError = $null
    
    while ($attempt -lt $Retries) {
        $attempt++
        Write-Verbose "Attempt $attempt of $Retries"
        
        try {
            $params = @{
                Method = $HttpMethod
                Uri = $Endpoint
                Headers = $RequestHeaders
                TimeoutSec = $Timeout
                ErrorAction = 'Stop'
            }
            
            if ($RequestBody) {
                $params.Body = $RequestBody | ConvertTo-Json -Depth 10 -Compress
                $params.ContentType = 'application/json'
            }
            
            if (-not $FollowRedirect) {
                $params.MaximumRedirection = 0
            }
            
            if ($SkipCertCheck) {
                $params.SkipCertificateCheck = $true
            }
            
            $response = Invoke-RestMethod @params
            Write-Verbose "Request successful"
            
            return @{
                Success = $true
                Data = $response
                Attempt = $attempt
            }
        }
        catch [System.Net.WebException] {
            $lastError = $_
            $statusCode = $_.Exception.Response.StatusCode.value__
            
            Write-Verbose "Request failed: $statusCode"
            
            if ($statusCode -in @(401, 403, 404, 422)) {
                Write-Verbose "Non-retryable status code: $statusCode"
                break
            }
            
            if ($attempt -lt $Retries) {
                Write-Verbose "Retrying in $RetryDelay second(s)..."
                Start-Sleep -Seconds $RetryDelay
            }
        }
        catch {
            $lastError = $_
            Write-Verbose "Request failed: $_"
            
            if ($attempt -lt $Retries) {
                Write-Verbose "Retrying in $RetryDelay second(s)..."
                Start-Sleep -Seconds $RetryDelay
            }
        }
    }
    
    return @{
        Success = $false
        Error = $lastError
        Attempt = $attempt
    }
}

function Format-ApiResponse {
    param(
        [object]$Response,
        [string]$Format = 'Table'
    )
    
    if (-not $Response) {
        return
    }
    
    switch ($Format) {
        'Json' {
            return $Response | ConvertTo-Json -Depth 10
        }
        
        'Table' {
            if ($Response -is [array]) {
                $Response | Format-Table -AutoSize -Wrap
            }
            elseif ($Response -is [hashtable]) {
                $Response.GetEnumerator() | Format-Table -AutoSize
            }
            else {
                $Response | Format-List
            }
        }
        
        default {
            $Response
        }
    }
}

function Get-ResponseHeaders {
    param(
        [object]$Response
    )
    
    Write-Host "`nResponse Information:"
    Write-Host "-------------------"
    
    if ($Response.PSObject.Properties.Name -contains 'StatusCode') {
        Write-Host "Status Code: $($Response.StatusCode)"
    }
    
    if ($Response.PSObject.Properties.Name -contains 'Headers') {
        Write-Host "Response Headers:"
        $Response.Headers.GetEnumerator() | ForEach-Object {
            Write-Host "  $($_.Key): $($_.Value)"
        }
    }
}

try {
    Write-Verbose "Starting REST API request: $Method $Uri"
    
    $requestHeaders = New-ApiHeaders -CustomHeaders $Headers -AuthType $AuthType -Token $Token -Credential $Credential -ApiKey $ApiKey -ApiKeyName $ApiKeyName
    
    Write-Verbose "Request Headers:"
    $requestHeaders.GetEnumerator() | ForEach-Object {
        Write-Verbose "  $($_.Key): $(if ($_.Key -eq 'Authorization') { '***' } else { $_.Value })"
    }
    
    $result = Invoke-ApiRequestWithRetry -Endpoint $Uri -HttpMethod $Method -RequestBody $Body -RequestHeaders $requestHeaders -Timeout $TimeoutSeconds -Retries $MaxRetries -RetryDelay $RetryDelaySeconds -FollowRedirect $FollowRedirects -SkipCertCheck $SkipCertificateCheck
    
    if ($result.Success) {
        Write-Host "`nRequest Successful (Attempt $($result.Attempt))" -ForegroundColor Green
        Format-ApiResponse -Response $result.Data
        Write-Verbose "API request completed successfully"
        return $result.Data
    }
    else {
        Write-Host "`nRequest Failed" -ForegroundColor Red
        Write-Host "Attempt: $($result.Attempt) of $MaxRetries"
        Write-Host "Error: $($result.Error.Exception.Message)"
        
        if ($result.Error.Exception.Response) {
            $statusCode = $result.Error.Exception.Response.StatusCode.value__
            Write-Host "Status Code: $statusCode"
            
            try {
                $responseStream = $result.Error.Exception.Response.GetResponseStream()
                $reader = [System.IO.StreamReader]::new($responseStream)
                $responseBody = $reader.ReadToEnd()
                $reader.Close()
                
                Write-Host "Response Body:"
                Write-Host $responseBody
            }
            catch {
                Write-Verbose "Could not read response body: $_"
            }
        }
        
        Write-Verbose "API request failed after $($result.Attempt) attempts"
        exit 1
    }
}
catch {
    Write-Error "API request execution failed: $_"
    exit 1
}
finally {
    Write-Verbose "REST API consumer script completed"
}

Export-ModuleMember -Function New-ApiHeaders, Invoke-ApiRequestWithRetry
