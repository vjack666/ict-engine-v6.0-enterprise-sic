#!/usr/bin/env python3
"""State Persistence - persistencia ligera de estado trading (posiciones/exposición)."""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Dict, Any, Optional
from pathlib import Path
import json
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

class StatePersistence:
    def __init__(self, 
                 base_path: Path, 
                 filename: str = "trading_state.json",
                 logger=None):
        self.base_path = base_path
        self.file = base_path / filename
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = get_unified_logger("StatePersistence")
        
        self._lock = threading.RLock()
        self._last_save = 0.0
        self.base_path.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        with self._lock:
            if not self.file.exists():
                return {}
            try:
                data = json.loads(self.file.read_text(encoding='utf-8'))
                if not isinstance(data, dict):
                    return {}
                return data
            except Exception as e:
                self.logger.error(f"Error cargando estado: {e}", "STATE")
                return {}

    def save(self, state: Dict[str, Any]) -> None:
        if not isinstance(state, dict):
            raise ValueError("state debe ser dict")
        with self._lock:
            try:
                tmp = self.file.with_suffix('.tmp')
                tmp.write_text(json.dumps(state, ensure_ascii=False, separators=(',', ':'), sort_keys=True), encoding='utf-8')
                tmp.replace(self.file)
                self._last_save = time.time()
            except Exception as e:
                self.logger.error(f"Error guardando estado: {e}", "STATE")

    def periodic_save(self, supplier, interval: float = 30.0, stop_flag: Optional[threading.Event] = None) -> None:
        while True:
            if stop_flag and stop_flag.is_set():
                break
            try:
                state = supplier()
                if isinstance(state, dict):
                    self.save(state)
            except Exception as e:
                self.logger.error(f"Periodic save error: {e}", "STATE")
            time.sleep(interval)

__all__ = ["StatePersistence"]
