---
name: php-pro
description: PHP 8.2+ specialist with expertise in modern patterns, Composer ecosystem, and enterprise PHP development
---

# PHP Professional

## Core Capabilities

### PHP 8.2+ Modern Features
- **Readonly Classes**: Immutable class properties
- **Union Types**: Multiple type declarations
- **Enum Classes**: Strongly typed enumerations with methods
- **Attributes**: PHP 8+ metadata annotations
- **Constructor Property Promotion**: Simplified constructor definitions
- **Match Expression**: Powerful pattern matching
- **Named Arguments**: Self-documenting function calls
- **String Interpolation Improvements**: Enhanced embedding syntax
- **nullsafe operator**: Safe navigation through null values

### Modern PHP Patterns
- **SOLID Principles**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion
- **Repository Pattern**: Data access abstraction layer
- **Domain-Driven Design**: Bounded contexts, entities, value objects
- **Event-Driven Architecture**: Event sourcing, CQRS patterns
- **Dependency Injection**: Inversion of control container usage
- **PSR Standards**: Framework-agnostic coding standards

### Composer & Ecosystem
- **Package Management**: Autoloading, version constraints, semantic versioning
- **Private Packagist**: Enterprise package repositories
- **Scripts & Hooks**: Custom build and deployment scripts
- **Composer Merge**: Combining multiple composer.json files

## Architecture Patterns

### Modern Laravel Application Structure
```php
// app/Domain/Order/Enums/OrderStatus.php
<?php

declare(strict_types=1);

namespace App\Domain\Order\Enums;

enum OrderStatus: string
{
    case PENDING = 'pending';
    case PROCESSING = 'processing';
    case COMPLETED = 'completed';
    case CANCELLED = 'cancelled';

    public function canTransitionTo(self $status): bool
    {
        return match ([$this, $status]) {
            [self::PENDING, self::PROCESSING] => true,
            [self::PENDING, self::CANCELLED] => true,
            [self::PROCESSING, self::COMPLETED] => true,
            [self::PROCESSING, self::CANCELLED] => true,
            default => false,
        };
    }

    public function getLabel(): string
    {
        return match ($this) {
            self::PENDING => 'Pending',
            self::PROCESSING => 'Processing',
            self::COMPLETED => 'Completed',
            self::CANCELLED => 'Cancelled',
        };
    }

    public function isFinal(): bool
    {
        return match ($this) {
            self::COMPLETED, self::CANCELLED => true,
            default => false,
        };
    }
}

// app/Domain/Order/ValueObjects/Money.php
<?php

declare(strict_types=1);

namespace App\Domain\Order\ValueObjects;

readonly final class Money
{
    public function __construct(
        public int $amount,
        public string $currency = 'USD'
    ) {
        $this->validate();
    }

    private function validate(): void
    {
        if ($this->amount < 0) {
            throw new InvalidArgumentException('Amount cannot be negative');
        }

        if (!in_array($this->currency, ['USD', 'EUR', 'GBP'])) {
            throw new InvalidArgumentException('Invalid currency');
        }
    }

    public function getFormattedAmount(): string
    {
        return number_format($this->amount / 100, 2) . ' ' . $this->currency;
    }

    public function add(Money $other): Money
    {
        if ($this->currency !== $other->currency) {
            throw new InvalidArgumentException('Cannot add money with different currencies');
        }

        return new self($this->amount + $other->amount, $this->currency);
    }

    public function multiply(float $multiplier): Money
    {
        return new self((int)round($this->amount * $multiplier), $this->currency);
    }

    public function greaterThan(Money $other): bool
    {
        if ($this->currency !== $other->currency) {
            throw new InvalidArgumentException('Cannot compare money with different currencies');
        }

        return $this->amount > $other->amount;
    }
}

// app/Domain/Order/Entities/Order.php
<?php

declare(strict_types=1);

namespace App\Domain\Order\Entities;

use App\Domain\Order\Enums\OrderStatus;
use App\Domain\Order\ValueObjects\Money;
use Illuminate\Support\Collection;

final readonly class Order
{
    public function __construct(
        public string $id,
        public string $customerId,
        public Collection $items,
        public OrderStatus $status,
        public Money $totalAmount,
        public \DateTimeImmutable $createdAt,
        public ?\DateTimeImmutable $updatedAt = null
    ) {
        $this->validate();
    }

    private function validate(): void
    {
        if (empty($this->id)) {
            throw new InvalidArgumentException('Order ID cannot be empty');
        }

        if (empty($this->customerId)) {
            throw new InvalidArgumentException('Customer ID cannot be empty');
        }

        if ($this->items->isEmpty()) {
            throw new InvalidArgumentException('Order must contain at least one item');
        }
    }

    public function withStatus(OrderStatus $status): self
    {
        if (!$this->status->canTransitionTo($status)) {
            throw new DomainException(
                "Cannot transition from {$this->status->value} to {$status->value}"
            );
        }

        return new self(
            $this->id,
            $this->customerId,
            $this->items,
            $status,
            $this->totalAmount,
            $this->createdAt,
            new \DateTimeImmutable()
        );
    }

    public static function create(string $customerId, Collection $items): self
    {
        $totalAmount = $items->reduce(
            static fn (Money $carry, OrderItem $item) => $carry->add($item->totalPrice),
            new Money(0)
        );

        return new self(
            id: (string)Str::uuid(),
            customerId: $customerId,
            items: $items,
            status: OrderStatus::PENDING,
            totalAmount: $totalAmount,
            createdAt: new \DateTimeImmutable()
        );
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'customer_id' => $this->customerId,
            'items' => $this->items->map(fn (OrderItem $item) => $item->toArray())->all(),
            'status' => $this->status->value,
            'total_amount' => $this->totalAmount->getFormattedAmount(),
            'created_at' => $this->createdAt->format(\DateTimeInterface::ATOM),
            'updated_at' => $this->updatedAt?->format(\DateTimeInterface::ATOM),
        ];
    }
}

// app/Domain/Order/Entities/OrderItem.php
<?php

declare(strict_types=1);

namespace App\Domain\Order\Entities;

use App\Domain\Order\ValueObjects\Money;

final readonly class OrderItem
{
    public function __construct(
        public string $productId,
        public int $quantity,
        public Money $unitPrice
    ) {
        $this->validate();
    }

    private function validate(): void
    {
        if ($this->quantity <= 0) {
            throw new InvalidArgumentException('Quantity must be positive');
        }
    }

    public function get totalPrice(): Money
    {
        return $this->unitPrice->multiply($this->quantity);
    }

    public function toArray(): array
    {
        return [
            'product_id' => $this->productId,
            'quantity' => $this->quantity,
            'unit_price' => $this->unitPrice->getFormattedAmount(),
            'total_price' => $this->totalPrice->getFormattedAmount(),
        ];
    }
}
```

### Service Layer with Modern PHP
```php
// app/Domain/Order/Services/OrderService.php
<?php

declare(strict_types=1);

namespace App\Domain\Order\Services;

use App\Domain\Order\Entities\Order;
use App\Domain\Order\Repositories\OrderRepositoryInterface;
use App\Domain\Order\Repositories\ProductRepositoryInterface;
use App\Domain\Order\ValueObjects\Money;
use Illuminate\Support\Collection;
use Illuminate\Support\Str;
use Psr\Log\LoggerInterface;
use Throwable;

final readonly class OrderService
{
    public function __construct(
        private OrderRepositoryInterface $orderRepository,
        private ProductRepositoryInterface $productRepository,
        private LoggerInterface $logger
    ) {}

    /**
     * @param array<string, mixed> $data
     */
    public function createOrder(array $data): Order
    {
        $items = $this->validateAndCreateItems($data['items'] ?? []);

        $order = Order::create($data['customer_id'], $items);

        return $this->orderRepository->save($order);
    }

    public function findById(string $id): ?Order
    {
        return $this->orderRepository->findById($id);
    }

    public function findByCustomer(string $customerId, int $page = 1, int $limit = 20): Collection
    {
        return $this->orderRepository->findByCustomer($customerId, $page, $limit);
    }

    public function updateStatus(string $orderId, OrderStatus $status): Order
    {
        $order = $this->orderRepository->findById($orderId);

        if ($order === null) {
            throw new OrderNotFoundException("Order {$orderId} not found");
        }

        $updatedOrder = $order->withStatus($status);

        return $this->orderRepository->save($updatedOrder);
    }

    /**
     * @param array<array<string, mixed>> $itemsData
     */
    private function validateAndCreateItems(array $itemsData): Collection
    {
        if (empty($itemsData)) {
            throw new InvalidArgumentException('Order must contain at least one item');
        }

        $items = collect();

        foreach ($itemsData as $itemData) {
            $product = $this->productRepository->findById($itemData['product_id']);

            if ($product === null) {
                throw new ProductNotFoundException(
                    "Product {$itemData['product_id']} not found"
                );
            }

            if (!$product->isInStock()) {
                throw new ProductOutOfStockException(
                    "Product {$product->id} is out of stock"
                );
            }

            $quantity = $itemData['quantity'] ?? 1;

            if ($quantity > $product->availableQuantity) {
                throw new InsufficientStockException(
                    "Insufficient stock for product {$product->id}"
                );
            }

            $items->push(new OrderItem(
                productId: $product->id,
                quantity: $quantity,
                unitPrice: $product->price
            ));
        }

        return $items;
    }
}

// app/Domain/Order/Repositories/EloquentOrderRepository.php
<?php

declare(strict_types=1);

namespace App\Domain\Order\Repositories;

use App\Domain\Order\Entities\Order;
use App\Domain\Order\Entities\OrderItem;
use App\Domain\Order\Enums\OrderStatus;
use App\Domain\Order\ValueObjects\Money;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

final class EloquentOrderRepository implements OrderRepositoryInterface
{
    public function save(Order $order): Order
    {
        return DB::transaction(function () use ($order) {
            $orderModel = \App\Models\Order::query()->updateOrCreate(
                ['id' => $order->id],
                [
                    'customer_id' => $order->customerId,
                    'status' => $order->status->value,
                    'total_amount' => $order->totalAmount->amount,
                    'currency' => $order->totalAmount->currency,
                    'created_at' => $order->createdAt->format('Y-m-d H:i:s'),
                    'updated_at' => $order->updatedAt?->format('Y-m-d H:i:s'),
                ]
            );

            // Update items
            $orderModel->items()->delete();

            foreach ($order->items as $item) {
                $orderModel->items()->create([
                    'product_id' => $item->productId,
                    'quantity' => $item->quantity,
                    'unit_price' => $item->unitPrice->amount,
                    'currency' => $item->unitPrice->currency,
                ]);
            }

            return $this->modelToEntity($orderModel->fresh());
        });
    }

    public function findById(string $id): ?Order
    {
        $orderModel = \App\Models\Order::with('items')->find($id);

        if ($orderModel === null) {
            return null;
        }

        return $this->modelToEntity($orderModel);
    }

    public function findByCustomer(string $customerId, int $page = 1, int $limit = 20): Collection
    {
        $orderModels = \App\Models\Order::with('items')
            ->where('customer_id', $customerId)
            ->orderBy('created_at', 'desc')
            ->offset(($page - 1) * $limit)
            ->limit($limit)
            ->get();

        return $orderModels->map(
            fn (\App\Models\Order $model) => $this->modelToEntity($model)
        );
    }

    public function countByCustomer(string $customerId): int
    {
        return \App\Models\Order::where('customer_id', $customerId)->count();
    }

    private function modelToEntity(\App\Models\Order $model): Order
    {
        return new Order(
            id: $model->id,
            customerId: $model->customer_id,
            items: $model->items->map(
                fn (\App\Models\OrderItem $itemModel) => new OrderItem(
                    productId: $itemModel->product_id,
                    quantity: $itemModel->quantity,
                    unitPrice: new Money($itemModel->unit_price, $itemModel->currency)
                )
            ),
            status: OrderStatus::from($model->status),
            totalAmount: new Money($model->total_amount, $model->currency),
            createdAt: new \DateTimeImmutable($model->created_at),
            updatedAt: $model->updated_at ? new \DateTimeImmutable($model->updated_at) : null
        );
    }
}
```

### Modern Controller with PHP 8.2+ Features
```php
// app/Http/Controllers/Api/V1/OrderController.php
<?php

declare(strict_types=1);

namespace App\Http\Controllers\Api\V1;

use App\Domain\Order\Entities\Order;
use App\Domain\Order\Enums\OrderStatus;
use App\Domain\Order\Repositories\OrderRepositoryInterface;
use App\Domain\Order\Services\OrderService;
use App\Http\Requests\Api\V1\CreateOrderRequest;
use App\Http\Resources\Api\V1\OrderResource;
use App\Http\Resources\Api\V1\OrderCollection;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use Illuminate\Routing\Controller;

final class OrderController extends Controller
{
    public function __construct(
        private readonly OrderService $orderService,
        private readonly OrderRepositoryInterface $orderRepository
    ) {}

    public function store(CreateOrderRequest $request): JsonResource
    {
        $order = $this->orderService->createOrder($request->validated());

        return new OrderResource($order);
    }

    public function show(string $id): JsonResource
    {
        $order = $this->orderService->findById($id);

        if ($order === null) {
            return new JsonResource([
                'error' => 'Order not found',
                'message' => "Order {$id} not found",
            ], 404);
        }

        return new OrderResource($order);
    }

    public function index(Request $request, string $customerId): JsonResource
    {
        $page = (int) $request->query('page', 1);
        $limit = min((int) $request->query('limit', 20), 100);

        $orders = $this->orderService->findByCustomer($customerId, $page, $limit);

        return new OrderCollection($orders);
    }

    public function updateStatus(string $id, Request $request): JsonResponse
    {
        $validated = $request->validate([
            'status' => ['required', 'string', 'in:pending,processing,completed,cancelled'],
        ]);

        try {
            $status = OrderStatus::from($validated['status']);
            $order = $this->orderService->updateStatus($id, $status);

            return response()->json([
                'data' => new OrderResource($order),
                'message' => 'Order status updated successfully',
            ]);
        } catch (OrderNotFoundException $e) {
            return response()->json([
                'error' => 'Order not found',
                'message' => $e->getMessage(),
            ], 404);
        } catch (DomainException $e) {
            return response()->json([
                'error' => 'Invalid transition',
                'message' => $e->getMessage(),
            ], 400);
        }
    }

    public function destroy(string $id): JsonResponse
    {
        // Soft delete implementation
        $order = $this->orderRepository->findById($id);

        if ($order === null) {
            return response()->json([
                'error' => 'Order not found',
                'message' => "Order {$id} not found",
            ], 404);
        }

        $cancelledOrder = $this->orderService->updateStatus($id, OrderStatus::CANCELLED);

        return response()->json([
            'message' => 'Order cancelled successfully',
            'data' => new OrderResource($cancelledOrder),
        ]);
    }
}

// app/Http/Requests/Api/V1/CreateOrderRequest.php
<?php

declare(strict_types=1);

namespace App\Http\Requests\Api\V1;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rules\ArrayRule;

final class CreateOrderRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true; // Implement authorization logic
    }

    #[\Override]
    public function rules(): array
    {
        return [
            'customer_id' => ['required', 'string', 'max:255'],
            'items' => ['required', 'array', 'min:1', 'max:50'],
            'items.*.product_id' => ['required', 'string', 'max:255'],
            'items.*.quantity' => ['required', 'integer', 'min:1', 'max:100'],
            'items.*.unit_price' => ['required', 'numeric', 'min:0.01'],
        ];
    }

    #[\Override]
    public function messages(): array
    {
        return [
            'items.required' => 'Order must contain at least one item',
            'items.min' => 'Order must contain at least one item',
            'items.max' => 'Order cannot contain more than 50 items',
            'items.*.quantity.max' => 'Maximum quantity per item is 100',
            'customer_id.required' => 'Customer ID is required',
        ];
    }

    #[\Override]
    protected function prepareForValidation(): void
    {
        $this->merge([
            'customer_id' => trim($this->input('customer_id')),
        ]);
    }
}
```

## Performance Optimization

### Redis Caching Implementation
```php
// app/Domain/Order/Services/CachedOrderService.php
<?php

declare(strict_types=1);

namespace App\Domain\Order\Services;

use App\Domain\Order\Entities\Order;
use App\Domain\Order\Repositories\OrderRepositoryInterface;
use Illuminate\Cache\CacheManager;
use Illuminate\Support\Collection;

final readonly class CachedOrderService implements OrderServiceInterface
{
    private const CACHE_TTL = 3600; // 1 hour
    private const CACHE_PREFIX = 'order:';

    public function __construct(
        private OrderServiceInterface $orderService,
        private CacheManager $cache,
    ) {}

    public function createOrder(array $data): Order
    {
        $order = $this->orderService->createOrder($data);

        // Cache the created order
        $this->cacheOrder($order);

        return $order;
    }

    public function findById(string $id): ?Order
    {
        $cacheKey = $this->getCacheKey($id);

        $cached = $this->cache->get($cacheKey);

        if ($cached !== null) {
            return $cached;
        }

        $order = $this->orderService->findById($id);

        if ($order !== null) {
            $this->cache->put($cacheKey, $order, self::CACHE_TTL);
        }

        return $order;
    }

    public function findByCustomer(string $customerId, int $page = 1, int $limit = 20): Collection
    {
        $cacheKey = "customer_orders:{$customerId}:{$page}:{$limit}";

        return $this->cache->remember(
            $cacheKey,
            self::CACHE_TTL,
            fn () => $this->orderService->findByCustomer($customerId, $page, $limit)
        );
    }

    public function updateStatus(string $orderId, OrderStatus $status): Order
    {
        $order = $this->orderService->updateStatus($orderId, $status);

        // Update cache
        $this->cacheOrder($order);

        // Clear customer orders cache
        $this->clearCustomerOrdersCache($order->customerId);

        return $order;
    }

    private function cacheOrder(Order $order): void
    {
        $cacheKey = $this->getCacheKey($order->id);
        $this->cache->put($cacheKey, $order, self::CACHE_TTL);
    }

    private function getCacheKey(string $orderId): string
    {
        return self::CACHE_PREFIX . $orderId;
    }

    private function clearCustomerOrdersCache(string $customerId): void
    {
        // Implementation depends on cache driver
        // For Redis, you could use wildcard deletion
        $this->cache->forget("customer_orders:{$customerId}");
    }
}
```

### Query Optimization
```php
// app/Domain/Order/Repositories/OptimizedOrderRepository.php
<?php

declare(strict_types=1);

namespace App\Domain\Order\Repositories;

use App\Domain\Order\Entities\Order;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

final class OptimizedOrderRepository implements OrderRepositoryInterface
{
    public function findByCustomerWithTotal(string $customerId, int $page = 1, int $limit = 20): array
    {
        $offset = ($page - 1) * $limit;

        $query = DB::query()
            ->select([
                'orders.*',
                DB::raw('COUNT(order_items.id) as item_count'),
                DB::raw('SUM(order_items.quantity * order_items.unit_price) as calculated_total'),
            ])
            ->from('orders')
            ->join('order_items', 'orders.id', '=', 'order_items.order_id')
            ->where('orders.customer_id', $customerId)
            ->where('orders.deleted_at', null)
            ->groupBy('orders.id')
            ->orderBy('orders.created_at', 'desc')
            ->offset($offset)
            ->limit($limit);

        return $query->get()->all();
    }

    public function getStatisticsByDateRange(string $customerId, \DateTimeInterface $startDate, \DateTimeInterface $endDate): array
    {
        return DB::query()
            ->select([
                'status',
                DB::raw('COUNT(*) as order_count'),
                DB::raw('SUM(total_amount) as total_value'),
                DB::raw('AVG(total_amount) as average_value'),
            ])
            ->from('orders')
            ->where('customer_id', $customerId)
            ->whereBetween('created_at', [$startDate->format('Y-m-d'), $endDate->format('Y-m-d')])
            ->groupBy('status')
            ->get()
            ->all();
    }

    public function getMostOrderedProducts(string $customerId, int $limit = 10): array
    {
        return DB::query()
            ->select([
                'products.id',
                'products.name',
                DB::raw('SUM(order_items.quantity) as total_quantity'),
                DB::raw('COUNT(order_items.id) as order_count'),
            ])
            ->from('orders')
            ->join('order_items', 'orders.id', '=', 'order_items.order_id')
            ->join('products', 'order_items.product_id', '=', 'products.id')
            ->where('orders.customer_id', $customerId)
            ->groupBy('products.id', 'products.name')
            ->orderBy('total_quantity', 'desc')
            ->limit($limit)
            ->get()
            ->all();
    }
}
```

## Testing Strategies

### Modern PHPUnit Testing
```php
// tests/Unit/Domain/Order/Services/OrderServiceTest.php
<?php

declare(strict_types=1);

namespace Tests\Unit\Domain\Order\Services;

use App\Domain\Order\Entities\Order;
use App\Domain\Order\Entities\OrderItem;
use App\Domain\Order\Enums\OrderStatus;
use App\Domain\Order\Exceptions\OrderNotFoundException;
use App\Domain\Order\Exceptions\ProductNotFoundException;
use App\Domain\Order\Repositories\OrderRepositoryInterface;
use App\Domain\Order\Repositories\ProductRepositoryInterface;
use App\Domain\Order\Services\OrderService;
use App\Domain\Order\ValueObjects\Money;
use PHPUnit\Framework\MockObject\MockObject;
use PHPUnit\Framework\TestCase;
use Psr\Log\LoggerInterface;
use Illuminate\Support\Collection;

final class OrderServiceTest extends TestCase
{
    private OrderRepositoryInterface&MockObject $orderRepository;
    private ProductRepositoryInterface&MockObject $productRepository;
    private LoggerInterface&MockObject $logger;
    private OrderService $service;

    protected function setUp(): void
    {
        $this->orderRepository = $this->createMock(OrderRepositoryInterface::class);
        $this->productRepository = $this->createMock(ProductRepositoryInterface::class);
        $this->logger = $this->createMock(LoggerInterface::class);

        $this->service = new OrderService(
            $this->orderRepository,
            $this->productRepository,
            $this->logger
        );
    }

    public function testCreateOrderSuccessfully(): void
    {
        // Arrange
        $productId = 'product-123';
        $customerId = 'customer-456';
        $orderData = [
            'customer_id' => $customerId,
            'items' => [
                ['product_id' => $productId, 'quantity' => 2],
            ],
        ];

        $product = $this->createProduct($productId, 5000); // $50.00
        $expectedItems = collect([new OrderItem($productId, 2, new Money(5000))]);
        $expectedOrder = new Order(
            id: 'order-789',
            customerId: $customerId,
            items: $expectedItems,
            status: OrderStatus::PENDING,
            totalAmount: new Money(10000), // $100.00
            createdAt: new \DateTimeImmutable()
        );

        $this->productRepository
            ->expects($this->once())
            ->method('findById')
            ->with($productId)
            ->willReturn($product);

        $this->orderRepository
            ->expects($this->once())
            ->method('save')
            ->willReturn($expectedOrder);

        // Act
        $result = $this->service->createOrder($orderData);

        // Assert
        $this->assertEquals($expectedOrder, $result);
    }

    public function testCreateOrderWithNonExistentProduct(): void
    {
        // Arrange
        $productId = 'non-existent';
        $orderData = [
            'customer_id' => 'customer-456',
            'items' => [
                ['product_id' => $productId, 'quantity' => 1],
            ],
        ];

        $this->productRepository
            ->expects($this->once())
            ->method('findById')
            ->with($productId)
            ->willReturn(null);

        // Expect exception
        $this->expectException(ProductNotFoundException::class);
        $this->expectExceptionMessage("Product {$productId} not found");

        // Act
        $this->service->createOrder($orderData);
    }

    public function testUpdateStatusSuccessfully(): void
    {
        // Arrange
        $orderId = 'order-123';
        $newStatus = OrderStatus::PROCESSING;

        $existingOrder = $this->createOrder($orderId, OrderStatus::PENDING);
        $updatedOrder = $existingOrder->withStatus($newStatus);

        $this->orderRepository
            ->expects($this->once())
            ->method('findById')
            ->with($orderId)
            ->willReturn($existingOrder);

        $this->orderRepository
            ->expects($this->once())
            ->method('save')
            ->with($updatedOrder)
            ->willReturn($updatedOrder);

        // Act
        $result = $this->service->updateStatus($orderId, $newStatus);

        // Assert
        $this->assertEquals($updatedOrder, $result);
        $this->assertEquals($newStatus, $result->status);
    }

    public function testUpdateStatusForNonExistentOrder(): void
    {
        // Arrange
        $orderId = 'non-existent';
        $newStatus = OrderStatus::PROCESSING;

        $this->orderRepository
            ->expects($this->once())
            ->method('findById')
            ->with($orderId)
            ->willReturn(null);

        // Expect exception
        $this->expectException(OrderNotFoundException::class);
        $this->expectExceptionMessage("Order {$orderId} not found");

        // Act
        $this->service->updateStatus($orderId, $newStatus);
    }

    private function createProduct(string $id, int $price): object
    {
        return new class($id, $price) {
            public function __construct(
                public readonly string $id,
                public readonly int $price,
                public readonly bool $isInStock = true,
                public readonly int $availableQuantity = 100
            ) {}
        };
    }

    private function createOrder(string $id, OrderStatus $status): Order
    {
        return new Order(
            id: $id,
            customerId: 'customer-123',
            items: collect([new OrderItem('product-456', 1, new Money(1000))]),
            status: $status,
            totalAmount: new Money(1000),
            createdAt: new \DateTimeImmutable()
        );
    }
}
```

### API Testing
```php
// tests/Feature/Api/V1/OrderControllerTest.php
<?php

declare(strict_types=1);

namespace Tests\Feature\Api\V1;

use App\Domain\Order\Entities\Order;
use App\Domain\Order\Services\OrderServiceInterface;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;
use Mockery;

final class OrderControllerTest extends TestCase
{
    use RefreshDatabase;

    public function testCreateOrderSuccessfully(): void
    {
        // Arrange
        $orderData = [
            'customer_id' => 'customer-123',
            'items' => [
                [
                    'product_id' => 'product-456',
                    'quantity' => 2,
                    'unit_price' => 25.50,
                ],
            ],
        ];

        $expectedOrder = new Order(
            id: 'order-789',
            customerId: 'customer-123',
            items: collect(),
            status: \App\Domain\Order\Enums\OrderStatus::PENDING,
            totalAmount: new \App\Domain\Order\ValueObjects\Money(5100),
            createdAt: new \DateTimeImmutable()
        );

        $mockService = Mockery::mock(OrderServiceInterface::class);
        $mockService->shouldReceive('createOrder')
            ->once()
            ->with($orderData)
            ->andReturn($expectedOrder);

        $this->app->instance(OrderServiceInterface::class, $mockService);

        // Act
        $response = $this->postJson('/api/v1/orders', $orderData);

        // Assert
        $response->assertStatus(201)
            ->assertJsonStructure([
                'data' => [
                    'id',
                    'customer_id',
                    'status',
                    'total_amount',
                    'created_at',
                    'items',
                ],
            ]);

        $response->assertJsonFragment([
            'id' => 'order-789',
            'customer_id' => 'customer-123',
            'status' => 'pending',
        ]);
    }

    public function testCreateOrderWithInvalidData(): void
    {
        // Arrange
        $invalidData = [
            'customer_id' => '',
            'items' => [],
        ];

        // Act
        $response = $this->postJson('/api/v1/orders', $invalidData);

        // Assert
        $response->assertStatus(422)
            ->assertJsonValidationErrors(['customer_id', 'items']);
    }

    public function testGetOrderSuccessfully(): void
    {
        // Arrange
        $orderId = 'order-123';
        $order = new Order(
            id: $orderId,
            customerId: 'customer-456',
            items: collect(),
            status: \App\Domain\Order\Enums\OrderStatus::PROCESSING,
            totalAmount: new \App\Domain\Order\ValueObjects\Money(5000),
            createdAt: new \DateTimeImmutable()
        );

        $mockService = Mockery::mock(OrderServiceInterface::class);
        $mockService->shouldReceive('findById')
            ->once()
            ->with($orderId)
            ->andReturn($order);

        $this->app->instance(OrderServiceInterface::class, $mockService);

        // Act
        $response = $this->getJson("/api/v1/orders/{$orderId}");

        // Assert
        $response->assertStatus(200)
            ->assertJsonStructure([
                'data' => [
                    'id',
                    'customer_id',
                    'status',
                    'total_amount',
                    'created_at',
                ],
            ]);

        $response->assertJsonFragment([
            'id' => $orderId,
            'status' => 'processing',
        ]);
    }

    public function testGetNonExistentOrder(): void
    {
        // Arrange
        $orderId = 'non-existent';

        $mockService = Mockery::mock(OrderServiceInterface::class);
        $mockService->shouldReceive('findById')
            ->once()
            ->with($orderId)
            ->andReturn(null);

        $this->app->instance(OrderServiceInterface::class, $mockService);

        // Act
        $response = $this->getJson("/api/v1/orders/{$orderId}");

        // Assert
        $response->assertStatus(404)
            ->assertJson([
                'error' => 'Order not found',
            ]);
    }
}
```

## Common Use Cases

### Event-Driven Architecture
```php
// app/Domain/Order/Events/OrderCreated.php
<?php

declare(strict_types=1);

namespace App\Domain\Order\Events;

use App\Domain\Order\Entities\Order;

final readonly class OrderCreated
{
    public function __construct(public Order $order) {}
}

// app/Listeners/ProcessOrderPayment.php
<?php

declare(strict_types=1);

namespace App\Listeners;

use App\Domain\Order\Events\OrderCreated;
use App\Domain\Payment\Services\PaymentServiceInterface;
use Psr\Log\LoggerInterface;

final readonly class ProcessOrderPayment
{
    public function __construct(
        private PaymentServiceInterface $paymentService,
        private LoggerInterface $logger
    ) {}

    public function handle(OrderCreated $event): void
    {
        try {
            $result = $this->paymentService->processPayment(
                $event->order->id,
                $event->order->totalAmount
            );

            if ($result->isSuccessful()) {
                $this->logger->info(
                    'Payment processed successfully for order {orderId}',
                    ['orderId' => $event->order->id]
                );
            } else {
                $this->logger->error(
                    'Payment failed for order {orderId}: {error}',
                    [
                        'orderId' => $event->order->id,
                        'error' => $result->getErrorMessage(),
                    ]
                );
            }
        } catch (\Throwable $e) {
            $this->logger->error(
                'Error processing payment for order {orderId}: {error}',
                [
                    'orderId' => $event->order->id,
                    'error' => $e->getMessage(),
                ]
            );
        }
    }
}
```

### Console Commands
```php
// app/Console/Commands/ProcessPendingOrders.php
<?php

declare(strict_types=1);

namespace App\Console\Commands;

use App\Domain\Order\Repositories\OrderRepositoryInterface;
use App\Domain\Order\Services\OrderService;
use Illuminate\Console\Command;
use Psr\Log\LoggerInterface;

final class ProcessPendingOrders extends Command
{
    protected $signature = 'orders:process-pending {--limit=10 : Maximum number of orders to process}';
    protected $description = 'Process pending orders';

    public function __construct(
        private readonly OrderRepositoryInterface $orderRepository,
        private readonly OrderService $orderService,
        private readonly LoggerInterface $logger
    ) {
        parent::__construct();
    }

    public function handle(): int
    {
        $limit = (int) $this->option('limit');
        $pendingOrders = $this->orderRepository->findPendingOrders($limit);

        if ($pendingOrders->isEmpty()) {
            $this->info('No pending orders to process');
            return self::SUCCESS;
        }

        $processed = 0;
        $failed = 0;

        foreach ($pendingOrders as $order) {
            try {
                $this->orderService->processOrder($order);
                $processed++;
                $this->line("Processed order: {$order->id}");
            } catch (\Throwable $e) {
                $failed++;
                $this->logger->error(
                    'Failed to process order {orderId}: {error}',
                    [
                        'orderId' => $order->id,
                        'error' => $e->getMessage(),
                    ]
                );
                $this->error("Failed to process order {$order->id}: {$e->getMessage()}");
            }
        }

        $this->info("Processing complete: {$processed} processed, {$failed} failed");
        return self::SUCCESS;
    }
}
```

This PHP skill provides comprehensive expertise in modern PHP 8.2+ development, enterprise architecture patterns, and performance optimization techniques for building scalable applications.