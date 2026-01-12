import { ClientSecretCredential } from '@azure/identity';
import { Client } from '@microsoft/microsoft-graph-client';
import 'isomorphic-fetch';

export interface TeamConfig {
  displayName: string;
  description?: string;
  teamId?: string;
}

export interface TeamCreationResult {
  success: boolean;
  teamId?: string;
  errors?: string[];
}

export interface ChannelConfig {
  displayName: string;
  description?: string;
  isFavoriteByDefault?: boolean;
}

export interface TeamMemberConfig {
  userId: string;
  role: 'Owner' | 'Member' | 'Guest';
}

export class TeamsManager {
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

  async createTeam(config: TeamConfig): Promise<TeamCreationResult> {
    const result: TeamCreationResult = { success: false, errors: [] };

    try {
      if (!config.displayName) {
        throw new Error('Team display name is required');
      }

      const team = {
        template@odata.bind: 'https://graph.microsoft.com/v1.0/teamsTemplates(\'standard\')',
        displayName: config.displayName,
        description: config.description || '',
        'members@odata.bind': []
      };

      const response = await this.graphClient.api('/teams').post(team);

      result.success = true;
      result.teamId = response.id;

    } catch (error: any) {
      result.errors?.push(`Team creation failed: ${error.message}`);
    }

    return result;
  }

  async deleteTeam(teamId: string): Promise<boolean> {
    try {
      await this.graphClient.api(`/teams/${teamId}`).delete();
      return true;
    } catch (error: any) {
      console.error(`Failed to delete team: ${error.message}`);
      return false;
    }
  }

  async createChannel(teamId: string, config: ChannelConfig): Promise<string | null> {
    try {
      if (!config.displayName) {
        throw new Error('Channel display name is required');
      }

      const channel = {
        displayName: config.displayName,
        description: config.description || '',
        isFavoriteByDefault: config.isFavoriteByDefault ?? false
      };

      const response = await this.graphClient
        .api(`/teams/${teamId}/channels`)
        .post(channel);

      return response.id;
    } catch (error: any) {
      console.error(`Failed to create channel: ${error.message}`);
      return null;
    }
  }

  async addMember(teamId: string, member: TeamMemberConfig): Promise<boolean> {
    try {
      const teamMember = {
        '@odata.type': '#microsoft.graph.aadUserConversationMember',
        roles: [member.role],
        'user@odata.bind': `https://graph.microsoft.com/v1.0/users('${member.userId}')`
      };

      await this.graphClient
        .api(`/teams/${teamId}/members`)
        .post(teamMember);

      return true;
    } catch (error: any) {
      console.error(`Failed to add team member: ${error.message}`);
      return false;
    }
  }

  async removeMember(teamId: string, membershipId: string): Promise<boolean> {
    try {
      await this.graphClient
        .api(`/teams/${teamId}/members/${membershipId}`)
        .delete();

      return true;
    } catch (error: any) {
      console.error(`Failed to remove team member: ${error.message}`);
      return false;
    }
  }

  async listTeams(): Promise<any[]> {
    try {
      const response = await this.graphClient
        .api('/me/joinedTeams')
        .select('id,displayName,description,teamId')
        .get();

      return response.value || [];
    } catch (error: any) {
      console.error(`Failed to list teams: ${error.message}`);
      return [];
    }
  }

  async listChannels(teamId: string): Promise<any[]> {
    try {
      const response = await this.graphClient
        .api(`/teams/${teamId}/channels`)
        .select('id,displayName,description,createdDateTime')
        .get();

      return response.value || [];
    } catch (error: any) {
      console.error(`Failed to list channels: ${error.message}`);
      return [];
    }
  }

  async listMembers(teamId: string): Promise<any[]> {
    try {
      const response = await this.graphClient
        .api(`/teams/${teamId}/members`)
        .select('id,displayName,email,roles')
        .expand('user')
        .get();

      return response.value || [];
    } catch (error: any) {
      console.error(`Failed to list members: ${error.message}`);
      return [];
    }
  }

  async updateTeam(teamId: string, updates: Partial<TeamConfig>): Promise<boolean> {
    try {
      const updateData: any = {};

      if (updates.displayName) updateData.displayName = updates.displayName;
      if (updates.description !== undefined) updateData.description = updates.description;

      await this.graphClient
        .api(`/teams/${teamId}`)
        .patch(updateData);

      return true;
    } catch (error: any) {
      console.error(`Failed to update team: ${error.message}`);
      return false;
    }
  }

  async archiveTeam(teamId: string): Promise<boolean> {
    try {
      await this.graphClient
        .api(`/teams/${teamId}/archive`)
        .post({ shouldSetSpoSiteReadOnlyForMembers: true });

      return true;
    } catch (error: any) {
      console.error(`Failed to archive team: ${error.message}`);
      return false;
    }
  }

  async unarchiveTeam(teamId: string): Promise<boolean> {
    try {
      await this.graphClient
        .api(`/teams/${teamId}/unarchive`)
        .post();

      return true;
    } catch (error: any) {
      console.error(`Failed to unarchive team: ${error.message}`);
      return false;
    }
  }

  async createGroupChat(userIds: string[]): Promise<string | null> {
    try {
      const chat = {
        chatType: 'group',
        members: userIds.map(id => ({
          '@odata.type': '#microsoft.graph.aadUserConversationMember',
          roles: ['owner'],
          'user@odata.bind': `https://graph.microsoft.com/v1.0/users('${id}')`
        }))
      };

      const response = await this.graphClient
        .api('/chats')
        .post(chat);

      return response.id;
    } catch (error: any) {
      console.error(`Failed to create group chat: ${error.message}`);
      return null;
    }
  }

  async getTeamSettings(teamId: string): Promise<any> {
    try {
      const response = await this.graphClient
        .api(`/teams/${teamId}`)
        .select('id,displayName,description,guestSettings,memberSettings,messagingSettings,funSettings')
        .get();

      return response;
    } catch (error: any) {
      console.error(`Failed to get team settings: ${error.message}`);
      return null;
    }
  }

  async updateTeamSettings(teamId: string, settings: any): Promise<boolean> {
    try {
      await this.graphClient
        .api(`/teams/${teamId}`)
        .patch(settings);

      return true;
    } catch (error: any) {
      console.error(`Failed to update team settings: ${error.message}`);
      return false;
    }
  }
}
