"""
AI Provider Management API

Routes for configuring and managing AI providers.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.models.model_provider import ModelProvider
from app.utils.security import get_current_user, require_role
from app.services.ai_service import AIService

router = APIRouter(prefix="/providers", tags=["AI Providers"])


class ProviderCreate(BaseModel):
    """Schema for creating a provider"""
    provider_type: str = Field(..., description="Provider type: llm, image, video, tts, bgm")
    provider_name: str = Field(..., description="Provider name: openai, anthropic, etc.")
    api_endpoint: Optional[str] = Field(None, description="API endpoint URL")
    api_key: str = Field(..., description="API key")
    config: dict = Field(default_factory=dict, description="Additional configuration")
    is_default: bool = Field(False, description="Whether this is the default provider")


class ProviderUpdate(BaseModel):
    """Schema for updating a provider"""
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    config: Optional[dict] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class ProviderResponse(BaseModel):
    """Schema for provider response"""
    id: int
    provider_type: str
    provider_name: str
    api_endpoint: Optional[str]
    is_default: bool
    is_active: bool
    health_status: Optional[str]
    config: Optional[dict]

    class Config:
        from_attributes = True


@router.get("", response_model=List[ProviderResponse])
async def list_providers(
    provider_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all configured AI providers"""
    query = db.query(ModelProvider)
    if provider_type:
        query = query.filter(ModelProvider.provider_type == provider_type)
    return query.all()


@router.get("/available", response_model=dict)
async def list_available_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all available provider types and implementations"""
    ai_service = AIService(db)
    return await ai_service.list_available_providers()


@router.post("", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    provider_data: ProviderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Create a new AI provider configuration"""
    # If this is set as default, unset other defaults for this type
    if provider_data.is_default:
        db.query(ModelProvider).filter(
            ModelProvider.provider_type == provider_data.provider_type,
            ModelProvider.is_default == True
        ).update({"is_default": False})

    provider = ModelProvider(
        provider_type=provider_data.provider_type,
        provider_name=provider_data.provider_name,
        api_endpoint=provider_data.api_endpoint,
        api_key=provider_data.api_key,
        config=provider_data.config,
        is_default=provider_data.is_default,
        is_active=True,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get provider details"""
    provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.put("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: int,
    provider_data: ProviderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Update provider configuration"""
    provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Update fields
    update_data = provider_data.model_dump(exclude_unset=True)

    # If setting as default, unset other defaults for this type
    if update_data.get("is_default"):
        db.query(ModelProvider).filter(
            ModelProvider.provider_type == provider.provider_type,
            ModelProvider.is_default == True,
            ModelProvider.id != provider_id
        ).update({"is_default": False})

    for field, value in update_data.items():
        setattr(provider, field, value)

    db.commit()
    db.refresh(provider)
    return provider


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Delete a provider configuration"""
    provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    db.delete(provider)
    db.commit()
    return None


@router.post("/{provider_id}/validate")
async def validate_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Validate provider connection"""
    provider = db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    ai_service = AIService(db)
    is_valid = await ai_service.validate_provider(provider.provider_type)

    # Update health status
    provider.health_status = "healthy" if is_valid else "unhealthy"
    from datetime import datetime
    provider.last_health_check = datetime.utcnow()
    db.commit()

    return {
        "provider_id": provider_id,
        "valid": is_valid,
        "health_status": provider.health_status,
    }


@router.post("/health-check")
async def health_check_all_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run health check on all active providers"""
    ai_service = AIService(db)
    providers = db.query(ModelProvider).filter(ModelProvider.is_active == True).all()

    results = []
    for provider in providers:
        is_valid = await ai_service.validate_provider(provider.provider_type)
        provider.health_status = "healthy" if is_valid else "unhealthy"
        from datetime import datetime
        provider.last_health_check = datetime.utcnow()
        results.append({
            "provider_id": provider.id,
            "provider_type": provider.provider_type,
            "provider_name": provider.provider_name,
            "valid": is_valid,
            "health_status": provider.health_status,
        })

    db.commit()
    return {"results": results}


@router.get("/types/{provider_type}/voices")
async def list_voices(
    provider_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List available voices for TTS provider"""
    if provider_type != "tts":
        raise HTTPException(status_code=400, detail="Only TTS providers have voices")

    ai_service = AIService(db)
    voices = await ai_service.list_voices()
    return {"voices": voices}
