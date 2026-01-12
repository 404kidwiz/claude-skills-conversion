---
name: spring-boot-engineer
description: Spring Boot 3+ specialist with expertise in Spring Cloud, microservices, and Kubernetes deployment
---

# Spring Boot Engineer

## Core Capabilities

### Spring Boot 3+ Features
- **Java 17+ Integration**: Full support for modern Java features including records, pattern matching, and sealed classes
- **Native Compilation**: GraalVM native image support for optimal performance
- **Observability**: Built-in Micrometer metrics, distributed tracing with OpenTelemetry
- **Configuration**: YAML/Properties configuration with environment profiles and Cloud Config
- **Startup Performance**: Lazy initialization, classpath scanning optimization

### Spring Cloud Expertise
- **Service Discovery**: Eureka, Consul, Kubernetes service discovery
- **API Gateway**: Spring Cloud Gateway with reactive routing and filters
- **Circuit Breakers**: Resilience4j implementation for fault tolerance
- **Load Balancing**: Spring Cloud LoadBalancer client-side load balancing
- **Configuration Management**: Centralized config server with Git/Vault backends
- **Message Bus**: RabbitMQ, Kafka integration with Spring Cloud Stream

### Container Orchestration
- **Kubernetes Deployment**: Helm charts, ConfigMaps, Secrets management
- **Docker Optimization**: Multi-stage builds, layer optimization, health checks
- **Service Mesh**: Istio integration for advanced traffic management
- **Resource Management**: CPU/Memory limits, HPA (Horizontal Pod Autoscaling)

## Architecture Patterns

### Microservices Design
```java
@SpringBootApplication
@EnableEurekaClient
@EnableCircuitBreaker
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}
```

### RESTful API Development
```java
@RestController
@RequestMapping("/api/v1/orders")
@Validated
public class OrderController {
    
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
            @Valid @RequestBody CreateOrderRequest request) {
        Order order = orderService.createOrder(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(OrderResponse.from(order));
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<OrderResponse> getOrder(@PathVariable UUID id) {
        return orderService.findById(id)
                .map(OrderResponse::from)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
```

### Data Access Layer
```java
@Service
@Transactional
public class OrderService {
    
    private final OrderRepository orderRepository;
    private final OrderMapper orderMapper;
    
    public Order createOrder(CreateOrderRequest request) {
        Order order = orderMapper.toEntity(request);
        order.setOrderNumber(generateOrderNumber());
        order.setStatus(OrderStatus.PENDING);
        return orderRepository.save(order);
    }
    
    @Retryable(maxAttempts = 3, backoff = @Backoff(delay = 1000))
    public Optional<Order> findById(UUID id) {
        return orderRepository.findByIdWithItems(id);
    }
}
```

## Development Best Practices

### Configuration Management
```yaml
# application.yml
spring:
  application:
    name: order-service
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}
  datasource:
    url: ${DATABASE_URL:jdbc:postgresql://localhost:5432/orders}
    username: ${DATABASE_USERNAME:orders}
    password: ${DATABASE_PASSWORD:password}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    properties:
      hibernate.format_sql: true

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when-authorized
```

### Exception Handling
```java
@ControllerAdvice
@Slf4j
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ErrorResponse> handleValidation(
            ValidationException ex) {
        log.warn("Validation error: {}", ex.getMessage());
        return ResponseEntity.badRequest()
                .body(ErrorResponse.of("VALIDATION_ERROR", ex.getMessage()));
    }
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            ResourceNotFoundException ex) {
        log.info("Resource not found: {}", ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(ErrorResponse.of("NOT_FOUND", ex.getMessage()));
    }
}
```

## Testing Strategies

### Unit Testing with JUnit 5
```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    
    @Mock
    private OrderRepository orderRepository;
    
    @InjectMocks
    private OrderService orderService;
    
    @Test
    @DisplayName("Should create order successfully")
    void createOrder_Success() {
        // Given
        CreateOrderRequest request = OrderTestData.createOrderRequest();
        Order expectedOrder = OrderTestData.newOrder();
        when(orderRepository.save(any(Order.class))).thenReturn(expectedOrder);
        
        // When
        Order result = orderService.createOrder(request);
        
        // Then
        assertThat(result.getStatus()).isEqualTo(OrderStatus.PENDING);
        assertThat(result.getOrderNumber()).isNotNull();
        verify(orderRepository).save(any(Order.class));
    }
}
```

### Integration Testing
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestPropertySource(properties = {
    "spring.datasource.url=jdbc:h2:mem:testdb",
    "spring.jpa.hibernate.ddl-auto=create-drop"
})
@Testcontainers
class OrderControllerIntegrationTest {
    
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Test
    void createOrder_Integration() {
        CreateOrderRequest request = OrderTestData.createOrderRequest();
        ResponseEntity<OrderResponse> response = restTemplate.postForEntity(
                "/api/v1/orders", request, OrderResponse.class);
        
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody().getOrderNumber()).isNotNull();
    }
}
```

## Performance Optimization

### Caching Strategies
```java
@Service
public class ProductCacheService {
    
    @Cacheable(value = "products", key = "#id", unless = "#result.price == null")
    public Product getProduct(UUID id) {
        return productRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found"));
    }
    
    @CacheEvict(value = "products", key = "#product.id")
    public Product updateProduct(Product product) {
        return productRepository.save(product);
    }
}
```

### Async Processing
```java
@Service
public class NotificationService {
    
    @Async("notificationExecutor")
    public CompletableFuture<Void> sendOrderConfirmation(Order order) {
        emailService.sendOrderConfirmation(order);
        smsService.sendOrderSms(order);
        return CompletableFuture.completedFuture(null);
    }
}

@Configuration
@EnableAsync
public class AsyncConfig {
    
    @Bean("notificationExecutor")
    public Executor notificationExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("Notification-");
        executor.initialize();
        return executor;
    }
}
```

## Security Implementation

### Spring Security Configuration
```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/v1/orders/**").hasRole("USER")
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> 
                oauth2.jwt(withDefaults()));
        
        return http.build();
    }
}
```

## Monitoring & Observability

### Metrics Configuration
```java
@Component
public class OrderMetrics {
    
    private final MeterRegistry meterRegistry;
    private final Counter orderCreatedCounter;
    private final Timer orderProcessingTimer;
    
    public OrderMetrics(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.orderCreatedCounter = Counter.builder("orders.created")
                .description("Total orders created")
                .register(meterRegistry);
        this.orderProcessingTimer = Timer.builder("orders.processing.time")
                .description("Order processing time")
                .register(meterRegistry);
    }
    
    public void recordOrderCreated() {
        orderCreatedCounter.increment();
    }
    
    public void recordProcessingTime(Duration duration) {
        orderProcessingTimer.record(duration);
    }
}
```

## Common Use Cases

### Event-Driven Architecture
```java
@KafkaListener(topics = "order-events", groupId = "order-service")
public void handleOrderEvent(OrderEvent event) {
    switch (event.getEventType()) {
        case ORDER_CREATED:
            paymentService.processPayment(event.getOrderId());
            inventoryService.reserveItems(event.getOrderItems());
            break;
        case PAYMENT_COMPLETED:
            shippingService.initiateShipping(event.getOrderId());
            break;
        case PAYMENT_FAILED:
            notificationService.sendPaymentFailedNotification(event.getOrderId());
            break;
    }
}
```

### Background Jobs
```java
@Component
public class OrderCleanupJob {
    
    @Scheduled(cron = "0 0 2 * * ?") // Daily at 2 AM
    public void cleanupExpiredOrders() {
        List<Order> expiredOrders = orderRepository
                .findExpiredOrders(LocalDateTime.now().minusDays(30));
        
        expiredOrders.forEach(order -> {
            order.setStatus(OrderStatus.CANCELLED);
            order.setCancellationReason("Auto-cancelled - expired");
        });
        
        orderRepository.saveAll(expiredOrders);
        log.info("Cleaned up {} expired orders", expiredOrders.size());
    }
}
```

This Spring Boot skill provides comprehensive expertise for building production-ready microservices with modern Spring ecosystem tools and Kubernetes deployment strategies.