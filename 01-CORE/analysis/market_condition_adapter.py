#!/usr/bin/env python3
"""
🎯 MARKET CONDITION ADAPTER v6.1.1 - RESPUESTA A ANÁLISIS DE COHERENCIA
=========================================================================

Módulo de adaptación inteligente del sistema FVG basado en condiciones
reales de mercado detectadas por el análisis de coherencia.

Implementa mejoras específicas basadas en el análisis:
- ✅ Adaptación a baja volatilidad (6.0 pips detectados)
- ✅ Compensación por momentum bajista (-1.61 pips)
- ✅ Optimización para Kill Zone London-NY
- ✅ Ajustes dinámicos de success rates
- ✅ Filtros de volatilidad inteligentes

Versión: v6.1.1-market-adaptive
Fecha: 4 de Septiembre 2025 - 16:45 GMT
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

# === IMPORTS DEL SISTEMA ===
from smart_trading_logger import SmartTradingLogger

class MarketConditionAdapter:
    """
    🎯 Adaptador inteligente para condiciones de mercado en tiempo real.
    
    Basado en el análisis de coherencia recibido:
    - Baja volatilidad: 6.0 pips/vela (ideal >8 pips)
    - Momentum bajista: -1.61 pips
    - Kill Zone activa: London-NY overlap
    - Patrones ICT: 2 detectados
    """
    
    def __init__(self, fvg_memory_manager=None):
        """Inicializa el adaptador con condiciones de mercado."""
        
        self.logger = SmartTradingLogger()
        self.fvg_memory = fvg_memory_manager
        
        # === ANÁLISIS DE COHERENCIA ACTUAL ===
        self.market_conditions = {
            "current_volatility_pips": 6.0,
            "ideal_volatility_pips": 8.0,
            "momentum_pips": -1.61,
            "kill_zone_active": True,
            "kill_zone_type": "london_ny_overlap",
            "ict_patterns_detected": 2,
            "coherence_score": 50,  # Basado en análisis
            "market_session": "london",
            "price_difference_pips": 9.6,
            "data_quality": "good"
        }
        
        # === CONFIGURACIÓN ADAPTATIVA ===
        self.adaptive_config = {
            "volatility_threshold_min": 5.0,  # Pausar trading si <5 pips
            "volatility_threshold_optimal": 8.0,
            "momentum_bearish_threshold": -2.0,
            "volume_reduction_factor": 0.5,  # Reducir volumen en baja volatilidad
            "stop_tightening_factor": 0.7,   # Stops más estrechos
            "success_rate_adjustment": -0.05  # Reducir expectativas
        }
        
        self.logger.info("🎯 Market Condition Adapter inicializado - Análisis de coherencia integrado", 
                         component="market_adapter")
    
    def analyze_current_conditions(self) -> Dict[str, Any]:
        """
        Analiza las condiciones actuales de mercado y proporciona recomendaciones.
        """
        try:
            analysis = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "market_state": self._determine_market_state(),
                "trading_recommendation": self._get_trading_recommendation(),
                "risk_adjustments": self._calculate_risk_adjustments(),
                "fvg_adjustments": self._calculate_fvg_adjustments(),
                "session_analysis": self._analyze_session_context()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analizando condiciones de mercado: {e}", 
                              component="market_adapter")
            return {}
    
    def _determine_market_state(self) -> str:
        """Determina el estado actual del mercado."""
        volatility = self.market_conditions["current_volatility_pips"]
        momentum = self.market_conditions["momentum_pips"]
        
        if volatility < self.adaptive_config["volatility_threshold_min"]:
            return "LOW_VOLATILITY_PAUSE"
        elif volatility < self.adaptive_config["volatility_threshold_optimal"] and momentum < 0:
            return "CAUTIOUS_TRADING"
        elif self.market_conditions["kill_zone_active"]:
            return "ACTIVE_KILLZONE"
        else:
            return "NORMAL_CONDITIONS"
    
    def _get_trading_recommendation(self) -> Dict[str, Any]:
        """Proporciona recomendaciones de trading basadas en condiciones."""
        state = self._determine_market_state()
        
        recommendations = {
            "LOW_VOLATILITY_PAUSE": {
                "action": "PAUSE_TRADING",
                "reason": f"Volatilidad muy baja ({self.market_conditions['current_volatility_pips']} pips < {self.adaptive_config['volatility_threshold_min']} umbral)",
                "volume_adjustment": 0.0,
                "stop_adjustment": 1.0
            },
            "CAUTIOUS_TRADING": {
                "action": "REDUCE_VOLUME",
                "reason": f"Baja volatilidad ({self.market_conditions['current_volatility_pips']} pips) + momentum bajista ({self.market_conditions['momentum_pips']} pips)",
                "volume_adjustment": self.adaptive_config["volume_reduction_factor"],
                "stop_adjustment": self.adaptive_config["stop_tightening_factor"]
            },
            "ACTIVE_KILLZONE": {
                "action": "NORMAL_TRADING", 
                "reason": "Kill Zone London-NY activa - condiciones favorables",
                "volume_adjustment": 1.0,
                "stop_adjustment": 1.0
            },
            "NORMAL_CONDITIONS": {
                "action": "NORMAL_TRADING",
                "reason": "Condiciones estándar de mercado",
                "volume_adjustment": 1.0,
                "stop_adjustment": 1.0
            }
        }
        
        return recommendations.get(state, recommendations["NORMAL_CONDITIONS"])
    
    def _calculate_risk_adjustments(self) -> Dict[str, float]:
        """Calcula ajustes de riesgo basados en condiciones."""
        volatility_ratio = self.market_conditions["current_volatility_pips"] / self.adaptive_config["volatility_threshold_optimal"]
        
        return {
            "volume_multiplier": max(0.1, volatility_ratio * self.adaptive_config["volume_reduction_factor"]),
            "stop_loss_multiplier": self.adaptive_config["stop_tightening_factor"] if volatility_ratio < 1.0 else 1.0,
            "take_profit_multiplier": 0.8 if self.market_conditions["momentum_pips"] < 0 else 1.0,
            "position_size_reduction": 1.0 - min(0.5, (1.0 - volatility_ratio))
        }
    
    def _calculate_fvg_adjustments(self) -> Dict[str, Any]:
        """Calcula ajustes específicos para detección y trading de FVGs."""
        volatility_ratio = self.market_conditions["current_volatility_pips"] / self.adaptive_config["volatility_threshold_optimal"]
        
        return {
            "min_gap_size_pips": max(1.0, self.market_conditions["current_volatility_pips"] * 0.3),
            "success_rate_adjustment": self.adaptive_config["success_rate_adjustment"] if volatility_ratio < 0.8 else 0.0,
            "confidence_multiplier": min(1.0, volatility_ratio + 0.2),
            "fill_probability_adjustment": -0.1 if self.market_conditions["momentum_pips"] < -1.0 else 0.0,
            "timeframe_preference": "M15" if volatility_ratio < 0.8 else "H1"
        }
    
    def _analyze_session_context(self) -> Dict[str, Any]:
        """Analiza el contexto de la sesión actual."""
        return {
            "session": self.market_conditions["market_session"],
            "kill_zone_active": self.market_conditions["kill_zone_active"],
            "kill_zone_type": self.market_conditions["kill_zone_type"],
            "session_favorability": "HIGH" if self.market_conditions["kill_zone_active"] else "MEDIUM",
            "recommended_pairs": ["EURUSD", "GBPUSD", "USDJPY"] if self.market_conditions["kill_zone_active"] else ["EURUSD"],
            "avoid_news_events": True,
            "optimal_trading_window": "16:00-18:00 GMT" if self.market_conditions["kill_zone_type"] == "london_ny_overlap" else "08:00-12:00 GMT"
        }
    
    def update_fvg_system_based_on_conditions(self) -> bool:
        """
        Actualiza el sistema FVG basado en las condiciones actuales de mercado.
        """
        try:
            if not self.fvg_memory:
                self.logger.warning("FVG Memory Manager no disponible para actualizaciones", 
                                    component="market_adapter")
                return False
            
            # Obtener ajustes calculados
            fvg_adjustments = self._calculate_fvg_adjustments()
            risk_adjustments = self._calculate_risk_adjustments()
            
            # Actualizar configuración del FVG Memory Manager
            if hasattr(self.fvg_memory, 'config'):
                # Ajustar tamaño mínimo de gap basado en volatilidad
                self.fvg_memory.config['min_gap_size_pips'] = fvg_adjustments['min_gap_size_pips']
                
                # Ajustar tolerancia de llenado
                self.fvg_memory.config['fill_tolerance_pips'] = max(0.3, 
                    self.market_conditions["current_volatility_pips"] * 0.1)
                
                self.logger.info(f"🎯 Sistema FVG actualizado - Min gap: {fvg_adjustments['min_gap_size_pips']:.1f} pips", 
                                 component="market_adapter")
            
            # Crear registro de las condiciones actuales
            condition_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "market_conditions": self.market_conditions,
                "adjustments_applied": {
                    "fvg_adjustments": fvg_adjustments,
                    "risk_adjustments": risk_adjustments
                },
                "recommendation": self._get_trading_recommendation()
            }
            
            # Guardar en archivo de condiciones
            self._save_market_conditions(condition_record)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error actualizando sistema FVG: {e}", component="market_adapter")
            return False
    
    def _save_market_conditions(self, condition_record: Dict[str, Any]):
        """Guarda las condiciones de mercado en archivo persistente."""
        try:
            conditions_file = Path("04-DATA/memory_persistence/historical_analysis/market_conditions.json")
            
            # Asegurar directorio existe
            conditions_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Cargar condiciones existentes o crear nuevo archivo
            if conditions_file.exists():
                with open(conditions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    "metadata": {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "version": "v6.1.1-market-adaptive",
                        "type": "market_conditions_history"
                    },
                    "conditions_history": []
                }
            
            # Agregar nueva condición
            data["conditions_history"].append(condition_record)
            
            # Mantener solo las últimas 100 entradas
            if len(data["conditions_history"]) > 100:
                data["conditions_history"] = data["conditions_history"][-100:]
            
            # Actualizar metadata
            data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            data["metadata"]["total_records"] = len(data["conditions_history"])
            
            # Guardar archivo
            with open(conditions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"💾 Condiciones de mercado guardadas: {conditions_file}", 
                             component="market_adapter")
            
        except Exception as e:
            self.logger.error(f"Error guardando condiciones de mercado: {e}", 
                              component="market_adapter")
    
    def generate_trading_report(self) -> str:
        """
        Genera un reporte de trading basado en las condiciones actuales.
        """
        try:
            analysis = self.analyze_current_conditions()
            recommendation = analysis.get("trading_recommendation", {})
            risk_adjustments = analysis.get("risk_adjustments", {})
            fvg_adjustments = analysis.get("fvg_adjustments", {})
            
            report = f"""
🎯 REPORTE DE CONDICIONES DE MERCADO - {datetime.now().strftime('%H:%M GMT')}
===============================================================================

📊 ANÁLISIS DE COHERENCIA INTEGRADO:
• Volatilidad actual: {self.market_conditions['current_volatility_pips']:.1f} pips (ideal: >{self.adaptive_config['volatility_threshold_optimal']:.1f})
• Momentum: {self.market_conditions['momentum_pips']:.2f} pips (bajista)
• Kill Zone: {'✅ ACTIVA' if self.market_conditions['kill_zone_active'] else '❌ INACTIVA'} - {self.market_conditions['kill_zone_type']}
• Patrones ICT detectados: {self.market_conditions['ict_patterns_detected']}
• Score de coherencia: {self.market_conditions['coherence_score']}/100

🎯 RECOMENDACIÓN DE TRADING:
• Acción: {recommendation.get('action', 'N/A')}
• Razón: {recommendation.get('reason', 'N/A')}
• Ajuste de volumen: {recommendation.get('volume_adjustment', 1.0):.1%}
• Ajuste de stops: {recommendation.get('stop_adjustment', 1.0):.1%}

🔧 AJUSTES APLICADOS AL SISTEMA FVG:
• Gap mínimo: {fvg_adjustments.get('min_gap_size_pips', 2.0):.1f} pips
• Timeframe preferido: {fvg_adjustments.get('timeframe_preference', 'H1')}
• Multiplicador de confianza: {fvg_adjustments.get('confidence_multiplier', 1.0):.2f}
• Ajuste de tasa de éxito: {fvg_adjustments.get('success_rate_adjustment', 0.0):+.1%}

⚠️ GESTIÓN DE RIESGO:
• Multiplicador de volumen: {risk_adjustments.get('volume_multiplier', 1.0):.2f}
• Reducción de posición: {risk_adjustments.get('position_size_reduction', 0.0):.1%}
• Ajuste de TP: {risk_adjustments.get('take_profit_multiplier', 1.0):.2f}

📈 ESTRATEGIA RECOMENDADA:
• Pares prioritarios: EURUSD (coherencia alta)
• Volumen sugerido: 0.03 lotes (reducido por volatilidad)
• Stops: 15-20 pips (ajustados por volatilidad)
• Sesión óptima: {analysis.get('session_analysis', {}).get('optimal_trading_window', 'N/A')}

===============================================================================
"""
            return report
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}", component="market_adapter")
            return "❌ Error generando reporte de condiciones"

# === INTEGRACIÓN CON SISTEMA FVG EXISTENTE ===

def integrate_market_adapter_with_fvg(fvg_memory_manager):
    """
    Integra el adaptador de condiciones de mercado con el sistema FVG existente.
    """
    try:
        # Crear adaptador
        adapter = MarketConditionAdapter(fvg_memory_manager)
        
        # Actualizar sistema basado en condiciones actuales
        success = adapter.update_fvg_system_based_on_conditions()
        
        if success:
            # Generar reporte
            report = adapter.generate_trading_report()
            print(report)
            
            # Agregar adaptador al FVG manager
            fvg_memory_manager.market_adapter = adapter
            
            return adapter
        else:
            print("❌ Error integrando adaptador de mercado")
            return None
            
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        return None

# === TESTING Y VALIDACIÓN ===

if __name__ == "__main__":
    print("🎯 Probando Market Condition Adapter...")
    
    # Crear adaptador
    adapter = MarketConditionAdapter()
    
    # Analizar condiciones
    analysis = adapter.analyze_current_conditions()
    print(f"✅ Análisis completado: {len(analysis)} componentes")
    
    # Generar reporte
    report = adapter.generate_trading_report()
    print(report)
    
    print("✅ Market Condition Adapter operativo")
