import { spawn, ChildProcess } from 'child_process';
import { promisify } from 'util';

interface PowerShellOptions {
  executionPolicy?: string;
  noProfile?: boolean;
  nonInteractive?: boolean;
  windowStyle?: string;
}

interface ADUserParams {
  username: string;
  action: 'Create' | 'Enable' | 'Disable' | 'Delete' | 'Unlock';
  ou?: string;
  groups?: string[];
  useWMI?: boolean;
}

interface WMIQueryParams {
  queryClass: string;
  propertyFilter?: string;
  filterExpression?: string;
  useCIM?: boolean;
  computerName?: string;
  protocol?: 'Default' | 'CimDSProtocol' | 'Dcom' | 'Wsman';
  timeout?: number;
}

interface DSCDeployParams {
  configurationName: string;
  targetNodes: string[];
  configurationPath?: string;
  mode?: 'Apply' | 'Test' | 'Publish';
  outputPath?: string;
  wait?: boolean;
  force?: boolean;
}

export class PowerShell51Manager {
  private scriptPath: string;

  constructor(scriptPath: string = './scripts') {
    this.scriptPath = scriptPath;
  }

  private buildPowerShellArgs(script: string, params: Record<string, any>, options?: PowerShellOptions): string[] {
    const args: string[] = [];

    if (options?.executionPolicy) {
      args.push('-ExecutionPolicy', options.executionPolicy);
    }
    if (options?.noProfile) {
      args.push('-NoProfile');
    }
    if (options?.nonInteractive) {
      args.push('-NonInteractive');
    }
    if (options?.windowStyle) {
      args.push('-WindowStyle', options.windowStyle);
    }

    args.push('-File', `${this.scriptPath}/${script}`);

    Object.entries(params).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => {
          args.push(`-${key}`, v.toString());
        });
      } else if (typeof value === 'boolean') {
        if (value) {
          args.push(`-${key}`);
        }
      } else if (value !== undefined && value !== null) {
        args.push(`-${key}`, value.toString());
      }
    });

    return args;
  }

  private async executePowerShell(script: string, params: Record<string, any>, options?: PowerShellOptions): Promise<string> {
    return new Promise((resolve, reject) => {
      const args = this.buildPowerShellArgs(script, params, options);
      const ps: ChildProcess = spawn('powershell.exe', args);

      let stdout = '';
      let stderr = '';

      ps.stdout?.on('data', (data: Buffer) => {
        stdout += data.toString();
      });

      ps.stderr?.on('data', (data: Buffer) => {
        stderr += data.toString();
      });

      ps.on('close', (code: number) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(`PowerShell failed with code ${code}: ${stderr}`));
        }
      });

      ps.on('error', (err: Error) => {
        reject(err);
      });
    });
  }

  async manageLegacyAD(params: ADUserParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      Username: params.username,
      Action: params.action,
    };

    if (params.ou) scriptParams.OrganizationalUnit = params.ou;
    if (params.groups) scriptParams.Groups = params.groups;
    if (params.useWMI) scriptParams.UseWMI = params.useWMI;

    return this.executePowerShell('manage_legacy_ad.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async queryWMI(params: WMIQueryParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      QueryClass: params.queryClass,
    };

    if (params.propertyFilter) scriptParams.PropertyFilter = params.propertyFilter;
    if (params.filterExpression) scriptParams.FilterExpression = params.filterExpression;
    if (params.useCIM) scriptParams.UseCIM = params.useCIM;
    if (params.computerName) scriptParams.ComputerName = params.computerName;
    if (params.protocol) scriptParams.Protocol = params.protocol;
    if (params.timeout) scriptParams.TimeoutSeconds = params.timeout;

    return this.executePowerShell('query_wmi.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async deployDSC(params: DSCDeployParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      ConfigurationName: params.configurationName,
      TargetNodes: params.targetNodes,
    };

    if (params.configurationPath) scriptParams.ConfigurationPath = params.configurationPath;
    if (params.mode) scriptParams.Mode = params.mode;
    if (params.outputPath) scriptParams.OutputPath = params.outputPath;
    if (params.wait) scriptParams.Wait = params.wait;
    if (params.force) scriptParams.Force = params.force;

    return this.executePowerShell('deploy_dsc.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async testActiveDirectoryModule(): Promise<boolean> {
    const result = await this.executePowerShell(
      'Get-Module -ListAvailable -Name ActiveDirectory',
      {},
      { executionPolicy: 'RemoteSigned', noProfile: true }
    );
    return result.trim().length > 0;
  }

  async getWMIClasses(pattern?: string): Promise<string> {
    let query = 'Get-WmiObject -List | Select-Object -First 50 Name';
    if (pattern) {
      query = `Get-WmiObject -List | Where-Object { $_.Name -like '*${pattern}*' } | Select-Object Name`;
    }
    return this.executePowerShell(query, {});
  }
}

export default PowerShell51Manager;
