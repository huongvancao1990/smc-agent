"""smc_agent — LLM orchestrator for Smart Money Concept analysis.

Wraps the pure-Python ``smc_core`` engine in a function-calling agent that uses
a local Ollama instance (via OpenAI-compatible API) as the reasoning layer.
"""

from .agent import SMCAgent
from .config import AgentConfig
from .laws import LawCheck, apply_trading_laws
from .ollama_client import OllamaClient
from .tools import TOOLS, build_tool_dispatcher

__all__ = [
    "TOOLS",
    "AgentConfig",
    "LawCheck",
    "OllamaClient",
    "SMCAgent",
    "apply_trading_laws",
    "build_tool_dispatcher",
]
