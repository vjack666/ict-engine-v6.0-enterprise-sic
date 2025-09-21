"""
CHoCH Historical Memory Configuration - Centralized
Configuración unificada para todas las integraciones CHoCH
"""

from typing import Dict, Any, Optional

# 🚀 Configuración CHoCH unificada para todos los detectores
CHOCH_DEFAULT_CONFIG: Dict[str, Any] = {
    'enabled': True,
    'min_historical_periods': 20,
    'confidence_boost_factor': 0.15,
    'max_historical_samples': 1000,
    'success_rate_threshold': 0.6,
    'cache_enabled': True,
    'cache_ttl_seconds': 300,  # 5 minutos
    'low_memory_mode': {
        'max_samples': 200,
        'retention_days': 30,
        'cache_ttl_seconds': 60  # 1 minuto
    }
}

# 🧠 Configuraciones específicas por detector
DETECTOR_SPECIFIC_CONFIG: Dict[str, Dict[str, Any]] = {
    'FVG': {
        'confidence_boost_factor': 0.12,  # Más conservador para FVG
        'min_historical_periods': 15
    },
    'BOS': {
        'confidence_boost_factor': 0.18,  # Más agresivo para BOS
        'min_historical_periods': 25
    },
    'MSS': {
        'confidence_boost_factor': 0.15,
        'min_historical_periods': 30
    },
    'ORDER_BLOCK': {
        'confidence_boost_factor': 0.20,
        'min_historical_periods': 20
    },
    'LIQUIDITY_GRAB': {
        'confidence_boost_factor': 0.16,
        'min_historical_periods': 18
    },
    'JUDAS_SWING': {
        'confidence_boost_factor': 0.14,
        'min_historical_periods': 22
    }
}


def get_choch_config(detector_type: str = 'DEFAULT', low_memory: bool = False) -> Dict[str, Any]:
    """
    Obtener configuración CHoCH específica para un detector
    
    Args:
        detector_type: Tipo de detector (FVG, BOS, MSS, etc.)
        low_memory: Si True, aplica configuración optimizada para memoria
        
    Returns:
        Diccionario con configuración CHoCH específica
    """
    # Comenzar con config base
    config = CHOCH_DEFAULT_CONFIG.copy()
    
    # Aplicar configuración específica del detector si existe
    if detector_type in DETECTOR_SPECIFIC_CONFIG:
        config.update(DETECTOR_SPECIFIC_CONFIG[detector_type])
    
    # Aplicar optimizaciones low-memory si están habilitadas
    if low_memory:
        config.update(config['low_memory_mode'])
    
    return config


def is_choch_enabled_for_detector(detector_type: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Verificar si CHoCH está habilitado para un detector específico
    
    Args:
        detector_type: Tipo de detector
        config: Configuración personalizada (opcional)
        
    Returns:
        True si CHoCH está habilitado
    """
    if config is None:
        config = get_choch_config(detector_type)
    
    return config.get('enabled', True)


def get_confidence_boost_factor(detector_type: str, low_memory: bool = False) -> float:
    """
    Obtener factor de boost de confianza específico para un detector
    
    Args:
        detector_type: Tipo de detector
        low_memory: Modo de memoria reducida
        
    Returns:
        Factor de boost (0.0 - 1.0)
    """
    config = get_choch_config(detector_type, low_memory)
    return float(config.get('confidence_boost_factor', 0.15))