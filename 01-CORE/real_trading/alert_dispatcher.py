#!/usr/bin/env python3
"""
🚨 ALERT DISPATCHER - ICT ENGINE v6.0 ENTERPRISE
===============================================
Centraliza emisión de alertas del sistema (riesgo, latencia, ejecución, sistema).
Salida actual: logging + archivo JSONL rotativo simple.
Preparado para futuras extensiones (webhook, email, slack).
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
from threading import Lock

try:
    from protocols.logging_central_protocols import create_safe_logger, LogLevel  # type: ignore
except Exception:
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
class Alert:
    timestamp: str
    severity: str  # INFO/WARNING/CRITICAL
    category: str  # RISK/LATENCY/EXECUTION/SYSTEM
    message: str
    meta: Dict[str, Any]

class AlertDispatcher:
    def __init__(self, 
                 base_dir: Optional[Path] = None, 
                 max_file_size: int = 512_000,
                 logger=None):
        self.base_dir = base_dir or Path("05-LOGS") / "alerts"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.base_dir / "alerts.jsonl"
        self.max_file_size = max_file_size
        self._lock = Lock()
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = create_safe_logger("AlertDispatcher", log_level=getattr(LogLevel, 'INFO', None))

    def _rotate_if_needed(self):
        try:
            if self.log_path.exists() and self.log_path.stat().st_size > self.max_file_size:
                ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                self.log_path.rename(self.base_dir / f"alerts_{ts}.jsonl")
        except Exception:
            pass

    def dispatch(self, severity: str, category: str, message: str, meta: Optional[Dict[str, Any]] = None) -> Alert:
        sev = severity.upper()
        cat = category.upper()
        alert = Alert(
            timestamp=datetime.utcnow().isoformat(),
            severity=sev,
            category=cat,
            message=message,
            meta=meta or {}
        )
        line = json.dumps(asdict(alert), ensure_ascii=False)
        with self._lock:
            self._rotate_if_needed()
            try:
                with self.log_path.open('a', encoding='utf-8') as f:
                    f.write(line + '\n')
            except Exception as e:
                self.logger.error(f"No se pudo escribir alerta: {e}", "ALERT")
        # Log severity mapping
        if sev == 'CRITICAL':
            self.logger.error(f"{cat} | {message} | {alert.meta}", "ALERT")
        elif sev == 'WARNING':
            self.logger.warning(f"{cat} | {message} | {alert.meta}", "ALERT")
        else:
            self.logger.info(f"{cat} | {message} | {alert.meta}", "ALERT")
        return alert

__all__ = ["AlertDispatcher", "Alert"]
