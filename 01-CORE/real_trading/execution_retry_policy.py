"""Execution Retry Policy

Pequeño wrapper para reintentar ejecuciones temporales (network / busy).
Evita reintentos agresivos con backoff incremental y jitter opcional.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass
from typing import Callable, Any, Optional, Tuple
import time
import random

try:
    from smart_trading_logger import SmartTradingLogger  # type: ignore
except Exception:  # pragma: no cover
    SmartTradingLogger = None  # type: ignore


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 0.5
    max_delay: float = 3.0
    jitter: bool = True
    retry_exceptions: Tuple[type, ...] = (Exception,)


class ExecutionRetryPolicy:
    def __init__(self, config: Optional[RetryConfig] = None, logger: Optional[Any] = None) -> None:
        self.config = config or RetryConfig()
        self.logger = logger or (SmartTradingLogger("RetryPolicy") if SmartTradingLogger else None)  # type: ignore

    def _log(self, msg: str, level: str = "info") -> None:
        if self.logger:
            try:
                getattr(self.logger, level, self.logger.info)(msg, "execution_retry")
            except Exception:  # pragma: no cover
                pass

    def run(self, func: Callable[[], Any]) -> Any:
        attempt = 0
        delay = self.config.base_delay
        while True:
            attempt += 1
            try:
                return func()
            except self.config.retry_exceptions as e:  # type: ignore
                if attempt >= self.config.max_attempts:
                    self._log(f"Retry agotado ({attempt}) - {e}", "error")
                    raise
                self._log(f"Retry intento {attempt} error: {e} -> esperando {delay:.2f}s", "warning")
                time.sleep(delay + (random.uniform(0, delay/4) if self.config.jitter else 0.0))
                delay = min(delay * 1.7, self.config.max_delay)

__all__ = ["ExecutionRetryPolicy", "RetryConfig"]
