# Event-Driven E-commerce Backend

A full microservice architecture for e-commerce with asynchronous event flows using Kafka.

## Architecture

This project implements a distributed microservices architecture with the following services:

- **Products Service**: Manages product catalog and inventory
- **Orders Service**: Handles order creation and management
- **Payments Service**: Processes payment transactions
- **Events Service**: Handles event notifications and logging

## Technology Stack

- **API Framework**: FastAPI
- **Message Broker**: Apache Kafka
- **Databases**: PostgreSQL (one per service)
- **Cache**: Redis
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions

## Project Structure

```
.
├── services/
│   ├── products/
│   ├── orders/
│   ├── payments/
│   └── events/
├── shared/
│   ├── kafka_client/
│   └── schemas/
├── k8s/
├── .github/
│   └── workflows/
└── docker-compose.yml
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Kafka (via Docker Compose)

### Local Development

1. Start all services with Docker Compose:
```bash
docker-compose up -d
```

2. Services will be available at:
   - Products API: http://localhost:8001
   - Orders API: http://localhost:8002
   - Payments API: http://localhost:8003
   - Events API: http://localhost:8004
   - Kafka UI: http://localhost:8080

3. Access API documentation:
   - Products: http://localhost:8001/docs
   - Orders: http://localhost:8002/docs
   - Payments: http://localhost:8003/docs
   - Events: http://localhost:8004/docs

### Running Individual Services

Each service can be run independently:

```bash
cd services/products
uvicorn main:app --reload --port 8001
```

## Event Flow

1. **Order Created**: Orders service publishes `order.created` event
2. **Payment Processing**: Payments service consumes `order.created` and processes payment
3. **Inventory Update**: Products service consumes `order.created` and updates inventory
4. **Notifications**: Events service consumes all events and sends notifications

## Kafka Topics

- `order.created` - Published when an order is created
- `order.cancelled` - Published when an order is cancelled
- `payment.processed` - Published when payment is processed
- `payment.failed` - Published when payment fails
- `inventory.updated` - Published when inventory is updated
- `product.created` - Published when a product is created

## Development

### Setting up a new service

1. Create service directory in `services/`
2. Copy structure from existing service
3. Update service-specific configurations
4. Add to docker-compose.yml
5. Add Kubernetes manifests

### Testing

Run tests for each service:
```bash
cd services/products
pytest
```

## Deployment

### Kubernetes

Deploy to Kubernetes:
```bash
kubectl apply -f k8s/
```

### CI/CD

GitHub Actions workflows are configured for:
- Automated testing
- Docker image building
- Kubernetes deployment

## License

MIT

