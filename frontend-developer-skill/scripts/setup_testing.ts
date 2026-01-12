import * as fs from 'fs';
import * as path from 'path';

class TestingSetup {
  setup(outputDir: string, framework: 'jest' | 'vitest' | 'playwright'): void {
    switch (framework) {
      case 'jest':
        this.setupJest(outputDir);
        break;
      case 'vitest':
        this.setupVitest(outputDir);
        break;
      case 'playwright':
        this.setupPlaywright(outputDir);
        break;
    }

    this.createTestUtils(outputDir);
    this.createMocks(outputDir);

    console.log(`✓ ${framework} testing setup complete`);
  }

  private setupJest(dir: string): void {
    const content = `module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx)',
    '**/?(*.)+(spec|test).+(ts|tsx)'
  ],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest'
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.tsx',
    '!src/main.tsx'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  moduleNameMapper: {
    '\\\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts']
};
`;

    const setupTests = `import '@testing-library/jest-dom';

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock scrollTo
window.scrollTo = jest.fn();
`;

    fs.writeFileSync(path.join(dir, 'jest.config.js'), content);
    fs.writeFileSync(path.join(dir, 'src', 'setupTests.ts'), setupTests);
  }

  private setupVitest(dir: string): void {
    const content = `import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        'src/main.tsx',
      ],
    },
  },
});
`;

    fs.writeFileSync(path.join(dir, 'vitest.config.ts'), content);
  }

  private setupPlaywright(dir: string): void {
    const content = `import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
`;

    fs.writeFileSync(path.join(dir, 'playwright.config.ts'), content);
  }

  private createTestUtils(dir: string): void {
    const content = `import { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const Wrapper = ({ children }: { children: React.ReactNode }) => {
    return <BrowserRouter>{children}</BrowserRouter>;
  };

  return render(ui, { wrapper: Wrapper, ...options });
};

export * from '@testing-library/react';
export { customRender as render };
`;

    fs.writeFileSync(path.join(dir, 'src', 'test', 'utils.tsx'), content);
  }

  private createMocks(dir: string): void {
    const content = `export const mockUser = {
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  avatar: 'https://i.pravatar.cc/150?img=1',
  createdAt: '2024-01-01T00:00:00Z',
};

export const mockUsers = Array.from({ length: 10 }, (_, i) => ({
  ...mockUser,
  id: i + 1,
  email: \`user\${i + 1}@example.com\`,
  name: \`User \${i + 1}\`,
}));

export const mockApiResponse = (data: any) => ({
  data,
  message: 'Success',
  meta: {
    page: 1,
    pageSize: 20,
    total: data.length,
  },
});
`;

    fs.writeFileSync(path.join(dir, 'src', 'test', 'mocks.ts'), content);
  }
}

const args = process.argv.slice(2);
const framework = args[0] || 'jest';

const setup = new TestingSetup();
setup.setup('.', framework as any);
