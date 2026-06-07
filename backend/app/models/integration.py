from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Integration details
    provider = Column(String, nullable=False)  # google, canvas, notion, gmail, health
    is_active = Column(Boolean, default=True)
    
    # OAuth tokens
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Provider-specific data
    provider_user_id = Column(String, nullable=True)
    provider_email = Column(String, nullable=True)
    
    # Configuration
    config = Column(JSON, nullable=True)  # Provider-specific settings
    
    # Sync metadata
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="integrations")

