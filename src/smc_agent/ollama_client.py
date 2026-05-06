"""Minimal OpenAI-compatible chat-completions client targeting Ollama.

We avoid pulling in the official ``openai`` SDK to keep the dependency surface
small. Ollama exposes ``/v1/chat/completions`` which mirrors OpenAI's schema
including tool/function calling.
"""

from __future__ import annotations

from typing import Any

import httpx


class OllamaClient:
    """Tiny client for Ollama's OpenAI-compatible chat endpoint."""

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:11434/v1",
        api_key: str = "ollama",
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def chat_completion(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] = "auto",
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Call POST /chat/completions and return the raw JSON response."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()
