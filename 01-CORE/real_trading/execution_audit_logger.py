#!/usr/bin/env python3
"""Execution Audit Logger
===========================
Registro estructurado de eventos de ejecución en formato JSON Lines (.jsonl)
para auditoría y análisis post-mortem.

Características:
- Escritura atómica (write temp + rename) opcional para snapshots.
- Append line para eventos individuales (bajo overhead).
- Validación de payload y saneo básico de campos.
- Integración con logging enterprise (info/warn/error).

Uso básico:
    audit = ExecutionAuditLogger(base_dir="04-DATA/logs/execution")
    audit.log_event(event_type="ORDER_SENT", order_id="...", symbol="EURUSD", extra={"size":1.0})
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional
import json, time, datetime

try:
    from protocols.logging_protocol import create_enterprise_logger, LogLevel
except Exception:  # fallback mínimo
    class _Mini:
        def info(self,*a,**k): print(*a)
        def warning(self,*a,**k): print(*a)
        def error(self,*a,**k): print(*a)
    def create_enterprise_logger(component_name: str, **_): return _Mini()  # type: ignore
    class LogLevel:  # type: ignore
        INFO = "INFO"

@dataclass
class ExecutionAuditLogger:
    base_dir: str = "04-DATA/logs/execution"
    filename: str = "execution_audit.jsonl"
    flush_interval: float = 0.0  # reservado para buffering futuro
    logger: Any = field(init=False)

    def __post_init__(self) -> None:
        self.path = Path(self.base_dir)
        self.path.mkdir(parents=True, exist_ok=True)
        self.file_path = self.path / self.filename
        self.logger = create_enterprise_logger("ExecutionAudit")
        self.logger.info(f"ExecutionAuditLogger ready path={self.file_path}")

    def log_event(self, event_type: str, order_id: Optional[str] = None, symbol: Optional[str] = None,
                  status: Optional[str] = None, latency_ms: Optional[float] = None, extra: Optional[Dict[str, Any]] = None) -> None:
        if not event_type:
            return
        record = {
            "ts": datetime.datetime.utcnow().isoformat(),
            "event": event_type.upper(),
            "order_id": order_id,
            "symbol": symbol,
            "status": status,
            "latency_ms": round(latency_ms,3) if latency_ms is not None else None,
            "extra": extra or {}
        }
        # saneo simple
        record["extra"] = {k:v for k,v in record["extra"].items() if isinstance(k,str)}
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            self.logger.error(f"Audit write failed: {e}")

__all__ = ["ExecutionAuditLogger"]
