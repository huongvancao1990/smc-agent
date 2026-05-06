"""Tests for Order Block detection."""

from __future__ import annotations

from smc_core import find_order_blocks, find_structure_events
from smc_core.types import Side


def test_bullish_ob_in_sample(sample_ohlcv):
    events = find_structure_events(sample_ohlcv)
    obs = find_order_blocks(sample_ohlcv, events=events)
    bull = [o for o in obs if o.side == Side.BUY]
    assert any(o.candle_index == 19 for o in bull), "Expected OB at idx 19 in sample data"


def test_ob_zone_bounds(sample_ohlcv):
    events = find_structure_events(sample_ohlcv)
    obs = find_order_blocks(sample_ohlcv, events=events)
    ob = next(o for o in obs if o.candle_index == 19)
    assert abs(ob.bottom - 0.58200) < 1e-6
    assert abs(ob.top - 0.58360) < 1e-6
