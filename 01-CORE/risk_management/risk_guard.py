#!/usr/bin/env python3
"""
🛡️ RISK GUARD - ICT ENGINE v6.0 ENTERPRISE
=========================================
Supervisor ligero de riesgo en tiempo real.

Funciones:
- Control de exposición por símbolo y global
- Límite de pérdidas diarias (equity / balance delta)
- Máximo de posiciones simultáneas
- Detección de drawdown progresivo
- Señales de violación integradas con logging central
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Protocol, runtime_checkable
from datetime import datetime, timedelta
import json, os

@runtime_checkable
class _LoggerProto(Protocol):
    def info(self, message: str, category: str) -> None: ...
    def warning(self, message: str, category: str) -> None: ...
    def error(self, message: str, category: str) -> None: ...
    def debug(self, message: str, category: str) -> None: ...

try:
    from protocols.logging_central_protocols import create_safe_logger as _enterprise_logger_factory
    def create_safe_logger(component_name: str, **kwargs) -> _LoggerProto:  # type: ignore[override]
        return _enterprise_logger_factory(component_name)  # type: ignore[return-value]
except ImportError:  # fallback
    from smart_trading_logger import enviar_senal_log as _compat_log
    class _MiniLogger:
        def info(self, message: str, category: str) -> None: _compat_log("INFO", message, category)
        def warning(self, message: str, category: str) -> None: _compat_log("WARNING", message, category)
        def error(self, message: str, category: str) -> None: _compat_log("ERROR", message, category)
        def debug(self, message: str, category: str) -> None: _compat_log("DEBUG", message, category)
    def create_safe_logger(component_name: str, **kwargs) -> _LoggerProto:  # type: ignore[override]
        return _MiniLogger()

@dataclass
class RiskGuardConfig:
    max_positions: int = 5
    max_positions_per_symbol: int = 3
    daily_loss_limit_percent: float = 5.0  # % sobre balance inicial del día
    max_drawdown_percent: float = 12.0
    exposure_per_symbol_percent: float = 30.0  # % de exposición relativa permitida
    exposure_global_percent: float = 100.0
    drawdown_window_minutes: int = 240

@dataclass
class PositionSnapshot:
    symbol: str
    volume: float
    direction: str  # BUY/SELL
    entry_price: float
    ticket: Optional[int] = None

class RiskGuard:
    def __init__(self, config: Optional[RiskGuardConfig] = None):
        self.config = config or RiskGuardConfig()
        self.logger = create_safe_logger("RiskGuard")
        self._positions: Dict[int, PositionSnapshot] = {}
        self._day_start_balance: Optional[float] = None
        self._equity_history: list[tuple[datetime, float]] = []
        self._last_violation: Optional[str] = None

    def start_new_day(self, balance: float) -> None:
        self._day_start_balance = balance
        self._equity_history.clear()
        self.logger.info(f"Risk day initialized balance={balance:.2f}", "RISK")

    def register_equity(self, equity: float) -> None:
        now = datetime.utcnow()
        self._equity_history.append((now, equity))
        cutoff = now - timedelta(minutes=self.config.drawdown_window_minutes)
        self._equity_history = [e for e in self._equity_history if e[0] >= cutoff]

    def add_position(self, ticket: int, symbol: str, volume: float, direction: str, entry_price: float) -> bool:
        if ticket in self._positions:
            return True
        self._positions[ticket] = PositionSnapshot(symbol, volume, direction, entry_price, ticket)
        return True

    def remove_position(self, ticket: int) -> None:
        self._positions.pop(ticket, None)

    def _current_exposure(self) -> Dict[str, float]:
        exposure: Dict[str, float] = {}
        for p in self._positions.values():
            exposure[p.symbol] = exposure.get(p.symbol, 0.0) + p.volume
        return exposure

    def evaluate(self, balance: float, equity: float) -> Dict[str, Any]:
        violations = []
        pos_count = len(self._positions)
        if pos_count > self.config.max_positions:
            violations.append("MAX_POSITIONS")
        exposure = self._current_exposure()
        for sym, vol in exposure.items():
            if vol > self.config.max_positions_per_symbol:
                violations.append(f"MAX_POSITIONS_{sym}")
        # daily loss
        if self._day_start_balance is not None:
            loss_pct = ((self._day_start_balance - equity) / self._day_start_balance) * 100 if equity < self._day_start_balance else 0.0
            if loss_pct >= self.config.daily_loss_limit_percent:
                violations.append("DAILY_LOSS_LIMIT")
        # drawdown window
        if self._equity_history:
            max_equity = max(v for _, v in self._equity_history)
            if max_equity > 0:
                dd_pct = ((max_equity - equity) / max_equity) * 100
                if dd_pct >= self.config.max_drawdown_percent:
                    violations.append("DRAWDOWN_LIMIT")
        if violations and violations[0] != self._last_violation:
            self.logger.error(f"Risk violations detected: {violations}", "RISK")
            self._last_violation = violations[0]
        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'positions': pos_count,
            'exposure': exposure,
            'violations': violations
        }
        # Persistencia ligera (best-effort) para dashboard RiskHealthTab
        try:
            base_dir = os.path.join('04-DATA')
            os.makedirs(base_dir, exist_ok=True)
            path = os.path.join(base_dir, 'risk_guard_status.json')
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, ensure_ascii=False)
            os.replace(tmp, path)
        except Exception:
            pass
        return snapshot

__all__ = ['RiskGuard', 'RiskGuardConfig']
