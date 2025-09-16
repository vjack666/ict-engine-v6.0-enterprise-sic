#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 ORDER BLOCKS BLACK BOX - ICT ENGINE v6.0 ENTERPRISE
=====================================================

Sistema de Order Blocks BlackBox optimizado para cuenta real con integración
de protocolos de logging central y enterprise features.

Bridge hacia el OrderBlocksBlackBox principal ubicado en order_blocks_logging.
Proporciona interfaz compatible con ict_engine module.

Características:
✅ Bridge hacia OrderBlocksBlackBox principal
✅ Logging centralizado con protocolos
✅ Optimizado para cuenta real
✅ Métricas enterprise
✅ Thread-safe operations

Autor: ICT Engine v6.0 Team
Fecha: 13 Septiembre 2025
"""

from protocols.unified_logging import get_unified_logger
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
import os

# Importar protocolos de logging central
try:
    from protocols import setup_module_logging, LogLevel
    _PROTOCOLS_AVAILABLE = True
    module_logger = setup_module_logging("OrderBlocksBridge", LogLevel.INFO)
except ImportError:
    _PROTOCOLS_AVAILABLE = False
    import logging
    logging.basicConfig(level=logging.INFO)
    module_logger = logging.getLogger("OrderBlocksBridge")

def _safe_log(level: str, message: str):
    """Logging seguro para el bridge Order Blocks"""
    try:
        if _PROTOCOLS_AVAILABLE:
            getattr(module_logger, level)(message, "OrderBlocksBridge")
        else:
            getattr(module_logger, level)(f"[OrderBlocksBridge] {message}")
    except Exception:
        print(f"[{level.upper()}] [OrderBlocksBridge] {message}")

# Importar OrderBlocksBlackBox principal
_ORDER_BLOCKS_BLACK_BOX_AVAILABLE = False
try:
    from order_blocks_logging.order_blocks_black_box import OrderBlocksBlackBox as _OrderBlocksBlackBoxMain
    _ORDER_BLOCKS_BLACK_BOX_AVAILABLE = True
    _safe_log("info", "✅ OrderBlocksBlackBox principal disponible")
except ImportError as e:
    _safe_log("warning", f"⚠️ OrderBlocksBlackBox principal no disponible: {e}")
    _OrderBlocksBlackBoxMain = None

class OrderBlocksBlackBox:
    """
    🔥 Bridge de Order Blocks BlackBox Enterprise
    
    Bridge hacia el OrderBlocksBlackBox principal con optimizaciones enterprise
    y integración de protocolos de logging centralizados.
    """
    
    def __init__(self, log_directory: Optional[str] = None):
        """
        Inicializar bridge de OrderBlocksBlackBox
        
        Args:
            log_directory: Directorio personalizado de logs
        """
        self.log_directory = log_directory
        self._main_black_box = None
        self._initialized = False
        
        # Inicializar componente principal si está disponible
        if _ORDER_BLOCKS_BLACK_BOX_AVAILABLE and _OrderBlocksBlackBoxMain:
            try:
                self._main_black_box = _OrderBlocksBlackBoxMain(log_directory)
                self._initialized = True
                _safe_log("info", "✅ OrderBlocksBlackBox bridge inicializado con componente principal")
            except Exception as e:
                _safe_log("error", f"❌ Error inicializando componente principal: {e}")
                self._initialize_fallback()
        else:
            self._initialize_fallback()
    
    def _initialize_fallback(self):
        """Inicializar sistema fallback"""
        _safe_log("info", "🔄 Inicializando sistema fallback OrderBlocksBlackBox")
        
        # Configurar directorio de logs fallback
        if not self.log_directory:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.log_directory = os.path.join(script_dir, "..", "..", "05-LOGS", "order_blocks")
        
        # Crear directorio si no existe
        os.makedirs(self.log_directory, exist_ok=True)
        
        # Métricas básicas
        self.session_metrics = {
            'session_start': datetime.now().isoformat(),
            'total_detections': 0,
            'total_validations': 0,
            'fallback_mode': True
        }
        
        self._initialized = True
        _safe_log("info", "✅ Sistema fallback OrderBlocksBlackBox inicializado")
    
    def log_detection(self, symbol: str, timeframe: str, input_data: Dict[str, Any], 
                     output_data: Dict[str, Any], execution_time_ms: float = 0) -> None:
        """
        Log de detección de Order Blocks
        
        Args:
            symbol: Símbolo del instrumento
            timeframe: Marco temporal
            input_data: Datos de entrada
            output_data: Resultados de detección
            execution_time_ms: Tiempo de ejecución en ms
        """
        if self._main_black_box and hasattr(self._main_black_box, 'log_detection'):
            try:
                self._main_black_box.log_detection(symbol, timeframe, input_data, 
                                                 output_data, execution_time_ms)
                _safe_log("debug", f"Detection logged: {symbol} {timeframe}")
            except Exception as e:
                _safe_log("error", f"Error logging detection: {e}")
                self._fallback_log("detection", symbol, timeframe, input_data, output_data)
        else:
            self._fallback_log("detection", symbol, timeframe, input_data, output_data)
    
    def log_validation(self, symbol: str, timeframe: str, live_data: Dict[str, Any], 
                      historical_data: Dict[str, Any], comparison_result: Dict[str, Any], 
                      execution_time_ms: float = 0) -> None:
        """
        Log de validación de Order Blocks
        
        Args:
            symbol: Símbolo del instrumento
            timeframe: Marco temporal
            live_data: Datos live de Order Blocks
            historical_data: Datos históricos
            comparison_result: Resultado de comparación
            execution_time_ms: Tiempo de ejecución en ms
        """
        if self._main_black_box and hasattr(self._main_black_box, 'log_validation'):
            try:
                self._main_black_box.log_validation(symbol, timeframe, live_data, 
                                                   historical_data, comparison_result, execution_time_ms)
                _safe_log("debug", f"Validation logged: {symbol} {timeframe}")
            except Exception as e:
                _safe_log("error", f"Error logging validation: {e}")
                self._fallback_log("validation", symbol, timeframe, 
                                 {'live_data': live_data, 'historical_data': historical_data}, 
                                 comparison_result)
        else:
            self._fallback_log("validation", symbol, timeframe, 
                             {'live_data': live_data, 'historical_data': historical_data}, 
                             comparison_result)
    
    def log_dashboard_update(self, component: str, update_type: str, data: Dict[str, Any], 
                           success: bool = True, error_msg: Optional[str] = None) -> None:
        """
        Log de actualización del dashboard
        
        Args:
            component: Componente del dashboard
            update_type: Tipo de actualización
            data: Datos de actualización
            success: Si la actualización fue exitosa
            error_msg: Mensaje de error si aplica
        """
        if self._main_black_box and hasattr(self._main_black_box, 'log_dashboard_update'):
            try:
                self._main_black_box.log_dashboard_update(component, update_type, data, success, error_msg)
                _safe_log("debug", f"Dashboard update logged: {component}")
            except Exception as e:
                _safe_log("error", f"Error logging dashboard update: {e}")
                self._fallback_log("dashboard", component, "", {}, data)
        else:
            self._fallback_log("dashboard", component, "", {}, data)
    
    def _fallback_log(self, log_type: str, symbol: str, timeframe: str, 
                     input_data: Dict[str, Any], output_data: Dict[str, Any]):
        """Sistema de logging fallback"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': log_type,
                'symbol': symbol,
                'timeframe': timeframe,
                'input_data': input_data,
                'output_data': output_data,
                'fallback_mode': True
            }
            
            # Log a archivo fallback
            log_directory = self.log_directory or os.path.join(os.getcwd(), "logs", "order_blocks")
            os.makedirs(log_directory, exist_ok=True)
            fallback_file = os.path.join(log_directory, f"order_blocks_fallback_{datetime.now().strftime('%Y-%m-%d')}.log")
            with open(fallback_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()}: {log_entry}\n")
            
            # Actualizar métricas
            if log_type == 'detection':
                self.session_metrics['total_detections'] += 1
            elif log_type == 'validation':
                self.session_metrics['total_validations'] += 1
            
            _safe_log("debug", f"Fallback log written: {log_type} for {symbol}")
            
        except Exception as e:
            _safe_log("error", f"Error in fallback logging: {e}")
    
    def get_session_metrics(self) -> Dict[str, Any]:
        """
        Obtener métricas de la sesión
        
        Returns:
            Dict con métricas de la sesión
        """
        if self._main_black_box and hasattr(self._main_black_box, 'session_metrics'):
            try:
                return self._main_black_box.session_metrics
            except Exception as e:
                _safe_log("error", f"Error getting main session metrics: {e}")
        
        return self.session_metrics.copy()
    
    def close_session(self):
        """Cerrar sesión de logging"""
        if self._main_black_box and hasattr(self._main_black_box, 'close'):
            try:
                self._main_black_box.close()
                _safe_log("info", "✅ Sesión principal cerrada")
            except Exception as e:
                _safe_log("error", f"Error closing main session: {e}")
        
        _safe_log("info", "🔥 OrderBlocksBlackBox bridge sesión cerrada")
    
    @property
    def is_initialized(self) -> bool:
        """Verificar si el bridge está inicializado"""
        return self._initialized
    
    @property
    def has_main_component(self) -> bool:
        """Verificar si el componente principal está disponible"""
        return self._main_black_box is not None

# Factory functions enterprise
def get_order_blocks_black_box(log_directory: Optional[str] = None) -> OrderBlocksBlackBox:
    """
    Factory function para obtener instancia de OrderBlocksBlackBox
    
    Args:
        log_directory: Directorio personalizado de logs
        
    Returns:
        OrderBlocksBlackBox: Instancia configurada
    """
    return OrderBlocksBlackBox(log_directory)

def create_enterprise_order_blocks_logger(config: Optional[Dict[str, Any]] = None) -> OrderBlocksBlackBox:
    """
    Crear logger enterprise para Order Blocks
    
    Args:
        config: Configuración personalizada
        
    Returns:
        OrderBlocksBlackBox: Logger enterprise configurado
    """
    log_directory = None
    if config and 'log_directory' in config:
        log_directory = config['log_directory']
    
    logger = OrderBlocksBlackBox(log_directory)
    _safe_log("info", "🚀 Enterprise Order Blocks logger creado")
    
    return logger

# Exports del módulo
__all__ = [
    'OrderBlocksBlackBox',
    'get_order_blocks_black_box', 
    'create_enterprise_order_blocks_logger'
]

# Inicialización del módulo
_safe_log("info", f"OrderBlocksBlackBox bridge inicializado - Principal disponible: {_ORDER_BLOCKS_BLACK_BOX_AVAILABLE}")