#!/usr/bin/env python3
"""Rate Limiter - ICT Engine v6.0 Enterprise
===========================================

Limitador ligero de órdenes por ventana usando Token Bucket.
Objetivos:
- Control global y por símbolo.
- Operaciones O(1) lock-minimized.
- Persistencia opcional de estado (best-effort) para diagnóstico.

Uso:
    rl = RateLimiter(global_rate=30, per_symbol_rate=10, window_sec=60)
    ok, reason = rl.try_consume(symbol="EURUSD")

Hook para ExecutionRouter:
    router.pre_order_hooks.append(lambda s,a,v,p: rl.hook_check(s))

Diseñado para evitar ráfagas accidentales que excedan límites de riesgo / broker.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Any
import time, threading, json, os

try:  # logger polimórfico
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except Exception:  # fallback
    def create_safe_logger(component_name: str, **_):  # type: ignore
        class _L:
            def info(self, m, c=""): print(f"[INFO][{component_name}]{c} {m}")
            def warning(self, m, c=""): print(f"[WARN][{component_name}]{c} {m}")
            def error(self, m, c=""): print(f"[ERROR][{component_name}]{c} {m}")
            def debug(self, m, c=""): pass
        return _L()

@dataclass
class RateLimiterConfig:
    global_rate: int = 30              # tokens por ventana
    per_symbol_rate: int = 10          # tokens por ventana por símbolo
    window_sec: int = 60               # tamaño de ventana (token bucket usa refill/time)
    persist_dir: Optional[str] = None  # carpeta para snapshot diagnóstico
    min_sleep_on_exhaust: float = 0.0  # reservado para futura retroalimentación

class RateLimiter:
    def __init__(self, config: Optional[RateLimiterConfig] = None) -> None:
        self.config = config or RateLimiterConfig()
        self.logger = get_unified_logger("RateLimiter")
        self._lock = threading.Lock()
        now = time.time()
        self._global_tokens = float(self.config.global_rate)
        self._symbol_tokens: Dict[str, float] = {}
        self._last_refill = now
        # pre-cálculo de tasa de refill (tokens por segundo)
        self._global_refill_rate = self.config.global_rate / self.config.window_sec if self.config.window_sec > 0 else 0.0
        self._symbol_refill_rate = self.config.per_symbol_rate / self.config.window_sec if self.config.window_sec > 0 else 0.0

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self._last_refill
        if elapsed <= 0:
            return
        self._last_refill = now
        if self._global_refill_rate > 0:
            self._global_tokens = min(float(self.config.global_rate), self._global_tokens + elapsed * self._global_refill_rate)
        if self._symbol_refill_rate > 0:
            for sym, current in list(self._symbol_tokens.items()):
                self._symbol_tokens[sym] = min(float(self.config.per_symbol_rate), current + elapsed * self._symbol_refill_rate)

    def try_consume(self, symbol: str, tokens: float = 1.0) -> Tuple[bool, Optional[str]]:
        if tokens <= 0:
            return True, None
        with self._lock:
            self._refill()
            # global
            if self._global_tokens < tokens:
                return False, "rate_limit_global"
            # symbol
            current_sym = self._symbol_tokens.get(symbol, float(self.config.per_symbol_rate))
            if current_sym < tokens:
                return False, f"rate_limit_symbol:{symbol}"
            # consume
            self._global_tokens -= tokens
            self._symbol_tokens[symbol] = current_sym - tokens
            return True, None

    def hook_check(self, symbol: str) -> Tuple[bool, Optional[str]]:
        ok, reason = self.try_consume(symbol, 1.0)
        if not ok:
            try:
                self.logger.warning(f"Rate limit bloquea orden: {reason}", "RATE")
            except Exception:
                pass
        return ok, reason

    def snapshot_state(self) -> Dict[str, Any]:
        with self._lock:
            data = {
                'ts': time.time(),
                'global_tokens': self._global_tokens,
                'symbol_tokens': {k: round(v,2) for k,v in self._symbol_tokens.items()}
            }
        if self.config.persist_dir:
            try:
                os.makedirs(self.config.persist_dir, exist_ok=True)
                path = os.path.join(self.config.persist_dir, 'rate_limiter_state.json')
                tmp = path + '.tmp'
                with open(tmp, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                os.replace(tmp, path)
            except Exception:
                pass
        return data

__all__ = ["RateLimiter", "RateLimiterConfig"]
