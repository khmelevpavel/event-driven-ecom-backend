import os
import sys
import logging
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from shared.kafka_client.consumer import KafkaConsumer
from shared.schemas.events import (
    OrderCreatedEvent,
    OrderCancelledEvent,
    PaymentProcessedEvent,
    PaymentFailedEvent,
    InventoryUpdatedEvent,
    ProductCreatedEvent
)
from database import SessionLocal, EventLog, Notification

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def create_notification(user_id: int, event_type: str, message: str, db):
    """Create a notification for a user."""
    notification = Notification(
        user_id=user_id,
        event_type=event_type,
        message=message
    )
    db.add(notification)
    return notification


def handle_event(event_type: str, event_data: dict):
    """Handle any event - log it and create notifications."""
    try:
        db = SessionLocal()
        
        try:
            # Extract IDs from event data
            user_id = event_data.get("user_id")
            order_id = event_data.get("order_id")
            product_id = event_data.get("product_id")
            payment_id = event_data.get("payment_id") or event_data.get("payment_id")
            
            # Log the event
            event_log = EventLog(
                event_type=event_type,
                event_data=event_data,
                user_id=user_id,
                order_id=order_id,
                product_id=product_id,
                payment_id=payment_id
            )
            db.add(event_log)
            
            # Create notifications based on event type
            if event_type == "order.created":
                event = OrderCreatedEvent(**event_data)
                message = f"Order #{event.order_id} has been created. Total: ${event.total_amount:.2f}"
                create_notification(event.user_id, event_type, message, db)
            
            elif event_type == "order.cancelled":
                event = OrderCancelledEvent(**event_data)
                message = f"Order #{event.order_id} has been cancelled. Reason: {event.reason}"
                create_notification(event.user_id, event_type, message, db)
            
            elif event_type == "payment.processed":
                event = PaymentProcessedEvent(**event_data)
                message = f"Payment for order #{event.order_id} has been processed successfully. Amount: ${event.amount:.2f}"
                create_notification(event.user_id, event_type, message, db)
            
            elif event_type == "payment.failed":
                event = PaymentFailedEvent(**event_data)
                message = f"Payment for order #{event.order_id} failed. Reason: {event.reason}"
                create_notification(event.user_id, event_type, message, db)
            
            elif event_type == "product.created":
                event = ProductCreatedEvent(**event_data)
                message = f"New product '{event.name}' has been added to the catalog"
                # No specific user_id for product creation, skip notification
            
            elif event_type == "inventory.updated":
                event = InventoryUpdatedEvent(**event_data)
                if event.new_stock < 10:
                    message = f"Low stock alert: Product #{event.product_id} has only {event.new_stock} units left"
                    # Would need to get product owner/admin user_id in real scenario
                    # For now, skip notification
            
            db.commit()
            logger.info(f"Event logged and processed: {event_type}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing event {event_type}: {e}")
            raise
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error handling event {event_type}: {e}")


def start_consumer():
    """Start Kafka consumer for events service."""
    topics = [
        "order.created",
        "order.cancelled",
        "payment.processed",
        "payment.failed",
        "inventory.updated",
        "product.created"
    ]
    
    consumer = KafkaConsumer(
        topics=topics,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="events-service-group"
    )
    logger.info("Starting Kafka consumer for events service...")
    
    def message_handler(event_data: dict):
        # Determine event type from topic (would need topic info in real implementation)
        # For now, infer from event data structure
        if "order_id" in event_data and "items" in event_data:
            handle_event("order.created", event_data)
        elif "order_id" in event_data and "reason" in event_data and "cancelled_at" in event_data:
            handle_event("order.cancelled", event_data)
        elif "transaction_id" in event_data:
            handle_event("payment.processed", event_data)
        elif "reason" in event_data and "failed_at" in event_data:
            handle_event("payment.failed", event_data)
        elif "product_id" in event_data and "new_stock" in event_data:
            handle_event("inventory.updated", event_data)
        elif "product_id" in event_data and "name" in event_data and "created_at" in event_data:
            handle_event("product.created", event_data)
        else:
            logger.warning(f"Unknown event type: {event_data}")
    
    consumer.consume(message_handler)

