# Architecture Documentation

## System Overview

This is an event-driven microservices architecture for an e-commerce platform. The system is designed to be scalable, resilient, and maintainable using modern distributed systems patterns.

## Architecture Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│              API Gateway (Future)               │
└─────────────────────────────────────────────────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Products │   │  Orders  │   │ Payments │   │  Events  │
│ Service  │   │ Service  │   │ Service  │   │ Service  │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │
     │              │              │              │
     ▼              ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│PostgreSQL│   │PostgreSQL│   │PostgreSQL│   │PostgreSQL│
└──────────┘   └──────────┘   └──────────┘   └──────────┘
     │              │              │              │
     └──────────────┴──────────────┴──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │     Redis    │
              │    (Cache)   │
              └──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │    Kafka     │
              │ (Event Bus)  │
              └──────────────┘
```

## Microservices

### 1. Products Service
**Responsibility**: Manages product catalog and inventory

**Endpoints**:
- `GET /api/v1/products/` - List products
- `POST /api/v1/products/` - Create product
- `GET /api/v1/products/{id}` - Get product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

**Kafka Events**:
- **Publishes**: `product.created`, `inventory.updated`
- **Consumes**: `order.created` (updates inventory)

**Database**: PostgreSQL (products_db)

### 2. Orders Service
**Responsibility**: Handles order creation and management

**Endpoints**:
- `GET /api/v1/orders/` - List orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/{id}` - Get order
- `PUT /api/v1/orders/{id}` - Update order
- `POST /api/v1/orders/{id}/cancel` - Cancel order

**Kafka Events**:
- **Publishes**: `order.created`, `order.cancelled`
- **Consumes**: `payment.processed`, `payment.failed` (updates order status)

**Database**: PostgreSQL (orders_db)

### 3. Payments Service
**Responsibility**: Processes payment transactions

**Endpoints**:
- `GET /api/v1/payments/` - List payments
- `POST /api/v1/payments/` - Create payment
- `GET /api/v1/payments/{id}` - Get payment
- `GET /api/v1/payments/order/{order_id}` - Get payments for order

**Kafka Events**:
- **Publishes**: `payment.processed`, `payment.failed`
- **Consumes**: `order.created` (auto-processes payment)

**Database**: PostgreSQL (payments_db)

### 4. Events Service
**Responsibility**: Event logging and notifications

**Endpoints**:
- `GET /api/v1/events/logs` - List event logs
- `GET /api/v1/events/logs/{id}` - Get event log
- `GET /api/v1/events/notifications` - List notifications
- `POST /api/v1/events/notifications/{id}/read` - Mark notification as read

**Kafka Events**:
- **Consumes**: All events (logs them and creates notifications)

**Database**: PostgreSQL (events_db)

## Event Flow

### Order Creation Flow

1. **Client** → **Orders Service**: Create order
2. **Orders Service**:
   - Saves order to database
   - Publishes `order.created` event to Kafka
3. **Payments Service** (consumes `order.created`):
   - Creates payment record
   - Processes payment
   - Publishes `payment.processed` or `payment.failed`
4. **Products Service** (consumes `order.created`):
   - Updates inventory
   - Publishes `inventory.updated`
5. **Orders Service** (consumes `payment.processed`):
   - Updates order status to "confirmed"
6. **Events Service** (consumes all events):
   - Logs events
   - Creates notifications for users

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Relational database (one per service)
- **Redis**: Caching layer

### Messaging
- **Apache Kafka**: Event streaming platform
- **Zookeeper**: Kafka coordination

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Local development orchestration
- **Kubernetes**: Production orchestration

### CI/CD
- **GitHub Actions**: Continuous Integration and Deployment

## Data Models

### Product
```python
{
    "id": int,
    "name": str,
    "description": str,
    "price": float,
    "stock": int,
    "category": str,
    "is_active": bool,
    "created_at": datetime,
    "updated_at": datetime
}
```

### Order
```python
{
    "id": int,
    "user_id": int,
    "items": [{"product_id": int, "quantity": int, "price": float}],
    "total_amount": float,
    "status": "pending" | "confirmed" | "processing" | "shipped" | "delivered" | "cancelled",
    "shipping_address": str,
    "created_at": datetime,
    "updated_at": datetime
}
```

### Payment
```python
{
    "id": int,
    "order_id": int,
    "user_id": int,
    "amount": float,
    "payment_method": str,
    "status": "pending" | "processing" | "completed" | "failed" | "refunded",
    "transaction_id": str,
    "failure_reason": str,
    "created_at": datetime,
    "updated_at": datetime
}
```

## Event Schemas

All events follow a consistent schema structure:

```python
{
    "event_type": str,
    "timestamp": datetime,
    "data": {...}
}
```

### Event Types

1. **order.created**: Published when an order is created
2. **order.cancelled**: Published when an order is cancelled
3. **payment.processed**: Published when payment succeeds
4. **payment.failed**: Published when payment fails
5. **inventory.updated**: Published when inventory changes
6. **product.created**: Published when a product is created

## Scalability Considerations

1. **Horizontal Scaling**: Each service can be scaled independently
2. **Database Sharding**: Each service has its own database
3. **Event-Driven**: Loose coupling allows services to scale independently
4. **Caching**: Redis reduces database load
5. **Load Balancing**: Kubernetes services provide load balancing

## Resilience Patterns

1. **Circuit Breaker**: (Future) Prevent cascade failures
2. **Retry Logic**: Kafka consumers retry failed messages
3. **Event Sourcing**: Events are logged for audit and replay
4. **Health Checks**: Each service exposes health endpoints
5. **Graceful Degradation**: Services can operate independently

## Security Considerations

1. **API Authentication**: (Future) JWT tokens
2. **Service-to-Service Auth**: (Future) mTLS
3. **Database Encryption**: (Future) Encrypt sensitive data
4. **Secrets Management**: Kubernetes secrets
5. **Input Validation**: Pydantic models validate all inputs

## Monitoring & Observability

1. **Health Endpoints**: `/health` on each service
2. **Event Logging**: All events logged in Events service
3. **Structured Logging**: JSON logs for parsing
4. **Metrics**: (Future) Prometheus integration
5. **Tracing**: (Future) Distributed tracing with Jaeger

## Future Enhancements

1. API Gateway for unified entry point
2. Service mesh (Istio) for advanced traffic management
3. GraphQL API layer
4. Real-time notifications via WebSockets
5. Advanced analytics and reporting
6. Multi-tenancy support
7. Event replay capabilities
8. Saga pattern for distributed transactions

