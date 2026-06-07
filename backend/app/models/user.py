from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # OAuth fields
    google_id = Column(String, unique=True, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    health_data = relationship("HealthData", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    quiz_responses = relationship("QuizResponse", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")

