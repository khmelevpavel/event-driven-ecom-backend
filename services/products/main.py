import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from database import init_db
from routers import products, health
from kafka_consumer import start_consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting Products Service...")
    init_db()
    # Start Kafka consumer in background
    import threading
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    logger.info("Products Service started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Products Service...")


app = FastAPI(
    title="Products Service",
    description="Microservice for managing product catalog and inventory",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(health.router, prefix="/health", tags=["health"])


@app.get("/")
async def root():
    return {"service": "products", "status": "running"}

