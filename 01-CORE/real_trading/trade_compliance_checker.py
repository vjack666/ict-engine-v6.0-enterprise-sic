"""Trade Compliance Checker

Valida reglas de compliance previas a enviar orden:
 - Horarios restringidos
 - Lista negra de símbolos
 - Máximo spread permitido
 - Pausa after-loss (cooldown)

Devuelve estructura con resultado y razones.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable
import time
import datetime as dt

try:
    from smart_trading_logger import SmartTradingLogger  # type: ignore
except Exception:  # pragma: no cover
    SmartTradingLogger = None  # type: ignore


@dataclass
class ComplianceResult:
    allowed: bool
    violations: List[str]
    warnings: List[str]
    context: Dict[str, Any]


class TradeComplianceChecker:
    def __init__(self,
                 time_provider: Callable[[], float] = time.time,
                 blacklist: Optional[List[str]] = None,
                 restricted_hours_utc: Optional[List[int]] = None,
                 max_spread_points: Optional[float] = None,
                 loss_cooldown_sec: int = 0,
                 logger: Optional[Any] = None) -> None:
        self.time_provider = time_provider
        self.blacklist = set(s.upper() for s in (blacklist or []))
        self.restricted_hours_utc = set(restricted_hours_utc or [])
        self.max_spread_points = max_spread_points
        self.loss_cooldown_sec = loss_cooldown_sec
        self._last_loss_ts: Optional[float] = None
        self.logger = logger or (SmartTradingLogger("ComplianceChecker") if SmartTradingLogger else None)  # type: ignore

    def _log(self, msg: str, level: str = "info") -> None:
        if self.logger:
            try:
                getattr(self.logger, level, self.logger.info)(msg, "trade_compliance")
            except Exception:  # pragma: no cover
                pass

    def register_loss(self) -> None:
        self._last_loss_ts = self.time_provider()
        self._log("Loss registrado para cooldown", "warning")

    def check(self, symbol: str, spread_points: Optional[float] = None) -> ComplianceResult:
        now_ts = self.time_provider()
        now = dt.datetime.utcfromtimestamp(now_ts)
        violations: List[str] = []
        warnings: List[str] = []
        up_symbol = symbol.upper()

        if up_symbol in self.blacklist:
            violations.append("SYMBOL_BLACKLISTED")
        if now.hour in self.restricted_hours_utc:
            violations.append("HOUR_RESTRICTED")
        if self.max_spread_points is not None and spread_points is not None and spread_points > self.max_spread_points:
            violations.append("SPREAD_TOO_WIDE")
        if self._last_loss_ts and (now_ts - self._last_loss_ts) < self.loss_cooldown_sec:
            violations.append("LOSS_COOLDOWN_ACTIVE")

        allowed = not violations
        if not allowed:
            self._log(f"Compliance bloquea orden {symbol}: {violations}", "warning")
        else:
            self._log(f"Compliance OK {symbol}")

        return ComplianceResult(allowed, violations, warnings, {
            "symbol": up_symbol,
            "utc_hour": now.hour,
            "spread_points": spread_points,
            "loss_cooldown_sec": self.loss_cooldown_sec,
            "seconds_since_last_loss": (now_ts - self._last_loss_ts) if self._last_loss_ts else None
        })

__all__ = ["TradeComplianceChecker", "ComplianceResult"]
