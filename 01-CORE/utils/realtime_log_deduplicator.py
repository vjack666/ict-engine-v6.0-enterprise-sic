#!/usr/bin/env python3
"""
🔧 DEDUPLICADOR EN TIEMPO REAL
ICT Engine v6.0 Enterprise - Previene logs duplicados en tiempo real
"""

import time
import hashlib
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
from pathlib import Path

class RealtimeLogDeduplicator:
    """🔧 Sistema de deduplicación en tiempo real para logs"""
    
    def __init__(self, max_duplicates_per_minute=5, window_minutes=1):
        self.max_duplicates = max_duplicates_per_minute
        self.window_seconds = window_minutes * 60
        self.message_history = deque(maxlen=1000)
        self.message_counts = {}
        
        # Cargar configuración si existe
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
        
    def should_log(self, message: str) -> bool:
        """
        Determina si un mensaje debe loggearse
        
        Args:
            message: Mensaje a evaluar
            
        Returns:
            True si debe loggearse, False si debe bloquearse
        """
        now = datetime.now()
        message_hash = hashlib.md5(message.encode()).hexdigest()
        
        # Limpiar mensajes antiguos
        self._cleanup_old_messages(now)
        
        # Contar ocurrencias recientes
        recent_count = self.message_counts.get(message_hash, 0)
        
        if recent_count >= self.max_duplicates:
            return False  # Bloquear mensaje duplicado
        
        # Registrar mensaje
        self.message_history.append((now, message_hash))
        self.message_counts[message_hash] = recent_count + 1
        
        return True
    
    def _cleanup_old_messages(self, current_time):
        """Limpiar mensajes fuera de la ventana de tiempo"""
        cutoff_time = current_time - timedelta(seconds=self.window_seconds)
        
        # Limpiar deque
        while self.message_history and self.message_history[0][0] < cutoff_time:
            old_time, old_hash = self.message_history.popleft()
            if old_hash in self.message_counts:
                self.message_counts[old_hash] -= 1
                if self.message_counts[old_hash] <= 0:
                    del self.message_counts[old_hash]
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas del deduplicador"""
        return {
            'active_messages': len(self.message_counts),
            'total_tracked': len(self.message_history),
            'window_seconds': self.window_seconds,
            'max_duplicates': self.max_duplicates
        }
    
    def reset(self):
        """Resetear el deduplicador"""
        self.message_history.clear()
        self.message_counts.clear()

# Instancia global
DEDUPLICATOR = RealtimeLogDeduplicator()

def should_log_message(message: str) -> bool:
    """Función de conveniencia para verificar si un mensaje debe loggearse"""
    return DEDUPLICATOR.should_log(message)

def get_deduplicator_stats() -> Dict:
    """Función de conveniencia para obtener estadísticas"""
    return DEDUPLICATOR.get_stats()

def reset_deduplicator():
    """Función de conveniencia para resetear el deduplicador"""
    DEDUPLICATOR.reset()
