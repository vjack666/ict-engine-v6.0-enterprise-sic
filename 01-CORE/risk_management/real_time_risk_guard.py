"""Real Time Risk Guard (P0)
Evalúa cada orden/señal contra límites configurados.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
from protocols.logging_central_protocols import create_safe_logger

@dataclass
class RiskLimits:
    max_risk_per_trade_pct: float = 1.0
    max_daily_loss_pct: float = 5.0
    max_concurrent_positions: int = 5
    max_symbol_exposure_pct: float = 3.0

@dataclass
class RiskEvaluationResult:
    approved: bool
    reasons: list[str]
    computed_risk_pct: float = 0.0

class RealTimeRiskGuard:
    def __init__(self, limits: Optional[RiskLimits] = None):
        self.logger = create_safe_logger("RealTimeRiskGuard")
        self.limits = limits or RiskLimits()
        self._open_positions: Dict[str, Dict[str, Any]] = {}
        self._daily_loss_pct = 0.0

    def update_equity_context(self, daily_loss_pct: float) -> None:
        self._daily_loss_pct = daily_loss_pct

    def register_position(self, symbol: str, risk_pct: float) -> None:
        self._open_positions[symbol] = {"risk_pct": risk_pct}

    def close_position(self, symbol: str) -> None:
        self._open_positions.pop(symbol, None)

    def evaluate(self, order_context: Dict[str, Any]) -> RiskEvaluationResult:
        reasons: list[str] = []
        risk_pct = float(order_context.get("risk_pct", 0.0))
        symbol = str(order_context.get("symbol", "UNKNOWN"))

        if risk_pct <= 0:
            reasons.append("invalid_risk")
        if risk_pct > self.limits.max_risk_per_trade_pct:
            reasons.append("risk_per_trade_exceeded")
        if self._daily_loss_pct > self.limits.max_daily_loss_pct:
            reasons.append("daily_loss_limit")
        if len(self._open_positions) >= self.limits.max_concurrent_positions:
            reasons.append("max_concurrent_positions")
        symbol_exposure = self._open_positions.get(symbol, {}).get("risk_pct", 0.0) + risk_pct
        if symbol_exposure > self.limits.max_symbol_exposure_pct:
            reasons.append("symbol_exposure_limit")

        approved = len(reasons) == 0
        if approved:
            self.logger.info(f"✅ Risk approved {symbol} risk_pct={risk_pct}", "risk")
        else:
            self.logger.warning(f"❌ Risk rejected {symbol} reasons={reasons}", "risk")

        return RiskEvaluationResult(approved=approved, reasons=reasons, computed_risk_pct=risk_pct)

__all__ = [
    "RealTimeRiskGuard", "RiskLimits", "RiskEvaluationResult"
]
