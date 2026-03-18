import os
from openai import AsyncOpenAI
from pydantic import BaseModel
import structlog

from app.core.config import settings

logger = structlog.get_logger()

class BaseLLMClient:
    """Protocol-like base class for LLM clients."""
    async def complete(self, prompt: str) -> str:
        raise NotImplementedError

class HuggingFaceLLMClient(BaseLLMClient):
    """
    OpenAI-compatible client pointing to Hugging Face Inference Providers.
    Requires HF_TOKEN with "Inference Providers" permission.
    """
    def __init__(self):
        # We use AsyncOpenAI to avoid blocking the FastAPI event loop
        self.client = AsyncOpenAI(
            base_url=settings.hf_base_url,
            api_key=settings.hf_token,
        )
        self.model = settings.hf_model_name

    async def complete(self, prompt: str) -> str:
        try:
            logger.info("llm_request_started", model=self.model)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            logger.info("llm_request_completed", model=self.model)
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error("llm_request_failed", error=str(e), model=self.model)
            raise

# Singleton instance for dependency injection
llm_client = HuggingFaceLLMClient()
