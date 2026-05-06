"""End-to-end tests for the 1:3 RR setup builder."""

from __future__ import annotations

from smc_core import build_setups
from smc_core.types import Side


def test_sample_yields_one_buy_setup(sample_ohlcv):
    setups = build_setups(sample_ohlcv)
    assert len(setups) == 1
    s = setups[0]
    assert s.side == Side.BUY


def test_sample_setup_levels(sample_ohlcv):
    setups = build_setups(sample_ohlcv)
    s = setups[0]
    assert s.entry_index == 27
    assert abs(s.entry - 0.58220) < 1e-6
    # SL just below OB bottom (0.58200) by 0.05% = ~0.58171
    assert s.stop_loss < 0.58200
    assert abs(s.stop_loss - 0.58200 * (1 - 0.0005)) < 1e-6
    # TP at 3R
    risk = abs(s.entry - s.stop_loss)
    expected_tp = s.entry + 3.0 * risk
    assert abs(s.take_profit - expected_tp) < 1e-6


def test_sample_setup_has_overlapping_fvg(sample_ohlcv):
    setups = build_setups(sample_ohlcv)
    s = setups[0]
    assert s.overlapping_fvg is not None
    assert s.overlapping_fvg.side == Side.BUY


def test_sample_setup_notes_mention_all_steps(sample_ohlcv):
    setups = build_setups(sample_ohlcv)
    s = setups[0]
    blob = " | ".join(s.notes)
    for keyword in ("BOS", "IDM", "Order Block"):
        assert keyword in blob
