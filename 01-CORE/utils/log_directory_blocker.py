#!/usr/bin/env python3
"""
Patch para evitar la creación automática de carpetas de logs vacías.

Este módulo intercepta y modifica las llamadas a mkdir() que crean
carpetas de logs innecesarias que permanecen vacías.
"""

import os
from pathlib import Path
from typing import Set

# Lista de patrones de carpetas que NO deben crearse automáticamente
BLOCKED_LOG_PATTERNS = {
    'logs/daily', 'logs/dashboard', 'logs/debug', 'logs/errors', 
    'logs/ict', 'logs/metrics', 'logs/mt5', 'logs/poi', 
    'logs/structured', 'logs/tct', 'logs/terminal_capture', 'logs/trading'
}

# Rutas específicas que NO deben crearse
BLOCKED_PATHS = {
    'data/logs/daily', 'data/logs/dashboard', 'data/logs/debug', 'data/logs/errors',
    'data/logs/ict', 'data/logs/metrics', 'data/logs/mt5', 'data/logs/poi',
    'data/logs/structured', 'data/logs/tct', 'data/logs/terminal_capture', 'data/logs/trading',
    
    '01-CORE/analysis/data/logs/daily', '01-CORE/analysis/data/logs/dashboard',
    '01-CORE/analysis/data/logs/debug', '01-CORE/analysis/data/logs/errors',
    '01-CORE/analysis/data/logs/ict', '01-CORE/analysis/data/logs/metrics',
    '01-CORE/analysis/data/logs/mt5', '01-CORE/analysis/data/logs/poi',
    '01-CORE/analysis/data/logs/structured', '01-CORE/analysis/data/logs/tct',
    '01-CORE/analysis/data/logs/terminal_capture', '01-CORE/analysis/data/logs/trading',
    
    '01-CORE/data/logs/daily', '01-CORE/data/logs/dashboard',
    '01-CORE/data/logs/debug', '01-CORE/data/logs/errors',
    '01-CORE/data/logs/ict', '01-CORE/data/logs/metrics',
    '01-CORE/data/logs/mt5', '01-CORE/data/logs/poi',
    '01-CORE/data/logs/structured', '01-CORE/data/logs/tct',
    '01-CORE/data/logs/terminal_capture', '01-CORE/data/logs/trading',
    
    '01-CORE/trading/data/logs/daily', '01-CORE/trading/data/logs/dashboard',
    '01-CORE/trading/data/logs/debug', '01-CORE/trading/data/logs/errors',
    '01-CORE/trading/data/logs/ict', '01-CORE/trading/data/logs/metrics',
    '01-CORE/trading/data/logs/mt5', '01-CORE/trading/data/logs/poi',
    '01-CORE/trading/data/logs/structured', '01-CORE/trading/data/logs/tct',
    '01-CORE/trading/data/logs/terminal_capture', '01-CORE/trading/data/logs/trading',
    
    '09-DASHBOARD/core/tabs/data/logs/daily', '09-DASHBOARD/core/tabs/data/logs/dashboard',
    '09-DASHBOARD/core/tabs/data/logs/debug', '09-DASHBOARD/core/tabs/data/logs/errors',
    '09-DASHBOARD/core/tabs/data/logs/ict', '09-DASHBOARD/core/tabs/data/logs/metrics',
    '09-DASHBOARD/core/tabs/data/logs/mt5', '09-DASHBOARD/core/tabs/data/logs/poi',
    '09-DASHBOARD/core/tabs/data/logs/structured', '09-DASHBOARD/core/tabs/data/logs/tct',
    '09-DASHBOARD/core/tabs/data/logs/terminal_capture', '09-DASHBOARD/core/tabs/data/logs/trading',
    
    '09-DASHBOARD/data/logs/daily', '09-DASHBOARD/data/logs/dashboard',
    '09-DASHBOARD/data/logs/debug', '09-DASHBOARD/data/logs/errors',
    '09-DASHBOARD/data/logs/ict', '09-DASHBOARD/data/logs/metrics',
    '09-DASHBOARD/data/logs/mt5', '09-DASHBOARD/data/logs/poi',
    '09-DASHBOARD/data/logs/structured', '09-DASHBOARD/data/logs/tct',
    '09-DASHBOARD/data/logs/terminal_capture', '09-DASHBOARD/data/logs/trading',
    
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/daily',
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/dashboard',
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/debug',
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/errors',
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/ict',
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/metrics',
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/mt5',
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/poi',
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/structured',
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/tct',
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/terminal_capture',
    '09-DASHBOARD/patterns_analysis/individual_patterns/data/logs/trading',
    
    '09-DASHBOARD/widgets/data/logs'
}

def should_block_path(path: Path) -> bool:
    """
    Determinar si una ruta debe ser bloqueada para evitar crear carpetas vacías.
    
    Args:
        path: Ruta a verificar
        
    Returns:
        True si la ruta debe ser bloqueada
    """
    path_str = str(path).replace('\\', '/')
    
    # Verificar patrones específicos
    for blocked_path in BLOCKED_PATHS:
        if blocked_path in path_str:
            return True
    
    # Verificar patrones generales
    for pattern in BLOCKED_LOG_PATTERNS:
        if pattern in path_str:
            return True
    
    return False

def safe_mkdir(path: Path, parents: bool = False, exist_ok: bool = False) -> bool:
    """
    Versión segura de mkdir que no crea carpetas de logs innecesarias.
    
    Args:
        path: Ruta a crear
        parents: Crear directorios padre
        exist_ok: No fallar si ya existe
        
    Returns:
        True si se creó o ya existía, False si se bloqueó
    """
    if should_block_path(path):
        # Solo imprimir advertencia si está en modo debug
        if os.environ.get('ICT_DEBUG_MKDIR'):
            print(f"🚫 [BLOCKED] Prevented creation of empty log directory: {path}")
        return False
    
    # Crear normalmente
    try:
        path.mkdir(parents=parents, exist_ok=exist_ok)
        return True
    except Exception:
        return False

def patch_pathlib():
    """
    Parchar pathlib.Path.mkdir para usar nuestra versión segura.
    Solo se activa si está habilitado el parche.
    """
    if not os.environ.get('ICT_ENABLE_MKDIR_PATCH'):
        return
    
    # Guardar el mkdir original
    original_mkdir = Path.mkdir
    
    def patched_mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """Versión parchada de mkdir"""
        if should_block_path(self):
            if os.environ.get('ICT_DEBUG_MKDIR'):
                print(f"🚫 [BLOCKED] mkdir({self})")
            return
        return original_mkdir(self, mode, parents, exist_ok)
    
    # Aplicar el parche
    Path.mkdir = patched_mkdir
    
    if os.environ.get('ICT_DEBUG_MKDIR'):
        print("✅ [PATCH] mkdir patch applied to prevent empty log directories")

# Aplicar automáticamente el parche si está habilitado
patch_pathlib()