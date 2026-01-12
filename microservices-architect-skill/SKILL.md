---
name: microservices-architect
description: Distributed systems expert specializing in service decomposition, orchestration, and microservices architecture patterns
---

# Microservices Architect Skill

## Architecture Patterns and Methodologies

### Service Decomposition Strategies
- **Domain-Driven Design (DDD)**: Bounded contexts as service boundaries
- **Single Responsibility Principle**: One business capability per service
- **Database-per-Service**: Each service owns its data persistence
- **Strangler Fig Pattern**: Gradual migration from monolith to microservices

### Communication Patterns
- **Synchronous Communication**: REST APIs, gRPC, GraphQL
- **Asynchronous Communication**: Message queues, event streaming
- **Event-Driven Architecture**: Domain events for loose coupling
- **CQRS (Command Query Responsibility Segregation)**: Separate read/write models

### Service Discovery and Registry
- **Service Registration**: Eureka, Consul, etcd
- **DNS-Based Discovery**: Kubernetes services
- **Client-Side Load Balancing**: Ribbon, Spring Cloud LoadBalancer
- **Server-Side Load Balancing**: NGINX, HAProxy, Envoy

## Service Boundaries and Communication

### API Gateway Patterns
```
Client → API Gateway → Services
         ↓
    Authentication
    Rate Limiting
    Request Routing
    Response Aggregation
    Circuit Breaking
```

### Inter-Service Communication
- **REST**: HTTP-based synchronous communication
- **gRPC**: High-performance binary protocol
- **Message Queues**: RabbitMQ, AWS SQS, Apache Kafka
- **Event Streams**: Kafka, Kinesis, NATS

### Data Management Patterns
- **Saga Pattern**: Distributed transaction management
- **Event Sourcing**: Immutable event logs as state source
- **CQRS**: Separate read/write data stores
- **Database-per-Service**: Independent data ownership

## Orchestration and Choreography

### Service Orchestration
- **Centralized Coordinator**: Single service manages workflow
- **Workflow Engines**: Camunda, Temporal, AWS Step Functions
- **Business Process Modeling**: BPMN for complex workflows
- **State Management**: Distributed state machines

### Event Choreography
- **Decentralized Events**: Each service responds to domain events
- **Event Bus**: Message brokers for event distribution
- **Event Sourcing**: Event-driven state changes
- **Snapshot Management**: Performance optimization for event stores

### Hybrid Approaches
- **Orchestration for Sagas**: Complex distributed transactions
- **Choreography for Events**: Simple notifications and updates
- **Pattern Selection**: Use case-based decision framework

## Behavioral Traits

### When to Use
- **Large, Complex Applications**: Multiple teams, complex domains
- **Independent Scalability**: Different scaling requirements per component
- **Technology Diversity**: Multiple programming languages/frameworks
- **Organizational Scaling**: Team autonomy and independent deployment

### Decision Framework
- **Conway's Law**: System design mirrors communication structure
- **Trade-off Analysis**: Consistency vs. Availability vs. Partition Tolerance
- **Operational Complexity**: Monitoring, deployment, and debugging overhead
- **Business Impact**: Time-to-market vs. technical debt

## Example Architectural Scenarios

### E-commerce Microservices
```
API Gateway
├── User Service (Authentication, Profiles)
├── Product Service (Catalog, Inventory)
├── Order Service (Order Management, Processing)
├── Payment Service (Payment Processing, Refunds)
├── Notification Service (Email, SMS, Push)
└── Analytics Service (Reporting, Metrics)
```

### Service Communication Flow
```
Order Service
├── Validates inventory (Product Service)
├── Processes payment (Payment Service)
├── Creates order (Local Database)
├── Sends confirmation (Notification Service)
└── Updates analytics (Analytics Service)
```

## Resilience and Fault Tolerance

### Circuit Breaker Pattern
```yaml
circuit-breaker:
  failure-rate-threshold: 50%
  wait-duration-in-open-state: 30s
  sliding-window-size: 20
  permitted-number-of-calls-in-half-open-state: 5
```

### Retry Patterns
- **Exponential Backoff**: Increasing delays between retries
- **Jitter**: Randomization to prevent thundering herd
- **Circuit Breaking**: Stop retries after consecutive failures
- **Timeout Management**: Appropriate timeout values per operation

### Bulkhead Isolation
- **Thread Pool Isolation**: Separate thread pools per service
- **Semaphore Isolation**: Limit concurrent requests per service
- **Process Isolation**: Separate containers/vm per critical service
- **Resource Quotas**: CPU, memory, and network limits

## DevOps and Observability

### Deployment Strategies
- **Blue-Green Deployment**: Zero-downtime deployments
- **Canary Releases**: Gradual traffic shifting
- **Feature Flags**: Runtime feature toggling
- **Rolling Updates**: Incremental service updates

### Monitoring and Observability
- **Distributed Tracing**: Jaeger, Zipkin, AWS X-Ray
- **Metrics Collection**: Prometheus, CloudWatch, DataDog
- **Log Aggregation**: ELK Stack, Splunk, Fluentd
- **Health Checks**: Service availability and dependency health

### Configuration Management
- **External Configuration**: Spring Cloud Config, Consul KV
- **Environment Variables**: Container-based configuration
- **Configuration Secrets**: HashiCorp Vault, AWS Secrets Manager
- **Dynamic Configuration**: Runtime configuration updates

## Best Practices

### Service Design Principles
- **High Cohesion**: Related functionality in single service
- **Low Coupling**: Minimal dependencies between services
- **Autonomous Development**: Independent teams per service
- **Failure Isolation**: Service failures don't cascade

### Data Considerations
- **Eventual Consistency**: Accept temporary data inconsistencies
- **Data Ownership**: Clear ownership of data entities
- **Replication Strategies**: Read replicas, multi-region deployment
- **Backup and Recovery**: Service-specific backup strategies

### Performance Optimization
- **Connection Pooling**: Database and external service connections
- **Caching Strategies**: Redis, Memcached, application-level caching
- **Async Processing**: Non-blocking operations for better throughput
- **Resource Management**: Efficient CPU and memory usage

This skill combines distributed systems expertise with practical implementation patterns to create scalable, resilient, and maintainable microservices architectures.