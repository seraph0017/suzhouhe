"""
Reviews API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.review import Review, ReviewType, ReviewStatus
from app.schemas.review import ReviewResponse, ReviewCreate, ReviewUpdate
from app.utils.security import get_current_user

router = APIRouter()


@router.get("/pending", response_model=List[ReviewResponse])
async def list_pending_reviews(
    type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List pending reviews
    """
    query = db.query(Review).filter(Review.status == ReviewStatus.PENDING)

    if type:
        review_type = ReviewType.FIRST_AUDIT if type == "first" else ReviewType.SECOND_AUDIT
        query = query.filter(Review.review_type == review_type)

    reviews = query.all()
    return reviews


@router.post("/first", response_model=ReviewResponse)
async def submit_first_audit(
    target_type: str,
    target_id: int,
    feedback: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit first audit (by team member)
    """
    review = Review(
        review_type=ReviewType.FIRST_AUDIT,
        target_type=target_type,
        target_id=target_id,
        reviewer_id=current_user.id,
        status=ReviewStatus.PENDING,
        feedback=feedback,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.post("/second", response_model=ReviewResponse)
async def submit_second_audit(
    target_type: str,
    target_id: int,
    feedback: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit second audit (by team lead)
    """
    review = Review(
        review_type=ReviewType.SECOND_AUDIT,
        target_type=target_type,
        target_id=target_id,
        reviewer_id=current_user.id,
        status=ReviewStatus.PENDING,
        feedback=feedback,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.post("/{review_id}/approve", response_model=ReviewResponse)
async def approve_review(
    review_id: int,
    feedback: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Approve review
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    review.status = ReviewStatus.APPROVED
    review.feedback = feedback
    review.reviewed_at = datetime.utcnow()

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.post("/{review_id}/reject", response_model=ReviewResponse)
async def reject_review(
    review_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reject review
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    review.status = ReviewStatus.REJECTED
    review.rejection_reason = reason
    review.reviewed_at = datetime.utcnow()

    db.add(review)
    db.commit()
    db.refresh(review)

    return review
