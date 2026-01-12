import { ClientSecretCredential } from '@azure/identity';
import { Client } from '@microsoft/microsoft-graph-client';
import 'isomorphic-fetch';

export interface MailboxConfig {
  displayName: string;
  email: string;
  userId: string;
}

export interface MailboxResult {
  success: boolean;
  mailboxId?: string;
  errors?: string[];
}

export interface DistributionGroupConfig {
  displayName: string;
  mailNickname: string;
  description?: string;
  members?: string[];
}

export interface CalendarEventConfig {
  subject: string;
  body?: string;
  start: string;
  end: string;
  attendees?: string[];
  location?: string;
  isOnlineMeeting?: boolean;
}

export class ExchangeManager {
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

  async createMailbox(userId: string): Promise<MailboxResult> {
    const result: MailboxResult = { success: false, errors: [] };

    try {
      if (!userId) {
        throw new Error('User ID is required');
      }

      const user = await this.graphClient
        .api(`/users/${userId}`)
        .select('id,mail,displayName')
        .get();

      if (!user.mail) {
        throw new Error('User does not have a mailbox');
      }

      result.success = true;
      result.mailboxId = user.id;

    } catch (error: any) {
      result.errors?.push(`Mailbox creation failed: ${error.message}`);
    }

    return result;
  }

  async getMailboxSettings(userId: string): Promise<any> {
    try {
      const settings = await this.graphClient
        .api(`/users/${userId}/mailboxSettings`)
        .get();

      return settings;
    } catch (error: any) {
      console.error(`Failed to get mailbox settings: ${error.message}`);
      return null;
    }
  }

  async updateMailboxSettings(userId: string, settings: any): Promise<boolean> {
    try {
      await this.graphClient
        .api(`/users/${userId}/mailboxSettings`)
        .patch(settings);

      return true;
    } catch (error: any) {
      console.error(`Failed to update mailbox settings: ${error.message}`);
      return false;
    }
  }

  async configureAutoReply(
    userId: string,
    internalReply: string,
    externalReply: string,
    startDate?: string,
    endDate?: string
  ): Promise<boolean> {
    try {
      const autoReplySettings: any = {
        status: 'Enabled',
        internalReplyMessage: internalReply,
        externalReplyMessage: externalReply
      };

      if (startDate && endDate) {
        autoReplySettings.scheduledStartDateTime = {
          dateTime: startDate,
          timeZone: 'UTC'
        };
        autoReplySettings.scheduledEndDateTime = {
          dateTime: endDate,
          timeZone: 'UTC'
        };
      }

      await this.graphClient
        .api(`/users/${userId}/mailboxSettings/automaticRepliesSetting`)
        .patch(autoReplySettings);

      return true;
    } catch (error: any) {
      console.error(`Failed to configure auto-reply: ${error.message}`);
      return false;
    }
  }

  async createDistributionGroup(config: DistributionGroupConfig): Promise<boolean> {
    try {
      const group = {
        displayName: config.displayName,
        mailNickname: config.mailNickname,
        description: config.description || '',
        mailEnabled: true,
        securityEnabled: false,
        'members@odata.bind': config.members?.map(id =>
          `https://graph.microsoft.com/v1.0/users('${id}')`
        ) || []
      };

      await this.graphClient.api('/groups').post(group);
      return true;
    } catch (error: any) {
      console.error(`Failed to create distribution group: ${error.message}`);
      return false;
    }
  }

  async addMemberToDistributionGroup(groupId: string, userId: string): Promise<boolean> {
    try {
      await this.graphClient
        .api(`/groups/${groupId}/members/$ref`)
        .post({
          '@odata.id': `https://graph.microsoft.com/v1.0/users('${userId}')`
        });

      return true;
    } catch (error: any) {
      console.error(`Failed to add member to group: ${error.message}`);
      return false;
    }
  }

  async removeMemberFromDistributionGroup(groupId: string, userId: string): Promise<boolean> {
    try {
      await this.graphClient
        .api(`/groups/${groupId}/members/${userId}/$ref`)
        .delete();

      return true;
    } catch (error: any) {
      console.error(`Failed to remove member from group: ${error.message}`);
      return false;
    }
  }

  async getDistributionGroups(): Promise<any[]> {
    try {
      const response = await this.graphClient
        .api('/groups')
        .filter("mailEnabled eq true and securityEnabled eq false")
        .select('id,displayName,mail,description')
        .get();

      return response.value || [];
    } catch (error: any) {
      console.error(`Failed to get distribution groups: ${error.message}`);
      return [];
    }
  }

  async createCalendarEvent(userId: string, event: CalendarEventConfig): Promise<string | null> {
    try {
      const eventBody = {
        subject: event.subject,
        body: {
          contentType: 'HTML',
          content: event.body || ''
        },
        start: {
          dateTime: event.start,
          timeZone: 'UTC'
        },
        end: {
          dateTime: event.end,
          timeZone: 'UTC'
        },
        location: event.location ? {
          displayName: event.location
        } : undefined,
        attendees: event.attendees?.map(email => ({
          emailAddress: {
            address: email
          },
          type: 'required'
        })),
        isOnlineMeeting: event.isOnlineMeeting ?? false
      };

      const response = await this.graphClient
        .api(`/users/${userId}/calendar/events`)
        .post(eventBody);

      return response.id;
    } catch (error: any) {
      console.error(`Failed to create calendar event: ${error.message}`);
      return null;
    }
  }

  async getCalendarEvents(userId: string, startDate: string, endDate: string): Promise<any[]> {
    try {
      const response = await this.graphClient
        .api(`/users/${userId}/calendar/calendarView`)
        .query({
          startDateTime: startDate,
          endDateTime: endDate
        })
        .select('id,subject,start,end,location,attendees')
        .orderby('start/dateTime')
        .get();

      return response.value || [];
    } catch (error: any) {
      console.error(`Failed to get calendar events: ${error.message}`);
      return [];
    }
  }

  async getInboxMessages(userId: string, limit: number = 50): Promise<any[]> {
    try {
      const response = await this.graphClient
        .api(`/users/${userId}/mailFolders/Inbox/messages`)
        .select('id,subject,from,receivedDateTime,isRead,hasAttachments')
        .top(limit)
        .orderby('receivedDateTime desc')
        .get();

      return response.value || [];
    } catch (error: any) {
      console.error(`Failed to get inbox messages: ${error.message}`);
      return [];
    }
  }

  async sendMessage(userId: string, to: string[], subject: string, body: string): Promise<boolean> {
    try {
      const message = {
        subject: subject,
        body: {
          contentType: 'HTML',
          content: body
        },
        toRecipients: to.map(email => ({
          emailAddress: {
            address: email
          }
        }))
      };

      await this.graphClient
        .api(`/users/${userId}/sendMail`)
        .post({ message: message });

      return true;
    } catch (error: any) {
      console.error(`Failed to send message: ${error.message}`);
      return false;
    }
  }

  async forwardMessage(userId: string, messageId: string, to: string[]): Promise<boolean> {
    try {
      await this.graphClient
        .api(`/users/${userId}/messages/${messageId}/forward`)
        .post({
          toRecipients: to.map(email => ({
            emailAddress: {
              address: email
            }
          }))
        });

      return true;
    } catch (error: any) {
      console.error(`Failed to forward message: ${error.message}`);
      return false;
    }
  }

  async deleteMessage(userId: string, messageId: string): Promise<boolean> {
    try {
      await this.graphClient
        .api(`/users/${userId}/messages/${messageId}`)
        .delete();

      return true;
    } catch (error: any) {
      console.error(`Failed to delete message: ${error.message}`);
      return false;
    }
  }
}
