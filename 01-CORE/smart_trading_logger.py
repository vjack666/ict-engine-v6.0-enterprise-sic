#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SMART TRADING LOGGER - ICT ENGINE v6.0 ENTERPRISE
====================================================

Sistema de logging centralizado para ICT Engine v6.1.0.
Integrado con Enterprise System.

Autor: ICT Engine v6.1.0 Team
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class SmartTradingLogger:
    """🔧 Logger inteligente para ICT Engine v6.1.0"""
    
    def __init__(self, name: str = "ICT_Engine", level: str = "INFO"):
        """
        🏗️ Inicializar Smart Trading Logger
        
        Args:
            name: Nombre del logger
            level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Configurar nivel
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self.logger.setLevel(level_map.get(level.upper(), logging.INFO))
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """🔧 Configurar handlers del logger"""
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        
        # File handler (opcional) - ESTRUCTURA CORRECTA DE CARPETAS
        try:
            # Usar la estructura oficial 05-LOGS/application en lugar de raíz/logs
            project_root = Path(__file__).parent.parent
            logs_dir = project_root / "05-LOGS" / "application"
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = logs_dir / f"ict_engine_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)
            
        except Exception:
            # Si no se puede crear archivo, continuar sin file logging
            pass
    
    def debug(self, message: str, component: str = "CORE", **kwargs):
        """🔍 Log debug message"""
        self.logger.debug(f"[{component}] {message}")
    
    def info(self, message: str, component: str = "CORE", **kwargs):
        """ℹ️ Log info message"""
        self.logger.info(f"[{component}] {message}")
    
    def warning(self, message: str, component: str = "CORE", **kwargs):
        """⚠️ Log warning message"""
        self.logger.warning(f"[{component}] {message}")
    
    def error(self, message: str, component: str = "CORE", **kwargs):
        """❌ Log error message"""
        self.logger.error(f"[{component}] {message}")
    
    def critical(self, message: str, component: str = "CORE", **kwargs):
        """🚨 Log critical message"""
        self.logger.critical(f"[{component}] {message}")

# Instancia global del logger
_smart_logger: Optional[SmartTradingLogger] = None

def get_smart_logger(name: str = "ICT_Engine", level: str = "INFO") -> SmartTradingLogger:
    """🔧 Obtener instancia del Smart Trading Logger"""
    global _smart_logger
    
    if _smart_logger is None:
        _smart_logger = SmartTradingLogger(name, level)
    
    return _smart_logger

# Funciones de conveniencia
def log_info(message: str, component: str = "CORE"):
    """ℹ️ Log info rápido"""
    get_smart_logger().info(message, component)

def log_warning(message: str, component: str = "CORE"):
    """⚠️ Log warning rápido"""
    get_smart_logger().warning(message, component)

def log_error(message: str, component: str = "CORE"):
    """❌ Log error rápido"""
    get_smart_logger().error(message, component)

def log_debug(message: str, component: str = "CORE"):
    """🔍 Log debug rápido"""
    get_smart_logger().debug(message, component)

# Alias para compatibilidad
SmartLogger = SmartTradingLogger

# =============================================================================
# TRADING DECISION CACHE v6.0 ENTERPRISE
# =============================================================================

import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class TradingDecisionCacheV6:
    """
    💾 Cache inteligente enterprise para decisiones de trading v6.0.
    
    Migrado y mejorado desde proyecto principal/core/smart_trading_logger.py.
    Evita redundancia en logs, mantiene memoria de estados significativos.
    
    Funcionalidades Enterprise v6.0:
    - ✅ Cache inteligente con configuración enterprise
    - ✅ Detección de cambios significativos multi-timeframe
    - ✅ Cache correlacionado para Smart Money analysis
    - ✅ Memoria persistente de decisiones
    - ✅ Configuración avanzada de thresholds
    """
    
    def __init__(self, cache_config: Optional[Dict[str, Any]] = None):
        """Inicializa cache de decisiones con configuración enterprise."""
        
        # === CONFIGURACIÓN ENTERPRISE ===
        self.cache_config = cache_config or {}
        self.logger = SmartTradingLogger()
        
        # === CACHE DE ESTADOS ===
        self.last_states: Dict[str, str] = {}
        self.last_log_times: Dict[str, datetime] = {}
        
        # === CONFIGURACIÓN DE THRESHOLDS ===
        enterprise_settings = self.cache_config.get("cache_settings", {})
        self.change_threshold = 60  # Segundos mínimos entre logs del mismo tipo
        self.important_threshold = 300  # 5 minutos para eventos importantes
        self.enable_intelligent_caching = enterprise_settings.get("enable_intelligent_caching", True)
        self.auto_cleanup_hours = enterprise_settings.get("auto_cleanup_hours", 24)
        
        # === CACHE MULTI-TIMEFRAME ===
        self.multi_tf_cache: Dict[str, Dict[str, Any]] = {}
        
        # === CACHE SMART MONEY ===
        self.smart_money_cache: Dict[str, Dict[str, Any]] = {}
        
        # === MÉTRICAS DE CACHE ===
        self.cache_hits = 0
        self.cache_misses = 0
        self.events_cached = 0
        self.events_logged = 0
        
        self.logger.info(
            f"💾 TradingDecisionCacheV6 inicializado - "
            f"Intelligent: {self.enable_intelligent_caching}, "
            f"Cleanup: {self.auto_cleanup_hours}h",
            component="decision_cache"
        )
    
    def should_log_event(self, event_type: str, data: Dict[str, Any], 
                        force_important: bool = False) -> bool:
        """
        Determina si un evento debe ser registrado basado en cambios reales.
        Función heredada y mejorada del sistema legacy.
        """
        if not self.enable_intelligent_caching:
            return True  # Si cache está deshabilitado, loggear todo
        
        try:
            current_time = datetime.now()
            
            # Crear hash del estado actual para detectar cambios
            data_hash = self._create_state_hash(data)
            
            # Obtener el último estado y tiempo para este tipo de evento
            last_hash = self.last_states.get(event_type)
            last_time = self.last_log_times.get(event_type)
            
            # Si es la primera vez o hay un cambio real en el estado
            if last_hash != data_hash:
                self.last_states[event_type] = data_hash
                self.last_log_times[event_type] = current_time
                self.cache_misses += 1
                self.events_logged += 1
                return True
            
            # Si es importante, permitir log cada 5 minutos aunque no haya cambios
            if force_important and last_time:
                time_diff = (current_time - last_time).total_seconds()
                if time_diff >= self.important_threshold:
                    self.last_log_times[event_type] = current_time
                    self.events_logged += 1
                    return True
            
            # Si ha pasado suficiente tiempo para eventos normales
            if last_time:
                time_diff = (current_time - last_time).total_seconds()
                if time_diff >= self.change_threshold:
                    self.last_log_times[event_type] = current_time
                    self.events_logged += 1
                    return True
            
            # No loggear - es redundante
            self.cache_hits += 1
            self.events_cached += 1
            return False
            
        except Exception as e:
            self.logger.error(f"Error en should_log_event: {e}", component="decision_cache")
            return True  # En caso de error, mejor loggear
    
    def cache_multi_timeframe_decision(self, analysis_results: Dict[str, Any]) -> None:
        """
        Cache inteligente para decisiones multi-timeframe.
        NUEVO v6.0: Cache correlacionado entre timeframes.
        """
        try:
            # Extraer símbolo de forma robusta
            symbol = analysis_results.get('symbol', 'EURUSD')  # Default to most liquid major pair
            timeframes = analysis_results.get('timeframes_analyzed', [])
            
            # Cache por símbolo
            if symbol not in self.multi_tf_cache:
                self.multi_tf_cache[symbol] = {}
            
            # Cache por timeframe con correlación
            for tf in timeframes:
                tf_data = analysis_results.get('timeframe_results', {}).get(tf, {})
                
                cache_key = f"{symbol}_{tf}"
                
                # Solo cachear si hay cambio significativo
                if self._is_significant_multi_tf_change(cache_key, tf_data):
                    self.multi_tf_cache[symbol][tf] = {
                        'timestamp': datetime.now(),
                        'data': tf_data,
                        'hash': self._create_state_hash(tf_data)
                    }
                    
                    self.logger.debug(
                        f"Multi-TF decision cached: {symbol}/{tf}",
                        component="decision_cache"
                    )
            
            # Limpiar cache antiguo
            self._cleanup_old_multi_tf_cache()
            
        except Exception as e:
            self.logger.error(f"Error caching multi-timeframe decision: {e}", 
                                component="decision_cache")
    
    def is_significant_smart_money_change(self, current_analysis: Dict[str, Any]) -> bool:
        """
        Detecta cambios significativos en análisis Smart Money.
        NUEVO v6.0: Cache inteligente para patrones institucionales.
        """
        try:
            analysis_hash = self._create_state_hash(current_analysis)
            
            # Obtener último análisis Smart Money
            last_sm_analysis = self.smart_money_cache.get('last_analysis')
            
            if not last_sm_analysis:
                # Primera vez - es significativo
                self.smart_money_cache['last_analysis'] = {
                    'timestamp': datetime.now(),
                    'hash': analysis_hash,
                    'data': current_analysis
                }
                return True
            
            last_hash = last_sm_analysis.get('hash')
            last_time = last_sm_analysis.get('timestamp')
            
            # Verificar cambio en hash
            if last_hash != analysis_hash:
                self.smart_money_cache['last_analysis'] = {
                    'timestamp': datetime.now(),
                    'hash': analysis_hash,
                    'data': current_analysis
                }
                return True
            
            # Verificar si ha pasado suficiente tiempo para Smart Money
            if last_time and (datetime.now() - last_time).total_seconds() > 900:  # 15 minutos
                self.smart_money_cache['last_analysis']['timestamp'] = datetime.now()
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking Smart Money change: {e}", 
                                component="decision_cache")
            return True  # En caso de error, considerar significativo
    
    def auto_cleanup_cache(self) -> None:
        """
        Limpieza automática de cache según configuración enterprise.
        Gestión automática de memoria con configuración enterprise.
        """
        try:
            current_time = datetime.now()
            cleanup_threshold = current_time - timedelta(hours=self.auto_cleanup_hours)
            
            # Limpiar cache de estados antiguos
            old_events = []
            for event_type, log_time in self.last_log_times.items():
                if log_time < cleanup_threshold:
                    old_events.append(event_type)
            
            for event_type in old_events:
                if event_type in self.last_states:
                    del self.last_states[event_type]
                if event_type in self.last_log_times:
                    del self.last_log_times[event_type]
            
            # Limpiar cache multi-timeframe
            for symbol in list(self.multi_tf_cache.keys()):
                for tf in list(self.multi_tf_cache[symbol].keys()):
                    tf_time = self.multi_tf_cache[symbol][tf].get('timestamp')
                    if tf_time and tf_time < cleanup_threshold:
                        del self.multi_tf_cache[symbol][tf]
                
                # Eliminar símbolo si no tiene timeframes
                if not self.multi_tf_cache[symbol]:
                    del self.multi_tf_cache[symbol]
            
            # Limpiar cache Smart Money
            sm_time = self.smart_money_cache.get('last_analysis', {}).get('timestamp')
            if sm_time and sm_time < cleanup_threshold:
                self.smart_money_cache.clear()
            
            self.logger.debug(
                f"Cache cleanup completado - Events removed: {len(old_events)}",
                component="decision_cache"
            )
            
        except Exception as e:
            self.logger.error(f"Error en auto cleanup: {e}", component="decision_cache")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache para monitoreo."""
        total_events = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_events * 100) if total_events > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'events_cached': self.events_cached,
            'events_logged': self.events_logged,
            'hit_rate_percent': round(hit_rate, 2),
            'multi_tf_symbols_cached': len(self.multi_tf_cache),
            'smart_money_cache_active': bool(self.smart_money_cache.get('last_analysis')),
            'last_cleanup': 'auto'
        }
    
    def _create_state_hash(self, data: Dict[str, Any]) -> str:
        """
        Crea un hash del estado actual para detectar cambios.
        Función heredada del sistema legacy.
        """
        try:
            # Convertir el diccionario a string ordenado y crear hash
            state_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(state_str.encode()).hexdigest()[:8]
        except Exception:
            # Fallback si hay problemas con serialización
            state_str = str(sorted(data.items()))
            return hashlib.md5(state_str.encode()).hexdigest()[:8]
    
    def _is_significant_multi_tf_change(self, cache_key: str, tf_data: Dict[str, Any]) -> bool:
        """Determina si hay cambio significativo en análisis multi-timeframe."""
        try:
            # Extraer símbolo y timeframe del cache_key
            parts = cache_key.split('_')
            if len(parts) < 2:
                return True
            
            symbol = parts[0]
            timeframe = parts[1]
            
            # Verificar cache existente
            if symbol not in self.multi_tf_cache:
                return True
            
            if timeframe not in self.multi_tf_cache[symbol]:
                return True
            
            cached_data = self.multi_tf_cache[symbol][timeframe]
            cached_hash = cached_data.get('hash')
            current_hash = self._create_state_hash(tf_data)
            
            return cached_hash != current_hash
            
        except Exception:
            return True  # En caso de error, considerar significativo
    
    def _cleanup_old_multi_tf_cache(self) -> None:
        """Limpia entradas antiguas del cache multi-timeframe."""
        try:
            current_time = datetime.now()
            threshold = current_time - timedelta(hours=self.auto_cleanup_hours)
            
            for symbol in list(self.multi_tf_cache.keys()):
                for tf in list(self.multi_tf_cache[symbol].keys()):
                    cached_time = self.multi_tf_cache[symbol][tf].get('timestamp')
                    if cached_time and cached_time < threshold:
                        del self.multi_tf_cache[symbol][tf]
                
                # Eliminar símbolo vacío
                if not self.multi_tf_cache[symbol]:
                    del self.multi_tf_cache[symbol]
                    
        except Exception as e:
            self.logger.error(f"Error en cleanup multi-TF cache: {e}", component="decision_cache")

    # Métodos de integración para UnifiedMemorySystem
    def set_market_context(self, market_context):
        """Establece el contexto de mercado asociado"""
        self.market_context = market_context
        self.logger.info(f"🔗 Decision cache conectado al market context")
        
    def set_unified_system(self, unified_system):
        """Establece el sistema unificado asociado"""
        self.unified_system = unified_system
        self.logger.info(f"🧠 Decision cache conectado al sistema unificado")

# Instancia global del cache enterprise
_trading_decision_cache_v6: Optional[TradingDecisionCacheV6] = None

def get_trading_decision_cache(cache_config: Optional[Dict[str, Any]] = None) -> TradingDecisionCacheV6:
    """🔧 Obtener instancia del Trading Decision Cache v6.0"""
    global _trading_decision_cache_v6
    
    if _trading_decision_cache_v6 is None:
        _trading_decision_cache_v6 = TradingDecisionCacheV6(cache_config)
    
    return _trading_decision_cache_v6

# Función de compatibilidad con sistema legacy
TradingDecisionCache = TradingDecisionCacheV6

# Instancia global para compatibilidad legacy
trading_cache = get_trading_decision_cache()

# =============================================================================
# ENHANCED LOGGING FUNCTIONS v6.0
# =============================================================================

def log_trading_decision_smart_v6(event_type: str, data: Dict[str, Any],
                                 level: str = "INFO", force_important: bool = False,
                                 symbol: str = "EURUSD") -> bool:
    """
    💾 Logger inteligente v6.0 que solo registra cambios significativos.
    
    Migrado y mejorado desde proyecto principal con funcionalidades enterprise:
    - Cache inteligente multi-timeframe
    - Detección de cambios Smart Money
    - Auto-cleanup configurable
    - Métricas de cache avanzadas
    
    Returns:
        bool: True si se loggeó, False si se cacheó
    """
    cache = get_trading_decision_cache()
    
    # Verificar si realmente debemos loggear este evento
    should_log = cache.should_log_event(event_type, data, force_important)
    
    if not should_log:
        return False  # Evento cacheado, no loggeado
    
    try:
        logger = get_smart_logger()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Formatear mensaje según tipo de evento
        if event_type == "BOS_DETECTION":
            message = (f"🎯 BOS {symbol}: {data.get('direction', 'N/A')} | "
                      f"TF: {data.get('timeframe', 'N/A')} | "
                      f"Strength: {data.get('strength', 'N/A')} | "
                      f"Price: {data.get('price', 'N/A')}")
            
        elif event_type == "CHOCH_DETECTION":
            message = (f"🔄 CHoCH {symbol}: {data.get('direction', 'N/A')} | "
                      f"TF: {data.get('timeframe', 'N/A')} | "
                      f"Strength: {data.get('strength', 'N/A')} | "
                      f"Price: {data.get('price', 'N/A')}")
            
        elif event_type == "SMART_MONEY_ANALYSIS":
            message = (f"🧠 Smart Money {symbol}: {data.get('bias', 'N/A')} | "
                      f"Institutional Flow: {data.get('flow_strength', 'N/A')} | "
                      f"Confidence: {data.get('confidence', 'N/A')}")
            
        elif event_type == "MULTI_TIMEFRAME_ANALYSIS":
            message = (f"📊 Multi-TF {symbol}: H4={data.get('h4_bias', 'N/A')} | "
                      f"M15={data.get('m15_structure', 'N/A')} | "
                      f"M5={data.get('m5_confirmation', 'N/A')}")
            
        else:
            # Formato genérico
            message = f"📈 {event_type} {symbol}: {json.dumps(data, default=str)}"
        
        # Log según nivel
        if level.upper() == "DEBUG":
            logger.debug(message, component="trading_decision")
        elif level.upper() == "WARNING":
            logger.warning(message, component="trading_decision")
        elif level.upper() == "ERROR":
            logger.error(message, component="trading_decision")
        else:
            logger.info(message, component="trading_decision")
        
        return True  # Evento loggeado exitosamente
        
    except Exception as e:
        # En caso de error en logging, usar print como fallback
        print(f"[{timestamp}] ERROR - logging_error: {e}")
        return False

# Alias para compatibilidad
log_trading_decision_smart = log_trading_decision_smart_v6

# NOTA: get_trading_decision_cache ya está definida arriba en línea 465
# No redeclarar para evitar error de Pylance

# Funciones de conveniencia para cache
def should_log_trading_event(event_type: str, data: Dict[str, Any], 
                           force_important: bool = False) -> bool:
    """💾 Verificar si evento de trading debe ser loggeado"""
    return get_trading_decision_cache().should_log_event(event_type, data, force_important)

def cache_multi_timeframe_decision(analysis_results: Dict[str, Any]) -> None:
    """🔗 Cachear decisión multi-timeframe"""
    get_trading_decision_cache().cache_multi_timeframe_decision(analysis_results)

def is_significant_smart_money_change(current_analysis: Dict[str, Any]) -> bool:
    """🧠 Verificar cambio significativo en Smart Money"""
    return get_trading_decision_cache().is_significant_smart_money_change(current_analysis)
