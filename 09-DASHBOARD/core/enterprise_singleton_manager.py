#!/usr/bin/env python3
"""
🏭 ENTERPRISE PATTERN SINGLETON MANAGER
======================================

Gestión centralizada de instancias singleton para optimización enterprise.
Evita la creación masiva de instancias duplicadas durante el inicio del dashboard.

Características Enterprise:
- ✅ Singleton estricto para Smart Money Analyzer
- ✅ Factory Pattern con cache para Pattern Detectors  
- ✅ UnifiedMemorySystem como singleton global
- ✅ Lazy loading para componentes pesados
- ✅ Pool de conexiones MT5 optimizado

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 10 de Septiembre, 2025
Versión: v1.0.0-enterprise
"""

import threading
from typing import Dict, Any, Optional, Callable, TypeVar, Type
import weakref
from pathlib import Path
import sys

# Configurar paths
project_root = Path(__file__).parent.parent.parent
core_path = project_root / "01-CORE"
sys.path.extend([str(project_root), str(core_path)])

T = TypeVar('T')

class EnterpriseSingletonManager:
    """🏭 Gestor centralizado de singletons enterprise"""
    
    _instances: Dict[str, Any] = {}
    _lock = threading.RLock()
    _weak_refs: Dict[str, Any] = {}
    
    @classmethod
    def get_singleton(cls, key: str, factory: Callable[[], T], *args, **kwargs) -> T:
        """
        Obtener o crear singleton de manera thread-safe
        
        Args:
            key: Clave única para el singleton
            factory: Factory function para crear la instancia
            *args, **kwargs: Argumentos para el factory
            
        Returns:
            Instancia singleton
        """
        if key not in cls._instances:
            with cls._lock:
                # Double-check locking pattern
                if key not in cls._instances:
                    print(f"🏭 [SINGLETON] Creando nueva instancia: {key}")
                    instance = factory(*args, **kwargs)
                    cls._instances[key] = instance
                    cls._weak_refs[key] = weakref.ref(instance)
                else:
                    print(f"♻️  [SINGLETON] Reutilizando instancia existente: {key}")
        else:
            print(f"♻️  [SINGLETON] Retornando instancia existente: {key}")
            
        return cls._instances[key]
    
    @classmethod
    def get_smart_money_analyzer(cls):
        """🧠 Obtener Smart Money Analyzer singleton"""
        def create_analyzer():
            try:
                from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
                print("💰 [SINGLETON] Inicializando Smart Money Concepts Analyzer v6.0 Enterprise...")
                return SmartMoneyAnalyzer()
            except ImportError as e:
                print(f"⚠️ [SINGLETON] Smart Money Analyzer no disponible: {e}")
                return None
                
        return cls.get_singleton('smart_money_analyzer', create_analyzer)
    
    @classmethod 
    def get_pattern_detector(cls, config: Optional[Dict[str, Any]] = None):
        """🔍 Obtener Pattern Detector singleton"""
        config_key = str(hash(str(config))) if config else 'default'
        key = f'pattern_detector_{config_key}'
        
        def create_detector():
            try:
                from analysis.pattern_detector import PatternDetector
                print("🎯 [SINGLETON] Inicializando Pattern Detector Enterprise v6.0...")
                return PatternDetector()
            except ImportError as e:
                print(f"⚠️ [SINGLETON] Pattern Detector no disponible: {e}")
                return None
                
        return cls.get_singleton(key, create_detector)
    
    @classmethod
    def get_unified_memory_system(cls):
        """🧠 Obtener Unified Memory System singleton"""
        def create_memory_system():
            try:
                from analysis.unified_memory_system import UnifiedMemorySystem
                print("🧠 [SINGLETON] Inicializando Unified Memory System v6.1...")
                return UnifiedMemorySystem()
            except ImportError as e:
                print(f"⚠️ [SINGLETON] Unified Memory System no disponible: {e}")
                return None
                
        return cls.get_singleton('unified_memory_system', create_memory_system)
    
    @classmethod
    def get_ict_data_manager(cls):
        """📊 Obtener ICT Data Manager singleton"""
        def create_data_manager():
            try:
                from data_management.ict_data_manager_singleton import get_ict_data_manager
                print("📊 [SINGLETON] Obteniendo ICT Data Manager singleton...")
                return get_ict_data_manager()
            except ImportError as e:
                print(f"⚠️ [SINGLETON] ICT Data Manager no disponible: {e}")
                return None
                
        return cls.get_singleton('ict_data_manager', create_data_manager)
    
    @classmethod
    def get_mt5_data_manager(cls):
        """📈 Obtener MT5 Data Manager singleton"""
        def create_mt5_manager():
            try:
                from data_management.mt5_data_manager import MT5DataManager
                print("📈 [SINGLETON] Inicializando MT5 Data Manager...")
                return MT5DataManager()
            except ImportError as e:
                print(f"⚠️ [SINGLETON] MT5 Data Manager no disponible: {e}")
                return None
                
        return cls.get_singleton('mt5_data_manager', create_mt5_manager)
    
    @classmethod
    def get_multi_timeframe_analyzer(cls):
        """⏰ Obtener Multi-Timeframe Analyzer singleton"""
        def create_analyzer():
            try:
                from analysis.multi_timeframe_analyzer import OptimizedICTAnalysisEnterprise
                print("⏰ [SINGLETON] Inicializando Multi-Timeframe Analyzer Enterprise v6.0...")
                return OptimizedICTAnalysisEnterprise()
            except ImportError as e:
                print(f"⚠️ [SINGLETON] Multi-Timeframe Analyzer no disponible: {e}")
                return None
                
        return cls.get_singleton('multi_timeframe_analyzer', create_analyzer)
    
    @classmethod
    def cleanup_singletons(cls):
        """🧹 Limpiar todos los singletons"""
        with cls._lock:
            print("🧹 [SINGLETON] Limpiando singletons...")
            
            cleanup_count = 0
            for key, instance in cls._instances.items():
                try:
                    if hasattr(instance, 'cleanup'):
                        instance.cleanup()
                    elif hasattr(instance, 'close'):
                        instance.close()
                    elif hasattr(instance, 'stop'):
                        instance.stop()
                    cleanup_count += 1
                except Exception as e:
                    print(f"⚠️ [SINGLETON] Error limpiando {key}: {e}")
            
            cls._instances.clear()
            cls._weak_refs.clear()
            
            print(f"✅ [SINGLETON] {cleanup_count} singletons limpiados")
    
    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """📊 Obtener estado de singletons"""
        return {
            'active_singletons': list(cls._instances.keys()),
            'count': len(cls._instances),
            'memory_refs': len(cls._weak_refs)
        }

# Alias para acceso fácil
ESM = EnterpriseSingletonManager

# Factory functions optimizadas para patrones
class EnterprisePatternFactory:
    """🏭 Factory optimizado para patrones enterprise"""
    
    _pattern_cache: Dict[str, Any] = {}
    _lock = threading.RLock()
    
    @classmethod
    def get_pattern_dashboard(cls, pattern_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Obtener dashboard de patrón con cache
        
        Args:
            pattern_name: Nombre del patrón
            config: Configuración del dashboard
            
        Returns:
            Instancia del dashboard del patrón
        """
        cache_key = f"{pattern_name}_{hash(str(config))}"
        
        if cache_key not in cls._pattern_cache:
            with cls._lock:
                if cache_key not in cls._pattern_cache:
                    print(f"🏭 [PATTERN_FACTORY] Creando dashboard para: {pattern_name}")
                    
                    # Crear dashboard usando componentes singleton
                    dashboard = cls._create_pattern_dashboard(pattern_name, config)
                    
                    if dashboard:
                        cls._pattern_cache[cache_key] = dashboard
                        print(f"✅ [PATTERN_FACTORY] Dashboard creado y cacheado: {pattern_name}")
                    else:
                        print(f"❌ [PATTERN_FACTORY] Error creando dashboard: {pattern_name}")
                        return None
                else:
                    print(f"♻️  [PATTERN_FACTORY] Reutilizando dashboard cacheado: {pattern_name}")
        else:
            print(f"♻️  [PATTERN_FACTORY] Retornando dashboard cacheado: {pattern_name}")
            
        return cls._pattern_cache.get(cache_key)
    
    @classmethod
    def _create_pattern_dashboard(cls, pattern_name: str, config: Optional[Dict[str, Any]]):
        """Crear dashboard de patrón usando componentes singleton"""
        try:
            # Usar singletons para todos los componentes pesados
            smart_money = ESM.get_smart_money_analyzer()
            pattern_detector = ESM.get_pattern_detector(config)
            memory_system = ESM.get_unified_memory_system()
            data_manager = ESM.get_ict_data_manager()
            
            # Configurar dashboard con componentes compartidos
            dashboard_config = config or {}
            dashboard_config.update({
                'shared_smart_money_analyzer': smart_money,
                'shared_pattern_detector': pattern_detector,
                'shared_memory_system': memory_system,
                'shared_data_manager': data_manager,
                'singleton_mode': True
            })
            
            # Crear dashboard específico del patrón
            from patterns_analysis.pattern_factory import PatternFactory
            factory = PatternFactory()
            return factory.create_pattern_dashboard(pattern_name, dashboard_config)
            
        except Exception as e:
            print(f"❌ [PATTERN_FACTORY] Error creando dashboard {pattern_name}: {e}")
            return None
    
    @classmethod
    def cleanup_cache(cls):
        """🧹 Limpiar cache de patrones"""
        with cls._lock:
            print("🧹 [PATTERN_FACTORY] Limpiando cache de patrones...")
            cls._pattern_cache.clear()
            print("✅ [PATTERN_FACTORY] Cache limpiado")

# Función de utilidad para inicialización optimizada
def initialize_enterprise_components():
    """🚀 Inicializar componentes enterprise de manera optimizada"""
    print("\n🏭 [ENTERPRISE] Inicializando componentes enterprise optimizados...")
    
    # Pre-cargar singletons críticos
    components = {
        'Smart Money Analyzer': ESM.get_smart_money_analyzer,
        'Unified Memory System': ESM.get_unified_memory_system,
        'ICT Data Manager': ESM.get_ict_data_manager,
        'MT5 Data Manager': ESM.get_mt5_data_manager,
        'Multi-Timeframe Analyzer': ESM.get_multi_timeframe_analyzer
    }
    
    initialized = 0
    for name, factory in components.items():
        try:
            factory()
            initialized += 1
            print(f"✅ [ENTERPRISE] {name} inicializado")
        except Exception as e:
            print(f"⚠️ [ENTERPRISE] Error inicializando {name}: {e}")
    
    print(f"🏁 [ENTERPRISE] {initialized}/{len(components)} componentes inicializados")
    return initialized == len(components)

def cleanup_enterprise_components():
    """🧹 Limpiar todos los componentes enterprise"""
    print("\n🧹 [ENTERPRISE] Limpiando componentes enterprise...")
    ESM.cleanup_singletons()
    EnterprisePatternFactory.cleanup_cache()
    print("✅ [ENTERPRISE] Limpieza completada")

if __name__ == "__main__":
    # Test del sistema
    print("🧪 [TEST] Probando Enterprise Singleton Manager...")
    
    # Probar inicialización
    initialize_enterprise_components()
    
    # Mostrar estado
    status = ESM.get_status()
    print(f"📊 [STATUS] Singletons activos: {status}")
    
    # Limpiar
    cleanup_enterprise_components()
    
    print("✅ [TEST] Test completado")
