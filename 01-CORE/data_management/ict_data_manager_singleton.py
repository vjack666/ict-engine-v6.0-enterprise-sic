#!/usr/bin/env python3
"""
🔧 ICT DATA MANAGER SINGLETON
============================

Wrapper singleton para ICTDataManager que evita múltiples inicializaciones
y optimiza el rendimiento del sistema para trading real.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 2025-09-10
"""

from protocols.unified_logging import get_unified_logger
import threading
from typing import Optional
from .ict_data_manager import ICTDataManager

class ICTDataManagerSingleton:
    """🔧 Singleton para ICTDataManager - Una sola instancia para todo el sistema"""
    
    _instance: Optional[ICTDataManager] = None
    _lock = threading.Lock()
    _initialized = False
    
    @classmethod
    def get_instance(cls, downloader=None) -> ICTDataManager:
        """
        Obtiene la instancia singleton de ICTDataManager
        
        Args:
            downloader: Downloader a usar (solo en primera inicialización)
            
        Returns:
            ICTDataManager: Instancia singleton
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    print("🔧 Creando nueva instancia ICTDataManager singleton...")
                    cls._instance = ICTDataManager(downloader)
                    
                    # Inicializar solo una vez
                    if not cls._initialized:
                        cls._instance.initialize()
                        cls._initialized = True
                        print("✅ ICTDataManager singleton inicializado")
                    
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """🧹 Reinicia la instancia singleton (para testing o cleanup)"""
        with cls._lock:
            if cls._instance:
                # Cleanup de la instancia anterior
                try:
                    cls._instance.__del__()
                except:
                    pass
            cls._instance = None
            cls._initialized = False
            print("🔄 ICTDataManager singleton reiniciado")
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Verifica si la instancia singleton está inicializada"""
        return cls._instance is not None and cls._initialized

# Función de conveniencia para obtener la instancia
def get_ict_data_manager(downloader=None) -> ICTDataManager:
    """
    Función de conveniencia para obtener la instancia singleton de ICTDataManager
    
    Args:
        downloader: Downloader a usar (opcional)
        
    Returns:
        ICTDataManager: Instancia singleton
    """
    return ICTDataManagerSingleton.get_instance(downloader)
