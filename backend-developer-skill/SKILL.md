# Backend Developer Skill

## Overview

The Backend Developer skill provides comprehensive tools and references for building production-ready server-side applications. It supports multiple frameworks, databases, and deployment strategies.

## Scripts

### API Scaffolding
```bash
python scripts/scaffold_api.py <framework> <project_name>

# Frameworks: express, fastapi, django, spring

# Example: scaffold an Express API
python scripts/scaffold_api.py express my-api

# Example: scaffold a FastAPI application
python scripts/scaffold_api.py fastapi my-app
```

### Database Model Generation
```bash
python scripts/generate_model.py <orm> --schema <schema_file> --output <output_dir>

# ORMs: sequelize, typeorm, sqlalchemy, django, jpa

# Example: generate TypeORM models
python scripts/generate_model.py typeorm --schema schema.json --output src/models
```

### Authentication Setup
```bash
python scripts/setup_auth.py <framework> <auth_type>

# Auth types: jwt, oauth2, session

# Example: setup JWT for Express
python scripts/setup_auth.py express jwt

# Example: setup OAuth2 for FastAPI
python scripts/setup_auth.py fastapi oauth2
```

### Middleware Generation
```bash
python scripts/create_middleware.py <framework> --output <output_dir>

# Frameworks: express, fastapi, django

# Example: create Express validation middleware
python scripts/create_middleware.py express --output src/middleware
```

### Error Handler Setup
```bash
python scripts/error_handler.py <framework> --output <output_dir>

# Frameworks: express, fastapi

# Example: create error handlers for Express
python scripts/error_handler.py express --output src
```

### Logging Configuration
```bash
python scripts/setup_logging.py --output <output_dir>

# Example: setup logging for project
python scripts/setup_logging.py --output src/utils
```

### API Documentation Generation
```bash
python scripts/generate_docs.py --output <output_dir> --config <config_file>

# Example: generate OpenAPI spec
python scripts/generate_docs.py --output docs --config api-config.json
```

### Unit Test Templates
```bash
python scripts/create_tests.py <framework> --output <output_dir>

# Frameworks: express, fastapi, django

# Example: create test templates for Express
python scripts/create_tests.py express --output tests
```

### Deployment Script
```bash
./scripts/deploy.sh [OPTIONS]

# Options:
# --skip-tests: Skip test execution
# --platform <kubernetes|aws|gcp>: Deployment platform
# --rollback: Rollback deployment
# --health-check: Run health check only

# Example: deploy to Kubernetes
./scripts/deploy.sh --platform kubernetes

# Example: deploy without tests
./scripts/deploy.sh --skip-tests --platform aws
```

## References

### API Patterns (`references/api_patterns.md`)
- REST API best practices
- Resource naming conventions
- HTTP status codes
- Pagination strategies
- Versioning approaches
- Common patterns (Repository, Service Layer, CQRS)
- Authentication patterns
- Error handling
- Database patterns
- Performance optimization
- Security patterns

### Backend Frameworks (`references/backend_frameworks.md`)
- Express.js (Node.js/TypeScript)
- FastAPI (Python)
- Django (Python)
- Spring Boot (Java)
- Gin (Go)
- Framework comparison
- Quick start guides
- Best practices
- Testing approaches
- Deployment strategies

### Testing Strategies (`references/testing_strategies.md`)
- Testing pyramid
- Unit testing
- Integration testing
- End-to-end testing
- Test data management
- Test organization
- Test coverage
- Mocking and stubs
- Performance testing
- Continuous testing
- Best practices

### Deployment Guide (`references/deployment_guide.md`)
- Deployment strategies (Blue-Green, Canary, Rolling)
- Docker deployment
- Kubernetes deployment
- Cloud deployment (AWS, GCP, Azure)
- CI/CD pipelines
- Database migrations
- Monitoring and observability
- Security
- Performance optimization
- Troubleshooting

## Quick Start

### Create a New Project

```bash
# 1. Scaffold API
python scripts/scaffold_api.py express my-backend-api

# 2. Navigate to project
cd my-backend-api

# 3. Generate models
python scripts/generate_model.py typeorm --schema schema.json --output src/models

# 4. Setup authentication
python scripts/setup_auth.py express jwt

# 5. Create error handlers
python scripts/error_handler.py express --output src

# 6. Generate test templates
python scripts/create_tests.py express --output tests
```

### Deploy to Production

```bash
# Build and deploy
./scripts/deploy.sh --platform kubernetes

# Run health check
./scripts/deploy.sh --health-check

# Rollback if needed
./scripts/deploy.sh --rollback
```

## Framework Support

### Node.js/TypeScript
- Express.js
- NestJS
- Koa.js
- Fastify

### Python
- FastAPI
- Django
- Flask
- Tornado

### Java
- Spring Boot
- Quarkus
- Micronaut

### Go
- Gin
- Echo
- Fiber

## Features

### API Development
- REST API scaffolding
- Input validation
- Error handling
- Logging
- Documentation generation

### Database
- Model generation
- ORM support
- Migration support
- Connection pooling

### Security
- JWT authentication
- OAuth2 integration
- Session management
- Input sanitization
- SQL injection prevention

### Testing
- Unit test templates
- Integration tests
- Test fixtures
- Mocking utilities
- Coverage configuration

### Deployment
- Docker support
- Kubernetes manifests
- Cloud deployment
- CI/CD integration
- Health checks
- Monitoring setup

## Best Practices

1. **Always validate input** - Use provided validation middleware
2. **Handle errors gracefully** - Use generated error handlers
3. **Write tests** - Use test templates for consistency
4. **Use environment variables** - Never hardcode secrets
5. **Implement logging** - Use provided logging configuration
6. **Monitor performance** - Set up metrics and alerts
7. **Security first** - Use provided authentication setup
8. **Version your API** - Follow versioning patterns
9. **Document your code** - Generate API docs automatically
10. **Deploy safely** - Use provided deployment scripts

## Common Patterns

### Repository Pattern
Use generated repositories for data access:
- Separation of concerns
- Easy testing
- Swappable implementations

### Service Layer
Use service layer for business logic:
- Centralized business rules
- Transaction management
- Error handling

### Middleware Stack
Use generated middleware for cross-cutting concerns:
- Authentication
- Authorization
- Validation
- Logging
- Error handling

## Troubleshooting

### Common Issues

**Database connection errors**
- Check connection string
- Verify database is running
- Check network connectivity
- Review connection pool settings

**Authentication failures**
- Verify JWT secret
- Check token expiration
- Validate token format
- Review middleware order

**Build failures**
- Check TypeScript configuration
- Verify dependencies are installed
- Review error messages
- Check for syntax errors

**Deployment issues**
- Verify Docker image builds
- Check Kubernetes pods
- Review logs
- Verify environment variables

## Resources

- [Express.js](https://expressjs.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Django](https://www.djangoproject.com/)
- [Spring Boot](https://spring.io/projects/spring-boot)
- [Kubernetes](https://kubernetes.io/)
- [Docker](https://www.docker.com/)

## Included Automation Scripts

The backend developer skill includes comprehensive automation scripts located in `scripts/`:

- **scaffold_api.py**: API scaffolding for Express, FastAPI, Django, and Spring frameworks with project structure and boilerplate code
- **generate_model.py**: Database model generation for Sequelize, TypeORM, SQLAlchemy, Django ORM, and JPA with schema-driven creation
- **setup_auth.py**: Authentication setup for JWT and OAuth2 in Express and FastAPI with secure token handling
- **create_middleware.py**: Middleware generation for Express, FastAPI, and Django with validation, logging, and error handling
- **error_handler.py**: Error handler setup for Express and FastAPI with consistent error responses and logging
- **setup_logging.py**: Logging configuration with structured logging, log levels, and output destinations
- **generate_docs.py**: API documentation generation with OpenAPI/Swagger specification
- **create_tests.py**: Unit test template generation for Express, FastAPI, and Django with test fixtures and mocking
- **deploy.sh**: Deployment script for Kubernetes, AWS, and GCP with health checks and rollback support

## References

### Reference Documentation (`references/` directory)
- **troubleshooting.md**: Troubleshooting guide for backend issues including database connections, authentication failures, and deployment problems
- **best_practices.md**: Best practices for API development, error handling, testing, security, and deployment