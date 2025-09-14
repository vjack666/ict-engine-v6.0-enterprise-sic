#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Order Blocks Black Box Logger v6.0 Enterprise
Sistema de logging especializado para Order Blocks detection y validation
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import threading
from dataclasses import dataclass, asdict

@dataclass
class OrderBlockEvent:
    """Estructura para eventos de Order Blocks"""
    timestamp: str
    component: str
    action: str
    symbol: str
    timeframe: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    performance: Dict[str, Any]
    level: str = "INFO"
    session_id: Optional[str] = None

class OrderBlocksBlackBox:
    """
    Caja Negra especializada para logging de Order Blocks
    Registra toda la actividad de detección, validación y dashboard
    """
    
    def __init__(self, log_directory: Optional[str] = None):
        self.log_directory = log_directory or self._get_default_log_directory()
        self.session_id = self._generate_session_id()
        self.lock = threading.Lock()
        
        # Configurar loggers especializados
        self.detection_logger = self._setup_logger("order_blocks_detection")
        self.validation_logger = self._setup_logger("order_blocks_validation")
        self.dashboard_logger = self._setup_logger("order_blocks_dashboard")
        
        # Métricas de sesión
        self.session_metrics = {
            'session_start': datetime.now(timezone.utc).isoformat(),
            'total_detections': 0,
            'total_validations': 0,
            'total_dashboard_updates': 0,
            'performance_metrics': []
        }
        
        print(f"🔥 [OrderBlocksBlackBox] Sistema de logging inicializado")
        print(f"   📂 Log Directory: {self.log_directory}")
        print(f"   🆔 Session ID: {self.session_id}")
    
    def _get_default_log_directory(self) -> str:
        """Obtiene directorio de logs por defecto"""
        script_dir = Path(__file__).parent.parent.parent
        return str(script_dir / "05-LOGS" / "order_blocks")
    
    def _generate_session_id(self) -> str:
        """Genera ID único de sesión"""
        return f"OB_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 100000}"
    
    def _setup_logger(self, logger_name: str) -> logging.Logger:
        """Configura logger especializado"""
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # Evitar duplicación de handlers
        if logger.handlers:
            return logger
        
        # Crear directorio si no existe
        os.makedirs(self.log_directory, exist_ok=True)
        
        # Archivo de log con fecha
        log_file = os.path.join(
            self.log_directory, 
            f"{logger_name}_{datetime.now().strftime('%Y-%m-%d')}.log"
        )
        
        # Handler de archivo con formato JSON
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter personalizado para JSON
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return logger
    
    def log_detection(self, symbol: str, timeframe: str, input_data: Dict[str, Any], 
                     output_data: Dict[str, Any], execution_time_ms: float = 0) -> None:
        """
        Log de detección de Order Blocks
        
        Args:
            symbol: Par de divisas (ej: 'EURUSD')
            timeframe: Timeframe analizado (ej: 'M15')
            input_data: Datos de entrada (barras, parámetros)
            output_data: Resultados (order blocks detectados)
            execution_time_ms: Tiempo de ejecución en milisegundos
        """
        event = OrderBlockEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            component="order_blocks_detector",
            action="detection_completed",
            symbol=symbol,
            timeframe=timeframe,
            input_data=input_data,
            output_data=output_data,
            performance={
                'execution_time_ms': round(execution_time_ms, 2),
                'session_id': self.session_id
            },
            session_id=self.session_id
        )
        
        self._write_event(self.detection_logger, event)
        
        with self.lock:
            self.session_metrics['total_detections'] += 1
            self.session_metrics['performance_metrics'].append({
                'component': 'detection',
                'execution_time_ms': execution_time_ms,
                'timestamp': event.timestamp
            })
    
    def log_validation(self, symbol: str, timeframe: str, live_data: Dict[str, Any],
                      historical_data: Dict[str, Any], comparison_result: Dict[str, Any],
                      execution_time_ms: float = 0) -> None:
        """
        Log de validación Order Blocks live vs histórico
        
        Args:
            symbol: Par de divisas
            timeframe: Timeframe
            live_data: Datos live de Order Blocks
            historical_data: Datos históricos
            comparison_result: Resultado de comparación
            execution_time_ms: Tiempo de ejecución
        """
        event = OrderBlockEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            component="order_blocks_validator",
            action="validation_completed",
            symbol=symbol,
            timeframe=timeframe,
            input_data={
                'live_data': live_data,
                'historical_data': historical_data
            },
            output_data={
                'comparison_result': comparison_result,
                'variance': comparison_result.get('signal_variance', 0),
                'accuracy_delta': comparison_result.get('accuracy_variance', 0)
            },
            performance={
                'execution_time_ms': round(execution_time_ms, 2),
                'session_id': self.session_id
            },
            session_id=self.session_id
        )
        
        self._write_event(self.validation_logger, event)
        
        with self.lock:
            self.session_metrics['total_validations'] += 1
    
    def log_dashboard_update(self, component: str, update_type: str, data: Dict[str, Any],
                           success: bool = True, error_msg: Optional[str] = None) -> None:
        """
        Log de actualizaciones del dashboard
        
        Args:
            component: Componente actualizado ('order_blocks_tab', 'metrics_panel', etc.)
            update_type: Tipo de actualización ('data_refresh', 'ui_update', etc.)
            data: Datos actualizados
            success: Si la actualización fue exitosa
            error_msg: Mensaje de error si aplica
        """
        event = OrderBlockEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            component="order_blocks_dashboard",
            action=f"{component}_{update_type}",
            symbol=data.get('symbol', 'N/A'),
            timeframe=data.get('timeframe', 'N/A'),
            input_data={
                'update_type': update_type,
                'component': component,
                'data_size': len(str(data)) if data else 0
            },
            output_data={
                'success': success,
                'error_message': error_msg,
                'updated_fields': list(data.keys()) if isinstance(data, dict) else []
            },
            performance={
                'session_id': self.session_id
            },
            level="ERROR" if not success else "INFO",
            session_id=self.session_id
        )
        
        self._write_event(self.dashboard_logger, event)
        
        with self.lock:
            self.session_metrics['total_dashboard_updates'] += 1
    
    def log_error(self, component: str, action: str, error: Exception, 
                  context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log de errores críticos
        
        Args:
            component: Componente donde ocurrió el error
            action: Acción que causó el error
            error: Excepción capturada
            context: Contexto adicional
        """
        event = OrderBlockEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            component=component,
            action=f"error_{action}",
            symbol=context.get('symbol', 'N/A') if context else 'N/A',
            timeframe=context.get('timeframe', 'N/A') if context else 'N/A',
            input_data=context or {},
            output_data={
                'error_type': type(error).__name__,
                'error_message': str(error),
                'error_traceback': str(error.__traceback__) if hasattr(error, '__traceback__') else None
            },
            performance={
                'session_id': self.session_id
            },
            level="ERROR",
            session_id=self.session_id
        )
        
        # Log a todos los loggers para errores críticos
        self._write_event(self.detection_logger, event)
        self._write_event(self.validation_logger, event)
        self._write_event(self.dashboard_logger, event)
    
    def _write_event(self, logger: logging.Logger, event: OrderBlockEvent) -> None:
        """Escribe evento al logger en formato JSON"""
        try:
            event_json = json.dumps(asdict(event), indent=None, ensure_ascii=False)
            logger.info(event_json)
        except Exception as e:
            # Fallback si falla serialización JSON
            logger.error(f"Error serializing event: {e} | Event: {event}")
    
    def get_session_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de la sesión actual"""
        with self.lock:
            return {
                **self.session_metrics,
                'session_duration_seconds': (
                    datetime.now(timezone.utc) - 
                    datetime.fromisoformat(self.session_metrics['session_start'])
                ).total_seconds()
            }
    
    def flush_logs(self) -> None:
        """Fuerza escritura de todos los logs pendientes"""
        for logger in [self.detection_logger, self.validation_logger, self.dashboard_logger]:
            for handler in logger.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()
    
    def close(self) -> None:
        """Cierra el sistema de logging"""
        self.flush_logs()
        
        # Log de sesión final
        final_metrics = self.get_session_metrics()
        self.log_dashboard_update(
            component="black_box_system",
            update_type="session_end",
            data=final_metrics,
            success=True
        )
        
        print(f"🔥 [OrderBlocksBlackBox] Sesión cerrada: {final_metrics['total_detections']} detecciones, {final_metrics['total_validations']} validaciones")


# Singleton global para uso en todo el sistema
_order_blocks_black_box_instance = None
_instance_lock = threading.Lock()

def get_order_blocks_black_box() -> OrderBlocksBlackBox:
    """Obtiene instancia singleton de OrderBlocksBlackBox"""
    global _order_blocks_black_box_instance
    
    if _order_blocks_black_box_instance is None:
        with _instance_lock:
            if _order_blocks_black_box_instance is None:
                _order_blocks_black_box_instance = OrderBlocksBlackBox()
    
    return _order_blocks_black_box_instance


# Funciones de conveniencia para uso rápido
def log_order_block_detection(symbol: str, timeframe: str, input_data: Dict[str, Any], 
                             output_data: Dict[str, Any], execution_time_ms: float = 0):
    """Función de conveniencia para log de detección"""
    get_order_blocks_black_box().log_detection(symbol, timeframe, input_data, output_data, execution_time_ms)

def log_order_block_validation(symbol: str, timeframe: str, live_data: Dict[str, Any],
                              historical_data: Dict[str, Any], comparison_result: Dict[str, Any],
                              execution_time_ms: float = 0):
    """Función de conveniencia para log de validación"""
    get_order_blocks_black_box().log_validation(symbol, timeframe, live_data, historical_data, comparison_result, execution_time_ms)

def log_order_block_dashboard_update(component: str, update_type: str, data: Dict[str, Any],
                                   success: bool = True, error_msg: Optional[str] = None):
    """Función de conveniencia para log de dashboard"""
    get_order_blocks_black_box().log_dashboard_update(component, update_type, data, success, error_msg)

def log_order_block_error(component: str, action: str, error: Exception, 
                         context: Optional[Dict[str, Any]] = None):
    """Función de conveniencia para log de errores"""
    get_order_blocks_black_box().log_error(component, action, error, context)


if __name__ == "__main__":
    # Test del sistema de logging
    print("🧪 Testeando OrderBlocksBlackBox...")
    
    black_box = OrderBlocksBlackBox()
    
    # Test detection log
    black_box.log_detection(
        symbol="EURUSD",
        timeframe="M15",
        input_data={"bars_analyzed": 500, "parameters": {"min_size": 20}},
        output_data={"order_blocks_detected": 3, "bullish": 1, "bearish": 2, "confidence_avg": 0.75},
        execution_time_ms=150.5
    )
    
    # Test validation log
    black_box.log_validation(
        symbol="EURUSD",
        timeframe="M15",
        live_data={"total_signals": 3},
        historical_data={"total_signals": 15},
        comparison_result={"signal_variance": -12, "accuracy_variance": -5.2},
        execution_time_ms=75.3
    )
    
    # Test dashboard log
    black_box.log_dashboard_update(
        component="order_blocks_tab",
        update_type="data_refresh",
        data={"symbol": "EURUSD", "timeframe": "M15", "new_blocks": 2}
    )
    
    # Mostrar métricas
    metrics = black_box.get_session_metrics()
    print(f"📊 Métricas de sesión: {json.dumps(metrics, indent=2)}")
    
    black_box.close()
    print("✅ Test completado exitosamente")