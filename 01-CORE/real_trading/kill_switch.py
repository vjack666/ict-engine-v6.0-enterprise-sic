#!/usr/bin/env python3
"""Kill Switch - parada global segura de trading."""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Optional, Dict, Any
import threading
import time

try:
    from protocols.logging_central_protocols import create_safe_logger, LogLevel  # type: ignore
except Exception:  # pragma: no cover
    def create_safe_logger(name: str, **_):  # type: ignore
        class _L:
            def info(self,m,c=""): print(f"[INFO][{name}][{c}] {m}")
            def warning(self,m,c=""): print(f"[WARN][{name}][{c}] {m}")
            def error(self,m,c=""): print(f"[ERR][{name}][{c}] {m}")
            def debug(self,m,c=""): print(f"[DBG][{name}][{c}] {m}")
        return _L()
    class LogLevel:  # type: ignore
        INFO = "INFO"

class KillSwitch:
    def __init__(self, logger=None):
        self._active = False
        self._reason: Optional[str] = None
        self._meta: Dict[str, Any] = {}
        self._ts: float = 0.0
        self._lock = threading.RLock()
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = get_unified_logger("KillSwitch")

    def engage(self, reason: str, **meta) -> None:
        if not reason:
            raise ValueError("reason requerido")
        with self._lock:
            if not self._active:
                self._active = True
                self._reason = reason
                self._meta = meta
                self._ts = time.time()
                self.logger.error(f"KILL SWITCH ACTIVADO reason={reason} meta={meta}", "KILL")

    def reset(self) -> None:
        with self._lock:
            if self._active:
                self.logger.warning(f"Rehabilitando trading (kill switch reset)", "KILL")
            self._active = False
            self._reason = None
            self._meta = {}
            self._ts = 0.0

    def is_active(self) -> bool:
        with self._lock:
            return self._active

    def status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'active': self._active,
                'reason': self._reason,
                'since': self._ts,
                'meta': dict(self._meta)
            }

__all__ = ["KillSwitch"]
