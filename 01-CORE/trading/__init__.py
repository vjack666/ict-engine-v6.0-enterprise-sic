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

__all__ = [
    # Core classes
    'RealTradingSystem',
    'TradeValidator',
    'TradeExecutor', 
    'DashboardTradingIntegrator',
    'RealTradingLogger',
    
    # Data classes
    'TradingLimits',
    'TradeResult',
    'DashboardTradeSignal',
    'DashboardTradeStatus',
    
    # Enums
    'OrderType'
]

# Version info
__version__ = "6.0.0"
__status__ = "Enterprise"
__author__ = "ICT Engine Development Team"
