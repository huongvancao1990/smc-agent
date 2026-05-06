"""Internal liquidity (IDM) sweep detection.

Per the SMC infographic, IDM = "thanh khoản bên trong, quét các đỉnh/đáy nhỏ
trước khi đi tiếp". Practically: between two consecutive *major* swing points
forming a leg, the most recent **minor** swing high/low (detected with a
shorter fractal window) is the IDM. After a BOS/CHoCH, price typically pulls
back and **sweeps** that minor level (wicks below the minor low for bullish
setups, wicks above the minor high for bearish setups) before continuing.

We expose a simple detector: for a target side (buy/sell), find a candle that
sweeps a minor swing low (buy) or high (sell) **after** a structural event,
without closing beyond it (a wick-only sweep).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .data import OHLCV
from .swings import find_swings
from .types import Side


@dataclass(frozen=True)
class IDMSweep:
    """A confirmed IDM (minor liquidity) sweep."""

    side: Side  # BUY = swept a minor low; SELL = swept a minor high
    sweep_index: int
    sweep_time: pd.Timestamp
    swept_level: float
    swept_swing_index: int
    after_event_index: int

    def __repr__(self) -> str:
        return f"IDM({self.side.value} sweep @ idx={self.sweep_index} level={self.swept_level:.5f})"


def find_idm_sweeps(
    data: OHLCV,
    *,
    after_index: int,
    side: Side,
    minor_left: int = 1,
    minor_right: int = 1,
    lookahead: int = 50,
) -> list[IDMSweep]:
    """Find IDM sweeps that occur after ``after_index``.

    Args:
        data: OHLCV container.
        after_index: only consider sweeps whose candle index > after_index.
        side: BUY -> looking for sweeps of a minor swing **low** (price wicks
            below it then closes back above). SELL -> mirror on minor swing **high**.
        minor_left/minor_right: fractal window for *minor* swings (smaller than
            structural swings; defaults to 1/1).
        lookahead: max number of candles after ``after_index`` to scan.
    """
    df = data.df
    n = len(df)
    end = min(n, after_index + 1 + max(0, lookahead))

    minor_swings = find_swings(data, left=minor_left, right=minor_right)
    target_kind = "low" if side == Side.BUY else "high"
    candidates = [s for s in minor_swings if s.kind == target_kind and s.index <= after_index]
    if not candidates:
        return []

    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    closes = df["close"].to_numpy()
    times = df["time"].tolist()

    sweeps: list[IDMSweep] = []
    used_swings: set[int] = set()

    for i in range(after_index + 1, end):
        for sw in candidates:
            if sw.index in used_swings:
                continue
            if side == Side.BUY:
                wick_through = lows[i] < sw.price
                close_back = closes[i] >= sw.price
            else:
                wick_through = highs[i] > sw.price
                close_back = closes[i] <= sw.price

            if wick_through and close_back:
                sweeps.append(
                    IDMSweep(
                        side=side,
                        sweep_index=int(i),
                        sweep_time=times[i],
                        swept_level=float(sw.price),
                        swept_swing_index=int(sw.index),
                        after_event_index=int(after_index),
                    )
                )
                used_swings.add(sw.index)

    return sweeps
