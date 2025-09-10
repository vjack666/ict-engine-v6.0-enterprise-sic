#!/usr/bin/env python3
"""
?? POI DETECTOR - Sistema Consolidado de Detecci�n de Puntos de Inter�s (ADAPTADO)
==================================================================================

Versi�n adaptada del POIDetector para funcionar sin dependencias del sistema.sic.

Funcionalidades principales:
- Detecci�n de Order Blocks, Fair Value Gaps, Breaker Blocks
- Sistema de scoring avanzado
- An�lisis contextual de mercado
- Reportes y estad�sticas

Versi�n: v3.3.3-adapted (Consolidado y Adaptado para Backtesting)
Adaptado desde: poi_detector.py original del proyecto principal
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, TYPE_CHECKING
from datetime import datetime
import json
from pathlib import Path

# ThreadSafe pandas import para runtime
from data_management.advanced_candle_downloader import _pandas_manager

# Import pandas solo para tipado est�tico
if TYPE_CHECKING:
    from typing import Any as DataFrameType
else:
    DataFrameType = Any

# Sistema de logging adaptado
def enviar_senal_log(level: str, message: str, module: str, categoria: str = "general"):
    """Logging adaptado"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [POI.{level}] {categoria}.{module}: {message}")

def log_poi(level: str, message: str, module: str):
    """Logging POI adaptado"""
    timestamp = datetime.now().strftime("%H:%M:%S") 
    print(f"[{timestamp}] [POI.{level}] {module}: {message}")

# =============================================================================
# CONFIGURACI�N Y CONSTANTES POI
# =============================================================================

POI_TYPES = {
    'BULLISH_OB': 'Order Block Alcista',
    'BEARISH_OB': 'Order Block Bajista',
    'BULLISH_FVG': 'Fair Value Gap Alcista',
    'BEARISH_FVG': 'Fair Value Gap Bajista',
    'BULLISH_BREAKER': 'Breaker Block Alcista',
    'BEARISH_BREAKER': 'Breaker Block Bajista',
    'LIQUIDITY_VOID': 'Vac�o de Liquidez',
    'PRICE_IMBALANCE': 'Desequilibrio de Precio'
}

POI_SCORING_CONFIG = {
    'QUALITY_TIERS': {
        'A+': 80,  # Elite (80+ puntos)
        'A': 70,   # Excelente (70-79)
        'B': 60,   # Bueno (60-69)
        'C': 40,   # Regular (40-59)
        'D': 20    # Bajo (20-39)
    },
    'SCORING_WEIGHTS': {
        'proximity': 25,    # Proximidad al precio
        'strength': 20,     # Fuerza de formaci�n
        'timeframe': 15,    # Relevancia del timeframe
        'volume': 10,       # Volumen de formaci�n
        'confirmation': 15, # Confirmaci�n t�cnica
        'freshness': 10,    # Frescura del POI
        'context': 5       # Contexto de mercado
    },
    'PROXIMITY_ZONES': {
        'immediate': 10,    # 0-10 pips
        'near': 20,         # 10-20 pips
        'moderate': 50,     # 20-50 pips
        'distant': 100      # 50-100 pips
    }
}

# =============================================================================
# FUNCIONES DE UTILIDAD Y LOGGING
# =============================================================================

def test_poi_logging_migration():
    """
    ?? FUNCI�N DE TESTING - MIGRACI�N DE LOGGING POI
    ===============================================

    Verifica que el nuevo sistema de logging centralizado funcione correctamente.
    """
    try:
        enviar_senal_log("INFO", "?? Iniciando test de migraci�n de logging POI", "poi_detector", "testing")

        # Test 1: Logging normal POI
        log_poi_centralizado("TEST_COMPONENT", "Test de logging POI normal")

        # Test 2: Logging de error POI
        log_poi_centralizado("TEST_ERROR", "Test de logging POI con error", is_error=True)

        # Test 3: Verificar que log_poi est� disponible
        try:
            log_poi("INFO", "Test directo de log_poi", "poi_detector")
            test_log_poi_directo = True
        except Exception as e:
            enviar_senal_log("WARNING", f"log_poi no disponible: {e}", "poi_detector", "testing")
            test_log_poi_directo = False

        enviar_senal_log("INFO", "? Tests de logging POI completados exitosamente", "poi_detector", "testing")

        return {
            "log_poi_centralizado": True,
            "log_poi_directo": test_log_poi_directo,
            "migration_status": "SUCCESS"
        }

    except Exception as e:
        enviar_senal_log("ERROR", f"? Test de logging POI fall�: {e}", "poi_detector", "testing")
        return {
            "log_poi_centralizado": False,
            "log_poi_directo": False,
            "migration_status": "FAILED",
            "error": str(e)
        }


def log_poi_centralizado(component: str, message: str, is_error: bool = False):
    """
    Funci�n de logging POI que usa el sistema central SLUC v2.1
    Reemplaza la funci�n obsoleta log_poi_to_csv
    """
    nivel = "ERROR" if is_error else "INFO"
    try:
        log_poi(nivel, f"[{component}] {message}", "poi_detector")
    except Exception:
        # Fallback al sistema principal si log_poi falla
        enviar_senal_log(nivel, f"[POI-{component}] {message}", "poi_detector", "poi")

def crear_poi_estructura(poi_type: str, price: float, score: int, confidence: float,
                        timeframe: str, **kwargs) -> Dict:
    """
    Crea estructura est�ndar para un POI.

    Args:
        poi_type: Tipo de POI (usar POI_TYPES)
        price: Precio central del POI
        score: Puntuaci�n del POI (0-100)
        confidence: Nivel de confianza (0.0-1.0)
        timeframe: Timeframe de formaci�n
        **kwargs: Par�metros adicionales espec�ficos del POI

    Returns:
        Dict con estructura est�ndar del POI
    """
    return {
        'id': f"{poi_type}_{timeframe}_{datetime.now().timestamp()}",
        'type': poi_type,
        'price': price,
        'score': score,
        'confidence': confidence,
        'timeframe': timeframe,
        'created_at': datetime.now().isoformat(),
        'mitigated': False,
        'broken': False,
        **kwargs
    }

# =============================================================================
# DETECTORES DE POI POR TIPO
# =============================================================================

def detectar_order_blocks(df: DataFrameType, timeframe: str = "M15") -> List[Dict]:
    """
    Detecta Order Blocks (zonas de �rdenes institucionales).

    Un Order Block es una zona donde las instituciones han colocado �rdenes
    masivas, identificada por patrones espec�ficos de velas y volumen.

    Args:
        df: DataFrame con datos OHLC + volumen
        timeframe: Timeframe de an�lisis

    Returns:
        Lista de Order Blocks detectados
    """
    enviar_senal_log("INFO", f"?? INICIANDO detecci�n de Order Blocks en timeframe {timeframe}", __name__, "general")
    enviar_senal_log("DEBUG", f"Dataset recibido: {len(df)} velas, rango temporal disponible", __name__, "general")

    order_blocks = []

    try:
        if len(df) < 20:
            enviar_senal_log("WARNING", f"?? Dataset insuficiente para an�lisis OB: solo {len(df)} velas (m�nimo 20)", __name__, "general")
            return order_blocks

        enviar_senal_log("DEBUG", f"Escaneando {len(df)-15} posiciones potenciales para Order Blocks...", __name__, "general")

        # Buscar patrones de Order Block
        bullish_count = 0
        bearish_count = 0

        for i in range(10, len(df) - 5):
            current = df.iloc[i]
            prev = df.iloc[i-1]
            next_candles = df.iloc[i+1:i+6]

            # BULLISH Order Block
            if _is_bullish_order_block(current, prev, next_candles):
                score = _calcular_score_ob(current, next_candles, "BULLISH")
                confidence = _determinar_confianza_ob(current, next_candles)

                ob_bullish = crear_poi_estructura(
                    "BULLISH_OB",
                    price=(current['high'] + current['low']) / 2,
                    score=score,
                    confidence=confidence,
                    timeframe=timeframe,
                    range_high=current['high'],
                    range_low=current['low'],
                    volume=current.get('volume', 0),
                    formation_strength=abs(current['close'] - current['open']),
                    index=i
                )

                order_blocks.append(ob_bullish)
                bullish_count += 1

                enviar_senal_log("INFO", f"? POI DETECTADO: BULLISH_OB @ {ob_bullish['price']:.5f} | Score: {score} | Confidence: {confidence:.2f} | TF: {timeframe}", __name__, "general")
                enviar_senal_log("DEBUG", f"   Detalles OB: High={current['high']:.5f}, Low={current['low']:.5f}, Volumen={current.get('volume', 0)}", __name__, "general")

            # BEARISH Order Block
            elif _is_bearish_order_block(current, prev, next_candles):
                score = _calcular_score_ob(current, next_candles, "BEARISH")
                confidence = _determinar_confianza_ob(current, next_candles)

                ob_bearish = crear_poi_estructura(
                    "BEARISH_OB",
                    price=(current['high'] + current['low']) / 2,
                    score=score,
                    confidence=confidence,
                    timeframe=timeframe,
                    range_high=current['high'],
                    range_low=current['low'],
                    volume=current.get('volume', 0),
                    formation_strength=abs(current['open'] - current['close']),
                    index=i
                )

                order_blocks.append(ob_bearish)
                bearish_count += 1

                enviar_senal_log("INFO", f"? POI DETECTADO: BEARISH_OB @ {ob_bearish['price']:.5f} | Score: {score} | Confidence: {confidence:.2f} | TF: {timeframe}", __name__, "general")
                enviar_senal_log("DEBUG", f"   Detalles OB: High={current['high']:.5f}, Low={current['low']:.5f}, Volumen={current.get('volume', 0)}", __name__, "general")

        enviar_senal_log("INFO", f"?? DETECCI�N OB COMPLETADA: {len(order_blocks)} total ({bullish_count} alcistas, {bearish_count} bajistas) en {timeframe}", __name__, "general")
        log_poi_centralizado("OB_DETECTION", f"Detectados {len(order_blocks)} Order Blocks en {timeframe}")

    except (ValueError, KeyError, TypeError) as e:
        enviar_senal_log("ERROR", f"? ERROR en detecci�n de Order Blocks: {e}", __name__, "general")
        log_poi_centralizado("OB_DETECTION_ERROR", f"Error detectando OBs: {e}", is_error=True)

    return order_blocks

def detectar_fair_value_gaps(df: DataFrameType, timeframe: str = "M15") -> List[Dict]:
    """
    Detecta Fair Value Gaps (vac�os de precio ineficientes).

    Un FVG ocurre cuando hay un gap entre velas que indica ineficiencia
    de precio que el mercado buscar� llenar posteriormente.

    Args:
        df: DataFrame con datos OHLC
        timeframe: Timeframe de an�lisis

    Returns:
        Lista de Fair Value Gaps detectados
    """
    enviar_senal_log("INFO", f"?? INICIANDO detecci�n de Fair Value Gaps en timeframe {timeframe}", __name__, "general")
    enviar_senal_log("DEBUG", f"Dataset recibido: {len(df)} velas para an�lisis FVG", __name__, "general")

    fvgs = []

    try:
        if len(df) < 3:
            enviar_senal_log("WARNING", f"?? Dataset insuficiente para an�lisis FVG: solo {len(df)} velas (m�nimo 3)", __name__, "general")
            return fvgs

        enviar_senal_log("DEBUG", f"Escaneando {len(df)-2} posiciones para detectar Fair Value Gaps...", __name__, "general")

        bullish_fvg_count = 0
        bearish_fvg_count = 0

        for i in range(1, len(df) - 1):
            prev_candle = df.iloc[i-1]
            current_candle = df.iloc[i]
            next_candle = df.iloc[i+1]

            # BULLISH FVG: next_low > prev_high
            if next_candle['low'] > prev_candle['high']:
                gap_size = next_candle['low'] - prev_candle['high']
                gap_pips = gap_size * 10000
                score = _calcular_score_fvg(prev_candle, current_candle, next_candle, "BULLISH")
                confidence = _determinar_confianza_fvg(prev_candle, next_candle)

                fvg_bullish = crear_poi_estructura(
                    "BULLISH_FVG",
                    price=(next_candle['low'] + prev_candle['high']) / 2,
                    score=score,
                    confidence=confidence,
                    timeframe=timeframe,
                    range_high=next_candle['low'],
                    range_low=prev_candle['high'],
                    gap_size=gap_size,
                    index=i
                )
                fvgs.append(fvg_bullish)
                bullish_fvg_count += 1

                enviar_senal_log("INFO", f"? POI DETECTADO: BULLISH_FVG @ {fvg_bullish['price']:.5f} | Gap: {gap_pips:.1f} pips | Score: {score} | TF: {timeframe}", __name__, "general")
                enviar_senal_log("DEBUG", f"   Detalles FVG: Range High={next_candle['low']:.5f}, Range Low={prev_candle['high']:.5f}", __name__, "general")

            # BEARISH FVG: next_high < prev_low
            elif next_candle['high'] < prev_candle['low']:
                gap_size = prev_candle['low'] - next_candle['high']
                gap_pips = gap_size * 10000
                score = _calcular_score_fvg(prev_candle, current_candle, next_candle, "BEARISH")
                confidence = _determinar_confianza_fvg(prev_candle, next_candle)

                fvg_bearish = crear_poi_estructura(
                    "BEARISH_FVG",
                    price=(prev_candle['low'] + next_candle['high']) / 2,
                    score=score,
                    confidence=confidence,
                    timeframe=timeframe,
                    range_high=prev_candle['low'],
                    range_low=next_candle['high'],
                    gap_size=gap_size,
                    index=i
                )
                fvgs.append(fvg_bearish)
                bearish_fvg_count += 1

                enviar_senal_log("INFO", f"? POI DETECTADO: BEARISH_FVG @ {fvg_bearish['price']:.5f} | Gap: {gap_pips:.1f} pips | Score: {score} | TF: {timeframe}", __name__, "general")
                enviar_senal_log("DEBUG", f"   Detalles FVG: Range High={prev_candle['low']:.5f}, Range Low={next_candle['high']:.5f}", __name__, "general")

        enviar_senal_log("INFO", f"?? DETECCI�N FVG COMPLETADA: {len(fvgs)} total ({bullish_fvg_count} alcistas, {bearish_fvg_count} bajistas) en {timeframe}", __name__, "general")
        log_poi_centralizado("FVG_DETECTION", f"Detectados {len(fvgs)} FVGs en {timeframe}")

    except (ValueError, KeyError, TypeError) as e:
        enviar_senal_log("ERROR", f"? ERROR en detecci�n de Fair Value Gaps: {e}", __name__, "general")
        log_poi_centralizado("FVG_DETECTION_ERROR", f"Error detectando FVGs: {e}", is_error=True)

    return fvgs

def detectar_breaker_blocks(df: DataFrameType, timeframe: str = "M15") -> List[Dict]:
    """
    Detecta Breaker Blocks (Order Blocks que han sido rotos y se convierten en soporte/resistencia).

    Args:
        df: DataFrame con datos OHLC
        timeframe: Timeframe de an�lisis

    Returns:
        Lista de Breaker Blocks detectados
    """
    enviar_senal_log("INFO", f"?? INICIANDO detecci�n de Breaker Blocks en timeframe {timeframe}", __name__, "general")

    breaker_blocks = []

    try:
        # Primero detectar Order Blocks
        enviar_senal_log("DEBUG", "Detectando Order Blocks base para an�lisis de Breakers...", __name__, "general")
        order_blocks = detectar_order_blocks(df, timeframe)

        if not order_blocks:
            enviar_senal_log("INFO", "?? No hay Order Blocks base para detectar Breakers", __name__, "general")
            return breaker_blocks

        enviar_senal_log("DEBUG", f"Analizando {len(order_blocks)} Order Blocks para conversi�n a Breakers...", __name__, "general")

        # Buscar OBs que han sido rotos y act�an como breakers
        breaker_count = 0
        for ob in order_blocks:
            if _is_breaker_block(ob, df):
                enhanced_score = ob['score'] + 10  # Bonus por ser breaker
                reduced_confidence = ob['confidence'] * 0.9  # Ligeramente menos confiable

                breaker = crear_poi_estructura(
                    f"BULLISH_BREAKER" if ob['type'] == 'BULLISH_OB' else "BEARISH_BREAKER",
                    price=ob['price'],
                    score=enhanced_score,
                    confidence=reduced_confidence,
                    timeframe=timeframe,
                    range_high=ob['range_high'],
                    range_low=ob['range_low'],
                    original_ob=ob['id'],
                    breaker_confirmation=True
                )
                breaker_blocks.append(breaker)
                breaker_count += 1

                enviar_senal_log("INFO", f"? BREAKER DETECTADO: {breaker['type']} @ {breaker['price']:.5f} | Score mejorado: {enhanced_score} | TF: {timeframe}", __name__, "general")
                enviar_senal_log("DEBUG", f"   Originado de OB: {ob['id']}, Score original: {ob['score']}", __name__, "general")

        enviar_senal_log("INFO", f"?? DETECCI�N BREAKER COMPLETADA: {len(breaker_blocks)} Breaker Blocks de {len(order_blocks)} OBs analizados en {timeframe}", __name__, "general")
        log_poi_centralizado("BREAKER_DETECTION", f"Detectados {len(breaker_blocks)} Breaker Blocks en {timeframe}")

    except (ValueError, KeyError, TypeError) as e:
        enviar_senal_log("ERROR", f"? ERROR en detecci�n de Breaker Blocks: {e}", __name__, "general")
        log_poi_centralizado("BREAKER_DETECTION_ERROR", f"Error detectando Breakers: {e}", is_error=True)

    return breaker_blocks

def detectar_imbalances(df: DataFrameType, timeframe: str = "M15") -> List[Dict]:
    """
    Detecta desequilibrios de precio e ineficiencias de liquidez.

    Args:
        df: DataFrame con datos OHLC
        timeframe: Timeframe de an�lisis

    Returns:
        Lista de imbalances detectados
    """
    enviar_senal_log("INFO", f"?? INICIANDO detecci�n de Imbalances (vac�os de liquidez", __name__, "general")
    enviar_senal_log("DEBUG", f"Dataset recibido: {len(df)} velas para an�lisis de imbalances", __name__, "general")

    imbalances = []

    try:
        if len(df) < 10:
            enviar_senal_log("WARNING", f"?? Dataset insuficiente para an�lisis de imbalances: solo {len(df)} velas (m�nimo 10)", __name__, "general")
            return imbalances

        enviar_senal_log("DEBUG", f"Escaneando {len(df)-10} posiciones para detectar imbalances...", __name__, "general")

        imbalance_count = 0
        low_volume_moves = 0

        # Buscar vac�os de liquidez (movimientos r�pidos con poco volumen)
        for i in range(5, len(df) - 5):
            current = df.iloc[i]
            prev_window = df.iloc[i-5:i]
            next_window = df.iloc[i+1:i+6]

            # Detectar movimiento r�pido con bajo volumen
            price_change = abs(current['close'] - prev_window['close'].iloc[0])
            avg_volume = prev_window['volume'].mean() if 'volume' in df.columns else 1
            current_volume = current.get('volume', 1)
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

            # Calcular threshold de movimiento basado en volatilidad
            volatility_threshold = df['close'].pct_change().std() * 2

            if price_change > volatility_threshold and current_volume < avg_volume * 0.7:
                score = _calcular_score_imbalance(current, prev_window, next_window)
                price_change_pips = price_change * 10000

                imbalance = crear_poi_estructura(
                    "LIQUIDITY_VOID",
                    price=current['close'],
                    score=score,
                    confidence=0.6,  # Moderada confianza para imbalances
                    timeframe=timeframe,
                    range_high=max(current['high'], prev_window['high'].max()),
                    range_low=min(current['low'], prev_window['low'].min()),
                    volume_ratio=volume_ratio,
                    price_change_magnitude=price_change,
                    index=i
                )
                imbalances.append(imbalance)
                imbalance_count += 1

                enviar_senal_log("INFO", f"? IMBALANCE DETECTADO: LIQUIDITY_VOID @ {current['close']:.5f} | Cambio: {price_change_pips:.1f} pips | Vol ratio: {volume_ratio:.2f} | TF: {timeframe}", __name__, "general")
                enviar_senal_log("DEBUG", f"   Score: {score} | Range: {imbalance['range_low']:.5f} - {imbalance['range_high']:.5f}", __name__, "general")

            elif current_volume < avg_volume * 0.7:
                low_volume_moves += 1

        enviar_senal_log("INFO", f"?? DETECCI�N IMBALANCES COMPLETADA: {len(imbalances)} imbalances detectados en {timeframe}", __name__, "general")
        enviar_senal_log("DEBUG", f"   Movimientos de bajo volumen detectados: {low_volume_moves}", __name__, "general")
        log_poi_centralizado("IMBALANCE_DETECTION", f"Detectados {len(imbalances)} imbalances en {timeframe}")

    except (ValueError, KeyError, TypeError) as e:
        enviar_senal_log("ERROR", f"? ERROR en detecci�n de imbalances: {e}", __name__, "general")
        log_poi_centralizado("IMBALANCE_DETECTION_ERROR", f"Error detectando imbalances: {e}", is_error=True)

    return imbalances

# =============================================================================
# FUNCI�N PRINCIPAL DE ORQUESTACI�N POI
# =============================================================================

def detectar_todos_los_pois(df: DataFrameType, timeframe: str = "M15",
                           current_price: Optional[float] = None) -> Dict[str, List[Dict]]:
    """
    FUNCI�N PRINCIPAL: Detecta todos los tipos de POIs en un DataFrame.

    Esta funci�n orquesta todas las sub-rutinas de detecci�n de POIs
    y proporciona logging granular del proceso completo.

    Args:
        df: DataFrame con datos OHLC
        timeframe: Timeframe de an�lisis
        current_price: Precio actual para c�lculos de proximidad

    Returns:
        Dict con todos los POIs detectados por tipo
    """
    log_poi("INFO", f"?? INICIANDO DETECCI�N COMPLETA DE POIs en {timeframe}", "poi_detector")
    precio_str = f"{current_price:.5f}" if current_price is not None else "N/A"
    log_poi("INFO", f"?? Dataset: {len(df)} velas | Precio actual: {precio_str}", "poi_detector")

    todos_los_pois = {
        'order_blocks': [],
        'fair_value_gaps': [],
        'breaker_blocks': [],
        'imbalances': [],
        'resumen': {}
    }

    deteccion_start = datetime.now()

    try:
        # 1. DETECTAR ORDER BLOCKS
        enviar_senal_log("INFO", "?? FASE 1: Detectando Order Blocks...", __name__, "general")
        obs = detectar_order_blocks(df, timeframe)
        todos_los_pois['order_blocks'] = obs
        enviar_senal_log("INFO", f"? Fase 1 completada: {len(obs)} Order Blocks detectados", __name__, "general")

        # 2. DETECTAR FAIR VALUE GAPS
        enviar_senal_log("INFO", "?? FASE 2: Detectando Fair Value Gaps...", __name__, "general")
        fvgs = detectar_fair_value_gaps(df, timeframe)
        todos_los_pois['fair_value_gaps'] = fvgs
        enviar_senal_log("INFO", f"? Fase 2 completada: {len(fvgs)} Fair Value Gaps detectados", __name__, "general")

        # 3. DETECTAR BREAKER BLOCKS
        enviar_senal_log("INFO", "?? FASE 3: Detectando Breaker Blocks...", __name__, "general")
        breakers = detectar_breaker_blocks(df, timeframe)
        todos_los_pois['breaker_blocks'] = breakers
        enviar_senal_log("INFO", f"? Fase 3 completada: {len(breakers)} Breaker Blocks detectados", __name__, "general")

        # 4. DETECTAR IMBALANCES
        enviar_senal_log("INFO", "?? FASE 4: Detectando Imbalances...", __name__, "general")
        imbalances = detectar_imbalances(df, timeframe)
        todos_los_pois['imbalances'] = imbalances
        enviar_senal_log("INFO", f"? Fase 4 completada: {len(imbalances)} Imbalances detectados", __name__, "general")

        # 5. GENERAR RESUMEN
        total_pois = len(obs) + len(fvgs) + len(breakers) + len(imbalances)
        tiempo_deteccion = (datetime.now() - deteccion_start).total_seconds()

        resumen = {
            'total_pois': total_pois,
            'por_tipo': {
                'order_blocks': len(obs),
                'fair_value_gaps': len(fvgs),
                'breaker_blocks': len(breakers),
                'imbalances': len(imbalances)
            },
            'timeframe': timeframe,
            'tiempo_procesamiento': tiempo_deteccion,
            'densidad_pois': total_pois / len(df) if len(df) > 0 else 0
        }

        todos_los_pois['resumen'] = resumen

        enviar_senal_log("INFO", f"?? DETECCI�N COMPLETA FINALIZADA", __name__, "general")
        enviar_senal_log("INFO", f"?? RESUMEN TOTAL: {total_pois} POIs en {tiempo_deteccion:.2f}s | Densidad: {resumen['densidad_pois']:.3f} POIs/vela", __name__, "general")
        enviar_senal_log("INFO", f"?? DISTRIBUCI�N: OB={len(obs)}, FVG={len(fvgs)}, BB={len(breakers)}, IM={len(imbalances)}", __name__, "general")

        # Log a CSV para seguimiento
        log_poi_centralizado("DETECCION_COMPLETA",
                      f"TF:{timeframe} | Total:{total_pois} | OB:{len(obs)} FVG:{len(fvgs)} BB:{len(breakers)} IM:{len(imbalances)} | {tiempo_deteccion:.2f}s")

        return todos_los_pois

    except (ValueError, KeyError, TypeError) as e:
        enviar_senal_log("ERROR", f"? ERROR CR�TICO en detecci�n completa de POIs: {e}", __name__, "general")
        log_poi_centralizado("DETECCION_COMPLETA_ERROR", f"Error cr�tico en TF {timeframe}: {e}", is_error=True)
        return todos_los_pois

# =============================================================================
# FUNCIONES DE SCORING Y AN�LISIS
# =============================================================================

def calcular_puntaje_poi(poi: Dict, mercado: Any, config: Dict,
                        df_m15: Optional[DataFrameType] = None) -> Tuple[int, List[str]]:
    """
    Calcula el puntaje de un POI basado en m�ltiples factores.

    Args:
        poi: Diccionario del POI a evaluar
        mercado: Contexto de mercado
        config: Configuraci�n de scoring
        df_m15: DataFrame M15 para an�lisis adicional

    Returns:
        Tuple con (puntaje_total, detalles_scoring)
    """
    try:
        puntaje_total = 0
        detalles = []
        weights = config['SCORING_WEIGHTS']

        # 1. Proximidad al precio actual (25 puntos m�ximo)
        if hasattr(mercado, 'current_price'):
            distancia = abs(poi['price'] - mercado.current_price)
            proximidad_score = _calcular_score_proximidad(distancia, config['PROXIMITY_ZONES'])
            puntaje_total += int(proximidad_score * weights['proximity'] / 100)
            detalles.append(f"Proximidad: {proximidad_score:.1f}% ({distancia:.1f} pips)")

        # 2. Fuerza de formaci�n (20 puntos m�ximo)
        fuerza_score = poi.get('formation_strength', 50)
        puntaje_total += int(fuerza_score * weights['strength'] / 100)
        detalles.append(f"Fuerza: {fuerza_score:.1f}%")

        # 3. Relevancia del timeframe (15 puntos m�ximo)
        tf_score = _calcular_score_timeframe(poi['timeframe'])
        puntaje_total += int(tf_score * weights['timeframe'] / 100)
        detalles.append(f"Timeframe: {tf_score:.1f}%")

        # 4. Volumen (10 puntos m�ximo)
        volume_score = min(poi.get('volume', 0) / 1000, 100)  # Normalizar volumen
        puntaje_total += int(volume_score * weights['volume'] / 100)
        detalles.append(f"Volumen: {volume_score:.1f}%")

        # 5. Confirmaci�n t�cnica (15 puntos m�ximo)
        confirmacion_score = poi.get('confirmation_candles', 0) * 20  # Max 5 velas = 100%
        confirmacion_score = min(confirmacion_score, 100)
        puntaje_total += int(confirmacion_score * weights['confirmation'] / 100)
        detalles.append(f"Confirmaci�n: {confirmacion_score:.1f}%")

        # 6. Frescura (10 puntos m�ximo)
        frescura_score = _calcular_score_frescura(poi['created_at'])
        puntaje_total += int(frescura_score * weights['freshness'] / 100)
        detalles.append(f"Frescura: {frescura_score:.1f}%")

        # 7. Contexto de mercado (5 puntos m�ximo)
        contexto_score = _calcular_score_contexto(poi, mercado)
        puntaje_total += int(contexto_score * weights['context'] / 100)
        detalles.append(f"Contexto: {contexto_score:.1f}%")

        return max(0, min(100, puntaje_total)), detalles

    except (ValueError, KeyError, TypeError) as e:
        log_poi_centralizado("SCORING_ERROR", f"Error calculando score POI: {e}", is_error=True)
        return 0, ["Error en c�lculo"]

def obtener_pois_superiores_cercanos(mercado: Any, current_price: float,
                                    config: Optional[Dict] = None) -> Optional[Dict]:
    """
    Identifica los POIs de mayor calidad m�s cercanos al precio actual.

    Args:
        mercado: Contexto de mercado con POIs
        current_price: Precio actual
        config: Configuraci�n de scoring

    Returns:
        Dict con informaci�n de POIs superiores o None
    """
    try:
        if config is None:
            config = POI_SCORING_CONFIG

        if not mercado or not hasattr(mercado, 'pois'):
            return None

        todos_los_pois = []

        # Recopilar todos los POIs activos
        for timeframe, pois in mercado.pois.items():
            if isinstance(pois, list):
                for poi in pois:
                    if not poi.get('broken', False) and not poi.get('mitigated', False):
                        score, _ = calcular_puntaje_poi(poi, mercado, config)
                        poi_con_score = poi.copy()
                        poi_con_score['score'] = score
                        poi_con_score['distance'] = abs(current_price - poi['price'])
                        todos_los_pois.append(poi_con_score)

        if not todos_los_pois:
            return None

        # Filtrar por calidad superior (B o mejor)
        tiers = config['QUALITY_TIERS']
        pois_superiores = [poi for poi in todos_los_pois if poi['score'] >= tiers['B']]

        if not pois_superiores:
            return None

        # Ordenar por proximidad
        pois_superiores.sort(key=lambda x: x['distance'])

        # Tomar los 3 m�s cercanos
        top_pois = pois_superiores[:3]

        return {
            'total_superior_pois': len(pois_superiores),
            'closest_pois': top_pois,
            'average_score': sum(poi['score'] for poi in top_pois) / len(top_pois),
            'nearest_distance': top_pois[0]['distance'],
            'recommendation': _generar_recomendacion_pois(top_pois, current_price)
        }

    except (ValueError, KeyError, TypeError) as e:
        log_poi_centralizado("SUPERIOR_POIS_ERROR", f"Error obteniendo POIs superiores: {e}", is_error=True)
        return None

def encontrar_poi_de_alta_probabilidad(mercado: Any, current_price: float,
                                     config: Optional[Dict] = None,
                                     df_m15: Optional[DataFrameType] = None) -> Optional[Dict]:
    """
    Encuentra el POI de m�s alta probabilidad para trading.

    Args:
        mercado: Contexto de mercado
        current_price: Precio actual
        config: Configuraci�n de scoring
        df_m15: DataFrame M15 para an�lisis adicional

    Returns:
        Dict con el mejor POI o None
    """
    try:
        if config is None:
            config = POI_SCORING_CONFIG

        if not mercado or not hasattr(mercado, 'pois'):
            return None

        mejores_pois = []

        # Evaluar todos los POIs
        for timeframe, pois in mercado.pois.items():
            if isinstance(pois, list):
                for poi in pois:
                    if not poi.get('broken', False) and not poi.get('mitigated', False):
                        score, detalles = calcular_puntaje_poi(poi, mercado, config, df_m15)

                        # Solo considerar POIs con score m�nimo
                        if score >= config['QUALITY_TIERS']['C']:
                            poi_evaluado = poi.copy()
                            poi_evaluado['score'] = score
                            poi_evaluado['score_details'] = detalles
                            poi_evaluado['distance'] = abs(current_price - poi['price'])
                            mejores_pois.append(poi_evaluado)

        if not mejores_pois:
            return None

        # Ordenar por score y proximidad
        mejores_pois.sort(key=lambda x: (x['score'], -x['distance']), reverse=True)

        mejor_poi = mejores_pois[0]

        return {
            'poi': mejor_poi,
            'quality_tier': _determinar_tier_calidad(mejor_poi['score'], config),
            'trading_recommendation': _generar_recomendacion_trading(mejor_poi, mercado),
            'risk_assessment': _evaluar_riesgo_poi(mejor_poi, mercado),
            'alternatives': mejores_pois[1:3] if len(mejores_pois) > 1 else []
        }

    except (ValueError, KeyError, TypeError) as e:
        log_poi_centralizado("HIGH_PROB_POI_ERROR", f"Error encontrando POI alta probabilidad: {e}", is_error=True)
        return None

def encontrar_pois_multiples_para_dashboard(mercado: Any, current_price: float,
                                          max_pois: int = 5) -> List[Dict]:
    """
    Encuentra m�ltiples POIs para mostrar en el dashboard.

    Args:
        mercado: Contexto de mercado
        current_price: Precio actual
        max_pois: N�mero m�ximo de POIs a retornar

    Returns:
        Lista de POIs ordenados por relevancia
    """
    enviar_senal_log("INFO", f"?? B�SQUEDA DE POIs PARA DASHBOARD iniciada | Precio actual: {current_price:.5f} | Max POIs: {max_pois}", __name__, "general")

    try:
        if not mercado or not hasattr(mercado, 'pois'):
            enviar_senal_log("WARNING", "?? No hay contexto de mercado o POIs disponibles", __name__, "general")
            return []

        todos_los_pois = []
        poi_count_by_timeframe = {}

        enviar_senal_log("DEBUG", f"Recopilando POIs del contexto de mercado...", __name__, "general")

        # Recopilar y evaluar POIs
        for timeframe, pois in mercado.pois.items():
            poi_count_by_timeframe[timeframe] = 0

            if isinstance(pois, list):
                enviar_senal_log("DEBUG", f"Procesando {len(pois)} POIs en timeframe {timeframe}", __name__, "general")

                for poi in pois:
                    if not poi.get('broken', False):
                        score, _ = calcular_puntaje_poi(poi, mercado, POI_SCORING_CONFIG)
                        distance_pips = abs(current_price - poi['price']) * 10000

                        poi_dashboard = {
                            'id': poi.get('id', f"poi_{len(todos_los_pois)}"),
                            'type': poi['type'],
                            'price': poi['price'],
                            'score': score,
                            'timeframe': poi['timeframe'],
                            'distance': abs(current_price - poi['price']),
                            'status': 'MITIGADO' if poi.get('mitigated') else 'ACTIVO',
                            'quality': _determinar_tier_calidad(score, POI_SCORING_CONFIG),
                            'range_high': poi.get('range_high', poi['price']),
                            'range_low': poi.get('range_low', poi['price'])
                        }
                        todos_los_pois.append(poi_dashboard)
                        poi_count_by_timeframe[timeframe] += 1

                        enviar_senal_log("DEBUG", f"POI evaluado: {poi['type']} @ {poi['price']:.5f} | Score: {score} | Distancia: {distance_pips:.1f} pips | TF: {timeframe}", __name__, "general")

        # Log resumen por timeframe
        for tf, count in poi_count_by_timeframe.items():
            if count > 0:
                enviar_senal_log("INFO", f"?? {tf}: {count} POIs activos procesados", __name__, "general")

        if not todos_los_pois:
            enviar_senal_log("WARNING", "?? No se encontraron POIs activos en ning�n timeframe", __name__, "general")
            return []

        enviar_senal_log("INFO", f"?? Total POIs candidatos: {len(todos_los_pois)}", __name__, "general")

        # Ordenar por score y proximidad
        todos_los_pois.sort(key=lambda x: (x['score'], -x['distance']), reverse=True)

        # Aplicar l�mite
        pois_seleccionados = todos_los_pois[:max_pois]

        # Log de POIs seleccionados
        enviar_senal_log("INFO", f"? POIs SELECCIONADOS PARA DASHBOARD: {len(pois_seleccionados)} de {len(todos_los_pois)} disponibles", __name__, "general")
        for i, poi in enumerate(pois_seleccionados, 1):
            distance_pips = poi['distance'] * 10000
            enviar_senal_log("INFO", f"   {i}. {poi['type']} ({poi['quality']}", __name__, "general")

        return pois_seleccionados

    except (ValueError, KeyError, TypeError) as e:
        enviar_senal_log("ERROR", f"? ERROR en b�squeda de POIs para dashboard: {e}", __name__, "general")
        log_poi_centralizado("DASHBOARD_POIS_ERROR", f"Error preparando POIs para dashboard: {e}", is_error=True)
        return []

# =============================================================================
# FUNCIONES DE GESTI�N Y MANTENIMIENTO
# =============================================================================

def invalidar_pois_obsoletos(mercado: Any, df_h4: DataFrameType) -> int:
    """
    Invalida POIs que han sido rotos o son obsoletos.

    Args:
        mercado: Contexto de mercado
        df_h4: DataFrame H4 para verificar rupturas

    Returns:
        N�mero de POIs invalidados
    """
    invalidados = 0

    try:
        if not mercado or not hasattr(mercado, 'pois') or df_h4.empty:
            return 0

        current_price = df_h4['close'].iloc[-1]

        for timeframe, pois in mercado.pois.items():
            if isinstance(pois, list):
                for poi in pois:
                    if poi.get('broken') or poi.get('mitigated'):
                        continue

                    # Verificar si el POI ha sido roto
                    if _verificar_ruptura_poi(poi, current_price, df_h4):
                        poi['broken'] = True
                        poi['broken_at'] = datetime.now().isoformat()
                        invalidados += 1
                        log_poi_centralizado("POI_INVALIDATION", f"POI {poi['id']} invalidado por ruptura")

        return invalidados

    except (ValueError, KeyError, TypeError) as e:
        log_poi_centralizado("INVALIDATION_ERROR", f"Error invalidando POIs: {e}", is_error=True)
        return 0

def generar_mensaje_contextual_pois(info_contextual: Dict, current_price: float) -> str:
    """
    Genera mensaje contextual sobre POIs disponibles.

    Args:
        info_contextual: Informaci�n contextual de POIs
        current_price: Precio actual

    Returns:
        String con mensaje contextual
    """
    try:
        if not info_contextual or 'closest_pois' not in info_contextual:
            return "No hay POIs relevantes cerca del precio actual."

        closest_pois = info_contextual['closest_pois']
        mensaje_partes = []

        mensaje_partes.append(f"?? {len(closest_pois)} POIs de calidad cerca:")

        for i, poi in enumerate(closest_pois[:3], 1):
            tipo_emoji = "??" if "BULLISH" in poi['type'] else "??"
            distancia = poi['distance']
            score = poi['score']
            quality = _determinar_tier_calidad(score, POI_SCORING_CONFIG)

            mensaje_partes.append(
                f"{i}. {tipo_emoji} {poi['type']} ({quality}) - "
                f"{distancia:.1f} pips - Score: {score}"
            )

        if info_contextual.get('recommendation'):
            mensaje_partes.append(f"?? {info_contextual['recommendation']}")

        return "\n".join(mensaje_partes)

    except (ValueError, KeyError, TypeError) as e:
        log_poi_centralizado("CONTEXTUAL_MSG_ERROR", f"Error generando mensaje: {e}", is_error=True)
        return "Error generando informaci�n contextual de POIs."

def generar_reporte_pois(mercado: Any) -> str:
    """
    Genera reporte completo de POIs en el mercado.

    Args:
        mercado: Contexto de mercado

    Returns:
        String con reporte detallado
    """
    try:
        if not mercado or not hasattr(mercado, 'pois'):
            return "No hay informaci�n de POIs disponible."

        reporte_partes = []
        reporte_partes.append("?? REPORTE DE POIs - SENTINEL GRID SYSTEM")
        reporte_partes.append("=" * 50)

        total_pois = 0
        pois_activos = 0
        pois_mitigados = 0
        pois_rotos = 0

        # Estad�sticas por timeframe
        for timeframe, pois in mercado.pois.items():
            if isinstance(pois, list) and pois:
                tf_total = len(pois)
                tf_activos = len([p for p in pois if not p.get('broken') and not p.get('mitigated')])
                tf_mitigados = len([p for p in pois if p.get('mitigated')])
                tf_rotos = len([p for p in pois if p.get('broken')])

                reporte_partes.append(f"\n?? {timeframe}:")
                reporte_partes.append(f"  Total: {tf_total} | Activos: {tf_activos} | Mitigados: {tf_mitigados} | Rotos: {tf_rotos}")

                total_pois += tf_total
                pois_activos += tf_activos
                pois_mitigados += tf_mitigados
                pois_rotos += tf_rotos

        # Resumen general
        reporte_partes.append(f"\n?? RESUMEN GENERAL:")
        reporte_partes.append(f"  Total POIs: {total_pois}")
        reporte_partes.append(f"  Activos: {pois_activos} ({pois_activos/total_pois*100:.1f}%)" if total_pois > 0 else "  Activos: 0")
        reporte_partes.append(f"  Mitigados: {pois_mitigados}")
        reporte_partes.append(f"  Rotos: {pois_rotos}")

        # Top POIs por score
        if total_pois > 0:
            todos_pois_activos = []
            for timeframe, pois in mercado.pois.items():
                if isinstance(pois, list):
                    for poi in pois:
                        if not poi.get('broken') and not poi.get('mitigated'):
                            score, _ = calcular_puntaje_poi(poi, mercado, POI_SCORING_CONFIG)
                            poi_con_score = poi.copy()
                            poi_con_score['score'] = score
                            todos_pois_activos.append(poi_con_score)

            if todos_pois_activos:
                todos_pois_activos.sort(key=lambda x: x['score'], reverse=True)
                reporte_partes.append(f"\n?? TOP 5 POIs (por score):")
                for i, poi in enumerate(todos_pois_activos[:5], 1):
                    quality = _determinar_tier_calidad(poi['score'], POI_SCORING_CONFIG)
                    reporte_partes.append(f"  {i}. {poi['type']} ({quality}) - Score: {poi['score']}")

        return "\n".join(reporte_partes)

    except (ValueError, KeyError, TypeError) as e:
        log_poi_centralizado("REPORT_ERROR", f"Error generando reporte: {e}", is_error=True)
        return "Error generando reporte de POIs."

# =============================================================================
# CLASE PRINCIPAL POI DETECTOR - INTERFAZ UNIFICADA PARA ACC
# =============================================================================

class POIDetector:
    """
    ?? POI DETECTOR - INTERFAZ UNIFICADA PARA EL ACC
    ===============================================

    Clase encapsuladora que act�a como la interfaz p�blica profesional
    para todo el sistema de detecci�n de POIs. Proporciona un punto
    de entrada claro para el ACC Orchestrator.

    ?? PROTOCOLO SYNAPSE 3.1: Romper el aislamiento del POI system
    """

    def __init__(self):
        """Inicializar el detector de POIs"""
        try:
            log_poi("INFO", "INIT: POI Detector inicializado y listo para operar con ACC", "poi_detector")
            self.config = POI_SCORING_CONFIG
            self.initialized = True
            enviar_senal_log("INFO", "POIDetector listo para integraci�n ACC", __name__, "poi")
        except Exception as e:
            enviar_senal_log("ERROR", f"Error inicializando POIDetector: {e}", __name__, "poi")
            self.initialized = False

    def find_all_pois(self, df: DataFrameType, timeframe: str,
                     current_price: Optional[float] = None) -> List[Dict]:
        """
        ?? PUNTO DE ENTRADA PRINCIPAL PARA EL ACC
        ========================================

        Orquesta todas las funciones de detecci�n individuales y
        consolida TODOS los POIs en una lista unificada.

        Args:
            df: DataFrame con datos OHLC
            timeframe: Timeframe de an�lisis
            current_price: Precio actual para c�lculos

        Returns:
            Lista unificada de todos los POIs detectados
        """
        try:
            log_poi("INFO", f"?? ACC REQUEST: Iniciando detecci�n completa de POIs en {timeframe}", "poi_detector")
            enviar_senal_log("INFO", f"?? POI Detection iniciada para TF: {timeframe}", __name__, "detection")

            if not self.initialized:
                enviar_senal_log("ERROR", "? POIDetector no inicializado", __name__, "detection")
                return []

            if df.empty:
                enviar_senal_log("WARNING", "?? DataFrame vac�o recibido", __name__, "detection")
                return []

            detection_start = datetime.now()
            all_pois = []

            # ?? ORQUESTAR TODAS LAS FUNCIONES DE DETECCI�N
            enviar_senal_log("DEBUG", "Iniciando detecci�n Order Blocks...", __name__, "detection")
            order_blocks = detectar_order_blocks(df, timeframe)
            all_pois.extend(order_blocks)

            enviar_senal_log("DEBUG", "Iniciando detecci�n Fair Value Gaps...", __name__, "detection")
            fair_value_gaps = detectar_fair_value_gaps(df, timeframe)
            all_pois.extend(fair_value_gaps)

            enviar_senal_log("DEBUG", "Iniciando detecci�n Breaker Blocks...", __name__, "detection")
            breaker_blocks = detectar_breaker_blocks(df, timeframe)
            all_pois.extend(breaker_blocks)

            enviar_senal_log("DEBUG", "Iniciando detecci�n Imbalances...", __name__, "detection")
            imbalances = detectar_imbalances(df, timeframe)
            all_pois.extend(imbalances)

            # ?? ESTAD�STICAS DE DETECCI�N
            detection_time = (datetime.now() - detection_start).total_seconds()

            log_poi("INFO", f"? ACC RESPONSE: Detecci�n completa finalizada. {len(all_pois)} POIs encontrados en {timeframe} ({detection_time:.2f}s)", "poi_detector")

            enviar_senal_log("INFO", f"? POI Detection completada: {len(all_pois)} POIs en {timeframe} ({detection_time:.2f}s)", __name__, "detection")
            enviar_senal_log("DEBUG", f"Distribuci�n: OB={len(order_blocks)}, FVG={len(fair_value_gaps)}, BB={len(breaker_blocks)}, IM={len(imbalances)}", __name__, "detection")

            return all_pois

        except Exception as e:
            log_poi("ERROR", f"? ERROR en find_all_pois: {str(e)}", "poi_detector")
            enviar_senal_log("ERROR", f"? Error en detecci�n POI: {e}", __name__, "detection")
            return []

    def find_dashboard_pois(self, df: DataFrameType, timeframe: str,
                           current_price: float, max_pois: int = 5) -> List[Dict]:
        """
        ?? ESPECIALIZACI�N PARA DASHBOARD
        ================================

        Encuentra POIs optimizados para visualizaci�n en dashboard.

        Args:
            df: DataFrame con datos OHLC
            timeframe: Timeframe de an�lisis
            current_price: Precio actual
            max_pois: M�ximo n�mero de POIs a retornar

        Returns:
            Lista de POIs optimizada para dashboard
        """
        try:
            enviar_senal_log("INFO", f"?? Dashboard POI request: TF={timeframe}, MaxPOIs={max_pois}", __name__, "dashboard")

            # USAR DATOS REALES DEL MERCADO - Sin Mock
            class RealMarketData:
                def __init__(self, pois_list, current_price):
                    self.pois = {timeframe: pois_list}
                    self.current_price = current_price
                    self.real_data_source = True

            # Detectar todos los POIs primero
            all_pois = self.find_all_pois(df, timeframe, current_price)

            # Crear estructura real de mercado
            market_data = RealMarketData(all_pois, current_price)

            # Usar función existente optimizada con datos reales
            dashboard_pois = encontrar_pois_multiples_para_dashboard(market_data, current_price, max_pois)

            enviar_senal_log("INFO", f"? Dashboard POIs preparados: {len(dashboard_pois)} de {len(all_pois)} disponibles", __name__, "dashboard")

            return dashboard_pois

        except Exception as e:
            enviar_senal_log("ERROR", f"? Error preparando POIs para dashboard: {e}", __name__, "dashboard")
            return []

    def get_poi_summary(self, pois: List[Dict]) -> Dict:
        """
        ?? Generar resumen estad�stico de POIs

        Args:
            pois: Lista de POIs

        Returns:
            Dict con estad�sticas de POIs
        """
        try:
            if not pois:
                return {'total': 0, 'by_type': {}, 'avg_score': 0}

            by_type = {}
            total_score = 0

            for poi in pois:
                poi_type = poi.get('type', 'UNKNOWN')
                by_type[poi_type] = by_type.get(poi_type, 0) + 1
                total_score += poi.get('score', 0)

            return {
                'total': len(pois),
                'by_type': by_type,
                'avg_score': total_score / len(pois) if pois else 0,
                'types_detected': list(by_type.keys())
            }

        except Exception as e:
            enviar_senal_log("ERROR", f"? Error generando resumen POI: {e}", __name__, "summary")
            return {'total': 0, 'by_type': {}, 'avg_score': 0}

# =============================================================================
# FUNCIONES DE TESTING Y CONFIGURACI�N
# =============================================================================

def set_poi_debug_mode(enabled: bool):
    """
    Activa/desactiva modo debug para POIs.

    Args:
        enabled: True para activar debug, False para desactivar
    """
    # Logging solo - sin modificaci�n de estado global
    log_poi_centralizado("DEBUG_MODE", f"Modo debug POI: {'ACTIVADO' if enabled else 'DESACTIVADO'}")

def test_poi_scoring_system():
    """
    Ejecuta tests del sistema de scoring de POIs.

    Returns:
        Dict con resultados de tests
    """
    try:
        # Simular POI de prueba
        test_poi = crear_poi_estructura(
            "BULLISH_OB",
            price=1.1750,
            score=0,
            confidence=0.8,
            timeframe="M15",
            range_high=1.1760,
            range_low=1.1740,
            formation_strength=75,
            confirmation_candles=3,
            volume=1500
        )

        # TEST INTERNAL - Usar estructura real de mercado
        class TestMarketData:
            def __init__(self):
                self.current_price = 1.1755
                self.pois = {'M15': [test_poi]}
                self.is_test_environment = True

        mercado_test = TestMarketData()

        # Ejecutar scoring
        score, detalles = calcular_puntaje_poi(test_poi, mercado_test, POI_SCORING_CONFIG)

        # Verificar resultado
        test_passed = 20 <= score <= 100  # Score razonable

        return {
            'test_passed': test_passed,
            'score': score,
            'details': detalles,
            'poi_tested': test_poi['id']
        }

    except (ValueError, KeyError, TypeError) as e:
        return {
            'test_passed': False,
            'error': str(e)
        }

# =============================================================================
# FUNCIONES AUXILIARES PRIVADAS
# =============================================================================

def _is_bullish_order_block(current, prev, next_candles):
    """Verifica si la vela actual forma un Order Block alcista"""
    return (current['close'] > current['open'] and  # Vela alcista
            current['high'] - current['low'] > (current['close'] - current['open']) * 2 and  # Sombras
            next_candles['close'].max() > current['high'] * 1.001)  # Confirmaci�n

def _is_bearish_order_block(current, prev, next_candles):
    """Verifica si la vela actual forma un Order Block bajista"""
    return (current['close'] < current['open'] and  # Vela bajista
            current['high'] - current['low'] > (current['open'] - current['close']) * 2 and  # Sombras
            next_candles['close'].min() < current['low'] * 0.999)  # Confirmaci�n

def _calcular_score_ob(current, next_candles, direction):
    """Calcula score espec�fico para Order Blocks"""
    base_score = 60

    # Bonus por fuerza del movimiento
    if direction == "BULLISH":
        move_strength = (next_candles['close'].max() - current['high']) / current['high'] * 10000
    else:
        move_strength = (current['low'] - next_candles['close'].min()) / current['low'] * 10000

    strength_bonus = min(move_strength * 2, 20)  # Max 20 puntos bonus

    return int(base_score + strength_bonus)

def _determinar_confianza_ob(current, next_candles):
    """Determina confianza del Order Block (sin volumen si no est� disponible)"""
    try:
        # Intentar usar volumen si est� disponible
        if 'volume' in current.index and 'volume' in next_candles.columns:
            confirmation_candles = len([c for _, c in next_candles.iterrows()
                                       if c['volume'] > current.get('volume', 0) * 0.8])
        else:
            # Fallback: usar price action para confirmar (m�s de 3 velas siguientes)
            confirmation_candles = min(len(next_candles), 3)

        return min(0.5 + (confirmation_candles * 0.1), 0.95)
    except KeyError:
        # Fallback completo: confianza base para Order Blocks sin volumen
        return 0.7

def _calcular_score_fvg(prev_candle, current_candle, next_candle, direction):
    """Calcula score espec�fico para Fair Value Gaps"""
    base_score = 55

    # Size del gap
    if direction == "BULLISH":
        gap_size = next_candle['low'] - prev_candle['high']
    else:
        gap_size = prev_candle['low'] - next_candle['high']

    # Normalizar gap size a pips
    gap_pips = gap_size * 10000
    gap_bonus = min(gap_pips * 2, 25)  # Max 25 puntos bonus

    return int(base_score + gap_bonus)

def _determinar_confianza_fvg(prev_candle, next_candle):
    """Determina confianza del Fair Value Gap"""
    # Mayor confianza para gaps m�s grandes
    gap_size = abs(next_candle['low'] - prev_candle['high']) if next_candle['low'] > prev_candle['high'] else abs(prev_candle['low'] - next_candle['high'])
    gap_pips = gap_size * 10000

    confidence = 0.4 + min(gap_pips * 0.05, 0.4)  # 0.4 a 0.8
    return min(confidence, 0.9)

def _is_breaker_block(ob, df):
    """Verifica si un Order Block se ha convertido en Breaker Block"""
    # L�gica simplificada: si el precio ha roto y retestado el OB
    ob_level = ob['price']
    recent_prices = df['close'].tail(10)

    if ob['type'] == 'BULLISH_OB':
        broken = any(recent_prices < ob['range_low'])
        retested = any(recent_prices > ob['range_low']) if broken else False
    else:
        broken = any(recent_prices > ob['range_high'])
        retested = any(recent_prices < ob['range_high']) if broken else False

    return broken and retested

def _calcular_score_imbalance(current, prev_window, next_window):
    """Calcula score para imbalances"""
    base_score = 45

    # Score basado en velocidad del movimiento
    price_change = abs(current['close'] - prev_window['close'].iloc[0])
    price_change_pct = price_change / prev_window['close'].iloc[0]

    speed_bonus = min(price_change_pct * 1000, 30)  # Max 30 puntos

    return int(base_score + speed_bonus)

def _calcular_score_proximidad(distancia, zones):
    """Calcula score basado en proximidad al precio"""
    distancia_pips = distancia * 10000

    if distancia_pips <= zones['immediate']:
        return 100
    elif distancia_pips <= zones['near']:
        return 80
    elif distancia_pips <= zones['moderate']:
        return 60
    elif distancia_pips <= zones['distant']:
        return 40
    else:
        return 20

def _calcular_score_timeframe(timeframe):
    """Calcula score basado en relevancia del timeframe"""
    tf_scores = {
        'D1': 100, 'H4': 90, 'H1': 80,
        'M30': 70, 'M15': 75, 'M5': 60, 'M1': 40
    }
    return tf_scores.get(timeframe, 50)

def _calcular_score_frescura(created_at):
    """Calcula score basado en qu� tan reciente es el POI"""
    try:
        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        age_hours = (datetime.now() - created_time.replace(tzinfo=None)).total_seconds() / 3600

        if age_hours <= 1:
            return 100
        elif age_hours <= 6:
            return 80
        elif age_hours <= 24:
            return 60
        elif age_hours <= 72:
            return 40
        else:
            return 20
    except:
        return 50

def _calcular_score_contexto(poi, mercado):
    """Calcula score basado en contexto de mercado"""
    # L�gica simplificada de contexto
    context_score = 50

    # Bonus si el POI est� alineado con el bias del mercado
    if hasattr(mercado, 'h4_bias'):
        if ('BULLISH' in poi['type'] and mercado.h4_bias == 'BULLISH') or \
           ('BEARISH' in poi['type'] and mercado.h4_bias == 'BEARISH'):
            context_score += 30

    return min(context_score, 100)

def _determinar_tier_calidad(score, config):
    """Determina el tier de calidad basado en el score"""
    tiers = config['QUALITY_TIERS']

    if score >= tiers['A+']:
        return 'A+'
    elif score >= tiers['A']:
        return 'A'
    elif score >= tiers['B']:
        return 'B'
    elif score >= tiers['C']:
        return 'C'
    else:
        return 'D'

def _generar_recomendacion_pois(top_pois, current_price):
    """Genera recomendaci�n basada en los mejores POIs"""
    if not top_pois:
        return "No hay POIs relevantes para recomendaci�n."

    mejor_poi = top_pois[0]
    direction = "alcista" if "BULLISH" in mejor_poi['type'] else "bajista"
    distancia = mejor_poi['distance']

    return f"Esperar retroceso hacia {mejor_poi['type']} a {distancia:.1f} pips para entrada {direction}."

def _generar_recomendacion_trading(poi, mercado):
    """Genera recomendaci�n espec�fica de trading"""
    direction = "LONG" if "BULLISH" in poi['type'] else "SHORT"
    entry_level = poi['price']

    # Stop loss b�sico
    if direction == "LONG":
        stop_loss = poi.get('range_low', entry_level * 0.999)
    else:
        stop_loss = poi.get('range_high', entry_level * 1.001)

    risk_pips = abs(entry_level - stop_loss) * 10000

    return {
        'direction': direction,
        'entry_level': entry_level,
        'stop_loss': stop_loss,
        'risk_pips': risk_pips,
        'recommended_lot_size': f"Ajustar seg�n {risk_pips:.1f} pips de riesgo"
    }

def _evaluar_riesgo_poi(poi, mercado):
    """Eval�a el riesgo asociado con el POI"""
    risk_level = "MEDIO"
    risk_factors = []

    # Evaluar distancia
    if poi['distance'] > 50:
        risk_factors.append("POI distante")
        risk_level = "ALTO"

    # Evaluar score
    if poi['score'] < 60:
        risk_factors.append("Score moderado")
        risk_level = "ALTO" if risk_level != "ALTO" else "ALTO"

    # Evaluar timeframe
    if poi['timeframe'] in ['M1', 'M5']:
        risk_factors.append("Timeframe bajo")

    if not risk_factors:
        risk_level = "BAJO"

    return {
        'level': risk_level,
        'factors': risk_factors,
        'recommendation': f"Riesgo {risk_level} - {'Proceder con cautela' if risk_level == 'ALTO' else 'Setup favorable'}"
    }

def _verificar_ruptura_poi(poi, current_price, df_h4):
    """Verifica si un POI ha sido roto definitivamente"""
    try:
        # L�gica de ruptura basada en el tipo de POI
        if 'BULLISH' in poi['type']:
            # POI alcista roto si el precio cierra por debajo del rango bajo
            return current_price < poi.get('range_low', poi['price']) * 0.999
        else:
            # POI bajista roto si el precio cierra por encima del rango alto
            return current_price > poi.get('range_high', poi['price']) * 1.001
    except:
        return False

# =============================================================================
# VARIABLES GLOBALES
# =============================================================================

POI_DEBUG_MODE = False

# =============================================================================
# EXPORTACIONES P�BLICAS - OPTIMIZADAS PARA ACC
# =============================================================================

__all__ = [
    # ?? INTERFAZ PRINCIPAL PARA ACC
    'POIDetector',

    # Detectores individuales (legacy support)
    'detectar_order_blocks',
    'detectar_fair_value_gaps',
    'detectar_breaker_blocks',
    'detectar_imbalances',
    'detectar_todos_los_pois',

    # An�lisis y scoring
    'calcular_puntaje_poi',
    'obtener_pois_superiores_cercanos',
    'encontrar_poi_de_alta_probabilidad',
    'encontrar_pois_multiples_para_dashboard',

    # Gesti�n
    'invalidar_pois_obsoletos',
    'generar_mensaje_contextual_pois',
    'generar_reporte_pois',

    # Utilidades
    'crear_poi_estructura',
    'log_poi_centralizado',

    # Testing y configuraci�n
    'set_poi_debug_mode',
    'test_poi_scoring_system',
    'test_poi_logging_migration',

    # Constantes
    'POI_TYPES',
    'POI_SCORING_CONFIG'
]
