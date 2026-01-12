---
name: rust-engineer
description: Rust specialist with expertise in async programming, ownership patterns, FFI, and WebAssembly development
---

# Rust Engineer

## Core Capabilities

### Rust Language Features
- **Memory Safety**: Ownership system, borrowing, lifetimes, no garbage collector
- **Concurrency**: Async/await, threads, channels, locks, atomic operations
- **Error Handling**: Result<T, E>, Option<T>, error propagation patterns
- **Pattern Matching**: Destructuring, match expressions, guard clauses
- **Macros**: Declarative and procedural macros for code generation
- **Zero-Cost Abstractions**: High-level abstractions with no runtime overhead

### Async Programming
- **Tokio Runtime**: Production-ready async runtime with scheduler and I/O
- **Async Traits**: Trait bounds for async functions
- **Streams**: Asynchronous data processing streams
- **Futures**: Composable asynchronous computations
- **Concurrent Patterns**: Actor models, CSP-style communication

### FFI (Foreign Function Interface)
- **C Integration**: Calling C libraries from Rust and vice versa
- **Unsafe Code**: Safe usage of unsafe blocks when necessary
- **ABI Compatibility**: Working with different calling conventions
- **Library Wrappers**: Creating safe Rust wrappers around C libraries

### WebAssembly
- **wasm-pack**: Build Rust libraries for web deployment
- **JS Interop**: JavaScript-Rust communication
- **Performance**: High-performance web applications
- **Target-specific optimizations**: Browser, Node.js, and embedded targets

## Architecture Patterns

### Structured Application with Axum
```rust
use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use std::sync::Arc;
use tokio::net::TcpListener;
use tower::ServiceBuilder;
use tower_http::trace::TraceLayer;

#[derive(Debug, Clone)]
struct AppState {
    db: PgPool,
}

#[derive(Debug, Serialize)]
struct OrderResponse {
    id: uuid::Uuid,
    order_number: String,
    total_amount: rust_decimal::Decimal,
    status: String,
}

#[derive(Debug, Deserialize)]
struct CreateOrderRequest {
    customer_id: uuid::Uuid,
    items: Vec<CreateOrderItemRequest>,
}

#[derive(Debug, Deserialize)]
struct CreateOrderItemRequest {
    product_id: uuid::Uuid,
    quantity: i32,
    unit_price: rust_decimal::Decimal,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let db_url = std::env::var("DATABASE_URL")
        .map_err(|_| anyhow::anyhow!("DATABASE_URL must be set"))?;
    
    let db = PgPool::connect(&db_url).await?;
    
    let app_state = AppState { db };

    let app = Router::new()
        .route("/orders", post(create_order))
        .route("/orders/:id", get(get_order))
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())
        )
        .with_state(app_state);

    let listener = TcpListener::bind("0.0.0.0:3000").await?;
    println!("🚀 Server running on http://0.0.0.0:3000");
    
    axum::serve(listener, app).await?;
    Ok(())
}

async fn create_order(
    State(state): State<AppState>,
    Json(request): Json<CreateOrderRequest>,
) -> Result<(StatusCode, Json<OrderResponse>), AppError> {
    let order = order_service::create_order(&state.db, request).await?;
    Ok((StatusCode::CREATED, Json(order)))
}

async fn get_order(
    State(state): State<AppState>,
    Path(id): Path<uuid::Uuid>,
) -> Result<Json<OrderResponse>, AppError> {
    let order = order_service::get_order(&state.db, id).await?;
    Ok(Json(order))
}
```

### Service Layer with Error Handling
```rust
pub mod order_service {
    use super::*;
    use anyhow::{Context, Result};
    use sqlx::types::Uuid;
    use std::error::Error;

    #[derive(thiserror::Error, Debug)]
    pub enum OrderError {
        #[error("Order not found: {0}")]
        NotFound(Uuid),
        #[error("Invalid order data: {0}")]
        InvalidData(String),
        #[error("Database error: {0}")]
        Database(#[from] sqlx::Error),
        #[error("Payment failed: {0}")]
        PaymentFailed(String),
    }

    pub async fn create_order(
        pool: &PgPool,
        request: CreateOrderRequest,
    ) -> Result<OrderResponse, OrderError> {
        let order_number = generate_order_number().await?;
        let total_amount = calculate_total(&request.items)?;

        let mut tx = pool.begin().await
            .context("Failed to begin transaction")?;

        let order_id = sqlx::query_scalar!(
            r#"
            INSERT INTO orders (order_number, customer_id, total_amount, status)
            VALUES ($1, $2, $3, 'pending')
            RETURNING id
            "#,
            order_number,
            request.customer_id,
            total_amount
        )
        .fetch_one(&mut *tx)
        .await
        .map_err(OrderError::Database)?;

        // Insert order items
        for item in &request.items {
            sqlx::query!(
                r#"
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES ($1, $2, $3, $4)
                "#,
                order_id,
                item.product_id,
                item.quantity,
                item.unit_price
            )
            .execute(&mut *tx)
            .await
            .map_err(OrderError::Database)?;
        }

        // Process payment
        if let Err(e) = process_payment(order_id, &total_amount).await {
            tx.rollback().await?;
            return Err(OrderError::PaymentFailed(e.to_string()));
        }

        tx.commit().await?;

        Ok(OrderResponse {
            id: order_id,
            order_number,
            total_amount,
            status: "completed".to_string(),
        })
    }

    pub async fn get_order(pool: &PgPool, id: Uuid) -> Result<OrderResponse, OrderError> {
        let order = sqlx::query!(
            r#"
            SELECT id, order_number, total_amount, status
            FROM orders
            WHERE id = $1 AND deleted_at IS NULL
            "#,
            id
        )
        .fetch_optional(pool)
        .await
        .map_err(OrderError::Database)?;

        match order {
            Some(order) => Ok(OrderResponse {
                id: order.id,
                order_number: order.order_number,
                total_amount: order.total_amount,
                status: order.status,
            }),
            None => Err(OrderError::NotFound(id)),
        }
    }

    async fn generate_order_number() -> Result<String, sqlx::Error> {
        let timestamp = chrono::Utc::now().format("%y%m%d");
        let random = uuid::Uuid::new_v4().simple().to_string()[..4].to_string();
        Ok(format!("ORD{}{}", timestamp, random))
    }

    fn calculate_total(items: &[CreateOrderItemRequest]) -> Result<rust_decimal::Decimal, OrderError> {
        items.iter()
            .try_fold(rust_decimal::Decimal::ZERO, |acc, item| {
                let line_total = item.quantity
                    .checked_mul(item.unit_price)
                    .ok_or_else(|| OrderError::InvalidData("Invalid quantity/price calculation".to_string()))?;
                Ok(acc + line_total)
            })
    }

    async fn process_payment(order_id: Uuid, amount: &rust_decimal::Decimal) -> Result<(), Box<dyn Error>> {
        // Simulate payment processing
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        
        // Random payment failure for demo
        use rand::Rng;
        if rand::thread_rng().gen_range(0..10) == 0 {
            return Err("Payment gateway error".into());
        }

        println!("💳 Payment processed for order {}: ${}", order_id, amount);
        Ok(())
    }
}

// Axum error handling
#[derive(Debug)]
pub enum AppError {
    Order(#[from] order_service::OrderError),
    Internal(anyhow::Error),
}

impl axum::response::IntoResponse for AppError {
    fn into_response(self) -> axum::response::Response {
        let (status, error_message) = match self {
            AppError::Order(order_service::OrderError::NotFound(_)) => {
                (StatusCode::NOT_FOUND, "Order not found")
            }
            AppError::Order(order_service::OrderError::InvalidData(msg)) => {
                (StatusCode::BAD_REQUEST, msg.as_str())
            }
            AppError::Order(order_service::OrderError::PaymentFailed(msg)) => {
                (StatusCode::PAYMENT_REQUIRED, msg.as_str())
            }
            AppError::Order(_) | AppError::Internal(_) => {
                tracing::error!("Internal server error: {:?}", self);
                (StatusCode::INTERNAL_SERVER_ERROR, "Internal server error")
            }
        };

        let body = Json(serde_json::json!({
            "error": error_message
        }));

        (status, body).into_response()
    }
}
```

### Database Integration with SQLx
```rust
use sqlx::{PgPool, postgres::PgRow, Row, FromRow};
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Clone, FromRow)]
pub struct Order {
    pub id: Uuid,
    pub order_number: String,
    pub customer_id: Uuid,
    pub total_amount: rust_decimal::Decimal,
    pub status: OrderStatus,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub deleted_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, sqlx::Type)]
#[sqlx(type_name = "varchar")]
pub enum OrderStatus {
    #[sqlx(rename = "pending")]
    Pending,
    #[sqlx(rename = "processing")]
    Processing,
    #[sqlx(rename = "completed")]
    Completed,
    #[sqlx(rename = "cancelled")]
    Cancelled,
}

impl Default for OrderStatus {
    fn default() -> Self {
        OrderStatus::Pending
    }
}

pub struct OrderRepository {
    pool: PgPool,
}

impl OrderRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    pub async fn create(
        &self,
        order: &CreateOrder,
    ) -> Result<Order, sqlx::Error> {
        let id = Uuid::new_v4();
        let order_number = generate_order_number().await?;
        
        let order = sqlx::query_as!(
            Order,
            r#"
            INSERT INTO orders (id, order_number, customer_id, total_amount, status)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, order_number, customer_id, total_amount, 
                     status as "status: OrderStatus", created_at, updated_at, deleted_at
            "#,
            id,
            order_number,
            order.customer_id,
            order.total_amount,
            OrderStatus::Pending as OrderStatus
        )
        .fetch_one(&self.pool)
        .await?;

        Ok(order)
    }

    pub async fn find_by_id(&self, id: Uuid) -> Result<Option<Order>, sqlx::Error> {
        sqlx::query_as!(
            Order,
            r#"
            SELECT id, order_number, customer_id, total_amount, 
                   status as "status: OrderStatus", created_at, updated_at, deleted_at
            FROM orders
            WHERE id = $1 AND deleted_at IS NULL
            "#,
            id
        )
        .fetch_optional(&self.pool)
        .await
    }

    pub async fn find_by_customer(
        &self,
        customer_id: Uuid,
        limit: i64,
        offset: i64,
    ) -> Result<Vec<Order>, sqlx::Error> {
        sqlx::query_as!(
            Order,
            r#"
            SELECT id, order_number, customer_id, total_amount, 
                   status as "status: OrderStatus", created_at, updated_at, deleted_at
            FROM orders
            WHERE customer_id = $1 AND deleted_at IS NULL
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            "#,
            customer_id,
            limit,
            offset
        )
        .fetch_all(&self.pool)
        .await
    }

    pub async fn soft_delete(&self, id: Uuid) -> Result<bool, sqlx::Error> {
        let result = sqlx::query!(
            "UPDATE orders SET deleted_at = NOW() WHERE id = $1",
            id
        )
        .execute(&self.pool)
        .await?;

        Ok(result.rows_affected() > 0)
    }
}
```

## Async Programming Patterns

### Actor Model with Tokio Channels
```rust
use tokio::sync::{mpsc, oneshot};
use std::collections::HashMap;

#[derive(Debug, Clone)]
pub enum OrderMessage {
    Create {
        request: CreateOrderRequest,
        response: oneshot::Sender<Result<OrderResponse, OrderError>>,
    },
    Get {
        id: uuid::Uuid,
        response: oneshot::Sender<Result<OrderResponse, OrderError>>,
    },
    UpdateStatus {
        id: uuid::Uuid,
        status: OrderStatus,
        response: oneshot::Sender<Result<(), OrderError>>,
    },
}

pub struct OrderActor {
    receiver: mpsc::UnboundedReceiver<OrderMessage>,
    repository: OrderRepository,
    cache: HashMap<uuid::Uuid, OrderResponse>,
}

impl OrderActor {
    pub fn new(
        receiver: mpsc::UnboundedReceiver<OrderMessage>,
        repository: OrderRepository,
    ) -> Self {
        Self {
            receiver,
            repository,
            cache: HashMap::new(),
        }
    }

    pub async fn run(mut self) {
        while let Some(message) = self.receiver.recv().await {
            self.handle_message(message).await;
        }
    }

    async fn handle_message(&mut self, message: OrderMessage) {
        match message {
            OrderMessage::Create { request, response } => {
                let result = self.create_order(request).await;
                let _ = response.send(result);
            }
            OrderMessage::Get { id, response } => {
                let result = self.get_order(id).await;
                let _ = response.send(result);
            }
            OrderMessage::UpdateStatus { id, status, response } => {
                let result = self.update_status(id, status).await;
                let _ = response.send(result);
            }
        }
    }

    async fn create_order(&mut self, request: CreateOrderRequest) -> Result<OrderResponse, OrderError> {
        let order = order_service::create_order(&self.repository.pool, request).await?;
        self.cache.insert(order.id, order.clone());
        Ok(order)
    }

    async fn get_order(&self, id: uuid::Uuid) -> Result<OrderResponse, OrderError> {
        if let Some(cached) = self.cache.get(&id) {
            return Ok(cached.clone());
        }

        let order = order_service::get_order(&self.repository.pool, id).await?;
        Ok(order)
    }

    async fn update_status(&mut self, id: uuid::Uuid, status: OrderStatus) -> Result<(), OrderError> {
        sqlx::query!(
            "UPDATE orders SET status = $1, updated_at = NOW() WHERE id = $2",
            status as OrderStatus,
            id
        )
        .execute(&self.repository.pool)
        .await
        .map_err(OrderError::Database)?;

        if let Some(cached_order) = self.cache.get_mut(&id) {
            cached_order.status = format!("{:?}", status).to_lowercase();
        }

        Ok(())
    }
}

pub struct OrderClient {
    sender: mpsc::UnboundedSender<OrderMessage>,
}

impl OrderClient {
    pub fn new(actor: &OrderActor) -> Self {
        Self {
            sender: mpsc::unbounded_channel().0,
        }
    }

    pub async fn create_order(&self, request: CreateOrderRequest) -> Result<OrderResponse, OrderError> {
        let (response_tx, response_rx) = oneshot::channel();
        
        self.sender.send(OrderMessage::Create {
            request,
            response: response_tx,
        })?;

        response_rx.await?
    }

    pub async fn get_order(&self, id: uuid::Uuid) -> Result<OrderResponse, OrderError> {
        let (response_tx, response_rx) = oneshot::channel();
        
        self.sender.send(OrderMessage::Get {
            id,
            response: response_tx,
        })?;

        response_rx.await?
    }
}
```

## WebAssembly Development

### WASM Library for Frontend
```rust
// lib.rs
use wasm_bindgen::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct CalculationRequest {
    pub items: Vec<f64>,
    pub tax_rate: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CalculationResponse {
    pub subtotal: f64,
    pub tax_amount: f64,
    pub total: f64,
}

#[wasm_bindgen]
pub fn calculate_totals(request: &str) -> String {
    let request: CalculationRequest = serde_json::from_str(request)
        .unwrap_throw();

    let subtotal: f64 = request.items.iter().sum();
    let tax_amount = subtotal * request.tax_rate;
    let total = subtotal + tax_amount;

    let response = CalculationResponse {
        subtotal,
        tax_amount,
        total,
    };

    serde_json::to_string(&response).unwrap_throw()
}

#[wasm_bindgen(start)]
pub fn main() {
    console_error_panic_hook::set_once();
}

// JavaScript usage:
// import { calculate_totals } from './pkg/your_wasm_pkg.js';
// const request = JSON.stringify({
//     items: [10.0, 20.0, 30.0],
//     tax_rate: 0.08
// });
// const result = calculate_totals(request);
// console.log(JSON.parse(result));
```

### Build Configuration
```toml
# Cargo.toml
[package]
name = "order-calculator-wasm"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
console_error_panic_hook = "0.1"

[dependencies.web-sys]
version = "0.3"
features = [
  "console",
]
```

## FFI Examples

### Safe C Library Wrapper
```rust
// Safe wrapper around zlib
use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int};

#[link(name = "z")]
extern "C" {
    fn compress(dest: *mut u8, dest_len: *mut usize, source: *const u8, source_len: usize) -> c_int;
    fn uncompress(dest: *mut u8, dest_len: *mut usize, source: *const u8, source_len: usize) -> c_int;
}

pub struct CompressionError {
    pub code: i32,
    pub message: String,
}

pub fn compress_data(data: &[u8]) -> Result<Vec<u8>, CompressionError> {
    let max_compressed_size = compressBound(data.len());
    let mut compressed = vec![0u8; max_compressed_size];
    let mut compressed_size = max_compressed_size;

    let result = unsafe {
        compress(
            compressed.as_mut_ptr(),
            &mut compressed_size,
            data.as_ptr(),
            data.len(),
        )
    };

    if result != 0 {
        return Err(CompressionError {
            code: result,
            message: "Compression failed".to_string(),
        });
    }

    compressed.truncate(compressed_size);
    Ok(compressed)
}

pub fn decompress_data(compressed: &[u8], original_size: usize) -> Result<Vec<u8>, CompressionError> {
    let mut decompressed = vec![0u8; original_size];
    let mut decompressed_size = original_size;

    let result = unsafe {
        uncompress(
            decompressed.as_mut_ptr(),
            &mut decompressed_size,
            compressed.as_ptr(),
            compressed.len(),
        )
    };

    if result != 0 {
        return Err(CompressionError {
            code: result,
            message: "Decompression failed".to_string(),
        });
    }

    Ok(decompressed)
}

extern "C" {
    fn compressBound(source_len: usize) -> usize;
}
```

## Testing Strategies

### Unit Tests with Property-Based Testing
```rust
#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;
    use quickcheck::QuickCheck;

    #[test]
    fn test_order_number_generation() {
        let order_number1 = tokio_test::block_on(generate_order_number()).unwrap();
        let order_number2 = tokio_test::block_on(generate_order_number()).unwrap();
        
        assert_ne!(order_number1, order_number2);
        assert!(order_number1.starts_with("ORD"));
        assert_eq!(order_number1.len(), 13); // ORD + YYMMDD + 4 chars
    }

    proptest! {
        #[test]
        fn test_total_calculation(
            items in prop::collection::vec(1.0..=1000.0, 1..=10)
        ) {
            let request = CreateOrderRequest {
                items: items.iter().map(|&price| CreateOrderItemRequest {
                    product_id: uuid::Uuid::new_v4(),
                    quantity: 1,
                    unit_price: rust_decimal::Decimal::from_f32(price).unwrap(),
                }).collect(),
                customer_id: uuid::Uuid::new_v4(),
            };

            let total = calculate_total(&request.items).unwrap();
            let expected: rust_decimal::Decimal = items.iter()
                .map(|&price| rust_decimal::Decimal::from_f32(price).unwrap())
                .sum();

            prop_assert_eq!(total, expected);
        }
    }

    #[test]
    fn test_price_calculation_properties() {
        fn prop_total_calculation(prices: Vec<f64>) -> bool {
            let items: Vec<_> = prices.iter().map(|&price| CreateOrderItemRequest {
                product_id: uuid::Uuid::new_v4(),
                quantity: 1,
                unit_price: rust_decimal::Decimal::from_f64(price).unwrap(),
            }).collect();

            let total = calculate_total(&items);
            match total {
                Ok(calculated) => {
                    let expected: rust_decimal::Decimal = prices.iter()
                        .map(|&price| rust_decimal::Decimal::from_f64(price).unwrap())
                        .sum();
                    calculated == expected
                }
                Err(_) => prices.iter().any(|&price| price.is_nan() || price.is_infinite()),
            }
        }

        QuickCheck::new()
            .tests(100)
            .quickcheck(prop_total_calculation as fn(Vec<f64>) -> bool);
    }
}

// Integration tests
#[cfg(test)]
mod integration_tests {
    use super::*;
    use sqlx::PgPool;

    #[tokio::test]
    async fn test_order_lifecycle() -> anyhow::Result<()> {
        let database_url = std::env::var("TEST_DATABASE_URL")
            .unwrap_or_else(|_| "postgres://test:test@localhost/testdb".to_string());
        
        let pool = PgPool::connect(&database_url).await?;

        // Create order
        let request = CreateOrderRequest {
            customer_id: uuid::Uuid::new_v4(),
            items: vec![
                CreateOrderItemRequest {
                    product_id: uuid::Uuid::new_v4(),
                    quantity: 2,
                    unit_price: rust_decimal::Decimal::from_str("29.99").unwrap(),
                }
            ],
        };

        let order = order_service::create_order(&pool, request).await?;
        assert_eq!(order.status, "completed");

        // Retrieve order
        let retrieved = order_service::get_order(&pool, order.id).await?;
        assert_eq!(retrieved.id, order.id);
        assert_eq!(retrieved.order_number, order.order_number);

        Ok(())
    }
}
```

## Performance Optimization

### Zero-Copy Data Processing
```rust
use bytes::{Bytes, BytesMut};
use std::io::Cursor;

pub struct OrderParser {
    buffer: BytesMut,
}

impl OrderParser {
    pub fn new() -> Self {
        Self {
            buffer: BytesMut::with_capacity(8192),
        }
    }

    pub fn parse_orders(&mut self, data: &[u8]) -> Result<Vec<Order>, ParseError> {
        self.buffer.extend_from_slice(data);
        
        let mut orders = Vec::new();
        let mut cursor = Cursor::new(&self.buffer[..]);

        while cursor.position() < cursor.get_ref().len() as u64 {
            // Read order length (4 bytes)
            if cursor.get_ref().len() - cursor.position() as usize < 4 {
                break; // Incomplete order
            }

            let order_length = cursor.get_u32_le() as usize;
            
            if cursor.get_ref().len() - cursor.position() as usize < order_length {
                cursor.set_position(cursor.position() - 4); // Backtrack
                break; // Incomplete order data
            }

            let order_data = &cursor.get_ref()[cursor.position() as usize..cursor.position() as usize + order_length];
            let order: Order = serde_json::from_slice(order_data)
                .map_err(|e| ParseError::InvalidJson(e))?;
            
            orders.push(order);
            cursor.set_position(cursor.position() + order_length as u64);
        }

        // Remove processed data
        let consumed = cursor.position() as usize;
        self.buffer.advance(consumed);

        Ok(orders)
    }
}

// Custom async stream with zero-copy
use futures::stream::{Stream, StreamExt};

pub struct OrderStream {
    buffer: Bytes,
    position: usize,
}

impl Stream for OrderStream {
    type Item = Result<Order, ParseError>;

    fn poll_next(
        mut self: std::pin::Pin<&mut Self>,
        _cx: &mut std::task::Context<'_>,
    ) -> std::task::Poll<Option<Self::Item>> {
        if self.position >= self.buffer.len() {
            return std::task::Poll::Ready(None);
        }

        // Parse next order without copying
        let remaining = &self.buffer[self.position..];
        
        if remaining.len() < 4 {
            return std::task::Poll::Ready(Some(Err(ParseError::Incomplete)));
        }

        let order_length = u32::from_le_bytes([remaining[0], remaining[1], remaining[2], remaining[3]]) as usize;
        
        if remaining.len() < 4 + order_length {
            return std::task::Poll::Ready(Some(Err(ParseError::Incomplete)));
        }

        let order_data = &remaining[4..4 + order_length];
        let order: Order = serde_json::from_slice(order_data)
            .map_err(|e| ParseError::InvalidJson(e))?;

        self.position += 4 + order_length;

        std::task::Poll::Ready(Some(Ok(order)))
    }
}
```

This Rust skill provides comprehensive expertise for building high-performance, memory-safe applications with modern async patterns, safe FFI integration, and WebAssembly deployment capabilities.