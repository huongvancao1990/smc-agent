"""Tests for FVG detection."""

from __future__ import annotations

import pandas as pd

from smc_core import find_fvgs, validate_ohlcv
from smc_core.types import Side


def test_bullish_fvg():
    df = pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=4, freq="2h"),
            "open": [1.0, 1.1, 1.5, 1.6],
            "high": [1.2, 1.3, 1.8, 1.7],
            "low": [0.9, 1.05, 1.4, 1.5],  # low[2]=1.4 > high[0]=1.2 -> bullish FVG
            "close": [1.1, 1.2, 1.7, 1.6],
        }
    )
    o = validate_ohlcv(df)
    fvgs = find_fvgs(o)
    bull = [f for f in fvgs if f.side == Side.BUY]
    assert any(f.middle_index == 1 and abs(f.bottom - 1.2) < 1e-9 for f in bull)


def test_bearish_fvg():
    df = pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=4, freq="2h"),
            "open": [2.0, 1.9, 1.5, 1.4],
            "high": [2.1, 2.0, 1.6, 1.5],  # high[2]=1.6 < low[0]=1.7 -> bearish FVG
            "low": [1.7, 1.6, 1.3, 1.2],
            "close": [1.9, 1.8, 1.4, 1.3],
        }
    )
    o = validate_ohlcv(df)
    fvgs = find_fvgs(o)
    bear = [f for f in fvgs if f.side == Side.SELL]
    assert any(f.middle_index == 1 for f in bear)


def test_fvg_filled_marker():
    df = pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=6, freq="2h"),
            "open": [1.0, 1.1, 1.5, 1.6, 1.5, 1.3],
            "high": [1.2, 1.3, 1.8, 1.7, 1.6, 1.35],
            "low": [0.9, 1.05, 1.4, 1.5, 1.15, 1.10],  # idx 4 low <= 1.4 fills the gap
            "close": [1.1, 1.2, 1.7, 1.6, 1.2, 1.15],
        }
    )
    o = validate_ohlcv(df)
    fvgs = find_fvgs(o, mark_filled_after=True)
    assert any(f.is_filled for f in fvgs)
