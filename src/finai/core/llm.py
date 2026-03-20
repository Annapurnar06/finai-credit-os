"""LLM router — custom multi-provider gateway.

Task-specific model routing with cost-aware selection.
Primary: Anthropic Claude. Fallback: OpenAI. Future: local SLMs via Ollama/vLLM.
"""
from __future__ import annotations

import time
from typing import Any

import structlog
from anthropic import AsyncAnthropic

from finai.config import get_settings

logger = structlog.get_logger()

# Model routing table: task → model
MODEL_ROUTES: dict[str, str] = {
    "extraction_fast": "claude-haiku-4-20250514",
    "extraction_vision": "claude-sonnet-4-20250514",
    "narrative": "claude-sonnet-4-20250514",
    "classification": "claude-haiku-4-20250514",
    "compliance": "claude-sonnet-4-20250514",
    "chat": "claude-haiku-4-20250514",
    "default": "claude-sonnet-4-20250514",
}


class LLMRouter:
    """Routes LLM calls to the appropriate model based on task type."""

    def __init__(self) -> None:
        settings = get_settings()
        self._anthropic = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._call_count = 0
        self._total_tokens = 0
        self._total_cost = 0.0

    def _get_model(self, task: str) -> str:
        return MODEL_ROUTES.get(task, MODEL_ROUTES["default"])

    async def complete(
        self,
        messages: list[dict[str, Any]],
        task: str = "default",
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.0,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        model = self._get_model(task)
        start = time.monotonic()

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system:
            kwargs["system"] = system

        try:
            response = await self._anthropic.messages.create(**kwargs)
            latency_ms = int((time.monotonic() - start) * 1000)

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            self._call_count += 1
            self._total_tokens += input_tokens + output_tokens

            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            logger.info(
                "llm_call",
                model=model,
                task=task,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
            )

            return {
                "content": content,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms,
                "stop_reason": response.stop_reason,
            }

        except Exception as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            logger.error("llm_call_failed", model=model, task=task, error=str(e), latency_ms=latency_ms)
            raise

    async def extract_structured(
        self,
        content: str,
        schema_description: str,
        task: str = "extraction_fast",
        system: str = "",
    ) -> dict[str, Any]:
        """Extract structured data from text using LLM."""
        full_system = (
            f"{system}\n\n" if system else ""
        ) + (
            "You are a document extraction agent. Extract structured data from the provided content.\n"
            f"Return ONLY valid JSON matching this schema:\n{schema_description}\n"
            "If a field cannot be extracted, use null. Be precise."
        )

        result = await self.complete(
            messages=[{"role": "user", "content": content}],
            task=task,
            system=full_system,
            temperature=0.0,
        )

        import json
        text = result["content"]
        # Extract JSON from response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        try:
            parsed = json.loads(text.strip())
        except json.JSONDecodeError:
            parsed = {"raw_response": text, "parse_error": True}

        result["parsed"] = parsed
        return result

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "total_calls": self._call_count,
            "total_tokens": self._total_tokens,
        }


_router: LLMRouter | None = None


def get_llm_router() -> LLMRouter:
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router
