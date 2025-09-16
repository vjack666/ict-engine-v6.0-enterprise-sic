from __future__ import annotations
from typing import Dict, List, Optional, Callable
import time
from threading import Lock

from .models import AdvancedAlert, AlertDedupPolicy, AdvancedChannelType
from .channels import BaseChannel, ConsoleChannel, FileChannel, MemoryChannel, CallbackChannel

try:
    from protocols.logging_central_protocols import setup_module_logging, LogLevel
    _logger = setup_module_logging("AdvancedAlertManager", LogLevel.INFO)
except Exception:  # pragma: no cover
    class _Fallback:
        def info(self,m,c=""): print(f"[INFO][AdvancedAlertManager][{c}] {m}")
        def warning(self,m,c=""): print(f"[WARN][AdvancedAlertManager][{c}] {m}")
        def error(self,m,c=""): print(f"[ERR][AdvancedAlertManager][{c}] {m}")
    _logger = _Fallback()

class AdvancedAlertManager:
    """Gestor avanzado de alertas con deduplicación y fan-out multi canal."""
    def __init__(self,
                 dedup_policy: AlertDedupPolicy = AlertDedupPolicy.CATEGORY_SYMBOL_WINDOW,
                 dedup_window_seconds: float = 30.0,
                 rate_limit_per_60s: int = 120,
                 default_channels: Optional[List[BaseChannel]] = None):
        self.dedup_policy = dedup_policy
        self.dedup_window_seconds = dedup_window_seconds
        self.rate_limit_per_60s = rate_limit_per_60s
        self._channels: List[BaseChannel] = default_channels or []
        self._lock = Lock()
        self._recent_keys: Dict[str, AdvancedAlert] = {}
        self._timestamps: List[float] = []
        self._memory_channel: Optional[MemoryChannel] = None
        _logger.info("AdvancedAlertManager inicializado", "INIT")

    def add_default_channel_set(self, base_path: str = "05-LOGS/alerts"):
        file_channel = FileChannel(f"{base_path}/advanced_alerts.jsonl")
        console_channel = ConsoleChannel(min_severity="medium")
        memory_channel = MemoryChannel(limit=2000)
        self.add_channel(file_channel)
        self.add_channel(console_channel)
        self.add_channel(memory_channel)
        self._memory_channel = memory_channel

    def add_channel(self, channel: BaseChannel):
        with self._lock:
            if channel not in self._channels:
                self._channels.append(channel)
                _logger.info(f"Canal agregado: {channel.__class__.__name__}", "CHANNEL")

    def add_callback(self, callback: Callable[[AdvancedAlert], None]):
        cb_channel = None
        for ch in self._channels:
            if isinstance(ch, CallbackChannel):
                cb_channel = ch
                break
        if not cb_channel:
            cb_channel = CallbackChannel()
            self.add_channel(cb_channel)
        cb_channel.add(callback)

    def _rate_ok(self) -> bool:
        now = time.time()
        cutoff = now - 60
        self._timestamps = [t for t in self._timestamps if t > cutoff]
        if len(self._timestamps) >= self.rate_limit_per_60s:
            return False
        self._timestamps.append(now)
        return True

    def _dedup_key(self, alert: AdvancedAlert) -> str:
        if self.dedup_policy == AlertDedupPolicy.NONE:
            return f"{alert.timestamp}:{id(alert)}"
        if self.dedup_policy == AlertDedupPolicy.MESSAGE_WINDOW:
            return f"MSG:{alert.message.lower()}"
        # CATEGORY_SYMBOL_WINDOW
        sym = alert.symbol or "*"
        return f"CATSYM:{alert.category}:{sym}:{alert.message.lower()}"

    def _prune_old(self):
        now = time.time()
        to_delete = []
        for k, a in self._recent_keys.items():
            if now - a.timestamp > self.dedup_window_seconds:
                to_delete.append(k)
        for k in to_delete:
            del self._recent_keys[k]

    def record_alert(self, category: str, severity: str, message: str, symbol: Optional[str] = None, meta: Optional[dict] = None) -> bool:
        if not self._rate_ok():
            _logger.warning("Rate limit alcanzado - alerta descartada", "RATE")
            return False
        alert = AdvancedAlert(time.time(), category, severity, message, symbol, meta or {})
        key = self._dedup_key(alert)
        with self._lock:
            self._prune_old()
            existing = self._recent_keys.get(key)
            if existing:
                existing.count += 1
                existing.meta["last_timestamp"] = alert.timestamp
                existing.meta["duplicate_count"] = existing.count
                # reenviar duplicados críticos como aggregated
                if severity in ("high","critical"):
                    self._fan_out(existing)
                return True
            self._recent_keys[key] = alert
        self._fan_out(alert)
        return True

    def _fan_out(self, alert: AdvancedAlert):
        for ch in list(self._channels):
            try:
                ch.send(alert)
            except Exception as e:  # pragma: no cover
                _logger.error(f"Canal {ch.__class__.__name__} fallo: {e}", "CHANNEL")

    def get_recent(self, limit: int = 100) -> List[dict]:
        if self._memory_channel:
            data = self._memory_channel.get()
            return data[-limit:]
        return []

# Singleton helper
_global_adv_manager: Optional[AdvancedAlertManager] = None

def get_advanced_alert_manager() -> AdvancedAlertManager:
    global _global_adv_manager
    if _global_adv_manager is None:
        _global_adv_manager = AdvancedAlertManager()
        _global_adv_manager.add_default_channel_set()
    return _global_adv_manager

__all__ = ["AdvancedAlertManager", "get_advanced_alert_manager", "AlertDedupPolicy", "AdvancedChannelType"]
