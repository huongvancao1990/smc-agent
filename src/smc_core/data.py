"""OHLCV data loading and validation utilities."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field, field_validator

REQUIRED_COLUMNS: tuple[str, ...] = ("time", "open", "high", "low", "close")


class Candle(BaseModel):
    """A single OHLCV candle."""

    index: int = Field(..., description="0-based row index in the source frame.")
    time: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("high")
    @classmethod
    def _high_ge_low(cls, v: float, info) -> float:
        low = info.data.get("low")
        if low is not None and v < low:
            raise ValueError(f"high ({v}) < low ({low}) at index {info.data.get('index')}")
        return v

    @property
    def is_bullish(self) -> bool:
        return self.close >= self.open

    @property
    def is_bearish(self) -> bool:
        return self.close < self.open

    @property
    def body_high(self) -> float:
        return max(self.open, self.close)

    @property
    def body_low(self) -> float:
        return min(self.open, self.close)


@dataclass(frozen=True)
class OHLCV:
    """Validated OHLCV container backed by a pandas DataFrame.

    The frame is guaranteed to have columns ``time, open, high, low, close, volume``
    and rows sorted by time ascending with a monotonic 0..N-1 integer index.
    """

    df: pd.DataFrame
    symbol: str = ""
    timeframe: str = ""

    def __len__(self) -> int:
        return len(self.df)

    def candle(self, i: int) -> Candle:
        row = self.df.iloc[i]
        return Candle(
            index=int(i),
            time=row["time"],
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row.get("volume", 0.0)),
        )

    def candles(self) -> Iterable[Candle]:
        for i in range(len(self.df)):
            yield self.candle(i)


def validate_ohlcv(df: pd.DataFrame, *, symbol: str = "", timeframe: str = "") -> OHLCV:
    """Validate and normalize a raw OHLCV DataFrame.

    Accepts columns case-insensitively. Adds ``volume=0`` if missing.
    """
    if df is None or len(df) == 0:
        raise ValueError("OHLCV dataframe is empty")

    rename_map = {c: c.lower() for c in df.columns}
    df = df.rename(columns=rename_map).copy()

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"OHLCV missing required columns: {missing}")

    if "volume" not in df.columns:
        df["volume"] = 0.0

    df["time"] = pd.to_datetime(df["time"], utc=False, errors="raise")
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col], errors="raise").astype(float)

    df = df.sort_values("time", kind="mergesort").reset_index(drop=True)

    bad = df[df["high"] < df["low"]]
    if len(bad) > 0:
        raise ValueError(f"Found {len(bad)} rows where high < low (e.g. index {bad.index[0]})")

    return OHLCV(
        df=df[["time", "open", "high", "low", "close", "volume"]],
        symbol=symbol,
        timeframe=timeframe,
    )


def load_ohlcv(path: str | Path, *, symbol: str = "", timeframe: str = "") -> OHLCV:
    """Load OHLCV from a CSV file. Expected columns: time, open, high, low, close[, volume]."""
    df = pd.read_csv(path)
    return validate_ohlcv(df, symbol=symbol, timeframe=timeframe)
