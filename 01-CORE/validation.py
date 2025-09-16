#!/usr/bin/env python3
"""
🛡️ VALIDATION MODULE - ICT ENGINE v6.0 ENTERPRISE
================================================

Módulo de validación centralizada para operaciones de trading en producción.
Valida datos, configuraciones, operaciones y condiciones del mercado antes
de ejecutar cualquier acción crítica.

Características principales:
✅ Validación multi-nivel (Basic, Advanced, Critical)
✅ Validación de integridad de datos de mercado
✅ Validación de operaciones de trading
✅ Validación de configuraciones
✅ Validación de recursos del sistema
✅ Thread-safe y optimizado para producción

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 16 Septiembre 2025
"""

from protocols.unified_logging import get_unified_logger
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import threading
import time
import logging


class ValidationLevel(Enum):
    """Niveles de validación disponibles"""
    BASIC = "basic"           # Validaciones básicas rápidas
    ADVANCED = "advanced"     # Validaciones detalladas
    CRITICAL = "critical"     # Validaciones exhaustivas para operaciones críticas


class ValidationResult:
    """Resultado de una validación"""
    
    def __init__(self, success: bool, message: str = "", details: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def __bool__(self) -> bool:
        return self.success
    
    def __str__(self) -> str:
        status = "✅ VALID" if self.success else "❌ INVALID"
        return f"{status}: {self.message}"


@dataclass
class MarketDataPoint:
    """Punto de datos del mercado para validación"""
    symbol: str
    timestamp: datetime
    bid: float
    ask: float
    volume: int = 0
    spread: float = 0.0


class ProductionValidator:
    """
    🛡️ Validador principal para operaciones de producción
    
    Centraliza todas las validaciones críticas del sistema para
    garantizar la integridad y seguridad de las operaciones.
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.ADVANCED):
        self.validation_level = validation_level
        self.logger = get_unified_logger("ProductionValidator")
        self._lock = threading.RLock()
        
        # Límites de validación
        self.max_spread_percent = 0.5  # 0.5% spread máximo
        self.max_data_age_seconds = 30  # Datos más antiguos de 30s son inválidos
        self.min_volume_threshold = 100  # Volumen mínimo aceptable
        
        # Contadores de validación
        self._validation_stats: Dict[str, Union[int, float]] = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'market_data_validations': 0,
            'trading_operations_validations': 0,
            'system_validations': 0
        }
        
        self.logger.info(f"✅ ProductionValidator initialized with level: {validation_level.value}")
    
    def validate_market_data(self, data_point: MarketDataPoint) -> ValidationResult:
        """
        📊 Validar datos de mercado
        
        Args:
            data_point: Punto de datos del mercado
            
        Returns:
            ValidationResult con el resultado de la validación
        """
        try:
            with self._lock:
                self._validation_stats['total_validations'] += 1
                self._validation_stats['market_data_validations'] += 1
                
                # Validación básica
                if not data_point.symbol:
                    return self._fail_validation("Symbol is required")
                
                if data_point.bid <= 0 or data_point.ask <= 0:
                    return self._fail_validation(f"Invalid prices: bid={data_point.bid}, ask={data_point.ask}")
                
                if data_point.ask <= data_point.bid:
                    return self._fail_validation(f"Ask ({data_point.ask}) must be greater than bid ({data_point.bid})")
                
                # Validación de spread
                spread_percent = ((data_point.ask - data_point.bid) / data_point.bid) * 100
                if spread_percent > self.max_spread_percent:
                    return self._fail_validation(f"Spread too wide: {spread_percent:.4f}% > {self.max_spread_percent}%")
                
                # Validación de timestamp (solo para ADVANCED y CRITICAL)
                if self.validation_level in [ValidationLevel.ADVANCED, ValidationLevel.CRITICAL]:
                    data_age = (datetime.now() - data_point.timestamp).total_seconds()
                    if data_age > self.max_data_age_seconds:
                        return self._fail_validation(f"Data too old: {data_age:.1f}s > {self.max_data_age_seconds}s")
                
                # Validación de volumen (solo para CRITICAL)
                if self.validation_level == ValidationLevel.CRITICAL:
                    if data_point.volume > 0 and data_point.volume < self.min_volume_threshold:
                        return self._fail_validation(f"Volume too low: {data_point.volume} < {self.min_volume_threshold}")
                
                return self._success_validation(f"Market data valid for {data_point.symbol}")
                
        except Exception as e:
            self.logger.error(f"Error validating market data: {e}")
            return self._fail_validation(f"Validation error: {str(e)}")
    
    def validate_trading_operation(self, operation_data: Dict[str, Any]) -> ValidationResult:
        """
        💼 Validar operación de trading
        
        Args:
            operation_data: Datos de la operación
            
        Returns:
            ValidationResult con el resultado
        """
        try:
            with self._lock:
                self._validation_stats['total_validations'] += 1
                self._validation_stats['trading_operations_validations'] += 1
                
                # Campos requeridos
                required_fields = ['symbol', 'action', 'volume', 'price']
                for field in required_fields:
                    if field not in operation_data:
                        return self._fail_validation(f"Required field missing: {field}")
                    
                    if operation_data[field] is None:
                        return self._fail_validation(f"Required field is None: {field}")
                
                # Validar acción
                valid_actions = ['BUY', 'SELL', 'BUY_LIMIT', 'SELL_LIMIT', 'BUY_STOP', 'SELL_STOP']
                if operation_data['action'] not in valid_actions:
                    return self._fail_validation(f"Invalid action: {operation_data['action']}")
                
                # Validar volumen
                volume = operation_data['volume']
                if not isinstance(volume, (int, float)) or volume <= 0:
                    return self._fail_validation(f"Invalid volume: {volume}")
                
                if volume > 10.0:  # Máximo 10 lotes para seguridad
                    return self._fail_validation(f"Volume too high: {volume} > 10.0")
                
                # Validar precio
                price = operation_data['price']
                if not isinstance(price, (int, float)) or price <= 0:
                    return self._fail_validation(f"Invalid price: {price}")
                
                # Validaciones avanzadas
                if self.validation_level in [ValidationLevel.ADVANCED, ValidationLevel.CRITICAL]:
                    # Validar stop loss y take profit si existen
                    if 'stop_loss' in operation_data and operation_data['stop_loss'] is not None:
                        sl = operation_data['stop_loss']
                        if not isinstance(sl, (int, float)) or sl <= 0:
                            return self._fail_validation(f"Invalid stop_loss: {sl}")
                    
                    if 'take_profit' in operation_data and operation_data['take_profit'] is not None:
                        tp = operation_data['take_profit']
                        if not isinstance(tp, (int, float)) or tp <= 0:
                            return self._fail_validation(f"Invalid take_profit: {tp}")
                
                return self._success_validation(f"Trading operation valid for {operation_data['symbol']}")
                
        except Exception as e:
            self.logger.error(f"Error validating trading operation: {e}")
            return self._fail_validation(f"Validation error: {str(e)}")
    
    def validate_system_resources(self) -> ValidationResult:
        """
        💻 Validar recursos del sistema
        
        Returns:
            ValidationResult con el estado de los recursos
        """
        try:
            with self._lock:
                self._validation_stats['total_validations'] += 1
                self._validation_stats['system_validations'] += 1
                
                import psutil
                
                # Validar memoria
                memory = psutil.virtual_memory()
                if memory.percent > 85:  # Más de 85% de uso de memoria
                    return self._fail_validation(f"High memory usage: {memory.percent:.1f}%")
                
                # Validar CPU (solo para ADVANCED y CRITICAL)
                if self.validation_level in [ValidationLevel.ADVANCED, ValidationLevel.CRITICAL]:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    if cpu_percent > 80:  # Más de 80% de uso de CPU
                        return self._fail_validation(f"High CPU usage: {cpu_percent:.1f}%")
                
                # Validar disco (solo para CRITICAL)
                if self.validation_level == ValidationLevel.CRITICAL:
                    disk = psutil.disk_usage('/')
                    if disk.percent > 90:  # Más de 90% de uso de disco
                        return self._fail_validation(f"High disk usage: {disk.percent:.1f}%")
                
                return self._success_validation("System resources are healthy")
                
        except ImportError:
            # psutil no disponible, skip validación
            self.logger.warning("psutil not available, skipping system resource validation")
            return self._success_validation("System resource validation skipped")
        except Exception as e:
            self.logger.error(f"Error validating system resources: {e}")
            return self._fail_validation(f"System validation error: {str(e)}")
    
    def validate_configuration(self, config: Dict[str, Any]) -> ValidationResult:
        """
        ⚙️ Validar configuración del sistema
        
        Args:
            config: Diccionario de configuración
            
        Returns:
            ValidationResult con el resultado
        """
        try:
            with self._lock:
                self._validation_stats['total_validations'] += 1
                
                # Validar campos críticos de trading
                if 'trading' in config:
                    trading_config = config['trading']
                    
                    # Max positions
                    if 'max_positions' in trading_config:
                        max_pos = trading_config['max_positions']
                        if not isinstance(max_pos, int) or max_pos < 1 or max_pos > 50:
                            return self._fail_validation(f"Invalid max_positions: {max_pos}")
                    
                    # Risk per trade
                    if 'risk_per_trade' in trading_config:
                        risk = trading_config['risk_per_trade']
                        if not isinstance(risk, (int, float)) or risk <= 0 or risk > 0.1:
                            return self._fail_validation(f"Invalid risk_per_trade: {risk}")
                
                # Validar configuración MT5
                if 'mt5' in config:
                    mt5_config = config['mt5']
                    
                    if 'connection' in mt5_config:
                        conn = mt5_config['connection']
                        if 'timeout' in conn:
                            timeout = conn['timeout']
                            if not isinstance(timeout, int) or timeout < 1000 or timeout > 60000:
                                return self._fail_validation(f"Invalid MT5 timeout: {timeout}")
                
                return self._success_validation("Configuration is valid")
                
        except Exception as e:
            self.logger.error(f"Error validating configuration: {e}")
            return self._fail_validation(f"Configuration validation error: {str(e)}")
    
    def get_validation_stats(self) -> Dict[str, Union[int, float]]:
        """📊 Obtener estadísticas de validación"""
        with self._lock:
            stats = self._validation_stats.copy()
            
            if stats['total_validations'] > 0:
                stats['success_rate'] = (stats['successful_validations'] / stats['total_validations']) * 100
            else:
                stats['success_rate'] = 0.0
                
            return stats
    
    def reset_stats(self) -> None:
        """🔄 Resetear estadísticas"""
        with self._lock:
            for key in self._validation_stats:
                if key != 'success_rate':
                    self._validation_stats[key] = 0
                else:
                    self._validation_stats[key] = 0.0
            self.logger.info("Validation statistics reset")
    
    def _success_validation(self, message: str) -> ValidationResult:
        """✅ Crear resultado exitoso"""
        self._validation_stats['successful_validations'] += 1
        return ValidationResult(True, message)
    
    def _fail_validation(self, message: str) -> ValidationResult:
        """❌ Crear resultado fallido"""
        self._validation_stats['failed_validations'] += 1
        self.logger.warning(f"Validation failed: {message}")
        return ValidationResult(False, message)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

_global_validator: Optional[ProductionValidator] = None
_validator_lock = threading.Lock()


def get_production_validator(level: ValidationLevel = ValidationLevel.ADVANCED, 
                           force_new: bool = False) -> ProductionValidator:
    """
    🏭 Factory function para obtener validador de producción
    
    Args:
        level: Nivel de validación deseado
        force_new: Forzar nueva instancia
        
    Returns:
        Instancia de ProductionValidator
    """
    global _global_validator
    
    with _validator_lock:
        if _global_validator is None or force_new:
            _global_validator = ProductionValidator(level)
        
        return _global_validator


def validate_market_data(data_point: MarketDataPoint) -> ValidationResult:
    """🎯 Función de conveniencia para validar datos de mercado"""
    return get_production_validator().validate_market_data(data_point)


def validate_trading_operation(operation_data: Dict[str, Any]) -> ValidationResult:
    """🎯 Función de conveniencia para validar operación de trading"""
    return get_production_validator().validate_trading_operation(operation_data)


def validate_system_health() -> ValidationResult:
    """🎯 Función de conveniencia para validar salud del sistema"""
    return get_production_validator().validate_system_resources()


def test_validation_module():
    """🧪 Test del módulo de validación"""
    print("🧪 Testing validation module...")
    
    try:
        # Test inicialización
        validator = get_production_validator(ValidationLevel.CRITICAL)
        print("✅ Validator initialized")
        
        # Test validación de datos de mercado
        market_data = MarketDataPoint(
            symbol="EURUSD",
            timestamp=datetime.now(),
            bid=1.0500,
            ask=1.0502,
            volume=1000
        )
        
        result = validator.validate_market_data(market_data)
        assert result.success, f"Market data validation failed: {result.message}"
        print("✅ Market data validation passed")
        
        # Test validación de operación de trading
        trading_op = {
            'symbol': 'EURUSD',
            'action': 'BUY',
            'volume': 0.1,
            'price': 1.0502,
            'stop_loss': 1.0480,
            'take_profit': 1.0530
        }
        
        result = validator.validate_trading_operation(trading_op)
        assert result.success, f"Trading operation validation failed: {result.message}"
        print("✅ Trading operation validation passed")
        
        # Test validación de recursos del sistema
        result = validator.validate_system_resources()
        print(f"✅ System resources validation: {result}")
        
        # Test estadísticas
        stats = validator.get_validation_stats()
        print(f"📊 Validation stats: {stats}")
        
        print("🎉 Validation module test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Validation module test failed: {e}")
        return False


if __name__ == "__main__":
    test_validation_module()