from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class QuizResponse(Base):
    __tablename__ = "quiz_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Quiz metadata
    quiz_type = Column(String, nullable=False)  # onboarding, periodic, adaptive
    quiz_version = Column(String, nullable=True)
    
    # Questions and responses
    questions = Column(JSON, nullable=False)  # Array of questions
    answers = Column(JSON, nullable=False)  # Array of user answers
    
    # Analysis
    insights = Column(JSON, nullable=True)  # AI-generated insights
    recommendations = Column(Text, nullable=True)
    
    # Completion
    completed = Column(Integer, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="quiz_responses")

