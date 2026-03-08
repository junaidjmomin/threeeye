"""
Pluggable LLM provider abstraction with Anthropic, OpenAI, and Azure implementations.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, system: str, user: str) -> str:
        """Send system + user prompt to LLM, return text response."""
        ...

    async def complete_json(self, system: str, user: str) -> dict[str, Any]:
        """Call complete() and parse the response as JSON."""
        raw = await self.complete(system, user)
        # Strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip().rstrip("```").strip()
        return json.loads(raw)


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.api_key = api_key
        self.model = model
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                import anthropic  # type: ignore[import]
                self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError as e:
                raise RuntimeError("Install anthropic SDK: pip install anthropic") from e
        return self._client

    async def complete(self, system: str, user: str) -> str:
        client = self._get_client()
        message = await client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return message.content[0].text


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                import openai  # type: ignore[import]
                self._client = openai.AsyncOpenAI(api_key=self.api_key)
            except ImportError as e:
                raise RuntimeError("Install openai SDK: pip install openai") from e
        return self._client

    async def complete(self, system: str, user: str) -> str:
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content or ""


class AzureOpenAIProvider(LLMProvider):
    def __init__(self, endpoint: str, api_key: str, deployment: str = "gpt-4o"):
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                import openai  # type: ignore[import]
                self._client = openai.AsyncAzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version="2024-02-01",
                )
            except ImportError as e:
                raise RuntimeError("Install openai SDK: pip install openai") from e
        return self._client

    async def complete(self, system: str, user: str) -> str:
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.deployment,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content or ""


def get_provider_from_settings() -> LLMProvider:
    """Instantiate the configured LLM provider from app settings."""
    from app.core.config import settings  # local import to avoid circular

    provider_name = getattr(settings, "LLM_PROVIDER", "anthropic").lower()

    if provider_name == "anthropic":
        return AnthropicProvider(
            api_key=settings.ANTHROPIC_API_KEY or "",
            model=getattr(settings, "ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        )
    elif provider_name == "openai":
        return OpenAIProvider(
            api_key=settings.OPENAI_API_KEY or "",
            model=getattr(settings, "OPENAI_MODEL", "gpt-4o"),
        )
    elif provider_name == "azure_openai":
        return AzureOpenAIProvider(
            endpoint=settings.AZURE_OPENAI_ENDPOINT or "",
            api_key=settings.AZURE_OPENAI_API_KEY or "",
            deployment=getattr(settings, "AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        )
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider_name}")
