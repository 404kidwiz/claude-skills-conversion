import { ClientSecretCredential, DefaultAzureCredential } from '@azure/identity';
import { Client } from '@microsoft/microsoft-graph-client';
import 'isomorphic-fetch';

export interface M365UserConfig {
  displayName: string;
  mailNickname: string;
  userPrincipalName: string;
  password: string;
  accountEnabled: boolean;
  usageLocation?: string;
  licenses?: string[];
}

export interface UserCreationResult {
  success: boolean;
  userId?: string;
  errors?: string[];
}

export class M365UserManager {
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

  async createUser(config: M365UserConfig): Promise<UserCreationResult> {
    const result: UserCreationResult = { success: false, errors: [] };

    try {
      if (!config.displayName || !config.userPrincipalName || !config.password) {
        throw new Error('displayName, userPrincipalName, and password are required');
      }

      const user = {
        accountEnabled: config.accountEnabled ?? true,
        displayName: config.displayName,
        mailNickname: config.mailNickname || config.userPrincipalName.split('@')[0],
        passwordProfile: {
          forceChangePasswordNextSignIn: true,
          password: config.password
        },
        usageLocation: config.usageLocation || 'US',
        userPrincipalName: config.userPrincipalName
      };

      const response = await this.graphClient.api('/users').post(user);

      if (response.id && config.licenses && config.licenses.length > 0) {
        await this.assignLicenses(response.id, config.licenses);
      }

      result.success = true;
      result.userId = response.id;

    } catch (error: any) {
      result.errors?.push(`User creation failed: ${error.message}`);
    }

    return result;
  }

  async deleteUser(userId: string): Promise<boolean> {
    try {
      await this.graphClient.api(`/users/${userId}`).delete();
      return true;
    } catch (error: any) {
      console.error(`Failed to delete user: ${error.message}`);
      return false;
    }
  }

  async assignLicenses(userId: string, licenseIds: string[]): Promise<boolean> {
    try {
      const licenseAssignment = {
        addLicenses: licenseIds.map(id => ({
          disabledPlans: [],
          skuId: id
        })),
        removeLicenses: []
      };

      await this.graphClient.api(`/users/${userId}/assignLicense`).post(licenseAssignment);
      return true;
    } catch (error: any) {
      console.error(`Failed to assign licenses: ${error.message}`);
      return false;
    }
  }

  async getUserByEmail(email: string): Promise<any> {
    try {
      const user = await this.graphClient
        .api(`/users/${email}`)
        .select('id,displayName,mail,userPrincipalName,accountEnabled')
        .get();

      return user;
    } catch (error: any) {
      console.error(`Failed to get user: ${error.message}`);
      return null;
    }
  }

  async listUsers(filter?: string): Promise<any[]> {
    try {
      let request = this.graphClient
        .api('/users')
        .select('id,displayName,mail,userPrincipalName,accountEnabled,createdDateTime')
        .top(999);

      if (filter) {
        request = request.filter(filter);
      }

      const response = await request.get();
      return response.value || [];
    } catch (error: any) {
      console.error(`Failed to list users: ${error.message}`);
      return [];
    }
  }

  async updateUser(userId: string, updates: Partial<M365UserConfig>): Promise<boolean> {
    try {
      const updateData: any = {};

      if (updates.displayName) updateData.displayName = updates.displayName;
      if (updates.accountEnabled !== undefined) updateData.accountEnabled = updates.accountEnabled;
      if (updates.usageLocation) updateData.usageLocation = updates.usageLocation;

      await this.graphClient.api(`/users/${userId}`).patch(updateData);
      return true;
    } catch (error: any) {
      console.error(`Failed to update user: ${error.message}`);
      return false;
    }
  }

  async resetPassword(userId: string, newPassword: string): Promise<boolean> {
    try {
      await this.graphClient.api(`/users/${userId}/changePassword`).post({
        currentPassword: newPassword,
        newPassword: newPassword
      });
      return true;
    } catch (error: any) {
      console.error(`Failed to reset password: ${error.message}`);
      return false;
    }
  }

  async blockUser(userId: string): Promise<boolean> {
    return this.updateUser(userId, { accountEnabled: false });
  }

  async unblockUser(userId: string): Promise<boolean> {
    return this.updateUser(userId, { accountEnabled: true });
  }
}

export function validateUserPrincipalName(upn: string): boolean {
  const upnPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return upnPattern.test(upn);
}

export function validatePassword(password: string): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }

  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number');
  }

  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

export async function bulkCreateUsers(
  userManager: M365UserManager,
  users: M365UserConfig[]
): Promise<{ successes: UserCreationResult[]; failures: UserCreationResult[] }> {
  const successes: UserCreationResult[] = [];
  const failures: UserCreationResult[] = [];

  for (const user of users) {
    const result = await userManager.createUser(user);

    if (result.success) {
      successes.push(result);
    } else {
      failures.push(result);
    }
  }

  return { successes, failures };
}
