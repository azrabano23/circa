from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.event import EventSource, EventType


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    event_type: EventType = EventType.OTHER
    is_flexible: bool = False
    priority: int = 3


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    event_type: Optional[EventType] = None
    is_flexible: Optional[bool] = None
    priority: Optional[int] = None


class EventResponse(EventBase):
    id: int
    user_id: int
    source: EventSource
    external_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

