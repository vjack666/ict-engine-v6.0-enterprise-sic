"""Risk Pipeline Facade - Fase 1
Centraliza el flujo de evaluación de riesgo y sizing reutilizando
componentes existentes sin introducir lógica duplicada.

Etapas:
1. Hard Guards (RiskGuard)
2. Strategic Adjustments (RiskManager)
3. Position Sizing (PositionSizingCalculator)
4. Per-Order Fast Gate (RealTimeRiskGuard)

Salida unificada: RiskPipelineDecision

No elimina rutas existentes; ofrece un único entrypoint para nuevas
integraciones (trading loop, dashboard, validation pipeline).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Protocol, runtime_checkable, TYPE_CHECKING
from datetime import datetime

class _LoggerLike(Protocol):
    def info(self, m: str, c: str) -> None: ...
    def warning(self, m: str, c: str) -> None: ...
    def error(self, m: str, c: str) -> None: ...
    def debug(self, m: str, c: str) -> None: ...

# Logging central (safe fallback)
try:  # Attempt enterprise logger
    from protocols.logging_central_protocols import create_safe_logger as _enterprise_create_safe_logger  # type: ignore
    def create_safe_logger(component_name: str, fallback_to_print: bool = True, log_level: Any = None, **kwargs: Any) -> _LoggerLike:  # type: ignore[override]
        return _enterprise_create_safe_logger(component_name, fallback_to_print=fallback_to_print, log_level=log_level, **kwargs)  # type: ignore
except ImportError:  # pragma: no cover - fallback to minimal logger
    from smart_trading_logger import enviar_senal_log as _compat_log
    class _CompatLogger:
        def info(self, m: str, c: str) -> None: _compat_log("INFO", m, c)
        def warning(self, m: str, c: str) -> None: _compat_log("WARNING", m, c)
        def error(self, m: str, c: str) -> None: _compat_log("ERROR", m, c)
        def debug(self, m: str, c: str) -> None: _compat_log("DEBUG", m, c)
    def create_safe_logger(component_name: str, fallback_to_print: bool = True, log_level: Any = None, **kwargs: Any) -> _LoggerLike:  # type: ignore[override]
        return _CompatLogger()

# Component imports (lazy; provide minimal runtime stubs if missing)
if TYPE_CHECKING:
    from .risk_guard import RiskGuard  # pragma: no cover
    from .risk_manager import RiskManager  # pragma: no cover
    from .position_sizing import PositionSizingCalculator, PositionSizingParameters, PositionSizingResult  # pragma: no cover
    from .real_time_risk_guard import RealTimeRiskGuard  # pragma: no cover
else:
    try:
        from .risk_guard import RiskGuard  # type: ignore
    except Exception:  # pragma: no cover
        class RiskGuard:  # type: ignore
            def evaluate(self, **_: Any) -> Dict[str, Any]: return {}
    try:
        from .risk_manager import RiskManager  # type: ignore
    except Exception:  # pragma: no cover
        class RiskManager:  # type: ignore
            def calculate_ict_position_size(self, *_: Any, **__: Any) -> float: return 0.0
            def calculate_correlation_risk(self, *_: Any, **__: Any) -> float: return 0.0
    try:
        from .position_sizing import PositionSizingCalculator, PositionSizingParameters, PositionSizingResult  # type: ignore
    except Exception:  # pragma: no cover
        class PositionSizingParameters:  # type: ignore
            def __init__(self, **_: Any): pass
        class PositionSizingResult:  # type: ignore
            lots: float = 0.0
            is_valid: bool = False
            risk_amount: float = 0.0
            confidence_score: float = 0.0
            position_value: float = 0.0
        class PositionSizingCalculator:  # type: ignore
            def calculate_position_size(self, _params: Any) -> PositionSizingResult: return PositionSizingResult()
    try:
        from .real_time_risk_guard import RealTimeRiskGuard  # type: ignore
    except Exception:  # pragma: no cover
        class RealTimeRiskGuard:  # type: ignore
            def evaluate(self, _ctx: Dict[str, Any]) -> Any:
                class _Res:
                    approved = True
                    computed_risk_pct = 0.0
                    reasons: List[str] = []
                return _Res()

@runtime_checkable
class AlertEmitter(Protocol):  # minimal subset
    def emit(self, **kwargs: Any) -> None: ...

@dataclass
class RiskPipelineDecision:
    approved: bool
    reasons: List[str] = field(default_factory=list)
    lots: float = 0.0
    risk_pct: float = 0.0
    stage: str = "initial"
    correlation_score: float = 0.0
    exposure: Dict[str, float] = field(default_factory=dict)
    ict_factors: Dict[str, Any] = field(default_factory=dict)
    sizing_metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class RiskPipeline:
    def __init__(self,
                 risk_guard: Optional[RiskGuard] = None,
                 risk_manager: Optional[RiskManager] = None,
                 position_sizer: Optional[PositionSizingCalculator] = None,
                 fast_gate: Optional[RealTimeRiskGuard] = None,
                 alert_emitter: Optional[AlertEmitter] = None):
        self.logger = create_safe_logger("RiskPipeline")  # type: ignore[assignment]
        self.risk_guard = risk_guard
        self.risk_manager = risk_manager
        self.position_sizer = position_sizer
        self.fast_gate = fast_gate
        self.alert_emitter = alert_emitter
        self._metrics = {
            'decisions_total': 0,
            'rejections_total': 0,
        }
        self.logger.info("✅ RiskPipeline inicializado (fase 1)", "risk_pipeline")

    def _emit_alert(self, level: str, message: str, code: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        if not self.alert_emitter:
            return
        try:
            self.alert_emitter.emit(
                level=level,
                message=message,
                code=code,
                component="risk_pipeline",
                metadata=metadata or {},
                channel="RISK",
            )
        except Exception:
            pass

    def evaluate_and_size(self, signal_ctx: Dict[str, Any]) -> RiskPipelineDecision:
        self._metrics['decisions_total'] += 1
        decision = RiskPipelineDecision(approved=False)

        # 1. Hard Guards
        if self.risk_guard:
            try:
                balance = float(signal_ctx.get('account_balance', 0.0))
                equity = float(signal_ctx.get('account_equity', balance))
                rg_snapshot = self.risk_guard.evaluate(balance=balance, equity=equity)
                decision.exposure = rg_snapshot.get('exposure', {})
                violations = rg_snapshot.get('violations', [])
                if violations:
                    decision.reasons.extend([v.lower() for v in violations])
                    decision.stage = 'risk_guard'
                    self._metrics['rejections_total'] += 1
                    self._emit_alert("CRITICAL", f"RiskGuard violaciones {violations}", "risk_guard_violation")
                    return decision
            except Exception as e:  # no abortar si guard falla
                self.logger.error(f"RiskGuard error: {e}", "risk_pipeline")

        # 2. Strategic Adjustments / ICT factors
        ict_adjust = {}
        correlation_score = 0.0
        lots_hint = None
        if self.risk_manager:
            try:
                # Sizing ICT si contamos con stop y entry
                entry = signal_ctx.get('entry_price')
                sl = signal_ctx.get('stop_loss')
                bal = signal_ctx.get('account_balance')
                poi_quality = signal_ctx.get('poi_quality', 'B')
                smart_flag = bool(signal_ctx.get('smart_money_signal', False))
                session = signal_ctx.get('session', 'london')
                if all(v is not None for v in (entry, sl, bal)):
                    try:
                        bal_f = float(bal)  # type: ignore[arg-type]
                        entry_f = float(entry)  # type: ignore[arg-type]
                        sl_f = float(sl)  # type: ignore[arg-type]
                        lots_hint = self.risk_manager.calculate_ict_position_size(
                            bal_f, entry_f, sl_f, poi_quality=poi_quality, smart_money_signal=smart_flag, session=session
                        )
                    except Exception as _conv_err:
                        self.logger.warning(f"Conv error sizing hint: {_conv_err}", "risk_pipeline")
                # Correlación simplificada
                open_positions = signal_ctx.get('open_positions', [])
                symbol = signal_ctx.get('symbol')
                if open_positions and symbol:
                    correlation_score = self.risk_manager.calculate_correlation_risk(open_positions, symbol)
                    if correlation_score >= 0.9:
                        decision.reasons.append('correlation_extreme')
                        decision.stage = 'risk_manager'
                        self._metrics['rejections_total'] += 1
                        self._emit_alert("WARNING", "Correlación extrema detectada", "correlation_extreme")
                        return decision
                    elif correlation_score >= 0.7:
                        self._emit_alert("INFO", "Correlación elevada", "correlation_high")
                ict_adjust = {
                    'poi_quality': poi_quality,
                    'smart_money_signal': smart_flag,
                    'session': session,
                }
            except Exception as e:
                self.logger.error(f"RiskManager etapa error: {e}", "risk_pipeline")

        decision.correlation_score = correlation_score
        decision.ict_factors = ict_adjust

        # 3. Position Sizing (base)
        lots = 0.0
        sizing_meta: Dict[str, Any] = {}
        if self.position_sizer and PositionSizingParameters is not None:
            try:
                entry = signal_ctx.get('entry_price')
                sl = signal_ctx.get('stop_loss')
                bal = signal_ctx.get('account_balance')
                risk_pct = float(signal_ctx.get('risk_percent', 1.0))
                symbol = signal_ctx.get('symbol', 'UNKNOWN')
                if all(v is not None for v in (entry, sl, bal)):
                    bal_f = float(bal)  # type: ignore[arg-type]
                    entry_f = float(entry)  # type: ignore[arg-type]
                    sl_f = float(sl)  # type: ignore[arg-type]
                    params = PositionSizingParameters(
                        symbol=symbol,
                        account_balance=bal_f,
                        risk_percent=risk_pct,
                        entry_price=entry_f,
                        stop_loss=sl_f,
                    )
                    result = self.position_sizer.calculate_position_size(params)
                    if result.is_valid:
                        lots = result.lots
                        sizing_meta = {
                            'risk_amount': result.risk_amount,
                            'confidence': result.confidence_score,
                            'base_position_value': result.position_value,
                        }
                    else:
                        decision.reasons.append('invalid_sizing')
                        decision.stage = 'position_sizing'
                        self._metrics['rejections_total'] += 1
                        return decision
            except Exception as e:
                self.logger.error(f"PositionSizing error: {e}", "risk_pipeline")
        # Si RiskManager dio hint más conservador o mayor coherente, usamos promedio simple
        if lots_hint and lots_hint > 0 and lots > 0:
            # blend respetando mínimo
            lots = round((lots + lots_hint) / 2, 2)
        elif lots_hint and lots == 0:
            lots = lots_hint

        decision.lots = lots
        decision.sizing_metadata = sizing_meta

        # 4. Per-Order Fast Gate
        if self.fast_gate:
            try:
                fast_res = self.fast_gate.evaluate({
                    'symbol': signal_ctx.get('symbol'),
                    'risk_pct': signal_ctx.get('risk_percent', 1.0)
                })
                decision.risk_pct = fast_res.computed_risk_pct
                if not fast_res.approved:
                    decision.reasons.extend(fast_res.reasons)
                    decision.stage = 'fast_gate'
                    self._metrics['rejections_total'] += 1
                    self._emit_alert("WARNING", f"Fast gate rechazo {fast_res.reasons}", "fast_gate_reject")
                    return decision
            except Exception as e:
                self.logger.error(f"FastGate error: {e}", "risk_pipeline")

        # Aprobado
        decision.approved = True
        decision.stage = 'approved'
        return decision

    def metrics_snapshot(self) -> Dict[str, Any]:
        return dict(self._metrics)

__all__ = [
    'RiskPipeline', 'RiskPipelineDecision'
]
