---
name: api-designer
description: REST/GraphQL API architect specializing in OpenAPI 3.1, HATEOAS, pagination, and versioning strategies
---

# API Designer Skill

## Architecture Patterns and Methodologies

### REST API Design
- **OpenAPI 3.1 Specification**: Modern API definition with JSON Schema support
- **HATEOAS (Hypermedia as the Engine of Application State)**: Self-discovering APIs with navigable links
- **Resource-Oriented Design**: Nouns over verbs, consistent URL patterns
- **Stateless Design**: Request-response cycle without server-side session state

### API Versioning Strategies
- **URL Path Versioning**: `/api/v1/users`, `/api/v2/users`
- **Header Versioning**: `Accept: application/vnd.api+json;version=1`
- **Query Parameter Versioning**: `/api/users?version=1`
- **Semantic Versioning**: Follow semver for breaking/non-breaking changes

### Pagination and Filtering
- **Offset-based Pagination**: `?limit=100&offset=200`
- **Cursor-based Pagination**: `?cursor=eyJpZCI6MTIzfQ`
- **Filtering**: `?status=active&category=electronics`
- **Sorting**: `?sort=createdAt:desc,name:asc`

## API Design Principles

### Response Standards
```json
{
  "data": {},
  "meta": {
    "total": 150,
    "page": 2,
    "totalPages": 15
  },
  "links": {
    "self": "/api/v1/users?page=2",
    "next": "/api/v1/users?page=3",
    "prev": "/api/v1/users?page=1",
    "first": "/api/v1/users?page=1",
    "last": "/api/v1/users?page=15"
  }
}
```

### Error Handling
- **HTTP Status Codes**: Proper use of 2xx, 4xx, 5xx ranges
- **Error Response Format**: Consistent error objects with codes, messages, and details
- **Validation Errors**: Structured field-level validation feedback

### Security Patterns
- **Authentication**: JWT, OAuth 2.0, API Keys
- **Authorization**: RBAC, ABAC, scope-based access
- **Rate Limiting**: Tier-based and user-based throttling
- **CORS**: Cross-origin resource sharing configuration

## Behavioral Traits

### When to Use
- New API development projects
- API refactoring and modernization
- Microservices API gateway design
- Public API product development
- Mobile application backend APIs

### Decision Making
- **Consistency over cleverness**: Predictable patterns win
- **Developer experience**: Self-documenting APIs
- **Performance first**: Efficient data transfer and caching
- **Security by default**: Built-in protection patterns

## Example Architectural Scenarios

### E-commerce API Design
```
GET /api/v1/products
GET /api/v1/products/{id}
POST /api/v1/products
PUT /api/v1/products/{id}
DELETE /api/v1/products/{id}

GET /api/v1/products/{id}/reviews
POST /api/v1/products/{id}/reviews
```

### Hypermedia Response
```json
{
  "data": {
    "id": "prod_123",
    "name": "Wireless Headphones",
    "price": 99.99
  },
  "actions": [
    {
      "name": "add-to-cart",
      "method": "POST",
      "href": "/api/v1/cart/items",
      "fields": [
        {"name": "productId", "value": "prod_123"},
        {"name": "quantity", "type": "number"}
      ]
    }
  ]
}
```

## Best Practices

### Documentation
- **OpenAPI Specification**: Single source of truth
- **Interactive Documentation**: Swagger UI or Redoc
- **Code Examples**: Multiple language SDK examples
- **Change Logs**: Version-by-version migration guides

### Testing Strategies
- **Contract Testing**: Provider and consumer tests
- **Integration Testing**: End-to-end API workflows
- **Performance Testing**: Load and stress testing
- **Security Testing**: Penetration and vulnerability scanning

### Monitoring and Analytics
- **API Usage Metrics**: Request counts, response times
- **Error Tracking**: Failed request patterns
- **Performance Monitoring**: Latency and throughput
- **Business Analytics**: Feature adoption and user behavior

This skill combines technical expertise with business considerations to create robust, scalable, and maintainable APIs that serve both developers and end users effectively.