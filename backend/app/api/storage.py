"""
File Upload API routes
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.asset import Asset, AssetType, AssetStatus
from app.schemas.asset import AssetResponse
from app.utils.security import get_current_user
from app.services.storage import get_minio, MinIOService

router = APIRouter()


ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav", "audio/ogg"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/webm"]


def get_asset_type(content_type: str) -> AssetType:
    """Determine asset type from content type"""
    if content_type.startswith("image/"):
        return AssetType.IMAGE
    elif content_type.startswith("audio/"):
        return AssetType.AUDIO
    elif content_type.startswith("video/"):
        return AssetType.VIDEO
    else:
        return AssetType.OTHER


@router.post("/upload", response_model=AssetResponse)
async def upload_file(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    storyboard_id: Optional[int] = Form(None),
    asset_type: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    minio: MinIOService = Depends(get_minio),
):
    """
    Upload file directly

    Use presigned URL for large files instead.
    """
    # Validate file size (100MB limit)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset

    if file_size > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 100MB limit"
        )

    # Determine asset type
    if asset_type:
        try:
            file_type = AssetType(asset_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid asset type: {asset_type}"
            )
    else:
        file_type = get_asset_type(file.content_type or "")

    # Generate object name
    ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    object_name = f"projects/{project_id}/{uuid.uuid4()}.{ext}"

    try:
        # Read file content
        content = await file.read()

        # Upload to MinIO
        url = minio.upload_file(
            file_bytes=content,
            object_name=object_name,
            content_type=file.content_type or "application/octet-stream",
            extra_metadata={
                "uploaded_by": str(current_user.id),
                "project_id": str(project_id),
            }
        )

        # Create asset record
        asset = Asset(
            project_id=project_id,
            storyboard_id=storyboard_id,
            type=file_type,
            file_name=file.filename,
            file_path=object_name,
            file_size=file_size,
            mime_type=file.content_type,
            url=url,
            status=AssetStatus.COMPLETED,
        )

        db.add(asset)
        db.commit()
        db.refresh(asset)

        return asset

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.post("/upload-url")
async def get_presigned_upload_url(
    project_id: int,
    filename: str,
    content_type: str,
    asset_type: str,
    storyboard_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    minio: MinIOService = Depends(get_minio),
):
    """
    Get presigned URL for direct upload

    Client can use this URL to upload directly to MinIO.
    """
    ext = filename.split(".")[-1] if "." in filename else "bin"
    object_name = f"projects/{project_id}/{uuid.uuid4()}.{ext}"

    try:
        # Generate presigned URL (valid for 1 hour)
        upload_url = minio.get_presigned_url(
            object_name=object_name,
            expiration=3600,
            http_method="PUT",
        )

        # Create pending asset record
        file_type = AssetType(asset_type) if asset_type else get_asset_type(content_type)

        asset = Asset(
            project_id=project_id,
            storyboard_id=storyboard_id,
            type=file_type,
            file_name=filename,
            file_path=object_name,
            mime_type=content_type,
            status=AssetStatus.PENDING,
        )

        db.add(asset)
        db.commit()
        db.refresh(asset)

        return {
            "upload_url": upload_url,
            "asset_id": asset.id,
            "object_name": object_name,
            "expires_in": 3600,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {str(e)}"
        )


@router.post("/{asset_id}/confirm-upload")
async def confirm_upload(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Confirm upload after using presigned URL"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    asset.status = AssetStatus.COMPLETED
    db.commit()

    return {"message": "Upload confirmed"}


@router.get("/{asset_id}/download-url")
async def get_download_url(
    asset_id: int,
    expiration: int = 3600,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    minio: MinIOService = Depends(get_minio),
):
    """Get presigned download URL for asset"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    try:
        download_url = minio.get_presigned_url(
            object_name=asset.file_path,
            expiration=expiration,
            http_method="GET",
        )

        return {
            "download_url": download_url,
            "expires_in": expiration,
            "file_name": asset.file_name,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download URL: {str(e)}"
        )


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    minio: MinIOService = Depends(get_minio),
):
    """Delete asset and file"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    try:
        # Delete from MinIO
        minio.delete_file(asset.file_path)

        # Delete from database
        db.delete(asset)
        db.commit()

        return {"message": "Asset deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )
