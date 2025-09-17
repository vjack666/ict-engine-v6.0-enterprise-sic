#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ LAZY LOADER - ICT ENGINE v6.0 ENTERPRISE
==========================================

Sistema de carga perezosa para módulos pesados que optimiza
el uso de memoria cargando componentes solo cuando se necesitan.
"""

import sys
import threading
import weakref
from typing import Dict, Any, Optional, Callable, Type
from pathlib import Path

# Añadir rutas
sys.path.append('01-CORE')

class LazyModule:
    """Wrapper para carga perezosa de módulos"""
    
    def __init__(self, module_name: str, import_callable: Callable, *args, **kwargs):
        self.module_name = module_name
        self.import_callable = import_callable
        self.args = args
        self.kwargs = kwargs
        self._instance = None
        self._lock = threading.Lock()
        self.load_count = 0
        
    def _load(self):
        """Cargar el módulo realmente"""
        if self._instance is None:
            with self._lock:
                if self._instance is None:  # Double-check locking
                    print(f"⚡ Lazy loading {self.module_name}...")
                    self._instance = self.import_callable(*self.args, **self.kwargs)
                    self.load_count += 1
                    print(f"✅ {self.module_name} cargado (load #{self.load_count})")
        return self._instance
    
    def __getattr__(self, name: str):
        """Interceptar acceso a atributos y cargar si es necesario"""
        instance = self._load()
        return getattr(instance, name)
    
    def __call__(self, *args, **kwargs):
        """Interceptar llamadas y cargar si es necesario"""
        instance = self._load()
        return instance(*args, **kwargs)
    
    @property
    def is_loaded(self) -> bool:
        """Verificar si el módulo está cargado"""
        return self._instance is not None
    
    def unload(self):
        """Descargar el módulo para liberar memoria"""
        with self._lock:
            if self._instance is not None:
                print(f"🗑️ Descargando {self.module_name} para liberar memoria...")
                # Intentar cleanup si existe
                if hasattr(self._instance, 'cleanup'):
                    try:
                        self._instance.cleanup()
                    except:
                        pass
                self._instance = None
                print(f"✅ {self.module_name} descargado")
    
    def reload(self):
        """Recargar el módulo"""
        self.unload()
        return self._load()

class LazySmartMoneyAnalyzer(LazyModule):
    """Lazy loader específico para SmartMoneyAnalyzer (el mayor consumidor de memoria)"""
    
    def __init__(self):
        def load_smart_money():
            from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
            return SmartMoneyAnalyzer()
        
        super().__init__(
            module_name="SmartMoneyAnalyzer", 
            import_callable=load_smart_money
        )

class LazyUnifiedMemorySystem(LazyModule):
    """Lazy loader para UnifiedMemorySystem"""
    
    def __init__(self):
        def load_unified_memory():
            # Intentar importar el sistema de memoria unificada
            try:
                from unified_memory.unified_memory_system import UnifiedMemorySystem
                return UnifiedMemorySystem()
            except ImportError:
                # Fallback si no existe
                return None
        
        super().__init__(
            module_name="UnifiedMemorySystem",
            import_callable=load_unified_memory
        )

class LazyMT5Connection(LazyModule):
    """Lazy loader para MT5 Connection"""
    
    def __init__(self):
        def load_mt5():
            from data_management.mt5_connection_manager import get_mt5_connection
            return get_mt5_connection()
        
        super().__init__(
            module_name="MT5ConnectionManager",
            import_callable=load_mt5
        )

class MemoryAwareLazyLoader:
    """Sistema de carga perezosa consciente de la memoria"""
    
    def __init__(self, memory_limit_mb: float = 100.0):
        self.memory_limit_mb = memory_limit_mb
        self.lazy_modules: Dict[str, LazyModule] = {}
        self._lock = threading.Lock()
        
    def register_lazy_module(self, name: str, lazy_module: LazyModule):
        """Registrar un módulo lazy"""
        with self._lock:
            self.lazy_modules[name] = lazy_module
            
    def get_module(self, name: str) -> Optional[LazyModule]:
        """Obtener un módulo lazy por nombre"""
        return self.lazy_modules.get(name)
    
    def check_memory_and_unload(self):
        """Verificar memoria y descargar módulos si es necesario"""
        try:
            import psutil
            current_memory_mb = psutil.Process().memory_info().rss / (1024 * 1024)
            
            if current_memory_mb > self.memory_limit_mb:
                print(f"⚠️ Memoria alta ({current_memory_mb:.1f}MB > {self.memory_limit_mb:.1f}MB)")
                # Descargar módulos menos críticos
                modules_to_unload = ['UnifiedMemorySystem', 'SmartMoneyAnalyzer']
                
                for module_name in modules_to_unload:
                    if module_name in self.lazy_modules:
                        lazy_module = self.lazy_modules[module_name]
                        if lazy_module.is_loaded:
                            lazy_module.unload()
                            
                # Forzar garbage collection
                import gc
                gc.collect()
                
                new_memory_mb = psutil.Process().memory_info().rss / (1024 * 1024)
                freed_mb = current_memory_mb - new_memory_mb
                print(f"✅ Memoria liberada: {freed_mb:.1f}MB")
        
        except Exception as e:
            print(f"⚠️ Error en verificación de memoria: {e}")
    
    def get_loaded_modules_info(self) -> Dict[str, Dict[str, Any]]:
        """Obtener información de módulos cargados"""
        info = {}
        for name, lazy_module in self.lazy_modules.items():
            info[name] = {
                'loaded': lazy_module.is_loaded,
                'load_count': lazy_module.load_count
            }
        return info

# Instancia global del sistema lazy loading
_global_lazy_loader = MemoryAwareLazyLoader(memory_limit_mb=80.0)  # 80MB límite

# Registrar módulos lazy
_global_lazy_loader.register_lazy_module('SmartMoneyAnalyzer', LazySmartMoneyAnalyzer())
_global_lazy_loader.register_lazy_module('UnifiedMemorySystem', LazyUnifiedMemorySystem()) 
_global_lazy_loader.register_lazy_module('MT5ConnectionManager', LazyMT5Connection())

def get_lazy_smart_money_analyzer():
    """Obtener SmartMoneyAnalyzer con lazy loading"""
    return _global_lazy_loader.get_module('SmartMoneyAnalyzer')

def get_lazy_unified_memory_system():
    """Obtener UnifiedMemorySystem con lazy loading"""
    return _global_lazy_loader.get_module('UnifiedMemorySystem')

def get_lazy_mt5_connection():
    """Obtener MT5Connection con lazy loading"""
    return _global_lazy_loader.get_module('MT5ConnectionManager')

def check_memory_usage():
    """Verificar uso de memoria y limpiar si es necesario"""
    _global_lazy_loader.check_memory_and_unload()

def get_lazy_loader_status():
    """Obtener estado del lazy loader"""
    return _global_lazy_loader.get_loaded_modules_info()

if __name__ == "__main__":
    print("⚡ Lazy Loader - ICT Engine v6.0 Enterprise")
    print("=" * 50)
    
    # Demostrar lazy loading
    print("📊 Estado inicial:")
    print(get_lazy_loader_status())
    
    print("\n⚡ Accediendo a SmartMoneyAnalyzer...")
    sma = get_lazy_smart_money_analyzer()
    # Intentar acceder a un método
    try:
        if hasattr(sma, 'analyze_market_structure'):
            print("✅ SmartMoneyAnalyzer listo para usar")
    except:
        print("⚠️ SmartMoneyAnalyzer no completamente cargado")
    
    print("\n📊 Estado después de carga:")
    print(get_lazy_loader_status())
    
    print("\n🧹 Verificando memoria...")
    check_memory_usage()
    
    print("\n📊 Estado final:")
    print(get_lazy_loader_status())