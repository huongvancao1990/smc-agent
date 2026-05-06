"""LLM-callable tools wrapping the smc_core engine.

Each tool is described as an OpenAI-style function schema and dispatches to a
pure-Python implementation that operates on a cached OHLCV context.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from smc_core import (
    OHLCV,
    build_setups,
    find_fvgs,
    find_idm_sweeps,
    find_order_blocks,
    find_structure_events,
    find_swings,
    load_ohlcv,
)
from smc_core.types import Side

from .laws import apply_trading_laws

# Tool schema (OpenAI-compatible function calling format)
TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "load_ohlcv_csv",
            "description": (
                "Load an OHLCV time series from a CSV file. Required columns: "
                "time, open, high, low, close[, volume]. Sets the active OHLCV "
                "context for subsequent SMC tools."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the CSV file."},
                    "symbol": {"type": "string", "description": "Symbol label.", "default": ""},
                    "timeframe": {
                        "type": "string",
                        "description": "Timeframe label (e.g., '2h').",
                        "default": "",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_swings",
            "description": "Detect fractal swing highs and lows in the loaded OHLCV.",
            "parameters": {
                "type": "object",
                "properties": {
                    "left": {"type": "integer", "default": 2, "minimum": 1},
                    "right": {"type": "integer", "default": 2, "minimum": 1},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_structure",
            "description": (
                "Detect Break of Structure (BOS) and Change of Character (CHoCH) events."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "left": {"type": "integer", "default": 2, "minimum": 1},
                    "right": {"type": "integer", "default": 2, "minimum": 1},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_idm_sweep",
            "description": (
                "Find IDM (internal liquidity) sweeps after a structural event index. "
                "Side BUY scans for swept minor lows; SELL scans for swept minor highs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "after_index": {"type": "integer", "minimum": 0},
                    "side": {"type": "string", "enum": ["buy", "sell"]},
                    "lookahead": {"type": "integer", "default": 50, "minimum": 1},
                },
                "required": ["after_index", "side"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_fvg",
            "description": "Detect bullish/bearish Fair Value Gaps (3-candle imbalances).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_order_block",
            "description": (
                "For each detected structural event, locate the originating Order Block."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "body_only": {"type": "boolean", "default": False},
                    "max_lookback": {"type": "integer", "default": 20, "minimum": 1},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_rr_setup",
            "description": (
                "End-to-end pipeline that combines structure, IDM sweep, OB, FVG and "
                "pullback to produce a list of complete 1:3 RR setups."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "rr_ratio": {"type": "number", "default": 3.0, "minimum": 1.0},
                    "swing_left": {"type": "integer", "default": 2, "minimum": 1},
                    "swing_right": {"type": "integer", "default": 2, "minimum": 1},
                    "minor_left": {"type": "integer", "default": 1, "minimum": 1},
                    "minor_right": {"type": "integer", "default": 1, "minimum": 1},
                    "sweep_lookahead": {"type": "integer", "default": 50, "minimum": 1},
                    "pullback_lookahead": {"type": "integer", "default": 50, "minimum": 1},
                    "sl_buffer_pct": {"type": "number", "default": 0.0005, "minimum": 0.0},
                    "body_only_ob": {"type": "boolean", "default": False},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_trading_laws",
            "description": (
                "Filter the most recently built setups through the 4 laws "
                "(Murphy/Kidlin/Wilson/Gilbert) and the 4 trader lessons. "
                "Returns severity (ok/caution/reject) for each setup."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


@dataclass
class AgentContext:
    """Mutable state shared across tool calls within a single agent run."""

    ohlcv: OHLCV | None = None
    last_setups: list = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.last_setups is None:
            self.last_setups = []


def _ohlcv_required(ctx: AgentContext) -> OHLCV:
    if ctx.ohlcv is None:
        raise RuntimeError("No OHLCV loaded. Call `load_ohlcv_csv` first.")
    return ctx.ohlcv


def build_tool_dispatcher(
    ctx: AgentContext | None = None,
) -> tuple[AgentContext, Callable[[str, dict[str, Any]], str]]:
    """Build a tool dispatcher closure.

    Returns:
        (ctx, dispatch) — ctx is the shared state, dispatch(name, args) -> JSON str.
    """
    ctx = ctx or AgentContext()

    def _serialize(obj: Any) -> Any:
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dataclass_fields__"):
            return {k: _serialize(getattr(obj, k)) for k in obj.__dataclass_fields__}
        if isinstance(obj, (list, tuple)):
            return [_serialize(x) for x in obj]
        if isinstance(obj, dict):
            return {k: _serialize(v) for k, v in obj.items()}
        if hasattr(obj, "value") and hasattr(obj, "name"):
            return obj.value
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return obj

    def dispatch(name: str, args: dict[str, Any]) -> str:
        if name == "load_ohlcv_csv":
            ohlcv = load_ohlcv(
                args["path"],
                symbol=args.get("symbol", ""),
                timeframe=args.get("timeframe", ""),
            )
            ctx.ohlcv = ohlcv
            return json.dumps(
                {
                    "ok": True,
                    "symbol": ohlcv.symbol,
                    "timeframe": ohlcv.timeframe,
                    "rows": len(ohlcv),
                    "first_time": str(ohlcv.df["time"].iloc[0]),
                    "last_time": str(ohlcv.df["time"].iloc[-1]),
                }
            )

        if name == "detect_swings":
            ohlcv = _ohlcv_required(ctx)
            swings = find_swings(
                ohlcv,
                left=int(args.get("left", 2)),
                right=int(args.get("right", 2)),
            )
            return json.dumps([_serialize(s) for s in swings])

        if name == "detect_structure":
            ohlcv = _ohlcv_required(ctx)
            events = find_structure_events(
                ohlcv,
                left=int(args.get("left", 2)),
                right=int(args.get("right", 2)),
            )
            return json.dumps([_serialize(e) for e in events])

        if name == "detect_idm_sweep":
            ohlcv = _ohlcv_required(ctx)
            side = Side(args["side"])
            sweeps = find_idm_sweeps(
                ohlcv,
                after_index=int(args["after_index"]),
                side=side,
                lookahead=int(args.get("lookahead", 50)),
            )
            return json.dumps([_serialize(s) for s in sweeps])

        if name == "detect_fvg":
            ohlcv = _ohlcv_required(ctx)
            fvgs = find_fvgs(ohlcv)
            return json.dumps([_serialize(f) for f in fvgs])

        if name == "detect_order_block":
            ohlcv = _ohlcv_required(ctx)
            events = find_structure_events(ohlcv)
            obs = find_order_blocks(
                ohlcv,
                events=events,
                body_only=bool(args.get("body_only", False)),
                max_lookback=int(args.get("max_lookback", 20)),
            )
            return json.dumps([_serialize(o) for o in obs])

        if name == "build_rr_setup":
            ohlcv = _ohlcv_required(ctx)
            setups = build_setups(
                ohlcv,
                rr_ratio=float(args.get("rr_ratio", 3.0)),
                swing_left=int(args.get("swing_left", 2)),
                swing_right=int(args.get("swing_right", 2)),
                minor_left=int(args.get("minor_left", 1)),
                minor_right=int(args.get("minor_right", 1)),
                sweep_lookahead=int(args.get("sweep_lookahead", 50)),
                pullback_lookahead=int(args.get("pullback_lookahead", 50)),
                sl_buffer_pct=float(args.get("sl_buffer_pct", 0.0005)),
                body_only_ob=bool(args.get("body_only_ob", False)),
            )
            ctx.last_setups = setups
            return json.dumps([s.to_dict() for s in setups])

        if name == "apply_trading_laws":
            checks = apply_trading_laws(ctx.last_setups or [])
            return json.dumps([c.to_dict() for c in checks])

        raise ValueError(f"Unknown tool: {name}")

    return ctx, dispatch
