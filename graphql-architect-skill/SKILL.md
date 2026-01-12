---
name: graphql-architect
description: GraphQL schema and federation expert specializing in resolver optimization, subscriptions, and API gateway patterns
---

# GraphQL Architect Skill

## Architecture Patterns and Methodologies

### Schema Design Principles
- **Schema First Approach**: Design schema before implementation
- **Type Safety**: Strongly typed schema with input validation
- **Single Endpoint**: One URL for all GraphQL operations
- **Hierarchical Data**: Natural graph relationships
- **Introspection**: Self-documenting API capabilities

### GraphQL Federation Patterns
- **Schema Composition**: Multiple subgraphs into unified gateway
- **Entity Resolution**: Cross-service data fetching
- **Reference Resolvers**: Distributed data relationships
- **Federated Directives**: @key, @requires, @provides, @external
- **Schema Registry**: Central schema management and versioning

### Gateway Architecture
```
Clients → GraphQL Gateway
    ├── User Service Subgraph
    ├── Product Service Subgraph
    ├── Order Service Subgraph
    └── Inventory Service Subgraph
```

## GraphQL Schema Design

### Type System Design
```graphql
type User {
  id: ID!
  email: String!
  profile: UserProfile
  orders: [Order!]! @connection
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Query {
  user(id: ID!): User
  users(filter: UserFilter, pagination: Pagination): UserConnection!
  me: User
}

type Mutation {
  updateUser(input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
}

type Subscription {
  userUpdated(id: ID!): User!
  userCreated: User!
}
```

### Federation Directives
```graphql
# Product Service
type Product @key(fields: "id") {
  id: ID!
  name: String!
  price: Float!
  inventory: Inventory @requires(fields: "id")
}

# Inventory Service
extend type Product @key(fields: "id") {
  id: ID! @external
  inventory: Inventory!
}

type Inventory {
  available: Int!
  reserved: Int!
  location: String!
}
```

### Input Types and Validation
```graphql
input ProductFilter {
  category: String
  minPrice: Float @constraint(min: 0)
  maxPrice: Float @constraint(max: 10000)
  inStock: Boolean
  search: String @constraint(minLength: 2, maxLength: 100)
}

input CreateProductInput {
  name: String! @constraint(minLength: 1, maxLength: 200)
  description: String
  price: Float! @constraint(min: 0.01)
  categoryId: ID!
  variants: [ProductVariantInput!]!
}
```

## Resolver Optimization

### Data Loader Pattern
```javascript
const batchUsers = async (ids) => {
  const users = await User.find({ _id: { $in: ids } });
  return ids.map(id => users.find(user => user.id === id));
};

const userLoader = new DataLoader(batchUsers);

const resolvers = {
  Query: {
    user: (_, { id }) => userLoader.load(id)
  },
  Order: {
    user: (order) => userLoader.load(order.userId)
  }
};
```

### N+1 Problem Solutions
- **Data Loader**: Batch loading for related data
- **Complex Resolvers**: Efficient database queries
- **Caching Layers**: Redis, Memcached integration
- **Field-level Resolution**: Lazy loading of expensive fields

### Performance Optimizations
```javascript
// Resolver Middleware
const resolvers = {
  Query: {
    products: async (_, { filter, pagination }, context) => {
      // Efficient pagination
      const { limit, offset } = pagination;
      const query = buildProductQuery(filter);
      
      // Parallel data fetching
      const [products, totalCount] = await Promise.all([
        Product.find(query).limit(limit).skip(offset),
        Product.countDocuments(query)
      ]);
      
      return {
        edges: products,
        pageInfo: { hasNextPage: offset + limit < totalCount },
        totalCount
      };
    }
  }
};
```

## Real-time with Subscriptions

### Subscription Implementation
```javascript
const resolvers = {
  Subscription: {
    productUpdated: {
      subscribe: (_, { id }, context) => {
        return pubsub.asyncIterator(`PRODUCT_UPDATED_${id}`);
      },
      resolve: (payload) => payload.product
    },
    
    orderCreated: {
      subscribe: () => pubsub.asyncIterator('ORDER_CREATED'),
      resolve: (payload) => payload.order
    }
  }
};
```

### Event-Driven Architecture
```javascript
// Event Publishing
const publishProductUpdate = async (productId, changes) => {
  const product = await Product.findByIdAndUpdate(productId, changes, { new: true });
  await pubsub.publish(`PRODUCT_UPDATED_${productId}`, { product });
  await pubsub.publish('PRODUCTS_CHANGED', { product, operation: 'UPDATE' });
};

// Subscription Events
const productEvents = {
  'PRODUCT_CREATED': 'productCreated',
  'PRODUCT_UPDATED': 'productUpdated', 
  'PRODUCT_DELETED': 'productDeleted'
};
```

## Behavioral Traits

### When to Use GraphQL
- **Multiple Client Types**: Web, mobile, third-party integrations
- **Complex Data Relationships**: Nested and interconnected data
- **Rapid Iteration**: Evolving API requirements
- **Client-Driven Development**: Frontend teams need flexibility
- **Mobile Applications**: Reduce over-fetching for bandwidth efficiency

### Decision Framework
- **Data Complexity**: High complexity favors GraphQL
- **Team Structure**: Multiple client teams benefit from GraphQL
- **Performance Requirements**: Consider latency and bandwidth
- **Caching Strategies**: HTTP caching vs. GraphQL-specific caching

## Integration Patterns

### Database Integration
```javascript
// Multi-database resolvers
const resolvers = {
  User: {
    orders: async (user) => {
      // MongoDB for orders
      return await Order.find({ userId: user.id });
    },
    
    profile: async (user) => {
      // PostgreSQL for profile
      return await Profile.findOne({ userId: user.id });
    }
  }
};
```

### External API Integration
```javascript
const resolvers = {
  Product: {
    reviews: async (product) => {
      // External review service
      const response = await fetch(`${REVIEWS_API}/products/${product.id}/reviews`);
      return response.json();
    },
    
    availability: async (product) => {
      // Inventory microservice
      return await inventoryService.getAvailability(product.id);
    }
  }
};
```

## Security and Authorization

### Field-Level Authorization
```javascript
const resolvers = {
  Query: {
    user: (_, { id }, context) => {
      // Authentication check
      if (!context.user) throw new AuthenticationError('Unauthorized');
      
      // Authorization check
      if (context.user.id !== id && !context.user.isAdmin) {
        throw new ForbiddenError('Cannot access other users');
      }
      
      return User.findById(id);
    }
  }
};
```

### Schema Directives
```graphql
directive @auth(role: String) on FIELD_DEFINITION
directive @rateLimit(limit: Int, window: Int) on FIELD_DEFINITION

type Query {
  adminUsers: [User!]! @auth(role: "admin") @rateLimit(limit: 100, window: 60)
  publicProducts: [Product!]!
}
```

## Performance Monitoring

### Query Complexity Analysis
```javascript
const complexity = new ComplexityExtension({
  // Simple complexity estimation
  estimators: [
    (type, fieldName, args) => {
      if (type === 'Query' && fieldName === 'users') {
        return args.pagination?.limit || 10;
      }
      return 1;
    }
  ],
  // Maximum complexity allowed
  maximumComplexity: 1000
});
```

### Performance Metrics
- **Query Analysis**: Execution time, complexity, data transferred
- **Resolver Performance**: Individual resolver timing
- **Database Query Analysis**: Slow query identification
- **Cache Hit Rates**: Effectiveness of caching strategies

## Best Practices

### Schema Evolution
- **Non-Breaking Changes**: Add fields, deprecate old fields
- **Versioning Strategy**: Semantic versioning for schemas
- **Backward Compatibility**: Support existing clients
- **Migration Planning**: Smooth transition paths

### Testing Strategies
- **Schema Testing**: Validate schema structure and types
- **Resolver Unit Testing**: Individual resolver logic
- **Integration Testing**: End-to-end query execution
- **Performance Testing**: Load testing for complex queries

### Documentation Standards
- **Schema Documentation**: Descriptions for all types and fields
- **Query Examples**: Common usage patterns
- **Deprecation Notices**: Clear migration paths for changes
- **API Guides**: Getting started and best practices

This skill combines GraphQL expertise with performance optimization and distributed systems patterns to create efficient, scalable, and maintainable GraphQL APIs.