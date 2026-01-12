#!/usr/bin/env python3
"""
REST API Scaffolding Script
Supports multiple frameworks: Express, FastAPI, Django, Spring Boot
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIScaffolder:
    """API scaffolding utility for multiple frameworks"""

    def __init__(self, framework: str, project_name: str, config: Dict):
        self.framework = framework.lower()
        self.project_name = project_name
        self.config = config
        self.project_path = Path(project_name)

        if self.framework not in ['express', 'fastapi', 'django', 'spring']:
            raise ValueError(f"Unsupported framework: {framework}")

    def scaffold(self):
        """Main scaffolding method"""
        logger.info(f"Scaffolding {self.framework} API project: {self.project_name}")

        self._create_project_structure()
        self._generate_config_files()
        self._create_base_files()

        logger.info(f"✓ {self.framework} API scaffolded successfully!")

    def _create_project_structure(self):
        """Create directory structure based on framework"""
        logger.info("Creating project structure...")

        dirs = []

        if self.framework == 'express':
            dirs = [
                'src',
                'src/routes',
                'src/controllers',
                'src/models',
                'src/middleware',
                'src/services',
                'src/utils',
                'tests',
                'tests/unit',
                'tests/integration'
            ]
        elif self.framework == 'fastapi':
            dirs = [
                'app',
                'app/api',
                'app/api/v1',
                'app/api/v1/endpoints',
                'app/core',
                'app/models',
                'app/schemas',
                'app/services',
                'app/tests',
                'alembic/versions'
            ]
        elif self.framework == 'django':
            dirs = [
                f'{self.project_name}',
                f'{self.project_name}/apps',
                f'{self.project_name}/apps/common',
                'config',
                'config/settings',
                'tests',
                'docs'
            ]
        elif self.framework == 'spring':
            dirs = [
                'src/main/java/com/example/' + self.project_name.replace('-', ''),
                'src/main/java/com/example/' + self.project_name.replace('-', '') + '/controller',
                'src/main/java/com/example/' + self.project_name.replace('-', '') + '/service',
                'src/main/java/com/example/' + self.project_name.replace('-', '') + '/model',
                'src/main/java/com/example/' + self.project_name.replace('-', '') + '/repository',
                'src/main/resources',
                'src/test/java',
                'docs'
            ]

        for dir_path in dirs:
            self.project_path.joinpath(dir_path).mkdir(parents=True, exist_ok=True)

    def _generate_config_files(self):
        """Generate framework-specific configuration files"""
        logger.info("Generating configuration files...")

        if self.framework == 'express':
            self._create_package_json()
            self._create_tsconfig_json()
            self._create_eslintrc()
            self._create_prettierrc()

        elif self.framework == 'fastapi':
            self._create_requirements_txt()
            self._create_pyproject_toml()
            self._create_pylintrc()

        elif self.framework == 'django':
            self._create_requirements_txt_django()
            self._create_django_settings()

        elif self.framework == 'spring':
            self._create_pom_xml()
            self._create_application_properties()

    def _create_base_files(self):
        """Create base application files"""
        logger.info("Creating base application files...")

        if self.framework == 'express':
            self._create_express_app()

        elif self.framework == 'fastapi':
            self._create_fastapi_app()

        elif self.framework == 'django':
            self._create_django_app()

        elif self.framework == 'spring':
            self._create_spring_app()

    def _create_package_json(self):
        """Create package.json for Express"""
        content = {
            "name": self.project_name,
            "version": "1.0.0",
            "description": "REST API built with Express",
            "main": "dist/index.js",
            "scripts": {
                "dev": "ts-node-dev src/index.ts",
                "build": "tsc",
                "start": "node dist/index.js",
                "test": "jest",
                "lint": "eslint src --ext .ts",
                "format": "prettier --write \"src/**/*.ts\""
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "helmet": "^7.0.0",
                "dotenv": "^16.3.1",
                "express-validator": "^7.0.1",
                "morgan": "^1.10.0",
                "compression": "^1.7.4"
            },
            "devDependencies": {
                "@types/express": "^4.17.17",
                "@types/node": "^20.5.0",
                "@types/cors": "^2.8.13",
                "@types/morgan": "^1.9.4",
                "@types/compression": "^1.7.2",
                "typescript": "^5.1.6",
                "ts-node-dev": "^2.0.0",
                "jest": "^29.6.2",
                "@types/jest": "^29.5.3",
                "eslint": "^8.47.0",
                "@typescript-eslint/eslint-plugin": "^6.3.0",
                "@typescript-eslint/parser": "^6.3.0",
                "prettier": "^3.0.1"
            }
        }

        with open(self.project_path / 'package.json', 'w') as f:
            json.dump(content, f, indent=2)

    def _create_tsconfig_json(self):
        """Create TypeScript configuration"""
        content = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True,
                "moduleResolution": "node",
                "allowSyntheticDefaultImports": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist", "tests"]
        }

        with open(self.project_path / 'tsconfig.json', 'w') as f:
            json.dump(content, f, indent=2)

    def _create_eslintrc(self):
        """Create ESLint configuration"""
        content = {
            "parser": "@typescript-eslint/parser",
            "extends": [
                "eslint:recommended",
                "plugin:@typescript-eslint/recommended"
            ],
            "plugins": ["@typescript-eslint"],
            "env": {
                "node": True,
                "es6": True
            },
            "rules": {
                "@typescript-eslint/no-unused-vars": "error",
                "@typescript-eslint/explicit-function-return-type": "warn",
                "no-console": "warn"
            }
        }

        with open(self.project_path / '.eslintrc.json', 'w') as f:
            json.dump(content, f, indent=2)

    def _create_prettierrc(self):
        """Create Prettier configuration"""
        content = {
            "semi": True,
            "singleQuote": True,
            "tabWidth": 2,
            "trailingComma": "es5",
            "printWidth": 80
        }

        with open(self.project_path / '.prettierrc', 'w') as f:
            json.dump(content, f, indent=2)

    def _create_express_app(self):
        """Create Express application entry point"""
        content = """import express, { Application, Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import compression from 'compression';
import { errorHandler } from './middleware/errorHandler';
import { notFoundHandler } from './middleware/notFoundHandler';

const app: Application = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('combined'));

// Health check
app.get('/health', (req: Request, res: Response) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API routes will be mounted here
// app.use('/api/v1', routes);

// Error handling
app.use(notFoundHandler);
app.use(errorHandler);

export default app;
"""

        with open(self.project_path / 'src' / 'index.ts', 'w') as f:
            f.write(content)

    def _create_requirements_txt(self):
        """Create requirements.txt for FastAPI"""
        content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
alembic==1.12.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
httpx==0.25.1
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
pylint==3.0.2
mypy==1.6.1
"""

        with open(self.project_path / 'requirements.txt', 'w') as f:
            f.write(content)

    def _create_pyproject_toml(self):
        """Create pyproject.toml for FastAPI"""
        content = """[tool.black]
line-length = 88
target-version = ['py311']

[tool.pylint.messages_control]
disable = "C0330, C0326"

[tool.pylint.format]
max-line-length = "88"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
"""

        with open(self.project_path / 'pyproject.toml', 'w') as f:
            f.write(content)

    def _create_pylintrc(self):
        """Create pylint configuration"""
        content = """[MASTER]
load-plugins=pylint_flask_sqlalchemy

[FORMAT]
max-line-length=88

[DESIGN]
max-args=7
"""

        with open(self.project_path / '.pylintrc', 'w') as f:
            f.write(content)

    def _create_fastapi_app(self):
        """Create FastAPI application entry point"""
        content = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.v1.api import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": settings.now()}
"""

        with open(self.project_path / 'app' / 'main.py', 'w') as f:
            f.write(content)

    def _create_requirements_txt_django(self):
        """Create requirements.txt for Django"""
        content = """Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-filter==23.5
djoser==2.2.2
python-decouple==3.8
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
gunicorn==21.2.0
whitenoise==6.6.0
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0
black==23.11.0
pylint==3.0.2
"""

        with open(self.project_path / 'requirements.txt', 'w') as f:
            f.write(content)

    def _create_django_settings(self):
        """Create Django settings"""
        content = """from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='your-secret-key')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='postgres'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000'
).split(',')
"""

        with open(self.project_path / 'config' / 'settings' / 'base.py', 'w') as f:
            f.write(content)

    def _create_django_app(self):
        """Create Django application structure"""
        content = """from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"""

        with open(self.project_path / 'config' / 'urls.py', 'w') as f:
            f.write(content)

    def _create_pom_xml(self):
        """Create pom.xml for Spring Boot"""
        content = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.5</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>${project-name}</artifactId>
    <version>1.0.0</version>
    <name>${project-name}</name>
    <description>REST API built with Spring Boot</description>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.liquibase</groupId>
            <artifactId>liquibase-core</artifactId>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.security</groupId>
            <artifactId>spring-security-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
"""

        with open(self.project_path / 'pom.xml', 'w') as f:
            f.write(content)

    def _create_application_properties(self):
        """Create application.properties for Spring Boot"""
        content = """server.port=8080
spring.application.name=${project-name}

# Database
spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
spring.datasource.username=postgres
spring.datasource.password=postgres
spring.datasource.driver-class-name=org.postgresql.Driver

# JPA
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect

# Liquibase
spring.liquibase.change-log=classpath:db/changelog/db.changelog-master.xml

# Logging
logging.level.com.example=INFO
logging.level.org.springframework.web=DEBUG

# Actuator
management.endpoints.web.exposure.include=health,info,metrics
management.endpoint.health.show-details=always
"""

        with open(self.project_path / 'src' / 'main' / 'resources' / 'application.properties', 'w') as f:
            f.write(content)

    def _create_spring_app(self):
        """Create Spring Boot application entry point"""
        package_name = self.project_name.replace('-', '')
        content = f"""package com.example.{package_name};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class {self.project_name.title().replace('-', '')}Application {{
    public static void main(String[] args) {{
        SpringApplication.run({self.project_name.title().replace('-', '')}Application.class, args);
    }}
}}
"""

        app_path = self.project_path / 'src' / 'main' / 'java' / 'com' / 'example' / package_name
        with open(app_path / f"{self.project_name.title().replace('-', '')}Application.java", 'w') as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser(description='Scaffold REST API with multiple frameworks')
    parser.add_argument('framework', choices=['express', 'fastapi', 'django', 'spring'],
                        help='Framework to use')
    parser.add_argument('project_name', help='Name of the project')
    parser.add_argument('--config', help='Path to custom config file (JSON)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {args.config}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file: {args.config}")
            sys.exit(1)

    try:
        scaffolder = APIScaffolder(args.framework, args.project_name, config)
        scaffolder.scaffold()
    except Exception as e:
        logger.error(f"Error scaffolding project: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
