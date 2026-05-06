"""Tests for the 4-laws filter."""

from __future__ import annotations

from smc_agent.laws import apply_trading_laws
from smc_core import build_setups


def test_sample_passes_all_laws(sample_ohlcv):
    setups = build_setups(sample_ohlcv)
    checks = apply_trading_laws(setups)
    assert len(checks) == 1
    c = checks[0]
    assert c.pass_all is True
    assert c.severity in ("ok", "caution")
    assert "chiu_trach_nhiem" in c.lessons_passed


def test_laws_with_no_setups():
    checks = apply_trading_laws([])
    assert checks == []
