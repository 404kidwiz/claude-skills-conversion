# Build Engineer - Troubleshooting

This guide helps troubleshoot common issues when using build engineer automation scripts.

## Script Execution Issues

### Python Scripts Not Found

**Problem**: `python scripts/config_webpack.py` returns "No such file or directory"

**Solutions**:
- Verify you're in the correct directory: `cd build-engineer-skill`
- Check scripts directory exists: `ls scripts/`
- Ensure Python 3.7+ is installed: `python --version`

### Missing Dependencies

**Problem**: `ModuleNotFoundError: No module named 'xxx'`

**Solutions**:
- Install required Python dependencies
- Install Node.js packages if needed: `npm install`
- Check package.json for required dependencies
- Review error messages for missing modules

### Permission Denied

**Problem**: `PermissionError: [Errno 13] Permission denied` when writing output files

**Solutions**:
- Check directory permissions: `ls -la scripts/`
- Make scripts executable: `chmod +x scripts/*.py`
- Verify write permissions for output directory
- Use sudo if necessary (not recommended)

## Webpack Configuration Issues

### Webpack Config Not Generated

**Problem**: Webpack configuration file not created

**Solutions**:
- Verify output directory exists: `mkdir -p dist` or use `--output .`
- Check write permissions for output directory
- Review script error messages for specific failures
- Use absolute path for output if relative fails

### Entry Point Not Found

**Problem**: `Entry module not found`

**Solutions**:
- Verify entry file exists: `src/index.tsx` or similar
- Check entry point is correct for your project
- Use `--language` flag to match entry file extension
- Verify project structure matches expected layout

### Loader/Plugin Errors

**Problem**: Cannot resolve loader or plugin

**Solutions**:
- Install missing loader: `npm install ts-loader css-loader`
- Install missing plugin: `npm install html-webpack-plugin`
- Verify loader/plugin is compatible with Webpack version
- Check webpack.config.js for correct syntax

## Vite Configuration Issues

### Vite Config Not Generated

**Problem**: Vite configuration file not created

**Solutions**:
- Verify output directory exists
- Check write permissions
- Review script error messages
- Use absolute path for output if needed

### Framework Plugin Issues

**Problem**: Framework plugin not working

**Solutions**:
- Install framework plugin: `npm install @vitejs/plugin-react`
- Verify framework in config matches installed: `--framework react` requires React plugin
- Check plugin configuration in generated vite.config.ts
- Review Vite documentation for framework-specific setup

### Alias Resolution Fails

**Problem**: Imports using aliases not resolving

**Solutions**:
- Verify alias is configured in vite.config.ts or webpack.config.js
- Check alias target paths exist
- Use absolute paths for alias targets
- Review resolve configuration

## Code Splitting Issues

### Splitting Not Working

**Problem**: Code not being split as expected

**Solutions**:
- Verify splitting type is correct: `route`, `component`, `webpack`, `vite`, `all`
- Check for lazy loading in your code
- Verify dynamic imports are used
- Review splitting configuration in generated config

### Import Errors After Splitting

**Problem**: Cannot find module after code splitting

**Solutions**:
- Check chunk names in config
- Verify publicPath configuration
- Review import statements for dynamic imports
- Check for circular dependencies

### Large Chunk Sizes

**Problem**: Individual chunks still too large

**Solutions**:
- Review vendor chunk configuration
- Check for common chunks configuration
- Analyze bundle with bundle analyzer
- Implement additional splitting strategies

## Caching Issues

### Cache Not Working

**Problem**: Rebuilds are not faster

**Solutions**:
- Verify cache directory is writable
- Check cache configuration in config
- Use `--loader` flag for Babel cache
- Verify Webpack file system cache is enabled
- Check for cache conflicts between projects

### Cache Corruption

**Problem**: Builds fail with cache errors

**Solutions**:
- Clear cache directory: `rm -rf node_modules/.cache` or `rm -rf .webpack_cache`
- Clear browser cache for dev server
- Rebuild without cache
- Disable cache temporarily to test

## Dev Server Issues

### Port Already in Use

**Problem**: `Error: Port 3000 already in use`

**Solutions**:
- Find process using port:
  - Mac/Linux: `lsof -i :3000`
  - Windows: `netstat -ano | findstr :3000`
- Kill process: `kill -9 <PID>`
- Use different port: `--port 3001`
- Wait for previous process to finish

### HMR Not Working

**Problem**: Changes not reflecting automatically

**Solutions**:
- Verify HMR is enabled in config
- Check WebSocket connections are not blocked
- Review firewall settings
- Check for HMR errors in browser console
- Restart dev server if issues persist

### Proxy Configuration Fails

**Problem**: Proxy to backend not working

**Solutions**:
- Verify proxy target URL is correct
- Check backend is running and accessible
- Review proxy configuration in dev server config
- Check for CORS issues
- Test proxy with curl command

## Production Build Issues

### Build Fails

**Problem**: Production build returns errors

**Solutions**:
- Check for TypeScript/ESLint errors
- Review error messages in build output
- Check for missing dependencies
- Verify all imports resolve correctly
- Test in development environment first

### Build Too Slow

**Problem**: Production builds take very long time

**Solutions**:
- Enable caching (file system, Babel cache)
- Use thread-loader or parallel-webpack for parallelism
- Check for excessive source map generation
- Reduce number of plugins
- Consider using esbuild or swc for faster builds

### Large Bundle Size

**Problem**: Final bundle is too large

**Solutions**:
- Analyze bundle with bundle analyzer
- Implement code splitting
- Tree shake unused code
- Compress output (minification, gzip)
- Use dynamic imports for lazy loading
- Review and remove large dependencies

## Common Issues Across All Scripts

### Node.js Version Issues

**Problem**: Scripts fail due to Node.js version

**Solutions**:
- Check Node.js version: `node --version`
- Use nvm to switch Node versions: `nvm use 16`
- Install required Node version if needed
- Review package.json for version requirements

### TypeScript Compilation Errors

**Problem**: TypeScript fails to compile

**Solutions**:
- Check tsconfig.json configuration
- Verify @types packages are installed
- Review type errors in compilation output
- Use `any` type temporarily (not recommended for production)
- Check for circular type references

### CSS Module Issues

**Problem**: CSS imports failing

**Solutions**:
- Configure CSS loaders correctly
- Install required CSS loader: `npm install css-loader style-loader`
- Check for CSS syntax errors
- Verify CSS file paths are correct
- Review webpack.config.js for CSS rules

## Framework-Specific Issues

### React

- Ensure React is installed: `npm install react react-dom`
- Check JSX transformation is configured
- Verify @types/react is installed for TypeScript
- Review React-specific loader configuration

### Vue

- Install Vue loader: `npm install vue-loader`
- Configure Vue-specific rules in webpack
- Check .vue file extension is handled
- Verify Vue template compiler is installed

### Angular

- Use Angular CLI for new projects
- Check for @angular/compiler-cli
- Review Angular webpack configuration
- Verify RxJS and zone.js are installed

## Debug Mode

### Verbose Output

```bash
# Get detailed build information
npm run build --verbose
```

### Source Maps

```bash
# Generate source maps for debugging
# In webpack.config.js
devtool: 'source-map'

# In vite.config.ts
build: {
  sourcemap: true
}
```

### Build Analysis

```bash
# Analyze bundle size
npm run build -- --analyze

# Or use webpack-bundle-analyzer
npm install --save-dev webpack-bundle-analyzer
```

## Getting Help

### Script Help

```bash
# Get help for any script
python scripts/config_webpack.py --help
python scripts/config_vite.py --help
```

### Framework Documentation

- Webpack: https://webpack.js.org/
- Vite: https://vitejs.dev/
- esbuild: https://esbuild.github.io/
- Rollup: https://rollupjs.org/

### Community Resources

- Stack Overflow: Search for specific error messages
- GitHub Issues: Check webpack/vite repositories
- Discord/Slack: Framework-specific communities
- Package documentation: Read npm package docs

## Prevention

### Best Practices

- Always test build in development first
- Use lockfiles (package-lock.json, yarn.lock)
- Pin dependency versions in CI/CD
- Monitor build times
- Keep build tools updated
- Review bundle sizes regularly

### Build Performance

- Enable caching for faster rebuilds
- Use thread-loader for parallelism
- Minimize plugins to reduce complexity
- Use file system cache for production builds
- Consider incremental builds if supported

### Dependency Management

- Audit dependencies regularly: `npm audit`
- Update dependencies with caution: `npm update`
- Remove unused dependencies
- Use peer dependencies correctly
- Document required Node.js versions

## Integration Issues

### CI/CD Integration

**Problem**: Build script works locally but fails in CI/CD

**Solutions**:
- Verify Node.js version in CI/CD matches local
- Check all dependencies are installed in CI/CD
- Review environment variables in CI/CD
- Check for platform-specific issues
- Review CI/CD logs for specific errors

### Docker Builds

**Problem**: Build fails in Docker container

**Solutions**:
- Verify Dockerfile has all dependencies
- Check for platform-specific issues
- Ensure sufficient memory allocation
- Review multi-stage build setup
- Check for permission issues in container

### Asset Optimization

**Problem**: Images or assets not optimized

**Solutions**:
- Install image optimization plugins
- Configure optimization settings
- Check file sizes before and after
- Verify optimization plugins are running
- Review optimization configuration

## Tool-Specific Troubleshooting

### Webpack

- Check webpack.config.js for syntax errors
- Verify loader order is correct
- Review plugins configuration
- Check for circular dependencies
- Use webpack CLI for debugging: `webpack --display-modules`

### Vite

- Check vite.config.ts for errors
- Verify plugins are compatible
- Review resolve configuration
- Check for esbuild errors
- Use Vite debug flag: `vite --debug`

### esbuild

- Check for esbuild version compatibility
- Review esbuild configuration
- Verify plugins are supported
- Check for API limitations
- Review esbuild documentation for specifics
