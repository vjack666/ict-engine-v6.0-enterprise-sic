#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔇 SILENT MODE MANAGER - ICT ENGINE v6.0 ENTERPRISE
==================================================

Gestor de modo silencioso para todo el sistema de logging.
Controla todos los loggers del sistema para un dashboard limpio.

Autor: ICT Engine v6.0 Team
"""

import logging
import sys
from typing import List, Dict, Any

class SilentModeManager:
    """🔇 Gestor centralizado del modo silencioso"""
    
    def __init__(self):
        self.original_handlers: Dict[str, List[logging.Handler]] = {}
        self.silent_mode_active = False
        
    def activate_silent_mode(self):
        """🔇 Activar modo silencioso para todo el sistema"""
        if self.silent_mode_active:
            return
            
        # Obtener el logger raíz
        root_logger = logging.getLogger()
        
        # Guardar handlers originales
        self.original_handlers['root'] = root_logger.handlers.copy()
        
        # Obtener todos los loggers activos
        loggers_to_silence = [
            '',  # Logger raíz
            'ImportCenter',
            'AdvancedCandleDownloader',
            'ICT_Engine',
            'ICT_SYSTEM',
            'ICT_DASHBOARD', 
            'ICT_PATTERNS',
            'ICT_TRADING',
            'ICT_GENERAL'
        ]
        
        for logger_name in loggers_to_silence:
            logger = logging.getLogger(logger_name)
            
            # Guardar handlers originales
            if logger_name not in self.original_handlers:
                self.original_handlers[logger_name] = logger.handlers.copy()
            
            # Remover handlers de consola
            console_handlers = [
                h for h in logger.handlers 
                if isinstance(h, logging.StreamHandler) and h.stream in (sys.stdout, sys.stderr)
            ]
            
            for handler in console_handlers:
                logger.removeHandler(handler)
        
        # Configurar nivel mínimo para reducir logs
        root_logger.setLevel(logging.WARNING)
        
        self.silent_mode_active = True
        print("🔇 Modo silencioso activado - logs solo en archivos")
    
    def deactivate_silent_mode(self):
        """🔊 Desactivar modo silencioso y restaurar handlers"""
        if not self.silent_mode_active:
            return
            
        # Restaurar handlers originales
        for logger_name, handlers in self.original_handlers.items():
            logger = logging.getLogger(logger_name)
            
            # Limpiar handlers actuales
            logger.handlers.clear()
            
            # Restaurar handlers originales
            for handler in handlers:
                logger.addHandler(handler)
        
        # Restaurar nivel del logger raíz
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        self.silent_mode_active = False
        self.original_handlers.clear()
        print("🔊 Modo silencioso desactivado - logs restaurados")
    
    def is_silent(self) -> bool:
        """🔇 Verificar si el modo silencioso está activo"""
        return self.silent_mode_active
    
    def apply_to_new_loggers(self):
        """🔇 Aplicar modo silencioso a nuevos loggers que se creen"""
        if not self.silent_mode_active:
            return
            
        # Esta función puede ser llamada periódicamente para capturar nuevos loggers
        all_loggers = [logging.getLogger(name) for name in logging.Logger.manager.loggerDict]
        
        for logger in all_loggers:
            if logger.name not in self.original_handlers:
                # Nuevo logger detectado
                self.original_handlers[logger.name] = logger.handlers.copy()
                
                # Remover handlers de consola
                console_handlers = [
                    h for h in logger.handlers 
                    if isinstance(h, logging.StreamHandler) and h.stream in (sys.stdout, sys.stderr)
                ]
                
                for handler in console_handlers:
                    logger.removeHandler(handler)

# Instancia global del gestor
silent_manager = SilentModeManager()

def activate_global_silent_mode():
    """🔇 Función helper para activar modo silencioso"""
    silent_manager.activate_silent_mode()

def deactivate_global_silent_mode():
    """🔊 Función helper para desactivar modo silencioso"""
    silent_manager.deactivate_silent_mode()

def is_silent_mode_active() -> bool:
    """🔇 Verificar si está en modo silencioso"""
    return silent_manager.is_silent()

if __name__ == "__main__":
    # Test del sistema
    print("🧪 Probando Silent Mode Manager...")
    
    # Crear algunos loggers de prueba
    test_logger1 = logging.getLogger("TestLogger1")
    test_logger2 = logging.getLogger("TestLogger2")
    
    # Configurar handlers de consola
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(name)s] %(message)s')
    handler.setFormatter(formatter)
    
    test_logger1.addHandler(handler)
    test_logger2.addHandler(handler)
    test_logger1.setLevel(logging.INFO)
    test_logger2.setLevel(logging.INFO)
    
    print("\n📝 Logs antes del modo silencioso:")
    test_logger1.info("Este mensaje debería aparecer")
    test_logger2.info("Este también debería aparecer")
    
    print("\n🔇 Activando modo silencioso...")
    activate_global_silent_mode()
    
    print("\n📝 Logs durante modo silencioso:")
    test_logger1.info("Este mensaje NO debería aparecer")
    test_logger2.info("Este tampoco debería aparecer")
    
    print("\n🔊 Desactivando modo silencioso...")
    deactivate_global_silent_mode()
    
    print("\n📝 Logs después del modo silencioso:")
    test_logger1.info("Este mensaje debería aparecer de nuevo")
    test_logger2.info("Este también debería aparecer de nuevo")
    
    print("\n✅ Test completado")
