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
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Protocol, Callable, runtime_checkable
from datetime import datetime, timezone, timedelta
import threading
import time
import json
import os
try:
    from .rate_limiter import RateLimiter, RateLimiterConfig
except Exception:
    RateLimiter = None  # type: ignore
    RateLimiterConfig = None  # type: ignore
try:
    from .session_state_manager import SessionStateManager, SessionStateConfig
except Exception:
    SessionStateManager = None  # type: ignore
    SessionStateConfig = None  # type: ignore
try:
    from .composite_health_monitor import CompositeHealthMonitor, CompositeHealthConfig
except Exception:
    CompositeHealthMonitor = None  # type: ignore
    CompositeHealthConfig = None  # type: ignore
try:
    from .slippage_tracker import SlippageTracker
except Exception:
    SlippageTracker = None
try:
    from .market_data_validator import MarketDataValidator
except Exception:
    MarketDataValidator = None
try:
    from .alert_dispatcher import AlertDispatcher, AlertCategory, AlertSeverity
except Exception:
    AlertDispatcher = None  # type: ignore
    AlertCategory = None  # type: ignore
    AlertSeverity = None  # type: ignore
try:
    from .position_sizer import PositionSizer
except Exception:
    PositionSizer = None  # type: ignore
try:
    from .portfolio_exposure_tracker import PortfolioExposureTracker
except Exception:
    PortfolioExposureTracker = None  # type: ignore
try:
    from .trade_compliance_checker import TradeComplianceChecker
except Exception:
    TradeComplianceChecker = None  # type: ignore
try:
    from .execution_retry_policy import ExecutionRetryPolicy, RetryConfig
except Exception:
    ExecutionRetryPolicy = None  # type: ignore
    RetryConfig = None  # type: ignore

@runtime_checkable
class _LoggerProto(Protocol):
    def info(self, message: str, category: str) -> None: ...
    def warning(self, message: str, category: str) -> None: ...
    def error(self, message: str, category: str) -> None: ...
    def debug(self, message: str, category: str) -> None: ...

try:
    from protocols.logging_central_protocols import create_safe_logger as _central_logger_factory, LogLevel as _CentralLogLevel
    _LOGLEVEL_AVAILABLE = True
    _DEFAULT_LOG_LEVEL = getattr(_CentralLogLevel, 'INFO', None)
    def create_safe_logger(component_name: str, **kwargs) -> _LoggerProto:  # type: ignore[override]
        return _central_logger_factory(component_name, **kwargs)  # type: ignore[return-value]
except ImportError:  # fallback mínimo
    from smart_trading_logger import enviar_senal_log as _compat_log
    _LOGLEVEL_AVAILABLE = False
    class _MiniLogger:
        def info(self, message: str, category: str) -> None: _compat_log("INFO", message, category)
        def warning(self, message: str, category: str) -> None: _compat_log("WARNING", message, category)
        def error(self, message: str, category: str) -> None: _compat_log("ERROR", message, category)
        def debug(self, message: str, category: str) -> None: _compat_log("DEBUG", message, category)
    def create_safe_logger(component_name: str, **kwargs) -> _LoggerProto:  # type: ignore[override]
        return _MiniLogger()
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
    rate_limit_enabled: bool = False
    rate_limit_global: int = 30
    rate_limit_per_symbol: int = 10
    rate_limit_window_sec: int = 60
    session_state_enabled: bool = False
    composite_health_enabled: bool = False
    composite_health_latency_ms: float = 900.0
    composite_health_market_age_sec: int = 180
    composite_health_heartbeat_age_sec: int = 90
    # módulos opcionales adicionales
    enable_position_sizer: bool = False
    enable_portfolio_exposure_tracker: bool = False
    enable_trade_compliance: bool = False
    enable_retry_policy: bool = False
    position_sizer_risk_pct: float = 0.01
    compliance_max_spread_points: float | None = None
    compliance_blacklist: list[str] | None = None
    compliance_restricted_hours: list[int] | None = None
    compliance_loss_cooldown_sec: int = 0

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
            now = datetime.now(timezone.utc)
            self.failures.append(now)
            cutoff = now - timedelta(seconds=self.window_sec)
            self.failures = [f for f in self.failures if f >= cutoff]
            if len(self.failures) >= self.threshold and not self.open_until:
                self.open_until = now + timedelta(seconds=self.cooldown_sec)

    def allow(self) -> bool:
        with self._lock:
            if self.open_until and datetime.now(timezone.utc) < self.open_until:
                return False
            if self.open_until and datetime.now(timezone.utc) >= self.open_until:
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
                 alert_dispatcher: Optional[Any] = None,
                 config: Optional[ExecutionRouterConfig] = None):
        self.primary = primary_executor
        self.backup = backup_executor
        self.risk_validator = risk_validator
        self.latency_monitor = latency_monitor
        self.health_monitor = health_monitor
        self.alert_dispatcher = alert_dispatcher
        self.config = config or ExecutionRouterConfig()
        # rate limiter opcional
        self._rate_limiter = None
        if getattr(self.config, 'rate_limit_enabled', False) and RateLimiter and RateLimiterConfig:
            try:
                rl_cfg = RateLimiterConfig(global_rate=self.config.rate_limit_global,
                                           per_symbol_rate=self.config.rate_limit_per_symbol,
                                           window_sec=self.config.rate_limit_window_sec,
                                           persist_dir=self.config.metrics_dir)
                self._rate_limiter = RateLimiter(rl_cfg)
            except Exception:
                self._rate_limiter = None
        # session state opcional
        self._session_state = None
        if getattr(self.config, 'session_state_enabled', False) and SessionStateManager and SessionStateConfig:
            try:
                self._session_state = SessionStateManager(SessionStateConfig())
            except Exception:
                self._session_state = None
        # composite health monitor (reemplaza health_monitor si se habilita)
        if getattr(self.config, 'composite_health_enabled', False) and CompositeHealthMonitor and CompositeHealthConfig:
            try:
                ch_cfg = CompositeHealthConfig(
                    max_latency_ms=self.config.composite_health_latency_ms,
                    max_market_data_age_sec=self.config.composite_health_market_age_sec,
                    max_heartbeat_age_sec=self.config.composite_health_heartbeat_age_sec
                )
                # intenta derivar proveedores desde objetos existentes
                market_data_provider = globals().get('get_last_market_data_ts')  # opcional
                heartbeat_ts_provider = globals().get('get_last_heartbeat_ts')
                heartbeat_alive_check = globals().get('is_external_service_alive')
                def _wrap_ts_provider(fn):  # garantiza float|None
                    if callable(fn):
                        def _inner():
                            v = fn()
                            try:
                                if v is None:
                                    return None
                                if isinstance(v, (int, float)):
                                    return float(v)
                                # intenta extraer atributo timestamp
                                ts = getattr(v, 'timestamp', None)
                                if isinstance(ts, (int, float)):
                                    return float(ts)
                                return None
                            except Exception:
                                return None
                        return _inner
                    return None
                def _wrap_alive(fn):
                    if callable(fn):
                        def _alive():
                            try:
                                return bool(fn())
                            except Exception:
                                return False
                        return _alive
                    return None
                self.health_monitor = CompositeHealthMonitor(
                    latency_monitor=self.latency_monitor,
                    market_data_last_ts_provider=_wrap_ts_provider(market_data_provider),
                    heartbeat_last_ts_provider=_wrap_ts_provider(heartbeat_ts_provider),
                    heartbeat_alive_check=_wrap_alive(heartbeat_alive_check),
                    config=ch_cfg
                )
            except Exception:
                pass
        if _LOGLEVEL_AVAILABLE:
            self.logger = get_unified_logger("ExecutionRouter")
        else:
            self.logger = get_unified_logger("ExecutionRouter")
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
            'created': datetime.now(timezone.utc).isoformat(),
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
        # slippage tracker opcional
        self.slippage_tracker = None  # type: ignore[assignment]
        try:
            if SlippageTracker and self.config.metrics_dir:
                self.slippage_tracker = SlippageTracker(persist_dir=self.config.metrics_dir)
        except Exception:
            self.slippage_tracker = None
        # market data validator opcional (hook con TTL simple)
        self._md_validator = None  # type: ignore[assignment]
        self._md_validator_ttl_sec = 5.0
        self._md_last_check_ts: float = 0.0
        self._md_last_ok: bool = True
        self._md_last_reason: Optional[str] = None
        if MarketDataValidator:
            try:
                self._md_validator = MarketDataValidator()
            except Exception:
                self._md_validator = None
        # hooks personalizables (callables que retornan (bool_ok, reason|None))
        self.pre_order_hooks: list[Callable[[str, str, float, Optional[float]], tuple[bool, Optional[str]]]] = []
        # Integración modular nueva (audit + recorder)
        self._metrics_recorder = None
        self._audit_logger = None
        try:
            if self.config.metrics_dir:
                from .execution_metrics import ExecutionMetricsRecorder, ExecutionMetricsConfig
                cfg = ExecutionMetricsConfig(metrics_dir=self.config.metrics_dir, history_limit=self.config.metrics_history_limit)
                self._metrics_recorder = ExecutionMetricsRecorder(cfg)
        except Exception:
            self._metrics_recorder = None
        try:
            from .execution_audit_logger import ExecutionAuditLogger
            self._audit_logger = ExecutionAuditLogger()
        except Exception:
            self._audit_logger = None

        # --- MÓDULOS NUEVOS OPCIONALES ---
        self._position_sizer = None
        if getattr(self.config, 'enable_position_sizer', False) and PositionSizer:
            try:
                def _balance_provider():
                    provider = globals().get('get_account_balance')
                    if callable(provider):
                        try:
                            raw = provider()
                            # intenta convertir por pathways típicos
                            if isinstance(raw, (int, float)):
                                return float(raw)
                            if raw is None:
                                return 0.0
                            return float(str(raw))
                        except Exception:  # pragma: no cover
                            return 0.0
                    return 0.0
                self._position_sizer = PositionSizer(_balance_provider, logger=self.logger)
            except Exception:
                self._position_sizer = None
        self._exposure_tracker = None
        if getattr(self.config, 'enable_portfolio_exposure_tracker', False) and PortfolioExposureTracker:
            try:
                persist_dir = self.config.metrics_dir or ''
                path = os.path.join(persist_dir, 'portfolio_exposure.json') if persist_dir else None
                self._exposure_tracker = PortfolioExposureTracker(persistence_path=path, logger=self.logger)
            except Exception:
                self._exposure_tracker = None
        self._compliance_checker = None
        if getattr(self.config, 'enable_trade_compliance', False) and TradeComplianceChecker:
            try:
                self._compliance_checker = TradeComplianceChecker(
                    blacklist=self.config.compliance_blacklist,
                    restricted_hours_utc=self.config.compliance_restricted_hours,
                    max_spread_points=self.config.compliance_max_spread_points,
                    loss_cooldown_sec=self.config.compliance_loss_cooldown_sec,
                    logger=self.logger
                )
            except Exception:
                self._compliance_checker = None
        self._retry_policy = None
        if getattr(self.config, 'enable_retry_policy', False) and ExecutionRetryPolicy and RetryConfig:
            try:
                self._retry_policy = ExecutionRetryPolicy(RetryConfig(max_attempts=self.config.max_retries+1), logger=self.logger)
            except Exception:
                self._retry_policy = None

    def _pre_checks(self, symbol: str, volume: float, action: str, price: Optional[float]) -> Optional[str]:
        # rate limiter primero para reducir carga si hay ráfaga
        if self._rate_limiter:
            ok, reason_rl = self._rate_limiter.hook_check(symbol)
            if not ok:
                return reason_rl
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
        # market data validation (si disponible) con caché TTL para reducir coste
        if self._md_validator:
            now_ts = time.time()
            if (now_ts - self._md_last_check_ts) > self._md_validator_ttl_sec:
                self._md_last_check_ts = now_ts
                try:
                    # Se asume existencia de un proveedor global de velas reciente si está declarado
                    candles_provider = globals().get('get_recent_candles')  # tipo flexible
                    if callable(candles_provider):
                        raw = candles_provider()
                        candles: list[dict[str, Any]] = []
                        if isinstance(raw, list):
                            for item in raw:
                                if isinstance(item, dict):
                                    candles.append(item)
                        ok, issues = self._md_validator.validate_candles(candles)
                        self._md_last_ok = ok
                        self._md_last_reason = None if ok else (issues[0] if issues else 'market_data_invalid')
                    else:
                        self._md_last_ok = True  # no bloquear si no hay proveedor
                        self._md_last_reason = None
                except Exception:
                    self._md_last_ok = True
                    self._md_last_reason = None
            if not self._md_last_ok:
                return self._md_last_reason or 'market_data_invalid'
        return None

    def place_order(self, symbol: str, action: str, volume: float, price: Optional[float] = None,
                    sl: Optional[float] = None, tp: Optional[float] = None) -> ExecutionResult:
        start = datetime.now(timezone.utc)
        # --- POSITION SIZING (override volume si habilitado) ---
        if self._position_sizer and getattr(self.config, 'enable_position_sizer', False):
            try:
                # Si se provee stop-loss podemos evaluar sizing basado en riesgo fijo
                if sl and price and sl > 0 and price > 0:
                    stop_distance = abs(price - sl)
                    sizing_res = self._position_sizer.fixed_risk(symbol, price, stop_distance, risk_pct=getattr(self.config, 'position_sizer_risk_pct', 0.01))
                    if sizing_res.valid and sizing_res.volume > 0:
                        volume = sizing_res.volume
                        self.logger.info(f"Sizing aplicado volume={volume:.2f} basis={sizing_res.basis}", "EXECUTION")
                # Futuro: fallback a volatility_adjusted si no hay SL
            except Exception as e:  # pragma: no cover
                self.logger.warning(f"PositionSizer error: {e}", "EXECUTION")

        # --- COMPLIANCE CHECK previa ---
        if self._compliance_checker and getattr(self.config, 'enable_trade_compliance', False):
            try:
                # spread opcional: buscar proveedor global
                spread_provider = globals().get('get_current_spread_points')
                spread_points = None
                if callable(spread_provider):
                    try:
                        sp_raw = spread_provider(symbol)
                        if isinstance(sp_raw, (int, float)):
                            spread_points = float(sp_raw)
                    except Exception:
                        spread_points = None
                comp_res = self._compliance_checker.check(symbol, spread_points=spread_points)
                if not comp_res.allowed:
                    reason = "compliance_block:" + ",".join(comp_res.violations)
                    self.logger.warning(f"Compliance bloquea orden {reason}", "EXECUTION")
                    # métrica bloqueos
                    self._metrics['blocked_reasons']['hook_blocked'] = self._metrics['blocked_reasons'].get('hook_blocked', 0) + 1
                    return ExecutionResult(False, error=reason)
            except Exception as e:  # pragma: no cover
                self.logger.warning(f"Compliance checker exception ignorada: {e}", "EXECUTION")

        pre_issue = self._pre_checks(symbol, volume, action, price)
        if pre_issue:
            self.logger.warning(f"Order blocked pre-check: {pre_issue}", "EXECUTION")
            # Emit alerts for specific blocking reasons
            if self.alert_dispatcher and AlertCategory and AlertSeverity:
                try:
                    if pre_issue == "circuit_open":
                        self.alert_dispatcher.dispatch_circuit_breaker(symbol, self.breaker.failures)
                    elif pre_issue == "risk_validation_failed":
                        self.alert_dispatcher.dispatch_risk_block(symbol, "risk validation failed", 
                                                                 {"volume": volume, "action": action, "price": price})
                    elif pre_issue.startswith("latency_too_high"):
                        latency_str = pre_issue.split(":")[1] if ":" in pre_issue else "unknown"
                        self.alert_dispatcher.dispatch_system_health("latency_monitor", "high_latency", 
                                                                   {"latency": latency_str, "threshold": self.config.max_latency_ms})
                    elif pre_issue == "system_unhealthy":
                        self.alert_dispatcher.dispatch_system_health("health_monitor", "unhealthy", {})
                except Exception:
                    pass  # no fallar por alertas
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
                    def _send_once():
                        return executor.send_order(symbol, action, volume, price, sl, tp)
                    if self._retry_policy and getattr(self.config, 'enable_retry_policy', False):
                        try:
                            result = self._retry_policy.run(_send_once)
                        except Exception as e:  # agotó retries internos de policy
                            result = {'success': False, 'error': f'retry_policy_failed:{e}'}
                    else:
                        result = _send_once()
                    if result.get('success'):
                        ticket = result.get('ticket')
                        self.logger.info(f"Order executed via {'primary' if idx == 0 else 'backup'} ticket={ticket}", "EXECUTION")
                        self._metrics['orders_total'] += 1
                        self._metrics['orders_ok'] += 1
                        if self.slippage_tracker:
                            try:
                                exp_px = price if price is not None else result.get('expected_price')
                                exec_px = result.get('executed_price') or result.get('fill_price') or price
                                if exp_px is not None and exec_px is not None:
                                    self.slippage_tracker.record(symbol, float(exp_px), float(exec_px))
                            except Exception:
                                pass
                        if self._metrics_recorder:
                            try:
                                self._metrics_recorder.record_order(True, self.latency_monitor.get_current_latency_ms() if self.latency_monitor else 0.0)
                            except Exception:
                                pass
                        if self._audit_logger:
                            try:
                                self._audit_logger.log_event(
                                    event_type="ORDER_OK",
                                    order_id=str(ticket), symbol=symbol, status="OK",
                                    latency_ms=(self.latency_monitor.get_current_latency_ms() if self.latency_monitor else None),
                                    extra={'action': action, 'volume': volume}
                                )
                            except Exception:
                                pass
                        if self._session_state and isinstance(ticket, int):
                            try:
                                self._session_state.record_success(ticket, symbol, action, volume, result)
                            except Exception:
                                pass
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
                        # actualizar exposición de portafolio
                        if self._exposure_tracker and getattr(self.config, 'enable_portfolio_exposure_tracker', False):
                            try:
                                self._exposure_tracker.apply_execution(symbol, volume, action)
                            except Exception:
                                pass
                        return ExecutionResult(True, ticket=ticket, retries=attempt,
                                               placed_at=datetime.now(timezone.utc), extra=result)
                    last_error = result.get('error', 'unknown_error')
                    self.logger.warning(f"Executor returned failure: {last_error}", "EXECUTION")
                    if self._metrics_recorder:
                        try:
                            self._metrics_recorder.record_order(False, self.latency_monitor.get_current_latency_ms() if self.latency_monitor else 0.0)
                        except Exception:
                            pass
                    if self.slippage_tracker:
                        try:
                            self.slippage_tracker.persist_snapshot()
                        except Exception:
                            pass
                    if self._audit_logger:
                        try:
                            self._audit_logger.log_event(
                                event_type="ORDER_FAIL",
                                order_id=str(result.get('ticket','')), symbol=symbol, status="FAIL",
                                latency_ms=(self.latency_monitor.get_current_latency_ms() if self.latency_monitor else None),
                                extra={'error': last_error, 'action': action}
                            )
                        except Exception:
                            pass
                except Exception as e:  # ejecución robusta
                    last_error = f"exception:{e}"
                    self.logger.error(f"Execution exception attempt {attempt+1}: {e}", "EXECUTION")
                    self.breaker.record_failure()
                    # Alert on execution exception that could trigger circuit breaker
                    if self.alert_dispatcher and AlertCategory and AlertSeverity:
                        try:
                            self.alert_dispatcher.dispatch_order_failure(symbol, f"execution_exception: {e}",
                                                                       {"attempt": attempt+1, "action": action})
                        except Exception:
                            pass
                    if self._metrics_recorder:
                        try:
                            self._metrics_recorder.record_order(False, 0.0)
                        except Exception:
                            pass
                    if self._audit_logger:
                        try:
                            self._audit_logger.log_event(
                                event_type="ORDER_EXCEPTION",
                                order_id=None, symbol=symbol, status="EXCEPTION",
                                latency_ms=None, extra={'exc': str(e)}
                            )
                        except Exception:
                            pass
            if attempt < self.config.max_retries:
                time.sleep(self.config.retry_delay_seconds)
        # fracaso total
        if last_error:
            self.breaker.record_failure()
            # Alert on final failure
            if self.alert_dispatcher and AlertCategory and AlertSeverity:
                try:
                    self.alert_dispatcher.dispatch_order_failure(symbol, last_error, 
                                                               {"retries": self.config.max_retries, 
                                                                "action": action, "volume": volume})
                except Exception:
                    pass
        self._metrics['orders_total'] += 1
        self._metrics['orders_failed'] += 1
        if self._metrics_recorder:
            try:
                self._metrics_recorder.maybe_persist()
            except Exception:
                pass
        if self._audit_logger:
            try:
                self._audit_logger.log_event(
                    event_type="ORDER_FINAL_FAIL", order_id=None, symbol=symbol, status="FINAL_FAIL",
                    latency_ms=None, extra={'last_error': last_error, 'action': action}
                )
            except Exception:
                pass
        if self._session_state:
            try:
                self._session_state.record_failure(symbol, action, volume, last_error or 'execution_failed')
            except Exception:
                pass
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
        # Normalizar estructura para compatibilidad hacia atrás
        if not isinstance(self._cumulative, dict):
            self._cumulative = {}
        if 'orders_total' not in self._cumulative or not isinstance(self._cumulative.get('orders_total'), (int, float)):
            self._cumulative['orders_total'] = 0
        if 'orders_ok' not in self._cumulative or not isinstance(self._cumulative.get('orders_ok'), (int, float)):
            self._cumulative['orders_ok'] = 0
        if 'orders_failed' not in self._cumulative or not isinstance(self._cumulative.get('orders_failed'), (int, float)):
            self._cumulative['orders_failed'] = 0
        if 'sessions' not in self._cumulative or not isinstance(self._cumulative.get('sessions'), (int, float)):
            self._cumulative['sessions'] = 0
        # last_update puede ser str|None, no forzar tipo
        self._cumulative['sessions'] = int(self._cumulative.get('sessions', 0)) + 1

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
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'orders_total': self._metrics['orders_total'],
            'orders_ok': self._metrics['orders_ok'],
            'orders_failed': self._metrics['orders_failed'],
            'avg_latency_ms': avg_latency,
            'latency_samples_count': len(lat_list),
            'latency_percentiles': percentiles,
            'blocked_reasons': self._metrics.get('blocked_reasons', {})
        }
        if self.slippage_tracker:
            try:
                stats = self.slippage_tracker.current_stats()
                data['slippage'] = stats
            except Exception:
                pass
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
            'generated': datetime.now(timezone.utc).isoformat(),
            'orders_total': self._metrics['orders_total'],
            'orders_ok': self._metrics['orders_ok'],
            'orders_failed': self._metrics['orders_failed'],
            'latency_avg_ms': avg_latency,
            'latency_percentiles': latency_percentiles,
            'history': self._metrics['history'][-50:],  # recorte
            'blocked_reasons': self._metrics.get('blocked_reasons', {})
        }
        if self.slippage_tracker:
            try:
                summary['slippage'] = self.slippage_tracker.current_stats()
            except Exception:
                pass
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
        # Asegurar claves mínimas antes de sumar
        if 'orders_total' not in self._cumulative or not isinstance(self._cumulative.get('orders_total'), (int, float)):
            self._cumulative['orders_total'] = 0
        if 'orders_ok' not in self._cumulative or not isinstance(self._cumulative.get('orders_ok'), (int, float)):
            self._cumulative['orders_ok'] = 0
        if 'orders_failed' not in self._cumulative or not isinstance(self._cumulative.get('orders_failed'), (int, float)):
            self._cumulative['orders_failed'] = 0
        self._cumulative['orders_total'] = int(self._cumulative.get('orders_total', 0)) + int(self._metrics.get('orders_total', 0))
        self._cumulative['orders_ok'] = int(self._cumulative.get('orders_ok', 0)) + int(self._metrics.get('orders_ok', 0))
        self._cumulative['orders_failed'] = int(self._cumulative.get('orders_failed', 0)) + int(self._metrics.get('orders_failed', 0))
        self._cumulative['last_update'] = datetime.now(timezone.utc).isoformat()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._cumulative, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        # asegurar summary final
        self._persist_summary()
        if self._metrics_recorder:
            try:
                self._metrics_recorder.persist_cumulative()
            except Exception:
                pass
        if self._audit_logger:
            try:
                self._audit_logger.log_event(event_type="SHUTDOWN", status="OK")
            except Exception:
                pass
        if self._session_state:
            try:
                self._session_state.flush()
                self._session_state.persist_snapshot()
            except Exception:
                pass

__all__ = [
    'ExecutionRouter', 'ExecutionRouterConfig', 'ExecutionResult'
]
