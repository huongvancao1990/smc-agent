"""Generate a deterministic synthetic OHLCV CSV containing a clean BUY setup.

The generated series simulates the NZDUSD-2H illustration from the SMC
infographic. It is designed candle-by-candle to satisfy the detectors with
``swing_left=swing_right=2`` and ``minor_left=minor_right=1``:

    * Phase A (idx 0-7) : rally to a major swing high (idx 5, h=0.59100).
    * Phase B (idx 8-14): bear leg printing a major swing low (idx 14, l=0.57950).
    * Phase C (idx 15-17): bounce printing a fresh swing high (idx 17, h=0.58500).
    * Phase D (idx 18-20): pullback printing a minor swing low (idx 20, l=0.58150).
    * Phase E (idx 21)  : impulse closes > 0.58500 -> BOS_BULL.
    * Phase F (idx 22-23): bullish continuation, leaves a bullish FVG.
    * Phase G (idx 24-26): retrace; idx 26 wicks below 0.58150 (IDM sweep) and closes back.
    * Phase H (idx 27)  : pullback re-enters the originating bullish Order Block (idx 19).
                          This is the entry candle.
    * Phase I (idx 28-34): bullish continuation reaching the 3R target.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

SEQUENCE: list[tuple[float, float, float, float]] = [
    # (open, high, low, close)
    (0.58300, 0.58400, 0.58290, 0.58390),  # 0
    (0.58390, 0.58520, 0.58380, 0.58510),  # 1
    (0.58510, 0.58680, 0.58500, 0.58670),  # 2
    (0.58670, 0.58850, 0.58660, 0.58830),  # 3
    (0.58830, 0.59000, 0.58820, 0.58990),  # 4
    (0.58990, 0.59100, 0.58980, 0.59080),  # 5  MAJOR SWING HIGH
    (0.59080, 0.59090, 0.58970, 0.58990),  # 6
    (0.58990, 0.59000, 0.58820, 0.58840),  # 7
    (0.58840, 0.58870, 0.58700, 0.58720),  # 8
    (0.58720, 0.58740, 0.58550, 0.58570),  # 9
    (0.58570, 0.58590, 0.58400, 0.58420),  # 10
    (0.58420, 0.58440, 0.58280, 0.58300),  # 11
    (0.58300, 0.58320, 0.58150, 0.58170),  # 12
    (0.58170, 0.58200, 0.58030, 0.58050),  # 13
    (0.58050, 0.58080, 0.57950, 0.57970),  # 14 MAJOR SWING LOW
    (0.57970, 0.58200, 0.57960, 0.58180),  # 15
    (0.58180, 0.58400, 0.58170, 0.58380),  # 16
    (0.58380, 0.58500, 0.58370, 0.58480),  # 17 fresh swing high
    (0.58480, 0.58490, 0.58320, 0.58340),  # 18
    (0.58340, 0.58360, 0.58200, 0.58220),  # 19 last bearish candle before impulse → OB
    (0.58220, 0.58280, 0.58150, 0.58270),  # 20 minor swing low (l=0.58150)
    (0.58270, 0.58520, 0.58260, 0.58510),  # 21 BOS_BULL (close 0.58510 > 0.58500)
    (0.58510, 0.58700, 0.58500, 0.58680),  # 22 continuation
    (0.58680, 0.58820, 0.58670, 0.58800),  # 23 continuation (creates FVG with idx 21)
    (0.58800, 0.58820, 0.58400, 0.58420),  # 24 pullback
    (0.58420, 0.58440, 0.58280, 0.58300),  # 25 pullback
    (0.58300, 0.58320, 0.58140, 0.58220),  # 26 IDM SWEEP: wicks <0.58150 then closes back
    (0.58220, 0.58280, 0.58200, 0.58270),  # 27 ENTRY: low touches OB top (0.58360) zone
    (0.58270, 0.58360, 0.58260, 0.58350),  # 28 push up
    (0.58350, 0.58460, 0.58340, 0.58450),  # 29 reach near TP
    (0.58450, 0.58560, 0.58440, 0.58550),  # 30 past TP
    (0.58550, 0.58620, 0.58540, 0.58610),  # 31
    (0.58610, 0.58680, 0.58600, 0.58670),  # 32
    (0.58670, 0.58740, 0.58660, 0.58730),  # 33
    (0.58730, 0.58800, 0.58720, 0.58790),  # 34
]


def build_series() -> pd.DataFrame:
    rows = []
    t = pd.Timestamp("2026-01-01 00:00")
    step = pd.Timedelta(hours=2)
    for o, h, low, c in SEQUENCE:
        rows.append(
            {
                "time": t,
                "open": o,
                "high": h,
                "low": low,
                "close": c,
                "volume": 1000.0,
            }
        )
        t = t + step
    return pd.DataFrame(rows)


def main() -> None:
    out = Path(__file__).parent / "data" / "sample_nzdusd_2h.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df = build_series()
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} candles to {out}")


if __name__ == "__main__":
    main()
