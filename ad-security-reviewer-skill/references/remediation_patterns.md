# Active Directory Security Remediation Patterns

Common patterns and best practices for remediating Active Directory security findings.

## Privileged Group Remediation

### Automated Privilege Reduction

```powershell
function Remove-ExcessivePrivilegedMembers {
    param(
        [string]$GroupName,
        [int]$MaxMembers
    )

    $group = Get-ADGroup -Identity $GroupName

    if ($group) {
        $members = Get-ADGroupMember -Identity $group

        if ($members.Count -gt $MaxMembers) {
            Write-Warning "Group $GroupName has $($members.Count) members (limit: $MaxMembers)"

            # Remove non-admin members
            foreach ($member in $members) {
                $user = Get-ADUser -Identity $member -ErrorAction SilentlyContinue

                if ($user) {
                    $isAdmin = $user.MemberOf | Where-Object {
                        $_ -match 'Admin|Administrator'
                    }

                    if (-not $isAdmin) {
                        Write-Host "Removing $($user.SamAccountName) from $GroupName"
                        Remove-ADGroupMember -Identity $group -Members $user -Confirm:$false
                    }
                }
            }
        }
    }
}
```

### Just-In-Time Admin Access

```typescript
interface JitAccessRequest {
  requesterId: string;
  targetRole: string;
  duration: number; // hours
  justification: string;
  approvalRequired: boolean;
}

async function grantJitAccess(request: JitAccessRequest): Promise<boolean> {
  // Validate request
  const requester = await getUserById(request.requesterId);
  const hasApproval = await checkManagerApproval(request);

  if (!hasApproval && request.approvalRequired) {
    console.log('Access request pending approval');
    return false;
  }

  // Add to privileged group temporarily
  const groupId = await getGroupIdByRole(request.targetRole);

  await addMemberToGroup(groupId, request.requesterId);

  // Schedule removal
  setTimeout(async () => {
    await removeMemberFromGroup(groupId, request.requesterId);
    console.log(`JIT access expired for user ${request.requesterId}`);
  }, request.duration * 60 * 60 * 1000);

  // Log the access grant
  await logAuditEvent({
    action: 'JitAccessGranted',
    userId: request.requesterId,
    role: request.targetRole,
    duration: request.duration,
    justification: request.justification
  });

  return true;
}
```

### PIM (Privileged Identity Management) Integration

```typescript
async function configurePIMRole(
  roleId: string,
  approvers: string[],
  settings: {
    maxDuration: number;
    justificationRequired: boolean;
    approvalRequired: boolean;
    notificationRequired: boolean;
  }
): Promise<boolean> {
  try {
    const pimSettings = {
      roleSettings: {
        isMfaOn: true,
        maxEligibleActivationDuration: settings.maxDuration,
        justificationRequiredOnActivation: settings.justificationRequired,
        approvalRequiredOnActivation: settings.approvalRequired,
        ticketingInfoRequiredOnActivation: false,
        notificationRequired: settings.notificationRequired,
        approvers: approvers.map(a => ({
          id: a,
          description: 'Manager',
          isDefault: true
        }))
      }
    };

    await graphClient
      .api(`/roleManagement/roleDefinitions/${roleId}/roleSettings`)
      .patch(pimSettings);

    return true;
  } catch (error) {
    console.error('Failed to configure PIM role:', error);
    return false;
  }
}
```

## Account Security Remediation

### Stale Account Remediation

```powershell
function Disable-StaleAccounts {
    param(
        [int]$InactiveDays = 90,
        [string[]]$ExcludedUsers = @(),
        [string]$LogPath = ".\stale_account_remediation.log"
    )

    $thresholdDate = (Get-Date).AddDays(-$InactiveDays)

    $staleUsers = Get-ADUser -Filter {
        Enabled -eq $true -and
        LastLogonDate -lt $thresholdDate
    } -Properties LastLogonDate,DisplayName,MemberOf

    foreach ($user in $staleUsers) {
        # Skip excluded users
        if ($user.SamAccountName -in $ExcludedUsers) {
            continue
        }

        # Check if user has any active roles
        $hasPrivileges = $user.MemberOf | Where-Object {
            $_ -match 'Admin|Operator|Creator'
        }

        if ($hasPrivileges) {
            Write-Warning "Privileged stale account: $($user.SamAccountName)"

            # Log but don't disable privileged accounts
            "$((Get-Date)) - Privileged stale account: $($user.SamAccountName), DN: $($user.DistinguishedName)" |
                Add-Content $LogPath
        } else {
            Write-Host "Disabling stale account: $($user.SamAccountName)"

            Disable-ADAccount -Identity $user -Confirm:$false

            # Move to disabled OU
            $disabledOU = "OU=Disabled Users,DC=example,DC=com"
            Move-ADObject -Identity $user.DistinguishedName -TargetPath $disabledOU

            "$((Get-Date)) - Disabled stale account: $($user.SamAccountName)" |
                Add-Content $LogPath
        }
    }
}
```

### Password Reset and MFA Enforcement

```typescript
async function enforceMFAForPrivilegedUsers(): Promise<{ enforced: number; failed: number }> {
  let enforced = 0;
  let failed = 0;

  // Get all privileged users
  const privilegedGroups = await getPrivilegedGroupIds();
  const privilegedUserIds = new Set<string>();

  for (const groupId of privilegedGroups) {
    const members = await getGroupMembers(groupId);
    members.forEach(m => privilegedUserIds.add(m.id));
  }

  // Check each user's MFA status
  for (const userId of privilegedUserIds) {
    const authMethods = await getUserAuthMethods(userId);

    const hasMFA = authMethods.some(m =>
      m['@odata.type'] === '#microsoft.graph.phoneAuthenticationMethod' ||
      m['@odata.type'] === '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod'
    );

    if (!hasMFA) {
      try {
        // Enable MFA requirement
        await setStrongMFARequirement(userId);

        // Send password reset link
        await initiatePasswordReset(userId);

        enforced++;
        console.log(`Enforced MFA for user ${userId}`);
      } catch (error) {
        failed++;
        console.error(`Failed to enforce MFA for user ${userId}:`, error);
      }
    }
  }

  return { enforced, failed };
}
```

## Delegation Remediation

### Removing Excessive Delegation

```powershell
function Remove-ExcessiveDelegation {
    param(
        [string]$ObjectDN,
        [string]$Trustee
    )

    try {
        $acl = Get-Acl -Path ("AD:\\" + $ObjectDN)

        foreach ($ace in $acl.Access) {
            if ($ace.IdentityReference.Value -eq $Trustee -and
                $ace.ActiveDirectoryRights -match 'GenericAll|Write') {

                Write-Host "Removing delegation from $ObjectDN to $Trustee"

                $acl.RemoveAccessRule($ace)
                Set-Acl -Path ("AD:\\" + $ObjectDN) -AclObject $acl

                # Log the change
                $logEntry = "$((Get-Date)) - Removed delegation: $ObjectDN -> $Trustee, Rights: $($ace.ActiveDirectoryRights)"
                Add-Content ".\delegation_remediation.log" $logEntry
            }
        }
    }
    catch {
        Write-Error "Failed to remove delegation: $($_.Exception.Message)"
    }
}
```

### Implementing Role-Based Access Control

```typescript
interface RoleDefinition {
  roleName: string;
  description: string;
  permissions: Permission[];
  allowedOUs: string[];
}

interface Permission {
  objectType: string;
  accessRights: string[];
}

async function implementRBAC(roleDefinitions: RoleDefinition[]): Promise<boolean> {
  try {
    for (const role of roleDefinitions) {
      // Create role groups
      const groupName = `RBAC_${role.roleName.replace(/\s+/g, '_')}`;

      const existingGroup = await findGroupByName(groupName);
      if (!existingGroup) {
        await createGroup({
          displayName: role.roleName,
          mailNickname: groupName,
          description: role.description
        });
      }

      // Apply permissions
      for (const permission of role.permissions) {
        for (const ou of role.allowedOUs) {
          await applyPermission({
            target: ou,
            trustee: groupName,
            objectType: permission.objectType,
            accessRights: permission.accessRights
          });
        }
      }

      // Create documentation
      await createRoleDocumentation(role);
    }

    return true;
  } catch (error) {
    console.error('Failed to implement RBAC:', error);
    return false;
  }
}
```

## Conditional Access Remediation

### Enforcing MFA for Admins

```typescript
async function createMFAForAdminsPolicy(): Promise<boolean> {
  try {
    const policy = {
      displayName: 'MFA Required for Administrators',
      state: 'enabled',
      conditions: {
        users: {
          includeRoles: [
            'Global Administrator',
            'Security Administrator',
            'Privileged Role Administrator',
            'Exchange Administrator',
            'SharePoint Administrator'
          ]
        },
        applications: {
          includeApplications: ['All']
        }
      },
      grantControls: {
        operator: 'OR',
        builtInControls: ['mfa']
      }
    };

    await graphClient
      .api('/identity/conditionalAccess/policies')
      .post(policy);

    console.log('MFA policy for administrators created');
    return true;
  } catch (error) {
    console.error('Failed to create MFA policy:', error);
    return false;
  }
}
```

### Geographic Access Restrictions

```typescript
async function createGeoRestrictionPolicy(
  allowedLocations: string[]
): Promise<boolean> {
  try {
    // Create named locations
    for (const location of allowedLocations) {
      await graphClient
        .api('/identity/conditionalAccess/namedLocations')
        .post({
          displayName: location,
          ipRanges: [
            {
              cidrAddress: await getLocationCIDR(location)
            }
          ]
        });
    }

    // Create policy
    const policy = {
      displayName: 'Geographic Access Restriction',
      state: 'enabled',
      conditions: {
        users: {
          includeUsers: ['All']
        },
        locations: {
          includeLocations: allowedLocations
        }
      },
      grantControls: {
        operator: 'OR',
        builtInControls: ['block']
      }
    };

    await graphClient
      .api('/identity/conditionalAccess/policies')
      .post(policy);

    console.log('Geographic restriction policy created');
    return true;
  } catch (error) {
    console.error('Failed to create geo restriction policy:', error);
    return false;
  }
}
```

## Automated Response Patterns

### Incident Response Workflow

```typescript
async function handleSecurityIncident(incident: SecurityIncident): Promise<boolean> {
  const incidentId = await createIncidentTicket(incident);

  try {
    // Step 1: Contain
    await containIncident(incident);

    // Step 2: Investigate
    const investigation = await investigateIncident(incident);

    // Step 3: Remediate
    await remediateIncident(incident, investigation);

    // Step 4: Document
    await updateIncidentTicket(incidentId, investigation, remediationActions);

    // Step 5: Post-incident review
    await schedulePostIncidentReview(incidentId);

    return true;
  } catch (error) {
    await updateIncidentStatus(incidentId, 'Failed', error.message);
    return false;
  }
}

async function containIncident(incident: SecurityIncident): Promise<void> {
  // Disable affected accounts
  for (const userId of incident.affectedUsers) {
    await disableAccount(userId);
  }

  // Block IPs
  for (const ip of incident.sourceIPs) {
    await blockIPAddress(ip);
  }

  // Revoke active sessions
  await revokeAllSessions(incident.affectedUsers);
}
```

### Continuous Monitoring Pattern

```typescript
async function continuousSecurityMonitoring(): Promise<void> {
  console.log('Starting continuous security monitoring...');

  setInterval(async () => {
    try {
      // Run security assessment
      const assessment = await performSecurityAssessment();

      // Check for new critical findings
      const criticalFindings = assessment.findings.filter(
        f => f.severity === 'Critical'
      );

      if (criticalFindings.length > 0) {
        await sendSecurityAlert(criticalFindings);
      }

      // Update security dashboard
      await updateSecurityDashboard(assessment);

    } catch (error) {
      console.error('Monitoring scan failed:', error);
    }
  }, 3600000); // Every hour
}
```

## Compliance Reporting

### Automated Compliance Checks

```typescript
interface ComplianceFramework {
  name: string;
  controls: ComplianceControl[];
}

interface ComplianceControl {
  controlId: string;
  description: string;
  testFunction: () => Promise<ComplianceResult>;
}

async function runComplianceAssessment(
  framework: ComplianceFramework
): Promise<ComplianceReport> {
  const results: ComplianceResult[] = [];

  for (const control of framework.controls) {
    console.log(`Testing control: ${control.controlId}`);

    const result = await control.testFunction();
    results.push(result);

    if (!result.compliant) {
      await createComplianceFinding(result);
    }
  }

  const compliantCount = results.filter(r => r.compliant).length;
  const compliancePercentage = (compliantCount / results.length) * 100;

  const report: ComplianceReport = {
    framework: framework.name,
    timestamp: new Date().toISOString(),
    results,
    summary: {
      total: results.length,
      compliant: compliantCount,
      nonCompliant: results.length - compliantCount,
      compliancePercentage
    }
  };

  return report;
}
```

## Recovery and Restoration

### Post-Remediation Verification

```powershell
function Test-RemediationSuccess {
    param(
        [string]$RemediationType,
        [hashtable]$TestCases
    )

    $results = @{}

    foreach ($testCase in $TestCases.GetEnumerator()) {
        Write-Host "Testing: $($testCase.Name)"

        switch ($RemediationType) {
            'GroupMembership' {
                $testGroup = Get-ADGroup -Identity $testCase.Value.GroupName
                $currentMembers = Get-ADGroupMember -Identity $testGroup | Select-Object -ExpandProperty Name

                if ($currentMembers.Count -eq $testCase.Value.ExpectedCount) {
                    $results[$testCase.Name] = 'PASS'
                } else {
                    $results[$testCase.Name] = 'FAIL - Expected $($testCase.Value.ExpectedCount), got $($currentMembers.Count)'
                }
            }
            'Delegation' {
                $acl = Get-Acl -Path ("AD:\\" + $testCase.Value.ObjectDN)
                $delegationExists = $acl.Access | Where-Object {
                    $_.IdentityReference.Value -eq $testCase.Value.Trustee -and
                    $_.ActiveDirectoryRights -match $testCase.Value.Rights
                }

                if ($delegationExists) {
                    $results[$testCase.Name] = 'FAIL - Delegation still exists'
                } else {
                    $results[$testCase.Name] = 'PASS'
                }
            }
        }
    }

    return $results
}
```

### Rollback Procedures

```typescript
async function rollbackSecurityChanges(changeId: string): Promise<boolean> {
  try {
    // Get change details
    const change = await getSecurityChange(changeId);

    // Restore previous state
    switch (change.type) {
      case 'GroupMembership':
        await restoreGroupMembers(change.groupId, change.previousMembers);
        break;

      case 'Delegation':
        await restoreDelegationPermissions(change.objectDN, change.previousACL);
        break;

      case 'ConditionalAccess':
        await restoreConditionalAccessPolicy(change.policyId, change.previousSettings);
        break;
    }

    // Mark change as rolled back
    await updateChangeStatus(changeId, 'Rolled Back');

    console.log(`Rollback completed for change ${changeId}`);
    return true;
  } catch (error) {
    console.error('Rollback failed:', error);
    return false;
  }
}
```
