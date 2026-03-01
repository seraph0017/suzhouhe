"""
Review schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ReviewType(str, Enum):
    """Review type enumeration"""
    FIRST_AUDIT = "first_audit"
    SECOND_AUDIT = "second_audit"
    SCRIPT_REVIEW = "script_review"
    STORYBOARD_REVIEW = "storyboard_review"


class ReviewStatus(str, Enum):
    """Review status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class ReviewBase(BaseModel):
    """Base review schema"""
    review_type: ReviewType
    target_type: str
    target_id: int


class ReviewCreate(ReviewBase):
    """Review creation schema"""
    reviewer_id: int
    feedback: Optional[str] = None


class ReviewUpdate(BaseModel):
    """Review update schema"""
    status: Optional[ReviewStatus] = None
    feedback: Optional[str] = None
    rejection_reason: Optional[str] = None


class ReviewResponse(ReviewBase):
    """Review response schema"""
    id: int
    reviewer_id: int
    status: ReviewStatus
    feedback: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
