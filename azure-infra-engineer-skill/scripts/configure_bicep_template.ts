import * as resources from '@azure/arm-resources';
import * as fs from 'fs/promises';
import { DefaultAzureCredential } from '@azure/identity';

export interface BicepDeploymentConfig {
  subscriptionId: string;
  resourceGroupName: string;
  deploymentName: string;
  templatePath: string;
  parameters?: Record<string, any>;
  location?: string;
}

export interface DeploymentResult {
  success: boolean;
  deploymentId?: string;
  outputs?: Record<string, any>;
  errors?: string[];
}

export async function deployBicepTemplate(config: BicepDeploymentConfig): Promise<DeploymentResult> {
  const result: DeploymentResult = { success: false, errors: [] };

  try {
    if (!config.subscriptionId || !config.resourceGroupName || !config.templatePath) {
      throw new Error('subscriptionId, resourceGroupName, and templatePath are required');
    }

    await fs.access(config.templatePath);

    const credential = new DefaultAzureCredential();
    const resourceClient = new resources.ResourceManagementClient(credential, config.subscriptionId);

    const templateContent = await fs.readFile(config.templatePath, 'utf-8');

    const deploymentParams: resources.Deployment = {
      properties: {
        template: JSON.parse(templateContent),
        parameters: config.parameters || {},
        mode: resources.DeploymentMode.Incremental
      },
      location: config.location
    };

    const poller = await resourceClient.deployments.beginCreateOrUpdateAndWait(
      config.resourceGroupName,
      config.deploymentName,
      deploymentParams
    );

    result.success = true;
    result.deploymentId = poller.id;
    result.outputs = poller.properties?.outputs;

  } catch (error: any) {
    if (error.code === 'ENOENT') {
      result.errors?.push(`Template file not found: ${config.templatePath}`);
    } else {
      result.errors?.push(`Bicep deployment failed: ${error.message}`);
    }
  }

  return result;
}

export async function validateDeployment(config: BicepDeploymentConfig): Promise<boolean> {
  try {
    if (!config.subscriptionId || !config.resourceGroupName || !config.templatePath) {
      throw new Error('Missing required configuration');
    }

    await fs.access(config.templatePath);

    const credential = new DefaultAzureCredential();
    const resourceClient = new resources.ResourceManagementClient(credential, config.subscriptionId);

    const templateContent = await fs.readFile(config.templatePath, 'utf-8');
    const template = JSON.parse(templateContent);

    const validateParams: resources.DeploymentsValidateOptionalParams = {
      properties: {
        template: template,
        parameters: config.parameters || {},
        mode: resources.DeploymentMode.Incremental
      }
    };

    await resourceClient.deployments.validate(
      config.resourceGroupName,
      config.deploymentName,
      validateParams
    );

    return true;

  } catch (error: any) {
    console.error(`Validation failed: ${error.message}`);
    return false;
  }
}

export async function whatIfDeployment(config: BicepDeploymentConfig): Promise<any> {
  const result: DeploymentResult = { success: false, errors: [] };

  try {
    const credential = new DefaultAzureCredential();
    const resourceClient = new resources.ResourceManagementClient(credential, config.subscriptionId);

    const templateContent = await fs.readFile(config.templatePath, 'utf-8');
    const template = JSON.parse(templateContent);

    const whatIfParams: resources.DeploymentsWhatIfOptionalParams = {
      properties: {
        template: template,
        parameters: config.parameters || {},
        mode: resources.DeploymentMode.Incremental
      }
    };

    const response = await resourceClient.deployments.beginCreateOrUpdateAndWait(
      config.resourceGroupName,
      config.deploymentName,
      whatIfParams as any
    );

    result.success = true;

  } catch (error: any) {
    result.errors?.push(`What-if operation failed: ${error.message}`);
  }

  return result;
}
