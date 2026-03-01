"""
Chapter Model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class ChapterStatus(str, enum.Enum):
    """Chapter status enumeration"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Chapter(Base):
    """Chapter model for script breakdown"""

    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=False)
    order = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    status = Column(SQLEnum(ChapterStatus), default=ChapterStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    script = relationship("Script", back_populates="chapters")
    storyboards = relationship("Storyboard", back_populates="chapter", cascade="all, delete-orphan", order_by="Storyboard.order")

    def __repr__(self):
        return f"<Chapter(id={self.id}, title={self.title}, order={self.order})>"
