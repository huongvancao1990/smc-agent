"""Smoke tests for the Typer CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_cli_show_prompt_runs():
    proc = subprocess.run(
        [sys.executable, "-m", "smc_agent", "show-prompt"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stderr
    assert "SMC Trading Agent" in proc.stdout


def test_cli_laws_runs():
    proc = subprocess.run(
        [sys.executable, "-m", "smc_agent", "laws"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stderr
    assert "Murphy" in proc.stdout
    assert "Kidlin" in proc.stdout
    assert "Wilson" in proc.stdout
    assert "Gilbert" in proc.stdout


def test_cli_analyze_no_llm(tmp_path, sample_df):
    csv = tmp_path / "sample.csv"
    sample_df.to_csv(csv, index=False)
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "smc_agent",
            "analyze",
            "--csv",
            str(csv),
            "--symbol",
            "NZDUSD",
            "--timeframe",
            "2h",
            "--no-llm",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert proc.returncode == 0, proc.stderr
    assert "BUY" in proc.stdout
