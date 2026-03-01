"""
Chapter schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ChapterStatus(str, Enum):
    """Chapter status enumeration"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ChapterBase(BaseModel):
    """Base chapter schema"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    summary: Optional[str] = None
    order: int = Field(..., ge=1)


class ChapterCreate(ChapterBase):
    """Chapter creation schema"""
    script_id: int


class ChapterUpdate(BaseModel):
    """Chapter update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    summary: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    status: Optional[ChapterStatus] = None


class ChapterResponse(ChapterBase):
    """Chapter response schema"""
    id: int
    script_id: int
    status: ChapterStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
