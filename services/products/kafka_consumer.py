import os
import sys
import logging
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from shared.kafka_client.consumer import KafkaConsumer
from shared.schemas.events import OrderCreatedEvent, InventoryUpdatedEvent
from database import SessionLocal, Product

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def handle_order_created(event_data: dict):
    """Handle order.created event - update inventory."""
    try:
        event = OrderCreatedEvent(**event_data)
        db = SessionLocal()
        
        try:
            for item in event.items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    old_stock = product.stock
                    product.stock -= item.quantity
                    if product.stock < 0:
                        product.stock = 0
                        logger.warning(
                            f"Product {product.id} stock went negative, set to 0"
                        )
                    
                    product.updated_at = datetime.utcnow()
                    
                    # Publish inventory update event
                    from kafka_producer import kafka_producer
                    inventory_event = InventoryUpdatedEvent(
                        product_id=product.id,
                        quantity_change=product.stock - old_stock,
                        new_stock=product.stock,
                        updated_at=datetime.utcnow()
                    )
                    kafka_producer.publish(
                        "inventory.updated",
                        inventory_event.dict(),
                        key=str(product.id)
                    )
                    
                    logger.info(
                        f"Inventory updated for product {product.id}: "
                        f"{old_stock} -> {product.stock}"
                    )
            
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating inventory: {e}")
            raise
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error handling order.created event: {e}")


def start_consumer():
    """Start Kafka consumer for products service."""
    consumer = KafkaConsumer(
        topics=["order.created"],
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="products-service-group"
    )
    logger.info("Starting Kafka consumer for products service...")
    consumer.consume(handle_order_created)

