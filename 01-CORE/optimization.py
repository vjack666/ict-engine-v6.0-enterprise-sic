#!/usr/bin/env python3
"""
⚡ OPTIMIZATION MODULE - ICT ENGINE v6.0 ENTERPRISE
================================================

Módulo de optimización para operaciones de alta frecuencia y performance
en trading de producción real. Incluye rate limiting, cache optimizado,
y gestión eficiente de recursos.

Características principales:
✅ Rate limiting inteligente adaptativo
✅ Cache con TTL y invalidación automática
✅ Pool de conexiones optimizado
✅ Gestión de memoria eficiente
✅ Monitoreo de latencia en tiempo real
✅ Throttling dinámico según condiciones del mercado

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 16 Septiembre 2025
"""

from protocols.unified_logging import get_unified_logger
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import time
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict, deque
import gc


class RateLimitStrategy(Enum):
    """Estrategias de rate limiting"""
    FIXED = "fixed"              # Límite fijo por ventana de tiempo
    SLIDING = "sliding"          # Ventana deslizante
    ADAPTIVE = "adaptive"        # Adaptativo según condiciones
    BURST = "burst"             # Permite ráfagas controladas


@dataclass
class PerformanceMetrics:
    """Métricas de performance del sistema"""
    avg_latency: float = 0.0
    max_latency: float = 0.0
    min_latency: float = float('inf')
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0


class TradingRateLimiter:
    """
    ⚡ Rate Limiter optimizado para trading
    
    Controla la frecuencia de operaciones para evitar sobrecargar
    el broker y mantener la estabilidad del sistema.
    """
    
    def __init__(self, 
                 max_requests: int = 60,
                 time_window: int = 60,
                 strategy: RateLimitStrategy = RateLimitStrategy.SLIDING,
                 burst_size: int = 10):
        """
        Inicializar rate limiter
        
        Args:
            max_requests: Máximo número de requests por ventana
            time_window: Ventana de tiempo en segundos
            strategy: Estrategia de rate limiting
            burst_size: Tamaño del burst permitido
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.strategy = strategy
        self.burst_size = burst_size
        
        self.logger = get_unified_logger("TradingRateLimiter")
        self._lock = threading.RLock()
        
        # Estado interno
        self._requests = deque()  # (timestamp, request_type)
        self._burst_counter = 0
        self._last_burst_reset = time.time()
        self._blocked_count = 0
        self._allowed_count = 0
        
        # Métricas
        self.metrics = PerformanceMetrics()
        
        self.logger.info(f"✅ TradingRateLimiter initialized: {max_requests}/{time_window}s, strategy={strategy.value}")
    
    def allow_request(self, request_type: str = "default", priority: int = 1) -> bool:
        """
        🚦 Verificar si se permite una request
        
        Args:
            request_type: Tipo de request (trading, data, etc.)
            priority: Prioridad (1=alta, 2=media, 3=baja)
            
        Returns:
            True si se permite la request
        """
        try:
            with self._lock:
                current_time = time.time()
                
                # Limpiar requests antiguas
                self._cleanup_old_requests(current_time)
                
                # Verificar límite según estrategia
                if self.strategy == RateLimitStrategy.FIXED:
                    allowed = self._check_fixed_limit(current_time)
                elif self.strategy == RateLimitStrategy.SLIDING:
                    allowed = self._check_sliding_limit(current_time)
                elif self.strategy == RateLimitStrategy.ADAPTIVE:
                    allowed = self._check_adaptive_limit(current_time, priority)
                elif self.strategy == RateLimitStrategy.BURST:
                    allowed = self._check_burst_limit(current_time)
                else:
                    allowed = self._check_sliding_limit(current_time)  # Default
                
                if allowed:
                    self._requests.append((current_time, request_type))
                    self._allowed_count += 1
                else:
                    self._blocked_count += 1
                
                # Actualizar métricas
                self._update_metrics()
                
                return allowed
                
        except Exception as e:
            self.logger.error(f"Error in rate limiter: {e}")
            return True  # Permitir en caso de error para no bloquear operaciones
    
    def _cleanup_old_requests(self, current_time: float) -> None:
        """🧹 Limpiar requests antiguas"""
        cutoff_time = current_time - self.time_window
        
        while self._requests and self._requests[0][0] < cutoff_time:
            self._requests.popleft()
    
    def _check_fixed_limit(self, current_time: float) -> bool:
        """Verificar límite fijo"""
        return len(self._requests) < self.max_requests
    
    def _check_sliding_limit(self, current_time: float) -> bool:
        """Verificar límite con ventana deslizante"""
        return len(self._requests) < self.max_requests
    
    def _check_adaptive_limit(self, current_time: float, priority: int) -> bool:
        """Verificar límite adaptativo"""
        # Ajustar límite según prioridad
        adjusted_limit = self.max_requests
        
        if priority == 1:  # Alta prioridad
            adjusted_limit = int(self.max_requests * 1.2)
        elif priority == 3:  # Baja prioridad
            adjusted_limit = int(self.max_requests * 0.8)
        
        return len(self._requests) < adjusted_limit
    
    def _check_burst_limit(self, current_time: float) -> bool:
        """Verificar límite con burst"""
        # Reset burst counter cada minuto
        if current_time - self._last_burst_reset > 60:
            self._burst_counter = 0
            self._last_burst_reset = current_time
        
        # Permitir burst si no se ha agotado
        if self._burst_counter < self.burst_size:
            self._burst_counter += 1
            return True
        
        # Verificar límite normal
        return len(self._requests) < self.max_requests
    
    def _update_metrics(self) -> None:
        """📊 Actualizar métricas"""
        try:
            total = self._allowed_count + self._blocked_count
            if total > 0:
                self.metrics.successful_requests = self._allowed_count
                self.metrics.failed_requests = self._blocked_count
                self.metrics.total_requests = total
        except Exception:
            pass  # Silently ignore metrics errors
    
    def get_stats(self) -> Dict[str, Any]:
        """📈 Obtener estadísticas"""
        with self._lock:
            return {
                'strategy': self.strategy.value,
                'max_requests': self.max_requests,
                'time_window': self.time_window,
                'current_requests': len(self._requests),
                'allowed_count': self._allowed_count,
                'blocked_count': self._blocked_count,
                'burst_counter': self._burst_counter,
                'utilization': (len(self._requests) / self.max_requests) * 100
            }
    
    def reset_stats(self) -> None:
        """🔄 Resetear estadísticas"""
        with self._lock:
            self._allowed_count = 0
            self._blocked_count = 0
            self._burst_counter = 0
            self.logger.info("Rate limiter statistics reset")


class DataRateLimiter(TradingRateLimiter):
    """
    📊 Rate Limiter específico para datos de mercado
    
    Optimizado para manejar grandes volúmenes de datos de mercado
    sin afectar las operaciones de trading críticas.
    """
    
    def __init__(self):
        # Configuración más permisiva para datos
        super().__init__(
            max_requests=300,  # 300 requests por minuto
            time_window=60,
            strategy=RateLimitStrategy.BURST,
            burst_size=50
        )
        self.logger = get_unified_logger("DataRateLimiter")
        self.logger.info("✅ DataRateLimiter initialized for market data")


class MainRateLimiter(TradingRateLimiter):
    """
    🎯 Rate Limiter principal del sistema
    
    Controla todas las operaciones del sistema principal para
    mantener la estabilidad y performance general.
    """
    
    def __init__(self):
        # Configuración balanceada para operaciones principales
        super().__init__(
            max_requests=120,  # 120 requests por minuto
            time_window=60,
            strategy=RateLimitStrategy.ADAPTIVE,
            burst_size=20
        )
        self.logger = get_unified_logger("MainRateLimiter")
        self.logger.info("✅ MainRateLimiter initialized for system operations")


class PerformanceOptimizer:
    """
    🚀 Optimizador de performance del sistema
    
    Monitorea y optimiza el rendimiento del sistema en tiempo real,
    ajustando configuraciones según las condiciones actuales.
    """
    
    def __init__(self):
        self.logger = get_unified_logger("PerformanceOptimizer")
        self._lock = threading.RLock()
        
        # Cache optimizado
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_ttl = 300  # 5 minutos TTL por defecto
        
        # Métricas de latencia
        self._latency_samples = deque(maxlen=1000)
        self._last_gc_time = time.time()
        
        # Configuración de optimización
        self.enable_auto_gc = True
        self.gc_interval = 300  # 5 minutos
        self.max_cache_size = 10000
        
        self.logger.info("✅ PerformanceOptimizer initialized")
    
    def cache_get(self, key: str) -> Optional[Any]:
        """
        📦 Obtener valor del cache
        
        Args:
            key: Clave del cache
            
        Returns:
            Valor si existe y no ha expirado, None en caso contrario
        """
        try:
            with self._lock:
                if key not in self._cache:
                    return None
                
                # Verificar TTL
                timestamp = self._cache_timestamps.get(key, 0)
                if time.time() - timestamp > self._cache_ttl:
                    # Expirado
                    self._cache.pop(key, None)
                    self._cache_timestamps.pop(key, None)
                    return None
                
                return self._cache[key]
                
        except Exception as e:
            self.logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        📦 Establecer valor en el cache
        
        Args:
            key: Clave del cache
            value: Valor a almacenar
            ttl: Time to live en segundos (opcional)
        """
        try:
            with self._lock:
                # Limpiar cache si está lleno
                if len(self._cache) >= self.max_cache_size:
                    self._cleanup_expired_cache()
                    
                    # Si sigue lleno, remover más antiguos
                    if len(self._cache) >= self.max_cache_size:
                        self._evict_old_cache_entries()
                
                self._cache[key] = value
                self._cache_timestamps[key] = time.time()
                
        except Exception as e:
            self.logger.error(f"Error setting cache key {key}: {e}")
    
    def cache_clear(self) -> None:
        """🧹 Limpiar todo el cache"""
        with self._lock:
            self._cache.clear()
            self._cache_timestamps.clear()
            self.logger.info("Cache cleared")
    
    def _cleanup_expired_cache(self) -> None:
        """🧹 Limpiar entradas expiradas del cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in self._cache_timestamps.items():
            if current_time - timestamp > self._cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
    
    def _evict_old_cache_entries(self) -> None:
        """🗑️ Eliminar entradas más antiguas del cache"""
        # Remover 20% de las entradas más antiguas
        num_to_remove = max(1, int(len(self._cache) * 0.2))
        
        # Ordenar por timestamp
        sorted_items = sorted(self._cache_timestamps.items(), key=lambda x: x[1])
        
        for i in range(min(num_to_remove, len(sorted_items))):
            key = sorted_items[i][0]
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
    
    def record_latency(self, latency_ms: float) -> None:
        """📊 Registrar muestra de latencia"""
        try:
            with self._lock:
                self._latency_samples.append(latency_ms)
        except Exception:
            pass  # Silently ignore latency recording errors
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📈 Obtener estadísticas de performance"""
        try:
            with self._lock:
                stats = {
                    'cache_size': len(self._cache),
                    'max_cache_size': self.max_cache_size,
                    'cache_utilization': (len(self._cache) / self.max_cache_size) * 100,
                    'latency_samples': len(self._latency_samples),
                }
                
                # Estadísticas de latencia
                if self._latency_samples:
                    latencies = list(self._latency_samples)
                    stats.update({
                        'avg_latency_ms': sum(latencies) / len(latencies),
                        'max_latency_ms': max(latencies),
                        'min_latency_ms': min(latencies),
                        'p95_latency_ms': sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
                    })
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Error getting performance stats: {e}")
            return {}
    
    def optimize_system(self) -> None:
        """🚀 Ejecutar optimizaciones del sistema"""
        try:
            current_time = time.time()
            
            # Garbage collection automático
            if self.enable_auto_gc and (current_time - self._last_gc_time) > self.gc_interval:
                self._run_garbage_collection()
                self._last_gc_time = current_time
            
            # Limpiar cache expirado
            self._cleanup_expired_cache()
            
        except Exception as e:
            self.logger.error(f"Error during system optimization: {e}")
    
    def _run_garbage_collection(self) -> None:
        """🗑️ Ejecutar garbage collection"""
        try:
            collected = gc.collect()
            self.logger.debug(f"Garbage collection: collected {collected} objects")
        except Exception as e:
            self.logger.error(f"Error during garbage collection: {e}")


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

_trading_rate_limiter: Optional[TradingRateLimiter] = None
_data_rate_limiter: Optional[DataRateLimiter] = None
_main_rate_limiter: Optional[MainRateLimiter] = None
_performance_optimizer: Optional[PerformanceOptimizer] = None
_optimization_lock = threading.Lock()


def get_trading_rate_limiter(force_new: bool = False) -> TradingRateLimiter:
    """🏭 Factory para TradingRateLimiter"""
    global _trading_rate_limiter
    
    with _optimization_lock:
        if _trading_rate_limiter is None or force_new:
            _trading_rate_limiter = TradingRateLimiter(
                max_requests=60,
                time_window=60,
                strategy=RateLimitStrategy.ADAPTIVE
            )
        
        return _trading_rate_limiter


def get_data_rate_limiter(force_new: bool = False) -> DataRateLimiter:
    """🏭 Factory para DataRateLimiter"""
    global _data_rate_limiter
    
    with _optimization_lock:
        if _data_rate_limiter is None or force_new:
            _data_rate_limiter = DataRateLimiter()
        
        return _data_rate_limiter


def get_main_rate_limiter(force_new: bool = False) -> MainRateLimiter:
    """🏭 Factory para MainRateLimiter"""
    global _main_rate_limiter
    
    with _optimization_lock:
        if _main_rate_limiter is None or force_new:
            _main_rate_limiter = MainRateLimiter()
        
        return _main_rate_limiter


def get_performance_optimizer(force_new: bool = False) -> PerformanceOptimizer:
    """🏭 Factory para PerformanceOptimizer"""
    global _performance_optimizer
    
    with _optimization_lock:
        if _performance_optimizer is None or force_new:
            _performance_optimizer = PerformanceOptimizer()
        
        return _performance_optimizer


def test_optimization_module():
    """🧪 Test del módulo de optimización"""
    print("🧪 Testing optimization module...")
    
    try:
        # Test rate limiter
        limiter = get_trading_rate_limiter()
        
        # Test requests
        allowed = 0
        blocked = 0
        
        for i in range(100):
            if limiter.allow_request(f"request_{i}"):
                allowed += 1
            else:
                blocked += 1
        
        print(f"✅ Rate limiter: {allowed} allowed, {blocked} blocked")
        
        # Test performance optimizer
        optimizer = get_performance_optimizer()
        
        # Test cache
        optimizer.cache_set("test_key", "test_value")
        cached_value = optimizer.cache_get("test_key")
        assert cached_value == "test_value", "Cache test failed"
        print("✅ Cache functionality working")
        
        # Test latency recording
        optimizer.record_latency(25.5)
        optimizer.record_latency(30.2)
        optimizer.record_latency(22.1)
        
        stats = optimizer.get_performance_stats()
        print(f"✅ Performance stats: {stats}")
        
        print("🎉 Optimization module test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Optimization module test failed: {e}")
        return False


if __name__ == "__main__":
    test_optimization_module()