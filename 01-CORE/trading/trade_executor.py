"""
Trade Executor - ICT Engine v6.0 Enterprise
Real Trade Execution System for Demo Accounts

Extends existing MT5ConnectionManager with actual trading capabilities
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
    from smart_trading_logger import SmartTradingLogger
except ImportError:
    import logging
    class SmartTradingLogger:
        @staticmethod
        def get_logger(name: str):
            return logging.getLogger(name)

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
    
    EXTENDS existing modules with actual trading capabilities:
    
    🔧 EXTENDS MT5ConnectionManager with:
    - place_buy_order() - MISSING in current implementation
    - place_sell_order() - MISSING in current implementation  
    - close_position() - MISSING in current implementation
    - modify_position() - MISSING in current implementation
    - get_open_positions() - MISSING in current implementation
    
    ✅ USES existing RiskManager for:
    - calculate_position_size() - AVAILABLE
    - Risk validation and limits - AVAILABLE
    
    ✅ INTEGRATES with existing SmartTradingLogger for:
    - Comprehensive trade logging - AVAILABLE
    
    🚨 CRITICAL MODULE EXTENSIONS NEEDED:
    This class identifies and implements the missing trading methods
    that need to be added to MT5ConnectionManager for real trading.
    """
    
    def __init__(self, validator: Optional[TradeValidator] = None):
        """Initialize trade executor with existing ICT modules"""
        # Use existing ICT Engine modules
        self.mt5_manager = get_mt5_connection()
        self.risk_manager = RiskManager()
        
        # Initialize logger correctly
        if hasattr(SmartTradingLogger, 'get_logger'):
            self.logger = SmartTradingLogger.get_logger(__name__)
        else:
            self.logger = logging.getLogger(__name__)
            
        self.validator = validator or TradeValidator()
        
        # Track execution statistics
        self.trades_executed = 0
        self.successful_trades = 0
        self.failed_trades = 0
        self.total_slippage = 0.0
        
        # Validate and extend MT5ConnectionManager capabilities
        self._validate_and_extend_mt5_capabilities()
        
    def _validate_and_extend_mt5_capabilities(self) -> None:
        """
        🚨 CRITICAL: Validate MT5ConnectionManager and add missing methods
        """
        self.logger.warning("""
🚨 CRITICAL: MT5ConnectionManager MISSING TRADING METHODS

Current MT5ConnectionManager has these methods:
- connect() ✅
- get_account_info() ✅  
- ensure_connection() ✅

MISSING METHODS for REAL TRADING:
- place_buy_order() ❌
- place_sell_order() ❌
- close_position() ❌
- modify_position() ❌
- get_open_positions() ❌

🔧 SOLUTION: TradeExecutor implements these methods temporarily
until MT5ConnectionManager is extended.
        """)
        
        # Extend MT5ConnectionManager with trading methods
        self._extend_mt5_manager()
        
    def _extend_mt5_manager(self) -> None:
        """
        Extend MT5ConnectionManager with missing trading methods
        This is a temporary solution until the main class is updated
        """
        # Add trading methods to existing MT5ConnectionManager instance
        self.mt5_manager.place_buy_order = self._place_buy_order
        self.mt5_manager.place_sell_order = self._place_sell_order
        self.mt5_manager.close_position = self._close_position
        self.mt5_manager.modify_position = self._modify_position
        self.mt5_manager.get_open_positions = self._get_open_positions
        
        self.logger.info("✅ MT5ConnectionManager extended with trading methods")
    
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
            
            # 5. Execute trade based on direction
            if signal['direction'].lower() == 'buy':
                result = self._place_buy_order(
                    symbol=signal['symbol'],
                    lot_size=signal['position_size'],
                    stop_loss=signal['stop_loss'],
                    take_profit=signal['take_profit'],
                    comment=f"ICT_SB_BUY_{datetime.now().strftime('%H%M%S')}"
                )
            else:  # sell
                result = self._place_sell_order(
                    symbol=signal['symbol'],
                    lot_size=signal['position_size'],
                    stop_loss=signal['stop_loss'],
                    take_profit=signal['take_profit'],
                    comment=f"ICT_SB_SELL_{datetime.now().strftime('%H%M%S')}"
                )
            
            # 6. Update statistics
            self._update_execution_stats(result)
            
            # 7. Update validator daily stats
            if result.success:
                self.validator.update_daily_stats({
                    'status': 'opened',
                    'profit': 0.0,  # Will be updated when closed
                    'symbol': signal['symbol']
                })
            
            # 8. Log execution result
            self._log_trade_execution(signal, result, account_info)
            
            return result
            
        except Exception as e:
            error_msg = f"Trade execution error: {str(e)}"
            self.logger.error(error_msg)
            return TradeResult(
                success=False,
                error_message=error_msg
            )
    
    def _place_buy_order(self, symbol: str, lot_size: float, stop_loss: Optional[float] = None, 
                        take_profit: Optional[float] = None, comment: str = "ICT_BUY") -> TradeResult:
        """
        🔧 MISSING FROM MT5ConnectionManager - Place buy order
        """
        try:
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_BUY,
                "deviation": 20,
                "magic": 12345,  # ICT Engine magic number
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Add stop loss and take profit if provided
            if stop_loss:
                request["sl"] = stop_loss
            if take_profit:
                request["tp"] = take_profit
            
            # Send order
            result = mt5.order_send(request)
            
            if result is None:
                return TradeResult(
                    success=False,
                    error_message="Order send failed - no result"
                )
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return TradeResult(
                    success=False,
                    error_code=result.retcode,
                    error_message=f"Order failed: {result.comment}"
                )
            
            # Calculate slippage
            ask_price = mt5.symbol_info_tick(symbol).ask
            slippage = abs(result.price - ask_price) if ask_price else 0.0
            
            return TradeResult(
                success=True,
                ticket=result.order,
                execution_price=result.price,
                execution_time=datetime.now(),
                slippage=slippage
            )
            
        except Exception as e:
            return TradeResult(
                success=False,
                error_message=f"Buy order error: {str(e)}"
            )
    
    def _place_sell_order(self, symbol: str, lot_size: float, stop_loss: Optional[float] = None, 
                         take_profit: Optional[float] = None, comment: str = "ICT_SELL") -> TradeResult:
        """
        🔧 MISSING FROM MT5ConnectionManager - Place sell order
        """
        try:
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_SELL,
                "deviation": 20,
                "magic": 12345,  # ICT Engine magic number
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Add stop loss and take profit if provided
            if stop_loss:
                request["sl"] = stop_loss
            if take_profit:
                request["tp"] = take_profit
            
            # Send order
            result = mt5.order_send(request)
            
            if result is None:
                return TradeResult(
                    success=False,
                    error_message="Order send failed - no result"
                )
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return TradeResult(
                    success=False,
                    error_code=result.retcode,
                    error_message=f"Order failed: {result.comment}"
                )
            
            # Calculate slippage
            bid_price = mt5.symbol_info_tick(symbol).bid
            slippage = abs(result.price - bid_price) if bid_price else 0.0
            
            return TradeResult(
                success=True,
                ticket=result.order,
                execution_price=result.price,
                execution_time=datetime.now(),
                slippage=slippage
            )
            
        except Exception as e:
            return TradeResult(
                success=False,
                error_message=f"Sell order error: {str(e)}"
            )
    
    def _close_position(self, ticket: int) -> TradeResult:
        """
        🔧 MISSING FROM MT5ConnectionManager - Close position
        """
        try:
            # Get position info
            position = None
            positions = mt5.positions_get(ticket=ticket)
            if positions and len(positions) > 0:
                position = positions[0]
            else:
                return TradeResult(
                    success=False,
                    error_message=f"Position {ticket} not found"
                )
            
            # Prepare close request
            close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": close_type,
                "position": ticket,
                "deviation": 20,
                "magic": 12345,
                "comment": f"Close_{ticket}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send close order
            result = mt5.order_send(request)
            
            if result is None:
                return TradeResult(
                    success=False,
                    error_message="Close order failed - no result"
                )
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return TradeResult(
                    success=False,
                    error_code=result.retcode,
                    error_message=f"Close failed: {result.comment}"
                )
            
            return TradeResult(
                success=True,
                ticket=result.order,
                execution_price=result.price,
                execution_time=datetime.now()
            )
            
        except Exception as e:
            return TradeResult(
                success=False,
                error_message=f"Close position error: {str(e)}"
            )
    
    def _modify_position(self, ticket: int, stop_loss: Optional[float] = None, 
                        take_profit: Optional[float] = None) -> TradeResult:
        """
        🔧 MISSING FROM MT5ConnectionManager - Modify position
        """
        try:
            # Get position info
            position = None
            positions = mt5.positions_get(ticket=ticket)
            if positions and len(positions) > 0:
                position = positions[0]
            else:
                return TradeResult(
                    success=False,
                    error_message=f"Position {ticket} not found"
                )
            
            # Prepare modification request
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": ticket,
                "sl": stop_loss if stop_loss else position.sl,
                "tp": take_profit if take_profit else position.tp,
            }
            
            # Send modification
            result = mt5.order_send(request)
            
            if result is None:
                return TradeResult(
                    success=False,
                    error_message="Modify order failed - no result"
                )
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return TradeResult(
                    success=False,
                    error_code=result.retcode,
                    error_message=f"Modify failed: {result.comment}"
                )
            
            return TradeResult(
                success=True,
                ticket=result.order,
                execution_time=datetime.now()
            )
            
        except Exception as e:
            return TradeResult(
                success=False,
                error_message=f"Modify position error: {str(e)}"
            )
    
    def _get_open_positions(self) -> List[Dict[str, Any]]:
        """
        🔧 MISSING FROM MT5ConnectionManager - Get open positions
        """
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []
            
            position_list = []
            for pos in positions:
                position_list.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'buy' if pos.type == mt5.ORDER_TYPE_BUY else 'sell',
                    'volume': pos.volume,
                    'open_price': pos.price_open,
                    'current_price': pos.price_current,
                    'stop_loss': pos.sl,
                    'take_profit': pos.tp,
                    'profit': pos.profit,
                    'swap': pos.swap,
                    'commission': pos.commission,
                    'comment': pos.comment,
                    'open_time': datetime.fromtimestamp(pos.time)
                })
            
            return position_list
            
        except Exception as e:
            self.logger.error(f"Error getting positions: {str(e)}")
            return []
    
    def emergency_stop_all(self) -> Dict[str, Any]:
        """
        🚨 EMERGENCY: Close all open positions immediately
        """
        try:
            self.logger.warning("🚨 EMERGENCY STOP: Closing all positions")
            
            positions = self._get_open_positions()
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
                result = self._close_position(position['ticket'])
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
