import * as monitor from '@azure/arm-monitor';
import * as resources from '@azure/arm-resources';
import { DefaultAzureCredential } from '@azure/identity';

export interface AlertRuleConfig {
  name: string;
  resourceGroupName: string;
  subscriptionId: string;
  targetResourceId: string;
  criteria: AlertCriteria;
  actionGroups?: string[];
}

export interface AlertCriteria {
  metricName: string;
  threshold: number;
  operator: 'GreaterThan' | 'LessThan' | 'GreaterThanOrEqual' | 'LessThanOrEqual';
  timeAggregation: 'Average' | 'Minimum' | 'Maximum' | 'Total';
  windowSize: string;
  evaluationFrequency: string;
}

export interface ActionGroupConfig {
  name: string;
  resourceGroupName: string;
  subscriptionId: string;
  location: string;
  emailReceivers?: EmailReceiver[];
  smsReceivers?: SmsReceiver[];
}

export interface EmailReceiver {
  name: string;
  emailAddress: string;
}

export interface SmsReceiver {
  name: string;
  countryCode: string;
  phoneNumber: string;
}

export async function createActionGroup(config: ActionGroupConfig): Promise<string | null> {
  try {
    if (!config.name || !config.resourceGroupName || !config.subscriptionId) {
      throw new Error('Action group name, resource group, and subscription ID are required');
    }

    const credential = new DefaultAzureCredential();
    const monitorClient = new monitor.MonitorManagementClient(credential, config.subscriptionId);

    const actionGroupParams: monitor.ActionGroupResource = {
      location: config.location,
      groupShortName: config.name.substring(0, 12),
      enabled: true,
      emailReceivers: config.emailReceivers?.map(e => ({
        name: e.name,
        emailAddress: e.emailAddress
      })),
      smsReceivers: config.smsReceivers?.map(s => ({
        name: s.name,
        countryCode: s.countryCode,
        phoneNumber: s.phoneNumber
      }))
    };

    const poller = await monitorClient.actionGroups.beginCreateOrUpdateAndWait(
      config.resourceGroupName,
      config.name,
      actionGroupParams
    );

    return poller.id;

  } catch (error: any) {
    console.error(`Failed to create action group: ${error.message}`);
    return null;
  }
}

export async function createMetricAlert(config: AlertRuleConfig): Promise<boolean> {
  try {
    if (!config.name || !config.targetResourceId || !config.criteria) {
      throw new Error('Alert name, target resource ID, and criteria are required');
    }

    const credential = new DefaultAzureCredential();
    const monitorClient = new monitor.MonitorManagementClient(credential, config.subscriptionId);

    const alertParams: monitor.MetricAlertResource = {
      location: 'global',
      description: `Alert for ${config.criteria.metricName}`,
      severity: 3,
      enabled: true,
      scopes: [config.targetResourceId],
      evaluationFrequency: { duration: config.criteria.evaluationFrequency },
      windowSize: { duration: config.criteria.windowSize },
      criteria: {
        'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria',
        allOf: [{
          threshold: config.criteria.threshold,
          name: `${config.criteria.metricName}_threshold`,
          metricName: config.criteria.metricName,
          metricNamespace: 'Microsoft.Compute/virtualMachines',
          dimensions: [],
          operator: config.criteria.operator,
          timeAggregation: config.criteria.timeAggregation,
          skipMetricValidation: false
        }]
      },
      actions: config.actionGroups?.map(ag => ({
        actionGroupId: ag
      }))
    };

    await monitorClient.metricAlerts.createOrUpdate(
      config.resourceGroupName,
      config.name,
      alertParams
    );

    return true;

  } catch (error: any) {
    console.error(`Failed to create metric alert: ${error.message}`);
    return false;
  }
}

export async function setupLogAnalytics(
  subscriptionId: string,
  resourceGroupName: string,
  workspaceName: string,
  location: string
): Promise<string | null> {
  try {
    const credential = new DefaultAzureCredential();
    const monitorClient = new monitor.MonitorManagementClient(credential, subscriptionId);

    const workspaceParams: monitor.Workspace = {
      location: location,
      sku: { name: 'PerGB2018' },
      retentionInDays: 30
    };

    const poller = await monitorClient.workspaces.beginCreateOrUpdateAndWait(
      resourceGroupName,
      workspaceName,
      workspaceParams
    );

    return poller.id;

  } catch (error: any) {
    console.error(`Failed to create Log Analytics workspace: ${error.message}`);
    return null;
  }
}

export async function enableDiagnostics(
  subscriptionId: string,
  resourceGroupName: string,
  resourceId: string,
  logAnalyticsWorkspaceId: string
): Promise<boolean> {
  try {
    const credential = new DefaultAzureCredential();
    const monitorClient = new monitor.MonitorManagementClient(credential, subscriptionId);

    const diagnosticSettings: monitor.DiagnosticSettingsResource = {
      location: 'global',
      logs: [
        { category: 'AllMetrics', enabled: true, retentionPolicy: { days: 30, enabled: true } }
      ],
      metrics: [
        { category: 'AllMetrics', enabled: true, retentionPolicy: { days: 30, enabled: true } }
      ],
      workspaceId: logAnalyticsWorkspaceId
    };

    await monitorClient.diagnosticSettings.createOrUpdate(
      resourceId,
      `${resourceGroupName}-diagnostics`,
      diagnosticSettings
    );

    return true;

  } catch (error: any) {
    console.error(`Failed to enable diagnostics: ${error.message}`);
    return false;
  }
}
