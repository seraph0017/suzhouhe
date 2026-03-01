"""
Project Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class ProjectStatus(str, enum.Enum):
    """Project status enumeration"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectMemberRole(str, enum.Enum):
    """Project member role enumeration"""
    LEAD = "lead"
    MEMBER = "member"
    VIEWER = "viewer"


class Project(Base):
    """Project model for manga/video production"""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING)
    team_lead_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    team_lead = relationship("User", back_populates="projects_led", foreign_keys=[team_lead_id])
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    scripts = relationship("Script", back_populates="project", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="project", cascade="all, delete-orphan")


class ProjectMember(Base):
    """Project membership model"""

    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(ProjectMemberRole), default=ProjectMemberRole.MEMBER)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

    __table_args__ = (
        UniqueConstraint('project_id', 'user_id', name='unique_project_user'),
    )
