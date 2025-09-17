"""
Emergency Stop System - ICT Engine v6.0 Enterprise  
===============================================

Sistema parada automática para protección cuenta real.
Monitoreo continuo condiciones críticas.

Características:
- Drawdown máximo protection
- Pérdidas consecutivas monitoring  
- Market conditions extremas detection
- Technical issues automatic handling
- Emergency procedures automation
"""

from protocols.unified_logging import get_unified_logger
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from threading import Thread, Event
import json

# Imports del sistema ICT existente
try:
    from ..data_management.mt5_data_manager import MT5DataManager
    from ..smart_trading_logger import SmartTradingLogger
    from ..enums import SystemStateV6
except ImportError:
    # Fallback para testing
    MT5DataManager = None
    SmartTradingLogger = None
    SystemStateV6 = None

class EmergencyLevel(Enum):
    """Niveles de emergencia del sistema"""
    GREEN = "normal"           # Operación normal
    YELLOW = "warning"         # Advertencia, monitoreo aumentado  
    ORANGE = "critical"        # Crítico, reducir operaciones
    RED = "emergency"          # Emergencia, detener todo trading

class StopReason(Enum):
    """Razones parada automática"""
    MAX_DRAWDOWN = "max_drawdown_reached"
    CONSECUTIVE_LOSSES = "max_consecutive_losses"
    TECHNICAL_FAILURE = "technical_failure"
    MARKET_CONDITIONS = "extreme_market_conditions"
    MANUAL_STOP = "manual_emergency_stop"
    CONNECTION_LOST = "mt5_connection_lost"
    ACCOUNT_ISSUE = "account_issue"

@dataclass
class EmergencyConfig:
    """Configuración sistema emergency stop"""
    max_drawdown_percent: float = 5.0          # 5% drawdown máximo
    max_consecutive_losses: int = 5            # 5 pérdidas consecutivas
    daily_loss_limit: float = 500.0           # $500 pérdida diaria máxima
    monitoring_interval: int = 30              # Segundos entre checks
    recovery_cooldown: int = 3600              # 1 hora cooldown después stop
    enable_weekend_stop: bool = True           # Parar durante fines semana
    enable_news_stop: bool = True              # Parar durante high impact news
    
    # Technical monitoring thresholds
    max_terminal_response_ms: float = 5000.0   # 5s max response time
    max_data_age_seconds: float = 60.0         # 1 min max data age
    max_failed_orders: int = 3                 # Max failed orders before alert
    
    # Market condition thresholds  
    max_volatility_threshold: float = 3.0      # Max volatility index
    max_price_gap_pips: float = 50.0          # Max price gap in pips
    avoid_weekend_trading: bool = True         # Avoid weekend trading

@dataclass 
class AccountHealth:
    """Estado salud cuenta trading"""
    current_balance: float = 0.0
    starting_balance: float = 0.0
    current_drawdown: float = 0.0
    peak_balance: float = 0.0
    daily_pnl: float = 0.0
    consecutive_losses: int = 0
    consecutive_wins: int = 0
    open_positions: int = 0
    last_trade_result: Optional[str] = None
    last_update: datetime = field(default_factory=datetime.now)
    
    # Technical health indicators
    failed_orders_count: int = 0
    volatility_index: float = 0.0
    max_price_gap: float = 0.0

@dataclass
class EmergencyAlert:
    """Alert emergencia del sistema"""
    level: EmergencyLevel
    reason: StopReason
    message: str
    timestamp: datetime
    account_health: AccountHealth
    actions_taken: List[str] = field(default_factory=list)

class EmergencyStopSystem:
    """
    Sistema parada automática para protección cuenta real
    
    Monitoreo continuo de:
    - Drawdown cuenta vs límites configurados
    - Secuencias pérdidas consecutivas
    - Condiciones técnicas MT5
    - Condiciones mercado extremas
    - Status conexión y integridad datos
    """
    
    def __init__(self, config: Optional[EmergencyConfig] = None):
        """
        Inicializa Emergency Stop System
        
        Args:
            config: Configuración sistema (None = default config)
        """
        self.config = config or EmergencyConfig()
        self.is_trading_enabled = True
        self.emergency_level = EmergencyLevel.GREEN
        self.stop_reason = None
        self.last_stop_time = None
        
        # Health tracking
        self.account_health = AccountHealth()
        self.alerts_history: List[EmergencyAlert] = []
        
        # Monitoring thread
        self._monitoring_active = False
        self._monitoring_thread = None
        self._stop_event = Event()
        
        # Integración sistema existente
        try:
            if MT5DataManager is not None:
                self.mt5_manager = MT5DataManager()
            else:
                self.mt5_manager = None
                
            if SmartTradingLogger is not None:
                self.logger = SmartTradingLogger("EmergencyStop")
            else:
                self.logger = logging.getLogger("EmergencyStop")
        except Exception as e:
            self.mt5_manager = None
            self.logger = logging.getLogger("EmergencyStop")
            print(f"Warning: Could not initialize MT5 components: {e}")
            
        # Estado inicial
        self._initialize_account_health()
        
        self.logger.info("EmergencyStopSystem initialized")
        self.logger.info(f"Max Drawdown: {self.config.max_drawdown_percent}%")
        self.logger.info(f"Max Consecutive Losses: {self.config.max_consecutive_losses}")
    
    def start_monitoring(self):
        """Inicia monitoreo automático"""
        if self._monitoring_active:
            self.logger.warning("Monitoring already active")
            return
            
        self._monitoring_active = True
        self._stop_event.clear()
        self._monitoring_thread = Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        
        self.logger.info("Emergency monitoring started")
    
    def stop_monitoring(self):
        """Detiene monitoreo automático"""
        self._monitoring_active = False
        self._stop_event.set()
        
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5.0)
            
        self.logger.info("Emergency monitoring stopped")
    
    def _monitoring_loop(self):
        """Loop principal monitoreo"""
        while self._monitoring_active and not self._stop_event.is_set():
            try:
                # Update account health
                self._update_account_health()
                
                # Check all emergency conditions
                self._check_emergency_conditions()
                
                # Sleep until next check
                self._stop_event.wait(self.config.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                time.sleep(10)  # Wait before retry
    
    def _initialize_account_health(self):
        """Inicializa estado salud cuenta"""
        if self.mt5_manager:
            try:
                # Get initial account info
                account_info = self.mt5_manager.get_connection_status()
                balance = account_info.get('balance', 0.0)
                
                self.account_health = AccountHealth(
                    current_balance=balance,
                    starting_balance=balance,
                    peak_balance=balance,
                    current_drawdown=0.0,
                    daily_pnl=0.0,
                    consecutive_losses=0,
                    consecutive_wins=0,
                    open_positions=0
                )
                
                self.logger.info(f"Initial account balance: ${balance:,.2f}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize account health: {str(e)}")
                # Initialize with default values
                self.account_health = AccountHealth()
    
    def _update_account_health(self):
        """Actualiza estado salud cuenta"""
        try:
            # Get current account info
            account_info = self.mt5_manager.get_connection_status() if self.mt5_manager else {}
            current_balance = account_info.get('balance', 0.0)
            equity = account_info.get('equity', current_balance)
            
            # Update balance tracking
            self.account_health.current_balance = current_balance
            if current_balance > self.account_health.peak_balance:
                self.account_health.peak_balance = current_balance
            
            # Calculate current drawdown
            if self.account_health.peak_balance > 0:
                self.account_health.current_drawdown = (
                    (self.account_health.peak_balance - current_balance) / 
                    self.account_health.peak_balance * 100
                )
            
            # Update open positions count
            self.account_health.open_positions = self._get_open_positions_count()
            
            # Update daily P&L
            self.account_health.daily_pnl = self._calculate_daily_pnl()
            
            # Update consecutive losses/wins
            self._update_consecutive_trades()
            
            self.account_health.last_update = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Failed to update account health: {str(e)}")
    
    def _check_emergency_conditions(self):
        """Verifica todas condiciones emergencia"""
        # 1. Check drawdown
        if self._check_max_drawdown():
            self._trigger_emergency_stop(StopReason.MAX_DRAWDOWN)
            return
        
        # 2. Check consecutive losses
        if self._check_consecutive_losses():
            self._trigger_emergency_stop(StopReason.CONSECUTIVE_LOSSES)
            return
        
        # 3. Check daily loss limit
        if self._check_daily_loss_limit():
            self._trigger_emergency_stop(StopReason.MAX_DRAWDOWN)  # Same category
            return
        
        # 4. Check technical issues
        if self._check_technical_issues():
            self._trigger_emergency_stop(StopReason.TECHNICAL_FAILURE)
            return
        
        # 5. Check connection
        if self._check_connection_health():
            self._trigger_emergency_stop(StopReason.CONNECTION_LOST)
            return
        
        # 6. Check market conditions
        if self._check_market_conditions():
            self._trigger_emergency_stop(StopReason.MARKET_CONDITIONS)
            return
        
        # 7. Update emergency level based on conditions
        self._update_emergency_level()
    
    def _check_max_drawdown(self) -> bool:
        """Verifica si drawdown supera límite"""
        return self.account_health.current_drawdown >= self.config.max_drawdown_percent
    
    def _check_consecutive_losses(self) -> bool:
        """Verifica pérdidas consecutivas"""
        return self.account_health.consecutive_losses >= self.config.max_consecutive_losses
    
    def _check_daily_loss_limit(self) -> bool:
        """Verifica límite pérdida diaria"""
        return self.account_health.daily_pnl <= -abs(self.config.daily_loss_limit)
    
    def _check_technical_issues(self) -> bool:
        """Verifica problemas técnicos"""
        try:
            # Check MT5 terminal response time
            if self.mt5_manager:
                start_time = time.time()
                terminal_info = self.mt5_manager.get_terminal_info()
                response_time = (time.time() - start_time) * 1000  # ms
                
                if response_time > self.config.max_terminal_response_ms:
                    self.logger.warning(f"MT5 terminal slow response: {response_time:.1f}ms")
                    return True
                
                # Check data feed quality - last tick age
                if hasattr(terminal_info, 'last_tick_time'):
                    tick_age = time.time() - terminal_info.last_tick_time
                    if tick_age > self.config.max_data_age_seconds:
                        self.logger.warning(f"Stale data feed: {tick_age:.1f}s old")
                        return True
                
                # Check order execution health
                if hasattr(self.account_health, 'failed_orders_count'):
                    if self.account_health.failed_orders_count > self.config.max_failed_orders:
                        self.logger.warning(f"Too many failed orders: {self.account_health.failed_orders_count}")
                        return True
                        
        except Exception as e:
            self.logger.error(f"Technical health check error: {e}")
            return True  # Error = technical issue
            
        return False
    
    def _check_connection_health(self) -> bool:
        """Verifica salud conexión MT5"""
        if not self.mt5_manager:
            return True  # No connection = emergency
            
        try:
            # Simple ping test
            connection_status = self.mt5_manager.get_connection_status()
            return not connection_status.get('connected', False)  # True if disconnected
        except Exception as e:
            self.logger.error(f"Connection health check failed: {e}")
            return True  # Connection failed
    
    def _check_market_conditions(self) -> bool:
        """Verifica condiciones mercado extremas"""
        try:
            # Check for volatility spikes
            if hasattr(self.account_health, 'volatility_index'):
                if self.account_health.volatility_index > self.config.max_volatility_threshold:
                    self.logger.warning(f"Extreme volatility detected: {self.account_health.volatility_index}")
                    return True
            
            # Check for gap events (price jumps > threshold)
            if hasattr(self.account_health, 'max_price_gap'):
                if self.account_health.max_price_gap > self.config.max_price_gap_pips:
                    self.logger.warning(f"Large price gap detected: {self.account_health.max_price_gap} pips")
                    return True
            
            # Check for weekend trading (should be avoided)
            current_time = datetime.now()
            if current_time.weekday() >= 5:  # Saturday=5, Sunday=6
                if self.config.avoid_weekend_trading:
                    self.logger.warning("Weekend trading detected")
                    return True
            
            # Check for major news events (if news calendar available)
            if hasattr(self, 'news_calendar') and self.news_calendar:
                upcoming_events = self.news_calendar.get_high_impact_events(minutes_ahead=30)
                if upcoming_events:
                    self.logger.warning(f"High impact news events in 30 minutes: {len(upcoming_events)}")
                    return True
                    
        except Exception as e:
            self.logger.error(f"Market conditions check error: {e}")
            return True  # Error = assume dangerous conditions
            
        return False
    
    def _update_emergency_level(self):
        """Actualiza nivel emergencia basado en condiciones"""
        current_dd = self.account_health.current_drawdown
        consecutive = self.account_health.consecutive_losses
        
        if current_dd >= self.config.max_drawdown_percent * 0.8 or consecutive >= self.config.max_consecutive_losses - 1:
            self.emergency_level = EmergencyLevel.ORANGE
        elif current_dd >= self.config.max_drawdown_percent * 0.6 or consecutive >= self.config.max_consecutive_losses - 2:
            self.emergency_level = EmergencyLevel.YELLOW
        else:
            self.emergency_level = EmergencyLevel.GREEN
    
    def _trigger_emergency_stop(self, reason: StopReason):
        """Activa parada emergencia"""
        if not self.is_trading_enabled:
            return  # Already stopped
            
        self.is_trading_enabled = False
        self.emergency_level = EmergencyLevel.RED
        self.stop_reason = reason
        self.last_stop_time = datetime.now()
        
        # Create emergency alert
        alert = EmergencyAlert(
            level=EmergencyLevel.RED,
            reason=reason,
            message=self._get_stop_message(reason),
            timestamp=self.last_stop_time,
            account_health=self.account_health
        )
        
        # Execute emergency actions
        actions_taken = self._execute_emergency_actions(reason)
        alert.actions_taken = actions_taken
        
        # Save alert
        self.alerts_history.append(alert)
        
        # Log emergency
        self.logger.critical(f"EMERGENCY STOP TRIGGERED: {reason.value}")
        self.logger.critical(f"Account Health: {self._format_health_summary()}")
        self.logger.critical(f"Actions Taken: {', '.join(actions_taken)}")
        
        # TODO: Send notifications (email, Telegram, etc.)
        try:
            self._send_emergency_notification(alert)
        except Exception as e:
            self.logger.error(f"Failed to send emergency notification: {e}")
    
    def _execute_emergency_actions(self, reason: StopReason) -> List[str]:
        """Ejecuta acciones emergencia automáticas"""
        actions = []
        
        try:
            # 1. Close all open positions
            if self._close_all_positions():
                actions.append("All positions closed")
            
            # 2. Cancel pending orders
            if self._cancel_all_orders():
                actions.append("All orders cancelled")
            
            # 3. Disable automated trading
            actions.append("Automated trading disabled")
            
            # 4. Save emergency state
            self._save_emergency_state()
            actions.append("Emergency state saved")
            
        except Exception as e:
            self.logger.error(f"Emergency actions failed: {str(e)}")
            actions.append(f"Action failed: {str(e)}")
        
        return actions
    
    def _close_all_positions(self) -> bool:
        """Cierra todas posiciones abiertas"""
        if not self.mt5_manager:
            return False
            
        try:
            import MetaTrader5 as mt5  # type: ignore
            
            # Get all open positions
            positions = mt5.positions_get()
            if positions is None:
                return True  # No positions to close
            
            closed_count = 0
            for position in positions:
                # Determine action (opposite of position type)
                action = mt5.TRADE_ACTION_DEAL
                if position.type == mt5.POSITION_TYPE_BUY:
                    order_type = mt5.ORDER_TYPE_SELL
                else:
                    order_type = mt5.ORDER_TYPE_BUY
                
                # Create close request
                request = {
                    "action": action,
                    "symbol": position.symbol,
                    "volume": position.volume,
                    "type": order_type,
                    "position": position.ticket,
                    "deviation": 20,
                    "comment": "EMERGENCY_CLOSE"
                }
                
                # Execute close order
                result = mt5.order_send(request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    closed_count += 1
                    self.logger.info(f"Emergency closed position {position.ticket}")
                else:
                    self.logger.error(f"Failed to close position {position.ticket}: {result.comment}")
            
            self.logger.info(f"Emergency close completed: {closed_count}/{len(positions)} positions closed")
            return closed_count == len(positions)
            
        except ImportError:
            self.logger.error("MT5 not available for position closing")
            return False
        except Exception as e:
            self.logger.error(f"Error closing positions: {e}")
            return False
    
    def _cancel_all_orders(self) -> bool:
        """Cancela todas órdenes pendientes"""
        if not self.mt5_manager:
            return False
            
        try:
            import MetaTrader5 as mt5  # type: ignore
            
            # Get all pending orders
            orders = mt5.orders_get()
            if orders is None:
                return True  # No orders to cancel
            
            cancelled_count = 0
            for order in orders:
                # Create cancel request
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": order.ticket,
                    "comment": "EMERGENCY_CANCEL"
                }
                
                # Execute cancel order
                result = mt5.order_send(request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    cancelled_count += 1
                    self.logger.info(f"Emergency cancelled order {order.ticket}")
                else:
                    self.logger.error(f"Failed to cancel order {order.ticket}: {result.comment}")
            
            self.logger.info(f"Emergency cancel completed: {cancelled_count}/{len(orders)} orders cancelled")
            return cancelled_count == len(orders)
            
        except ImportError:
            self.logger.error("MT5 not available for order cancellation")
            return False
        except Exception as e:
            self.logger.error(f"Error cancelling orders: {e}")
            return False
    
    def manual_emergency_stop(self, reason: str = "Manual intervention"):
        """Activación manual parada emergencia"""
        self.logger.warning(f"Manual emergency stop requested: {reason}")
        self._trigger_emergency_stop(StopReason.MANUAL_STOP)
    
    def reset_emergency_stop(self) -> bool:
        """Resetea sistema después parada emergencia"""
        if not self.last_stop_time:
            return True  # No emergency to reset
            
        # Check cooldown period
        cooldown_elapsed = datetime.now() - self.last_stop_time
        if cooldown_elapsed.total_seconds() < self.config.recovery_cooldown:
            remaining = self.config.recovery_cooldown - cooldown_elapsed.total_seconds()
            self.logger.warning(f"Cooldown active. {remaining:.0f} seconds remaining")
            return False
        
        # Reset emergency state
        self.is_trading_enabled = True
        self.emergency_level = EmergencyLevel.GREEN
        self.stop_reason = None
        
        # Reset consecutive losses (fresh start)
        self.account_health.consecutive_losses = 0
        self.account_health.consecutive_wins = 0
        
        self.logger.info("Emergency stop reset - Trading re-enabled")
        return True
    
    def get_health_report(self) -> Dict[str, Any]:
        """Obtiene reporte completo salud sistema"""
        return {
            'timestamp': datetime.now().isoformat(),
            'trading_enabled': self.is_trading_enabled,
            'emergency_level': self.emergency_level.value,
            'stop_reason': self.stop_reason.value if self.stop_reason else None,
            'last_stop_time': self.last_stop_time.isoformat() if self.last_stop_time else None,
            'account_health': {
                'current_balance': self.account_health.current_balance,
                'starting_balance': self.account_health.starting_balance,
                'peak_balance': self.account_health.peak_balance,
                'current_drawdown': self.account_health.current_drawdown,
                'daily_pnl': self.account_health.daily_pnl,
                'consecutive_losses': self.account_health.consecutive_losses,
                'consecutive_wins': self.account_health.consecutive_wins,
                'open_positions': self.account_health.open_positions
            },
            'config': {
                'max_drawdown_percent': self.config.max_drawdown_percent,
                'max_consecutive_losses': self.config.max_consecutive_losses,
                'daily_loss_limit': self.config.daily_loss_limit
            },
            'recent_alerts': [
                {
                    'level': alert.level.value,
                    'reason': alert.reason.value,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'actions_taken': alert.actions_taken
                }
                for alert in self.alerts_history[-5:]  # Last 5 alerts
            ]
        }
    
    # Helper methods
    def _get_account_info(self) -> Dict[str, Any]:
        """Obtiene información cuenta MT5"""
        if self.mt5_manager:
            try:
                return self.mt5_manager.get_connection_status()
            except Exception as e:
                self.logger.error(f"Error getting account info: {e}")
                return {}
        return {}
    
    def _get_open_positions_count(self) -> int:
        """Cuenta posiciones abiertas"""
        try:
            import MetaTrader5 as mt5  # type: ignore
            
            positions = mt5.positions_get()
            return len(positions) if positions is not None else 0
            
        except ImportError:
            self.logger.warning("MT5 not available for position count")
            return 0
        except Exception as e:
            self.logger.error(f"Error counting positions: {e}")
            return 0
    
    def _calculate_daily_pnl(self) -> float:
        """Calcula P&L diario"""
        try:
            import MetaTrader5 as mt5  # type: ignore
            from datetime import datetime, time
            
            # Get today's date range
            today = datetime.now().date()
            start_of_day = datetime.combine(today, time.min)
            
            # Get deals from today
            deals = mt5.history_deals_get(start_of_day, datetime.now())
            if deals is None:
                return 0.0
            
            # Calculate total P&L for today
            daily_pnl = 0.0
            for deal in deals:
                if hasattr(deal, 'profit'):
                    daily_pnl += deal.profit
                    
            return daily_pnl
            
        except ImportError:
            self.logger.warning("MT5 not available for P&L calculation")
            return 0.0
        except Exception as e:
            self.logger.error(f"Error calculating daily P&L: {e}")
            return 0.0
    
    def _update_consecutive_trades(self):
        """Actualiza contador trades consecutivos"""
        try:
            import MetaTrader5 as mt5  # type: ignore
            from datetime import datetime, timedelta
            
            # Get recent deals (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            deals = mt5.history_deals_get(yesterday, datetime.now())
            
            if deals is None or len(deals) == 0:
                return
            
            # Sort deals by time (newest first)
            sorted_deals = sorted(deals, key=lambda x: x.time, reverse=True)
            
            # Count consecutive wins/losses from most recent
            consecutive_losses = 0
            consecutive_wins = 0
            
            for deal in sorted_deals:
                if hasattr(deal, 'profit') and deal.profit != 0:  # Only count actual trades, not balance operations
                    if deal.profit < 0:  # Loss
                        if consecutive_wins == 0:  # Still counting losses
                            consecutive_losses += 1
                        else:
                            break  # Hit a win, stop counting losses
                    elif deal.profit > 0:  # Win
                        if consecutive_losses == 0:  # Still counting wins
                            consecutive_wins += 1
                        else:
                            break  # Hit a loss, stop counting wins
            
            # Update account health
            self.account_health.consecutive_losses = consecutive_losses
            self.account_health.consecutive_wins = consecutive_wins
            
            # Set last trade result
            if len(sorted_deals) > 0 and hasattr(sorted_deals[0], 'profit'):
                if sorted_deals[0].profit > 0:
                    self.account_health.last_trade_result = "WIN"
                elif sorted_deals[0].profit < 0:
                    self.account_health.last_trade_result = "LOSS"
                else:
                    self.account_health.last_trade_result = "NEUTRAL"
            
        except ImportError:
            self.logger.warning("MT5 not available for trade history analysis")
        except Exception as e:
            self.logger.error(f"Error updating consecutive trades: {e}")
    
    def _get_stop_message(self, reason: StopReason) -> str:
        """Genera mensaje parada según razón"""
        messages = {
            StopReason.MAX_DRAWDOWN: f"Maximum drawdown reached: {self.account_health.current_drawdown:.2f}%",
            StopReason.CONSECUTIVE_LOSSES: f"Maximum consecutive losses: {self.account_health.consecutive_losses}",
            StopReason.TECHNICAL_FAILURE: "Technical failure detected",
            StopReason.MARKET_CONDITIONS: "Extreme market conditions detected", 
            StopReason.MANUAL_STOP: "Manual emergency stop activated",
            StopReason.CONNECTION_LOST: "MT5 connection lost",
            StopReason.ACCOUNT_ISSUE: "Account issue detected"
        }
        return messages.get(reason, "Emergency stop activated")
    
    def _format_health_summary(self) -> str:
        """Formatea resumen salud para logging"""
        h = self.account_health
        return (f"Balance: ${h.current_balance:,.2f}, "
                f"Drawdown: {h.current_drawdown:.2f}%, "
                f"Consecutive Losses: {h.consecutive_losses}, "
                f"Daily P&L: ${h.daily_pnl:,.2f}")
    
    def _save_emergency_state(self):
        """Guarda estado emergencia a disco"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'emergency_level': self.emergency_level.value,
                'stop_reason': self.stop_reason.value if self.stop_reason else None,
                'is_trading_enabled': self.is_trading_enabled,
                'account_health': {
                    'current_balance': self.account_health.current_balance,
                    'current_drawdown': self.account_health.current_drawdown,
                    'daily_pnl': self.account_health.daily_pnl,
                    'consecutive_losses': self.account_health.consecutive_losses,
                    'open_positions': self.account_health.open_positions
                },
                'config': {
                    'max_drawdown_percent': self.config.max_drawdown_percent,
                    'max_consecutive_losses': self.config.max_consecutive_losses,
                    'daily_loss_limit': self.config.daily_loss_limit
                }
            }
            
            # Save to emergency state file
            emergency_file = "04-DATA/state/emergency_state.json"
            import os
            os.makedirs(os.path.dirname(emergency_file), exist_ok=True)
            
            with open(emergency_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            self.logger.info(f"Emergency state saved to {emergency_file}")
        except Exception as e:
            self.logger.error(f"Failed to save emergency state: {str(e)}")
    
    def _send_emergency_notification(self, alert: EmergencyAlert):
        """Envía notificación de emergencia"""
        try:
            # Log critical alert
            self.logger.critical(f"🚨 EMERGENCY ALERT 🚨")
            self.logger.critical(f"Level: {alert.level.value.upper()}")
            self.logger.critical(f"Reason: {alert.reason.value}")
            self.logger.critical(f"Message: {alert.message}")
            self.logger.critical(f"Actions: {', '.join(alert.actions_taken)}")
            
            # TODO: Implement additional notification methods
            # - Email notification
            # - Telegram bot message  
            # - SMS alert
            # - Discord webhook
            # - Phone call via Twilio
            
            # For now, just ensure critical logging
            notification_summary = {
                'timestamp': alert.timestamp.isoformat(),
                'level': alert.level.value,
                'reason': alert.reason.value,
                'message': alert.message,
                'account_balance': alert.account_health.current_balance,
                'drawdown': alert.account_health.current_drawdown,
                'actions_taken': alert.actions_taken
            }
            
            # Save notification to emergency log
            emergency_log_file = "05-LOGS/emergency/emergency_notifications.json"
            import os
            os.makedirs(os.path.dirname(emergency_log_file), exist_ok=True)
            
            # Append to notifications log
            try:
                with open(emergency_log_file, 'r') as f:
                    notifications = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                notifications = []
            
            notifications.append(notification_summary)
            
            # Keep only last 100 notifications
            if len(notifications) > 100:
                notifications = notifications[-100:]
            
            with open(emergency_log_file, 'w') as f:
                json.dump(notifications, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to send emergency notification: {e}")
            # Fallback - at least print to console
            print(f"🚨 EMERGENCY: {alert.message}")
            print(f"Level: {alert.level.value} | Reason: {alert.reason.value}")
            print(f"Actions: {', '.join(alert.actions_taken)}")


# Ejemplo uso:
if __name__ == "__main__":
    # Testing basic functionality
    config = EmergencyConfig(
        max_drawdown_percent=3.0,  # 3% max drawdown
        max_consecutive_losses=3,   # 3 consecutive losses
        daily_loss_limit=200.0     # $200 daily limit
    )
    
    emergency_system = EmergencyStopSystem(config)
    emergency_system.start_monitoring()
    
    # Simulate some conditions
    print("Emergency System Status:")
    print(json.dumps(emergency_system.get_health_report(), indent=2))
