"""
AI Service Integration Layer

High-level service for AI operations that combines:
- Provider selection from database
- Job progress tracking
- Storage integration
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.services.ai.base import (
    ProviderConfig,
    GenerationResult,
    AIProviderFactory,
    LLMProvider,
    ImageProvider,
    VideoProvider,
    TTSProvider,
    BGMProvider,
)
from app.services.storage import MinIOStorage
from app.models.model_provider import ModelProvider

logger = logging.getLogger(__name__)


class AIService:
    """
    High-level AI Service for pipeline operations
    """

    def __init__(self, db: Session):
        self.db = db

    def _get_provider(self, provider_type: str) -> Optional[ModelProvider]:
        """Get default provider from database"""
        provider = self.db.query(ModelProvider).filter(
            ModelProvider.provider_type == provider_type,
            ModelProvider.is_default == True,
            ModelProvider.is_active == True
        ).first()
        return provider

    def _create_provider_instance(
        self, provider: ModelProvider
    ) -> Optional[Any]:
        """Create provider instance from database record"""
        try:
            config = ProviderConfig(
                provider_type=provider.provider_type,
                name=provider.provider_name,
                api_endpoint=provider.api_endpoint,
                api_key=provider.api_key,
                config=provider.config or {},
            )
            return AIProviderFactory.create(
                provider.provider_type,
                provider.provider_name,
                config,
            )
        except Exception as e:
            logger.error(f"Failed to create provider instance: {e}")
            return None

    # ============================================
    # LLM Operations
    # ============================================

    async def generate_script(
        self,
        theme: str,
        genre: str = "奇幻",
        tone: str = "轻松",
        length: int = 1000,
        provider_name: Optional[str] = None,
    ) -> GenerationResult:
        """
        Generate script using LLM

        Args:
            theme: Story theme
            genre: Genre (奇幻，爱情，冒险，etc.)
            tone: Tone (轻松，严肃，悬疑，etc.)
            length: Target length in characters
            provider_name: Optional specific provider name

        Returns:
            GenerationResult with script content
        """
        provider = self._get_provider("llm")
        if not provider:
            return GenerationResult(
                success=False,
                data=None,
                error="No LLM provider configured"
            )

        llm = self._create_provider_instance(provider)
        if not llm:
            return GenerationResult(
                success=False,
                data=None,
                error="Failed to initialize LLM provider"
            )

        return await llm.generate_script(
            theme=theme,
            genre=genre,
            tone=tone,
            length=length,
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> GenerationResult:
        """Generate text using LLM"""
        provider = self._get_provider("llm")
        if not provider:
            return GenerationResult(
                success=False,
                data=None,
                error="No LLM provider configured"
            )

        llm = self._create_provider_instance(provider)
        if not llm:
            return GenerationResult(
                success=False,
                data=None,
                error="Failed to initialize LLM provider"
            )

        return await llm.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    # ============================================
    # Image Operations
    # ============================================

    async def generate_images(
        self,
        prompt: str,
        count: int = 3,
        width: int = 1024,
        height: int = 1024,
        save_to_storage: bool = True,
    ) -> GenerationResult:
        """
        Generate images for storyboard

        Args:
            prompt: Image generation prompt
            count: Number of images to generate (抽卡制)
            width: Image width
            height: Image height
            save_to_storage: Whether to save to MinIO

        Returns:
            GenerationResult with image URLs
        """
        provider = self._get_provider("image")
        if not provider:
            return GenerationResult(
                success=False,
                data=None,
                error="No image provider configured"
            )

        image_provider = self._create_provider_instance(provider)
        if not image_provider:
            return GenerationResult(
                success=False,
                data=None,
                error="Failed to initialize image provider"
            )

        result = await image_provider.generate_image(
            prompt=prompt,
            num_images=count,
            width=width,
            height=height,
        )

        if result.success and save_to_storage:
            # Download and save images to MinIO
            storage = MinIOStorage()
            saved_images = []

            for img_data in result.data:
                try:
                    # Download image from URL
                    import httpx
                    async with httpx.AsyncClient() as client:
                        response = await client.get(img_data["url"])
                        response.raise_for_status()
                        image_bytes = response.content

                    # Save to MinIO
                    import uuid
                    object_name = f"generated/{uuid.uuid4()}.png"
                    storage.upload_from_bytes(
                        object_name,
                        image_bytes,
                        content_type="image/png",
                    )

                    saved_images.append({
                        "url": storage.get_presigned_url(object_name),
                        "object_name": object_name,
                        "width": width,
                        "height": height,
                    })
                except Exception as e:
                    logger.error(f"Failed to save image to storage: {e}")

            result.data = saved_images

        return result

    # ============================================
    # TTS Operations
    # ============================================

    async def synthesize_audio(
        self,
        text: str,
        voice_id: str = "alloy",
        save_to_storage: bool = True,
    ) -> GenerationResult:
        """
        Synthesize audio from text

        Args:
            text: Text to synthesize
            voice_id: Voice ID to use
            save_to_storage: Whether to save to MinIO

        Returns:
            GenerationResult with audio URL
        """
        provider = self._get_provider("tts")
        if not provider:
            return GenerationResult(
                success=False,
                data=None,
                error="No TTS provider configured"
            )

        tts_provider = self._create_provider_instance(provider)
        if not tts_provider:
            return GenerationResult(
                success=False,
                data=None,
                error="Failed to initialize TTS provider"
            )

        result = await tts_provider.synthesize(
            text=text,
            voice_id=voice_id,
        )

        if result.success and save_to_storage:
            storage = MinIOStorage()
            try:
                import uuid
                audio_data = result.data
                object_name = f"generated/audio/{uuid.uuid4()}.mp3"

                storage.upload_from_bytes(
                    object_name,
                    audio_data["audio_bytes"],
                    content_type="audio/mpeg",
                )

                result.data = {
                    "url": storage.get_presigned_url(object_name),
                    "object_name": object_name,
                    "duration": 5.0,  # TODO: Get actual duration
                    "voice_id": voice_id,
                }
            except Exception as e:
                logger.error(f"Failed to save audio to storage: {e}")
                result.data = {"error": "Failed to save audio"}

        return result

    async def list_voices(self) -> List[Dict[str, Any]]:
        """List available TTS voices"""
        provider = self._get_provider("tts")
        if not provider:
            return []

        tts_provider = self._create_provider_instance(provider)
        if not tts_provider:
            return []

        return await tts_provider.list_voices()

    # ============================================
    # Video Operations
    # ============================================

    async def generate_video(
        self,
        image_url: str,
        audio_url: Optional[str] = None,
        duration: float = 5.0,
        lip_sync: bool = True,
        save_to_storage: bool = True,
    ) -> GenerationResult:
        """
        Generate video from image (and optional audio)

        Args:
            image_url: Source image URL
            audio_url: Optional audio URL for lip-sync
            duration: Video duration in seconds
            lip_sync: Whether to enable lip-sync
            save_to_storage: Whether to save to MinIO

        Returns:
            GenerationResult with video URL
        """
        provider = self._get_provider("video")
        if not provider:
            return GenerationResult(
                success=False,
                data=None,
                error="No video provider configured"
            )

        video_provider = self._create_provider_instance(provider)
        if not video_provider:
            return GenerationResult(
                success=False,
                data=None,
                error="Failed to initialize video provider"
            )

        result = await video_provider.generate_video(
            image_url=image_url,
            audio_url=audio_url,
            duration=duration,
            lip_sync=lip_sync,
        )

        if result.success and save_to_storage:
            storage = MinIOStorage()
            try:
                import uuid
                import httpx

                # Download video
                async with httpx.AsyncClient() as client:
                    response = await client.get(result.data["url"])
                    response.raise_for_status()
                    video_bytes = response.content

                object_name = f"generated/video/{uuid.uuid4()}.mp4"
                storage.upload_from_bytes(
                    object_name,
                    video_bytes,
                    content_type="video/mp4",
                )

                result.data = {
                    "url": storage.get_presigned_url(object_name),
                    "object_name": object_name,
                    "duration": duration,
                    "lip_sync": lip_sync,
                }
            except Exception as e:
                logger.error(f"Failed to save video to storage: {e}")

        return result

    # ============================================
    # BGM Operations
    # ============================================

    async def recommend_bgm(
        self,
        mood: str,
        emotion: str,
        duration: float = 60.0,
    ) -> GenerationResult:
        """
        Recommend BGM based on mood/emotion

        Args:
            mood: Overall mood (欢快，悲伤，紧张，etc.)
            emotion: Specific emotion
            duration: Target duration

        Returns:
            GenerationResult with BGM recommendations
        """
        provider = self._get_provider("bgm")
        if not provider:
            # Return mock recommendations if no provider
            return GenerationResult(
                success=True,
                data=[
                    {"title": f"{mood} Background 1", "mood": mood, "url": "/bgm/default1.mp3"},
                    {"title": f"{mood} Background 2", "mood": mood, "url": "/bgm/default2.mp3"},
                ]
            )

        bgm_provider = self._create_provider_instance(provider)
        if not bgm_provider:
            return GenerationResult(
                success=False,
                data=None,
                error="Failed to initialize BGM provider"
            )

        return await bgm_provider.recommend_bgm(
            mood=mood,
            emotion=emotion,
            duration=duration,
        )

    # ============================================
    # Provider Management
    # ============================================

    async def validate_provider(self, provider_type: str) -> bool:
        """Validate provider connection"""
        provider = self._get_provider(provider_type)
        if not provider:
            return False

        provider_instance = self._create_provider_instance(provider)
        if not provider_instance:
            return False

        return await provider_instance.validate_connection()

    async def list_available_providers(self) -> Dict[str, List[str]]:
        """List all available providers by type"""
        providers = self.db.query(ModelProvider).filter(
            ModelProvider.is_active == True
        ).all()

        result = {}
        for provider in providers:
            if provider.provider_type not in result:
                result[provider.provider_type] = []
            result[provider.provider_type].append({
                "name": provider.provider_name,
                "is_default": provider.is_default,
            })

        return result
