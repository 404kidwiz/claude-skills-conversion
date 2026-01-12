# Microsoft 365 Administration Patterns

Common patterns and best practices for Microsoft 365 administration using TypeScript and Microsoft Graph API.

## User Management Patterns

### User Lifecycle Management

```typescript
interface UserLifecycleState {
  onboarding: UserOnboardingConfig;
  offboarding: UserOffboardingConfig;
  lifecycle: UserLifecycleConfig;
}

interface UserOnboardingConfig {
  assignLicenses: string[];
  addToGroups: string[];
  sendWelcomeEmail: boolean;
  createTeamsMembership: boolean;
}

async function onboardUser(
  userManager: M365UserManager,
  teamsManager: TeamsManager,
  exchangeManager: ExchangeManager,
  userConfig: M365UserConfig,
  onboardingConfig: UserOnboardingConfig
): Promise<boolean> {
  try {
    // Create user
    const userResult = await userManager.createUser(userConfig);

    if (!userResult.success || !userResult.userId) {
      console.error('Failed to create user');
      return false;
    }

    const userId = userResult.userId;

    // Assign licenses
    if (onboardingConfig.assignLicenses.length > 0) {
      await userManager.assignLicenses(userId, onboardingConfig.assignLicenses);
    }

    // Add to groups
    for (const groupId of onboardingConfig.addToGroups) {
      await exchangeManager.addMemberToDistributionGroup(groupId, userId);
    }

    // Create Teams membership
    if (onboardingConfig.createTeamsMembership) {
      const teamName = `${userConfig.displayName}'s Team`;
      const teamResult = await teamsManager.createTeam({
        displayName: teamName,
        description: `Personal team for ${userConfig.displayName}`
      });

      if (teamResult.success && teamResult.teamId) {
        await teamsManager.addMember(teamResult.teamId, {
          userId: userId,
          role: 'Owner'
        });
      }
    }

    // Send welcome email
    if (onboardingConfig.sendWelcomeEmail) {
      await sendWelcomeEmail(userManager, exchangeManager, userId);
    }

    console.log(`User ${userConfig.displayName} onboarded successfully`);
    return true;
  } catch (error: any) {
    console.error(`Onboarding failed: ${error.message}`);
    return false;
  }
}
```

### Bulk User Operations

```typescript
async function bulkUserOperation(
  userManager: M365UserManager,
  users: M365UserConfig[],
  operation: 'create' | 'update' | 'delete',
  concurrencyLimit: number = 5
): Promise<{ succeeded: number; failed: number; errors: string[] }> {
  let succeeded = 0;
  let failed = 0;
  const errors: string[] = [];

  // Process users in batches
  for (let i = 0; i < users.length; i += concurrencyLimit) {
    const batch = users.slice(i, i + concurrencyLimit);

    const batchPromises = batch.map(async (user) => {
      try {
        let result;

        switch (operation) {
          case 'create':
            result = await userManager.createUser(user);
            break;
          case 'update':
            result = await userManager.updateUser(user.userPrincipalName, user);
            break;
          case 'delete':
            result = await userManager.deleteUser(user.userPrincipalName);
            break;
        }

        if (result.success) {
          succeeded++;
        } else {
          failed++;
          errors.push(`User ${user.userPrincipalName}: ${result.errors?.join(', ')}`);
        }
      } catch (error: any) {
        failed++;
        errors.push(`User ${user.userPrincipalName}: ${error.message}`);
      }
    });

    await Promise.all(batchPromises);

    // Add delay between batches to respect API limits
    if (i + concurrencyLimit < users.length) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  return { succeeded, failed, errors };
}
```

### Guest User Management

```typescript
async function inviteGuest(
  userManager: M365UserManager,
  email: string,
  redirectUrl: string
): Promise<boolean> {
  try {
    const guestInvitation = {
      invitedUserEmailAddress: email,
      sendInvitationMessage: true,
      inviteRedirectUrl: redirectUrl
    };

    await userManager.graphClient
      .api('/invitations')
      .post(guestInvitation);

    console.log(`Guest invitation sent to ${email}`);
    return true;
  } catch (error: any) {
    console.error(`Failed to invite guest: ${error.message}`);
    return false;
  }
}

async function manageGuestAccess(
  userManager: M365UserManager,
  email: string,
  groups: string[],
  action: 'add' | 'remove'
): Promise<boolean> {
  try {
    const guest = await userManager.getUserByEmail(email);

    if (!guest) {
      console.error(`Guest ${email} not found`);
      return false;
    }

    for (const groupId of groups) {
      if (action === 'add') {
        await exchangeManager.addMemberToDistributionGroup(groupId, guest.id);
      } else {
        await exchangeManager.removeMemberFromDistributionGroup(groupId, guest.id);
      }
    }

    return true;
  } catch (error: any) {
    console.error(`Failed to manage guest access: ${error.message}`);
    return false;
  }
}
```

## Teams Administration Patterns

### Team Template System

```typescript
interface TeamTemplate {
  name: string;
  description: string;
  channels: ChannelTemplate[];
  apps: string[];
  policies: TeamPolicies;
}

interface ChannelTemplate {
  name: string;
  description?: string;
  isFavorite: boolean;
}

interface TeamPolicies {
  allowCreateUpdateRemoveChannels: boolean;
  allowCreateUpdateRemoveConnectors: boolean;
  allowAddRemoveApps: boolean;
}

const teamTemplates: Record<string, TeamTemplate> = {
  'project-team': {
    name: 'Project Team',
    description: 'Standard project team configuration',
    channels: [
      { name: 'General', description: 'General discussions', isFavorite: true },
      { name: 'Announcements', description: 'Project announcements', isFavorite: true },
      { name: 'Development', description: 'Development discussions', isFavorite: false },
      { name: 'Testing', description: 'Testing discussions', isFavorite: false },
      { name: 'Documentation', description: 'Project documentation', isFavorite: false }
    ],
    apps: ['planner', 'onenote', 'tabs'],
    policies: {
      allowCreateUpdateRemoveChannels: true,
      allowCreateUpdateRemoveConnectors: false,
      allowAddRemoveApps: false
    }
  },
  'department-team': {
    name: 'Department Team',
    description: 'Standard department team configuration',
    channels: [
      { name: 'General', description: 'General discussions', isFavorite: true },
      { name: 'Announcements', description: 'Department announcements', isFavorite: true },
      { name: 'HR', description: 'HR communications', isFavorite: false },
      { name: 'Events', description: 'Department events', isFavorite: false }
    ],
    apps: ['planner', 'forms', 'tabs'],
    policies: {
      allowCreateUpdateRemoveChannels: true,
      allowCreateUpdateRemoveConnectors: true,
      allowAddRemoveApps: false
    }
  }
};

async function createTeamFromTemplate(
  teamsManager: TeamsManager,
  templateKey: string,
  teamName: string
): Promise<string | null> {
  const template = teamTemplates[templateKey];

  if (!template) {
    console.error(`Template ${templateKey} not found`);
    return null;
  }

  // Create team
  const teamResult = await teamsManager.createTeam({
    displayName: teamName,
    description: template.description
  });

  if (!teamResult.success || !teamResult.teamId) {
    return null;
  }

  const teamId = teamResult.teamId;

  // Create channels from template
  for (const channel of template.channels) {
    await teamsManager.createChannel(teamId, {
      displayName: channel.name,
      description: channel.description,
      isFavoriteByDefault: channel.isFavorite
    });
  }

  // Apply policies
  await teamsManager.updateTeamSettings(teamId, {
    memberSettings: {
      allowCreateUpdateRemoveChannels: template.policies.allowCreateUpdateRemoveChannels,
      allowCreateUpdateRemoveConnectors: template.policies.allowCreateUpdateRemoveConnectors,
      allowAddRemoveApps: template.policies.allowAddRemoveApps
    }
  });

  return teamId;
}
```

### Team Hierarchy Management

```typescript
interface TeamHierarchy {
  parent: string;
  children: string[];
  sharedChannels: string[];
}

async function createTeamHierarchy(
  teamsManager: TeamsManager,
  hierarchy: TeamHierarchy
): Promise<boolean> {
  try {
    // Create parent team
    const parentResult = await teamsManager.createTeam({
      displayName: hierarchy.parent,
      description: 'Parent team'
    });

    if (!parentResult.success || !parentResult.teamId) {
      return false;
    }

    const parentTeamId = parentResult.teamId;

    // Create child teams
    const childTeamIds: string[] = [];

    for (const child of hierarchy.children) {
      const childResult = await teamsManager.createTeam({
        displayName: child,
        description: `Child team of ${hierarchy.parent}`
      });

      if (childResult.success && childResult.teamId) {
        childTeamIds.push(childResult.teamId);
      }
    }

    // Create shared channels in parent team
    for (const sharedChannel of hierarchy.sharedChannels) {
      const channelId = await teamsManager.createChannel(parentTeamId, {
        displayName: sharedChannel,
        description: 'Shared channel with child teams',
        isFavoriteByDefault: false
      });

      // Share channel with child teams
      if (channelId) {
        for (const childTeamId of childTeamIds) {
          // Note: Shared channels require specific Graph API calls
          // This is a simplified example
          console.log(`Sharing channel ${sharedChannel} with child team`);
        }
      }
    }

    return true;
  } catch (error: any) {
    console.error(`Failed to create team hierarchy: ${error.message}`);
    return false;
  }
}
```

## Exchange Online Patterns

### Email Automation Patterns

```typescript
async function sendBulkEmail(
  exchangeManager: ExchangeManager,
  senderUserId: string,
  recipients: string[],
  subject: string,
  body: string,
  batchSize: number = 10,
  delayBetweenBatches: number = 2000
): Promise<{ sent: number; failed: number; errors: string[] }> {
  let sent = 0;
  let failed = 0;
  const errors: string[] = [];

  for (let i = 0; i < recipients.length; i += batchSize) {
    const batch = recipients.slice(i, i + batchSize);

    for (const recipient of batch) {
      try {
        await exchangeManager.sendMessage(senderUserId, [recipient], subject, body);
        sent++;
      } catch (error: any) {
        failed++;
        errors.push(`Failed to send to ${recipient}: ${error.message}`);
      }
    }

    // Delay between batches
    if (i + batchSize < recipients.length) {
      await new Promise(resolve => setTimeout(resolve, delayBetweenBatches));
    }
  }

  return { sent, failed, errors };
}
```

### Calendar Management

```typescript
async function scheduleMeeting(
  exchangeManager: ExchangeManager,
  organizerId: string,
  attendees: string[],
  subject: string,
  duration: number,
  startAfter: Date,
  preferredTimes: string[]
): Promise<Date | null> {
  // Find common available time slots
  const availableSlots = await findAvailableTimeSlots(
    exchangeManager,
    organizerId,
    attendees,
    startAfter,
    preferredTimes
  );

  if (availableSlots.length === 0) {
    console.error('No available time slots found');
    return null;
  }

  // Schedule meeting at first available slot
  const slot = availableSlots[0];
  const meetingStart = new Date(slot.start);
  const meetingEnd = new Date(meetingStart.getTime() + duration * 60000);

  const eventId = await exchangeManager.createCalendarEvent(organizerId, {
    subject: subject,
    start: meetingStart.toISOString(),
    end: meetingEnd.toISOString(),
    attendees: attendees,
    isOnlineMeeting: true
  });

  if (eventId) {
    return meetingStart;
  }

  return null;
}

async function findAvailableTimeSlots(
  exchangeManager: ExchangeManager,
  organizerId: string,
  attendees: string[],
  startDate: Date,
  preferredTimes: string[]
): Promise<Array<{ start: string; end: string }>> {
  const slots: Array<{ start: string; end: string }> = [];

  for (const time of preferredTimes) {
    // Check each attendee's calendar for this time slot
    let isAvailable = true;

    const [hours, minutes] = time.split(':').map(Number);
    const slotStart = new Date(startDate);
    slotStart.setHours(hours, minutes, 0, 0);

    const slotEnd = new Date(slotStart.getTime() + 60 * 60000); // 1 hour

    for (const attendee of attendees) {
      const events = await exchangeManager.getCalendarEvents(
        attendee,
        slotStart.toISOString(),
        slotEnd.toISOString()
      );

      if (events.length > 0) {
        isAvailable = false;
        break;
      }
    }

    if (isAvailable) {
      slots.push({
        start: slotStart.toISOString(),
        end: slotEnd.toISOString()
      });
    }
  }

  return slots;
}
```

## Security and Compliance Patterns

### Conditional Access Management

```typescript
async function configureConditionalAccess(
  accessToken: string,
  policyConfig: {
    name: string;
    conditions: any;
    grantControls: any;
    sessionControls: any;
  }
): Promise<boolean> {
  try {
    const policy = {
      displayName: policyConfig.name,
      state: 'enabled',
      conditions: policyConfig.conditions,
      grantControls: {
        operator: 'OR',
        builtInControls: policyConfig.grantControls
      },
      sessionControls: policyConfig.sessionControls
    };

    const response = await fetch(
      'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(policy)
      }
    );

    return response.ok;
  } catch (error: any) {
    console.error(`Failed to configure conditional access: ${error.message}`);
    return false;
  }
}
```

### Audit Log Monitoring

```typescript
async function monitorAuditLogs(
  userManager: M365UserManager,
  eventType: string,
  callback: (logEntry: any) => void,
  pollingInterval: number = 60000
): Promise<void> {
  let lastCheckTime = new Date();

  while (true) {
    try {
      const logs = await userManager.graphClient
        .api('/auditLogs/directoryAudits')
        .filter(`activityDateTime ge ${lastCheckTime.toISOString()}`)
        .filter(`activityDisplayName eq '${eventType}'`)
        .orderby('activityDateTime desc')
        .get();

      for (const log of logs.value) {
        callback(log);
      }

      lastCheckTime = new Date();

      await new Promise(resolve => setTimeout(resolve, pollingInterval));
    } catch (error: any) {
      console.error(`Audit log monitoring error: ${error.message}`);
      await new Promise(resolve => setTimeout(resolve, pollingInterval));
    }
  }
}
```

## License Management

```typescript
interface LicenseAllocation {
  skuId: string;
  allocated: number;
  available: number;
}

async function getLicenseAvailability(
  userManager: M365UserManager
): Promise<Record<string, LicenseAllocation>> {
  try {
    const subscribedSku = await userManager.graphClient
      .api('/subscribedSkus')
      .select('skuId,prepaidUnits')
      .get();

    const availability: Record<string, LicenseAllocation> = {};

    for (const sku of subscribedSku.value) {
      availability[sku.skuId] = {
        skuId: sku.skuId,
        allocated: sku.prepaidUnits.consumed,
        available: sku.prepaidUnits.enabled - sku.prepaidUnits.consumed
      };
    }

    return availability;
  } catch (error: any) {
    console.error(`Failed to get license availability: ${error.message}`);
    return {};
  }
}

async function assignLicenseWithAvailabilityCheck(
  userManager: M365UserManager,
  userId: string,
  licenseSkuId: string
): Promise<boolean> {
  // Check availability
  const availability = await getLicenseAvailability(userManager);

  const licenseInfo = availability[licenseSkuId];

  if (!licenseInfo || licenseInfo.available <= 0) {
    console.error(`No available licenses for SKU ${licenseSkuId}`);
    return false;
  }

  // Assign license
  return await userManager.assignLicenses(userId, [licenseSkuId]);
}
```

## Backup and Recovery

```typescript
async function backupTeam(
  teamsManager: TeamsManager,
  teamId: string
): Promise<any> {
  try {
    const backup = {
      team: await teamsManager.getTeamSettings(teamId),
      channels: await teamsManager.listChannels(teamId),
      members: await teamsManager.listMembers(teamId),
      timestamp: new Date().toISOString()
    };

    return backup;
  } catch (error: any) {
    console.error(`Failed to backup team: ${error.message}`);
    return null;
  }
}

async function restoreTeam(
  teamsManager: TeamsManager,
  backup: any
): Promise<boolean> {
  try {
    // Create team
    const teamResult = await teamsManager.createTeam({
      displayName: backup.team.displayName,
      description: backup.team.description
    });

    if (!teamResult.success || !teamResult.teamId) {
      return false;
    }

    // Create channels
    for (const channel of backup.channels) {
      await teamsManager.createChannel(teamResult.teamId, {
        displayName: channel.displayName,
        description: channel.description,
        isFavoriteByDefault: channel.isFavoriteByDefault
      });
    }

    // Add members
    for (const member of backup.members) {
      await teamsManager.addMember(teamResult.teamId, {
        userId: member.id,
        role: member.roles[0] || 'Member'
      });
    }

    return true;
  } catch (error: any) {
    console.error(`Failed to restore team: ${error.message}`);
    return false;
  }
}
```
