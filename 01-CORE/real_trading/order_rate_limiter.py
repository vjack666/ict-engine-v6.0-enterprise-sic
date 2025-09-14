#!/usr/bin/env python3
"""
⏱️ ORDER RATE LIMITER - ICT ENGINE v6.0 ENTERPRISE
==================================================
Controla frecuencia de órdenes para evitar bursts peligrosos.
- Ventana deslizante por símbolo
- Ventana deslizante global
- Métricas internas
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Tuple
from threading import Lock
import time

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

@dataclass
class RateLimiterConfig:
    per_symbol_window_sec: int = 60
    per_symbol_max: int = 12
    global_window_sec: int = 60
    global_max: int = 60
    cooldown_sec: int = 5  # micro-pausa si se bloquea

class OrderRateLimiter:
    def __init__(self, 
                 config: RateLimiterConfig | None = None,
                 logger=None,
                 max_orders_per_minute: int = 180,
                 per_symbol_limit: int = 30):
        
        # Create config with parameters if not provided
        if config is None:
            config = RateLimiterConfig(
                per_symbol_max=per_symbol_limit,
                global_max=max_orders_per_minute
            )
        
        self.config = config
        self._per_symbol: Dict[str, Deque[float]] = {}
        self._global: Deque[float] = deque()
        self._lock = Lock()
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = create_safe_logger("OrderRateLimiter", log_level=getattr(LogLevel, 'INFO', None))
        
        self._blocked_counts = {"symbol": 0, "global": 0}

    def _purge(self, now: float):
        gs = self.config.global_window_sec
        while self._global and (now - self._global[0]) > gs:
            self._global.popleft()
        for sym, dq in list(self._per_symbol.items()):
            ps = self.config.per_symbol_window_sec
            while dq and (now - dq[0]) > ps:
                dq.popleft()
            if not dq:
                self._per_symbol.pop(sym, None)

    def allow(self, symbol: str) -> Tuple[bool, str]:
        now = time.time()
        with self._lock:
            self._purge(now)
            dq_sym = self._per_symbol.setdefault(symbol, deque())
            # check symbol
            if len(dq_sym) >= self.config.per_symbol_max:
                self._blocked_counts["symbol"] += 1
                self.logger.warning(f"Rate limit SYMBOL excedido {symbol}", "RATE_LIMIT")
                return False, "symbol_limit"
            # check global
            if len(self._global) >= self.config.global_max:
                self._blocked_counts["global"] += 1
                self.logger.warning("Rate limit GLOBAL excedido", "RATE_LIMIT")
                return False, "global_limit"
            # commit
            dq_sym.append(now)
            self._global.append(now)
            return True, "ok"

    def metrics(self) -> Dict[str, int]:
        with self._lock:
            return {
                'active_symbols': len(self._per_symbol),
                'global_in_window': len(self._global),
                'blocked_symbol': self._blocked_counts['symbol'],
                'blocked_global': self._blocked_counts['global']
            }

__all__ = ["OrderRateLimiter", "RateLimiterConfig"]
