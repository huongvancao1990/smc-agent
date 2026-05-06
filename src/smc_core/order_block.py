"""Order Block (OB) detection.

A bullish Order Block is the **last bearish candle** before a strong impulsive
move up that breaks structure (BOS_BULL). Symmetrically, a bearish Order Block
is the last bullish candle before a BOS_BEAR.

The OB's price range is taken as ``[low, high]`` of that candle (some traders
use the body only — exposed via ``body_only=True``). The detector walks back
from the BOS candle until it finds the first opposite-color candle.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .data import OHLCV
from .structure import StructureEvent
from .types import EventKind, Side


@dataclass(frozen=True)
class OrderBlock:
    """A detected Order Block zone."""

    side: Side  # BUY -> bullish OB (demand); SELL -> bearish OB (supply)
    candle_index: int
    candle_time: pd.Timestamp
    top: float
    bottom: float
    triggered_event_index: int

    @property
    def mid(self) -> float:
        return (self.top + self.bottom) / 2.0

    def contains(self, price: float) -> bool:
        return self.bottom <= price <= self.top


def find_order_blocks(
    data: OHLCV,
    *,
    events: list[StructureEvent],
    body_only: bool = False,
    max_lookback: int = 20,
) -> list[OrderBlock]:
    """For each bullish/bearish BOS or CHoCH event, locate the originating OB.

    Args:
        data: OHLCV container.
        events: pre-computed structural events (BOS/CHoCH).
        body_only: if True, use the candle body (open/close) range; else the full wick range.
        max_lookback: how many candles to scan back from the event candle.
    """
    df = data.df
    opens = df["open"].to_numpy()
    closes = df["close"].to_numpy()
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    times = df["time"].tolist()

    obs: list[OrderBlock] = []

    for ev in events:
        bullish_event = ev.kind in (EventKind.BOS_BULL, EventKind.CHOCH_BULL)
        ob_side = Side.BUY if bullish_event else Side.SELL
        target_color_is_bearish = bullish_event

        ob_idx: int | None = None
        start = ev.index - 1
        stop = max(-1, ev.index - 1 - max_lookback)
        for i in range(start, stop, -1):
            o = opens[i]
            c = closes[i]
            is_bearish = c < o
            is_bullish = c > o
            if target_color_is_bearish and is_bearish:
                ob_idx = i
                break
            if (not target_color_is_bearish) and is_bullish:
                ob_idx = i
                break

        if ob_idx is None:
            continue

        if body_only:
            top = float(max(opens[ob_idx], closes[ob_idx]))
            bottom = float(min(opens[ob_idx], closes[ob_idx]))
        else:
            top = float(highs[ob_idx])
            bottom = float(lows[ob_idx])

        obs.append(
            OrderBlock(
                side=ob_side,
                candle_index=int(ob_idx),
                candle_time=times[ob_idx],
                top=top,
                bottom=bottom,
                triggered_event_index=int(ev.index),
            )
        )

    return obs
