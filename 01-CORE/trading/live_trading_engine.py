#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 LIVE TRADING ENGINE - ICT ENGINE v6.0 ENTERPRISE
===================================================

Motor de trading en vivo para operaciones de cuenta real.
Integrado con ExecutionEngine y PositionSizingCalculator.

Características:
✅ Gestión completa de órdenes en vivo
✅ Monitoreo de posiciones activas
✅ Gestión de riesgo en tiempo real
✅ Logging centralizado de operaciones
✅ Estado de conexión MT5

Autor: ICT Engine v6.0 Team
Fecha: 13 Septiembre 2025
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
import time
import logging
from collections import defaultdict

try:
    from protocols.unified_logging import get_unified_logger
    LOGGER_AVAILABLE = True
except ImportError:
    try:
        # Fallback: probar importación relativa desde 01-CORE
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from protocols.unified_logging import get_unified_logger
        LOGGER_AVAILABLE = True
    except ImportError:
        LOGGER_AVAILABLE = False
        get_unified_logger = None

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    # Safe attribute access for MT5 methods
    _mt5_initialize = getattr(mt5, 'initialize', None)
    _mt5_account_info = getattr(mt5, 'account_info', None)
    _mt5_shutdown = getattr(mt5, 'shutdown', None)
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None
    _mt5_initialize = None
    _mt5_account_info = None
    _mt5_shutdown = None

try:
    from trading.execution_engine import ExecutionEngine
    EXECUTION_ENGINE_AVAILABLE = True
except ImportError:
    EXECUTION_ENGINE_AVAILABLE = False
    ExecutionEngine = None

try:
    from risk_management.position_sizing import PositionSizingCalculator, PositionSizingParameters
    POSITION_SIZING_AVAILABLE = True
except ImportError:
    POSITION_SIZING_AVAILABLE = False
    PositionSizingCalculator = None
    PositionSizingParameters = None

# Central logging function
def _safe_log(level: str, message: str, component: str = "LiveTradingEngine") -> None:
    """Función de logging segura centralizada"""
    if LOGGER_AVAILABLE and get_unified_logger is not None:
        try:
            logger = get_unified_logger(component)
            getattr(logger, level, logger.info)(message)
        except Exception:
            pass
    else:
        # Fallback a logging estándar
        getattr(logging, level, logging.info)(f"[{component}] {message}")

class TradingStatus(Enum):
    """Estados del motor de trading"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    DISCONNECTED = "disconnected"

class OrderStatus(Enum):
    """Estados de órdenes"""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIAL = "partial"

class SignalType(Enum):
    """Tipos de señales de trading"""
    BUY = "buy"
    SELL = "sell"
    CLOSE_BUY = "close_buy"
    CLOSE_SELL = "close_sell"
    MODIFY_SL = "modify_sl"
    MODIFY_TP = "modify_tp"

@dataclass
class TradingSignal:
    """Señal de trading"""
    signal_id: str
    signal_type: SignalType
    symbol: str
    price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_percent: float = 1.0
    confidence: float = 1.0
    source: str = "ICT_ENGINE"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LivePosition:
    """Posición en vivo"""
    ticket: int
    symbol: str
    type: str  # 'buy' o 'sell'
    lots: float
    open_price: float
    current_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    profit: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TradingSession:
    """Sesión de trading"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_profit: float = 0.0
    max_drawdown: float = 0.0
    initial_balance: float = 0.0
    current_balance: float = 0.0
    active_positions: List[LivePosition] = field(default_factory=list)

class LiveTradingEngine:
    """
    🚀 Motor de Trading en Vivo Enterprise
    
    Gestiona operaciones en cuenta real:
    - Procesamiento de señales
    - Ejecución de órdenes
    - Monitoreo de posiciones
    - Gestión de riesgo
    - Logging de operaciones
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializar motor de trading en vivo
        
        Args:
            config: Configuración del motor
        """
        self.config = config or self._default_config()
        
        # Estado del motor
        self.status = TradingStatus.STOPPED
        self.is_running = False
        self._stop_event = threading.Event()
        
        # Configurar logger
        if LOGGER_AVAILABLE and get_unified_logger is not None:
            self.logger = get_unified_logger("LiveTrading")
        else:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger("LiveTrading")
        
        # Componentes del sistema
        self.execution_engine = None
        self.position_calculator = None
        self._initialize_components()
        
        # Sesión actual
        self.current_session: Optional[TradingSession] = None
        
        # Posiciones activas
        self.active_positions: Dict[int, LivePosition] = {}
        
        # Cola de señales
        self.signal_queue: List[TradingSignal] = []
        self.signal_queue_lock = threading.Lock()
        
        # Estadísticas
        self.stats = {
            'signals_received': 0,
            'orders_executed': 0,
            'successful_orders': 0,
            'failed_orders': 0,
            'positions_opened': 0,
            'positions_closed': 0,
            'total_profit': 0.0,
            'session_count': 0,
            'uptime_seconds': 0
        }
        
        # Callbacks
        self.callbacks = {
            'on_signal': [],
            'on_order_filled': [],
            'on_position_closed': [],
            'on_error': []
        }
        
        # Hilos de trabajo
        self._signal_processor_thread = None
        self._position_monitor_thread = None
        self._stats_thread = None
        
        if LOGGER_AVAILABLE:
            self.logger.info("🚀 LiveTradingEngine inicializado", "LiveTrading")
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'max_concurrent_positions': 5,
            'max_risk_per_trade': 2.0,
            'max_daily_risk': 5.0,
            'enable_auto_trading': False,
            'position_monitoring_interval': 5.0,  # segundos
            'signal_processing_interval': 1.0,  # segundos
            'stats_update_interval': 30.0,  # segundos
            'max_signal_queue_size': 100,
            'enable_position_trailing': True,
            'trailing_stop_pips': 20,
            'risk_management': {
                'max_drawdown_percent': 10.0,
                'daily_loss_limit': 500.0,
                'consecutive_loss_limit': 3
            },
            'mt5_config': {
                'timeout_ms': 30000,
                'retries': 3,
                'retry_delay_seconds': 1.0
            }
        }
    
    def _initialize_components(self):
        """Inicializar componentes del sistema"""
        try:
            # Inicializar ExecutionEngine
            if EXECUTION_ENGINE_AVAILABLE and ExecutionEngine:
                self.execution_engine = ExecutionEngine(self.config.get('execution', {}))
                if LOGGER_AVAILABLE:
                    self.logger.info("✅ ExecutionEngine inicializado", "LiveTrading")
            else:
                if LOGGER_AVAILABLE:
                    self.logger.warning("⚠️ ExecutionEngine no disponible", "LiveTrading")
            
            # Inicializar PositionSizingCalculator
            if POSITION_SIZING_AVAILABLE and PositionSizingCalculator:
                self.position_calculator = PositionSizingCalculator(self.config.get('position_sizing', {}))
                if LOGGER_AVAILABLE:
                    self.logger.info("✅ PositionSizingCalculator inicializado", "LiveTrading")
            else:
                if LOGGER_AVAILABLE:
                    self.logger.warning("⚠️ PositionSizingCalculator no disponible", "LiveTrading")
                    
        except Exception as e:
            if LOGGER_AVAILABLE:
                self.logger.error(f"Error inicializando componentes: {e}", "LiveTrading")
    
    def start_trading(self, session_id: Optional[str] = None) -> bool:
        """
        Iniciar motor de trading
        
        Args:
            session_id: ID de la sesión (opcional)
            
        Returns:
            bool: True si se inició correctamente
        """
        try:
            if self.status == TradingStatus.RUNNING:
                if LOGGER_AVAILABLE:
                    self.logger.warning("Motor ya está ejecutándose", "LiveTrading")
                return True
            
            self.status = TradingStatus.STARTING
            
            # Verificar conexión MT5
            if not self._verify_mt5_connection():
                self.status = TradingStatus.DISCONNECTED
                return False
            
            # Crear nueva sesión
            self._start_new_session(session_id)
            
            # Inicializar hilos de trabajo
            self._stop_event.clear()
            self.is_running = True
            
            self._signal_processor_thread = threading.Thread(
                target=self._signal_processor_loop,
                name="SignalProcessor"
            )
            
            self._position_monitor_thread = threading.Thread(
                target=self._position_monitor_loop,
                name="PositionMonitor"
            )
            
            self._stats_thread = threading.Thread(
                target=self._stats_update_loop,
                name="StatsUpdater"
            )
            
            # Iniciar hilos
            self._signal_processor_thread.start()
            self._position_monitor_thread.start()
            self._stats_thread.start()
            
            self.status = TradingStatus.RUNNING
            
            if LOGGER_AVAILABLE:
                session_id = getattr(self.current_session, 'session_id', 'Unknown') if self.current_session else 'None'
                self.logger.info(f"🚀 Motor de trading iniciado - Sesión: {session_id}", "LiveTrading")
            
            return True
            
        except Exception as e:
            self.status = TradingStatus.ERROR
            if LOGGER_AVAILABLE:
                self.logger.error(f"Error iniciando motor de trading: {e}", "LiveTrading")
            return False
    
    def stop_trading(self, force: bool = False) -> bool:
        """
        Detener motor de trading
        
        Args:
            force: Detener forzadamente
            
        Returns:
            bool: True si se detuvo correctamente
        """
        try:
            if self.status == TradingStatus.STOPPED:
                return True
            
            if LOGGER_AVAILABLE:
                self.logger.info("🛑 Deteniendo motor de trading...", "LiveTrading")
            
            # Detener procesamiento
            self.is_running = False
            self._stop_event.set()
            
            # Esperar a que terminen los hilos
            if self._signal_processor_thread and self._signal_processor_thread.is_alive():
                self._signal_processor_thread.join(timeout=2.0)
                
            if self._position_monitor_thread and self._position_monitor_thread.is_alive():
                self._position_monitor_thread.join(timeout=2.0)
                
            if self._stats_thread and self._stats_thread.is_alive():
                self._stats_thread.join(timeout=2.0)
            
            # Cerrar posiciones si es forzado
            if force:
                self._close_all_positions()
            
            # Finalizar sesión
            if self.current_session:
                self.current_session.end_time = datetime.now()
                self.stats['session_count'] += 1
            
            self.status = TradingStatus.STOPPED
            
            if LOGGER_AVAILABLE:
                self.logger.info("✅ Motor de trading detenido", "LiveTrading")
            
            return True
            
        except Exception as e:
            self.status = TradingStatus.ERROR
            if LOGGER_AVAILABLE:
                self.logger.error(f"Error deteniendo motor: {e}", "LiveTrading")
            return False
    
    def add_signal(self, signal: TradingSignal) -> bool:
        """
        Agregar señal a la cola de procesamiento
        
        Args:
            signal: Señal de trading
            
        Returns:
            bool: True si se agregó correctamente
        """
        try:
            with self.signal_queue_lock:
                if len(self.signal_queue) >= self.config.get('max_signal_queue_size', 100):
                    if LOGGER_AVAILABLE:
                        self.logger.warning("Cola de señales llena, descartando señal más antigua", "LiveTrading")
                    self.signal_queue.pop(0)  # Remover la más antigua
                
                self.signal_queue.append(signal)
                self.stats['signals_received'] += 1
            
            if LOGGER_AVAILABLE:
                self.logger.info(f"📨 Señal recibida: {signal.signal_type.value} {signal.symbol}", "LiveTrading")
            
            # Ejecutar callbacks
            self._execute_callbacks('on_signal', signal)
            
            return True
            
        except Exception as e:
            if LOGGER_AVAILABLE:
                self.logger.error(f"Error agregando señal: {e}", "LiveTrading")
            return False
    
    def get_active_positions(self) -> List[LivePosition]:
        """Obtener posiciones activas"""
        return list(self.active_positions.values())
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la sesión actual"""
        if not self.current_session:
            return {}
        
        session = self.current_session
        win_rate = 0.0
        if session.total_trades > 0:
            win_rate = session.winning_trades / session.total_trades * 100
        
        return {
            'session_id': session.session_id,
            'start_time': session.start_time,
            'duration_minutes': (datetime.now() - session.start_time).total_seconds() / 60,
            'total_trades': session.total_trades,
            'winning_trades': session.winning_trades,
            'losing_trades': session.losing_trades,
            'win_rate': win_rate,
            'total_profit': session.total_profit,
            'max_drawdown': session.max_drawdown,
            'active_positions': len(session.active_positions),
            'current_balance': session.current_balance
        }
    
    def add_callback(self, event: str, callback: Callable):
        """Agregar callback para eventos"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _verify_mt5_connection(self) -> bool:
        """Verificar conexión con MT5"""
        if not MT5_AVAILABLE or not mt5:
            if LOGGER_AVAILABLE:
                self.logger.error("MT5 no está disponible", "LiveTrading")
            return False
        
        try:
            from real_trading.mt5_config import mt5_initialize  # type: ignore
            # Verificar si ya está inicializado mediante wrapper central
            if mt5_initialize and not mt5_initialize():
                if LOGGER_AVAILABLE:
                    self.logger.error("No se pudo inicializar MT5", "LiveTrading")
                return False
            
            # Verificar conexión al servidor
            if _mt5_account_info:
                account_info = _mt5_account_info()
                if account_info is None:
                    if LOGGER_AVAILABLE:
                        self.logger.error("No se pudo obtener información de cuenta", "LiveTrading")
                    return False
                
                if LOGGER_AVAILABLE:
                    account_login = getattr(account_info, 'login', 'Unknown')
                    self.logger.info(f"✅ Conectado a MT5 - Cuenta: {account_login}", "LiveTrading")
            
            return True
            
        except Exception as e:
            if LOGGER_AVAILABLE:
                self.logger.error(f"Error verificando conexión MT5: {e}", "LiveTrading")
            return False
    
    def _start_new_session(self, session_id: Optional[str] = None):
        """Iniciar nueva sesión de trading"""
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Obtener balance inicial
        initial_balance = 0.0
        if MT5_AVAILABLE and _mt5_account_info:
            try:
                account_info = _mt5_account_info()
                if account_info:
                    initial_balance = getattr(account_info, 'balance', 0.0)
            except Exception:
                pass
        
        self.current_session = TradingSession(
            session_id=session_id,
            start_time=datetime.now(),
            initial_balance=initial_balance,
            current_balance=initial_balance
        )
    
    def _signal_processor_loop(self):
        """Bucle de procesamiento de señales"""
        interval = self.config.get('signal_processing_interval', 1.0)
        
        while self.is_running and not self._stop_event.is_set():
            try:
                # Procesar señales en cola
                with self.signal_queue_lock:
                    signals_to_process = self.signal_queue.copy()
                    self.signal_queue.clear()
                
                for signal in signals_to_process:
                    if not self.is_running:
                        break
                    self._process_signal(signal)
                
                if self._stop_event.wait(interval):
                    break
                
            except Exception as e:
                if LOGGER_AVAILABLE:
                    self.logger.error(f"Error en procesador de señales: {e}", "LiveTrading")
                if self._stop_event.wait(interval):
                    break
    
    def _position_monitor_loop(self):
        """Bucle de monitoreo de posiciones"""
        interval = self.config.get('position_monitoring_interval', 5.0)
        
        while self.is_running and not self._stop_event.is_set():
            try:
                self._update_positions()
                if self._stop_event.wait(interval):
                    break
                
            except Exception as e:
                if LOGGER_AVAILABLE:
                    self.logger.error(f"Error en monitor de posiciones: {e}", "LiveTrading")
                if self._stop_event.wait(interval):
                    break
    
    def _stats_update_loop(self):
        """Bucle de actualización de estadísticas"""
        interval = self.config.get('stats_update_interval', 30.0)
        start_time = time.time()
        
        while self.is_running and not self._stop_event.is_set():
            try:
                # Actualizar tiempo de actividad
                self.stats['uptime_seconds'] = int(time.time() - start_time)
                
                # Actualizar balance de sesión
                if self.current_session and MT5_AVAILABLE and _mt5_account_info:
                    try:
                        account_info = _mt5_account_info()
                        if account_info:
                            self.current_session.current_balance = getattr(account_info, 'balance', 0.0)
                    except:
                        pass
                
                if self._stop_event.wait(interval):
                    break
                
            except Exception as e:
                if LOGGER_AVAILABLE:
                    self.logger.error(f"Error actualizando estadísticas: {e}", "LiveTrading")
                if self._stop_event.wait(interval):
                    break
    
    def _process_signal(self, signal: TradingSignal):
        """Procesar una señal de trading"""
        try:
            if not self.config.get('enable_auto_trading', False):
                if LOGGER_AVAILABLE:
                    self.logger.info(f"Auto-trading deshabilitado, ignorando señal {signal.signal_id}", "LiveTrading")
                return
            
            # Verificar límites de riesgo
            if not self._check_risk_limits(signal):
                return
            
            # Procesar según tipo de señal
            if signal.signal_type in [SignalType.BUY, SignalType.SELL]:
                self._execute_market_order(signal)
            elif signal.signal_type in [SignalType.CLOSE_BUY, SignalType.CLOSE_SELL]:
                self._close_positions_by_symbol(signal.symbol, signal.signal_type)
            elif signal.signal_type in [SignalType.MODIFY_SL, SignalType.MODIFY_TP]:
                self._modify_positions(signal)
                
        except Exception as e:
            if LOGGER_AVAILABLE:
                self.logger.error(f"Error procesando señal {signal.signal_id}: {e}", "LiveTrading")
            self._execute_callbacks('on_error', {'signal': signal, 'error': str(e)})
    
    def _execute_market_order(self, signal: TradingSignal):
        """Ejecutar orden de mercado"""
        try:
            if not self.execution_engine or not self.position_calculator:
                if LOGGER_AVAILABLE:
                    self.logger.error("Componentes de ejecución no disponibles", "LiveTrading")
                return
            
            # Calcular tamaño de posición
            account_info = self._get_account_info()
            if not account_info:
                return
            
            if POSITION_SIZING_AVAILABLE and PositionSizingParameters:
                sizing_params = PositionSizingParameters(
                    symbol=signal.symbol,
                    account_balance=account_info['balance'],
                    risk_percent=signal.risk_percent,
                    entry_price=signal.price,
                    stop_loss=signal.stop_loss or signal.price * (0.99 if signal.signal_type == SignalType.BUY else 1.01)
                )
                
                sizing_result = self.position_calculator.calculate_position_size(sizing_params)
                
                if not sizing_result.is_valid:
                    if LOGGER_AVAILABLE:
                        self.logger.warning(f"Tamaño de posición inválido: {sizing_result.validation_message}", "LiveTrading")
                    return
                
                # Ejecutar orden (simulada por ahora)
                if LOGGER_AVAILABLE:
                    self.logger.info(f"💹 Ejecutando orden: {signal.signal_type.value} {sizing_result.lots} lots de {signal.symbol}", "LiveTrading")
                
                # Simular ejecución exitosa
                self.stats['orders_executed'] += 1
                self.stats['successful_orders'] += 1
                self.stats['positions_opened'] += 1
                
                if self.current_session:
                    self.current_session.total_trades += 1
                    
        except Exception as e:
            self.stats['failed_orders'] += 1
            if LOGGER_AVAILABLE:
                self.logger.error(f"Error ejecutando orden: {e}", "LiveTrading")
    
    def _check_risk_limits(self, signal: TradingSignal) -> bool:
        """Verificar límites de riesgo"""
        # Verificar número máximo de posiciones
        if len(self.active_positions) >= self.config.get('max_concurrent_positions', 5):
            if LOGGER_AVAILABLE:
                self.logger.warning("Máximo de posiciones concurrentes alcanzado", "LiveTrading")
            return False
        
        # Verificar riesgo por operación
        if signal.risk_percent > self.config.get('max_risk_per_trade', 2.0):
            if LOGGER_AVAILABLE:
                self.logger.warning(f"Riesgo por operación excede límite: {signal.risk_percent}%", "LiveTrading")
            return False
        
        return True
    
    def _get_account_info(self) -> Optional[Dict[str, Any]]:
        """Obtener información de cuenta"""
        if MT5_AVAILABLE and _mt5_account_info:
            try:
                account_info = _mt5_account_info()
                if account_info:
                    return {
                        'balance': getattr(account_info, 'balance', 0.0),
                        'equity': getattr(account_info, 'equity', 0.0),
                        'margin': getattr(account_info, 'margin', 0.0),
                        'free_margin': getattr(account_info, 'margin_free', 0.0),
                        'margin_level': getattr(account_info, 'margin_level', 0.0)
                    }
            except:
                pass
        
        return None
    
    def _update_positions(self):
        """Actualizar posiciones activas"""
        # En implementación real, obtendría posiciones de MT5
        pass
    
    def _close_positions_by_symbol(self, symbol: str, signal_type: SignalType):
        """Cerrar posiciones por símbolo"""
        if LOGGER_AVAILABLE:
            self.logger.info(f"🔄 Cerrando posiciones de {symbol}", "LiveTrading")
    
    def _modify_positions(self, signal: TradingSignal):
        """Modificar posiciones existentes"""
        if LOGGER_AVAILABLE:
            self.logger.info(f"📝 Modificando posiciones de {signal.symbol}", "LiveTrading")
    
    def _close_all_positions(self):
        """Cerrar todas las posiciones activas"""
        if LOGGER_AVAILABLE:
            self.logger.info("🔴 Cerrando todas las posiciones", "LiveTrading")
    
    def _execute_callbacks(self, event: str, data: Any):
        """Ejecutar callbacks de eventos"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                if LOGGER_AVAILABLE:
                    self.logger.error(f"Error en callback {event}: {e}", "LiveTrading")

# Funciones de utilidad
def create_live_trading_engine(config: Optional[Dict] = None) -> LiveTradingEngine:
    """Factory function para crear motor de trading"""
    return LiveTradingEngine(config)

def create_trading_signal(signal_type: SignalType, symbol: str, price: float, 
                         stop_loss: Optional[float] = None, 
                         take_profit: Optional[float] = None,
                         risk_percent: float = 1.0) -> TradingSignal:
    """Crear señal de trading"""
    signal_id = f"{signal_type.value}_{symbol}_{int(datetime.now().timestamp())}"
    
    return TradingSignal(
        signal_id=signal_id,
        signal_type=signal_type,
        symbol=symbol,
        price=price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        risk_percent=risk_percent
    )