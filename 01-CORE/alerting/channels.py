from __future__ import annotations
from pathlib import Path
from typing import List, Callable, Optional, Dict, Any
import json, time
from .models import AdvancedAlert, AdvancedChannelType

try:
    from protocols.logging_central_protocols import setup_module_logging, LogLevel
    _logger = setup_module_logging("AlertingChannels", LogLevel.INFO)
except Exception:  # pragma: no cover
    class _Fallback:
        def info(self,m,c=""): print(f"[INFO][AlertingChannels][{c}] {m}")
        def warning(self,m,c=""): print(f"[WARN][AlertingChannels][{c}] {m}")
        def error(self,m,c=""): print(f"[ERR][AlertingChannels][{c}] {m}")
    _logger = _Fallback()

class BaseChannel:
    channel_type: AdvancedChannelType = AdvancedChannelType.CONSOLE
    def send(self, alert: AdvancedAlert) -> None:  # pragma: no cover - interface
        raise NotImplementedError

class ConsoleChannel(BaseChannel):
    channel_type = AdvancedChannelType.CONSOLE
    def __init__(self, min_severity: str = "medium"):
        self.min_severity = min_severity
        self._order = ["low","medium","high","critical"]
    def send(self, alert: AdvancedAlert) -> None:
        if self._order.index(alert.severity) < self._order.index(self.min_severity):
            return
        sev = alert.severity.upper()
        _logger.info(f"[{sev}] {alert.category} - {alert.message}", "ConsoleChannel")

class FileChannel(BaseChannel):
    channel_type = AdvancedChannelType.FILE
    def __init__(self, path: str, rotate_size: int = 512_000):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.rotate_size = rotate_size
    def _rotate(self):
        try:
            if self.path.exists() and self.path.stat().st_size > self.rotate_size:
                ts = time.strftime('%Y%m%d_%H%M%S')
                self.path.rename(self.path.parent / f"alerts_{ts}.jsonl")
        except Exception:
            pass
    def send(self, alert: AdvancedAlert) -> None:
        try:
            self._rotate()
            with self.path.open('a', encoding='utf-8') as f:
                f.write(json.dumps(alert.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:  # pragma: no cover
            _logger.error(f"FileChannel write failed: {e}", "FileChannel")

class MemoryChannel(BaseChannel):
    channel_type = AdvancedChannelType.MEMORY
    def __init__(self, limit: int = 1000):
        self.limit = limit
        self._alerts: List[AdvancedAlert] = []
    def send(self, alert: AdvancedAlert) -> None:
        self._alerts.append(alert)
        if len(self._alerts) > self.limit:
            self._alerts.pop(0)
    def get(self) -> List[Dict[str,Any]]:
        return [a.to_dict() for a in self._alerts]

class CallbackChannel(BaseChannel):
    channel_type = AdvancedChannelType.CALLBACK
    def __init__(self, callbacks: Optional[List[Callable[[AdvancedAlert], None]]] = None):
        self.callbacks = callbacks or []
    def add(self, cb: Callable[[AdvancedAlert],None]):
        if cb not in self.callbacks:
            self.callbacks.append(cb)
    def send(self, alert: AdvancedAlert) -> None:
        for cb in list(self.callbacks):
            try:
                cb(alert)
            except Exception as e:  # pragma: no cover
                _logger.error(f"Callback failed: {e}", "CallbackChannel")

__all__ = [
    "BaseChannel","ConsoleChannel","FileChannel","MemoryChannel","CallbackChannel"
]
