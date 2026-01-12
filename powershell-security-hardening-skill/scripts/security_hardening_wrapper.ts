import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';

interface PowerShellOptions {
  executionPolicy?: string;
  noProfile?: boolean;
  nonInteractive?: boolean;
}

interface EnforceExecutionPolicyParams {
  scope: 'MachinePolicy' | 'UserPolicy' | 'Process' | 'CurrentUser' | 'LocalMachine';
  policy: 'Restricted' | 'AllSigned' | 'RemoteSigned' | 'Unrestricted' | 'Bypass' | 'Undefined';
  validate?: boolean;
  audit?: boolean;
  logCompliance?: boolean;
}

interface SetupConstrainedModeParams {
  mode: 'FullLanguage' | 'ConstrainedLanguage' | 'Restricted' | 'NoLanguage';
  systemLockdown?: boolean;
  auditOnly?: boolean;
  enableScriptBlockLogging?: boolean;
  enableModuleLogging?: boolean;
  enableTranscription?: boolean;
  transcriptionPath?: string;
}

interface ConfigureScriptBlockLoggingParams {
  enable?: boolean;
  disable?: boolean;
  logInvocation?: boolean;
  eventLog?: boolean;
  customPath?: string;
  maxLogSizeMB?: number;
  retentionDays?: number;
  testLogging?: boolean;
}

interface SignModuleParams {
  path: string;
  certificate?: string;
  certificatePath?: string;
  timestampServer?: string;
  recurse?: boolean;
  verify?: boolean;
  force?: boolean;
}

export class PowerShellSecurityHardening {
  private scriptPath: string;

  constructor(scriptPath: string = './scripts') {
    this.scriptPath = scriptPath;
  }

  private async executePowerShell(script: string, params: Record<string, any>, options?: PowerShellOptions): Promise<string> {
    return new Promise((resolve, reject) => {
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

      args.push('-File', path.join(this.scriptPath, script));

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

  async enforceExecutionPolicy(params: EnforceExecutionPolicyParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      Scope: params.scope,
      Policy: params.policy,
    };

    if (params.validate) scriptParams.Validate = params.validate;
    if (params.audit) scriptParams.Audit = params.audit;
    if (params.logCompliance) scriptParams.LogCompliance = params.logCompliance;

    return this.executePowerShell('enforce_execution_policy.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async setupConstrainedMode(params: SetupConstrainedModeParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      Mode: params.mode,
    };

    if (params.systemLockdown) scriptParams.SystemLockdown = params.systemLockdown;
    if (params.auditOnly) scriptParams.AuditOnly = params.auditOnly;
    if (params.enableScriptBlockLogging) scriptParams.EnableScriptBlockLogging = params.enableScriptBlockLogging;
    if (params.enableModuleLogging) scriptParams.EnableModuleLogging = params.enableModuleLogging;
    if (params.enableTranscription) scriptParams.EnableTranscription = params.enableTranscription;
    if (params.transcriptionPath) scriptParams.TranscriptionPath = params.transcriptionPath;

    return this.executePowerShell('setup_constrained_mode.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async configureScriptBlockLogging(params: ConfigureScriptBlockLoggingParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {};

    if (params.enable) scriptParams.Enable = params.enable;
    if (params.disable) scriptParams.Disable = params.disable;
    if (params.logInvocation) scriptParams.LogInvocation = params.logInvocation;
    if (params.eventLog) scriptParams.EventLog = params.eventLog;
    if (params.customPath) scriptParams.CustomPath = params.customPath;
    if (params.maxLogSizeMB) scriptParams.MaxLogSizeMB = params.maxLogSizeMB;
    if (params.retentionDays) scriptParams.RetentionDays = params.retentionDays;
    if (params.testLogging) scriptParams.TestLogging = params.testLogging;

    return this.executePowerShell('configure_script_block_logging.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async signModule(params: SignModuleParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      Path: params.path,
    };

    if (params.certificate) scriptParams.Certificate = params.certificate;
    if (params.certificatePath) scriptParams.CertificatePath = params.certificatePath;
    if (params.timestampServer) scriptParams.TimestampServer = params.timestampServer;
    if (params.recurse) scriptParams.Recurse = params.recurse;
    if (params.verify) scriptParams.Verify = params.verify;
    if (params.force) scriptParams.Force = params.force;

    return this.executePowerShell('sign_module.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async getExecutionPolicy(scope?: string): Promise<any> {
    const command = scope 
      ? `Get-ExecutionPolicy -Scope ${scope} | ConvertTo-Json`
      : '$scopes = @("MachinePolicy", "UserPolicy", "Process", "CurrentUser", "LocalMachine"); $policies = @{}; foreach ($s in $scopes) { $policies[$s] = Get-ExecutionPolicy -Scope $s }; $policies | ConvertTo-Json';
    
    const result = await this.executePowerShell(command, {});
    return JSON.parse(result);
  }

  async getLanguageMode(): Promise<string> {
    const result = await this.executePowerShell('$ExecutionContext.SessionState.LanguageMode.ToString()', {});
    return result.trim();
  }

  async getScriptBlockLoggingStatus(): Promise<boolean> {
    const result = await this.executePowerShell(
      '(Get-ItemProperty "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\PowerShell\\ScriptBlockLogging" -ErrorAction SilentlyContinue).EnableScriptBlockLogging -eq 1',
      {}
    );
    return result.trim().toLowerCase() === 'true';
  }

  async getCodeSigningCertificates(): Promise<any[]> {
    const command = 'Get-ChildItem -Path Cert:\\CurrentUser\\My -CodeSigningCert | Select-Object Subject, Thumbprint, NotBefore, NotAfter | ConvertTo-Json';
    const result = await this.executePowerShell(command, {});
    return JSON.parse(result);
  }
}

export default PowerShellSecurityHardening;
