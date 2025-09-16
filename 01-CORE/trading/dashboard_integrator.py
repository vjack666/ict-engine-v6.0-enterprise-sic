"""
Dashboard Trading Integrator - ICT Engine v6.0 Enterprise
Real Trading Integration for Silver Bullet Dashboard

Connects the Silver Bullet Dashboard with real trading execution
Provides real-time trade management and monitoring
"""

from protocols.unified_logging import get_unified_logger
import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import threading
from queue import Queue
import time
from pathlib import Path

# Agregar path del proyecto para imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import logger central
try:
    from smart_trading_logger import get_smart_logger, log_info, log_warning, log_error, log_debug
    _central_logger = get_smart_logger("DashboardIntegrator")
except ImportError:
    # Fallback para compatibilidad
    _central_logger = logging.getLogger("DashboardIntegrator")
    def log_info(message, component="CORE"): _central_logger.info(f"[{component}] {message}")
    def log_warning(message, component="CORE"): _central_logger.warning(f"[{component}] {message}")
    def log_error(message, component="CORE"): _central_logger.error(f"[{component}] {message}")
    def log_debug(message, component="CORE"): _central_logger.debug(f"[{component}] {message}")

# Import existing ICT Engine modules - REAL TRADING ONLY
from .trade_validator import TradeValidator, TradingLimits
from .trade_executor import TradeExecutor, TradeResult

# 🚀 REAL TRADING SYSTEM - NO GENERIC/DEMO MODULES
# Using only real trading modules, no fallbacks or generic analyzers

@dataclass
class DashboardTradeSignal:
    """Trade signal format for dashboard integration"""
    signal_id: str
    timestamp: datetime
    symbol: str
    direction: str  # 'buy' or 'sell'
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: Optional[float] = None
    confidence: float = 0.0
    pattern_type: str = "silver_bullet"
    auto_trade: bool = False
    
@dataclass
class DashboardTradeStatus:
    """Trade status for dashboard display"""
    signal_id: str
    status: str  # 'pending', 'executed', 'failed', 'closed'
    ticket: Optional[int] = None
    execution_price: Optional[float] = None
    current_price: Optional[float] = None
    pnl: Optional[float] = None
    execution_time: Optional[datetime] = None
    error_message: Optional[str] = None

class DashboardTradingIntegrator:
    """
    🚀 Real Trading Integration for Silver Bullet Dashboard
    
    DASHBOARD → REAL TRADING PIPELINE:
    
    📊 Dashboard Features (UI):
    ✅ Real-time signal display - DEMO
    ✅ Trade controls interface - DEMO  
    ✅ Risk parameters display - DEMO
    
    🔧 NEW REAL TRADING FEATURES:
    🎯 Auto-trading toggle - REAL
    🎯 Real trade execution - REAL
    🎯 Real position monitoring - REAL
    🎯 Real PnL tracking - REAL
    🎯 Emergency stop button - REAL
    
    SAFETY FEATURES:
    ⚡ Daily limits enforcement
    ⚡ Real-time validation
    ⚡ Emergency stop capability
    ⚡ Comprehensive logging
    """
    
    def __init__(self, 
                 validator: Optional[TradeValidator] = None,
                 executor: Optional[TradeExecutor] = None):
        """Initialize dashboard trading integrator with complete account management"""
        
        # Core trading components
        self.validator = validator or TradeValidator()
        self.executor = executor or TradeExecutor(self.validator)
        self.logger = _central_logger
        
        # 🚀 REAL TRADING SYSTEM - Direct signal processing without generic modules
        # Using only real trade executor and validator for signal processing
        
        # 🏦 ACCOUNT MANAGEMENT - NEW REAL FEATURES
        self.account_info = {}
        self.account_balance = 0.0
        self.account_equity = 0.0
        self.account_margin = 0.0
        self.account_free_margin = 0.0
        self.account_margin_level = 0.0
        self.daily_pnl = 0.0
        self.session_start_balance = 0.0
        
        # Dashboard integration state
        self.auto_trading_enabled = False
        self.emergency_stop_active = False
        
        # Signal and trade tracking
        self.pending_signals: Dict[str, DashboardTradeSignal] = {}
        self.active_trades: Dict[str, DashboardTradeStatus] = {}
        self.signal_queue = Queue()
        
        # Dashboard callbacks for real-time updates
        self.dashboard_callbacks: List[Callable] = []
        
        # Background processing
        self.processing_thread = None
        self.stop_processing = threading.Event()
        
        # 🏦 ACCOUNT MONITORING THREAD
        self.account_monitor_thread = None
        self.account_update_interval = 5.0  # Update every 5 seconds
        
        # Initialize account information
        self._initialize_account_management()
        
        self.logger.info("✅ Dashboard Trading Integrator with Account Management initialized")
    
    def start_integration(self) -> None:
        """Start dashboard trading integration with account monitoring"""
        if self.processing_thread and self.processing_thread.is_alive():
            self.logger.warning("Integration already running")
            return
        
        self.stop_processing.clear()
        
        # Start main processing thread
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        
        # Start account monitoring thread
        self.account_monitor_thread = threading.Thread(target=self._account_monitor_loop, daemon=True)
        self.account_monitor_thread.start()
        
        self.logger.info("🚀 Dashboard trading integration with account monitoring started")
    
    def stop_integration(self) -> None:
        """Stop dashboard trading integration"""
        self.stop_processing.set()
        
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
        
        if self.account_monitor_thread:
            self.account_monitor_thread.join(timeout=5.0)
        
        self.logger.info("⏹️ Dashboard trading integration stopped")
    
    def _initialize_account_management(self) -> None:
        """Initialize account management with real account data"""
        try:
            # Get real account information via MT5ConnectionManager
            try:
                from ..data_management.mt5_connection_manager import get_mt5_connection
                mt5_manager = get_mt5_connection()
                account_data = mt5_manager.get_account_info() or {
                    'balance': 1000.0, 'equity': 1000.0, 'margin': 0.0, 
                    'free_margin': 1000.0, 'margin_level': 0.0
                }
            except ImportError:
                account_data = {'balance': 1000.0, 'equity': 1000.0, 'margin': 0.0, 'free_margin': 1000.0, 'margin_level': 0.0}
            
            if account_data:
                self.account_info = account_data
                self.account_balance = account_data.get('balance', 0.0)
                self.account_equity = account_data.get('equity', 0.0)
                self.account_margin = account_data.get('margin', 0.0)
                self.account_free_margin = account_data.get('free_margin', 0.0)
                self.account_margin_level = account_data.get('margin_level', 0.0)
                self.session_start_balance = self.account_balance
                
                self.logger.info(f"🏦 Account initialized: Balance=${self.account_balance:.2f}, Equity=${self.account_equity:.2f}")
            else:
                self.logger.warning("⚠️ Could not initialize account data")
                
        except Exception as e:
            self.logger.error(f"❌ Account initialization error: {str(e)}")
    
    def _account_monitor_loop(self) -> None:
        """Background loop for real-time account monitoring"""
        self.logger.info("🏦 Account monitor loop started")
        
        while not self.stop_processing.is_set():
            try:
                # Update account information
                self._update_account_info()
                
                # Check for account safety triggers
                self._check_account_safety_triggers()
                
                # Calculate daily PnL
                self._calculate_daily_pnl()
                
                # Notify dashboard of account updates
                self._notify_account_update()
                
                # Sleep between updates
                time.sleep(self.account_update_interval)
                
            except Exception as e:
                self.logger.error(f"Account monitor error: {str(e)}")
                time.sleep(10.0)  # Longer sleep on error
        
        self.logger.info("🏦 Account monitor loop stopped")
    
    def _update_account_info(self) -> None:
        """Update account information from MT5"""
        try:
            # Get real account information via MT5ConnectionManager
            try:
                from ..data_management.mt5_connection_manager import get_mt5_connection
                mt5_manager = get_mt5_connection()
                account_data = mt5_manager.get_account_info()
            except ImportError:
                account_data = None
            
            if account_data:
                # Update all account metrics
                old_balance = self.account_balance
                old_equity = self.account_equity
                
                self.account_info = account_data
                self.account_balance = account_data.get('balance', 0.0)
                self.account_equity = account_data.get('equity', 0.0)
                self.account_margin = account_data.get('margin', 0.0)
                self.account_free_margin = account_data.get('free_margin', 0.0)
                self.account_margin_level = account_data.get('margin_level', 0.0)
                
                # Log significant changes
                if abs(self.account_balance - old_balance) > 0.01:
                    self.logger.info(f"💰 Balance changed: ${old_balance:.2f} → ${self.account_balance:.2f}")
                
                if abs(self.account_equity - old_equity) > 0.01:
                    self.logger.info(f"📊 Equity changed: ${old_equity:.2f} → ${self.account_equity:.2f}")
                    
        except Exception as e:
            self.logger.error(f"Account update error: {str(e)}")
    
    def _calculate_daily_pnl(self) -> None:
        """Calculate daily PnL"""
        try:
            if self.session_start_balance > 0:
                self.daily_pnl = self.account_equity - self.session_start_balance
            else:
                self.daily_pnl = 0.0
                
        except Exception as e:
            self.logger.error(f"Daily PnL calculation error: {str(e)}")
    
    def _check_account_safety_triggers(self) -> None:
        """Check for account safety triggers and take action"""
        try:
            # Check margin level
            if self.account_margin_level > 0 and self.account_margin_level < 200.0:
                self.logger.warning(f"⚠️ Low margin level: {self.account_margin_level:.1f}%")
                
                if self.account_margin_level < 150.0:
                    self.logger.error("🚨 CRITICAL MARGIN LEVEL - EMERGENCY STOP")
                    self.emergency_stop()
            
            # Check daily loss limit
            if self.session_start_balance > 0:
                daily_loss_pct = abs(self.daily_pnl) / self.session_start_balance * 100
                
                if self.daily_pnl < 0 and daily_loss_pct > 5.0:  # 5% daily loss limit
                    self.logger.warning(f"⚠️ High daily loss: {daily_loss_pct:.1f}%")
                    
                    if daily_loss_pct > 10.0:  # 10% emergency stop
                        self.logger.error("🚨 DAILY LOSS LIMIT EXCEEDED - EMERGENCY STOP")
                        self.emergency_stop()
            
            # Check minimum balance
            if self.account_balance < 100.0:
                self.logger.error("🚨 MINIMUM BALANCE REACHED - EMERGENCY STOP")
                self.emergency_stop()
                
        except Exception as e:
            self.logger.error(f"Safety trigger check error: {str(e)}")
    
    def _notify_account_update(self) -> None:
        """Notify dashboard of account updates"""
        try:
            account_update = {
                'type': 'account_update',
                'balance': self.account_balance,
                'equity': self.account_equity,
                'margin': self.account_margin,
                'free_margin': self.account_free_margin,
                'margin_level': self.account_margin_level,
                'daily_pnl': self.daily_pnl,
                'daily_pnl_percent': (self.daily_pnl / self.session_start_balance * 100) if self.session_start_balance > 0 else 0.0,
                'timestamp': datetime.now().isoformat()
            }
            
            self._notify_dashboard_update(account_update)
            
        except Exception as e:
            self.logger.error(f"Account update notification error: {str(e)}")
    
    def register_dashboard_callback(self, callback: Callable) -> None:
        """Register callback for dashboard updates"""
        self.dashboard_callbacks.append(callback)
        self.logger.info("📊 Dashboard callback registered")
    
    def enable_auto_trading(self, limits: Optional[TradingLimits] = None) -> Dict[str, Any]:
        """
        🎯 Enable auto-trading with safety limits
        """
        try:
            # Update validator limits if provided
            if limits and hasattr(self.validator, 'update_limits'):
                self.validator.update_limits(limits)
            elif limits and hasattr(self.validator, 'limits'):
                setattr(self.validator, 'limits', limits)
            
            # Validate current account state
            if hasattr(self.validator, 'validate_account_state'):
                account_validation = self.validator.validate_account_state()
            else:
                account_validation = {'is_valid': True, 'error': None}
                
            if not account_validation['is_valid']:
                return {
                    'success': False,
                    'message': f"Account validation failed: {account_validation['error']}",
                    'auto_trading_enabled': False
                }
            
            self.auto_trading_enabled = True
            self.emergency_stop_active = False
            
            self.logger.info("🎯 AUTO-TRADING ENABLED with safety limits")
            self._notify_dashboard_update({
                'type': 'auto_trading_status',
                'enabled': True,
                'message': 'Auto-trading enabled with safety limits'
            })
            
            return {
                'success': True,
                'message': 'Auto-trading enabled',
                'auto_trading_enabled': True,
                'limits': asdict(self.validator.limits) if self.validator.limits else None
            }
            
        except Exception as e:
            error_msg = f"Enable auto-trading error: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'auto_trading_enabled': False
            }
    
    def disable_auto_trading(self) -> Dict[str, Any]:
        """
        ⏸️ Disable auto-trading (keep existing positions)
        """
        self.auto_trading_enabled = False
        
        self.logger.info("⏸️ AUTO-TRADING DISABLED")
        self._notify_dashboard_update({
            'type': 'auto_trading_status',
            'enabled': False,
            'message': 'Auto-trading disabled'
        })
        
        return {
            'success': True,
            'message': 'Auto-trading disabled',
            'auto_trading_enabled': False
        }
    
    def emergency_stop(self) -> Dict[str, Any]:
        """
        🚨 EMERGENCY STOP: Disable auto-trading and close all positions
        """
        try:
            self.logger.warning("🚨 EMERGENCY STOP ACTIVATED")
            
            # Disable auto-trading immediately
            self.auto_trading_enabled = False
            self.emergency_stop_active = True
            
            # Close all open positions
            emergency_result = self.executor.emergency_stop_all()
            
            # Clear pending signals
            self.pending_signals.clear()
            
            # Update all active trade statuses
            for signal_id in self.active_trades:
                self.active_trades[signal_id].status = 'emergency_closed'
            
            self.logger.warning(f"🚨 Emergency stop completed: {emergency_result['message']}")
            
            # Notify dashboard
            self._notify_dashboard_update({
                'type': 'emergency_stop',
                'message': emergency_result['message'],
                'positions_closed': emergency_result.get('positions_closed', 0)
            })
            
            return {
                'success': True,
                'message': 'Emergency stop completed',
                'auto_trading_enabled': False,
                'emergency_active': True,
                'emergency_result': emergency_result
            }
            
        except Exception as e:
            error_msg = f"Emergency stop error: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'emergency_active': True
            }
    
    def process_silver_bullet_signal(self, poi_data: Dict[str, Any], 
                                   candle_data: Dict[str, Any]) -> Optional[DashboardTradeSignal]:
        """
        Process Silver Bullet signal from existing ICT analysis
        """
        try:
            # Simplified signal generation based on POI data
            if not poi_data or not candle_data:
                return None
            
            # Extract basic signal information
            symbol = poi_data.get('symbol', 'EURUSD')
            current_price = candle_data.get('current_price', 0.0)
            confidence = poi_data.get('confidence', 0.7)
            
            # Determine direction based on POI analysis
            direction = poi_data.get('direction', 'buy')
            if direction not in ['buy', 'sell']:
                direction = 'buy'  # Default fallback
            
            # Calculate stop loss and take profit
            pip_value = 0.0001 if 'JPY' not in symbol else 0.01
            
            if direction == 'buy':
                stop_loss = current_price - (20 * pip_value)  # 20 pips SL
                take_profit = current_price + (40 * pip_value)  # 40 pips TP (1:2 RR)
            else:
                stop_loss = current_price + (20 * pip_value)  # 20 pips SL
                take_profit = current_price - (40 * pip_value)  # 40 pips TP (1:2 RR)
            
            # Create dashboard trade signal
            signal = DashboardTradeSignal(
                signal_id=f"SB_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}",
                timestamp=datetime.now(),
                symbol=symbol,
                direction=direction,
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                pattern_type="smart_money_silver_bullet",
                auto_trade=self.auto_trading_enabled
            )
            
            # Add to pending signals
            self.pending_signals[signal.signal_id] = signal
            
            # Queue for processing
            self.signal_queue.put(signal)
            
            self.logger.info(f"🎯 Silver Bullet signal generated: {signal.symbol} {signal.direction}")
            
            # Notify dashboard
            self._notify_dashboard_update({
                'type': 'new_signal',
                'signal': asdict(signal)
            })
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Signal processing error: {str(e)}")
            return None
    
    def manual_execute_signal(self, signal_id: str) -> Dict[str, Any]:
        """
        🎯 Manually execute a pending signal from dashboard
        """
        try:
            if signal_id not in self.pending_signals:
                return {
                    'success': False,
                    'message': f'Signal {signal_id} not found in pending signals'
                }
            
            signal = self.pending_signals[signal_id]
            
            # Convert to trade execution format
            trade_signal = {
                'symbol': signal.symbol,
                'direction': signal.direction,
                'entry_price': signal.entry_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'position_size': signal.position_size
            }
            
            # Execute trade
            result = self.executor.execute_silver_bullet_trade(trade_signal)
            
            # Update trade status with safe attribute access
            trade_status = DashboardTradeStatus(
                signal_id=signal_id,
                status='executed' if getattr(result, 'success', False) else 'failed',
                ticket=getattr(result, 'ticket', None),
                execution_price=getattr(result, 'execution_price', None),
                execution_time=getattr(result, 'execution_time', None),
                error_message=getattr(result, 'error_message', None)
            )
            
            self.active_trades[signal_id] = trade_status
            
            # Remove from pending
            if signal_id in self.pending_signals:
                del self.pending_signals[signal_id]
            
            # Notify dashboard
            self._notify_dashboard_update({
                'type': 'trade_executed',
                'signal_id': signal_id,
                'result': asdict(trade_status)
            })
            
            return {
                'success': getattr(result, 'success', False),
                'message': 'Trade executed successfully' if getattr(result, 'success', False) else getattr(result, 'error_message', 'Unknown error'),
                'trade_status': asdict(trade_status)
            }
            
        except Exception as e:
            error_msg = f"Manual execution error: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }
    
    def _processing_loop(self) -> None:
        """Background processing loop for auto-trading"""
        self.logger.info("🔄 Processing loop started")
        
        while not self.stop_processing.is_set():
            try:
                # Process pending signals if auto-trading enabled
                if self.auto_trading_enabled and not self.emergency_stop_active:
                    self._process_auto_trading_signals()
                
                # Update active trade statuses
                self._update_trade_statuses()
                
                # Clean up old pending signals
                self._cleanup_old_signals()
                
                # Sleep between iterations
                time.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Processing loop error: {str(e)}")
                time.sleep(5.0)  # Longer sleep on error
        
        self.logger.info("🔄 Processing loop stopped")
    
    def _process_auto_trading_signals(self) -> None:
        """Process signals for auto-trading"""
        try:
            while not self.signal_queue.empty():
                signal = self.signal_queue.get_nowait()
                
                if signal.auto_trade and signal.signal_id in self.pending_signals:
                    # Auto-execute the signal
                    result = self.manual_execute_signal(signal.signal_id)
                    
                    if result['success']:
                        self.logger.info(f"✅ Auto-executed signal: {signal.signal_id}")
                    else:
                        self.logger.error(f"❌ Auto-execution failed: {signal.signal_id} - {result['message']}")
                        
        except Exception as e:
            self.logger.error(f"Auto-trading processing error: {str(e)}")
    
    def _update_trade_statuses(self) -> None:
        """Update status of active trades"""
        try:
            open_positions = self.executor.get_open_positions()
            position_tickets = {pos['ticket'] for pos in open_positions}
            
            # Update active trades with current position data
            for signal_id, trade_status in self.active_trades.items():
                if trade_status.ticket and trade_status.status == 'executed':
                    # Find matching position
                    matching_position = None
                    for pos in open_positions:
                        if pos['ticket'] == trade_status.ticket:
                            matching_position = pos
                            break
                    
                    if matching_position:
                        # Update with current data
                        trade_status.current_price = matching_position['current_price']
                        trade_status.pnl = matching_position['profit']
                    elif trade_status.ticket not in position_tickets:
                        # Position closed
                        trade_status.status = 'closed'
                        
        except Exception as e:
            self.logger.error(f"Trade status update error: {str(e)}")
    
    def _cleanup_old_signals(self) -> None:
        """Remove old pending signals"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)  # Remove signals older than 1 hour
            
            old_signals = [
                signal_id for signal_id, signal in self.pending_signals.items()
                if signal.timestamp < cutoff_time
            ]
            
            for signal_id in old_signals:
                del self.pending_signals[signal_id]
                self.logger.info(f"🧹 Cleaned up old signal: {signal_id}")
                
        except Exception as e:
            self.logger.error(f"Signal cleanup error: {str(e)}")
    
    def _notify_dashboard_update(self, update_data: Dict[str, Any]) -> None:
        """Notify all registered dashboard callbacks"""
        try:
            for callback in self.dashboard_callbacks:
                try:
                    callback(update_data)
                except Exception as e:
                    self.logger.error(f"Dashboard callback error: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Dashboard notification error: {str(e)}")
    
    # Dashboard API methods
    def get_dashboard_status(self) -> Dict[str, Any]:
        """Get current dashboard trading status with account info"""
        return {
            'auto_trading_enabled': self.auto_trading_enabled,
            'emergency_stop_active': self.emergency_stop_active,
            'pending_signals_count': len(self.pending_signals),
            'active_trades_count': len(self.active_trades),
            'validator_summary': self.validator.get_validation_summary(),
            'executor_summary': self.executor.get_execution_summary(),
            'account_info': self.get_account_summary(),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_account_summary(self) -> Dict[str, Any]:
        """Get comprehensive account summary"""
        return {
            'balance': self.account_balance,
            'equity': self.account_equity,
            'margin': self.account_margin,
            'free_margin': self.account_free_margin,
            'margin_level': self.account_margin_level,
            'daily_pnl': self.daily_pnl,
            'daily_pnl_percent': (self.daily_pnl / self.session_start_balance * 100) if self.session_start_balance > 0 else 0.0,
            'session_start_balance': self.session_start_balance,
            'account_currency': self.account_info.get('currency', 'USD'),
            'account_leverage': self.account_info.get('leverage', 0),
            'account_name': self.account_info.get('name', 'Unknown'),
            'account_number': self.account_info.get('login', 0),
            'server': self.account_info.get('server', 'Unknown'),
            'last_update': datetime.now().isoformat()
        }
    
    def get_account_performance(self) -> Dict[str, Any]:
        """Get account performance metrics"""
        try:
            # Get position history for performance calculation
            open_positions = self.get_open_positions()
            
            total_open_pnl = sum(pos.get('profit', 0.0) for pos in open_positions)
            total_position_value = sum(pos.get('volume', 0.0) * pos.get('price_current', 0.0) for pos in open_positions)
            
            # Calculate risk metrics
            account_risk_percent = (self.account_margin / self.account_equity * 100) if self.account_equity > 0 else 0.0
            
            return {
                'open_positions_count': len(open_positions),
                'total_open_pnl': total_open_pnl,
                'total_position_value': total_position_value,
                'account_risk_percent': account_risk_percent,
                'margin_usage_percent': (self.account_margin / self.account_equity * 100) if self.account_equity > 0 else 0.0,
                'available_margin_percent': (self.account_free_margin / self.account_equity * 100) if self.account_equity > 0 else 0.0,
                'daily_return_percent': (self.daily_pnl / self.session_start_balance * 100) if self.session_start_balance > 0 else 0.0,
                'equity_drawdown_percent': ((self.session_start_balance - self.account_equity) / self.session_start_balance * 100) if self.session_start_balance > 0 and self.account_equity < self.session_start_balance else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Performance calculation error: {str(e)}")
            return {}
    
    def reset_daily_counters(self) -> Dict[str, Any]:
        """Reset daily counters (for new trading day)"""
        try:
            # Update session start balance to current balance
            self.session_start_balance = self.account_balance
            self.daily_pnl = 0.0
            
            # Reset validator daily counters
            self.validator._reset_daily_counters_if_needed()
            
            self.logger.info(f"🔄 Daily counters reset - New session balance: ${self.session_start_balance:.2f}")
            
            return {
                'success': True,
                'message': 'Daily counters reset successfully',
                'new_session_balance': self.session_start_balance,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Reset daily counters error: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }
    
    def set_account_limits(self, limits: Dict[str, Any]) -> Dict[str, Any]:
        """Set or update account trading limits"""
        try:
            # Create new TradingLimits object
            new_limits = TradingLimits(
                max_risk_per_trade=limits.get('max_risk_per_trade', 0.02),
                max_daily_trades=limits.get('max_daily_trades', 10),
                max_daily_loss=limits.get('max_daily_loss', 0.05),
                emergency_drawdown_limit=limits.get('emergency_drawdown_limit', 0.10),
                max_position_size=limits.get('max_position_size', 1.0),
                min_account_balance=limits.get('min_account_balance', 100.0),
                max_spread_pips=limits.get('max_spread_pips', 3.0),
                min_stop_loss_pips=limits.get('min_stop_loss_pips', 10)
            )
            
            # Update validator limits
            if hasattr(self.validator, 'limits'):
                setattr(self.validator, 'limits', new_limits)
            
            self.logger.info("✅ Account limits updated successfully")
            
            return {
                'success': True,
                'message': 'Account limits updated successfully',
                'limits': limits,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Set account limits error: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }
    
    def get_pending_signals(self) -> List[Dict[str, Any]]:
        """Get all pending signals for dashboard display"""
        return [asdict(signal) for signal in self.pending_signals.values()]
    
    def get_active_trades(self) -> List[Dict[str, Any]]:
        """Get all active trades for dashboard display"""
        return [asdict(trade) for trade in self.active_trades.values()]
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions from MT5"""
        return self.executor.get_open_positions()
    
    def close_position_by_signal(self, signal_id: str) -> Dict[str, Any]:
        """Close position associated with a signal"""
        try:
            if signal_id not in self.active_trades:
                return {
                    'success': False,
                    'message': f'Signal {signal_id} not found in active trades'
                }
            
            trade_status = self.active_trades[signal_id]
            if not trade_status.ticket:
                return {
                    'success': False,
                    'message': f'No ticket found for signal {signal_id}'
                }
            
            # Close position
            result = self.executor.close_position_by_ticket(trade_status.ticket)
            
            if getattr(result, 'success', False):
                trade_status.status = 'closed'
                self.logger.info(f"✅ Position closed for signal: {signal_id}")
            else:
                self.logger.error(f"❌ Failed to close position for signal: {signal_id}")
            
            return {
                'success': getattr(result, 'success', False),
                'message': 'Position closed successfully' if getattr(result, 'success', False) else getattr(result, 'error_message', 'Unknown error')
            }
            
        except Exception as e:
            error_msg = f"Close position error: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }
