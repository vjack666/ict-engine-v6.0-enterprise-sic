"""
📊 MARKET STRUCTURE INTELLIGENCE v6.1
Advanced market structure analysis with context awareness

OPTIMIZADO PARA LOGGING CENTRAL:
- Integración completa con sistema de logging unificado
- Fallback robusto para operaciones sin sistema central
- Eliminación de redeclaraciones de funciones
- Logging dual: centralizado + local para máxima robustez

PHASE 2 - DAY 3 Implementation:
- Market structure state machine
- Trend/range identification with ICT methodology
- Support/resistance intelligence
- Market phase detection (Accumulation, Manipulation, Distribution)
- Structure break detection with confluence

Dependencies:
- PatternConfluenceEngine (v6.1)
- UnifiedMemorySystem (v6.1)
- Black Box Logger (v6.1)  
- ICT methodologies integration
- UnifiedLoggingSystem (centralizado)
"""

import time
import threading
import importlib.util
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
import pandas as pd

# Enterprise logging integration - Optimizado para logging central
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Sistema de logging centralizado con fallback robusto
create_unified_logger_func = None  # Variable global para función
SLUC_AVAILABLE = False

try:
    from ict_engine.unified_logging import (
        log_info, log_warning, log_error, log_debug,
        UnifiedLoggingSystem, create_unified_logger
    )
    create_unified_logger_func = create_unified_logger
    SLUC_AVAILABLE = True
except ImportError:
    SLUC_AVAILABLE = False
    logging.basicConfig(level=logging.INFO)
    # Fallback logging functions
    def log_info(message, component="CORE"): logging.info(f"[{component}] {message}")
    def log_warning(message, component="CORE"): logging.warning(f"[{component}] {message}") 
    def log_error(message, component="CORE"): logging.error(f"[{component}] {message}")
    def log_debug(message, component="CORE"): logging.debug(f"[{component}] {message}")

def get_smart_logger(name="MarketStructureIntelligence"):
    """🎯 Get smart logger optimizado para sistema central"""
    if SLUC_AVAILABLE and create_unified_logger_func:
        return create_unified_logger_func(name)
    else:
        return logging.getLogger(name)

# Black box logging
try:
    # Add black box logger path
    black_box_logger_path = Path(__file__).parent.parent.parent / "05-LOGS" / "black_box_analysis"
    if str(black_box_logger_path) not in sys.path:
        sys.path.insert(0, str(black_box_logger_path))
    
    # Dynamic import to avoid Pylance issues
    spec = importlib.util.spec_from_file_location(
        "black_box_logger", 
        black_box_logger_path / "black_box_logger.py"
    )
    if spec and spec.loader:
        black_box_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(black_box_module)
        get_black_box_logger = getattr(black_box_module, 'get_black_box_logger')
        BLACK_BOX_AVAILABLE = True
    else:
        BLACK_BOX_AVAILABLE = False
except Exception:
    BLACK_BOX_AVAILABLE = False


class MarketPhase(Enum):
    """📈 ICT Market phases"""
    ACCUMULATION = "ACCUMULATION"       # Smart money accumulating
    MANIPULATION = "MANIPULATION"       # Price manipulation/liquidity grab
    DISTRIBUTION = "DISTRIBUTION"       # Smart money distributing
    REBALANCE = "REBALANCE"            # Market rebalancing
    UNKNOWN = "UNKNOWN"                # Unclear phase


class TrendDirection(Enum):
    """📊 Trend direction"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"  
    SIDEWAYS = "SIDEWAYS"
    TRANSITIONING = "TRANSITIONING"


class StructureType(Enum):
    """🏗️ Market structure types"""
    HIGHER_HIGH = "HH"           # Higher High
    HIGHER_LOW = "HL"            # Higher Low
    LOWER_HIGH = "LH"            # Lower High
    LOWER_LOW = "LL"             # Lower Low
    EQUAL_HIGH = "EQH"           # Equal High
    EQUAL_LOW = "EQL"            # Equal Low


class StructureBreakType(Enum):
    """💥 Structure break types"""
    BOS = "BREAK_OF_STRUCTURE"          # Break of Structure
    CHOCH = "CHANGE_OF_CHARACTER"       # Change of Character
    MSB = "MARKET_STRUCTURE_BREAK"      # Market Structure Break
    LIQUIDITY_SWEEP = "LIQUIDITY_SWEEP" # Liquidity Sweep


@dataclass
class SupportResistanceLevel:
    """📏 Support/Resistance level data"""
    level_id: str
    price: float
    level_type: str  # "SUPPORT" or "RESISTANCE"
    strength: float  # 0-100
    touch_count: int
    last_touch: datetime
    created_timestamp: datetime
    timeframe: str
    confluence_factors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StructurePoint:
    """🏗️ Market structure point"""
    point_id: str
    price: float
    timestamp: datetime
    structure_type: StructureType
    significance: float  # 0-100
    confirmed: bool
    timeframe: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StructureBreak:
    """💥 Structure break event"""
    break_id: str
    break_type: StructureBreakType
    broken_level: float
    break_price: float
    break_timestamp: datetime
    strength: float  # 0-100
    follow_through: float  # 0-100
    timeframe: str
    direction: str  # "BULLISH" or "BEARISH"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketStructureAnalysis:
    """📊 Complete market structure analysis"""
    analysis_id: str
    symbol: str
    timeframe: str
    current_phase: MarketPhase
    trend_direction: TrendDirection
    structure_points: List[StructurePoint]
    support_levels: List[SupportResistanceLevel]
    resistance_levels: List[SupportResistanceLevel]
    recent_breaks: List[StructureBreak]
    phase_confidence: float  # 0-100
    trend_strength: float   # 0-100
    next_key_level: Optional[float]
    expected_direction: Optional[str]
    analysis_timestamp: datetime
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class MarketStructureIntelligence:
    """
    📊 MARKET STRUCTURE INTELLIGENCE v6.1
    Advanced market structure analysis with ICT methodology
    """
    
    def __init__(self):
        """Initialize Market Structure Intelligence with centralized logging"""
        # Smart logging integration - Usar siempre función centralizada
        self.logger = get_smart_logger("MarketStructureIntelligence")
        
        # Black box logging
        self.black_box = get_black_box_logger() if BLACK_BOX_AVAILABLE else None
        
        # Performance tracking
        self.lock = threading.Lock()
        self.analysis_count = 0
        self.total_processing_time = 0.0
        
        # Structure detection parameters
        self.structure_sensitivity = 0.002  # 20 pips for major pairs
        self.min_structure_distance = 50    # Minimum candles between structures
        self.sr_level_strength_threshold = 0.7
        
        # Session statistics
        self.session_stats = {
            'total_analyses': 0,
            'phases_detected': {},
            'structure_breaks_detected': 0,
            'avg_processing_time_ms': 0.0,
            'accuracy_metrics': {}
        }
        
        # Cache for recent analyses
        self.analysis_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Initialization logging con sistema centralizado
        log_info("📊 Market Structure Intelligence v6.1 initialized", "MSI")
        self.logger.info("📊 Market Structure Intelligence v6.1 initialized")
        if self.black_box:
            self.black_box.log_health_status("MarketStructureIntelligence", {
                "status": "initialized", 
                "version": "v6.1",
                "logging_system": "centralized" if SLUC_AVAILABLE else "fallback",
                "timestamp": datetime.now().isoformat()
            })
    
    def analyze_market_structure(self, candles, symbol: str, timeframe: str) -> MarketStructureAnalysis:
        """
        📊 Main market structure analysis method
        
        Args:
            candles: OHLC price data (pandas DataFrame)
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            MarketStructureAnalysis: Complete market structure analysis
        """
        start_time = time.time()
        analysis_id = f"MSA_{symbol}_{timeframe}_{int(time.time())}"
        
        try:
            # Logging centralizado para análisis crítico
            log_info(f"📊 Starting market structure analysis: {symbol} {timeframe}", "MSI")
            self.logger.info(f"📊 Starting market structure analysis: {symbol} {timeframe}")
            
            # Convert to DataFrame if needed
            if not isinstance(candles, pd.DataFrame):
                candles = pd.DataFrame(candles)
            
            # 1. Identify structure points (HH, HL, LH, LL)
            structure_points = self._identify_structure_points(candles, timeframe, symbol)
            
            # 2. Determine trend direction
            trend_direction = self._determine_trend_direction(structure_points)
            
            # 3. Detect market phase
            current_phase, phase_confidence = self._detect_market_phase(candles, structure_points, trend_direction)
            
            # 4. Identify support/resistance levels
            support_levels, resistance_levels = self._identify_sr_levels(candles, structure_points, timeframe)
            
            # 5. Detect recent structure breaks
            recent_breaks = self._detect_structure_breaks(candles, structure_points, timeframe)
            
            # 6. Calculate trend strength
            trend_strength = self._calculate_trend_strength(structure_points, recent_breaks)
            
            # 7. Predict next key level and direction
            next_key_level, expected_direction = self._predict_next_move(
                candles, structure_points, support_levels, resistance_levels
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            # Create market structure analysis
            analysis = MarketStructureAnalysis(
                analysis_id=analysis_id,
                symbol=symbol,
                timeframe=timeframe,
                current_phase=current_phase,
                trend_direction=trend_direction,
                structure_points=structure_points,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                recent_breaks=recent_breaks,
                phase_confidence=phase_confidence,
                trend_strength=trend_strength,
                next_key_level=next_key_level,
                expected_direction=expected_direction,
                analysis_timestamp=datetime.now(),
                processing_time_ms=processing_time,
                metadata={
                    'candle_count': len(candles),
                    'structure_count': len(structure_points),
                    'sr_levels_count': len(support_levels) + len(resistance_levels),
                    'breaks_count': len(recent_breaks),
                    'version': '6.1'
                }
            )
            
            # Update session statistics
            self._update_session_stats(analysis, processing_time)
            
            # Cache analysis
            self._cache_analysis(analysis)
            
            # Log results con sistema centralizado
            success_msg = (
                f"📊 Market structure analysis completed: {len(structure_points)} structures | "
                f"Phase: {current_phase.value} | Trend: {trend_direction.value} | "
                f"{processing_time:.2f}ms"
            )
            log_info(success_msg, "MSI")
            self.logger.info(success_msg)
            
            if self.black_box:
                self.black_box.log_market_structure_analysis(analysis)
            
            return analysis
            
        except Exception as e:
            # Error logging con sistema centralizado
            error_msg = f"❌ Error in market structure analysis: {e}"
            log_error(error_msg, "MSI")
            self.logger.error(error_msg)
            processing_time = (time.time() - start_time) * 1000
            
            # Return basic analysis on error
            return MarketStructureAnalysis(
                analysis_id=analysis_id,
                symbol=symbol,
                timeframe=timeframe,
                current_phase=MarketPhase.UNKNOWN,
                trend_direction=TrendDirection.SIDEWAYS,
                structure_points=[],
                support_levels=[],
                resistance_levels=[],
                recent_breaks=[],
                phase_confidence=0.0,
                trend_strength=0.0,
                next_key_level=None,
                expected_direction=None,
                analysis_timestamp=datetime.now(),
                processing_time_ms=processing_time,
                metadata={'error': str(e)}
            )
    
    def _identify_structure_points(self, candles: pd.DataFrame, timeframe: str, symbol: str = "UNKNOWN") -> List[StructurePoint]:
        """🏗️ Identify market structure points (HH, HL, LH, LL)"""
        structure_points = []
        
        if len(candles) < 10:
            return structure_points
        
        try:
            # Find swing highs and lows
            highs = candles['high'].values
            lows = candles['low'].values
            timestamps = candles.index
            
            # Identify swing points using simple peak/trough detection
            swing_highs = []
            swing_lows = []
            
            for i in range(2, len(candles) - 2):
                # Swing high: higher than previous 2 and next 2 highs
                if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                    highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                    swing_highs.append((i, highs[i], timestamps[i]))
                
                # Swing low: lower than previous 2 and next 2 lows
                if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                    lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                    swing_lows.append((i, lows[i], timestamps[i]))
            
            # Classify structure points
            for i, (idx, price, timestamp) in enumerate(swing_highs):
                if i > 0:
                    prev_high = swing_highs[i-1][1]
                    if price > prev_high:
                        structure_type = StructureType.HIGHER_HIGH
                    elif abs(price - prev_high) / prev_high < 0.001:  # Within 0.1%
                        structure_type = StructureType.EQUAL_HIGH
                    else:
                        structure_type = StructureType.LOWER_HIGH
                else:
                    structure_type = StructureType.HIGHER_HIGH  # First high
                
                structure_points.append(StructurePoint(
                    point_id=f"SP_H_{symbol}_{timeframe}_{idx}",
                    price=price,
                    timestamp=timestamp,
                    structure_type=structure_type,
                    significance=self._calculate_structure_significance(price, np.array(highs)),
                    confirmed=True,
                    timeframe=timeframe,
                    metadata={'type': 'swing_high', 'index': idx}
                ))
            
            for i, (idx, price, timestamp) in enumerate(swing_lows):
                if i > 0:
                    prev_low = swing_lows[i-1][1]
                    if price < prev_low:
                        structure_type = StructureType.LOWER_LOW
                    elif abs(price - prev_low) / prev_low < 0.001:  # Within 0.1%
                        structure_type = StructureType.EQUAL_LOW
                    else:
                        structure_type = StructureType.HIGHER_LOW
                else:
                    structure_type = StructureType.LOWER_LOW  # First low
                
                structure_points.append(StructurePoint(
                    point_id=f"SP_L_{symbol}_{timeframe}_{idx}",
                    price=price,
                    timestamp=timestamp,
                    structure_type=structure_type,
                    significance=self._calculate_structure_significance(price, np.array(lows)),
                    confirmed=True,
                    timeframe=timeframe,
                    metadata={'type': 'swing_low', 'index': idx}
                ))
            
            # Sort by timestamp
            structure_points.sort(key=lambda x: x.timestamp)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error identifying structure points: {e}")
        
        return structure_points
    
    def _determine_trend_direction(self, structure_points: List[StructurePoint]) -> TrendDirection:
        """📈 Determine overall trend direction from structure points"""
        if len(structure_points) < 4:
            return TrendDirection.SIDEWAYS
        
        # Count recent structure types (last 6 points)
        recent_points = structure_points[-6:] if len(structure_points) >= 6 else structure_points
        
        hh_count = sum(1 for p in recent_points if p.structure_type == StructureType.HIGHER_HIGH)
        hl_count = sum(1 for p in recent_points if p.structure_type == StructureType.HIGHER_LOW)
        lh_count = sum(1 for p in recent_points if p.structure_type == StructureType.LOWER_HIGH)
        ll_count = sum(1 for p in recent_points if p.structure_type == StructureType.LOWER_LOW)
        
        bullish_signals = hh_count + hl_count
        bearish_signals = lh_count + ll_count
        
        if bullish_signals > bearish_signals * 1.5:
            return TrendDirection.BULLISH
        elif bearish_signals > bullish_signals * 1.5:
            return TrendDirection.BEARISH
        elif abs(bullish_signals - bearish_signals) <= 1:
            return TrendDirection.SIDEWAYS
        else:
            return TrendDirection.TRANSITIONING
    
    def _detect_market_phase(self, candles: pd.DataFrame, structure_points: List[StructurePoint], 
                           trend_direction: TrendDirection) -> Tuple[MarketPhase, float]:
        """📊 Detect current market phase using ICT methodology"""
        if len(candles) < 20:
            return MarketPhase.UNKNOWN, 0.0
        
        try:
            # Analyze recent price action (last 20 candles)
            recent_candles = candles.tail(20)
            
            # Volume analysis (if available)
            volume_increasing = False
            if 'volume' in recent_candles.columns:
                recent_volume = recent_candles['volume'].rolling(5).mean()
                volume_increasing = recent_volume.iloc[-1] > recent_volume.iloc[-5]
            
            # Range analysis
            recent_range = recent_candles['high'].max() - recent_candles['low'].min()
            avg_range = (recent_candles['high'] - recent_candles['low']).mean()
            range_expansion = recent_range > avg_range * 1.5
            
            # Structure analysis
            recent_structures = [p for p in structure_points if p.timestamp >= recent_candles.index[0]]
            structure_count = len(recent_structures)
            
            # Phase detection logic
            if trend_direction == TrendDirection.SIDEWAYS and structure_count <= 2:
                if volume_increasing:
                    return MarketPhase.ACCUMULATION, 75.0
                else:
                    return MarketPhase.REBALANCE, 60.0
            
            elif range_expansion and structure_count >= 3:
                if trend_direction in [TrendDirection.BULLISH, TrendDirection.BEARISH]:
                    return MarketPhase.DISTRIBUTION, 80.0
                else:
                    return MarketPhase.MANIPULATION, 70.0
            
            elif trend_direction == TrendDirection.TRANSITIONING:
                return MarketPhase.MANIPULATION, 65.0
            
            else:
                # Default based on trend
                if trend_direction == TrendDirection.BULLISH:
                    return MarketPhase.DISTRIBUTION, 50.0
                elif trend_direction == TrendDirection.BEARISH:
                    return MarketPhase.DISTRIBUTION, 50.0
                else:
                    return MarketPhase.REBALANCE, 40.0
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Error detecting market phase: {e}")
            return MarketPhase.UNKNOWN, 0.0
    
    def _identify_sr_levels(self, candles: pd.DataFrame, structure_points: List[StructurePoint], 
                          timeframe: str) -> Tuple[List[SupportResistanceLevel], List[SupportResistanceLevel]]:
        """📏 Identify support and resistance levels"""
        support_levels = []
        resistance_levels = []
        
        try:
            # Extract swing highs and lows from structure points
            swing_highs = [p.price for p in structure_points if 'swing_high' in p.metadata.get('type', '')]
            swing_lows = [p.price for p in structure_points if 'swing_low' in p.metadata.get('type', '')]
            
            # Identify resistance levels from swing highs
            for i, high in enumerate(swing_highs):
                touch_count = sum(1 for h in swing_highs if abs(h - high) / high < 0.001)
                if touch_count >= 2:  # At least 2 touches
                    strength = min(100.0, touch_count * 25.0)
                    
                    resistance_levels.append(SupportResistanceLevel(
                        level_id=f"R_{timeframe}_{i}",
                        price=high,
                        level_type="RESISTANCE",
                        strength=strength,
                        touch_count=touch_count,
                        last_touch=datetime.now(),
                        created_timestamp=datetime.now(),
                        timeframe=timeframe,
                        confluence_factors=['swing_high', 'multiple_touches']
                    ))
            
            # Identify support levels from swing lows
            for i, low in enumerate(swing_lows):
                touch_count = sum(1 for l in swing_lows if abs(l - low) / low < 0.001)
                if touch_count >= 2:  # At least 2 touches
                    strength = min(100.0, touch_count * 25.0)
                    
                    support_levels.append(SupportResistanceLevel(
                        level_id=f"S_{timeframe}_{i}",
                        price=low,
                        level_type="SUPPORT",
                        strength=strength,
                        touch_count=touch_count,
                        last_touch=datetime.now(),
                        created_timestamp=datetime.now(),
                        timeframe=timeframe,
                        confluence_factors=['swing_low', 'multiple_touches']
                    ))
            
            # Sort by strength
            support_levels.sort(key=lambda x: x.strength, reverse=True)
            resistance_levels.sort(key=lambda x: x.strength, reverse=True)
            
            # Keep only top levels
            support_levels = support_levels[:5]
            resistance_levels = resistance_levels[:5]
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error identifying S/R levels: {e}")
        
        return support_levels, resistance_levels
    
    def _detect_structure_breaks(self, candles: pd.DataFrame, structure_points: List[StructurePoint], 
                               timeframe: str) -> List[StructureBreak]:
        """💥 Detect recent structure breaks"""
        structure_breaks = []
        
        # TODO: Implement sophisticated structure break detection
        # This is a placeholder for structure break logic
        
        return structure_breaks
    
    def _calculate_trend_strength(self, structure_points: List[StructurePoint], 
                                recent_breaks: List[StructureBreak]) -> float:
        """💪 Calculate trend strength"""
        if not structure_points:
            return 0.0
        
        # Base strength from structure consistency
        recent_points = structure_points[-6:] if len(structure_points) >= 6 else structure_points
        
        # Count consistent structures
        bullish_structures = sum(1 for p in recent_points if p.structure_type in [
            StructureType.HIGHER_HIGH, StructureType.HIGHER_LOW
        ])
        bearish_structures = sum(1 for p in recent_points if p.structure_type in [
            StructureType.LOWER_HIGH, StructureType.LOWER_LOW
        ])
        
        total_structures = len(recent_points)
        if total_structures == 0:
            return 0.0
        
        consistency_ratio = max(bullish_structures, bearish_structures) / total_structures
        base_strength = consistency_ratio * 100
        
        # Boost strength with recent breaks
        break_boost = min(20.0, len(recent_breaks) * 10.0)
        
        trend_strength = base_strength + break_boost
        return min(100.0, max(0.0, trend_strength))
    
    def _predict_next_move(self, candles: pd.DataFrame, structure_points: List[StructurePoint],
                         support_levels: List[SupportResistanceLevel], 
                         resistance_levels: List[SupportResistanceLevel]) -> Tuple[Optional[float], Optional[str]]:
        """🔮 Predict next key level and direction"""
        if not candles.empty:
            current_price = candles['close'].iloc[-1]
            
            # Find nearest levels
            nearest_resistance = None
            nearest_support = None
            
            for level in resistance_levels:
                if level.price > current_price:
                    if nearest_resistance is None or level.price < nearest_resistance:
                        nearest_resistance = level.price
            
            for level in support_levels:
                if level.price < current_price:
                    if nearest_support is None or level.price > nearest_support:
                        nearest_support = level.price
            
            # Determine next key level and direction
            if nearest_resistance and nearest_support:
                resistance_distance = abs(nearest_resistance - current_price)
                support_distance = abs(current_price - nearest_support)
                
                if resistance_distance < support_distance:
                    return nearest_resistance, "BULLISH"
                else:
                    return nearest_support, "BEARISH"
            elif nearest_resistance:
                return nearest_resistance, "BULLISH"
            elif nearest_support:
                return nearest_support, "BEARISH"
        
        return None, None
    
    def _calculate_structure_significance(self, price: float, price_array: np.ndarray) -> float:
        """📊 Calculate structure point significance"""
        # Simple significance based on price position in recent range
        recent_prices = price_array[-50:] if len(price_array) >= 50 else price_array
        price_range = recent_prices.max() - recent_prices.min()
        
        if price_range == 0:
            return 50.0
        
        # Normalize price position
        price_position = (price - recent_prices.min()) / price_range
        
        # Higher significance for extreme levels
        if price_position > 0.8 or price_position < 0.2:
            return 80.0
        elif price_position > 0.7 or price_position < 0.3:
            return 60.0
        else:
            return 40.0
    
    def _update_session_stats(self, analysis: MarketStructureAnalysis, processing_time: float) -> None:
        """📊 Update session statistics"""
        with self.lock:
            self.session_stats['total_analyses'] += 1
            
            # Track phases
            phase = analysis.current_phase.value
            if phase not in self.session_stats['phases_detected']:
                self.session_stats['phases_detected'][phase] = 0
            self.session_stats['phases_detected'][phase] += 1
            
            # Track structure breaks
            self.session_stats['structure_breaks_detected'] += len(analysis.recent_breaks)
            
            # Update processing time average
            self.total_processing_time += processing_time
            self.analysis_count += 1
            self.session_stats['avg_processing_time_ms'] = self.total_processing_time / self.analysis_count
    
    def _cache_analysis(self, analysis: MarketStructureAnalysis) -> None:
        """💾 Cache analysis for performance"""
        cache_key = f"{analysis.symbol}_{analysis.timeframe}"
        self.analysis_cache[cache_key] = {
            'analysis': analysis,
            'timestamp': time.time()
        }
        
        # Cleanup old cache entries
        current_time = time.time()
        keys_to_remove = [
            key for key, value in self.analysis_cache.items()
            if current_time - value['timestamp'] > self.cache_ttl
        ]
        for key in keys_to_remove:
            del self.analysis_cache[key]
    
    def get_session_stats(self) -> Dict[str, Any]:
        """📊 Get session statistics"""
        return self.session_stats.copy()


# Singleton pattern for global access
_market_structure_instance = None
_market_structure_lock = threading.Lock()


def get_market_structure_intelligence() -> MarketStructureIntelligence:
    """📊 Get Market Structure Intelligence singleton instance"""
    global _market_structure_instance
    
    if _market_structure_instance is None:
        with _market_structure_lock:
            if _market_structure_instance is None:
                _market_structure_instance = MarketStructureIntelligence()
    
    return _market_structure_instance


if __name__ == "__main__":
    # Basic test
    intelligence = get_market_structure_intelligence()
    print("📊 Market Structure Intelligence v6.1 test completed")
