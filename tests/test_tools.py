"""Tests for the LLM tool dispatcher."""

from __future__ import annotations

import json

from smc_agent.tools import build_tool_dispatcher


def test_load_and_full_pipeline(tmp_path, sample_df):
    csv = tmp_path / "sample.csv"
    sample_df.to_csv(csv, index=False)

    _ctx, dispatch = build_tool_dispatcher()
    out = dispatch("load_ohlcv_csv", {"path": str(csv), "symbol": "NZDUSD", "timeframe": "2h"})
    payload = json.loads(out)
    assert payload["ok"] is True
    assert payload["rows"] == len(sample_df)

    setups = json.loads(dispatch("build_rr_setup", {}))
    assert len(setups) == 1

    checks = json.loads(dispatch("apply_trading_laws", {}))
    assert len(checks) == 1
    assert checks[0]["pass_all"] is True


def test_detect_structure_includes_bos_bull(tmp_path, sample_df):
    csv = tmp_path / "sample.csv"
    sample_df.to_csv(csv, index=False)
    _ctx, dispatch = build_tool_dispatcher()
    dispatch("load_ohlcv_csv", {"path": str(csv)})
    events = json.loads(dispatch("detect_structure", {}))
    assert any(e["kind"] == "bos_bull" for e in events)


def test_unknown_tool_raises():
    _, dispatch = build_tool_dispatcher()
    try:
        dispatch("nope", {})
    except ValueError as e:
        assert "Unknown tool" in str(e)
    else:
        raise AssertionError("Expected ValueError")


def test_idm_sweep_via_dispatcher(tmp_path, sample_df):
    csv = tmp_path / "sample.csv"
    sample_df.to_csv(csv, index=False)
    _, dispatch = build_tool_dispatcher()
    dispatch("load_ohlcv_csv", {"path": str(csv)})
    sweeps = json.loads(dispatch("detect_idm_sweep", {"after_index": 21, "side": "buy"}))
    assert any(s["sweep_index"] == 26 for s in sweeps)
