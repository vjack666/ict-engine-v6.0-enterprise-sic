"""
Trade Executor - ICT Engine v6.0 Enterprise
Real Trade Execution System for Live Trading

Direct integration with MT5 API for real trading operations
Integrates with existing RiskManager for position sizing and risk management
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Import existing ICT Engine modules
from data_management.mt5_connection_manager import MT5ConnectionManager, get_mt5_connection
from risk_management.risk_manager import RiskManager

try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from smart_trading_logger import SmartTradingLogger
except ImportError:
    import logging
    SmartTradingLogger = None

from .trade_validator import TradeValidator, TradingLimits

# Import MT5 for trading operations
import MetaTrader5 as mt5

class OrderType(Enum):
    """Order types for trading"""
    BUY = mt5.ORDER_TYPE_BUY
    SELL = mt5.ORDER_TYPE_SELL
    BUY_LIMIT = mt5.ORDER_TYPE_BUY_LIMIT
    SELL_LIMIT = mt5.ORDER_TYPE_SELL_LIMIT
    BUY_STOP = mt5.ORDER_TYPE_BUY_STOP
    SELL_STOP = mt5.ORDER_TYPE_SELL_STOP

@dataclass
class TradeResult:
    """Result of trade execution"""
    success: bool
    ticket: Optional[int] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    execution_price: Optional[float] = None
    execution_time: Optional[datetime] = None
    slippage: Optional[float] = None
    
class TradeExecutor:
    """
    🚀 Real Trade Execution System for ICT Engine v6.0 Enterprise
    
    Direct MT5 API integration for real trading:
    - Real buy/sell order execution
    - Real position management
    - Real risk validation
    - Real trade logging
    
    No fallback or demo logic - only real trading operations
    """
    
    def __init__(self, validator: Optional[TradeValidator] = None):
        """Initialize trade executor with existing ICT modules"""
        # Use existing ICT Engine modules
        self.mt5_manager = get_mt5_connection()
        self.risk_manager = RiskManager()
        
        # Initialize logger correctly
        if SmartTradingLogger:
            self.logger = SmartTradingLogger(__name__).logger
        else:
            self.logger = logging.getLogger(__name__)
            
        self.validator = validator or TradeValidator()
        
        # Track execution statistics
        self.trades_executed = 0
        self.successful_trades = 0
        self.failed_trades = 0
        self.total_slippage = 0.0
        
        self.logger.info("✅ TradeExecutor initialized with real MT5 integration")
    def execute_silver_bullet_trade(self, signal: Dict[str, Any]) -> TradeResult:
        """
        Execute a Silver Bullet trade signal with full validation and risk management
        
        Args:
            signal: Trading signal with symbol, direction, entry_price, stop_loss, take_profit
            
        Returns:
            TradeResult with execution details
        """
        try:
            self.logger.info(f"🎯 Executing Silver Bullet trade: {signal['symbol']} {signal['direction']}")
            
            # 1. Ensure MT5 connection
            if not self.mt5_manager.ensure_connection():
                return TradeResult(
                    success=False,
                    error_message="MT5 connection failed"
                )
            
            # 2. Get current account info
            account_info = self.mt5_manager.get_account_info()
            if not account_info:
                return TradeResult(
                    success=False,
                    error_message="Cannot get account information"
                )
            
            # 3. Validate trade signal
            is_valid, validation_error = self.validator.validate_trade_signal(signal, account_info)
            if not is_valid:
                return TradeResult(
                    success=False,
                    error_message=f"Validation failed: {validation_error}"
                )
            
            # 4. Calculate position size using existing RiskManager
            if 'position_size' not in signal:
                position_size = self.risk_manager.calculate_position_size(
                    account_balance=account_info['balance'],
                    entry_price=signal['entry_price'],
                    stop_loss=signal['stop_loss']
                )
                signal['position_size'] = position_size
                
            self.logger.info(f"Position size calculated: {signal['position_size']} lots")
            
            # 5. Execute trade based on direction using MT5ConnectionManager
            if signal['direction'].lower() == 'buy':
                mt5_result = self.mt5_manager.place_buy_order(
                    symbol=signal['symbol'],
                    volume=signal['position_size'],
                    sl=signal['stop_loss'],
                    tp=signal['take_profit'],
                    comment=f"ICT_SB_BUY_{datetime.now().strftime('%H%M%S')}"
                )
            else:  # sell
                mt5_result = self.mt5_manager.place_sell_order(
                    symbol=signal['symbol'],
                    volume=signal['position_size'],
                    sl=signal['stop_loss'],
                    tp=signal['take_profit'],
                    comment=f"ICT_SB_SELL_{datetime.now().strftime('%H%M%S')}"
                )
            
            # 6. Convert MT5 result to TradeResult
            if mt5_result['success']:
                result = TradeResult(
                    success=True,
                    ticket=mt5_result.get('ticket'),
                    execution_time=datetime.now()
                )
            else:
                result = TradeResult(
                    success=False,
                    error_code=mt5_result.get('error_code'),
                    error_message=mt5_result.get('message')
                )
            
            # 7. Update statistics
            self._update_execution_stats(result)
            
            # 8. Update validator daily stats
            if result.success:
                self.validator.update_daily_stats({
                    'status': 'opened',
                    'profit': 0.0,  # Will be updated when closed
                    'symbol': signal['symbol']
                })
            
            # 9. Log execution result
            self._log_trade_execution(signal, result, account_info)
            
            return result
            
        except Exception as e:
            error_msg = f"Trade execution error: {str(e)}"
            self.logger.error(error_msg)
            return TradeResult(
                success=False,
                error_message=error_msg
            )
    
    def close_position_by_ticket(self, ticket: int) -> TradeResult:
        """Close position using MT5ConnectionManager"""
        try:
            result = self.mt5_manager.close_position(ticket=ticket)
            
            if result['success']:
                trade_result = TradeResult(
                    success=True,
                    ticket=result.get('ticket'),
                    execution_time=datetime.now()
                )
            else:
                trade_result = TradeResult(
                    success=False,
                    error_code=result.get('error_code'),
                    error_message=result.get('message')
                )
                
            self._update_execution_stats(trade_result)
            return trade_result
            
        except Exception as e:
            return TradeResult(
                success=False,
                error_message=f"Close position error: {str(e)}"
            )
    
    def modify_position_by_ticket(self, ticket: int, stop_loss: Optional[float] = None, 
                                take_profit: Optional[float] = None) -> TradeResult:
        """Modify position using MT5ConnectionManager"""
        try:
            result = self.mt5_manager.modify_position(
                ticket=ticket,
                sl=stop_loss,
                tp=take_profit
            )
            
            if result['success']:
                trade_result = TradeResult(
                    success=True,
                    ticket=result.get('ticket'),
                    execution_time=datetime.now()
                )
            else:
                trade_result = TradeResult(
                    success=False,
                    error_code=result.get('error_code'),
                    error_message=result.get('message')
                )
                
            self._update_execution_stats(trade_result)
            return trade_result
            
        except Exception as e:
            return TradeResult(
                success=False,
                error_message=f"Modify position error: {str(e)}"
            )
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """Get open positions using MT5ConnectionManager"""
        try:
            return self.mt5_manager.get_open_positions()
        except Exception as e:
            self.logger.error(f"Error getting positions: {str(e)}")
            return []
    
    def emergency_stop_all(self) -> Dict[str, Any]:
        """
        🚨 EMERGENCY: Close all open positions immediately
        """
        try:
            self.logger.warning("🚨 EMERGENCY STOP: Closing all positions")
            
            positions = self.get_open_positions()
            if not positions:
                return {
                    'success': True,
                    'message': 'No open positions to close',
                    'positions_closed': 0
                }
            
            closed_count = 0
            failed_count = 0
            errors = []
            
            for position in positions:
                result = self.close_position_by_ticket(position['ticket'])
                if result.success:
                    closed_count += 1
                    self.logger.info(f"✅ Emergency closed position {position['ticket']}")
                else:
                    failed_count += 1
                    errors.append(f"Position {position['ticket']}: {result.error_message}")
                    self.logger.error(f"❌ Failed to close position {position['ticket']}: {result.error_message}")
            
            return {
                'success': failed_count == 0,
                'message': f'Emergency stop completed: {closed_count} closed, {failed_count} failed',
                'positions_closed': closed_count,
                'positions_failed': failed_count,
                'errors': errors
            }
            
        except Exception as e:
            error_msg = f"Emergency stop error: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'positions_closed': 0
            }
    
    def _update_execution_stats(self, result: TradeResult) -> None:
        """Update execution statistics"""
        self.trades_executed += 1
        
        if result.success:
            self.successful_trades += 1
            if result.slippage:
                self.total_slippage += result.slippage
        else:
            self.failed_trades += 1
    
    def _log_trade_execution(self, signal: Dict[str, Any], result: TradeResult, 
                           account_info: Dict[str, Any]) -> None:
        """Log complete trade execution details"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'signal': signal,
            'result': {
                'success': result.success,
                'ticket': result.ticket,
                'execution_price': result.execution_price,
                'slippage': result.slippage,
                'error_message': result.error_message
            },
            'account_before': {
                'balance': account_info['balance'],
                'equity': account_info['equity'],
                'margin_free': account_info['margin_free']
            },
            'execution_stats': {
                'total_trades': self.trades_executed,
                'successful_trades': self.successful_trades,
                'failed_trades': self.failed_trades,
                'success_rate': self.successful_trades / max(self.trades_executed, 1),
                'avg_slippage': self.total_slippage / max(self.successful_trades, 1)
            }
        }
        
        if result.success:
            self.logger.info(f"✅ TRADE EXECUTED: {signal['symbol']} {signal['direction']} at {result.execution_price}")
        else:
            self.logger.error(f"❌ TRADE FAILED: {signal['symbol']} {signal['direction']} - {result.error_message}")
        
        # Log detailed data
        self.logger.info(f"📊 Trade execution details: {log_data}")
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution statistics summary"""
        return {
            'total_trades_executed': self.trades_executed,
            'successful_trades': self.successful_trades,
            'failed_trades': self.failed_trades,
            'success_rate': self.successful_trades / max(self.trades_executed, 1) * 100,
            'average_slippage': self.total_slippage / max(self.successful_trades, 1),
            'validator_summary': self.validator.get_validation_summary()
        }
