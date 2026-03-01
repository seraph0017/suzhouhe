"""
Storyboard Model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class StoryboardStatus(str, enum.Enum):
    """Storyboard status enumeration"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    LOCKED = "locked"
    MATERIALS_GENERATED = "materials_generated"
    VIDEO_GENERATED = "video_generated"
    COMPLETED = "completed"


class Storyboard(Base):
    """Storyboard model with shot directions"""

    __tablename__ = "storyboards"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    order = Column(Integer, nullable=False)
    title = Column(String(200))
    visual_description = Column(Text, nullable=False)
    camera_direction = Column(Text)
    dialogue = Column(Text)
    duration_seconds = Column(Float, default=5.0)
    emotion = Column(String(50))

    # Status tracking
    status = Column(SQLEnum(StoryboardStatus), default=StoryboardStatus.DRAFT)
    is_locked = Column(Boolean, default=False)

    # Asset references
    selected_image_id = Column(Integer, ForeignKey("assets.id"))
    selected_audio_id = Column(Integer, ForeignKey("assets.id"))
    selected_video_id = Column(Integer, ForeignKey("assets.id"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    locked_at = Column(DateTime(timezone=True))

    # Relationships
    chapter = relationship("Chapter", back_populates="storyboards")
    selected_image = relationship("Asset", foreign_keys=[selected_image_id])
    selected_audio = relationship("Asset", foreign_keys=[selected_audio_id])
    selected_video = relationship("Asset", foreign_keys=[selected_video_id])

    # Generated assets (multiple images per storyboard for selection)
    generated_images = relationship("Asset", back_populates="storyboard", foreign_keys="Asset.storyboard_id")

    def __repr__(self):
        return f"<Storyboard(id={self.id}, order={self.order}, title={self.title})>"
