#!/usr/bin/env python3
"""
📡 DATA FEED FALLBACK - ICT ENGINE v6.0 ENTERPRISE
=================================================
Gestor de resiliencia para feed de mercado:
- Monitorea timestamps de últimos ticks
- Cambia a feed secundario si hay silencio prolongado
- Puede activar modo simulación básica si ambos feeds fallan

API expuesta:
- update_tick(source: str, timestamp: float)
- get_active_source() -> str
- is_degraded() -> bool
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass
from typing import Optional, Dict
import time
from datetime import datetime, timezone

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except ImportError:  # fallback
    from smart_trading_logger import enviar_senal_log as _compat_log  # type: ignore
    class _MiniLogger:
        def info(self,m,c): _compat_log("INFO",m,c)
        def warning(self,m,c): _compat_log("WARNING",m,c)
        def error(self,m,c): _compat_log("ERROR",m,c)
        def debug(self,m,c): _compat_log("DEBUG",m,c)
    def create_safe_logger(component_name: str, **_): return _MiniLogger()  # type: ignore

@dataclass
class FeedFallbackConfig:
    max_silence_primary_sec: float = 8.0
    max_silence_secondary_sec: float = 10.0
    simulation_tick_interval_sec: float = 1.5

class DataFeedFallback:
    def __init__(self, config: Optional[FeedFallbackConfig] = None):
        self.config = config or FeedFallbackConfig()
        self.logger = get_unified_logger("DataFeedFallback")
        self._last_tick: Dict[str, float] = {}
        self._active: str = 'primary'
        self._simulation_price: float = 1.1000
        self._last_sim_tick: Optional[float] = None
        self._degraded: bool = False

    def update_tick(self, source: str, timestamp: Optional[float] = None, price: Optional[float] = None) -> None:
        ts = timestamp or time.time()
        self._last_tick[source] = ts
        if price is not None:
            self._simulation_price = price  # anclar

    def evaluate(self) -> None:
        now = time.time()
        primary_silence = now - self._last_tick.get('primary', 0)
        secondary_silence = now - self._last_tick.get('secondary', 0)
        self._degraded = False
        if self._active == 'primary' and primary_silence > self.config.max_silence_primary_sec:
            if secondary_silence < self.config.max_silence_secondary_sec:
                self.logger.warning("Primary feed silent switching->secondary", "FEED")
                self._active = 'secondary'
                self._degraded = True
            else:
                self.logger.error("Both feeds silent entering simulation", "FEED")
                self._active = 'simulation'
                self._degraded = True
        elif self._active == 'secondary':
            # intentar volver a primary si volvió
            if primary_silence < self.config.max_silence_primary_sec * 0.5:
                self.logger.info("Primary feed recovered switching->primary", "FEED")
                self._active = 'primary'
        elif self._active == 'simulation':
            if primary_silence < self.config.max_silence_primary_sec * 0.5:
                self.logger.info("Primary feed recovered leaving simulation", "FEED")
                self._active = 'primary'
        # generar tick simulado
        if self._active == 'simulation':
            if not self._last_sim_tick or (now - self._last_sim_tick) >= self.config.simulation_tick_interval_sec:
                # drift leve
                self._simulation_price += 0.0001 if int(now) % 2 == 0 else -0.0001
                self._last_sim_tick = now

    def get_active_source(self) -> str:
        self.evaluate()
        return self._active

    def is_degraded(self) -> bool:
        self.evaluate()
        return self._degraded

    def get_status(self) -> dict:
        self.evaluate()
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'active': self._active,
            'degraded': self._degraded,
            'last_primary': self._last_tick.get('primary'),
            'last_secondary': self._last_tick.get('secondary')
        }

__all__ = ['DataFeedFallback', 'FeedFallbackConfig']
