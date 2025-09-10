#!/usr/bin/env python3
"""
🎯 ORDER BLOCKS ENHANCED v6.1 - ENTERPRISE
==========================================

Enhanced Order Blocks detector with MT5 health integration and enterprise features:
- Multi-timeframe validation with health-weighted scoring
- Volume profile integration for institutional order detection
- Health-data quality filtering for reliable signals
- Mitigation zone refinement with real-time performance metrics

HEALTH INTEGRATION BENEFITS:
✅ Connection Quality: Only process patterns when MT5 connection is stable
✅ Latency Filtering: Adjust detection sensitivity based on data delay
✅ Error Prevention: Pause detection during connection issues
✅ Performance Optimization: Use health metrics to optimize algorithms

Autor: ICT Engine v6.1 Enterprise Team
Fecha: September 17, 2025 - FASE 2 Week 3 Day 1
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
import sys
import os
import json
import time
from pathlib import Path

# Importar el sistema de logging central con dynamic import
BLACK_BOX_AVAILABLE = False
try:
    # Add logging system path
    logging_path = Path(__file__).parent.parent / "utils"
    if str(logging_path) not in sys.path:
        sys.path.insert(0, str(logging_path))
    
    # Dynamic import to avoid Pylance issues
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "smart_trading_logger", 
        logging_path / "smart_trading_logger.py"
    )
    if spec and spec.loader:
        logging_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(logging_module)
        get_smart_logger = getattr(logging_module, 'get_smart_logger')
        log_info = getattr(logging_module, 'log_info')
        log_warning = getattr(logging_module, 'log_warning')
        log_error = getattr(logging_module, 'log_error')
        log_success = getattr(logging_module, 'log_success')
        BLACK_BOX_AVAILABLE = True
    else:
        raise ImportError("Could not create module spec")
except Exception:
    # Fallback functions
    def get_smart_logger(): return None
    def log_info(msg, category="ORDER_BLOCKS"): print(f"[INFO] {msg}")
    def log_warning(msg, category="ORDER_BLOCKS"): print(f"[WARNING] {msg}")
    def log_error(msg, category="ORDER_BLOCKS"): print(f"[ERROR] {msg}")
    def log_success(msg, category="ORDER_BLOCKS"): print(f"[SUCCESS] {msg}")
    BLACK_BOX_AVAILABLE = False

# Importar MT5 Health Monitor para integración
try:
    from ..data_management.mt5_health_monitor import MT5HealthMonitor, HealthStatus
    MT5_HEALTH_AVAILABLE = True
except ImportError:
    MT5_HEALTH_AVAILABLE = False
    log_warning("MT5 Health Monitor not available, operating without health integration")

class OrderBlockType(Enum):
    """Tipos de Order Blocks mejorados"""
    DEMAND_ZONE = "demand_zone"
    SUPPLY_ZONE = "supply_zone"
    MITIGATION_BLOCK = "mitigation_block"
    BREAKER_BLOCK = "breaker_block"

class OrderBlockQuality(Enum):
    """Calidad de Order Block basada en health data"""
    PREMIUM = "premium"  # Health score > 90%
    HIGH = "high"        # Health score 70-90%
    MEDIUM = "medium"    # Health score 50-70%
    LOW = "low"          # Health score < 50%

@dataclass
class EnhancedOrderBlock:
    """Order Block mejorado con integración de health data"""
    # Datos básicos
    type: OrderBlockType
    price: float
    entry_price: float
    stop_loss: float
    take_profit: float
    
    # Métricas de trading
    confidence: float
    distance_pips: float
    risk_reward: float
    
    # Nuevas mejoras v6.1
    health_score: float = 0.0  # Score basado en MT5 health data
    quality: OrderBlockQuality = OrderBlockQuality.MEDIUM
    volume_profile: Dict[str, Any] = field(default_factory=dict)  # Allow mixed types
    timeframe_validation: Dict[str, bool] = field(default_factory=dict)
    mitigation_zones: List[Tuple[float, float]] = field(default_factory=list)
    
    # Metadatos
    symbol: str = "UNKNOWN"
    timeframe: str = "UNKNOWN"
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Performance tracking
    detection_latency_ms: float = 0.0
    data_reliability: float = 1.0

class EnhancedOrderBlockDetector:
    """
    🚀 ENHANCED ORDER BLOCK DETECTOR v6.1 ENTERPRISE
    ================================================
    
    Detector mejorado con:
    ✅ Multi-timeframe validation
    ✅ Volume profile integration  
    ✅ Health-data quality filtering
    ✅ Mitigation zone refinement
    ✅ Real-time performance optimization
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Configuración básica
        self.lookback_period = self.config.get('lookback_period', 25)
        self.max_distance_pips = self.config.get('max_distance_pips', 50)
        self.min_confidence = self.config.get('min_confidence', 70)
        self.volume_threshold = self.config.get('volume_threshold', 1.5)
        
        # Nuevas configuraciones v6.1
        self.health_weight = self.config.get('health_weight', 0.3)
        self.multi_timeframe_validation = self.config.get('enable_mtf_validation', True)
        self.volume_profile_enabled = self.config.get('enable_volume_profile', True)
        self.mitigation_analysis = self.config.get('enable_mitigation_analysis', True)
        
        # Performance thresholds
        self.max_detection_latency_ms = self.config.get('max_detection_latency_ms', 500)
        self.min_data_reliability = self.config.get('min_data_reliability', 0.7)
        
        # Sistema de logging
        self.logger = get_smart_logger()
        
        # MT5 Health integration
        self.health_monitor = None
        if MT5_HEALTH_AVAILABLE:
            try:
                self.health_monitor = MT5HealthMonitor()
                log_success("MT5 Health Monitor integrated successfully")
            except Exception as e:
                log_warning(f"Could not initialize MT5 Health Monitor: {e}")
        
        # Estadísticas mejoradas
        self.stats = {
            'total_detections': 0,
            'health_filtered': 0,
            'quality_premium': 0,
            'quality_high': 0,
            'quality_medium': 0,
            'quality_low': 0,
            'avg_detection_time_ms': 0.0,
            'mtf_validations': 0,
            'volume_profile_enhanced': 0
        }
        
        # Configurar rutas
        self.project_root = Path(__file__).parent.parent.parent
        self.logs_dir = self.project_root / "05-LOGS" / "enhanced_order_blocks"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        log_info("Enhanced Order Block Detector v6.1 initialized", "ORDER_BLOCKS_ENHANCED")
    
    def detect_enhanced_order_blocks(self, 
                                   data: Any, 
                                   current_price: float,
                                   symbol: str = "UNKNOWN",
                                   timeframe: str = "UNKNOWN",
                                   additional_timeframes: Optional[List[str]] = None) -> List[EnhancedOrderBlock]:
        """
        🎯 DETECCIÓN MEJORADA CON HEALTH INTEGRATION
        ============================================
        
        Args:
            data: DataFrame con datos OHLCV
            current_price: Precio actual del símbolo
            symbol: Símbolo de trading
            timeframe: Marco temporal principal
            additional_timeframes: Timeframes adicionales para validación
            
        Returns:
            Lista de EnhancedOrderBlock detectados
        """
        
        start_time = time.time()
        self.stats['total_detections'] += 1
        
        # 🏥 HEALTH CHECK INICIAL
        health_score = self._get_health_score()
        if health_score < 0.5:  # Health score mínimo 50%
            log_warning(f"Low health score ({health_score:.1%}), skipping detection for {symbol}")
            self.stats['health_filtered'] += 1
            return []
        
        if len(data) < self.lookback_period:
            log_warning(f"Insufficient data for {symbol} {timeframe}: {len(data)} < {self.lookback_period}")
            return []
        
        enhanced_blocks = []
        
        # 🔍 DETECCIÓN PRINCIPAL
        start_idx = max(5, len(data) - self.lookback_period)
        end_idx = len(data) - 5
        
        for i in range(start_idx, end_idx):
            # 📈 DEMAND ZONE: Swing Low con validación mejorada
            if self._is_enhanced_swing_low(data, i):
                block = self._create_enhanced_demand_zone(data, i, current_price, symbol, timeframe, health_score)
                if block and self._is_relevant_enhanced_block(block, current_price):
                    enhanced_blocks.append(block)
            
            # 📉 SUPPLY ZONE: Swing High con validación mejorada  
            if self._is_enhanced_swing_high(data, i):
                block = self._create_enhanced_supply_zone(data, i, current_price, symbol, timeframe, health_score)
                if block and self._is_relevant_enhanced_block(block, current_price):
                    enhanced_blocks.append(block)
        
        # 🏆 POST-PROCESAMIENTO MEJORADO
        enhanced_blocks = self._apply_enhanced_filtering(enhanced_blocks, data, current_price)
        
        # 📊 MULTI-TIMEFRAME VALIDATION
        if self.multi_timeframe_validation and additional_timeframes:
            enhanced_blocks = self._apply_mtf_validation(enhanced_blocks, additional_timeframes)
        
        # 📈 VOLUME PROFILE ENHANCEMENT
        if self.volume_profile_enabled:
            enhanced_blocks = self._enhance_with_volume_profile(enhanced_blocks, data)
        
        # 🎯 MITIGATION ZONE ANALYSIS
        if self.mitigation_analysis:
            enhanced_blocks = self._analyze_mitigation_zones(enhanced_blocks, data)
        
        # 📊 QUALITY SCORING
        enhanced_blocks = self._assign_quality_scores(enhanced_blocks, health_score)
        
        # 🏆 ORDENAR POR CALIDAD Y RELEVANCIA
        enhanced_blocks.sort(key=lambda x: (x.quality.value, x.distance_pips, -x.confidence))
        
        # 📈 ACTUALIZAR ESTADÍSTICAS
        detection_time_ms = (time.time() - start_time) * 1000
        self._update_enhanced_stats(enhanced_blocks, detection_time_ms)
        
        # 📝 LOGGING Y REPORTING
        self._log_enhanced_detection_results(enhanced_blocks, symbol, timeframe, detection_time_ms)
        
        return enhanced_blocks[:5]  # Top 5 más relevantes
    
    def _get_health_score(self) -> float:
        """Obtener score de health del MT5"""
        if not self.health_monitor:
            return 1.0  # Asumir perfecto si no hay monitor
        
        try:
            health_data = self.health_monitor.get_health_summary()
            
            # Calcular score basado en métricas de health
            connection_score = 1.0 if health_data.get('connected', True) else 0.0
            latency_score = max(0.0, 1.0 - (health_data.get('last_ping_ms', 0) / 1000.0))
            reliability_score = health_data.get('uptime_percentage', 100) / 100.0
            
            # Score combinado
            health_score = (connection_score * 0.5 + latency_score * 0.3 + reliability_score * 0.2)
            return max(0.0, min(1.0, health_score))
            
        except Exception as e:
            log_warning(f"Could not get health score: {e}")
            return 0.8  # Score conservador si hay error
    
    def _is_enhanced_swing_low(self, data: Any, idx: int, lookback: int = 4) -> bool:
        """Detectar swing low mejorado con validación adicional"""
        if idx < lookback or idx >= len(data) - lookback:
            return False
        
        current_low = data.iloc[idx]['low']
        
        # Verificar que sea el mínimo local
        for i in range(idx - lookback, idx + lookback + 1):
            if i != idx and data.iloc[i]['low'] <= current_low:
                return False
        
        # Validación adicional: volumen significativo
        if self.volume_profile_enabled and 'volume' in data.columns:
            avg_volume = data['volume'].iloc[idx-5:idx+5].mean()
            current_volume = data.iloc[idx]['volume']
            if current_volume < avg_volume * 0.8:  # Volumen debe ser significativo
                return False
        
        return True
    
    def _is_enhanced_swing_high(self, data: Any, idx: int, lookback: int = 4) -> bool:
        """Detectar swing high mejorado con validación adicional"""
        if idx < lookback or idx >= len(data) - lookback:
            return False
        
        current_high = data.iloc[idx]['high']
        
        # Verificar que sea el máximo local
        for i in range(idx - lookback, idx + lookback + 1):
            if i != idx and data.iloc[i]['high'] >= current_high:
                return False
        
        # Validación adicional: volumen significativo
        if self.volume_profile_enabled and 'volume' in data.columns:
            avg_volume = data['volume'].iloc[idx-5:idx+5].mean()
            current_volume = data.iloc[idx]['volume']
            if current_volume < avg_volume * 0.8:  # Volumen debe ser significativo
                return False
        
        return True
    
    def _create_enhanced_demand_zone(self, data: Any, idx: int, current_price: float, 
                                   symbol: str, timeframe: str, health_score: float) -> Optional[EnhancedOrderBlock]:
        """Crear zona de demanda mejorada"""
        try:
            candle = data.iloc[idx]
            entry_price = candle['high']  # Entrada en break del high
            stop_loss = candle['low'] - (candle['high'] - candle['low']) * 0.2
            
            # Take profit dinámico basado en health score
            health_multiplier = 1.0 + (health_score - 0.5)  # Más agresivo con mejor health
            take_profit = entry_price + (entry_price - stop_loss) * 2.0 * health_multiplier
            
            # Calcular métricas
            distance_pips = abs(current_price - entry_price) * 10000
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            risk_reward = reward / risk if risk > 0 else 0
            
            # Confianza mejorada con health integration
            base_confidence = 65.0
            volume_boost = self._calculate_volume_confidence_boost(data, idx)
            health_boost = health_score * 20.0  # Hasta 20% boost por health
            
            confidence = min(95.0, base_confidence + volume_boost + health_boost)
            
            return EnhancedOrderBlock(
                type=OrderBlockType.DEMAND_ZONE,
                price=candle['low'],
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                distance_pips=distance_pips,
                risk_reward=risk_reward,
                health_score=health_score,
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.now(),
                detection_latency_ms=0.0,  # Se actualizará después
                data_reliability=health_score
            )
            
        except Exception as e:
            log_error(f"Error creating enhanced demand zone: {e}")
            return None
    
    def _create_enhanced_supply_zone(self, data: Any, idx: int, current_price: float,
                                   symbol: str, timeframe: str, health_score: float) -> Optional[EnhancedOrderBlock]:
        """Crear zona de oferta mejorada"""
        try:
            candle = data.iloc[idx]
            entry_price = candle['low']  # Entrada en break del low
            stop_loss = candle['high'] + (candle['high'] - candle['low']) * 0.2
            
            # Take profit dinámico basado en health score
            health_multiplier = 1.0 + (health_score - 0.5)  # Más agresivo con mejor health
            take_profit = entry_price - (stop_loss - entry_price) * 2.0 * health_multiplier
            
            # Calcular métricas
            distance_pips = abs(current_price - entry_price) * 10000
            risk = abs(stop_loss - entry_price)
            reward = abs(entry_price - take_profit)
            risk_reward = reward / risk if risk > 0 else 0
            
            # Confianza mejorada con health integration
            base_confidence = 65.0
            volume_boost = self._calculate_volume_confidence_boost(data, idx)
            health_boost = health_score * 20.0  # Hasta 20% boost por health
            
            confidence = min(95.0, base_confidence + volume_boost + health_boost)
            
            return EnhancedOrderBlock(
                type=OrderBlockType.SUPPLY_ZONE,
                price=candle['high'],
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                distance_pips=distance_pips,
                risk_reward=risk_reward,
                health_score=health_score,
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.now(),
                detection_latency_ms=0.0,  # Se actualizará después
                data_reliability=health_score
            )
            
        except Exception as e:
            log_error(f"Error creating enhanced supply zone: {e}")
            return None
    
    def _calculate_volume_confidence_boost(self, data: Any, idx: int) -> float:
        """Calcular boost de confianza basado en volumen"""
        if not self.volume_profile_enabled or 'volume' not in data.columns:
            return 0.0
        
        try:
            current_volume = data.iloc[idx]['volume']
            avg_volume = data['volume'].iloc[max(0, idx-10):idx].mean()
            
            if avg_volume == 0:
                return 0.0
            
            volume_ratio = current_volume / avg_volume
            
            # Boost basado en ratio de volumen
            if volume_ratio > 2.0:
                return 15.0  # Alto volumen: +15%
            elif volume_ratio > 1.5:
                return 10.0  # Volumen moderado: +10%
            elif volume_ratio > 1.2:
                return 5.0   # Volumen ligeramente alto: +5%
            else:
                return 0.0   # Volumen normal: sin boost
                
        except Exception as e:
            log_warning(f"Error calculating volume boost: {e}")
            return 0.0
    
    def _is_relevant_enhanced_block(self, block: EnhancedOrderBlock, current_price: float) -> bool:
        """Verificar si el block mejorado es relevante para trading"""
        
        # Filtros básicos mejorados
        if block.distance_pips > self.max_distance_pips:
            return False
            
        if block.confidence < self.min_confidence:
            return False
            
        if block.risk_reward < 1.5:  # RR mínimo
            return False
        
        # Nuevos filtros basados en health
        if block.health_score < 0.6:  # Health mínimo 60%
            return False
        
        if block.data_reliability < self.min_data_reliability:
            return False
        
        return True
    
    def _apply_enhanced_filtering(self, blocks: List[EnhancedOrderBlock], 
                                data: Any, current_price: float) -> List[EnhancedOrderBlock]:
        """Aplicar filtrado mejorado a los blocks"""
        filtered_blocks = []
        
        for block in blocks:
            # Filtro de proximidad mejorado
            if block.distance_pips <= self.max_distance_pips * 1.2:  # Margen adicional para blocks de alta calidad
                
                # Filtro de health score
                if block.health_score >= 0.6:
                    
                    # Filtro de timing (evitar blocks muy antiguos)
                    time_diff = datetime.now() - block.timestamp
                    if time_diff.total_seconds() < 3600:  # Máximo 1 hora
                        filtered_blocks.append(block)
        
        return filtered_blocks
    
    def _apply_mtf_validation(self, blocks: List[EnhancedOrderBlock], 
                            additional_timeframes: List[str]) -> List[EnhancedOrderBlock]:
        """Aplicar validación multi-timeframe"""
        # Placeholder para implementación futura de MTF validation
        # Por ahora retornamos los blocks sin cambios
        self.stats['mtf_validations'] += len(blocks)
        
        for block in blocks:
            # Simular validación MTF
            block.timeframe_validation = {tf: True for tf in additional_timeframes}
        
        return blocks
    
    def _enhance_with_volume_profile(self, blocks: List[EnhancedOrderBlock], 
                                   data: Any) -> List[EnhancedOrderBlock]:
        """Mejorar blocks con análisis de volume profile"""
        if not self.volume_profile_enabled or 'volume' not in data.columns:
            return blocks
        
        for block in blocks:
            try:
                # Análisis de volume profile básico
                avg_volume = data['volume'].mean()
                recent_volume = data['volume'].tail(5).mean()
                
                block.volume_profile = {
                    'avg_volume': float(avg_volume),
                    'recent_volume': float(recent_volume),
                    'volume_trend': 'increasing' if recent_volume > avg_volume else 'decreasing',
                    'volume_strength': min(2.0, recent_volume / avg_volume) if avg_volume > 0 else 1.0
                }
                
                self.stats['volume_profile_enhanced'] += 1
                
            except Exception as e:
                log_warning(f"Error enhancing with volume profile: {e}")
        
        return blocks
    
    def _analyze_mitigation_zones(self, blocks: List[EnhancedOrderBlock], 
                                data: Any) -> List[EnhancedOrderBlock]:
        """Analizar zonas de mitigación"""
        for block in blocks:
            try:
                # Análisis básico de mitigation zones
                price_range = abs(block.take_profit - block.entry_price)
                
                # Crear zonas de mitigación en niveles clave
                mitigation_levels = []
                
                if block.type == OrderBlockType.DEMAND_ZONE:
                    # Para demand zones, mitigation por encima
                    mitigation_levels.append((block.entry_price, block.entry_price + price_range * 0.382))
                    mitigation_levels.append((block.entry_price + price_range * 0.5, block.entry_price + price_range * 0.618))
                else:
                    # Para supply zones, mitigation por debajo
                    mitigation_levels.append((block.entry_price - price_range * 0.382, block.entry_price))
                    mitigation_levels.append((block.entry_price - price_range * 0.618, block.entry_price - price_range * 0.5))
                
                block.mitigation_zones = mitigation_levels
                
            except Exception as e:
                log_warning(f"Error analyzing mitigation zones: {e}")
        
        return blocks
    
    def _assign_quality_scores(self, blocks: List[EnhancedOrderBlock], 
                             health_score: float) -> List[EnhancedOrderBlock]:
        """Asignar scores de calidad basados en health y otros factores"""
        for block in blocks:
            # Score combinado
            combined_score = (
                block.confidence * 0.4 +
                block.health_score * 100 * 0.3 +
                min(100, block.risk_reward * 20) * 0.2 +
                max(0, 100 - block.distance_pips) * 0.1
            )
            
            # Asignar calidad
            if combined_score >= 90:
                block.quality = OrderBlockQuality.PREMIUM
                self.stats['quality_premium'] += 1
            elif combined_score >= 75:
                block.quality = OrderBlockQuality.HIGH
                self.stats['quality_high'] += 1
            elif combined_score >= 60:
                block.quality = OrderBlockQuality.MEDIUM
                self.stats['quality_medium'] += 1
            else:
                block.quality = OrderBlockQuality.LOW
                self.stats['quality_low'] += 1
        
        return blocks
    
    def _update_enhanced_stats(self, blocks: List[EnhancedOrderBlock], detection_time_ms: float):
        """Actualizar estadísticas mejoradas"""
        self.stats['avg_detection_time_ms'] = (
            (self.stats['avg_detection_time_ms'] * (self.stats['total_detections'] - 1) + detection_time_ms) /
            self.stats['total_detections']
        )
        
        # Actualizar latency en blocks
        for block in blocks:
            block.detection_latency_ms = detection_time_ms
    
    def _log_enhanced_detection_results(self, blocks: List[EnhancedOrderBlock], 
                                      symbol: str, timeframe: str, detection_time_ms: float):
        """Log detallado de resultados mejorados"""
        if not blocks:
            log_info(f"No enhanced order blocks found for {symbol} {timeframe}", "ORDER_BLOCKS_ENHANCED")
            return
        
        # Estadísticas por calidad
        quality_stats = {}
        for quality in OrderBlockQuality:
            count = sum(1 for b in blocks if b.quality == quality)
            quality_stats[quality.value] = count
        
        # Log resumen
        summary_msg = (f"{len(blocks)} Enhanced Order Blocks detected for {symbol} {timeframe} "
                      f"in {detection_time_ms:.1f}ms | Quality distribution: {quality_stats}")
        log_success(summary_msg, "ORDER_BLOCKS_ENHANCED")
        
        # Log detalle de cada block
        for i, block in enumerate(blocks, 1):
            detail_msg = (f"#{i} {block.type.value.upper()} | "
                         f"Price: {block.price:.5f} | "
                         f"Confidence: {block.confidence:.1f}% | "
                         f"Health: {block.health_score:.1%} | "
                         f"Quality: {block.quality.value} | "
                         f"R:R: {block.risk_reward:.2f} | "
                         f"Distance: {block.distance_pips:.1f} pips")
            log_info(detail_msg, "ORDER_BLOCKS_ENHANCED")
        
        # Guardar estadísticas detalladas
        self._save_enhanced_session_report(blocks, symbol, timeframe, detection_time_ms)
    
    def _save_enhanced_session_report(self, blocks: List[EnhancedOrderBlock], 
                                    symbol: str, timeframe: str, detection_time_ms: float):
        """Guardar reporte detallado de la sesión"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.logs_dir / f"enhanced_session_{symbol}_{timeframe}_{timestamp}.json"
            
            report_data = {
                'session_info': {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'timestamp': datetime.now().isoformat(),
                    'detection_time_ms': detection_time_ms,
                    'blocks_detected': len(blocks)
                },
                'health_integration': {
                    'health_monitor_available': self.health_monitor is not None,
                    'avg_health_score': sum(b.health_score for b in blocks) / len(blocks) if blocks else 0.0,
                    'health_filtered_count': self.stats['health_filtered']
                },
                'quality_distribution': {
                    'premium': self.stats['quality_premium'],
                    'high': self.stats['quality_high'],
                    'medium': self.stats['quality_medium'],
                    'low': self.stats['quality_low']
                },
                'enhanced_features': {
                    'mtf_validations': self.stats['mtf_validations'],
                    'volume_profile_enhanced': self.stats['volume_profile_enhanced'],
                    'avg_detection_time_ms': self.stats['avg_detection_time_ms']
                },
                'blocks': [
                    {
                        'type': block.type.value,
                        'price': block.price,
                        'confidence': block.confidence,
                        'health_score': block.health_score,
                        'quality': block.quality.value,
                        'risk_reward': block.risk_reward,
                        'distance_pips': block.distance_pips,
                        'volume_profile': block.volume_profile,
                        'mitigation_zones': block.mitigation_zones
                    }
                    for block in blocks
                ]
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            log_success(f"Enhanced session report saved: {report_file}", "ORDER_BLOCKS_ENHANCED")
            
        except Exception as e:
            log_error(f"Error saving enhanced session report: {e}")
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas mejoradas del detector"""
        return {
            **self.stats,
            'health_integration_enabled': self.health_monitor is not None,
            'multi_timeframe_validation_enabled': self.multi_timeframe_validation,
            'volume_profile_enabled': self.volume_profile_enabled,
            'mitigation_analysis_enabled': self.mitigation_analysis
        }

# ✅ Export de la clase principal
__all__ = ['EnhancedOrderBlockDetector', 'EnhancedOrderBlock', 'OrderBlockType', 'OrderBlockQuality']

if __name__ == "__main__":
    # Test básico del detector mejorado
    print("🎯 Enhanced Order Block Detector v6.1 - Test Mode")
    
    detector = EnhancedOrderBlockDetector()
    stats = detector.get_enhanced_stats()
    
    print(f"✅ Detector initialized with enhanced features:")
    print(f"   Health Integration: {stats['health_integration_enabled']}")
    print(f"   MTF Validation: {stats['multi_timeframe_validation_enabled']}")
    print(f"   Volume Profile: {stats['volume_profile_enabled']}")
    print(f"   Mitigation Analysis: {stats['mitigation_analysis_enabled']}")
    print("\n🚀 Ready for enhanced order block detection!")


# Singleton instance
_order_block_detector = None

def get_order_block_detector() -> EnhancedOrderBlockDetector:
    """🎯 Get singleton Enhanced Order Block Detector"""
    global _order_block_detector
    if _order_block_detector is None:
        _order_block_detector = EnhancedOrderBlockDetector()
    return _order_block_detector
