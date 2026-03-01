"""
Script Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class ScriptStatus(str, enum.Enum):
    """Script status enumeration"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    LOCKED = "locked"
    ARCHIVED = "archived"


class Script(Base):
    """Script model for manga/video content"""

    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    version = Column(Integer, default=1)
    status = Column(SQLEnum(ScriptStatus), default=ScriptStatus.DRAFT)
    is_locked = Column(Boolean, default=False)
    locked_at = Column(DateTime(timezone=True))
    locked_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="scripts")
    versions = relationship("ScriptVersion", back_populates="script", cascade="all, delete-orphan", order_by="ScriptVersion.version")
    chapters = relationship("Chapter", back_populates="script", cascade="all, delete-orphan", order_by="Chapter.order")
    lock_user = relationship("User", foreign_keys=[locked_by])


class ScriptVersion(Base):
    """Script version history model"""

    __tablename__ = "script_versions"

    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    change_description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    script = relationship("Script", back_populates="versions")
    creator = relationship("User")
