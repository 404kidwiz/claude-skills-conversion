# Build Optimization Strategies

## Overview

Build optimization is crucial for delivering fast, efficient web applications. This guide covers comprehensive optimization strategies across the build pipeline.

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

### Component-based Splitting

```typescript
import { lazy, Suspense } from 'react';

const HeavyChart = lazy(() => import('./HeavyChart'));

export const Dashboard = () => {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <button onClick={() => setShowChart(true)}>
        Show Chart
      </button>
      {showChart && (
        <Suspense fallback={<Loading />}>
          <HeavyChart />
        </Suspense>
      )}
    </div>
  );
};
```

### Vendor Splitting

```javascript
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
        },
      },
    },
  },
};
```

## Tree Shaking

### ES Modules

```javascript
//GOOD - ES modules
export { func1, func2 } from './utils';

// BAD - CommonJS
module.exports = { func1, func2 };
```

### Package.json Side Effects

```json
{
  "sideEffects": false,
  "sideEffects": ["*.css", "./src/**/*.scss"]
}
```

### Webpack Configuration

```javascript
module.exports = {
  optimization: {
    usedExports: true,
    sideEffects: true,
  },
};
```

## Minification

### JavaScript

```javascript
// Terser configuration
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
            pure_funcs: ['console.log'],
            dead_code: true,
            unused: true,
          },
          mangle: {
            safari10: true,
          },
        },
      }),
    ],
  },
};
```

### CSS

```javascript
// CSS Nano configuration
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  optimization: {
    minimizer: [
      new CssMinimizerPlugin({
        minimizerOptions: {
          preset: [
            'default',
            {
              discardComments: { removeAll: true },
              normalizeWhitespace: true,
              minifyFontValues: true,
            },
          ],
        },
      }),
    ],
  },
};
```

### HTML

```javascript
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  plugins: [
    new HtmlWebpackPlugin({
      minify: {
        removeComments: true,
        collapseWhitespace: true,
        removeAttributeQuotes: true,
        minifyJS: true,
        minifyCSS: true,
      },
    }),
  ],
};
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
      generateStatsFile: true,
      statsFilename: 'bundle-stats.json',
    }),
  ],
};
```

### Source Map Explorer

```bash
npm run build
npm run build:analyze
```

## Asset Optimization

### Images

```javascript
const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');

module.exports = {
  module: {
    rules: [
      {
        test: /\.(jpe?g|png|gif|svg)$/i,
        type: 'asset',
        parser: {
          dataUrlCondition: {
            maxSize: 8 * 1024,
          },
        },
        generator: {
          filename: 'images/[name].[contenthash][ext]',
        },
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

### Fonts

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource',
        generator: {
          filename: 'fonts/[name][ext]',
        },
      },
    ],
  },
};
```

### SVG Optimization

```javascript
const SvgrWebpackPlugin = require('svg-sprite-loader');

module.exports = {
  module: {
    rules: [
      {
        test: /\.svg$/,
        use: ['@svgr/webpack'],
      },
    ],
  },
};
```

## Caching

### File System Cache

```javascript
module.exports = {
  cache: {
    type: 'filesystem',
    cacheDirectory: '.webpack_cache',
    maxAge: 1000 * 60 * 60 * 24 * 7, // 1 week
    compression: 'gzip',
  },
};
```

### Babel Cache

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        use: {
          loader: 'babel-loader',
          options: {
            cacheDirectory: true,
            cacheCompression: true,
          },
        },
      },
    ],
  },
};
```

### Persistent Build

```javascript
module.exports = {
  snapshot: {
    managedPaths: [path.join(process.cwd(), 'node_modules')],
    immutablePaths: [],
    buildDependencies: {
      config: [__filename],
    },
  },
};
```

## Performance Monitoring

### Build Metrics

```javascript
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      reportFilename: './bundle-report.html',
      generateStatsFile: true,
      statsOptions: { source: false },
    }),
  ],
};
```

### Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI

on: [push]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v3
        with:
          urls: |
            https://example.com
          uploadArtifacts: true
          temporaryPublicStorage: true
```

## Environment-specific Optimization

### Development

```javascript
module.exports = {
  mode: 'development',
  devtool: 'eval-cheap-module-source-map',
  
  optimization: {
    runtimeChunk: true,
    removeAvailableModules: false,
    removeEmptyChunks: false,
    splitChunks: false,
  },
  
  cache: {
    type: 'memory',
  },
};
```

### Production

```javascript
module.exports = {
  mode: 'production',
  devtool: 'source-map',
  
  optimization: {
    minimize: true,
    nodeEnv: 'production',
    
    splitChunks: {
      chunks: 'all',
      maxInitialRequests: 25,
      minSize: 20000,
    },
    
    runtimeChunk: 'single',
  },
  
  performance: {
    hints: 'warning',
    maxEntrypointSize: 512000,
    maxAssetSize: 512000,
  },
};
```

## Advanced Strategies

### DLL Plugin for Dependencies

```javascript
const webpack = require('webpack');
const path = require('path');

module.exports = {
  entry: {
    vendor: ['react', 'react-dom', 'react-router-dom'],
  },
  output: {
    path: path.join(__dirname, 'dll'),
    filename: '[name].dll.js',
    library: '[name]_library',
  },
  plugins: [
    new webpack.DllPlugin({
      name: '[name]_library',
      path: path.join(__dirname, 'dll', '[name]-manifest.json'),
    }),
  ],
};
```

### Module Federation

```javascript
const ModuleFederationPlugin = require('webpack').container
  .ModuleFederationPlugin;

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'app1',
      filename: 'remoteEntry.js',
      exposes: {
        './Button': './src/Button',
      },
      shared: {
        react: { singleton: true, eager: true },
        'react-dom': { singleton: true, eager: true },
      },
    }),
  ],
};
```

### Preloading & Prefetching

```typescript
// Preload critical resources
<link rel="preload" href="/styles/main.css" as="style">
<link rel="preload" href="/fonts/main.woff2" as="font" crossorigin>

// Prefetch likely next navigation
<link rel="prefetch" href="/about.js">
<link rel="prefetch" href="/dashboard.js">
```

## Checklist

### Pre-build
- [ ] Analyze bundle size
- [ ] Identify unused code
- [ ] Review dependencies
- [ ] Set up code splitting strategy
- [ ] Configure compression

### During Build
- [ ] Enable minification
- [ ] Configure source maps
- [ ] Set up caching
- [ ] Enable tree shaking
- [ ] Optimize assets

### Post-build
- [ ] Review bundle reports
- [ ] Test loading performance
- [ ] Verify source maps work
- [ ] Check Lighthouse scores
- [ ] Monitor production metrics

### Continuous
- [ ] Track bundle size over time
- [ ] Monitor build times
- [ ] Review Lighthouse CI results
- [ ] Update dependencies regularly
- [ ] Review optimization strategies
