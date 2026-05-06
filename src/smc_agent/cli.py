"""CLI entrypoint: ``smc-agent analyze --csv ... [--symbol ... --timeframe ...]``."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from smc_core import build_setups, load_ohlcv

from .agent import SMCAgent, build_system_prompt
from .config import AgentConfig
from .laws import apply_trading_laws

app = typer.Typer(
    name="smc-agent",
    help="SMC Trading Agent — phân tích Smart Money Concept và setup 1:3 RR.",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()


@app.command()
def analyze(
    csv: Path = typer.Option(..., "--csv", help="Đường dẫn file CSV OHLCV."),
    symbol: str = typer.Option("", "--symbol", help="Tên symbol (e.g., NZDUSD)."),
    timeframe: str = typer.Option("", "--timeframe", help="Timeframe (e.g., 2h)."),
    rr_ratio: float = typer.Option(3.0, "--rr", help="Tỉ lệ Risk-Reward."),
    use_llm: bool = typer.Option(
        False, "--llm/--no-llm", help="Gọi LLM (Ollama) để tổng hợp báo cáo."
    ),
    model: str | None = typer.Option(
        None, "--model", help="Override model Ollama (default qwen2.5:7b)."
    ),
) -> None:
    """Phân tích file CSV và in setup 1:3 RR (tùy chọn dùng LLM)."""
    if not csv.exists():
        console.print(f"[red]File không tồn tại:[/red] {csv}")
        raise typer.Exit(code=2)

    ohlcv = load_ohlcv(csv, symbol=symbol, timeframe=timeframe)
    console.print(
        Panel(
            f"[bold]Loaded[/bold] {len(ohlcv)} candles · {symbol or '?'} · {timeframe or '?'}",
            title="OHLCV",
            border_style="cyan",
        )
    )

    setups = build_setups(ohlcv, rr_ratio=rr_ratio)
    if not setups:
        console.print("[yellow]Không có setup 1:3 RR hợp lệ trong dữ liệu hiện tại.[/yellow]")
        raise typer.Exit(code=0)

    checks = apply_trading_laws(setups)

    table = Table(title=f"Setups ({len(setups)})", show_lines=True)
    for col in ("#", "Side", "Entry", "SL", "TP", "RR", "Severity", "Notes"):
        table.add_column(col)

    for i, (s, c) in enumerate(zip(setups, checks, strict=True)):
        table.add_row(
            str(i),
            s.side.value.upper(),
            f"{s.entry:.5f}",
            f"{s.stop_loss:.5f}",
            f"{s.take_profit:.5f}",
            f"1:{s.rr_ratio:.1f}",
            c.severity,
            "; ".join(s.notes[:2]),
        )
    console.print(table)

    if use_llm:
        cfg = AgentConfig.from_env()
        if model:
            cfg = AgentConfig(
                base_url=cfg.base_url,
                model=model,
                api_key=cfg.api_key,
                temperature=cfg.temperature,
                max_tool_iterations=cfg.max_tool_iterations,
                request_timeout_seconds=cfg.request_timeout_seconds,
                language=cfg.language,
            )
        agent = SMCAgent(cfg)
        query = (
            f"Hãy phân tích file OHLCV ở đường dẫn {csv}. "
            f"Symbol={symbol or 'unknown'}, timeframe={timeframe or 'unknown'}. "
            "Chạy đầy đủ quy trình 5 bước SMC + lọc qua 4 định luật, sau đó báo cáo "
            "theo đúng format đã quy định."
        )
        result = agent.run(query)
        console.print(
            Panel(
                result.final_message,
                title=f"LLM Report ({cfg.model})",
                border_style="green",
            )
        )


@app.command()
def show_prompt() -> None:
    """In ra system prompt đầy đủ (methodology + 4 laws + output format)."""
    console.print(build_system_prompt())


@app.command()
def laws() -> None:
    """In ra nội dung 4 định luật giao dịch đang được lưu trong agent's memory."""
    from importlib import resources

    text = (
        resources.files("smc_agent.knowledge")
        .joinpath("trading_laws.md")
        .read_text(encoding="utf-8")
    )
    console.print(text)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
