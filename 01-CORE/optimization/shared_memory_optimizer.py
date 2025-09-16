#!/usr/bin/env python3
"""
🧠 SHARED MEMORY OPTIMIZER
Optimización de memoria compartida para detectores paralelos
"""

from protocols.unified_logging import get_unified_logger
import threading
import weakref
from typing import Dict, Any, Optional, List
import json
import time
from pathlib import Path

from analysis.unified_memory_system import get_unified_memory_system


class SharedMemoryOptimizer:
    """Memoria compartida optimizada para detectores paralelos"""
    
    def __init__(self):
        self.shared_cache = {}
        self.memory_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_requests': 0,
            'memory_usage_mb': 0.0
        }
        self._cache_lock = threading.RLock()
        self._memory_system = None
        self._initialized = False
        
        print("🧠 Shared Memory Optimizer inicializado")
    
    def initialize_shared_memory(self) -> bool:
        """Inicializar memoria compartida una sola vez"""
        if self._initialized:
            return True
        
        try:
            print("   🔧 Inicializando shared unified memory system...")
            self._memory_system = get_unified_memory_system()
            
            # Pre-cargar datos comunes en memoria compartida
            self._preload_common_data()
            
            self._initialized = True
            print("   ✅ Shared memory system inicializado exitosamente")
            return True
            
        except Exception as e:
            print(f"   ❌ Error inicializando shared memory: {e}")
            return False
    
    def _preload_common_data(self):
        """Pre-cargar datos comunes que serán utilizados por múltiples detectores"""
        try:
            # Pre-cargar configuraciones comunes
            common_configs = [
                'default_detector_config',
                'timeframe_settings',
                'pattern_thresholds'
            ]
            
            for config_key in common_configs:
                self.shared_cache[config_key] = self._load_common_config(config_key)
            
            print(f"     🔥 Pre-cargados {len(common_configs)} configuraciones comunes")
            
        except Exception as e:
            print(f"     ⚠️ Warning: Pre-load common data failed: {e}")
    
    def _load_common_config(self, config_key: str) -> Dict[str, Any]:
        """Cargar configuración común"""
        # Configuraciones predefinidas comunes
        configs = {
            'default_detector_config': {
                'confidence_threshold': 0.7,
                'min_pattern_size': 5,
                'max_patterns_per_analysis': 10
            },
            'timeframe_settings': {
                'M15': {'candles_required': 100, 'lookback_periods': 20},
                'H1': {'candles_required': 50, 'lookback_periods': 15},
                'H4': {'candles_required': 25, 'lookback_periods': 10}
            },
            'pattern_thresholds': {
                'BOS': 0.75,
                'CHoCH': 0.70,
                'FVG': 0.65,
                'OB': 0.80
            }
        }
        return configs.get(config_key, {})
    
    def get_shared_data(self, key: str, default=None) -> Any:
        """Obtener datos de memoria compartida thread-safe"""
        with self._cache_lock:
            self.memory_stats['total_requests'] += 1
            
            if key in self.shared_cache:
                self.memory_stats['cache_hits'] += 1
                return self.shared_cache[key]
            else:
                self.memory_stats['cache_misses'] += 1
                return default
    
    def set_shared_data(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Guardar datos en memoria compartida thread-safe"""
        with self._cache_lock:
            cache_entry = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl_seconds,
                'access_count': 0
            }
            self.shared_cache[key] = cache_entry
    
    def clear_expired_data(self):
        """Limpiar datos expirados de la memoria compartida"""
        current_time = time.time()
        expired_keys = []
        
        with self._cache_lock:
            for key, entry in self.shared_cache.items():
                if isinstance(entry, dict) and 'ttl' in entry and entry['ttl']:
                    if current_time - entry['timestamp'] > entry['ttl']:
                        expired_keys.append(key)
            
            for key in expired_keys:
                del self.shared_cache[key]
        
        if expired_keys:
            print(f"🧹 Limpiados {len(expired_keys)} entradas expiradas de memoria compartida")
    
    def sync_detector_memory(self, detector_id: int, patterns: List[Any]):
        """Sincronizar memoria entre detectores del pool"""
        if not self._initialized:
            return
        
        try:
            # Guardar patrones encontrados en memoria compartida
            cache_key = f"detector_{detector_id}_patterns"
            pattern_data = {
                'patterns': patterns,
                'detector_id': detector_id,
                'timestamp': time.time(),
                'pattern_count': len(patterns)
            }
            
            self.set_shared_data(cache_key, pattern_data, ttl_seconds=3600)  # TTL 1 hora
            
            # Sincronizar con el sistema de memoria unificada
            if self._memory_system and patterns:
                for pattern in patterns:
                    try:
                        # Convertir pattern a dict si es necesario
                        if hasattr(pattern, '__dict__'):
                            pattern_dict = pattern.__dict__
                        else:
                            pattern_dict = pattern
                        
                        # Solo sincronizar si tiene la estructura correcta
                        if isinstance(pattern_dict, dict) and 'pattern_type' in pattern_dict:
                            # Usar método correcto del sistema de memoria
                            try:
                                symbol = pattern_dict.get('symbol', 'XAUUSD')  # Gold para optimización de memoria compartida
                                self._memory_system.update_market_memory(pattern_dict, symbol)
                            except (AttributeError, Exception):
                                # Fallback silencioso si el método no existe o falla
                                pass
                    except Exception as e:
                        # Ignorar errores de sincronización individual
                        pass
            
        except Exception as e:
            print(f"   ⚠️ Warning: Sync detector memory failed: {e}")
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de memoria compartida"""
        with self._cache_lock:
            hit_rate = 0.0
            if self.memory_stats['total_requests'] > 0:
                hit_rate = (self.memory_stats['cache_hits'] / 
                           self.memory_stats['total_requests']) * 100
            
            # Calcular uso de memoria aproximado
            memory_usage = 0
            for entry in self.shared_cache.values():
                # Estimación básica del tamaño en memoria
                memory_usage += len(str(entry)) * 2  # Aproximación UTF-8
            
            self.memory_stats['memory_usage_mb'] = memory_usage / (1024 * 1024)
            
            return {
                'cache_entries': len(self.shared_cache),
                'cache_hit_rate_percent': hit_rate,
                'total_requests': self.memory_stats['total_requests'],
                'cache_hits': self.memory_stats['cache_hits'],
                'cache_misses': self.memory_stats['cache_misses'],
                'memory_usage_mb': self.memory_stats['memory_usage_mb'],
                'initialized': self._initialized
            }
    
    def cleanup(self):
        """Limpiar memoria compartida"""
        with self._cache_lock:
            self.shared_cache.clear()
            self.memory_stats = {
                'cache_hits': 0,
                'cache_misses': 0,
                'total_requests': 0,
                'memory_usage_mb': 0.0
            }
            self._initialized = False
        print("🧹 Shared memory limpiada")


# Instancia global del optimizador de memoria compartida
_shared_memory_instance = None
_shared_memory_lock = threading.Lock()


def get_shared_memory_optimizer() -> SharedMemoryOptimizer:
    """Obtener instancia singleton del optimizador de memoria compartida"""
    global _shared_memory_instance
    
    with _shared_memory_lock:
        if _shared_memory_instance is None:
            _shared_memory_instance = SharedMemoryOptimizer()
        return _shared_memory_instance


def cleanup_shared_memory():
    """Limpiar memoria compartida global"""
    global _shared_memory_instance
    
    with _shared_memory_lock:
        if _shared_memory_instance is not None:
            _shared_memory_instance.cleanup()
            _shared_memory_instance = None
