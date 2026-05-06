"""Tests for IDM sweep detection."""

from __future__ import annotations

from smc_core import find_idm_sweeps
from smc_core.types import Side


def test_idm_sweep_after_bos_bull(sample_ohlcv):
    sweeps = find_idm_sweeps(sample_ohlcv, after_index=21, side=Side.BUY)
    assert len(sweeps) >= 1
    s = sweeps[0]
    assert s.sweep_index == 26
    assert abs(s.swept_level - 0.58150) < 1e-6
