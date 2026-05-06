"""Fair Value Gap (FVG) / imbalance detection.

A bullish FVG forms on a 3-candle window (i-2, i-1, i) when:
    low[i] > high[i-2]
The gap is the price range (high[i-2], low[i]).

A bearish FVG forms when:
    high[i] < low[i-2]
The gap is (high[i], low[i-2]).

We optionally mark an FVG as "filled" once a later candle's price re-enters
the gap.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .data import OHLCV
from .types import Side


@dataclass(frozen=True)
class FVG:
    """A detected Fair Value Gap."""

    side: Side  # BUY-side FVG (bullish gap) supports longs; SELL-side supports shorts
    middle_index: int
    middle_time: pd.Timestamp
    top: float
    bottom: float
    filled_index: int | None = None

    @property
    def is_filled(self) -> bool:
        return self.filled_index is not None

    @property
    def mid(self) -> float:
        return (self.top + self.bottom) / 2.0

    def contains(self, price: float) -> bool:
        return self.bottom <= price <= self.top


def find_fvgs(data: OHLCV, *, mark_filled_after: bool = True) -> list[FVG]:
    """Detect all bullish/bearish FVGs in the series.

    Args:
        data: OHLCV container.
        mark_filled_after: if True, scan candles after each gap to set ``filled_index``
            once price re-enters the range.
    """
    df = data.df
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    times = df["time"].tolist()
    n = len(df)

    gaps: list[FVG] = []

    for i in range(2, n):
        h_prev2 = highs[i - 2]
        l_prev2 = lows[i - 2]
        h = highs[i]
        low = lows[i]

        if low > h_prev2:
            gaps.append(
                FVG(
                    side=Side.BUY,
                    middle_index=int(i - 1),
                    middle_time=times[i - 1],
                    top=float(low),
                    bottom=float(h_prev2),
                )
            )
        elif h < l_prev2:
            gaps.append(
                FVG(
                    side=Side.SELL,
                    middle_index=int(i - 1),
                    middle_time=times[i - 1],
                    top=float(l_prev2),
                    bottom=float(h),
                )
            )

    if not mark_filled_after:
        return gaps

    filled: list[FVG] = []
    for gap in gaps:
        fill_idx: int | None = None
        for j in range(gap.middle_index + 2, n):
            if gap.side == Side.BUY:
                if lows[j] <= gap.top:
                    fill_idx = int(j)
                    break
            else:
                if highs[j] >= gap.bottom:
                    fill_idx = int(j)
                    break
        filled.append(
            FVG(
                side=gap.side,
                middle_index=gap.middle_index,
                middle_time=gap.middle_time,
                top=gap.top,
                bottom=gap.bottom,
                filled_index=fill_idx,
            )
        )
    return filled
