"""
Anthropic Provider Implementation

Supports:
- LLM (Claude)
"""

import httpx
from typing import Dict, List, Optional
import logging

from app.services.ai.base import (
    ProviderConfig,
    GenerationResult,
    BaseLLMProvider,
    AIProviderFactory,
)

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Provider"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.api_endpoint or "https://api.anthropic.com/v1"
        self.api_key = config.api_key
        self.model = config.config.get("model", "claude-sonnet-4-20250514")

    async def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make API request to Anthropic"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
                json=data,
                timeout=120.0,
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
        """Generate text using Claude"""
        try:
            response = await self._make_request("/messages", {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_prompt or "You are a helpful assistant.",
                "messages": [{"role": "user", "content": prompt}],
                **kwargs
            })

            content = response["content"][0]["text"]

            return GenerationResult(
                success=True,
                data=content,
                usage=response.get("usage")
            )
        except Exception as e:
            logger.error(f"Anthropic text generation failed: {e}")
            return GenerationResult(success=False, data=None, error=str(e))

    async def generate_script(
        self,
        theme: str,
        genre: str,
        tone: str,
        length: int = 1000,
        **kwargs
    ) -> GenerationResult:
        """Generate script using Claude"""
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
        """List available Claude models"""
        return [
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
        ]

    async def validate_connection(self) -> bool:
        """Validate Anthropic API connection"""
        try:
            result = await self.generate_text("Hello", max_tokens=10)
            return result.success
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False


# Register Anthropic provider
AIProviderFactory.register("llm", "anthropic", AnthropicProvider)
