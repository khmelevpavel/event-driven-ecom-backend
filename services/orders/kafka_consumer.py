import os
import sys
import logging
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from shared.kafka_client.consumer import KafkaConsumer
from shared.schemas.events import PaymentProcessedEvent, PaymentFailedEvent
from database import SessionLocal, Order, OrderStatus

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def handle_payment_processed(event_data: dict):
    """Handle payment.processed event - update order status."""
    try:
        event = PaymentProcessedEvent(**event_data)
        db = SessionLocal()
        
        try:
            order = db.query(Order).filter(Order.id == event.order_id).first()
            if order:
                order.status = OrderStatus.CONFIRMED
                order.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Order {order.id} confirmed after payment")
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating order status: {e}")
            raise
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error handling payment.processed event: {e}")


def handle_payment_failed(event_data: dict):
    """Handle payment.failed event - update order status."""
    try:
        event = PaymentFailedEvent(**event_data)
        db = SessionLocal()
        
        try:
            order = db.query(Order).filter(Order.id == event.order_id).first()
            if order:
                order.status = OrderStatus.CANCELLED
                order.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Order {order.id} cancelled due to payment failure")
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating order status: {e}")
            raise
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error handling payment.failed event: {e}")


def start_consumer():
    """Start Kafka consumer for orders service."""
    consumer = KafkaConsumer(
        topics=["payment.processed", "payment.failed"],
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="orders-service-group"
    )
    logger.info("Starting Kafka consumer for orders service...")
    
    def message_handler(event_data: dict):
        # Determine event type and route to appropriate handler
        if "transaction_id" in event_data:
            handle_payment_processed(event_data)
        elif "reason" in event_data and "failed_at" in event_data:
            handle_payment_failed(event_data)
    
    consumer.consume(message_handler)

