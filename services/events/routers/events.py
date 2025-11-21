import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db, EventLog, Notification
from models import EventLogResponse, NotificationResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/logs", response_model=List[EventLogResponse])
async def list_event_logs(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    user_id: Optional[int] = None,
    order_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all event logs with optional filtering."""
    query = db.query(EventLog)
    
    if event_type:
        query = query.filter(EventLog.event_type == event_type)
    if user_id:
        query = query.filter(EventLog.user_id == user_id)
    if order_id:
        query = query.filter(EventLog.order_id == order_id)
    
    events = query.order_by(desc(EventLog.created_at)).offset(skip).limit(limit).all()
    return events


@router.get("/logs/{event_id}", response_model=EventLogResponse)
async def get_event_log(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get an event log by ID."""
    event = db.query(EventLog).filter(EventLog.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event log not found"
        )
    return event


@router.get("/notifications", response_model=List[NotificationResponse])
async def list_notifications(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """List notifications for a user."""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter(Notification.is_read == 0)
    
    notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
    return notifications


@router.post("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = 1
    db.commit()
    db.refresh(notification)
    
    return notification

