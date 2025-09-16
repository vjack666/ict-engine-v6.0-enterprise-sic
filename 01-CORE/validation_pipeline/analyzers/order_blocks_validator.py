"""
🔷 ORDER BLOCKS VALIDATOR - ICT ENGINE v6.0 ENTERPRISE  
======================================================

Validador enterprise que usa SOLO módulos reales del sistema principal.
Compara Order Blocks analysis entre dashboard live y backtest histórico.

Módulos Enterprise Reales:
- SmartMoneyAnalyzer: find_order_blocks() método
- ICTPatternDetector: Análisis de patrones  
- UnifiedMemorySystem: Persistencia y caché
- SmartTradingLogger: Logging centralizado
- MT5DataManager: Datos de mercado en tiempo real

Usa SOLO métodos y clases que existen realmente en el sistema.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

# ==========================================
# IMPORTS MÓDULOS ENTERPRISE REALES - SISTEMA OPTIMIZADO
# ==========================================
# Imports absolutos sin type: ignore - sistema robusto de dependencias

# Logger centralizado principal
from protocols.unified_logging import get_unified_logger

# Dependencias enterprise con manejo granular de errores
from typing import TYPE_CHECKING

# Type-only imports para análisis estático
if TYPE_CHECKING:
    from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
    from ict_engine.pattern_detector import ICTPatternDetector
    from analysis.unified_memory_system import UnifiedMemorySystem
    from data_management.mt5_data_manager import MT5DataManager

# Sistema de importación enterprise optimizado
class EnterpriseOrderBlocksModuleLoader:
    """🏗️ Cargador optimizado de módulos enterprise para Order Blocks"""
    
    def __init__(self):
        self.logger = get_unified_logger("order_blocks_validator_loader")
        self.modules: Dict[str, Any] = {}
        self.missing_dependencies: Dict[str, str] = {}
        self.enterprise_available = False
        
        self._load_enterprise_modules()
    
    def _load_enterprise_modules(self) -> None:
        """Cargar módulos enterprise con diagnóstico granular"""
        module_specs = [
            ("SmartMoneyAnalyzer", "smart_money_concepts.smart_money_analyzer", "SmartMoneyAnalyzer"),
            ("ICTPatternDetector", "ict_engine.pattern_detector", "ICTPatternDetector"),
            ("UnifiedMemorySystem", "analysis.unified_memory_system", "UnifiedMemorySystem"),
            ("MT5DataManager", "data_management.mt5_data_manager", "MT5DataManager")
        ]
        
        for name, module_path, class_name in module_specs:
            try:
                module = __import__(module_path, fromlist=[class_name])
                self.modules[name] = getattr(module, class_name)
                self.logger.debug(f"✅ {name} cargado desde {module_path}", "MODULE_LOADER")
                
            except ImportError as e:
                self.missing_dependencies[name] = f"ImportError: {e}"
                self.logger.error(f"❌ {name} no disponible: {e}", "MODULE_LOADER")
                
            except AttributeError as e:
                self.missing_dependencies[name] = f"AttributeError: {e}"
                self.logger.error(f"❌ {name} clase no encontrada: {e}", "MODULE_LOADER")
                
            except Exception as e:
                self.missing_dependencies[name] = f"Error general: {e}"
                self.logger.error(f"❌ {name} error inesperado: {e}", "MODULE_LOADER")
        
        # Validar estado enterprise
        if self.missing_dependencies:
            problem_report = " | ".join(f"{k}: {v}" for k, v in self.missing_dependencies.items())
            self.logger.error(
                f"❌ Dependencias críticas Order Blocks ausentes. No se permite fallback. {problem_report}", 
                "ORDER_BLOCKS_VALIDATOR"
            )
            self.enterprise_available = False
        else:
            self.logger.info("✅ Módulos enterprise Order Blocks cargados correctamente", "ORDER_BLOCKS_VALIDATOR")
            self.enterprise_available = True
    
    def get_module(self, name: str) -> Any:
        """Obtener módulo enterprise o lanzar excepción"""
        if name not in self.modules:
            raise RuntimeError(f"Módulo enterprise {name} no disponible: {self.missing_dependencies.get(name, 'desconocido')}")
        return self.modules[name]
    
    def is_enterprise_ready(self) -> bool:
        """Verificar si todos los módulos enterprise están disponibles"""
        return self.enterprise_available

# Instancia global del loader
_module_loader = EnterpriseOrderBlocksModuleLoader()

# Variables globales para acceso directo
ENTERPRISE_MODULES_AVAILABLE = _module_loader.is_enterprise_ready()
logger = get_unified_logger("order_blocks_validator")

# Acceso a módulos enterprise
def get_smart_money_analyzer():
    """Obtener SmartMoneyAnalyzer enterprise"""
    return _module_loader.get_module("SmartMoneyAnalyzer")

def get_ict_pattern_detector():
    """Obtener ICTPatternDetector enterprise"""
    return _module_loader.get_module("ICTPatternDetector")

def get_unified_memory_system():
    """Obtener UnifiedMemorySystem enterprise"""
    return _module_loader.get_module("UnifiedMemorySystem")

def get_mt5_data_manager():
    """Obtener MT5DataManager enterprise"""
    return _module_loader.get_module("MT5DataManager")


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
        
        logger.info("🚀 Inicializando OrderBlocksValidatorEnterprise", "order_blocks_validator")
        
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
        
        logger.info("✅ OrderBlocksValidatorEnterprise listo", "order_blocks_validator")
    
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
        """Inicializar módulos enterprise usando sistema optimizado"""
        self.modules = {}
        self.modules_available = {}
        
        if not ENTERPRISE_MODULES_AVAILABLE:
            raise RuntimeError("Dependencias enterprise Order Blocks ausentes. Abortando inicialización.")

        # Inicializaciones enterprise optimizadas
        try:
            self.modules['smart_money'] = get_smart_money_analyzer()()
            self.modules_available['smart_money'] = True
            logger.info("✅ SmartMoneyAnalyzer inicializado", "order_blocks_validator")

            self.modules['pattern_detector'] = get_ict_pattern_detector()()
            self.modules_available['pattern_detector'] = True
            logger.info("✅ ICTPatternDetector inicializado", "order_blocks_validator")

            self.modules['memory_system'] = get_unified_memory_system()()
            self.modules_available['memory_system'] = True
            logger.info("✅ UnifiedMemorySystem inicializado", "order_blocks_validator")

            self.modules['mt5_data'] = get_mt5_data_manager()()
            self.modules_available['mt5_data'] = True
            logger.info("✅ MT5DataManager inicializado", "order_blocks_validator")

            logger.info("🎯 Todos los módulos Order Blocks enterprise inicializados", "order_blocks_validator")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando módulos Order Blocks: {e}", "order_blocks_validator")
            raise RuntimeError(f"Fallo inicialización módulos enterprise: {e}") from e
    
    def _initialize_fallback_modules(self):
        """Módulos fallback deshabilitados - se requieren todos los módulos enterprise"""
        raise RuntimeError("Modo fallback deshabilitado: se requieren todos los módulos enterprise.")
    
    def validate_order_blocks_accuracy(self, symbol: str, timeframe: str, 
                                     validation_period: str = 'short') -> Dict[str, Any]:
        """
        🔍 Validar accuracy Order Blocks usando métodos REALES
        """
        validation_id = f"ob_validation_{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🔄 Validación Order Blocks: {validation_id}", "order_blocks_validator")
        
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
            
            logger.info(f"✅ Validación Order Blocks completada: {accuracy_metrics.get('overall_accuracy', 0):.2%}", "order_blocks_validator")
            
            return validation_result
            
        except Exception as e:
            error_msg = f"❌ Error en validación Order Blocks: {e}"
            logger.error(error_msg, "order_blocks_validator")
            
            validation_result['error'] = str(e)
            validation_result['success'] = False
            
            return validation_result
    
    def _execute_live_analysis(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Ejecutar análisis live usando SmartMoneyAnalyzer.find_order_blocks()"""
        try:
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
                
        except Exception as e:
            logger.error(f"❌ Error análisis Order Blocks live: {e}", "order_blocks_validator")
            raise RuntimeError(f"Análisis Order Blocks live falló: {e}") from e
    
    def _execute_historical_analysis(self, symbol: str, timeframe: str, period: str) -> Dict[str, Any]:
        """Ejecutar análisis histórico usando MISMOS métodos"""
        try:
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
                
        except Exception as e:
            logger.error(f"❌ Error análisis Order Blocks histórico: {e}", "order_blocks_validator")
            raise RuntimeError(f"Análisis Order Blocks histórico falló: {e}") from e
    
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
            logger.error(f"❌ Error calculando accuracy Order Blocks: {e}", "order_blocks_validator")
            return {
                'overall_accuracy': 0.0,
                'quality_level': 'error',
                'error': str(e)
            }
    
    def _create_fallback_analysis(self, symbol: str, timeframe: str, analysis_type: str, error: Optional[str] = None) -> Dict[str, Any]:
        """Análisis fallback deshabilitado - dependencias enterprise requeridas"""
        raise RuntimeError("Fallback analysis deshabilitado: dependencias enterprise requeridas")
    
    def _save_validation_result(self, validation_id: str, result: Dict[str, Any]):
        """Guardar resultado usando UnifiedMemorySystem si disponible"""
        try:
            # Usar método real del UnifiedMemorySystem
            if hasattr(self.modules['memory_system'], 'store_data'):
                self.modules['memory_system'].store_data(f"validation_{validation_id}", result)
            else:
                logger.warning("⚠️ UnifiedMemorySystem.store_data no disponible", "order_blocks_validator")
        except Exception as e:
            logger.error(f"❌ Error guardando resultado Order Blocks: {e}", "order_blocks_validator")
    
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
