import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from database import get_db, Order, OrderStatus
from models import OrderCreate, OrderUpdate, OrderResponse
from kafka_producer import kafka_producer
from shared.schemas.events import OrderCreatedEvent, OrderCancelledEvent

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    """Create a new order."""
    # Calculate total amount
    total_amount = sum(item.price * item.quantity for item in order.items)
    
    # Create order
    db_order = Order(
        user_id=order.user_id,
        items=[item.dict() for item in order.items],
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        shipping_address=order.shipping_address
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Publish order created event
    event = OrderCreatedEvent(
        order_id=db_order.id,
        user_id=db_order.user_id,
        items=order.items,
        total_amount=total_amount,
        created_at=datetime.utcnow()
    )
    kafka_producer.publish("order.created", event.dict(), key=str(db_order.id))

    logger.info(f"Order created: {db_order.id}")
    return db_order


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """List all orders with optional filtering."""
    query = db.query(Order)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Get an order by ID."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db)
):
    """Update an order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status":
            setattr(order, field, OrderStatus(value))
        else:
            setattr(order, field, value)
    
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

    logger.info(f"Order updated: {order_id}")
    return order


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    reason: str = "Customer request",
    db: Session = Depends(get_db)
):
    """Cancel an order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is already cancelled"
        )
    
    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

    # Publish order cancelled event
    event = OrderCancelledEvent(
        order_id=order.id,
        user_id=order.user_id,
        reason=reason,
        cancelled_at=datetime.utcnow()
    )
    kafka_producer.publish("order.cancelled", event.dict(), key=str(order.id))

    logger.info(f"Order cancelled: {order_id}")
    return order

