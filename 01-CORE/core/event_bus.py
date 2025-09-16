#!/usr/bin/env python3
"""
Event Bus - ICT Engine v6.0 Enterprise
Thread-safe publicador/suscriptor ligero para desacoplar módulos.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Callable, Dict, List, Any, DefaultDict
from collections import defaultdict
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

EventHandler = Callable[[str, Any], None]

class EventBus:
    def __init__(self, logger=None):
        self._subs: DefaultDict[str, List[EventHandler]] = defaultdict(list)
        self._lock = threading.RLock()
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = get_unified_logger("EventBus")
        
        self._events_published = 0
        self._events_failed = 0
        self._last_publish = 0.0

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        if not topic or not callable(handler):
            raise ValueError("topic y handler válidos requeridos")
        with self._lock:
            self._subs[topic].append(handler)
        self.logger.debug(f"Suscrito handler a topic={topic}", "EVENTBUS")

    def unsubscribe(self, topic: str, handler: EventHandler) -> None:
        with self._lock:
            handlers = self._subs.get(topic, [])
            if handler in handlers:
                handlers.remove(handler)
                self.logger.debug(f"Desuscrito handler topic={topic}", "EVENTBUS")

    def publish(self, topic: str, payload: Any) -> None:
        now = time.time()
        with self._lock:
            handlers = list(self._subs.get(topic, []))
        if not handlers:
            return
        for h in handlers:
            try:
                h(topic, payload)
                self._events_published += 1
            except Exception as e:
                self._events_failed += 1
                self.logger.error(f"Handler error topic={topic}: {e}", "EVENTBUS")
        self._last_publish = now

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'topics': len(self._subs),
                'handlers': sum(len(v) for v in self._subs.values()),
                'events_published': self._events_published,
                'events_failed': self._events_failed,
                'last_publish': self._last_publish
            }

__all__ = ["EventBus", "EventHandler"]
