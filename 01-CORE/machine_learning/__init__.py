#!/usr/bin/env python3
"""
🧠 MACHINE LEARNING SYSTEM v6.0 ENTERPRISE - ICT ENGINE
========================================================

Sistema de Machine Learning integrado para potenciar:
- POI (Points of Interest) detection y scoring
- BOS (Break of Structure) pattern recognition  
- Liquidity analysis y grab detection
- Smart Money concepts enhancement
- Order Blocks validation

Arquitectura:
- Feature extraction desde datos existentes ICT
- Modelos ML especializados por tipo de análisis  
- Pipeline de entrenamiento automatizado
- Inferencia tiempo real integrada
- Validación y backtesting continuo

Autor: ICT Engine v6.0 Enterprise ML Team
Fecha: 15 Septiembre 2025
Versión: v6.0.0-ml-integration
"""

import os
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Tuple, TYPE_CHECKING
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import logging
from typing import TYPE_CHECKING

# Market Structure integration (opcional con guardas de tipos)
_MS_AVAILABLE = False
if not TYPE_CHECKING:
    try:  # noqa: E402
        from market_structure.engine import MarketStructureEngine, MarketStructureResult  # type: ignore
        _MS_AVAILABLE = True
    except Exception:  # pragma: no cover
        MarketStructureEngine = object  # type: ignore
        MarketStructureResult = object  # type: ignore
else:  # Durante type checking preferimos referencias forward para evitar errores
    try:  # type: ignore
        from market_structure.engine import MarketStructureEngine, MarketStructureResult  # type: ignore
    except Exception:  # pragma: no cover
        class MarketStructureEngine:  # type: ignore
            ...
        class MarketStructureResult:  # type: ignore
            ...

# ML Libraries
try:
    import sklearn
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split, GridSearchCV
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    import joblib
    ML_AVAILABLE = True
except ImportError:
    print("⚠️ ML libraries not available - install sklearn, joblib")
    ML_AVAILABLE = False

# Integración con sistema existente (protegida)
try:
    from smart_trading_logger import log_trading_decision_smart_v6  # type: ignore
except ImportError:  # Fallback no-op para evitar NameError en runtime / type check
    def log_trading_decision_smart_v6(event: str, data: Dict[str, Any]):  # type: ignore
        pass

try:
    from analysis.poi_system import POI, POIType, POISignificance  # type: ignore
except ImportError:
    POI = Any  # type: ignore
    POIType = Any  # type: ignore
    POISignificance = Any  # type: ignore

try:
    from ict_engine.pattern_detector import ICTPattern  # type: ignore
except ImportError:
    ICTPattern = Any  # type: ignore

try:
    from analysis.unified_memory_system import get_unified_memory_system  # type: ignore
    _UNIFIED_MEMORY_AVAILABLE = True
except ImportError:
    _UNIFIED_MEMORY_AVAILABLE = False
    def get_unified_memory_system():  # type: ignore
        return None

SYSTEM_INTEGRATION_AVAILABLE = any([
    'log_trading_decision_smart_v6' in globals(),
    'POI' in globals(),
    _UNIFIED_MEMORY_AVAILABLE
])

# Alias de tipo seguro para POI en anotaciones
try:
    if isinstance(POI, type):  # type: ignore
        POITypeAlias = POI  # type: ignore
    else:  # pragma: no cover
        POITypeAlias = Any  # type: ignore
except Exception:  # pragma: no cover
    POITypeAlias = Any  # type: ignore

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLModelType(Enum):
    """Tipos de modelos ML disponibles"""
    POI_CLASSIFIER = "poi_classifier"
    POI_SCORER = "poi_scorer"
    BOS_DETECTOR = "bos_detector"
    BOS_CONFIDENCE = "bos_confidence"
    LIQUIDITY_ANALYZER = "liquidity_analyzer"
    PATTERN_VALIDATOR = "pattern_validator"
    SMART_MONEY_SCORER = "smart_money_scorer"

class MLFeatureType(Enum):
    """Tipos de features ML"""
    PRICE_ACTION = "price_action"
    VOLUME_PROFILE = "volume_profile"
    MARKET_STRUCTURE = "market_structure"
    LIQUIDITY_METRICS = "liquidity_metrics"
    TEMPORAL_PATTERNS = "temporal_patterns"
    CONFLUENCE_INDICATORS = "confluence_indicators"

@dataclass
class MLPrediction:
    """Resultado de predicción ML"""
    model_type: MLModelType
    prediction: Union[str, float, int, List]
    confidence: float
    features_used: List[str]
    timestamp: datetime
    model_version: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MLTrainingResult:
    """Resultado de entrenamiento ML"""
    model_type: MLModelType
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int
    validation_samples: int
    training_time: float
    model_path: str
    feature_importance: Dict[str, float]
    hyperparameters: Dict[str, Any]
    timestamp: datetime

class ICTMLSystem:
    """
    🧠 SISTEMA ML PRINCIPAL PARA ICT ENGINE
    
    Coordina todos los aspectos de ML:
    - Feature extraction
    - Model training y management
    - Inferencia tiempo real
    - Validation y monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Inicializar sistema ML"""
        self.config = self._load_default_config()
        if config:
            self.config.update(config)
        
        # Rutas del sistema
        self.base_path = Path(self.config['base_path'])
        self.models_path = self.base_path / "models"
        self.data_path = self.base_path / "data"
        self.logs_path = self.base_path / "logs"
        
        # Crear directorios
        for path in [self.models_path, self.data_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Estado del sistema
        self.loaded_models: Dict[MLModelType, Any] = {}
        self.feature_extractors: Dict[MLFeatureType, Any] = {}
        self.scalers: Dict[str, Any] = {}
        
        # Métricas
        self.prediction_cache: Dict[str, MLPrediction] = {}
        self.performance_metrics: Dict[str, Any] = {}
        
        # Integración con sistema ICT
        self.memory_system = None
        if _UNIFIED_MEMORY_AVAILABLE and SYSTEM_INTEGRATION_AVAILABLE:
            try:
                self.memory_system = get_unified_memory_system()
            except Exception:
                self.memory_system = None

        # Market Structure Engine (estructura mínima)
        self.market_structure_engine = None
        if _MS_AVAILABLE:
            try:
                self.market_structure_engine = MarketStructureEngine()  # type: ignore[call-arg]
            except Exception:
                self.market_structure_engine = None
        
        self._initialize_components()
        
        try:
            log_trading_decision_smart_v6("ML_SYSTEM_INITIALIZED", {
                "component": "ICTMLSystem",
                "models_path": str(self.models_path),
                "ml_available": ML_AVAILABLE,
                "system_integration": SYSTEM_INTEGRATION_AVAILABLE
            })
        except Exception:
            pass
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del sistema ML"""
        return {
            'base_path': '01-CORE/machine_learning',
            'cache_predictions': True,
            'cache_timeout': 300,  # 5 minutos
            'auto_retrain': True,
            'retrain_threshold': 0.85,  # Accuracy mínima
            'feature_selection': True,
            'hyperparameter_tuning': True,
            'cross_validation_folds': 5,
            'test_size': 0.2,
            'random_state': 42,
            
            # Configuración por modelo
            'models': {
                'poi_classifier': {
                    'algorithm': 'random_forest',
                    'n_estimators': 100,
                    'max_depth': 10,
                    'min_samples_split': 5
                },
                'poi_scorer': {
                    'algorithm': 'gradient_boosting',
                    'n_estimators': 200,
                    'learning_rate': 0.1,
                    'max_depth': 6
                },
                'bos_detector': {
                    'algorithm': 'random_forest',
                    'n_estimators': 150,
                    'max_depth': 12,
                    'min_samples_split': 3
                }
            }
        }
    
    def _initialize_components(self):
        """Inicializar componentes ML"""
        try:
            # Inicializar extractores de features
            self._initialize_feature_extractors()
            
            # Cargar modelos existentes
            self._load_existing_models()
            
            logger.info("✅ ML System components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing ML components: {e}")
    
    def _initialize_feature_extractors(self):
        """Inicializar extractores de features"""
        # Placeholder - implementar en siguiente fase
        pass
    
    def _load_existing_models(self):
        """Cargar modelos ML existentes"""
        if not ML_AVAILABLE:
            return
        
        for model_file in self.models_path.glob("*.joblib"):
            try:
                model_name = model_file.stem
                model = joblib.load(model_file)  # type: ignore[arg-type]
                
                # Determinar tipo de modelo
                for model_type in MLModelType:
                    if model_type.value in model_name:
                        self.loaded_models[model_type] = model
                        logger.info(f"✅ Loaded model: {model_name}")
                        break
                        
            except Exception as e:
                logger.error(f"❌ Error loading model {model_file}: {e}")
    
    # ============================================================================
    # 🔍 FEATURE EXTRACTION
    # ============================================================================
    
    def extract_poi_features(self, market_data: Any, poi: Any) -> Dict[str, float]:
        """Extraer features para análisis POI"""
        features = {}
        
        if not hasattr(market_data, 'close'):
            return features
        
        try:
            # Features básicos de precio
            features['price_distance'] = abs(poi.price_level - market_data['close'].iloc[-1])
            features['price_distance_pct'] = features['price_distance'] / market_data['close'].iloc[-1]
            
            # Features de volatilidad
            if len(market_data) >= 20:
                features['volatility_20'] = market_data['close'].rolling(20).std().iloc[-1]
                features['atr_ratio'] = features['price_distance'] / features['volatility_20']
            
            # Features temporales
            if poi.created_at:
                age_hours = (datetime.now() - poi.created_at).total_seconds() / 3600
                features['poi_age_hours'] = age_hours
                features['poi_age_normalized'] = min(age_hours / 24, 1.0)  # Normalizar a 24h
            
            # Features de confluencia
            features['confluence_count'] = len(poi.confluences) if poi.confluences else 0
            features['poi_strength'] = poi.strength / 100.0  # Normalizar 0-1
            features['test_count'] = poi.test_count
            
            # Features de zona de precio
            zone_size = abs(poi.price_zone[1] - poi.price_zone[0])
            features['zone_size'] = zone_size
            features['zone_size_pct'] = zone_size / market_data['close'].iloc[-1]
            
        except Exception as e:
            logger.error(f"Error extracting POI features: {e}")
        
        return features
    
    def extract_bos_features(self, market_data: Any, structure_data: Optional[Dict] = None) -> Dict[str, float]:
        """Extraer features para detección BOS"""
        features = {}
        
        if not hasattr(market_data, 'close'):
            return features
        
        try:
            # Features de price action
            if len(market_data) >= 50:
                # Momentum features
                features['roc_10'] = (market_data['close'].iloc[-1] / market_data['close'].iloc[-11] - 1)
                features['roc_20'] = (market_data['close'].iloc[-1] / market_data['close'].iloc[-21] - 1)
                
                # Volatility features
                features['volatility_ratio'] = (
                    market_data['close'].rolling(10).std().iloc[-1] / 
                    market_data['close'].rolling(20).std().iloc[-1]
                )
                
                # Structure features
                recent_high = market_data['high'].rolling(20).max().iloc[-1]
                recent_low = market_data['low'].rolling(20).min().iloc[-1]
                current_price = market_data['close'].iloc[-1]
                
                features['position_in_range'] = (
                    (current_price - recent_low) / (recent_high - recent_low)
                    if recent_high != recent_low else 0.5
                )
            
            # Features de volumen si disponible
            if 'volume' in market_data.columns:
                vol_ma = market_data['volume'].rolling(20).mean().iloc[-1]
                current_vol = market_data['volume'].iloc[-1]
                features['volume_ratio'] = current_vol / vol_ma if vol_ma > 0 else 1.0
            
            # Features de estructura si disponibles
            if structure_data:
                features['trend_strength'] = structure_data.get('trend_strength', 0.5)
                features['support_resistance_strength'] = structure_data.get('sr_strength', 0.5)
            # Si no se provee structure_data e engine disponible, derivar bias interno
            elif self.market_structure_engine is not None:
                try:
                    # Construcción rápida de velas mínimas si posible
                    # Se espera que market_data sea DataFrame OHLC
                    tail = market_data.tail(60)
                    candles = []
                    for idx, row in tail.iterrows():  # type: ignore[attr-defined]
                        candles.append({
                            'time': getattr(idx, 'isoformat', lambda: str(idx))(),
                            'open': float(row.get('open', row['close'])),
                            'high': float(row['high']),
                            'low': float(row['low']),
                            'close': float(row['close'])
                        })
                    sym = getattr(market_data, 'symbol', 'UNKNOWN')
                    tf = getattr(market_data, 'timeframe', 'UNK')
                    ms_result = self.market_structure_engine.run_full_analysis(symbol=sym, timeframe=tf, candles=candles)  # type: ignore[attr-defined]
                    # Extraer algunos rasgos estructurales base
                    features['ms_bias_flag'] = 1 if ms_result.market_bias == 'BULLISH' else (-1 if ms_result.market_bias == 'BEARISH' else 0)
                    features['ms_choch_count'] = len(ms_result.choch_events)
                    features['ms_bos_count'] = len(ms_result.bos_events)
                    features['ms_ob_count'] = len(ms_result.order_blocks)
                    features['ms_fvg_count'] = len(ms_result.fvg_zones)
                except Exception as e:  # pragma: no cover
                    logger.debug(f"MS integration fallback in BOS features: {e}")
                
        except Exception as e:
            logger.error(f"Error extracting BOS features: {e}")
        
        return features

    # ========================================================================
    # 🧱 MARKET STRUCTURE INTEGRATION
    # ========================================================================
    def get_market_structure_analysis(self, symbol: str, timeframe: str, candles: List[Dict[str, Any]], mtf_context: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> Optional[Any]:
        """Ejecuta análisis completo de market structure y retorna resultado.
        Retorna None si engine no disponible o error.
        """
        if self.market_structure_engine is None:
            return None
        try:
            return self.market_structure_engine.run_full_analysis(symbol, timeframe, candles, mtf_context)  # type: ignore[arg-type]
        except Exception as e:  # pragma: no cover
            logger.debug(f"MarketStructure analysis failed: {e}")
            return None

    def extract_market_structure_features(self, ms_result: Optional[Any]) -> Dict[str, float]:
        """Convierte un MarketStructureResult en features planos para ML."""
        feats: Dict[str, float] = {}
        if not ms_result:
            return feats
        try:
            feats['ms_bias_bull'] = 1.0 if ms_result.market_bias == 'BULLISH' else 0.0
            feats['ms_bias_bear'] = 1.0 if ms_result.market_bias == 'BEARISH' else 0.0
            feats['ms_bias_neutral'] = 1.0 if ms_result.market_bias == 'NEUTRAL' else 0.0
            feats['ms_choch'] = float(len(ms_result.choch_events))
            feats['ms_bos'] = float(len(ms_result.bos_events))
            feats['ms_ob'] = float(len(ms_result.order_blocks))
            feats['ms_fvg'] = float(len(ms_result.fvg_zones))
            agreement = ms_result.multi_timeframe_context.get('agreement_score') if isinstance(ms_result.multi_timeframe_context, dict) else None
            if isinstance(agreement, (int, float)):
                feats['ms_mtf_agreement'] = float(agreement)
        except Exception as e:  # pragma: no cover
            logger.debug(f"Error extracting MS features: {e}")
        return feats
    
    # ============================================================================
    # 🎯 PREDICCIONES ML
    # ============================================================================
    
    def predict_poi_significance(self, market_data: Any, poi: Any) -> Optional[MLPrediction]:
        """Predecir significancia de POI usando ML"""
        if not ML_AVAILABLE or MLModelType.POI_CLASSIFIER not in self.loaded_models:
            return None
        
        try:
            # Extraer features
            features = self.extract_poi_features(market_data, poi)
            if not features:
                return None
            
            # Preparar datos para predicción
            feature_array = np.array([list(features.values())]).reshape(1, -1)
            
            # Escalar features si hay scaler disponible
            scaler_key = f"{MLModelType.POI_CLASSIFIER.value}_scaler"
            if scaler_key in self.scalers:
                feature_array = self.scalers[scaler_key].transform(feature_array)
            
            # Realizar predicción
            model = self.loaded_models[MLModelType.POI_CLASSIFIER]
            prediction = model.predict(feature_array)[0]
            confidence = max(model.predict_proba(feature_array)[0])
            
            return MLPrediction(
                model_type=MLModelType.POI_CLASSIFIER,
                prediction=prediction,
                confidence=confidence,
                features_used=list(features.keys()),
                timestamp=datetime.now(),
                model_version="v1.0",
                metadata={'original_poi_strength': poi.strength}
            )
            
        except Exception as e:
            logger.error(f"Error predicting POI significance: {e}")
            return None
    
    def predict_bos_probability(self, market_data: Any, structure_data: Optional[Dict] = None) -> Optional[MLPrediction]:
        """Predecir probabilidad de BOS usando ML"""
        if not ML_AVAILABLE or MLModelType.BOS_DETECTOR not in self.loaded_models:
            return None
        
        try:
            # Extraer features
            features = self.extract_bos_features(market_data, structure_data)
            if not features:
                return None
            
            # Preparar datos para predicción
            feature_array = np.array([list(features.values())]).reshape(1, -1)
            
            # Escalar features si hay scaler disponible
            scaler_key = f"{MLModelType.BOS_DETECTOR.value}_scaler"
            if scaler_key in self.scalers:
                feature_array = self.scalers[scaler_key].transform(feature_array)
            
            # Realizar predicción
            model = self.loaded_models[MLModelType.BOS_DETECTOR]
            prediction = model.predict(feature_array)[0]
            confidence = max(model.predict_proba(feature_array)[0])
            
            return MLPrediction(
                model_type=MLModelType.BOS_DETECTOR,
                prediction=prediction,
                confidence=confidence,
                features_used=list(features.keys()),
                timestamp=datetime.now(),
                model_version="v1.0",
                metadata=features
            )
            
        except Exception as e:
            logger.error(f"Error predicting BOS probability: {e}")
            return None
    
    # ============================================================================
    # 📊 UTILIDADES Y STATUS
    # ============================================================================
    
    def get_system_status(self) -> Dict[str, Any]:
        """Estado del sistema ML"""
        return {
            'ml_available': ML_AVAILABLE,
            'system_integration': SYSTEM_INTEGRATION_AVAILABLE,
            'loaded_models': list(self.loaded_models.keys()),
            'models_count': len(self.loaded_models),
            'cache_size': len(self.prediction_cache),
            'last_prediction': max([p.timestamp for p in self.prediction_cache.values()]) if self.prediction_cache else None,
            'base_path': str(self.base_path),
            'timestamp': datetime.now()
        }
    
    def clear_cache(self):
        """Limpiar cache de predicciones"""
        self.prediction_cache.clear()
        logger.info("🧹 ML prediction cache cleared")

# ============================================================================
# 🎯 SINGLETON Y FACTORY
# ============================================================================

_ict_ml_system_instance: Optional[ICTMLSystem] = None

def get_ict_ml_system(config: Optional[Dict[str, Any]] = None) -> ICTMLSystem:
    """Obtener instancia singleton del sistema ML"""
    global _ict_ml_system_instance
    
    if _ict_ml_system_instance is None:
        _ict_ml_system_instance = ICTMLSystem(config)
    
    return _ict_ml_system_instance

def reset_ict_ml_system():
    """Reset del sistema ML (para testing)"""
    global _ict_ml_system_instance
    _ict_ml_system_instance = None

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================================

def enhance_poi_with_ml(poi: Any, market_data: Any) -> Any:  # type: ignore[name-defined]
    """Potenciar POI con análisis ML"""
    if not SYSTEM_INTEGRATION_AVAILABLE:
        return poi
    try:
        ml_system = get_ict_ml_system()
        prediction = ml_system.predict_poi_significance(market_data, poi)
        if prediction and prediction.confidence > 0.7:
            if not hasattr(poi, 'metadata') or getattr(poi, 'metadata') is None:
                try:
                    setattr(poi, 'metadata', {})
                except Exception:
                    pass
            try:
                poi.metadata['ml_enhanced'] = True  # type: ignore[index]
                poi.metadata['ml_prediction'] = prediction.prediction  # type: ignore[index]
                poi.metadata['ml_confidence'] = prediction.confidence  # type: ignore[index]
                poi.metadata['ml_timestamp'] = prediction.timestamp.isoformat()  # type: ignore[index]
            except Exception:
                pass
            if prediction.confidence > 0.8:
                try:
                    ml_factor = 1.0 + (prediction.confidence - 0.5) * 0.2
                    poi.strength = min(100.0, poi.strength * ml_factor)  # type: ignore[attr-defined]
                except Exception:
                    pass
    except Exception as ex:  # noqa: BLE001
        logger.error(f"Error enhancing POI with ML: {ex}")
    return poi

def enhance_bos_pattern_with_ml(pattern: Dict[str, Any], market_data: Any) -> Dict[str, Any]:
    """Potenciar patrón BOS con análisis ML"""
    if not SYSTEM_INTEGRATION_AVAILABLE:
        return pattern
    try:
        ml_system = get_ict_ml_system()
        prediction = ml_system.predict_bos_probability(market_data)
        if prediction and prediction.confidence > 0.7:
            if 'ml_analysis' not in pattern:
                pattern['ml_analysis'] = {}
            try:
                pattern['ml_analysis']['enhanced'] = True
                pattern['ml_analysis']['prediction'] = prediction.prediction
                pattern['ml_analysis']['confidence'] = prediction.confidence
                pattern['ml_analysis']['timestamp'] = prediction.timestamp.isoformat()
            except Exception:
                pass
            if prediction.confidence > 0.8:
                try:
                    original_confidence = pattern.get('confidence', 0.5)
                    ml_boost = (prediction.confidence - 0.5) * 0.3
                    pattern['confidence'] = min(1.0, original_confidence + ml_boost)
                except Exception:
                    pass
    except Exception as ex:  # noqa: BLE001
        logger.error(f"Error enhancing BOS pattern with ML: {ex}")
    return pattern

# ============================================================================
# 📝 EXPORTS
# ============================================================================

__all__ = [
    'ICTMLSystem',
    'MLModelType', 
    'MLFeatureType',
    'MLPrediction',
    'MLTrainingResult',
    'get_ict_ml_system',
    'enhance_poi_with_ml',
    'enhance_bos_pattern_with_ml'
]