#!/usr/bin/env python3
"""
🧠 MARKET CONTEXT v6.0 ENTERPRISE - MEMORIA CENTRAL DEL MERCADO
=============================================================

Memoria central del sistema ICT v6.0 Enterprise con contexto persistente.
Migrado y mejorado desde proyecto principal/core/ict_engine/ict_detector.py

Funcionalidades Enterprise:
- ✅ Memoria persistente entre sesiones
- ✅ Configuración enterprise desde memory_config.json
- ✅ Cache inteligente optimizado 
- ✅ Contexto multi-timeframe correlacionado
- ✅ Integración con Smart Money concepts
- ✅ Memoria histórica de patrones ICT
- ✅ Comportamiento de trader real

Versión: v6.1.0-enterprise-memory
Fecha: 8 de Agosto 2025 - 20:15 GMT
"""

# === IMPORTS ENTERPRISE v6.0 ===
from protocols.unified_logging import get_unified_logger
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
import pandas as pd
import numpy as np

# === IMPORTS ENTERPRISE LOGGING ===
from smart_trading_logger import SmartTradingLogger

class MarketContextV6:
    """
    🧠 Memoria central del mercado para ICT Engine v6.1.0 Enterprise.
    
    Funciona como la memoria de un trader real profesional:
    - Recuerda condiciones de mercado pasadas
    - Mantiene contexto histórico de patrones
    - Aprende de experiencias anteriores
    - Persiste memoria entre sesiones
    """

    def __init__(self, memory_config_path: str = "config/memory_config.json"):
        """Inicializa el contexto de mercado con configuración enterprise."""
        
        # === CONFIGURACIÓN ENTERPRISE ===
        self.memory_config = self._load_memory_config(memory_config_path)
        self.logger = SmartTradingLogger(name="MarketContext")
        
        self.logger.info("🧠 Inicializando Market Context v6.0 Enterprise", 
                         component="market_memory")
        
        # === ESTADO ACTUAL DEL MERCADO ===
        self.current_price: float = 0.0
        self.market_bias: str = "NEUTRAL"  # BULLISH, BEARISH, NEUTRAL
        self.confidence_level: float = 0.0  # 0.0 - 1.0
        self.analysis_quality: str = "MEDIUM"  # LOW, MEDIUM, HIGH, EXCELLENT
        self.market_phase: str = "RANGING"  # RANGING, TRENDING, BREAKOUT, REVERSAL
        self.last_updated: datetime = datetime.now(timezone.utc)
        
        # === BIAS MULTI-TIMEFRAME ===
        self.timeframe_bias: Dict[str, str] = {
            "W1": "NEUTRAL",
            "D1": "NEUTRAL", 
            "H4": "NEUTRAL",
            "H1": "NEUTRAL",
            "M15": "NEUTRAL",
            "M5": "NEUTRAL",
            "M1": "NEUTRAL"
        }
        
        # === MEMORIA HISTÓRICA ICT PATTERNS ===
        self.previous_pois: List[dict] = []
        self.bos_events: List[dict] = []
        self.choch_events: List[dict] = []
        self.order_blocks: List[dict] = []  # NUEVO v6.0
        self.fvg_events: List[dict] = []    # NUEVO v6.0
        self.displacement_events: List[dict] = []  # NUEVO v6.0
        
        # === SWING POINTS HISTÓRICOS - TRADING CRITICAL ===
        self.swing_points: Dict[str, Any] = {
            "highs": [],  # List[dict] - Swing highs históricos
            "lows": [],   # List[dict] - Swing lows históricos 
            "last_high": 0.0,  # float - TRADING CRITICAL: Never None
            "last_low": 0.0    # float - TRADING CRITICAL: Never None
        }
        
        # === CONTEXTO DE SESIÓN ACTUAL - TRADING SAFE ===
        self.current_session: str = "LONDON_KILLZONE"  # Específico: London Killzone - mejor para ICT
        self.session_data: dict = {}
        self.daily_range: Dict[str, float] = {'high': 0.0, 'low': 0.0, 'mid': 0.0}
        self.trading_conditions: dict = {"liquidity": "HIGH", "volatility": "ACTIVE"}  # Condiciones de London
        
        # === MEMORIA SMART MONEY ENTERPRISE ===
        self.smart_money_context: Dict[str, Any] = {
            "institutional_bias": "NEUTRAL",
            "liquidity_pools": [],
            "market_maker_activity": {},
            "killzone_efficiency": {},
            "institutional_flow": "NEUTRAL"
        }
        
        # === KILLZONE MEMORY ===
        self.killzone_memory: Dict[str, Any] = {
            "asian_session": {"efficiency": 0.65, "recent_performance": []},
            "london_session": {"efficiency": 0.85, "recent_performance": []},
            "newyork_session": {"efficiency": 0.90, "recent_performance": []},
            "overlap_sessions": {"efficiency": 0.95, "recent_performance": []}
        }
        
        # === CONTEXTO MULTI-TIMEFRAME - TRADING SAFE ===
        self.timeframe_contexts: Dict[str, dict] = {}
        for tf in ["W1", "D1", "H4", "H1", "M15", "M5", "M1"]:
            self.timeframe_contexts[tf] = {
                "last_analysis": {},  # Empty dict instead of None
                "patterns_detected": [],
                "structure_quality": "DEVELOPING" if tf in ["M1", "M5"] else "ESTABLISHED",  # Específico por TF
                "trend_direction": "NEUTRAL",
                "last_updated": datetime.now(timezone.utc)  # Valid timestamp
            }
        
        # === CACHE ENTERPRISE ===
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_config = self.memory_config.get("cache_settings", {})
        
        # === CONFIGURACIONES ENTERPRISE ===
        self.retention_periods = self.memory_config.get("market_context", {}).get("bias_retention_periods", 50)
        self.max_poi_history = self.memory_config.get("market_context", {}).get("poi_history_max_count", 200)
        self.max_swing_points = self.memory_config.get("market_context", {}).get("swing_points_retention", 100)
        self.max_bos_events = self.memory_config.get("market_context", {}).get("bos_events_retention", 150)
        self.max_choch_events = self.memory_config.get("market_context", {}).get("choch_events_retention", 150)
        
        # === PERSISTENCIA DE MEMORIA ENTERPRISE ===
        # Usar directorio 04-DATA/memory_persistence para consistencia
        project_root = Path(__file__).parent.parent.parent
        memory_persistence_dir = str(project_root / "04-DATA" / "memory_persistence")
        self.memory_cache_dir = self._cache_config.get("cache_directory", memory_persistence_dir)
        self._ensure_cache_directory()
        
        # === INICIALIZACIÓN EXITOSA ===
        self.logger.info(
            f"✅ Market Context v6.0 Enterprise inicializado - "
            f"Retención: {self.retention_periods} periodos, "
            f"Max POIs: {self.max_poi_history}, "
            f"Cache: {self.memory_cache_dir}",
            component="market_memory"
        )
    
    def _load_memory_config(self, config_path: str) -> dict:
        """Carga configuración de memoria enterprise."""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config
            else:
                # Configuración por defecto si no existe el archivo
                return {
                    "memory_management": {
                        "max_memory_gb": 4.0,
                        "cache_timeout_minutes": 30,
                        "historical_analysis_depth": 1000,
                        "context_retention_hours": 168
                    },
                    "market_context": {
                        "bias_retention_periods": 50,
                        "poi_history_max_count": 200,
                        "swing_points_retention": 100,
                        "bos_events_retention": 150,
                        "choch_events_retention": 150
                    }
                }
        except Exception as e:
            self.logger.error(f"Error cargando memory_config: {e}", component="market_memory")
            return {}
    
    def _ensure_cache_directory(self) -> None:
        """Asegura que el directorio de cache existe."""
        try:
            os.makedirs(self.memory_cache_dir, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Error creando directorio cache: {e}", component="market_memory")
    
    def update_market_context(self, analysis_results: Dict[str, Any]) -> None:
        """
        Actualiza el contexto de mercado con nuevos resultados.
        Funciona como un trader real actualizando su percepción del mercado.
        
        TRADING CRITICAL: Valida todos los datos de entrada para evitar None o valores inválidos.
        """
        try:
            # TRADING CRITICAL: Validar que analysis_results no sea None o vacío
            if not analysis_results or not isinstance(analysis_results, dict):
                self.logger.error("❌ TRADING CRITICAL: analysis_results es None o inválido", 
                                  component="market_memory")
                return
            
            # Actualizar timestamp - siempre válido
            self.last_updated = datetime.now(timezone.utc)
            
            # Actualizar precio actual - validar que sea un número válido
            if 'current_price' in analysis_results:
                price = analysis_results['current_price']
                if price is not None and (isinstance(price, (int, float)) and price > 0):
                    self.current_price = float(price)
                else:
                    self.logger.warning("⚠️ TRADING WARNING: current_price inválido ignorado", 
                                        component="market_memory")
            
            # Actualizar bias si está disponible - validar valores permitidos
            if 'market_bias' in analysis_results:
                bias = analysis_results['market_bias']
                valid_bias = ["BULLISH", "BEARISH", "NEUTRAL"]
                if bias and bias in valid_bias:
                    old_bias = self.market_bias
                    self.market_bias = bias
                    
                    # Log cambio de bias (memoria de cambios significativos)
                    if old_bias != self.market_bias:
                        self.logger.info(
                            f"📈 Cambio de bias detectado: {old_bias} → {self.market_bias}",
                            component="market_memory"
                        )
                else:
                    self.logger.warning(f"⚠️ TRADING WARNING: market_bias inválido '{bias}' ignorado", 
                                        component="market_memory")
            
            # Actualizar bias multi-timeframe - validar timeframes
            if 'timeframe_bias' in analysis_results:
                tf_bias = analysis_results['timeframe_bias']
                if tf_bias and isinstance(tf_bias, dict):
                    valid_bias = ["BULLISH", "BEARISH", "NEUTRAL"]
                    for tf, bias in tf_bias.items():
                        if tf in self.timeframe_bias and bias in valid_bias:
                            self.timeframe_bias[tf] = bias
                        else:
                            self.logger.warning(f"⚠️ TRADING WARNING: timeframe_bias inválido {tf}:{bias}", 
                                                component="market_memory")
            
            # Actualizar contexto multi-timeframe - validar datos
            if 'timeframe_results' in analysis_results:
                tf_results = analysis_results['timeframe_results']
                if tf_results and isinstance(tf_results, dict):
                    for tf, tf_data in tf_results.items():
                        if tf in self.timeframe_contexts and tf_data:
                            self.timeframe_contexts[tf].update({
                                'last_analysis': tf_data if isinstance(tf_data, dict) else {},
                                'last_updated': self.last_updated
                            })
            
            # Actualizar memoria de patrones ICT - validación robusta
            self._update_pattern_memory(analysis_results)
            
            # Actualizar memoria Smart Money - validación robusta
            self._update_smart_money_memory(analysis_results)
            
            self.logger.debug(
                f"Context actualizado - Bias: {self.market_bias}, "
                f"Phase: {self.market_phase}, Quality: {self.analysis_quality}",
                component="market_memory"
            )
            
        except Exception as e:
            self.logger.error(f"Error actualizando market context: {e}", component="market_memory")
    
    def _update_pattern_memory(self, analysis_results: Dict[str, Any]) -> None:
        """Actualiza memoria de patrones ICT detectados."""
        try:
            # Actualizar POIs
            if 'pois_detected' in analysis_results:
                new_pois = analysis_results['pois_detected']
                self.previous_pois.extend(new_pois)
                # Mantener límite de memoria
                if len(self.previous_pois) > self.max_poi_history:
                    self.previous_pois = self.previous_pois[-self.max_poi_history:]
            
            # Actualizar BOS events
            if 'bos_detected' in analysis_results:
                bos_event = {
                    'timestamp': self.last_updated,
                    'data': analysis_results['bos_detected'],
                    'price': self.current_price
                }
                self.bos_events.append(bos_event)
                if len(self.bos_events) > self.max_bos_events:
                    self.bos_events = self.bos_events[-self.max_bos_events:]
            
            # Actualizar CHoCH events
            if 'choch_detected' in analysis_results:
                choch_event = {
                    'timestamp': self.last_updated,
                    'data': analysis_results['choch_detected'],
                    'price': self.current_price
                }
                self.choch_events.append(choch_event)
                if len(self.choch_events) > self.max_choch_events:
                    self.choch_events = self.choch_events[-self.max_choch_events:]

            # NUEVO: Integrar CHoCH desde datos genéricos de patrón (pattern_type == 'CHoCH')
            if str(analysis_results.get('pattern_type', '')).upper() == 'CHOCH':
                # Normalizar estructura mínima requerida por consumidores
                # Normalizar confianza a escala 0-100 si viene en 0-1
                raw_conf = analysis_results.get('confidence', 0.0)
                try:
                    conf_val = float(raw_conf or 0.0)
                except Exception:
                    conf_val = 0.0
                confidence_pct = conf_val * 100.0 if conf_val <= 1.0 else conf_val

                choch_data = {
                    'direction': analysis_results.get('direction', analysis_results.get('metadata', {}).get('direction', 'NEUTRAL') if isinstance(analysis_results.get('metadata'), dict) else 'NEUTRAL'),
                    'confidence': confidence_pct,
                    'timeframe': analysis_results.get('timeframe', 'UNKNOWN'),
                    'break_level': analysis_results.get('break_level', analysis_results.get('entry_price', self.current_price)),
                    'target_level': analysis_results.get('target_level', analysis_results.get('entry_price', self.current_price)),
                    'symbol': analysis_results.get('symbol', None),
                    'metadata': analysis_results.get('metadata', {})
                }
                choch_event = {
                    'timestamp': self.last_updated,
                    'data': choch_data,
                    'price': self.current_price
                }
                self.choch_events.append(choch_event)
                if len(self.choch_events) > self.max_choch_events:
                    self.choch_events = self.choch_events[-self.max_choch_events:]
            
            # Actualizar swing points - TRADING CRITICAL VALIDATION
            if 'swing_points' in analysis_results:
                swing_data = analysis_results['swing_points']
                
                # Validar que swing_data no sea None o vacío
                if swing_data and isinstance(swing_data, dict):
                    if 'high' in swing_data and swing_data['high'] is not None:
                        high_price = float(swing_data['high'])
                        if high_price > 0:  # Validar precio válido
                            self.swing_points['highs'].append({
                                'timestamp': self.last_updated,
                                'price': high_price,
                                'data': swing_data
                            })
                            self.swing_points['last_high'] = high_price
                    
                    if 'low' in swing_data and swing_data['low'] is not None:
                        low_price = float(swing_data['low'])
                        if low_price > 0:  # Validar precio válido
                            self.swing_points['lows'].append({
                                'timestamp': self.last_updated,
                                'price': low_price,
                                'data': swing_data
                            })
                            self.swing_points['last_low'] = low_price
                
                # Mantener límite de swing points - SAFE CASTING
                highs_list = self.swing_points['highs']
                lows_list = self.swing_points['lows']
                
                if isinstance(highs_list, list) and len(highs_list) > self.max_swing_points:
                    self.swing_points['highs'] = highs_list[-self.max_swing_points:]
                if isinstance(lows_list, list) and len(lows_list) > self.max_swing_points:
                    self.swing_points['lows'] = lows_list[-self.max_swing_points:]
                    
        except Exception as e:
            self.logger.error(f"Error actualizando pattern memory: {e}", component="market_memory")
    
    def _update_smart_money_memory(self, analysis_results: Dict[str, Any]) -> None:
        """Actualiza memoria de conceptos Smart Money."""
        try:
            if 'smart_money_analysis' in analysis_results:
                sm_data = analysis_results['smart_money_analysis']
                
                # Actualizar bias institucional
                if 'institutional_bias' in sm_data:
                    self.smart_money_context['institutional_bias'] = sm_data['institutional_bias']
                
                # Actualizar liquidity pools
                if 'liquidity_pools' in sm_data:
                    self.smart_money_context['liquidity_pools'] = sm_data['liquidity_pools']
                
                # Actualizar eficiencia de killzones
                if 'killzone_efficiency' in sm_data:
                    for session, efficiency in sm_data['killzone_efficiency'].items():
                        if session in self.killzone_memory:
                            self.killzone_memory[session]['efficiency'] = efficiency
        
        except Exception as e:
            self.logger.error(f"Error actualizando smart money memory: {e}", component="market_memory")
    
    def get_historical_context(self, lookback_periods: int = 50) -> Dict[str, Any]:
        """
        Recupera contexto histórico para análisis.
        Como un trader real consultando su experiencia pasada.
        
        Args:
            lookback_periods: Número de períodos para análisis histórico (default: 50)
        """
        # TRADING CRITICAL: Siempre usar un valor válido, nunca None
        if lookback_periods <= 0:
            lookback_periods = self.retention_periods
        
        try:
            return {
                'market_bias_history': self._get_bias_history(lookback_periods),
                'recent_patterns': self._get_recent_patterns(lookback_periods),
                'swing_points_context': self._get_swing_context(lookback_periods),
                'smart_money_context': self.smart_money_context.copy(),
                'timeframe_correlation': self._get_timeframe_correlation(),
                'market_memory_quality': self._calculate_memory_quality()
            }
        
        except Exception as e:
            self.logger.error(f"Error obteniendo contexto histórico: {e}", component="market_memory")
            return {}
    
    def _get_bias_history(self, periods: int) -> List[dict]:
        """Obtiene historial de bias para contexto."""
        # Implementación simplificada - en producción cargaría de persistencia
        return [
            {
                'timestamp': self.last_updated,
                'bias': self.market_bias,
                'confidence': self.confidence_level
            }
        ]
    
    def _get_recent_patterns(self, periods: int) -> Dict[str, Any]:
        """Obtiene patrones recientes para contexto."""
        return {
            'recent_bos': self.bos_events[-periods:] if self.bos_events else [],
            'recent_choch': self.choch_events[-periods:] if self.choch_events else [],
            'recent_pois': self.previous_pois[-periods:] if self.previous_pois else []
        }
    
    def _get_swing_context(self, periods: int) -> Dict[str, Any]:
        """Obtiene contexto de swing points - TRADING SAFE."""
        # TRADING CRITICAL: Asegurar que siempre devolvemos listas válidas
        highs_list = self.swing_points.get('highs', [])
        lows_list = self.swing_points.get('lows', [])
        
        # Validar que sean listas antes de hacer slicing
        if not isinstance(highs_list, list):
            highs_list = []
        if not isinstance(lows_list, list):
            lows_list = []
            
        return {
            'recent_highs': highs_list[-periods:] if highs_list else [],
            'recent_lows': lows_list[-periods:] if lows_list else [],
            'last_high': self.swing_points.get('last_high', 0.0),
            'last_low': self.swing_points.get('last_low', 0.0)
        }
    
    def get_last_choch_for_trading(self, symbol: Optional[str] = None, timeframe: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        🎯 TRADING CRITICAL: Obtiene el último CHoCH válido para trading
        
        Returns:
            Dict con información del último CHoCH o None si no hay
            
        Structure:
            {
                'timestamp': datetime,
                'direction': 'BULLISH'|'BEARISH',
                'price': float,
                'confidence': float,
                'timeframe': str,
                'break_level': float,
                'target_level': float,
                'age_minutes': int,
                'is_valid_for_trading': bool,
                'strength': 'STRONG'|'MODERATE'|'WEAK'
            }
        """
        if not self.choch_events:
            return None

        # Seleccionar el evento más reciente, con filtrado opcional por símbolo/TF si se especifica
        last_choch = None
        if symbol or timeframe:
            for ev in reversed(self.choch_events):
                data = ev.get('data', {}) if isinstance(ev, dict) else {}
                if symbol and data.get('symbol') != symbol:
                    continue
                if timeframe and data.get('timeframe') != timeframe:
                    continue
                last_choch = ev
                break
            if last_choch is None:
                return None
        else:
            last_choch = self.choch_events[-1]
        
        try:
            # Extraer datos del CHoCH
            choch_data = last_choch.get('data', {})
            timestamp = last_choch.get('timestamp')
            price = last_choch.get('price', 0.0)
            
            # Calcular edad en minutos
            age_minutes = 0
            if timestamp and self.last_updated:
                age_delta = self.last_updated - timestamp
                age_minutes = age_delta.total_seconds() / 60
            
            # Determinar si es válido para trading (max 4 horas)
            is_valid = age_minutes <= 240  # 4 horas
            
            # Extraer información específica del CHoCH
            direction = choch_data.get('direction', 'NEUTRAL')
            confidence = choch_data.get('confidence', 0.0)
            timeframe = choch_data.get('timeframe', 'UNKNOWN')
            break_level = choch_data.get('break_level', price)
            target_level = choch_data.get('target_level', price)
            
            # Determinar fuerza basada en confianza y edad
            if confidence >= 85 and age_minutes <= 60:
                strength = 'STRONG'
            elif confidence >= 75 and age_minutes <= 120:
                strength = 'MODERATE'
            else:
                strength = 'WEAK'
            
            return {
                'timestamp': timestamp,
                'direction': direction,
                'price': price,
                'confidence': confidence,
                'timeframe': timeframe,
                'break_level': break_level,
                'target_level': target_level,
                'age_minutes': int(age_minutes),
                'is_valid_for_trading': is_valid,
                'strength': strength
            }
            
        except Exception as e:
            self.logger.error(f"Error processing last CHoCH: {e}", component="market_memory")
            return None
    
    def get_valid_choch_levels_for_trading(self, symbol: Optional[str] = None, timeframe: Optional[str] = None) -> Dict[str, Any]:
        """
        🎯 TRADING CRITICAL: Obtiene niveles CHoCH válidos para trading
        
        Returns:
            Dict con niveles clave del último CHoCH válido
        """
        last_choch = self.get_last_choch_for_trading(symbol=symbol, timeframe=timeframe)
        
        if not last_choch or not last_choch['is_valid_for_trading']:
            return {
                'has_valid_choch': False,
                'break_level': 0.0,
                'target_level': 0.0,
                'direction': 'NEUTRAL',
                'confidence': 0.0
            }
        
        return {
            'has_valid_choch': True,
            'break_level': last_choch['break_level'],
            'target_level': last_choch['target_level'],
            'direction': last_choch['direction'],
            'confidence': last_choch['confidence'],
            'timeframe': last_choch['timeframe'],
            'age_minutes': last_choch['age_minutes'],
            'strength': last_choch['strength'],
            'trading_bias': 'BUY' if last_choch['direction'] == 'BULLISH' else 'SELL' if last_choch['direction'] == 'BEARISH' else 'NEUTRAL'
        }
    
    def _get_timeframe_correlation(self) -> Dict[str, str]:
        """Obtiene correlación entre timeframes."""
        return self.timeframe_bias.copy()
    
    def _calculate_memory_quality(self) -> str:
        """Calcula calidad de la memoria actual."""
        total_patterns = len(self.previous_pois) + len(self.bos_events) + len(self.choch_events)
        
        if total_patterns > 100:
            return "EXCELLENT"
        elif total_patterns > 50:
            return "HIGH"
        elif total_patterns > 20:
            return "MEDIUM"
        else:
            return "LOW"
    
    def persist_memory_state(self) -> None:
        """
        Persiste estado de memoria para sesiones futuras.
        Actualiza metadata y usa directorio enterprise configurado.
        """
        try:
            # Determinar estado actual del sistema
            total_events = len(self.previous_pois) + len(self.bos_events) + len(self.choch_events)
            system_state = 'EXPERIENCED' if total_events > 10 else 'LEARNING'
            
            memory_state = {
                'metadata': {
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'version': 'v6.1.0-enterprise',
                    'state_type': 'market_context',
                    'system_state': system_state,
                    'total_events_analyzed': total_events
                },
                'timestamp': self.last_updated.isoformat(),
                'market_context': {
                    'market_bias': self.market_bias,
                    'confidence_level': self.confidence_level,
                    'analysis_quality': self.analysis_quality,
                    'market_phase': self.market_phase,
                    'timeframe_bias': self.timeframe_bias
                },
                'pattern_memory': {
                    'previous_pois': self.previous_pois[-50:],  # Solo recientes
                    'bos_events': self.bos_events[-50:],
                    'choch_events': self.choch_events[-50:],
                    'order_blocks': self.order_blocks[-50:] if hasattr(self, 'order_blocks') else [],
                    'fvg_events': self.fvg_events[-50:] if hasattr(self, 'fvg_events') else [],
                    'displacement_events': self.displacement_events[-50:] if hasattr(self, 'displacement_events') else []
                },
                'smart_money_context': self.smart_money_context,
                'swing_points': {
                    'highs': (self.swing_points.get('highs', []) or [])[-20:],
                    'lows': (self.swing_points.get('lows', []) or [])[-20:],
                    'last_high': self.swing_points.get('last_high', 0.0),
                    'last_low': self.swing_points.get('last_low', 0.0)
                }
            }
            
            # Guardar en archivo
            memory_file = os.path.join(self.memory_cache_dir, 'market_context_state.json')
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_state, f, indent=2, default=str)
            
            self.logger.info(f"💾 Contexto de mercado actualizado en {memory_file}", 
                               component="market_memory")
            
        except Exception as e:
            self.logger.error(f"Error persistiendo memoria: {e}", component="market_memory")
    
    def _create_initial_memory_state(self) -> bool:
        """
        🧠 Crea estado de memoria inicial para primera ejecución del sistema.
        Establece contexto inicial inteligente para arranque limpio.
        """
        try:
            initial_state = {
                'metadata': {
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'version': 'v6.1.0-enterprise',
                    'state_type': 'market_context',
                    'system_state': 'FIRST_RUN_INITIALIZED'
                },
                'market_context': {
                    'market_bias': 'NEUTRAL',
                    'confidence_level': 0.5,
                    'analysis_quality': 'MEDIUM',
                    'market_phase': 'RANGING',
                    'timeframe_bias': {
                        "W1": "NEUTRAL", "D1": "NEUTRAL", "H4": "NEUTRAL",
                        "H1": "NEUTRAL", "M15": "NEUTRAL", "M5": "NEUTRAL", "M1": "NEUTRAL"
                    }
                },
                'pattern_memory': {
                    'previous_pois': [],
                    'bos_events': [],
                    'choch_events': [],
                    'order_blocks': [],
                    'fvg_events': [],
                    'displacement_events': []
                },
                'smart_money_context': {
                    'institutional_bias': 'NEUTRAL',
                    'liquidity_pools': [],
                    'market_maker_activity': {},
                    'killzone_efficiency': {
                        'asian_session': 0.65,
                        'london_session': 0.85,
                        'newyork_session': 0.90,
                        'overlap_sessions': 0.95
                    },
                    'institutional_flow': 'NEUTRAL'
                },
                'swing_points': {
                    'highs': [],
                    'lows': [],
                    'last_high': 0.0,
                    'last_low': 0.0
                }
            }
            
            memory_file = os.path.join(self.memory_cache_dir, 'market_context_state.json')
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(initial_state, f, indent=2)
            
            self.logger.info(f"🧠 Estado de memoria inicial creado en {memory_file}", 
                             component="market_memory")
            self.logger.info("✅ Market Context listo para acumular experiencia", 
                             component="market_memory")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creando estado inicial de memoria: {e}", component="market_memory")
            return False

    def restore_memory_state(self) -> bool:
        """
        Restaura estado de memoria de sesiones pasadas.
        Si no existe, crea estado inicial automáticamente.
        """
        try:
            memory_file = os.path.join(self.memory_cache_dir, 'market_context_state.json')
            
            if not os.path.exists(memory_file):
                self.logger.info("Primera ejecución detectada - Inicializando contexto de mercado", 
                                 component="market_memory")
                
                # Crear estado inicial automáticamente
                if self._create_initial_memory_state():
                    # Intentar cargar el estado recién creado
                    return self.restore_memory_state()
                else:
                    self.logger.error("No se pudo crear estado inicial de memoria", 
                                      component="market_memory")
                    return False
            
            with open(memory_file, 'r', encoding='utf-8') as f:
                memory_state = json.load(f)

            # Helper: parse ISO timestamps back to datetime
            def _to_datetime(value):
                from datetime import datetime, timezone
                if isinstance(value, datetime):
                    return value
                if isinstance(value, str):
                    try:
                        # Support possible 'Z' suffix
                        iso = value.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(iso)
                        return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
                    except Exception:
                        return self.last_updated
                return self.last_updated

            def _normalize_event_timestamps(events):
                if not isinstance(events, list):
                    return events
                for ev in events:
                    try:
                        if isinstance(ev, dict) and 'timestamp' in ev:
                            ev['timestamp'] = _to_datetime(ev['timestamp'])
                    except Exception:
                        pass
                return events
            
            # Restaurar timestamp global del estado si existe
            if 'timestamp' in memory_state:
                self.last_updated = _to_datetime(memory_state.get('timestamp'))

            # Restaurar contexto de mercado
            if 'market_context' in memory_state:
                mc = memory_state['market_context']
                self.market_bias = mc.get('market_bias', 'NEUTRAL')
                self.confidence_level = mc.get('confidence_level', 0.0)
                self.analysis_quality = mc.get('analysis_quality', 'MEDIUM')
                self.market_phase = mc.get('market_phase', 'RANGING')
                self.timeframe_bias = mc.get('timeframe_bias', self.timeframe_bias)
            
            # Restaurar memoria de patrones - TRADING SAFE
            if 'pattern_memory' in memory_state:
                pm = memory_state['pattern_memory']
                self.previous_pois = _normalize_event_timestamps(pm.get('previous_pois', []))
                self.bos_events = _normalize_event_timestamps(pm.get('bos_events', []))
                self.choch_events = _normalize_event_timestamps(pm.get('choch_events', []))
                self.order_blocks = _normalize_event_timestamps(pm.get('order_blocks', []))
                self.fvg_events = _normalize_event_timestamps(pm.get('fvg_events', []))
                self.displacement_events = _normalize_event_timestamps(pm.get('displacement_events', []))
            
            # Restaurar contexto Smart Money
            if 'smart_money_context' in memory_state:
                smc = memory_state['smart_money_context']
                self.smart_money_context.update(smc)
            
            # Restaurar swing points - TRADING CRITICAL
            if 'swing_points' in memory_state:
                sp = memory_state['swing_points']
                self.swing_points['highs'] = sp.get('highs', [])
                self.swing_points['lows'] = sp.get('lows', [])
                self.swing_points['last_high'] = sp.get('last_high', 0.0)
                self.swing_points['last_low'] = sp.get('last_low', 0.0)
            
            # Log de información sobre el estado cargado
            metadata = memory_state.get('metadata', {})
            system_state = metadata.get('system_state', 'UNKNOWN')
            
            if system_state == 'FIRST_RUN_INITIALIZED':
                self.logger.info("🧠 Contexto inicial cargado - Sistema listo para análisis", 
                                 component="market_memory")
            else:
                self.logger.info(f"📚 Contexto de mercado restaurado desde {memory_file}", 
                                 component="market_memory")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error restaurando memoria: {e}", component="market_memory")
            return False
    
    # === CACHE METHODS (HEREDADOS Y MEJORADOS) ===
    
    def get_cache_key(self, key: str, timeframe: str = "default") -> str:
        """Genera clave de caché única."""
        return f"{timeframe}_{key}"
    
    def is_cache_valid(self, cache_key: str, max_age_minutes: int = 5) -> bool:
        """Verifica si un valor en caché sigue siendo válido."""
        if cache_key not in self._cache_timestamps:
            return False
        
        cache_time = self._cache_timestamps[cache_key]
        age = datetime.now(timezone.utc) - cache_time
        return age.total_seconds() < (max_age_minutes * 60)
    
    def set_cache(self, cache_key: str, value: Any) -> None:
        """Establece un valor en caché."""
        self._cache[cache_key] = value
        self._cache_timestamps[cache_key] = datetime.now(timezone.utc)
    
    def get_cache(self, cache_key: str) -> Optional[Any]:
        """Obtiene un valor del caché si es válido."""
        if self.is_cache_valid(cache_key):
            return self._cache.get(cache_key)
        return None
    
    def clear_cache(self) -> None:
        """Limpia cache para optimización de memoria."""
        self._cache.clear()
        self._cache_timestamps.clear()
        self.logger.debug("Cache de memoria limpiado", component="market_memory")
    
    # === INTEGRACIÓN CON ICTDataManager ===
    
    def integrate_with_ict_data_manager(self, ict_data_manager) -> None:
        """Integración con ICTDataManager existente para memoria unificada."""
        try:
            # Registrar callback para actualizaciones de datos
            if hasattr(ict_data_manager, 'register_context_callback'):
                ict_data_manager.register_context_callback(self.update_market_context)
            
            self.logger.info("🔗 Integración con ICTDataManager completada", 
                               component="market_memory")
            
        except Exception as e:
            self.logger.error(f"Error integrando con ICTDataManager: {e}", 
                                component="market_memory")
    
    # === INTEGRACIÓN CON SISTEMA UNIFICADO ===
    
    def set_historical_analyzer(self, historical_analyzer) -> None:
        """
        🔗 Establece conexión con el analizador histórico
        
        Args:
            historical_analyzer: Instancia del ICTHistoricalAnalyzerV6
        """
        try:
            self.historical_analyzer = historical_analyzer
            self.logger.info("🔗 Historical Analyzer conectado exitosamente", 
                               component="market_memory")
            
            # Sincronizar datos si el analizador está disponible
            if hasattr(historical_analyzer, 'sync_with_market_context'):
                historical_analyzer.sync_with_market_context(self)
                
        except Exception as e:
            self.logger.error(f"Error conectando Historical Analyzer: {e}", 
                                component="market_memory")
    
    def set_memory(self, unified_memory) -> None:
        """
        🧠 Establece conexión con el sistema de memoria unificado
        
        Args:
            unified_memory: Instancia del UnifiedMemorySystem
        """
        try:
            self.unified_memory = unified_memory
            self.logger.info("🧠 Unified Memory System conectado exitosamente", 
                               component="market_memory")
                               
        except Exception as e:
            self.logger.error(f"Error conectando Unified Memory: {e}", 
                                component="market_memory")
    
    def get_contextual_insight(self, query: str, timeframe: str) -> Dict[str, Any]:
        """
        💡 Obtiene insight contextual basado en memoria histórica
        
        Args:
            query: Consulta para obtener insight
            timeframe: Marco temporal para el contexto
            
        Returns:
            Dict con el insight contextual
        """
        try:
            insight = {
                'query': query,
                'timeframe': timeframe,
                'market_bias': self.market_bias,
                'market_phase': self.market_phase,
                'recent_patterns': self._get_recent_patterns(10),
                'confidence': self.confidence_level,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Agregar contexto histórico si está disponible
            if hasattr(self, 'historical_analyzer') and self.historical_analyzer:
                if hasattr(self.historical_analyzer, 'get_contextual_data'):
                    historical_data = self.historical_analyzer.get_contextual_data(query, timeframe)
                    insight['historical_context'] = historical_data
            
            return insight
            
        except Exception as e:
            self.logger.error(f"Error generando insight contextual: {e}", 
                                component="market_memory")
            return {
                'query': query,
                'timeframe': timeframe,
                'error': str(e),
                'status': 'error'
            }
    
    def update_from_data(self, new_data: Dict[str, Any], symbol: str) -> None:
        """
        🔄 Actualiza contexto desde nuevos datos
        
        Args:
            new_data: Nuevos datos de mercado
            symbol: Símbolo del instrumento
        """
        try:
            # Actualizar contexto principal
            self.update_market_context(new_data)
            
            # Log de actualización
            self.logger.info(f"💾 Contexto actualizado para {symbol}", 
                               component="market_memory")
                               
        except Exception as e:
            self.logger.error(f"Error actualizando desde datos: {e}", 
                                component="market_memory")

    def __repr__(self) -> str:
        """Representación legible del contexto v6.0."""
        total_patterns = len(self.previous_pois) + len(self.bos_events) + len(self.choch_events)
        
        return (
            f"MarketContextV6("
            f"bias={self.market_bias}, "
            f"phase={self.market_phase}, "
            f"quality={self.analysis_quality}, "
            f"patterns_memory={total_patterns}, "
            f"timeframes_active={len([tf for tf, bias in self.timeframe_bias.items() if bias != 'NEUTRAL'])}, "
            f"last_update={self.last_updated.strftime('%H:%M:%S')})"
        )
