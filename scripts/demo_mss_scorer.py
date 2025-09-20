import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add 01-CORE to sys.path so we can import machine_learning
ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / '01-CORE'
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from machine_learning.mss.service import MSSShiftScorer  # type: ignore


def make_window(n=80, base=1.1000, scale=0.0005):
    rng = np.random.default_rng(42)
    # Random walk closes
    deltas = rng.normal(0, scale, size=n)
    closes = base + np.cumsum(deltas)
    opens = np.r_[closes[0], closes[:-1]]
    highs = np.maximum(opens, closes) + rng.normal(0, scale * 0.5, size=n).clip(min=0)
    lows = np.minimum(opens, closes) - rng.normal(0, scale * 0.5, size=n).clip(min=0)
    volume = rng.integers(500, 2000, size=n)
    idx = pd.date_range(end=datetime.now(), periods=n, freq="15min")
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volume,
    }, index=idx)
    return df


def main():
    scorer = MSSShiftScorer()
    window = make_window(n=100, base=1.1000, scale=0.0006)

    symbols = ["EURUSD", "USDJPY", "XAUUSD"]
    timeframes = ["M15", "H1"]

    print("\nMSSShiftScorer demo (confidence normalized by symbol/timeframe)\n")
    for sym in symbols:
        for tf in timeframes:
            res = scorer.score(window, symbol=sym, timeframe=tf)
            # Access internal helpers just for demo transparency
            pip = scorer._get_pip_value(sym)
            ref = scorer._ref_pips_by_timeframe(tf)
            print(f"{sym:6s} {tf:3s} | prob_shift={res['prob_shift']:.3f}  confidence={res['confidence']:.3f}  (pip={pip}, ref_pips={ref})")
    print("\nDone.\n")


if __name__ == "__main__":
    main()
