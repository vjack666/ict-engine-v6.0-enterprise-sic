#!/usr/bin/env python3
"""
📌 POSITION MANAGER - ICT ENGINE v6.0 ENTERPRISE
================================================

Responsabilidad:
- Mantener snapshot ligero de posiciones abiertas
- Calcular exposición neta por símbolo y global
- Validar límites rápidos antes de enviar orden (hook ExecutionRouter)
- Complementar RiskGuard (no duplicar reglas avanzadas)

Notas:
- Thread-safe mediante lock
- No depende de MT5 directamente (se puede sincronizar externamente)
- Optimizado para consultas frecuentes en tiempo real
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple
from threading import Lock
from datetime import datetime, timezone

try:
    from protocols.logging_central_protocols import create_safe_logger, LogLevel  # type: ignore
    _LOG_OK = True
except Exception:
    _LOG_OK = False
    def create_safe_logger(name: str, **_):  # type: ignore
        class _L:  # pragma: no cover
            def info(self,m,c=""): print(f"[INFO][{name}][{c}] {m}")
            def warning(self,m,c=""): print(f"[WARN][{name}][{c}] {m}")
            def error(self,m,c=""): print(f"[ERR][{name}][{c}] {m}")
            def debug(self,m,c=""): print(f"[DBG][{name}][{c}] {m}")
        return _L()
    class LogLevel:  # type: ignore
        INFO = "INFO"

@dataclass(frozen=True)
class Position:
    symbol: str
    direction: str  # 'buy' / 'sell'
    volume: float
    entry_price: float
    ticket: Optional[int]
    opened_at: datetime

class PositionManagerConfig:
    def __init__(self,
                 max_positions_global: int = 20,
                 max_positions_per_symbol: int = 8,
                 max_volume_per_symbol: float = 10.0,
                 max_total_volume: float = 50.0):
        self.max_positions_global = max_positions_global
        self.max_positions_per_symbol = max_positions_per_symbol
        self.max_volume_per_symbol = max_volume_per_symbol
        self.max_total_volume = max_total_volume

class PositionManager:
    def __init__(self, 
                 config: Optional[PositionManagerConfig] = None,
                 logger=None,
                 max_positions: int = 100,
                 max_exposure_per_symbol: float = 150000.0):
        self.config = config or PositionManagerConfig(
            max_positions_global=max_positions,
            max_volume_per_symbol=max_exposure_per_symbol
        )
        self._positions: Dict[int, Position] = {}
        self._lock = Lock()
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = get_unified_logger("PositionManager")
        
        # Compatibility properties
        self.max_exposure_per_symbol = max_exposure_per_symbol
        self._exposure = {}  # Symbol -> current exposure

    def get_symbol_exposure(self, symbol: str) -> float:
        """Get current exposure for a symbol"""
        with self._lock:
            return self._exposure.get(symbol, 0.0)
    
    def update_symbol_exposure(self, symbol: str, volume: float, direction: str) -> None:
        """Update exposure when position is added/removed"""
        with self._lock:
            current = self._exposure.get(symbol, 0.0)
            if direction.lower() == 'buy':
                self._exposure[symbol] = current + volume
            else:  # sell
                self._exposure[symbol] = current - volume

    # ---------------- Core Ops ----------------
    def add_position(self, ticket: int, symbol: str, direction: str, volume: float, entry_price: float) -> None:
        if volume <= 0:
            self.logger.warning(f"Ignorando add_position volumen<=0 ticket={ticket}", "POSITION")
            return
        pos = Position(symbol=symbol, direction=direction.lower(), volume=volume, entry_price=entry_price,
                       ticket=ticket, opened_at=datetime.now(timezone.utc))
        with self._lock:
            self._positions[ticket] = pos
            
        # Update exposure tracking
        self.update_symbol_exposure(symbol, volume, direction)
        self.logger.debug(f"Añadida posición ticket={ticket} {symbol} {direction} {volume}", "POSITION")

    def remove_position(self, ticket: int) -> None:
        with self._lock:
            if ticket in self._positions:
                pos = self._positions.pop(ticket, None)
                if pos:
                    # Update exposure tracking (reverse direction)
                    opposite_direction = 'sell' if pos.direction == 'buy' else 'buy'
                    self.update_symbol_exposure(pos.symbol, pos.volume, opposite_direction)
                self.logger.debug(f"Removida posición ticket={ticket}", "POSITION")

    def snapshot(self) -> List[Position]:
        with self._lock:
            return list(self._positions.values())

    # ---------------- Exposure Metrics ----------------
    def exposure_per_symbol(self) -> Dict[str, float]:
        exp: Dict[str, float] = {}
        with self._lock:
            for p in self._positions.values():
                exp[p.symbol] = exp.get(p.symbol, 0.0) + p.volume
        return exp

    def total_volume(self) -> float:
        with self._lock:
            return sum(p.volume for p in self._positions.values())

    def counts(self) -> Tuple[int, Dict[str, int]]:
        per_symbol: Dict[str, int] = {}
        with self._lock:
            for p in self._positions.values():
                per_symbol[p.symbol] = per_symbol.get(p.symbol, 0) + 1
            return len(self._positions), per_symbol

    # ---------------- Validation ----------------
    def validate_new_order(self, symbol: str, volume: float) -> Tuple[bool, str]:
        if volume <= 0:
            return False, "invalid_volume"
        with self._lock:
            current_positions = len(self._positions)
            if current_positions >= self.config.max_positions_global:
                return False, "max_positions_global"
            per_symbol_count = sum(1 for p in self._positions.values() if p.symbol == symbol)
            if per_symbol_count >= self.config.max_positions_per_symbol:
                return False, "max_positions_symbol"
            exp_symbol = sum(p.volume for p in self._positions.values() if p.symbol == symbol)
            if (exp_symbol + volume) > self.config.max_volume_per_symbol:
                return False, "max_volume_symbol"
            total_vol = sum(p.volume for p in self._positions.values())
            if (total_vol + volume) > self.config.max_total_volume:
                return False, "max_volume_total"
        return True, "ok"

__all__ = ["PositionManager", "PositionManagerConfig", "Position"]
