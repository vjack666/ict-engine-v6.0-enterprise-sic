"""Lightweight Position Sizer

Complementa AutoPositionSizer ofreciendo una interfaz mínima y determinística
para casos donde se requiere un sizing rápido basado en riesgo fijo o
volatilidad simple (ATR-like) sin dependencias externas.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import math

try:
    from smart_trading_logger import SmartTradingLogger  # type: ignore
except Exception:  # pragma: no cover
    SmartTradingLogger = None  # type: ignore


@dataclass
class SizingResult:
    volume: float
    risk_amount: float
    basis: str
    valid: bool
    message: str = ""


class PositionSizer:
    def __init__(self, account_balance_provider, logger: Optional[Any] = None,
                 max_leverage: float = 30.0, max_symbol_volume: float = 250000.0) -> None:
        self.account_balance_provider = account_balance_provider  # callable -> float
        self.max_leverage = max_leverage
        self.max_symbol_volume = max_symbol_volume
        self.logger = logger or (SmartTradingLogger("PositionSizer") if SmartTradingLogger else None)  # type: ignore

    def _log(self, level: str, msg: str) -> None:
        if self.logger:
            try:
                getattr(self.logger, level, self.logger.info)(msg, "position_sizer")
            except Exception:  # pragma: no cover
                pass

    def fixed_risk(self, symbol: str, price: float, stop_distance: float, risk_pct: float = 0.01) -> SizingResult:
        if stop_distance <= 0 or price <= 0:
            return SizingResult(0.0, 0.0, "fixed", False, "Invalid price/stop")
        balance = float(self.account_balance_provider() or 0.0)
        risk_amount = balance * risk_pct
        # naive pip value assumption: 0.0001 for FX majors
        pip_value = 0.0001
        volume = (risk_amount / (stop_distance * pip_value)) if stop_distance > 0 else 0.0
        volume = min(volume, self.max_symbol_volume)
        if volume <= 0:
            return SizingResult(0.0, risk_amount, "fixed", False, "Computed zero volume")
        self._log("info", f"Sizing fixed_risk {symbol} -> volume={volume:.2f} risk={risk_amount:.2f}")
        return SizingResult(volume, risk_amount, "fixed", True, "OK")

    def volatility_adjusted(self, symbol: str, price: float, recent_range: float, target_vol_fraction: float = 0.002) -> SizingResult:
        if price <= 0 or recent_range <= 0:
            return SizingResult(0.0, 0.0, "volatility", False, "Invalid price/range")
        balance = float(self.account_balance_provider() or 0.0)
        risk_amount = balance * target_vol_fraction
        # approximate sizing: risk_amount / (recent_range * price fraction)
        volume = risk_amount / max(recent_range * price, 1e-8)
        volume = min(volume, self.max_symbol_volume)
        if volume <= 0:
            return SizingResult(0.0, risk_amount, "volatility", False, "Computed zero volume")
        self._log("info", f"Sizing volatility {symbol} -> volume={volume:.2f} risk={risk_amount:.2f}")
        return SizingResult(volume, risk_amount, "volatility", True, "OK")

__all__ = ["PositionSizer", "SizingResult"]
