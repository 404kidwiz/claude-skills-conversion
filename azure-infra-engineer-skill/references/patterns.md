# Azure Infrastructure Patterns

Common patterns and best practices for Azure infrastructure deployment and management.

## Infrastructure as Code Patterns

### Modular Bicep Templates

```bicep
// main.bicep
param location string = resourceGroup().location

module vnetModule 'modules/vnet.bicep' = {
  name: 'vnet-deployment'
  params: {
    location: location
    vnetName: 'main-vnet'
    addressSpace: '10.0.0.0/16'
  }
}

module vmModule 'modules/vm.bicep' = {
  name: 'vm-deployment'
  params: {
    location: location
    subnetId: vnetModule.outputs.subnetId
    vmName: 'main-vm'
  }
  dependsOn: [
    vnetModule
  ]
}
```

### Parameterized Templates

```typescript
const parameters = {
  environment: 'production',
  location: 'eastus',
  vmCount: 3,
  databaseTier: 'Premium'
};

const config = {
  parameters,
  // ... other config
};
```

## Network Patterns

### Hub and Spoke Topology

```typescript
const hubVNetConfig = {
  name: 'hub-vnet',
  addressSpace: ['10.0.0.0/16'],
  subnets: [
    { name: 'GatewaySubnet', addressPrefix: '10.0.0.0/24' },
    { name: 'AzureFirewallSubnet', addressPrefix: '10.0.1.0/24' },
    { name: 'SharedServicesSubnet', addressPrefix: '10.0.2.0/24' }
  ]
};

const spokeVNetConfig = {
  name: 'spoke-vnet',
  addressSpace: ['10.1.0.0/16'],
  subnets: [
    { name: 'WorkloadSubnet', addressPrefix: '10.1.1.0/24' }
  ]
};
```

### VNet Peering Configuration

```typescript
// Peer VNets for connectivity
await deployVNetPeering({
  peeringName: 'hub-to-spoke',
  sourceVNet: hubVNetId,
  targetVNet: spokeVNetId,
  allowForwardedTraffic: true,
  allowGatewayTransit: false
});
```

### NSG Rule Patterns

```typescript
const commonRules: NSGRule[] = [
  {
    name: 'AllowHTTP',
    priority: 100,
    direction: 'Inbound',
    access: 'Allow',
    protocol: 'Tcp',
    sourceAddressPrefix: '*',
    sourcePortRange: '*',
    destinationAddressPrefix: '*',
    destinationPortRange: '80'
  },
  {
    name: 'AllowHTTPS',
    priority: 110,
    direction: 'Inbound',
    access: 'Allow',
    protocol: 'Tcp',
    sourceAddressPrefix: '*',
    sourcePortRange: '*',
    destinationAddressPrefix: '*',
    destinationPortRange: '443'
  },
  {
    name: 'DenyAll',
    priority: 4096,
    direction: 'Inbound',
    access: 'Deny',
    protocol: '*',
    sourceAddressPrefix: '*',
    sourcePortRange: '*',
    destinationAddressPrefix: '*',
    destinationPortRange: '*'
  }
];
```

## Security Patterns

### Managed Identity Pattern

```typescript
// Use Managed Identity for service-to-service authentication
const vmConfig = {
  identity: {
    type: 'UserAssigned',
    userAssignedIdentities: {
      [managedIdentityId]: {}
    }
  }
};
```

### RBAC Assignment Pattern

```typescript
await assignRole({
  roleDefinitionId: '/providers/Microsoft.Authorization/roleDefinitions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
  principalId: servicePrincipalObjectId,
  scope: resourceGroupScope,
  principalType: 'ServicePrincipal'
});
```

### Azure Policy Pattern

```typescript
const policyDefinition = {
  policyRule: {
    if: {
      field: 'type',
      equals: 'Microsoft.Compute/virtualMachines'
    },
    then: {
      effect: 'deny',
      details: {
        type: 'Microsoft.Authorization/policyDefinitions',
        resourceActions: ['Microsoft.Compute/virtualMachines/write']
      }
    }
  }
};
```

## Monitoring Patterns

### Multi-Metric Alert Pattern

```typescript
const multiMetricAlert = {
  criteria: {
    'odata.type': 'Microsoft.Azure.Monitor.MultipleResourceMultipleMetricCriteria',
    allOf: [
      {
        threshold: 80,
        name: 'CPUHigh',
        metricName: 'Percentage CPU',
        operator: 'GreaterThan',
        timeAggregation: 'Average'
      },
      {
        threshold: 90,
        name: 'MemoryHigh',
        metricName: 'Available Memory',
        operator: 'LessThan',
        timeAggregation: 'Average'
      }
    ]
  }
};
```

### Log Analytics Query Pattern

```typescript
const query = `
AzureActivity
| where OperationName == 'Microsoft.Compute/virtualMachines/write'
| project TimeGenerated, Caller, OperationName, ActivityStatusValue
| sort by TimeGenerated desc
`;
```

## Deployment Patterns

### Blue-Green Deployment

```typescript
// Deploy new infrastructure alongside existing
const greenConfig = { ...blueConfig, name: 'app-green' };
await deployBicepTemplate(greenConfig);

// Test green environment
await runIntegrationTests('app-green');

// Switch traffic
await updateTrafficManager({
  profileName: 'app-profile',
  endpoints: [
    { name: 'green', target: 'app-green', weight: 100 },
    { name: 'blue', target: 'app-blue', weight: 0 }
  ]
});

// Clean up blue after validation
await deleteResourceGroup('app-blue');
```

### Rolling Update Pattern

```typescript
for (let i = 0; i < vmCount; i++) {
  await updateVM(vmNames[i], newImageVersion);
  await healthCheck(vmNames[i]);
}
```

## Cost Optimization Patterns

### Auto-Scale Configuration

```typescript
const autoScaleConfig = {
  profile: {
    capacity: {
      minimum: '1',
      maximum: '5',
      default: '2'
    },
    rules: [
      {
        metricTrigger: {
          metricName: 'Percentage CPU',
          metricResourceUri: vmResourceId,
          timeGrain: 'PT1M',
          statistic: 'Average',
          threshold: 75,
          operator: 'GreaterThan'
        },
        scaleAction: {
          direction: 'Increase',
          type: 'ChangeCount',
          value: '1',
          cooldown: 'PT5M'
        }
      }
    ]
  }
};
```

### Reserved Instance Pattern

```typescript
const reservationConfig = {
  sku: {
    name: 'Standard_D2s_v3'
  },
  location: 'eastus',
  reservedResourceType: 'VirtualMachines',
  billingScopeId: subscriptionId,
  quantity: 3,
  term: 'P1Y'
};
```

## Error Handling Patterns

### Retry Pattern

```typescript
async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  maxRetries = 3,
  delayMs = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error: any) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, delayMs * Math.pow(2, i)));
    }
  }
  throw new Error('Max retries exceeded');
}
```

### Circuit Breaker Pattern

```typescript
class CircuitBreaker {
  private failures = 0;
  private lastFailureTime = 0;
  private readonly threshold = 3;
  private readonly timeout = 60000;

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.isOpen()) {
      throw new Error('Circuit breaker is open');
    }

    try {
      const result = await operation();
      this.reset();
      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }

  private isOpen(): boolean {
    return this.failures >= this.threshold &&
      Date.now() - this.lastFailureTime < this.timeout;
  }
}
```

## Tagging Strategy

```typescript
const standardTags = {
  'CostCenter': 'IT-001',
  'Environment': environment,
  'Owner': 'DevOps Team',
  'Project': project,
  'CreatedBy': userName,
  'CreatedDate': new Date().toISOString()
};

const resourceConfig = {
  // ... other config
  tags: standardTags
};
```

## Resource Naming Conventions

```typescript
function getResourceName(resourceType: string, environment: string, appName: string, instance?: string): string {
  const suffixes = {
    'VirtualNetwork': 'vnet',
    'NetworkSecurityGroup': 'nsg',
    'VirtualMachine': 'vm',
    'AppServicePlan': 'asp',
    'WebApp': 'app'
  };

  const parts = [appName, environment, suffixes[resourceType] || 'res'];
  if (instance) parts.push(instance);

  return parts.join('-').toLowerCase();
}

// Examples:
// getResourceName('VirtualMachine', 'prod', 'myapp', '01') => 'myapp-prod-vm-01'
// getResourceName('WebApp', 'dev', 'api') => 'api-dev-app'
```
