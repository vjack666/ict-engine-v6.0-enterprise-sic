"""
🔍 VALIDATION # Imports de validadores enterprise
from .smart_money_validator import SmartMoneyValidatorEnterprise, create_smart_money_validator
from .order_blocks_validator import OrderBlocksValidatorEnterprise, create_order_blocks_validator
from .fvg_validator import FVGValidatorEnterprise, create_fvg_validator
from .enterprise_signal_validator import EnterpriseSignalValidator, create_enterprise_signal_validatorYZERS - ICT ENGINE v6.0 ENTERPRISE
===================================================

Módulo de analizadores de validación que comparan
resultados entre dashboard live y backtesting histórico.

Validadores Disponibles:
- SmartMoneyValidator: Valida análisis Smart Money
- OrderBlocksValidator: Valida análisis Order Blocks  
- FVGValidator: Valida análisis Fair Value Gaps

Todos usan EXACTAMENTE los mismos componentes del dashboard
para garantizar comparaciones válidas y métricas precisas.
"""

from typing import Dict, Any, Optional
from datetime import datetime

# Imports de validadores enterprise
from .smart_money_validator import SmartMoneyValidator, get_smart_money_validator
from .order_blocks_validator import OrderBlocksValidatorEnterprise, create_order_blocks_validator
from .fvg_validator import FVGValidatorEnterprise, create_fvg_validator

# Versión del módulo
__version__ = "1.0.0"

# Configuración por defecto para todos los validadores
DEFAULT_VALIDATION_CONFIG = {
    'symbols': ['EURUSD', 'GBPUSD'],
    'timeframes': ['M15', 'H1', 'H4'],
    'validation_periods': {
        'short': 1,    # día
        'medium': 7,   # días
        'long': 30     # días
    },
    'accuracy_thresholds': {
        'excellent': 0.95,  # 95%+
        'good': 0.85,      # 85%+
        'acceptable': 0.75  # 75%+
    },
    'save_results': True,
    'enable_detailed_logging': True
}

# Mapeo de validadores disponibles
AVAILABLE_VALIDATORS = {
    'smart_money': SmartMoneyValidatorEnterprise,  # Clase actualizada
    'order_blocks': OrderBlocksValidatorEnterprise,  # Clase actualizada
    'fvg': FVGValidatorEnterprise,  # Clase actualizada
    'enterprise_validator': EnterpriseSignalValidator  # Validador centralizado
}

# Funciones de conveniencia
VALIDATOR_GETTERS = {
    'smart_money': create_smart_money_validator,  # Factory function actualizada
    'order_blocks': create_order_blocks_validator,  # Factory function actualizada
    'fvg': create_fvg_validator,  # Factory function actualizada
    'enterprise_validator': create_enterprise_signal_validator  # Factory centralizado
}


def get_validator(validator_type: str, config: Optional[Dict] = None):
    """
    🔍 Obtener instancia de validador específico
    
    Args:
        validator_type: Tipo de validador ('smart_money', 'order_blocks', 'fvg')
        config: Configuración opcional para el validador
    
    Returns:
        Instancia del validador solicitado
    """
    if validator_type not in VALIDATOR_GETTERS:
        raise ValueError(f"Tipo de validador no disponible: {validator_type}. "
                        f"Disponibles: {list(VALIDATOR_GETTERS.keys())}")
    
    getter_func = VALIDATOR_GETTERS[validator_type]
    return getter_func(config)


def create_validation_suite(config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    🎯 Crear suite completa de validadores
    
    Args:
        config: Configuración opcional para todos los validadores
    
    Returns:
        Dict con todos los validadores inicializados
    """
    final_config = DEFAULT_VALIDATION_CONFIG.copy()
    if config:
        final_config.update(config)
    
    suite = {
        'smart_money_validator': get_smart_money_validator(final_config),
        'order_blocks_validator': create_order_blocks_validator(final_config),  # Factory function
        'fvg_validator': create_fvg_validator(final_config),  # Factory function
        'config': final_config,
        'created_at': datetime.now(),
        'version': __version__
    }
    
    return suite


def run_complete_validation(symbol: str, timeframe: str, 
                          validation_period: str = 'short',
                          config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    🚀 Ejecutar validación completa de todos los analizadores
    
    Args:
        symbol: Símbolo a validar (ej: 'EURUSD')
        timeframe: Timeframe a validar (ej: 'H1')
        validation_period: Período de validación ('short', 'medium', 'long')
        config: Configuración opcional
    
    Returns:
        Resultados completos de validación de todos los analizadores
    """
    validation_start = datetime.now()
    
    # Crear suite de validadores
    suite = create_validation_suite(config)
    
    # Ejecutar validaciones
    results = {
        'validation_info': {
            'symbol': symbol,
            'timeframe': timeframe,
            'validation_period': validation_period,
            'started_at': validation_start,
            'suite_version': __version__
        },
        'smart_money_validation': None,
        'order_blocks_validation': None,
        'fvg_validation': None,
        'summary': None,
        'execution_info': None
    }
    
    try:
        # 1. Validación Smart Money
        print(f"🔄 Ejecutando validación Smart Money...")
        sm_validator = suite['smart_money_validator']
        results['smart_money_validation'] = sm_validator.validate_smart_money_accuracy(
            symbol, timeframe, validation_period
        )
        
        # 2. Validación Order Blocks
        print(f"🔄 Ejecutando validación Order Blocks...")
        ob_validator = suite['order_blocks_validator']
        results['order_blocks_validation'] = ob_validator.validate_order_blocks_accuracy(
            symbol, timeframe, validation_period
        )
        
        # 3. Validación FVG
        print(f"🔄 Ejecutando validación FVG...")
        fvg_validator = suite['fvg_validator']
        results['fvg_validation'] = fvg_validator.validate_fvg_accuracy(
            symbol, timeframe, validation_period
        )
        
        # 4. Crear resumen general
        results['summary'] = _create_complete_validation_summary(results)
        
        # 5. Info de ejecución
        results['execution_info'] = {
            'duration': (datetime.now() - validation_start).total_seconds(),
            'completed_at': datetime.now(),
            'validations_executed': 3,
            'all_successful': all([
                results['smart_money_validation'].get('validation_summary', {}).get('validation_status') == 'PASSED',
                results['order_blocks_validation'].get('validation_summary', {}).get('validation_status') == 'PASSED',
                results['fvg_validation'].get('validation_summary', {}).get('validation_status') == 'PASSED'
            ])
        }
        
        print(f"✅ Validación completa finalizada en {results['execution_info']['duration']:.1f}s")
        return results
        
    except Exception as e:
        print(f"❌ Error en validación completa: {e}")
        results['error'] = str(e)
        results['execution_info'] = {
            'duration': (datetime.now() - validation_start).total_seconds(),
            'completed_at': datetime.now(),
            'error': True
        }
        return results


def _create_complete_validation_summary(results: Dict) -> Dict[str, Any]:
    """Crear resumen de validación completa"""
    sm_result = results.get('smart_money_validation', {})
    ob_result = results.get('order_blocks_validation', {})
    fvg_result = results.get('fvg_validation', {})
    
    # Extraer accuracies
    sm_accuracy = sm_result.get('accuracy_metrics', {}).get('overall_accuracy', 0.0)
    ob_accuracy = ob_result.get('accuracy_metrics', {}).get('overall_accuracy', 0.0)
    fvg_accuracy = fvg_result.get('accuracy_metrics', {}).get('overall_accuracy', 0.0)
    
    # Calcular accuracy general
    overall_accuracy = (sm_accuracy + ob_accuracy + fvg_accuracy) / 3 if all([sm_accuracy, ob_accuracy, fvg_accuracy]) else 0.0
    
    # Determinar status general
    sm_status = sm_result.get('validation_summary', {}).get('validation_status', 'FAILED')
    ob_status = ob_result.get('validation_summary', {}).get('validation_status', 'FAILED')
    fvg_status = fvg_result.get('validation_summary', {}).get('validation_status', 'FAILED')
    
    all_passed = all(status == 'PASSED' for status in [sm_status, ob_status, fvg_status])
    overall_status = 'PASSED' if all_passed else 'PARTIAL' if any(status == 'PASSED' for status in [sm_status, ob_status, fvg_status]) else 'FAILED'
    
    return {
        'overall_status': overall_status,
        'overall_accuracy': round(overall_accuracy, 3),
        'individual_results': {
            'smart_money': {'accuracy': sm_accuracy, 'status': sm_status},
            'order_blocks': {'accuracy': ob_accuracy, 'status': ob_status},
            'fvg': {'accuracy': fvg_accuracy, 'status': fvg_status}
        },
        'key_findings': [
            f"Smart Money: {sm_accuracy:.1%} ({sm_status})",
            f"Order Blocks: {ob_accuracy:.1%} ({ob_status})",
            f"FVG: {fvg_accuracy:.1%} ({fvg_status})"
        ],
        'recommendation': _get_overall_recommendation(overall_status, overall_accuracy)
    }


def _get_overall_recommendation(status: str, accuracy: float) -> str:
    """Obtener recomendación general"""
    if status == 'PASSED' and accuracy >= 0.95:
        return "🎯 Excellent validation results. Dashboard analysis is highly accurate across all modules."
    elif status == 'PASSED' and accuracy >= 0.85:
        return "✅ Good validation results. Dashboard analysis is reliable with minor optimization opportunities."
    elif status == 'PARTIAL':
        return "⚠️ Partial validation success. Some modules need attention and optimization."
    else:
        return "❌ Validation concerns detected. Dashboard analysis requires review and optimization."


def get_validation_status_summary() -> Dict[str, Any]:
    """
    📊 Obtener resumen de estado de todos los validadores
    """
    try:
        # Obtener instancias de validadores
        sm_validator = get_smart_money_validator()
        ob_validator = create_order_blocks_validator()  # Factory function
        fvg_validator = create_fvg_validator()  # Factory function
        
        return {
            'smart_money_status': sm_validator.get_validator_status(),
            'order_blocks_status': ob_validator.get_validator_status(),
            'fvg_status': fvg_validator.get_validator_status(),
            'module_info': {
                'version': __version__,
                'available_validators': list(AVAILABLE_VALIDATORS.keys()),
                'last_update': datetime.now()
            }
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'module_info': {
                'version': __version__,
                'available_validators': list(AVAILABLE_VALIDATORS.keys()),
                'last_update': datetime.now()
            }
        }


# Exportar funciones principales
__all__ = [
    # Validadores
    'SmartMoneyValidatorEnterprise',  # Clase actualizada
    'OrderBlocksValidatorEnterprise',  # Clase actualizada
    'FVGValidatorEnterprise',  # Clase actualizada
    'EnterpriseSignalValidator',  # Validador centralizado
    
    # Funciones de conveniencia
    'get_validator',
    'create_smart_money_validator',  # Factory function actualizada
    'create_order_blocks_validator',  # Factory function actualizada
    'create_fvg_validator',  # Factory function actualizada
    'create_enterprise_signal_validator',  # Factory centralizado
    
    # Suite completa
    'create_validation_suite',
    'run_complete_validation',
    'get_validation_status_summary',
    
    # Configuración
    'DEFAULT_VALIDATION_CONFIG',
    'AVAILABLE_VALIDATORS',
    
    # Meta
    '__version__'
]


if __name__ == "__main__":
    # Test básico del módulo
    print(f"🚀 Testing Validation Analyzers v{__version__}...")
    
    try:
        # Test suite creation
        suite = create_validation_suite()
        print(f"✅ Suite de validadores creada correctamente")
        
        # Test status summary
        status = get_validation_status_summary()
        print(f"📊 Status summary obtenido correctamente")
        
        # Test validación rápida
        print(f"🔍 Ejecutando validación completa...")
        results = run_complete_validation('EURUSD', 'H1', 'short')
        print(f"✅ Validación completa: {results['summary']['overall_status']} - {results['summary']['overall_accuracy']:.1%}")
        
    except Exception as e:
        print(f"❌ Error en testing: {e}")