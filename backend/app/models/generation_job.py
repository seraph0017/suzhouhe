"""
Generation Job Model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class JobStatus(str, enum.Enum):
    """Generation job status enumeration"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    """Generation job type enumeration"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    BGM = "bgm"
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    COMPOSE = "compose"
    EXPORT = "export"


class GenerationJob(Base):
    """Generation job model for async task tracking"""

    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    storyboard_id = Column(Integer, ForeignKey("storyboards.id"))
    chapter_id = Column(Integer, ForeignKey("chapters.id"))

    job_type = Column(SQLEnum(JobType), nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.QUEUED)

    # Model provider used
    model_config_id = Column(Integer, ForeignKey("model_providers.id"))

    # Request and result data
    request_params = Column(JSON, default=dict)
    result_data = Column(JSON)
    error_message = Column(Text)

    # Progress tracking
    progress = Column(Integer, default=0)  # 0-100
    retry_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    project = relationship("Project")
    storyboard = relationship("Storyboard")
    chapter = relationship("Chapter")
    model_config = relationship("ModelProvider")

    def __repr__(self):
        return f"<GenerationJob(id={self.id}, type={self.job_type}, status={self.status})>"
