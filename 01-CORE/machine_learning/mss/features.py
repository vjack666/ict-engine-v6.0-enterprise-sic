from __future__ import annotations
from typing import Dict, Any, Any as _Any
import numpy as np

try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None  # type: ignore


def extract_mss_features(window: _Any) -> Dict[str, Any]:
    """Extract lightweight MSS features from a small OHLCV window.
    Returns dict with numeric features; robust to missing volume.
    """
    if window is None or len(window) < 5 or pd is None:
        return {
            'volatility': 0.0,
            'body_ratio': 0.0,
            'wick_imbalance': 0.0,
            'direction_consistency': 0.5,
            'gap_flag': 0.0,
        }

    closes = window['close'].to_numpy(dtype=float)
    opens = window['open'].to_numpy(dtype=float)
    highs = window['high'].to_numpy(dtype=float)
    lows = window['low'].to_numpy(dtype=float)

    bodies = np.abs(closes - opens)
    ranges = np.maximum(highs - lows, 1e-9)
    body_ratio = float(np.clip(np.mean(bodies / ranges), 0.0, 5.0))

    upper_wicks = highs - np.maximum(opens, closes)
    lower_wicks = np.minimum(opens, closes) - lows
    wick_imb = float(np.clip(np.mean(upper_wicks - lower_wicks), -1e6, 1e6))

    price_changes = np.diff(closes)
    if closes[-1] > opens[0]:
        direction_consistency = float((price_changes > 0).sum() / max(len(price_changes), 1))
    else:
        direction_consistency = float((price_changes < 0).sum() / max(len(price_changes), 1))

    # Simple gap flag akin to potential FVG
    gap_flag = 0.0
    for i in range(1, len(window) - 1):
        if (lows[i] > highs[i-1] and lows[i] > highs[i+1]) or (highs[i] < lows[i-1] and highs[i] < lows[i+1]):
            gap_flag = 1.0
            break

    # Volatility: mean TR
    tr = np.maximum(
        highs[1:] - lows[1:],
        np.maximum(np.abs(highs[1:] - closes[:-1]), np.abs(lows[1:] - closes[:-1]))
    )
    volatility = float(np.mean(tr)) if len(tr) else 0.0

    return {
        'volatility': volatility,
        'body_ratio': body_ratio,
        'wick_imbalance': wick_imb,
        'direction_consistency': direction_consistency,
        'gap_flag': gap_flag,
    }
