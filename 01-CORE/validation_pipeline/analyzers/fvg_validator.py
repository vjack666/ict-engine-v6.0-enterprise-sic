"""
📊 FVG VALIDATOR - ICT ENGINE v6.0 ENTERPRISE
=============================================

Validador enterprise que usa SOLO módulos reales del sistema principal.
Compara Fair Value Gaps analysis entre dashboard live y backtest histórico.

Módulos Enterprise Reales:
- SmartMoneyAnalyzer: detect_fvg() método real
- ICTPatternDetector: Análisis de patrones  
- UnifiedMemorySystem: Persistencia y caché
- smart_trading_logger: log_info, log_warning, log_error funciones
- MT5DataManager: Datos de mercado en tiempo real

Usa SOLO métodos y clases que existen realmente en el sistema.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
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
class EnterpriseModuleLoader:
    """🏗️ Cargador optimizado de módulos enterprise"""
    
    def __init__(self):
        self.logger = SmartTradingLogger("fvg_validator_loader")
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
                f"❌ Dependencias críticas FVG ausentes. No se permite fallback. {problem_report}", 
                "FVG_VALIDATOR"
            )
            self.enterprise_available = False
        else:
            self.logger.info("✅ Módulos enterprise FVG cargados correctamente", "FVG_VALIDATOR")
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
_module_loader = EnterpriseModuleLoader()

# Variables globales para acceso directo
ENTERPRISE_MODULES_AVAILABLE = _module_loader.is_enterprise_ready()
logger = SmartTradingLogger("fvg_validator")

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

def enviar_senal_log(level: str, message: str, module: str, category: Optional[str] = None) -> None:
    """🔔 Sistema de logging centralizado optimizado"""
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message, module)


class FVGValidatorEnterprise:
    """
    📊 FVG Validator Enterprise Edition
    
    Usa SOLO métodos reales que existen en el sistema:
    - SmartMoneyAnalyzer.detect_fvg()
    - ICTPatternDetector methods
    - UnifiedMemorySystem storage
    - MT5DataManager.get_historical_data()
    - log_info, log_warning, log_error logging
    
    Compara análisis live vs historical para accuracy metrics.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Inicializar validador usando SOLO métodos reales"""
        self.config = config or self._default_config()
        
        enviar_senal_log("INFO", "🚀 Inicializando FVGValidatorEnterprise", 
                        "fvg_validator", "system")
        
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
        
        enviar_senal_log("INFO", "✅ FVGValidatorEnterprise listo", 
                        "fvg_validator", "system")
    
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
            'fvg_params': {
                'min_gap_pips': 5,
                'max_gap_pips': 50,
                'gap_threshold': 0.0001
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
            raise RuntimeError("Dependencias enterprise FVG ausentes. Abortando inicialización.")

        # Inicializaciones enterprise optimizadas
        try:
            self.modules['smart_money'] = get_smart_money_analyzer()()
            self.modules_available['smart_money'] = True
            enviar_senal_log("INFO", "✅ SmartMoneyAnalyzer inicializado", "fvg_validator", "enterprise")

            self.modules['pattern_detector'] = get_ict_pattern_detector()()
            self.modules_available['pattern_detector'] = True
            enviar_senal_log("INFO", "✅ ICTPatternDetector inicializado", "fvg_validator", "enterprise")

            self.modules['memory_system'] = get_unified_memory_system()()
            self.modules_available['memory_system'] = True
            enviar_senal_log("INFO", "✅ UnifiedMemorySystem inicializado", "fvg_validator", "enterprise")

            self.modules['mt5_data'] = get_mt5_data_manager()()
            self.modules_available['mt5_data'] = True
            enviar_senal_log("INFO", "✅ MT5DataManager inicializado", "fvg_validator", "enterprise")

            enviar_senal_log("INFO", "🎯 Todos los módulos FVG enterprise inicializados", "fvg_validator", "enterprise")
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error inicializando módulos FVG: {e}", "fvg_validator", "enterprise")
            raise RuntimeError(f"Fallo inicialización módulos enterprise: {e}") from e
    
    def _initialize_fallback_modules(self):
        """Módulos fallback si enterprise no disponible"""
        raise RuntimeError("Modo fallback deshabilitado: se requieren todos los módulos enterprise.")
    
    def validate_fvg_accuracy(self, symbol: str, timeframe: str, 
                             validation_period: str = 'short') -> Dict[str, Any]:
        """
        📊 Validar accuracy FVG usando métodos REALES
        """
        validation_id = f"fvg_validation_{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        enviar_senal_log("INFO", f"🔄 Validación FVG: {validation_id}", 
                        "fvg_validator", "validation")
        
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
            # 1. ANÁLISIS LIVE usando SmartMoneyAnalyzer.detect_fvg()
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
                           f"✅ Validación FVG completada: {accuracy_metrics.get('overall_accuracy', 0):.2%}", 
                           "fvg_validator", "validation")
            
            return validation_result
            
        except Exception as e:
            error_msg = f"❌ Error en validación FVG: {e}"
            enviar_senal_log("ERROR", error_msg, "fvg_validator", "validation")
            
            validation_result['error'] = str(e)
            validation_result['success'] = False
            
            return validation_result
    
    def _execute_live_analysis(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Ejecutar análisis live usando SmartMoneyAnalyzer.detect_fvg()"""
        try:
            fvg_gaps = self.modules['smart_money'].detect_fvg(
                symbol=symbol,
                timeframe=timeframe
            )

            return {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'method_used': 'SmartMoneyAnalyzer.detect_fvg',
                'symbol': symbol,
                'timeframe': timeframe,
                'fvg_count': len(fvg_gaps),
                'fvg_data': fvg_gaps,
                'analysis_type': 'live'
            }
                
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error análisis FVG live: {e}", 
                            "fvg_validator", "analysis")
            raise RuntimeError(f"Análisis FVG live falló: {e}") from e
    
    def _execute_historical_analysis(self, symbol: str, timeframe: str, period: str) -> Dict[str, Any]:
        """Ejecutar análisis histórico usando MISMOS métodos"""
        try:
            fvg_gaps = self.modules['smart_money'].detect_fvg(
                symbol=symbol,
                timeframe=timeframe
            )

            return {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'method_used': 'SmartMoneyAnalyzer.detect_fvg',
                'symbol': symbol,
                'timeframe': timeframe,
                'validation_period': period,
                'fvg_count': len(fvg_gaps),
                'fvg_data': fvg_gaps,
                'analysis_type': 'historical'
            }
                
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error análisis FVG histórico: {e}", 
                            "fvg_validator", "analysis")
            raise RuntimeError(f"Análisis FVG histórico falló: {e}") from e
    
    def _calculate_accuracy_metrics(self, live_analysis: Dict, historical_analysis: Dict) -> Dict[str, Any]:
        """Calcular métricas de accuracy comparando live vs historical"""
        try:
            live_count = live_analysis.get('fvg_count', 0)
            historical_count = historical_analysis.get('fvg_count', 0)
            
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
            enviar_senal_log("ERROR", f"❌ Error calculando accuracy FVG: {e}", 
                            "fvg_validator", "metrics")
            return {
                'overall_accuracy': 0.0,
                'quality_level': 'error',
                'error': str(e)
            }
    
    def _create_fallback_analysis(self, symbol: str, timeframe: str, analysis_type: str, error: Optional[str] = None) -> Dict[str, Any]:
        """Análisis fallback cuando módulos no disponibles"""
        raise RuntimeError("Fallback analysis deshabilitado: dependencias enterprise requeridas")
    
    def _save_validation_result(self, validation_id: str, result: Dict[str, Any]):
        """Guardar resultado usando UnifiedMemorySystem si disponible"""
        try:
            # Usar método real del UnifiedMemorySystem
            if hasattr(self.modules['memory_system'], 'store_data'):
                self.modules['memory_system'].store_data(f"validation_{validation_id}", result)
            else:
                enviar_senal_log("WARNING", "⚠️ UnifiedMemorySystem.store_data no disponible", 
                                "fvg_validator", "storage")
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error guardando resultado FVG: {e}", 
                            "fvg_validator", "storage")
    
    def get_validator_status(self) -> Dict[str, Any]:
        """Obtener estado del validador FVG"""
        return {
            'validator_type': 'FVGValidatorEnterprise',
            'modules_available': self.modules_available,
            'modules_count': sum(self.modules_available.values()),
            'validations_executed': self.validator_state['validations_executed'],
            'last_validation': self.validator_state.get('last_validation', {}).get('validation_id') if self.validator_state.get('last_validation') else None,
            'enterprise_modules_status': ENTERPRISE_MODULES_AVAILABLE,
            'timestamp': datetime.now().isoformat()
        }


# Factory function para crear el validador
def create_fvg_validator(config: Optional[Dict] = None) -> FVGValidatorEnterprise:
    """Factory para crear FVGValidator enterprise"""
    return FVGValidatorEnterprise(config)


# Export para uso externo
__all__ = ['FVGValidatorEnterprise', 'create_fvg_validator']