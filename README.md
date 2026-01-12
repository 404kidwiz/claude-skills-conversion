# Development Tooling and Automation Framework

Comprehensive collection of scripts, references, and documentation for modern software development workflows.

## Skills Overview

This framework includes three main development skills:

### 1. Backend Developer (`backend-developer-skill/`)
Tools and references for building production-ready server-side applications.

**Features:**
- Multi-framework API scaffolding (Express, FastAPI, Django, Spring Boot)
- Database model generation (Sequelize, TypeORM, SQLAlchemy, Django ORM, JPA)
- Authentication/authorization templates (JWT, OAuth2, Session)
- Input validation middleware
- Error handling patterns
- Logging and monitoring setup
- API documentation generation (OpenAPI/Swagger)
- Unit test templates
- Deployment scripts (Docker, Kubernetes, AWS, GCP)

**Scripts:**
- `scripts/scaffold_api.py` - API scaffolding
- `scripts/generate_model.py` - Database model generation
- `scripts/setup_auth.py` - Authentication setup
- `scripts/create_middleware.py` - Middleware generation
- `scripts/error_handler.py` - Error handling
- `scripts/setup_logging.py` - Logging configuration
- `scripts/generate_docs.py` - API documentation
- `scripts/create_tests.py` - Test templates
- `scripts/deploy.sh` - Deployment automation

**References:**
- `references/api_patterns.md` - REST API patterns and best practices
- `references/backend_frameworks.md` - Framework guides (Express, FastAPI, Django, Spring Boot)
- `references/testing_strategies.md` - Testing strategies and patterns
- `references/deployment_guide.md` - Deployment strategies and configurations

### 2. Frontend Developer (`frontend-developer-skill/`)
Tools and references for building modern, performant web applications.

**Features:**
- React component scaffolding with hooks
- State management setup (Redux, Zustand, Context API, Jotai, Recoil)
- API client generation (Axios, Fetch)
- CSS-in-JS utility patterns
- TypeScript configuration
- Linting and formatting setup (ESLint, Prettier)
- Testing setup (Vitest, Jest, Playwright)
- Build optimization (Vite, Webpack)
- Deployment scripts (Vercel, Netlify, AWS, GitHub Pages)

**Scripts:**
- `scripts/scaffold_component.tsx` - React component scaffolding
- `scripts/setup_state.ts` - State management setup
- `scripts/create_api_client.ts` - API client generation
- `scripts/create_utils.ts` - Utility functions generation
- `scripts/setup_linting.ts` - Linting and formatting setup
- `scripts/setup_testing.ts` - Testing configuration
- `scripts/optimize_build.ts` - Build optimization
- `scripts/deploy.sh` - Frontend deployment

**References:**
- `references/react_patterns.md` - React component patterns and hooks
- `references/state_management.md` - State management comparison and usage
- `references/performance_guide.md` - Performance optimization strategies
- `references/frontend_tooling.md` - Frontend development tools and workflows

### 3. Build Engineer (`build-engineer-skill/`)
Tools and references for configuring, optimizing, and managing build systems.

**Features:**
- Webpack configuration generator
- Vite configuration generator
- esbuild configuration
- Turbopack setup
- Build cache optimization
- Code splitting strategies
- Bundle size analysis
- Incremental build setup
- TypeScript compilation optimization
- Babel configuration
- PostCSS/Tailwind integration
- Development server setup
- Production build optimization

**Scripts:**
- `scripts/config_webpack.py` - Webpack configuration
- `scripts/config_vite.py` - Vite configuration
- `scripts/config_esbuild.py` - esbuild configuration
- `scripts/optimize_cache.py` - Cache optimization
- `scripts/code_splitting.py` - Code splitting strategies
- `scripts/analyze_bundle_size.py` - Bundle analysis
- `scripts/setup_incremental.py` - Incremental builds
- `scripts/optimize_typescript.py` - TypeScript optimization
- `scripts/config_babel.py` - Babel configuration
- `scripts/integrate_postcss.py` - PostCSS integration
- `scripts/setup_tailwind.py` - Tailwind CSS setup
- `scripts/dev_server.py` - Development server
- `scripts/optimize_production.py` - Production optimization

**References:**
- `references/bundler_guide.md` - Bundler comparison and configuration
- `references/optimization_strategies.md` - Build optimization techniques
- `references/framework_selection.md` - Framework selection guide
- `references/plugin_development.md` - Plugin development guide

## Quick Start

### Backend Developer

```bash
# Scaffold a new Express API
cd backend-developer-skill
python scripts/scaffold_api.py express my-api

# Setup authentication
python scripts/setup_auth.py express jwt

# Generate database models
python scripts/generate_model.py typeorm --schema schema.json --output src/models

# Create tests
python scripts/create_tests.py express --output tests

# Deploy
cd my-api
./scripts/deploy.sh --platform kubernetes
```

### Frontend Developer

```bash
# Create a React component
cd frontend-developer-skill
ts-node scripts/scaffold_component.tsx UserProfile --hooks=useState,useEffect

# Setup state management
ts-node scripts/setup_state.ts User redux

# Generate API client
ts-node scripts/create_api_client.ts axios

# Setup testing
ts-node scripts/setup_testing.ts vitest

# Deploy
./scripts/deploy.sh --platform vercel
```

### Build Engineer

```bash
# Configure Vite
cd build-engineer-skill
python scripts/config_vite.py --framework react --port 3000

# Setup caching
python scripts/optimize_cache.py

# Configure code splitting
python scripts/code_splitting.py --type vite

# Optimize for production
python scripts/optimize_production.py
```

## Architecture

### Script Features

All scripts include:
- **Error handling and logging** - Comprehensive error handling with informative messages
- **Configuration file support** - JSON/YAML configuration files
- **Input validation** - Validate all inputs before processing
- **Modular design** - Reusable functions and utilities
- **Type safety** - TypeScript where applicable
- **Clear documentation** - Inline comments and help text
- **Security best practices** - No hardcoded secrets, secure defaults

### Reference Documentation

All references include:
- **Quick start guide** - Get started quickly with examples
- **Code patterns** - Reusable patterns and best practices
- **API design guidelines** - RESTful API design principles
- **Framework-specific guides** - Detailed framework documentation
- **Testing strategies** - Comprehensive testing approaches
- **Troubleshooting section** - Common issues and solutions

## Integration

### Combined Workflow

```bash
# 1. Create backend
cd backend-developer-skill
python scripts/scaffold_api.py express my-api
cd my-api
python scripts/setup_auth.py express jwt

# 2. Create frontend
cd ../frontend-developer-skill
ts-node scripts/setup_state.ts User redux
ts-node scripts/create_api_client.ts axios
cd my-frontend

# 3. Configure build
cd ../build-engineer-skill
python scripts/config_vite.py --framework react
python scripts/optimize_cache.py
```

### CI/CD Integration

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Backend Tests
        run: |
          cd backend-developer-skill
          python scripts/create_tests.py express
          npm test
      - name: Frontend Tests
        run: |
          cd frontend-developer-skill
          ts-node scripts/setup_testing.ts vitest
          npm test
      - name: Build
        run: |
          cd build-engineer-skill
          python scripts/optimize_production.py
          npm run build
```

## Best Practices

### Development

1. **Use version control** - All code should be in Git
2. **Write tests** - Use generated test templates
3. **Document code** - Follow documentation patterns
4. **Use type safety** - Leverage TypeScript
5. **Follow patterns** - Use provided code patterns

### Build Process

1. **Optimize builds** - Use provided optimization scripts
2. **Implement caching** - Speed up build times
3. **Code splitting** - Reduce initial bundle size
4. **Minify output** - Reduce bundle size
5. **Analyze bundles** - Identify optimization opportunities

### Deployment

1. **Test thoroughly** - Run all tests before deployment
2. **Use environment variables** - Never hardcode secrets
3. **Implement health checks** - Monitor application health
4. **Use CI/CD** - Automate deployment pipeline
5. **Monitor production** - Set up monitoring and alerts

## Troubleshooting

### Common Issues

**Script permissions:**
```bash
chmod +x scripts/*.py
chmod +x scripts/*.sh
```

**Dependencies not found:**
```bash
# Python
pip install -r requirements.txt

# Node.js
npm install
```

**Build failures:**
```bash
# Clear cache
rm -rf node_modules .cache

# Reinstall dependencies
npm install

# Rebuild
npm run build
```

## Contributing

To add new features:

1. Create new script in `scripts/` directory
2. Follow existing script structure
3. Include error handling and logging
4. Add documentation in `references/` directory
5. Update relevant SKILL.md

## License

MIT License - Feel free to use and modify for your projects.

## Support

For issues or questions:
1. Check SKILL.md for detailed instructions
2. Review references for best practices
3. Check script help text with `-h` or `--help`
4. Review example usage in documentation

## Resources

- [Backend Developer SKILL.md](backend-developer-skill/SKILL.md)
- [Frontend Developer SKILL.md](frontend-developer-skill/SKILL.md)
- [Build Engineer SKILL.md](build-engineer-skill/SKILL.md)
