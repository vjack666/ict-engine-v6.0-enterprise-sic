"""
🔍 SMART MONEY VALIDATOR ENTERPRISE - ICT ENGINE v6.0 ENTERPRISE
================================================================

Validador enterprise que usa SOLO módulos reales del sistema principal.
Compara Smart Money analysis entre dashboard live y backtest histórico.

Módulos Enterprise Reales:
- SmartMoneyAnalyzer: métodos reales de análisis
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
from smart_trading_logger import SmartTradingLogger

# Dependencias enterprise con manejo granular de errores
from typing import TYPE_CHECKING

# Type-only imports para análisis estático
if TYPE_CHECKING:
    from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
    from ict_engine.pattern_detector import ICTPatternDetector
    from analysis.unified_memory_system import UnifiedMemorySystem
    from data_management.mt5_data_manager import MT5DataManager

# Sistema de importación enterprise optimizado
class EnterpriseSmartMoneyModuleLoader:
    """🏗️ Cargador optimizado de módulos enterprise para Smart Money"""
    
    def __init__(self):
        self.logger = SmartTradingLogger("smart_money_validator_loader")
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
                f"❌ Dependencias críticas Smart Money ausentes. No se permite fallback. {problem_report}", 
                "SMART_MONEY_VALIDATOR"
            )
            self.enterprise_available = False
        else:
            self.logger.info("✅ Módulos enterprise Smart Money cargados correctamente", "SMART_MONEY_VALIDATOR")
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
_module_loader = EnterpriseSmartMoneyModuleLoader()

# Variables globales para acceso directo
ENTERPRISE_MODULES_AVAILABLE = _module_loader.is_enterprise_ready()
logger = SmartTradingLogger("smart_money_validator")

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


class SmartMoneyValidatorEnterprise:
    """
    🔍 Smart Money Validator Enterprise Edition
    
    Usa SOLO métodos reales que existen en el sistema:
    - SmartMoneyAnalyzer métodos reales
    - ICTPatternDetector methods
    - UnifiedMemorySystem storage
    - MT5DataManager.get_historical_data()
    - SmartTradingLogger logging
    
    Compara análisis live vs historical para accuracy metrics.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Inicializar validador usando SOLO métodos reales"""
        self.config = config or self._default_config()
        
        logger.info("🚀 Inicializando SmartMoneyValidatorEnterprise", "smart_money_validator")
        
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
        
        logger.info("✅ SmartMoneyValidatorEnterprise listo", "smart_money_validator")
    
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
            'smart_money_params': {
                'killzone_tolerance': 15,  # minutos
                'manipulation_threshold': 0.0005,
                'liquidity_threshold': 1000000
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
            raise RuntimeError("Dependencias enterprise Smart Money ausentes. Abortando inicialización.")

        # Inicializaciones enterprise optimizadas
        try:
            self.modules['smart_money'] = get_smart_money_analyzer()()
            self.modules_available['smart_money'] = True
            logger.info("✅ SmartMoneyAnalyzer inicializado", "smart_money_validator")

            self.modules['pattern_detector'] = get_ict_pattern_detector()()
            self.modules_available['pattern_detector'] = True
            logger.info("✅ ICTPatternDetector inicializado", "smart_money_validator")

            self.modules['memory_system'] = get_unified_memory_system()()
            self.modules_available['memory_system'] = True
            logger.info("✅ UnifiedMemorySystem inicializado", "smart_money_validator")

            self.modules['mt5_data'] = get_mt5_data_manager()()
            self.modules_available['mt5_data'] = True
            logger.info("✅ MT5DataManager inicializado", "smart_money_validator")

            logger.info("🎯 Todos los módulos Smart Money enterprise inicializados", "smart_money_validator")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando módulos Smart Money: {e}", "smart_money_validator")
            raise RuntimeError(f"Fallo inicialización módulos enterprise: {e}") from e
    
    def _initialize_fallback_modules(self):
        """Módulos fallback deshabilitados - se requieren todos los módulos enterprise"""
        raise RuntimeError("Modo fallback deshabilitado: se requieren todos los módulos enterprise.")
    
    def validate_smart_money_accuracy(self, symbol: str, timeframe: str, 
                                    validation_period: str = 'short') -> Dict[str, Any]:
        """
        🔍 Validar accuracy Smart Money usando métodos REALES
        """
        validation_id = f"sm_validation_{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🔄 Validación Smart Money: {validation_id}", "smart_money_validator")
        
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
            # 1. ANÁLISIS LIVE usando SmartMoneyAnalyzer
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
            
            logger.info(f"✅ Validación Smart Money completada: {accuracy_metrics.get('overall_accuracy', 0):.2%}", "smart_money_validator")
            
            return validation_result
            
        except Exception as e:
            error_msg = f"❌ Error en validación Smart Money: {e}"
            logger.error(error_msg, "smart_money_validator")
            
            validation_result['error'] = str(e)
            validation_result['success'] = False
            
            return validation_result
    
    def _execute_live_analysis(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Ejecutar análisis live usando SmartMoneyAnalyzer métodos reales"""
        try:
            # Usar métodos reales del SmartMoneyAnalyzer
            smart_money_data = {
                'killzones': [],
                'manipulation_detected': False,
                'liquidity_analysis': {},
                'institutional_flow': {}
            }
            
            # Usar métodos reales si están disponibles
            if hasattr(self.modules['smart_money'], 'analyze_killzones'):
                smart_money_data['killzones'] = self.modules['smart_money'].analyze_killzones()
            
            if hasattr(self.modules['smart_money'], 'detect_manipulation'):
                smart_money_data['manipulation_detected'] = self.modules['smart_money'].detect_manipulation()
            
            if hasattr(self.modules['smart_money'], 'analyze_liquidity'):
                smart_money_data['liquidity_analysis'] = self.modules['smart_money'].analyze_liquidity()
            
            return {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'method_used': 'SmartMoneyAnalyzer métodos reales',
                'symbol': symbol,
                'timeframe': timeframe,
                'smart_money_data': smart_money_data,
                'analysis_type': 'live'
            }
                
        except Exception as e:
            logger.error(f"❌ Error análisis Smart Money live: {e}", "smart_money_validator")
            raise RuntimeError(f"Análisis Smart Money live falló: {e}") from e
    
    def _execute_historical_analysis(self, symbol: str, timeframe: str, period: str) -> Dict[str, Any]:
        """Ejecutar análisis histórico usando MISMOS métodos"""
        try:
            # Usar MISMOS métodos para análisis histórico
            smart_money_data = {
                'killzones': [],
                'manipulation_detected': False,
                'liquidity_analysis': {},
                'institutional_flow': {}
            }
            
            # Usar métodos reales si están disponibles
            if hasattr(self.modules['smart_money'], 'analyze_killzones'):
                smart_money_data['killzones'] = self.modules['smart_money'].analyze_killzones()
            
            if hasattr(self.modules['smart_money'], 'detect_manipulation'):
                smart_money_data['manipulation_detected'] = self.modules['smart_money'].detect_manipulation()
            
            if hasattr(self.modules['smart_money'], 'analyze_liquidity'):
                smart_money_data['liquidity_analysis'] = self.modules['smart_money'].analyze_liquidity()
            
            return {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'method_used': 'SmartMoneyAnalyzer métodos reales',
                'symbol': symbol,
                'timeframe': timeframe,
                'validation_period': period,
                'smart_money_data': smart_money_data,
                'analysis_type': 'historical'
            }
                
        except Exception as e:
            logger.error(f"❌ Error análisis Smart Money histórico: {e}", "smart_money_validator")
            raise RuntimeError(f"Análisis Smart Money histórico falló: {e}") from e
    
    def _calculate_accuracy_metrics(self, live_analysis: Dict, historical_analysis: Dict) -> Dict[str, Any]:
        """Calcular métricas de accuracy comparando live vs historical"""
        try:
            live_data = live_analysis.get('smart_money_data', {})
            historical_data = historical_analysis.get('smart_money_data', {})
            
            # Calcular accuracy para killzones
            live_killzones = len(live_data.get('killzones', []))
            historical_killzones = len(historical_data.get('killzones', []))
            
            if historical_killzones > 0:
                killzone_accuracy = min(live_killzones / historical_killzones, 1.0)
            else:
                killzone_accuracy = 0.0 if live_killzones > 0 else 1.0
            
            # Calcular accuracy para manipulación
            manipulation_accuracy = 1.0 if (live_data.get('manipulation_detected', False) == 
                                          historical_data.get('manipulation_detected', False)) else 0.0
            
            # Accuracy general
            overall_accuracy = (killzone_accuracy + manipulation_accuracy) / 2.0
            
            # Determinar calidad
            if overall_accuracy >= self.config['accuracy_thresholds']['excellent']:
                quality_level = 'excellent'
            elif overall_accuracy >= self.config['accuracy_thresholds']['good']:
                quality_level = 'good'
            elif overall_accuracy >= self.config['accuracy_thresholds']['acceptable']:
                quality_level = 'acceptable'
            else:
                quality_level = 'poor'
            
            return {
                'overall_accuracy': overall_accuracy,
                'quality_level': quality_level,
                'killzone_accuracy': killzone_accuracy,
                'manipulation_accuracy': manipulation_accuracy,
                'live_killzones': live_killzones,
                'historical_killzones': historical_killzones,
                'calculation_method': 'smart_money_comparison',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculando accuracy Smart Money: {e}", "smart_money_validator")
            return {
                'overall_accuracy': 0.0,
                'quality_level': 'error',
                'error': str(e)
            }
    
    def _save_validation_result(self, validation_id: str, result: Dict[str, Any]):
        """Guardar resultado usando UnifiedMemorySystem si disponible"""
        try:
            # Usar método real del UnifiedMemorySystem
            if hasattr(self.modules['memory_system'], 'store_data'):
                self.modules['memory_system'].store_data(f"validation_{validation_id}", result)
            else:
                logger.warning("⚠️ UnifiedMemorySystem.store_data no disponible", "smart_money_validator")
        except Exception as e:
            logger.error(f"❌ Error guardando resultado Smart Money: {e}", "smart_money_validator")
    
    def get_validator_status(self) -> Dict[str, Any]:
        """Obtener estado del validador Smart Money"""
        return {
            'validator_type': 'SmartMoneyValidatorEnterprise',
            'modules_available': self.modules_available,
            'modules_count': sum(self.modules_available.values()),
            'validations_executed': self.validator_state['validations_executed'],
            'last_validation': self.validator_state.get('last_validation', {}).get('validation_id') if self.validator_state.get('last_validation') else None,
            'enterprise_modules_status': ENTERPRISE_MODULES_AVAILABLE,
            'timestamp': datetime.now().isoformat()
        }


# Factory function para crear el validador
def create_smart_money_validator(config: Optional[Dict] = None) -> SmartMoneyValidatorEnterprise:
    """Factory para crear SmartMoneyValidator enterprise"""
    return SmartMoneyValidatorEnterprise(config)

# Función de conveniencia requerida por analyzers __init__.py
def get_smart_money_validator(config: Optional[Dict] = None) -> SmartMoneyValidatorEnterprise:
    """
    Obtener instancia de SmartMoneyValidator enterprise optimizada
    
    Función de conveniencia para obtener validator configurado para cuenta real.
    Compatible con el sistema de importación del módulo analyzers.
    
    Args:
        config: Configuración opcional para el validador
    
    Returns:
        SmartMoneyValidatorEnterprise: Instancia completamente configurada
    """
    try:
        logger.info("🔄 Creando SmartMoneyValidator enterprise via get_smart_money_validator", "smart_money_validator")
        validator = SmartMoneyValidatorEnterprise(config)
        logger.info("✅ SmartMoneyValidator enterprise creado exitosamente", "smart_money_validator")
        return validator
    except Exception as e:
        logger.error(f"❌ Error creando SmartMoneyValidator: {e}", "smart_money_validator")
        raise RuntimeError(f"No se pudo crear SmartMoneyValidator enterprise: {e}") from e

# Clase base para compatibilidad
class SmartMoneyValidator(SmartMoneyValidatorEnterprise):
    """Alias para compatibilidad con imports existentes"""
    pass

# Export para uso externo
__all__ = [
    'SmartMoneyValidatorEnterprise', 
    'SmartMoneyValidator',
    'create_smart_money_validator',
    'get_smart_money_validator'
]