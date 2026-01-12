---
name: dotnet-core-expert
description: .NET 8 cross-platform specialist with expertise in MAUI, EF Core, and modern C# development
---

# .NET Core Expert

## Core Capabilities

### .NET 8 Platform Features
- **Cross-Platform Development**: Windows, Linux, macOS deployment and development
- **Performance Improvements**: Native AOT, ahead-of-time compilation, reduced memory footprint
- **Language Features**: C# 12 support with primary constructors, collection expressions, lambda improvements
- **Container Support**: Optimized Docker images, multi-stage builds, small container footprints
- **Blazor Integration**: WebAssembly and server-side Blazor for full-stack C# development

### MAUI Development
- **Cross-Platform UI**: Single codebase targeting Android, iOS, Windows, macOS
- **Native Controls**: Platform-specific UI elements with unified API surface
- **Performance**: Native app performance with .NET runtime
- **MVVM Pattern**: Built-in data binding, command patterns, view models
- **Device Integration**: Camera, GPS, sensors, native API access

### Entity Framework Core
- **Database Providers**: SQL Server, PostgreSQL, MySQL, SQLite, Cosmos DB
- **Code-First Design**: Migrations, model configuration, relationship mapping
- **Performance Optimization**: Query optimization, caching, batch operations
- **Advanced Features**: Shadow properties, owned types, value conversions

## Architecture Patterns

### ASP.NET Core Web API
```csharp
// Program.cs with minimal APIs
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));
builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddAutoMapper(AppDomain.CurrentDomain.GetAssemblies());

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => {
        // JWT configuration
    });

var app = builder.Build();

// Middleware pipeline
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

// Minimal API endpoints
app.MapPost("/api/orders", async (CreateOrderRequest request, IOrderService service) =>
{
    var order = await service.CreateOrderAsync(request);
    return Results.Created($"/api/orders/{order.Id}", order);
})
.RequireAuthorization();

app.Run();
```

### Service Layer Implementation
```csharp
public interface IOrderService
{
    Task<OrderDto> CreateOrderAsync(CreateOrderRequest request);
    Task<OrderDto> GetOrderAsync(Guid id);
    Task<PagedResult<OrderDto>> GetOrdersAsync(OrderFilter filter, PaginationOptions pagination);
}

public class OrderService : IOrderService
{
    private readonly ApplicationDbContext _context;
    private readonly IMapper _mapper;
    private readonly ILogger<OrderService> _logger;

    public OrderService(
        ApplicationDbContext context,
        IMapper mapper,
        ILogger<OrderService> logger)
    {
        _context = context;
        _mapper = mapper;
        _logger = logger;
    }

    public async Task<OrderDto> CreateOrderAsync(CreateOrderRequest request)
    {
        var order = _mapper.Map<Order>(request);
        order.OrderNumber = await GenerateOrderNumberAsync();
        order.Status = OrderStatus.Pending;
        order.CreatedAt = DateTime.UtcNow;

        using var transaction = await _context.Database.BeginTransactionAsync();
        try
        {
            await _context.Orders.AddAsync(order);
            await _context.SaveChangesAsync();
            
            // Process payment
            await ProcessPaymentAsync(order);
            
            await transaction.CommitAsync();
            
            _logger.LogInformation("Order {OrderId} created successfully", order.Id);
            return _mapper.Map<OrderDto>(order);
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }

    private async Task<string> GenerateOrderNumberAsync()
    {
        var lastOrder = await _context.Orders
            .OrderByDescending(o => o.CreatedAt)
            .FirstOrDefaultAsync();
            
        var sequence = lastOrder?.OrderNumber[^4..] ?? "0000";
        var nextSequence = (int.Parse(sequence) + 1).ToString("D4");
        return $"ORD{DateTime.UtcNow:yyMMdd}{nextSequence}";
    }
}
```

### Data Access Layer with EF Core
```csharp
public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<Order> Orders { get; set; }
    public DbSet<OrderItem> OrderItems { get; set; }
    public DbSet<Customer> Customers { get; set; }
    public DbSet<Product> Products { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(ApplicationDbContext).Assembly);
        
        // Global query filters
        modelBuilder.Entity<Order>()
            .HasQueryFilter(o => !o.IsDeleted);
            
        modelBuilder.Entity<OrderItem>()
            .HasQueryFilter(oi => !oi.Order.IsDeleted);
    }

    public override async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        UpdateTimestamps();
        return await base.SaveChangesAsync(cancellationToken);
    }

    private void UpdateTimestamps()
    {
        var entries = ChangeTracker.Entries<IBaseEntity>();
        
        foreach (var entry in entries)
        {
            if (entry.State == EntityState.Added)
                entry.Entity.CreatedAt = DateTime.UtcNow;
            else if (entry.State == EntityState.Modified)
                entry.Entity.UpdatedAt = DateTime.UtcNow;
        }
    }
}

// Entity configuration
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.HasKey(o => o.Id);
        builder.Property(o => o.OrderNumber)
            .IsRequired()
            .HasMaxLength(20)
            .IsUnicode(false);
            
        builder.Property(o => o.TotalAmount)
            .HasPrecision(18, 2);
            
        builder.HasOne(o => o.Customer)
            .WithMany(c => c.Orders)
            .HasForeignKey(o => o.CustomerId)
            .OnDelete(DeleteBehavior.Restrict);
            
        builder.HasMany(o => o.Items)
            .WithOne(oi => oi.Order)
            .HasForeignKey(oi => oi.OrderId)
            .OnDelete(DeleteBehavior.Cascade);
            
        builder.HasIndex(o => o.OrderNumber)
            .IsUnique();
    }
}
```

## Development Best Practices

### Configuration Management
```csharp
// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=orders;Username=postgres;Password=password"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "JwtSettings": {
    "SecretKey": "your-256-bit-secret-key",
    "Issuer": "OrderApi",
    "Audience": "OrderApi",
    "ExpirationInMinutes": 60
  },
  "Redis": {
    "ConnectionString": "localhost:6379"
  }
}

// Configuration models
public class JwtSettings
{
    public string SecretKey { get; set; }
    public string Issuer { get; set; }
    public string Audience { get; set; }
    public int ExpirationInMinutes { get; set; }
}

// DI registration
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddApplicationServices(
        this IServiceCollection services, 
        IConfiguration configuration)
    {
        services.Configure<JwtSettings>(configuration.GetSection("JwtSettings"));
        
        services.AddScoped<IOrderService, OrderService>();
        services.AddScoped<IProductService, ProductService>();
        services.AddScoped<IAuthService, AuthService>();
        
        services.AddAutoMapper(typeof(MappingProfile));
        services.AddMediatR(typeof(OrderCreateCommand).Assembly);
        
        services.AddStackExchangeRedisCache(options =>
        {
            options.Configuration = configuration.GetConnectionString("Redis");
        });
        
        return services;
    }
}
```

### Exception Handling and Validation
```csharp
// Custom exceptions
public class NotFoundException : Exception
{
    public NotFoundException(string message) : base(message) { }
    public NotFoundException(string message, Exception innerException) : base(message, innerException) { }
}

public class BusinessRuleException : Exception
{
    public BusinessRuleException(string message) : base(message) { }
}

// Global exception filter
public class GlobalExceptionFilter : IExceptionFilter
{
    private readonly ILogger<GlobalExceptionFilter> _logger;

    public GlobalExceptionFilter(ILogger<GlobalExceptionFilter> logger)
    {
        _logger = logger;
    }

    public void OnException(ExceptionContext context)
    {
        var response = context.Exception switch
        {
            NotFoundException ex => new ErrorResponse("NOT_FOUND", ex.Message),
            BusinessRuleException ex => new ErrorResponse("BUSINESS_RULE_VIOLATION", ex.Message),
            ValidationException ex => new ErrorResponse("VALIDATION_ERROR", ex.Message),
            _ => new ErrorResponse("INTERNAL_ERROR", "An unexpected error occurred")
        };

        _logger.LogError(context.Exception, "Error occurred: {Message}", context.Exception.Message);
        
        context.Result = new ObjectResult(response)
        {
            StatusCode = GetStatusCode(context.Exception)
        };
        context.ExceptionHandled = true;
    }

    private static int GetStatusCode(Exception exception) =>
        exception switch
        {
            NotFoundException => StatusCodes.Status404NotFound,
            BusinessRuleException => StatusCodes.Status400BadRequest,
            ValidationException => StatusCodes.Status400BadRequest,
            _ => StatusCodes.Status500InternalServerError
        };
}
```

## Testing Strategies

### Unit Testing with xUnit
```csharp
public class OrderServiceTests
{
    private readonly Mock<ApplicationDbContext> _mockContext;
    private readonly Mock<IMapper> _mockMapper;
    private readonly OrderService _orderService;

    public OrderServiceTests()
    {
        _mockContext = new Mock<ApplicationDbContext>();
        _mockMapper = new Mock<IMapper>();
        _orderService = new OrderService(_mockContext.Object, _mockMapper.Object, Mock.Of<ILogger<OrderService>>());
    }

    [Fact]
    public async Task CreateOrder_ValidRequest_ShouldCreateOrder()
    {
        // Arrange
        var request = new CreateOrderRequest { CustomerId = Guid.NewGuid(), TotalAmount = 100.00m };
        var order = new Order { Id = Guid.NewGuid(), OrderNumber = "ORD202312010001" };
        var orderDto = new OrderDto { Id = order.Id, OrderNumber = order.OrderNumber };

        _mockMapper.Setup(m => m.Map<Order>(request)).Returns(order);
        _mockContext.Setup(c => c.SaveChangesAsync(It.IsAny<CancellationToken>())).ReturnsAsync(1);
        _mockMapper.Setup(m => m.Map<OrderDto>(order)).Returns(orderDto);

        // Act
        var result = await _orderService.CreateOrderAsync(request);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(order.Id, result.Id);
        _mockContext.Verify(c => c.Orders.AddAsync(order, It.IsAny<CancellationToken>()), Times.Once);
        _mockContext.Verify(c => c.SaveChangesAsync(It.IsAny<CancellationToken>()), Times.Once);
    }
}
```

### Integration Testing
```csharp
public class OrdersControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;

    public OrdersControllerTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                var descriptor = services.SingleOrDefault(
                    d => d.ServiceType == typeof(DbContextOptions<ApplicationDbContext>));
                    
                if (descriptor != null)
                {
                    services.Remove(descriptor);
                }

                services.AddDbContext<ApplicationDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb"));
            });
        });

        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task CreateOrder_ValidRequest_ShouldReturnCreated()
    {
        // Arrange
        var request = new CreateOrderRequest 
        { 
            CustomerId = Guid.NewGuid(), 
            TotalAmount = 100.00m,
            Items = new List<CreateOrderItemRequest>
            {
                new() { ProductId = Guid.NewGuid(), Quantity = 2, UnitPrice = 50.00m }
            }
        };

        var content = new StringContent(
            JsonSerializer.Serialize(request),
            Encoding.UTF8,
            "application/json");

        // Act
        var response = await _client.PostAsync("/api/orders", content);

        // Assert
        response.EnsureSuccessStatusCode();
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        
        var responseContent = await response.Content.ReadAsStringAsync();
        var createdOrder = JsonSerializer.Deserialize<OrderDto>(responseContent, new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        });
        
        Assert.NotNull(createdOrder);
        Assert.NotNull(createdOrder.OrderNumber);
    }
}
```

## MAUI Development

### Cross-Platform ViewModel
```csharp
public partial class OrderListViewModel : ObservableObject
{
    private readonly IOrderService _orderService;

    [ObservableProperty]
    private ObservableCollection<OrderDto> orders = new();

    [ObservableProperty]
    private bool isLoading;

    [ObservableProperty]
    private string? errorMessage;

    public OrderListViewModel(IOrderService orderService)
    {
        _orderService = orderService;
        LoadOrdersCommand = new AsyncRelayCommand(LoadOrdersAsync);
        RefreshCommand = new AsyncRelayCommand(RefreshOrdersAsync);
    }

    public ICommand LoadOrdersCommand { get; }
    public ICommand RefreshCommand { get; }

    private async Task LoadOrdersAsync()
    {
        if (IsLoading) return;

        try
        {
            IsLoading = true;
            ErrorMessage = null;

            var result = await _orderService.GetOrdersAsync(new OrderFilter(), new PaginationOptions());
            
            Orders.Clear();
            foreach (var order in result.Items)
            {
                Orders.Add(order);
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = $"Failed to load orders: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }

    private async Task RefreshOrdersAsync()
    {
        await LoadOrdersAsync();
    }
}
```

### MAUI XAML UI
```xml
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             xmlns:viewmodels="clr-namespace:OrderApp.ViewModels"
             x:DataType="viewmodels:OrderListViewModel"
             x:Class="OrderApp.Views.OrderListPage">

    <Grid RowDefinitions="Auto,*,Auto">
        <!-- Header -->
        <Label Grid.Row="0" 
               Text="Orders" 
               FontSize="Large" 
               FontAttributes="Bold"
               Margin="16"/>

        <!-- Loading indicator -->
        <ActivityIndicator Grid.Row="1" 
                          IsRunning="{Binding IsLoading}"
                          IsVisible="{Binding IsLoading}"
                          VerticalOptions="Center"
                          HorizontalOptions="Center"/>

        <!-- Error message -->
        <Label Grid.Row="1"
               Text="{Binding ErrorMessage}"
               IsVisible="{Binding ErrorMessage, Converter={StaticResource NotNullConverter}}"
               TextColor="Red"
               HorizontalTextAlignment="Center"
               VerticalOptions="Center"/>

        <!-- Orders list -->
        <CollectionView Grid.Row="1"
                        ItemsSource="{Binding Orders}"
                        IsVisible="{Binding IsLoading, Converter={StaticResource InverseBoolConverter}}">
            <CollectionView.ItemTemplate>
                <DataTemplate>
                    <Grid Padding="16" RowDefinitions="Auto,Auto,Auto">
                        <Label Grid.Row="0" 
                               Text="{Binding OrderNumber}" 
                               FontAttributes="Bold"/>
                        <Label Grid.Row="1" 
                               Text="{Binding TotalAmount, StringFormat='${0:F2}'}"/>
                        <Label Grid.Row="2" 
                               Text="{Binding Status}"
                               TextColor="{Binding Status, Converter={StaticResource StatusColorConverter}}"/>
                    </Grid>
                </DataTemplate>
            </CollectionView.ItemTemplate>
        </CollectionView>

        <!-- Refresh button -->
        <Button Grid.Row="2"
                Text="Refresh"
                Command="{Binding RefreshCommand}"
                Margin="16"
                IsEnabled="{Binding IsLoading, Converter={StaticResource InverseBoolConverter}}"/>
    </Grid>
</ContentPage>
```

## Performance Optimization

### Caching with Redis
```csharp
public class CachedOrderService : IOrderService
{
    private readonly IOrderService _innerService;
    private readonly IDistributedCache _cache;
    private readonly ILogger<CachedOrderService> _logger;

    public CachedOrderService(
        IOrderService innerService,
        IDistributedCache cache,
        ILogger<CachedOrderService> logger)
    {
        _innerService = innerService;
        _cache = cache;
        _logger = logger;
    }

    public async Task<OrderDto> GetOrderAsync(Guid id)
    {
        var cacheKey = $"order:{id}";
        var cachedData = await _cache.GetStringAsync(cacheKey);

        if (cachedData != null)
        {
            _logger.LogDebug("Order {OrderId} found in cache", id);
            return JsonSerializer.Deserialize<OrderDto>(cachedData);
        }

        var order = await _innerService.GetOrderAsync(id);
        
        if (order != null)
        {
            var options = new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(30)
            };
            
            await _cache.SetStringAsync(
                cacheKey, 
                JsonSerializer.Serialize(order), 
                options);
        }

        return order;
    }
}
```

### Background Services
```csharp
public class OrderProcessingService : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<OrderProcessingService> _logger;

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
            using var scope = _serviceProvider.CreateScope();
            var orderService = scope.ServiceProvider.GetRequiredService<IOrderService>();

            try
            {
                await ProcessPendingOrdersAsync(orderService, stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing pending orders");
            }

            await Task.Delay(TimeSpan.FromMinutes(5), stoppingToken);
        }
    }

    private async Task ProcessPendingOrdersAsync(IOrderService orderService, CancellationToken cancellationToken)
    {
        var pendingOrders = await orderService.GetPendingOrdersAsync();

        foreach (var order in pendingOrders)
        {
            await ProcessOrderAsync(order, cancellationToken);
        }
    }

    private async Task ProcessOrderAsync(OrderDto order, CancellationToken cancellationToken)
    {
        // Process payment, update inventory, send notifications
        _logger.LogInformation("Processing order {OrderId}", order.Id);
        
        // Implementation details...
    }
}
```

## Security Implementation

### JWT Authentication
```csharp
public class JwtTokenGenerator : IJwtTokenGenerator
{
    private readonly JwtSettings _settings;
    private readonly UserManager<ApplicationUser> _userManager;

    public JwtTokenGenerator(
        IOptions<JwtSettings> settings,
        UserManager<ApplicationUser> userManager)
    {
        _settings = settings.Value;
        _userManager = userManager;
    }

    public async Task<string> GenerateTokenAsync(ApplicationUser user)
    {
        var claims = new List<Claim>
        {
            new(ClaimTypes.NameIdentifier, user.Id),
            new(ClaimTypes.Email, user.Email),
            new(ClaimTypes.Name, user.UserName),
            new(JwtRegisteredClaimNames.Sub, user.Id),
            new(JwtRegisteredClaimNames.Email, user.Email),
            new(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString())
        };

        var userRoles = await _userManager.GetRolesAsync(user);
        claims.AddRange(userRoles.Select(role => new Claim(ClaimTypes.Role, role)));

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_settings.SecretKey));
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: _settings.Issuer,
            audience: _settings.Audience,
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(_settings.ExpirationInMinutes),
            signingCredentials: credentials);

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
```

## Common Use Cases

### MediatR Command Pattern
```csharp
// Command
public record CreateOrderCommand(CreateOrderRequest Request) : IRequest<OrderDto>;

// Handler
public class CreateOrderCommandHandler : IRequestHandler<CreateOrderCommand, OrderDto>
{
    private readonly IOrderService _orderService;

    public CreateOrderCommandHandler(IOrderService orderService)
    {
        _orderService = orderService;
    }

    public async Task<OrderDto> Handle(CreateOrderCommand request, CancellationToken cancellationToken)
    {
        return await _orderService.CreateOrderAsync(request.Request);
    }
}

// Controller
[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{
    private readonly IMediator _mediator;

    public OrdersController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost]
    public async Task<ActionResult<OrderDto>> CreateOrder(CreateOrderRequest request)
    {
        var command = new CreateOrderCommand(request);
        var result = await _mediator.Send(command);
        return CreatedAtAction(nameof(GetOrder), new { id = result.Id }, result);
    }
}
```

This .NET Core skill provides comprehensive expertise for building cross-platform applications with modern .NET 8 technologies, including web APIs, mobile apps with MAUI, and enterprise-grade data access with EF Core.