#!/usr/bin/env python3
"""
� DEDUPLICADOR INTELIGENTE EN TIEMPO REAL - ICT ENGINE v6.0 ENTERPRISE
========================================================================
Sistema avanzado de deduplicación que combina:
- Deduplicación tradicional por hash
- Análisis de patrones inteligente
- Detección de logs críticos
- Supresión automática de logs verbosos
- Estadísticas de optimización en tiempo real

Autor: ICT Engine v6.0 Team
Fecha: 2025-09-10 (Optimizado)
"""

from protocols.unified_logging import get_unified_logger
import time
import hashlib
import re
from collections import deque, defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Set, List
import json
from pathlib import Path

class RealtimeLogDeduplicator:
    """🧠 Sistema inteligente de deduplicación en tiempo real para logs"""
    
    def __init__(self, max_duplicates_per_minute=5, window_minutes=1):
        self.max_duplicates = max_duplicates_per_minute
        self.window_seconds = window_minutes * 60
        self.message_history = deque(maxlen=1000)
        self.message_counts = {}
        
        # === NUEVAS CARACTERÍSTICAS INTELIGENTES ===
        
        # Patrones críticos que NUNCA deben suprimirse
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
        
        # Patrones verbosos que pueden suprimirse agresivamente
        self.verbose_patterns = [
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
        
        # Estadísticas inteligentes
        self.stats = {
            'total_processed': 0,
            'critical_preserved': 0,
            'verbose_suppressed': 0,
            'duplicate_suppressed': 0,
            'normal_logged': 0,
            'last_reset': datetime.now()
        }
        
        # Cache de similitud para detección avanzada
        self.similarity_cache = {}
        self.last_cleanup = datetime.now()
        
        # Cargar configuración
        self._load_config()
        
    def _load_config(self):
        """Cargar configuración de throttling"""
        try:
            config_path = Path("01-CORE/config/log_throttle_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    self.max_duplicates = config.get("max_duplicates_per_minute", 5)
                    rate_limit = config.get("rate_limiting", {})
                    if rate_limit.get("enabled", True):
                        self.max_duplicates = rate_limit.get("max_identical_messages", 5)
        except:
            pass  # Usar valores por defecto
        
    def should_log(self, message: str, component: str = "UNKNOWN") -> bool:
        """
        🧠 Determina inteligentemente si un mensaje debe loggearse
        
        Args:
            message: Mensaje a evaluar
            component: Componente que genera el log
            
        Returns:
            True si debe loggearse, False si debe bloquearse
        """
        self.stats['total_processed'] += 1
        now = datetime.now()
        
        # PASO 1: Verificar si es crítico (NUNCA suprimir)
        if self._is_critical_message(message):
            self.stats['critical_preserved'] += 1
            self._register_message(message, now)
            return True
        
        # PASO 2: Verificar si es verboso (suprimir agresivamente)
        if self._is_verbose_message(message):
            # Para mensajes verbosos, usar límites más estrictos
            if not self._should_allow_verbose(message, now):
                self.stats['verbose_suppressed'] += 1
                return False
        
        # PASO 3: Deduplicación tradicional mejorada
        message_hash = self._get_smart_hash(message)
        
        # Limpiar mensajes antiguos
        self._cleanup_old_messages(now)
        
        # Contar ocurrencias recientes
        recent_count = self.message_counts.get(message_hash, 0)
        
        if recent_count >= self.max_duplicates:
            self.stats['duplicate_suppressed'] += 1
            return False  # Bloquear mensaje duplicado
        
        # PASO 4: Registrar mensaje y permitir
        self._register_message(message, now, message_hash)
        self.stats['normal_logged'] += 1
        
        return True
    
    def _is_critical_message(self, message: str) -> bool:
        """🚨 Verificar si es un mensaje crítico que nunca debe suprimirse"""
        for pattern in self.critical_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False
    
    def _is_verbose_message(self, message: str) -> bool:
        """🔇 Verificar si es un mensaje verboso que puede suprimirse"""
        for pattern in self.verbose_patterns:
            if re.search(pattern, message):
                return True
        return False
    
    def _should_allow_verbose(self, message: str, current_time: datetime) -> bool:
        """⏰ Verificar si permitir mensaje verboso (límites más estrictos)"""
        # Para mensajes verbosos, permitir máximo 1 cada 10 segundos del mismo tipo
        message_hash = self._get_smart_hash(message)
        
        if message_hash in self.similarity_cache:
            last_time = self.similarity_cache[message_hash]
            time_diff = (current_time - last_time).total_seconds()
            if time_diff < 10:  # Límite estricto de 10 segundos para verbosos
                return False
        
        self.similarity_cache[message_hash] = current_time
        return True
    
    def _get_smart_hash(self, message: str) -> str:
        """🔑 Obtener hash inteligente normalizando valores variables"""
        # Normalizar mensaje removiendo timestamps y valores que cambian
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}.*?\d{2}:\d{2}:\d{2}', '[TIME]', message)
        normalized = re.sub(r'\d+\.\d+ms', '[MS]', normalized)
        normalized = re.sub(r'\d+\.\d+', '[NUM]', normalized)
        normalized = re.sub(r'\d{5,}', '[BIGNUM]', normalized)  # Números grandes como velas
        normalized = re.sub(r'\d+/\d+', '[FRAC]', normalized)  # Fracciones como 3/15
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _register_message(self, message: str, current_time: datetime, message_hash: Optional[str] = None):
        """📝 Registrar mensaje en el historial"""
        if message_hash is None:
            message_hash = self._get_smart_hash(message)
        
        # Registrar en historial
        self.message_history.append((current_time, message_hash))
        self.message_counts[message_hash] = self.message_counts.get(message_hash, 0) + 1
    
    def _cleanup_old_messages(self, current_time):
        """🧹 Limpiar mensajes fuera de la ventana de tiempo + cache de similitud"""
        cutoff_time = current_time - timedelta(seconds=self.window_seconds)
        
        # Limpiar deque
        while self.message_history and self.message_history[0][0] < cutoff_time:
            old_time, old_hash = self.message_history.popleft()
            if old_hash in self.message_counts:
                self.message_counts[old_hash] -= 1
                if self.message_counts[old_hash] <= 0:
                    del self.message_counts[old_hash]
        
        # Limpiar cache de similitud cada 60 segundos
        if (current_time - self.last_cleanup).total_seconds() > 60:
            similarity_cutoff = current_time - timedelta(seconds=30)
            self.similarity_cache = {
                h: t for h, t in self.similarity_cache.items() 
                if t > similarity_cutoff
            }
            self.last_cleanup = current_time
    
    def get_stats(self) -> Dict:
        """📊 Obtener estadísticas completas del deduplicador inteligente"""
        total_processed = self.stats['total_processed']
        total_suppressed = (self.stats['verbose_suppressed'] + 
                          self.stats['duplicate_suppressed'])
        
        return {
            # Estadísticas básicas
            'active_messages': len(self.message_counts),
            'total_tracked': len(self.message_history),
            'similarity_cache_size': len(self.similarity_cache),
            'window_seconds': self.window_seconds,
            'max_duplicates': self.max_duplicates,
            
            # Estadísticas inteligentes
            'total_processed': total_processed,
            'critical_preserved': self.stats['critical_preserved'],
            'verbose_suppressed': self.stats['verbose_suppressed'], 
            'duplicate_suppressed': self.stats['duplicate_suppressed'],
            'normal_logged': self.stats['normal_logged'],
            'total_suppressed': total_suppressed,
            'suppression_rate': f"{(total_suppressed / max(1, total_processed) * 100):.1f}%",
            'critical_rate': f"{(self.stats['critical_preserved'] / max(1, total_processed) * 100):.1f}%",
            'last_reset': self.stats['last_reset'].isoformat()
        }
    
    def reset(self):
        """🔄 Resetear el deduplicador y estadísticas"""
        self.message_history.clear()
        self.message_counts.clear()
        self.similarity_cache.clear()
        
        # Resetear estadísticas
        self.stats = {
            'total_processed': 0,
            'critical_preserved': 0,
            'verbose_suppressed': 0,
            'duplicate_suppressed': 0,
            'normal_logged': 0,
            'last_reset': datetime.now()
        }

# Instancia global
DEDUPLICATOR = RealtimeLogDeduplicator()

def should_log_message(message: str, component: str = "UNKNOWN") -> bool:
    """🧠 Función inteligente para verificar si un mensaje debe loggearse"""
    return DEDUPLICATOR.should_log(message, component)

def get_deduplicator_stats() -> Dict:
    """📊 Función de conveniencia para obtener estadísticas completas"""
    return DEDUPLICATOR.get_stats()

def reset_deduplicator():
    """🔄 Función de conveniencia para resetear el deduplicador"""
    DEDUPLICATOR.reset()

def show_deduplicator_summary():
    """📊 Mostrar resumen completo del deduplicador"""
    stats = get_deduplicator_stats()
    
    print("\n🧠 RESUMEN DEDUPLICADOR INTELIGENTE")
    print("=" * 50)
    print(f"📈 Total procesados: {stats['total_processed']}")
    print(f"🔇 Total suprimidos: {stats['total_suppressed']}")
    print(f"   • Verbosos: {stats['verbose_suppressed']}")
    print(f"   • Duplicados: {stats['duplicate_suppressed']}")
    print(f"🚨 Críticos preservados: {stats['critical_preserved']}")
    print(f"✅ Normales loggeados: {stats['normal_logged']}")
    print(f"📊 Tasa supresión: {stats['suppression_rate']}")
    print(f"🎯 Tasa críticos: {stats['critical_rate']}")
    print(f"💾 Cache activo: {stats['similarity_cache_size']} patrones")
    print("=" * 50)
