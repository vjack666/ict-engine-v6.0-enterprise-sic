#!/usr/bin/env python3
"""Session State Manager - ICT Engine v6.0 Enterprise
===================================================
Persistencia ligera de estado de sesión para permitir warm restart seguro.

Alcance:
- Registrar órdenes exitosas (ticket, symbol, action, volume, timestamps).
- Registrar fallos finales para análisis (motivo principal).
- Persistir snapshot incremental JSON + log append JSONL.
- Restaurar estado de tickets previos al reinicio (solo metadata, no re-sincroniza broker).

Estrategia de rendimiento:
- Escrituras atómicas (archivo temporal + replace) para snapshot.
- Buffer en memoria para eventos y flush periódico configurable.

Integración sugerida en ExecutionRouter:
- Al ejecutar orden OK -> record_success(...)
- Al fallar final -> record_failure(...)
- Al apagado -> flush() y persist_snapshot()
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import time, json, threading

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except Exception:  # fallback básico
    def create_safe_logger(component_name: str, **_):  # type: ignore
        class _L:
            def info(self, m, c=""): print(f"[INFO][{component_name}]{c} {m}")
            def warning(self, m, c=""): print(f"[WARN][{component_name}]{c} {m}")
            def error(self, m, c=""): print(f"[ERR][{component_name}]{c} {m}")
        return _L()

@dataclass
class SessionStateConfig:
    base_dir: str = "04-DATA/session_state"
    snapshot_filename: str = "session_snapshot.json"
    events_filename: str = "session_events.jsonl"
    max_events_in_memory: int = 500
    flush_interval_sec: float = 15.0

@dataclass
class OrderRecord:
    ticket: int
    symbol: str
    action: str
    volume: float
    placed_at: float
    extra: Dict[str, Any] = field(default_factory=dict)

class SessionStateManager:
    def __init__(self, config: Optional[SessionStateConfig] = None) -> None:
        self.config = config or SessionStateConfig()
        self.logger = create_safe_logger("SessionStateManager")
        self._lock = threading.Lock()
        self._orders: Dict[int, OrderRecord] = {}
        self._failed: List[Dict[str, Any]] = []
        self._events_buffer: List[Dict[str, Any]] = []
        self._last_flush = time.time()
        self._base = Path(self.config.base_dir)
        self._base.mkdir(parents=True, exist_ok=True)
        self._snapshot_path = self._base / self.config.snapshot_filename
        self._events_path = self._base / self.config.events_filename
        self._load_snapshot()

    # -------------------- Carga Inicial --------------------
    def _load_snapshot(self) -> None:
        if not self._snapshot_path.exists():
            return
        try:
            data = json.loads(self._snapshot_path.read_text(encoding="utf-8"))
            orders = data.get("orders", {})
            for k, v in orders.items():
                try:
                    ticket = int(k)
                    self._orders[ticket] = OrderRecord(
                        ticket=ticket,
                        symbol=str(v.get("symbol","")),
                        action=str(v.get("action","")),
                        volume=float(v.get("volume",0)),
                        placed_at=float(v.get("placed_at",0)),
                        extra=v.get("extra",{}) if isinstance(v.get("extra",{}), dict) else {}
                    )
                except Exception:
                    continue
        except Exception:
            pass

    # -------------------- Registro --------------------
    def record_success(self, ticket: int, symbol: str, action: str, volume: float, extra: Optional[Dict[str, Any]] = None) -> None:
        rec = OrderRecord(ticket, symbol, action, volume, time.time(), extra or {})
        with self._lock:
            self._orders[ticket] = rec
            self._events_buffer.append({
                'ts': time.time(), 'type': 'ORDER_OK', 'ticket': ticket,
                'symbol': symbol, 'action': action, 'volume': volume
            })
            self._maybe_flush_locked()

    def record_failure(self, symbol: str, action: str, volume: float, reason: str) -> None:
        with self._lock:
            self._failed.append({'ts': time.time(), 'symbol': symbol, 'action': action, 'volume': volume, 'reason': reason})
            self._events_buffer.append({
                'ts': time.time(), 'type': 'ORDER_FAIL', 'symbol': symbol,
                'action': action, 'volume': volume, 'reason': reason
            })
            self._maybe_flush_locked()

    # -------------------- Persistencia --------------------
    def _maybe_flush_locked(self) -> None:
        now = time.time()
        if (now - self._last_flush) < self.config.flush_interval_sec and len(self._events_buffer) < self.config.max_events_in_memory:
            return
        self._last_flush = now
        buf = list(self._events_buffer)
        self._events_buffer.clear()
        if not buf:
            return
        try:
            with open(self._events_path, 'a', encoding='utf-8') as f:
                for ev in buf:
                    f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def persist_snapshot(self) -> None:
        with self._lock:
            data = {
                'generated': time.time(),
                'orders': {str(k): {
                    'symbol': v.symbol,
                    'action': v.action,
                    'volume': v.volume,
                    'placed_at': v.placed_at,
                    'extra': v.extra
                } for k,v in self._orders.items()},
                'failed_recent': self._failed[-50:]
            }
        try:
            tmp = self._snapshot_path.with_suffix('.tmp')
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            tmp.replace(self._snapshot_path)
        except Exception:
            pass

    def flush(self) -> None:
        with self._lock:
            self._maybe_flush_locked()

__all__ = ["SessionStateManager", "SessionStateConfig"]
