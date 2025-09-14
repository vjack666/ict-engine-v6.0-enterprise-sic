"""Account Health Monitor
=========================
Monitorea el estado de la cuenta en tiempo real para detectar condiciones
críticas que requieran reducción de riesgo, cierre de posiciones o parada
emergente.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import threading
import random


@dataclass
class AccountSnapshot:
    timestamp: datetime
    balance: float
    equity: float
    free_margin: float
    margin_level: float
    open_positions: int
    floating_pl: float
    risk_exposure_pct: float


class AccountHealthStatus:
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AccountHealthMonitor:
    def __init__(self,
                 fetch_account_metrics: Optional[Callable[[], Dict[str, Any]]] = None,
                 check_interval: int = 30,
                 warning_drawdown_pct: float = 5.0,
                 critical_drawdown_pct: float = 10.0,
                 max_risk_exposure_pct: float = 25.0) -> None:
        self.fetch_account_metrics = fetch_account_metrics or self._default_fetch
        self.check_interval = check_interval
        self.warning_drawdown_pct = warning_drawdown_pct
        self.critical_drawdown_pct = critical_drawdown_pct
        self.max_risk_exposure_pct = max_risk_exposure_pct

        self._last_snapshot: Optional[AccountSnapshot] = None
        self._baseline_balance: Optional[float] = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._callbacks: list[Callable[[Dict[str, Any]], None]] = []

    # ------------------------------------------------------------------
    def start(self) -> bool:
        if self._thread and self._thread.is_alive():
            return True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop_event.set()

    def add_callback(self, cb: Callable[[Dict[str, Any]], None]) -> None:
        self._callbacks.append(cb)

    # ------------------------------------------------------------------
    def get_last_snapshot(self) -> Optional[AccountSnapshot]:
        with self._lock:
            return self._last_snapshot

    def get_health_summary(self) -> Dict[str, Any]:
        snap = self.get_last_snapshot()
        if not snap:
            return {"status": "UNKNOWN"}
        status = self._evaluate_status(snap)
        return {
            "status": status,
            "balance": snap.balance,
            "equity": snap.equity,
            "margin_level": snap.margin_level,
            "open_positions": snap.open_positions,
            "risk_exposure_pct": snap.risk_exposure_pct,
            "floating_pl": snap.floating_pl,
            "timestamp": snap.timestamp
        }

    # ------------------------------------------------------------------
    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                metrics = self.fetch_account_metrics()
                snap = AccountSnapshot(
                    timestamp=datetime.utcnow(),
                    balance=metrics.get("balance", 10000.0),
                    equity=metrics.get("equity", 10000.0),
                    free_margin=metrics.get("free_margin", 9000.0),
                    margin_level=metrics.get("margin_level", 1000.0),
                    open_positions=metrics.get("open_positions", 0),
                    floating_pl=metrics.get("floating_pl", 0.0),
                    risk_exposure_pct=metrics.get("risk_exposure_pct", 0.0)
                )
                with self._lock:
                    self._last_snapshot = snap
                    if self._baseline_balance is None:
                        self._baseline_balance = snap.balance
                summary = self.get_health_summary()
                for cb in list(self._callbacks):
                    try:
                        cb(summary)
                    except Exception:
                        pass
            except Exception:
                pass
            self._stop_event.wait(self.check_interval)

    def _evaluate_status(self, snap: AccountSnapshot) -> str:
        if self._baseline_balance is None:
            return AccountHealthStatus.OK
        drawdown_pct = max(0.0, (self._baseline_balance - snap.equity) / self._baseline_balance * 100.0)
        if drawdown_pct >= self.critical_drawdown_pct or snap.margin_level < 200 or snap.risk_exposure_pct > self.max_risk_exposure_pct:
            return AccountHealthStatus.CRITICAL
        if drawdown_pct >= self.warning_drawdown_pct or snap.margin_level < 400:
            return AccountHealthStatus.WARNING
        return AccountHealthStatus.OK

    def _default_fetch(self) -> Dict[str, Any]:
        base = 10000.0
        equity = base + random.uniform(-300, 300)
        return {
            "balance": base,
            "equity": equity,
            "free_margin": equity * 0.9,
            "margin_level": random.uniform(300, 1200),
            "open_positions": random.randint(0, 8),
            "floating_pl": equity - base,
            "risk_exposure_pct": random.uniform(0, 30)
        }


__all__ = ["AccountHealthMonitor", "AccountHealthStatus", "AccountSnapshot"]
