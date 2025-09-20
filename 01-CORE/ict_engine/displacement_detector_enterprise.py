"""
🎯 DISPLACEMENT DETECTOR ENTERPRISE V6.0 - ICT SMART MONEY CONCEPTS
==================================================================

📅 Fecha: 2025-08-09 08:35:00 GMT
🎯 Objetivo: Detectar Displacement real con datos MT5 + Memory Integration
✅ Cumplimiento: REGLAS_COPILOT.md #7 #8 - Test-first, datos reales

Displacement Detection ICT:
1. 🚀 Movimientos institucionales >50 pips en <4 horas
2. 📊 Analysis de momentum y volumen institucional
3. 🧠 Memory integration para success rate histórico
4. 🎯 Target estimation basado en ICT methodology
"""

from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas as pd

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import json
import logging

# 🏗️ ENTERPRISE ARCHITECTURE v6.0 - Thread-safe pandas
try:
    from data_management.advanced_candle_downloader import _pandas_manager
except ImportError:
    print("⚠️ Thread-safe pandas manager no disponible - usando fallback")
    _pandas_manager = None

try:
    from ..smart_trading_logger import log_trading_decision_smart_v6  # type: ignore
    from ..analysis.unified_memory_system import UnifiedMemorySystem  # type: ignore
    from ..analysis.market_structure_analyzer import MarketStructureAnalyzer as MarketStructureAnalyzerV6  # type: ignore
    from ..data_management.advanced_candle_downloader import AdvancedCandleDownloader  # type: ignore
except ImportError:
    # Fallback logging para desarrollo
    def log_trading_decision_smart_v6(event_type, data, level="INFO", force_important=False, symbol="EURUSD") -> bool:  # type: ignore
        print(f"📈 {event_type} {symbol}: {data}")
        return True
    
    # Fallback classes
    class UnifiedMemorySystem:  # type: ignore
        """Fallback UnifiedMemorySystem"""
        def __init__(self):
            pass
        def store_displacement(self, *args, **kwargs):
            pass
        def get_historical_performance(self, *args, **kwargs):
            return {"success_rate": 0.5, "avg_pips": 0}
        def update_memory(self, *args, **kwargs):
            pass
        def get_historical_insight(self, *args, **kwargs):  # type: ignore
            return {"performance": "no_data", "success_rate": 0.5}
    
    class MarketStructureAnalyzerV6:  # type: ignore  
        """Fallback MarketStructureAnalyzerV6"""
        def __init__(self):
            pass
        def analyze_structure(self, *args, **kwargs):
            return {"trend": "SIDEWAYS", "strength": 0.5}
        def get_structure_breaks(self, *args, **kwargs):
            return []
    
    class AdvancedCandleDownloader:  # type: ignore
        """Fallback AdvancedCandleDownloader"""
        def __init__(self):
            pass
        def get_candles(self, *args, **kwargs):
            return None
        def download_timeframe_data(self, *args, **kwargs):
            return None

@dataclass
class DisplacementSignal:
    """📈 Señal de Displacement ICT Enterprise"""
    # Core ICT attributes
    displacement_type: str  # "BULLISH_DISPLACEMENT", "BEARISH_DISPLACEMENT"
    start_price: float
    end_price: float
    displacement_pips: float
    timeframe_detected: str
    timestamp: datetime
    momentum_score: float
    institutional_signature: bool
    target_estimation: float
    confluence_factors: List[str]
    
    # Enterprise enhancements
    memory_enhanced: bool = False
    historical_success_rate: float = 0.0
    session_optimization: str = ""
    sic_stats: Dict[str, Any] = field(default_factory=dict)
    sluc_integration: bool = False
    
    # Advanced ICT metrics
    liquidity_cleared: float = 0.0
    order_flow_imbalance: float = 0.0
    relative_equal_highs_lows: bool = False
    fair_value_gap_created: bool = False
    market_structure_shift: bool = False
    # ML scoring for MSS (optional)
    ml_score: float = 0.0
    ml_confidence: float = 0.0

class DisplacementDetectorEnterprise:
    """🎯 Displacement Detector Enterprise con ICT Smart Money Concepts v6.0"""
    
    def __init__(self):
        """🚀 Inicializar Displacement Detector Enterprise"""
        self.version = "6.0-enterprise-sic"
        self.logger = logging.getLogger(__name__)
        
        try:
            self.memory_system = UnifiedMemorySystem()
            self.market_analyzer = MarketStructureAnalyzerV6()
            self.candle_downloader = AdvancedCandleDownloader()
            self.memory_enabled = True
        except Exception as e:
            self.logger.warning(f"Memory system fallback: {e}")
            self.memory_enabled = False
        
        # ICT Displacement parameters
        self.min_displacement_pips = 50.0  # Minimum ICT displacement
        self.max_time_window = 240  # 4 hours in minutes
        self.institutional_volume_threshold = 1.5  # Volume spike multiplier
        self.momentum_threshold = 0.7  # Minimum momentum score
        
        log_trading_decision_smart_v6(
            "DISPLACEMENT_DETECTOR_INIT", {
                "version": self.version,
                "memory_enabled": self.memory_enabled,
                "min_displacement_pips": self.min_displacement_pips,
                "ict_compliance": "FULL"
            }, symbol="SYSTEM"
        )
        # CHoCH memory availability check (lazy import with fallback)
        self._choch_available = False
        try:
            from memory.choch_historical_memory import (
                compute_historical_bonus,
                calculate_historical_success_rate,
            )  # type: ignore
            self._compute_choch_bonus = compute_historical_bonus
            self._choch_success_rate = calculate_historical_success_rate
            self._choch_available = True
        except Exception as e:
            self._compute_choch_bonus = lambda **kwargs: {"historical_bonus": 0.0, "samples": 0}
            self._choch_success_rate = lambda **kwargs: 0.0
            self.logger.warning(f"CHoCH memory not available: {e}")

        # MSS ML scorer (optional)
        self._mss_scorer = None
        try:
            from machine_learning.mss.service import MSSShiftScorer  # type: ignore
            self._mss_scorer = MSSShiftScorer()
        except Exception as e:
            self.logger.warning(f"MSSShiftScorer not available: {e}")

        # Pip cache for symbols
        self._pip_cache: Dict[str, float] = {}

    def _get_pip_value(self, symbol: str) -> float:
        """Obtener pip_value por símbolo desde config, con heurística de fallback."""
        try:
            if symbol in self._pip_cache:
                return self._pip_cache[symbol]

            # Buscar archivo de configuración relativo al módulo
            config_path = Path(__file__).resolve().parents[1] / 'config' / 'trading_symbols_config.json'
            pip_val = None
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                sym_cfg = (cfg.get('symbol_configurations', {}) or {}).get(symbol.upper())
                if sym_cfg and 'pip_value' in sym_cfg:
                    pip_val = float(sym_cfg['pip_value'])

            # Heurística si no está en config
            if pip_val is None:
                s = symbol.upper()
                if 'JPY' in s or s.endswith('JPY'):
                    pip_val = 0.01
                elif s in {'XAUUSD', 'GOLD', 'XAU'}:
                    pip_val = 0.01
                else:
                    pip_val = 0.0001

            self._pip_cache[symbol] = pip_val
            return pip_val
        except Exception:
            return 0.0001
    
    def _get_pandas_manager(self):
        """🐼 Obtener instancia thread-safe de pandas"""
        try:
            # Usar _pandas_manager global thread-safe
            if _pandas_manager is not None:
                return _pandas_manager.get_safe_pandas_instance()
            else:
                # Fallback a importación directa (solo para development)
                # pandas access via thread-safe manager
                return pd
        except Exception as e:
            self.logger.error(f"Error obteniendo pandas manager: {e}")
            # Fallback a importación directa (solo para development)
            # pandas access via thread-safe manager
            return pd
    
    def detect_displacement(self, data: pd.DataFrame, symbol: str = "EURUSD", 
                          timeframe: str = "M15") -> List[DisplacementSignal]:
        """🎯 Detectar Displacement con criterios ICT enterprise"""
        
        log_trading_decision_smart_v6(
            "DISPLACEMENT_DETECTION_START", {
                "data_points": len(data),
                "timeframe": timeframe,
                "detection_method": "ICT_ENTERPRISE_v6.0"
            }, symbol=symbol
        )
        
        displacement_signals = []
        
        # Validar datos suficientes
        if len(data) < 50:
            self.logger.warning("Insufficient data for displacement detection")
            return displacement_signals
        
        # Análisis ventana deslizante
        window_size = min(16, len(data) // 4)  # Adaptive window
        
        for i in range(window_size, len(data) - 1):
            # Ventana de análisis para displacement
            analysis_window = data.iloc[i-window_size:i+1]
            
            # Core displacement detection
            displacement_signal = self._analyze_displacement_window(
                analysis_window, symbol, timeframe, i
            )
            
            if displacement_signal:
                # Enterprise enhancements
                displacement_signal = self._enhance_with_memory(displacement_signal, symbol)
                displacement_signal = self._enhance_with_sic_stats(displacement_signal, analysis_window)
                displacement_signal = self._enhance_with_market_structure(displacement_signal, analysis_window)

                # ML scoring for MSS (optional)
                try:
                    if self._mss_scorer is not None:
                        ml = self._mss_scorer.score(analysis_window, symbol=symbol, timeframe=timeframe)
                        displacement_signal.ml_score = float(ml.get('prob_shift', 0.0) or 0.0)
                        displacement_signal.ml_confidence = float(ml.get('confidence', 0.0) or 0.0)
                        # If ML strongly indicates shift, enforce flag
                        if displacement_signal.ml_score >= 0.8 and displacement_signal.ml_confidence >= 0.6:
                            displacement_signal.market_structure_shift = True
                except Exception as e:
                    self.logger.warning(f"MSS ML scoring failed: {e}")

                # Mild CHoCH-based enrichment for MSS context
                try:
                    if self._choch_available:
                        bonus_info = self._compute_choch_bonus(symbol=symbol, timeframe=timeframe, break_level=float(displacement_signal.end_price))
                        hist_bonus = float(bonus_info.get('historical_bonus', 0.0) or 0.0)
                        # Reflect bonus by adjusting target estimation slightly and embedding stats
                        displacement_signal.target_estimation = displacement_signal.target_estimation * (1.0 + (hist_bonus / 500.0))
                        signal_sr = self._choch_success_rate(symbol=symbol, timeframe=timeframe)
                        displacement_signal.sic_stats["choch_bonus"] = hist_bonus
                        displacement_signal.sic_stats["choch_success_rate"] = signal_sr
                except Exception as e:
                    self.logger.warning(f"CHoCH enrichment failed: {e}")
                
                displacement_signals.append(displacement_signal)
                
                log_trading_decision_smart_v6(
                    "DISPLACEMENT_DETECTED", {
                        "displacement_type": displacement_signal.displacement_type,
                        "displacement_pips": displacement_signal.displacement_pips,
                        "momentum_score": displacement_signal.momentum_score,
                        "institutional_signature": displacement_signal.institutional_signature,
                        "memory_enhanced": displacement_signal.memory_enhanced
                    }, symbol=symbol
                )
        
        log_trading_decision_smart_v6(
            "DISPLACEMENT_DETECTION_COMPLETE", {
                "total_displacements": len(displacement_signals),
                "bullish_count": len([d for d in displacement_signals if d.displacement_type == "BULLISH_DISPLACEMENT"]),
                "bearish_count": len([d for d in displacement_signals if d.displacement_type == "BEARISH_DISPLACEMENT"]),
                "avg_displacement_pips": sum(d.displacement_pips for d in displacement_signals) / max(len(displacement_signals), 1)
            }, symbol=symbol
        )
        
        return displacement_signals
    
    def _analyze_displacement_window(self, window: pd.DataFrame, symbol: str, 
                                   timeframe: str, index: int) -> Optional[DisplacementSignal]:
        """📊 Analizar ventana para displacement ICT"""
        
        if len(window) < 5:
            return None
        
        # Calcular movimiento de precio
        start_price = window.iloc[0]['open']
        end_price = window.iloc[-1]['close']
        price_movement = end_price - start_price
        pip = self._get_pip_value(symbol)
        displacement_pips = abs(price_movement) / max(pip, 1e-9)
        
        # Filtro mínimo ICT
        if displacement_pips < self.min_displacement_pips:
            return None
        
        # Calcular momentum score
        momentum_score = self._calculate_momentum_score(window)
        if momentum_score < self.momentum_threshold:
            return None
        
        # Detectar institutional signature
        institutional_signature = self._detect_institutional_signature(window)
        
        # Estimar target ICT
        target_estimation = self._calculate_ict_target(start_price, end_price, price_movement)
        
        # Detectar confluence factors
        confluence_factors = self._analyze_confluence_factors(window)
        
        # Crear señal displacement
        displacement_signal = DisplacementSignal(
            displacement_type="BULLISH_DISPLACEMENT" if price_movement > 0 else "BEARISH_DISPLACEMENT",
            start_price=start_price,
            end_price=end_price,
            displacement_pips=displacement_pips,
            timeframe_detected=timeframe,
            timestamp=window.index[-1],
            momentum_score=momentum_score,
            institutional_signature=institutional_signature,
            target_estimation=target_estimation,
            confluence_factors=confluence_factors
        )
        
        return displacement_signal
    
    def _calculate_momentum_score(self, window: pd.DataFrame) -> float:
        """⚡ Calcular momentum score ICT"""
        
        # Velocity análisis
        price_changes = window['close'].diff().dropna()
        velocity = abs(price_changes.mean()) / window['close'].std() if window['close'].std() > 0 else 0
        
        # Volume análisis - compatible con MT5 y fallback data
        volume_col = 'tick_volume' if 'tick_volume' in window.columns else 'volume'
        if volume_col in window.columns:
            avg_volume = window[volume_col].mean()
            max_volume = window[volume_col].max()
            volume_score = min(1.0, max_volume / avg_volume) if avg_volume > 0 else 0.5
        else:
            volume_score = 0.5  # Default score
        
        # Consistency análisis
        if window.iloc[-1]['close'] > window.iloc[0]['open']:
            directional_moves = (price_changes.astype(float) > 0).sum()
        else:
            directional_moves = (price_changes.astype(float) < 0).sum()
        consistency = directional_moves / len(price_changes) if len(price_changes) > 0 else 0.5
        
        # Combined momentum score
        momentum_score = (velocity * 0.4) + (volume_score * 0.3) + (consistency * 0.3)
        return min(1.0, momentum_score)
    
    def _detect_institutional_signature(self, window: pd.DataFrame) -> bool:
        """🏛️ Detectar institutional signature ICT"""
        
        # Volume spike detection - compatible con MT5 y fallback data
        volume_col = 'tick_volume' if 'tick_volume' in window.columns else 'volume'
        if volume_col in window.columns:
            avg_volume = window[volume_col].mean()
            max_volume = window[volume_col].max()
            volume_spike = max_volume > (avg_volume * self.institutional_volume_threshold)
        else:
            volume_spike = True  # Assume institutional activity if no volume data
        
        # Large candle detection (institutional activity)
        candle_sizes = abs(window['close'] - window['open'])
        avg_candle_size = candle_sizes.mean()
        max_candle_size = candle_sizes.max()
        large_candle = max_candle_size > (avg_candle_size * 2.0)
        
        # Wick analysis (stop hunting/liquidity clearing)
        upper_wicks = window['high'] - window[['open', 'close']].max(axis=1)
        lower_wicks = window[['open', 'close']].min(axis=1) - window['low']
        significant_wicks = (upper_wicks > candle_sizes).any() or (lower_wicks > candle_sizes).any()
        
        return bool(volume_spike and (large_candle or significant_wicks))
    
    def _calculate_ict_target(self, start_price: float, end_price: float, price_movement: float) -> float:
        """🎯 Calcular target estimation ICT methodology"""
        
        # ICT typical target: 2-5x displacement range
        displacement_range = abs(price_movement)
        
        # Adaptive target based on displacement strength
        if displacement_range > 0.0100:  # >100 pips
            target_multiplier = 2.0  # Conservative for large moves
        elif displacement_range > 0.0075:  # >75 pips
            target_multiplier = 2.5
        else:  # 50-75 pips
            target_multiplier = 3.0  # More aggressive for smaller moves
        
        # Calculate target
        target_distance = displacement_range * target_multiplier
        direction = 1 if end_price > start_price else -1
        target_estimation = end_price + (target_distance * direction)
        
        return target_estimation
    
    def _analyze_confluence_factors(self, window: pd.DataFrame) -> List[str]:
        """🔄 Analizar confluence factors ICT"""
        
        confluence_factors = []
        
        # Basic displacement momentum
        confluence_factors.append("displacement_momentum")
        
        # Volume signature
        avg_volume = window['volume'].mean()
        if window['volume'].max() > avg_volume * 1.5:
            confluence_factors.append("institutional_volume")
        
        # Large candle signature
        candle_sizes = abs(window['close'] - window['open'])
        if candle_sizes.max() > candle_sizes.mean() * 2:
            confluence_factors.append("institutional_candle")
        
        # Time-based factors
        hour = window.index[-1].hour
        if hour in [8, 9, 15, 16]:  # London/NY killzones
            confluence_factors.append("killzone_timing")
        
        # Gap detection (potential FVG)
        gaps = self._detect_potential_gaps(window)
        if gaps:
            confluence_factors.append("fair_value_gaps")
        
        return confluence_factors
    
    def _detect_potential_gaps(self, window: pd.DataFrame) -> bool:
        """📊 Detectar potential Fair Value Gaps"""
        
        if len(window) < 3:
            return False
        
        for i in range(1, len(window) - 1):
            prev_candle = window.iloc[i-1]
            current_candle = window.iloc[i]
            next_candle = window.iloc[i+1]
            
            # Bullish FVG pattern
            if (current_candle['low'] > prev_candle['high'] and 
                current_candle['low'] > next_candle['high']):
                return True
            
            # Bearish FVG pattern
            if (current_candle['high'] < prev_candle['low'] and 
                current_candle['high'] < next_candle['low']):
                return True
        
        return False
    
    def _enhance_with_memory(self, signal: DisplacementSignal, symbol: str) -> DisplacementSignal:
        """🧠 Enhance with UnifiedMemorySystem v6.1"""
        
        if not self.memory_enabled:
            return signal
        
        try:
            # Query historical success rate
            memory_key = f"displacement_{signal.displacement_type}_{symbol}"
            historical_data = self.memory_system.get_historical_insight(memory_key, "M15")
            
            if historical_data:
                signal.memory_enhanced = True
                signal.historical_success_rate = historical_data.get('success_rate', 0.0)
                signal.session_optimization = historical_data.get('best_session', 'LONDON_NY')
            else:
                # Initialize memory entry
                signal.memory_enhanced = True
                signal.historical_success_rate = 0.75  # ICT baseline
                signal.session_optimization = "LONDON_NY_OPTIMIZED"
        
        except Exception as e:
            self.logger.warning(f"Memory enhancement failed: {e}")
        
        return signal
    
    def _enhance_with_sic_stats(self, signal: DisplacementSignal, window: pd.DataFrame) -> DisplacementSignal:
        """📊 Enhance with SIC v3.1 statistics"""
        
        # Calculate SIC statistics
        signal.sic_stats = {
            "volatility_percentile": self._calculate_volatility_percentile(window),
            "volume_profile": self._analyze_volume_profile(window),
            "market_session": self._identify_market_session(signal.timestamp),
            "displacement_strength": "STRONG" if signal.displacement_pips > 75 else "MODERATE"
        }
        
        signal.sluc_integration = True
        
        return signal
    
    def _enhance_with_market_structure(self, signal: DisplacementSignal, window: pd.DataFrame) -> DisplacementSignal:
        """🏗️ Enhance with market structure analysis"""
        
        # Liquidity analysis
        signal.liquidity_cleared = self._calculate_liquidity_cleared(window)
        
        # Order flow imbalance
        signal.order_flow_imbalance = self._calculate_order_flow_imbalance(window)
        
        # Equal highs/lows detection
        signal.relative_equal_highs_lows = self._detect_equal_highs_lows(window)
        
        # FVG creation
        signal.fair_value_gap_created = self._detect_potential_gaps(window)
        
        # Market structure shift
        signal.market_structure_shift = self._detect_structure_shift(window)
        
        return signal
    
    def _calculate_volatility_percentile(self, window: pd.DataFrame) -> float:
        """📈 Calculate volatility percentile"""
        true_ranges = []
        for i in range(1, len(window)):
            tr = max(
                window.iloc[i]['high'] - window.iloc[i]['low'],
                abs(window.iloc[i]['high'] - window.iloc[i-1]['close']),
                abs(window.iloc[i]['low'] - window.iloc[i-1]['close'])
            )
            true_ranges.append(tr)
        
        if not true_ranges:
            return 0.5
        
        current_tr = true_ranges[-1]
        avg_tr = sum(true_ranges) / len(true_ranges)
        
        return min(1.0, current_tr / avg_tr) if avg_tr > 0 else 0.5
    
    def _analyze_volume_profile(self, window: pd.DataFrame) -> str:
        """📊 Analyze volume profile"""
        volumes = window['volume'].astype(float)
        avg_vol = volumes.mean()
        
        if volumes[-1] > avg_vol * 2:
            return "EXPLOSIVE"
        elif volumes[-1] > avg_vol * 1.5:
            return "HIGH"
        elif volumes[-1] > avg_vol:
            return "ABOVE_AVERAGE"
        else:
            return "NORMAL"
    
    def _identify_market_session(self, timestamp: datetime) -> str:
        """⏰ Identify market session"""
        hour = timestamp.hour
        
        if 6 <= hour <= 10:
            return "LONDON_OPEN"
        elif 13 <= hour <= 17:
            return "NY_OPEN"
        elif 21 <= hour <= 23:
            return "ASIA_OPEN"
        else:
            return "OVERLAP_SESSION"
    
    def _calculate_liquidity_cleared(self, window: pd.DataFrame) -> float:
        """💧 Calculate liquidity cleared estimate"""
        # Simplified: Based on wick sizes and volume
        total_wicks = 0
        for i in range(len(window)):
            candle = window.iloc[i]
            body_size = abs(candle['close'] - candle['open'])
            upper_wick = candle['high'] - max(candle['open'], candle['close'])
            lower_wick = min(candle['open'], candle['close']) - candle['low']
            total_wicks += (upper_wick + lower_wick) / max(body_size, 0.0001)
        
        return total_wicks / len(window)
    
    def _calculate_order_flow_imbalance(self, window: pd.DataFrame) -> float:
        """⚖️ Calculate order flow imbalance"""
        # Simplified: Based on price and volume relationship
        price_changes = window['close'].diff().dropna()
        volume_changes = window['volume'].diff().dropna()
        
        if len(price_changes) == 0 or len(volume_changes) == 0:
            return 0.0
        
        # Correlation between price and volume changes
        correlation = np.corrcoef(price_changes, volume_changes[:len(price_changes)])[0, 1]
        return correlation if not np.isnan(correlation) else 0.0
    
    def _detect_equal_highs_lows(self, window: pd.DataFrame) -> bool:
        """⚖️ Detect relative equal highs/lows"""
        tolerance = 0.0005  # 5 pips tolerance
        
        highs = window['high'].values
        lows = window['low'].values
        
        # Check for equal highs
        for i in range(len(highs) - 2):
            for j in range(i + 2, len(highs)):
                if abs(highs[i] - highs[j]) <= tolerance:
                    return True
        
        # Check for equal lows
        for i in range(len(lows) - 2):
            for j in range(i + 2, len(lows)):
                if abs(lows[i] - lows[j]) <= tolerance:
                    return True
        
        return False
    
    def _detect_structure_shift(self, window: pd.DataFrame) -> bool:
        """🏗️ Detect market structure shift (MSS) with robust swing/BOS logic"""
        try:
            if len(window) < 10:
                return False

            # Volatility gate using simple ATR-like measure
            high_np = window['high'].to_numpy(dtype=float)
            low_np = window['low'].to_numpy(dtype=float)
            close_np = window['close'].to_numpy(dtype=float)
            tr = np.maximum(
                high_np[1:] - low_np[1:],
                np.maximum(
                    np.abs(high_np[1:] - close_np[:-1]),
                    np.abs(low_np[1:] - close_np[:-1]),
                ),
            )
            avg_tr = float(np.mean(tr)) if len(tr) else 0.0
            if avg_tr <= 0:
                return False

            # Identify recent swings (zigzag-lite): a point is swing high if high prev<curr>next, swing low if low prev>curr<next
            highs = window['high'].values
            lows = window['low'].values
            closes = window['close'].values

            swing_highs: List[int] = []
            swing_lows: List[int] = []
            for i in range(1, len(window) - 1):
                if highs[i] > highs[i - 1] and highs[i] > highs[i + 1]:
                    swing_highs.append(i)
                if lows[i] < lows[i - 1] and lows[i] < lows[i + 1]:
                    swing_lows.append(i)

            if len(swing_highs) < 2 and len(swing_lows) < 2:
                return False

            # Determine current bias using last two closes
            bias_up = closes[-1] > closes[-2]

            # Define BOS thresholds relative to volatility (e.g., 1.2x ATR)
            bos_buffer = 1.2 * avg_tr

            # Check bearish shift: break below last confirmed swing low after making a lower high
            bearish_shift = False
            if len(swing_lows) >= 2 and len(swing_highs) >= 1:
                last_low_idx = swing_lows[-1]
                prior_low = lows[last_low_idx]
                # Require a lower high structure before break (optional for robustness)
                last_high_idx = swing_highs[-1]
                prior_high = highs[last_high_idx]
                # Price currently below last swing low by buffer
                if closes[-1] < (prior_low - bos_buffer):
                    bearish_shift = True

            # Check bullish shift: break above last confirmed swing high after making a higher low
            bullish_shift = False
            if len(swing_highs) >= 2 and len(swing_lows) >= 1:
                last_high_idx = swing_highs[-1]
                prior_high = highs[last_high_idx]
                last_low_idx = swing_lows[-1]
                prior_low = lows[last_low_idx]
                if closes[-1] > (prior_high + bos_buffer):
                    bullish_shift = True

            # Optional confirmation: candle body close beyond level and displacement body size > 0.8*ATR
            body = abs(window['close'].iloc[-1] - window['open'].iloc[-1])
            if body < 0.8 * avg_tr:
                # If body is small, demand stronger breach
                if bullish_shift and closes[-1] <= (prior_high + 1.5 * bos_buffer):
                    bullish_shift = False
                if bearish_shift and closes[-1] >= (prior_low - 1.5 * bos_buffer):
                    bearish_shift = False

            # Final decision
            return bool(bullish_shift or bearish_shift)

        except Exception:
            # Fallback to previous simple trend reversal heuristic
            if len(window) < 5:
                return False
            first_half = window.iloc[: len(window) // 2]
            second_half = window.iloc[len(window) // 2 :]
            first_trend = first_half.iloc[-1]['close'] - first_half.iloc[0]['open']
            second_trend = second_half.iloc[-1]['close'] - second_half.iloc[0]['open']
            return (first_trend * second_trend < 0) and (
                abs(first_trend) > 0.0020 or abs(second_trend) > 0.0020
            )

# 🚀 Enterprise factory function
def create_displacement_detector_enterprise() -> DisplacementDetectorEnterprise:
    """🏭 Factory function para DisplacementDetectorEnterprise"""
    return DisplacementDetectorEnterprise()

if __name__ == "__main__":
    # 🧪 Quick test
    print("🎯 Testing DisplacementDetectorEnterprise v6.0...")
    
    detector = create_displacement_detector_enterprise()
    
    # Create sample data
    dates = pd.date_range(start=datetime.now() - timedelta(hours=24), periods=100, freq='15min')
    sample_data = pd.DataFrame({
        'open': np.random.normal(1.0900, 0.0020, 100),
        'high': np.random.normal(1.0920, 0.0025, 100),
        'low': np.random.normal(1.0880, 0.0025, 100),
        'close': np.random.normal(1.0910, 0.0020, 100),
        'volume': np.random.randint(500, 2000, 100)
    }, index=dates)
    
    # Add displacement pattern
    sample_data.iloc[50:55, 3] += 0.0080  # Create 80 pip displacement
    
    displacements = detector.detect_displacement(sample_data, "EURUSD", "M15")
    
    print(f"✅ Detected {len(displacements)} displacement signals")
    for d in displacements:
        print(f"📈 {d.displacement_type}: {d.displacement_pips:.1f} pips, Score: {d.momentum_score:.2f}")
