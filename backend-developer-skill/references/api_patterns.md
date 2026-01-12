# Backend API Patterns

## Quick Start

### REST API Best Practices

#### Resource Naming

Use plural nouns for resources:
```
GET    /users          # List all users
GET    /users/{id}     # Get specific user
POST   /users          # Create user
PUT    /users/{id}     # Update user
DELETE /users/{id}     # Delete user
```

#### HTTP Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `204 No Content` - Success but no content returned
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `422 Unprocessable Entity` - Validation failed
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

#### Request/Response Format

**Request Example:**
```json
{
  "data": {
    "type": "users",
    "attributes": {
      "email": "user@example.com",
      "name": "John Doe"
    }
  }
}
```

**Response Example:**
```json
{
  "data": {
    "type": "users",
    "id": "123",
    "attributes": {
      "email": "user@example.com",
      "name": "John Doe",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  },
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 100
  }
}
```

### Pagination Strategies

#### Offset-based Pagination
```
GET /users?page=1&pageSize=20
```

#### Cursor-based Pagination
```
GET /users?cursor=abc123&limit=20
```

#### Keyset Pagination
```
GET /users?lastId=123&limit=20
```

### Filtering and Sorting

**Query Parameters:**
```
GET /users?filter[status]=active&sort=name,desc
```

**Complex Filters:**
```
GET /users?filter[age][gte]=18&filter[age][lte]=65
```

### Versioning Strategies

#### URL Versioning
```
/api/v1/users
/api/v2/users
```

#### Header Versioning
```
Accept: application/vnd.api.v1+json
```

#### Query Parameter Versioning
```
/api/users?version=1
```

## Common Patterns

### Repository Pattern

```typescript
interface UserRepository {
  findById(id: number): Promise<User | null>;
  findAll(options?: FindOptions): Promise<User[]>;
  create(user: UserCreate): Promise<User>;
  update(id: number, user: UserUpdate): Promise<User>;
  delete(id: number): Promise<void>;
}

class SQLUserRepository implements UserRepository {
  async findById(id: number): Promise<User | null> {
    return db.users.findUnique({ where: { id } });
  }
}
```

### Service Layer Pattern

```typescript
class UserService {
  constructor(
    private userRepository: UserRepository,
    private emailService: EmailService
  ) {}

  async createUser(data: UserCreate): Promise<User> {
    const existing = await this.userRepository.findByEmail(data.email);
    if (existing) {
      throw new ConflictError('Email already exists');
    }

    const user = await this.userRepository.create(data);
    await this.emailService.sendWelcomeEmail(user);

    return user;
  }
}
```

### Unit of Work Pattern

```python
class UnitOfWork:
    def __init__(self, session):
        self.session = session
        self.users = UserRepository(session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()

# Usage
with UnitOfWork(session) as uow:
    user = uow.users.create(user_data)
    uow.users.update(user.id, updates)
```

### CQRS (Command Query Responsibility Segregation)

```typescript
// Command (Write)
class CreateUserCommand {
  constructor(
    public email: string,
    public name: string
  ) {}
}

// Query (Read)
class GetUserQuery {
  constructor(public id: number) {}
}

// Command Handler
class CreateUserCommandHandler {
  async execute(command: CreateUserCommand): Promise<void> {
    await this.userRepository.create(command);
  }
}

// Query Handler
class GetUserQueryHandler {
  async execute(query: GetUserQuery): Promise<User | null> {
    return this.userRepository.findById(query.id);
  }
}
```

## Authentication Patterns

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "email": "user@example.com",
    "role": "admin",
    "iat": 1516239022,
    "exp": 1516242622
  }
}
```

### Token Refresh Flow

```
Client                    Server
  |                         |
  |  POST /refresh         |
  |  refresh_token         |
  |----------------------->|
  |                         |
  |  access_token          |
  |  refresh_token         |
  |<-----------------------|
```

### Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP'
});

app.use('/api/', limiter);
```

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "requestId": "abc-123-def",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Global Error Handler

```typescript
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  const statusCode = err instanceof AppError ? err.statusCode : 500;

  res.status(statusCode).json({
    error: {
      code: err.name,
      message: err.message,
      ...(process.env.NODE_ENV === 'development' && {
        stack: err.stack
      })
    }
  });
});
```

## Database Patterns

### Soft Deletes

```typescript
@Entity()
export class User {
  id: number;
  email: string;
  deletedAt: Date | null;

  @BeforeUpdate()
  softDelete() {
    this.deletedAt = new Date();
  }
}
```

### Auditing

```typescript
@Entity()
export class AuditLog {
  id: number;
  entity: string;
  entityId: number;
  action: 'CREATE' | 'UPDATE' | 'DELETE';
  changes: Record<string, any>;
  userId: number;
  timestamp: Date;
}
```

### Optimistic Locking

```typescript
@Entity()
export class Product {
  @VersionColumn()
  version: number;
}

// Update with version check
await repository.update(
  { id: 1, version: 2 },
  { name: 'New Name' }
);
```

## Performance Patterns

### Caching Strategy

```typescript
import Redis from 'ioredis';

const redis = new Redis();

async function getUser(id: number): Promise<User> {
  const cacheKey = `user:${id}`;

  // Try cache first
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }

  // Fetch from database
  const user = await userRepository.findById(id);

  // Set cache with TTL
  await redis.setex(cacheKey, 3600, JSON.stringify(user));

  return user;
}
```

### Database Connection Pooling

```typescript
import { Pool } from 'pg';

const pool = new Pool({
  host: process.env.DB_HOST,
  port: 5432,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  max: 20, // Maximum pool size
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
});
```

### Batch Operations

```typescript
// Instead of multiple individual inserts
for (const user of users) {
  await userRepository.create(user);
}

// Use batch insert
await userRepository.createMany(users);
```

## Security Patterns

### Input Sanitization

```typescript
import validator from 'validator';

function sanitizeInput(input: string): string {
  return validator.escape(input.trim());
}
```

### SQL Injection Prevention

```typescript
// BAD
const query = `SELECT * FROM users WHERE id = ${userId}`;

// GOOD
const query = 'SELECT * FROM users WHERE id = $1';
const result = await db.query(query, [userId]);
```

### CORS Configuration

```typescript
const corsOptions = {
  origin: process.env.ALLOWED_ORIGINS?.split(',') || [],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

app.use(cors(corsOptions));
```

## Testing Patterns

### Unit Testing

```typescript
describe('UserService', () => {
  let service: UserService;
  let mockRepo: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepo = createMockUserRepository();
    service = new UserService(mockRepo);
  });

  it('should create user', async () => {
    const user = await service.createUser(userData);

    expect(mockRepo.create).toHaveBeenCalledWith(userData);
    expect(user.email).toBe(userData.email);
  });
});
```

### Integration Testing

```typescript
describe('User API', () => {
  let app: Application;

  beforeAll(async () => {
    app = createApp();
    await setupDatabase();
  });

  afterAll(async () => {
    await cleanupDatabase();
  });

  it('should create user via API', async () => {
    const response = await request(app)
      .post('/api/v1/users')
      .send(userData)
      .expect(201);

    expect(response.body.data.email).toBe(userData.email);
  });
});
```

## Monitoring and Observability

### Structured Logging

```typescript
logger.info('User created', {
  userId: user.id,
  email: user.email,
  action: 'CREATE',
  timestamp: new Date().toISOString()
});
```

### Metrics Collection

```typescript
import { Counter, Histogram } from 'prom-client';

const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration
      .labels(req.method, req.route?.path || '', res.statusCode.toString())
      .observe(duration);
  });
  next();
});
```

### Health Checks

```typescript
app.get('/health', async (req, res) => {
  const health = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    checks: {
      database: await checkDatabase(),
      redis: await checkRedis(),
      api: await checkExternalAPI()
    }
  };

  const isHealthy = Object.values(health.checks).every(check => check.status === 'ok');
  res.status(isHealthy ? 200 : 503).json(health);
});
```

## Troubleshooting

### Common Issues

#### Connection Pool Exhaustion
- **Symptoms**: Slow responses, timeouts
- **Solution**: Increase pool size, reduce connection lifetime, add connection timeout

#### Memory Leaks
- **Symptoms**: Memory usage increases over time
- **Solution**: Profile with heap snapshots, check for event listeners, close connections

#### N+1 Query Problem
- **Symptoms**: Many database queries for single request
- **Solution**: Use eager loading, batch queries, implement GraphQL DataLoader pattern

#### Slow API Responses
- **Symptoms**: High response times
- **Solution**: Add caching, optimize queries, use database indexes, implement pagination
