"""
🧠 PATTERN CONFLUENCE ENGINE v6.1
Advanced multi-pattern analysis system

PHASE 1 - DAY 3 Implementation:
- Combine FVG + Order Blocks + Smart Money patterns
- Multi-pattern scoring algorithm
- Confluence strength calculation  
- Decision confidence matrix
- Real-time confluence updates

Dependencies:
- FairValueGapDetector (Enterprise v6.1)
- EnhancedOrderBlockDetector (v6.1) 
- SmartMoneyDetector (v6.1)
- UnifiedMemorySystem (v6.1)
- Black Box Logger (v6.1)
"""

import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np

# Enterprise logging integration
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from smart_trading_logger import get_smart_logger
    SLUC_AVAILABLE = True
except ImportError:
    SLUC_AVAILABLE = False
    logging.basicConfig(level=logging.INFO)

# Black box logging
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "05-LOGS" / "black_box_analysis"))
    from black_box_logger import get_black_box_logger
    BLACK_BOX_AVAILABLE = True
except ImportError:
    BLACK_BOX_AVAILABLE = False

# Pattern detectors integration
try:
    from smart_money_concepts.fair_value_gaps import FairValueGapDetector, FairValueGap
    from smart_money_concepts.order_blocks import EnhancedOrderBlockDetector
    from smart_money_concepts.smart_money_detector import SmartMoneyDetector
    PATTERN_DETECTORS_AVAILABLE = True
except ImportError:
    PATTERN_DETECTORS_AVAILABLE = False

# Memory system integration
try:
    from analysis.unified_memory_system import get_unified_memory_system
    MEMORY_SYSTEM_AVAILABLE = True
except ImportError:
    MEMORY_SYSTEM_AVAILABLE = False


class ConfluenceStrength(Enum):
    """🎯 Confluence strength levels"""
    WEAK = "WEAK"           # 0-30
    MODERATE = "MODERATE"   # 31-60
    STRONG = "STRONG"       # 61-80
    EXTREME = "EXTREME"     # 81-100


class PatternType(Enum):
    """📊 Pattern types for confluence analysis"""
    FVG = "FAIR_VALUE_GAP"
    ORDER_BLOCK = "ORDER_BLOCK"
    SMART_MONEY = "SMART_MONEY"
    LIQUIDITY_SWEEP = "LIQUIDITY_SWEEP"
    BOS_CHOCH = "BOS_CHOCH"


class MarketBias(Enum):
    """📈 Market bias determination"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    CONFLICTED = "CONFLICTED"


@dataclass
class PatternConfluence:
    """🔗 Individual pattern confluence data"""
    pattern_type: PatternType
    pattern_id: str
    confidence: float
    strength: float
    direction: str
    price_level: float
    timeframe: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfluenceAnalysis:
    """🧠 Complete confluence analysis result"""
    confluence_id: str
    overall_strength: float
    strength_level: ConfluenceStrength
    market_bias: MarketBias
    dominant_patterns: List[PatternType]
    supporting_patterns: List[PatternType]
    conflicting_patterns: List[PatternType]
    pattern_confluences: List[PatternConfluence]
    decision_confidence: float
    recommended_action: str
    price_target: Optional[float]
    stop_loss: Optional[float]
    risk_reward_ratio: Optional[float]
    analysis_timestamp: datetime
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class PatternConfluenceEngine:
    """
    🧠 PATTERN CONFLUENCE ENGINE v6.1
    Advanced multi-pattern analysis system for trading decisions
    """
    
    def __init__(self):
        """Initialize Pattern Confluence Engine"""
        # Smart logging integration
        if SLUC_AVAILABLE:
            self.logger = get_smart_logger("PatternConfluenceEngine")
        else:
            self.logger = logging.getLogger("PatternConfluenceEngine")
        
        # Black box logging
        self.black_box = get_black_box_logger() if BLACK_BOX_AVAILABLE else None
        
        # Memory system integration
        self.memory_system = get_unified_memory_system() if MEMORY_SYSTEM_AVAILABLE else None
        
        # Pattern detectors
        self.fvg_detector = FairValueGapDetector() if PATTERN_DETECTORS_AVAILABLE else None
        self.order_block_detector = None  # Will be initialized if available
        self.smart_money_detector = None  # Will be initialized if available
        
        # Performance tracking
        self.lock = threading.Lock()
        self.analysis_count = 0
        self.total_processing_time = 0.0
        
        # Confluence weights (adaptive learning will modify these)
        self.pattern_weights = {
            PatternType.FVG: 0.25,
            PatternType.ORDER_BLOCK: 0.30,
            PatternType.SMART_MONEY: 0.25,
            PatternType.LIQUIDITY_SWEEP: 0.10,
            PatternType.BOS_CHOCH: 0.10
        }
        
        # Session statistics
        self.session_stats = {
            'total_analyses': 0,
            'strong_confluences': 0,
            'successful_predictions': 0,
            'avg_processing_time_ms': 0.0,
            'pattern_success_rates': {}
        }
        
        self.logger.info("🧠 Pattern Confluence Engine v6.1 initialized")
        if self.black_box:
            self.black_box.log_system_event("PatternConfluenceEngine_v6.1_Initialized")
    
    def analyze_confluence(self, candles, symbol: str, timeframe: str) -> ConfluenceAnalysis:
        """
        🎯 Main confluence analysis method
        
        Args:
            candles: OHLC price data
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            ConfluenceAnalysis: Complete confluence analysis
        """
        start_time = time.time()
        confluence_id = f"CONF_{symbol}_{timeframe}_{int(time.time())}"
        
        try:
            self.logger.info(f"🧠 Starting confluence analysis: {symbol} {timeframe}")
            
            # Collect patterns from all detectors
            pattern_confluences = []
            
            # 1. Fair Value Gap patterns
            fvg_confluences = self._analyze_fvg_patterns(candles, symbol, timeframe)
            pattern_confluences.extend(fvg_confluences)
            
            # 2. Order Block patterns
            ob_confluences = self._analyze_order_block_patterns(candles, symbol, timeframe)
            pattern_confluences.extend(ob_confluences)
            
            # 3. Smart Money patterns
            sm_confluences = self._analyze_smart_money_patterns(candles, symbol, timeframe)
            pattern_confluences.extend(sm_confluences)
            
            # Calculate overall confluence strength
            overall_strength = self._calculate_overall_strength(pattern_confluences)
            strength_level = self._determine_strength_level(overall_strength)
            
            # Determine market bias
            market_bias = self._determine_market_bias(pattern_confluences)
            
            # Categorize patterns
            dominant_patterns, supporting_patterns, conflicting_patterns = self._categorize_patterns(pattern_confluences)
            
            # Calculate decision confidence
            decision_confidence = self._calculate_decision_confidence(pattern_confluences, overall_strength)
            
            # Generate recommendations
            recommended_action, price_target, stop_loss, risk_reward = self._generate_recommendations(
                pattern_confluences, market_bias, overall_strength
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            # Create confluence analysis
            confluence_analysis = ConfluenceAnalysis(
                confluence_id=confluence_id,
                overall_strength=overall_strength,
                strength_level=strength_level,
                market_bias=market_bias,
                dominant_patterns=dominant_patterns,
                supporting_patterns=supporting_patterns,
                conflicting_patterns=conflicting_patterns,
                pattern_confluences=pattern_confluences,
                decision_confidence=decision_confidence,
                recommended_action=recommended_action,
                price_target=price_target,
                stop_loss=stop_loss,
                risk_reward_ratio=risk_reward,
                analysis_timestamp=datetime.now(),
                processing_time_ms=processing_time,
                metadata={
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'pattern_count': len(pattern_confluences),
                    'engine_version': '6.1'
                }
            )
            
            # Update statistics
            self._update_session_stats(confluence_analysis, processing_time)
            
            # Memory enhancement
            if self.memory_system:
                self._enhance_with_memory(confluence_analysis)
            
            # Log results
            self.logger.info(
                f"🧠 Confluence analysis completed: {len(pattern_confluences)} patterns | "
                f"Strength: {overall_strength:.1f} | Bias: {market_bias.value} | "
                f"{processing_time:.2f}ms"
            )
            
            if self.black_box:
                self.black_box.log_confluence_analysis(confluence_analysis)
            
            return confluence_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error in confluence analysis: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            # Return empty analysis on error
            return ConfluenceAnalysis(
                confluence_id=confluence_id,
                overall_strength=0.0,
                strength_level=ConfluenceStrength.WEAK,
                market_bias=MarketBias.NEUTRAL,
                dominant_patterns=[],
                supporting_patterns=[],
                conflicting_patterns=[],
                pattern_confluences=[],
                decision_confidence=0.0,
                recommended_action="WAIT",
                price_target=None,
                stop_loss=None,
                risk_reward_ratio=None,
                analysis_timestamp=datetime.now(),
                processing_time_ms=processing_time,
                metadata={'error': str(e)}
            )
    
    def _analyze_fvg_patterns(self, candles, symbol: str, timeframe: str) -> List[PatternConfluence]:
        """📊 Analyze Fair Value Gap patterns"""
        fvg_confluences = []
        
        if not self.fvg_detector:
            return fvg_confluences
        
        try:
            # Detect FVGs
            fvgs = self.fvg_detector.detect_fair_value_gaps(candles, symbol, timeframe)
            
            for fvg in fvgs:
                confluence = PatternConfluence(
                    pattern_type=PatternType.FVG,
                    pattern_id=fvg.fvg_id,
                    confidence=fvg.confidence,
                    strength=fvg.score,
                    direction=fvg.direction.value,
                    price_level=(fvg.high_price + fvg.low_price) / 2,
                    timeframe=timeframe,
                    timestamp=fvg.timestamp,
                    metadata={
                        'gap_size_pips': fvg.gap_pips,
                        'fill_percentage': fvg.fill_percentage,
                        'status': fvg.status.value,
                        'confluences': fvg.confluences
                    }
                )
                fvg_confluences.append(confluence)
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error analyzing FVG patterns: {e}")
        
        return fvg_confluences
    
    def _analyze_order_block_patterns(self, candles, symbol: str, timeframe: str) -> List[PatternConfluence]:
        """🏗️ Analyze Order Block patterns"""
        ob_confluences = []
        
        # TODO: Integrate with EnhancedOrderBlockDetector when available
        # This is a placeholder for Order Block analysis
        
        return ob_confluences
    
    def _analyze_smart_money_patterns(self, candles, symbol: str, timeframe: str) -> List[PatternConfluence]:
        """💰 Analyze Smart Money patterns"""
        sm_confluences = []
        
        # TODO: Integrate with SmartMoneyDetector when available
        # This is a placeholder for Smart Money analysis
        
        return sm_confluences
    
    def _calculate_overall_strength(self, pattern_confluences: List[PatternConfluence]) -> float:
        """📊 Calculate overall confluence strength"""
        if not pattern_confluences:
            return 0.0
        
        total_weighted_strength = 0.0
        total_weight = 0.0
        
        for confluence in pattern_confluences:
            weight = self.pattern_weights.get(confluence.pattern_type, 0.1)
            weighted_strength = confluence.strength * confluence.confidence * weight
            total_weighted_strength += weighted_strength
            total_weight += weight
        
        overall_strength = (total_weighted_strength / total_weight) if total_weight > 0 else 0.0
        return min(100.0, max(0.0, overall_strength))
    
    def _determine_strength_level(self, overall_strength: float) -> ConfluenceStrength:
        """🎯 Determine confluence strength level"""
        if overall_strength >= 81:
            return ConfluenceStrength.EXTREME
        elif overall_strength >= 61:
            return ConfluenceStrength.STRONG
        elif overall_strength >= 31:
            return ConfluenceStrength.MODERATE
        else:
            return ConfluenceStrength.WEAK
    
    def _determine_market_bias(self, pattern_confluences: List[PatternConfluence]) -> MarketBias:
        """📈 Determine overall market bias"""
        if not pattern_confluences:
            return MarketBias.NEUTRAL
        
        bullish_weight = 0.0
        bearish_weight = 0.0
        
        for confluence in pattern_confluences:
            weight = self.pattern_weights.get(confluence.pattern_type, 0.1) * confluence.confidence
            
            if confluence.direction.upper() in ['BULLISH', 'BUY', 'UP']:
                bullish_weight += weight
            elif confluence.direction.upper() in ['BEARISH', 'SELL', 'DOWN']:
                bearish_weight += weight
        
        total_weight = bullish_weight + bearish_weight
        if total_weight == 0:
            return MarketBias.NEUTRAL
        
        bias_ratio = abs(bullish_weight - bearish_weight) / total_weight
        
        if bias_ratio < 0.2:  # Very close, conflicted
            return MarketBias.CONFLICTED
        elif bias_ratio < 0.4:  # Close, neutral
            return MarketBias.NEUTRAL
        elif bullish_weight > bearish_weight:
            return MarketBias.BULLISH
        else:
            return MarketBias.BEARISH
    
    def _categorize_patterns(self, pattern_confluences: List[PatternConfluence]) -> Tuple[List[PatternType], List[PatternType], List[PatternType]]:
        """🏷️ Categorize patterns by influence"""
        if not pattern_confluences:
            return [], [], []
        
        # Sort by weighted strength
        weighted_patterns = [
            (conf.pattern_type, conf.strength * conf.confidence * self.pattern_weights.get(conf.pattern_type, 0.1))
            for conf in pattern_confluences
        ]
        weighted_patterns.sort(key=lambda x: x[1], reverse=True)
        
        total_patterns = len(weighted_patterns)
        dominant_count = max(1, total_patterns // 3)
        
        dominant_patterns = [p[0] for p in weighted_patterns[:dominant_count]]
        supporting_patterns = [p[0] for p in weighted_patterns[dominant_count:]]
        
        # TODO: Implement conflicting pattern logic
        conflicting_patterns = []
        
        return dominant_patterns, supporting_patterns, conflicting_patterns
    
    def _calculate_decision_confidence(self, pattern_confluences: List[PatternConfluence], overall_strength: float) -> float:
        """🎯 Calculate decision confidence"""
        if not pattern_confluences:
            return 0.0
        
        # Base confidence from overall strength
        base_confidence = overall_strength
        
        # Boost confidence with pattern count
        pattern_count_boost = min(20.0, len(pattern_confluences) * 5.0)
        
        # Boost confidence with pattern diversity
        unique_types = len(set(conf.pattern_type for conf in pattern_confluences))
        diversity_boost = min(15.0, unique_types * 3.0)
        
        decision_confidence = base_confidence + pattern_count_boost + diversity_boost
        return min(100.0, max(0.0, decision_confidence))
    
    def _generate_recommendations(self, pattern_confluences: List[PatternConfluence], 
                                market_bias: MarketBias, overall_strength: float) -> Tuple[str, Optional[float], Optional[float], Optional[float]]:
        """🎯 Generate trading recommendations"""
        # Default recommendations
        recommended_action = "WAIT"
        price_target = None
        stop_loss = None
        risk_reward = None
        
        # Only generate actionable recommendations for strong confluences
        if overall_strength >= 60 and market_bias in [MarketBias.BULLISH, MarketBias.BEARISH]:
            if market_bias == MarketBias.BULLISH:
                recommended_action = "BUY"
            else:
                recommended_action = "SELL"
            
            # TODO: Implement sophisticated price target and stop loss calculation
            # This is a placeholder for advanced recommendations
        
        return recommended_action, price_target, stop_loss, risk_reward
    
    def _update_session_stats(self, confluence_analysis: ConfluenceAnalysis, processing_time: float) -> None:
        """📊 Update session statistics"""
        with self.lock:
            self.session_stats['total_analyses'] += 1
            
            if confluence_analysis.strength_level in [ConfluenceStrength.STRONG, ConfluenceStrength.EXTREME]:
                self.session_stats['strong_confluences'] += 1
            
            # Update processing time average
            self.total_processing_time += processing_time
            self.analysis_count += 1
            self.session_stats['avg_processing_time_ms'] = self.total_processing_time / self.analysis_count
    
    def _enhance_with_memory(self, confluence_analysis: ConfluenceAnalysis) -> None:
        """🧠 Enhance analysis with memory system"""
        if not self.memory_system:
            return
        
        try:
            # Update memory with confluence analysis
            memory_data = {
                'pattern_type': 'confluence_analysis',
                'strength': confluence_analysis.overall_strength,
                'bias': confluence_analysis.market_bias.value,
                'confidence': confluence_analysis.decision_confidence,
                'pattern_count': len(confluence_analysis.pattern_confluences),
                'timestamp': confluence_analysis.analysis_timestamp,
                'processing_time_ms': confluence_analysis.processing_time_ms
            }
            
            # TODO: Implement memory enhancement logic
            # This is a placeholder for memory integration
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error enhancing with memory: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """📊 Get session statistics"""
        return self.session_stats.copy()


# Singleton pattern for global access
_confluence_engine_instance = None
_confluence_engine_lock = threading.Lock()


def get_confluence_engine() -> PatternConfluenceEngine:
    """🧠 Get Pattern Confluence Engine singleton instance"""
    global _confluence_engine_instance
    
    if _confluence_engine_instance is None:
        with _confluence_engine_lock:
            if _confluence_engine_instance is None:
                _confluence_engine_instance = PatternConfluenceEngine()
    
    return _confluence_engine_instance


if __name__ == "__main__":
    # Basic test
    engine = get_confluence_engine()
    print("🧠 Pattern Confluence Engine v6.1 test completed")
