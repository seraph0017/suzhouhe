"""
AI Provider Abstraction Layer

Hot-swappable AI provider interface with factory pattern.
Supports LLM, Image Generation, Video Generation, and TTS providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """AI Provider configuration"""
    provider_type: str
    name: str
    api_endpoint: str
    api_key: str
    config: Dict[str, Any]


@dataclass
class GenerationResult:
    """Base generation result"""
    success: bool
    data: Any
    error: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None


# ============================================
# Provider Interfaces by Category
# ============================================

class LLMProvider(ABC):
    """LLM Provider Interface"""

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> GenerationResult:
        """Generate text from prompt"""
        pass

    @abstractmethod
    async def generate_script(
        self,
        theme: str,
        genre: str,
        tone: str,
        length: int = 1000,
        **kwargs
    ) -> GenerationResult:
        """Generate script content"""
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models"""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate API connection"""
        pass


class ImageProvider(ABC):
    """Image Generation Provider Interface"""

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        seed: Optional[int] = None,
        **kwargs
    ) -> GenerationResult:
        """Generate image from prompt"""
        pass

    @abstractmethod
    async def image_to_image(
        self,
        image_url: str,
        prompt: str,
        strength: float = 0.7,
        **kwargs
    ) -> GenerationResult:
        """Modify existing image"""
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available image models"""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate API connection"""
        pass


class VideoProvider(ABC):
    """Video Generation Provider Interface"""

    @abstractmethod
    async def generate_video(
        self,
        image_url: str,
        audio_url: Optional[str] = None,
        duration: float = 5.0,
        lip_sync: bool = True,
        **kwargs
    ) -> GenerationResult:
        """Generate video from image (and optional audio)"""
        pass

    @abstractmethod
    async def image_to_video(
        self,
        image_url: str,
        prompt: str,
        duration: float = 5.0,
        **kwargs
    ) -> GenerationResult:
        """Generate video from image with motion"""
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available video models"""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate API connection"""
        pass


class TTSProvider(ABC):
    """Text-to-Speech Provider Interface"""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: str,
        speed: float = 1.0,
        pitch: float = 1.0,
        **kwargs
    ) -> GenerationResult:
        """Synthesize speech from text"""
        pass

    @abstractmethod
    async def list_voices(self) -> List[Dict[str, Any]]:
        """List available voices"""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate API connection"""
        pass


class BGMProvider(ABC):
    """BGM Generation/Recommendation Provider Interface"""

    @abstractmethod
    async def generate_bgm(
        self,
        mood: str,
        duration: float = 60.0,
        tempo: Optional[str] = None,
        instruments: Optional[List[str]] = None,
        **kwargs
    ) -> GenerationResult:
        """Generate background music"""
        pass

    @abstractmethod
    async def recommend_bgm(
        self,
        mood: str,
        emotion: str,
        duration: float = 60.0,
    ) -> GenerationResult:
        """Recommend BGM from library"""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate API connection"""
        pass


# ============================================
# Provider Factory
# ============================================

class AIProviderFactory:
    """Factory for creating AI provider instances"""

    _providers: Dict[str, Dict[str, type]] = {
        "llm": {},
        "image": {},
        "video": {},
        "tts": {},
        "bgm": {},
    }

    @classmethod
    def register(cls, provider_type: str, name: str, provider_class: type):
        """Register a provider implementation"""
        if provider_type not in cls._providers:
            cls._providers[provider_type] = {}
        cls._providers[provider_type][name] = provider_class
        logger.info(f"Registered provider: {provider_type}/{name}")

    @classmethod
    def create(cls, provider_type: str, name: str, config: ProviderConfig) -> Any:
        """Create a provider instance"""
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider type: {provider_type}")

        if name not in cls._providers[provider_type]:
            raise ValueError(f"Unknown provider: {name}")

        provider_class = cls._providers[provider_type][name]
        return provider_class(config)

    @classmethod
    def list_providers(cls, provider_type: str = None) -> Dict[str, Dict[str, type]]:
        """List all registered providers"""
        if provider_type:
            return {provider_type: cls._providers.get(provider_type, {})}
        return cls._providers


# ============================================
# Base Provider Implementation Template
# ============================================

class BaseLLMProvider(LLMProvider):
    """Base LLM Provider with common functionality"""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session = None

    async def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make API request (implement in subclass)"""
        raise NotImplementedError

    async def validate_connection(self) -> bool:
        """Validate API connection"""
        try:
            await self._make_request("/health", {})
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False


class BaseImageProvider(ImageProvider):
    """Base Image Provider with common functionality"""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session = None

    async def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make API request (implement in subclass)"""
        raise NotImplementedError

    async def validate_connection(self) -> bool:
        """Validate API connection"""
        try:
            await self._make_request("/health", {})
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False


class BaseVideoProvider(VideoProvider):
    """Base Video Provider with common functionality"""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session = None

    async def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make API request (implement in subclass)"""
        raise NotImplementedError

    async def validate_connection(self) -> bool:
        """Validate API connection"""
        try:
            await self._make_request("/health", {})
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False


class BaseTTSProvider(TTSProvider):
    """Base TTS Provider with common functionality"""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session = None

    async def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make API request (implement in subclass)"""
        raise NotImplementedError

    async def validate_connection(self) -> bool:
        """Validate API connection"""
        try:
            await self._make_request("/health", {})
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False


class BaseBGMProvider(BGMProvider):
    """Base BGM Provider with common functionality"""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.session = None

    async def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make API request (implement in subclass)"""
        raise NotImplementedError

    async def validate_connection(self) -> bool:
        """Validate API connection"""
        try:
            await self._make_request("/health", {})
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False
