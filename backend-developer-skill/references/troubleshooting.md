# Backend Developer - Troubleshooting

This guide helps troubleshoot common issues when using backend developer automation scripts.

## Script Execution Issues

### Python Scripts Not Found

**Problem**: `python scripts/scaffold_api.py` returns "No such file or directory"

**Solutions**:
- Verify you're in the correct directory: `cd backend-developer-skill`
- Check scripts directory exists: `ls scripts/`
- Ensure Python 3.7+ is installed: `python --version`

### Framework Dependencies Not Installed

**Problem**: `ModuleNotFoundError: No module named 'fastapi'` or similar

**Solutions**:
- Install required framework: `pip install fastapi express django flask`
- Install development dependencies: `pip install -r requirements.txt` (if exists)
- Check framework-specific requirements:
  - FastAPI: `pip install fastapi uvicorn`
  - Django: `pip install django django-rest-framework`
  - Express: `npm install express` (Node.js)
  - Spring: Requires Java/Maven setup

### Permission Denied

**Problem**: `PermissionError: [Errno 13] Permission denied` when creating files

**Solutions**:
- Check directory permissions: `ls -la scripts/`
- Verify write permissions for output directory
- Use sudo if necessary (not recommended): `sudo python scripts/scaffold_api.py`
- Create output directory if it doesn't exist

## API Scaffolding Issues

### Invalid Framework

**Problem**: Framework not recognized

**Solutions**:
- Use supported frameworks: `express`, `fastapi`, `django`, `spring`
- Check spelling and case sensitivity
- Review supported frameworks in scaffold_api.py

### Project Creation Fails

**Problem**: Project directory not created or incomplete

**Solutions**:
- Check available disk space: `df -h`
- Verify directory doesn't already exist
- Run with verbose mode if available: `--verbose`
- Check for permission issues

### Missing Dependencies

**Problem**: Generated project fails to run due to missing dependencies

**Solutions**:
- Install all dependencies listed in generated requirements.txt/package.json
- Check for version conflicts: `pip list` or `npm list`
- Use virtual environments: `python -m venv venv` or `npm install`
- Review generated installation instructions

## Model Generation Issues

### Invalid ORM

**Problem**: `ValueError: Unknown ORM`

**Solutions**:
- Use supported ORMs: `sequelize`, `typeorm`, `sqlalchemy`, `django`, `jpa`
- Check spelling and case sensitivity
- Review supported ORMs in generate_model.py

### Schema Parsing Fails

**Problem**: Schema file cannot be parsed

**Solutions**:
- Verify schema file format (JSON/YAML)
- Check schema file is valid JSON/YAML
- Use proper schema structure
- Test schema with online validator

### Output Directory Issues

**Problem**: Models not written to output directory

**Solutions**:
- Create output directory if it doesn't exist: `mkdir -p src/models`
- Check write permissions
- Verify output path is correct
- Use absolute paths if relative paths fail

## Authentication Setup Issues

### Invalid Auth Type

**Problem**: Auth type not recognized

**Solutions**:
- Use supported types: `jwt`, `oauth2`, `session`
- Check spelling and case sensitivity
- Review supported types in setup_auth.py

### Framework Compatibility

**Problem**: Auth setup fails for specific framework

**Solutions**:
- Verify framework supports selected auth type
- Check framework compatibility matrix:
  - Express: JWT, OAuth2, Session
  - FastAPI: JWT, OAuth2
  - Django: JWT, OAuth2, Session
  - Spring: JWT, OAuth2

### Secret Configuration

**Problem**: JWT secret or OAuth credentials missing

**Solutions**:
- Generate JWT secret: `openssl rand -base64 32`
- Create .env file with secrets
- Add .env to .gitignore
- Set environment variables: `export JWT_SECRET=your_secret`

## Middleware Issues

### Invalid Framework

**Problem**: Middleware generation fails for framework

**Solutions**:
- Verify framework is supported: `express`, `fastapi`, `django`
- Check framework compatibility matrix
- Review supported frameworks in create_middleware.py

### Middleware Not Applied

**Problem**: Generated middleware not working

**Solutions**:
- Verify middleware is imported in application
- Check middleware registration order
- Review framework-specific middleware setup
- Test middleware with sample requests

## Error Handler Issues

### Error Handlers Not Catching Errors

**Problem**: Errors not being handled by generated handlers

**Solutions**:
- Verify error handlers are registered
- Check error handler signatures match framework
- Review error handler placement in code
- Test with deliberate errors

### Incorrect Error Responses

**Problem**: Error responses not in expected format

**Solutions**:
- Customize error response format in handler
- Check framework-specific error handling patterns
- Verify error codes are correct
- Test error responses with API clients

## Logging Issues

### Logs Not Appearing

**Problem**: No logs are being generated

**Solutions**:
- Check logging configuration
- Verify log level is appropriate (INFO, DEBUG, ERROR)
- Check log file permissions
- Verify log directory exists and is writable

### Incorrect Log Format

**Problem**: Logs not in expected format

**Solutions**:
- Customize log format in configuration
- Review format options in logging library
- Add required fields (timestamp, level, service, message)
- Test log format with sample logs

## Deployment Issues

### Deploy Script Fails

**Problem**: Deployment script returns errors

**Solutions**:
- Check platform selection: `--platform kubernetes` or `--platform aws`
- Verify deployment prerequisites are met:
  - Kubernetes: kubectl configured, cluster accessible
  - AWS: AWS CLI configured, credentials valid
  - GCP: gcloud configured, credentials valid
- Review deploy.sh for specific error messages

### Health Check Failures

**Problem**: Health check returns unhealthy status

**Solutions**:
- Verify health endpoint exists: `/health` or `/healthz`
- Check dependencies are running
- Review health check configuration
- Test health endpoint manually: `curl http://localhost:3000/health`

### Rollback Fails

**Problem**: Rollback procedure doesn't work

**Solutions**:
- Verify previous version is available
- Check rollback script has correct version
- Test rollback process before production deployment
- Review deployment history

## Common Issues Across All Scripts

### Port Already in Use

**Problem**: `Error: Port 3000 already in use`

**Solutions**:
- Find process using port: `lsof -i :3000` (Mac/Linux) or `netstat -ano | findstr :3000` (Windows)
- Kill process: `kill -9 <PID>` or use `pkill node`
- Use different port: `--port 3001`
- Wait for previous process to finish

### Virtual Environment Issues

**Problem**: Scripts using wrong Python environment

**Solutions**:
- Activate virtual environment: `source venv/bin/activate` or `.\venv\Scripts\activate` (Windows)
- Deactivate if needed: `deactivate`
- Create new virtual environment: `python -m venv venv`
- Verify Python path: `which python`

### Module Import Errors

**Problem**: Generated code has import errors

**Solutions**:
- Verify all dependencies are installed
- Check Python path includes project directory
- Use proper import syntax for framework
- Install missing dependencies from error messages

## Debug Mode

### Verbose Output

```bash
# Get detailed output
python scripts/scaffold_api.py express my-api --verbose
python scripts/generate_model.py typeorm --schema schema.json --output src/models --verbose
```

### Dry Run Mode

```bash
# Test without creating files
python scripts/scaffold_api.py express my-api --dry-run
```

### Help Documentation

```bash
# Get help for any script
python scripts/scaffold_api.py --help
python scripts/generate_model.py --help
python scripts/setup_auth.py --help
```

## Framework-Specific Issues

### Express.js

- Ensure Node.js and npm are installed: `node --version`, `npm --version`
- Initialize package.json: `npm init -y` if needed
- Install dependencies: `npm install`
- Run with: `node index.js` or `npm start`

### FastAPI

- Ensure Python 3.7+ is installed
- Install dependencies: `pip install fastapi uvicorn`
- Run with: `uvicorn main:app --reload`

### Django

- Ensure Python 3.8+ is installed
- Install Django: `pip install django`
- Run migrations: `python manage.py migrate`
- Run server: `python manage.py runserver`

### Spring Boot

- Ensure Java 11+ and Maven are installed
- Verify pom.xml is configured correctly
- Build with: `mvn clean package`
- Run with: `java -jar target/app.jar`

## Database Issues

### Connection Failures

**Problem**: Cannot connect to database

**Solutions**:
- Verify database is running
- Check connection string in generated code
- Verify credentials are correct
- Check network connectivity to database
- Review firewall settings

### Migration Failures

**Problem**: Database migrations fail

**Solutions**:
- Verify model definitions are correct
- Check for existing schema conflicts
- Review migration SQL before applying
- Test migrations in development first
- Backup database before migrating

## Testing Issues

### Test Framework Not Installed

**Problem**: Cannot run tests due to missing test framework

**Solutions**:
- Install test dependencies:
  - Express: `npm install --save-dev jest supertest`
  - FastAPI: `pip install pytest pytest-asyncio httpx`
  - Django: Test framework included
- Verify test configuration file exists
- Review test templates for framework-specific setup

### Tests Not Found

**Problem**: `No tests found` when running test command

**Solutions**:
- Verify test files are in correct directory
- Check test file naming convention (e.g., `*.test.js`, `test_*.py`)
- Verify test configuration includes test directory
- Run with verbose output to see test discovery

## Getting Help

### Documentation

- Read generated README files
- Review framework documentation
- Check generated code comments
- Look for inline help text

### Community Resources

- Stack Overflow: Search for specific error messages
- Framework documentation: Express, FastAPI, Django, Spring
- GitHub issues: Check framework repositories for similar issues
- Discord/Slack communities: Framework-specific communities

## Prevention

### Best Practices

- Always test in development environment first
- Use virtual environments to isolate dependencies
- Review generated code before committing
- Test all generated functionality
- Keep dependencies updated but stable
- Follow framework conventions

### Code Review

- Have code reviewed before production
- Check for security vulnerabilities
- Verify error handling is complete
- Ensure logging is configured
- Test all edge cases
