"""
Script schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ScriptStatus(str, Enum):
    """Script status enumeration"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    LOCKED = "locked"
    ARCHIVED = "archived"


class ScriptBase(BaseModel):
    """Base script schema"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    summary: Optional[str] = None


class ScriptCreate(ScriptBase):
    """Script creation schema"""
    project_id: int


class ScriptUpdate(BaseModel):
    """Script update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[ScriptStatus] = None


class ScriptResponse(ScriptBase):
    """Script response schema"""
    id: int
    project_id: int
    version: int
    status: ScriptStatus
    is_locked: bool
    locked_at: Optional[datetime] = None
    locked_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
