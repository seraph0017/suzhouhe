"""
Model Provider Configuration Model
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func

from app.database import Base


class ModelProvider(Base):
    """Model provider configuration for hot-swappable AI models"""

    __tablename__ = "model_providers"

    id = Column(Integer, primary_key=True, index=True)

    # Provider type: llm, image, video, tts
    provider_type = Column(String(50), nullable=False)

    # Provider name: openai, anthropic, midjourney, elevenlabs, etc.
    name = Column(String(100), nullable=False)

    # Display name
    display_name = Column(String(200))

    # API Configuration
    api_endpoint = Column(String(500))
    api_key = Column(String(500), nullable=False)

    # Additional configuration (stored as JSON)
    config = Column(JSON, default=dict)

    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    # Health check
    last_health_check = Column(DateTime(timezone=True))
    health_status = Column(String(50))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ModelProvider(id={self.id}, name={self.name}, type={self.provider_type})>"
