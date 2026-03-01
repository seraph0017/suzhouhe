"""
Project schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enumeration"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    team_lead_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    team_lead_id: Optional[int] = None


class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: int
    status: ProjectStatus
    team_lead_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
