#!/usr/bin/env python3
"""RiskGuardValidator Adapter - bridges RiskGuard to RiskValidatorProtocol.

Permite usar RiskGuard directamente como validador en ExecutionRouter.
Evalúa violaciones recientes y bloquea nuevas órdenes si se detectan severas.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Optional, List, Any
import time, json, os

try:
    from .risk_guard import RiskGuard, RiskGuardConfig  # type: ignore
except Exception:  # pragma: no cover
    class RiskGuard:  # minimal stub para tipado
        pass
    class RiskGuardConfig:  # minimal stub
        pass

try:  # logger opcional
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except Exception:
    def create_safe_logger(component_name: str, **_):  # type: ignore
        class _L:
            def info(self, m, c=""): pass
            def warning(self, m, c=""): print(f"[WARN][{component_name}] {m}")
            def error(self, m, c=""): print(f"[ERR][{component_name}] {m}")
        return _L()

SEVERE_VIOLATIONS = {"DAILY_LOSS_LIMIT", "DRAWDOWN_LIMIT"}

class RiskGuardValidator:
    """Adaptador ligero para usar RiskGuard como validador.

    Estrategia:
    - No recalcula internamente; se apoya en snapshots o actualizaciones externas.
    - Permite actualizar violaciones vía `update_violations`.
    - Puede leer snapshot `04-DATA/risk_guard_status.json` cada N segundos si no hay guard directo.
    """
    def __init__(self, guard: Optional[RiskGuard], snapshot_refresh_sec: float = 5.0):
        self.guard = guard
        self._last_violations: List[str] = []
        self._last_snapshot_read: float = 0.0
        self._snapshot_refresh_sec = snapshot_refresh_sec
        self._snapshot_path = os.path.join('04-DATA', 'risk_guard_status.json')
        self.logger = get_unified_logger("RiskGuardValidator")

    # ----------------- Actualización Externa -----------------
    def update_violations(self, violations: List[str]) -> None:
        self._last_violations = list(violations[-5:])

    def _maybe_refresh_from_snapshot(self) -> None:
        if self.guard is not None:  # si hay instancia real, asumir otra capa la alimenta
            return
        now = time.time()
        if (now - self._last_snapshot_read) < self._snapshot_refresh_sec:
            return
        self._last_snapshot_read = now
        try:
            if os.path.exists(self._snapshot_path):
                with open(self._snapshot_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                v = data.get('violations')
                if isinstance(v, list):
                    self._last_violations = [str(x) for x in v][-5:]
        except Exception:
            pass

    # ----------------- Protocolo de Validación -----------------
    def validate_order(self, symbol: str, volume: float, action: str, price: float) -> bool:  # noqa: D401
        # refrescar snapshot si no hay guard directo
        self._maybe_refresh_from_snapshot()
        if any(v in SEVERE_VIOLATIONS for v in self._last_violations):
            try:
                self.logger.warning(f"Orden bloqueada por violaciones: {self._last_violations}", "RISK")
            except Exception:
                pass
            return False
        return True

__all__ = ["RiskGuardValidator"]
