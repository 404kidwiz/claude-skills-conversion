<#
.SYNOPSIS
    Builds WPF-based GUI applications in PowerShell
.DESCRIPTION
    Creates WPF applications with XAML, MVVM patterns, and data binding
.PARAMETER XamlPath
    Path to XAML file for WPF UI definition
.PARAMETER ViewModel
    Hashtable containing ViewModel properties
.PARAMETER Show
    Display the WPF window
.EXAMPLE
    .\build_wpf.ps1 -XamlPath "./MainWindow.xaml" -Show
#>

#Requires -Version 5.1
#Requires -Assembly PresentationFramework, PresentationCore, WindowsBase

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateScript({
        if (-not (Test-Path $_)) {
            throw "XAML file does not exist: $_"
        }
        $true
    })]
    [string]$XamlPath,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$ViewModel,
    
    [Parameter(Mandatory=$false)]
    [switch]$Show,
    
    [Parameter(Mandatory=$false)]
    [switch]$GenerateXaml,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputXamlPath,
    
    [Parameter(Mandatory=$false)]
    [string]$WindowTitle = "WPF Application",
    
    [Parameter(Mandatory=$false)]
    [int]$Width = 400,
    
    [Parameter(Mandatory=$false)]
    [int]$Height = 300
)

function Initialize-WpfAssemblies {
    Write-Verbose "Loading WPF assemblies"
    
    try {
        Add-Type -AssemblyName PresentationFramework
        Add-Type -AssemblyName PresentationCore
        Add-Type -AssemblyName WindowsBase
        Write-Verbose "WPF assemblies loaded successfully"
    }
    catch {
        Write-Error "Failed to load WPF assemblies: $_"
        throw
    }
}

function New-WpfWindow {
    param(
        [string]$Title,
        [int]$WindowWidth,
        [int]$WindowHeight
    )
    
    Write-Verbose "Creating WPF window"
    
    $window = New-Object System.Windows.Window
    $window.Title = $Title
    $window.Width = $WindowWidth
    $window.Height = $WindowHeight
    $window.WindowStartupLocation = 'CenterScreen'
    $window.ResizeMode = 'CanResize'
    
    return $window
}

function Read-XamlFile {
    param(
        [string]$Path
    )
    
    Write-Verbose "Reading XAML from: $Path"
    
    try {
        $xamlContent = Get-Content -Path $Path -Raw -ErrorAction Stop
        
        # Remove BOM if present
        if ($xamlContent[0] -eq 0xEF -and $xamlContent[1] -eq 0xBB -and $xamlContent[2] -eq 0xBF) {
            $xamlContent = $xamlContent.Substring(3)
        }
        
        return $xamlContent
    }
    catch {
        Write-Error "Failed to read XAML file: $_"
        throw
    }
}

function Convert-XamlToWindow {
    param(
        [string]$Xaml
    )
    
    Write-Verbose "Converting XAML to WPF window"
    
    try {
        $reader = [System.Xml.XmlReader]::Create([System.IO.StringReader]::new($Xaml))
        $window = [System.Windows.Markup.XamlReader]::Load($reader)
        return $window
    }
    catch {
        Write-Error "Failed to parse XAML: $_"
        throw
    }
}

function Set-WpfDataContext {
    param(
        [System.Windows.Window]$Window,
        [hashtable]$Data
    )
    
    Write-Verbose "Setting data context"
    
    if ($Data) {
        $Window.DataContext = $Data
        Write-Verbose "Data context set with $($Data.Count) properties"
    }
}

function Find-WpfElement {
    param(
        [System.Windows.Window]$Window,
        [string]$Name
    )
    
    Write-Verbose "Finding element: $Name"
    
    try {
        $element = $Window.FindName($Name)
        return $element
    }
    catch {
        Write-Warning "Could not find element: $Name"
        return $null
    }
}

function Add-WpfEventHandler {
    param(
        [System.Windows.Window]$Window,
        [string]$ElementName,
        [string]$EventName,
        [scriptblock]$Handler
    )
    
    Write-Verbose "Adding event handler: $ElementName.$EventName"
    
    $element = Find-WpfElement -Window $Window -Name $ElementName
    
    if (-not $element) {
        Write-Warning "Element not found: $ElementName"
        return
    }
    
    try {
        $eventInfo = $element.GetType().GetEvent($EventName)
        $eventInfo.AddEventHandler($element, $Handler)
        Write-Verbose "Event handler added successfully"
    }
    catch {
        Write-Warning "Failed to add event handler: $_"
    }
}

function Update-WpfBinding {
    param(
        [System.Windows.Window]$Window,
        [string]$ElementName,
        [string]$PropertyName,
        [object]$Value
    )
    
    Write-Verbose "Updating binding: $ElementName.$PropertyName"
    
    $element = Find-WpfElement -Window $Window -Name $ElementName
    
    if ($element) {
        $element.GetType().GetProperty($PropertyName).SetValue($element, $Value)
    }
}

function New-WpfXamlTemplate {
    param(
        [string]$Title,
        [int]$WindowWidth,
        [int]$WindowHeight
    )
    
    Write-Verbose "Generating WPF XAML template"
    
    $xaml = @"
<Window x:Class="$Title.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="$Title"
        Width="$WindowWidth"
        Height="$WindowHeight"
        WindowStartupLocation="CenterScreen">
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>
        
        <!-- Header -->
        <StackPanel Grid.Row="0" Background="#FF2D2D30" Padding="10">
            <TextBlock Text="$Title" FontSize="18" Foreground="White" FontWeight="Bold"/>
        </StackPanel>
        
        <!-- Main Content -->
        <StackPanel Grid.Row="1" Margin="20">
            <TextBlock Text="Content Area" FontSize="14" Margin="0,0,0,10"/>
            <TextBox Name="txtContent" Height="100" TextWrapping="Wrap" AcceptsReturn="True"/>
        </StackPanel>
        
        <!-- Footer -->
        <StackPanel Grid.Row="2" Orientation="Horizontal" HorizontalAlignment="Right" Margin="20">
            <Button Name="btnOk" Content="OK" Width="80" Margin="0,0,10,0"/>
            <Button Name="btnCancel" Content="Cancel" Width="80"/>
        </StackPanel>
    </Grid>
</Window>
"@
    
    return $xaml
}

function New-MvvmViewModel {
    param(
        [hashtable]$Properties,
        [hashtable]$Commands
    )
    
    Write-Verbose "Creating MVVM ViewModel"
    
    $viewModel = [PSCustomObject]@{
        Properties = $Properties
        Commands = $Commands
    }
    
    # Implement INotifyPropertyChanged
    $viewModel | Add-Member -Name PropertyChanged -MemberType ScriptProperty -Value {
        param($property)
        Write-Verbose "Property changed: $property"
    }
    
    return $viewModel
}

function Show-WpfDialog {
    param(
        [System.Windows.Window]$Window
    )
    
    Write-Verbose "Showing WPF dialog"
    
    try {
        $app = New-Object System.Windows.Application
        $app.Run($Window) | Out-Null
        Write-Verbose "WPF dialog closed"
    }
    catch {
        Write-Error "Failed to show WPF dialog: $_"
        throw
    }
}

try {
    Write-Verbose "Starting WPF build process"
    
    Initialize-WpfAssemblies
    
    $window = $null
    
    if ($XamlPath) {
        $xamlContent = Read-XamlFile -Path $XamlPath
        $window = Convert-XamlToWindow -Xaml $xamlContent
        
        Set-WpfDataContext -Window $window -Data $ViewModel
        
        Write-Host "WPF window loaded from XAML"
    }
    elseif ($GenerateXaml) {
        $xamlTemplate = New-WpfXamlTemplate -Title $WindowTitle -WindowWidth $Width -WindowHeight $Height
        
        if ($OutputXamlPath) {
            Set-Content -Path $OutputXamlPath -Value $xamlTemplate -Encoding UTF8
            Write-Host "XAML template generated: $OutputXamlPath"
        }
        
        $window = Convert-XamlToWindow -Xaml $xamlTemplate
        
        Write-Host "WPF window created from template"
    }
    else {
        $window = New-WpfWindow -Title $WindowTitle -WindowWidth $Width -WindowHeight $Height
        
        # Add basic content
        $stackPanel = New-Object System.Windows.Controls.StackPanel
        $window.Content = $stackPanel
        
        $label = New-Object System.Windows.Controls.Label
        $label.Content = "WPF Application"
        $label.FontSize = 16
        $stackPanel.Children.Add($label) | Out-Null
        
        Write-Host "Basic WPF window created"
    }
    
    if ($ViewModel) {
        Set-WpfDataContext -Window $window -Data $ViewModel
    }
    
    if ($Show) {
        Show-WpfDialog -Window $window
    }
    else {
        Write-Host "WPF application built successfully"
        Write-Host "Title: $WindowTitle"
        Write-Host "Size: ${Width}x$Height"
    }
    
    Write-Verbose "WPF build completed"
}
catch {
    Write-Error "WPF build failed: $_"
    exit 1
}
finally {
    Write-Verbose "Build WPF script completed"
}

Export-ModuleMember -Function New-WpfWindow, Read-XamlFile, Convert-XamlToWindow, Set-WpfDataContext
