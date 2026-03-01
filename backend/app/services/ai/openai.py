"""
OpenAI Provider Implementation

Supports:
- LLM (GPT-4)
- Image (DALL-E 3)
- TTS (OpenAI TTS)
"""

import httpx
from typing import Dict, List, Any, Optional
import logging

from app.services.ai.base import (
    ProviderConfig,
    GenerationResult,
    BaseLLMProvider,
    BaseImageProvider,
    BaseTTSProvider,
    AIProviderFactory,
)

logger = logging.getLogger(__name__)


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI GPT Provider"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.api_endpoint or "https://api.openai.com/v1"
        self.api_key = config.api_key
        self.model = config.config.get("model", "gpt-4")

    async def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make API request to OpenAI"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=data,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> GenerationResult:
        """Generate text using GPT"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self._make_request("/chat/completions", {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            })

            content = response["choices"][0]["message"]["content"]
            usage = response.get("usage")

            return GenerationResult(
                success=True,
                data=content,
                usage=usage
            )
        except Exception as e:
            logger.error(f"OpenAI text generation failed: {e}")
            return GenerationResult(success=False, data=None, error=str(e))

    async def generate_script(
        self,
        theme: str,
        genre: str,
        tone: str,
        length: int = 1000,
        **kwargs
    ) -> GenerationResult:
        """Generate script using GPT"""
        system_prompt = """你是一位专业的编剧，擅长创作引人入胜的漫剧剧本。
请根据用户提供的主题、类型和语调创作剧本。
剧本格式应包含场景描述、角色对话和镜头指示。"""

        prompt = f"""请创作一个{genre}类型的剧本：
- 主题：{theme}
- 语调：{tone}
- 长度：约{length}字

请包含以下元素：
1. 故事背景介绍
2. 主要角色设定
3. 情节发展
4. 高潮和结局"""

        return await self.generate_text(prompt, system_prompt=system_prompt, **kwargs)

    async def list_models(self) -> List[str]:
        """List available OpenAI models"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return [self.model]

    async def validate_connection(self) -> bool:
        """Validate OpenAI API connection"""
        try:
            await self._make_request("/models", {})
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False


class OpenAIImageProvider(BaseImageProvider):
    """OpenAI DALL-E 3 Provider"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.api_endpoint or "https://api.openai.com/v1"
        self.api_key = config.api_key
        self.model = config.config.get("model", "dall-e-3")

    async def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make API request to OpenAI"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=data,
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()

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
        """Generate image using DALL-E 3"""
        try:
            # DALL-E 3 only supports 1024x1024, 1024x1792, 1792x1024
            size = f"{width}x{height}"
            if size not in ["1024x1024", "1024x1792", "1792x1024"]:
                size = "1024x1024"

            response = await self._make_request("/images/generations", {
                "model": self.model,
                "prompt": prompt,
                "n": num_images,
                "size": size,
                **kwargs
            })

            images = [
                {
                    "url": img.get("url"),
                    "revised_prompt": img.get("revised_prompt"),
                }
                for img in response.get("data", [])
            ]

            return GenerationResult(success=True, data=images)
        except Exception as e:
            logger.error(f"DALL-E image generation failed: {e}")
            return GenerationResult(success=False, data=None, error=str(e))

    async def list_models(self) -> List[str]:
        """List available image models"""
        return ["dall-e-3", "dall-e-2"]

    async def validate_connection(self) -> bool:
        """Validate connection"""
        try:
            await self.generate_image("test", num_images=1)
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False


class OpenAITTSProvider(BaseTTSProvider):
    """OpenAI TTS Provider"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.api_endpoint or "https://api.openai.com/v1"
        self.api_key = config.api_key
        self.model = config.config.get("model", "tts-1")

    async def _make_request(self, endpoint: str, data: Dict) -> bytes:
        """Make API request to OpenAI TTS"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=data,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.content

    async def synthesize(
        self,
        text: str,
        voice_id: str,
        speed: float = 1.0,
        pitch: float = 1.0,
        **kwargs
    ) -> GenerationResult:
        """Synthesize speech using OpenAI TTS"""
        try:
            audio_data = await self._make_request("/audio/speech", {
                "model": self.model,
                "input": text,
                "voice": voice_id,
                "speed": speed,
                **kwargs
            })

            # Return audio bytes (should be saved to storage)
            return GenerationResult(
                success=True,
                data={"audio_bytes": audio_data, "format": "mp3"}
            )
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return GenerationResult(success=False, data=None, error=str(e))

    async def list_voices(self) -> List[Dict[str, Any]]:
        """List available TTS voices"""
        voices = [
            {"id": "alloy", "name": "Alloy", "gender": "neutral"},
            {"id": "echo", "name": "Echo", "gender": "male"},
            {"id": "fable", "name": "Fable", "gender": "neutral"},
            {"id": "onyx", "name": "Onyx", "gender": "male"},
            {"id": "nova", "name": "Nova", "gender": "female"},
            {"id": "shimmer", "name": "Shimmer", "gender": "female"},
        ]
        return voices

    async def validate_connection(self) -> bool:
        """Validate connection"""
        try:
            result = await self.synthesize("test", voice_id="alloy")
            return result.success
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False


# Register OpenAI providers
AIProviderFactory.register("llm", "openai", OpenAILLMProvider)
AIProviderFactory.register("image", "openai", OpenAIImageProvider)
AIProviderFactory.register("tts", "openai", OpenAITTSProvider)
