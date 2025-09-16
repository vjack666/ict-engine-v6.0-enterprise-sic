"""StrategyPipeline
Orquesta flujo: validar entorno/datos -> evaluar riesgo -> sizing -> ejecutar.
Depende de RiskPipeline existente y trackers opcionales.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Dict, Any, Optional
from datetime import datetime, timezone

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except Exception:  # pragma: no cover
    def create_safe_logger(name: str, **_):
        class _Mini:
            def info(self, m: str, c: str): print(f"[INFO][{c}] {m}")
            def warning(self, m: str, c: str): print(f"[WARN][{c}] {m}")
            def error(self, m: str, c: str): print(f"[ERROR][{c}] {m}")
        return _Mini()

class StrategyPipeline:
    def __init__(self,
                 risk_pipeline: Any,
                 env_validator: Optional[Any] = None,
                 data_validator: Optional[Any] = None,
                 order_tracker: Optional[Any] = None,
                 metrics: Optional[Any] = None,
                 executor: Optional[Any] = None):
        self.logger = get_unified_logger("StrategyPipeline")
        self.risk_pipeline = risk_pipeline
        self.env_validator = env_validator
        self.data_validator = data_validator
        self.order_tracker = order_tracker
        self.metrics = metrics
        self.executor = executor

    def process_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        start_ts = datetime.now(timezone.utc)
        decision_data: Dict[str, Any] = {
            'signal_id': signal.get('id'),
            'received_at': start_ts.isoformat(),
            'status': 'PENDING'
        }
        # Environment pre-check (cached result)
        if self.env_validator:
            env_last = self.env_validator.last_result() if hasattr(self.env_validator, 'last_result') else {}
            if env_last.get('status') == 'ERROR':
                decision_data['status'] = 'BLOCKED_ENV'
                return decision_data
        # Data quality quick check (non blocking unless ERROR future case)
        if self.data_validator:
            dq_last = self.data_validator.last_result() if hasattr(self.data_validator, 'last_result') else {}
            if dq_last.get('status') == 'WARN':
                decision_data['data_quality_warning'] = True
        # Risk evaluation + sizing
        try:
            rp_decision = self.risk_pipeline.evaluate_and_size(signal)
            decision_data['risk'] = {
                'approved': rp_decision.approved,
                'lots': rp_decision.lots,
                'stage': rp_decision.stage,
                'reasons': rp_decision.reasons,
                'correlation': rp_decision.correlation_score
            }
            if not rp_decision.approved:
                decision_data['status'] = 'REJECTED'
                if self.metrics:
                    self.metrics.incr('risk_rejections')
                return decision_data
        except Exception as e:  # pragma: no cover
            decision_data['status'] = 'ERROR_RISK'
            decision_data['error'] = str(e)
            return decision_data
        # Execution (placeholder or real)
        executed = False
        if self.executor and hasattr(self.executor, 'execute_order'):
            try:
                self.executor.execute_order(signal, rp_decision.lots)  # type: ignore[arg-type]
                executed = True
            except Exception as e:  # pragma: no cover
                decision_data['status'] = 'ERROR_EXEC'
                decision_data['error'] = str(e)
                return decision_data
        else:
            # Simulación mínima sin side-effects persistentes
            executed = True
        if executed and self.order_tracker and rp_decision.lots > 0:
            self.order_tracker.upsert_position(
                symbol=signal.get('symbol', 'UNKNOWN'),
                lots=rp_decision.lots,
                entry_price=signal.get('entry_price', 0.0),
                direction=signal.get('direction', 'buy')
            )
        end_ts = datetime.now(timezone.utc)
        latency_ms = (end_ts - start_ts).total_seconds() * 1000.0
        decision_data['latency_ms'] = round(latency_ms, 2)
        decision_data['status'] = 'EXECUTED'
        if self.metrics:
            self.metrics.incr('signals_processed')
            self.metrics.set_gauge('last_latency_ms', latency_ms)
        return decision_data

__all__ = ["StrategyPipeline"]
