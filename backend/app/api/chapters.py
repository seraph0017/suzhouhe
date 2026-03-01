"""
Chapters API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.chapter import Chapter, ChapterStatus
from app.schemas.chapter import ChapterResponse, ChapterCreate, ChapterUpdate
from app.utils.security import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ChapterResponse])
async def list_chapters(
    script_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List chapters
    """
    query = db.query(Chapter)

    if script_id:
        query = query.filter(Chapter.script_id == script_id)

    chapters = query.order_by(Chapter.order).offset(skip).limit(limit).all()
    return chapters


@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get chapter by ID
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found",
        )
    return chapter


@router.post("/", response_model=ChapterResponse)
async def create_chapter(
    chapter_in: ChapterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new chapter
    """
    chapter = Chapter(
        script_id=chapter_in.script_id,
        title=chapter_in.title,
        content=chapter_in.content,
        summary=chapter_in.summary,
        order=chapter_in.order,
        status=ChapterStatus.DRAFT,
    )

    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    return chapter


@router.put("/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: int,
    chapter_in: ChapterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update chapter
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found",
        )

    update_data = chapter_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chapter, field, value)

    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    return chapter


@router.delete("/{chapter_id}")
async def delete_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete chapter
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found",
        )

    db.delete(chapter)
    db.commit()

    return {"message": "Chapter deleted successfully"}
