"""Shared enums and lightweight type aliases for smc_core."""

from __future__ import annotations

from enum import Enum


class Side(str, Enum):
    """Setup direction."""

    BUY = "buy"
    SELL = "sell"


class Bias(str, Enum):
    """Market bias / trend direction."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class EventKind(str, Enum):
    """Structural event taxonomy used by the detectors."""

    BOS_BULL = "bos_bull"
    BOS_BEAR = "bos_bear"
    CHOCH_BULL = "choch_bull"
    CHOCH_BEAR = "choch_bear"
