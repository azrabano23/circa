from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Task details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Scheduling
    due_date = Column(DateTime(timezone=True), nullable=True)
    scheduled_start = Column(DateTime(timezone=True), nullable=True)
    scheduled_end = Column(DateTime(timezone=True), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # minutes
    
    # Status and priority
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # Source tracking
    source = Column(String, nullable=True)  # e.g., "canvas", "gmail", "manual"
    external_id = Column(String, nullable=True)
    
    # AI metadata
    ai_extracted = Column(Boolean, default=False)  # Was this extracted by AI?
    difficulty_score = Column(Float, nullable=True)  # AI-estimated difficulty (0-1)
    optimal_time_of_day = Column(String, nullable=True)  # morning, afternoon, evening, night
    
    # Completion tracking
    completed_at = Column(DateTime(timezone=True), nullable=True)
    actual_duration = Column(Integer, nullable=True)  # minutes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tasks")

