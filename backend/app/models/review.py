"""
Review Model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class ReviewType(str, enum.Enum):
    """Review type enumeration"""
    FIRST_AUDIT = "first_audit"
    SECOND_AUDIT = "second_audit"
    SCRIPT_REVIEW = "script_review"
    STORYBOARD_REVIEW = "storyboard_review"


class ReviewStatus(str, enum.Enum):
    """Review status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class Review(Base):
    """Review model for audit workflow"""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    review_type = Column(SQLEnum(ReviewType), nullable=False)
    target_type = Column(String(50), nullable=False)  # script, storyboard, chapter_video
    target_id = Column(Integer, nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.PENDING)
    feedback = Column(Text)
    rejection_reason = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))

    # Relationships
    reviewer = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, type={self.review_type}, status={self.status})>"
