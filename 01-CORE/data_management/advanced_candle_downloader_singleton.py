#!/usr/bin/env python3
"""
🔧 ADVANCED CANDLE DOWNLOADER SINGLETON
=======================================

Wrapper singleton para AdvancedCandleDownloader que evita múltiples inicializaciones
y optimiza el rendimiento del sistema para trading real.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 2025-09-10
"""

import threading
from typing import Optional
from .advanced_candle_downloader import AdvancedCandleDownloader

class AdvancedCandleDownloaderSingleton:
    """🔧 Singleton para AdvancedCandleDownloader - Una sola instancia para todo el sistema"""
    
    _instance: Optional[AdvancedCandleDownloader] = None
    _lock = threading.Lock()
    _initialized = False
    
    @classmethod
    def get_instance(cls, config=None) -> AdvancedCandleDownloader:
        """
        Obtiene la instancia singleton de AdvancedCandleDownloader
        
        Args:
            config: Configuración a usar (solo en primera inicialización)
            
        Returns:
            AdvancedCandleDownloader: Instancia singleton
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    if not cls._initialized:
                        print("🔧 Creando nueva instancia AdvancedCandleDownloader singleton...")
                    cls._instance = AdvancedCandleDownloader(config=config)
                    cls._initialized = True
                    
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """🧹 Reinicia la instancia singleton (para testing o cleanup)"""
        with cls._lock:
            if cls._instance:
                # Cleanup de la instancia anterior
                try:
                    if hasattr(cls._instance, 'stop_download'):
                        cls._instance.stop_download()
                except:
                    pass
            cls._instance = None
            cls._initialized = False
            print("🔄 AdvancedCandleDownloader singleton reiniciado")
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Verifica si la instancia singleton está inicializada"""
        return cls._instance is not None and cls._initialized

# Función de conveniencia para obtener la instancia
def get_advanced_candle_downloader(config=None) -> AdvancedCandleDownloader:
    """
    Función de conveniencia para obtener la instancia singleton de AdvancedCandleDownloader
    
    Args:
        config: Configuración a usar (opcional)
        
    Returns:
        AdvancedCandleDownloader: Instancia singleton
    """
    return AdvancedCandleDownloaderSingleton.get_instance(config)
