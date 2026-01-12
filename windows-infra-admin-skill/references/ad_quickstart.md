# Windows Infrastructure Admin - Quick Start Guide

This guide helps you get started with the Windows infrastructure admin skill's scripts and tools.

## Prerequisites

- Windows Server 2016 or later
- Remote Server Administration Tools (RSAT) installed
- Domain Administrator privileges for most operations
- PowerShell 5.1 or later
- Active Directory module for AD operations

## Installing Required Modules

```powershell
# Install RSAT features (if not already installed)
Install-WindowsFeature RSAT-AD-PowerShell
Install-WindowsFeature RSAT-DNS-Server
Install-WindowsFeature RSAT-Group-Policy-Management

# Import modules
Import-Module ActiveDirectory
Import-Module DnsServer
Import-Module GroupPolicy
```

## Authentication

The scripts require appropriate permissions:

- **Active Directory Operations**: Domain Admin or delegated permissions
- **DNS Management**: DNS Administrator or Domain Admin
- **Group Policy**: Group Policy Creator Owner or Domain Admin

## Quick Examples

### Managing Active Directory Users

```powershell
# Create a new user
.\manage_ad_users.ps1 -Action Create `
  -Username "jdoe" `
  -FirstName "John" `
  -LastName "Doe" `
  -Email "jdoe@example.com" `
  -OU "OU=Users,DC=example,DC=com" `
  -Enabled $true

# List all users
.\manage_ad_users.ps1 -Action List

# Disable a user account
.\manage_ad_users.ps1 -Action Disable -Username "jdoe"

# Enable a user account
.\manage_ad_users.ps1 -Action Enable -Username "jdoe"

# Update user information
.\manage_ad_users.ps1 -Action Update `
  -Username "jdoe" `
  -Email "john.doe@newdomain.com" `
  -FirstName "Jonathan"
```

### Configuring DNS

```powershell
# Create a new DNS zone
.\configure_dns.ps1 -Action CreateZone -ZoneName "example.com"

# Create an A record
.\configure_dns.ps1 -Action CreateRecord `
  -ZoneName "example.com" `
  -RecordName "www" `
  -RecordType "A" `
  -RecordData "192.168.1.10"

# Create an MX record
.\configure_dns.ps1 -Action CreateRecord `
  -ZoneName "example.com" `
  -RecordName "@" `
  -RecordType "MX" `
  -RecordData "mail.example.com" `
  -Priority 10

# Query DNS
.\configure_dns.ps1 -Action QueryDNS -ZoneName "www.example.com" -RecordType "A"

# Test DNS health
.\configure_dns.ps1 -Action TestDNS -ZoneName "example.com"
```

### Managing Group Policy

```powershell
# Create a new GPO
.\setup_gpo.ps1 -Action CreateGPO `
  -GPOName "Workstation Security" `
  -Description "Security policies for workstations"

# Link GPO to OU
.\setup_gpo.ps1 -Action LinkGPO `
  -GPOName "Workstation Security" `
  -TargetOU "OU=Workstations,DC=example,DC=com"

# List all GPOs
.\setup_gpo.ps1 -Action ListGPOs

# Backup a GPO
.\setup_gpo.ps1 -Action BackupGPO `
  -GPOName "Workstation Security" `
  -BackupPath ".\GPOBackups"

# Generate GPO report
.\setup_gpo.ps1 -Action ReportGPO -GPOName "Workstation Security"
```

## Common Patterns

### Batch User Creation

```powershell
$users = @(
    @{Username="user1"; FirstName="User"; LastName="One"; Email="user1@example.com"},
    @{Username="user2"; FirstName="User"; LastName="Two"; Email="user2@example.com"}
)

foreach ($user in $users) {
    .\manage_ad_users.ps1 -Action Create `
        -Username $user.Username `
        -FirstName $user.FirstName `
        -LastName $user.LastName `
        -Email $user.Email
}
```

### Bulk DNS Record Creation

```powershell
$records = @(
    @{Name="www"; Type="A"; Data="192.168.1.10"},
    @{Name="mail"; Type="A"; Data="192.168.1.20"},
    @{Name="ftp"; Type="A"; Data="192.168.1.30"}
)

foreach ($record in $records) {
    .\configure_dns.ps1 -Action CreateRecord `
        -ZoneName "example.com" `
        -RecordName $record.Name `
        -RecordType $record.Type `
        -RecordData $record.Data
}
```

### GPO Security Settings

```powershell
$settings = @{
    PasswordPolicy = @{
        MinLength = 12
        History = 12
        MaxAgeDays = 60
    }
    AuditPolicy = @{
        "Logon" = @{Success = $true; Failure = $true}
        "Privilege Use" = @{Success = $true; Failure = $true}
        "Process Tracking" = @{Success = $false; Failure = $false}
    }
}

.\setup_gpo.ps1 -Action ApplySettings `
  -GPOName "Security Baseline" `
  -GPOSettings $settings
```

## Best Practices

1. **Test in lab environment first** - Always test scripts in a non-production environment
2. **Use descriptive OU structures** - Organize OUs by function, location, or department
3. **Document GPO changes** - Keep a record of GPO modifications and their purposes
4. **Backup before changes** - Always backup GPOs before making modifications
5. **Use least privilege** - Grant only necessary permissions for scripts
6. **Enable logging** - Use the LogPath parameter to track operations
7. **Validate inputs** - All scripts include built-in validation
8. **Plan DNS changes** - Document DNS record changes and maintain a DNS inventory

## Troubleshooting

### AD Module Not Found

```
Error: Active Directory module not available
```

**Solution**:
```powershell
Install-WindowsFeature RSAT-AD-PowerShell -IncludeManagementTools
Import-Module ActiveDirectory
```

### Permission Denied Errors

```
Error: Access denied
```

**Solutions**:
1. Run PowerShell as Administrator
2. Ensure you have Domain Admin privileges
3. Check if the account has necessary delegated permissions

### GPO Link Failed

```
Error: Failed to link GPO
```

**Solutions**:
1. Verify the OU path is correct
2. Ensure the GPO exists
3. Check if you have permissions on the target OU

### DNS Record Not Resolving

```
Error: DNS query failed
```

**Solutions**:
1. Check if the DNS server service is running
2. Verify the record exists
3. Check DNS server replication
4. Test with `nslookup` command

### User Creation Fails

```
Error: Failed to create user
```

**Solutions**:
1. Check if username already exists
2. Verify OU path is valid
3. Ensure password policy allows the temporary password
4. Check if account has Create User permissions in the OU

## Useful PowerShell Commands

```powershell
# Find a user
Get-ADUser -Filter {Name -like "*John*"}

# Check user groups
Get-ADUser -Identity "jdoe" -Properties MemberOf | Select-Object -ExpandProperty MemberOf

# Get GPO links
Get-GPLink -Target "OU=Users,DC=example,DC=com"

# Test DNS resolution
Resolve-DnsName -Name "www.example.com"

# Check DNS server status
Get-Service -Name DNS

# Get DNS zones
Get-DnsServerZone

# View GPO inheritance
gpresult /r
```

## Security Considerations

1. **Secure credentials** - Never hardcode passwords in scripts
2. **Use managed service accounts** - For automated tasks
3. **Audit privileged operations** - Enable logging for admin actions
4. **Implement tiered administration** - Separate admin and regular user accounts
5. **Regular password rotations** - Use managed service accounts with automatic password rotation
6. **Monitor AD changes** - Set up alerts for critical AD modifications

## Additional Resources

- [Active Directory Documentation](https://docs.microsoft.com/active-directory)
- [DNS Server Documentation](https://docs.microsoft.com/windows-server/networking/dns)
- [Group Policy Documentation](https://docs.microsoft.com/windows-server/group-policy)
- [PowerShell Documentation](https://docs.microsoft.com/powershell)
- [Server Administration Tools](https://docs.microsoft.com/windows-server/administration/server-manager)
