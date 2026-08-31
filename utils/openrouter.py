import json
import os
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import requests

from config.settings import settings


class OpenRouterClient:
    """Small OpenAI-compatible client for the WordPress automation agents."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    @staticmethod
    def _is_retryable_model_error(error: Exception) -> bool:
        message = str(error).lower()
        return (
            "429" in str(error)
            or "rate_limit" in message
            or "rate limit" in message
            or "too many requests" in message
            or "quota" in message
        )

    def _build_request_payload(
        self,
        model_name: str,
        messages: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": model_name,
            "messages": messages or [],
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format is not None:
            payload["response_format"] = response_format
        return payload

    def _send_request(
        self,
        model_name: str,
        messages: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> Any:
        payload = self._build_request_payload(
            model_name=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://seoautomation.local",
                "X-Title": "SEO Automation",
            },
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("OpenRouter returned no completion choices")

        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str):
            raise ValueError("OpenRouter returned an invalid message content")
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )

    def _create(
        self,
        model: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> Any:
        primary_model = model or self.model or settings.openrouter_model or "openai/gpt-4o-mini"
        fallback_models = []
        for candidate in settings.openrouter_fallback_models:
            if candidate and candidate != primary_model and candidate not in fallback_models:
                fallback_models.append(candidate)

        model_chain = [primary_model] + fallback_models
        last_error: Optional[Exception] = None

        for model_name in model_chain:
            try:
                return self._send_request(
                    model_name=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                )
            except Exception as exc:  # pragma: no cover - exercised via integration tests
                last_error = exc
                if not self._is_retryable_model_error(exc) or model_name == model_chain[-1]:
                    raise

        if last_error is not None:
            raise last_error
        raise RuntimeError("OpenRouter request failed without a response")
