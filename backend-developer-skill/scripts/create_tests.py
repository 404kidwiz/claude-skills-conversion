#!/usr/bin/env python3
"""
Unit Test Templates Generator
"""

import sys
import argparse
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_express_test_templates(output_path: Path):
    controller_test = """import request from 'supertest';
import express, { Application } from 'express';
import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';

describe('UserController', () => {
    let app: Application;

    beforeEach(() => {
        app = express();
        app.use(express.json());
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('POST /api/v1/users', () => {
        it('should create a new user', async () => {
            const userData = {
                email: 'test@example.com',
                name: 'Test User',
                password: 'SecurePass123!',
            };

            const response = await request(app)
                .post('/api/v1/users')
                .send(userData)
                .expect(201);

            expect(response.body).toHaveProperty('id');
            expect(response.body.email).toBe(userData.email);
            expect(response.body).not.toHaveProperty('password');
        });

        it('should return 400 for invalid email', async () => {
            const userData = {
                email: 'invalid-email',
                name: 'Test User',
                password: 'SecurePass123!',
            };

            await request(app)
                .post('/api/v1/users')
                .send(userData)
                .expect(400);
        });
    });

    describe('GET /api/v1/users/:id', () => {
        it('should return user by id', async () => {
            const userId = 1;

            const response = await request(app)
                .get(`/api/v1/users/${userId}`)
                .expect(200);

            expect(response.body.id).toBe(userId);
        });

        it('should return 404 for non-existent user', async () => {
            const userId = 9999;

            await request(app)
                .get(`/api/v1/users/${userId}`)
                .expect(404);
        });
    });
});
"""

    service_test = """import { UserService } from '../services/UserService';
import { describe, it, expect, beforeEach, jest } from '@jest/globals';

describe('UserService', () => {
    let userService: UserService;

    beforeEach(() => {
        userService = new UserService();
    });

    describe('createUser', () => {
        it('should create a user successfully', async () => {
            const userData = {
                email: 'test@example.com',
                name: 'Test User',
                password: 'SecurePass123!',
            };

            const user = await userService.createUser(userData);

            expect(user).toHaveProperty('id');
            expect(user.email).toBe(userData.email);
        });

        it('should throw error if email already exists', async () => {
            const userData = {
                email: 'existing@example.com',
                name: 'Test User',
                password: 'SecurePass123!',
            };

            await expect(userService.createUser(userData)).rejects.toThrow();
        });
    });

    describe('findById', () => {
        it('should return user if found', async () => {
            const user = await userService.findById(1);

            expect(user).toBeDefined();
            expect(user?.id).toBe(1);
        });

        it('should return null if not found', async () => {
            const user = await userService.findById(9999);

            expect(user).toBeNull();
        });
    });
});
"""

    tests_path = output_path / 'tests'
    tests_path.mkdir(parents=True, exist_ok=True)
    unit_path = tests_path / 'unit'
    unit_path.mkdir(parents=True, exist_ok=True)
    integration_path = tests_path / 'integration'
    integration_path.mkdir(parents=True, exist_ok=True)

    with open(unit_path / 'user.controller.test.ts', 'w') as f:
        f.write(controller_test)
    with open(unit_path / 'user.service.test.ts', 'w') as f:
        f.write(service_test)

    jest_config = {
        "preset": "ts-jest",
        "testEnvironment": "node",
        "roots": ["<rootDir>/src", "<rootDir>/tests"],
        "testMatch": ["**/__tests__/**/*.ts", "**/?(*.)+(spec|test).ts"],
        "collectCoverageFrom": ["src/**/*.ts", "!src/**/*.d.ts"],
        "coverageDirectory": "coverage",
        "coverageReporters": ["text", "lcov", "html"],
        "setupFilesAfterEnv": ["<rootDir>/tests/setup.ts"]
    }

    with open(output_path / 'jest.config.js', 'w') as f:
        f.write(f"module.exports = {json.dumps(jest_config, indent=4)}")


def create_fastapi_test_templates(output_path: Path):
    api_test = """import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_user(db):
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data


def test_get_user(db):
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1


def test_get_user_not_found():
    response = client.get("/api/v1/users/9999")
    assert response.status_code == 404


def test_invalid_email():
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "invalid-email",
            "name": "Test User",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 422
"""

    service_test = """import pytest
from app.services.user_service import UserService
from app.schemas.user import UserCreate

@pytest.fixture
def user_service(db):
    return UserService(db)

def test_create_user(user_service):
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="SecurePass123!"
    )

    user = user_service.create_user(user_data)

    assert user.email == "test@example.com"
    assert user.id is not None
    assert user.hashed_password is not None
    assert user.hashed_password != "SecurePass123!"

def test_get_user_by_email(user_service):
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="SecurePass123!"
    )
    user_service.create_user(user_data)

    user = user_service.get_user_by_email("test@example.com")

    assert user is not None
    assert user.email == "test@example.com"

def test_get_user_by_email_not_found(user_service):
    user = user_service.get_user_by_email("nonexistent@example.com")
    assert user is None
"""

    tests_path = output_path / 'app' / 'tests'
    tests_path.mkdir(parents=True, exist_ok=True)

    with open(tests_path / 'test_api.py', 'w') as f:
        f.write(api_test)
    with open(tests_path / 'test_services.py', 'w') as f:
        f.write(service_test)


def main():
    import json
    parser = argparse.ArgumentParser(description='Create test templates')
    parser.add_argument('framework', choices=['express', 'fastapi', 'django'],
                        help='Framework to use')
    parser.add_argument('--output', default='.', help='Output directory')
    args = parser.parse_args()

    output_path = Path(args.output)

    try:
        if args.framework == 'express':
            create_express_test_templates(output_path)
        elif args.framework == 'fastapi':
            create_fastapi_test_templates(output_path)

        logger.info(f"✓ Created test templates for {args.framework}")
    except Exception as e:
        logger.error(f"Error creating test templates: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
