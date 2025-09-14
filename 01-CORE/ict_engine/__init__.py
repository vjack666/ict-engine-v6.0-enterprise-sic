#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏗️ ICT ENGINE MODULE - ICT ENGINE v6.0 ENTERPRISE
=================================================

Módulo principal del motor ICT para análisis de patrones institucionales.
Incluye detección de patrones, análisis de estructura de mercado y herramientas ICT.

Componentes:
- ICTPatternDetector: Detector de patrones ICT
- OrderBlocksBlackBox: Sistema de Order Blocks
- Otras herramientas de análisis ICT

Autor: ICT Engine v6.0 Team
Fecha: 13 Septiembre 2025
"""

# Importaciones principales
try:
    from .pattern_detector import ICTPatternDetector
    PATTERN_DETECTOR_AVAILABLE = True
except ImportError:
    ICTPatternDetector = None
    PATTERN_DETECTOR_AVAILABLE = False

try:
    from .order_blocks_black_box import OrderBlocksBlackBox
    ORDER_BLOCKS_AVAILABLE = True
except ImportError:
    OrderBlocksBlackBox = None
    ORDER_BLOCKS_AVAILABLE = False

# Exportaciones del módulo
__all__ = [
    'ICTPatternDetector',
    'OrderBlocksBlackBox',
    'PATTERN_DETECTOR_AVAILABLE',
    'ORDER_BLOCKS_AVAILABLE'
]

# Información del módulo
__version__ = "6.0.0"
__author__ = "ICT Engine v6.0 Team"
__description__ = "Motor ICT para análisis de patrones institucionales"

def get_available_components():
    """
    Obtener componentes disponibles del módulo ICT Engine
    
    Returns:
        Dict[str, bool]: Diccionario con disponibilidad de componentes
    """
    return {
        'ICTPatternDetector': PATTERN_DETECTOR_AVAILABLE,
        'OrderBlocksBlackBox': ORDER_BLOCKS_AVAILABLE
    }