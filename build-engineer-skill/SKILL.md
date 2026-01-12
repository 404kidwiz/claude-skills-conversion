# Build Engineer Skill

## Overview

The Build Engineer skill provides comprehensive tools and references for configuring, optimizing, and managing build systems for modern web applications. It supports multiple bundlers and optimization strategies.

## Scripts

### Webpack Configuration
```bash
python scripts/config_webpack.py [OPTIONS]

# Options:
# --output <dir>: Output directory (default: .)
# --language <ext>: Entry file extension (default: tsx)
# --port <number>: Dev server port (default: 3000)

# Example: Generate Webpack config
python scripts/config_webpack.py --language tsx --port 3000
```

### Vite Configuration
```bash
python scripts/config_vite.py [OPTIONS]

# Options:
# --output <dir>: Output directory (default: .)
# --framework <name>: Framework (default: react)
# --port <number>: Dev server port (default: 3000)

# Example: Generate Vite config for React
python scripts/config_vite.py --framework react --port 3000
```

### Cache Optimization
```bash
python scripts/optimize_cache.py [OPTIONS]

# Options:
# --output <dir>: Output directory (default: .)
# --loader: Generate cache loader

# Example: Setup caching
python scripts/optimize_cache.py

# Example: Setup with loader
python scripts/optimize_cache.py --loader
```

### Code Splitting
```bash
python scripts/code_splitting.py [OPTIONS]

# Options:
# --output <dir>: Output directory (default: .)
# --type <type>: Splitting type (route, component, webpack, vite, all)

# Example: Generate all splitting configs
python scripts/code_splitting.py --type all

# Example: Generate route splitting
python scripts/code_splitting.py --type route
```

### Development Server
```bash
python scripts/dev_server.py [OPTIONS]

# Options:
# --output <dir>: Output directory (default: .)
# --bundler <name>: Bundler type (vite, webpack)
# --port <number>: Port number (default: 3000)
# --proxy <url>: Proxy target URL

# Example: Setup Vite dev server
python scripts/dev_server.py --bundler vite --port 3000

# Example: Setup Webpack dev server with proxy
python scripts/dev_server.py --bundler webpack --port 3000 --proxy http://localhost:4000
```

### Production Optimization
```bash
python scripts/optimize_production.py [OPTIONS]

# Options:
# --output <dir>: Output directory (default: .)

# Example: Generate production configs
python scripts/optimize_production.py
```

## References

### Bundler Guide (`references/bundler_guide.md`)
- Webpack configuration
- Vite configuration
- esbuild usage
- Turbopack setup
- Loaders and plugins
- Optimization strategies
- Bundle analysis
- Framework comparison
- When to use which bundler
- Best practices

### Optimization Strategies (`references/optimization_strategies.md`)
- Code splitting (route-based, component-based)
- Tree shaking
- Minification (JS, CSS, HTML)
- Bundle analysis
- Asset optimization (images, fonts, SVG)
- Caching strategies (file system, Babel, persistent)
- Performance monitoring
- Environment-specific optimization
- Advanced strategies (DLL, Module Federation)
- Preloading and prefetching

### Framework Selection (`references/framework_selection.md`)
- Decision matrix
- Tool comparison (Webpack, Vite, esbuild, Turbopack, Rollup, Parcel)
- Recommendations by use case
- Project size considerations
- Team size factors
- Technical requirements
- Performance benchmarks
- Migration guides
- Final recommendations

## Quick Start

### Setup Webpack Project

```bash
# 1. Generate Webpack configuration
python scripts/config_webpack.py --language tsx --port 3000

# 2. Setup caching
python scripts/optimize_cache.py --loader

# 3. Configure code splitting
python scripts/code_splitting.py --type webpack

# 4. Setup dev server
python scripts/dev_server.py --bundler webpack --port 3000

# 5. Optimize for production
python scripts/optimize_production.py
```

### Setup Vite Project

```bash
# 1. Generate Vite configuration
python scripts/config_vite.py --framework react --port 3000

# 2. Configure code splitting
python scripts/code_splitting.py --type vite

# 3. Setup dev server
python scripts/dev_server.py --bundler vite --port 3000

# 4. Optimize for production
python scripts/optimize_production.py
```

## Build Configuration

### Webpack

#### Basic Setup
```javascript
const path = require('path');

module.exports = {
  entry: './src/index.tsx',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
  },
  mode: 'production',
};
```

#### Loaders
```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        use: 'ts-loader',
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
};
```

#### Plugins
```javascript
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
  ],
};
```

### Vite

#### Basic Setup
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
  },
});
```

#### Aliases
```typescript
export default defineConfig({
  resolve: {
    alias: {
      '@': '/src',
    },
  },
});
```

## Code Splitting

### Route-based Splitting

```typescript
import { lazy, Suspense } from 'react';

const Home = lazy(() => import('./pages/Home'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

export const App = () => (
  <Suspense fallback={<Loading />}>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  </Suspense>
);
```

### Vendor Splitting

```javascript
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
        },
      },
    },
  },
};
```

## Caching

### Webpack File System Cache

```javascript
module.exports = {
  cache: {
    type: 'filesystem',
    cacheDirectory: '.webpack_cache',
  },
};
```

### Vite Dependency Cache

```typescript
export default defineConfig({
  optimizeDeps: {
    cacheDir: './node_modules/.vite',
  },
});
```

## Bundle Analysis

### Webpack Bundle Analyzer

```javascript
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer');

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
    }),
  ],
};
```

### Vite Rollup Visualizer

```typescript
import { defineConfig } from 'vite';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    visualizer({
      open: false,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
});
```

## Performance Optimization

### Minification

```javascript
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
          },
        },
      }),
    ],
  },
};
```

### Asset Optimization

```javascript
const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');

module.exports = {
  module: {
    rules: [
      {
        test: /\.(jpe?g|png|gif|svg)$/i,
        use: [
          {
            loader: ImageMinimizerPlugin.loader,
            options: {
              minimizer: {
                implementation: ImageMinimizerPlugin.imageminGenerate,
                options: {
                  plugins: [
                    ['imagemin-mozjpeg', { quality: 75 }],
                    ['imagemin-pngquant', { quality: [0.65, 0.9] }],
                  ],
                },
              },
            },
          },
        ],
      },
    ],
  },
};
```

## Development Workflow

### Start Development Server

```bash
# Webpack
webpack serve --config webpack.dev.config.js

# Vite
vite

# With proxy
vite --proxy http://localhost:3000
```

### Build for Production

```bash
# Webpack
webpack --mode production

# Vite
vite build

# With analysis
ANALYZE=true npm run build
```

### Watch Mode

```bash
# Webpack
webpack --watch

# Vite
vite --watch
```

## Best Practices

1. **Choose the right bundler** - Consider project size and team needs
2. **Implement code splitting** - Reduce initial bundle size
3. **Enable caching** - Speed up rebuild times
4. **Minify output** - Reduce bundle size
5. **Optimize assets** - Compress images and fonts
6. **Use source maps** - Aid debugging
7. **Analyze bundles** - Identify large dependencies
8. **Configure environment variables** - Manage different environments
9. **Set up proxy** - Avoid CORS issues
10. **Monitor performance** - Track build times and bundle sizes

## Common Issues

### Slow Builds
- Enable caching
- Use DLL plugin
- Check for unnecessary plugins
- Review bundle size

### Large Bundle Size
- Implement code splitting
- Remove unused dependencies
- Use tree shaking
- Optimize images
- Minimize code

### HMR Not Working
- Check dev server configuration
- Verify HMR is enabled
- Review firewall settings
- Check for WebSocket issues

### Build Failures
- Review error messages
- Check configuration syntax
- Verify dependencies
- Clean cache

## Troubleshooting

### Webpack

**Common Issues:**
- Module resolution failures
- Circular dependencies
- Memory issues
- Slow builds

**Solutions:**
- Check resolve configuration
- Use circular-dependency-plugin
- Increase memory limit
- Enable caching

### Vite

**Common Issues:**
- HMR not working
- Alias not resolving
- Plugin conflicts

**Solutions:**
- Check server configuration
- Verify alias configuration
- Review plugin compatibility

## Resources

- [Webpack Documentation](https://webpack.js.org/)
- [Vite Documentation](https://vitejs.dev/)
- [esbuild Documentation](https://esbuild.github.io/)
- [Rollup Documentation](https://rollupjs.org/)
- [Parcel Documentation](https://parceljs.org/)
- [Turbopack Documentation](https://turbo.build/pack)

## Included Automation Scripts

The build engineer skill includes comprehensive automation scripts located in `scripts/`:

- **config_webpack.py**: Webpack configuration generation with loaders, plugins, optimization, and dev server setup
- **config_vite.py**: Vite configuration generation for React, Vue, and vanilla JavaScript with plugins and aliases
- **optimize_cache.py**: Cache optimization setup with file system cache, Babel cache, and persistent cache configuration
- **code_splitting.py**: Code splitting configuration for route-based, component-based, vendor splitting, and library chunking
- **dev_server.py**: Development server setup for Webpack and Vite with HMR, proxy configuration, and port customization
- **optimize_production.py**: Production optimization configuration with minification, asset optimization, and bundle analysis

## References

### Reference Documentation (`references/` directory)
- **troubleshooting.md**: Troubleshooting guide for build system issues including slow builds, bundle size problems, HMR failures, and deployment issues
- **best_practices.md**: Best practices for build configuration, optimization strategies, code splitting, and caching