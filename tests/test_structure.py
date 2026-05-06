"""Tests for BOS / CHoCH detection."""

from __future__ import annotations

from smc_core import find_structure_events
from smc_core.types import EventKind


def test_sample_data_yields_bos_bull(sample_ohlcv):
    events = find_structure_events(sample_ohlcv)
    assert len(events) >= 1
    bos = [e for e in events if e.kind == EventKind.BOS_BULL]
    assert any(e.index == 21 for e in bos), "Expected BOS_BULL at idx 21 in sample data"


def test_sample_data_break_level(sample_ohlcv):
    events = find_structure_events(sample_ohlcv)
    bos = next(e for e in events if e.kind == EventKind.BOS_BULL and e.index == 21)
    assert abs(bos.broken_swing_price - 0.58500) < 1e-6
