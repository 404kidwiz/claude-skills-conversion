<#
.SYNOPSIS
    Designs Terminal User Interface (TUI) applications in PowerShell
.DESCRIPTION
    Creates console-based UI with menus, forms, tables, and interactive controls
.PARAMETER Title
    Application title
.PARAMETER MenuItems
    Array of menu item definitions
.PARAMETER TableData
    Data to display in table format
.EXAMPLE
    .\design_tui.ps1 -Title "My App" -MenuItems @(@{Label="Option 1";Action={}})
#>

#Requires -Version 5.1

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$Title = "TUI Application",
    
    [Parameter(Mandatory=$false)]
    [hashtable[]]$MenuItems,
    
    [Parameter(Mandatory=$false)]
    [object[]]$TableData,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$FormFields,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('Menu', 'Table', 'Form', 'Progress', 'Wizard')]
    [string]$Mode = 'Menu',
    
    [Parameter(Mandatory=$false)]
    [switch]$ClearScreen,
    
    [Parameter(Mandatory=$false)]
    [string]$ForegroundColor = 'White',
    
    [Parameter(Mandatory=$false)]
    [string]$BackgroundColor = 'Black'
)

function Initialize-TuiColors {
    param(
        [string]$Fore,
        [string]$Back
    )
    
    $host.UI.RawUI.ForegroundColor = $Fore
    $host.UI.RawUI.BackgroundColor = $Back
    Clear-Host
}

function Write-TuiHeader {
    param(
        [string]$Title,
        [int]$Width = 80
    )
    
    $border = "=" * $Width
    $padding = " " * [Math]::Floor(($Width - $Title.Length - 2) / 2)
    $titleLine = "$padding $Title $padding"
    
    Write-Host $border -ForegroundColor Cyan
    Write-Host $titleLine -ForegroundColor White
    Write-Host $border -ForegroundColor Cyan
    Write-Host ""
}

function Write-TuiMenu {
    param(
        [hashtable[]]$Items
    )
    
    Write-Host "Main Menu" -ForegroundColor Yellow
    Write-Host "-" * 20 -ForegroundColor Yellow
    Write-Host ""
    
    for ($i = 0; $i -lt $Items.Count; $i++) {
        $label = $Items[$i].Label
        $shortcut = $Items[$i].Shortcut
        
        if ($shortcut) {
            Write-Host "  [$($i + 1)]" -NoNewline -ForegroundColor Cyan
            Write-Host " $label " -NoNewline
            Write-Host "($shortcut)" -ForegroundColor DarkGray
        }
        else {
            Write-Host "  [$($i + 1)] $label" -ForegroundColor White
        }
    }
    
    Write-Host ""
    Write-Host "  [Q] Quit" -ForegroundColor Red
    Write-Host ""
}

function Show-TuiMenu {
    param(
        [hashtable[]]$Items,
        [string]$Prompt = "Select an option: "
    )
    
    while ($true) {
        if ($ClearScreen) {
            Clear-Host
        }
        
        Write-TuiHeader -Title $Title
        Write-TuiMenu -Items $Items
        Write-Host $Prompt -NoNewline -ForegroundColor Green
        
        $input = Read-Host
        
        if ($input -eq 'q' -or $input -eq 'Q') {
            return 'Quit'
        }
        
        $selectedIndex = 0
        if ([int]::TryParse($input, [ref]$selectedIndex)) {
            $selectedIndex--
            
            if ($selectedIndex -ge 0 -and $selectedIndex -lt $Items.Count) {
                $selectedItem = $Items[$selectedIndex]
                
                if ($selectedItem.Action) {
                    & $selectedItem.Action
                }
                
                if ($selectedItem.SubMenu) {
                    Show-TuiMenu -Items $selectedItem.SubMenu -Prompt $Prompt
                }
                
                if (-not $selectedItem.KeepOpen) {
                    return $selectedItem
                }
            }
            else {
                Write-Host "Invalid selection. Please try again." -ForegroundColor Red
                Start-Sleep -Seconds 1
            }
        }
        else {
            # Check for shortcuts
            foreach ($item in $Items) {
                if ($item.Shortcut -and $input -eq $item.Shortcut) {
                    if ($item.Action) {
                        & $item.Action
                    }
                    if (-not $item.KeepOpen) {
                        return $item
                    }
                    break
                }
            }
            
            Write-Host "Invalid selection. Please try again." -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}

function Write-TuiTable {
    param(
        [object[]]$Data,
        [string[]]$Properties
    )
    
    if (-not $Data) {
        Write-Host "No data to display" -ForegroundColor Yellow
        return
    }
    
    if (-not $Properties) {
        $Properties = $Data[0].PSObject.Properties.Name
    }
    
    # Calculate column widths
    $colWidths = @{}
    foreach ($prop in $Properties) {
        $maxWidth = $prop.Length
        foreach ($item in $Data) {
            $value = $item.$prop ?? ''
            $maxWidth = [Math]::Max($maxWidth, $value.ToString().Length)
        }
        $colWidths[$prop] = $maxWidth + 2
    }
    
    # Write header
    $header = ""
    foreach ($prop in $Properties) {
        $header += ("{0,-$($colWidths[$prop])}" -f $prop)
    }
    Write-Host $header -ForegroundColor Cyan
    Write-Host ("-" * $header.Length) -ForegroundColor Cyan
    
    # Write data rows
    foreach ($item in $Data) {
        $row = ""
        foreach ($prop in $Properties) {
            $value = $item.$prop ?? ''
            $row += ("{0,-$($colWidths[$prop])}" -f $value)
        }
        Write-Host $row -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "Total: $($Data.Count) items" -ForegroundColor Gray
}

function Show-TuiForm {
    param(
        [hashtable]$Fields
    )
    
    $results = @{}
    
    Write-Host "Form Entry" -ForegroundColor Yellow
    Write-Host "-" * 20 -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($field in $Fields.GetEnumerator()) {
        $fieldName = $field.Key
        $fieldInfo = $field.Value
        
        $label = $fieldInfo.Label ?? $fieldName
        $default = $fieldInfo.Default
        $required = $fieldInfo.Required
        
        $prompt = "$label"
        if ($required) {
            $prompt += "*"
        }
        $prompt += ": "
        
        Write-Host $prompt -NoNewline -ForegroundColor Green
        
        if ($default) {
            Write-Host "[$default] " -NoNewline -ForegroundColor DarkGray
        }
        
        $input = Read-Host
        
        if ([string]::IsNullOrEmpty($input)) {
            if ($required) {
                Write-Host "This field is required." -ForegroundColor Red
                # Try again
                # Simplified: continue for now
            }
            elseif ($default) {
                $results[$fieldName] = $default
            }
            else {
                $results[$fieldName] = $null
            }
        }
        else {
            $results[$fieldName] = $input
        }
    }
    
    Write-Host ""
    Write-Host "Form completed. Press any key to continue..." -ForegroundColor Gray
    $null = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    return $results
}

function Show-TuiProgress {
    param(
        [int]$PercentComplete,
        [string]$Activity,
        [string]$Status = "Processing..."
    )
    
    $width = 50
    $filled = [Math]::Floor($width * $PercentComplete / 100)
    $empty = $width - $filled
    
    $bar = ("█" * $filled) + ("░" * $empty)
    
    Write-Host "`r$Activity" -ForegroundColor Yellow -NoNewline
    Write-Host " " -NoNewline
    Write-Host "[$bar] $PercentComplete%" -ForegroundColor Green -NoNewline
    Write-Host " $Status" -ForegroundColor Gray
}

function Show-TuiWizard {
    param(
        [hashtable[]]$Steps
    )
    
    $currentStep = 0
    $wizardData = @{}
    
    while ($currentStep -lt $Steps.Count) {
        if ($ClearScreen) {
            Clear-Host
        }
        
        Write-TuiHeader -Title "$Title - Wizard"
        
        $step = $Steps[$currentStep]
        
        Write-Host "Step $($currentStep + 1) of $($Steps.Count)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host $step.Title -ForegroundColor White
        Write-Host $step.Description -ForegroundColor DarkGray
        Write-Host ""
        
        if ($step.Type -eq 'Form') {
            $formData = Show-TuiForm -Fields $step.Fields
            $wizardData[$step.Name] = $formData
        }
        elseif ($step.Type -eq 'Info') {
            Write-Host $step.Content -ForegroundColor White
            Write-Host ""
            Write-Host "Press any key to continue..." -ForegroundColor Gray
            $null = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        
        Write-Host ""
        Write-Host "[N] Next  [P] Previous  [Q] Quit" -ForegroundColor Green
        $choice = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").Character
        
        switch ($choice) {
            'n' {
                if ($currentStep -lt $Steps.Count - 1) {
                    $currentStep++
                }
            }
            'p' {
                if ($currentStep -gt 0) {
                    $currentStep--
                }
            }
            'q' {
                return $null
            }
        }
    }
    
    return $wizardData
}

try {
    Write-Verbose "Starting TUI design: $Title"
    
    Initialize-TuiColors -Fore $ForegroundColor -Back $BackgroundColor
    
    switch ($Mode) {
        'Menu' {
            $result = Show-TuiMenu -Items $MenuItems
            Write-Host "Selected: $($result.Label)" -ForegroundColor Green
        }
        
        'Table' {
            Write-TuiHeader -Title $Title
            Write-TuiTable -Data $TableData
        }
        
        'Form' {
            Write-TuiHeader -Title $Title
            $result = Show-TuiForm -Fields $FormFields
            Write-Host "`nForm data:" -ForegroundColor Yellow
            $result.GetEnumerator() | ForEach-Object {
                Write-Host "  $($_.Key): $($_.Value)" -ForegroundColor White
            }
        }
        
        'Progress' {
            Write-TuiHeader -Title $Title
            for ($i = 0; $i -le 100; $i += 10) {
                Show-TuiProgress -PercentComplete $i -Activity "Processing" -Status "Step $i/100"
                Start-Sleep -Milliseconds 200
            }
            Write-Host "`nComplete!" -ForegroundColor Green
        }
        
        'Wizard' {
            $result = Show-TuiWizard -Steps $MenuItems
            if ($result) {
                Write-Host "`nWizard completed!" -ForegroundColor Green
            }
        }
    }
    
    Write-Verbose "TUI design completed"
}
catch {
    Write-Error "TUI design failed: $_"
    exit 1
}
finally {
    Write-Verbose "Design TUI script completed"
}

Export-ModuleMember -Function Write-TuiMenu, Show-TuiMenu, Write-TuiTable, Show-TuiForm, Show-TuiProgress
