"""
🔍 VALIDATION ANALYZERS - ICT ENGINE v6.0 ENTERPRISE
===================================================

Módulo de analizadores de validación que comparan
resultados entre dashboard live y backtesting histórico.
"""

from typing import Dict, Any, Optional
from datetime import datetime

# Imports principales
try:
    from .smart_money_validator import SmartMoneyValidator, SmartMoneyValidatorEnterprise, create_smart_money_validator
except ImportError:
    SmartMoneyValidator = None
    SmartMoneyValidatorEnterprise = None
    create_smart_money_validator = None

try:
    from .order_blocks_validator import OrderBlocksValidatorEnterprise, create_order_blocks_validator
except ImportError:
    OrderBlocksValidatorEnterprise = None
    create_order_blocks_validator = None

try:
    from .fvg_validator import FVGValidatorEnterprise, create_fvg_validator
except ImportError:
    FVGValidatorEnterprise = None
    create_fvg_validator = None

try:
    from .enterprise_signal_validator import EnterpriseSignalValidator, create_enterprise_signal_validator
except ImportError:
    EnterpriseSignalValidator = None
    create_enterprise_signal_validator = None

# Validator registry
VALIDATOR_CLASSES = {
    'smart_money': SmartMoneyValidatorEnterprise,
    'order_blocks': OrderBlocksValidatorEnterprise,
    'fvg': FVGValidatorEnterprise,
    'enterprise_signal': EnterpriseSignalValidator
}

def get_validator(validator_type: str, config: Optional[Dict] = None):
    """Obtener instancia de validador específico"""
    validator_class = VALIDATOR_CLASSES.get(validator_type)
    if validator_class is None:
        raise ValueError(f"Validator type '{validator_type}' not found")
    return validator_class(config)

# Exports
__all__ = [
    'SmartMoneyValidator',
    'SmartMoneyValidatorEnterprise', 
    'OrderBlocksValidatorEnterprise',
    'FVGValidatorEnterprise',
    'EnterpriseSignalValidator',
    'get_validator',
    'VALIDATOR_CLASSES'
]