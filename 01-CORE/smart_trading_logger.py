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
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

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
        """🔧 Configurar handlers del logger con archivos diarios organizados"""
        
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
        
        # File handlers organizados por categoría y fecha
        self._setup_daily_file_handlers(formatter)
    
    def _setup_daily_file_handlers(self, formatter):
        """📅 Configurar handlers de archivos diarios organizados"""
        try:
            project_root = Path(__file__).parent.parent
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Estructura de logging diario
            log_categories = {
                'general': project_root / "05-LOGS" / "application",
                'ict': project_root / "01-CORE" / "data" / "logs" / "ict",
                'trading': project_root / "01-CORE" / "data" / "logs" / "trading",
                'structured': project_root / "01-CORE" / "data" / "logs" / "structured",
                'daily': project_root / "01-CORE" / "data" / "logs" / "daily"
            }
            
            # Crear directorios si no existen
            for category, log_dir in log_categories.items():
                log_dir.mkdir(parents=True, exist_ok=True)
            
            # Handler principal para logs generales
            general_log = log_categories['general'] / f"ict_engine_{date_str}.log"
            file_handler = logging.FileHandler(general_log, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)
            
            # Handler para resumen diario
            daily_summary_log = log_categories['daily'] / f"summary_{date_str}.log"
            summary_handler = logging.FileHandler(daily_summary_log, encoding='utf-8')
            summary_handler.setFormatter(formatter)
            summary_handler.setLevel(logging.INFO)
            self.logger.addHandler(summary_handler)
            
            # Guardar referencias para uso posterior
            self.log_categories = log_categories
            self.date_str = date_str
            
        except Exception as e:
            # Si no se puede crear archivos, continuar sin file logging
            self.log_categories = {}
            self.date_str = datetime.now().strftime('%Y-%m-%d')
    
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
    
    # ===== MÉTODOS ESPECIALIZADOS PARA ICT ENGINE =====
    
    def log_ict_pattern(self, pattern_type: str, pattern_data: Dict[str, Any], symbol: str = "UNKNOWN"):
        """📊 Log específico para patrones ICT con archivo diario estructurado"""
        try:
            if hasattr(self, 'log_categories') and 'ict' in self.log_categories:
                # Archivo JSON diario para patrones ICT
                ict_file = self.log_categories['ict'] / f"patterns_{self.date_str}.json"
                
                pattern_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'pattern_type': pattern_type,
                    'symbol': symbol,
                    'data': pattern_data
                }
                
                # Leer archivo existente o crear nuevo
                patterns_data = []
                if ict_file.exists():
                    try:
                        with open(ict_file, 'r', encoding='utf-8') as f:
                            patterns_data = json.load(f)
                    except:
                        patterns_data = []
                
                # Agregar nuevo patrón
                patterns_data.append(pattern_entry)
                
                # Guardar archivo actualizado
                with open(ict_file, 'w', encoding='utf-8') as f:
                    json.dump(patterns_data, f, indent=2, ensure_ascii=False)
            
            # Log también en consola/archivo principal
            self.info(f"ICT Pattern Detected: {pattern_type} for {symbol}", "ICT_PATTERNS")
            
        except Exception as e:
            self.error(f"Error logging ICT pattern: {str(e)}", "ICT_LOGGER")
    
    def log_order_blocks(self, blocks_data: Dict[str, Any], symbol: str = "UNKNOWN"):
        """🧱 Log específico para Order Blocks detectados"""
        try:
            if hasattr(self, 'log_categories') and 'ict' in self.log_categories:
                # Archivo específico para Order Blocks
                ob_file = self.log_categories['ict'] / f"order_blocks_{self.date_str}.json"
                
                ob_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'blocks_detected': blocks_data.get('blocks_count', 0),
                    'bullish_blocks': blocks_data.get('bullish_count', 0),
                    'bearish_blocks': blocks_data.get('bearish_count', 0),
                    'blocks_details': blocks_data.get('blocks', []),
                    'analysis_timeframe': blocks_data.get('timeframe', 'unknown'),
                    'confidence_score': blocks_data.get('confidence', 0.0)
                }
                
                # Manejar archivo JSON acumulativo
                self._append_to_json_file(ob_file, ob_entry)
            
            # Log resumen en consola
            blocks_count = blocks_data.get('blocks_count', 0)
            self.info(f"Order Blocks Analysis: {blocks_count} blocks detected for {symbol}", "ORDER_BLOCKS")
            
        except Exception as e:
            self.error(f"Error logging Order Blocks: {str(e)}", "OB_LOGGER")
    
    def log_trading_session_summary(self, summary_data: Dict[str, Any]):
        """📈 Log resumen de sesión de trading"""
        try:
            if hasattr(self, 'log_categories') and 'daily' in self.log_categories:
                # Archivo de resumen diario
                summary_file = self.log_categories['daily'] / f"session_summary_{self.date_str}.json"
                
                summary_entry = {
                    'session_timestamp': datetime.now().isoformat(),
                    'patterns_detected': summary_data.get('total_patterns', 0),
                    'symbols_analyzed': summary_data.get('symbols', []),
                    'execution_time': summary_data.get('execution_time', 0.0),
                    'system_performance': summary_data.get('performance', {}),
                    'memory_usage': summary_data.get('memory_stats', {}),
                    'errors_count': summary_data.get('errors', 0)
                }
                
                self._append_to_json_file(summary_file, summary_entry)
            
            # Log en consola
            patterns = summary_data.get('total_patterns', 0)
            self.info(f"Session Summary: {patterns} patterns analyzed", "SESSION")
            
        except Exception as e:
            self.error(f"Error logging session summary: {str(e)}", "SESSION_LOGGER")
    
    def _append_to_json_file(self, file_path: Path, new_entry: Dict[str, Any]):
        """🔧 Helper para agregar entradas a archivos JSON"""
        try:
            # Leer archivo existente
            data = []
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]
                except:
                    data = []
            
            # Agregar nueva entrada
            data.append(new_entry)
            
            # Mantener solo últimas 1000 entradas para eficiencia
            if len(data) > 1000:
                data = data[-1000:]
            
            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.error(f"Error appending to JSON file: {str(e)}", "JSON_HELPER")

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

# ===== FUNCIONES ESPECIALIZADAS ICT =====

def log_ict_pattern_detected(pattern_type: str, pattern_data: Dict[str, Any], symbol: str = "UNKNOWN"):
    """📊 Log rápido para patrones ICT detectados"""
    get_smart_logger().log_ict_pattern(pattern_type, pattern_data, symbol)

def log_order_blocks_analysis(blocks_data: Dict[str, Any], symbol: str = "UNKNOWN"):
    """🧱 Log rápido para análisis de Order Blocks"""
    get_smart_logger().log_order_blocks(blocks_data, symbol)

def log_session_summary(summary_data: Dict[str, Any]):
    """📈 Log rápido para resumen de sesión"""
    get_smart_logger().log_trading_session_summary(summary_data)

def create_daily_summary_report():
    """📋 Crear reporte diario consolidado"""
    try:
        logger = get_smart_logger()
        if hasattr(logger, 'log_categories') and 'daily' in logger.log_categories:
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Consolidar datos del día
            summary_data = {
                'date': date_str,
                'report_generated': datetime.now().isoformat(),
                'files_processed': _count_daily_files(logger.log_categories),
                'total_patterns': _count_patterns_in_files(logger.log_categories, date_str),
                'system_health': 'OPERATIONAL'
            }
            
            # Crear reporte
            report_file = logger.log_categories['daily'] / f"daily_report_{date_str}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            log_info(f"Daily report generated: {report_file}", "DAILY_REPORT")
            return report_file
            
    except Exception as e:
        log_error(f"Error creating daily summary: {str(e)}", "DAILY_REPORT")
        return None

def _count_daily_files(log_categories: Dict[str, Path]) -> Dict[str, int]:
    """🔢 Contar archivos generados en el día"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    file_counts = {}
    
    for category, path in log_categories.items():
        if path.exists():
            daily_files = list(path.glob(f"*{date_str}*"))
            file_counts[category] = len(daily_files)
        else:
            file_counts[category] = 0
    
    return file_counts

def _count_patterns_in_files(log_categories: Dict[str, Path], date_str: str) -> int:
    """📊 Contar patrones detectados en el día"""
    total_patterns = 0
    
    try:
        # Contar desde archivo de patrones ICT
        if 'ict' in log_categories:
            patterns_file = log_categories['ict'] / f"patterns_{date_str}.json"
            if patterns_file.exists():
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    patterns_data = json.load(f)
                    total_patterns += len(patterns_data) if isinstance(patterns_data, list) else 1
        
        # Contar desde archivo de Order Blocks
        if 'ict' in log_categories:
            ob_file = log_categories['ict'] / f"order_blocks_{date_str}.json"
            if ob_file.exists():
                with open(ob_file, 'r', encoding='utf-8') as f:
                    ob_data = json.load(f)
                    if isinstance(ob_data, list):
                        total_patterns += sum(entry.get('blocks_detected', 0) for entry in ob_data)
    
    except Exception:
        pass
    
    return total_patterns

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

# ================== MÉTODOS CRÍTICOS PARA TRADING REAL ==================

def log_trade_entry(symbol: str, action: str, volume: float, price: float, 
                   sl: Optional[float] = None, tp: Optional[float] = None,
                   ticket: Optional[int] = None) -> bool:
    """
    🚀 MÉTODO CRÍTICO: Log entrada de trade real
    
    Args:
        symbol: Símbolo operado
        action: 'BUY' o 'SELL'
        volume: Volumen en lotes
        price: Precio de entrada
        sl: Stop Loss
        tp: Take Profit
        ticket: Ticket de la orden
        
    Returns:
        bool: True si se loggeó exitosamente
    """
    try:
        logger = SmartTradingLogger("ICT_Trading")
        
        entry_data = {
            'event_type': 'TRADE_ENTRY',
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': action,
            'volume': volume,
            'entry_price': price,
            'stop_loss': sl,
            'take_profit': tp,
            'ticket': ticket,
            'status': 'OPENED'
        }
        
        logger.info(f"🎯 TRADE ENTRY: {action} {volume} lots {symbol} at {price}")
        logger.info(f"📊 Trade Details: {json.dumps(entry_data, default=str)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to log trade entry: {e}")
        return False

def log_trade_exit(ticket: int, symbol: str, close_price: float, profit: float,
                  reason: str = "Manual close") -> bool:
    """
    🚀 MÉTODO CRÍTICO: Log salida de trade real
    
    Args:
        ticket: Ticket de la posición cerrada
        symbol: Símbolo
        close_price: Precio de cierre
        profit: Ganancia/pérdida en USD
        reason: Razón del cierre
        
    Returns:
        bool: True si se loggeó exitosamente
    """
    try:
        logger = SmartTradingLogger("ICT_Trading")
        
        exit_data = {
            'event_type': 'TRADE_EXIT',
            'timestamp': datetime.now().isoformat(),
            'ticket': ticket,
            'symbol': symbol,
            'close_price': close_price,
            'profit': profit,
            'reason': reason,
            'status': 'CLOSED'
        }
        
        profit_status = "PROFIT" if profit > 0 else "LOSS"
        logger.info(f"🏁 TRADE EXIT: {symbol} ticket {ticket} closed at {close_price} - {profit_status}: ${profit:.2f}")
        logger.info(f"📊 Exit Details: {json.dumps(exit_data, default=str)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to log trade exit: {e}")
        return False

def log_risk_violation(rule_type: str, details: Dict[str, Any]) -> bool:
    """
    🚨 MÉTODO CRÍTICO: Log violación de reglas de riesgo
    
    Args:
        rule_type: Tipo de regla violada (MAX_POSITIONS, MAX_DRAWDOWN, etc.)
        details: Detalles de la violación
        
    Returns:
        bool: True si se loggeó exitosamente
    """
    try:
        logger = SmartTradingLogger("ICT_Risk")
        
        violation_data = {
            'event_type': 'RISK_VIOLATION',
            'timestamp': datetime.now().isoformat(),
            'rule_type': rule_type,
            'details': details,
            'severity': 'HIGH'
        }
        
        logger.error(f"🚨 RISK VIOLATION: {rule_type}")
        logger.error(f"📊 Violation Details: {json.dumps(violation_data, default=str)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to log risk violation: {e}")
        return False

def log_account_status(balance: float, equity: float, margin: float,
                      free_margin: Optional[float] = None) -> bool:
    """
    📊 MÉTODO CRÍTICO: Log status de cuenta en tiempo real
    
    Args:
        balance: Balance de la cuenta
        equity: Equity actual
        margin: Margen usado
        free_margin: Margen libre
        
    Returns:
        bool: True si se loggeó exitosamente
    """
    try:
        logger = SmartTradingLogger("ICT_Account")
        
        account_data = {
            'event_type': 'ACCOUNT_STATUS',
            'timestamp': datetime.now().isoformat(),
            'balance': balance,
            'equity': equity,
            'margin_used': margin,
            'margin_free': free_margin,
            'margin_level': (equity / margin * 100) if margin > 0 else 0.0,
            'floating_pnl': equity - balance
        }
        
        logger.info(f"💰 ACCOUNT STATUS: Balance=${balance:.2f}, Equity=${equity:.2f}, Margin=${margin:.2f}")
        logger.debug(f"📊 Account Details: {json.dumps(account_data, default=str)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to log account status: {e}")
        return False

def log_emergency_action(action_type: str, details: Dict[str, Any], 
                        positions_affected: int = 0) -> bool:
    """
    🚨 MÉTODO CRÍTICO: Log acciones de emergencia
    
    Args:
        action_type: Tipo de acción (EMERGENCY_STOP, DRAWDOWN_LIMIT, etc.)
        details: Detalles de la acción
        positions_affected: Número de posiciones afectadas
        
    Returns:
        bool: True si se loggeó exitosamente
    """
    try:
        logger = SmartTradingLogger("ICT_Emergency")
        
        emergency_data = {
            'event_type': 'EMERGENCY_ACTION',
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'details': details,
            'positions_affected': positions_affected,
            'severity': 'CRITICAL'
        }
        
        logger.critical(f"🚨 EMERGENCY ACTION: {action_type} - {positions_affected} positions affected")
        logger.critical(f"📊 Emergency Details: {json.dumps(emergency_data, default=str)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to log emergency action: {e}")
        return False

def get_trading_session_summary() -> Dict[str, Any]:
    """
    📈 NUEVO: Obtener resumen de sesión de trading (simplificado)
    
    Returns:
        Dict con métricas básicas de la sesión
    """
    try:
        current_time = datetime.now()
        
        return {
            'session_time': current_time.isoformat(),
            'logger_active': True,
            'cache_available': True,
            'session_status': 'ACTIVE'
        }
        
    except Exception as e:
        return {'error': f'Failed to generate session summary: {e}'}

# ================== FIN DE MÉTODOS CRÍTICOS PARA TRADING REAL ==================
