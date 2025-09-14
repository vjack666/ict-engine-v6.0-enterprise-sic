#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 EXECUTION ENGINE - ICT ENGINE v6.0 ENTERPRISE
================================================

Motor de ejecución de órdenes para cuenta real MetaTrader 5.
Integrado con SmartTradingLogger y sistema de validación enterprise.

Características:
✅ Ejecución de órdenes real MT5
✅ Manejo robusto de errores
✅ Logging centralizado
✅ Validación previa de señales
✅ Rate limiting para protección

Autor: ICT Engine v6.0 Team
Fecha: 13 Septiembre 2025
"""

import time
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

try:
    from ..smart_trading_logger import SmartTradingLogger
    LOGGER_AVAILABLE = True
except ImportError:
    try:
        # Fallback: probar importación relativa desde 01-CORE
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from smart_trading_logger import SmartTradingLogger
        LOGGER_AVAILABLE = True
    except ImportError:
        LOGGER_AVAILABLE = False
        SmartTradingLogger = None

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    # Type check to ensure MT5 attributes are available
    _mt5_initialize = getattr(mt5, 'initialize', None)
    _mt5_last_error = getattr(mt5, 'last_error', None)
    _mt5_account_info = getattr(mt5, 'account_info', None)
    _mt5_order_send = getattr(mt5, 'order_send', None)
    _mt5_symbol_info = getattr(mt5, 'symbol_info', None)
    _mt5_shutdown = getattr(mt5, 'shutdown', None)
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None
    _mt5_initialize = None
    _mt5_last_error = None
    _mt5_account_info = None
    _mt5_order_send = None
    _mt5_symbol_info = None
    _mt5_shutdown = None

class OrderType(Enum):
    """Tipos de órdenes soportadas"""
    BUY = "buy"
    SELL = "sell"
    BUY_STOP = "buy_stop"
    SELL_STOP = "sell_stop"
    BUY_LIMIT = "buy_limit"
    SELL_LIMIT = "sell_limit"

class OrderStatus(Enum):
    """Estados de las órdenes"""
    PENDING = "pending"
    EXECUTED = "executed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    PARTIAL = "partial"

@dataclass
class TradingSignal:
    """Señal de trading para ejecución"""
    symbol: str
    order_type: OrderType
    volume: float
    price: float
    stop_loss: float
    take_profit: float
    comment: str
    magic_number: int = 12345
    confidence: float = 0.0

@dataclass
class OrderRequest:
    """Solicitud de orden de trading - Compatible con real_trading module"""
    symbol: str
    order_type: OrderType
    volume: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    comment: str = ""
    magic_number: int = 12345
    deviation: int = 20

@dataclass
class OrderResult:
    """Resultado de ejecución de orden - Compatible con real_trading module"""
    success: bool
    order_id: Optional[int] = None
    ticket: Optional[int] = None
    execution_price: Optional[float] = None
    execution_time_ms: float = 0.0
    error_code: Optional[int] = None
    error_message: str = ""
    slippage_pips: float = 0.0
    
class ExecutionResult:
    """Resultado de ejecución de orden"""
    def __init__(self, success: bool, order_id: Optional[int] = None, 
                 error: Optional[str] = None, details: Optional[Dict] = None):
        self.success = success
        self.order_id = order_id
        self.error = error
        self.details = details or {}
        self.timestamp = datetime.now()

class ExecutionEngine:
    """
    🔧 Motor de Ejecución Enterprise
    
    Ejecuta señales de trading validadas en cuenta real MT5
    con protección y logging avanzado.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializar motor de ejecución
        
        Args:
            config: Configuración del motor
        """
        self.config = config or self._default_config()
        
        # Configurar logger
        if LOGGER_AVAILABLE and SmartTradingLogger:
            self.logger = SmartTradingLogger("ExecutionEngine")
        else:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger("ExecutionEngine")
            
        # Estado del motor
        self.is_initialized = False
        self.is_active = False
        self.execution_count = 0
        self.last_execution = None
        
        # Rate limiting
        self.min_execution_interval = self.config.get('min_execution_interval', 5)
        
        # Estadísticas
        self.stats = {
            'total_orders': 0,
            'successful_orders': 0,
            'rejected_orders': 0,
            'avg_execution_time': 0.0
        }
        
        self._initialize_mt5()
        
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del motor"""
        return {
            'max_volume_per_order': 1.0,
            'max_orders_per_minute': 5,
            'enable_stop_loss': True,
            'enable_take_profit': True,
            'min_execution_interval': 5,  # segundos
            'retry_attempts': 3,
            'retry_delay': 1,  # segundos
            'validate_signals': True,
            'dry_run': False  # Para testing
        }
        
    def _initialize_mt5(self) -> bool:
        """Inicializar conexión MetaTrader 5"""
        if not MT5_AVAILABLE or not mt5:
            if LOGGER_AVAILABLE:
                self.logger.error("MetaTrader 5 no disponible", "ExecutionEngine")
            return False
            
        try:
            if MT5_AVAILABLE and mt5 and _mt5_initialize:
                if not _mt5_initialize():
                    if _mt5_last_error:
                        error = _mt5_last_error()
                        if LOGGER_AVAILABLE:
                            self.logger.error(f"Error inicializando MT5: {error}", "ExecutionEngine")
                    return False
                    
                # Verificar cuenta
                if _mt5_account_info:
                    account_info = _mt5_account_info()
                    if account_info is None:
                        if LOGGER_AVAILABLE:
                            self.logger.error("No se pudo obtener información de cuenta", "ExecutionEngine")
                        return False
                    
                    if LOGGER_AVAILABLE:
                        account_login = getattr(account_info, 'login', 'Unknown')
                        self.logger.info(f"✅ MT5 inicializado - Cuenta: {account_login}", "ExecutionEngine")
                        
            self.is_initialized = True
            return True
            
        except Exception as e:
            if LOGGER_AVAILABLE:
                self.logger.error(f"Error inicializando MT5: {e}", "ExecutionEngine")
            return False
            
    def activate(self) -> bool:
        """Activar el motor de ejecución"""
        if not self.is_initialized:
            if LOGGER_AVAILABLE:
                self.logger.error("Motor no inicializado", "ExecutionEngine")
            return False
            
        self.is_active = True
        if LOGGER_AVAILABLE:
            self.logger.info("🚀 Motor de ejecución ACTIVADO", "ExecutionEngine")
        return True
        
    def deactivate(self) -> bool:
        """Desactivar el motor de ejecución"""
        self.is_active = False
        if LOGGER_AVAILABLE:
            self.logger.info("⏹️ Motor de ejecución DESACTIVADO", "ExecutionEngine")
        return True
        
    def execute_signal(self, signal: TradingSignal) -> ExecutionResult:
        """
        Ejecutar señal de trading
        
        Args:
            signal: Señal de trading a ejecutar
            
        Returns:
            ExecutionResult: Resultado de la ejecución
        """
        start_time = time.time()
        
        # Verificaciones previas
        if not self.is_active:
            return ExecutionResult(False, error="Motor de ejecución no activo")
            
        if not self._validate_signal(signal):
            return ExecutionResult(False, error="Señal no válida")
            
        if not self._check_rate_limit():
            return ExecutionResult(False, error="Rate limit excedido")
            
        if self.config.get('dry_run', False):
            return self._simulate_execution(signal)
            
        try:
            # Preparar orden para MT5
            request = self._prepare_order_request(signal)
            
            if LOGGER_AVAILABLE:
                self.logger.info(f"📤 Ejecutando orden: {signal.symbol} {signal.order_type.value}", "ExecutionEngine")
                
            # Ejecutar orden
            if not _mt5_order_send:
                return ExecutionResult(False, error="MT5 order_send no disponible")
                
            result = _mt5_order_send(request)
            
            execution_time = time.time() - start_time
            trade_retcode_done = getattr(mt5, 'TRADE_RETCODE_DONE', 10009) if mt5 else 10009
            self._update_stats(execution_time, result.retcode == trade_retcode_done)
            
            if result.retcode == trade_retcode_done:
                if LOGGER_AVAILABLE:
                    self.logger.info(f"✅ Orden ejecutada: #{result.order} - Vol: {signal.volume}", "ExecutionEngine")
                    
                self.last_execution = datetime.now()
                return ExecutionResult(True, result.order, details={
                    'volume': result.volume,
                    'price': result.price,
                    'execution_time': execution_time
                })
            else:
                error_msg = f"Error ejecutando orden: {result.retcode} - {result.comment}"
                if LOGGER_AVAILABLE:
                    self.logger.error(error_msg, "ExecutionEngine")
                    
                return ExecutionResult(False, error=error_msg, details={
                    'retcode': result.retcode,
                    'comment': result.comment
                })
                
        except Exception as e:
            if LOGGER_AVAILABLE:
                self.logger.error(f"Excepción ejecutando orden: {e}", "ExecutionEngine")
            return ExecutionResult(False, error=str(e))
            
    def _validate_signal(self, signal: TradingSignal) -> bool:
        """Validar señal de trading"""
        try:
            # Verificaciones básicas
            if not signal.symbol or len(signal.symbol) < 3:
                return False
                
            if signal.volume <= 0 or signal.volume > self.config.get('max_volume_per_order', 1.0):
                return False
                
            if signal.price <= 0:
                return False
                
            # Verificar símbolo existe en MT5
            if MT5_AVAILABLE and _mt5_symbol_info:
                symbol_info = _mt5_symbol_info(signal.symbol)
                if symbol_info is None:
                    return False
                    
            return True
            
        except Exception as e:
            if LOGGER_AVAILABLE:
                self.logger.error(f"Error validando señal: {e}", "ExecutionEngine")
            return False
            
    def _check_rate_limit(self) -> bool:
        """Verificar rate limiting"""
        if self.last_execution is None:
            return True
            
        time_since_last = (datetime.now() - self.last_execution).total_seconds()
        return time_since_last >= self.min_execution_interval
        
    def _prepare_order_request(self, signal: TradingSignal) -> Dict:
        """Preparar request de orden para MT5"""
        if not MT5_AVAILABLE or not mt5:
            return {}
            
        action_map = {
            OrderType.BUY: mt5.TRADE_ACTION_DEAL,
            OrderType.SELL: mt5.TRADE_ACTION_DEAL,
            OrderType.BUY_STOP: mt5.TRADE_ACTION_PENDING,
            OrderType.SELL_STOP: mt5.TRADE_ACTION_PENDING,
            OrderType.BUY_LIMIT: mt5.TRADE_ACTION_PENDING,
            OrderType.SELL_LIMIT: mt5.TRADE_ACTION_PENDING
        }
        
        type_map = {
            OrderType.BUY: mt5.ORDER_TYPE_BUY,
            OrderType.SELL: mt5.ORDER_TYPE_SELL,
            OrderType.BUY_STOP: mt5.ORDER_TYPE_BUY_STOP,
            OrderType.SELL_STOP: mt5.ORDER_TYPE_SELL_STOP,
            OrderType.BUY_LIMIT: mt5.ORDER_TYPE_BUY_LIMIT,
            OrderType.SELL_LIMIT: mt5.ORDER_TYPE_SELL_LIMIT
        }
        
        request = {
            "action": action_map[signal.order_type],
            "symbol": signal.symbol,
            "volume": signal.volume,
            "type": type_map[signal.order_type],
            "price": signal.price,
            "magic": signal.magic_number,
            "comment": signal.comment[:31],  # MT5 limit
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Agregar SL/TP si están configurados
        if self.config.get('enable_stop_loss', True) and signal.stop_loss > 0:
            request["sl"] = signal.stop_loss
            
        if self.config.get('enable_take_profit', True) and signal.take_profit > 0:
            request["tp"] = signal.take_profit
            
        return request
        
    def _simulate_execution(self, signal: TradingSignal) -> ExecutionResult:
        """Simular ejecución para testing (dry run)"""
        if LOGGER_AVAILABLE:
            self.logger.info(f"🧪 SIMULACIÓN: {signal.symbol} {signal.order_type.value} {signal.volume}", "ExecutionEngine")
            
        # Simular delay de ejecución
        time.sleep(0.1)
        
        # Generar ID simulado
        import random
        fake_order_id = random.randint(100000, 999999)
        
        self.last_execution = datetime.now()
        self._update_stats(0.1, True)
        
        return ExecutionResult(True, fake_order_id, details={
            'simulated': True,
            'volume': signal.volume,
            'price': signal.price
        })
        
    def _update_stats(self, execution_time: float, success: bool):
        """Actualizar estadísticas de ejecución"""
        self.stats['total_orders'] += 1
        
        if success:
            self.stats['successful_orders'] += 1
        else:
            self.stats['rejected_orders'] += 1
            
        # Actualizar tiempo promedio de ejecución
        total_time = self.stats['avg_execution_time'] * (self.stats['total_orders'] - 1)
        self.stats['avg_execution_time'] = (total_time + execution_time) / self.stats['total_orders']
        
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del motor"""
        success_rate = 0.0
        if self.stats['total_orders'] > 0:
            success_rate = self.stats['successful_orders'] / self.stats['total_orders'] * 100
            
        return {
            **self.stats,
            'success_rate': success_rate,
            'is_active': self.is_active,
            'is_initialized': self.is_initialized,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None
        }
        
    def shutdown(self):
        """Cerrar motor de ejecución"""
        self.deactivate()
        
        if MT5_AVAILABLE and _mt5_shutdown:
            _mt5_shutdown()
            
        if LOGGER_AVAILABLE:
            self.logger.info("🔒 Motor de ejecución cerrado", "ExecutionEngine")

# Función de utilidad para crear motor de ejecución
def create_execution_engine(config: Optional[Dict] = None) -> ExecutionEngine:
    """Factory function para crear ExecutionEngine"""
    return ExecutionEngine(config)

# Función para crear señal de trading rápida
def create_trading_signal(symbol: str, order_type: str, volume: float, 
                         price: float, stop_loss: float = 0.0, 
                         take_profit: float = 0.0, comment: str = "ICT Signal") -> TradingSignal:
    """Crear señal de trading rápida"""
    return TradingSignal(
        symbol=symbol,
        order_type=OrderType(order_type.lower()),
        volume=volume,
        price=price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        comment=comment
    )