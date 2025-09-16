#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 POSITION SIZING CALCULATOR - ICT ENGINE v6.0 ENTERPRISE
===========================================================

Calculadora avanzada de tamaño de posición para cuenta real.
Integrado con SmartTradingLogger y sistema de riesgo enterprise.

Características:
✅ Cálculo preciso de tamaño de posición
✅ Múltiples métodos de riesgo
✅ Protección de capital avanzada
✅ Logging centralizado
✅ Validación de parámetros

Autor: ICT Engine v6.0 Team
Fecha: 13 Septiembre 2025
"""

from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import math

# Importar protocolos de logging central
try:
    from ..protocols import setup_module_logging, LogLevel, EnterpriseLoggerProtocol
    PROTOCOLS_AVAILABLE = True
except ImportError:
    PROTOCOLS_AVAILABLE = False
    setup_module_logging = None
    LogLevel = None

# Importar logging estándar
import logging

# Fallback tradicional
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
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None

class RiskMethod(Enum):
    """Métodos de cálculo de riesgo"""
    FIXED_AMOUNT = "fixed_amount"  # Cantidad fija en dinero
    FIXED_PERCENT = "fixed_percent"  # Porcentaje fijo del capital
    ATR_BASED = "atr_based"  # Basado en ATR
    VOLATILITY_ADJUSTED = "volatility_adjusted"  # Ajustado por volatilidad
    KELLY_CRITERION = "kelly_criterion"  # Criterio de Kelly

class RiskLevel(Enum):
    """Niveles de riesgo predefinidos"""
    CONSERVATIVE = "conservative"  # 0.5%
    MODERATE = "moderate"  # 1.0%
    AGGRESSIVE = "aggressive"  # 2.0%
    HIGH_RISK = "high_risk"  # 5.0%

@dataclass
class PositionSizingParameters:
    """Parámetros para cálculo de posición"""
    symbol: str
    account_balance: float
    risk_percent: float
    entry_price: float
    stop_loss: float
    risk_method: RiskMethod = RiskMethod.FIXED_PERCENT
    max_position_size: float = 10.0  # Lots máximos
    min_position_size: float = 0.01  # Lots mínimos

@dataclass 
class PositionSizingResult:
    """Resultado del cálculo de posición"""
    lots: float
    risk_amount: float
    position_value: float
    risk_reward_ratio: float
    is_valid: bool
    validation_message: str
    confidence_score: float = 1.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class PositionSizingCalculator:
    """
    💰 Calculadora Enterprise de Tamaño de Posición
    
    Calcula el tamaño óptimo de posición considerando:
    - Riesgo definido por el usuario
    - Condiciones de mercado
    - Límites de la cuenta
    - Volatilidad del activo
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializar calculadora de posición
        
        Args:
            config: Configuración de la calculadora
        """
        self.config = config or self._default_config()
        
        # Configurar logger usando protocolos centrales
        if PROTOCOLS_AVAILABLE and setup_module_logging and LogLevel:
            self.logger = setup_module_logging("PositionSizing", LogLevel.INFO)
        elif LOGGER_AVAILABLE and get_unified_logger is not None:
            self.logger = get_unified_logger("PositionSizing")
        else:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger("PositionSizing")
            
        # Cache para información de símbolos
        self._symbol_cache = {}
        
        # Estadísticas
        self.stats = {
            'calculations_performed': 0,
            'valid_calculations': 0,
            'invalid_calculations': 0,
            'avg_position_size': 0.0,
            'avg_risk_amount': 0.0
        }
        
        # Usar protocolo de logging si está disponible
        def _log_info(message: str):
            self._safe_log("info", message)
        
        def _log_warning(message: str):
            self._safe_log("warning", message)
        
        def _log_error(message: str):
            self._safe_log("error", message)
        
        _log_info("💰 PositionSizingCalculator inicializado")
    
    def _safe_log(self, level: str, message: str):
        """Método seguro para logging con fallbacks"""
        try:
            if PROTOCOLS_AVAILABLE and setup_module_logging and LogLevel:
                getattr(self.logger, level)(message, "PositionSizing")
            elif LOGGER_AVAILABLE and hasattr(self.logger, level):
                try:
                    # Probar con 2 parámetros (SmartTradingLogger)
                    getattr(self.logger, level)(message, "PositionSizing")
                except TypeError:
                    # Fallback a 1 parámetro (logging estándar)
                    getattr(self.logger, level)(f"[PositionSizing] {message}")
            else:
                print(f"[{level.upper()}] [PositionSizing] {message}")
        except Exception:
            print(f"[{level.upper()}] [PositionSizing] {message}")
            
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'max_risk_per_trade': 2.0,  # 2% máximo
            'min_risk_per_trade': 0.1,  # 0.1% mínimo
            'max_position_size': 10.0,  # 10 lots máximo
            'min_position_size': 0.01,  # 0.01 lots mínimo
            'currency_conversion': True,
            'use_symbol_cache': True,
            'cache_expiry_seconds': 300,  # 5 minutos
            'risk_levels': {
                RiskLevel.CONSERVATIVE: 0.5,
                RiskLevel.MODERATE: 1.0,
                RiskLevel.AGGRESSIVE: 2.0,
                RiskLevel.HIGH_RISK: 5.0
            }
        }
    
    def calculate_position_size(self, params: PositionSizingParameters) -> PositionSizingResult:
        """
        Calcular tamaño de posición óptimo
        
        Args:
            params: Parámetros para el cálculo
            
        Returns:
            PositionSizingResult: Resultado del cálculo
        """
        self.stats['calculations_performed'] += 1
        
        try:
            # Validar parámetros
            validation_result = self._validate_parameters(params)
            if not validation_result['is_valid']:
                self.stats['invalid_calculations'] += 1
                return PositionSizingResult(
                    lots=0.0,
                    risk_amount=0.0,
                    position_value=0.0,
                    risk_reward_ratio=0.0,
                    is_valid=False,
                    validation_message=validation_result['message'],
                    confidence_score=0.0
                )
            
            # Obtener información del símbolo
            symbol_info = self._get_symbol_info(params.symbol)
            
            # Calcular riesgo en dinero
            risk_amount = self._calculate_risk_amount(params)
            
            # Calcular distancia de stop loss en pips
            pip_value = self._get_pip_value(params.symbol, symbol_info)
            stop_distance_pips = abs(params.entry_price - params.stop_loss) / pip_value
            
            # Calcular valor por pip para el tamaño mínimo
            pip_value_per_lot = self._get_pip_value_per_lot(params.symbol, symbol_info)
            
            # Calcular tamaño de posición
            if stop_distance_pips > 0 and pip_value_per_lot > 0:
                lots = risk_amount / (stop_distance_pips * pip_value_per_lot)
            else:
                lots = 0.0
                
            # Aplicar límites de posición
            lots = self._apply_position_limits(lots, params)
            
            # Calcular métricas adicionales
            position_value = lots * params.entry_price * symbol_info.get('contract_size', 100000)
            actual_risk = lots * stop_distance_pips * pip_value_per_lot
            
            # Calcular confidence score
            confidence = self._calculate_confidence_score(params, lots, actual_risk)
            
            # Validar resultado final
            is_valid = lots > 0 and lots >= params.min_position_size
            
            result = PositionSizingResult(
                lots=round(lots, 2),
                risk_amount=actual_risk,
                position_value=position_value,
                risk_reward_ratio=self._calculate_risk_reward_ratio(params),
                is_valid=is_valid,
                validation_message="Cálculo exitoso" if is_valid else "Posición muy pequeña",
                confidence_score=confidence,
                metadata={
                    'method': params.risk_method.value,
                    'stop_distance_pips': stop_distance_pips,
                    'pip_value_per_lot': pip_value_per_lot,
                    'symbol_info': symbol_info
                }
            )
            
            # Actualizar estadísticas
            if is_valid:
                self.stats['valid_calculations'] += 1
                self._update_stats(lots, actual_risk)
            else:
                self.stats['invalid_calculations'] += 1
                
            if LOGGER_AVAILABLE:
                self.logger.info(
                    f"💰 Posición calculada: {params.symbol} - {lots} lots (${actual_risk:.2f} riesgo)",
                    "PositionSizing"
                )
                
            return result
            
        except Exception as e:
            self.stats['invalid_calculations'] += 1
            if LOGGER_AVAILABLE:
                self.logger.error(f"Error calculando posición: {e}", "PositionSizing")
                
            return PositionSizingResult(
                lots=0.0,
                risk_amount=0.0,
                position_value=0.0,
                risk_reward_ratio=0.0,
                is_valid=False,
                validation_message=f"Error en cálculo: {str(e)}",
                confidence_score=0.0
            )
    
    def calculate_by_risk_level(self, symbol: str, account_balance: float, 
                               entry_price: float, stop_loss: float,
                               risk_level: RiskLevel) -> PositionSizingResult:
        """
        Calcular posición usando nivel de riesgo predefinido
        
        Args:
            symbol: Símbolo del activo
            account_balance: Balance de la cuenta
            entry_price: Precio de entrada
            stop_loss: Precio de stop loss
            risk_level: Nivel de riesgo predefinido
            
        Returns:
            PositionSizingResult: Resultado del cálculo
        """
        risk_percent = self.config['risk_levels'][risk_level]
        
        params = PositionSizingParameters(
            symbol=symbol,
            account_balance=account_balance,
            risk_percent=risk_percent,
            entry_price=entry_price,
            stop_loss=stop_loss,
            risk_method=RiskMethod.FIXED_PERCENT
        )
        
        return self.calculate_position_size(params)
    
    def _validate_parameters(self, params: PositionSizingParameters) -> Dict[str, Any]:
        """Validar parámetros de entrada"""
        if params.account_balance <= 0:
            return {'is_valid': False, 'message': 'Balance de cuenta debe ser positivo'}
            
        if params.risk_percent <= 0:
            return {'is_valid': False, 'message': 'Porcentaje de riesgo debe ser positivo'}
            
        if params.risk_percent > self.config.get('max_risk_per_trade', 2.0):
            return {'is_valid': False, 'message': f'Riesgo excede máximo permitido ({self.config["max_risk_per_trade"]}%)'}
            
        if params.entry_price <= 0:
            return {'is_valid': False, 'message': 'Precio de entrada debe ser positivo'}
            
        if params.stop_loss <= 0:
            return {'is_valid': False, 'message': 'Stop loss debe ser positivo'}
            
        if params.entry_price == params.stop_loss:
            return {'is_valid': False, 'message': 'Precio de entrada y stop loss no pueden ser iguales'}
            
        return {'is_valid': True, 'message': 'Parámetros válidos'}
    
    def _calculate_risk_amount(self, params: PositionSizingParameters) -> float:
        """Calcular cantidad de riesgo en dinero"""
        if params.risk_method == RiskMethod.FIXED_AMOUNT:
            return min(params.risk_percent, params.account_balance * 0.1)  # Max 10% if using fixed amount
        elif params.risk_method == RiskMethod.FIXED_PERCENT:
            return params.account_balance * (params.risk_percent / 100.0)
        else:
            # Para métodos más complejos, usar porcentaje por defecto
            return params.account_balance * (params.risk_percent / 100.0)
    
    def _get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Obtener información del símbolo"""
        # Verificar cache primero
        if (self.config.get('use_symbol_cache', True) and 
            symbol in self._symbol_cache):
            
            cache_entry = self._symbol_cache[symbol]
            if (datetime.now() - cache_entry['timestamp']).seconds < self.config.get('cache_expiry_seconds', 300):
                return cache_entry['data']
        
        # Obtener de MT5 si está disponible
        if MT5_AVAILABLE and mt5:
            try:
                # Usar getattr para evitar error de Pylance
                symbol_info_func = getattr(mt5, 'symbol_info', None)
                if symbol_info_func:
                    symbol_info = symbol_info_func(symbol)
                    if symbol_info is not None:
                        info_dict = {
                            'point': symbol_info.point,
                            'digits': symbol_info.digits,
                            'contract_size': symbol_info.trade_contract_size,
                            'currency_base': symbol_info.currency_base,
                            'currency_profit': symbol_info.currency_profit,
                            'currency_margin': symbol_info.currency_margin
                        }
                        
                        # Guardar en cache
                        if self.config.get('use_symbol_cache', True):
                            self._symbol_cache[symbol] = {
                                'data': info_dict,
                                'timestamp': datetime.now()
                            }
                        
                        return info_dict
            except Exception as e:
                if LOGGER_AVAILABLE:
                    self._safe_log("warning", f"No se pudo obtener info de símbolo {symbol}: {e}")
        
        # Valores por defecto para pares forex comunes
        defaults = {
            'point': 0.00001 if 'JPY' not in symbol else 0.001,
            'digits': 5 if 'JPY' not in symbol else 3,
            'contract_size': 100000,
            'currency_base': symbol[:3] if len(symbol) >= 6 else 'USD',
            'currency_profit': 'USD',
            'currency_margin': 'USD'
        }
        
        return defaults
    
    def _get_pip_value(self, symbol: str, symbol_info: Dict[str, Any]) -> float:
        """Obtener valor de un pip para el símbolo"""
        point = symbol_info.get('point', 0.00001)
        if 'JPY' in symbol:
            return point * 100  # Para pares JPY, pip = 100 points
        else:
            return point * 10   # Para otros pares, pip = 10 points
    
    def _get_pip_value_per_lot(self, symbol: str, symbol_info: Dict[str, Any]) -> float:
        """Obtener valor monetario de un pip por lot"""
        pip_value = self._get_pip_value(symbol, symbol_info)
        contract_size = symbol_info.get('contract_size', 100000)
        
        # Para simplificar, asumimos conversión 1:1 a USD
        # En implementación real, se haría conversión de moneda
        return pip_value * contract_size
    
    def _apply_position_limits(self, lots: float, params: PositionSizingParameters) -> float:
        """Aplicar límites de posición"""
        # Límite mínimo
        lots = max(lots, params.min_position_size)
        
        # Límite máximo
        lots = min(lots, params.max_position_size)
        
        # Límites de configuración
        lots = min(lots, self.config.get('max_position_size', 10.0))
        lots = max(lots, self.config.get('min_position_size', 0.01))
        
        return lots
    
    def _calculate_risk_reward_ratio(self, params: PositionSizingParameters) -> float:
        """Calcular ratio riesgo-beneficio"""
        try:
            risk_distance = abs(params.entry_price - params.stop_loss)
            if risk_distance > 0:
                # Asumiendo take profit de 1:2 por defecto si no se proporciona
                reward_distance = risk_distance * 2
                return reward_distance / risk_distance
            return 0.0
        except:
            return 0.0
    
    def _calculate_confidence_score(self, params: PositionSizingParameters, 
                                  lots: float, actual_risk: float) -> float:
        """Calcular score de confianza del cálculo"""
        score = 1.0
        
        # Reducir confianza si el riesgo es muy alto
        risk_ratio = actual_risk / params.account_balance
        if risk_ratio > 0.02:  # Más de 2%
            score *= 0.8
        
        # Reducir confianza si la posición es muy grande
        if lots > 5.0:
            score *= 0.9
        
        # Reducir confianza si los parámetros son límite
        if params.risk_percent > 1.5:
            score *= 0.85
            
        return max(0.1, score)  # Mínimo 10% de confianza
    
    def _update_stats(self, lots: float, risk_amount: float):
        """Actualizar estadísticas"""
        valid_count = self.stats['valid_calculations']
        
        # Actualizar promedio de tamaño de posición
        current_avg_size = self.stats['avg_position_size']
        self.stats['avg_position_size'] = ((current_avg_size * (valid_count - 1)) + lots) / valid_count
        
        # Actualizar promedio de riesgo
        current_avg_risk = self.stats['avg_risk_amount']
        self.stats['avg_risk_amount'] = ((current_avg_risk * (valid_count - 1)) + risk_amount) / valid_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la calculadora"""
        total_calcs = self.stats['calculations_performed']
        success_rate = 0.0
        if total_calcs > 0:
            success_rate = self.stats['valid_calculations'] / total_calcs * 100
            
        return {
            **self.stats,
            'success_rate': success_rate,
            'cache_size': len(self._symbol_cache)
        }
    
    def clear_cache(self):
        """Limpiar cache de símbolos"""
        self._symbol_cache.clear()
        if LOGGER_AVAILABLE:
            self.logger.info("🧹 Cache de símbolos limpiado", "PositionSizing")

# Funciones de utilidad
def create_position_sizing_calculator(config: Optional[Dict] = None) -> PositionSizingCalculator:
    """Factory function para crear calculadora"""
    return PositionSizingCalculator(config)

def quick_position_calculation(symbol: str, account_balance: float, 
                             risk_percent: float, entry_price: float, 
                             stop_loss: float) -> PositionSizingResult:
    """Cálculo rápido de posición"""
    calculator = PositionSizingCalculator()
    
    params = PositionSizingParameters(
        symbol=symbol,
        account_balance=account_balance,
        risk_percent=risk_percent,
        entry_price=entry_price,
        stop_loss=stop_loss
    )
    
    return calculator.calculate_position_size(params)

def calculate_conservative_position(symbol: str, account_balance: float, 
                                  entry_price: float, stop_loss: float) -> PositionSizingResult:
    """Cálculo de posición conservadora (0.5% riesgo)"""
    return quick_position_calculation(symbol, account_balance, 0.5, entry_price, stop_loss)

def calculate_moderate_position(symbol: str, account_balance: float, 
                               entry_price: float, stop_loss: float) -> PositionSizingResult:
    """Cálculo de posición moderada (1% riesgo)"""
    return quick_position_calculation(symbol, account_balance, 1.0, entry_price, stop_loss)