from __future__ import annotations
from typing import Any, Dict, Optional, Tuple

# Centralized wrappers around CHoCH historical memory to avoid duplication across patterns
try:
    from .choch_historical_memory import (
        adjust_confidence_with_memory,
        predict_target_based_on_history,
        calculate_historical_success_rate,
        find_similar_choch_in_history,
    )
    CHOCH_MEMORY_AVAILABLE = True
except Exception:
    # Fallback stubs keep call sites simple
    CHOCH_MEMORY_AVAILABLE = False
    def adjust_confidence_with_memory(base_confidence: float, symbol: str, timeframe: str, break_level: float) -> float:
        return float(base_confidence)
    def predict_target_based_on_history(symbol: str, timeframe: str, direction: str, break_level: float, default_target: Optional[float] = None) -> Optional[float]:
        return default_target
    def calculate_historical_success_rate(symbol: str, timeframe: str, direction: Optional[str] = None) -> float:
        return 0.0
    def find_similar_choch_in_history(symbol: str, timeframe: str, direction: Optional[str] = None, break_level_range: Optional[Tuple[float, float]] = None):
        return []


def estimate_break_level_from_swings(data: Any, direction: str, lookback: int = 20) -> float:
    """Generic swing-based estimator for CHoCH break level.
    direction: 'BULLISH'|'BEARISH'|'buy'|'sell'
    """
    try:
        recent = data.tail(lookback)
        if direction.lower() in ("buy", "bullish"):
            return float(recent['high'].max())
        elif direction.lower() in ("sell", "bearish"):
            return float(recent['low'].min())
        return float(recent['close'].iloc[-1])
    except Exception:
        try:
            return float(data['close'].iloc[-1])
        except Exception:
            return 0.0


def apply_choch_adjustments(base_confidence: float,
                             symbol: str,
                             timeframe: str,
                             direction: str,
                             break_level: float,
                             max_bonus: float = 10.0,
                             default_target: Optional[float] = None) -> Tuple[float, Optional[float], float]:
    """Return (adjusted_confidence, target_hint, bonus_applied)."""
    adjusted = adjust_confidence_with_memory(base_confidence, symbol, timeframe, break_level)
    raw_bonus = float(adjusted) - float(base_confidence)
    bonus = max(-max_bonus, min(max_bonus, raw_bonus))
    final_conf = max(0.0, min(100.0, float(base_confidence) + bonus))

    dir_str = 'BULLISH' if direction.lower() in ("buy","bullish") else ('BEARISH' if direction.lower() in ("sell","bearish") else 'NEUTRAL')
    target_hint = predict_target_based_on_history(symbol, timeframe, dir_str, break_level, default_target=default_target)

    return final_conf, target_hint, bonus
