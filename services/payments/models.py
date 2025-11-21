from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PaymentCreate(BaseModel):
    order_id: int
    user_id: int
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., min_length=1)


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    amount: float
    payment_method: str
    status: str
    transaction_id: Optional[str]
    failure_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

