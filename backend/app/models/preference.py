from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Time, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Circadian rhythm preferences
    wake_time = Column(Time, nullable=True)
    sleep_time = Column(Time, nullable=True)
    peak_focus_time = Column(String, nullable=True)  # morning, afternoon, evening
    
    # Study preferences
    study_session_duration = Column(Integer, default=50)  # minutes
    break_duration = Column(Integer, default=10)  # minutes
    preferred_study_times = Column(JSON, nullable=True)  # Array of time ranges
    
    # Fitness preferences
    gym_frequency = Column(Integer, default=3)  # times per week
    preferred_workout_time = Column(String, nullable=True)
    workout_duration = Column(Integer, default=60)  # minutes
    
    # Diet preferences
    meal_times = Column(JSON, nullable=True)  # breakfast, lunch, dinner times
    dietary_restrictions = Column(JSON, nullable=True)
    
    # Social preferences
    social_battery_level = Column(Integer, default=5)  # 1-10 scale
    preferred_social_times = Column(JSON, nullable=True)
    
    # Work/study habits
    procrastination_tendency = Column(Integer, default=5)  # 1-10 scale
    multitasking_preference = Column(Boolean, default=False)
    notification_preference = Column(String, default="moderate")  # low, moderate, high
    
    # Scheduling preferences
    buffer_time = Column(Integer, default=15)  # minutes between events
    auto_reschedule = Column(Boolean, default=True)
    flexibility_level = Column(Integer, default=5)  # 1-10, how flexible is the schedule
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")

