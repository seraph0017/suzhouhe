"""
Asset Model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class AssetType(str, enum.Enum):
    """Asset type enumeration"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    OTHER = "other"


class AssetStatus(str, enum.Enum):
    """Asset status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Asset(Base):
    """Asset model for generated media files"""

    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    storyboard_id = Column(Integer, ForeignKey("storyboards.id"))
    type = Column(SQLEnum(AssetType), nullable=False)
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.PENDING)

    # Storage
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    url = Column(String(500))

    # Metadata (stored as JSON)
    metadata_ = Column("metadata", JSON, default=dict)

    # Generation info
    provider = Column(String(100))
    model_name = Column(String(100))
    generation_params = Column(JSON)

    # Processing
    duration_seconds = Column(Float)
    width = Column(Integer)
    height = Column(Integer)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project")
    storyboard = relationship("Storyboard", back_populates="generated_images", foreign_keys=[storyboard_id])

    def __repr__(self):
        return f"<Asset(id={self.id}, type={self.type}, file_name={self.file_name})>"
