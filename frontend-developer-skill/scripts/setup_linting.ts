import * as fs from 'fs';
import * as path from 'path';

class LintingSetup {
  setup(outputDir: string, tools: ('eslint' | 'prettier')[]): void {
    this.createESLintConfig(outputDir);
    this.createPrettierConfig(outputDir);
    this.createIgnoreFiles(outputDir);
    this.updatePackageScripts(outputDir);

    console.log('✓ Linting and formatting setup complete');
  }

  private createESLintConfig(dir: string): void {
    const content = `{
  "parser": "@typescript-eslint/parser",
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "plugin:jsx-a11y/recommended",
    "plugin:prettier/recommended"
  ],
  "parserOptions": {
    "ecmaVersion": 2022,
    "sourceType": "module",
    "ecmaFeatures": {
      "jsx": true
    },
    "project": "./tsconfig.json"
  },
  "plugins": [
    "@typescript-eslint",
    "react",
    "react-hooks",
    "jsx-a11y",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/explicit-function-return-type": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-explicit-any": "warn",
    "react/react-in-jsx-scope": "off",
    "react/prop-types": "off",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "prettier/prettier": "error",
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  },
  "env": {
    "browser": true,
    "es2022": true,
    "node": true
  }
}
`;

    fs.writeFileSync(path.join(dir, '.eslintrc.json'), content);
  }

  private createPrettierConfig(dir: string): void {
    const content = `{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "arrowParens": "always",
  "bracketSpacing": true,
  "endOfLine": "lf"
}
`;

    fs.writeFileSync(path.join(dir, '.prettierrc'), content);
  }

  private createIgnoreFiles(dir: string): void {
    const eslintIgnore = `node_modules
dist
build
coverage
.next
.nuxt
.vscode
.idea
*.config.js
*.config.ts
`;

    const prettierIgnore = `node_modules
dist
build
coverage
.next
.nuxt
package-lock.json
yarn.lock
pnpm-lock.yaml
`;

    fs.writeFileSync(path.join(dir, '.eslintignore'), eslintIgnore);
    fs.writeFileSync(path.join(dir, '.prettierignore'), prettierIgnore);
  }

  private updatePackageScripts(dir: string): void {
    const packageJsonPath = path.join(dir, 'package.json');

    if (fs.existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
      packageJson.scripts = {
        ...packageJson.scripts,
        lint: 'eslint src --ext .ts,.tsx',
        'lint:fix': 'eslint src --ext .ts,.tsx --fix',
        format: 'prettier --write "src/**/*.{ts,tsx,json,css,md}"',
        'format:check': 'prettier --check "src/**/*.{ts,tsx,json,css,md}"',
        'lint-and-format': 'npm run lint:fix && npm run format',
      };
      fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
    }
  }
}

const setup = new LintingSetup();
setup.setup('.', ['eslint', 'prettier']);
