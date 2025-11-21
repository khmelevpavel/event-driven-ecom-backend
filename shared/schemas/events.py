from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderCreatedEvent(BaseModel):
    order_id: int
    user_id: int
    items: List[OrderItem]
    total_amount: float
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": 1,
                "user_id": 123,
                "items": [
                    {"product_id": 1, "quantity": 2, "price": 29.99}
                ],
                "total_amount": 59.98,
                "created_at": "2024-01-01T12:00:00"
            }
        }


class OrderCancelledEvent(BaseModel):
    order_id: int
    user_id: int
    reason: str
    cancelled_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": 1,
                "user_id": 123,
                "reason": "Customer request",
                "cancelled_at": "2024-01-01T12:00:00"
            }
        }


class PaymentProcessedEvent(BaseModel):
    payment_id: int
    order_id: int
    user_id: int
    amount: float
    payment_method: str
    transaction_id: str
    processed_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": 1,
                "order_id": 1,
                "user_id": 123,
                "amount": 59.98,
                "payment_method": "credit_card",
                "transaction_id": "txn_123456",
                "processed_at": "2024-01-01T12:00:00"
            }
        }


class PaymentFailedEvent(BaseModel):
    payment_id: int
    order_id: int
    user_id: int
    amount: float
    reason: str
    failed_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": 1,
                "order_id": 1,
                "user_id": 123,
                "amount": 59.98,
                "reason": "Insufficient funds",
                "failed_at": "2024-01-01T12:00:00"
            }
        }


class InventoryUpdatedEvent(BaseModel):
    product_id: int
    quantity_change: int
    new_stock: int
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "quantity_change": -2,
                "new_stock": 98,
                "updated_at": "2024-01-01T12:00:00"
            }
        }


class ProductCreatedEvent(BaseModel):
    product_id: int
    name: str
    price: float
    stock: int
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "name": "Laptop",
                "price": 999.99,
                "stock": 100,
                "created_at": "2024-01-01T12:00:00"
            }
        }

