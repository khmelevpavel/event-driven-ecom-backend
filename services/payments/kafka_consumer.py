import os
import sys
import logging
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from shared.kafka_client.consumer import KafkaConsumer
from shared.schemas.events import OrderCreatedEvent
from database import SessionLocal, Payment, PaymentStatus
from kafka_producer import kafka_producer
from shared.schemas.events import PaymentProcessedEvent, PaymentFailedEvent

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def process_payment_for_order(amount: float, payment_method: str = "credit_card") -> tuple[bool, str]:
    """Simulate payment processing."""
    if amount > 10000:
        return False, "Amount exceeds limit"
    return True, "Payment processed successfully"


def handle_order_created(event_data: dict):
    """Handle order.created event - automatically process payment."""
    try:
        event = OrderCreatedEvent(**event_data)
        db = SessionLocal()
        
        try:
            import uuid
            transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
            
            # Create payment record
            payment = Payment(
                order_id=event.order_id,
                user_id=event.user_id,
                amount=event.total_amount,
                payment_method="credit_card",  # Default payment method
                status=PaymentStatus.PROCESSING,
                transaction_id=transaction_id
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)

            # Process payment
            success, message = process_payment_for_order(event.total_amount)
            
            if success:
                payment.status = PaymentStatus.COMPLETED
                db.commit()
                db.refresh(payment)

                # Publish payment processed event
                payment_event = PaymentProcessedEvent(
                    payment_id=payment.id,
                    order_id=payment.order_id,
                    user_id=payment.user_id,
                    amount=payment.amount,
                    payment_method=payment.payment_method,
                    transaction_id=payment.transaction_id,
                    processed_at=datetime.utcnow()
                )
                kafka_producer.publish(
                    "payment.processed",
                    payment_event.dict(),
                    key=str(payment.order_id)
                )
                logger.info(f"Payment auto-processed for order {event.order_id}")
            else:
                payment.status = PaymentStatus.FAILED
                payment.failure_reason = message
                db.commit()
                db.refresh(payment)

                # Publish payment failed event
                payment_event = PaymentFailedEvent(
                    payment_id=payment.id,
                    order_id=payment.order_id,
                    user_id=payment.user_id,
                    amount=payment.amount,
                    reason=message,
                    failed_at=datetime.utcnow()
                )
                kafka_producer.publish(
                    "payment.failed",
                    payment_event.dict(),
                    key=str(payment.order_id)
                )
                logger.warning(f"Payment failed for order {event.order_id}: {message}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing payment: {e}")
            raise
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error handling order.created event: {e}")


def start_consumer():
    """Start Kafka consumer for payments service."""
    consumer = KafkaConsumer(
        topics=["order.created"],
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="payments-service-group"
    )
    logger.info("Starting Kafka consumer for payments service...")
    consumer.consume(handle_order_created)

