# Backend Testing Strategies

## Overview

Testing backend APIs requires a comprehensive approach covering unit, integration, and end-to-end tests. This guide covers strategies for modern backend frameworks.

## Testing Pyramid

```
        /\
       /E2E\     - Few, slow, high value
      /------\
     /Integration\  - Moderate number, medium speed
    /------------\
   /    Unit      \ - Many, fast, focused
  /----------------\
```

## Unit Testing

### Test Structure

```typescript
describe('UserService', () => {
  let userService: UserService;
  let mockUserRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockUserRepository = createMockRepository();
    userService = new UserService(mockUserRepository);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });
});
```

### Testing Pure Functions

```typescript
describe('Password Validation', () => {
  it('should validate strong password', () => {
    expect(validatePassword('StrongP@ss123')).toBe(true);
  });

  it('should reject weak password', () => {
    expect(validatePassword('weak')).toBe(false);
  });
});
```

### Mocking Dependencies

```typescript
describe('UserService', () => {
  it('should send welcome email', async () => {
    const mockEmailService = {
      sendWelcomeEmail: jest.fn().mockResolvedValue(undefined)
    };

    const service = new UserService(mockRepo, mockEmailService);
    await service.createUser(userData);

    expect(mockEmailService.sendWelcomeEmail).toHaveBeenCalledWith(
      expect.objectContaining({ email: userData.email })
    );
  });
});
```

### Testing Edge Cases

```typescript
describe('User Creation', () => {
  it('should handle duplicate email', async () => {
    mockRepo.findByEmail.mockResolvedValue(existingUser);

    await expect(
      service.createUser({ email: 'test@example.com' })
    ).rejects.toThrow(ConflictError);
  });

  it('should handle database errors', async () => {
    mockRepo.create.mockRejectedValue(new Error('DB Error'));

    await expect(
      service.createUser(userData)
    ).rejects.toThrow('DB Error');
  });
});
```

## Integration Testing

### Test Database Setup

```typescript
// tests/setup.ts
import { setupTestDatabase, teardownTestDatabase } from './test-utils';

beforeAll(async () => {
  await setupTestDatabase();
});

afterAll(async () => {
  await teardownTestDatabase();
});

beforeEach(async () => {
  await truncateDatabase();
});
```

### API Endpoint Testing

```typescript
describe('POST /api/v1/users', () => {
  it('should create user', async () => {
    const response = await request(app)
      .post('/api/v1/users')
      .send({
        email: 'test@example.com',
        name: 'Test User',
        password: 'SecurePass123!'
      })
      .expect(201);

    expect(response.body.data.email).toBe('test@example.com');
    expect(response.body.data).not.toHaveProperty('password');
  });

  it('should validate input', async () => {
    const response = await request(app)
      .post('/api/v1/users')
      .send({
        email: 'invalid-email',
        name: 'Test'
      })
      .expect(400);

    expect(response.body.errors).toBeDefined();
  });
});
```

### Database Integration

```typescript
describe('User Repository Integration', () => {
  let repository: UserRepository;

  beforeAll(async () => {
    const connection = await createTestConnection();
    repository = new UserRepository(connection);
  });

  it('should create and find user', async () => {
    const user = await repository.create({
      email: 'test@example.com',
      name: 'Test User'
    });

    const found = await repository.findById(user.id);
    expect(found).not.toBeNull();
    expect(found?.email).toBe('test@example.com');
  });
});
```

### Authentication Testing

```typescript
describe('Authentication', () => {
  it('should authenticate with valid credentials', async () => {
    const response = await request(app)
      .post('/api/v1/auth/login')
      .send({
        email: 'test@example.com',
        password: 'correct-password'
      })
      .expect(200);

    expect(response.body.data.token).toBeDefined();
  });

  it('should reject invalid credentials', async () => {
    await request(app)
      .post('/api/v1/auth/login')
      .send({
        email: 'test@example.com',
        password: 'wrong-password'
      })
      .expect(401);
  });

  it('should require auth for protected routes', async () => {
    await request(app)
      .get('/api/v1/users/me')
      .expect(401);
  });
});
```

## End-to-End Testing

### API Flow Testing

```typescript
describe('User Registration Flow', () => {
  it('should complete full registration flow', async () => {
    // 1. Register user
    const registerResponse = await request(app)
      .post('/api/v1/auth/register')
      .send({
        email: 'new@example.com',
        password: 'SecurePass123!'
      })
      .expect(201);

    const { token, user } = registerResponse.data;

    // 2. Login
    const loginResponse = await request(app)
      .post('/api/v1/auth/login')
      .send({
        email: 'new@example.com',
        password: 'SecurePass123!'
      })
      .expect(200);

    expect(loginResponse.data.token).toBeDefined();

    // 3. Access protected route
    const profileResponse = await request(app)
      .get('/api/v1/users/me')
      .set('Authorization', `Bearer ${token}`)
      .expect(200);

    expect(profileResponse.data.email).toBe('new@example.com');
  });
});
```

### External Service Integration

```typescript
describe('Payment Integration', () => {
  it('should process payment', async () => {
    // Mock external payment service
    const mockPaymentService = new MockPaymentService();

    const response = await request(app)
      .post('/api/v1/payments')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        amount: 100,
        currency: 'USD'
      })
      .expect(201);

    expect(response.body.data.status).toBe('completed');
    expect(mockPaymentService.chargeWasCalled()).toBe(true);
  });
});
```

## Test Data Management

### Fixtures

```typescript
// tests/fixtures/user.fixture.ts
export class UserFixture {
  static createValid(overrides = {}) {
    return {
      email: 'test@example.com',
      name: 'Test User',
      password: 'SecurePass123!',
      ...overrides
    };
  }

  static createInvalid() {
    return {
      email: 'invalid-email',
      name: ''
    };
  }
}
```

### Factories

```typescript
// tests/factories/user.factory.ts
export class UserFactory {
  static create(overrides: Partial<User> = {}): User {
    return {
      id: 1,
      email: `user${Date.now()}@example.com`,
      name: 'Test User',
      ...overrides
    };
  }

  static createMany(count: number): User[] {
    return Array.from({ length: count }, () => this.create());
  }
}
```

## Test Organization

### File Structure

```
tests/
├── unit/
│   ├── services/
│   │   ├── user.service.test.ts
│   │   └── auth.service.test.ts
│   └── utils/
│       └── validation.test.ts
├── integration/
│   ├── api/
│   │   ├── user.api.test.ts
│   │   └── auth.api.test.ts
│   └── repositories/
│       └── user.repository.test.ts
├── e2e/
│   ├── flows/
│   │   └── registration.flow.test.ts
│   └── scenarios/
│       └── payment.scenario.test.ts
├── fixtures/
│   └── user.fixture.ts
├── factories/
│   └── user.factory.ts
├── setup.ts
└── teardown.ts
```

## Test Coverage

### Coverage Targets

```
Lines:      80%
Functions:  80%
Branches:   75%
Statements: 80%
```

### Coverage Configuration

```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.interface.ts'
  ],
  coverageThreshold: {
    global: {
      lines: 80,
      functions: 80,
      branches: 75,
      statements: 80
    }
  }
};
```

## Mocking and Stubs

### HTTP Request Mocking

```typescript
import nock from 'nock';

describe('External API Service', () => {
  it('should fetch user data', async () => {
    nock('https://api.external.com')
      .get('/users/123')
      .reply(200, {
        id: 123,
        name: 'External User'
      });

    const user = await externalService.getUser(123);
    expect(user.name).toBe('External User');
  });
});
```

### Database Mocking

```typescript
describe('User Repository', () => {
  it('should find user by email', async () => {
    const mockQueryBuilder = {
      where: jest.fn().mockReturnThis(),
      first: jest.fn().mockResolvedValue(mockUser)
    };

    const mockDb = {
      queryBuilder: jest.fn().mockReturnValue(mockQueryBuilder)
    };

    const repository = new UserRepository(mockDb);
    const user = await repository.findByEmail('test@example.com');

    expect(user).toEqual(mockUser);
    expect(mockQueryBuilder.where).toHaveBeenCalledWith('email', 'test@example.com');
  });
});
```

## Performance Testing

### Load Testing

```typescript
import { check, sleep } from 'k6';
import http from 'k6/http';

export let options = {
  stages: [
    { duration: '30s', target: 100 },  // Ramp up
    { duration: '1m', target: 100 },    // Stay
    { duration: '30s', target: 0 }      // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01']
  }
};

export default function() {
  let res = http.post('http://localhost:3000/api/v1/users', {
    email: `user${__VU}@example.com`,
    password: 'TestPass123!'
  });

  check(res, {
    'status was 201': (r) => r.status == 201
  });

  sleep(1);
}
```

### Benchmarking

```typescript
describe('Performance Benchmarks', () => {
  it('should process 1000 users in < 1s', async () => {
    const start = Date.now();

    const users = Array.from({ length: 1000 }, () =>
      service.createUser({ email: `user${Date.now()}@example.com` })
    );

    await Promise.all(users);

    const duration = Date.now() - start;
    expect(duration).toBeLessThan(1000);
  });
});
```

## Continuous Testing

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'npm'

      - run: npm ci
      - run: npm test
      - run: npm run test:coverage
```

## Test Best Practices

### Naming Conventions

```typescript
// BAD
it('should work', () => {});

// GOOD
it('should create user with valid data', () => {});
it('should return 400 when email is invalid', () => {});
it('should throw error when duplicate email exists', () => {});
```

### AAA Pattern

```typescript
it('should create user', () => {
  // Arrange
  const userData = { email: 'test@example.com' };
  mockRepo.create.mockResolvedValue(createdUser);

  // Act
  const result = await service.createUser(userData);

  // Assert
  expect(result.email).toBe(userData.email);
});
```

### One Assertion per Test

```typescript
// GOOD
it('should set user email', () => {
  const user = service.createUser({ email: 'test@example.com' });
  expect(user.email).toBe('test@example.com');
});

it('should hash user password', () => {
  const user = service.createUser({ password: 'password' });
  expect(user.password).not.toBe('password');
});
```

## Troubleshooting

### Flaky Tests

```typescript
// Use retries for flaky tests
describe('Flaky Integration', () => {
  jest.retryTimes(3);

  it('should eventually succeed', async () => {
    // Test code
  });
});
```

### Test Isolation

```typescript
// Reset state between tests
beforeEach(async () => {
  await resetDatabase();
  await clearRedis();
  jest.clearAllMocks();
});
```

### Debugging

```typescript
// Enable debug logging
describe('Debug', () => {
  beforeEach(() => {
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  it('should log user creation', () => {
    service.createUser({ email: 'test@example.com' });
    expect(console.log).toHaveBeenCalledWith(expect.stringContaining('user created'));
  });
});
```

## Resources

- Jest: https://jestjs.io/
- pytest: https://docs.pytest.org/
- Supertest: https://github.com/visionmedia/supertest
- K6: https://k6.io/
- Testcontainers: https://www.testcontainers.org/
