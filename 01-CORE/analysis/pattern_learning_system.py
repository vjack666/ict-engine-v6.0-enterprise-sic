"""
🧠 PATTERN LEARNING SYSTEM v6.1
Adaptive pattern recognition with ML-enhanced analytics

PHASE 4 - DAY 3 Implementation:
- Adaptive pattern recognition with learning capabilities
- Pattern success rate tracking and optimization
- Machine learning integration for pattern enhancement
- Historical pattern performance analysis
- Predictive pattern scoring based on market conditions

Dependencies:
- PatternConfluenceEngine (v6.1)
- MarketStructureIntelligence (v6.1) 
- TradingSignalSynthesizer (v6.1)
- UnifiedMemorySystem (v6.1)
- Historical market data
"""

import time
import threading
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
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

# Analysis engines integration
try:
    from analysis.pattern_confluence_engine import get_confluence_engine, PatternType
    from analysis.market_structure_intelligence import get_market_structure_intelligence, MarketPhase
    from analysis.trading_signal_synthesizer import get_trading_signal_synthesizer, TradingSignal
    ANALYSIS_ENGINES_AVAILABLE = True
except ImportError:
    ANALYSIS_ENGINES_AVAILABLE = False


class LearningMode(Enum):
    """🧠 Learning modes"""
    PASSIVE = "PASSIVE"             # Observe and learn without trading
    ACTIVE = "ACTIVE"               # Learn while trading
    SIMULATION = "SIMULATION"       # Learn from simulation
    HISTORICAL = "HISTORICAL"       # Learn from historical data


class PatternConfidence(Enum):
    """🎯 Pattern confidence levels"""
    VERY_HIGH = "VERY_HIGH"         # 90-100%
    HIGH = "HIGH"                   # 75-89%
    MEDIUM = "MEDIUM"               # 50-74%
    LOW = "LOW"                     # 25-49%
    VERY_LOW = "VERY_LOW"           # 0-24%


class PatternOutcome(Enum):
    """📊 Pattern trade outcomes"""
    BIG_WIN = "BIG_WIN"             # >3R profit
    WIN = "WIN"                     # 1-3R profit
    SMALL_WIN = "SMALL_WIN"         # 0-1R profit
    BREAKEVEN = "BREAKEVEN"         # -0.2R to 0.2R
    SMALL_LOSS = "SMALL_LOSS"       # -1R to -0.2R
    LOSS = "LOSS"                   # -3R to -1R
    BIG_LOSS = "BIG_LOSS"           # <-3R loss


@dataclass
class PatternPerformanceData:
    """📊 Pattern performance tracking"""
    pattern_type: PatternType
    total_occurrences: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    total_profit_r: float = 0.0     # Total profit in R multiples
    total_loss_r: float = 0.0       # Total losses in R multiples
    win_rate: float = 0.0           # Percentage win rate
    avg_win_r: float = 0.0          # Average win in R
    avg_loss_r: float = 0.0         # Average loss in R
    profit_factor: float = 0.0      # Gross profit / Gross loss
    expectancy_r: float = 0.0       # Expected value per trade
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    last_performance_update: datetime = field(default_factory=datetime.now)
    performance_by_timeframe: Dict[str, Dict[str, float]] = field(default_factory=dict)
    performance_by_market_phase: Dict[str, Dict[str, float]] = field(default_factory=dict)
    confidence_score: float = 50.0  # Dynamic confidence based on performance


@dataclass
class MarketConditionContext:
    """🌍 Market condition context for learning"""
    volatility_regime: str          # HIGH, MEDIUM, LOW
    trend_strength: float           # 0-100
    market_phase: MarketPhase
    session_time: str              # LONDON, NEW_YORK, ASIAN, OVERLAP
    day_of_week: str               # MONDAY, TUESDAY, etc.
    news_impact_level: str         # HIGH, MEDIUM, LOW, NONE
    liquidity_condition: str       # HIGH, MEDIUM, LOW
    correlation_environment: str   # RISK_ON, RISK_OFF, MIXED


@dataclass
class PatternLearningRecord:
    """📝 Individual pattern learning record"""
    record_id: str
    pattern_type: PatternType
    symbol: str
    timeframe: str
    detection_timestamp: datetime
    pattern_strength: float
    confluence_score: float
    market_context: MarketConditionContext
    predicted_outcome: PatternOutcome
    predicted_confidence: PatternConfidence
    actual_outcome: Optional[PatternOutcome] = None
    actual_profit_r: Optional[float] = None
    outcome_timestamp: Optional[datetime] = None
    learning_feedback: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningInsight:
    """💡 Learning insights and recommendations"""
    insight_id: str
    insight_type: str              # PATTERN_IMPROVEMENT, MARKET_TIMING, CONFLUENCE_OPTIMIZATION
    pattern_types: List[PatternType]
    market_conditions: List[str]
    confidence_level: float
    recommendation: str
    supporting_evidence: List[str]
    potential_impact: str          # HIGH, MEDIUM, LOW
    implementation_priority: int   # 1-10
    created_timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class PatternLearningSystem:
    """
    🧠 PATTERN LEARNING SYSTEM v6.1
    Adaptive pattern recognition with ML-enhanced analytics
    """
    
    def __init__(self):
        """Initialize Pattern Learning System"""
        # Smart logging integration
        if SLUC_AVAILABLE:
            self.logger = get_smart_logger("PatternLearningSystem")
        else:
            self.logger = logging.getLogger("PatternLearningSystem")
        
        # Analysis engines
        self.confluence_engine = get_confluence_engine() if ANALYSIS_ENGINES_AVAILABLE else None
        self.structure_intelligence = get_market_structure_intelligence() if ANALYSIS_ENGINES_AVAILABLE else None
        self.signal_synthesizer = get_trading_signal_synthesizer() if ANALYSIS_ENGINES_AVAILABLE else None
        
        # Learning state
        self.learning_mode = LearningMode.ACTIVE
        self.lock = threading.Lock()
        
        # Performance tracking
        self.pattern_performance: Dict[PatternType, PatternPerformanceData] = {}
        self.learning_records: deque = deque(maxlen=10000)  # Keep last 10k records
        self.learning_insights: List[LearningInsight] = []
        
        # Learning parameters
        self.min_samples_for_confidence = 20    # Minimum samples for reliable statistics
        self.confidence_update_threshold = 10   # Update confidence every N new samples
        self.insight_generation_interval = 100  # Generate insights every N records
        
        # Market condition mapping
        self.session_times = {
            'ASIAN': (0, 8),      # UTC hours
            'LONDON': (8, 16),
            'NEW_YORK': (13, 21),
            'OVERLAP': [(8, 13), (16, 21)]
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            'excellent_win_rate': 70.0,
            'good_win_rate': 60.0,
            'minimum_win_rate': 40.0,
            'excellent_profit_factor': 2.0,
            'good_profit_factor': 1.5,
            'minimum_profit_factor': 1.2,
            'excellent_expectancy': 0.5,
            'good_expectancy': 0.2,
            'minimum_expectancy': 0.1
        }
        
        # Session statistics
        self.session_stats = {
            'total_learning_records': 0,
            'patterns_tracked': 0,
            'insights_generated': 0,
            'confidence_updates': 0,
            'learning_accuracy': 0.0,
            'avg_pattern_confidence': 0.0
        }
        
        # Initialize pattern performance tracking
        self._initialize_pattern_tracking()
        
        self.logger.info("🧠 Pattern Learning System v6.1 initialized")
    
    def _initialize_pattern_tracking(self) -> None:
        """📊 Initialize pattern performance tracking"""
        for pattern_type in PatternType:
            self.pattern_performance[pattern_type] = PatternPerformanceData(
                pattern_type=pattern_type
            )
    
    def record_pattern_detection(self, pattern_type: PatternType, symbol: str, timeframe: str,
                               pattern_strength: float, confluence_score: float, 
                               market_context: Optional[MarketConditionContext] = None) -> str:
        """
        📝 Record pattern detection for learning
        
        Args:
            pattern_type: Type of pattern detected
            symbol: Trading symbol
            timeframe: Analysis timeframe
            pattern_strength: Pattern strength (0-100)
            confluence_score: Confluence score (0-100)
            market_context: Market condition context
            
        Returns:
            str: Learning record ID
        """
        record_id = f"PLR_{pattern_type.value}_{symbol}_{int(time.time())}"
        
        try:
            # Generate market context if not provided
            if market_context is None:
                market_context = self._generate_market_context(symbol, timeframe)
            
            # Predict outcome based on current learning
            predicted_outcome, predicted_confidence = self._predict_pattern_outcome(
                pattern_type, pattern_strength, confluence_score, market_context
            )
            
            # Create learning record
            learning_record = PatternLearningRecord(
                record_id=record_id,
                pattern_type=pattern_type,
                symbol=symbol,
                timeframe=timeframe,
                detection_timestamp=datetime.now(),
                pattern_strength=pattern_strength,
                confluence_score=confluence_score,
                market_context=market_context,
                predicted_outcome=predicted_outcome,
                predicted_confidence=predicted_confidence,
                metadata={
                    'learning_system_version': '6.1',
                    'learning_mode': self.learning_mode.value
                }
            )
            
            # Store record
            with self.lock:
                self.learning_records.append(learning_record)
                self.session_stats['total_learning_records'] += 1
            
            self.logger.info(
                f"📝 Pattern recorded: {pattern_type.value} | {symbol} | "
                f"Strength: {pattern_strength:.1f} | Predicted: {predicted_outcome.value}"
            )
            
            return record_id
            
        except Exception as e:
            self.logger.error(f"❌ Error recording pattern detection: {e}")
            return record_id
    
    def update_pattern_outcome(self, record_id: str, actual_outcome: PatternOutcome, 
                             actual_profit_r: float, learning_feedback: Optional[str] = None) -> None:
        """
        📊 Update pattern outcome for learning
        
        Args:
            record_id: Learning record ID
            actual_outcome: Actual trade outcome
            actual_profit_r: Actual profit in R multiples
            learning_feedback: Optional feedback for learning
        """
        try:
            # Find the learning record
            learning_record = None
            with self.lock:
                for record in reversed(self.learning_records):
                    if record.record_id == record_id:
                        learning_record = record
                        break
            
            if not learning_record:
                self.logger.warning(f"⚠️ Learning record not found: {record_id}")
                return
            
            # Update outcome
            learning_record.actual_outcome = actual_outcome
            learning_record.actual_profit_r = actual_profit_r
            learning_record.outcome_timestamp = datetime.now()
            learning_record.learning_feedback = learning_feedback
            
            # Update pattern performance
            self._update_pattern_performance(learning_record)
            
            # Update pattern confidence
            self._update_pattern_confidence(learning_record.pattern_type)
            
            # Check for insight generation
            if self.session_stats['total_learning_records'] % self.insight_generation_interval == 0:
                self._generate_learning_insights()
            
            self.logger.info(
                f"📊 Outcome updated: {record_id} | {actual_outcome.value} | "
                f"R: {actual_profit_r:.2f}"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error updating pattern outcome: {e}")
    
    def _generate_market_context(self, symbol: str, timeframe: str) -> MarketConditionContext:
        """🌍 Generate market condition context"""
        now = datetime.now()
        
        # Basic context generation (can be enhanced with real market data)
        market_context = MarketConditionContext(
            volatility_regime="MEDIUM",
            trend_strength=50.0,
            market_phase=MarketPhase.ACCUMULATION,
            session_time=self._get_session_time(now),
            day_of_week=now.strftime("%A").upper(),
            news_impact_level="LOW",
            liquidity_condition="MEDIUM",
            correlation_environment="MIXED"
        )
        
        # Enhanced context with structure intelligence
        if self.structure_intelligence:
            try:
                # Get latest structure analysis (would need candle data in real implementation)
                # For now, use defaults
                pass
            except Exception as e:
                self.logger.debug(f"Could not enhance market context: {e}")
        
        return market_context
    
    def _get_session_time(self, timestamp: datetime) -> str:
        """🕐 Determine trading session based on timestamp"""
        hour = timestamp.hour
        
        if 0 <= hour < 8:
            return "ASIAN"
        elif 8 <= hour < 13:
            return "LONDON"
        elif 13 <= hour < 16:
            return "OVERLAP"
        elif 16 <= hour < 21:
            return "NEW_YORK"
        else:
            return "ASIAN"
    
    def _predict_pattern_outcome(self, pattern_type: PatternType, pattern_strength: float,
                               confluence_score: float, market_context: MarketConditionContext) -> Tuple[PatternOutcome, PatternConfidence]:
        """🔮 Predict pattern outcome based on learning"""
        try:
            # Get pattern performance data
            performance = self.pattern_performance.get(pattern_type)
            
            if not performance or performance.total_occurrences < self.min_samples_for_confidence:
                # Insufficient data, use default prediction
                if pattern_strength > 80 and confluence_score > 70:
                    return PatternOutcome.WIN, PatternConfidence.MEDIUM
                elif pattern_strength > 60 and confluence_score > 50:
                    return PatternOutcome.SMALL_WIN, PatternConfidence.LOW
                else:
                    return PatternOutcome.BREAKEVEN, PatternConfidence.VERY_LOW
            
            # Calculate prediction score based on historical performance and current conditions
            base_score = performance.win_rate
            
            # Adjust based on pattern strength
            strength_adjustment = (pattern_strength - 50) * 0.5
            
            # Adjust based on confluence
            confluence_adjustment = (confluence_score - 50) * 0.3
            
            # Adjust based on market context
            context_adjustment = self._calculate_context_adjustment(pattern_type, market_context)
            
            final_score = base_score + strength_adjustment + confluence_adjustment + context_adjustment
            final_score = max(0, min(100, final_score))
            
            # Determine predicted outcome
            if final_score > 75:
                predicted_outcome = PatternOutcome.WIN
                confidence = PatternConfidence.HIGH
            elif final_score > 60:
                predicted_outcome = PatternOutcome.SMALL_WIN
                confidence = PatternConfidence.MEDIUM
            elif final_score > 40:
                predicted_outcome = PatternOutcome.BREAKEVEN
                confidence = PatternConfidence.MEDIUM
            elif final_score > 25:
                predicted_outcome = PatternOutcome.SMALL_LOSS
                confidence = PatternConfidence.LOW
            else:
                predicted_outcome = PatternOutcome.LOSS
                confidence = PatternConfidence.VERY_LOW
            
            return predicted_outcome, confidence
            
        except Exception as e:
            self.logger.error(f"❌ Error predicting pattern outcome: {e}")
            return PatternOutcome.BREAKEVEN, PatternConfidence.VERY_LOW
    
    def _calculate_context_adjustment(self, pattern_type: PatternType, 
                                    market_context: MarketConditionContext) -> float:
        """🎯 Calculate adjustment based on market context"""
        adjustment = 0.0
        
        # Volatility adjustment
        if market_context.volatility_regime == "HIGH":
            adjustment += 5.0  # High volatility can be good for patterns
        elif market_context.volatility_regime == "LOW":
            adjustment -= 5.0  # Low volatility may reduce pattern effectiveness
        
        # Session time adjustment
        if market_context.session_time in ["LONDON", "NEW_YORK", "OVERLAP"]:
            adjustment += 3.0  # Active sessions
        else:
            adjustment -= 2.0  # Less active sessions
        
        # Market phase adjustment
        if market_context.market_phase == MarketPhase.ACCUMULATION:
            adjustment += 5.0  # Accumulation phase is good for patterns
        elif market_context.market_phase == MarketPhase.MANIPULATION:
            adjustment -= 3.0  # Manipulation can be challenging
        
        return adjustment
    
    def _update_pattern_performance(self, learning_record: PatternLearningRecord) -> None:
        """📊 Update pattern performance statistics"""
        pattern_type = learning_record.pattern_type
        performance = self.pattern_performance[pattern_type]
        
        with self.lock:
            # Update basic counts
            performance.total_occurrences += 1
            
            # Classify outcome
            if learning_record.actual_outcome in [PatternOutcome.BIG_WIN, PatternOutcome.WIN, PatternOutcome.SMALL_WIN]:
                performance.successful_trades += 1
                if learning_record.actual_profit_r is not None:
                    performance.total_profit_r += learning_record.actual_profit_r
            else:
                performance.failed_trades += 1
                if learning_record.actual_profit_r is not None:
                    performance.total_loss_r += abs(learning_record.actual_profit_r)
            
            # Calculate metrics
            if performance.total_occurrences > 0:
                performance.win_rate = (performance.successful_trades / performance.total_occurrences) * 100
            
            if performance.successful_trades > 0:
                performance.avg_win_r = performance.total_profit_r / performance.successful_trades
            
            if performance.failed_trades > 0:
                performance.avg_loss_r = performance.total_loss_r / performance.failed_trades
            
            if performance.total_loss_r > 0:
                performance.profit_factor = performance.total_profit_r / performance.total_loss_r
            
            # Calculate expectancy
            if performance.total_occurrences > 0:
                win_prob = performance.successful_trades / performance.total_occurrences
                lose_prob = performance.failed_trades / performance.total_occurrences
                performance.expectancy_r = (win_prob * performance.avg_win_r) - (lose_prob * performance.avg_loss_r)
            
            performance.last_performance_update = datetime.now()
    
    def _update_pattern_confidence(self, pattern_type: PatternType) -> None:
        """🎯 Update pattern confidence based on performance"""
        performance = self.pattern_performance[pattern_type]
        
        # Calculate confidence based on multiple factors
        base_confidence = 50.0
        
        # Win rate component
        if performance.win_rate >= self.performance_thresholds['excellent_win_rate']:
            win_rate_bonus = 30.0
        elif performance.win_rate >= self.performance_thresholds['good_win_rate']:
            win_rate_bonus = 20.0
        elif performance.win_rate >= self.performance_thresholds['minimum_win_rate']:
            win_rate_bonus = 10.0
        else:
            win_rate_bonus = -20.0
        
        # Profit factor component
        if performance.profit_factor >= self.performance_thresholds['excellent_profit_factor']:
            pf_bonus = 15.0
        elif performance.profit_factor >= self.performance_thresholds['good_profit_factor']:
            pf_bonus = 10.0
        elif performance.profit_factor >= self.performance_thresholds['minimum_profit_factor']:
            pf_bonus = 5.0
        else:
            pf_bonus = -10.0
        
        # Sample size factor (higher confidence with more samples)
        sample_factor = min(20.0, performance.total_occurrences / 10.0)
        
        # Final confidence calculation
        performance.confidence_score = max(0.0, min(100.0, 
            base_confidence + win_rate_bonus + pf_bonus + sample_factor))
        
        with self.lock:
            self.session_stats['confidence_updates'] += 1
    
    def _generate_learning_insights(self) -> None:
        """💡 Generate learning insights and recommendations"""
        try:
            insights = []
            
            # Analyze pattern performance
            for pattern_type, performance in self.pattern_performance.items():
                if performance.total_occurrences >= self.min_samples_for_confidence:
                    
                    # High-performing pattern insight
                    if (performance.win_rate >= self.performance_thresholds['excellent_win_rate'] and 
                        performance.profit_factor >= self.performance_thresholds['excellent_profit_factor']):
                        
                        insight = LearningInsight(
                            insight_id=f"INSIGHT_{pattern_type.value}_{int(time.time())}",
                            insight_type="PATTERN_IMPROVEMENT",
                            pattern_types=[pattern_type],
                            market_conditions=["ALL"],
                            confidence_level=performance.confidence_score,
                            recommendation=f"Increase allocation to {pattern_type.value} patterns - excellent performance",
                            supporting_evidence=[
                                f"Win rate: {performance.win_rate:.1f}%",
                                f"Profit factor: {performance.profit_factor:.2f}",
                                f"Expectancy: {performance.expectancy_r:.3f}R"
                            ],
                            potential_impact="HIGH",
                            implementation_priority=9,
                            created_timestamp=datetime.now()
                        )
                        insights.append(insight)
                    
                    # Poor-performing pattern insight
                    elif (performance.win_rate < self.performance_thresholds['minimum_win_rate'] or 
                          performance.profit_factor < self.performance_thresholds['minimum_profit_factor']):
                        
                        insight = LearningInsight(
                            insight_id=f"INSIGHT_{pattern_type.value}_{int(time.time())}",
                            insight_type="PATTERN_IMPROVEMENT",
                            pattern_types=[pattern_type],
                            market_conditions=["ALL"],
                            confidence_level=performance.confidence_score,
                            recommendation=f"Review {pattern_type.value} pattern criteria - underperforming",
                            supporting_evidence=[
                                f"Win rate: {performance.win_rate:.1f}%",
                                f"Profit factor: {performance.profit_factor:.2f}",
                                f"Sample size: {performance.total_occurrences}"
                            ],
                            potential_impact="HIGH",
                            implementation_priority=8,
                            created_timestamp=datetime.now()
                        )
                        insights.append(insight)
            
            # Store insights
            with self.lock:
                self.learning_insights.extend(insights)
                self.session_stats['insights_generated'] += len(insights)
            
            if insights:
                self.logger.info(f"💡 Generated {len(insights)} learning insights")
                
        except Exception as e:
            self.logger.error(f"❌ Error generating learning insights: {e}")
    
    def get_pattern_confidence(self, pattern_type: PatternType) -> float:
        """🎯 Get current confidence for a pattern type"""
        performance = self.pattern_performance.get(pattern_type)
        return performance.confidence_score if performance else 50.0
    
    def get_pattern_performance_summary(self) -> Dict[str, Any]:
        """📊 Get pattern performance summary"""
        summary = {}
        
        for pattern_type, performance in self.pattern_performance.items():
            summary[pattern_type.value] = {
                'total_occurrences': performance.total_occurrences,
                'win_rate': performance.win_rate,
                'profit_factor': performance.profit_factor,
                'expectancy_r': performance.expectancy_r,
                'confidence_score': performance.confidence_score,
                'last_update': performance.last_performance_update.isoformat()
            }
        
        return summary
    
    def get_recent_insights(self, max_insights: int = 10) -> List[LearningInsight]:
        """💡 Get recent learning insights"""
        with self.lock:
            return sorted(self.learning_insights, 
                         key=lambda x: x.created_timestamp, reverse=True)[:max_insights]
    
    def get_session_stats(self) -> Dict[str, Any]:
        """📊 Get session statistics"""
        with self.lock:
            # Calculate learning accuracy
            correct_predictions = 0
            total_predictions = 0
            
            for record in self.learning_records:
                if record.actual_outcome is not None:
                    total_predictions += 1
                    # Simple accuracy check (can be enhanced)
                    if ((record.predicted_outcome in [PatternOutcome.WIN, PatternOutcome.SMALL_WIN, PatternOutcome.BIG_WIN] and
                         record.actual_outcome in [PatternOutcome.WIN, PatternOutcome.SMALL_WIN, PatternOutcome.BIG_WIN]) or
                        (record.predicted_outcome in [PatternOutcome.LOSS, PatternOutcome.SMALL_LOSS, PatternOutcome.BIG_LOSS] and
                         record.actual_outcome in [PatternOutcome.LOSS, PatternOutcome.SMALL_LOSS, PatternOutcome.BIG_LOSS]) or
                        record.predicted_outcome == record.actual_outcome):
                        correct_predictions += 1
            
            if total_predictions > 0:
                self.session_stats['learning_accuracy'] = (correct_predictions / total_predictions) * 100
            
            # Calculate average pattern confidence
            total_confidence = sum(p.confidence_score for p in self.pattern_performance.values())
            pattern_count = len(self.pattern_performance)
            self.session_stats['avg_pattern_confidence'] = total_confidence / pattern_count if pattern_count > 0 else 0
            
            self.session_stats['patterns_tracked'] = len([p for p in self.pattern_performance.values() if p.total_occurrences > 0])
            
            return self.session_stats.copy()


# Singleton pattern for global access
_learning_system_instance = None
_learning_system_lock = threading.Lock()


def get_pattern_learning_system() -> PatternLearningSystem:
    """🧠 Get Pattern Learning System singleton instance"""
    global _learning_system_instance
    
    if _learning_system_instance is None:
        with _learning_system_lock:
            if _learning_system_instance is None:
                _learning_system_instance = PatternLearningSystem()
    
    return _learning_system_instance


if __name__ == "__main__":
    # Basic test
    learning_system = get_pattern_learning_system()
    print("🧠 Pattern Learning System v6.1 test completed")
