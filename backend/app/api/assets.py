"""
Assets API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.asset import Asset, AssetType, AssetStatus
from app.schemas.asset import AssetResponse, AssetCreate, AssetUpdate
from app.utils.security import get_current_user

router = APIRouter()


@router.get("/", response_model=List[AssetResponse])
async def list_assets(
    project_id: int = None,
    storyboard_id: int = None,
    asset_type: AssetType = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List assets
    """
    query = db.query(Asset)

    if project_id:
        query = query.filter(Asset.project_id == project_id)

    if storyboard_id:
        query = query.filter(Asset.storyboard_id == storyboard_id)

    if asset_type:
        query = query.filter(Asset.type == asset_type)

    assets = query.offset(skip).limit(limit).all()
    return assets


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get asset by ID
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    return asset


@router.post("/", response_model=AssetResponse)
async def create_asset(
    asset_in: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new asset
    """
    asset = Asset(
        project_id=asset_in.project_id,
        storyboard_id=asset_in.storyboard_id,
        type=asset_in.type,
        file_name=asset_in.file_name,
        file_path=asset_in.file_path,
        mime_type=asset_in.mime_type,
        file_size=asset_in.file_size,
        url=asset_in.url,
        metadata=asset_in.metadata,
        provider=asset_in.provider,
        model_name=asset_in.model_name,
        status=AssetStatus.COMPLETED,
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_in: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update asset
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    update_data = asset_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete asset
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    db.delete(asset)
    db.commit()

    return {"message": "Asset deleted successfully"}
