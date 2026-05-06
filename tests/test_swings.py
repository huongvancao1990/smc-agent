"""Tests for fractal swing detection."""

from __future__ import annotations

import pandas as pd
import pytest

from smc_core import find_swings, validate_ohlcv


def _ohlcv(highs, lows):
    n = len(highs)
    df = pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=n, freq="2h"),
            "open": [(h + low) / 2 for h, low in zip(highs, lows, strict=True)],
            "high": list(highs),
            "low": list(lows),
            "close": [(h + low) / 2 for h, low in zip(highs, lows, strict=True)],
        }
    )
    return validate_ohlcv(df)


def test_find_swings_simple_high_and_low():
    highs = [1.0, 2.0, 3.0, 2.0, 1.0, 1.5, 2.0, 2.5, 2.0, 1.5]
    lows = [0.5, 1.5, 2.5, 1.5, 0.5, 1.0, 1.5, 2.0, 1.5, 1.0]
    o = _ohlcv(highs, lows)
    swings = find_swings(o, left=2, right=2)
    high_idx = [s.index for s in swings if s.kind == "high"]
    low_idx = [s.index for s in swings if s.kind == "low"]
    assert 2 in high_idx  # peak at idx 2
    assert 4 in low_idx  # trough at idx 4


def test_find_swings_skips_endpoints():
    """The first ``left`` and last ``right`` candles can never be swings."""
    highs = [3.0, 2.0, 1.0, 2.0, 3.0]
    lows = [2.0, 1.5, 0.5, 1.5, 2.0]
    o = _ohlcv(highs, lows)
    swings = find_swings(o, left=2, right=2)
    assert all(2 <= s.index <= 2 for s in swings)


def test_find_swings_invalid_window():
    highs = [1.0, 2.0, 3.0]
    lows = [0.5, 1.0, 2.0]
    o = _ohlcv(highs, lows)
    with pytest.raises(ValueError):
        find_swings(o, left=0, right=2)
