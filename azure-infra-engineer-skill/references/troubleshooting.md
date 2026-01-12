# Azure Infrastructure Troubleshooting

Common issues and solutions for Azure infrastructure deployments and management.

## Authentication Issues

### DefaultAzureCredential Authentication Failed

**Symptoms:**
```
Error: DefaultAzureCredential: Authentication failed. Attempted 4 credential types
```

**Solutions:**

1. **Authenticate with Azure CLI:**
   ```bash
   az login
   az account set --subscription <subscription-id>
   ```

2. **Set environment variables for Service Principal:**
   ```bash
   export AZURE_CLIENT_ID=<client-id>
   export AZURE_CLIENT_SECRET=<client-secret>
   export AZURE_TENANT_ID=<tenant-id>
   ```

3. **Check token expiration:**
   ```bash
   az account get-access-token
   ```

4. **Verify subscription access:**
   ```bash
   az account list --output table
   ```

### Insufficient Permissions

**Symptoms:**
```
Error: AuthorizationFailed: The client 'xxx' with object id 'yyy' does not have authorization to perform action
```

**Solutions:**

1. **Check current role assignments:**
   ```bash
   az role assignment list --assignee $(az ad signed-in-user show --query objectId -o tsv)
   ```

2. **Assign Contributor role:**
   ```bash
   az role assignment create --assignee <user-or-service-principal> \
     --role Contributor \
     --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>
   ```

3. **Use Azure Portal to verify permissions:**
   - Navigate to Resource Group → Access Control (IAM)
   - Check if you have necessary roles

## Deployment Issues

### Bicep Template Validation Failed

**Symptoms:**
```
Error: Template validation failed: The template is not valid
```

**Solutions:**

1. **Compile Bicep to JSON for better error messages:**
   ```bash
   az bicep build main.bicep
   ```

2. **Check for syntax errors:**
   - Verify all parameters are defined
   - Check for missing commas
   - Ensure proper indentation

3. **Validate parameters:**
   ```typescript
   if (!config.parameters || Object.keys(config.parameters).length === 0) {
     throw new Error('Parameters object is empty');
   }
   ```

4. **Use what-if to preview changes:**
   ```typescript
   await whatIfDeployment(config);
   ```

### Deployment Timeout

**Symptoms:**
```
Error: Deployment operation timed out after 30 minutes
```

**Solutions:**

1. **Increase timeout in poller configuration:**
   ```typescript
   const poller = await client.virtualNetworks.beginCreateOrUpdateAndWait(
     resourceGroupName,
     vnetName,
     params,
     {
       abortSignal: AbortSignal.timeout(60 * 60 * 1000) // 1 hour timeout
     }
   );
   ```

2. **Check Azure service health:**
   ```bash
   az service-health list-events --output table
   ```

3. **Verify network connectivity:**
   ```bash
   ping login.microsoftonline.com
   ```

4. **Review deployment status:**
   ```bash
   az deployment group show \
     --resource-group <rg-name> \
     --name <deployment-name>
   ```

### Resource Already Exists Error

**Symptoms:**
```
Error: The Resource 'Microsoft.Network/virtualNetworks/my-vnet' under resource group 'my-rg' already exists
```

**Solutions:**

1. **Check if resource exists:**
   ```bash
   az resource show \
     --resource-group <rg-name> \
     --name <resource-name> \
     --resource-type Microsoft.Network/virtualNetworks
   ```

2. **Update existing resource instead of creating new:**
   ```typescript
   const existingVNet = await client.virtualNetworks.get(resourceGroupName, vnetName);
   if (existingVNet) {
     // Update existing resource
     await client.virtualNetworks.beginCreateOrUpdateAndWait(/* ... */);
   }
   ```

3. **Use unique deployment names:**
   ```typescript
   const deploymentName = `deploy-${Date.now()}`;
   ```

## Network Issues

### VNet Deployment Fails

**Symptoms:**
```
Error: Virtual network creation failed with code 'VnetSizeTooSmall'
```

**Solutions:**

1. **Validate address prefix format:**
   ```typescript
   const isValid = validateAddressPrefix('10.0.0.0/16');
   if (!isValid) {
     throw new Error('Invalid CIDR format');
   }
   ```

2. **Check for overlapping address spaces:**
   ```bash
   az network vnet list --query "[].addressSpace.addressPrefixes" --output json
   ```

3. **Ensure subnet prefixes don't overlap:**
   ```typescript
   // Subnets must be within VNet address space
   const vnetPrefix = '10.0.0.0/16';
   const subnetPrefix = '10.0.1.0/24';
   // Verify subnet is within VNet range
   ```

### NSG Rule Conflicts

**Symptoms:**
```
Error: NSG rule priority conflict
```

**Solutions:**

1. **Check for duplicate priorities:**
   ```typescript
   const priorities = config.rules.map(r => r.priority);
   const duplicates = priorities.filter((p, i) => priorities.indexOf(p) !== i);
   if (duplicates.length > 0) {
     throw new Error(`Duplicate priorities: ${duplicates.join(', ')}`);
   }
   ```

2. **Use priority ranges by rule type:**
   ```typescript
   const priorityRanges = {
     'allow': 100-1000,
     'deny': 3000-4000,
     'system': 5000-4096
   };
   ```

3. **Order rules from specific to general:**
   ```typescript
   const sortedRules = config.rules.sort((a, b) => a.priority - b.priority);
   ```

## Monitoring Issues

### Action Group Creation Fails

**Symptoms:**
```
Error: Action group validation failed
```

**Solutions:**

1. **Validate email addresses:**
   ```typescript
   const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
   if (!emailRegex.test(config.emailAddress)) {
     throw new Error('Invalid email address');
   }
   ```

2. **Validate phone numbers for SMS:**
   ```typescript
   if (!config.phoneNumber || !config.countryCode) {
     throw new Error('Phone number and country code are required');
   }
   ```

3. **Check action group short name length:**
   ```typescript
   if (config.groupShortName.length > 12) {
     throw new Error('Group short name must be 12 characters or less');
   }
   ```

### Alert Rule Not Triggering

**Symptoms:**
```
Alert configured but not firing when conditions are met
```

**Solutions:**

1. **Check if alert is enabled:**
   ```typescript
   const alert = await monitorClient.metricAlerts.get(rgName, alertName);
   if (!alert.enabled) {
     await monitorClient.metricAlerts.createOrUpdate(rgName, alertName, { enabled: true });
   }
   ```

2. **Verify metric is available:**
   ```bash
   az monitor metrics list-definitions \
     --resource <resource-id> \
     --query "[].name.value"
   ```

3. **Check threshold and aggregation:**
   ```typescript
   // Ensure threshold is realistic
   if (config.criteria.threshold < 0 || config.criteria.threshold > 100) {
     console.warn('Threshold may be outside expected range');
   }
   ```

4. **Test with manual metric data:**
   ```typescript
   const metricData = await monitorClient.metrics.list(resourceId, {
     timespan: 'PT1H',
     interval: 'PT5M',
     metricnames: config.criteria.metricName
   });
   ```

## Cost Issues

### Unexpected Costs

**Symptoms:**
```
Azure bill higher than expected
```

**Solutions:**

1. **Enable cost alerts:**
   ```typescript
   await createBudget({
     name: 'monthly-budget',
     amount: 1000,
      timeGrain: 'Monthly',
      notification: {
        emailContacts: ['finance@example.com'],
        threshold: 80
      }
   });
   ```

2. **Review resource usage:**
   ```bash
   az consumption usage list --top 100 --output table
   ```

3. **Check for idle resources:**
   ```bash
   az vm list --show-details --query "[?powerState!='VM running']"
   ```

4. **Implement auto-shutdown:**
   ```typescript
   await setAutoShutdown({
     vmId: vmResourceId,
     schedule: '22:00',
     timezone: 'Eastern Standard Time'
   });
   ```

## Performance Issues

### Slow Deployment Performance

**Symptoms:**
```
Deployments taking longer than expected
```

**Solutions:**

1. **Check Azure region availability:**
   ```bash
   az account list-locations --query "[].name" --output table
   ```

2. **Use parallel deployments:**
   ```typescript
   await Promise.all([
     deployResource(resource1),
     deployResource(resource2),
     deployResource(resource3)
   ]);
   ```

3. **Optimize Bicep templates:**
   - Use modules for reusable components
   - Minimize dependencies
   - Use deployment scripts sparingly

4. **Monitor deployment performance:**
   ```typescript
   const startTime = Date.now();
   await deployBicepTemplate(config);
   const duration = Date.now() - startTime;
   console.log(`Deployment took ${duration}ms`);
   ```

## Debugging Tips

### Enable Debug Logging

```typescript
import { setLogLevel } from '@azure/logger';

setLogLevel('verbose');
```

### Use Azure CLI for Troubleshooting

```bash
# Show detailed error information
az deployment group show \
  --resource-group <rg-name> \
  --name <deployment-name> \
  --output json | jq '.error'
```

### Check Deployment History

```bash
az deployment operation group list \
  --resource-group <rg-name> \
  --name <deployment-name> \
  --output table
```

### Export Logs for Analysis

```bash
az monitor activity-log list \
  --resource-group <rg-name> \
  --start-time 2024-01-01T00:00:00Z \
  --output json > activity-logs.json
```

## Getting Help

- [Azure Status](https://status.azure.com/) - Check Azure service health
- [Azure Portal Diagnostics](https://portal.azure.com/#blade/Microsoft_Azure_Support/DiagnosticsBlade) - Interactive troubleshooting
- [Azure Documentation](https://docs.microsoft.com/azure) - Official documentation
- [Azure Support](https://azure.microsoft.com/support/) - Contact Azure support

### Common Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| `AuthorizationFailed` | Insufficient permissions | Assign appropriate RBAC role |
| `ResourceNotFound` | Resource doesn't exist | Verify resource ID and existence |
| `SubscriptionNotFound` | Subscription doesn't exist | Check subscription ID and access |
| `InvalidTemplate` | Template validation failed | Fix template syntax and parameters |
| `DeploymentActive` | Deployment already in progress | Wait for deployment to complete or cancel |
| `QuotaExceeded` | Resource quota exceeded | Request quota increase or use different tier |
