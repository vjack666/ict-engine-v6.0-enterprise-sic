"""
ICT Engine v6.0 Enterprise - Real Trading Module
Complete real trading system with validation, execution, and safety features

This module converts the ICT Engine from demo/analysis to full real trading capabilities
while maintaining all existing functionality and adding enterprise-grade safety features.
"""

from .trade_validator import TradeValidator, TradingLimits
from .trade_executor import TradeExecutor, TradeResult, OrderType
from .dashboard_integrator import (
    DashboardTradingIntegrator, 
    DashboardTradeSignal, 
    DashboardTradeStatus
)
from .real_trading_logger import RealTradingLogger
from .real_trading_system import RealTradingSystem

# Nuevos módulos enterprise para cuenta real
try:
    from .execution_engine import ExecutionEngine, OrderRequest, OrderResult, OrderType as ExecutionOrderType
    EXECUTION_ENGINE_AVAILABLE = True
except ImportError:
    ExecutionEngine = None
    OrderRequest = None
    OrderResult = None
    ExecutionOrderType = None
    EXECUTION_ENGINE_AVAILABLE = False

try:
    from .live_trading_engine import (
        LiveTradingEngine, 
        TradingSignal, 
        SignalType,
        TradingStatus,
        LivePosition,
        create_live_trading_engine,
        create_trading_signal
    )
    LIVE_TRADING_ENGINE_AVAILABLE = True
except ImportError:
    LiveTradingEngine = None
    TradingSignal = None
    SignalType = None
    TradingStatus = None
    LivePosition = None
    create_live_trading_engine = None
    create_trading_signal = None
    LIVE_TRADING_ENGINE_AVAILABLE = False

__all__ = [
    # Core classes
    'RealTradingSystem',
    'TradeValidator',
    'TradeExecutor', 
    'DashboardTradingIntegrator',
    'RealTradingLogger',
    
    # Nuevos módulos enterprise
    'ExecutionEngine',
    'LiveTradingEngine',
    
    # Data classes
    'TradingLimits',
    'TradeResult',
    'DashboardTradeSignal',
    'DashboardTradeStatus',
    'OrderRequest',
    'OrderResult',
    'TradingSignal',
    'LivePosition',
    
    # Enums
    'OrderType',
    'SignalType',
    'TradingStatus',
    
    # Factory functions
    'create_live_trading_engine',
    'create_trading_signal',
    
    # Flags de disponibilidad
    'EXECUTION_ENGINE_AVAILABLE',
    'LIVE_TRADING_ENGINE_AVAILABLE'
]

# Version info
__version__ = "6.0.0"
__status__ = "Enterprise"
__author__ = "ICT Engine Development Team"
