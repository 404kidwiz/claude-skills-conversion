# AD Security Reviewer - Quick Start Guide

This guide helps you get started with the AD security reviewer skill's scripts and tools.

## Prerequisites

- Windows Server 2016 or later with Active Directory
- Remote Server Administration Tools (RSAT) installed
- Domain Administrator privileges for comprehensive audits
- PowerShell 5.1 or later
- For TypeScript scripts: Node.js 16+, Azure AD app registration

## Installing Required Modules

```powershell
# Install RSAT features (PowerShell)
Install-WindowsFeature RSAT-AD-PowerShell -IncludeManagementTools

# Import modules
Import-Module ActiveDirectory
```

## Azure AD App Registration (for TypeScript scripts)

1. **Create App Registration:**
   ```bash
   # Azure Portal → App registrations → New registration
   # Name: AD Security Reviewer
   # Permissions: Directory.Read.All, AuditLog.Read.All
   ```

2. **Generate Client Secret:**
   ```bash
   # Certificates & secrets → New client secret
   ```

## Quick Examples

### PowerShell: Auditing Privileged Groups

```powershell
# Audit all privileged groups in the domain
.\audit_privileged_groups.ps1 -Domain "example.com" -Threshold 5

# Audit with custom inactive days threshold
.\audit_privileged_groups.ps1 -Domain "example.com" -InactiveDays 60

# Generate report to specific location
.\audit_privileged_groups.ps1 -ReportPath "C:\Reports\privileged_audit.html"
```

### PowerShell: Reviewing Delegation

```powershell
# Review delegation across entire domain
.\review_delegation.ps1 -SearchBase "DC=example,DC=com"

# Review specific OU only
.\review_delegation.ps1 -SearchBase "OU=Users,DC=example,DC=com"

# Set custom report path
.\review_delegation.ps1 -ReportPath "C:\Reports\delegation_review.html"
```

### TypeScript: Running Security Assessment

```typescript
import { ADSecurityAnalyzer } from './scripts/analyze_ad_security';

const analyzer = new ADSecurityAnalyzer(
  'client-id',
  'client-secret',
  'tenant-id'
);

// Perform comprehensive security assessment
const assessment = await analyzer.performSecurityAssessment();

// Generate report
const report = generateSecurityReport(assessment);
console.log(report);

// Save report to file
const fs = require('fs');
fs.writeFileSync('security_report.md', report);
```

## Common Patterns

### Automated Security Assessments

```powershell
# Run all security audits daily
$today = Get-Date -Format "yyyy-MM-dd"
$reportPath = "C:\Reports\$today-security-audit.html"

# Run privileged group audit
.\audit_privileged_groups.ps1 -ReportPath "$reportPath-groupts.html"

# Run delegation review
.\review_delegation.ps1 -ReportPath "$reportPath-delegation.html"

# Run TypeScript assessment
node assess_security.js
```

### Monthly Security Reviews

```typescript
import { ADSecurityAnalyzer, generateSecurityReport } from './scripts/analyze_ad_security';
import * as fs from 'fs';

async function monthlySecurityReview() {
  const analyzer = new ADSecurityAnalyzer(
    process.env.AZURE_CLIENT_ID,
    process.env.AZURE_CLIENT_SECRET,
    process.env.AZURE_TENANT_ID
  );

  // Perform assessment
  const assessment = await analyzer.performSecurityAssessment();

  // Generate report
  const report = generateSecurityReport(assessment);

  // Save with timestamp
  const timestamp = new Date().toISOString().split('T')[0];
  const reportPath = `security_report_${timestamp}.md`;
  fs.writeFileSync(reportPath, report);

  console.log(`Report saved to: ${reportPath}`);

  // Alert if critical findings
  if (assessment.summary.critical > 0) {
    console.error(`ALERT: ${assessment.summary.critical} critical findings detected!`);
    // Send alert notification...
  }
}

monthlySecurityReview().catch(console.error);
```

### Targeted Delegation Audits

```powershell
# Find all delegation from specific user
$targetUser = "jdoe"
$reportPath = "C:\Reports\delegation_${targetUser}.html"

.\review_delegation.ps1 -SearchBase "DC=example,DC=com" | Out-String |
    Select-String -Pattern $targetUser -Context 0, 2 |
    Out-File $reportPath
```

## Security Assessment Components

The TypeScript security analyzer performs the following checks:

1. **Privileged Group Memberships**
   - Enterprise Admins
   - Domain Admins
   - Schema Admins
   - Administrators
   - Account Operators
   - Backup Operators

2. **Stale Account Detection**
   - Accounts inactive for 90+ days
   - Users with no recent sign-in activity

3. **Password Policy Review**
   - Lockout threshold validation
   - Lockout duration verification
   - Password complexity requirements

4. **MFA Enrollment Check**
   - Percentage of users with MFA enabled
   - Identification of non-MFA privileged accounts

5. **Suspicious Sign-In Analysis**
   - High-risk sign-in attempts
   - Unusual geographic locations
   - Atypical device usage

6. **Conditional Access Policies**
   - Policy existence check
   - MFA requirement for admins
   - Geographic restrictions

7. **Risky User Detection**
   - Medium and high risk users
   - Compromised account indicators

## Best Practices

1. **Run Regular Audits** - Weekly or monthly security assessments
2. **Review Findings Promptly** - Address critical issues immediately
3. **Document Remediation** - Track fixes and their effectiveness
4. **Implement Baselines** - Establish security baselines and monitor deviations
5. **Use Least Privilege** - Regularly review and reduce privileged access
6. **Monitor Changes** - Set up alerts for privileged group modifications
7. **Educate Users** - Train staff on security best practices
8. **Test Recovery** - Ensure remediation procedures work correctly

## Troubleshooting

### Module Import Errors

```
Error: Active Directory module not available
```

**Solution:**
```powershell
Install-WindowsFeature RSAT-AD-PowerShell -IncludeManagementTools
Import-Module ActiveDirectory
```

### Permission Denied Errors

```
Error: Access is denied
```

**Solutions:**
1. Run PowerShell as Administrator
2. Use Domain Admin credentials
3. Ensure account has necessary delegated permissions

### Graph API Authentication Failed

```
Error: Access token request failed
```

**Solutions:**
1. Verify client ID, client secret, and tenant ID
2. Check if app registration is active
3. Ensure Directory.Read.All permission is granted
4. Verify admin consent has been granted

### Large Dataset Timeouts

```
Error: Operation timed out
```

**Solutions:**
1. Process in smaller batches
2. Increase script timeout values
3. Use specific OUs instead of entire domain
4. Run during off-peak hours

## Interpreting Findings

### Critical Severity

Findings that pose immediate security risk:
- Unnecessary Domain Admin memberships
- Disabled accounts with privileges
- GenericAll delegation rights
- High-risk sign-ins from unknown locations

**Action Required:** Immediate remediation

### High Severity

Significant security concerns:
- Excessive privileged group members
- Accounts inactive >90 days with privileges
- MFA not enabled for admins
- Weak password policies

**Action Required:** Remediation within 24-48 hours

### Medium Severity

Security issues that should be addressed:
- Non-privileged accounts with delegation
- Passwords not changed >365 days
- Moderate risk users
- Incomplete conditional access coverage

**Action Required:** Remediation within 1-2 weeks

### Low Severity

Minor security concerns:
- Documentation gaps
- Naming convention violations
- Minor policy inconsistencies

**Action Required:** Address during next maintenance window

## Integration with Monitoring

### Email Alerts for Critical Findings

```typescript
import { sendEmail } from './email_utils';

async function alertOnCriticalFindings(assessment: SecurityAssessmentResult) {
  const criticalFindings = assessment.findings.filter(f => f.severity === 'Critical');

  if (criticalFindings.length > 0) {
    const subject = `CRITICAL: ${criticalFindings.length} security findings detected`;
    const body = generateSecurityReport(assessment);

    await sendEmail('security-team@example.com', subject, body);
  }
}
```

### SIEM Integration

```powershell
# Send audit events to SIEM
$events = Get-Content ".\audit_log.log" | ConvertFrom-Csv

foreach ($event in $events) {
    if ($event.Level -eq 'ERROR' -or $event.Level -eq 'CRITICAL') {
        # Send to SIEM (example for Sentinel)
        Invoke-RestMethod -Uri "https://siem.example.com/api/events" `
            -Method Post `
            -Body ($event | ConvertTo-Json) `
            -ContentType "application/json"
    }
}
```

## Additional Resources

- [Active Directory Security Best Practices](https://docs.microsoft.com/windows-server/identity/ad-ds/plan/security-best-practices)
- [Microsoft Graph Security API](https://docs.microsoft.com/graph/api/resources/security-overview)
- [Azure Identity Protection](https://docs.microsoft.com/azure/active-directory/identity-protection/overview)
- [Privileged Identity Management](https://docs.microsoft.com/azure/active-directory/privileged-identity-management/)
- [Conditional Access Policies](https://docs.microsoft.com/azure/active-directory/conditional-access/)
