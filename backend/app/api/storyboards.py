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
from app.services.ai_service import AIService

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


@router.post("/generate", response_model=List[StoryboardResponse])
async def generate_storyboards(
    chapter_id: int,
    style: str = "anime_jp",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate storyboards from chapter using AI
    """
    # Get chapter to get script content
    from app.models.chapter import Chapter

    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found",
        )

    # Get script content
    script = chapter.script
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )

    # Use AI service to generate storyboards from chapter content
    ai_service = AIService(db)

    # Generate storyboard prompts from chapter content
    chapter_content = chapter.content or chapter.title
    prompt = f"""
    根据以下章节内容生成 {5} 个分镜描述：

    章节标题：{chapter.title}
    章节内容：{chapter_content}
    风格：{style}

    请为每个分镜提供：
    1. 画面描述（visual_description）
    2. 镜头语言（camera_direction）
    3. 角色台词（dialogue）
    4. 情绪基调（emotion）
    5. 建议时长（duration_seconds）

    以 JSON 格式返回，包含 order, visual_description, camera_direction, dialogue, emotion, duration_seconds 字段
    """

    result = await ai_service.generate_text(
        prompt=prompt,
        system_prompt="你是一个专业的分镜师，擅长根据剧本内容生成分镜描述。",
        max_tokens=2048,
    )

    if not result.success or not result.data:
        # Fallback: create mock storyboards
        storyboards = []
        for i in range(5):
            storyboard = Storyboard(
                chapter_id=chapter_id,
                visual_description=f"分镜{i + 1}的画面描述",
                camera_direction="中景，固定镜头",
                dialogue=f"台词{i + 1}",
                duration_seconds=5.0,
                emotion="calm",
                order=i + 1,
                status=StoryboardStatus.DRAFT,
            )
            db.add(storyboard)
        db.commit()
        return db.query(Storyboard).filter(Storyboard.chapter_id == chapter_id).all()

    # Parse AI response and create storyboards
    import json
    try:
        storyboard_data = json.loads(result.data.get("text", "[]"))
        storyboards = []

        for i, data in enumerate(storyboard_data):
            storyboard = Storyboard(
                chapter_id=chapter_id,
                visual_description=data.get("visual_description", ""),
                camera_direction=data.get("camera_direction", ""),
                dialogue=data.get("dialogue", ""),
                duration_seconds=data.get("duration_seconds", 5.0),
                emotion=data.get("emotion", ""),
                order=data.get("order", i + 1),
                status=StoryboardStatus.DRAFT,
            )
            db.add(storyboard)
            storyboards.append(storyboard)

        db.commit()
        return storyboards
    except Exception as e:
        # Fallback on parse error
        storyboards = []
        for i in range(5):
            storyboard = Storyboard(
                chapter_id=chapter_id,
                visual_description=f"分镜{i + 1}的画面描述",
                camera_direction="中景，固定镜头",
                dialogue=f"台词{i + 1}",
                duration_seconds=5.0,
                emotion="calm",
                order=i + 1,
                status=StoryboardStatus.DRAFT,
            )
            db.add(storyboard)
        db.commit()
        return db.query(Storyboard).filter(Storyboard.chapter_id == chapter_id).all()


@router.post("/{storyboard_id}/generate-image", response_model=dict)
async def generate_storyboard_image(
    storyboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate image for storyboard
    """
    storyboard = db.query(Storyboard).filter(Storyboard.id == storyboard_id).first()
    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found",
        )

    # Use AI service to generate image
    ai_service = AIService(db)

    # Build image prompt from storyboard description
    image_prompt = f"{storyboard.visual_description}"
    if storyboard.camera_direction:
        image_prompt += f", {storyboard.camera_direction}"
    if storyboard.emotion:
        image_prompt += f", {storyboard.emotion} emotion"

    result = await ai_service.generate_images(
        prompt=image_prompt,
        count=1,
        width=1024,
        height=1024,
        save_to_storage=True,
    )

    if not result.success or not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="图片生成失败",
        )

    # Create asset record for generated image
    from app.models.asset import Asset, AssetType

    image_data = result.data[0] if isinstance(result.data, list) else result.data
    asset = Asset(
        asset_type=AssetType.IMAGE,
        url=image_data.get("url", ""),
        object_name=image_data.get("object_name", ""),
        metadata={
            "width": image_data.get("width", 1024),
            "height": image_data.get("height", 1024),
            "storyboard_id": storyboard_id,
        },
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    # Associate asset with storyboard
    storyboard.selected_image_id = asset.id
    db.add(storyboard)
    db.commit()

    return {
        "id": asset.id,
        "url": asset.url,
        "type": "image",
    }
