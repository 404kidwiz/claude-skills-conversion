import * as fs from 'fs';
import * as path from 'path';

class BuildOptimizer {
  optimize(outputDir: string, bundler: 'vite' | 'webpack'): void {
    switch (bundler) {
      case 'vite':
        this.optimizeVite(outputDir);
        break;
      case 'webpack':
        this.optimizeWebpack(outputDir);
        break;
    }

    this.createEnvironmentConfigs(outputDir);
    this.updatePackageScripts(outputDir);

    console.log(`✓ ${bundler} build optimization complete`);
  }

  private optimizeVite(dir: string): void {
    const content = `import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [
    react({
      jsxImportSource: '@emotion/react',
      babel: {
        plugins: ['@emotion/babel-plugin'],
      },
    }),
  ],

  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['@mui/material', '@mui/icons-material'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  server: {
    port: 3000,
    host: true,
    open: true,
  },
});
`;

    fs.writeFileSync(path.join(dir, 'vite.config.ts'), content);
  }

  private optimizeWebpack(dir: string): void {
    const content = `const path = require('path');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  entry: path.resolve(__dirname, 'src/index.tsx'),
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    chunkFilename: '[name].[contenthash].js',
    clean: true,
  },

  optimization: {
    minimize: true,
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\\\/]node_modules[\\\\/]/,
          name: 'vendors',
          priority: 10,
        },
        common: {
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
        },
      },
    },
    runtimeChunk: 'single',
  },

  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
    }),
  ],
};
`;

    fs.writeFileSync(path.join(dir, 'webpack.config.js'), content);
  }

  private createEnvironmentConfigs(dir: string): void {
    const devEnv = `VITE_API_URL=http://localhost:3000/api
VITE_APP_NAME=My App
VITE_ENABLE_DEBUG=true`;

    const prodEnv = `VITE_API_URL=https://api.example.com
VITE_APP_NAME=My App
VITE_ENABLE_DEBUG=false`;

    fs.writeFileSync(path.join(dir, '.env.development'), devEnv);
    fs.writeFileSync(path.join(dir, '.env.production'), prodEnv);
    fs.writeFileSync(
      path.join(dir, '.env.example'),
      `VITE_API_URL=your-api-url
VITE_APP_NAME=Your App
VITE_ENABLE_DEBUG=true/false`
    );
  }

  private updatePackageScripts(dir: string): void {
    const packageJsonPath = path.join(dir, 'package.json');

    if (fs.existsSync(packageJsonPath)) {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
      packageJson.scripts = {
        ...packageJson.scripts,
        'build:analyze': 'ANALYZE=true npm run build',
        'preview': 'vite preview',
      };
      fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
    }
  }
}

const args = process.argv.slice(2);
const bundler = args[0] || 'vite';

const optimizer = new BuildOptimizer();
optimizer.optimize('.', bundler as any);
