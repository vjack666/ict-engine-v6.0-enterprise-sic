#!/usr/bin/env python3
"""
🔥 LOGGING MODULE v6.0 ENTERPRISE - ORDER BLOCKS SPECIALIZED
===========================================================

Módulo especializado de logging para Order Blocks detection, validation y dashboard integration.
Proporciona logging estructurado y auditoría completa del sistema Order Blocks.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 12 Septiembre 2025
"""

from .order_blocks_black_box import OrderBlocksBlackBox, get_order_blocks_black_box

__all__ = [
    'OrderBlocksBlackBox',
    'get_order_blocks_black_box'
]