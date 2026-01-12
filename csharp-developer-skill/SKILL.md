---
name: csharp-developer
description: .NET 8 and C# 12 specialist with expertise in ASP.NET Core, EF Core, and modern enterprise development
---

# C# Developer

## Core Capabilities

### C# 12 Language Features
- **Primary Constructors**: Simplified class and struct initialization
- **Collection Expressions**: Natural syntax for creating collections `[1, 2, 3]`
- **Lambda Improvements**: Default parameters, explicit return types
- **Ref Readonly Parameters**: Performance optimization for large structs
- **Experimental Attributes**: Mark preview features explicitly
- **Inline Arrays**: Fixed-size buffers without unsafe code
- **Interceptors**: Method call interception for AOP scenarios

### .NET 8 Platform Features
- **Native AOT**: Compile to native executables for reduced memory and faster startup
- **Blazor United**: Server and WebAssembly seamless rendering
- **Minimal API Enhancements**: Better routing, binding, and OpenAPI generation
- **JSON Improvements**: Source generation for better performance
- **Cloud Native**: Container optimization, health checks, metrics
- **Performance**: Span<T>, Memory<T>, ValueTask for zero-allocation operations

### ASP.NET Core Web API
- **Performance**: 30% faster request processing in .NET 8
- **Minimal APIs**: Simplified endpoint definitions
- **OpenAPI Integration**: Automatic Swagger generation
- **Authentication**: JWT, OAuth, OpenID Connect
- **Rate Limiting**: Built-in request throttling
- **Output Caching**: Intelligent response caching

## Architecture Patterns

### Modern ASP.NET Core Application
```csharp
// Program.cs - Minimal API with modern patterns
using Microsoft.AspNetCore.OpenApi;
using System.Security.Claims;

var builder = WebApplication.CreateBuilder(args);

// Configure services
builder.Services.AddAuthentication()
    .AddJwtBearer();
builder.Services.AddAuthorization();

builder.Services.AddDbContext<OrderDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddScoped<ICustomerService, CustomerService>();
builder.Services.AddAutoMapper(AppDomain.CurrentDomain.GetAssemblies());

// Health checks
builder.Services.AddHealthChecks()
    .AddDbContextCheck<OrderDbContext>()
    .AddRedis(builder.Configuration.GetConnectionString("Redis"));

// Rate limiting
builder.Services.AddRateLimiter(options =>
{
    options.AddPolicy("Api", context =>
        RateLimitPartition.GetSlidingWindowLimiter(
            partitionKey: context.Connection.RemoteIpAddress?.ToString() ?? "anonymous",
            factory: _ => new SlidingWindowRateLimiterOptions
            {
                PermitLimit = 100,
                Window = TimeSpan.FromMinutes(1),
                SegmentsPerWindow = 3
            }));
});

var app = builder.Build();

// Middleware pipeline
app.UseAuthentication();
app.UseAuthorization();
app.UseRateLimiter();

// OpenAPI documentation
app.MapOpenApi();

// API Endpoints
var orders = app.MapGroup("/api/orders")
    .RequireAuthorization()
    .WithTags("Orders")
    .AddEndpointFilter<RequestLoggingFilter>()
    .RequireRateLimiting("Api");

orders.MapPost("/", async (CreateOrderRequest request, IOrderService service) =>
    Results.Created($"/api/orders/{result.Id}", await service.CreateOrderAsync(request)))
    .Accepts<CreateOrderRequest>("application/json")
    .Produces<OrderDto>(StatusCodes.Status201Created)
    .ProducesValidationProblem(StatusCodes.Status400BadRequest);

orders.MapGet("/{id:guid}", async (Guid id, IOrderService service) =>
    await service.GetOrderAsync(id) is { } order
        ? Results.Ok(order)
        : Results.NotFound())
    .Produces<OrderDto>()
    .ProducesProblem(StatusCodes.Status404NotFound);

// Advanced routing with delegates
orders.MapGet("/customer/{customerId:guid}", async (
    Guid customerId, 
    [FromQuery] int page = 1,
    [FromQuery] int size = 10,
    IOrderService service) =>
{
    var pagedOrders = await service.GetOrdersByCustomerAsync(customerId, page, size);
    return Results.Ok(pagedOrders);
});

app.MapHealthChecks("/health");

app.Run();
```

### Domain-Driven Design with C# 12 Features
```csharp
// Domain/Order.cs - Rich domain model
namespace OrderSystem.Domain;

public record OrderId(Guid Value);

public record CustomerId(Guid Value);

public record OrderStatus(string Value)
{
    public static OrderStatus Pending = new("pending");
    public static OrderStatus Processing = new("processing");
    public static OrderStatus Completed = new("completed");
    public static OrderStatus Cancelled = new("cancelled");
    
    private static readonly OrderStatus[] All = [Pending, Processing, Completed, Cancelled];
    
    public static bool IsValid(string value) => All.Any(s => s.Value == value);
}

public readonly struct Money(decimal Amount, string Currency)
{
    public decimal Amount { get; } = Amount;
    public string Currency { get; } = Currency;
    
    public static Money Zero(string currency) => new(0m, currency);
    
    public Money Add(Money other) => other.Currency != Currency 
        ? throw new ArgumentException("Currency mismatch") 
        : new(Amount + other.Amount, Currency);
    
    public Money Multiply(decimal factor) => new(Amount * factor, Currency);
    
    public static implicit operator decimal(Money money) => money.Amount;
}

public sealed class Order
{
    private readonly List<OrderItem> _items = [];
    
    public OrderId Id { get; init; } = OrderId.New();
    public CustomerId CustomerId { get; private set; }
    public IReadOnlyList<OrderItem> Items => _items.AsReadOnly();
    public OrderStatus Status { get; private set; } = OrderStatus.Pending;
    public Money TotalAmount { get; private set; }
    public DateTime CreatedAt { get; } = DateTime.UtcNow;
    public DateTime? UpdatedAt { get; private set; }
    
    // Primary constructor (C# 12)
    public Order(CustomerId customerId, Money currency)
    {
        CustomerId = customerId;
        TotalAmount = Money.Zero(currency.Currency);
    }
    
    public void AddItem(ProductId productId, int quantity, Money unitPrice)
    {
        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException("Cannot add items to non-pending order");
            
        if (quantity <= 0)
            throw new ArgumentException("Quantity must be positive");
        
        var existingItem = _items.FirstOrDefault(i => i.ProductId == productId);
        if (existingItem is not null)
        {
            existingItem.UpdateQuantity(existingItem.Quantity + quantity);
        }
        else
        {
            var item = new OrderItem(productId, quantity, unitPrice);
            _items.Add(item);
        }
        
        RecalculateTotal();
        UpdatedAt = DateTime.UtcNow;
    }
    
    public void MarkAsProcessing()
    {
        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException("Order must be pending to start processing");
            
        Status = OrderStatus.Processing;
        UpdatedAt = DateTime.UtcNow;
    }
    
    public void Complete()
    {
        if (Status != OrderStatus.Processing)
            throw new InvalidOperationException("Order must be processing to complete");
            
        Status = OrderStatus.Completed;
        UpdatedAt = DateTime.UtcNow;
    }
    
    public void Cancel(string reason)
    {
        if (Status is OrderStatus.Completed)
            throw new InvalidOperationException("Cannot cancel completed order");
            
        Status = OrderStatus.Cancelled;
        UpdatedAt = DateTime.UtcNow;
        // Domain event could be raised here
    }
    
    private void RecalculateTotal()
    {
        var currency = _items.FirstOrDefault()?.UnitPrice.Currency ?? "USD";
        var total = _items.Aggregate(
            Money.Zero(currency), 
            (acc, item) => acc.Add(item.TotalPrice)
        );
        TotalAmount = total;
    }
}

public record OrderItem(ProductId ProductId, int Quantity, Money UnitPrice)
{
    public Money TotalPrice => UnitPrice.Multiply(Quantity);
    
    public void UpdateQuantity(int newQuantity)
    {
        if (newQuantity <= 0)
            throw new ArgumentException("Quantity must be positive");
            
        Quantity = newQuantity;
    }
}

// Domain events for event sourcing
public abstract record DomainEvent(DateTime OccurredAt = default)
{
    public DateTime OccurredAt { get; } = OccurredAt == default ? DateTime.UtcNow : OccurredAt;
}

public record OrderCreated(OrderId OrderId, CustomerId CustomerId) : DomainEvent;
public record OrderItemAdded(OrderId OrderId, ProductId ProductId, int Quantity, Money UnitPrice) : DomainEvent;
public record OrderCompleted(OrderId OrderId) : DomainEvent;
```

### Modern Service Layer with C# 12
```csharp
// Application/Services/OrderService.cs
namespace OrderSystem.Application.Services;

public interface IOrderService
{
    Task<OrderDto> CreateOrderAsync(CreateOrderRequest request, CancellationToken cancellationToken = default);
    Task<OrderDto?> GetOrderAsync(OrderId orderId, CancellationToken cancellationToken = default);
    Task<PagedResult<OrderDto>> GetOrdersByCustomerAsync(
        CustomerId customerId, int page, int size, CancellationToken cancellationToken = default);
    Task<OrderDto> UpdateOrderStatusAsync(
        OrderId orderId, OrderStatus status, CancellationToken cancellationToken = default);
}

public class OrderService(
    IOrderRepository orderRepository,
    IProductRepository productRepository,
    IUnitOfWork unitOfWork,
    IMapper mapper,
    ILogger<OrderService> logger) : IOrderService
{
    public async Task<OrderDto> CreateOrderAsync(
        CreateOrderRequest request, CancellationToken cancellationToken = default)
    {
        var customerId = new CustomerId(request.CustomerId);
        var currency = Money.Zero("USD"); // Default currency
        
        var order = new Order(customerId, currency);
        
        // Validate and add items
        foreach (var itemRequest in request.Items)
        {
            var product = await productRepository.GetByIdAsync(new ProductId(itemRequest.ProductId), cancellationToken)
                         ?? throw new NotFoundException($"Product {itemRequest.ProductId} not found");
            
            if (!product.IsInStock)
                throw new DomainException($"Product {product.Id} is out of stock");
            
            if (itemRequest.Quantity > product.AvailableQuantity)
                throw new DomainException($"Insufficient stock for product {product.Id}");
            
            order.AddItem(product.Id, itemRequest.Quantity, product.Price);
        }
        
        // Business rule validation
        if (order.TotalAmount.Amount <= 0)
            throw new DomainException("Order total must be greater than zero");
        
        if (order.TotalAmount.Amount > 10000)
            throw new DomainException("Order total exceeds maximum allowed amount");
        
        await orderRepository.AddAsync(order, cancellationToken);
        await unitOfWork.SaveChangesAsync(cancellationToken);
        
        logger.LogInformation("Order {OrderId} created for customer {CustomerId} with total {TotalAmount}",
            order.Id, order.CustomerId, order.TotalAmount);
        
        return mapper.Map<OrderDto>(order);
    }
    
    public async Task<OrderDto?> GetOrderAsync(OrderId orderId, CancellationToken cancellationToken = default)
    {
        var order = await orderRepository.GetByIdAsync(orderId, cancellationToken);
        return order is not null ? mapper.Map<OrderDto>(order) : null;
    }
    
    public async Task<PagedResult<OrderDto>> GetOrdersByCustomerAsync(
        CustomerId customerId, int page, int size, CancellationToken cancellationToken = default)
    {
        var (orders, total) = await orderRepository.GetByCustomerAsync(customerId, page, size, cancellationToken);
        var orderDtos = mapper.Map<IReadOnlyList<OrderDto>>(orders);
        
        return new PagedResult<OrderDto>(orderDtos, total, page, size);
    }
    
    public async Task<OrderDto> UpdateOrderStatusAsync(
        OrderId orderId, OrderStatus status, CancellationToken cancellationToken = default)
    {
        var order = await orderRepository.GetByIdAsync(orderId, cancellationToken)
                   ?? throw new NotFoundException($"Order {orderId} not found");
        
        switch (status.Value)
        {
            case "processing":
                order.MarkAsProcessing();
                break;
            case "completed":
                order.Complete();
                break;
            case "cancelled":
                order.Cancel("Cancelled by admin");
                break;
            default:
                throw new ArgumentException($"Invalid status: {status.Value}");
        }
        
        await orderRepository.UpdateAsync(order, cancellationToken);
        await unitOfWork.SaveChangesAsync(cancellationToken);
        
        return mapper.Map<OrderDto>(order);
    }
}

// Repository pattern with C# 12 features
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(OrderId orderId, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<Order>> GetByCustomerAsync(
        CustomerId customerId, int page, int size, CancellationToken cancellationToken = default);
    Task<(IReadOnlyList<Order> Orders, int Total)> GetByCustomerWithCountAsync(
        CustomerId customerId, int page, int size, CancellationToken cancellationToken = default);
    Task AddAsync(Order order, CancellationToken cancellationToken = default);
    Task UpdateAsync(Order order, CancellationToken cancellationToken = default);
}

public class EfOrderRepository(OrderDbContext context) : IOrderRepository
{
    public async Task<Order?> GetByIdAsync(OrderId orderId, CancellationToken cancellationToken = default) =>
        await context.Orders
            .Include(o => o.Items)
            .FirstOrDefaultAsync(o => o.Id == orderId, cancellationToken);

    public async Task<IReadOnlyList<Order>> GetByCustomerAsync(
        CustomerId customerId, int page, int size, CancellationToken cancellationToken = default) =>
        await context.Orders
            .Include(o => o.Items)
            .Where(o => o.CustomerId == customerId)
            .OrderByDescending(o => o.CreatedAt)
            .Skip((page - 1) * size)
            .Take(size)
            .ToListAsync(cancellationToken);

    public async Task<(IReadOnlyList<Order> Orders, int Total)> GetByCustomerWithCountAsync(
        CustomerId customerId, int page, int size, CancellationToken cancellationToken = default)
    {
        var query = context.Orders
            .Include(o => o.Items)
            .Where(o => o.CustomerId == customerId);
            
        var total = await query.CountAsync(cancellationToken);
        var orders = await query
            .OrderByDescending(o => o.CreatedAt)
            .Skip((page - 1) * size)
            .Take(size)
            .ToListAsync(cancellationToken);
            
        return (orders, total);
    }

    public async Task AddAsync(Order order, CancellationToken cancellationToken = default)
    {
        await context.Orders.AddAsync(order, cancellationToken);
    }

    public Task UpdateAsync(Order order, CancellationToken cancellationToken = default)
    {
        context.Orders.Update(order);
        return Task.CompletedTask;
    }
}
```

## Performance Optimization

### High-Performance Data Access with EF Core 8
```csharp
// Data/Configurations/OrderConfiguration.cs
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.HasKey(o => o.Id);
        
        builder.Property(o => o.Id)
            .HasConversion(
                id => id.Value,
                value => new OrderId(value));
            
        builder.Property(o => o.CustomerId)
            .HasConversion(
                id => id.Value,
                value => new CustomerId(value));
            
        builder.OwnsOne(o => o.TotalAmount, money =>
        {
            money.Property(m => m.Amount)
                .HasPrecision(18, 2)
                .HasColumnName("total_amount");
            money.Property(m => m.Currency)
                .HasMaxLength(3)
                .HasColumnName("currency");
        });
        
        builder.Property(o => o.Status)
            .HasConversion(
                status => status.Value,
                value => new OrderStatus(value))
            .HasMaxLength(20);
            
        builder.Property(o => o.CreatedAt)
            .HasDefaultValueSql("CURRENT_TIMESTAMP");
            
        builder.HasIndex(o => o.CustomerId);
        builder.HasIndex(o => o.Status);
        builder.HasIndex(o => o.CreatedAt);
        
        // Query filter for soft deletes if needed
        builder.HasQueryFilter(o => o.Status.Value != "deleted");
    }
}

// Performance-optimized queries
public class OrderQueryService(OrderDbContext context)
{
    public async Task<PagedResult<OrderDto>> GetOrdersWithFiltersAsync(
        OrderFilter filter,
        PaginationOptions pagination,
        CancellationToken cancellationToken = default)
    {
        var query = context.Orders
            .AsNoTracking()
            .Include(o => o.Items)
            .AsSplitQuery() // Split queries for better performance
            .Where(o => o.Status.Value == filter.Status);
            
        if (!string.IsNullOrEmpty(filter.CustomerId))
        {
            query = query.Where(o => o.CustomerId.Value.ToString() == filter.CustomerId);
        }
        
        if (filter.MinAmount.HasValue)
        {
            query = query.Where(o => o.TotalAmount.Amount >= filter.MinAmount.Value);
        }
        
        if (filter.MaxAmount.HasValue)
        {
            query = query.Where(o => o.TotalAmount.Amount <= filter.MaxAmount.Value);
        }
        
        if (filter.StartDate.HasValue)
        {
            query = query.Where(o => o.CreatedAt >= filter.StartDate.Value);
        }
        
        if (filter.EndDate.HasValue)
        {
            query = query.Where(o => o.CreatedAt <= filter.EndDate.Value);
        }
        
        // Use compiled queries for better performance
        var totalCount = await query.CountAsync(cancellationToken);
        
        var orders = await query
            .OrderByDescending(o => o.CreatedAt)
            .Skip((pagination.Page - 1) * pagination.Size)
            .Take(pagination.Size)
            .ToListAsync(cancellationToken);
            
        return new PagedResult<OrderDto>(orders, totalCount, pagination.Page, pagination.Size);
    }
    
    // Compiled query for frequently executed query
    private static readonly Func<OrderDbContext, CustomerId, IAsyncEnumerable<Order>> GetOrdersByCustomerCompiled =
        EF.CompileAsyncQuery((OrderDbContext context, CustomerId customerId) =>
            context.Orders
                .Include(o => o.Items)
                .Where(o => o.CustomerId == customerId)
                .OrderByDescending(o => o.CreatedAt));
    
    public async Task<IReadOnlyList<OrderDto>> GetOrdersByCustomerOptimizedAsync(
        CustomerId customerId,
        CancellationToken cancellationToken = default)
    {
        var orders = new List<Order>();
        await foreach (var order in GetOrdersByCustomerCompiled(context, customerId))
        {
            orders.Add(order);
        }
        
        return orders.Select(o => new OrderDto
        {
            Id = o.Id.Value,
            CustomerId = o.CustomerId.Value,
            Status = o.Status.Value,
            TotalAmount = o.TotalAmount.Amount,
            Currency = o.TotalAmount.Currency,
            CreatedAt = o.CreatedAt,
            Items = o.Items.Select(item => new OrderItemDto
            {
                ProductId = item.ProductId.Value,
                Quantity = item.Quantity,
                UnitPrice = item.UnitPrice.Amount,
                TotalPrice = item.TotalPrice.Amount
            }).ToList()
        }).ToList();
    }
}
```

## Modern C# Patterns

### Functional Programming with Records and Pattern Matching
```csharp
// Application/Validators/OrderValidator.cs
public static class OrderValidator
{
    public static Result<Order> Validate(CreateOrderRequest request)
    {
        return ValidateCustomer(request.CustomerId)
            .Bind(() => ValidateItems(request.Items))
            .Bind(items => CreateOrder(request.CustomerId, items));
    }
    
    private static Result<CustomerId> ValidateCustomer(string customerIdStr)
    {
        return Guid.TryParse(customerIdStr, out var customerId)
            ? Result.Ok(new CustomerId(customerId))
            : Result.Error<CustomerId>("Invalid customer ID format");
    }
    
    private static Result<List<OrderItemRequest>> ValidateItems(List<OrderItemRequest> items)
    {
        return items.Count switch
        {
            0 => Result.Error<List<OrderItemRequest>>("Order must contain at least one item"),
            > 50 => Result.Error<List<OrderItemRequest>>("Order cannot contain more than 50 items"),
            _ => ValidateItemDetails(items)
        };
    }
    
    private static Result<List<OrderItemRequest>> ValidateItemDetails(List<OrderItemRequest> items)
    {
        var errors = new List<string>();
        
        foreach (var item in items)
        {
            if (item.Quantity <= 0)
                errors.Add($"Product {item.ProductId}: quantity must be positive");
                
            if (item.UnitPrice <= 0)
                errors.Add($"Product {item.ProductId}: unit price must be positive");
        }
        
        return errors.Count > 0 
            ? Result.Error<List<OrderItemRequest>>(string.Join("; ", errors))
            : Result.Ok(items);
    }
    
    private static Result<Order> CreateOrder(string customerIdStr, List<OrderItemRequest> items)
    {
        try
        {
            var customerId = new CustomerId(Guid.Parse(customerIdStr));
            var order = new Order(customerId, Money.Zero("USD"));
            
            foreach (var item in items)
            {
                order.AddItem(
                    new ProductId(Guid.Parse(item.ProductId)),
                    item.Quantity,
                    new Money(item.UnitPrice, "USD"));
            }
            
            return Result.Ok(order);
        }
        catch (Exception ex)
        {
            return Result.Error<Order>($"Failed to create order: {ex.Message}");
        }
    }
}

// Result type for functional error handling
public record Result<T>(T? Value, bool IsSuccess, string Error)
{
    public static Result<T> Ok(T value) => new(value, true, string.Empty);
    public static Result<T> Error(string error) => new(default, false, error);
    
    public Result<U> Bind<U>(Func<T, Result<U>> func) =>
        IsSuccess ? func(Value!) : Error<U>(Error);
}

public static class Result
{
    public static Result<T> Ok<T>(T value) => Result<T>.Ok(value);
    public static Result<T> Error<T>(string error) => Result<T>.Error(error);
}

// Advanced pattern matching
public static class OrderStatusTransition
{
    public static bool IsValidTransition(OrderStatus from, OrderStatus to) =>
        (from.Value, to.Value) switch
        {
            ("pending", "processing") => true,
            ("pending", "cancelled") => true,
            ("processing", "completed") => true,
            ("processing", "cancelled") => true,
            ("completed", "cancelled") => false, // Cannot cancel completed
            ("cancelled", _) => false,          // Cannot transition from cancelled
            _ => false
        };
    
    public static OrderStatus GetNextStatus(OrderStatus current, string action) =>
        (current.Value, action) switch
        {
            ("pending", "start_processing") => OrderStatus.Processing,
            ("pending", "cancel") => OrderStatus.Cancelled,
            ("processing", "complete") => OrderStatus.Completed,
            ("processing", "cancel") => OrderStatus.Cancelled,
            _ => throw new InvalidTransitionException($"Cannot {action} order in status {current.Value}")
        };
}

public class InvalidTransitionException : Exception
{
    public InvalidTransitionException(string message) : base(message) { }
}
```

## Testing Strategies

### Modern Testing with xUnit and Minimal APIs
```csharp
// Tests/OrderServiceTests.cs
public class OrderServiceTests
{
    private readonly Mock<IOrderRepository> _orderRepositoryMock = new();
    private readonly Mock<IProductRepository> _productRepositoryMock = new();
    private readonly Mock<IUnitOfWork> _unitOfWorkMock = new();
    private readonly Mock<IMapper> _mapperMock = new();
    private readonly Mock<ILogger<OrderService>> _loggerMock = new();
    
    private readonly OrderService _sut;

    public OrderServiceTests()
    {
        _sut = new OrderService(
            _orderRepositoryMock.Object,
            _productRepositoryMock.Object,
            _unitOfWorkMock.Object,
            _mapperMock.Object,
            _loggerMock.Object);
    }

    [Theory]
    [MemberData(nameof(ValidOrderRequests))]
    public async Task CreateOrder_WithValidRequest_ShouldCreateOrder(
        CreateOrderRequest request, Product[] products)
    {
        // Arrange
        foreach (var product in products)
        {
            _productRepositoryMock
                .Setup(x => x.GetByIdAsync(new ProductId(product.Id), It.IsAny<CancellationToken>()))
                .ReturnsAsync(product);
        }

        var order = new Order(new CustomerId(request.CustomerId), Money.Zero("USD"));
        _mapperMock.Setup(x => x.Map<OrderDto>(order)).Returns(new OrderDto { Id = Guid.NewGuid() });

        // Act
        var result = await _sut.CreateOrderAsync(request);

        // Assert
        result.Should().NotBeNull();
        _orderRepositoryMock.Verify(x => x.AddAsync(It.IsAny<Order>(), It.IsAny<CancellationToken>()), Times.Once);
        _unitOfWorkMock.Verify(x => x.SaveChangesAsync(It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task CreateOrder_WithNonExistentProduct_ShouldThrowNotFoundException()
    {
        // Arrange
        var request = new CreateOrderRequest
        {
            CustomerId = Guid.NewGuid().ToString(),
            Items = [new OrderItemRequest { ProductId = Guid.NewGuid().ToString(), Quantity = 1, UnitPrice = 10.0 }]
        };

        _productRepositoryMock
            .Setup(x => x.GetByIdAsync(It.IsAny<ProductId>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((Product?)null);

        // Act & Assert
        await _sut.Invoking(x => x.CreateOrderAsync(request))
            .Should().ThrowAsync<NotFoundException>()
            .WithMessage("Product * not found");
    }

    public static IEnumerable<object[]> ValidOrderRequests()
    {
        var customerId = Guid.NewGuid().ToString();
        
        yield return new object[]
        {
            new CreateOrderRequest
            {
                CustomerId = customerId,
                Items =
                [
                    new OrderItemRequest { ProductId = Guid.NewGuid().ToString(), Quantity = 2, UnitPrice = 10.0 }
                ]
            },
            new[]
            {
                new Product { Id = Guid.NewGuid(), Price = new Money(10.0, "USD"), IsInStock = true, AvailableQuantity = 10 }
            }
        };
    }
}

// Integration tests with WebApplicationFactory
public class OrderApiTests : IClassFixture<TestApplicationFactory>
{
    private readonly HttpClient _client;
    private readonly TestApplicationFactory _factory;

    public OrderApiTests(TestApplicationFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task CreateOrder_ValidRequest_Returns201()
    {
        // Arrange
        var request = new
        {
            CustomerId = Guid.NewGuid().ToString(),
            Items = new[]
            {
                new { ProductId = Guid.NewGuid().ToString(), Quantity = 2, UnitPrice = 10.0 }
            }
        };

        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        // Act
        var response = await _client.PostAsync("/api/orders", content);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        
        var responseContent = await response.Content.ReadAsStringAsync();
        var createdOrder = JsonSerializer.Deserialize<OrderDto>(responseContent, new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        });
        
        createdOrder.Should().NotBeNull();
        createdOrder!.Id.Should().NotBeEmpty();
        createdOrder.Status.Should().Be("pending");
    }

    [Fact]
    public async Task GetOrder_WithValidId_Returns200()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        
        using var scope = _factory.Services.CreateScope();
        var dbContext = scope.ServiceProvider.GetRequiredService<OrderDbContext>();
        
        var order = new Order(new CustomerId(Guid.NewGuid()), Money.Zero("USD"));
        order.GetType().GetProperty("Id")?.SetValue(order, new OrderId(orderId));
        
        await dbContext.Orders.AddAsync(order);
        await dbContext.SaveChangesAsync();

        // Act
        var response = await _client.GetAsync($"/api/orders/{orderId}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        
        var responseContent = await response.Content.ReadAsStringAsync();
        var orderDto = JsonSerializer.Deserialize<OrderDto>(responseContent, new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        });
        
        orderDto.Should().NotBeNull();
        orderDto!.Id.Should().Be(orderId);
    }
}
```

## Common Use Cases

### Background Services and Hosted Services
```csharp
// Background/OrderProcessingService.cs
public class OrderProcessingService : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<OrderProcessingService> _logger;
    private readonly TimeSpan _processingInterval = TimeSpan.FromSeconds(30);

    public OrderProcessingService(
        IServiceProvider serviceProvider,
        ILogger<OrderProcessingService> logger)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ProcessPendingOrdersAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error occurred while processing pending orders");
            }

            await Task.Delay(_processingInterval, stoppingToken);
        }
    }

    private async Task ProcessPendingOrdersAsync(CancellationToken cancellationToken)
    {
        using var scope = _serviceProvider.CreateScope();
        var orderRepository = scope.ServiceProvider.GetRequiredService<IOrderRepository>();
        var paymentService = scope.ServiceProvider.GetRequiredService<IPaymentService>();
        var inventoryService = scope.ServiceProvider.GetRequiredService<IInventoryService>();

        var pendingOrders = await orderRepository.GetOrdersByStatusAsync(
            OrderStatus.Pending, 
            cancellationToken: cancellationToken);

        foreach (var order in pendingOrders)
        {
            try
            {
                await ProcessSingleOrderAsync(order, paymentService, inventoryService);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to process order {OrderId}", order.Id);
            }
        }
    }

    private async Task ProcessSingleOrderAsync(
        Order order,
        IPaymentService paymentService,
        IInventoryService inventoryService)
    {
        // Reserve inventory
        await inventoryService.ReserveProductsAsync(order.Items, CancellationToken.None);
        
        try
        {
            // Process payment
            var paymentResult = await paymentService.ProcessPaymentAsync(
                order.Id, order.TotalAmount, CancellationToken.None);
            
            if (paymentResult.IsSuccess)
            {
                order.Complete();
                _logger.LogInformation("Order {OrderId} completed successfully", order.Id);
            }
            else
            {
                await inventoryService.ReleaseProductsAsync(order.Items, CancellationToken.None);
                order.Cancel($"Payment failed: {paymentResult.ErrorMessage}");
                _logger.LogWarning("Order {OrderId} failed: {Error}", order.Id, paymentResult.ErrorMessage);
            }
        }
        catch
        {
            await inventoryService.ReleaseProductsAsync(order.Items, CancellationToken.None);
            throw;
        }
    }
}
```

This C# skill provides comprehensive expertise in modern C# 12 development, .NET 8 platform features, and enterprise-grade application architecture patterns.