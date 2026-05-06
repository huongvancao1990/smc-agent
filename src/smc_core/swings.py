"""Fractal swing high/low detection.

A swing high at index ``i`` is a candle whose high is strictly greater than the
``left`` previous and ``right`` following candles' highs. Swing low is the
mirror condition on lows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from .data import OHLCV

SwingKind = Literal["high", "low"]


@dataclass(frozen=True)
class SwingPoint:
    """A confirmed swing high or low."""

    index: int
    time: pd.Timestamp
    price: float
    kind: SwingKind

    def __repr__(self) -> str:
        return f"Swing({self.kind} @ idx={self.index} t={self.time} px={self.price:.5f})"


def find_swings(data: OHLCV, *, left: int = 2, right: int = 2) -> list[SwingPoint]:
    """Detect fractal swing highs and lows.

    Args:
        data: validated OHLCV container.
        left: number of candles to the left that must be lower (high) / higher (low).
        right: number of candles to the right that must be lower (high) / higher (low).

    Returns:
        List of SwingPoint sorted by index. Endpoints (where right neighbours
        don't exist) are skipped: a swing is only emitted once it is fully
        confirmed by ``right`` candles.
    """
    if left < 1 or right < 1:
        raise ValueError("left and right must be >= 1")

    df = data.df
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    times = df["time"].tolist()

    n = len(df)
    swings: list[SwingPoint] = []

    for i in range(left, n - right):
        h = highs[i]
        is_high = all(h > highs[j] for j in range(i - left, i)) and all(
            h > highs[j] for j in range(i + 1, i + right + 1)
        )
        if is_high:
            swings.append(SwingPoint(index=i, time=times[i], price=float(h), kind="high"))
            continue

        low = lows[i]
        is_low = all(low < lows[j] for j in range(i - left, i)) and all(
            low < lows[j] for j in range(i + 1, i + right + 1)
        )
        if is_low:
            swings.append(SwingPoint(index=i, time=times[i], price=float(low), kind="low"))

    return swings
