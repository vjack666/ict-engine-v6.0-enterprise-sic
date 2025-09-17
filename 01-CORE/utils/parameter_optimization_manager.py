#!/usr/bin/env python3
"""
🎯 PARAMETER OPTIMIZATION MANAGER - ICT Engine v6.0 Enterprise
==============================================================

Sistema de gestión de parámetros optimizados para detección de patrones ICT.
Permite cargar, aplicar y ajustar dinámicamente parámetros de detección
para mejorar precisión y reducir falsos positivos.

Funcionalidades:
- Carga de configuración optimizada desde YAML
- Aplicación dinámica de parámetros por componente
- Adaptación automática según condiciones de mercado
- Monitoreo de performance y ajuste automático
- Validación de parámetros antes de aplicar

Autor: ICT Engine v6.1.0 Enterprise Team
Fecha: Septiembre 2025
"""

import yaml
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """Regímenes de mercado para adaptación de parámetros"""
    TRENDING_HIGH_VOL = "trending_high_volatility"
    TRENDING_LOW_VOL = "trending_low_volatility" 
    RANGING_HIGH_VOL = "ranging_high_volatility"
    RANGING_LOW_VOL = "ranging_low_volatility"
    UNKNOWN = "unknown"

class OptimizationLevel(Enum):
    """Niveles de optimización disponibles"""
    CONSERVATIVE = "conservative"     # Parámetros conservadores, menos falsos positivos
    BALANCED = "balanced"            # Balance entre precisión y cobertura
    AGGRESSIVE = "aggressive"        # Más detecciones, puede incrementar falsos positivos
    ADAPTIVE = "adaptive"            # Ajuste automático según performance

@dataclass
class PerformanceMetrics:
    """Métricas de performance para evaluación"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    false_positive_rate: float = 0.0
    processing_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    pattern_count: int = 0
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ParameterOptimizationManager:
    """
    🎯 Manager principal de optimización de parámetros
    
    Gestiona la carga, aplicación y optimización dinámica de parámetros
    de detección para todos los componentes del sistema ICT.
    """
    
    def __init__(self, config_path: Optional[str] = None, optimization_level: OptimizationLevel = OptimizationLevel.BALANCED):
        """
        Inicializar el manager de optimización
        
        Args:
            config_path: Ruta al archivo de configuración YAML
            optimization_level: Nivel de optimización a aplicar
        """
        self.optimization_level = optimization_level
        self.config_path = config_path or self._get_default_config_path()
        self.parameters = {}
        self.performance_history: List[PerformanceMetrics] = []
        self.current_market_regime = MarketRegime.UNKNOWN
        self.last_adjustment = datetime.now()
        self.adjustment_interval = timedelta(hours=24)
        
        # Cargar configuración inicial
        self.load_configuration()
        
        # Aplicar nivel de optimización
        self.apply_optimization_level()
        
        logger.info(f"🎯 ParameterOptimizationManager initialized with level: {optimization_level.value}")
        
    def _get_default_config_path(self) -> str:
        """Obtener ruta por defecto del archivo de configuración"""
        current_dir = Path(__file__).parent
        return str(current_dir / "optimized_detection_parameters.yaml")
    
    def load_configuration(self) -> bool:
        """
        Cargar configuración desde archivo YAML
        
        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"❌ Archivo de configuración no encontrado: {self.config_path}")
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.parameters = yaml.safe_load(file)
            
            logger.info(f"✅ Configuración cargada desde: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            return False
    
    def apply_optimization_level(self):
        """Aplicar ajustes según el nivel de optimización seleccionado"""
        if self.optimization_level == OptimizationLevel.CONSERVATIVE:
            self._apply_conservative_adjustments()
        elif self.optimization_level == OptimizationLevel.AGGRESSIVE:
            self._apply_aggressive_adjustments()
        elif self.optimization_level == OptimizationLevel.ADAPTIVE:
            self._setup_adaptive_parameters()
        
        logger.info(f"🔧 Aplicados ajustes para nivel: {self.optimization_level.value}")
    
    def _apply_conservative_adjustments(self):
        """Aplicar ajustes conservadores para reducir falsos positivos"""
        adjustments = {
            'order_blocks': {'min_confidence': 75.0, 'volume_threshold': 1.8},
            'choch': {'base_confidence': 80.0, 'min_swing_size_pips': 20},
            'bos': {'min_confidence': 80.0, 'break_confirmation_pips': 5},
            'fair_value_gaps': {'min_gap_size_pips': 4.0}
        }
        self._apply_parameter_adjustments(adjustments)
    
    def _apply_aggressive_adjustments(self):
        """Aplicar ajustes agresivos para mayor cobertura"""
        adjustments = {
            'order_blocks': {'min_confidence': 55.0, 'volume_threshold': 1.2},
            'choch': {'base_confidence': 60.0, 'min_swing_size_pips': 10},
            'bos': {'min_confidence': 65.0, 'break_confirmation_pips': 2},
            'fair_value_gaps': {'min_gap_size_pips': 2.0}
        }
        self._apply_parameter_adjustments(adjustments)
    
    def _setup_adaptive_parameters(self):
        """Configurar parámetros adaptativos"""
        if 'adaptive' not in self.parameters:
            self.parameters['adaptive'] = {}
        
        self.parameters['adaptive']['auto_adjustment']['enabled'] = True
        logger.info("🤖 Modo adaptativo habilitado")
    
    def _apply_parameter_adjustments(self, adjustments: Dict[str, Dict[str, Any]]):
        """Aplicar ajustes específicos a los parámetros"""
        for component, params in adjustments.items():
            if component in self.parameters:
                self.parameters[component].update(params)
    
    def get_parameters_for_component(self, component: str) -> Dict[str, Any]:
        """
        Obtener parámetros optimizados para un componente específico
        
        Args:
            component: Nombre del componente (order_blocks, choch, bos, etc.)
            
        Returns:
            Dict con parámetros del componente
        """
        if component not in self.parameters:
            logger.warning(f"⚠️ Componente '{component}' no encontrado en configuración")
            return {}
        
        params = self.parameters[component].copy()
        
        # Aplicar adaptación por régimen de mercado si está habilitada
        if self.current_market_regime != MarketRegime.UNKNOWN:
            params = self._adapt_parameters_for_market_regime(params, component)
        
        return params
    
    def _adapt_parameters_for_market_regime(self, params: Dict[str, Any], component: str) -> Dict[str, Any]:
        """
        Adaptar parámetros según el régimen de mercado actual
        
        Args:
            params: Parámetros base del componente
            component: Nombre del componente
            
        Returns:
            Parámetros adaptados
        """
        # Ejemplo de adaptación para FVG en alta volatilidad
        if component == 'fair_value_gaps' and 'high_volatility' in self.current_market_regime.value:
            if 'market_conditions' in params and 'high_volatility' in params['market_conditions']:
                high_vol_config = params['market_conditions']['high_volatility']
                
                # Aplicar multiplicador de gap mínimo
                if 'min_gap_size_multiplier' in high_vol_config:
                    params['min_gap_size_pips'] *= high_vol_config['min_gap_size_multiplier']
                
                # Aplicar ajuste de confianza
                if 'confidence_adjustment' in high_vol_config and 'base_confidence' in params:
                    params['base_confidence'] += high_vol_config['confidence_adjustment']
        
        return params
    
    def update_market_regime(self, volatility: float, trend_strength: float, volume_profile: float):
        """
        Actualizar el régimen de mercado basado en métricas
        
        Args:
            volatility: Nivel de volatilidad (0.0-1.0)
            trend_strength: Fuerza de la tendencia (0.0-1.0)
            volume_profile: Perfil de volumen (0.0-1.0)
        """
        # Lógica simplificada para determinar régimen
        is_high_volatility = volatility > 0.6
        is_trending = trend_strength > 0.6
        
        if is_trending and is_high_volatility:
            self.current_market_regime = MarketRegime.TRENDING_HIGH_VOL
        elif is_trending and not is_high_volatility:
            self.current_market_regime = MarketRegime.TRENDING_LOW_VOL
        elif not is_trending and is_high_volatility:
            self.current_market_regime = MarketRegime.RANGING_HIGH_VOL
        else:
            self.current_market_regime = MarketRegime.RANGING_LOW_VOL
        
        logger.info(f"📊 Régimen de mercado actualizado: {self.current_market_regime.value}")
    
    def record_performance_metrics(self, metrics: PerformanceMetrics):
        """
        Registrar métricas de performance para evaluación
        
        Args:
            metrics: Métricas de performance del sistema
        """
        self.performance_history.append(metrics)
        
        # Mantener solo las últimas 100 métricas para evitar consumo excesivo de memoria
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
        
        # Evaluar si es necesario un ajuste automático
        if self.optimization_level == OptimizationLevel.ADAPTIVE:
            self._evaluate_auto_adjustment(metrics)
        
        logger.info(f"📈 Métricas registradas - Accuracy: {metrics.accuracy:.2%}, "
                   f"FPR: {metrics.false_positive_rate:.2%}, "
                   f"Processing: {metrics.processing_time_ms:.1f}ms")
    
    def _evaluate_auto_adjustment(self, current_metrics: PerformanceMetrics):
        """
        Evaluar si se requiere ajuste automático de parámetros
        
        Args:
            current_metrics: Métricas actuales de performance
        """
        # Verificar si ha pasado suficiente tiempo desde el último ajuste
        if datetime.now() - self.last_adjustment < self.adjustment_interval:
            return
        
        # Verificar si tenemos suficiente historial para evaluación
        if len(self.performance_history) < 10:
            return
        
        # Calcular métricas promedio de los últimos 10 registros
        recent_metrics = self.performance_history[-10:]
        avg_accuracy = sum(m.accuracy for m in recent_metrics) / len(recent_metrics)
        avg_fpr = sum(m.false_positive_rate for m in recent_metrics) / len(recent_metrics)
        
        # Definir umbrales para ajuste
        target_accuracy = self.parameters.get('validation', {}).get('quality_metrics', {}).get('min_pattern_accuracy', 0.70)
        max_fpr = self.parameters.get('validation', {}).get('quality_metrics', {}).get('max_false_positive_rate', 0.20)
        
        adjustment_needed = False
        adjustment_direction = "none"
        
        # Determinar si necesitamos ajuste
        if avg_accuracy < target_accuracy:
            adjustment_needed = True
            adjustment_direction = "conservative"  # Reducir falsos positivos
        elif avg_fpr > max_fpr:
            adjustment_needed = True
            adjustment_direction = "conservative"  # Reducir falsos positivos
        elif avg_accuracy > target_accuracy + 0.1 and avg_fpr < max_fpr * 0.5:
            adjustment_needed = True
            adjustment_direction = "aggressive"    # Incrementar cobertura
        
        if adjustment_needed:
            self._perform_auto_adjustment(adjustment_direction)
            self.last_adjustment = datetime.now()
    
    def _perform_auto_adjustment(self, direction: str):
        """
        Realizar ajuste automático de parámetros
        
        Args:
            direction: Dirección del ajuste ("conservative" o "aggressive")
        """
        max_adjustment = self.parameters.get('adaptive', {}).get('auto_adjustment', {}).get('max_adjustment_percent', 0.20)
        
        if direction == "conservative":
            # Incrementar umbrales para reducir falsos positivos
            adjustments = {
                'order_blocks': {'min_confidence': lambda x: min(95.0, x * (1 + max_adjustment * 0.5))},
                'choch': {'base_confidence': lambda x: min(95.0, x * (1 + max_adjustment * 0.5))},
                'bos': {'min_confidence': lambda x: min(95.0, x * (1 + max_adjustment * 0.5))}
            }
        else:  # aggressive
            # Reducir umbrales para incrementar cobertura
            adjustments = {
                'order_blocks': {'min_confidence': lambda x: max(50.0, x * (1 - max_adjustment * 0.5))},
                'choch': {'base_confidence': lambda x: max(50.0, x * (1 - max_adjustment * 0.5))},
                'bos': {'min_confidence': lambda x: max(50.0, x * (1 - max_adjustment * 0.5))}
            }
        
        # Aplicar ajustes
        for component, param_adjustments in adjustments.items():
            if component in self.parameters:
                for param_name, adjustment_func in param_adjustments.items():
                    if param_name in self.parameters[component]:
                        old_value = self.parameters[component][param_name]
                        new_value = adjustment_func(old_value)
                        self.parameters[component][param_name] = new_value
                        
                        logger.info(f"🔧 Ajuste automático - {component}.{param_name}: "
                                  f"{old_value:.1f} → {new_value:.1f} ({direction})")
    
    def export_optimized_config(self, output_path: Optional[str] = None) -> str:
        """
        Exportar configuración optimizada actual a archivo YAML
        
        Args:
            output_path: Ruta de salida (opcional)
            
        Returns:
            Ruta del archivo generado
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"optimized_config_{timestamp}.yaml"
        
        # Agregar metadata
        export_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'optimization_level': self.optimization_level.value,
                'market_regime': self.current_market_regime.value,
                'performance_samples': len(self.performance_history)
            },
            **self.parameters
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                yaml.dump(export_data, file, default_flow_style=False, indent=2, allow_unicode=True)
            
            logger.info(f"✅ Configuración optimizada exportada: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error exportando configuración: {e}")
            raise
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de performance actual
        
        Returns:
            Dict con resumen de métricas
        """
        if not self.performance_history:
            return {"status": "No performance data available"}
        
        recent_metrics = self.performance_history[-10:] if len(self.performance_history) >= 10 else self.performance_history
        
        return {
            "current_regime": self.current_market_regime.value,
            "optimization_level": self.optimization_level.value,
            "samples_count": len(self.performance_history),
            "recent_performance": {
                "avg_accuracy": sum(m.accuracy for m in recent_metrics) / len(recent_metrics),
                "avg_precision": sum(m.precision for m in recent_metrics) / len(recent_metrics),
                "avg_recall": sum(m.recall for m in recent_metrics) / len(recent_metrics),
                "avg_fpr": sum(m.false_positive_rate for m in recent_metrics) / len(recent_metrics),
                "avg_processing_time_ms": sum(m.processing_time_ms for m in recent_metrics) / len(recent_metrics)
            },
            "last_adjustment": self.last_adjustment.isoformat(),
            "next_adjustment_due": (self.last_adjustment + self.adjustment_interval).isoformat()
        }

def create_parameter_manager(optimization_level: str = "balanced") -> ParameterOptimizationManager:
    """
    Factory function para crear manager de parámetros
    
    Args:
        optimization_level: Nivel de optimización ("conservative", "balanced", "aggressive", "adaptive")
        
    Returns:
        ParameterOptimizationManager configurado
    """
    level = OptimizationLevel(optimization_level.lower())
    return ParameterOptimizationManager(optimization_level=level)

if __name__ == "__main__":
    # Ejemplo de uso
    print("🎯 ICT Parameter Optimization Manager v6.0")
    print("=" * 50)
    
    # Crear manager con nivel balanced
    manager = create_parameter_manager("balanced")
    
    # Obtener parámetros para order blocks
    ob_params = manager.get_parameters_for_component("order_blocks")
    print(f"📦 Order Blocks Parameters: {ob_params}")
    
    # Simular métricas de performance
    test_metrics = PerformanceMetrics(
        accuracy=0.78,
        precision=0.82,
        recall=0.75,
        false_positive_rate=0.15,
        processing_time_ms=45.2
    )
    manager.record_performance_metrics(test_metrics)
    
    # Mostrar resumen
    summary = manager.get_performance_summary()
    print(f"📊 Performance Summary: {summary}")
    
    # Exportar configuración optimizada
    output_file = manager.export_optimized_config()
    print(f"📁 Configuración exportada: {output_file}")
    
    print("✅ Optimización completada")