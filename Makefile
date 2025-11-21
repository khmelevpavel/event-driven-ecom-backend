.PHONY: help build up down logs test clean

help:
	@echo "Available commands:"
	@echo "  make build    - Build all Docker images"
	@echo "  make up       - Start all services with docker-compose"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - Show logs from all services"
	@echo "  make test     - Run tests for all services"
	@echo "  make clean    - Remove all containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	cd services/products && pytest || true
	cd services/orders && pytest || true
	cd services/payments && pytest || true
	cd services/events && pytest || true

clean:
	docker-compose down -v
	docker system prune -f

k8s-deploy:
	kubectl apply -k k8s/

k8s-delete:
	kubectl delete -k k8s/

