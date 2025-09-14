"""
Real Trading Module - ICT Engine v6.0 Enterprise
==============================================

Componentes críticos para trading en cuenta real:
- Auto Position Sizing
- Emergency Stop System  
- Signal Validation
- Execution Engine

Integra con sistema ICT Engine existente.
"""

from .auto_position_sizer import AutoPositionSizer
from .emergency_stop_system import EmergencyStopSystem
from .signal_validator import SignalValidator
from .execution_engine import ExecutionEngine

# Advanced monitoring & risk modules (import errors ignorados gracefully)
try:
    from .account_health_monitor import AccountHealthMonitor, AccountHealthStatus
except Exception:  # pragma: no cover - ausencia opcional
    AccountHealthMonitor = None  # type: ignore
    AccountHealthStatus = None  # type: ignore

try:
    from .connection_watchdog import ConnectionWatchdog, ConnectionStats
except Exception:  # pragma: no cover
    ConnectionWatchdog = None  # type: ignore
    ConnectionStats = None  # type: ignore

try:
    from .latency_monitor import LatencyMonitor, LatencySample
except Exception:  # pragma: no cover
    LatencyMonitor = None  # type: ignore
    LatencySample = None  # type: ignore

try:
    from .metrics_collector import MetricsCollector, MetricPoint
except Exception:  # pragma: no cover
    MetricsCollector = None  # type: ignore
    MetricPoint = None  # type: ignore

try:
    from .trade_journal import TradeJournal, JournalEntry
except Exception:  # pragma: no cover
    TradeJournal = None  # type: ignore
    JournalEntry = None  # type: ignore

try:
    from .dynamic_risk_adjuster import DynamicRiskAdjuster, RiskAdjustmentDecision
except Exception:  # pragma: no cover
    DynamicRiskAdjuster = None  # type: ignore
    RiskAdjustmentDecision = None  # type: ignore

__all__ = [
    'AutoPositionSizer',
    'EmergencyStopSystem', 
    'SignalValidator',
    'ExecutionEngine',
    # Advanced (solo si disponibles)
    'AccountHealthMonitor', 'AccountHealthStatus',
    'ConnectionWatchdog', 'ConnectionStats',
    'LatencyMonitor', 'LatencySample',
    'MetricsCollector', 'MetricPoint',
    'TradeJournal', 'JournalEntry',
    'DynamicRiskAdjuster', 'RiskAdjustmentDecision'
]

__version__ = "1.0.0"
