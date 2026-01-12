# Bundler Guide

## Overview

Modern web applications use bundlers to transform, optimize, and bundle source code for browser consumption. This guide covers major bundlers and their configurations.

## Webpack

### Basic Configuration

```javascript
const path = require('path');

module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
  },
  mode: 'production',
};
```

### Loaders

```javascript
module.exports = {
  module: {
    rules: [
      // JavaScript/TypeScript
      {
        test: /\.(ts|tsx|js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              '@babel/preset-env',
              '@babel/preset-react',
              '@babel/preset-typescript',
            ],
          },
        },
      },
      
      // CSS
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
      
      // Images
      {
        test: /\.(png|jpe?g|gif|svg)$/,
        type: 'asset/resource',
      },
      
      // Fonts
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource',
      },
    ],
  },
};
```

### Plugins

```javascript
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');

module.exports = {
  plugins: [
    new CleanWebpackPlugin(),
    
    new HtmlWebpackPlugin({
      template: './public/index.html',
      filename: 'index.html',
      minify: true,
    }),
    
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css',
      chunkFilename: '[name].[contenthash].css',
    }),
  ],
};
```

### Optimization

```javascript
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

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
      new CssMinimizerPlugin(),
    ],
    
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
        },
      },
    },
    
    runtimeChunk: 'single',
  },
};
```

## Vite

### Configuration

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  
  build: {
    outDir: 'dist',
    sourcemap: true,
    
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },
  
  server: {
    port: 3000,
    open: true,
  },
});
```

### Plugins

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import eslint from 'vite-plugin-eslint';
import svgr from 'vite-plugin-svgr';

export default defineConfig({
  plugins: [
    react(),
    eslint(),
    svgr(),
  ],
});
```

### Environment Variables

```typescript
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __API_URL__: JSON.stringify(process.env.VITE_API_URL),
  },
});
```

## esbuild

### Basic Usage

```javascript
const esbuild = require('esbuild');

esbuild.build({
  entryPoints: ['src/index.js'],
  bundle: true,
  outfile: 'dist/bundle.js',
  minify: true,
  sourcemap: true,
  target: 'es2015',
});
```

### Watch Mode

```javascript
esbuild.context({
  entryPoints: ['src/index.js'],
  outfile: 'dist/bundle.js',
  bundle: true,
}).then(ctx => {
  ctx.watch();
});
```

## Turbopack

### Configuration

```javascript
module.exports = {
  experimental: {
    turbo: {},
  },
};
```

### Development Server

```javascript
const { createServer } = require('turbo');

createServer({
  entry: './src/index.js',
  dev: true,
  hmr: true,
});
```

## Comparison

| Feature | Webpack | Vite | esbuild | Turbopack |
|---------|----------|-------|----------|------------|
| Build Speed | Slow | Fast | Very Fast | Very Fast |
| HMR | Good | Excellent | Good | Excellent |
| Ecosystem | Extensive | Growing | Limited | New |
| Configuration | Complex | Simple | Simple | Simple |
| TypeScript | Via loader | Native | Native | Native |
| Learning Curve | High | Low | Low | Low |

## When to Use Which

### Webpack
- Maximum configurability needed
- Advanced optimization required
- Legacy browser support
- Large enterprise applications

### Vite
- Modern browser support
- Fast development experience
- TypeScript-first
- React/Vue/Svelte projects

### esbuild
- Maximum build speed
- Simple projects
- Minimal dependencies
- Build-time transformation only

### Turbopack
- Next.js projects
- Maximum performance
- React-based applications
- Want to stay bleeding-edge

## Best Practices

### Performance

```javascript
// Enable persistent cache
module.exports = {
  cache: {
    type: 'filesystem',
    cacheDirectory: '.webpack_cache',
  },
};
```

### Bundle Size

```javascript
// Analyze bundle size
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

### Development

```javascript
// Fast rebuilds
module.exports = {
  devtool: 'eval-cheap-module-source-map',
  cache: true,
};
```

### Production

```javascript
// Optimize for production
module.exports = {
  mode: 'production',
  optimization: {
    minimize: true,
    usedExports: true,
    sideEffects: true,
  },
};
```
