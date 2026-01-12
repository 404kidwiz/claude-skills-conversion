import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

interface ComponentTemplate {
  name: string;
  type: 'functional' | 'class';
  hooks: string[];
  props: Prop[];
  styles: 'css' | 'styled-components' | 'emotion' | 'module';
  testing: boolean;
}

interface Prop {
  name: string;
  type: string;
  required: boolean;
  defaultValue?: any;
}

class ComponentScaffolder {
  private template: ComponentTemplate;

  constructor(template: ComponentTemplate) {
    this.template = template;
  }

  scaffold(outputDir: string): void {
    const componentDir = path.join(outputDir, this.template.name);
    fs.mkdirSync(componentDir, { recursive: true });

    if (this.template.type === 'functional') {
      this.createFunctionalComponent(componentDir);
    } else {
      this.createClassComponent(componentDir);
    }

    this.createStyles(componentDir);
    this.createTest(componentDir);
    this.createIndex(componentDir);

    console.log(`✓ Component ${this.template.name} scaffolded successfully`);
  }

  private createFunctionalComponent(dir: string): void {
    const imports: string[] = ['React'];

    if (this.template.hooks.includes('useState')) {
      imports.push('useState');
    }
    if (this.template.hooks.includes('useEffect')) {
      imports.push('useEffect');
    }
    if (this.template.hooks.includes('useCallback')) {
      imports.push('useCallback');
    }
    if (this.template.hooks.includes('useMemo')) {
      imports.push('useMemo');
    }
    if (this.template.hooks.includes('useRef')) {
      imports.push('useRef');
    }

    const propsInterface = this.generatePropsInterface();
    const hooks = this.generateHooks();

    const content = `import { ${imports.join(', ')} } from 'react';
${propsInterface}
${this.template.styles === 'styled-components' ? `import styled from 'styled-components';` : ''}
${this.template.styles === 'emotion' ? `import { css } from '@emotion/react';` : ''}

${this.template.styles === 'module' ? `import styles from './${this.template.name}.module.css';` : ''}

interface ${this.template.name}Props {
${this.template.props.map(p => `  ${p.name}${p.required ? '' : '?'}: ${p.type};`).join('\n')}
}

export const ${this.template.name}: React.FC<${this.template.name}Props> = ({${this.getPropNames()}}) => {
${hooks}
  return (
${this.generateJSX()}
  );
};

export default ${this.template.name};
`;

    fs.writeFileSync(path.join(dir, `${this.template.name}.tsx`), content);
  }

  private generatePropsInterface(): string {
    if (this.template.props.length === 0) return '';

    return `
interface Props {
${this.template.props.map(p => `  ${p.name}${p.required ? '' : '?'}: ${p.type};`).join('\n')}
}`;
  }

  private generateHooks(): string {
    let hooksCode = '';

    if (this.template.hooks.includes('useState')) {
      hooksCode += `  const [state, setState] = useState<${this.template.props[0]?.type || 'any'}>(null);\n\n`;
    }

    if (this.template.hooks.includes('useEffect')) {
      hooksCode += `  useEffect(() => {
    // Effect logic here
  }, []);\n\n`;
    }

    if (this.template.hooks.includes('useCallback')) {
      hooksCode += `  const handleClick = useCallback(() => {
    // Handler logic here
  }, []);\n\n`;
    }

    if (this.template.hooks.includes('useMemo')) {
      hooksCode += `  const memoizedValue = useMemo(() => {
    // Memoized computation
    return computedValue;
  }, [dependencies]);\n\n`;
    }

    if (this.template.hooks.includes('useRef')) {
      hooksCode += `  const ref = useRef<HTMLDivElement>(null);\n\n`;
    }

    return hooksCode;
  }

  private generateJSX(): string {
    let jsx = `    <div className="${this.template.name.toLowerCase()}"${this.template.styles === 'module' ? ` ${styles.container}` : ''}>\n`;
    jsx += `      {/* Component content */}\n`;
    jsx += `    </div>`;
    return jsx;
  }

  private getPropNames(): string {
    const names = this.template.props.map(p => p.name);
    if (names.length > 0) {
      return ` ${names.join(', ')}`;
    }
    return '';
  }

  private createClassComponent(dir: string): void {
    const content = `import React, { Component } from 'react';

interface ${this.template.name}Props {
${this.template.props.map(p => `  ${p.name}${p.required ? '' : '?'}: ${p.type};`).join('\n')}
}

interface ${this.template.name}State {
  data: any;
  loading: boolean;
}

export class ${this.template.name} extends Component<${this.template.name}Props, ${this.template.name}State> {
  constructor(props: ${this.template.name}Props) {
    super(props);
    this.state = {
      data: null,
      loading: false
    };
  }

  componentDidMount(): void {
    // Initialize component
  }

  componentDidUpdate(prevProps: ${this.template.name}Props): void {
    // Handle updates
  }

  componentWillUnmount(): void {
    // Cleanup
  }

  render(): JSX.Element {
    return (
      <div className="${this.template.name.toLowerCase()}">
        {/* Component content */}
      </div>
    );
  }
}

export default ${this.template.name};
`;

    fs.writeFileSync(path.join(dir, `${this.template.name}.tsx`), content);
  }

  private createStyles(dir: string): void {
    let content = '';

    switch (this.template.styles) {
      case 'css':
        content = `.${this.template.name.toLowerCase()} {
  /* Styles here */
}

${this.template.name.toLowerCase()}__container {
  /* Container styles */
}
`;
        fs.writeFileSync(path.join(dir, `${this.template.name}.css`), content);
        break;

      case 'module':
        content = `.container {
  /* Container styles */
}
`;
        fs.writeFileSync(path.join(dir, `${this.template.name}.module.css`), content);
        break;

      case 'styled-components':
        // Styled components are included in the component file
        break;

      case 'emotion':
        // Emotion styles are included in the component file
        break;
    }
  }

  private createTest(dir: string): void {
    if (!this.template.testing) return;

    const content = `import { render, screen } from '@testing-library/react';
import { ${this.template.name} } from './${this.template.name}';

describe('${this.template.name}', () => {
  it('renders without crashing', () => {
    render(<${this.template.name} />);
  });

${this.template.props.length > 0 ? `  it('renders with props', () => {
    render(<${this.template.name} ${this.getPropsForTest()} />);
    // Add assertions
  });

` : ''}  it('matches snapshot', () => {
    const { asFragment } = render(<${this.template.name} />);
    expect(asFragment()).toMatchSnapshot();
  });
});
`;

    fs.writeFileSync(path.join(dir, `${this.template.name}.test.tsx`), content);
  }

  private getPropsForTest(): string {
    return this.template.props
      .map(p => {
        const value = this.getDefaultValueForType(p.type);
        return `${p.name}={${value}}`;
      })
      .join(' ');
  }

  private getDefaultValueForType(type: string): string {
    if (type === 'string') return "'test'";
    if (type === 'number') return '42';
    if (type === 'boolean') return 'true';
    if (type === '() => void') return 'jest.fn()';
    if (type.includes('[]')) return '[]';
    return 'null';
  }

  private createIndex(dir: string): void {
    const content = `export { ${this.template.name} } from './${this.template.name}';
export default ${this.template.name};
`;

    fs.writeFileSync(path.join(dir, 'index.ts'), content);
  }
}

// CLI interface
const args = process.argv.slice(2);
const name = args[0];

if (!name) {
  console.error('Component name is required');
  process.exit(1);
}

const template: ComponentTemplate = {
  name,
  type: 'functional',
  hooks: [],
  props: [],
  styles: 'css',
  testing: true
};

// Parse additional arguments
args.slice(1).forEach(arg => {
  if (arg === '--hooks=useState,useEffect') {
    template.hooks = ['useState', 'useEffect'];
  } else if (arg.startsWith('--props=')) {
    const propsStr = arg.replace('--props=', '');
    template.props = JSON.parse(propsStr);
  } else if (arg.startsWith('--styles=')) {
    template.styles = arg.replace('--styles=', '') as any;
  } else if (arg === '--no-test') {
    template.testing = false;
  }
});

const scaffolder = new ComponentScaffolder(template);
scaffolder.scaffold('./src/components');
