import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';

interface PowerShellOptions {
  executionPolicy?: string;
  noProfile?: boolean;
  nonInteractive?: boolean;
}

interface WinFormsParams {
  formTitle: string;
  width?: number;
  height?: number;
  controls?: WinFormsControl[];
  formBorderStyle?: 'FixedSingle' | 'Fixed3D' | 'FixedDialog' | 'Sizable' | 'FixedToolWindow' | 'SizableToolWindow';
  startPosition?: 'Normal' | 'Minimized' | 'Maximized' | 'CenterScreen' | 'WindowsDefaultLocation' | 'WindowsDefaultBounds' | 'CenterParent';
  show?: boolean;
  generateScript?: boolean;
  outputPath?: string;
}

interface WinFormsControl {
  type: 'Button' | 'TextBox' | 'Label' | 'ListBox' | 'ComboBox';
  name: string;
  text?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  multiline?: boolean;
  readOnly?: boolean;
}

interface WpfParams {
  xamlPath?: string;
  viewModel?: Record<string, any>;
  show?: boolean;
  generateXaml?: boolean;
  outputXamlPath?: string;
  windowTitle?: string;
  width?: number;
  height?: number;
}

interface TuiParams {
  title?: string;
  menuItems?: TuiMenuItem[];
  tableData?: any[];
  formFields?: Record<string, any>;
  mode?: 'Menu' | 'Table' | 'Form' | 'Progress' | 'Wizard';
  clearScreen?: boolean;
  foregroundColor?: string;
  backgroundColor?: string;
}

interface TuiMenuItem {
  label: string;
  shortcut?: string;
  action?: string;
  subMenu?: TuiMenuItem[];
  keepOpen?: boolean;
}

export class PowerShellUIArchitect {
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
            args.push(`-${key}`, `'${JSON.stringify(v).replace(/'/g, "''")}'`);
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

  async createWinForms(params: WinFormsParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {
      FormTitle: params.formTitle,
    };

    if (params.width) scriptParams.Width = params.width;
    if (params.height) scriptParams.Height = params.height;
    if (params.controls) scriptParams.Controls = params.controls;
    if (params.formBorderStyle) scriptParams.FormBorderStyle = params.formBorderStyle;
    if (params.startPosition) scriptParams.StartPosition = params.startPosition;
    if (params.show) scriptParams.Show = params.show;
    if (params.generateScript) scriptParams.GenerateScript = params.generateScript;
    if (params.outputPath) scriptParams.OutputPath = params.outputPath;

    return this.executePowerShell('create_winforms.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async buildWpf(params: WpfParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {};

    if (params.xamlPath) scriptParams.XamlPath = params.xamlPath;
    if (params.viewModel) scriptParams.ViewModel = params.viewModel;
    if (params.show) scriptParams.Show = params.show;
    if (params.generateXaml) scriptParams.GenerateXaml = params.generateXaml;
    if (params.outputXamlPath) scriptParams.OutputXamlPath = params.outputXamlPath;
    if (params.windowTitle) scriptParams.WindowTitle = params.windowTitle;
    if (params.width) scriptParams.Width = params.width;
    if (params.height) scriptParams.Height = params.height;

    return this.executePowerShell('build_wpf.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async designTui(params: TuiParams, options?: PowerShellOptions): Promise<string> {
    const scriptParams: Record<string, any> = {};

    if (params.title) scriptParams.Title = params.title;
    if (params.menuItems) scriptParams.MenuItems = params.menuItems;
    if (params.tableData) scriptParams.TableData = params.tableData;
    if (params.formFields) scriptParams.FormFields = params.formFields;
    if (params.mode) scriptParams.Mode = params.mode;
    if (params.clearScreen) scriptParams.ClearScreen = params.clearScreen;
    if (params.foregroundColor) scriptParams.ForegroundColor = params.foregroundColor;
    if (params.backgroundColor) scriptParams.BackgroundColor = params.backgroundColor;

    return this.executePowerShell('design_tui.ps1', scriptParams, {
      executionPolicy: 'RemoteSigned',
      ...options
    });
  }

  async checkWindowsFormsSupport(): Promise<boolean> {
    try {
      const result = await this.executePowerShell(
        'Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop; $true',
        {}
      );
      return result.trim().toLowerCase() === 'true';
    } catch {
      return false;
    }
  }

  async checkWpfSupport(): Promise<boolean> {
    try {
      const result = await this.executePowerShell(
        'Add-Type -AssemblyName PresentationFramework -ErrorAction Stop; $true',
        {}
      );
      return result.trim().toLowerCase() === 'true';
    } catch {
      return false;
    }
  }

  createWinFormsButton(name: string, text: string, x: number, y: number, width: number = 100, height: number = 30): WinFormsControl {
    return {
      type: 'Button',
      name,
      text,
      x,
      y,
      width,
      height
    };
  }

  createWinFormsTextBox(name: string, text: string, x: number, y: number, width: number = 200, height: number = 20, multiline: boolean = false, readOnly: boolean = false): WinFormsControl {
    return {
      type: 'TextBox',
      name,
      text,
      x,
      y,
      width,
      height,
      multiline,
      readOnly
    };
  }

  createWinFormsLabel(name: string, text: string, x: number, y: number, width: number = 100, height: number = 20): WinFormsControl {
    return {
      type: 'Label',
      name,
      text,
      x,
      y,
      width,
      height
    };
  }

  createTuiMenuItem(label: string, action?: string, shortcut?: string): TuiMenuItem {
    return {
      label,
      action,
      shortcut
    };
  }
}

export default PowerShellUIArchitect;
