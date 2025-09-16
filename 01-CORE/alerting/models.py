from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable
from enum import Enum
import time

try:
    from protocols.logging_central_protocols import setup_module_logging, LogLevel
    _logger = setup_module_logging("AlertingModels", LogLevel.INFO)
except Exception:  # pragma: no cover
    class _Fallback:
        def info(self,m,c=""): print(f"[INFO][AlertingModels][{c}] {m}")
        def warning(self,m,c=""): print(f"[WARN][AlertingModels][{c}] {m}")
        def error(self,m,c=""): print(f"[ERR][AlertingModels][{c}] {m}")
    _logger = _Fallback()

class AdvancedChannelType(Enum):
    CONSOLE = "console"
    FILE = "file"
    CALLBACK = "callback"
    MEMORY = "memory"
    WEBHOOK = "webhook"
    EMAIL = "email"

class AlertDedupPolicy(Enum):
    NONE = "none"
    MESSAGE_WINDOW = "message_window"
    CATEGORY_SYMBOL_WINDOW = "category_symbol_window"

@dataclass
class AdvancedAlert:
    timestamp: float
    category: str
    severity: str
    message: str
    symbol: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)
    count: int = 1  # para deduplicación

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "datetime": time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(self.timestamp)),
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "symbol": self.symbol,
            "meta": self.meta,
            "count": self.count
        }

DedupKeyFunc = Callable[[AdvancedAlert], str]

__all__ = [
    "AdvancedChannelType",
    "AlertDedupPolicy",
    "AdvancedAlert",
    "DedupKeyFunc"
]
