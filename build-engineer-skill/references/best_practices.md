# Build Engineer - Best Practices

This guide outlines best practices for build system configuration, optimization, code splitting, and deployment.

## Core Principles

### Fast Builds

- Enable caching (file system, Babel cache, persistent cache)
- Use parallel processing where possible
- Optimize build configuration for minimal overhead
- Use modern, fast bundlers (Vite, esbuild, Turbopack)
- Monitor build times and optimize bottlenecks

### Small Bundles

- Implement code splitting strategies
- Tree shake unused code
- Compress output (minification, gzip, brotli)
- Use dynamic imports for lazy loading
- Analyze bundle sizes regularly
- Remove unused dependencies

### Developer Experience

- Fast HMR (Hot Module Replacement)
- Clear error messages with source maps
- Easy local development setup
- Proxy configuration for API calls
- Environment variable management
- Source map generation for debugging

## Build Tool Selection

### Tool Comparison

| Tool | Strengths | Use Cases |
|------|-------------|------------|
| Webpack | Highly configurable, huge ecosystem | Complex builds, legacy projects |
| Vite | Fast, HMR, simple config | Modern projects, Vue/React |
| esbuild | Extremely fast, minimal config | Production builds, simple projects |
| Turbopack | Next-gen, Rust-based | New projects, performance-critical |
| Rollup | Great for libraries | Package/library development |
| Parcel | Zero-config, fast | Quick prototyping, small projects |

### When to Use Each

- **Webpack**: Complex enterprise applications, legacy migrations
- **Vite**: Modern web apps, Vue/React projects, DX priority
- **esbuild**: Production builds, performance-critical, simple setups
- **Turbopack**: New projects, performance experimentation, early adopters
- **Rollup**: Library/package development, tree shaking focus
- **Parcel**: Quick prototypes, learning projects, zero-config needs

## Webpack Configuration

### Optimizations

#### Performance

```javascript
module.exports = {
  cache: {
    type: 'filesystem',
    cacheDirectory: '.webpack_cache',
  },
  parallelism: true, // Use all CPU cores
  stats: {
    preset: 'minimal', // Reduce output
  },
}
```

#### Code Splitting

```javascript
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
        common: {
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
        },
      },
    },
  },
}
```

### Loaders

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
}
```

## Vite Configuration

### Optimizations

#### Build Options

```typescript
export default defineConfig({
  build: {
    minify: 'terser',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },
})
```

#### Performance

```typescript
export default defineConfig({
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
  server: {
    hmr: {
      overlay: true,
    },
  },
})
```

### Plugins

```typescript
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      open: false,
      gzipSize: true,
    }),
  ],
})
```

## Code Splitting Strategies

### Route-Based Splitting

- Lazy load route components
- Use React.lazy() or similar
- Benefits: Faster initial load, parallel downloads

```typescript
const Home = lazy(() => import('./pages/Home'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
```

### Component-Based Splitting

- Lazy load heavy components
- Use dynamic imports
- Benefits: Load components on demand

```typescript
const HeavyChart = lazy(() => import('./components/HeavyChart'));
```

### Vendor Splitting

- Separate third-party libraries
- Cache vendor chunks separately
- Benefits: Better caching, faster rebuilds

```javascript
// Webpack
splitChunks: {
  cacheGroups: {
    vendor: {
      test: /[\\/]node_modules[\\/]/,
      name: 'vendors',
    },
  },
}
```

### Library Splitting

- Split large libraries (React, Vue, etc.)
- Load from CDN when possible
- Benefits: Smaller bundle, CDN caching

## Caching Strategies

### Webpack Caching

#### File System Cache

```javascript
module.exports = {
  cache: {
    type: 'filesystem',
    cacheDirectory: '.webpack_cache',
    maxAge: 604800000, // 1 week
  },
}
```

#### Babel Cache

```javascript
{
  test: /\.(js|jsx)$/,
  use: {
    loader: 'babel-loader',
    options: {
      cacheDirectory: true,
    },
  },
}
```

### Vite Caching

```typescript
export default defineConfig({
  cacheDir: './node_modules/.vite',
  optimizeDeps: {
    force: false, // Only re-optimizes on change
  },
})
```

### Persistent Cache

- Use browser caching headers
- Implement service workers
- Use CDN caching for static assets
- Set appropriate cache timeouts
- Cache bust with content hash

## Production Optimization

### Minification

- Use Terser for JavaScript minification
- Use cssnano for CSS optimization
- Enable dead code elimination
- Remove console.log in production
- Minify HTML with html-minifier

### Asset Optimization

- Compress images (ImageMin, imagemin)
- Use modern image formats (WebP, AVIF)
- SVG optimization (svgo)
- Font subsetting
- Inline small assets when beneficial

### Bundle Analysis

- Use webpack-bundle-analyzer
- Use rollup-plugin-visualizer for Vite
- Analyze bundle size composition
- Identify large dependencies
- Find optimization opportunities

```javascript
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer');

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
    }),
  ],
}
```

## Development Experience

### Hot Module Replacement (HMR)

- Enable HMR for fast feedback
- Preserve state during HMR when possible
- Use overlay for build errors
- Configure HMR timeout appropriately
- Handle HMR errors gracefully

### Dev Server Configuration

```javascript
// Webpack
devServer: {
  port: 3000,
  hot: true,
  open: false,
  proxy: {
    '/api': {
      target: 'http://localhost:4000',
      changeOrigin: true,
    },
  },
}

// Vite
server: {
  port: 3000,
  open: false,
  proxy: {
    '/api': {
      target: 'http://localhost:4000',
      changeOrigin: true,
    },
  },
}
```

### Source Maps

- Use `source-map` for production
- Use `eval-source-map` for development
- Exclude source maps from production bundle
- Configure source map hosting
- Consider security implications

## Performance Monitoring

### Build Time Monitoring

- Track build time in CI/CD
- Alert on build time degradation
- Optimize slow build steps
- Cache dependencies to reduce build time
- Monitor for build time regressions

### Bundle Size Monitoring

- Track bundle sizes over time
- Alert on size increases
- Set size budgets in config
- Monitor individual chunk sizes
- Track total bundle size

### Runtime Performance

- Monitor Time to Interactive (TTI)
- Track Lighthouse scores
- Monitor Core Web Vitals
- Track JavaScript execution time
- Monitor bundle parse time

## Dependency Management

### Dependency Auditing

```bash
# Check for vulnerabilities
npm audit

# Fix vulnerabilities
npm audit fix

# Check outdated packages
npm outdated

# Update packages
npm update
```

### Dependency Optimization

- Remove unused dependencies
- Use smaller alternatives when possible
- Bundle critical dependencies
- Use tree shaking for conditional imports
- Consider CDN for large libraries

## Environment Configuration

### Environment Variables

- Use .env files for local development
- Load environment variables in build
- Document required variables
- Validate configuration on startup
- Never commit .env files

### Multi-Environment Configs

```javascript
// webpack.config.js
const isProduction = process.env.NODE_ENV === 'production';

module.exports = {
  mode: isProduction ? 'production' : 'development',
  // Environment-specific config
};
```

## Testing Build Configs

### Configuration Validation

- Test config in multiple environments
- Verify all plugins load correctly
- Check loaders resolve files
- Test with sample files
- Validate source map generation

### Build Testing

- Test production build locally
- Verify all assets are generated
- Test in staging environment
- Test with real user data
- Verify CDN uploads work

## CI/CD Integration

### Build Caching

```yaml
# GitHub Actions example
- name: Cache node modules
  uses: actions/cache@v2
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

### Parallel Builds

- Run test and build in parallel
- Use matrix builds for multiple configurations
- Split long builds into stages
- Use build artifacts between stages

### Deployment Automation

- Automated deployment on successful build
- Rollback on deployment failure
- Blue-green deployment strategy
- Canary releases for gradual rollout
- Health checks before routing traffic

## Security Best Practices

### Source Map Security

- Don't expose full source maps in production
- Upload source maps to error tracking services
- Use hidden source maps when needed
- Consider security implications

### Dependency Security

- Regularly audit dependencies
- Fix vulnerabilities promptly
- Review licenses of dependencies
- Use Snyk or Dependabot for alerts
- Patch dependencies automatically in CI/CD

### Build Environment Security

- Use isolated build environments
- Don't expose secrets in build output
- Sanitize environment variables
- Use secure artifact storage
- Verify no secrets in bundles

## Documentation

### Build Documentation

- Document build configuration decisions
- Explain complex optimizations
- Document dependency rationale
- Include troubleshooting steps
- Document environment requirements

### README for Build

- Quick start guide for building
- Development workflow
- Production build instructions
- Common issues and solutions
- Environment variable documentation
- Deployment instructions

## Troubleshooting Build Issues

### Common Patterns

- **Slow builds**: Enable caching, check for unnecessary plugins
- **Large bundles**: Analyze with bundle analyzer, implement splitting
- **HMR not working**: Check WebSockets, verify config
- **Caching issues**: Clear cache, verify permissions
- **Source maps**: Verify generation, check paths
- **Proxy issues**: Check backend is running, verify CORS

### Debug Tools

- Use `--display-modules` for Webpack
- Use bundle analyzer for Vite
- Check webpack stats for insights
- Use browser DevTools for runtime debugging
- Monitor network tab for asset loading

## Continuous Improvement

### Regular Review

- Review bundle sizes weekly
- Analyze build times monthly
- Review dependency updates quarterly
- Update tools and plugins regularly
- Monitor for new optimization techniques

### Performance Budgets

```javascript
// webpack.config.js
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin({
      defaultSizes: 'gzip',
      analyzerMode: 'static',
      generateStatsFile: true,
      statsOptions: { source: false },
    }),
  ],
  performance: {
    hints: false,
    maxEntrypointSize: 512000, // 500 KB
    maxAssetSize: 512000, // 500 KB
  },
}
```

### Learning from Errors

- Document build errors and solutions
- Create internal knowledge base
- Share solutions with team
- Update scripts based on common issues
- Contribute back to tool communities
