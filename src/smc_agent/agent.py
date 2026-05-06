"""SMC Agent — function-calling orchestrator.

Workflow:
    1. Build system prompt = SMC methodology + 4 trading laws + output format.
2. Send user query + tool schemas to Ollama via OpenAI-compatible API.
3. Loop: while assistant returns tool_calls, dispatch each tool, append
   tool results, and re-prompt — up to ``max_tool_iterations``.
4. Return the final assistant message and the full transcript.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib import resources
from typing import Any

from .config import AgentConfig
from .ollama_client import OllamaClient
from .tools import TOOLS, AgentContext, build_tool_dispatcher


def _load_text(package_path: str) -> str:
    """Load a packaged text resource (e.g. 'knowledge/trading_laws.md')."""
    module, _, filename = package_path.rpartition("/")
    if not module:
        module = ""
    pkg = "smc_agent" if not module else f"smc_agent.{module.replace('/', '.')}"
    return resources.files(pkg).joinpath(filename).read_text(encoding="utf-8")


def build_system_prompt() -> str:
    """Compose the full system prompt: methodology + laws + output format."""
    methodology = _load_text("knowledge/smc_methodology.md")
    laws = _load_text("knowledge/trading_laws.md")
    instructions = _load_text("prompts/system_vi.md")

    return (
        f"{instructions}\n\n"
        f"---\n\n"
        f"# Phương pháp SMC (tham khảo)\n\n{methodology}\n\n"
        f"---\n\n"
        f"# Bộ nhớ trade — 4 định luật & 4 bài học\n\n{laws}\n"
    )


@dataclass
class AgentRun:
    """Result of a single agent invocation."""

    final_message: str
    messages: list[dict[str, Any]] = field(default_factory=list)
    tool_calls_made: int = 0
    iterations: int = 0


class SMCAgent:
    """High-level SMC analysis agent."""

    def __init__(
        self,
        config: AgentConfig | None = None,
        *,
        client: OllamaClient | None = None,
        context: AgentContext | None = None,
    ) -> None:
        self.config = config or AgentConfig.from_env()
        self.client = client or OllamaClient(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            timeout=self.config.request_timeout_seconds,
        )
        self.context, self.dispatch = build_tool_dispatcher(context)
        self.system_prompt = build_system_prompt()

    def run(self, user_query: str) -> AgentRun:
        """Run a single user query through the tool-calling loop."""
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query},
        ]
        tool_calls_made = 0

        for iteration in range(1, self.config.max_tool_iterations + 1):
            resp = self.client.chat_completion(
                model=self.config.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=self.config.temperature,
            )
            choice = resp["choices"][0]
            msg = choice["message"]
            messages.append(msg)

            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                return AgentRun(
                    final_message=msg.get("content") or "",
                    messages=messages,
                    tool_calls_made=tool_calls_made,
                    iterations=iteration,
                )

            for call in tool_calls:
                tool_calls_made += 1
                fn = call["function"]
                name = fn["name"]
                args_str = fn.get("arguments") or "{}"
                try:
                    args = json.loads(args_str) if isinstance(args_str, str) else args_str
                except json.JSONDecodeError:
                    args = {}

                try:
                    result = self.dispatch(name, args)
                except Exception as exc:
                    result = json.dumps({"error": str(exc)})

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id", ""),
                        "name": name,
                        "content": result,
                    }
                )

        # Forced exit; ask the model to produce a final answer with no more tools.
        forced_messages = [
            *messages,
            {
                "role": "user",
                "content": (
                    "Đã hết số vòng tool. Hãy tổng hợp kết quả cuối cùng "
                    "bằng tiếng Việt theo format yêu cầu."
                ),
            },
        ]
        resp = self.client.chat_completion(
            model=self.config.model,
            messages=forced_messages,
            tools=None,
            temperature=self.config.temperature,
        )
        final = resp["choices"][0]["message"].get("content") or ""
        messages.append({"role": "assistant", "content": final})
        return AgentRun(
            final_message=final,
            messages=messages,
            tool_calls_made=tool_calls_made,
            iterations=self.config.max_tool_iterations,
        )
