import { spawn, ChildProcess } from 'child_process';
import { promises as fs } from 'fs';
import * as path from 'path';

interface PowerShellOptions {
  executionPolicy?: string;
  noProfile?: boolean;
  nonInteractive?: boolean;
}

interface ScaffoldParams {
  moduleName: string;
  path?: string;
  author?: string;
  description?: string;
  includeTests?: boolean;
  includeExamples?: boolean;
  powerShellVersion?: string;
  force?: boolean;
}

interface CreateManifestParams {
  modulePath?: string;
  moduleName?: string;
  manifestPath?: string;
  scanFunctions?: boolean;
  scanRequiredModules?: boolean;
  additionalData?: Record<string, any>;
  validate?: boolean;
}

interface ValidateFunctionsParams {
  modulePath: string;
  strictMode?: boolean;
  checkPSScriptAnalyzer?: boolean;
  checkHelp?: boolean;
  checkSyntax?: boolean;
  excludeRules?: string[];
  functionWhitelist?: Record<string, string[]>;
}

export class PowerShellModuleArchitect {
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

  async scaffoldModule(params: ScaffoldParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      ModuleName: params.moduleName,
    };

    if (params.path) scriptParams.Path = params.path;
    if (params.author) scriptParams.Author = params.author;
    if (params.description) scriptParams.Description = params.description;
    if (params.includeTests) scriptParams.IncludeTests = params.includeTests;
    if (params.includeExamples) scriptParams.IncludeExamples = params.includeExamples;
    if (params.powerShellVersion) scriptParams.PowerShellVersion = params.powerShellVersion;
    if (params.force) scriptParams.Force = params.force;

    return this.executePowerShell('scaffold_module.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async createManifest(params: CreateManifestParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {};

    if (params.modulePath) scriptParams.ModulePath = params.modulePath;
    if (params.moduleName) scriptParams.ModuleName = params.moduleName;
    if (params.manifestPath) scriptParams.ManifestPath = params.manifestPath;
    if (params.scanFunctions) scriptParams.ScanFunctions = params.scanFunctions;
    if (params.scanRequiredModules) scriptParams.ScanRequiredModules = params.scanRequiredModules;
    if (params.additionalData) scriptParams.AdditionalData = params.additionalData;
    if (params.validate) scriptParams.Validate = params.validate;

    return this.executePowerShell('create_manifest.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async validateFunctions(params: ValidateFunctionsParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      ModulePath: params.modulePath,
    };

    if (params.strictMode) scriptParams.StrictMode = params.strictMode;
    if (params.checkPSScriptAnalyzer) scriptParams.CheckPSScriptAnalyzer = params.checkPSScriptAnalyzer;
    if (params.checkHelp) scriptParams.CheckHelp = params.checkHelp;
    if (params.checkSyntax) scriptParams.CheckSyntax = params.checkSyntax;
    if (params.excludeRules) scriptParams.ExcludeRules = params.excludeRules;
    if (params.functionWhitelist) scriptParams.FunctionWhitelist = params.functionWhitelist;

    return this.executePowerShell('validate_functions.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async analyzeModule(modulePath: string): Promise<{
    functions: string[];
    dependencies: string[];
    structure: string[];
  }> {
    const modulePathNormalized = path.resolve(modulePath);

    const structure = await this.getDirectoryStructure(modulePathNormalized);
    
    const publicPath = path.join(modulePathNormalized, 'Public');
    const functions: string[] = [];
    
    try {
      const files = await fs.readdir(publicPath);
      for (const file of files) {
        if (file.endsWith('.ps1')) {
          const functionName = path.basename(file, '.ps1');
          functions.push(functionName);
        }
      }
    } catch {
      // Public directory doesn't exist
    }

    return {
      functions,
      dependencies: [],
      structure
    };
  }

  private async getDirectoryStructure(dirPath: string, depth: number = 0): Promise<string[]> {
    const structure: string[] = [];
    const maxDepth = 3;

    if (depth > maxDepth) {
      return structure;
    }

    try {
      const items = await fs.readdir(dirPath, { withFileTypes: true });
      
      for (const item of items) {
        const fullPath = path.join(dirPath, item.name);
        const indent = '  '.repeat(depth);
        
        if (item.isDirectory()) {
          structure.push(`${indent}[DIR] ${item.name}`);
          structure.push(...await this.getDirectoryStructure(fullPath, depth + 1));
        } else {
          structure.push(`${indent}[FILE] ${item.name}`);
        }
      }
    } catch (error) {
      // Ignore errors
    }

    return structure;
  }

  async createDocumentation(modulePath: string, outputPath?: string): Promise<void> {
    const analysis = await this.analyzeModule(modulePath);
    
    const docs = `# Module Documentation

## Functions

${analysis.functions.map(fn => `### ${fn}`).join('\n\n')}

## Module Structure

${analysis.structure.map(line => line).join('\n')}

---

Generated by PowerShell Module Architect
`;

    const output = outputPath || path.join(modulePath, 'DOCUMENTATION.md');
    await fs.writeFile(output, docs, 'utf-8');
  }
}

export default PowerShellModuleArchitect;
