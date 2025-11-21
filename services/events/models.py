from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class EventLogResponse(BaseModel):
    id: int
    event_type: str
    event_data: Dict[str, Any]
    user_id: Optional[int]
    order_id: Optional[int]
    product_id: Optional[int]
    payment_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    event_type: str
    message: str
    is_read: int
    created_at: datetime

    class Config:
        from_attributes = True

