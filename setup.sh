#!/bin/bash

# Setup script for Event-Driven E-commerce Backend

set -e

echo "🚀 Setting up Event-Driven E-commerce Backend..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database URLs
DATABASE_URL_PRODUCTS=postgresql://postgres:postgres@postgres-products:5432/products_db
DATABASE_URL_ORDERS=postgresql://postgres:postgres@postgres-orders:5432/orders_db
DATABASE_URL_PAYMENTS=postgresql://postgres:postgres@postgres-payments:5432/payments_db
DATABASE_URL_EVENTS=postgresql://postgres:postgres@postgres-events:5432/events_db

# Redis
REDIS_URL=redis://redis:6379

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
EOF
    echo "✅ .env file created"
else
    echo "ℹ️  .env file already exists"
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
services=("products-service:8001" "orders-service:8002" "payments-service:8003" "events-service:8004")

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    if curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $name is healthy"
    else
        echo "⚠️  $name is not responding yet (this is normal, it may take a moment)"
    fi
done

echo ""
echo "✨ Setup complete!"
echo ""
echo "Services are running at:"
echo "  - Products API:  http://localhost:8001/docs"
echo "  - Orders API:    http://localhost:8002/docs"
echo "  - Payments API:  http://localhost:8003/docs"
echo "  - Events API:    http://localhost:8004/docs"
echo "  - Kafka UI:      http://localhost:8080"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo ""
echo "To test the event flow, run:"
echo "  python examples/test_event_flow.py"

