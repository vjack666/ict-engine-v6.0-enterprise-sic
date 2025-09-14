"""Dynamic Risk Adjuster
=======================
Ajusta dinámicamente parámetros de riesgo (lotes, max concurrent trades,
stop multipliers) según condiciones de mercado y salud de la cuenta.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class RiskAdjustmentDecision:
    lot_multiplier: float
    max_concurrent_trades: int
    stop_multiplier: float
    reason: str


class DynamicRiskAdjuster:
    def __init__(self,
                 base_lot: float = 0.1,
                 base_max_trades: int = 5,
                 base_stop_multiplier: float = 1.0) -> None:
        self.base_lot = base_lot
        self.base_max_trades = base_max_trades
        self.base_stop_multiplier = base_stop_multiplier

    def adjust(self, market_conditions: Dict[str, Any], account_health: Dict[str, Any]) -> RiskAdjustmentDecision:
        vol = market_conditions.get("volatility", 1.0)  # 1.0 baseline
        trend_conf = market_conditions.get("trend_confidence", 0.5)  # 0..1
        status = account_health.get("status", "OK")
        drawdown_factor = 1.0
        if status == "WARNING":
            drawdown_factor = 0.7
        elif status == "CRITICAL":
            drawdown_factor = 0.4

        # Volatilidad alta reduce lotes, confianza alta aumenta ligeramente
        lot_multiplier = drawdown_factor * (1.0 / max(0.5, min(vol, 2.0))) * (0.9 + trend_conf * 0.3)
        stop_multiplier = self.base_stop_multiplier * (1.0 + (vol - 1.0) * 0.5)
        max_trades = int(self.base_max_trades * drawdown_factor)
        reason = f"status={status} vol={vol:.2f} trend_conf={trend_conf:.2f}"
        return RiskAdjustmentDecision(
            lot_multiplier=max(0.1, lot_multiplier),
            max_concurrent_trades=max(1, max_trades),
            stop_multiplier=max(0.5, stop_multiplier),
            reason=reason
        )


__all__ = ["DynamicRiskAdjuster", "RiskAdjustmentDecision"]
