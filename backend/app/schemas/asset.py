"""
Asset schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    """Asset type enumeration"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    OTHER = "other"


class AssetStatus(str, Enum):
    """Asset status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class AssetBase(BaseModel):
    """Base asset schema"""
    type: AssetType
    file_name: str = Field(..., max_length=255)
    file_path: str = Field(..., max_length=500)


class AssetCreate(AssetBase):
    """Asset creation schema"""
    project_id: int
    storyboard_id: Optional[int] = None
    mime_type: Optional[str] = Field(None, max_length=100)
    file_size: Optional[int] = None
    url: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None


class AssetUpdate(BaseModel):
    """Asset update schema"""
    status: Optional[AssetStatus] = None
    file_path: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None


class AssetResponse(AssetBase):
    """Asset response schema"""
    id: int
    project_id: int
    storyboard_id: Optional[int] = None
    status: AssetStatus
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
