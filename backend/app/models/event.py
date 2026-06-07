from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class EventSource(str, enum.Enum):
    GOOGLE_CALENDAR = "google_calendar"
    MANUAL = "manual"
    CANVAS = "canvas"
    GMAIL = "gmail"
    NOTION = "notion"


class EventType(str, enum.Enum):
    CLASS = "class"
    EXAM = "exam"
    ASSIGNMENT = "assignment"
    MEETING = "meeting"
    SOCIAL = "social"
    GYM = "gym"
    MEAL = "meal"
    STUDY = "study"
    OTHER = "other"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Event details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    
    # Timing
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    all_day = Column(Boolean, default=False)
    
    # Classification
    event_type = Column(Enum(EventType), default=EventType.OTHER)
    source = Column(Enum(EventSource), default=EventSource.MANUAL)
    
    # Integration references
    external_id = Column(String, nullable=True)  # ID from external system
    calendar_id = Column(String, nullable=True)  # Calendar ID in external system
    
    # Scheduling metadata
    is_flexible = Column(Boolean, default=False)  # Can be rescheduled
    priority = Column(Integer, default=3)  # 1-5, 5 being highest
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="events")

