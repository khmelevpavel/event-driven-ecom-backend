from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItem] = Field(..., min_items=1)
    shipping_address: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    shipping_address: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]
    total_amount: float
    status: str
    shipping_address: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

