"""
CHoCH Query Cache - Sistema de caché para consultas históricas
Evita consultas repetidas mejorando el performance
"""

import time
from typing import Dict, Any, Optional, Tuple
from threading import Lock
import os

class CHoCHQueryCache:
    """Cache thread-safe para consultas CHoCH históricas"""
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        """
        Inicializar cache CHoCH
        
        Args:
            ttl_seconds: Tiempo de vida de las entradas en segundos
            max_size: Tamaño máximo del cache
        """
        self._cache: Dict[str, Tuple[float, Any]] = {}  # key: (timestamp, data)
        self._lock = Lock()
        self._ttl_seconds = ttl_seconds
        self._max_size = max_size
        
        # Optimización low-memory basada en variable de entorno
        if os.getenv('ICT_LOW_MEM', '0') == '1':
            self._ttl_seconds = min(ttl_seconds, 60)  # TTL más corto
            self._max_size = min(max_size, 100)       # Cache más pequeño
    
    def _generate_cache_key(self, symbol: str, timeframe: str, break_level: float, 
                          query_type: str = 'bonus') -> str:
        """Generar clave única para el cache"""
        return f"{query_type}:{symbol}:{timeframe}:{round(break_level, 6)}"
    
    def _is_expired(self, timestamp: float) -> bool:
        """Verificar si una entrada ha expirado"""
        return (time.time() - timestamp) > self._ttl_seconds
    
    def _cleanup_expired(self):
        """Limpiar entradas expiradas (sin lock - llamado internamente)"""
        current_time = time.time()
        expired_keys = [
            key for key, (timestamp, _) in self._cache.items()
            if (current_time - timestamp) > self._ttl_seconds
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def _enforce_size_limit(self):
        """Enforcar límite de tamaño eliminando entradas más antiguas"""
        if len(self._cache) <= self._max_size:
            return
            
        # Ordenar por timestamp y eliminar las más antiguas
        sorted_items = sorted(self._cache.items(), key=lambda x: x[1][0])
        excess_count = len(self._cache) - self._max_size
        
        for i in range(excess_count):
            key = sorted_items[i][0]
            del self._cache[key]
    
    def get_historical_bonus(self, symbol: str, timeframe: str, break_level: float) -> Optional[Dict[str, Any]]:
        """
        Obtener bonus histórico desde cache
        
        Returns:
            Dict con datos o None si no existe/expiró
        """
        cache_key = self._generate_cache_key(symbol, timeframe, break_level, 'bonus')
        
        with self._lock:
            if cache_key in self._cache:
                timestamp, data = self._cache[cache_key]
                if not self._is_expired(timestamp):
                    return data
                else:
                    # Eliminar entrada expirada
                    del self._cache[cache_key]
            return None
    
    def set_historical_bonus(self, symbol: str, timeframe: str, break_level: float, 
                           data: Dict[str, Any]) -> None:
        """
        Almacenar bonus histórico en cache
        
        Args:
            symbol: Símbolo de trading
            timeframe: Marco temporal
            break_level: Nivel de ruptura
            data: Datos a cachear
        """
        cache_key = self._generate_cache_key(symbol, timeframe, break_level, 'bonus')
        
        with self._lock:
            # Limpiar entradas expiradas
            self._cleanup_expired()
            
            # Añadir nueva entrada
            self._cache[cache_key] = (time.time(), data)
            
            # Enforcar límite de tamaño
            self._enforce_size_limit()
    
    def get_success_rate(self, symbol: str, timeframe: str) -> Optional[float]:
        """Obtener success rate desde cache"""
        cache_key = self._generate_cache_key(symbol, timeframe, 0.0, 'success_rate')
        
        with self._lock:
            if cache_key in self._cache:
                timestamp, data = self._cache[cache_key]
                if not self._is_expired(timestamp):
                    return data
                else:
                    del self._cache[cache_key]
            return None
    
    def set_success_rate(self, symbol: str, timeframe: str, success_rate: float) -> None:
        """Almacenar success rate en cache"""
        cache_key = self._generate_cache_key(symbol, timeframe, 0.0, 'success_rate')
        
        with self._lock:
            self._cleanup_expired()
            self._cache[cache_key] = (time.time(), success_rate)
            self._enforce_size_limit()
    
    def clear_cache(self) -> None:
        """Limpiar completamente el cache"""
        with self._lock:
            self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        with self._lock:
            current_time = time.time()
            expired_count = sum(
                1 for timestamp, _ in self._cache.values()
                if (current_time - timestamp) > self._ttl_seconds
            )
            
            return {
                'total_entries': len(self._cache),
                'expired_entries': expired_count,
                'active_entries': len(self._cache) - expired_count,
                'max_size': self._max_size,
                'ttl_seconds': self._ttl_seconds
            }


# Singleton global para el cache
_global_choch_cache: Optional[CHoCHQueryCache] = None


def get_choch_cache() -> CHoCHQueryCache:
    """Obtener instancia singleton del cache CHoCH"""
    global _global_choch_cache
    
    if _global_choch_cache is None:
        # Configuración basada en modo low-memory
        if os.getenv('ICT_LOW_MEM', '0') == '1':
            _global_choch_cache = CHoCHQueryCache(ttl_seconds=60, max_size=100)
        else:
            _global_choch_cache = CHoCHQueryCache(ttl_seconds=300, max_size=1000)
    
    return _global_choch_cache


def clear_choch_cache() -> None:
    """Limpiar el cache global CHoCH"""
    global _global_choch_cache
    if _global_choch_cache is not None:
        _global_choch_cache.clear_cache()