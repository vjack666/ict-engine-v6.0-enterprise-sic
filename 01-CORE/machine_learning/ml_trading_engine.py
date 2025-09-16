#!/usr/bin/env python3
"""
Production ML Trading Engine - ICT Engine v6.0 Enterprise
=========================================================

Sistema de Machine Learning optimizado para trading en producción.
Enfoque en análisis de patrones ICT, predicción de tendencias y optimización de entradas.

Características:
✅ Modelos ligeros para inferencia en tiempo real
✅ Feature engineering específico para ICT patterns
✅ Ensemble de modelos para mayor robustez
✅ Cache inteligente para optimización de rendimiento
✅ Métricas de confianza adaptativas

Autor: ICT Engine v6.0 Team
"""
from __future__ import annotations

import json
import pickle
import numpy as np
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from collections import deque, defaultdict

try:
    from protocols.logging_central_protocols import create_production_logger, LogLevel
    logger = create_production_logger("MLTradingEngine", LogLevel.INFO)
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("MLTradingEngine")

# Feature Engineering
class FeatureType(Enum):
    """Tipos de features para ML"""
    PRICE_ACTION = "price_action"
    VOLATILITY = "volatility" 
    VOLUME = "volume"
    ICT_PATTERNS = "ict_patterns"
    MARKET_STRUCTURE = "market_structure"
    TEMPORAL = "temporal"

@dataclass
class MLFeatures:
    """Features para machine learning"""
    symbol: str
    timestamp: datetime
    timeframe: str
    
    # Price action features
    price_momentum: float = 0.0
    price_trend_strength: float = 0.0
    support_resistance_distance: float = 0.0
    
    # ICT specific features
    order_block_presence: float = 0.0
    fair_value_gap_score: float = 0.0
    liquidity_grab_signal: float = 0.0
    market_structure_break: float = 0.0
    
    # Volatility features
    atr_normalized: float = 0.0
    volatility_regime: float = 0.0
    
    # Volume features (if available)
    volume_profile_score: float = 0.0
    
    # Temporal features
    session_type: float = 0.0  # 0=asia, 0.5=london, 1.0=ny
    time_of_day_normalized: float = 0.0
    
    # Market context
    trend_alignment_multi_tf: float = 0.0
    correlation_strength: float = 0.0
    
    def to_array(self) -> np.ndarray:
        """Convertir features a array numpy para ML"""
        return np.array([
            self.price_momentum,
            self.price_trend_strength,
            self.support_resistance_distance,
            self.order_block_presence,
            self.fair_value_gap_score,
            self.liquidity_grab_signal,
            self.market_structure_break,
            self.atr_normalized,
            self.volatility_regime,
            self.volume_profile_score,
            self.session_type,
            self.time_of_day_normalized,
            self.trend_alignment_multi_tf,
            self.correlation_strength
        ], dtype=np.float32)
    
    @classmethod
    def feature_names(cls) -> List[str]:
        """Obtener nombres de las features"""
        return [
            'price_momentum', 'price_trend_strength', 'support_resistance_distance',
            'order_block_presence', 'fair_value_gap_score', 'liquidity_grab_signal',
            'market_structure_break', 'atr_normalized', 'volatility_regime',
            'volume_profile_score', 'session_type', 'time_of_day_normalized',
            'trend_alignment_multi_tf', 'correlation_strength'
        ]

@dataclass
class MLPrediction:
    """Predicción de machine learning"""
    symbol: str
    timestamp: datetime
    direction: str  # 'buy', 'sell', 'neutral'
    confidence: float
    expected_movement_pips: float
    time_horizon_minutes: int
    model_ensemble_agreement: float
    
    # Risk assessment
    risk_score: float = 0.5
    volatility_adjusted_confidence: float = 0.0
    
    # Model attribution
    model_contributions: Dict[str, float] = field(default_factory=dict)
    
    def is_high_confidence(self, threshold: float = 0.75) -> bool:
        """Verificar si es predicción de alta confianza"""
        return (self.confidence >= threshold and 
                self.model_ensemble_agreement >= 0.7 and
                self.volatility_adjusted_confidence >= threshold * 0.8)

class SimpleMLModel:
    """Modelo ML simple basado en reglas ponderadas para producción"""
    
    def __init__(self, name: str, weights: Optional[Dict[str, float]] = None):
        self.name = name
        self.weights = weights or self._default_weights()
        self.last_update = datetime.now()
        self.prediction_count = 0
        
    def _default_weights(self) -> Dict[str, float]:
        """Pesos por defecto basados en importancia ICT"""
        return {
            'order_block_presence': 0.25,
            'fair_value_gap_score': 0.20,
            'liquidity_grab_signal': 0.15,
            'market_structure_break': 0.15,
            'price_momentum': 0.10,
            'trend_alignment_multi_tf': 0.10,
            'volatility_regime': 0.05
        }
    
    def predict(self, features: MLFeatures) -> Tuple[float, float]:
        """
        Realizar predicción
        
        Returns:
            Tuple[direction_score, confidence]: 
            - direction_score: -1 to 1 (-1=strong sell, 1=strong buy)
            - confidence: 0 to 1
        """
        feature_array = features.to_array()
        feature_names = MLFeatures.feature_names()
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for i, feature_name in enumerate(feature_names):
            if feature_name in self.weights:
                weight = self.weights[feature_name]
                feature_value = feature_array[i]
                
                # Normalize feature value to [-1, 1] range
                normalized_value = np.tanh(feature_value)
                
                weighted_score += weight * normalized_value
                total_weight += weight
        
        # Normalize by total weight
        if total_weight > 0:
            direction_score = weighted_score / total_weight
        else:
            direction_score = 0.0
        
        # Calculate confidence based on signal strength and consistency
        signal_strength = abs(direction_score)
        volatility_factor = 1.0 - min(features.volatility_regime, 1.0)
        confidence = signal_strength * volatility_factor
        
        self.prediction_count += 1
        return direction_score, min(confidence, 1.0)

class VolatilityRegimeModel:
    """Modelo especializado en detectar regímenes de volatilidad"""
    
    def __init__(self):
        self.name = "volatility_regime"
        self.lookback_periods = 20
        self.volatility_history = deque(maxlen=self.lookback_periods)
        
    def update_volatility(self, atr_value: float):
        """Actualizar historial de volatilidad"""
        if atr_value > 0:
            self.volatility_history.append(atr_value)
    
    def get_regime_score(self) -> float:
        """
        Obtener score de régimen de volatilidad
        
        Returns:
            float: 0-1 donde 0=baja volatilidad, 1=alta volatilidad
        """
        if len(self.volatility_history) < 5:
            return 0.5  # Default neutral
        
        recent_vol = list(self.volatility_history)
        current_vol = recent_vol[-1]
        avg_vol = np.mean(recent_vol)
        std_vol = np.std(recent_vol)
        
        if std_vol == 0:
            return 0.5
        
        # Z-score normalizado
        z_score = (current_vol - avg_vol) / std_vol
        
        # Convertir a escala 0-1
        regime_score = 0.5 + (z_score / 6.0)  # Assuming 3-sigma range
        return max(0.0, min(1.0, regime_score))

class MLTradingEngine:
    """
    Motor de Machine Learning para trading en producción
    
    Características:
    - Ensemble de modelos ligeros
    - Feature engineering en tiempo real
    - Cache inteligente para performance
    - Métricas de tracking automáticas
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # Models
        self.models: Dict[str, SimpleMLModel] = {}
        self.volatility_model = VolatilityRegimeModel()
        self._initialize_models()
        
        # Feature cache
        self._feature_cache: Dict[str, Tuple[MLFeatures, datetime]] = {}
        self._cache_ttl_seconds = self.config.get('feature_cache_ttl', 30)
        
        # Performance tracking
        self.prediction_history: deque = deque(maxlen=1000)
        self.performance_metrics = {
            'total_predictions': 0,
            'high_confidence_predictions': 0,
            'cache_hit_rate': 0.0,
            'avg_prediction_time_ms': 0.0
        }
        
        # Threading
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="MLEngine")
        self._lock = threading.RLock()
        
        logger.info("MLTradingEngine initialized", "INIT")
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'feature_cache_ttl': 30,
            'min_confidence_threshold': 0.6,
            'ensemble_agreement_threshold': 0.7,
            'volatility_adjustment_factor': 0.8,
            'prediction_timeout_seconds': 2.0,
            'enable_feature_cache': True,
            'max_prediction_history': 1000
        }
    
    def _initialize_models(self) -> None:
        """Inicializar modelos del ensemble"""
        # Modelo conservador (favorece señales fuertes)
        conservative_weights = {
            'order_block_presence': 0.30,
            'fair_value_gap_score': 0.25,
            'market_structure_break': 0.20,
            'trend_alignment_multi_tf': 0.15,
            'liquidity_grab_signal': 0.10
        }
        
        # Modelo agresivo (incluye más señales)
        aggressive_weights = {
            'liquidity_grab_signal': 0.25,
            'price_momentum': 0.20,
            'order_block_presence': 0.20,
            'fair_value_gap_score': 0.15,
            'market_structure_break': 0.15,
            'volatility_regime': 0.05
        }
        
        # Modelo balanced
        balanced_weights = {
            'order_block_presence': 0.22,
            'fair_value_gap_score': 0.18,
            'liquidity_grab_signal': 0.18,
            'market_structure_break': 0.18,
            'trend_alignment_multi_tf': 0.12,
            'price_momentum': 0.08,
            'volatility_regime': 0.04
        }
        
        self.models['conservative'] = SimpleMLModel('conservative', conservative_weights)
        self.models['aggressive'] = SimpleMLModel('aggressive', aggressive_weights)
        self.models['balanced'] = SimpleMLModel('balanced', balanced_weights)
        
        logger.info(f"Initialized {len(self.models)} ML models", "MODELS")
    
    def extract_features(self, market_data: Dict[str, Any]) -> MLFeatures:
        """
        Extraer features de datos de mercado
        
        Args:
            market_data: Datos de mercado con OHLCV, indicadores, etc.
            
        Returns:
            MLFeatures: Features extraídas
        """
        symbol = market_data.get('symbol', 'UNKNOWN')
        timestamp = market_data.get('timestamp', datetime.now())
        timeframe = market_data.get('timeframe', 'M5')
        
        features = MLFeatures(symbol=symbol, timestamp=timestamp, timeframe=timeframe)
        
        # Cache check
        cache_key = f"{symbol}_{timeframe}_{timestamp.isoformat()}"
        if self.config['enable_feature_cache']:
            if cache_key in self._feature_cache:
                cached_features, cached_time = self._feature_cache[cache_key]
                if (datetime.now() - cached_time).total_seconds() < self._cache_ttl_seconds:
                    return cached_features
        
        try:
            # Price action features
            close_prices = market_data.get('close_prices', [])
            if len(close_prices) >= 2:
                price_change = (close_prices[-1] - close_prices[-2]) / close_prices[-2]
                features.price_momentum = float(price_change * 100)  # En porcentaje
            
            # Trend strength
            if len(close_prices) >= 10:
                trend_slope = self._calculate_trend_slope(close_prices[-10:])
                features.price_trend_strength = float(trend_slope)
            
            # ICT patterns (simplificados para demo)
            ict_signals = market_data.get('ict_signals', {})
            features.order_block_presence = float(ict_signals.get('order_block_strength', 0.0))
            features.fair_value_gap_score = float(ict_signals.get('fvg_score', 0.0))
            features.liquidity_grab_signal = float(ict_signals.get('liquidity_grab', 0.0))
            features.market_structure_break = float(ict_signals.get('msb_signal', 0.0))
            
            # Volatility
            atr = market_data.get('atr', 0.0)
            if atr > 0:
                avg_price = (market_data.get('high', 0) + market_data.get('low', 0)) / 2
                if avg_price > 0:
                    features.atr_normalized = float(atr / avg_price)
                
                # Update volatility model
                self.volatility_model.update_volatility(atr)
                features.volatility_regime = self.volatility_model.get_regime_score()
            
            # Temporal features
            features.session_type = self._get_session_score(timestamp)
            features.time_of_day_normalized = self._get_time_of_day_score(timestamp)
            
            # Multi-timeframe alignment (simplificado)
            features.trend_alignment_multi_tf = float(market_data.get('trend_alignment', 0.5))
            
            # Cache result
            if self.config['enable_feature_cache']:
                self._feature_cache[cache_key] = (features, datetime.now())
                
                # Cleanup old cache entries
                if len(self._feature_cache) > 100:
                    oldest_key = min(self._feature_cache.keys(), 
                                   key=lambda k: self._feature_cache[k][1])
                    del self._feature_cache[oldest_key]
            
        except Exception as e:
            logger.warning(f"Error extracting features: {e}", "FEATURES")
        
        return features
    
    def predict(self, market_data: Dict[str, Any]) -> Optional[MLPrediction]:
        """
        Generar predicción usando ensemble de modelos
        
        Args:
            market_data: Datos de mercado para predicción
            
        Returns:
            MLPrediction o None si no se puede predecir
        """
        start_time = time.time()
        
        try:
            with self._lock:
                # Extract features
                features = self.extract_features(market_data)
                
                # Get predictions from all models
                model_predictions: Dict[str, Tuple[float, float]] = {}
                
                for model_name, model in self.models.items():
                    try:
                        direction_score, confidence = model.predict(features)
                        model_predictions[model_name] = (direction_score, confidence)
                    except Exception as e:
                        logger.warning(f"Model {model_name} prediction failed: {e}", "PREDICT")
                        continue
                
                if not model_predictions:
                    logger.warning("No model predictions available", "PREDICT")
                    return None
                
                # Ensemble aggregation
                ensemble_result = self._aggregate_predictions(model_predictions, features)
                
                # Performance tracking
                prediction_time_ms = (time.time() - start_time) * 1000
                self._update_performance_metrics(prediction_time_ms)
                
                return ensemble_result
                
        except Exception as e:
            logger.error(f"Prediction error: {e}", "PREDICT")
            return None
    
    def _aggregate_predictions(self, 
                             model_predictions: Dict[str, Tuple[float, float]], 
                             features: MLFeatures) -> MLPrediction:
        """Agregar predicciones del ensemble"""
        
        # Weighted average of predictions
        total_weight = 0.0
        weighted_direction = 0.0
        weighted_confidence = 0.0
        
        # Model weights based on performance (simplified)
        model_weights = {
            'conservative': 0.4,
            'balanced': 0.35, 
            'aggressive': 0.25
        }
        
        model_contributions = {}
        
        for model_name, (direction_score, confidence) in model_predictions.items():
            weight = model_weights.get(model_name, 1.0)
            
            weighted_direction += direction_score * confidence * weight
            weighted_confidence += confidence * weight
            total_weight += weight
            
            model_contributions[model_name] = direction_score * confidence
        
        if total_weight > 0:
            avg_direction = weighted_direction / total_weight
            avg_confidence = weighted_confidence / total_weight
        else:
            avg_direction = 0.0
            avg_confidence = 0.0
        
        # Determine final direction
        if avg_direction > 0.1:
            direction = 'buy'
        elif avg_direction < -0.1:
            direction = 'sell'
        else:
            direction = 'neutral'
        
        # Calculate ensemble agreement
        direction_scores = [pred[0] for pred in model_predictions.values()]
        agreement = self._calculate_agreement(direction_scores)
        
        # Volatility adjustment
        volatility_factor = max(0.3, 1.0 - features.volatility_regime)
        volatility_adjusted_confidence = avg_confidence * volatility_factor
        
        # Expected movement (simplified)
        expected_movement_pips = abs(avg_direction) * 20 * (1 + features.volatility_regime)
        
        # Time horizon based on timeframe and volatility
        time_horizon = self._calculate_time_horizon(features.timeframe, features.volatility_regime)
        
        prediction = MLPrediction(
            symbol=features.symbol,
            timestamp=features.timestamp,
            direction=direction,
            confidence=avg_confidence,
            expected_movement_pips=expected_movement_pips,
            time_horizon_minutes=time_horizon,
            model_ensemble_agreement=agreement,
            risk_score=1.0 - avg_confidence,
            volatility_adjusted_confidence=volatility_adjusted_confidence,
            model_contributions=model_contributions
        )
        
        # Store in history
        self.prediction_history.append({
            'timestamp': datetime.now(),
            'symbol': features.symbol,
            'direction': direction,
            'confidence': avg_confidence,
            'volatility_adjusted_confidence': volatility_adjusted_confidence
        })
        
        return prediction
    
    def _calculate_trend_slope(self, prices: List[float]) -> float:
        """Calcular pendiente de tendencia"""
        if len(prices) < 2:
            return 0.0
        
        x = np.arange(len(prices))
        y = np.array(prices)
        
        # Linear regression slope
        slope, _ = np.polyfit(x, y, 1)
        
        # Normalize by average price
        avg_price = np.mean(y)
        if avg_price > 0:
            normalized_slope = slope / avg_price
        else:
            normalized_slope = 0.0
        
        return float(normalized_slope * 1000)  # Scale for visibility
    
    def _get_session_score(self, timestamp: datetime) -> float:
        """Obtener score de sesión de trading"""
        hour_utc = timestamp.hour
        
        # Asia: 22-6 UTC (0.0)
        # London: 7-15 UTC (0.5) 
        # NY: 13-21 UTC (1.0)
        
        if 22 <= hour_utc or hour_utc <= 6:
            return 0.0  # Asia
        elif 7 <= hour_utc <= 12:
            return 0.5  # London
        elif 13 <= hour_utc <= 15:
            return 0.75  # London-NY overlap
        elif 16 <= hour_utc <= 21:
            return 1.0  # NY
        else:
            return 0.25  # Transition
    
    def _get_time_of_day_score(self, timestamp: datetime) -> float:
        """Normalizar hora del día a 0-1"""
        hour = timestamp.hour
        minute = timestamp.minute
        
        total_minutes = hour * 60 + minute
        return total_minutes / (24 * 60)
    
    def _calculate_agreement(self, direction_scores: List[float]) -> float:
        """Calcular acuerdo entre modelos"""
        if len(direction_scores) < 2:
            return 1.0
        
        # Check if all models agree on direction
        positive_count = sum(1 for score in direction_scores if score > 0.1)
        negative_count = sum(1 for score in direction_scores if score < -0.1)
        total_count = len(direction_scores)
        
        if positive_count == total_count or negative_count == total_count:
            return 1.0  # Perfect agreement
        elif positive_count > total_count * 0.7 or negative_count > total_count * 0.7:
            return 0.8  # Strong agreement
        elif positive_count > total_count * 0.5 or negative_count > total_count * 0.5:
            return 0.6  # Moderate agreement
        else:
            return 0.3  # Low agreement
    
    def _calculate_time_horizon(self, timeframe: str, volatility_regime: float) -> int:
        """Calcular horizonte temporal para la predicción"""
        base_horizon = {
            'M1': 5,
            'M5': 15,
            'M15': 45,
            'M30': 90,
            'H1': 180,
            'H4': 720
        }.get(timeframe, 30)
        
        # Adjust based on volatility
        volatility_multiplier = 0.5 + volatility_regime
        
        return int(base_horizon * volatility_multiplier)
    
    def _update_performance_metrics(self, prediction_time_ms: float) -> None:
        """Actualizar métricas de rendimiento"""
        self.performance_metrics['total_predictions'] += 1
        
        # Update average prediction time
        current_avg = self.performance_metrics['avg_prediction_time_ms']
        total_predictions = self.performance_metrics['total_predictions']
        
        new_avg = ((current_avg * (total_predictions - 1)) + prediction_time_ms) / total_predictions
        self.performance_metrics['avg_prediction_time_ms'] = new_avg
        
        # Update cache hit rate (simplified)
        if hasattr(self, '_cache_hits'):
            self._cache_hits += 1
        else:
            self._cache_hits = 0
        
        self.performance_metrics['cache_hit_rate'] = self._cache_hits / total_predictions
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de rendimiento"""
        with self._lock:
            recent_predictions = list(self.prediction_history)[-100:]  # Last 100
            
            high_confidence_count = sum(1 for pred in recent_predictions 
                                      if pred.get('volatility_adjusted_confidence', 0) > 0.7)
            
            metrics = self.performance_metrics.copy()
            metrics.update({
                'high_confidence_predictions': high_confidence_count,
                'recent_predictions_count': len(recent_predictions),
                'model_count': len(self.models),
                'feature_cache_size': len(self._feature_cache),
                'last_prediction_time': recent_predictions[-1]['timestamp'].isoformat() if recent_predictions else None
            })
            
            return metrics
    
    def reset_performance_metrics(self) -> None:
        """Resetear métricas de rendimiento"""
        self.performance_metrics = {
            'total_predictions': 0,
            'high_confidence_predictions': 0,
            'cache_hit_rate': 0.0,
            'avg_prediction_time_ms': 0.0
        }
        self.prediction_history.clear()
        logger.info("Performance metrics reset", "METRICS")

# Global instance management
_global_ml_engine: Optional[MLTradingEngine] = None

def get_ml_trading_engine() -> MLTradingEngine:
    """Obtener instancia global del motor ML"""
    global _global_ml_engine
    if _global_ml_engine is None:
        _global_ml_engine = MLTradingEngine()
    return _global_ml_engine

def set_ml_trading_engine(engine: MLTradingEngine) -> None:
    """Establecer instancia global del motor ML"""
    global _global_ml_engine
    _global_ml_engine = engine

__all__ = [
    'MLTradingEngine',
    'MLFeatures',
    'MLPrediction', 
    'FeatureType',
    'SimpleMLModel',
    'VolatilityRegimeModel',
    'get_ml_trading_engine',
    'set_ml_trading_engine'
]
