"""
Storyboards API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.storyboard import Storyboard, StoryboardStatus
from app.schemas.storyboard import StoryboardResponse, StoryboardCreate, StoryboardUpdate
from app.utils.security import get_current_user

router = APIRouter()


@router.get("/", response_model=List[StoryboardResponse])
async def list_storyboards(
    chapter_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List storyboards
    """
    query = db.query(Storyboard)

    if chapter_id:
        query = query.filter(Storyboard.chapter_id == chapter_id)

    storyboards = query.order_by(Storyboard.order).offset(skip).limit(limit).all()
    return storyboards


@router.get("/{storyboard_id}", response_model=StoryboardResponse)
async def get_storyboard(
    storyboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get storyboard by ID
    """
    storyboard = db.query(Storyboard).filter(Storyboard.id == storyboard_id).first()
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )
    return storyboard


@router.post("/", response_model=StoryboardResponse)
async def create_storyboard(
    storyboard_in: StoryboardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new storyboard
    """
    storyboard = Storyboard(
        chapter_id=storyboard_in.chapter_id,
        title=storyboard_in.title,
        visual_description=storyboard_in.visual_description,
        camera_direction=storyboard_in.camera_direction,
        dialogue=storyboard_in.dialogue,
        duration_seconds=storyboard_in.duration_seconds,
        emotion=storyboard_in.emotion,
        order=storyboard_in.order,
        status=StoryboardStatus.DRAFT,
    )

    db.add(storyboard)
    db.commit()
    db.refresh(storyboard)

    return storyboard


@router.put("/{storyboard_id}", response_model=StoryboardResponse)
async def update_storyboard(
    storyboard_id: int,
    storyboard_in: StoryboardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update storyboard
    """
    storyboard = db.query(Storyboard).filter(Storyboard.id == storyboard_id).first()
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )

    update_data = storyboard_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(storyboard, field, value)

    db.add(storyboard)
    db.commit()
    db.refresh(storyboard)

    return storyboard


@router.post("/{storyboard_id}/lock", response_model=StoryboardResponse)
async def lock_storyboard(
    storyboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lock storyboard
    """
    storyboard = db.query(Storyboard).filter(Storyboard.id == storyboard_id).first()
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )

    storyboard.is_locked = True
    storyboard.locked_at = datetime.utcnow()
    storyboard.status = StoryboardStatus.LOCKED

    db.add(storyboard)
    db.commit()
    db.refresh(storyboard)

    return storyboard


@router.delete("/{storyboard_id}")
async def delete_storyboard(
    storyboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete storyboard
    """
    storyboard = db.query(Storyboard).filter(Storyboard.id == storyboard_id).first()
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )

    db.delete(storyboard)
    db.commit()

    return {"message": "Storyboard deleted successfully"}
