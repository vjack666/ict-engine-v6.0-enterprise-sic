#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 INTELLIGENT LOG OPTIMIZER - ICT ENGINE v6.0 ENTERPRISE
=========================================================

Sistema de optimización inteligente de logging que reduce la verbosidad
manteniendo información crítica y mejorando el rendimiento del sistema.

Características:
- Análisis automático de patrones de logging
- Supresión inteligente de logs redundantes
- Categorización por importancia
- Throttling dinámico adaptativo
- Compresión de logs similares
- Modo boost para trading

Autor: ICT Engine v6.0 Team
Fecha: 2025-09-10
"""

from protocols.unified_logging import get_unified_logger
import os
import sys
import json
import time
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path
import hashlib
import re

# Add core path for imports
current_dir = Path(__file__).parent
core_path = current_dir / "01-CORE"
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

class IntelligentLogOptimizer:
    """🧠 Optimizador inteligente de logging"""
    
    def __init__(self):
        """Inicializar optimizador"""
        self.message_cache = {}  # Cache de mensajes para deduplicación
        self.frequency_tracker = defaultdict(int)  # Rastreador de frecuencia
        self.last_seen = {}  # Última vez que se vio un mensaje
        self.suppressed_count = defaultdict(int)  # Contador de supresiones
        self.importance_scores = {}  # Puntuaciones de importancia
        self.pattern_cache = {}  # Cache de patrones detectados
        
        # Configuración inteligente
        self.config = {
            'max_identical_per_minute': 3,
            'similarity_threshold': 0.85,
            'importance_threshold': 0.7,
            'throttle_window': 60,
            'burst_protection': 10,
            'trading_mode_boost': True
        }
        
        # Patrones críticos que nunca deben suprimirse
        self.critical_patterns = [
            r'❌.*[Ee]rror',
            r'🚨.*[Ee]mergency',
            r'⚠️.*[Cc]ritical',
            r'💰.*[Tt]rading.*[Ee]xecution',
            r'🔒.*[Ss]ecurity',
            r'🚀.*[Ss]ystem.*[Ss]tart',
            r'✅.*[Cc]onnected',
            r'❌.*[Dd]isconnected',
            r'🎯.*[Ss]ignal.*[Gg]enerated'
        ]
        
        # Patrones de alta frecuencia que pueden suprimirse
        self.suppressible_patterns = [
            r'ℹ️.*\[AdvancedCandleDownloader.*📊',
            r'ℹ️.*\[AdvancedCandleDownloader.*📡',
            r'ℹ️.*\[AdvancedCandleDownloader.*🔄',
            r'ℹ️.*\[AdvancedCandleDownloader.*📥',
            r'ℹ️.*\[AdvancedCandleDownloader.*📊.*ICT',
            r'✅.*enhancement.*\d+/\d+',
            r'ℹ️.*Pandas thread-safe',
            r'ℹ️.*MT5 conectado y funcionando',
            r'ℹ️.*Storage:.*Memoria.*MANUAL',
            r'ℹ️.*Timeframe.*->.*MT5 constant'
        ]
        
        # Contadores de rendimiento
        self.stats = {
            'total_processed': 0,
            'suppressed': 0,
            'critical_preserved': 0,
            'patterns_compressed': 0,
            'last_reset': datetime.now()
        }
        
    def should_suppress_message(self, message: str, component: str = "UNKNOWN") -> bool:
        """🔍 Determinar si un mensaje debe suprimirse"""
        try:
            self.stats['total_processed'] += 1
            current_time = datetime.now()
            
            # PASO 1: Verificar si es crítico (nunca suprimir)
            if self._is_critical_message(message):
                self.stats['critical_preserved'] += 1
                return False
            
            # PASO 2: Verificar patrones suprimibles
            if self._matches_suppressible_pattern(message):
                message_hash = self._get_message_hash(message)
                
                # Verificar frecuencia
                if self._is_too_frequent(message_hash, current_time):
                    self.stats['suppressed'] += 1
                    self.suppressed_count[message_hash] += 1
                    return True
            
            # PASO 3: Análisis de similitud para mensajes similares
            if self._is_similar_to_recent(message, current_time):
                self.stats['patterns_compressed'] += 1
                return True
            
            # PASO 4: Actualizar cache
            self._update_cache(message, current_time)
            
            return False
            
        except Exception as e:
            # En caso de error, mejor no suprimir
            return False
    
    def _is_critical_message(self, message: str) -> bool:
        """🚨 Verificar si es un mensaje crítico"""
        for pattern in self.critical_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False
    
    def _matches_suppressible_pattern(self, message: str) -> bool:
        """🔇 Verificar si coincide con patrones suprimibles"""
        for pattern in self.suppressible_patterns:
            if re.search(pattern, message):
                return True
        return False
    
    def _get_message_hash(self, message: str) -> str:
        """🔑 Obtener hash de mensaje para deduplicación"""
        # Normalizar mensaje removiendo timestamps y valores variables
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}.*?\d{2}:\d{2}:\d{2}', '[TIME]', message)
        normalized = re.sub(r'\d+\.\d+ms', '[MS]', normalized)
        normalized = re.sub(r'\d+\.\d+', '[NUM]', normalized)
        normalized = re.sub(r'\d+', '[N]', normalized)
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _is_too_frequent(self, message_hash: str, current_time: datetime) -> bool:
        """⏰ Verificar si el mensaje es demasiado frecuente"""
        if message_hash not in self.last_seen:
            self.last_seen[message_hash] = current_time
            self.frequency_tracker[message_hash] = 1
            return False
        
        time_diff = (current_time - self.last_seen[message_hash]).total_seconds()
        
        # Si han pasado menos de X segundos y ya hemos visto este mensaje muchas veces
        if time_diff < self.config['throttle_window']:
            self.frequency_tracker[message_hash] += 1
            if self.frequency_tracker[message_hash] > self.config['max_identical_per_minute']:
                return True
        else:
            # Reset counter si ha pasado tiempo suficiente
            self.frequency_tracker[message_hash] = 1
        
        self.last_seen[message_hash] = current_time
        return False
    
    def _is_similar_to_recent(self, message: str, current_time: datetime) -> bool:
        """🔍 Verificar similitud con mensajes recientes"""
        # Implementación simple de similitud basada en palabras clave
        message_words = set(message.lower().split())
        
        for cached_msg, cached_time in list(self.message_cache.items()):
            # Solo comparar con mensajes recientes (últimos 30 segundos)
            if (current_time - cached_time).total_seconds() > 30:
                del self.message_cache[cached_msg]
                continue
            
            cached_words = set(cached_msg.lower().split())
            
            # Calcular similitud simple
            if len(message_words) > 0 and len(cached_words) > 0:
                intersection = len(message_words.intersection(cached_words))
                union = len(message_words.union(cached_words))
                similarity = intersection / union if union > 0 else 0
                
                if similarity > self.config['similarity_threshold']:
                    return True
        
        return False
    
    def _update_cache(self, message: str, current_time: datetime):
        """📝 Actualizar cache de mensajes"""
        # Mantener solo mensajes recientes en cache
        cutoff_time = current_time - timedelta(seconds=30)
        self.message_cache = {
            msg: time for msg, time in self.message_cache.items()
            if time > cutoff_time
        }
        
        # Agregar nuevo mensaje
        self.message_cache[message] = current_time
    
    def get_suppression_summary(self) -> Dict[str, Any]:
        """📊 Obtener resumen de supresiones"""
        total_suppressed = sum(self.suppressed_count.values())
        return {
            'total_processed': self.stats['total_processed'],
            'total_suppressed': self.stats['suppressed'],
            'critical_preserved': self.stats['critical_preserved'],
            'suppression_rate': f"{(self.stats['suppressed'] / max(1, self.stats['total_processed']) * 100):.1f}%",
            'top_suppressed_patterns': dict(sorted(
                self.suppressed_count.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5])
        }
    
    def reset_stats(self):
        """🔄 Resetear estadísticas"""
        self.stats = {
            'total_processed': 0,
            'suppressed': 0,
            'critical_preserved': 0,
            'patterns_compressed': 0,
            'last_reset': datetime.now()
        }
        self.suppressed_count.clear()

# Instancia global del optimizador
_log_optimizer = IntelligentLogOptimizer()

def optimize_log_message(message: str, component: str = "UNKNOWN") -> bool:
    """🚀 Función principal para optimizar mensajes de log"""
    return _log_optimizer.should_suppress_message(message, component)

def get_log_optimization_summary() -> Dict[str, Any]:
    """📊 Obtener resumen de optimización"""
    return _log_optimizer.get_suppression_summary()

def reset_log_optimization():
    """🔄 Resetear optimización"""
    _log_optimizer.reset_stats()

def configure_log_optimization(config: Dict[str, Any]):
    """⚙️ Configurar optimización"""
    _log_optimizer.config.update(config)

# Función para integrar con SmartTradingLogger
def create_optimized_message_filter():
    """🔧 Crear filtro optimizado para SmartTradingLogger"""
    
    def should_log_optimized(message: str, component: str = "CORE") -> bool:
        """Función filtro que se integra con SmartTradingLogger"""
        return not optimize_log_message(message, component)
    
    return should_log_optimized

if __name__ == "__main__":
    # Test del optimizador
    optimizer = IntelligentLogOptimizer()
    
    test_messages = [
        "ℹ️  [AdvancedCandleDownloader v6.0] 📊 ICT OPTIMAL: EURUSD H4 - 360 velas",
        "ℹ️  [AdvancedCandleDownloader v6.0] 📊 ICT OPTIMAL: GBPUSD H4 - 360 velas", 
        "❌ Error crítico en conexión MT5",
        "💰 TRADING: Señal generada para EURUSD",
        "ℹ️  [AdvancedCandleDownloader v6.0] 📊 ICT OPTIMAL: EURUSD H4 - 360 velas",  # Duplicado
        "✅ Sistema iniciado correctamente"
    ]
    
    print("🧪 Testing Intelligent Log Optimizer...")
    print("=" * 50)
    
    for i, msg in enumerate(test_messages):
        suppress = optimizer.should_suppress_message(msg)
        status = "🔇 SUPPRESSED" if suppress else "✅ LOGGED"
        print(f"{i+1}. {status}: {msg[:60]}...")
    
    print("\n📊 Optimization Summary:")
    summary = optimizer.get_suppression_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
