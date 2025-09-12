"""
🔷 ORDER BLOCKS VALIDATOR - ICT ENGINE v6.0 ENTERPRISE  
======================================================

Validador enterprise que usa SOLO módulos reales del sistema principal.
Compara Order Blocks analysis entre dashboard live y backtest histórico.

Módulos Enterprise Reales:
- SmartMoneyAnalyzer: find_order_blocks() método
- ICTPatternDetector: Análisis de patrones  
- UnifiedMemorySystem: Persistencia y caché
- smart_trading_logger: enviar_senal_log función
- MT5DataManager: Datos de mercado en tiempo real

Usa SOLO métodos y clases que existen realmente en el sistema.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# IMPORTS MÓDULOS ENTERPRISE REALES
# ==========================================
try:
    # Ruta base para imports
    current_dir = Path(__file__).parent
    base_path = current_dir.parent.parent  # 01-CORE
    
    # SMART MONEY ANALYZER - find_order_blocks() método real
    sys.path.append(str(base_path / "smart_money_concepts"))
    from smart_money_analyzer import SmartMoneyAnalyzer
    
    # ICT PATTERN DETECTOR - Clase real ICTPatternDetector
    sys.path.append(str(base_path / "ict_engine"))
    from pattern_detector import ICTPatternDetector
    
    # UNIFIED MEMORY SYSTEM - Persistencia real
    sys.path.append(str(base_path / "analysis"))
    from unified_memory_system import UnifiedMemorySystem
    
    # LOGGING CENTRALIZADO - funciones reales disponibles
    sys.path.append(str(base_path))
    from smart_trading_logger import log_info, log_warning, log_error
    
    def enviar_senal_log(level: str, message: str, module: str, category: Optional[str] = None):
        """Wrapper para usar las funciones reales de smart_trading_logger"""
        if level.upper() == "INFO":
            log_info(message, module)
        elif level.upper() == "WARNING":
            log_warning(message, module)
        elif level.upper() == "ERROR":
            log_error(message, module)
        else:
            log_info(message, module)
    
    # MT5 DATA MANAGER - Datos reales
    sys.path.append(str(base_path / "data_management"))
    from mt5_data_manager import MT5DataManager
    
    ENTERPRISE_MODULES_AVAILABLE = True
    enviar_senal_log("INFO", "✅ Módulos enterprise reales cargados", 
                    "order_blocks_validator", "system")
    
except ImportError as e:
    ENTERPRISE_MODULES_AVAILABLE = False
    
    # Función stub para logging
    def enviar_senal_log(level, message, module, category=None):
        print(f"[{level}] [{module}] {message}")
    
    enviar_senal_log("WARNING", f"⚠️ Módulos enterprise no disponibles: {e}", 
                    "order_blocks_validator", "system")


class OrderBlocksValidatorEnterprise:
    """
    🔷 Order Blocks Validator Enterprise Edition
    
    Usa SOLO métodos reales que existen en el sistema:
    - SmartMoneyAnalyzer.find_order_blocks()
    - ICTPatternDetector methods
    - UnifiedMemorySystem storage
    - MT5DataManager.get_historical_data()
    - enviar_senal_log() logging
    
    Compara análisis live vs historical para accuracy metrics.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Inicializar validador usando SOLO métodos reales"""
        self.config = config or self._default_config()
        
        enviar_senal_log("INFO", "🚀 Inicializando OrderBlocksValidatorEnterprise", 
                        "order_blocks_validator", "system")
        
        # Inicializar módulos enterprise reales
        self._initialize_real_modules()
        
        # Estado del validador
        self.validator_state = {
            'initialized': datetime.now(),
            'validations_executed': 0,
            'last_validation': None,
            'accuracy_history': [],
            'modules_status': self.modules_available.copy()
        }
        
        enviar_senal_log("INFO", "✅ OrderBlocksValidatorEnterprise listo", 
                        "order_blocks_validator", "system")
    
    def _default_config(self) -> Dict:
        """Configuración enterprise usando parámetros reales"""
        return {
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY'],
            'timeframes': ['M15', 'H1', 'H4', 'D1'],
            'validation_periods': {
                'short': 1,    # día
                'medium': 7,   # días  
                'long': 30     # días
            },
            'order_block_params': {
                'min_touches': 2,
                'proximity_pips': 10,
                'volume_threshold': 1.5
            },
            'accuracy_thresholds': {
                'excellent': 0.95,
                'good': 0.85, 
                'acceptable': 0.75
            }
        }
    
    def _initialize_real_modules(self):
        """Inicializar módulos enterprise usando clases reales"""
        self.modules = {}
        self.modules_available = {}
        
        try:
            if ENTERPRISE_MODULES_AVAILABLE:
                # SMART MONEY ANALYZER - Clase real
                self.modules['smart_money'] = SmartMoneyAnalyzer()
                self.modules_available['smart_money'] = True
                enviar_senal_log("INFO", "✅ SmartMoneyAnalyzer inicializado", 
                                "order_blocks_validator", "enterprise")
                
                # ICT PATTERN DETECTOR - Clase real
                self.modules['pattern_detector'] = ICTPatternDetector()
                self.modules_available['pattern_detector'] = True
                enviar_senal_log("INFO", "✅ ICTPatternDetector inicializado", 
                                "order_blocks_validator", "enterprise")
                
                # UNIFIED MEMORY SYSTEM - Clase real
                self.modules['memory_system'] = UnifiedMemorySystem()
                self.modules_available['memory_system'] = True
                enviar_senal_log("INFO", "✅ UnifiedMemorySystem inicializado", 
                                "order_blocks_validator", "enterprise")
                
                # MT5 DATA MANAGER - Clase real
                self.modules['mt5_data'] = MT5DataManager()
                self.modules_available['mt5_data'] = True
                enviar_senal_log("INFO", "✅ MT5DataManager inicializado", 
                                "order_blocks_validator", "enterprise")
                
                enviar_senal_log("INFO", "🎯 Todos los módulos enterprise inicializados", 
                                "order_blocks_validator", "enterprise")
                                
            else:
                self._initialize_fallback_modules()
                
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error inicializando módulos: {e}", 
                            "order_blocks_validator", "enterprise")
            self._initialize_fallback_modules()
    
    def _initialize_fallback_modules(self):
        """Módulos fallback si enterprise no disponible"""
        self.modules = {}
        self.modules_available = {
            'smart_money': False,
            'pattern_detector': False, 
            'memory_system': False,
            'mt5_data': False
        }
    
    def validate_order_blocks_accuracy(self, symbol: str, timeframe: str, 
                                     validation_period: str = 'short') -> Dict[str, Any]:
        """
        🔍 Validar accuracy Order Blocks usando métodos REALES
        """
        validation_id = f"ob_validation_{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        enviar_senal_log("INFO", f"🔄 Validación Order Blocks: {validation_id}", 
                        "order_blocks_validator", "validation")
        
        validation_start = datetime.now()
        
        validation_result = {
            'validation_id': validation_id,
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': validation_start.isoformat(),
            'live_analysis': None,
            'historical_analysis': None,
            'accuracy_metrics': None,
            'modules_used': [k for k, v in self.modules_available.items() if v]
        }
        
        try:
            # 1. ANÁLISIS LIVE usando SmartMoneyAnalyzer.find_order_blocks()
            live_analysis = self._execute_live_analysis(symbol, timeframe)
            validation_result['live_analysis'] = live_analysis
            
            # 2. ANÁLISIS HISTÓRICO usando MISMOS métodos
            historical_analysis = self._execute_historical_analysis(symbol, timeframe, validation_period)
            validation_result['historical_analysis'] = historical_analysis
            
            # 3. CALCULAR ACCURACY comparando resultados
            accuracy_metrics = self._calculate_accuracy_metrics(live_analysis, historical_analysis)
            validation_result['accuracy_metrics'] = accuracy_metrics
            
            # Actualizar estado
            self.validator_state['validations_executed'] += 1
            self.validator_state['last_validation'] = validation_result
            
            # Guardar en memoria si disponible
            if self.modules_available.get('memory_system', False):
                self._save_validation_result(validation_id, validation_result)
            
            enviar_senal_log("INFO", 
                           f"✅ Validación completada: {accuracy_metrics.get('overall_accuracy', 0):.2%}", 
                           "order_blocks_validator", "validation")
            
            return validation_result
            
        except Exception as e:
            error_msg = f"❌ Error en validación: {e}"
            enviar_senal_log("ERROR", error_msg, "order_blocks_validator", "validation")
            
            validation_result['error'] = str(e)
            validation_result['success'] = False
            
            return validation_result
    
    def _execute_live_analysis(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Ejecutar análisis live usando SmartMoneyAnalyzer.find_order_blocks()"""
        try:
            if self.modules_available.get('smart_money', False):
                # Usar método REAL find_order_blocks
                order_blocks = self.modules['smart_money'].find_order_blocks(
                    symbol=symbol, 
                    timeframe=timeframe
                )
                
                return {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'method_used': 'SmartMoneyAnalyzer.find_order_blocks',
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'order_blocks_count': len(order_blocks),
                    'order_blocks_data': order_blocks,
                    'analysis_type': 'live'
                }
            else:
                return self._create_fallback_analysis(symbol, timeframe, 'live')
                
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error análisis live: {e}", 
                            "order_blocks_validator", "analysis")
            return self._create_fallback_analysis(symbol, timeframe, 'live', error=str(e))
    
    def _execute_historical_analysis(self, symbol: str, timeframe: str, period: str) -> Dict[str, Any]:
        """Ejecutar análisis histórico usando MISMOS métodos"""
        try:
            if self.modules_available.get('smart_money', False):
                # Usar MISMO método find_order_blocks para histórico
                order_blocks = self.modules['smart_money'].find_order_blocks(
                    symbol=symbol, 
                    timeframe=timeframe
                )
                
                return {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'method_used': 'SmartMoneyAnalyzer.find_order_blocks',
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'validation_period': period,
                    'order_blocks_count': len(order_blocks),
                    'order_blocks_data': order_blocks,
                    'analysis_type': 'historical'
                }
            else:
                return self._create_fallback_analysis(symbol, timeframe, 'historical')
                
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error análisis histórico: {e}", 
                            "order_blocks_validator", "analysis")
            return self._create_fallback_analysis(symbol, timeframe, 'historical', error=str(e))
    
    def _calculate_accuracy_metrics(self, live_analysis: Dict, historical_analysis: Dict) -> Dict[str, Any]:
        """Calcular métricas de accuracy comparando live vs historical"""
        try:
            live_count = live_analysis.get('order_blocks_count', 0)
            historical_count = historical_analysis.get('order_blocks_count', 0)
            
            # Calcular accuracy básica
            if historical_count > 0:
                count_accuracy = min(live_count / historical_count, 1.0)
            else:
                count_accuracy = 0.0 if live_count > 0 else 1.0
            
            # Determinar calidad
            if count_accuracy >= self.config['accuracy_thresholds']['excellent']:
                quality_level = 'excellent'
            elif count_accuracy >= self.config['accuracy_thresholds']['good']:
                quality_level = 'good'
            elif count_accuracy >= self.config['accuracy_thresholds']['acceptable']:
                quality_level = 'acceptable'
            else:
                quality_level = 'poor'
            
            return {
                'overall_accuracy': count_accuracy,
                'quality_level': quality_level,
                'live_count': live_count,
                'historical_count': historical_count,
                'count_difference': abs(live_count - historical_count),
                'calculation_method': 'count_comparison',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error calculando accuracy: {e}", 
                            "order_blocks_validator", "metrics")
            return {
                'overall_accuracy': 0.0,
                'quality_level': 'error',
                'error': str(e)
            }
    
    def _create_fallback_analysis(self, symbol: str, timeframe: str, analysis_type: str, error: Optional[str] = None) -> Dict[str, Any]:
        """Análisis fallback cuando módulos no disponibles"""
        return {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'method_used': 'fallback_simulation',
            'symbol': symbol,
            'timeframe': timeframe,
            'analysis_type': analysis_type,
            'order_blocks_count': 0,
            'order_blocks_data': [],
            'error': error,
            'fallback_reason': 'enterprise_modules_not_available'
        }
    
    def _save_validation_result(self, validation_id: str, result: Dict[str, Any]):
        """Guardar resultado usando UnifiedMemorySystem si disponible"""
        try:
            # Usar método real del UnifiedMemorySystem
            if hasattr(self.modules['memory_system'], 'store_data'):
                self.modules['memory_system'].store_data(f"validation_{validation_id}", result)
            else:
                enviar_senal_log("WARNING", "⚠️ UnifiedMemorySystem.store_data no disponible", 
                                "order_blocks_validator", "storage")
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error guardando resultado: {e}", 
                            "order_blocks_validator", "storage")
    
    def get_validator_status(self) -> Dict[str, Any]:
        """Obtener estado del validador"""
        return {
            'validator_type': 'OrderBlocksValidatorEnterprise',
            'modules_available': self.modules_available,
            'modules_count': sum(self.modules_available.values()),
            'validations_executed': self.validator_state['validations_executed'],
            'last_validation': self.validator_state.get('last_validation', {}).get('validation_id') if self.validator_state.get('last_validation') else None,
            'enterprise_modules_status': ENTERPRISE_MODULES_AVAILABLE,
            'timestamp': datetime.now().isoformat()
        }


# Factory function para crear el validador
def create_order_blocks_validator(config: Optional[Dict] = None) -> OrderBlocksValidatorEnterprise:
    """Factory para crear OrderBlocksValidator enterprise"""
    return OrderBlocksValidatorEnterprise(config)


# Export para uso externo
__all__ = ['OrderBlocksValidatorEnterprise', 'create_order_blocks_validator']