"""Break of Structure (BOS) and Change of Character (CHoCH) detection.

Convention used (as drawn in the SMC infographic):

* BOS_BULL: in a bullish leg, price closes above the most recent **major swing
  high** -> trend continuation.
* BOS_BEAR: in a bearish leg, price closes below the most recent major swing
  low -> trend continuation.
* CHOCH_BULL: while bias is bearish, price closes above the most recent major
  swing high -> bias flips bullish (early reversal).
* CHOCH_BEAR: while bias is bullish, price closes below the most recent major
  swing low -> bias flips bearish.

The algorithm sweeps candles in order. A swing point only becomes a "reference
break level" once it is confirmed (i.e. ``swing.index + right`` candles have
elapsed). When a candle close pierces the most recent unbroken reference, an
event is emitted.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .data import OHLCV
from .swings import SwingPoint, find_swings
from .types import Bias, EventKind


@dataclass(frozen=True)
class StructureEvent:
    """A confirmed BOS or CHoCH event."""

    index: int
    time: pd.Timestamp
    price: float
    kind: EventKind
    broken_swing_index: int
    broken_swing_price: float
    new_bias: Bias

    @property
    def is_bos(self) -> bool:
        return self.kind in (EventKind.BOS_BULL, EventKind.BOS_BEAR)

    @property
    def is_choch(self) -> bool:
        return self.kind in (EventKind.CHOCH_BULL, EventKind.CHOCH_BEAR)


def find_structure_events(
    data: OHLCV,
    *,
    swings: list[SwingPoint] | None = None,
    left: int = 2,
    right: int = 2,
    initial_bias: Bias = Bias.NEUTRAL,
) -> list[StructureEvent]:
    """Detect BOS / CHoCH events sequentially.

    Args:
        data: OHLCV container.
        swings: optional pre-computed swings; if None, computed via ``find_swings``.
        left/right: passed to ``find_swings`` if ``swings`` is None.
        initial_bias: starting bias before the first event. Default NEUTRAL — the
            first break is classified as BOS regardless of direction.
    """
    if swings is None:
        swings = find_swings(data, left=left, right=right)

    df = data.df
    closes = df["close"].to_numpy()
    times = df["time"].tolist()
    n = len(df)

    swings_by_confirm: dict[int, list[SwingPoint]] = {}
    for sw in swings:
        confirm_at = sw.index + right
        swings_by_confirm.setdefault(confirm_at, []).append(sw)

    last_high: SwingPoint | None = None
    last_low: SwingPoint | None = None
    bias = initial_bias
    events: list[StructureEvent] = []

    for i in range(n):
        for sw in swings_by_confirm.get(i, []):
            if sw.kind == "high":
                last_high = sw
            else:
                last_low = sw

        c = float(closes[i])

        if last_high is not None and c > last_high.price:
            kind = EventKind.CHOCH_BULL if bias == Bias.BEARISH else EventKind.BOS_BULL
            events.append(
                StructureEvent(
                    index=i,
                    time=times[i],
                    price=c,
                    kind=kind,
                    broken_swing_index=last_high.index,
                    broken_swing_price=last_high.price,
                    new_bias=Bias.BULLISH,
                )
            )
            bias = Bias.BULLISH
            last_high = None
            continue

        if last_low is not None and c < last_low.price:
            kind = EventKind.CHOCH_BEAR if bias == Bias.BULLISH else EventKind.BOS_BEAR
            events.append(
                StructureEvent(
                    index=i,
                    time=times[i],
                    price=c,
                    kind=kind,
                    broken_swing_index=last_low.index,
                    broken_swing_price=last_low.price,
                    new_bias=Bias.BEARISH,
                )
            )
            bias = Bias.BEARISH
            last_low = None

    return events
