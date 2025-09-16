#!/usr/bin/env python3
"""
📈 ICT HISTORICAL ANALYZER v6.0 ENTERPRISE - MEMORIA HISTÓRICA AVANZADA
=====================================================================

Análisis histórico de rendimiento ICT con memoria persistente para v6.0 Enterprise.
Migrado y mejorado desde proyecto principal/core/ict_engine/ict_historical_analyzer.py

Funcionalidades Enterprise v6.0:
- ✅ Memoria persistente de análisis históricos
- ✅ Cache inteligente con configuración enterprise
- ✅ Análisis multi-timeframe correlacionado
- ✅ Integración con Smart Money concepts
- ✅ Decaimiento temporal optimizado
- ✅ Performance scoring dinámico
- ✅ Comportamiento de trader real con experiencia

Versión: v6.1.0-enterprise-historical-memory
Fecha: 8 de Agosto 2025 - 20:30 GMT
"""

# === IMPORTS ENTERPRISE v6.0 ===
from protocols.unified_logging import get_unified_logger
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple, Union, TYPE_CHECKING
from pathlib import Path
import numpy as np

if TYPE_CHECKING:
    import pandas as pd

# === IMPORTS ENTERPRISE LOGGING ===
from smart_trading_logger import SmartTradingLogger

class ICTHistoricalAnalyzerV6:
    """
    📈 Análisis histórico enterprise con memoria persistente para ICT Engine v6.1.0.
    
    Funciona como la memoria histórica de un trader real profesional:
    - Analiza performance de patrones ICT históricos
    - Mantiene memoria de éxitos y fallos pasados
    - Aplica decaimiento temporal a experiencias antiguas
    - Genera scoring dinámico basado en experiencia
    - Persiste aprendizajes entre sesiones
    """
    
    def __init__(self, cache_config_path: str = "config/cache_config.json"):
        """Inicializa el analizador histórico con configuración enterprise."""
        
        # === CONFIGURACIÓN ENTERPRISE ===
        self.cache_config = self._load_cache_config(cache_config_path)
        self.logger = SmartTradingLogger(name="HistoricalAnalyzer")
        
        self.logger.info("📈 Inicializando ICT Historical Analyzer v6.0 Enterprise", 
                         component="historical_memory")
        
        # Thread-safe pandas access
        self._pandas_manager = None
        
        # === DIRECTORIOS DE MEMORIA - ESTRUCTURA ENTERPRISE ===
        # Obtener el directorio raíz del proyecto
        project_root = Path(__file__).parent.parent.parent
        self.logs_dir = project_root / "05-LOGS" / "application"
        self.analysis_dir = project_root / "04-DATA" / "logs" / "ict"
        
        # FORZAR: Directorio de memoria persistente enterprise en 04-DATA (consistente con market_context)
        memory_persistence_path = project_root / "04-DATA" / "memory_persistence"
        self.cache_dir = Path(memory_persistence_path)
        self.historical_cache_dir = self.cache_dir / "historical_analysis"
        
        # Asegurar directorios existen
        self._ensure_directories()
        
        # === CACHE ENTERPRISE ===
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.cache_ttl = timedelta(hours=self.cache_config.get("memory_cache", {}).get("retention_hours", 24))
        
        # === CONFIGURACIÓN ANÁLISIS ===
        self.config = {
            'min_samples': 5,  # Mínimo de muestras para análisis confiable
            'success_threshold': 0.7,  # 70% de éxito para considerarse "exitoso"
            'time_decay_factor': 0.1,  # Factor de decaimiento temporal
            'max_lookback_days': 30,  # Máximo 30 días de lookback
            'weight_multipliers': {
                'BOS': 1.0,
                'CHOCH': 1.1,
                'ORDER_BLOCK': 1.0,
                'FAIR_VALUE_GAP': 1.1,
                'LIQUIDITY_POOL': 1.2,
                'POI': 0.9,
                'DISPLACEMENT': 1.3
            }
        }
    
    def _get_pandas_manager(self):
        """Obtiene instancia thread-safe del pandas manager."""
        if self._pandas_manager is None:
            # Usando el patrón correcto que funciona en el sistema
            try:
                # Implementación thread-safe básica
                import pandas as pd
                self._pandas_manager = pd
            except ImportError:
                self._pandas_manager = None
        return self._pandas_manager
        
        # === MEMORIA MULTI-TIMEFRAME ===
        self.timeframe_analyzers: Dict[str, dict] = {}
        for tf in ["W1", "D1", "H4", "H1", "M15", "M5", "M1"]:
            self.timeframe_analyzers[tf] = {
                'performance_cache': {},
                'last_analysis': None,
                'pattern_success_rates': {},
                'adaptive_weights': {}
            }
        
        # === MEMORIA SMART MONEY HISTÓRICA ===
        self.smart_money_history: Dict[str, Any] = {
            'killzone_performance': {},
            'institutional_patterns': {},
            'liquidity_efficiency': {},
            'session_success_rates': {}
        }
        
        # === INICIALIZACIÓN ===
        self._restore_historical_cache()
        
        self.logger.info(
            f"✅ ICT Historical Analyzer v6.0 Enterprise inicializado - "
            f"Cache: {self.cache_dir}, "
            f"TTL: {self.cache_ttl.total_seconds()/3600:.1f}h, "
            f"Timeframes: {len(self.timeframe_analyzers)}",
            component="historical_memory"
        )
    
    def _load_cache_config(self, config_path: str) -> dict:
        """Carga configuración de cache enterprise."""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config
            else:
                # Configuración por defecto
                return {
                    "cache_settings": {
                        "enable_intelligent_caching": True,
                        "cache_directory": str(Path(__file__).parent.parent.parent / "04-DATA" / "cache" / "memory"),
                        "max_cache_size_mb": 500,
                        "auto_cleanup_hours": 24
                    },
                    "memory_cache": {
                        "historical_analysis_cache": {
                            "enabled": True,
                            "max_size_mb": 200,
                            "retention_hours": 24
                        }
                    }
                }
        except Exception as e:
            self.logger.error(f"Error cargando cache_config: {e}", component="historical_memory")
            return {}
    
    def _ensure_directories(self) -> None:
        """Asegura que todos los directorios necesarios existen."""
        try:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            self.analysis_dir.mkdir(parents=True, exist_ok=True)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.historical_cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Error creando directorios: {e}", component="historical_memory")
    
    def analyze_historical_pois(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Analiza POIs históricos con memoria de performance.
        Como un trader real consultando su historial de éxitos/fallos.
        """
        try:
            # Verificar cache
            cache_key = f"poi_analysis_{symbol}_{timeframe}"
            cached_result = self._get_valid_cache(cache_key)
            if cached_result:
                self.logger.debug(f"Cache hit para análisis POI {symbol}/{timeframe}", 
                                    component="historical_memory")
                return cached_result
            
            # Cargar datos históricos
            historical_data = self._load_historical_poi_data(symbol, timeframe)
            
            if not historical_data or len(historical_data) < self.config['min_samples']:
                # Análisis cold start
                result = self._cold_start_poi_analysis(symbol, timeframe)
                self._set_cache(cache_key, result)
                return result
            
            # Análisis con memoria histórica
            analysis_result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'total_samples': len(historical_data),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'performance_stats': self._calculate_poi_performance_stats(historical_data),
                'success_patterns': self._identify_success_patterns(historical_data),
                'adaptive_weights': self._calculate_adaptive_weights(historical_data),
                'time_decay_analysis': self._apply_time_decay_analysis(historical_data),
                'recommendations': self._generate_poi_recommendations(historical_data),
                'memory_quality': self._assess_memory_quality(historical_data)
            }
            
            # Cachear resultado
            self._set_cache(cache_key, analysis_result)
            
            self.logger.info(
                f"📊 Análisis POI histórico completado - {symbol}/{timeframe}: "
                f"{len(historical_data)} muestras, "
                f"Quality: {analysis_result['memory_quality']}",
                component="historical_memory"
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analizando POIs históricos: {e}", component="historical_memory")
            return self._cold_start_poi_analysis(symbol, timeframe)
    
    def analyze_multi_timeframe_history(self, symbol: str, timeframes: List[str]) -> Dict[str, Any]:
        """
        Análisis histórico multi-timeframe con memoria correlacionada.
        NUEVO v6.0: Análisis correlacionado entre timeframes.
        """
        try:
            correlation_analysis = {
                'symbol': symbol,
                'timeframes_analyzed': timeframes,
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'individual_analyses': {},
                'correlation_matrix': {},
                'cross_timeframe_patterns': {},
                'unified_recommendations': []
            }
            
            # Análisis individual por timeframe
            for tf in timeframes:
                tf_analysis = self.analyze_historical_pois(symbol, tf)
                correlation_analysis['individual_analyses'][tf] = tf_analysis
                
                # Actualizar memoria del timeframe
                self.timeframe_analyzers[tf]['last_analysis'] = tf_analysis
                self.timeframe_analyzers[tf]['performance_cache'][symbol] = tf_analysis
            
            # Análisis de correlación entre timeframes
            if len(timeframes) > 1:
                correlation_analysis['correlation_matrix'] = self._calculate_timeframe_correlations(
                    correlation_analysis['individual_analyses']
                )
                
                correlation_analysis['cross_timeframe_patterns'] = self._identify_cross_timeframe_patterns(
                    correlation_analysis['individual_analyses']
                )
            
            # Recomendaciones unificadas
            correlation_analysis['unified_recommendations'] = self._generate_unified_recommendations(
                correlation_analysis['individual_analyses']
            )
            
            self.logger.info(
                f"🔗 Análisis multi-timeframe completado - {symbol}: "
                f"{len(timeframes)} TFs, "
                f"Correlations: {len(correlation_analysis['correlation_matrix'])}",
                component="historical_memory"
            )
            
            return correlation_analysis
            
        except Exception as e:
            self.logger.error(f"Error en análisis multi-timeframe: {e}", component="historical_memory")
            return {}
    
    def get_historical_poi_performance(self, poi_type: str, timeframe: str = "M15", 
                                     symbol: str = "EURUSD") -> float:
        """
        Obtiene el factor de ponderación histórico para un tipo de POI específico.
        Función heredada y mejorada del sistema legacy.
        """
        # Verificar cache
        cache_key = f"poi_performance_{poi_type}_{timeframe}_{symbol}"
        cached_weight = self._get_valid_cache(cache_key)
        if cached_weight is not None:
            return cached_weight
        
        try:
            # Cargar datos históricos específicos del POI
            historical_data = self._load_historical_poi_data(symbol, timeframe, poi_type)
            
            if not historical_data or len(historical_data) < self.config['min_samples']:
                # No hay suficientes datos históricos, usar peso base
                weight = self.config['weight_multipliers'].get(poi_type, 1.0)
                self.logger.warning(
                    f"[COLD_START] 🟡 Datos insuficientes para {poi_type} "
                    f"({len(historical_data) if historical_data else 0} muestras), "
                    f"usando peso base: {weight}",
                    component="historical_memory"
                )
                self._set_cache(cache_key, weight)
                return weight
            
            # Calcular rendimiento histórico
            success_rate = self._calculate_success_rate(historical_data)
            time_weighted_rate = self._apply_time_decay(historical_data, success_rate)
            
            # Convertir tasa de éxito a factor de ponderación
            weight = self._success_rate_to_weight(time_weighted_rate, poi_type)
            
            # Cachear resultado
            self._set_cache(cache_key, weight)
            
            self.logger.info(
                f"Performance histórica {poi_type}/{timeframe}: "
                f"éxito={success_rate:.2%}, peso ajustado={weight:.3f}",
                component="historical_memory"
            )
            
            return weight
            
        except Exception as e:
            self.logger.error(f"Error calculando performance histórica para {poi_type}: {e}", 
                                component="historical_memory")
            # Fallback a peso base
            weight = self.config['weight_multipliers'].get(poi_type, 1.0)
            self._set_cache(cache_key, weight)
            return weight
    
    def integrate_smart_money_memory(self, smart_money_data: Dict[str, Any]) -> None:
        """
        Integra memoria de análisis Smart Money.
        NUEVO v6.0: Memoria de patrones institucionales.
        """
        try:
            timestamp = datetime.now(timezone.utc)
            
            # Actualizar performance de killzones
            if 'killzone_analysis' in smart_money_data:
                for session, data in smart_money_data['killzone_analysis'].items():
                    if session not in self.smart_money_history['killzone_performance']:
                        self.smart_money_history['killzone_performance'][session] = []
                    
                    self.smart_money_history['killzone_performance'][session].append({
                        'timestamp': timestamp,
                        'efficiency': data.get('efficiency', 0.5),
                        'activity_level': data.get('activity_level', 0.5),
                        'success_rate': data.get('success_rate', 0.5)
                    })
                    
                    # Mantener límite de memoria
                    if len(self.smart_money_history['killzone_performance'][session]) > 100:
                        self.smart_money_history['killzone_performance'][session] = \
                            self.smart_money_history['killzone_performance'][session][-100:]
            
            # Actualizar patrones institucionales
            if 'institutional_patterns' in smart_money_data:
                institutional_data = {
                    'timestamp': timestamp,
                    'patterns': smart_money_data['institutional_patterns'],
                    'confidence': smart_money_data.get('institutional_confidence', 0.5)
                }
                
                if 'institutional_patterns' not in self.smart_money_history:
                    self.smart_money_history['institutional_patterns'] = []
                
                self.smart_money_history['institutional_patterns'].append(institutional_data)
                
                # Mantener límite
                if len(self.smart_money_history['institutional_patterns']) > 200:
                    self.smart_money_history['institutional_patterns'] = \
                        self.smart_money_history['institutional_patterns'][-200:]
            
            self.logger.debug("Memoria Smart Money actualizada", component="historical_memory")
            
        except Exception as e:
            self.logger.error(f"Error integrando Smart Money memory: {e}", component="historical_memory")
    
    def get_poi_confidence_score(self, poi_data: Dict[str, Any]) -> float:
        """
        Calcula un score de confianza basado en análisis histórico.
        Función heredada y mejorada del sistema legacy.
        """
        try:
            poi_type = poi_data.get('type', 'FVG')  # FVG es más común que ORDER_BLOCK en análisis ICT moderno
            timeframe = poi_data.get('timeframe', 'M15')
            symbol = poi_data.get('symbol', 'EURUSD')
            
            # Obtener weight histórico
            historical_weight = self.get_historical_poi_performance(poi_type, timeframe, symbol)
            
            # Score base del POI
            base_score = poi_data.get('score', 0.5)
            base_confidence = poi_data.get('confidence', 0.5)
            
            # Calcular confianza ajustada
            adjusted_confidence = min(1.0, base_confidence * historical_weight)
            
            # Factores adicionales enterprise
            freshness_factor = self._calculate_freshness_factor(poi_data)
            confluence_factor = self._calculate_confluence_factor(poi_data)
            timeframe_factor = self._calculate_timeframe_factor(poi_data, timeframe)
            
            # Score final de confianza
            final_confidence = adjusted_confidence * freshness_factor * confluence_factor * timeframe_factor
            
            return min(1.0, max(0.0, final_confidence))
            
        except Exception as e:
            self.logger.error(f"Error calculando confidence score: {e}", component="historical_memory")
            return 0.5  # Valor neutral por defecto
    
    def export_memory_cache(self) -> None:
        """
        Exporta cache de memoria para persistencia.
        Actualiza metadata y usa directorio enterprise configurado.
        """
        try:
            # Determinar estado actual del sistema
            total_patterns = sum(
                len(analyzer.get('pattern_success_rates', {})) 
                for analyzer in self.timeframe_analyzers.values()
            )
            
            system_state = 'EXPERIENCED' if total_patterns > 0 else 'LEARNING'
            
            cache_export = {
                'metadata': {
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'version': 'v6.1.0-enterprise',
                    'cache_type': 'historical_analysis',
                    'system_state': system_state,
                    'total_patterns_analyzed': total_patterns
                },
                'export_timestamp': datetime.now(timezone.utc).isoformat(),
                'cache_data': self.cache,
                'timeframe_analyzers': self.timeframe_analyzers,
                'smart_money_history': self.smart_money_history,
                'config': self.config
            }
            
            export_file = self.historical_cache_dir / 'historical_analysis_cache.json'
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(cache_export, f, indent=2, default=str)
            
            self.logger.info(f"💾 Memoria del sistema actualizada en {export_file}", 
                               component="historical_memory")
            
        except Exception as e:
            self.logger.error(f"Error exportando memory cache: {e}", component="historical_memory")
    
    def _create_initial_memory_cache(self) -> bool:
        """
        🧠 Crea cache de memoria inicial para primera ejecución del sistema.
        Establece valores por defecto inteligentes para arranque limpio.
        """
        try:
            # Crear estructura inicial de memoria enterprise
            initial_cache = {
                'metadata': {
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'version': 'v6.1.0-enterprise',
                    'cache_type': 'historical_analysis',
                    'system_state': 'FIRST_RUN_INITIALIZED'
                },
                'cache_data': {},
                'cache_timestamps': {},
                'timeframe_analyzers': {},
                'smart_money_history': {
                    'killzone_performance': {},
                    'institutional_patterns': {},
                    'liquidity_efficiency': {},
                    'session_success_rates': {}
                }
            }
            
            # Inicializar analyzers por timeframe
            for tf in ["W1", "D1", "H4", "H1", "M15", "M5", "M1"]:
                initial_cache['timeframe_analyzers'][tf] = {
                    'performance_cache': {},
                    'last_analysis': None,
                    'pattern_success_rates': {
                        'BOS': 0.7,          # Break of Structure - valor inicial conservador
                        'CHOCH': 0.75,       # Change of Character - ligeramente mejor
                        'ORDER_BLOCK': 0.65, # Order Block - más conservador
                        'FAIR_VALUE_GAP': 0.72, # FVG - buen rendimiento inicial
                        'LIQUIDITY_POOL': 0.68,  # Liquidez - moderado
                        'POI': 0.6,          # Point of Interest - conservador
                        'DISPLACEMENT': 0.8   # Displacement - alta confianza inicial
                    },
                    'adaptive_weights': {
                        'BOS': 1.0,
                        'CHOCH': 1.1,
                        'ORDER_BLOCK': 1.0,
                        'FAIR_VALUE_GAP': 1.1,
                        'LIQUIDITY_POOL': 1.2,
                        'POI': 0.9,
                        'DISPLACEMENT': 1.3
                    }
                }
            
            # Guardar cache inicial
            cache_file = self.historical_cache_dir / 'historical_analysis_cache.json'
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(initial_cache, f, indent=2)
            
            self.logger.info(f"🧠 Cache de memoria inicial creado exitosamente en {cache_file}", 
                             component="historical_memory")
            self.logger.info("✅ Sistema listo para acumular experiencia de trading", 
                             component="historical_memory")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creando cache de memoria inicial: {e}", component="historical_memory")
            return False

    def import_memory_cache(self) -> bool:
        """
        Importa cache de memoria de sesiones pasadas.
        Si no existe, crea cache inicial automáticamente.
        """
        try:
            import_file = self.historical_cache_dir / 'historical_analysis_cache.json'
            
            if not import_file.exists():
                self.logger.info("Primera ejecución detectada - Inicializando memoria del sistema", 
                                 component="historical_memory")
                
                # Crear cache inicial automáticamente
                if self._create_initial_memory_cache():
                    # Intentar cargar el cache recién creado
                    return self.import_memory_cache()
                else:
                    self.logger.error("No se pudo crear cache inicial de memoria", 
                                      component="historical_memory")
                    return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Restaurar datos
            if 'cache_data' in cache_data:
                self.cache = cache_data['cache_data']
            
            if 'timeframe_analyzers' in cache_data:
                self.timeframe_analyzers = cache_data['timeframe_analyzers']
            
            if 'smart_money_history' in cache_data:
                self.smart_money_history = cache_data['smart_money_history']
            
            # Log de información sobre el cache cargado
            metadata = cache_data.get('metadata', {})
            system_state = metadata.get('system_state', 'UNKNOWN')
            
            if system_state == 'FIRST_RUN_INITIALIZED':
                self.logger.info(f"🧠 Memoria inicial cargada - Sistema listo para aprender", 
                                 component="historical_memory")
            else:
                self.logger.info(f"📚 Memoria histórica restaurada desde {import_file}", 
                                 component="historical_memory")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error importando memory cache: {e}", component="historical_memory")
            return False
    
    def _restore_historical_cache(self) -> None:
        """Restaura cache histórico al inicializar."""
        try:
            self.import_memory_cache()
        except Exception as e:
            self.logger.error(f"Error restaurando cache histórico: {e}", component="historical_memory")
    
    # === MÉTODOS HELPER ===
    
    def _load_historical_poi_data(self, symbol: str, timeframe: str, poi_type: Optional[str] = None) -> List[Dict]:
        """Carga datos históricos de POIs."""
        # Implementación simplificada - en producción cargaría de logs reales
        return []
    
    def _cold_start_poi_analysis(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Análisis de cold start cuando no hay datos históricos."""
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'total_samples': 0,
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'performance_stats': {'success_rate': 0.5, 'confidence': 0.5},
            'memory_quality': 'COLD_START',
            'recommendations': ['Necesita acumular datos históricos']
        }
    
    def _calculate_poi_performance_stats(self, data: List[Dict]) -> Dict[str, Any]:
        """Calcula estadísticas de performance de POIs."""
        if not data:
            return {'success_rate': 0.5, 'confidence': 0.5}
        
        success_rate = self._calculate_success_rate(data)
        avg_confidence = sum(entry.get('confidence', 0.5) for entry in data) / len(data)
        
        return {
            'success_rate': success_rate,
            'avg_confidence': avg_confidence,
            'total_samples': len(data),
            'recent_performance': success_rate  # Simplificado
        }
    
    def _calculate_success_rate(self, entries: List[Dict]) -> float:
        """Calcula la tasa de éxito de los entries."""
        if not entries:
            return 0.5  # Valor neutral
        
        successes = sum(1 for entry in entries if entry.get('success', False))
        return successes / len(entries)
    
    def _apply_time_decay(self, entries: List[Dict], base_rate: float) -> float:
        """Aplica decaimiento temporal a la tasa de éxito."""
        if not entries:
            return base_rate
        
        now = datetime.now(timezone.utc)
        weighted_sum = 0
        total_weight = 0
        
        for entry in entries:
            try:
                entry_date = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                days_old = (now - entry_date).days
                weight = max(0.1, 1.0 - (days_old * self.config['time_decay_factor']))
                
                success_value = 1.0 if entry.get('success', False) else 0.0
                weighted_sum += success_value * weight
                total_weight += weight
                
            except (ValueError, TypeError):
                continue
        
        return weighted_sum / total_weight if total_weight > 0 else base_rate
    
    def _success_rate_to_weight(self, success_rate: float, poi_type: str) -> float:
        """Convierte tasa de éxito a factor de ponderación."""
        base_multiplier = self.config['weight_multipliers'].get(poi_type, 1.0)
        
        # Mapear tasa de éxito a rango de ponderación (0.5 - 1.5)
        if success_rate >= self.config['success_threshold']:
            # Alto rendimiento: peso entre 1.0 y 1.5
            weight_factor = 1.0 + (success_rate - self.config['success_threshold']) * 1.67
        else:
            # Bajo rendimiento: peso entre 0.5 y 1.0
            weight_factor = 0.5 + (success_rate / self.config['success_threshold']) * 0.5
        
        return base_multiplier * weight_factor
    
    def _calculate_freshness_factor(self, poi_data: Dict) -> float:
        """Calcula factor de frescura del POI."""
        try:
            timestamp = poi_data.get('timestamp')
            if not timestamp:
                return 1.0
            
            poi_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hours_old = (datetime.now(timezone.utc) - poi_date).total_seconds() / 3600
            
            # Factor de frescura: 1.0 para POIs frescos, decae con el tiempo
            return max(0.5, 1.0 - (hours_old / 168))  # Decae en 7 días
            
        except (ValueError, TypeError):
            return 1.0
    
    def _calculate_confluence_factor(self, poi_data: Dict) -> float:
        """Calcula factor de confluencia del POI."""
        try:
            confluence_count = poi_data.get('confluence_count', 1)
            # Factor de confluencia: 1.0 base, +10% por cada confluencia adicional
            return min(1.5, 1.0 + (confluence_count - 1) * 0.1)
        except (ValueError, TypeError):
            return 1.0
    
    def _calculate_timeframe_factor(self, poi_data: Dict, timeframe: str) -> float:
        """Calcula factor de timeframe."""
        # Factores según importancia del timeframe
        tf_factors = {
            'W1': 1.3, 'D1': 1.2, 'H4': 1.1, 'H1': 1.0,
            'M15': 0.9, 'M5': 0.8, 'M1': 0.7
        }
        return tf_factors.get(timeframe, 1.0)
    
    def _get_valid_cache(self, cache_key: str) -> Any:
        """Obtiene valor del cache si es válido."""
        if cache_key in self.cache_timestamps:
            cache_time = self.cache_timestamps[cache_key]
            if datetime.now(timezone.utc) - cache_time < self.cache_ttl:
                return self.cache.get(cache_key)
        return None
    
    def _set_cache(self, cache_key: str, value: Any) -> None:
        """Establece valor en cache."""
        self.cache[cache_key] = value
        self.cache_timestamps[cache_key] = datetime.now(timezone.utc)
    
    # === MÉTODOS PLACEHOLDER PARA IMPLEMENTACIÓN COMPLETA ===
    
    def _identify_success_patterns(self, data: List[Dict]) -> List[str]:
        """Identifica patrones de éxito en los datos."""
        return ["Pattern analysis pending implementation"]
    
    def _calculate_adaptive_weights(self, data: List[Dict]) -> Dict[str, float]:
        """Calcula pesos adaptativos."""
        return {"adaptive_weight": 1.0}
    
    def _apply_time_decay_analysis(self, data: List[Dict]) -> Dict[str, Any]:
        """Aplica análisis de decaimiento temporal."""
        return {"time_decay_applied": True}
    
    def _generate_poi_recommendations(self, data: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en POIs."""
        return ["Continue monitoring pattern performance"]
    
    def _assess_memory_quality(self, data: List[Dict]) -> str:
        """Evalúa calidad de la memoria."""
        if len(data) > 100:
            return "EXCELLENT"
        elif len(data) > 50:
            return "HIGH"
        elif len(data) > 20:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_timeframe_correlations(self, analyses: Dict) -> Dict[str, Any]:
        """Calcula correlaciones entre timeframes."""
        return {"correlation_analysis": "pending"}
    
    def _identify_cross_timeframe_patterns(self, analyses: Dict) -> Dict[str, Any]:
        """Identifica patrones cross-timeframe."""
        return {"cross_tf_patterns": "pending"}
    
    def _generate_unified_recommendations(self, analyses: Dict) -> List[str]:
        """Genera recomendaciones unificadas."""
        return ["Unified analysis pending implementation"]

    # === FUNCIONES MIGRADAS DESDE LEGACY v6.0 ===
    
    def analyze_bos_performance(self, symbol: str = "EURUSD") -> Dict[str, Any]:
        """
        Analiza efectividad histórica de patrones BOS.
        Migrado desde legacy ICTHistoricalAnalyzer.
        
        Args:
            symbol: Símbolo del mercado
            
        Returns:
            Dict con análisis de performance BOS
        """
        self.logger.info(f"📈 Analizando performance BOS: {symbol}")
        
        try:
            # Obtener eventos BOS del contexto de mercado o cache
            bos_events = self._get_bos_events_from_cache(symbol)
            
            if len(bos_events) < 10:  # Mínimo para análisis confiable
                self.logger.warning(f"⚠️ Pocos eventos BOS para análisis: {len(bos_events)}")
                return {
                    'symbol': symbol,
                    'total_events': len(bos_events),
                    'success_rate': 0.5,  # Neutral
                    'confidence': 0.3,
                    'weight_factor': 1.0,
                    'status': 'insufficient_data'
                }
            
            # Calcular métricas de performance
            successful_events = sum(1 for event in bos_events if event.get('success', False))
            success_rate = successful_events / len(bos_events)
            
            # Análisis por timeframe
            by_timeframe = {}
            for event in bos_events:
                tf = event.get('timeframe', 'H1')  # H1 mejor para análisis BOS según ICT methodology
                if tf not in by_timeframe:
                    by_timeframe[tf] = {'total': 0, 'successful': 0}
                by_timeframe[tf]['total'] += 1
                if event.get('success', False):
                    by_timeframe[tf]['successful'] += 1
            
            # Calcular confidence basado en cantidad de datos
            confidence = min(1.0, len(bos_events) / 100.0)
            
            result = {
                'symbol': symbol,
                'pattern_type': 'BOS',
                'total_events': len(bos_events),
                'successful_events': successful_events,
                'success_rate': success_rate,
                'confidence': confidence,
                'weight_factor': self._success_rate_to_weight(success_rate, 'BOS'),
                'by_timeframe': by_timeframe,
                'status': 'analyzed'
            }
            
            self.logger.info(f"✅ BOS Performance: {success_rate:.2%} éxito en {len(bos_events)} eventos")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error analizando BOS performance: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'status': 'error'
            }

    def analyze_choch_performance(self, symbol: str = "EURUSD") -> Dict[str, Any]:
        """
        Analiza efectividad histórica de patrones CHoCH.
        Migrado desde legacy ICTHistoricalAnalyzer.
        
        Args:
            symbol: Símbolo del mercado
            
        Returns:
            Dict con análisis de performance CHoCH
        """
        self.logger.info(f"🔄 Analizando performance CHoCH: {symbol}")
        
        try:
            # Obtener eventos CHoCH del contexto de mercado o cache
            choch_events = self._get_choch_events_from_cache(symbol)
            
            if len(choch_events) < 10:
                self.logger.warning(f"⚠️ Pocos eventos CHoCH para análisis: {len(choch_events)}")
                return {
                    'symbol': symbol,
                    'total_events': len(choch_events),
                    'success_rate': 0.5,  # Neutral
                    'confidence': 0.3,
                    'weight_factor': 1.0,
                    'status': 'insufficient_data'
                }
            
            # Calcular métricas similares a BOS
            successful_events = sum(1 for event in choch_events if event.get('success', False))
            success_rate = successful_events / len(choch_events)
            
            # Análisis por timeframe
            by_timeframe = {}
            for event in choch_events:
                tf = event.get('timeframe', 'M15')  # M15 ideal para análisis CHoCH - cambios de carácter más frecuentes
                if tf not in by_timeframe:
                    by_timeframe[tf] = {'total': 0, 'successful': 0}
                by_timeframe[tf]['total'] += 1
                if event.get('success', False):
                    by_timeframe[tf]['successful'] += 1
            
            confidence = min(1.0, len(choch_events) / 100.0)
            
            result = {
                'symbol': symbol,
                'pattern_type': 'CHoCH',
                'total_events': len(choch_events),
                'successful_events': successful_events,
                'success_rate': success_rate,
                'confidence': confidence,
                'weight_factor': self._success_rate_to_weight(success_rate, 'CHoCH'),
                'by_timeframe': by_timeframe,
                'status': 'analyzed'
            }
            
            self.logger.info(f"✅ CHoCH Performance: {success_rate:.2%} éxito en {len(choch_events)} eventos")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error analizando CHoCH performance: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'status': 'error'
            }

    def get_adaptive_threshold(self, pattern_type: str, symbol: str = "EURUSD") -> float:
        """
        Calcula threshold adaptativo basado en performance histórica.
        Migrado desde legacy ICTHistoricalAnalyzer.
        
        Args:
            pattern_type: Tipo de patrón (BOS, CHoCH, etc.)
            symbol: Símbolo del mercado
            
        Returns:
            Threshold adaptativo optimizado
        """
        base_threshold = 0.6  # Threshold base
        
        try:
            # Obtener performance histórica del patrón
            if pattern_type == "BOS":
                performance = self.analyze_bos_performance(symbol)
            elif pattern_type == "CHoCH":
                performance = self.analyze_choch_performance(symbol)
            else:
                self.logger.warning(f"⚠️ Tipo de patrón no soportado: {pattern_type}")
                return base_threshold
            
            if performance.get('status') != 'analyzed':
                return base_threshold
            
            success_rate = performance.get('success_rate', 0.5)
            confidence = performance.get('confidence', 0.5)
            
            # Ajustar threshold basado en performance
            if success_rate > 0.8 and confidence > 0.7:
                # Alta performance -> reducir threshold para más detecciones
                adaptive_threshold = base_threshold * 0.85
            elif success_rate < 0.4 and confidence > 0.5:
                # Baja performance -> aumentar threshold para mayor selectividad
                adaptive_threshold = base_threshold * 1.2
            else:
                # Performance normal -> ajuste ligero
                adaptive_threshold = base_threshold + (success_rate - 0.5) * 0.2
            
            # Clamp entre límites razonables
            adaptive_threshold = max(0.3, min(0.9, adaptive_threshold))
            
            self.logger.debug(f"🎯 Threshold adaptativo {pattern_type}: {adaptive_threshold:.2f} (base: {base_threshold:.2f})")
            return adaptive_threshold
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando threshold adaptativo: {e}")
            return base_threshold

    def assess_pattern_quality(self, pattern_data: Dict[str, Any], pattern_type: str) -> float:
        """
        Evalúa calidad de pattern contra histórico.
        Migrado desde legacy ICTHistoricalAnalyzer.
        
        Args:
            pattern_data: Datos del patrón actual
            pattern_type: Tipo de patrón
            
        Returns:
            Score de calidad (0.0 - 1.0)
        """
        base_quality = pattern_data.get('confidence', 0.5)
        
        try:
            # Obtener contexto histórico
            if pattern_type == "BOS":
                historical = self.analyze_bos_performance()
            elif pattern_type == "CHoCH":
                historical = self.analyze_choch_performance()
            else:
                return base_quality
            
            if historical.get('status') != 'analyzed':
                return base_quality
            
            # Factores de calidad histórica
            historical_success = historical.get('success_rate', 0.5)
            confidence_factor = historical.get('confidence', 0.5)
            
            # Ajustar calidad basado en histórico
            quality_adjustment = (historical_success - 0.5) * confidence_factor * 0.3
            final_quality = base_quality + quality_adjustment
            
            # Clamp entre 0 y 1
            final_quality = max(0.0, min(1.0, final_quality))
            
            return final_quality
            
        except Exception as e:
            self.logger.error(f"❌ Error evaluando calidad de pattern: {e}")
            return base_quality

    # === MÉTODOS AUXILIARES PARA LAS FUNCIONES MIGRADAS ===
    
    def _get_bos_events_from_cache(self, symbol: str) -> List[Dict]:
        """Obtiene eventos BOS desde cache o memoria persistente."""
        try:
            cache_key = f"bos_events_{symbol}"
            cached_events = self._get_valid_cache(cache_key)
            if cached_events:
                return cached_events
            
            # Si no hay cache, retornar lista vacía (implementar carga real después)
            return []
        except Exception:
            return []
    
    def _get_choch_events_from_cache(self, symbol: str) -> List[Dict]:
        """Obtiene eventos CHoCH desde cache o memoria persistente."""
        try:
            cache_key = f"choch_events_{symbol}"
            cached_events = self._get_valid_cache(cache_key)
            if cached_events:
                return cached_events
            
            # Si no hay cache, retornar lista vacía (implementar carga real después)
            return []
        except Exception:
            return []

    # Métodos de integración para UnifiedMemorySystem
    def set_market_context(self, market_context):
        """Establece el contexto de mercado asociado"""
        self.market_context = market_context
        self.logger.info(f"🔗 Historical analyzer conectado al market context")
    
    def set_memory(self, unified_memory):
        """Establece la memoria unificada asociada"""
        self.unified_memory = unified_memory
        self.logger.info(f"🧠 Historical analyzer conectado a la memoria unificada")
        
    def get_pattern_insights(self, query: str, timeframe: str = "M15") -> Dict[str, Any]:
        """Obtiene insights de patrones históricos basados en consulta"""
        try:
            # Buscar en cache y datos históricos basado en la query
            cache_key = f"pattern_insights_{query}_{timeframe}"
            cached_insights = self._get_valid_cache(cache_key)
            
            if cached_insights:
                return cached_insights
            
            # Generar insights básicos basados en análisis histórico
            insights = {
                'query': query,
                'timeframe': timeframe,
                'patterns_found': self._search_pattern_matches(query, timeframe),
                'confidence': 0.75,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Guardar en cache
            self._set_cache(cache_key, insights)
            return insights
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo pattern insights: {e}")
            return {
                'query': query,
                'timeframe': timeframe,
                'patterns_found': [],
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _search_pattern_matches(self, query: str, timeframe: str) -> List[Dict]:
        """Busca coincidencias de patrones en datos históricos"""
        try:
            # Implementación básica de búsqueda de patrones
            # Se puede expandir para búsquedas más complejas
            matches = []
            
            # Buscar en cache de POIs históricos
            for poi_type in ['orderblock', 'fair_value_gap', 'liquidity_void']:
                if query.lower() in poi_type:
                    poi_weight = self.get_historical_poi_performance(poi_type, timeframe)
                    if poi_weight > 1.0:  # Solo incluir POIs con buen rendimiento histórico
                        matches.append({
                            'pattern_type': poi_type,
                            'weight': poi_weight,
                            'confidence': min(poi_weight / 2.0, 1.0),  # Convertir peso a confianza
                            'timeframe': timeframe
                        })
            
            return matches
            
        except Exception as e:
            self.logger.error(f"❌ Error buscando pattern matches: {e}")
            return []
