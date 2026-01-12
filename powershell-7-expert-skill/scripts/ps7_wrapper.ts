import { spawn, ChildProcess } from 'child_process';
import { promisify } from 'util';

interface PowerShellOptions {
  executionPolicy?: string;
  noProfile?: boolean;
  nonInteractive?: boolean;
  windowStyle?: string;
}

interface CrossPlatformParams {
  targetOS: 'Windows' | 'Linux' | 'macOS';
  action: 'Deploy' | 'Configure' | 'Monitor' | 'Backup';
  apiEndpoint?: string;
  containerImage?: string;
  configurationData?: Record<string, any>;
  dockerAvailable?: boolean;
  skipContainerCheck?: boolean;
}

interface PublishToGalleryParams {
  modulePath: string;
  apiKey: string;
  skipTests?: boolean;
  prerelease?: boolean;
  repository?: string;
  force?: boolean;
  whatIf?: boolean;
}

interface RestApiParams {
  uri: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS';
  body?: any;
  authType?: 'None' | 'Bearer' | 'Basic' | 'OAuth' | 'ApiKey';
  token?: string;
  headers?: Record<string, string>;
  apiKey?: string;
  apiKeyName?: string;
  timeout?: number;
  maxRetries?: number;
  retryDelay?: number;
  followRedirects?: boolean;
  skipCertificateCheck?: boolean;
}

export class PowerShell7Manager {
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
      } else if (typeof value === 'object') {
        args.push(`-${key}`, `"${JSON.stringify(value).replace(/"/g, '\\"')}"`);
      } else if (value !== undefined && value !== null) {
        args.push(`-${key}`, value.toString());
      }
    });

    return args;
  }

  private async executePowerShell(script: string, params: Record<string, any>, options?: PowerShellOptions): Promise<string> {
    return new Promise((resolve, reject) => {
      const args = this.buildPowerShellArgs(script, params, options);
      const ps: ChildProcess = spawn('pwsh', args);

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

  async crossPlatformAutomation(params: CrossPlatformParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      TargetOS: params.targetOS,
      Action: params.action,
    };

    if (params.apiEndpoint) scriptParams.ApiEndpoint = params.apiEndpoint;
    if (params.containerImage) scriptParams.ContainerImage = params.containerImage;
    if (params.configurationData) scriptParams.ConfigurationData = params.configurationData;
    if (params.dockerAvailable) scriptParams.DockerAvailable = params.dockerAvailable;
    if (params.skipContainerCheck) scriptParams.SkipContainerCheck = params.skipContainerCheck;

    return this.executePowerShell('crossplatform_automation.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async publishToGallery(params: PublishToGalleryParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      ModulePath: params.modulePath,
      ApiKey: params.apiKey,
    };

    if (params.skipTests) scriptParams.SkipTests = params.skipTests;
    if (params.prerelease) scriptParams.Prerelease = params.prerelease;
    if (params.repository) scriptParams.Repository = params.repository;
    if (params.force) scriptParams.Force = params.force;
    if (params.whatIf) scriptParams.WhatIf = params.whatIf;

    return this.executePowerShell('publish_to_gallery.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async consumeRestApi(params: RestApiParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      Uri: params.uri,
    };

    if (params.method) scriptParams.Method = params.method;
    if (params.body) scriptParams.Body = params.body;
    if (params.authType) scriptParams.AuthType = params.authType;
    if (params.token) scriptParams.Token = params.token;
    if (params.headers) scriptParams.Headers = params.headers;
    if (params.apiKey) scriptParams.ApiKey = params.apiKey;
    if (params.apiKeyName) scriptParams.ApiKeyName = params.apiKeyName;
    if (params.timeout) scriptParams.TimeoutSeconds = params.timeout;
    if (params.maxRetries) scriptParams.MaxRetries = params.maxRetries;
    if (params.retryDelay) scriptParams.RetryDelaySeconds = params.retryDelay;
    if (params.followRedirects) scriptParams.FollowRedirects = params.followRedirects;
    if (params.skipCertificateCheck) scriptParams.SkipCertificateCheck = params.skipCertificateCheck;

    return this.executePowerShell('rest_api_consumer.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async checkPowerShell7Installed(): Promise<boolean> {
    try {
      await this.executePowerShell('$PSVersionTable.PSVersion', {});
      return true;
    } catch {
      return false;
    }
  }

  async getPowerShell7Version(): Promise<string> {
    const result = await this.executePowerShell('$PSVersionTable.PSVersion.ToString()', {});
    return result.trim();
  }

  async checkModuleInstalled(moduleName: string): Promise<boolean> {
    const result = await this.executePowerShell(
      `Get-Module -ListAvailable -Name ${moduleName}`,
      {}
    );
    return result.trim().length > 0;
  }

  async installModule(moduleName: string, repository: string = 'PSGallery'): Promise<string> {
    return this.executePowerShell(
      `Install-Module -Name ${moduleName} -Repository ${repository} -Force -Scope CurrentUser`,
      {}
    );
  }
}

export default PowerShell7Manager;
