"""
Model provider schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ModelProviderBase(BaseModel):
    """Base model provider schema"""
    provider_type: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)


class ModelProviderCreate(ModelProviderBase):
    """Model provider creation schema"""
    api_endpoint: Optional[str] = Field(None, max_length=500)
    api_key: str = Field(..., max_length=500)
    config: Optional[Dict[str, Any]] = None
    is_default: bool = False


class ModelProviderUpdate(BaseModel):
    """Model provider update schema"""
    display_name: Optional[str] = Field(None, max_length=200)
    api_endpoint: Optional[str] = Field(None, max_length=500)
    api_key: Optional[str] = Field(None, max_length=500)
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class ModelProviderResponse(ModelProviderBase):
    """Model provider response schema"""
    id: int
    api_endpoint: Optional[str] = None
    is_active: bool
    is_default: bool
    health_status: Optional[str] = None
    last_health_check: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
