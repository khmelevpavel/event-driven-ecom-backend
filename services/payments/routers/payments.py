import logging
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from database import get_db, Payment, PaymentStatus
from models import PaymentCreate, PaymentResponse
from kafka_producer import kafka_producer
from shared.schemas.events import PaymentProcessedEvent, PaymentFailedEvent

logger = logging.getLogger(__name__)
router = APIRouter()


def process_payment_simulation(amount: float, payment_method: str) -> tuple[bool, str]:
    """
    Simulate payment processing.
    In production, this would integrate with payment gateways like Stripe, PayPal, etc.
    """
    # Simple simulation: fail if amount > 10000 or payment_method is "invalid"
    if payment_method.lower() == "invalid":
        return False, "Invalid payment method"
    if amount > 10000:
        return False, "Amount exceeds limit"
    return True, "Payment processed successfully"


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    """Create and process a payment."""
    # Generate transaction ID
    transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
    
    # Create payment record
    db_payment = Payment(
        order_id=payment.order_id,
        user_id=payment.user_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        status=PaymentStatus.PROCESSING,
        transaction_id=transaction_id
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # Process payment (simulation)
    success, message = process_payment_simulation(payment.amount, payment.payment_method)
    
    if success:
        db_payment.status = PaymentStatus.COMPLETED
        db.commit()
        db.refresh(db_payment)

        # Publish payment processed event
        event = PaymentProcessedEvent(
            payment_id=db_payment.id,
            order_id=db_payment.order_id,
            user_id=db_payment.user_id,
            amount=db_payment.amount,
            payment_method=db_payment.payment_method,
            transaction_id=db_payment.transaction_id,
            processed_at=datetime.utcnow()
        )
        kafka_producer.publish("payment.processed", event.dict(), key=str(db_payment.order_id))
        logger.info(f"Payment processed: {db_payment.id}")
    else:
        db_payment.status = PaymentStatus.FAILED
        db_payment.failure_reason = message
        db.commit()
        db.refresh(db_payment)

        # Publish payment failed event
        event = PaymentFailedEvent(
            payment_id=db_payment.id,
            order_id=db_payment.order_id,
            user_id=db_payment.user_id,
            amount=db_payment.amount,
            reason=message,
            failed_at=datetime.utcnow()
        )
        kafka_producer.publish("payment.failed", event.dict(), key=str(db_payment.order_id))
        logger.warning(f"Payment failed: {db_payment.id} - {message}")

    return db_payment


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    order_id: int = None,
    db: Session = Depends(get_db)
):
    """List all payments with optional filtering."""
    query = db.query(Payment)
    
    if user_id:
        query = query.filter(Payment.user_id == user_id)
    if order_id:
        query = query.filter(Payment.order_id == order_id)
    
    payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Get a payment by ID."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment


@router.get("/order/{order_id}", response_model=List[PaymentResponse])
async def get_payments_by_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Get all payments for an order."""
    payments = db.query(Payment).filter(Payment.order_id == order_id).all()
    return payments

