#!/usr/bin/env python3
"""Account Sync Service - sincroniza información de cuenta periódicamente."""
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

class AccountSyncService:
    def __init__(self, 
                 executor, 
                 interval: float = 15.0,
                 logger=None):
        self.executor = executor
        self.interval = interval
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = get_unified_logger("AccountSyncService")
        
        self._last_snapshot: Dict[str, Any] = {}

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="AccountSync", daemon=True)
        self._thread.start()
        self.logger.info("AccountSync iniciado", "ACCOUNT")

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                snap = {}
                if hasattr(self.executor, 'get_account_snapshot'):
                    snap = self.executor.get_account_snapshot()  # type: ignore
                if isinstance(snap, dict) and snap:
                    self._last_snapshot = snap
            except Exception as e:
                self.logger.error(f"Sync error: {e}", "ACCOUNT")
            time.sleep(self.interval)

    def last(self) -> Dict[str, Any]:
        return dict(self._last_snapshot)

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self.logger.info("AccountSync detenido", "ACCOUNT")

__all__ = ["AccountSyncService"]
