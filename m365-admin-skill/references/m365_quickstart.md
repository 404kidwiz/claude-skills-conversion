# Microsoft 365 Admin - Quick Start Guide

This guide helps you get started with the M365 admin skill's scripts and tools.

## Prerequisites

- Node.js 16+ installed
- Microsoft 365 tenant with Global Administrator access
- App registered in Azure AD with necessary permissions
- TypeScript installed globally

## Azure AD App Registration

1. **Create App Registration:**
   ```bash
   # Go to Azure Portal → App registrations → New registration
   # Name: M365 Admin Script
   # Supported account types: Accounts in this organizational directory only
   ```

2. **Add API Permissions:**
   - Microsoft Graph → User.ReadWrite.All
   - Microsoft Graph → Group.ReadWrite.All
   - Microsoft Graph → Team.Create
   - Microsoft Graph → TeamSettings.ReadWrite.All

3. **Generate Client Secret:**
   ```bash
   # Go to Certificates & secrets → New client secret
   # Copy the secret value (you won't see it again)
   ```

4. **Grant Admin Consent:**
   ```bash
   # Go to API permissions → Click Grant admin consent for your organization
   ```

## Installation

```bash
npm install @azure/identity @microsoft/microsoft-graph-client @azure/msal-node isomorphic-fetch
npm install -D typescript @types/node
```

## Authentication

The scripts use Azure AD app authentication:

```typescript
const userManager = new M365UserManager(
  'client-id',
  'client-secret',
  'tenant-id'
);
```

Or use environment variables:

```bash
export AZURE_CLIENT_ID='your-client-id'
export AZURE_CLIENT_SECRET='your-client-secret'
export AZURE_TENANT_ID='your-tenant-id'
```

## Quick Examples

### Managing Users

```typescript
import { M365UserManager } from './scripts/create_m365_users';

const userManager = new M365UserManager(
  'client-id',
  'client-secret',
  'tenant-id'
);

// Create a new user
const userResult = await userManager.createUser({
  displayName: 'John Doe',
  mailNickname: 'jdoe',
  userPrincipalName: 'jdoe@yourdomain.com',
  password: 'SecurePassword123!',
  accountEnabled: true,
  usageLocation: 'US',
  licenses: ['LICENSE-ID-HERE']
});

if (userResult.success) {
  console.log(`User created with ID: ${userResult.userId}`);
}

// List users
const users = await userManager.listUsers();
console.log(users.map(u => u.displayName));

// Block a user
await userManager.blockUser('user-id');

// Reset password
await userManager.resetPassword('user-id', 'NewPassword123!');
```

### Configuring Teams

```typescript
import { TeamsManager } from './scripts/configure_teams';

const teamsManager = new TeamsManager(
  'client-id',
  'client-secret',
  'tenant-id'
);

// Create a new team
const teamResult = await teamsManager.createTeam({
  displayName: 'Project Alpha Team',
  description: 'Team for Project Alpha development'
});

if (teamResult.success) {
  console.log(`Team created with ID: ${teamResult.teamId}`);

  // Create channels
  const channelId = await teamsManager.createChannel(teamResult.teamId!, {
    displayName: 'General',
    description: 'General discussions',
    isFavoriteByDefault: true
  });

  // Add members
  await teamsManager.addMember(teamResult.teamId!, {
    userId: 'user-id',
    role: 'Owner'
  });
}

// List all teams
const teams = await teamsManager.listTeams();
console.log(teams.map(t => t.displayName));

// Create group chat
const chatId = await teamsManager.createGroupChat(['user1-id', 'user2-id', 'user3-id']);
```

### Managing Exchange Online

```typescript
import { ExchangeManager } from './scripts/setup_exchange';

const exchangeManager = new ExchangeManager(
  'client-id',
  'client-secret',
  'tenant-id'
);

// Create mailbox for user
const mailboxResult = await exchangeManager.createMailbox('user-id');

// Configure auto-reply
await exchangeManager.configureAutoReply(
  'user-id',
  'Internal: I am out of office',
  'External: I am out of office',
  '2024-01-01T00:00:00Z',
  '2024-01-15T00:00:00Z'
);

// Create distribution group
await exchangeManager.createDistributionGroup({
  displayName: 'All Employees',
  mailNickname: 'all-employees',
  description: 'Distribution list for all employees',
  members: ['user-id-1', 'user-id-2']
});

// Get inbox messages
const messages = await exchangeManager.getInboxMessages('user-id', 20);
console.log(messages);

// Send email
await exchangeManager.sendMessage(
  'user-id',
  ['recipient@example.com'],
  'Subject',
  '<p>Email body in HTML</p>'
);

// Create calendar event
const eventId = await exchangeManager.createCalendarEvent('user-id', {
  subject: 'Team Meeting',
  body: 'Weekly team sync',
  start: '2024-01-15T10:00:00Z',
  end: '2024-01-15T11:00:00Z',
  attendees: ['attendee1@example.com', 'attendee2@example.com'],
  location: 'Conference Room A',
  isOnlineMeeting: true
});
```

## Common Patterns

### Bulk User Creation

```typescript
const users = [
  {
    displayName: 'User One',
    mailNickname: 'userone',
    userPrincipalName: 'user1@domain.com',
    password: 'Password123!',
    accountEnabled: true,
    usageLocation: 'US'
  },
  {
    displayName: 'User Two',
    mailNickname: 'usertwo',
    userPrincipalName: 'user2@domain.com',
    password: 'Password123!',
    accountEnabled: true,
    usageLocation: 'US'
  }
];

const { successes, failures } = await bulkCreateUsers(userManager, users);
console.log(`Created: ${successes.length}, Failed: ${failures.length}`);
```

### Team Onboarding Workflow

```typescript
async function onboardNewTeam(teamName: string, ownerIds: string[], memberIds: string[]) {
  // Create team
  const team = await teamsManager.createTeam({ displayName: teamName });

  if (team.success && team.teamId) {
    // Create standard channels
    await teamsManager.createChannel(team.teamId, {
      displayName: 'General',
      description: 'General discussions'
    });

    await teamsManager.createChannel(team.teamId, {
      displayName: 'Announcements',
      description: 'Important announcements'
    });

    await teamsManager.createChannel(team.teamId, {
      displayName: 'Documents',
      description: 'Shared documents'
    });

    // Add owner
    for (const ownerId of ownerIds) {
      await teamsManager.addMember(team.teamId, {
        userId: ownerId,
        role: 'Owner'
      });
    }

    // Add members
    for (const memberId of memberIds) {
      await teamsManager.addMember(team.teamId, {
        userId: memberId,
        role: 'Member'
      });
    }
  }
}
```

### User Offboarding Workflow

```typescript
async function offboardUser(userId: string) {
  // Block user account
  await userManager.blockUser(userId);

  // Reset password
  await userManager.resetPassword(userId, generateRandomPassword());

  // Remove from all Teams (would require listing teams)
  const teams = await teamsManager.listTeams();

  for (const team of teams) {
    const members = await teamsManager.listMembers(team.id);

    for (const member of members) {
      if (member.id === userId) {
        await teamsManager.removeMember(team.id, member.id);
      }
    }
  }

  // Remove from distribution groups (would require listing groups)
  const groups = await exchangeManager.getDistributionGroups();

  for (const group of groups) {
    await exchangeManager.removeMemberFromDistributionGroup(group.id, userId);
  }
}
```

## Best Practices

1. **Validate inputs** - Use built-in validation functions
2. **Handle errors gracefully** - Check result.success before proceeding
3. **Use least privilege** - Grant only necessary permissions to the app
4. **Log all operations** - Track user management for audit purposes
5. **Test in non-production** - Test scripts in a test tenant first
6. **Implement retry logic** - Add retries for transient failures
7. **Use environment variables** - Store credentials securely
8. **Monitor API limits** - Be aware of Graph API throttling limits

## Troubleshooting

### Authentication Failed

```
Error: Access token request failed
```

**Solutions:**
1. Verify client ID, client secret, and tenant ID are correct
2. Check if app registration is still active
3. Ensure admin consent has been granted
4. Verify API permissions are correct

### User Already Exists

```
Error: Request returned status code 400 with message: Another object with the same value for property userPrincipalName already exists
```

**Solutions:**
1. Check if user already exists using `getUserByEmail()`
2. Use `updateUser()` instead of creating a new user
3. Or delete the existing user first

### Permission Denied

```
Error: Access is denied. Check credentials and try again.
```

**Solutions:**
1. Verify app has necessary permissions
2. Grant admin consent for the permissions
3. Check if you're using the correct app registration

### Team Creation Failed

```
Error: Failed to create team
```

**Solutions:**
1. Verify team name doesn't already exist
2. Check if Graph API permissions are correct
3. Ensure Microsoft Teams license is assigned to users

### License Assignment Failed

```
Error: Insufficient licenses available
```

**Solutions:**
1. Check available licenses in Microsoft 365 admin center
2. Verify license SKU ID is correct
3. Purchase additional licenses if needed

## API Limits

Microsoft Graph API has throttling limits:

- **Requests per minute**: Up to 100 requests per app
- **Requests per 10 seconds**: Up to 15 requests per app
- **Concurrent requests**: Up to 10 requests

For bulk operations, implement batching and retry logic:

```typescript
async function bulkOperationWithRetry<T>(
  operation: () => Promise<T>,
  maxRetries = 3
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error: any) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 2000 * (i + 1)));
    }
  }
  throw new Error('Max retries exceeded');
}
```

## Security Considerations

1. **Never hardcode credentials** - Use environment variables or key vault
2. **Rotate client secrets regularly** - Update secrets every 90 days
3. **Use certificate-based auth** - More secure than client secrets for production
4. **Monitor audit logs** - Review Microsoft 365 audit logs regularly
5. **Implement conditional access** - Require MFA for admin operations
6. **Use privileged identity management** - Just-in-time admin access
7. **Regularly review permissions** - Remove unnecessary app permissions

## Additional Resources

- [Microsoft Graph API Documentation](https://docs.microsoft.com/graph/api)
- [Microsoft Graph SDK for TypeScript](https://github.com/microsoftgraph/msgraph-sdk-typescript)
- [Microsoft 365 Admin Center](https://admin.microsoft.com/)
- [Azure AD App Registration](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
- [Graph API Limits](https://docs.microsoft.com/graph/throttling)
