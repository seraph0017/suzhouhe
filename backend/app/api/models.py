"""
Model Configuration API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.model_provider import ModelProvider
from app.schemas.model import ModelProviderResponse, ModelProviderCreate, ModelProviderUpdate
from app.utils.security import get_current_admin_user, get_current_user

router = APIRouter()


@router.get("/", response_model=List[ModelProviderResponse])
async def list_model_providers(
    provider_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List model providers
    """
    query = db.query(ModelProvider)

    if provider_type:
        query = query.filter(ModelProvider.provider_type == provider_type)

    providers = query.all()
    return providers


@router.get("/{provider_id}", response_model=ModelProviderResponse)
async def get_model_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get model provider by ID
    """
    provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model provider not found",
        )
    return provider


@router.post("/", response_model=ModelProviderResponse)
async def create_model_provider(
    provider_in: ModelProviderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Create new model provider (admin only)
    """
    provider = ModelProvider(
        provider_type=provider_in.provider_type,
        name=provider_in.name,
        display_name=provider_in.display_name,
        api_endpoint=provider_in.api_endpoint,
        api_key=provider_in.api_key,
        config=provider_in.config,
        is_active=True,
        is_default=provider_in.is_default,
    )

    db.add(provider)
    db.commit()
    db.refresh(provider)

    return provider


@router.put("/{provider_id}", response_model=ModelProviderResponse)
async def update_model_provider(
    provider_id: int,
    provider_in: ModelProviderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Update model provider (admin only)
    """
    provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model provider not found",
        )

    update_data = provider_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(provider, field, value)

    db.add(provider)
    db.commit()
    db.refresh(provider)

    return provider


@router.delete("/{provider_id}")
async def delete_model_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Delete model provider (admin only)
    """
    provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model provider not found",
        )

    db.delete(provider)
    db.commit()

    return {"message": "Model provider deleted successfully"}


@router.post("/{provider_id}/set-default", response_model=ModelProviderResponse)
async def set_default_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Set default provider for a type (admin only)
    """
    provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model provider not found",
        )

    # Unset other defaults for this type
    db.query(ModelProvider).filter(
        ModelProvider.provider_type == provider.provider_type,
        ModelProvider.is_default == True
    ).update({"is_default": False})

    # Set new default
    provider.is_default = True
    db.add(provider)
    db.commit()
    db.refresh(provider)

    return provider
