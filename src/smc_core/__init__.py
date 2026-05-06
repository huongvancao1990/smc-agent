"""smc_core — pure-Python Smart Money Concept (SMC) detection engine.

Detectors:
- swings:      fractal-based swing high/low detection
- structure:   Break of Structure (BOS) and Change of Character (CHoCH)
- liquidity:   Internal Liquidity (IDM) sweeps of minor swing highs/lows
- fvg:         Fair Value Gap (3-candle imbalance) detection
- order_block: bullish/bearish Order Block extraction
- setup:       1:3 Risk-Reward Buy/Sell setup builder

Public API mirrors the SMC infographic methodology:
    BOS -> IDM sweep -> retrace into Order Block / FVG -> entry signal -> SL/TP @ 1:3 RR.
"""

from .data import OHLCV, Candle, load_ohlcv, validate_ohlcv
from .fvg import FVG, find_fvgs
from .liquidity import IDMSweep, find_idm_sweeps
from .order_block import OrderBlock, find_order_blocks
from .setup import RRSetup, build_setups
from .structure import StructureEvent, find_structure_events
from .swings import SwingPoint, find_swings
from .types import Bias, EventKind, Side

__all__ = [
    "FVG",
    "OHLCV",
    "Bias",
    "Candle",
    "EventKind",
    "IDMSweep",
    "OrderBlock",
    "RRSetup",
    "Side",
    "StructureEvent",
    "SwingPoint",
    "build_setups",
    "find_fvgs",
    "find_idm_sweeps",
    "find_order_blocks",
    "find_structure_events",
    "find_swings",
    "load_ohlcv",
    "validate_ohlcv",
]
