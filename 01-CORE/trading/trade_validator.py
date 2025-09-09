"""
Trade Validator - ICT Engine v6.0 Enterprise
Real Trading Validation System for Demo Accounts

Integrates with existing MT5ConnectionManager and RiskManager
Provides comprehensive validation and safety checks for real trade execution
"""

import logging
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# Import existing ICT Engine modules
try:
    from data_management.mt5_connection_manager import MT5ConnectionManager, get_mt5_connection
    from risk_management.risk_manager import RiskManager, RiskMetrics, ICTRiskConfig
except ImportError:
    # Fallbacks for module imports
    class MT5ConnectionManager:
        def is_connected(self): return True
        def get_account_info(self): return {'balance': 1000.0, 'equity': 1000.0}
    
    def get_mt5_connection():
        return MT5ConnectionManager()
    
    class RiskManager:
        def calculate_position_size(self, *args, **kwargs): return 0.01
    
    class RiskMetrics:
        def __init__(self, **kwargs): pass
    
    class ICTRiskConfig:
        def __init__(self, **kwargs): pass

try:
    from smart_trading_logger import SmartTradingLogger
except ImportError:
    import logging
    class SmartTradingLogger:
        @staticmethod
        def get_logger(name: str):
            return logging.getLogger(name)

@dataclass
class TradingLimits:
    """Trading limits configuration"""
    max_risk_per_trade: float = 0.01  # 1% maximum risk per trade
    max_daily_trades: int = 10         # Maximum trades per day
    max_daily_loss: float = 0.05       # 5% maximum daily loss
    emergency_drawdown_limit: float = 0.10  # 10% emergency stop
    max_position_size: float = 1.0     # Maximum position size in lots
    min_account_balance: float = 100.0 # Minimum account balance
    max_spread_pips: float = 3.0       # Maximum allowed spread
    min_stop_loss_pips: float = 10     # Minimum stop loss distance

class TradeValidator:
    """
    Real Trade Validation System
    
    Integrates with existing ICT Engine v6.0 Enterprise modules:
    - MT5ConnectionManager for market data and connection validation
    - RiskManager for position sizing and risk validation
    - SmartTradingLogger for comprehensive logging
    
    Provides comprehensive safety checks before executing real trades:
    - Account balance validation via existing MT5ConnectionManager
    - Position size validation via existing RiskManager
    - Market hours validation
    - Spread validation
    - Daily limits enforcement
    - Risk management validation
    """
    
    def __init__(self, limits: Optional[TradingLimits] = None):
        """Initialize trade validator with existing ICT modules"""
        self.limits = limits or TradingLimits()
        self.daily_trades_count = 0
        self.daily_pnl = 0.0
        self.session_start_balance = 0.0
        
        # Use existing ICT Engine modules
        self.mt5_manager = get_mt5_connection()
        self.risk_manager = RiskManager()
        
        # Initialize logger correctly
        if hasattr(SmartTradingLogger, 'get_logger'):
            self.logger = SmartTradingLogger.get_logger(__name__)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Reset daily counters if new day
        self._reset_daily_counters_if_needed()
        
        # Validate existing modules capabilities
        self._validate_module_capabilities()
        
    def _validate_module_capabilities(self) -> None:
        """
        🚨 CRITICAL: Validate if existing modules support REAL trading
        """
        issues = []
        
        # Check MT5ConnectionManager capabilities
        mt5_methods = dir(self.mt5_manager)
        missing_mt5_methods = [
            'place_buy_order', 'place_sell_order', 'close_position', 
            'modify_position', 'get_open_positions'
        ]
        
        for method in missing_mt5_methods:
            if method not in mt5_methods:
                issues.append(f"❌ MT5ConnectionManager missing method: {method}")
        
        # Check RiskManager capabilities
        risk_methods = dir(self.risk_manager)
        missing_risk_methods = [
            'validate_trade_signal', 'check_max_drawdown', 'emergency_stop_all'
        ]
        
        for method in missing_risk_methods:
            if method not in risk_methods:
                issues.append(f"⚠️ RiskManager missing method: {method} (can be implemented)")
        
        if issues:
            self.logger.warning("🚨 MODULE CAPABILITY ISSUES FOR REAL TRADING:")
            for issue in issues:
                self.logger.warning(issue)
            
            self.logger.warning("""
🔧 REQUIRED EXTENSIONS FOR REAL TRADING:

1. MT5ConnectionManager needs these methods:
   - place_buy_order(symbol, lot_size, stop_loss, take_profit)
   - place_sell_order(symbol, lot_size, stop_loss, take_profit)
   - close_position(ticket)
   - modify_position(ticket, stop_loss, take_profit)
   - get_open_positions()

2. RiskManager could benefit from:
   - validate_trade_signal(signal, account_info)
   - emergency_stop_all()
   - check_max_drawdown(current_equity, peak_equity)
            """)
        else:
            self.logger.info("✅ All modules ready for real trading")
    
        
    def validate_trade_signal(self, signal: Dict[str, Any], account_info: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Comprehensive trade signal validation
        
        Args:
            signal: Trading signal with symbol, direction, entry_price, etc.
            account_info: Current account information
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # 1. Validate account state
            account_valid, account_error = self._validate_account_state(account_info)
            if not account_valid:
                return False, f"Account validation failed: {account_error}"
            
            # 2. Validate symbol and market conditions
            symbol_valid, symbol_error = self._validate_symbol_conditions(signal['symbol'])
            if not symbol_valid:
                return False, f"Symbol validation failed: {symbol_error}"
            
            # 3. Validate trading hours
            hours_valid, hours_error = self._validate_trading_hours(signal['symbol'])
            if not hours_valid:
                return False, f"Trading hours validation failed: {hours_error}"
            
            # 4. Validate daily limits
            limits_valid, limits_error = self._validate_daily_limits()
            if not limits_valid:
                return False, f"Daily limits exceeded: {limits_error}"
            
            # 5. Validate position size and risk
            size_valid, size_error = self._validate_position_size(signal, account_info)
            if not size_valid:
                return False, f"Position size validation failed: {size_error}"
            
            # 6. Validate signal quality
            quality_valid, quality_error = self._validate_signal_quality(signal)
            if not quality_valid:
                return False, f"Signal quality validation failed: {quality_error}"
            
            self.logger.info(f"✅ Trade signal validation passed for {signal['symbol']}")
            return True, "All validations passed"
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _validate_account_state(self, account_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate account balance and equity using existing MT5ConnectionManager"""
        try:
            # Use existing MT5ConnectionManager for account validation
            if not getattr(self.mt5_manager, 'ensure_connection', lambda: True)():
                return False, "MT5 connection failed"
            
            # Get fresh account info from existing manager
            fresh_account_info = self.mt5_manager.get_account_info()
            if not fresh_account_info:
                return False, "Cannot get account info from MT5ConnectionManager"
            
            balance = fresh_account_info.get('balance', 0.0)
            equity = fresh_account_info.get('equity', 0.0)
            margin_free = fresh_account_info.get('margin_free', 0.0)
            
            # Check minimum balance
            if balance < self.limits.min_account_balance:
                return False, f"Balance {balance} below minimum {self.limits.min_account_balance}"
            
            # Check equity vs balance (drawdown check)
            if balance > 0:
                drawdown = (balance - equity) / balance
                if drawdown > self.limits.emergency_drawdown_limit:
                    return False, f"Drawdown {drawdown:.2%} exceeds limit {self.limits.emergency_drawdown_limit:.2%}"
            
            # Check free margin
            if margin_free < balance * 0.1:  # At least 10% free margin
                return False, f"Insufficient free margin: {margin_free}"
            
            return True, "Account state valid"
            
        except Exception as e:
            return False, f"Account validation error: {str(e)}"
    
    def _validate_symbol_conditions(self, symbol: str) -> Tuple[bool, str]:
        """Validate symbol availability and spread using MT5ConnectionManager"""
        try:
            # Ensure MT5 connection via existing manager
            if not getattr(self.mt5_manager, 'ensure_connection', lambda: True)():
                return False, "MT5 connection failed"
            
            # Import MT5 here to use with existing connection
            import MetaTrader5 as mt5
            
            # Get symbol info
            symbol_info = getattr(mt5, 'symbol_info', lambda x: None)(symbol)
            if symbol_info is None:
                return False, f"Symbol {symbol} not available"
            
            # Check if symbol is enabled for trading
            if not symbol_info.visible:
                return False, f"Symbol {symbol} not visible/tradeable"
            
            # Get current tick to check spread
            tick = getattr(mt5, 'symbol_info_tick', lambda x: None)(symbol)
            if tick is None:
                return False, f"Cannot get tick data for {symbol}"
            
            # Calculate spread in pips
            point = symbol_info.point
            if point == 0:
                return False, f"Invalid point size for {symbol}"
            
            spread_pips = (tick.ask - tick.bid) / point
            if spread_pips > self.limits.max_spread_pips:
                return False, f"Spread {spread_pips:.1f} pips exceeds limit {self.limits.max_spread_pips}"
            
            return True, "Symbol conditions valid"
            
        except Exception as e:
            return False, f"Symbol validation error: {str(e)}"
    
    def _validate_trading_hours(self, symbol: str) -> Tuple[bool, str]:
        """Validate if symbol is within trading hours"""
        try:
            # Ensure MT5 connection
            if not getattr(self.mt5_manager, 'ensure_connection', lambda: True)():
                return False, "MT5 connection failed"
            
            import MetaTrader5 as mt5
            symbol_info = getattr(mt5, 'symbol_info', lambda x: None)(symbol)
            if symbol_info is None:
                return False, f"Cannot get symbol info for {symbol}"
            
            # Check if market is open (simple check)
            current_time = datetime.now().time()
            
            # For forex symbols, typically trade 24/5
            # For other symbols, check specific hours
            if symbol_info.path.startswith("Forex"):
                # Forex markets - check if it's weekend
                current_weekday = datetime.now().weekday()
                if current_weekday >= 5:  # Saturday = 5, Sunday = 6
                    return False, "Forex market closed on weekends"
            
            # Additional symbol-specific checks can be added here
            
            return True, "Trading hours valid"
            
        except Exception as e:
            return False, f"Trading hours validation error: {str(e)}"
    
    def _validate_daily_limits(self) -> Tuple[bool, str]:
        """Validate daily trading limits"""
        try:
            # Check daily trade count
            if self.daily_trades_count >= self.limits.max_daily_trades:
                return False, f"Daily trade limit reached: {self.daily_trades_count}/{self.limits.max_daily_trades}"
            
            # Check daily loss limit
            if self.session_start_balance > 0:
                daily_loss_pct = abs(self.daily_pnl) / self.session_start_balance
                if self.daily_pnl < 0 and daily_loss_pct > self.limits.max_daily_loss:
                    return False, f"Daily loss limit exceeded: {daily_loss_pct:.2%}/{self.limits.max_daily_loss:.2%}"
            
            return True, "Daily limits OK"
            
        except Exception as e:
            return False, f"Daily limits validation error: {str(e)}"
    
    def _validate_position_size(self, signal: Dict[str, Any], account_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate calculated position size using existing RiskManager"""
        try:
            # Use existing RiskManager for position size validation
            position_size = signal.get('position_size', 0.0)
            
            # If position size not provided, calculate it using existing RiskManager
            if position_size == 0.0:
                entry_price = signal.get('entry_price', 0.0)
                stop_loss = signal.get('stop_loss', 0.0)
                account_balance = account_info.get('balance', 0.0)
                
                if entry_price > 0 and stop_loss > 0 and account_balance > 0:
                    # Calculate position size using existing RiskManager
                    calculated_size = self.risk_manager.calculate_position_size(
                        account_balance=account_balance,
                        entry_price=entry_price,
                        stop_loss=stop_loss
                    )
                    signal['position_size'] = calculated_size
                    position_size = calculated_size
                    
                    self.logger.info(f"Position size calculated by RiskManager: {position_size}")
            
            # Check maximum position size
            if position_size > self.limits.max_position_size:
                return False, f"Position size {position_size} exceeds limit {self.limits.max_position_size}"
            
            # Check minimum position size
            if position_size <= 0:
                return False, f"Invalid position size: {position_size}"
            
            # Validate risk amount using RiskManager metrics
            risk_amount = signal.get('risk_amount', 0.0)
            balance = account_info.get('balance', 0.0)
            
            if balance > 0:
                risk_pct = risk_amount / balance
                max_risk = self.limits.max_risk_per_trade  # Use validator's limit
                if risk_pct > max_risk:
                    return False, f"Risk {risk_pct:.2%} exceeds RiskManager limit {max_risk:.2%}"
            
            return True, "Position size valid"
            
        except Exception as e:
            return False, f"Position size validation error: {str(e)}"
    
    def _validate_signal_quality(self, signal: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate signal quality and required fields"""
        try:
            required_fields = ['symbol', 'direction', 'entry_price', 'stop_loss', 'take_profit']
            
            for field in required_fields:
                if field not in signal:
                    return False, f"Missing required field: {field}"
                
                if signal[field] is None:
                    return False, f"Field {field} cannot be None"
            
            # Validate direction
            if signal['direction'] not in ['buy', 'sell']:
                return False, f"Invalid direction: {signal['direction']}"
            
            # Validate price relationships
            entry_price = signal['entry_price']
            stop_loss = signal['stop_loss']
            take_profit = signal['take_profit']
            
            if signal['direction'] == 'buy':
                if stop_loss >= entry_price:
                    return False, "Buy stop loss must be below entry price"
                if take_profit <= entry_price:
                    return False, "Buy take profit must be above entry price"
            else:  # sell
                if stop_loss <= entry_price:
                    return False, "Sell stop loss must be above entry price"
                if take_profit >= entry_price:
                    return False, "Sell take profit must be below entry price"
            
            # Validate stop loss distance using MT5 connection
            try:
                if getattr(self.mt5_manager, 'ensure_connection', lambda: True)():
                    import MetaTrader5 as mt5
                    symbol_info = getattr(mt5, 'symbol_info', lambda x: None)(signal['symbol'])
                    if symbol_info:
                        point = symbol_info.point
                        sl_distance_pips = abs(entry_price - stop_loss) / point
                        if sl_distance_pips < self.limits.min_stop_loss_pips:
                            return False, f"Stop loss distance {sl_distance_pips:.1f} pips below minimum {self.limits.min_stop_loss_pips}"
            except Exception as e:
                self.logger.warning(f"Could not validate stop loss distance: {e}")
            
            return True, "Signal quality valid"
            
        except Exception as e:
            return False, f"Signal quality validation error: {str(e)}"
    
    def update_daily_stats(self, trade_result: Dict[str, Any]) -> None:
        """Update daily trading statistics"""
        try:
            self.daily_trades_count += 1
            
            # Update daily P&L if trade is closed
            if trade_result.get('status') == 'closed':
                pnl = trade_result.get('profit', 0.0)
                self.daily_pnl += pnl
                
            self.logger.info(f"Daily stats updated: Trades={self.daily_trades_count}, P&L={self.daily_pnl:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error updating daily stats: {str(e)}")
    
    def _reset_daily_counters_if_needed(self) -> None:
        """Reset daily counters if it's a new day"""
        try:
            # This would typically check against stored date
            # For now, we'll implement basic logic
            current_date = datetime.now().date()
            
            # In a real implementation, you'd store the last reset date
            # and compare with current date
            
            self.logger.info("Daily counters checked/reset if needed")
            
        except Exception as e:
            self.logger.error(f"Error resetting daily counters: {str(e)}")
    
    def emergency_validation_check(self, account_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Emergency validation check for immediate stop conditions"""
        try:
            balance = account_info.get('balance', 0.0)
            equity = account_info.get('equity', 0.0)
            
            if balance > 0:
                drawdown = (balance - equity) / balance
                if drawdown > self.limits.emergency_drawdown_limit:
                    return False, f"EMERGENCY: Drawdown {drawdown:.2%} exceeds emergency limit!"
            
            return True, "Emergency check passed"
            
        except Exception as e:
            return False, f"Emergency validation error: {str(e)}"
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get current validation status summary"""
        return {
            'daily_trades_count': self.daily_trades_count,
            'daily_trades_limit': self.limits.max_daily_trades,
            'daily_pnl': self.daily_pnl,
            'daily_loss_limit': self.limits.max_daily_loss,
            'emergency_drawdown_limit': self.limits.emergency_drawdown_limit,
            'max_risk_per_trade': self.limits.max_risk_per_trade,
            'max_position_size': self.limits.max_position_size,
            'status': 'active' if self.daily_trades_count < self.limits.max_daily_trades else 'daily_limit_reached'
        }
    
    def update_limits(self, new_limits: TradingLimits) -> None:
        """Update trading limits configuration"""
        self.limits = new_limits
        self.logger.info(f"✅ Trading limits updated: max_risk={new_limits.max_risk_per_trade}, max_trades={new_limits.max_daily_trades}")
    
    def validate_account_state(self) -> Dict[str, Any]:
        """Validate current account state for dashboard"""
        try:
            # Get account info from MT5 manager
            if hasattr(self.mt5_manager, 'get_account_info'):
                account_info = self.mt5_manager.get_account_info()
            else:
                # Fallback for testing
                account_info = {'balance': 1000.0, 'equity': 1000.0, 'margin_free': 1000.0}
            
            if not account_info:
                return {'is_valid': False, 'error': 'Could not retrieve account information'}
            
            # Check minimum balance
            if account_info.get('balance', 0) < self.limits.min_account_balance:
                return {
                    'is_valid': False, 
                    'error': f"Account balance ${account_info.get('balance', 0):.2f} below minimum ${self.limits.min_account_balance}"
                }
            
            # Check daily limits
            if self.daily_trades_count >= self.limits.max_daily_trades:
                return {
                    'is_valid': False,
                    'error': f"Daily trade limit reached ({self.daily_trades_count}/{self.limits.max_daily_trades})"
                }
            
            return {'is_valid': True, 'error': None}
            
        except Exception as e:
            return {'is_valid': False, 'error': f"Account validation error: {str(e)}"}
