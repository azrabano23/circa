from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class HealthData(Base):
    __tablename__ = "health_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Date of the data
    date = Column(Date, nullable=False, index=True)
    
    # Activity metrics
    steps = Column(Integer, nullable=True)
    active_minutes = Column(Integer, nullable=True)
    calories_burned = Column(Float, nullable=True)
    
    # Sleep metrics
    sleep_hours = Column(Float, nullable=True)
    sleep_quality = Column(Float, nullable=True)  # 0-100 score
    deep_sleep_minutes = Column(Integer, nullable=True)
    
    # Heart rate
    resting_heart_rate = Column(Integer, nullable=True)
    avg_heart_rate = Column(Integer, nullable=True)
    
    # Stress and recovery
    stress_level = Column(Float, nullable=True)  # 0-100
    recovery_score = Column(Float, nullable=True)  # 0-100
    
    # Exercise
    workout_duration = Column(Integer, nullable=True)  # minutes
    workout_type = Column(String, nullable=True)
    
    # Source
    data_source = Column(String, nullable=True)  # apple_health, google_fit, manual
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="health_data")

