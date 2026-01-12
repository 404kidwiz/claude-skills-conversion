<#
.SYNOPSIS
    Creates WinForms-based GUI applications in PowerShell
.DESCRIPTION
    Generates WinForms GUI templates with controls, event handlers, and data binding
.PARAMETER FormTitle
    Title of the form
.PARAMETER Width
    Form width in pixels
.PARAMETER Height
    Form height in pixels
.PARAMETER Controls
    Array of control definitions
.EXAMPLE
    .\create_winforms.ps1 -FormTitle "My App" -Width 400 -Height 300
#>

#Requires -Version 5.1
#Requires -Assembly System.Windows.Forms, System.Drawing

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateNotNullOrEmpty()]
    [string]$FormTitle,
    
    [Parameter(Mandatory=$false)]
    [int]$Width = 400,
    
    [Parameter(Mandatory=$false)]
    [int]$Height = 300,
    
    [Parameter(Mandatory=$false)]
    [hashtable[]]$Controls = @(),
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('FixedSingle', 'Fixed3D', 'FixedDialog', 'Sizable', 'FixedToolWindow', 'SizableToolWindow')]
    [string]$FormBorderStyle = 'Sizable',
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('Normal', 'Minimized', 'Maximized', 'CenterScreen', 'WindowsDefaultLocation', 'WindowsDefaultBounds', 'CenterParent')]
    [string]$StartPosition = 'CenterScreen',
    
    [Parameter(Mandatory=$false)]
    [switch]$Show,
    
    [Parameter(Mandatory=$false)]
    [switch]$GenerateScript,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath
)

function New-WinFormsForm {
    param(
        [string]$Title,
        [int]$FormWidth,
        [int]$FormHeight,
        [string]$BorderStyle,
        [string]$StartPos
    )
    
    Write-Verbose "Creating WinForms form"
    
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    
    $form = New-Object System.Windows.Forms.Form
    $form.Text = $Title
    $form.Width = $FormWidth
    $form.Height = $FormHeight
    $form.FormBorderStyle = $BorderStyle
    $form.StartPosition = $StartPos
    
    return $form
}

function New-WinFormsButton {
    param(
        [string]$Text,
        [int]$X,
        [int]$Y,
        [int]$Width = 100,
        [int]$Height = 30,
        [scriptblock]$OnClick
    )
    
    Write-Verbose "Creating button: $Text"
    
    $button = New-Object System.Windows.Forms.Button
    $button.Text = $Text
    $button.Location = New-Object System.Drawing.Point($X, $Y)
    $button.Size = New-Object System.Drawing.Size($Width, $Height)
    
    if ($OnClick) {
        $button.Add_Click($OnClick)
    }
    
    return $button
}

function New-WinFormsTextBox {
    param(
        [string]$Text = '',
        [int]$X,
        [int]$Y,
        [int]$Width = 200,
        [int]$Height = 20,
        [switch]$Multiline,
        [switch]$ReadOnly
    )
    
    Write-Verbose "Creating textbox"
    
    $textBox = New-Object System.Windows.Forms.TextBox
    $textBox.Text = $Text
    $textBox.Location = New-Object System.Drawing.Point($X, $Y)
    $textBox.Size = New-Object System.Drawing.Size($Width, $Height)
    $textBox.Multiline = $Multiline
    $textBox.ReadOnly = $ReadOnly
    
    return $textBox
}

function New-WinFormsLabel {
    param(
        [string]$Text,
        [int]$X,
        [int]$Y,
        [int]$Width = 100,
        [int]$Height = 20
    )
    
    Write-Verbose "Creating label: $Text"
    
    $label = New-Object System.Windows.Forms.Label
    $label.Text = $Text
    $label.Location = New-Object System.Drawing.Point($X, $Y)
    $label.Size = New-Object System.Drawing.Size($Width, $Height)
    
    return $label
}

function New-WinFormsListBox {
    param(
        [int]$X,
        [int]$Y,
        [int]$Width = 200,
        [int]$Height = 100
    )
    
    Write-Verbose "Creating listbox"
    
    $listBox = New-Object System.Windows.Forms.ListBox
    $listBox.Location = New-Object System.Drawing.Point($X, $Y)
    $listBox.Size = New-Object System.Drawing.Size($Width, $Height)
    
    return $listBox
}

function New-WinFormsComboBox {
    param(
        [int]$X,
        [int]$Y,
        [int]$Width = 150,
        [int]$Height = 20,
        [switch]$DropDownStyle
    )
    
    Write-Verbose "Creating combobox"
    
    $comboBox = New-Object System.Windows.Forms.ComboBox
    $comboBox.Location = New-Object System.Drawing.Point($X, $Y)
    $comboBox.Size = New-Object System.Drawing.Size($Width, $Height)
    
    if ($DropDownStyle) {
        $comboBox.DropDownStyle = 'DropDownList'
    }
    
    return $comboBox
}

function Add-ControlToForm {
    param(
        [System.Windows.Forms.Form]$Form,
        [hashtable]$ControlDef
    )
    
    Write-Verbose "Adding control: $($ControlDef.Type)"
    
    $type = $ControlDef.Type
    $x = $ControlDef.X
    $y = $ControlDef.Y
    
    switch ($type) {
        'Button' {
            $control = New-WinFormsButton -Text $ControlDef.Text -X $x -Y $y `
                                          -Width $ControlDef.Width -Height $ControlDef.Height
        }
        
        'TextBox' {
            $control = New-WinFormsTextBox -Text $ControlDef.Text -X $x -Y $y `
                                            -Width $ControlDef.Width -Height $ControlDef.Height `
                                            -Multiline:$ControlDef.Multiline -ReadOnly:$ControlDef.ReadOnly
        }
        
        'Label' {
            $control = New-WinFormsLabel -Text $ControlDef.Text -X $x -Y $y `
                                        -Width $ControlDef.Width -Height $ControlDef.Height
        }
        
        'ListBox' {
            $control = New-WinFormsListBox -X $x -Y $y -Width $ControlDef.Width -Height $ControlDef.Height
        }
        
        'ComboBox' {
            $control = New-WinFormsComboBox -X $x -Y $y -Width $ControlDef.Width -Height $ControlDef.Height
        }
        
        default {
            Write-Warning "Unknown control type: $type"
            return
        }
    }
    
    if ($ControlDef.Name) {
        $control.Name = $ControlDef.Name
        $Form.Controls.Add($control)
        
        # Add to form's tag for easy access
        if (-not $Form.Tag) {
            $Form.Tag = @{}
        }
        $Form.Tag[$ControlDef.Name] = $control
    }
    else {
        $Form.Controls.Add($control)
    }
}

function Show-WinFormsDialog {
    param(
        [System.Windows.Forms.Form]$Form
    )
    
    Write-Verbose "Showing form dialog"
    
    try {
        $result = $Form.ShowDialog()
        Write-Verbose "Form closed with result: $result"
        return $result
    }
    catch {
        Write-Error "Form display failed: $_"
        throw
    }
}

function Export-WinFormsScript {
    param(
        [string]$Title,
        [int]$FormWidth,
        [int]$FormHeight,
        [hashtable[]]$ControlList,
        [string]$OutputFile
    )
    
    Write-Verbose "Exporting WinForms script"
    
    $scriptContent = @"
<#
.SYNOPSIS
    Auto-generated WinForms application
.DESCRIPTION
    Title: $Title
    Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
#>

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

`$form = New-Object System.Windows.Forms.Form
`$form.Text = "$Title"
`$form.Width = $FormWidth
`$form.Height = $FormHeight
`$form.StartPosition = "CenterScreen"

"@
    
    foreach ($control in $ControlList) {
        $type = $control.Type
        $x = $control.X
        $y = $control.Y
        $width = $control.Width
        $height = $control.Height
        
        switch ($type) {
            'Button' {
                $scriptContent += @"

`$$($control.Name) = New-Object System.Windows.Forms.Button
`$$($control.Name).Text = "$($control.Text)"
`$$($control.Name).Location = New-Object System.Drawing.Point($x, $y)
`$$($control.Name).Size = New-Object System.Drawing.Size($width, $height)
`$$($control.Name).Add_Click({
    # Add click handler logic here
    Write-Host "Button clicked"
})
`$form.Controls.Add(`$$($control.Name))

"@
            }
            
            'TextBox' {
                $scriptContent += @"

`$$($control.Name) = New-Object System.Windows.Forms.TextBox
`$$($control.Name).Text = "$($control.Text)"
`$$($control.Name).Location = New-Object System.Drawing.Point($x, $y)
`$$($control.Name).Size = New-Object System.Drawing.Size($width, $height)
$($control.Multiline ? "`$$($control.Name).Multiline = `$true`n" : "")
$($control.ReadOnly ? "`$$($control.Name).ReadOnly = `$true`n" : "")
`$form.Controls.Add(`$$($control.Name))

"@
            }
            
            'Label' {
                $scriptContent += @"

`$$($control.Name) = New-Object System.Windows.Forms.Label
`$$($control.Name).Text = "$($control.Text)"
`$$($control.Name).Location = New-Object System.Drawing.Point($x, $y)
`$$($control.Name).Size = New-Object System.Drawing.Size($width, $height)
`$form.Controls.Add(`$$($control.Name))

"@
            }
        }
    }
    
    $scriptContent += @"

`$form.ShowDialog()

"@
    
    if ($OutputFile) {
        Set-Content -Path $OutputFile -Value $scriptContent -Encoding UTF8
        Write-Host "Script exported to: $OutputFile"
    }
    
    return $scriptContent
}

try {
    Write-Verbose "Starting WinForms creation: $FormTitle"
    
    $form = New-WinFormsForm -Title $FormTitle -FormWidth $Width -FormHeight $Height -BorderStyle $FormBorderStyle -StartPos $StartPosition
    
    foreach ($control in $Controls) {
        Add-ControlToForm -Form $form -ControlDef $control
    }
    
    if ($GenerateScript) {
        $scriptPath = if ($OutputPath) { $OutputPath } else { "$FormTitle.ps1" }
        Export-WinFormsScript -Title $FormTitle -FormWidth $Width -FormHeight $Height -ControlList $Controls -OutputFile $scriptPath
    }
    
    if ($Show) {
        Show-WinFormsDialog -Form $form
    }
    else {
        Write-Host "WinForms form created successfully"
        Write-Host "Title: $FormTitle"
        Write-Host "Size: ${Width}x$Height"
        Write-Host "Controls: $($Controls.Count)"
    }
    
    Write-Verbose "WinForms creation completed"
}
catch {
    Write-Error "WinForms creation failed: $_"
    exit 1
}
finally {
    Write-Verbose "Create WinForms script completed"
}

Export-ModuleMember -Function New-WinFormsForm, New-WinFormsButton, New-WinFormsTextBox, New-WinFormsLabel
