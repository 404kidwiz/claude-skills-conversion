# Backend Deployment Guide

## Overview

This guide covers deployment strategies for backend applications across different platforms and environments.

## Deployment Strategies

### Blue-Green Deployment

```
Current Flow:  User -> Blue  (v1)
                    ↓
Deploy v2 to Green
                    ↓
Health check
                    ↓
Switch Traffic: User -> Green (v2)
                    ↓
Rollback:     User -> Blue  (v1)
```

### Canary Deployment

```
v1 (90%) ────────┬─────── v2 (10%)
                ↓
Monitor metrics
                ↓
Gradual shift: v1 (50%) ─ v2 (50%)
                ↓
Full switch: v2 (100%)
```

### Rolling Update

```
Pod 1: v1 -> v2 ── Health Check
Pod 2: v1 -> v2 ── Health Check
Pod 3: v1 -> v2 ── Health Check
```

## Docker Deployment

### Dockerfile Best Practices

```dockerfile
# Multi-stage build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY --from=builder /app/dist ./dist
ENV NODE_ENV=production
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/mydb
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-api
  labels:
    app: backend-api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: backend-api
  template:
    metadata:
      labels:
        app: backend-api
    spec:
      containers:
      - name: api
        image: gcr.io/my-project/backend-api:v1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-api-service
spec:
  selector:
    app: backend-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
data:
  NODE_ENV: "production"
  LOG_LEVEL: "info"
  REDIS_HOST: "redis"
  REDIS_PORT: "6379"
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secrets
type: Opaque
data:
  url: cG9zdGdyZXNxbDovL3Bvc3RncmVzOnBhc3N3b3JkQGRiOjU0MzIvbXlkYg==
  password: cGFzc3dvcmQ=
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Cloud Deployment

### AWS (ECS)

#### Task Definition

```json
{
  "family": "backend-api",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "your-registry/backend-api:latest",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:db-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/backend-api",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "256",
  "memory": "512"
}
```

### Google Cloud (Cloud Run)

#### Deployment

```bash
gcloud run deploy backend-api \
  --image gcr.io/my-project/backend-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --max-instances 100 \
  --min-instances 1 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 80 \
  --set-env-vars NODE_ENV=production \
  --set-secrets DATABASE_URL=db-url:latest
```

### Azure (Container Instances)

```bash
az container create \
  --resource-group myResourceGroup \
  --name backend-api \
  --image your-registry/backend-api:latest \
  --cpu 1 \
  --memory 1 \
  --ports 3000 \
  --environment-variables NODE_ENV=production \
  --secrets DATABASE_URL=$DATABASE_URL \
  --dns-name-label backend-api-unique
```

## CI/CD Pipelines

### GitHub Actions

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: 18

    - name: Install dependencies
      run: npm ci

    - name: Run tests
      run: npm test

    - name: Build
      run: npm run build

    - name: Build Docker image
      run: |
        docker build -t backend-api:${{ github.sha }} .
        docker tag backend-api:${{ github.sha }} backend-api:latest

    - name: Push to Registry
      run: |
        echo ${{ secrets.REGISTRY_PASSWORD }} | docker login -u ${{ secrets.REGISTRY_USER }} --password-stdin
        docker push backend-api:${{ github.sha }}
        docker push backend-api:latest

    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/backend-api api=backend-api:${{ github.sha }}
        kubectl rollout status deployment/backend-api
```

### GitLab CI

```yaml
stages:
  - build
  - test
  - deploy

variables:
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

build:
  stage: build
  script:
    - docker build -t $IMAGE_TAG .
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker push $IMAGE_TAG

test:
  stage: test
  script:
    - docker run $IMAGE_TAG npm test

deploy:
  stage: deploy
  script:
    - kubectl set image deployment/backend-api api=$IMAGE_TAG
    - kubectl rollout status deployment/backend-api
  only:
    - main
```

## Database Migrations

### Migration Strategy

```bash
# Apply migrations
npm run migrate:up

# Rollback migrations
npm run migrate:down

# Create new migration
npm run migrate:create
```

### Zero-Downtime Migration

```sql
-- Phase 1: Add new column
ALTER TABLE users ADD COLUMN new_email VARCHAR(255);

-- Phase 2: Backfill data
UPDATE users SET new_email = email;

-- Phase 3: Switch application to use new column

-- Phase 4: Drop old column
ALTER TABLE users DROP COLUMN email;
```

## Monitoring and Observability

### Logging

```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: '/var/log/app/error.log', level: 'error' }),
    new winston.transports.File({ filename: '/var/log/app/combined.log' })
  ]
});
```

### Metrics

```typescript
import { Counter, Histogram, register } from 'prom-client';

const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const requestCounter = new Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration
      .labels(req.method, req.route?.path || '', res.statusCode.toString())
      .observe(duration);
    requestCounter
      .labels(req.method, req.route?.path || '', res.statusCode.toString())
      .inc();
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
      externalApi: await checkExternalApi()
    }
  };

  const isHealthy = Object.values(health.checks).every(
    check => check.status === 'ok'
  );

  res.status(isHealthy ? 200 : 503).json(health);
});
```

## Security

### Secrets Management

```bash
# Kubernetes
kubectl create secret generic db-secrets \
  --from-literal=url=postgresql://user:pass@host:5432/db

# AWS Secrets Manager
aws secretsmanager create-secret \
  --name db-url \
  --secret-string "postgresql://user:pass@host:5432/db"

# GCP Secret Manager
gcloud secrets create db-url --data-file=- <<EOF
postgresql://user:pass@host:5432/db
EOF
```

### SSL/TLS Configuration

```yaml
# Ingress with TLS
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-api-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-api-service
            port:
              number: 80
```

## Performance Optimization

### Nginx Configuration

```nginx
upstream backend {
    server backend-api-service:3000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

### Connection Pooling

```typescript
const pool = new Pool({
  host: process.env.DB_HOST,
  port: 5432,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
});
```

## Troubleshooting

### Common Issues

#### Pod Not Starting
```bash
# Check pod status
kubectl describe pod backend-api-xxx

# Check logs
kubectl logs backend-api-xxx

# Check events
kubectl get events
```

#### Database Connection Issues
```bash
# Check connectivity
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- nslookup db-service

# Test connection
kubectl run -it --rm psql --image=postgres:15 --restart=Never -- psql postgresql://user:pass@host:5432/db
```

#### Memory Issues
```bash
# Check resource usage
kubectl top pods

# Adjust limits
kubectl patch deployment backend-api -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","resources":{"limits":{"memory":"1Gi"}}}]}}}}'
```

## Resources

- Kubernetes Docs: https://kubernetes.io/docs/
- Docker Docs: https://docs.docker.com/
- AWS ECS: https://aws.amazon.com/ecs/
- GCP Cloud Run: https://cloud.google.com/run
- Azure Container Instances: https://azure.microsoft.com/services/container-instances/
