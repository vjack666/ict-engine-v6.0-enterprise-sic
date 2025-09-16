"""Connection Watchdog
======================
Supervisa estabilidad de la conexión (ej. MT5 / broker API) y expone
métricas de latencia, reconexiones y disponibilidad.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timezone
import threading
import time
import random


@dataclass
class ConnectionStats:
    last_check: datetime
    last_latency_ms: float
    consecutive_failures: int
    reconnect_attempts: int
    is_connected: bool


class ConnectionWatchdog:
    def __init__(self,
                 ping_function: Optional[Callable[[], float]] = None,
                 reconnect_function: Optional[Callable[[], bool]] = None,
                 check_interval: int = 15,
                 max_failures_before_reconnect: int = 3) -> None:
        self.ping_function = ping_function or self._default_ping
        self.reconnect_function = reconnect_function or self._default_reconnect
        self.check_interval = check_interval
        self.max_failures_before_reconnect = max_failures_before_reconnect
        self._stats = ConnectionStats(datetime.now(timezone.utc), 0.0, 0, 0, True)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._callbacks: list[Callable[[Dict[str, Any]], None]] = []

    def start(self) -> bool:
        if self._thread and self._thread.is_alive():
            return True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop_event.set()

    def add_callback(self, cb: Callable[[Dict[str, Any]], None]) -> None:
        self._callbacks.append(cb)

    def get_stats(self) -> Dict[str, Any]:
        s = self._stats
        return {
            "last_check": s.last_check,
            "last_latency_ms": s.last_latency_ms,
            "consecutive_failures": s.consecutive_failures,
            "reconnect_attempts": s.reconnect_attempts,
            "is_connected": s.is_connected
        }

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            latency_ms = None
            success = False
            try:
                latency_ms = self.ping_function()
                success = True
            except Exception:
                success = False

            self._stats.last_check = datetime.now(timezone.utc)
            if success and latency_ms is not None:
                self._stats.last_latency_ms = latency_ms
                self._stats.consecutive_failures = 0
                self._stats.is_connected = True
            else:
                self._stats.consecutive_failures += 1
                if self._stats.consecutive_failures >= self.max_failures_before_reconnect:
                    if self.reconnect_function():
                        self._stats.reconnect_attempts += 1
                        self._stats.consecutive_failures = 0
                        self._stats.is_connected = True
                    else:
                        self._stats.is_connected = False

            payload = self.get_stats()
            for cb in list(self._callbacks):
                try:
                    cb(payload)
                except Exception:
                    pass
            self._stop_event.wait(self.check_interval)

    # ------------------------------------------------------------------
    def _default_ping(self) -> float:
        # Simula ping en ms, ocasionalmente error
        if random.random() < 0.1:
            raise RuntimeError("simulated ping failure")
        time.sleep(0.01)
        return random.uniform(20.0, 120.0)

    def _default_reconnect(self) -> bool:
        time.sleep(0.05)
        return random.random() > 0.2


__all__ = ["ConnectionWatchdog", "ConnectionStats"]
