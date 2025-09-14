#!/usr/bin/env python3
"""
🚀 EXECUTION ROUTER - ICT ENGINE v6.0 ENTERPRISE
==============================================

Enrutador de ejecución central para órdenes en trading real.
Responsabilidades:
- Validación previa (riesgo, latencia, salud del sistema)
- Selección de canal de ejecución (primario, backup)
- Retries controlados y circuit breaker
- Logging estructurado mediante protocolos

Diseñado para integrarse sin bloquear el hilo principal y con bajo overhead.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Protocol, Callable
from datetime import datetime, timedelta
import threading
import time
import json
import os

try:
    from protocols.logging_central_protocols import create_safe_logger, LogLevel  # type: ignore
    _LOGLEVEL_AVAILABLE = True
except ImportError:  # fallback mínimo
    from smart_trading_logger import enviar_senal_log as _compat_log  # type: ignore
    _LOGLEVEL_AVAILABLE = False
    class _MiniLogger:  # pragma: no cover - fallback simple
        def info(self,m,c): _compat_log("INFO",m,c)
        def warning(self,m,c): _compat_log("WARNING",m,c)
        def error(self,m,c): _compat_log("ERROR",m,c)
        def debug(self,m,c): _compat_log("DEBUG",m,c)
    def create_safe_logger(component_name: str, **_): return _MiniLogger()  # type: ignore
    class LogLevel:  # fallback enum-like
        INFO = "INFO"

class RiskValidatorProtocol(Protocol):
    def validate_order(self, symbol: str, volume: float, action: str, price: float) -> bool: ...

class LatencyMonitorProtocol(Protocol):
    def get_current_latency_ms(self) -> float: ...

class HealthMonitorProtocol(Protocol):
    def is_system_healthy(self) -> bool: ...

class BrokerExecutorProtocol(Protocol):
    def send_order(self, symbol: str, action: str, volume: float, price: Optional[float], sl: Optional[float], tp: Optional[float]) -> Dict[str, Any]: ...

@dataclass
class ExecutionResult:
    success: bool
    ticket: Optional[int] = None
    error: Optional[str] = None
    retries: int = 0
    placed_at: Optional[datetime] = None
    extra: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionRouterConfig:
    max_retries: int = 2
    retry_delay_seconds: float = 0.8
    max_latency_ms: float = 850.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_window_sec: int = 120
    circuit_breaker_cooldown_sec: int = 90
    moderate_violation_volume_limit: float = 0.5  # (configurable) límite para permitir violaciones moderadas
    metrics_dir: Optional[str] = None  # ruta donde escribir métricas JSON
    metrics_history_limit: int = 500  # entradas de historial

class CircuitBreaker:
    def __init__(self, threshold: int, window_sec: int, cooldown_sec: int):
        self.threshold = threshold
        self.window_sec = window_sec
        self.cooldown_sec = cooldown_sec
        self.failures: list[datetime] = []
        self.open_until: Optional[datetime] = None
        self._lock = threading.Lock()

    def record_failure(self):
        with self._lock:
            now = datetime.utcnow()
            self.failures.append(now)
            cutoff = now - timedelta(seconds=self.window_sec)
            self.failures = [f for f in self.failures if f >= cutoff]
            if len(self.failures) >= self.threshold and not self.open_until:
                self.open_until = now + timedelta(seconds=self.cooldown_sec)

    def allow(self) -> bool:
        with self._lock:
            if self.open_until and datetime.utcnow() < self.open_until:
                return False
            if self.open_until and datetime.utcnow() >= self.open_until:
                # reset breaker
                self.open_until = None
                self.failures.clear()
            return True

class ExecutionRouter:
    def __init__(self,
                 primary_executor: BrokerExecutorProtocol,
                 backup_executor: Optional[BrokerExecutorProtocol] = None,
                 risk_validator: Optional[RiskValidatorProtocol] = None,
                 latency_monitor: Optional[LatencyMonitorProtocol] = None,
                 health_monitor: Optional[HealthMonitorProtocol] = None,
                 config: Optional[ExecutionRouterConfig] = None):
        self.primary = primary_executor
        self.backup = backup_executor
        self.risk_validator = risk_validator
        self.latency_monitor = latency_monitor
        self.health_monitor = health_monitor
        self.config = config or ExecutionRouterConfig()
        if _LOGLEVEL_AVAILABLE:
            self.logger = create_safe_logger("ExecutionRouter", log_level=LogLevel.INFO)
        else:
            self.logger = create_safe_logger("ExecutionRouter")
        self.breaker = CircuitBreaker(self.config.circuit_breaker_threshold,
                                      self.config.circuit_breaker_window_sec,
                                      self.config.circuit_breaker_cooldown_sec)
        # métricas
        self._metrics = {
            'orders_total': 0,
            'orders_ok': 0,
            'orders_failed': 0,
            'last_log_ts': time.time(),
            'latency_samples': [],
            'created': datetime.utcnow().isoformat(),
            'history': [],  # lista de snapshots resumidos
            'blocked_reasons': {
                'system_unhealthy': 0,
                'latency_too_high': 0,
                'risk_validation_failed': 0,
                'circuit_open': 0,
                'hook_blocked': 0
            }
        }
        self._load_cumulative()
        # hooks personalizables (callables que retornan (bool_ok, reason|None))
        self.pre_order_hooks: list[Callable[[str, str, float, Optional[float]], tuple[bool, Optional[str]]]] = []

    def _pre_checks(self, symbol: str, volume: float, action: str, price: Optional[float]) -> Optional[str]:
        if self.health_monitor and not self.health_monitor.is_system_healthy():
            return "system_unhealthy"
        if self.latency_monitor:
            latency = self.latency_monitor.get_current_latency_ms()
            if latency > self.config.max_latency_ms:
                return f"latency_too_high:{latency:.0f}ms"
        if self.risk_validator and not self.risk_validator.validate_order(symbol, volume, action, price or 0.0):
            return "risk_validation_failed"
        if not self.breaker.allow():
            return "circuit_open"
        # custom hooks
        for hook in self.pre_order_hooks:
            try:
                ok, reason = hook(symbol, action, volume, price)
                if not ok:
                    return reason or 'hook_blocked'
            except Exception as e:  # no bloquear por excepción de hook
                self.logger.error(f"Hook exception ignorada: {e}", "EXECUTION")
        return None

    def place_order(self, symbol: str, action: str, volume: float, price: Optional[float] = None,
                    sl: Optional[float] = None, tp: Optional[float] = None) -> ExecutionResult:
        start = datetime.utcnow()
        pre_issue = self._pre_checks(symbol, volume, action, price)
        if pre_issue:
            self.logger.warning(f"Order blocked pre-check: {pre_issue}", "EXECUTION")
            # métricas de bloqueo
            key = pre_issue.split(':')[0]
            if key.startswith('latency_too_high'):
                key = 'latency_too_high'
            if key not in self._metrics['blocked_reasons']:
                key = 'hook_blocked'
            self._metrics['blocked_reasons'][key] += 1
            return ExecutionResult(False, error=pre_issue)

        executor_sequence = [self.primary] + ([self.backup] if self.backup else [])
        last_error = None
        for attempt in range(self.config.max_retries + 1):
            for idx, executor in enumerate(executor_sequence):
                try:
                    result = executor.send_order(symbol, action, volume, price, sl, tp)
                    if result.get('success'):
                        ticket = result.get('ticket')
                        self.logger.info(f"Order executed via {'primary' if idx == 0 else 'backup'} ticket={ticket}", "EXECUTION")
                        self._metrics['orders_total'] += 1
                        self._metrics['orders_ok'] += 1
                        now = time.time()
                        if self.latency_monitor:
                            try:
                                self._metrics['latency_samples'].append(self.latency_monitor.get_current_latency_ms())
                                if len(self._metrics['latency_samples']) > 100:
                                    self._metrics['latency_samples'].pop(0)
                            except Exception:
                                pass
                        if (now - self._metrics['last_log_ts']) > 30:
                            self._emit_metrics(now)
                        return ExecutionResult(True, ticket=ticket, retries=attempt,
                                               placed_at=datetime.utcnow(), extra=result)
                    last_error = result.get('error', 'unknown_error')
                    self.logger.warning(f"Executor returned failure: {last_error}", "EXECUTION")
                except Exception as e:  # ejecución robusta
                    last_error = f"exception:{e}"
                    self.logger.error(f"Execution exception attempt {attempt+1}: {e}", "EXECUTION")
                    self.breaker.record_failure()
            if attempt < self.config.max_retries:
                time.sleep(self.config.retry_delay_seconds)
        # fracaso total
        if last_error:
            self.breaker.record_failure()
        self._metrics['orders_total'] += 1
        self._metrics['orders_failed'] += 1
        now = time.time()
        if (now - self._metrics['last_log_ts']) > 30:
            self._emit_metrics(now)
        return ExecutionResult(False, error=last_error or 'execution_failed', retries=self.config.max_retries)

    def _emit_metrics(self, now: float) -> None:
        lat_list = self._metrics.get('latency_samples', [])
        lat_avg = sum(lat_list)/len(lat_list) if lat_list else 0.0
        self.logger.info(
            f"METRICS total={self._metrics['orders_total']} ok={self._metrics['orders_ok']} fail={self._metrics['orders_failed']} avg_latency_ms={lat_avg:.1f}",
            "EXECUTION"
        )
        self._metrics['last_log_ts'] = now
        self._persist_live(lat_avg)

    # ----------------------------- MÉTRICAS PERSISTENCIA ------------------
    def _ensure_dir(self):
        if not self.config.metrics_dir:
            return None
        try:
            os.makedirs(self.config.metrics_dir, exist_ok=True)
        except Exception:
            pass
        return self.config.metrics_dir

    def _live_file(self):
        d = self._ensure_dir()
        return os.path.join(d, 'metrics_live.json') if d else None

    def _summary_file(self):
        d = self._ensure_dir()
        return os.path.join(d, 'metrics_summary.json') if d else None

    def _cumulative_file(self):
        d = self._ensure_dir()
        return os.path.join(d, 'metrics_cumulative.json') if d else None

    def _load_cumulative(self):
        path = self._cumulative_file()
        if not path or not os.path.exists(path):
            self._cumulative = {
                'orders_total': 0,
                'orders_ok': 0,
                'orders_failed': 0,
                'sessions': 0,
                'last_update': None
            }
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self._cumulative = json.load(f)
        except Exception:
            self._cumulative = {
                'orders_total': 0,
                'orders_ok': 0,
                'orders_failed': 0,
                'sessions': 0,
                'last_update': None
            }
        self._cumulative['sessions'] = self._cumulative.get('sessions', 0) + 1

    def _persist_live(self, avg_latency: float):
        lf = self._live_file()
        if not lf:
            return
        # calcular percentiles si hay suficientes muestras
        lat_list = list(self._metrics.get('latency_samples', []))
        lat_list_sorted = sorted(lat_list)
        def _pct(p: float) -> float:
            if not lat_list_sorted:
                return 0.0
            k = (len(lat_list_sorted)-1) * p
            f = int(k)
            c = min(f+1, len(lat_list_sorted)-1)
            if f == c:
                return float(lat_list_sorted[f])
            d0 = lat_list_sorted[f] * (c - k)
            d1 = lat_list_sorted[c] * (k - f)
            return float(d0 + d1)

        percentiles = {
            'p50': _pct(0.50),
            'p75': _pct(0.75),
            'p90': _pct(0.90),
            'p95': _pct(0.95),
            'p99': _pct(0.99)
        }
        data = {
            'timestamp': datetime.utcnow().isoformat(),
            'orders_total': self._metrics['orders_total'],
            'orders_ok': self._metrics['orders_ok'],
            'orders_failed': self._metrics['orders_failed'],
            'avg_latency_ms': avg_latency,
            'latency_samples_count': len(lat_list),
            'latency_percentiles': percentiles
        }
        try:
            with open(lf, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # historial resumido
        hist_entry = {
            't': data['timestamp'],
            'total': data['orders_total'],
            'ok': data['orders_ok'],
            'fail': data['orders_failed'],
            'lat': avg_latency
        }
        self._metrics['history'].append(hist_entry)
        if len(self._metrics['history']) > self.config.metrics_history_limit:
            self._metrics['history'].pop(0)
        self._persist_summary()

    def _persist_summary(self):
        sf = self._summary_file()
        if not sf:
            return
        lat_list = self._metrics.get('latency_samples', [])
        avg_latency = sum(lat_list)/len(lat_list) if lat_list else 0.0
        lat_list_sorted = sorted(lat_list)
        def _pct(p: float) -> float:
            if not lat_list_sorted:
                return 0.0
            k = (len(lat_list_sorted)-1) * p
            f = int(k)
            c = min(f+1, len(lat_list_sorted)-1)
            if f == c:
                return float(lat_list_sorted[f])
            d0 = lat_list_sorted[f] * (c - k)
            d1 = lat_list_sorted[c] * (k - f)
            return float(d0 + d1)
        latency_percentiles = {
            'p50': _pct(0.50),
            'p75': _pct(0.75),
            'p90': _pct(0.90),
            'p95': _pct(0.95),
            'p99': _pct(0.99)
        }
        summary = {
            'generated': datetime.utcnow().isoformat(),
            'orders_total': self._metrics['orders_total'],
            'orders_ok': self._metrics['orders_ok'],
            'orders_failed': self._metrics['orders_failed'],
            'latency_avg_ms': avg_latency,
            'latency_percentiles': latency_percentiles,
            'history': self._metrics['history'][-50:],  # recorte
        }
        try:
            with open(sf, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def persist_on_shutdown(self):
        # combinar en cumulativo
        path = self._cumulative_file()
        if not path:
            return
        self._cumulative['orders_total'] += self._metrics['orders_total']
        self._cumulative['orders_ok'] += self._metrics['orders_ok']
        self._cumulative['orders_failed'] += self._metrics['orders_failed']
        self._cumulative['last_update'] = datetime.utcnow().isoformat()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._cumulative, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        # asegurar summary final
        self._persist_summary()

__all__ = [
    'ExecutionRouter', 'ExecutionRouterConfig', 'ExecutionResult'
]
