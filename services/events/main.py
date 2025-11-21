import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from database import init_db
from routers import events, health
from kafka_consumer import start_consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting Events Service...")
    init_db()
    # Start Kafka consumer in background
    import threading
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    logger.info("Events Service started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Events Service...")


app = FastAPI(
    title="Events Service",
    description="Microservice for event logging and notifications",
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

app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(health.router, prefix="/health", tags=["health"])


@app.get("/")
async def root():
    return {"service": "events", "status": "running"}

