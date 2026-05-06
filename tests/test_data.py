"""Tests for the OHLCV data loader."""

from __future__ import annotations

import pandas as pd
import pytest

from smc_core import validate_ohlcv


def test_validate_ohlcv_happy_path():
    df = pd.DataFrame(
        {
            "time": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "open": [1.0, 2.0],
            "high": [1.5, 2.5],
            "low": [0.5, 1.5],
            "close": [1.2, 2.2],
        }
    )
    o = validate_ohlcv(df, symbol="X", timeframe="1d")
    assert len(o) == 2
    assert o.symbol == "X"
    assert o.timeframe == "1d"
    assert (o.df["volume"] == 0.0).all()


def test_validate_ohlcv_rejects_bad_high():
    df = pd.DataFrame(
        {
            "time": pd.to_datetime(["2026-01-01"]),
            "open": [1.0],
            "high": [0.5],
            "low": [1.0],
            "close": [0.8],
        }
    )
    with pytest.raises(ValueError, match="high"):
        validate_ohlcv(df)


def test_validate_ohlcv_rejects_missing_columns():
    df = pd.DataFrame({"time": pd.to_datetime(["2026-01-01"]), "open": [1.0]})
    with pytest.raises(ValueError, match="missing required columns"):
        validate_ohlcv(df)


def test_validate_ohlcv_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        validate_ohlcv(pd.DataFrame())


def test_validate_ohlcv_sorts_by_time():
    df = pd.DataFrame(
        {
            "time": pd.to_datetime(["2026-01-02", "2026-01-01"]),
            "open": [2.0, 1.0],
            "high": [2.5, 1.5],
            "low": [1.5, 0.5],
            "close": [2.2, 1.2],
        }
    )
    o = validate_ohlcv(df)
    assert o.df["time"].iloc[0] == pd.Timestamp("2026-01-01")
