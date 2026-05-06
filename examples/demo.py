"""End-to-end demo: load sample data, run all detectors, print one BUY setup.

Run::

    python examples/demo.py

Does not require Ollama or any LLM to be running — it exercises ``smc_core``
and the deterministic 4-laws filter only.
"""

from __future__ import annotations

import json
from pathlib import Path

from smc_agent.laws import apply_trading_laws
from smc_core import build_setups, load_ohlcv


def main() -> None:
    csv = Path(__file__).parent / "data" / "sample_nzdusd_2h.csv"
    if not csv.exists():
        from .generate_sample_data import main as gen

        gen()

    ohlcv = load_ohlcv(csv, symbol="NZDUSD", timeframe="2h")
    print(f"[loaded] {len(ohlcv)} candles ({ohlcv.symbol} {ohlcv.timeframe})")

    setups = build_setups(ohlcv, rr_ratio=3.0)
    print(f"[setups] {len(setups)} setup(s) detected\n")

    checks = apply_trading_laws(setups)

    for i, (setup, check) in enumerate(zip(setups, checks, strict=True)):
        print(f"=== Setup #{i} · {setup.side.value.upper()} · severity={check.severity} ===")
        print(json.dumps(setup.to_dict(), indent=2, default=str))
        print(f"  Laws check: {check.to_dict()}")
        print()


if __name__ == "__main__":
    main()
