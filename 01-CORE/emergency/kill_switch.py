"""Kill Switch (P0)
Centro de control para detener trading ante condiciones críticas.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from protocols.logging_central_protocols import create_safe_logger

@dataclass
class KillSwitchTrigger:
    reason: str
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class KillSwitchActive(Exception): ...

class KillSwitch:
    def __init__(self, on_activate: Optional[Callable[[KillSwitchTrigger], None]] = None):
        self.logger = create_safe_logger("KillSwitch")
        self._active: bool = False
        self._last_trigger: Optional[KillSwitchTrigger] = None
        self._on_activate = on_activate

    def trigger(self, reason: str, **metadata: Any) -> None:
        if self._active:
            return
        trigger = KillSwitchTrigger(reason=reason, metadata=metadata)
        self._active = True
        self._last_trigger = trigger
        self.logger.error(f"🚨 KILL SWITCH ACTIVATED reason={reason} metadata={metadata}", "emergency")
        if self._on_activate:
            try:
                self._on_activate(trigger)
            except Exception as e:
                self.logger.error(f"Kill switch callback error: {e}", "emergency")

    def is_active(self) -> bool:
        return self._active

    def ensure_not_active(self) -> None:
        if self._active:
            raise KillSwitchActive(f"Kill switch active: {self._last_trigger.reason if self._last_trigger else 'UNKNOWN'}")

    def reset(self, auth: Optional[str] = None) -> bool:
        # Futuro: validar auth/token/role
        if not self._active:
            return False
        self.logger.warning("🔄 Kill switch reset", "emergency")
        self._active = False
        self._last_trigger = None
        return True

    def status_report(self) -> Dict[str, Any]:
        return {
            "active": self._active,
            "trigger": self._last_trigger.reason if self._last_trigger else None,
            "since": self._last_trigger.timestamp.isoformat() if self._last_trigger else None,
        }

__all__ = ["KillSwitch", "KillSwitchActive", "KillSwitchTrigger"]
