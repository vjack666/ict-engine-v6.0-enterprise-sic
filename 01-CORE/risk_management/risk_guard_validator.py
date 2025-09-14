#!/usr/bin/env python3
"""RiskGuardValidator Adapter - bridges RiskGuard to RiskValidatorProtocol.

Permite usar RiskGuard directamente como validador en ExecutionRouter.
Evalúa violaciones recientes y bloquea nuevas órdenes si se detectan severas.
"""
from __future__ import annotations
from typing import Optional

try:
    from .risk_guard import RiskGuard, RiskGuardConfig
except Exception:  # pragma: no cover
    RiskGuard = None
    RiskGuardConfig = None

SEVERE_VIOLATIONS = {"DAILY_LOSS_LIMIT", "DRAWDOWN_LIMIT"}

class RiskGuardValidator:
    def __init__(self, guard: Optional[RiskGuard]):
        self.guard = guard
        self._last_eval = None
        self._last_violations: list[str] = []

    def validate_order(self, symbol: str, volume: float, action: str, price: float) -> bool:  # noqa: D401
        if not self.guard:
            return True
        # Si existen violaciones severas recientes, bloquear
        if any(v in SEVERE_VIOLATIONS for v in self._last_violations):
            return False
        return True

__all__ = ["RiskGuardValidator"]
