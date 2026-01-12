import { ClientSecretCredential } from '@azure/identity';
import { Client } from '@microsoft/microsoft-graph-client';
import 'isomorphic-fetch';

export interface SecurityFinding {
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | 'Informational';
  category: string;
  title: string;
  description: string;
  recommendation: string;
  affectedResources: string[];
}

export interface SecurityAssessmentResult {
  timestamp: string;
  findings: SecurityFinding[];
  summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    informational: number;
  };
}

export class ADSecurityAnalyzer {
  private graphClient: Client;

  constructor(private clientId: string, private clientSecret: string, private tenantId: string) {
    const credential = new ClientSecretCredential(
      this.tenantId,
      this.clientId,
      this.clientSecret
    );

    this.graphClient = Client.initWithMiddleware({
      authProvider: {
        getAccessToken: async () => {
          const token = await credential.getToken('https://graph.microsoft.com/.default');
          return token.token;
        }
      }
    });
  }

  async performSecurityAssessment(): Promise<SecurityAssessmentResult> {
    const findings: SecurityFinding[] = [];

    console.log('Starting Active Directory security assessment...');

    // Check privileged group memberships
    findings.push(...await this.checkPrivilegedGroupMemberships());

    // Check for stale accounts
    findings.push(...await this.checkStaleAccounts());

    // Check password policies
    findings.push(...await this.checkPasswordPolicies());

    // Check MFA enrollment
    findings.push(...await this.checkMFAEnrollment());

    // Check for suspicious sign-ins
    findings.push(...await this.checkSuspiciousSignIns());

    // Check conditional access policies
    findings.push(...await this.checkConditionalAccessPolicies());

    // Check for risky users
    findings.push(...await this.checkRiskyUsers());

    // Calculate summary
    const summary = this.calculateSummary(findings);

    const result: SecurityAssessmentResult = {
      timestamp: new Date().toISOString(),
      findings,
      summary
    };

    console.log(`Assessment complete. Total findings: ${findings.length}`);
    console.log(`Critical: ${summary.critical}, High: ${summary.high}, Medium: ${summary.medium}, Low: ${summary.low}, Info: ${summary.informational}`);

    return result;
  }

  async checkPrivilegedGroupMemberships(): Promise<SecurityFinding[]> {
    const findings: SecurityFinding[] = [];

    try {
      const privilegedGroups = [
        'Enterprise Admins',
        'Domain Admins',
        'Schema Admins',
        'Administrators',
        'Account Operators',
        'Backup Operators'
      ];

      for (const groupName of privilegedGroups) {
        const group = await this.findGroupByName(groupName);

        if (group) {
          const members = await this.graphClient
            .api(`/groups/${group.id}/members`)
            .select('id,displayName,userPrincipalName,mail')
            .top(999)
            .get();

          if (members.value && members.value.length > 0) {
            findings.push({
              severity: group.name.includes('Enterprise') || group.name.includes('Domain') ? 'Critical' : 'High',
              category: 'Privileged Access',
              title: `Large number of members in privileged group: ${groupName}`,
              description: `The privileged group "${groupName}" has ${members.value.length} members. This increases the attack surface and risk of privilege escalation.`,
              recommendation: 'Review group memberships regularly and implement least privilege principles. Consider removing unnecessary members.',
              affectedResources: members.value.map((m: any) => m.userPrincipalName || m.displayName)
            });
          }
        }
      }
    } catch (error: any) {
      console.error(`Error checking privileged groups: ${error.message}`);
    }

    return findings;
  }

  async checkStaleAccounts(): Promise<SecurityFinding[]> {
    const findings: SecurityFinding[] = [];

    try {
      const staleThreshold = 90; // days
      const thresholdDate = new Date();
      thresholdDate.setDate(thresholdDate.getDate() - staleThreshold);

      const users = await this.graphClient
        .api('/users')
        .filter(`accountEnabled eq true and signInActivity/lastSignInDateTime le ${thresholdDate.toISOString()}`)
        .select('id,displayName,userPrincipalName,signInActivity')
        .top(999)
        .get();

      if (users.value && users.value.length > 0) {
        findings.push({
          severity: 'Medium',
          category: 'Account Management',
          title: `Found ${users.value.length} potentially stale user accounts`,
          description: 'Users who haven\'t signed in for more than 90 days should be reviewed. Stale accounts can be exploited by attackers.',
          recommendation: 'Review and disable or delete accounts that are no longer needed. Implement a lifecycle policy for user accounts.',
          affectedResources: users.value.map((u: any) => u.userPrincipalName)
        });
      }
    } catch (error: any) {
      console.error(`Error checking stale accounts: ${error.message}`);
    }

    return findings;
  }

  async checkPasswordPolicies(): Promise<SecurityFinding[]> {
    const findings: SecurityFinding[] = [];

    try {
      const passwordPolicy = await this.graphClient
        .api('/domainSettings/passwordPolicy')
        .get();

      if (passwordPolicy.length === 0) {
        findings.push({
          severity: 'High',
          category: 'Password Policy',
          title: 'Weak or missing password policy',
          description: 'The directory does not have a strong password policy configured.',
          recommendation: 'Implement strong password policies including minimum length (12+), complexity requirements, and regular expiration.',
          affectedResources: ['Password Policy']
        });
      } else {
        const policy = passwordPolicy[0];

        if (policy.lockoutThreshold < 5) {
          findings.push({
            severity: 'Medium',
            category: 'Password Policy',
            title: 'Account lockout threshold is too permissive',
            description: `Current lockout threshold is ${policy.lockoutThreshold} attempts. This allows more brute force attempts.`,
            recommendation: 'Set lockout threshold to 5 or fewer attempts.',
            affectedResources: ['Password Policy']
          });
        }

        if (policy.lockoutDuration < 900) {
          findings.push({
            severity: 'Medium',
            category: 'Password Policy',
            title: 'Account lockout duration is too short',
            description: `Current lockout duration is ${policy.lockoutDuration} seconds. This may not be sufficient to prevent attacks.`,
            recommendation: 'Set lockout duration to at least 15 minutes (900 seconds).',
            affectedResources: ['Password Policy']
          });
        }
      }
    } catch (error: any) {
      console.error(`Error checking password policies: ${error.message}`);
    }

    return findings;
  }

  async checkMFAEnrollment(): Promise<SecurityFinding[]> {
    const findings: SecurityFinding[] = [];

    try {
      const users = await this.graphClient
        .api('/users')
        .filter('accountEnabled eq true')
        .select('id,displayName,userPrincipalName')
        .top(999)
        .get();

      let mfaEnrolled = 0;
      const nonMfaUsers: string[] = [];

      for (const user of users.value) {
        const authMethods = await this.graphClient
          .api(`/users/${user.id}/authentication/methods`)
          .get();

        const hasMfa = authMethods.value.some((m: any) =>
          m['@odata.type'] === '#microsoft.graph.passwordAuthenticationMethod' ||
          m['@odata.type'] === '#microsoft.graph.fido2AuthenticationMethod' ||
          m['@odata.type'] === '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod'
        );

        if (hasMfa) {
          mfaEnrolled++;
        } else {
          nonMfaUsers.push(user.userPrincipalName);
        }
      }

      const mfaPercentage = (mfaEnrolled / users.value.length) * 100;

      if (mfaPercentage < 80) {
        findings.push({
          severity: 'High',
          category: 'Authentication',
          title: `Low MFA enrollment rate: ${mfaPercentage.toFixed(1)}%`,
          description: `${nonMfaUsers.length} users do not have MFA enabled. This increases risk of credential compromise.`,
          recommendation: 'Enable MFA for all users. Consider implementing MFA as mandatory for privileged accounts.',
          affectedResources: nonMfaUsers
        });
      }
    } catch (error: any) {
      console.error(`Error checking MFA enrollment: ${error.message}`);
    }

    return findings;
  }

  async checkSuspiciousSignIns(): Promise<SecurityFinding[]> {
    const findings: SecurityFinding[] = [];

    try {
      const signIns = await this.graphClient
        .api('/auditLogs/signIns')
        .filter("riskEventTypes/riskLevel eq 'high'")
        .select('id,userPrincipalName,createdDateTime,riskEventTypes,location')
        .orderby('createdDateTime desc')
        .top(50)
        .get();

      if (signIns.value && signIns.value.length > 0) {
        findings.push({
          severity: 'Critical',
          category: 'Suspicious Activity',
          title: `Found ${signIns.value.length} high-risk sign-in attempts`,
          description: 'High-risk sign-in activities detected. These may indicate compromised credentials or attacks.',
          recommendation: 'Investigate these sign-ins immediately. Consider blocking suspicious IPs and resetting affected user passwords.',
          affectedResources: signIns.value.map((s: any) => `${s.userPrincipalName} (${s.createdDateTime})`)
        });
      }
    } catch (error: any) {
      console.error(`Error checking suspicious sign-ins: ${error.message}`);
    }

    return findings;
  }

  async checkConditionalAccessPolicies(): Promise<SecurityFinding[]> {
    const findings: SecurityFinding[] = [];

    try {
      const policies = await this.graphClient
        .api('/identity/conditionalAccess/policies')
        .select('id,displayName,state,conditions,grantControls')
        .get();

      const enabledPolicies = policies.value.filter((p: any) => p.state === 'enabled');

      if (enabledPolicies.length === 0) {
        findings.push({
          severity: 'Critical',
          category: 'Access Control',
          title: 'No conditional access policies enabled',
          description: 'Conditional Access is not configured. This leaves the organization vulnerable to unauthorized access.',
          recommendation: 'Implement Conditional Access policies to enforce MFA, location-based access, and device compliance.',
          affectedResources: ['Conditional Access']
        });
      } else {
        // Check for MFA requirement in privileged access
        const hasMfaForAdmins = enabledPolicies.some((p: any) =>
          p.conditions?.users?.includeRoles?.some((r: any) => r.id.includes('Admin')) &&
          p.grantControls?.builtInControls?.includes('mfa')
        );

        if (!hasMfaForAdmins) {
          findings.push({
            severity: 'High',
            category: 'Access Control',
            title: 'MFA not required for admin access',
            description: 'Conditional Access policies do not require MFA for administrator accounts.',
            recommendation: 'Create a Conditional Access policy requiring MFA for all privileged role assignments.',
            affectedResources: ['Conditional Access']
          });
        }
      }
    } catch (error: any) {
      console.error(`Error checking conditional access policies: ${error.message}`);
    }

    return findings;
  }

  async checkRiskyUsers(): Promise<SecurityFinding[]> {
    const findings: SecurityFinding[] = [];

    try {
      const riskyUsers = await this.graphClient
        .api('/identityProtection/riskyUsers')
        .filter('riskLevel eq \'high\' or riskLevel eq \'medium\'')
        .select('id,userPrincipalName,riskLevel,riskDetail')
        .top(50)
        .get();

      if (riskyUsers.value && riskyUsers.value.length > 0) {
        findings.push({
          severity: 'High',
          category: 'Identity Protection',
          title: `Found ${riskyUsers.value.length} risky user accounts`,
          description: 'Users flagged with medium or high risk levels. These may be compromised.',
          recommendation: 'Review risky users, force password reset if necessary, and investigate suspicious activity.',
          affectedResources: riskyUsers.value.map((u: any) => `${u.userPrincipalName} (${u.riskLevel})`)
        });
      }
    } catch (error: any) {
      console.error(`Error checking risky users: ${error.message}`);
    }

    return findings;
  }

  private async findGroupByName(groupName: string): Promise<any> {
    const groups = await this.graphClient
      .api('/groups')
      .filter(`displayName eq '${groupName}'`)
      .select('id,name')
      .get();

    return groups.value?.[0];
  }

  private calculateSummary(findings: SecurityFinding[]): any {
    return {
      critical: findings.filter(f => f.severity === 'Critical').length,
      high: findings.filter(f => f.severity === 'High').length,
      medium: findings.filter(f => f.severity === 'Medium').length,
      low: findings.filter(f => f.severity === 'Low').length,
      informational: findings.filter(f => f.severity === 'Informational').length
    };
  }
}

export function generateSecurityReport(assessment: SecurityAssessmentResult): string {
  let report = `
# Active Directory Security Assessment Report

**Generated:** ${assessment.timestamp}

## Executive Summary

| Severity | Count |
|-----------|-------|
| Critical  | ${assessment.summary.critical} |
| High      | ${assessment.summary.high} |
| Medium    | ${assessment.summary.medium} |
| Low       | ${assessment.summary.low} |
| Info      | ${assessment.summary.informational} |

## Detailed Findings

`;

  for (const finding of assessment.findings) {
    report += `
### ${finding.title}

**Severity:** ${finding.severity}  
**Category:** ${finding.category}

${finding.description}

**Affected Resources:**
${finding.affectedResources.map(r => `- ${r}`).join('\n')}

**Recommendation:** ${finding.recommendation}

---
`;
  }

  return report;
}
