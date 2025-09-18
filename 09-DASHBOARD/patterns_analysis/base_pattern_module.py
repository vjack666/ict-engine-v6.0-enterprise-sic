#!/usr/bin/env python3
"""
🎯 BASE PATTERN DASHBOARD MODULE
===============================

Clase base para todos los módulos de análisis de patrones ICT.
Proporciona funcionalidad común y interfaz estándar.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: Septiembre 6, 2025
Versión: v1.0.0-modular
"""

import time
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path

# Configurar rutas para acceso a módulos core
dashboard_root = Path(__file__).parent.parent
project_root = dashboard_root.parent
sys.path.insert(0, str(project_root / "01-CORE"))
sys.path.insert(0, str(project_root / "01-CORE" / "data_management"))
sys.path.insert(0, str(project_root))  # Raíz del proyecto para validador

# Importar validador de datos crítico
try:
    # El validador está en 01-CORE/data_management/
    sys.path.insert(0, str(project_root / "01-CORE" / "data_management"))
    from data_validator_real_trading import RealTradingDataValidator  # type: ignore
    VALIDATOR_AVAILABLE = True
    print("✅ Validador de datos importado correctamente")
except ImportError as e:
    print(f"⚠️ Validador de datos no disponible: {e}")
    # Crear fallback
    class RealTradingDataValidator:  # type: ignore
        def __init__(self): pass
        def validate_data(self, data): return True
        def validate_price_data(self, data): return data  # Retorna los datos sin modificar
        def validate_pattern_analysis(self, result): return result  # Retorna el resultado sin modificar
    VALIDATOR_AVAILABLE = False

@dataclass
class PatternAnalysisResult:
    """Resultado estándar de análisis de patrón"""
    pattern_name: str
    symbol: str
    timeframe: str
    timestamp: datetime
    
    # Datos del patrón
    confidence: float  # 0-100
    strength: float    # 0-100
    direction: str     # BUY/SELL/NEUTRAL
    
    # Niveles de precio
    entry_zone: Tuple[float, float]
    stop_loss: float
    take_profit_1: float
    take_profit_2: Optional[float] = None
    
    # Métricas
    risk_reward_ratio: float = 0.0
    probability: float = 0.0
    
    # Recomendaciones
    scalping_viability: str = "UNKNOWN"  # HIGH/MEDIUM/LOW/NONE
    intraday_viability: str = "UNKNOWN"  # HIGH/MEDIUM/LOW/NONE
    recommended_timeframes: List[str] = field(default_factory=list)
    
    # Contexto
    session: str = "UNKNOWN"
    confluences: List[str] = field(default_factory=list)
    invalidation_criteria: str = ""
    narrative: str = ""
    
    # Metadata
    analysis_id: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)


class BasePatternDashboard(ABC):
    """
    🎯 Clase base para módulos de análisis de patrones
    
    Proporciona funcionalidad común para todos los tipos de patrones:
    - Conexión con detectores del core
    - Procesamiento de datos estándar
    - Generación de recomendaciones
    - Layout de dashboard
    """
    
    def __init__(self, pattern_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar módulo base de patrón
        
        Args:
            pattern_name: Nombre del patrón (ej: "silver_bullet", "judas_swing")
            config: Configuración específica del patrón
        """
        self.pattern_name = pattern_name
        self.config = config or {}
        self.last_analysis_time = None
        self.cached_results = {}
        self.cache_ttl = self.config.get('cache_ttl_seconds', 300)  # 5 minutos default
        
        # Inicializar validador de datos crítico
        if VALIDATOR_AVAILABLE and RealTradingDataValidator is not None:
            try:
                self.data_validator = RealTradingDataValidator()
                print(f"✅ Validador inicializado para {self.pattern_name}")
            except Exception as e:
                print(f"⚠️ Error inicializando validador: {e}")
                self.data_validator = None
        else:
            self.data_validator = None
        
        # Cargar configuración específica del patrón
        self._load_pattern_config()
        
        # Inicializar conexión con detector del core
        self._initialize_pattern_detector()
        
    def validate_market_data(self, data: Union[dict, Any]) -> Union[dict, Any]:
        """
        Validar datos de mercado usando el validador crítico
        
        Args:
            data: Datos de mercado a validar
            
        Returns:
            Datos validados con valores seguros
        """
        if self.data_validator is None:
            # Sin validador, usar datos directamente (riesgo alto)
            print(f"⚠️ Validador no disponible para {self.pattern_name}")
            return data
            
        try:
            validated_data = self.data_validator.validate_price_data(data)
            return validated_data
        except Exception as e:
            print(f"❌ Error validando datos en {self.pattern_name}: {e}")
            # Retornar datos seguros por defecto
            return {}
    
    def validate_pattern_result(self, result: dict) -> dict:
        """
        Validar resultado de análisis de patrón
        
        Args:
            result: Diccionario con resultado de análisis
            
        Returns:
            Resultado validado con valores seguros
        """
        if self.data_validator is None:
            print(f"⚠️ Validador no disponible para resultado de {self.pattern_name}")
            return result
            
        try:
            validated_result = self.data_validator.validate_pattern_analysis(result)
            return validated_result
        except Exception as e:
            print(f"❌ Error validando resultado en {self.pattern_name}: {e}")
            # Retornar resultado seguro por defecto
            return {
                'signal': 'HOLD',
                'confidence': 0.0,
                'risk_reward_ratio': 0.0,
                'pattern_name': self.pattern_name,
                'timestamp': datetime.now(),
                'error': f"Validación fallida: {e}"
            }
        
    def _load_pattern_config(self):
        """Cargar configuración específica del patrón"""
        try:
            config_path = Path(__file__).parent / "config" / f"{self.pattern_name}_config.json"
            if config_path.exists():
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    pattern_config = json.load(f)
                    self.config.update(pattern_config)
        except Exception as e:
            print(f"⚠️ No se pudo cargar config para {self.pattern_name}: {e}")
    
    def _initialize_pattern_detector(self):
        """Inicializar conexión con detector del core"""
        try:
            # Intentar cargar el detector principal
            from ict_engine.pattern_detector import PatternDetector
            self.pattern_detector = PatternDetector()
            print(f"✅ Detector inicializado para patrón: {self.pattern_name}")
        except ImportError as e:
            print(f"⚠️ No se pudo cargar PatternDetector: {e}")
            self.pattern_detector = None
    
    def is_cache_valid(self, symbol: str, timeframe: str) -> bool:
        """Verificar si el cache es válido para el símbolo y timeframe"""
        cache_key = f"{symbol}_{timeframe}"
        if cache_key not in self.cached_results:
            return False
        
        cached_time = self.cached_results[cache_key].get('timestamp')
        if not cached_time:
            return False
        
        age = (datetime.now() - cached_time).total_seconds()
        return age < self.cache_ttl
    
    def get_cached_result(self, symbol: str, timeframe: str) -> Optional[PatternAnalysisResult]:
        """Obtener resultado desde cache si está disponible"""
        cache_key = f"{symbol}_{timeframe}"
        if self.is_cache_valid(symbol, timeframe):
            cached_data = self.cached_results[cache_key]
            return cached_data.get('result')
        return None
    
    def cache_result(self, symbol: str, timeframe: str, result: PatternAnalysisResult):
        """Guardar resultado en cache"""
        cache_key = f"{symbol}_{timeframe}"
        self.cached_results[cache_key] = {
            'timestamp': datetime.now(),
            'result': result
        }
    
    def analyze_pattern(self, symbol: str, timeframe: str, force_refresh: bool = False) -> PatternAnalysisResult:
        """
        Analizar patrón para símbolo y timeframe específico
        
        Args:
            symbol: Símbolo a analizar (ej: "EURUSD")
            timeframe: Timeframe (ej: "M15", "H1")
            force_refresh: Forzar análisis sin usar cache
        
        Returns:
            PatternAnalysisResult con análisis completo
        """
        # Verificar cache si no se fuerza refresh
        if not force_refresh:
            cached_result = self.get_cached_result(symbol, timeframe)
            if cached_result:
                return cached_result
        
        try:
            # Realizar análisis específico del patrón
            result = self._perform_pattern_analysis(symbol, timeframe)
            
            # Validar datos del resultado si el validador está disponible
            if self.data_validator is not None and hasattr(result, '__dict__'):
                try:
                    result_dict = result.__dict__
                    validated_dict = self.validate_pattern_result(result_dict)
                    
                    # Actualizar resultado con datos validados
                    for key, value in validated_dict.items():
                        if hasattr(result, key):
                            setattr(result, key, value)
                except Exception as validation_error:
                    print(f"⚠️ Error en validación de {self.pattern_name}: {validation_error}")
            
            # Generar recomendaciones
            result = self._generate_recommendations(result)
            
            # Guardar en cache
            self.cache_result(symbol, timeframe, result)
            
            return result
            
        except Exception as e:
            print(f"❌ Error en análisis de {self.pattern_name} para {symbol} {timeframe}: {e}")
            # Retornar resultado seguro por defecto
            safe_result = PatternAnalysisResult(
                pattern_name=self.pattern_name,
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.now(),
                confidence=0.0,
                strength=0.0,
                direction="NEUTRAL",
                entry_zone=(0.0, 0.0),
                stop_loss=0.0,
                take_profit_1=0.0,
                risk_reward_ratio=0.0
            )
            return safe_result
    
    def analyze_market_data(self, symbol: str = "EURUSD", timeframe: str = "H1", 
                          force_refresh: bool = False) -> Optional[PatternAnalysisResult]:
        """
        Alias para analyze_pattern - Analizar datos de mercado
        
        Args:
            symbol: Símbolo a analizar (ej: "EURUSD")
            timeframe: Timeframe (ej: "M15", "H1")
            force_refresh: Forzar análisis sin usar cache
        
        Returns:
            PatternAnalysisResult con análisis completo
        """
        return self.analyze_pattern(symbol, timeframe, force_refresh)
    
    @abstractmethod
    def _perform_pattern_analysis(self, symbol: str, timeframe: str) -> PatternAnalysisResult:
        """
        Realizar análisis específico del patrón (implementar en subclases)
        
        Args:
            symbol: Símbolo a analizar
            timeframe: Timeframe a analizar
        
        Returns:
            PatternAnalysisResult con datos básicos del patrón
        """
        pass
    
    def _generate_recommendations(self, result: PatternAnalysisResult) -> PatternAnalysisResult:
        """
        Generar recomendaciones de scalping e intraday basadas en métricas
        
        Args:
            result: Resultado básico del análisis
        
        Returns:
            Resultado con recomendaciones añadidas
        """
        # Recomendaciones de scalping (timeframes cortos, alta probabilidad)
        if result.confidence >= 80 and result.timeframe in ['M1', 'M5', 'M15']:
            if result.risk_reward_ratio >= 1.5:
                result.scalping_viability = "HIGH"
            elif result.risk_reward_ratio >= 1.0:
                result.scalping_viability = "MEDIUM"
            else:
                result.scalping_viability = "LOW"
        else:
            result.scalping_viability = "LOW"
        
        # Recomendaciones intraday (timeframes medios, buen R:R)
        if result.confidence >= 70 and result.timeframe in ['M15', 'M30', 'H1']:
            if result.risk_reward_ratio >= 2.0:
                result.intraday_viability = "HIGH"
            elif result.risk_reward_ratio >= 1.5:
                result.intraday_viability = "MEDIUM"
            else:
                result.intraday_viability = "LOW"
        else:
            result.intraday_viability = "LOW"
        
        # Timeframes recomendados
        if result.scalping_viability in ["HIGH", "MEDIUM"]:
            result.recommended_timeframes.extend(["M1", "M5", "M15"])
        if result.intraday_viability in ["HIGH", "MEDIUM"]:
            result.recommended_timeframes.extend(["M15", "M30", "H1"])
        
        # Eliminar duplicados
        result.recommended_timeframes = list(set(result.recommended_timeframes))
        
        return result
    
    @abstractmethod
    def create_dashboard_layout(self, result: PatternAnalysisResult) -> str:
        """
        Crear layout del dashboard para mostrar el análisis
        
        Args:
            result: Resultado del análisis del patrón
        
        Returns:
            String con markup para el dashboard (Rich markup)
        """
        pass
    
    def get_pattern_summary(self, symbol: str, timeframes: List[str]) -> Dict[str, Any]:
        """
        Obtener resumen del patrón para múltiples timeframes
        
        Args:
            symbol: Símbolo a analizar
            timeframes: Lista de timeframes
        
        Returns:
            Diccionario con resumen consolidado
        """
        results = {}
        best_setup = None
        best_confidence = 0
        
        for tf in timeframes:
            try:
                result = self.analyze_pattern(symbol, tf)
                results[tf] = result
                
                if result.confidence > best_confidence:
                    best_confidence = result.confidence
                    best_setup = result
                    
            except Exception as e:
                print(f"⚠️ Error analizando {self.pattern_name} en {tf}: {e}")
                continue
        
        return {
            'pattern_name': self.pattern_name,
            'symbol': symbol,
            'timeframes_analyzed': list(results.keys()),
            'best_setup': best_setup,
            'all_results': results,
            'overall_recommendation': self._get_overall_recommendation(results)
        }
    
    def _get_overall_recommendation(self, results: Dict[str, PatternAnalysisResult]) -> Dict[str, Any]:
        """Generar recomendación general basada en todos los timeframes"""
        if not results:
            return {'recommendation': 'NO_SIGNAL', 'confidence': 0}
        
        # Encontrar mejor configuración
        best_result = max(results.values(), key=lambda x: x.confidence)
        
        # Contar señales por dirección
        buy_signals = sum(1 for r in results.values() if r.direction == 'BUY' and r.confidence >= 60)
        sell_signals = sum(1 for r in results.values() if r.direction == 'SELL' and r.confidence >= 60)
        
        # Determinar recomendación
        if buy_signals > sell_signals and best_result.confidence >= 70:
            recommendation = 'BUY'
        elif sell_signals > buy_signals and best_result.confidence >= 70:
            recommendation = 'SELL'
        else:
            recommendation = 'WAIT'
        
        return {
            'recommendation': recommendation,
            'confidence': best_result.confidence,
            'best_timeframe': best_result.timeframe,
            'risk_reward': best_result.risk_reward_ratio,
            'scalping_ready': best_result.scalping_viability in ['HIGH', 'MEDIUM'],
            'intraday_ready': best_result.intraday_viability in ['HIGH', 'MEDIUM']
        }


class PatternDashboardUtils:
    """Utilidades comunes para módulos de patrones"""
    
    @staticmethod
    def format_price(price: float, symbol: str) -> str:
        """Formatear precio según el símbolo"""
        if symbol.endswith('JPY'):
            return f"{price:.3f}"
        elif 'XAU' in symbol:  # Gold
            return f"{price:.2f}"
        else:
            return f"{price:.5f}"
    
    @staticmethod
    def get_confidence_color(confidence: float) -> str:
        """Obtener color para mostrar confianza"""
        if confidence >= 80:
            return "bold green"
        elif confidence >= 60:
            return "bold yellow"
        elif confidence >= 40:
            return "bold orange"
        else:
            return "bold red"
    
    @staticmethod
    def get_direction_emoji(direction: str) -> str:
        """Obtener emoji según dirección"""
        if direction == 'BUY':
            return "🟢"
        elif direction == 'SELL':
            return "🔴"
        else:
            return "⚪"
    
    @staticmethod
    def format_timeframe_display(timeframe: str) -> str:
        """Formatear timeframe para display"""
        tf_map = {
            'M1': '1min',
            'M5': '5min', 
            'M15': '15min',
            'M30': '30min',
            'H1': '1h',
            'H4': '4h',
            'D1': '1D'
        }
        return tf_map.get(timeframe, timeframe)
