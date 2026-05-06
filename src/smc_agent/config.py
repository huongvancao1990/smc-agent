"""Agent configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentConfig:
    """Configuration for the SMC Agent.

    Defaults target a local Ollama instance with OpenAI-compatible chat
    completions endpoint. No API key is required.
    """

    base_url: str = "http://localhost:11434/v1"
    model: str = "qwen2.5:7b"
    api_key: str = "ollama"  # Ollama ignores the value but the OpenAI client requires one.
    temperature: float = 0.2
    max_tool_iterations: int = 6
    request_timeout_seconds: float = 120.0
    language: str = "vi"

    @classmethod
    def from_env(cls) -> AgentConfig:
        """Build config from environment variables, falling back to defaults."""
        return cls(
            base_url=os.getenv("SMC_AGENT_BASE_URL", cls.base_url),
            model=os.getenv("SMC_AGENT_MODEL", cls.model),
            api_key=os.getenv("SMC_AGENT_API_KEY", cls.api_key),
            temperature=float(os.getenv("SMC_AGENT_TEMPERATURE", str(cls.temperature))),
            max_tool_iterations=int(
                os.getenv("SMC_AGENT_MAX_TOOL_ITERATIONS", str(cls.max_tool_iterations))
            ),
            request_timeout_seconds=float(
                os.getenv("SMC_AGENT_TIMEOUT", str(cls.request_timeout_seconds))
            ),
            language=os.getenv("SMC_AGENT_LANGUAGE", cls.language),
        )
