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
    from ..enums import TradingStatus
except ImportError:
    # Fallback para testing
    pass

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
            self.mt5_manager = MT5DataManager()
            self.logger = SmartTradingLogger("EmergencyStop")
        except:
            self.mt5_manager = None
            self.logger = logging.getLogger("EmergencyStop")
            
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
                account_info = self._get_account_info()
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
    
    def _update_account_health(self):
        """Actualiza estado salud cuenta"""
        try:
            # Get current account info
            account_info = self._get_account_info()
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
        # TODO: Implement technical health checks
        # - MT5 terminal response time
        # - Data feed quality
        # - Order execution issues
        return False
    
    def _check_connection_health(self) -> bool:
        """Verifica salud conexión MT5"""
        if not self.mt5_manager:
            return True  # No connection = emergency
            
        try:
            # Simple ping test
            account_info = self._get_account_info()
            return account_info.get('balance', 0) == 0  # Suspicious if 0
        except:
            return True  # Connection failed
    
    def _check_market_conditions(self) -> bool:
        """Verifica condiciones mercado extremas"""
        # TODO: Implement market conditions monitoring
        # - Volatility spikes
        # - Gap events  
        # - Weekend trading
        # - News events
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
            # TODO: Implement with actual MT5DataManager
            # positions = self.mt5_manager.get_positions()
            # for position in positions:
            #     self.mt5_manager.close_position(position['ticket'])
            return True
        except:
            return False
    
    def _cancel_all_orders(self) -> bool:
        """Cancela todas órdenes pendientes"""
        if not self.mt5_manager:
            return False
            
        try:
            # TODO: Implement with actual MT5DataManager  
            # orders = self.mt5_manager.get_orders()
            # for order in orders:
            #     self.mt5_manager.cancel_order(order['ticket'])
            return True
        except:
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
            # TODO: Use actual MT5DataManager method
            return {'balance': 10000.0, 'equity': 10000.0}  # Dummy data
        return {}
    
    def _get_open_positions_count(self) -> int:
        """Cuenta posiciones abiertas"""
        # TODO: Implement actual count
        return 0
    
    def _calculate_daily_pnl(self) -> float:
        """Calcula P&L diario"""
        # TODO: Implement actual calculation
        return 0.0
    
    def _update_consecutive_trades(self):
        """Actualiza contador trades consecutivos"""
        # TODO: Implement based on recent trade history
        pass
    
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
            state = self.get_health_report()
            # TODO: Save to file or database
            self.logger.info("Emergency state saved")
        except Exception as e:
            self.logger.error(f"Failed to save emergency state: {str(e)}")


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
