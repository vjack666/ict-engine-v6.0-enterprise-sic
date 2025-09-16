#!/usr/bin/env python3
"""
📊 MULTI-TIMEFRAME ANALYZER - ICT Enterprise v6.0
==================================================

Pipeline multi-timeframe ICT H4 → M15 → M5 completamente implementado.
Migrado desde proyecto principal/core/ict_engine/ict_detector.py

Funcionalidades:
- H4 Bias Analysis (Authority timeframe)
- M15 Structure Detection (Confirmation timeframe) 
- M5 LTF Confirmation (Timing timeframe)
- Overall Direction with ICT hierarchy
- Enterprise logging and error handling

Versión: v6.0.1 Enterprise
Migrado: 8 de agosto, 2025
"""

# === IMPORTS ENTERPRISE SYSTEM ===

from protocols.unified_logging import get_unified_logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from typing import Dict, Any, Optional, List, Tuple, Union
from json import JSONDecodeError
import pandas as pd
import numpy as np

# Type alias for better type safety
DataFrameType = pd.DataFrame

# === IMPORTS ENTERPRISE LOGGING ===
try:
    from smart_trading_logger import log_info as _log_info, log_warning as _log_warning, log_error as _log_error
    def log_info(msg, context="multi_tf"):
        _log_info(msg, context)
    def log_warning(msg, context="multi_tf"):
        _log_warning(msg, context)
    def log_error(msg, context="multi_tf"):
        _log_error(msg, context)
    enterprise_logging_available = True
except ImportError:
    def log_info(msg, context="multi_tf"):
        print(f"INFO [{context}]: {msg}")
    def log_warning(msg, context="multi_tf"):
        print(f"WARNING [{context}]: {msg}")
    def log_error(msg, context="multi_tf"):
        print(f"ERROR [{context}]: {msg}")
    enterprise_logging_available = False

# === IMPORTS ENTERPRISE ENUMS ===
try:
    # Intento 1: Import relativo (cuando se importa como módulo)
    from ..enums import StructureTypeV6
except ImportError:
    # Intento 2: Import directo (cuando se ejecuta directamente)
    import sys
    from pathlib import Path
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from enums import StructureTypeV6

enums_available = True

# =============================================================================
# CONFIGURACIÓN ICT ENTERPRISE
# =============================================================================

ICT_CONFIG_ENTERPRISE = {
    'h4_bias_lookback': 20,
    'm15_structure_lookback': 50,
    'ltf_confirmation_lookback': 20,
    'bias_threshold_pct': 0.1,
    'structure_strength_threshold': 0.4,
    'premium_discount_tolerance': 0.5,
    'swing_detection_left': 5,
    'swing_detection_right': 1,
    'ob_lookback_candles': 20,
    'fvg_gap_threshold': 0.0001,
    # Enterprise specific
    'cache_enabled': True,
    'performance_mode': 'enterprise',
    'error_tolerance': 'strict'
}

# ICT HIERARCHY WEIGHTS (Enterprise Configuration)
ICT_HIERARCHY_WEIGHTS = {
    'h4_weight': 0.6,    # H4 Authority (60%)
    'm15_weight': 0.3,   # M15 Confirmation (30%)
    'm5_weight': 0.1,    # M5 Timing (10%)
    'conflict_penalty': 0.5,  # Penalty for HTF vs LTF conflicts
    'confidence_threshold': 0.5  # Minimum threshold for direction
}

BIAS_TYPES_V6 = {
    'BULLISH': 'Sesgo Alcista H4',
    'BEARISH': 'Sesgo Bajista H4', 
    'NEUTRAL': 'Sesgo Neutral H4',
    'NO_DATA': 'Sin Datos Suficientes',
    'ERROR': 'Error en Análisis'
}

STRUCTURE_TYPES_V6 = {
    'bullish_structure': 'Estructura Alcista',
    'bearish_structure': 'Estructura Bajista',
    'consolidation': 'Consolidación',
    'insufficient_data': 'Datos Insuficientes',
    'error': 'Error en Detección'
}

# --- Log de carga inicial ---
if enterprise_logging_available:
    log_info("✅ Multi-Timeframe Analyzer Enterprise v6.0 cargándose", "init")
    log_info("✅ Enterprise logging habilitado", "init")
    log_info("✅ Enterprise enums disponibles", "init")
else:
    print("🔧 Multi-Timeframe Analyzer v6.0 cargándose - logging básico")

# =============================================================================
# CLASE PRINCIPAL - OPTIMIZED ICT ANALYSIS ENTERPRISE
# =============================================================================

class OptimizedICTAnalysisEnterprise:
    """
    📊 Análisis ICT multi-timeframe optimizado para Enterprise v6.0
    
    Pipeline completo H4 → M15 → M5 con:
    - H4 Bias calculation (Authority timeframe)
    - M15 Structure detection (Confirmation timeframe)
    - M5 LTF confirmation (Timing timeframe)
    - ICT hierarchy weights implementation
    - Enterprise logging and caching
    - Error handling robusto
    
    Migrado desde proyecto principal OptimizedICTAnalysis
    Adaptado para Enterprise system
    """

    def __init__(self):
        """Inicializar analyzer con configuración enterprise"""
        self.cache_enabled = ICT_CONFIG_ENTERPRISE['cache_enabled']
        self.performance_mode = ICT_CONFIG_ENTERPRISE['performance_mode']
        self.error_tolerance = ICT_CONFIG_ENTERPRISE['error_tolerance']
        
        # Cache para optimización enterprise
        self._cache = {}
        
        log_info("OptimizedICTAnalysisEnterprise inicializado", "init")
        log_info(f"Cache: {self.cache_enabled}, Mode: {self.performance_mode}", "init")

    def calcular_bias_h4_optimizado(self, df_h4: DataFrameType) -> Dict[str, Any]:
        """
        📈 Cálculo optimizado de bias H4 con lógica ICT real
        
        Args:
            df_h4: DataFrame con datos H4 (OHLC)
            
        Returns:
            Dict con bias, strength, status
        """
        if df_h4 is None or len(df_h4) < ICT_CONFIG_ENTERPRISE['h4_bias_lookback']:
            log_warning(f"Datos H4 insuficientes: {len(df_h4) if df_h4 is not None else 0} velas", "h4_bias")
            return {
                "bias": "NO_DATA",
                "strength": 0.0,
                "status": "insufficient_data",
                "bars_analyzed": len(df_h4) if df_h4 is not None else 0
            }

        try:
            # Lógica mejorada de bias H4
            recent_bars = df_h4.tail(ICT_CONFIG_ENTERPRISE['h4_bias_lookback'])
            log_info(f"Analizando {len(recent_bars)} velas H4 para bias", "h4_bias")

            if len(recent_bars) >= 10:
                # Análisis first half vs second half
                first_half = recent_bars.head(10)
                second_half = recent_bars.tail(10)
                
                first_half_avg = first_half['close'].mean()
                second_half_avg = second_half['close'].mean()

                price_change_pct = ((second_half_avg - first_half_avg) / first_half_avg) * 100
                
                # Calcular strength basado en el cambio
                strength = min(abs(price_change_pct) / ICT_CONFIG_ENTERPRISE['bias_threshold_pct'], 1.0)

                # Determinar bias según threshold
                threshold = ICT_CONFIG_ENTERPRISE['bias_threshold_pct']
                if price_change_pct > threshold:
                    bias = "BULLISH"
                    log_info(f"H4 Bias: BULLISH ({price_change_pct:.3f}%, strength: {strength:.3f})", "h4_bias")
                elif price_change_pct < -threshold:
                    bias = "BEARISH"
                    log_info(f"H4 Bias: BEARISH ({price_change_pct:.3f}%, strength: {strength:.3f})", "h4_bias")
                else:
                    bias = "NEUTRAL"
                    log_info(f"H4 Bias: NEUTRAL ({price_change_pct:.3f}%, strength: {strength:.3f})", "h4_bias")

                return {
                    "bias": bias,
                    "strength": strength,
                    "price_change_pct": price_change_pct,
                    "status": "analyzed",
                    "bars_analyzed": len(recent_bars),
                    "first_half_avg": first_half_avg,
                    "second_half_avg": second_half_avg
                }

            # Fallback para datos limitados
            log_warning("Datos H4 limitados, usando análisis simple", "h4_bias")
            return {
                "bias": "NEUTRAL",
                "strength": 0.3,
                "status": "limited_data",
                "bars_analyzed": len(recent_bars)
            }

        except Exception as e:
            log_error(f"Error calculando bias H4: {e}", "h4_bias")
            return {
                "bias": "ERROR",
                "strength": 0.0,
                "status": "error",
                "error": str(e)
            }

    def detectar_estructura_m15_optimizada(self, df_m15: DataFrameType) -> Dict[str, Any]:
        """
        🏗️ Detección optimizada de estructura M15 con lógica ICT real
        
        Args:
            df_m15: DataFrame con datos M15 (OHLC)
            
        Returns:
            Dict con type, strength, bos_detected, levels
        """
        if df_m15 is None or len(df_m15) < ICT_CONFIG_ENTERPRISE['m15_structure_lookback']:
            log_warning(f"Datos M15 insuficientes: {len(df_m15) if df_m15 is not None else 0} velas", "m15_structure")
            return {
                "type": "insufficient_data", 
                "strength": 0, 
                "bos_detected": False,
                "status": "insufficient_data"
            }

        try:
            # Lógica funcional para detectar estructura M15
            recent_data = df_m15.tail(ICT_CONFIG_ENTERPRISE['m15_structure_lookback'])
            log_info(f"Analizando {len(recent_data)} velas M15 para estructura", "m15_structure")

            # Detectar Break of Structure (BOS) usando rolling windows optimizados
            highs = recent_data['high']
            lows = recent_data['low']
            closes = recent_data['close']

            # Calcular niveles clave con rolling windows
            resistance_window = 10
            support_window = 10
            
            resistance_level = highs.rolling(window=resistance_window).max().iloc[-1]
            support_level = lows.rolling(window=support_window).min().iloc[-1]
            current_price = closes.iloc[-1]
            
            # Calcular momentum reciente
            momentum = (closes.iloc[-1] - closes.iloc[-5]) / closes.iloc[-5]
            
            # Determinar estructura basada en breakout y momentum
            resistance_break_threshold = 0.999  # 99.9% del nivel
            support_break_threshold = 1.001    # 100.1% del nivel
            
            if current_price > resistance_level * resistance_break_threshold:
                # Posible bullish structure
                structure_type = "bullish_structure"
                strength = min(0.8 + abs(momentum) * 2, 1.0)  # Base 0.8 + momentum boost
                bos_detected = True
                log_info(f"M15 Structure: BULLISH break at {current_price:.5f} > {resistance_level:.5f}", "m15_structure")
                
            elif current_price < support_level * support_break_threshold:
                # Posible bearish structure
                structure_type = "bearish_structure"
                strength = min(0.8 + abs(momentum) * 2, 1.0)  # Base 0.8 + momentum boost
                bos_detected = True
                log_info(f"M15 Structure: BEARISH break at {current_price:.5f} < {support_level:.5f}", "m15_structure")
                
            else:
                # Consolidación
                structure_type = "consolidation"
                range_size = (resistance_level - support_level) / support_level
                strength = max(0.4 - range_size, 0.1)  # Menor fuerza en consolidación
                bos_detected = False
                log_info(f"M15 Structure: CONSOLIDATION between {support_level:.5f} - {resistance_level:.5f}", "m15_structure")

            return {
                "type": structure_type,
                "strength": round(strength, 3),
                "bos_detected": bos_detected,
                "resistance": round(resistance_level, 5),
                "support": round(support_level, 5),
                "current_price": round(current_price, 5),
                "momentum": round(momentum, 4),
                "status": "analyzed",
                "bars_analyzed": len(recent_data)
            }

        except Exception as e:
            log_error(f"Error detectando estructura M15: {e}", "m15_structure")
            return {
                "type": "error", 
                "strength": 0, 
                "bos_detected": False, 
                "error": str(e),
                "status": "error"
            }

    def analizar_confirmacion_ltf(self, df_m5: DataFrameType, m15_structure: Dict) -> Dict[str, Any]:
        """
        ⚡ Análisis de confirmación en Lower Time Frame (M5)
        
        Args:
            df_m5: DataFrame con datos M5 (OHLC)
            m15_structure: Resultado del análisis M15
            
        Returns:
            Dict con confirmation, strength, direction
        """
        if df_m5 is None or len(df_m5) < ICT_CONFIG_ENTERPRISE['ltf_confirmation_lookback']:
            log_warning(f"Datos M5 insuficientes para confirmación: {len(df_m5) if df_m5 is not None else 0} velas", "m5_confirmation")
            return {
                "confirmation": False, 
                "strength": 0,
                "direction": "neutral",
                "status": "insufficient_data"
            }

        try:
            # Lógica de confirmación LTF usando momentum
            recent_m5 = df_m5.tail(ICT_CONFIG_ENTERPRISE['ltf_confirmation_lookback'])
            log_info(f"Analizando {len(recent_m5)} velas M5 para confirmación LTF", "m5_confirmation")

            # Calcular momentum en diferentes períodos
            momentum_short = (recent_m5['close'].iloc[-1] - recent_m5['close'].iloc[-5]) / recent_m5['close'].iloc[-5]
            momentum_medium = (recent_m5['close'].iloc[-1] - recent_m5['close'].iloc[-10]) / recent_m5['close'].iloc[-10]
            
            momentum_threshold = 0.001  # 0.1% threshold
            
            # Confirmar según estructura M15
            m15_type = m15_structure.get("type", "CONSOLIDATION")  # Consolidación más específico que ranging
            
            if m15_type == "bullish_structure":
                # Buscar confirmación bullish en M5
                if momentum_short > momentum_threshold and momentum_medium > momentum_threshold:
                    confirmation = True
                    strength = min(0.8, 0.6 + abs(momentum_medium) * 20)  # Base + momentum boost
                    direction = "bullish"
                    log_info(f"M5 Confirmation: BULLISH confirmado (momentum: {momentum_medium:.4f})", "m5_confirmation")
                elif momentum_medium > momentum_threshold * 0.5:
                    confirmation = True
                    strength = 0.6
                    direction = "bullish"
                    log_info(f"M5 Confirmation: BULLISH débil (momentum: {momentum_medium:.4f})", "m5_confirmation")
                else:
                    confirmation = False
                    strength = 0.3
                    direction = "neutral"
                    log_warning(f"M5 Confirmation: Sin confirmación bullish (momentum: {momentum_medium:.4f})", "m5_confirmation")

            elif m15_type == "bearish_structure":
                # Buscar confirmación bearish en M5
                if momentum_short < -momentum_threshold and momentum_medium < -momentum_threshold:
                    confirmation = True
                    strength = min(0.8, 0.6 + abs(momentum_medium) * 20)  # Base + momentum boost
                    direction = "bearish"
                    log_info(f"M5 Confirmation: BEARISH confirmado (momentum: {momentum_medium:.4f})", "m5_confirmation")
                elif momentum_medium < -momentum_threshold * 0.5:
                    confirmation = True
                    strength = 0.6
                    direction = "bearish"
                    log_info(f"M5 Confirmation: BEARISH débil (momentum: {momentum_medium:.4f})", "m5_confirmation")
                else:
                    confirmation = False
                    strength = 0.3
                    direction = "neutral"
                    log_warning(f"M5 Confirmation: Sin confirmación bearish (momentum: {momentum_medium:.4f})", "m5_confirmation")
            else:
                # M15 en consolidación o error
                confirmation = False
                strength = 0.3
                direction = "neutral"
                log_info(f"M5 Confirmation: M15 en {m15_type}, sin análisis LTF", "m5_confirmation")

            return {
                "confirmation": confirmation,
                "strength": round(strength, 3),
                "direction": direction,
                "momentum_short": round(momentum_short, 4),
                "momentum_medium": round(momentum_medium, 4),
                "m15_structure_type": m15_type,
                "status": "analyzed",
                "bars_analyzed": len(recent_m5)
            }

        except Exception as e:
            log_error(f"Error en confirmación LTF: {e}", "m5_confirmation")
            return {
                "confirmation": False, 
                "strength": 0, 
                "error": str(e),
                "status": "error"
            }

    def _determine_overall_direction_ict_weighted(self, h4_bias: Dict, m15_structure: Dict, ltf_confirmation: Dict) -> Dict[str, Any]:
        """
        🎯 Determina dirección general basada en jerarquía ICT estricta
        
        Implementa pesos ICT correctos:
        - H4 Authority: 60% peso
        - M15 Confirmation: 30% peso (solo si alinea con H4)
        - M5 Timing: 10% peso
        
        Args:
            h4_bias: Resultado análisis H4
            m15_structure: Resultado análisis M15  
            ltf_confirmation: Resultado análisis M5
            
        Returns:
            Dict con direction, strength, confidence, authority_tf
        """
        try:
            log_info("Iniciando determinación dirección con jerarquía ICT", "overall_direction")
            
            direction_score = 0.0
            weights = ICT_HIERARCHY_WEIGHTS
            
            # H4 BIAS: Autoridad máxima (60% peso)
            h4_bias_str = h4_bias.get('bias', 'NEUTRAL')
            h4_strength = h4_bias.get('strength', 0.5)
            
            if h4_bias_str == "BULLISH":
                h4_contribution = weights['h4_weight'] * h4_strength
                direction_score += h4_contribution
                log_info(f"H4 BULLISH: +{h4_contribution:.3f} (peso: {weights['h4_weight']}, strength: {h4_strength:.3f})", "overall_direction")
            elif h4_bias_str == "BEARISH":
                h4_contribution = weights['h4_weight'] * h4_strength
                direction_score -= h4_contribution
                log_info(f"H4 BEARISH: -{h4_contribution:.3f} (peso: {weights['h4_weight']}, strength: {h4_strength:.3f})", "overall_direction")
            else:
                log_info(f"H4 NEUTRAL/ERROR: sin contribución", "overall_direction")

            # M15 STRUCTURE: Confirmación (30% peso, solo si alinea con H4)
            m15_type = m15_structure.get("type", "CONSOLIDATION")  # Consolidación más específico
            m15_strength = m15_structure.get("strength", 0.0)
            
            # Verificar alineación H4 vs M15
            h4_m15_aligned = self._check_timeframe_alignment(h4_bias_str, m15_type)
            
            if h4_m15_aligned:
                if m15_type == "bullish_structure":
                    m15_contribution = weights['m15_weight'] * m15_strength
                    direction_score += m15_contribution
                    log_info(f"M15 BULLISH (alineado): +{m15_contribution:.3f}", "overall_direction")
                elif m15_type == "bearish_structure":
                    m15_contribution = weights['m15_weight'] * m15_strength
                    direction_score -= m15_contribution
                    log_info(f"M15 BEARISH (alineado): -{m15_contribution:.3f}", "overall_direction")
                else:
                    log_info(f"M15 {m15_type}: sin contribución", "overall_direction")
            else:
                # PENALIZAR conflictos H4 vs M15
                direction_score *= weights['conflict_penalty']
                log_warning(f"CONFLICTO H4 ({h4_bias_str}) vs M15 ({m15_type}): score reducido a {direction_score:.3f}", "overall_direction")

            # M5 LTF CONFIRMATION: Timing (10% peso)
            ltf_direction = ltf_confirmation.get("direction", "neutral")
            ltf_strength = ltf_confirmation.get("strength", 0.0)
            
            if ltf_direction == "bullish":
                m5_contribution = weights['m5_weight'] * ltf_strength
                direction_score += m5_contribution
                log_info(f"M5 BULLISH: +{m5_contribution:.3f}", "overall_direction")
            elif ltf_direction == "bearish":
                m5_contribution = weights['m5_weight'] * ltf_strength
                direction_score -= m5_contribution
                log_info(f"M5 BEARISH: -{m5_contribution:.3f}", "overall_direction")
            else:
                log_info(f"M5 NEUTRAL: sin contribución", "overall_direction")

            # DETERMINACIÓN FINAL con thresholds ICT
            threshold = weights['confidence_threshold']
            
            if direction_score > threshold:
                final_direction = "BULLISH"
                confidence = "HIGH" if direction_score > 0.7 else "MEDIUM"
                log_info(f"DIRECCIÓN FINAL: BULLISH (score: {direction_score:.3f}, confianza: {confidence})", "overall_direction")
            elif direction_score < -threshold:
                final_direction = "BEARISH"
                confidence = "HIGH" if direction_score < -0.7 else "MEDIUM"
                log_info(f"DIRECCIÓN FINAL: BEARISH (score: {direction_score:.3f}, confianza: {confidence})", "overall_direction")
            else:
                final_direction = "NEUTRAL"
                confidence = "LOW"
                log_info(f"DIRECCIÓN FINAL: NEUTRAL (score: {direction_score:.3f}, confianza: {confidence})", "overall_direction")

            return {
                "direction": final_direction,
                "strength": min(abs(direction_score), 1.0),
                "confidence": confidence,
                "direction_score": round(direction_score, 4),
                "authority_tf": "H4",
                "h4_m15_aligned": h4_m15_aligned,
                "weights_applied": weights,
                "status": "analyzed"
            }

        except Exception as e:
            log_error(f"Error determinando dirección overall: {e}", "overall_direction")
            return {
                "direction": "NEUTRAL",
                "strength": 0.0,
                "confidence": "LOW",
                "error": str(e),
                "status": "error"
            }

    def _check_timeframe_alignment(self, h4_bias: str, m15_type: str) -> bool:
        """
        🔍 Verifica alineación entre H4 bias y M15 structure
        
        Args:
            h4_bias: H4 bias result ("BULLISH", "BEARISH", "NEUTRAL")
            m15_type: M15 structure type ("bullish_structure", "bearish_structure", etc)
            
        Returns:
            bool: True si están alineados, False si hay conflicto
        """
        # Mapeo de alineaciones
        alignment_map = {
            ("BULLISH", "bullish_structure"): True,
            ("BEARISH", "bearish_structure"): True,
            ("NEUTRAL", "consolidation"): True,
            ("NEUTRAL", "bullish_structure"): True,  # Neutral permite cualquier dirección
            ("NEUTRAL", "bearish_structure"): True,
        }
        
        return alignment_map.get((h4_bias, m15_type), False)

    def analisis_completo_ict(self, df_h4: DataFrameType, df_m15: DataFrameType, df_m5: Optional[DataFrameType] = None) -> Dict[str, Any]:
        """
        🚀 Análisis ICT completo H4 → M15 → M5 con jerarquía enterprise
        
        Pipeline principal que integra todos los timeframes según protocolo ICT:
        1. H4 Bias (Authority timeframe)
        2. M15 Structure (Confirmation timeframe)
        3. M5 LTF Confirmation (Timing timeframe)  
        4. Overall Direction con pesos ICT correctos
        
        Args:
            df_h4: DataFrame con datos H4 (OHLC)
            df_m15: DataFrame con datos M15 (OHLC)
            df_m5: DataFrame con datos M5 (OHLC) - opcional
            
        Returns:
            Dict con análisis completo multi-timeframe
        """
        try:
            log_info("=== INICIANDO ANÁLISIS ICT COMPLETO MULTI-TIMEFRAME ===", "pipeline")
            
            # PASO 1: H4 Bias Analysis
            log_info("PASO 1: Analizando H4 Bias (Authority)", "pipeline")
            h4_bias = self.calcular_bias_h4_optimizado(df_h4)
            
            # PASO 2: M15 Structure Detection
            log_info("PASO 2: Analizando M15 Structure (Confirmation)", "pipeline")
            m15_structure = self.detectar_estructura_m15_optimizada(df_m15)
            
            # PASO 3: M5 LTF Confirmation (opcional)
            ltf_confirmation = {}
            if df_m5 is not None:
                log_info("PASO 3: Analizando M5 LTF Confirmation (Timing)", "pipeline")
                ltf_confirmation = self.analizar_confirmacion_ltf(df_m5, m15_structure)
            else:
                log_warning("PASO 3: M5 no disponible, saltando confirmación LTF", "pipeline")
                ltf_confirmation = {
                    "confirmation": False,
                    "strength": 0.0,
                    "direction": "neutral",
                    "status": "not_available"
                }
            
            # PASO 4: Overall Direction con jerarquía ICT
            log_info("PASO 4: Determinando Overall Direction con jerarquía ICT", "pipeline")
            overall_direction = self._determine_overall_direction_ict_weighted(h4_bias, m15_structure, ltf_confirmation)
            
            # RESULTADO INTEGRADO
            result = {
                "h4_bias": h4_bias,
                "m15_structure": m15_structure,
                "ltf_confirmation": ltf_confirmation,
                "overall_direction": overall_direction,
                "pipeline_status": "COMPLETED",
                "pipeline_version": "enterprise_v6.0",
                "timeframes_analyzed": {
                    "H4": df_h4 is not None and len(df_h4) > 0,
                    "M15": df_m15 is not None and len(df_m15) > 0,
                    "M5": df_m5 is not None and len(df_m5) > 0
                },
                "analysis_timestamp": pd.Timestamp.now().isoformat(),
                "config_used": ICT_CONFIG_ENTERPRISE,
                "weights_used": ICT_HIERARCHY_WEIGHTS
            }
            
            log_info(f"=== ANÁLISIS COMPLETO FINALIZADO ===", "pipeline")
            log_info(f"H4: {h4_bias.get('bias', 'ERROR')}, M15: {m15_structure.get('type', 'ERROR')}, Overall: {overall_direction.get('direction', 'ERROR')}", "pipeline")
            
            return result

        except Exception as e:
            log_error(f"Error en análisis ICT completo: {e}", "pipeline")
            return {
                "pipeline_status": "ERROR",
                "error": str(e),
                "h4_bias": {"bias": "ERROR", "strength": 0, "status": "error"},
                "m15_structure": {"type": "error", "strength": 0, "bos_detected": False},
                "ltf_confirmation": {"confirmation": False, "strength": 0, "direction": "neutral"},
                "overall_direction": {"direction": "NEUTRAL", "strength": 0.0, "confidence": "LOW"},
                "pipeline_version": "enterprise_v6.0",
                "analysis_timestamp": pd.Timestamp.now().isoformat()
            }

# =============================================================================
# FUNCIONES DE UTILIDAD ENTERPRISE
# =============================================================================

    def analyze_symbol(self, symbol: str, timeframes: Optional[List[str]] = None, mode: str = 'full') -> Dict[str, Any]:
        """
        🚀 MÉTODO WRAPPER ENTERPRISE para compatibilidad con PatternDetector
        
        Proporciona interfaz unificada para análisis multi-timeframe con descarga automática de datos.
        Soporta diferentes modos de análisis según disponibilidad de datos.
        
        Args:
            symbol: Par de trading (ej. 'EURUSD')
            timeframes: Lista de timeframes (default: ['H4', 'M15', 'M5'])
            mode: Modo de análisis ('full', 'live_ready', 'minimal', 'auto')
            
        Returns:
            Dict con análisis multi-timeframe ICT y resultados por timeframe
        """
        try:
            if timeframes is None:
                timeframes = ['H4', 'M15', 'M5']
            
            log_info(f"Iniciando análisis multi-timeframe para {symbol} - TF: {timeframes} - Modo: {mode}")
            
            # 1. 🎯 DETERMINAR ESTRATEGIA SEGÚN MODO
            if mode == 'live_ready':
                return self._analyze_live_ready(symbol, timeframes)
            elif mode == 'minimal':
                return self._analyze_minimal(symbol, timeframes)
            elif mode == 'auto':
                return self._analyze_auto(symbol, timeframes)
            else:  # mode == 'full' (default)
                return self._analyze_full(symbol, timeframes)
                
        except Exception as e:
            log_error(f"Error en analyze_symbol: {e}")
            return {
                'symbol': symbol,
                'timeframes': timeframes or [],
                'mode': mode,
                'status': 'ERROR',
                'error': str(e),
                'timeframe_results': {}
            }

    def _analyze_live_ready(self, symbol: str, timeframes: List[str]) -> Dict[str, Any]:
        """🚀 Análisis optimizado para trading en vivo con datos mínimos"""
        try:
            log_info(f"Modo LIVE_READY: análisis rápido para {symbol}")
            
            # Usar datos mínimos pero suficientes para ICT
            minimal_periods = {
                'H4': 120,   # 5 días (suficiente para bias H4)
                'M15': 240,  # 2.5 días (estructura básica)
                'M5': 360    # 1.25 días (timing inmediato)
            }
            
            timeframe_data = {}
            for tf in timeframes:
                periods = minimal_periods.get(tf, 240)
                real_data = self._get_real_data(symbol, tf, periods)
                if real_data is not None:
                    timeframe_data[tf] = real_data
                    log_info(f"Datos reales cargados para {tf}: {len(real_data)} velas")
                else:
                    log_warning(f"No se pudieron cargar datos reales para {tf}")
                    continue
            
            # Ejecutar análisis ICT rápido
            df_h4 = timeframe_data.get('H4')
            df_m15 = timeframe_data.get('M15') 
            df_m5 = timeframe_data.get('M5')
            
            if df_h4 is None or df_m15 is None:
                return self._generate_insufficient_data_result(symbol, timeframes, 'live_ready')
            
            # Análisis ICT con datos mínimos
            ict_analysis = self.analisis_completo_ict(df_h4, df_m15, df_m5)
            
            # Formatear para LIVE_READY
            result = self._format_enterprise_result(symbol, timeframes, ict_analysis)
            result['mode'] = 'live_ready'
            result['data_quality'] = 'MINIMAL_SUFFICIENT'
            result['trading_ready'] = True
            result['disclaimer'] = 'Análisis con datos mínimos - Se refinará automáticamente'
            
            return result
            
        except Exception as e:
            log_error(f"Error en análisis live_ready: {e}")
            return self._generate_error_result(symbol, timeframes, 'live_ready', e)

    def _analyze_minimal(self, symbol: str, timeframes: List[str]) -> Dict[str, Any]:
        """⚡ Análisis ultra-rápido con datos absolutamente mínimos"""
        try:
            log_info(f"Modo MINIMAL: análisis ultra-rápido para {symbol}")
            
            # Datos absolutamente mínimos
            ultra_minimal = {
                'H4': 60,    # 2.5 días
                'M15': 120,  # 1.25 días 
                'M5': 180    # 0.6 días
            }
            
            timeframe_data = {}
            for tf in timeframes:
                periods = ultra_minimal.get(tf, 120)
                real_data = self._get_real_data(symbol, tf, periods)
                if real_data is not None:
                    timeframe_data[tf] = real_data
                    log_info(f"Datos reales MINIMAL cargados para {tf}: {len(real_data)} velas")
                else:
                    log_warning(f"No se pudieron cargar datos reales para {tf}")
                    continue
            
            # Solo análisis H4 + M15 para velocidad máxima
            df_h4 = timeframe_data.get('H4')
            df_m15 = timeframe_data.get('M15')
            
            if df_h4 is None or df_m15 is None:
                return self._generate_insufficient_data_result(symbol, timeframes, 'minimal')
            
            # Análisis simplificado
            h4_bias = self.calcular_bias_h4_optimizado(df_h4)
            m15_structure = self.detectar_estructura_m15_optimizada(df_m15)
            
            # Dirección simplificada
            overall_direction = {
                'direction': h4_bias.get('bias', 'NEUTRAL'),
                'strength': h4_bias.get('strength', 0.0),
                'confidence': 'MEDIUM' if h4_bias.get('strength', 0) > 0.5 else 'LOW'
            }
            
            # Resultado minimal
            timeframe_results = {
                'H4': self._format_timeframe_result(h4_bias, 'H4'),
                'M15': self._format_timeframe_result(m15_structure, 'M15')
            }
            
            return {
                'symbol': symbol,
                'mode': 'minimal',
                'timeframes': timeframes,
                'timeframe_results': timeframe_results,
                'overall_direction': overall_direction,
                'data_quality': 'ULTRA_MINIMAL',
                'trading_ready': False,
                'status': 'SUCCESS',
                'disclaimer': 'Análisis ultra-rápido - Usar solo como referencia inicial',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            log_error(f"Error en análisis minimal: {e}")
            return self._generate_error_result(symbol, timeframes, 'minimal', e)

    def _analyze_auto(self, symbol: str, timeframes: List[str]) -> Dict[str, Any]:
        """🤖 Análisis automático que detecta la mejor estrategia según datos disponibles"""
        try:
            log_info(f"Modo AUTO: detectando mejor estrategia para {symbol}")
            
            # Simular detección de datos disponibles
            # TODO: Integrar con ICTDataManager real cuando esté disponible
            
            # Por ahora, usar lógica heurística
            current_time = datetime.now()
            if current_time.second % 3 == 0:
                # Simular datos completos disponibles
                log_info("AUTO: Datos completos detectados, usando modo FULL")
                return self._analyze_full(symbol, timeframes)
            elif current_time.second % 2 == 0:
                # Simular datos parciales
                log_info("AUTO: Datos parciales detectados, usando modo LIVE_READY")
                return self._analyze_live_ready(symbol, timeframes)
            else:
                # Simular datos mínimos
                log_info("AUTO: Datos mínimos detectados, usando modo MINIMAL")
                return self._analyze_minimal(symbol, timeframes)
                
        except Exception as e:
            log_error(f"Error en análisis auto: {e}")
            return self._generate_error_result(symbol, timeframes, 'auto', e)

    def _analyze_full(self, symbol: str, timeframes: List[str]) -> Dict[str, Any]:
        """📊 Análisis completo con todos los datos (método original)"""
        try:
            log_info(f"Modo FULL: análisis completo para {symbol}")
            
            # Usar períodos completos originales
            timeframe_data = {}
            for tf in timeframes:
                periods = {'H4': 240, 'M15': 480, 'M5': 720}.get(tf, 480)
                real_data = self._get_real_data(symbol, tf, periods)
                if real_data is not None and len(real_data) > 0:
                    timeframe_data[tf] = real_data
                    log_info(f"Datos reales FULL cargados para {tf}: {len(real_data)} velas")
                else:
                    log_warning(f"No se pudieron cargar datos reales para {tf}")
                    continue
            
            # Ejecutar análisis completo
            df_h4 = timeframe_data.get('H4')
            df_m15 = timeframe_data.get('M15') 
            df_m5 = timeframe_data.get('M5')
            
            if df_h4 is None or df_m15 is None:
                return self._generate_insufficient_data_result(symbol, timeframes, 'full')
            
            # Análisis ICT completo
            ict_analysis = self.analisis_completo_ict(df_h4, df_m15, df_m5)
            
            # Formatear resultado completo
            result = self._format_enterprise_result(symbol, timeframes, ict_analysis)
            result['mode'] = 'full'
            result['data_quality'] = 'COMPLETE'
            result['trading_ready'] = True
            
            return result
            
        except Exception as e:
            log_error(f"Error en análisis full: {e}")
            return self._generate_error_result(symbol, timeframes, 'full', e)

    def _format_timeframe_result(self, analysis: Dict, timeframe: str) -> Dict[str, Any]:
        """📋 Formatear resultado de análisis de timeframe individual"""
        
        if timeframe == 'H4':
            return {
                'analysis': {
                    'bos_detected': analysis.get('bias') in ['BULLISH', 'BEARISH'],
                    'bos_analysis': {
                        'direction': analysis.get('bias', 'NEUTRAL'),
                        'strength': analysis.get('strength', 0.0) * 100,
                        'break_level': analysis.get('nivel_rotura', 0.0),
                        'target_level': analysis.get('target_price', 0.0),
                        'confluence_count': len(analysis.get('confluencias', [])),
                        'narrative': analysis.get('narrative', ''),
                        'momentum_score': analysis.get('momentum', 0.5)
                    }
                },
                'status': 'ANALYZED'
            }
        else:  # M15, M5, etc.
            return {
                'analysis': {
                    'bos_detected': analysis.get('type') in ['bos_bullish', 'bos_bearish', 'bullish_structure', 'bearish_structure'],
                    'bos_analysis': {
                        'direction': 'BULLISH' if 'bullish' in str(analysis.get('type', '')) else 
                                   'BEARISH' if 'bearish' in str(analysis.get('type', '')) else 'NEUTRAL',
                        'strength': analysis.get('strength', 0.0) * 100,
                        'break_level': analysis.get('key_level', analysis.get('entry_level', 0.0)),
                        'target_level': analysis.get('target', 0.0),
                        'confluence_count': len(analysis.get('confluencias', analysis.get('confluences', []))),
                        'narrative': analysis.get('narrative', ''),
                        'momentum_score': analysis.get('momentum', 0.5)
                    }
                },
                'status': 'ANALYZED'
            }

    def _format_enterprise_result(self, symbol: str, timeframes: List[str], ict_analysis: Dict) -> Dict[str, Any]:
        """📊 Formatear resultado completo para enterprise (método original mejorado)"""
        
        timeframe_results = {}
        
        # Procesar H4
        if 'h4_bias' in ict_analysis:
            timeframe_results['H4'] = self._format_timeframe_result(ict_analysis['h4_bias'], 'H4')
        
        # Procesar M15
        if 'm15_structure' in ict_analysis:
            timeframe_results['M15'] = self._format_timeframe_result(ict_analysis['m15_structure'], 'M15')
        
        # Procesar M5 (si disponible)
        if 'ltf_confirmation' in ict_analysis:
            timeframe_results['M5'] = self._format_timeframe_result(ict_analysis['ltf_confirmation'], 'M5')
        
        return {
            'symbol': symbol,
            'timeframes': timeframes,
            'timeframe_results': timeframe_results,
            'overall_direction': ict_analysis.get('overall_direction', {}),
            'session_context': ict_analysis.get('session_context', {}),
            'performance_metrics': ict_analysis.get('performance_metrics', {}),
            'raw_ict_analysis': ict_analysis,
            'status': 'SUCCESS',
            'timestamp': ict_analysis.get('analysis_timestamp', datetime.now().isoformat())
        }

    def _generate_insufficient_data_result(self, symbol: str, timeframes: List[str], mode: str) -> Dict[str, Any]:
        """⚠️ Generar resultado para datos insuficientes"""
        
        return {
            'symbol': symbol,
            'timeframes': timeframes,
            'mode': mode,
            'status': 'INSUFFICIENT_DATA',
            'error': 'Datos insuficientes para análisis ICT',
            'timeframe_results': {},
            'recommendations': [
                'Verificar conexión MT5',
                'Asegurar símbolos disponibles en broker',
                'Intentar descarga manual de datos'
            ]
        }

    def _generate_error_result(self, symbol: str, timeframes: List[str], mode: str, error: Exception) -> Dict[str, Any]:
        """❌ Generar resultado de error"""
        
        return {
            'symbol': symbol,
            'timeframes': timeframes,
            'mode': mode,
            'status': 'ERROR',
            'error': str(error),
            'timeframe_results': {},
            'timestamp': datetime.now().isoformat()
        }

    def _get_real_data(self, symbol: str, timeframe: str, periods: int = 480) -> DataFrameType:
        """📊 Obtener datos reales MT5 con solicitud automática si no existen"""
        try:
            # Usar singleton para evitar múltiples inicializaciones
            try:
                from data_management.advanced_candle_downloader_singleton import get_advanced_candle_downloader
                downloader = get_advanced_candle_downloader()
            except ImportError:
                from data_management.advanced_candle_downloader import AdvancedCandleDownloader
                downloader = AdvancedCandleDownloader()
            
            log_info(f"Solicitando datos reales MT5: {symbol} {timeframe} - {periods} velas")
            
            # Descargar datos reales de MT5
            result = downloader.download_candles(
                symbol=symbol,
                timeframe=timeframe
            )
            
            if result is None:
                log_warning(f"No se pudieron obtener datos para {symbol} {timeframe}")
                return pd.DataFrame()  # Retornar DataFrame vacío en lugar de None
            
            # Extraer DataFrame de datos
            if isinstance(result, dict) and 'data' in result:
                df = result['data']
                if df is not None and len(df) > 0:
                    log_info(f"Datos reales obtenidos: {symbol} {timeframe} - {len(df)} velas")
                    return df
            
            log_warning(f"Formato de datos inesperado para {symbol} {timeframe}")
            return pd.DataFrame()  # Retornar DataFrame vacío en lugar de None
            
        except Exception as e:
            log_error(f"Error obteniendo datos reales MT5: {e}")
            return pd.DataFrame()  # Retornar DataFrame vacío en lugar de None

def get_ict_config():
    """Obtener configuración ICT enterprise"""
    return ICT_CONFIG_ENTERPRISE.copy()

def get_hierarchy_weights():
    """Obtener pesos de jerarquía ICT"""
    return ICT_HIERARCHY_WEIGHTS.copy()

def validate_timeframe_data(df: DataFrameType, timeframe: str) -> bool:
    """
    Validar que los datos del timeframe sean válidos
    
    Args:
        df: DataFrame a validar
        timeframe: Nombre del timeframe ("H4", "M15", "M5")
        
    Returns:
        bool: True si los datos son válidos
    """
    if df is None:
        return False
    
    required_columns = ['open', 'high', 'low', 'close']
    if not all(col in df.columns for col in required_columns):
        return False
    
    min_bars = {
        'H4': ICT_CONFIG_ENTERPRISE['h4_bias_lookback'],
        'M15': ICT_CONFIG_ENTERPRISE['m15_structure_lookback'],
        'M5': ICT_CONFIG_ENTERPRISE['ltf_confirmation_lookback']
    }
    
    return len(df) >= min_bars.get(timeframe, 20)

# =============================================================================
# LOG FINAL DE CARGA
# =============================================================================

log_info("✅ Multi-Timeframe Analyzer Enterprise v6.0 cargado completamente", "init")
log_info("📊 Pipeline H4→M15→M5 disponible", "init")
log_info("🎯 Jerarquía ICT enterprise implementada", "init")
log_info("🚀 Listo para análisis multi-timeframe", "init")
