"""1:3 Risk-Reward Buy/Sell setup builder.

Combines the SMC primitives into the 5-step process from the infographic:

    1. Identify trend (BOS).
    2. Find the IDM that gets swept.
    3. Locate the originating Order Block (and overlapping FVG, if any).
    4. Wait for a price-action confirmation: pullback re-enters the OB/FVG.
    5. Place entry with SL beyond the OB; TP at 3R.

The output ``RRSetup`` describes a complete trade plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .data import OHLCV
from .fvg import FVG, find_fvgs
from .liquidity import IDMSweep, find_idm_sweeps
from .order_block import OrderBlock, find_order_blocks
from .structure import StructureEvent, find_structure_events
from .types import EventKind, Side


@dataclass(frozen=True)
class RRSetup:
    """A 1:3 RR Buy or Sell setup."""

    side: Side
    triggered_event: StructureEvent
    idm_sweep: IDMSweep
    order_block: OrderBlock
    overlapping_fvg: FVG | None
    entry_index: int
    entry_time: pd.Timestamp
    entry: float
    stop_loss: float
    take_profit: float
    rr_ratio: float = 3.0
    notes: list[str] = field(default_factory=list)

    @property
    def risk_per_unit(self) -> float:
        return abs(self.entry - self.stop_loss)

    @property
    def reward_per_unit(self) -> float:
        return abs(self.take_profit - self.entry)

    def to_dict(self) -> dict:
        return {
            "side": self.side.value,
            "triggered_event": {
                "kind": self.triggered_event.kind.value,
                "index": self.triggered_event.index,
                "time": str(self.triggered_event.time),
                "price": self.triggered_event.price,
                "broken_swing_price": self.triggered_event.broken_swing_price,
            },
            "idm_sweep": {
                "sweep_index": self.idm_sweep.sweep_index,
                "sweep_time": str(self.idm_sweep.sweep_time),
                "swept_level": self.idm_sweep.swept_level,
            },
            "order_block": {
                "candle_index": self.order_block.candle_index,
                "top": self.order_block.top,
                "bottom": self.order_block.bottom,
            },
            "overlapping_fvg": (
                None
                if self.overlapping_fvg is None
                else {
                    "middle_index": self.overlapping_fvg.middle_index,
                    "top": self.overlapping_fvg.top,
                    "bottom": self.overlapping_fvg.bottom,
                }
            ),
            "entry_index": self.entry_index,
            "entry_time": str(self.entry_time),
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "rr_ratio": self.rr_ratio,
            "risk_per_unit": self.risk_per_unit,
            "reward_per_unit": self.reward_per_unit,
            "notes": list(self.notes),
        }


def _find_overlapping_fvg(fvgs: list[FVG], ob: OrderBlock) -> FVG | None:
    """Return the FVG (same side as OB) that overlaps the OB price range, if any."""
    for f in fvgs:
        if f.side != ob.side:
            continue
        if f.middle_index < ob.candle_index:
            continue
        if f.bottom <= ob.top and f.top >= ob.bottom:
            return f
    return None


def _detect_pullback_entry(
    data: OHLCV,
    *,
    side: Side,
    ob: OrderBlock,
    after_index: int,
    lookahead: int = 50,
) -> int | None:
    """Find the first candle after ``after_index`` that re-enters the OB zone."""
    df = data.df
    n = len(df)
    end = min(n, after_index + 1 + lookahead)
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()

    for i in range(after_index + 1, end):
        if side == Side.BUY:
            if lows[i] <= ob.top and lows[i] >= ob.bottom * 0.999:
                return int(i)
        else:
            if highs[i] >= ob.bottom and highs[i] <= ob.top * 1.001:
                return int(i)
    return None


def build_setups(
    data: OHLCV,
    *,
    rr_ratio: float = 3.0,
    swing_left: int = 2,
    swing_right: int = 2,
    minor_left: int = 1,
    minor_right: int = 1,
    sweep_lookahead: int = 50,
    pullback_lookahead: int = 50,
    sl_buffer_pct: float = 0.0005,
    body_only_ob: bool = False,
) -> list[RRSetup]:
    """Build all 1:3 RR Buy and Sell setups in the data series.

    Pipeline:
        1. Detect structure events (BOS/CHoCH).
        2. For each event, infer side: BOS_BULL/CHOCH_BULL -> BUY; BOS_BEAR/CHOCH_BEAR -> SELL.
        3. Find IDM sweep AFTER the event in the corresponding direction.
        4. Locate the originating Order Block.
        5. Optionally overlap with an FVG.
        6. Detect first pullback that re-enters the OB; that candle's open is the entry.
        7. SL = OB.bottom (BUY) / OB.top (SELL) -+ ``sl_buffer_pct`` of price.
        8. TP = entry +/- rr_ratio * |entry - SL|.
    """
    events = find_structure_events(data, left=swing_left, right=swing_right)
    if not events:
        return []

    obs = find_order_blocks(data, events=events, body_only=body_only_ob)
    obs_by_event = {ob.triggered_event_index: ob for ob in obs}

    fvgs = find_fvgs(data)

    setups: list[RRSetup] = []

    df = data.df
    opens = df["open"].to_numpy()
    times = df["time"].tolist()

    for ev in events:
        side = Side.BUY if ev.kind in (EventKind.BOS_BULL, EventKind.CHOCH_BULL) else Side.SELL

        sweeps = find_idm_sweeps(
            data,
            after_index=ev.index,
            side=side,
            minor_left=minor_left,
            minor_right=minor_right,
            lookahead=sweep_lookahead,
        )
        if not sweeps:
            continue
        sweep = sweeps[0]

        ob = obs_by_event.get(ev.index)
        if ob is None:
            continue

        fvg = _find_overlapping_fvg(fvgs, ob)

        entry_idx = _detect_pullback_entry(
            data,
            side=side,
            ob=ob,
            after_index=sweep.sweep_index,
            lookahead=pullback_lookahead,
        )
        if entry_idx is None:
            continue

        entry_price = float(opens[entry_idx])

        if side == Side.BUY:
            sl = ob.bottom * (1.0 - sl_buffer_pct)
            risk = abs(entry_price - sl)
            tp = entry_price + rr_ratio * risk
        else:
            sl = ob.top * (1.0 + sl_buffer_pct)
            risk = abs(entry_price - sl)
            tp = entry_price - rr_ratio * risk

        notes = [
            f"BOS/CHoCH at idx {ev.index} ({ev.kind.value}) broke swing @ {ev.broken_swing_price:.5f}",
            f"IDM sweep at idx {sweep.sweep_index} took level {sweep.swept_level:.5f}",
            f"Order Block idx {ob.candle_index}: [{ob.bottom:.5f}, {ob.top:.5f}]",
        ]
        if fvg is not None:
            notes.append(
                f"Overlapping FVG idx {fvg.middle_index}: [{fvg.bottom:.5f}, {fvg.top:.5f}]"
            )

        setups.append(
            RRSetup(
                side=side,
                triggered_event=ev,
                idm_sweep=sweep,
                order_block=ob,
                overlapping_fvg=fvg,
                entry_index=int(entry_idx),
                entry_time=times[entry_idx],
                entry=entry_price,
                stop_loss=float(sl),
                take_profit=float(tp),
                rr_ratio=float(rr_ratio),
                notes=notes,
            )
        )

    return setups
