"""
Storyboard schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class StoryboardStatus(str, Enum):
    """Storyboard status enumeration"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    LOCKED = "locked"
    MATERIALS_GENERATED = "materials_generated"
    VIDEO_GENERATED = "video_generated"
    COMPLETED = "completed"


class StoryboardBase(BaseModel):
    """Base storyboard schema"""
    title: Optional[str] = Field(None, max_length=200)
    visual_description: str
    camera_direction: Optional[str] = None
    dialogue: Optional[str] = None
    duration_seconds: float = Field(default=5.0, ge=1)
    emotion: Optional[str] = Field(None, max_length=50)
    order: int = Field(..., ge=1)


class StoryboardCreate(StoryboardBase):
    """Storyboard creation schema"""
    chapter_id: int


class StoryboardUpdate(BaseModel):
    """Storyboard update schema"""
    title: Optional[str] = Field(None, max_length=200)
    visual_description: Optional[str] = None
    camera_direction: Optional[str] = None
    dialogue: Optional[str] = None
    duration_seconds: Optional[float] = Field(None, ge=1)
    emotion: Optional[str] = Field(None, max_length=50)
    order: Optional[int] = Field(None, ge=1)
    status: Optional[StoryboardStatus] = None
    selected_image_id: Optional[int] = None
    selected_audio_id: Optional[int] = None


class StoryboardResponse(StoryboardBase):
    """Storyboard response schema"""
    id: int
    chapter_id: int
    status: StoryboardStatus
    is_locked: bool
    selected_image_id: Optional[int] = None
    selected_audio_id: Optional[int] = None
    selected_video_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    locked_at: Optional[datetime] = None

    class Config:
        from_attributes = True
