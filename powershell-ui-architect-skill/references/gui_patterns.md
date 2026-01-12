# PowerShell GUI Patterns

## Overview

This guide covers GUI development patterns for PowerShell, including WinForms, WPF, and Terminal User Interfaces (TUI).

## WinForms Patterns

### Basic Form Structure

```powershell
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Show-WinFormsDialog {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "PowerShell WinForms"
    $form.Width = 400
    $form.Height = 300
    $form.StartPosition = "CenterScreen"
    
    # Add controls
    $button = New-Object System.Windows.Forms.Button
    $button.Text = "Click Me"
    $button.Location = New-Object System.Drawing.Point(150, 200)
    $button.Size = New-Object System.Drawing.Size(100, 30)
    
    $button.Add_Click({
        [System.Windows.Forms.MessageBox]::Show("Button clicked!")
    })
    
    $form.Controls.Add($button)
    
    $form.ShowDialog()
}
```

### Data Binding

```powershell
function Show-BoundData {
    # Create data source
    $data = @(
        [PSCustomObject]@{ Name = "Item 1"; Value = 100 },
        [PSCustomObject]@{ Name = "Item 2"; Value = 200 },
        [PSCustomObject]@{ Name = "Item 3"; Value = 300 }
    )
    
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Data Binding Example"
    
    # Create DataGridView
    $dataGridView = New-Object System.Windows.Forms.DataGridView
    $dataGridView.Location = New-Object System.Drawing.Point(20, 20)
    $dataGridView.Size = New-Object System.Drawing.Size(340, 200)
    $dataGridView.AutoGenerateColumns = $true
    $dataGridView.DataSource = $data
    
    $form.Controls.Add($dataGridView)
    $form.ShowDialog()
}
```

### Event Handling

```powershell
function Show-EventHandling {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Event Handling"
    
    $textBox = New-Object System.Windows.Forms.TextBox
    $textBox.Location = New-Object System.Drawing.Point(20, 20)
    $textBox.Size = New-Object System.Drawing.Size(340, 20)
    
    # Text changed event
    $textBox.Add_TextChanged({
        param($sender, $e)
        Write-Host "Text changed: $($sender.Text)"
    })
    
    # Key press event
    $textBox.Add_KeyPress({
        param($sender, $e)
        if ($e.KeyChar -eq [char]13) {
            [System.Windows.Forms.MessageBox]::Show("Enter pressed")
        }
    })
    
    $form.Controls.Add($textBox)
    $form.ShowDialog()
}
```

## WPF Patterns

### XAML-Based WPF

```powershell
$xaml = @"
<Window x:Class="MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="PowerShell WPF" Height="300" Width="400">
    <Grid>
        <Button Name="btnClick" Content="Click Me" 
                HorizontalAlignment="Center" 
                VerticalAlignment="Center"
                Width="100" Height="30"/>
    </Grid>
</Window>
"@

Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore

$reader = [System.Xml.XmlReader]::Create([System.IO.StringReader]::new($xaml))
$window = [System.Windows.Markup.XamlReader]::Load($reader)

# Add event handler
$btnClick = $window.FindName("btnClick")
$btnClick.Add_Click({
    [System.Windows.MessageBox]::Show("Button clicked!")
})

$window.ShowDialog()
```

### MVVM Pattern

```powershell
# ViewModel
class MyViewModel : System.ComponentModel.INotifyPropertyChanged {
    [string]$_name
    
    [string]$Name {
        get { return $this._name }
        set {
            if ($this._name -ne $value) {
                $this._name = $value
                $this.OnPropertyChanged("Name")
            }
        }
    }
    
    [System.Collections.ObjectModel.ObservableCollection[string]]$Items
    
    MyViewModel() {
        $this.Items = [System.Collections.ObjectModel.ObservableCollection[string]]::new()
        $this.Items.Add("Item 1")
        $this.Items.Add("Item 2")
    }
    
    [void]$OnPropertyChanged($propertyName) {
        if ($this.PropertyChanged -ne $null) {
            $this.PropertyChanged.Invoke($this, [System.ComponentModel.PropertyChangedEventArgs]::new($propertyName))
        }
    }
    
    event PropertyChanged($sender, $e)
    hidden [System.ComponentModel.PropertyChangedEventHandler]$PropertyChanged
}
```

### Data Binding in WPF

```powershell
$xaml = @"
<Window x:Class="MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <StackPanel>
        <TextBlock Text="Enter Name:"/>
        <TextBox Name="txtName" Height="25"/>
        <TextBlock Name="lblName" Height="25" Text="{Binding Name}"/>
    </StackPanel>
</Window>
"@

$reader = [System.Xml.XmlReader]::Create([System.IO.StringReader]::new($xaml))
$window = [System.Windows.Markup.XamlReader]::Load($reader)

# Create ViewModel
$viewModel = [MyViewModel]::new()
$window.DataContext = $viewModel

# Bind TextBox
$txtName = $window.FindName("txtName")
$txtName.SetBinding([System.Windows.Controls.TextBox]::TextProperty, "Name")

$window.ShowDialog()
```

## TUI (Terminal User Interface) Patterns

### Basic TUI Menu

```powershell
function Show-TuiMenu {
    $menuItems = @(
        @{ Label = "Option 1"; Action = { Write-Host "Selected Option 1" } },
        @{ Label = "Option 2"; Action = { Write-Host "Selected Option 2" } },
        @{ Label = "Option 3"; Action = { Write-Host "Selected Option 3" } }
    )
    
    while ($true) {
        Clear-Host
        Write-Host "=== Main Menu ===" -ForegroundColor Cyan
        Write-Host ""
        
        for ($i = 0; $i -lt $menuItems.Count; $i++) {
            Write-Host "  [$($i + 1)] $($menuItems[$i].Label)" -ForegroundColor White
        }
        
        Write-Host "  [Q] Quit" -ForegroundColor Red
        Write-Host ""
        
        $selection = Read-Host "Select option"
        
        if ($selection -eq 'q' -or $selection -eq 'Q') {
            break
        }
        
        $selectedIndex = 0
        if ([int]::TryParse($selection, [ref]$selectedIndex)) {
            $selectedIndex--
            
            if ($selectedIndex -ge 0 -and $selectedIndex -lt $menuItems.Count) {
                Clear-Host
                & $menuItems[$selectedIndex].Action
                Read-Host "Press Enter to continue"
            }
        }
    }
}
```

### TUI Table Display

```powershell
function Show-TuiTable {
    $data = @(
        @{ Name = "Item 1"; Status = "Active"; Value = 100 },
        @{ Name = "Item 2"; Status = "Inactive"; Value = 200 },
        @{ Name = "Item 3"; Status = "Active"; Value = 300 }
    )
    
    Clear-Host
    Write-Host "=== Data Table ===" -ForegroundColor Cyan
    Write-Host ""
    
    $data | Format-Table -AutoSize
    
    Write-Host ""
    Read-Host "Press Enter to continue"
}
```

### TUI Progress Bar

```powershell
function Show-TuiProgress {
    $totalItems = 100
    
    for ($i = 0; $i -le $totalItems; $i++) {
        $progress = ($i / $totalItems) * 100
        $filled = [Math]::Floor(50 * $progress / 100)
        $empty = 50 - $filled
        
        $bar = "█" * $filled + "░" * $empty
        
        Write-Host "`r[$bar] $progress%" -NoNewline -ForegroundColor Green
        
        Start-Sleep -Milliseconds 50
    }
    
    Write-Host "`nComplete!" -ForegroundColor Green
}
```

## Framework Selection

### When to Use WinForms

**Pros:**
- Simple to implement
- Lightweight
- Good for simple dialogs

**Cons:**
- Limited styling options
- Not modern looking
- Limited data binding

**Use Cases:**
- Simple input forms
- Utility dialogs
- Quick prototypes

### When to Use WPF

**Pros:**
- Modern appearance
- Rich styling options
- Advanced data binding
- MVVM pattern support

**Cons:**
- Steeper learning curve
- More complex to implement
- Heavier than WinForms

**Use Cases:**
- Complex applications
- Data-heavy interfaces
- Professional-looking GUIs
- MVVM pattern required

### When to Use TUI

**Pros:**
- Cross-platform compatible
- Lightweight
- No GUI dependencies
- Works over SSH

**Cons:**
- Limited interaction options
- No graphics
- Terminal-based only

**Use Cases:**
- Server administration
- SSH/remote sessions
- Command-line tools
- Cross-platform compatibility needed

## Common Patterns

### Modal Dialogs

```powershell
function Show-ModalDialog {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Modal Dialog"
    $form.ShowDialog() | Out-Null
}
```

### Asynchronous Operations

```powershell
function Show-Progress {
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Processing..."
    
    $progressBar = New-Object System.Windows.Forms.ProgressBar
    $progressBar.Location = New-Object System.Drawing.Point(20, 50)
    $progressBar.Size = New-Object System.Drawing.Size(340, 20)
    
    $form.Controls.Add($progressBar)
    
    # Start operation in background
    $job = Start-Job -ScriptBlock {
        Start-Sleep -Seconds 5
    }
    
    # Update progress
    while ($job.State -eq 'Running') {
        $progressBar.Value += 10
        $form.Refresh()
        Start-Sleep -Milliseconds 500
    }
    
    Remove-Job $job
    $form.ShowDialog()
}
```

## Best Practices

1. **Framework Selection**: Choose the right framework for your needs
2. **Event Handling**: Implement proper event handlers
3. **Error Handling**: Add try-catch blocks for user interactions
4. **Responsiveness**: Keep UI responsive during operations
5. **Accessibility**: Consider accessibility features
6. **Cross-Platform**: Use TUI for cross-platform needs
7. **Testing**: Test GUI applications thoroughly
8. **Performance**: Optimize for performance with large datasets

## Resources

- [WinForms Documentation](https://docs.microsoft.com/en-us/dotnet/desktop/winforms/)
- [WPF Documentation](https://docs.microsoft.com/en-us/dotnet/desktop/wpf/)
- [PowerShell GUI Examples](https://github.com/pscookiemonster/GUI-Examples)
