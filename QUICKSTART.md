# Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- Git

## Option 1: Using Docker Compose (Recommended)

### 1. Clone and Setup

```bash
# Navigate to project directory
cd event-driven-ecom-backend

# Run setup script (Linux/Mac)
chmod +x setup.sh
./setup.sh

# Or manually start services
docker-compose up -d
```

### 2. Verify Services

Check that all services are running:

```bash
docker-compose ps
```

### 3. Access Services

- **Products API**: http://localhost:8001/docs
- **Orders API**: http://localhost:8002/docs
- **Payments API**: http://localhost:8003/docs
- **Events API**: http://localhost:8004/docs
- **Kafka UI**: http://localhost:8080

### 4. Test Event Flow

```bash
# Install Python dependencies
pip install requests

# Run test script
python examples/test_event_flow.py
```

## Option 2: Local Development

### 1. Start Infrastructure

```bash
# Start only infrastructure services (Kafka, PostgreSQL, Redis)
docker-compose up -d zookeeper kafka postgres-products postgres-orders postgres-payments postgres-events redis
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Services Locally

Open separate terminals for each service:

**Terminal 1 - Products Service:**
```bash
cd services/products
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/products_db"
export REDIS_URL="redis://localhost:6379"
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
uvicorn main:app --reload --port 8001
```

**Terminal 2 - Orders Service:**
```bash
cd services/orders
export DATABASE_URL="postgresql://postgres:postgres@localhost:5433/orders_db"
export REDIS_URL="redis://localhost:6379"
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
uvicorn main:app --reload --port 8002
```

**Terminal 3 - Payments Service:**
```bash
cd services/payments
export DATABASE_URL="postgresql://postgres:postgres@localhost:5434/payments_db"
export REDIS_URL="redis://localhost:6379"
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
uvicorn main:app --reload --port 8003
```

**Terminal 4 - Events Service:**
```bash
cd services/events
export DATABASE_URL="postgresql://postgres:postgres@localhost:5435/events_db"
export REDIS_URL="redis://localhost:6379"
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
uvicorn main:app --reload --port 8004
```

## Testing the System

### Manual API Testing

1. **Create a Product:**
```bash
curl -X POST "http://localhost:8001/api/v1/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "stock": 100,
    "category": "Electronics"
  }'
```

2. **Create an Order:**
```bash
curl -X POST "http://localhost:8002/api/v1/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "items": [
      {
        "product_id": 1,
        "quantity": 2,
        "price": 999.99
      }
    ],
    "shipping_address": "123 Main St"
  }'
```

3. **Check Payment Status:**
```bash
curl "http://localhost:8003/api/v1/payments/order/1"
```

4. **View Event Logs:**
```bash
curl "http://localhost:8004/api/v1/events/logs?limit=10"
```

5. **View Notifications:**
```bash
curl "http://localhost:8004/api/v1/events/notifications?user_id=123"
```

### Using the Test Script

```bash
python examples/test_event_flow.py
```

This script will:
1. Create a product
2. Create an order (triggers payment and inventory update)
3. Check payment status
4. Check updated inventory
5. View event logs
6. View notifications

## Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f products-service
docker-compose logs -f orders-service
docker-compose logs -f payments-service
docker-compose logs -f events-service

# Kafka logs
docker-compose logs -f kafka
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Troubleshooting

### Services not starting

1. Check if ports are already in use:
```bash
# Check ports
netstat -an | grep -E "8001|8002|8003|8004|9092|5432|6379"
```

2. Check Docker logs:
```bash
docker-compose logs [service-name]
```

### Database connection errors

1. Ensure PostgreSQL containers are running:
```bash
docker-compose ps | grep postgres
```

2. Check database logs:
```bash
docker-compose logs postgres-products
```

### Kafka connection errors

1. Ensure Kafka and Zookeeper are running:
```bash
docker-compose ps | grep -E "kafka|zookeeper"
```

2. Check Kafka logs:
```bash
docker-compose logs kafka
```

3. Access Kafka UI: http://localhost:8080

### Import errors in Python

Make sure the shared directory is in the Python path. Services automatically add it, but if running manually:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation
- Explore API documentation at service `/docs` endpoints
- Check Kafka topics and messages in Kafka UI
- Review event logs in Events service

## Production Deployment

For production deployment using Kubernetes:

```bash
# Create namespace and secrets
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy infrastructure
kubectl apply -f k8s/postgres-products.yaml
kubectl apply -f k8s/postgres-orders.yaml
kubectl apply -f k8s/postgres-payments.yaml
kubectl apply -f k8s/postgres-events.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/kafka.yaml

# Deploy services
kubectl apply -f k8s/products-service.yaml
kubectl apply -f k8s/orders-service.yaml
kubectl apply -f k8s/payments-service.yaml
kubectl apply -f k8s/events-service.yaml

# Or use kustomize
kubectl apply -k k8s/
```

