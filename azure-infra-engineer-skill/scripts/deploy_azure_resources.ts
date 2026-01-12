import * as azure from '@azure/arm-resources';
import * as network from '@azure/arm-network';
import { DefaultAzureCredential } from '@azure/identity';

export interface VNetConfig {
  name: string;
  addressSpace: string[];
  subnets: SubnetConfig[];
  location: string;
  resourceGroupName: string;
}

export interface SubnetConfig {
  name: string;
  addressPrefix: string;
  nsgRules?: NSGRule[];
}

export interface NSGRule {
  name: string;
  priority: number;
  direction: 'Inbound' | 'Outbound';
  access: 'Allow' | 'Deny';
  protocol: 'Tcp' | 'Udp' | 'Icmp' | '*';
  sourceAddressPrefix: string;
  sourcePortRange: string;
  destinationAddressPrefix: string;
  destinationPortRange: string;
}

export interface DeploymentResult {
  success: boolean;
  vnetId?: string;
  subnets?: string[];
  errors?: string[];
}

export async function deployVNet(config: VNetConfig): Promise<DeploymentResult> {
  const result: DeploymentResult = { success: false, errors: [] };

  try {
    if (!config.name || !config.addressSpace || config.addressSpace.length === 0) {
      throw new Error('Invalid VNet configuration: name and addressSpace are required');
    }

    if (!config.resourceGroupName) {
      throw new Error('resourceGroupName is required');
    }

    const credential = new DefaultAzureCredential();
    const networkClient = new network.NetworkManagementClient(credential, config.subscriptionId);

    const vnetParams: network.VirtualNetwork = {
      location: config.location,
      addressSpace: { addressPrefixes: config.addressSpace },
      subnets: config.subnets.map(s => ({
        name: s.name,
        addressPrefix: s.addressPrefix
      }))
    };

    const poller = await networkClient.virtualNetworks.beginCreateOrUpdateAndWait(
      config.resourceGroupName,
      config.name,
      vnetParams
    );

    result.success = true;
    result.vnetId = poller.id;
    result.subnets = config.subnets.map(s => s.name);

  } catch (error: any) {
    result.errors?.push(`VNet deployment failed: ${error.message}`);
  }

  return result;
}

export async function deployNSG(config: NSGConfig): Promise<DeploymentResult> {
  const result: DeploymentResult = { success: false, errors: [] };

  try {
    if (!config.name || !config.resourceGroupName) {
      throw new Error('NSG name and resource group are required');
    }

    const credential = new DefaultAzureCredential();
    const networkClient = new network.NetworkManagementClient(credential, config.subscriptionId);

    const nsgParams: network.NetworkSecurityGroup = {
      location: config.location,
      securityRules: config.rules.map(r => ({
        name: r.name,
        priority: r.priority,
        direction: r.direction,
        access: r.access,
        protocol: r.protocol,
        sourceAddressPrefix: r.sourceAddressPrefix,
        sourcePortRange: r.sourcePortRange,
        destinationAddressPrefix: r.destinationAddressPrefix,
        destinationPortRange: r.destinationPortRange
      }))
    };

    const poller = await networkClient.networkSecurityGroups.beginCreateOrUpdateAndWait(
      config.resourceGroupName,
      config.name,
      nsgParams
    );

    result.success = true;
    result.vnetId = poller.id;

  } catch (error: any) {
    result.errors?.push(`NSG deployment failed: ${error.message}`);
  }

  return result;
}

export interface NSGConfig {
  subscriptionId: string;
  name: string;
  location: string;
  resourceGroupName: string;
  rules: NSGRule[];
}

export async function validateAddressPrefix(addressPrefix: string): boolean {
  const cidrPattern = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\/(\d{1,2})$/;
  const match = addressPrefix.match(cidrPattern);

  if (!match) return false;

  const [, octet1, octet2, octet3, octet4, prefix] = match.map(Number);

  if (octet1 > 255 || octet2 > 255 || octet3 > 255 || octet4 > 255) return false;
  if (prefix < 0 || prefix > 32) return false;

  return true;
}
