"""Shared pytest fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))


@pytest.fixture(scope="session")
def sample_df() -> pd.DataFrame:
    """The deterministic NZDUSD-2H synthetic series used in examples and tests."""
    from generate_sample_data import build_series

    return build_series()


@pytest.fixture(scope="session")
def sample_ohlcv(sample_df: pd.DataFrame):
    from smc_core import validate_ohlcv

    return validate_ohlcv(sample_df, symbol="NZDUSD", timeframe="2h")
