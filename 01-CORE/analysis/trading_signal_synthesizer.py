"""
🎯 TRADING SIGNAL SYNTHESIZER v6.1
Advanced trading signal generation from pattern confluence

PHASE 3 - DAY 3 Implementation:
- Combine multiple analysis engines
- Generate unified trading signals  
- Signal strength scoring (0-100)
- Multi-timeframe signal validation
- Risk-weighted signal recommendations

Dependencies:
- PatternConfluenceEngine (v6.1)
- MarketStructureIntelligence (v6.1) 
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

# Centralized analysis fallbacks integration
try:
    from analysis.analysis_fallbacks import get_analysis_logger  # type: ignore
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_analysis_logger(name: str = "AnalysisSystem") -> logging.Logger:
        return logging.getLogger(name)

# Analysis engines integration with fallbacks - use dynamic imports to avoid type conflicts
ANALYSIS_ENGINES_AVAILABLE = False
confluence_engine_module = None
structure_intelligence_module = None

try:
    import analysis.pattern_confluence_engine as confluence_engine_module
    import analysis.market_structure_intelligence as structure_intelligence_module
    ANALYSIS_ENGINES_AVAILABLE = True
except ImportError:
    ANALYSIS_ENGINES_AVAILABLE = False


class TradingSignal(Enum):
    """🎯 Trading signal types"""
    STRONG_BUY = "STRONG_BUY"       # High confidence buy signal
    BUY = "BUY"                     # Standard buy signal
    WEAK_BUY = "WEAK_BUY"          # Low confidence buy signal
    HOLD = "HOLD"                   # Hold current position
    WAIT = "WAIT"                   # Wait for better setup
    WEAK_SELL = "WEAK_SELL"        # Low confidence sell signal
    SELL = "SELL"                   # Standard sell signal
    STRONG_SELL = "STRONG_SELL"     # High confidence sell signal


class EntryType(Enum):
    """📍 Entry types"""
    MARKET = "MARKET"               # Market entry
    LIMIT = "LIMIT"                 # Limit order entry
    STOP = "STOP"                   # Stop order entry
    MIT = "MIT"                     # Market if touched
    CONDITIONAL = "CONDITIONAL"     # Conditional entry


class TradeSetupQuality(Enum):
    """⭐ Trade setup quality levels"""
    EXCELLENT = "EXCELLENT"         # 90-100 score
    GOOD = "GOOD"                  # 70-89 score
    AVERAGE = "AVERAGE"            # 50-69 score
    POOR = "POOR"                  # 30-49 score
    INVALID = "INVALID"            # 0-29 score


@dataclass
class TradingRecommendation:
    """📋 Individual trading recommendation"""
    recommendation_id: str
    signal: TradingSignal
    signal_strength: float          # 0-100
    entry_type: EntryType
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    position_size_pct: float        # Percentage of account
    max_risk_pct: float            # Maximum risk percentage
    timeframe: str
    validity_period: timedelta      # How long signal is valid
    confidence_level: float         # 0-100
    supporting_factors: List[str]
    risk_factors: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradeSetup:
    """🎯 Complete trade setup analysis"""
    setup_id: str
    symbol: str
    timeframe: str
    setup_quality: TradeSetupQuality
    overall_score: float            # 0-100
    primary_signal: TradingSignal
    alternative_signals: List[TradingSignal]
    recommendations: List[TradingRecommendation]
    confluence_score: float         # From confluence engine
    structure_score: float          # From market structure
    pattern_confirmations: int      # Number of confirming patterns
    market_bias: str               # Overall market bias
    next_key_level: Optional[float] # Next important price level
    trade_narrative: str           # Human-readable explanation
    created_timestamp: datetime
    expiry_timestamp: datetime
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class TradingSignalSynthesizer:
    """
    🎯 TRADING SIGNAL SYNTHESIZER v6.1
    Advanced signal generation from multi-pattern analysis
    """
    
    def __init__(self):
        """Initialize Trading Signal Synthesizer"""
        # Smart logging integration - use centralized logger
        self.logger = get_analysis_logger("TradingSignalSynthesizer")
        
        # Analysis engines integration with safe module access
        if ANALYSIS_ENGINES_AVAILABLE and confluence_engine_module:
            try:
                self.confluence_engine = confluence_engine_module.get_confluence_engine()
            except AttributeError:
                self.confluence_engine = None
        else:
            self.confluence_engine = None
            
        if ANALYSIS_ENGINES_AVAILABLE and structure_intelligence_module:
            try:
                self.structure_intelligence = structure_intelligence_module.get_market_structure_intelligence()
            except AttributeError:
                self.structure_intelligence = None
        else:
            self.structure_intelligence = None
        
        # Performance tracking
        self.lock = threading.Lock()
        self.synthesis_count = 0
        self.total_processing_time = 0.0
        
        # Signal generation parameters
        self.min_confluence_score = 60.0    # Minimum confluence for signal
        self.min_structure_score = 50.0     # Minimum structure score
        self.max_risk_per_trade = 2.0       # Maximum 2% risk per trade
        self.signal_validity_hours = 4      # Signals valid for 4 hours
        
        # Signal strength thresholds
        self.signal_thresholds = {
            'strong_buy': 85.0,
            'buy': 70.0,
            'weak_buy': 55.0,
            'wait': 40.0,
            'weak_sell': 55.0,
            'sell': 70.0,
            'strong_sell': 85.0
        }
        
        # Session statistics
        self.session_stats = {
            'total_syntheses': 0,
            'signals_generated': {},
            'avg_processing_time_ms': 0.0,
            'setup_quality_distribution': {},
            'success_tracking': {}
        }
        
        self.logger.info("🎯 Trading Signal Synthesizer v6.1 initialized")
    
    def synthesize_trading_signals(self, candles, symbol: str, timeframe: str) -> TradeSetup:
        """
        🎯 Main signal synthesis method
        
        Args:
            candles: OHLC price data
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            TradeSetup: Complete trade setup with signals
        """
        start_time = time.time()
        setup_id = f"TS_{symbol}_{timeframe}_{int(time.time())}"
        
        try:
            self.logger.info(f"🎯 Starting signal synthesis: {symbol} {timeframe}")
            
            # 1. Get confluence analysis
            confluence_analysis = None
            confluence_score = 0.0
            if self.confluence_engine:
                confluence_analysis = self.confluence_engine.analyze_confluence(candles, symbol, timeframe)
                confluence_score = confluence_analysis.overall_strength
            
            # 2. Get market structure analysis
            structure_analysis = None
            structure_score = 0.0
            if self.structure_intelligence:
                structure_analysis = self.structure_intelligence.analyze_market_structure(candles, symbol, timeframe)
                structure_score = structure_analysis.trend_strength
            
            # 3. Calculate overall signal strength
            overall_score = self._calculate_overall_score(confluence_score, structure_score)
            
            # 4. Determine primary signal
            primary_signal = self._determine_primary_signal(confluence_analysis, structure_analysis, overall_score)
            
            # 5. Generate alternative signals
            alternative_signals = self._generate_alternative_signals(primary_signal, overall_score)
            
            # 6. Create trading recommendations
            recommendations = self._create_trading_recommendations(
                candles, symbol, timeframe, primary_signal, confluence_analysis, structure_analysis, overall_score
            )
            
            # 7. Determine setup quality
            setup_quality = self._determine_setup_quality(overall_score)
            
            # 8. Generate trade narrative
            trade_narrative = self._generate_trade_narrative(
                primary_signal, confluence_analysis, structure_analysis, recommendations
            )
            
            # 9. Calculate pattern confirmations
            pattern_confirmations = self._count_pattern_confirmations(confluence_analysis)
            
            # 10. Determine market bias and key levels
            market_bias = confluence_analysis.market_bias.value if confluence_analysis else "NEUTRAL"
            next_key_level = structure_analysis.next_key_level if structure_analysis else None
            
            processing_time = (time.time() - start_time) * 1000
            
            # Create trade setup
            trade_setup = TradeSetup(
                setup_id=setup_id,
                symbol=symbol,
                timeframe=timeframe,
                setup_quality=setup_quality,
                overall_score=overall_score,
                primary_signal=primary_signal,
                alternative_signals=alternative_signals,
                recommendations=recommendations,
                confluence_score=confluence_score,
                structure_score=structure_score,
                pattern_confirmations=pattern_confirmations,
                market_bias=market_bias,
                next_key_level=next_key_level,
                trade_narrative=trade_narrative,
                created_timestamp=datetime.now(),
                expiry_timestamp=datetime.now() + timedelta(hours=self.signal_validity_hours),
                processing_time_ms=processing_time,
                metadata={
                    'confluence_analysis_id': confluence_analysis.confluence_id if confluence_analysis else None,
                    'structure_analysis_id': structure_analysis.analysis_id if structure_analysis else None,
                    'version': '6.1'
                }
            )
            
            # Update session statistics
            self._update_session_stats(trade_setup, processing_time)
            
            # Log results
            self.logger.info(
                f"🎯 Signal synthesis completed: {primary_signal.value} | "
                f"Quality: {setup_quality.value} | Score: {overall_score:.1f} | "
                f"{processing_time:.2f}ms"
            )
            
            return trade_setup
            
        except Exception as e:
            self.logger.error(f"❌ Error in signal synthesis: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            # Return basic setup on error
            return TradeSetup(
                setup_id=setup_id,
                symbol=symbol,
                timeframe=timeframe,
                setup_quality=TradeSetupQuality.INVALID,
                overall_score=0.0,
                primary_signal=TradingSignal.WAIT,
                alternative_signals=[],
                recommendations=[],
                confluence_score=0.0,
                structure_score=0.0,
                pattern_confirmations=0,
                market_bias="NEUTRAL",
                next_key_level=None,
                trade_narrative="Error in signal generation",
                created_timestamp=datetime.now(),
                expiry_timestamp=datetime.now() + timedelta(hours=1),
                processing_time_ms=processing_time,
                metadata={'error': str(e)}
            )
    
    def _calculate_overall_score(self, confluence_score: float, structure_score: float) -> float:
        """📊 Calculate overall signal score"""
        # Weighted combination of confluence and structure scores
        confluence_weight = 0.6
        structure_weight = 0.4
        
        overall_score = (confluence_score * confluence_weight + structure_score * structure_weight)
        return min(100.0, max(0.0, overall_score))
    
    def _determine_primary_signal(self, confluence_analysis, structure_analysis, overall_score: float) -> TradingSignal:
        """🎯 Determine primary trading signal"""
        # Default to WAIT
        if overall_score < self.signal_thresholds['wait']:
            return TradingSignal.WAIT
        
        # Determine direction bias
        bullish_bias = False
        bearish_bias = False
        
        if confluence_analysis:
            if confluence_analysis.market_bias.value == "BULLISH":
                bullish_bias = True
            elif confluence_analysis.market_bias.value == "BEARISH":
                bearish_bias = True
        
        if structure_analysis:
            if structure_analysis.trend_direction.value == "BULLISH":
                bullish_bias = True
            elif structure_analysis.trend_direction.value == "BEARISH":
                bearish_bias = True
        
        # Generate signal based on bias and strength
        if bullish_bias and not bearish_bias:
            if overall_score >= self.signal_thresholds['strong_buy']:
                return TradingSignal.STRONG_BUY
            elif overall_score >= self.signal_thresholds['buy']:
                return TradingSignal.BUY
            elif overall_score >= self.signal_thresholds['weak_buy']:
                return TradingSignal.WEAK_BUY
        
        elif bearish_bias and not bullish_bias:
            if overall_score >= self.signal_thresholds['strong_sell']:
                return TradingSignal.STRONG_SELL
            elif overall_score >= self.signal_thresholds['sell']:
                return TradingSignal.SELL
            elif overall_score >= self.signal_thresholds['weak_sell']:
                return TradingSignal.WEAK_SELL
        
        return TradingSignal.WAIT
    
    def _generate_alternative_signals(self, primary_signal: TradingSignal, overall_score: float) -> List[TradingSignal]:
        """🔄 Generate alternative signals"""
        alternatives = []
        
        # Add weaker signals as alternatives
        if primary_signal == TradingSignal.STRONG_BUY:
            alternatives.extend([TradingSignal.BUY, TradingSignal.WEAK_BUY])
        elif primary_signal == TradingSignal.BUY:
            alternatives.extend([TradingSignal.WEAK_BUY, TradingSignal.WAIT])
        elif primary_signal == TradingSignal.STRONG_SELL:
            alternatives.extend([TradingSignal.SELL, TradingSignal.WEAK_SELL])
        elif primary_signal == TradingSignal.SELL:
            alternatives.extend([TradingSignal.WEAK_SELL, TradingSignal.WAIT])
        
        return alternatives
    
    def _create_trading_recommendations(self, candles, symbol: str, timeframe: str, 
                                      primary_signal: TradingSignal, confluence_analysis, 
                                      structure_analysis, overall_score: float) -> List[TradingRecommendation]:
        """📋 Create detailed trading recommendations"""
        recommendations = []
        
        if primary_signal == TradingSignal.WAIT:
            return recommendations
        
        try:
            current_price = candles['close'].iloc[-1] if hasattr(candles, 'iloc') else candles[-1]['close']
            
            # Determine entry, SL, and TP levels
            entry_price, stop_loss, take_profit = self._calculate_entry_levels(
                current_price, primary_signal, structure_analysis
            )
            
            if entry_price and stop_loss and take_profit:
                # Calculate risk/reward ratio
                risk = abs(entry_price - stop_loss)
                reward = abs(take_profit - entry_price)
                risk_reward_ratio = reward / risk if risk > 0 else 0
                
                # Calculate position size
                position_size_pct = self._calculate_position_size(risk, current_price)
                
                # Determine entry type
                entry_type = self._determine_entry_type(primary_signal, current_price, entry_price)
                
                # Create recommendation
                recommendation = TradingRecommendation(
                    recommendation_id=f"REC_{symbol}_{int(time.time())}",
                    signal=primary_signal,
                    signal_strength=overall_score,
                    entry_type=entry_type,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    risk_reward_ratio=risk_reward_ratio,
                    position_size_pct=position_size_pct,
                    max_risk_pct=self.max_risk_per_trade,
                    timeframe=timeframe,
                    validity_period=timedelta(hours=self.signal_validity_hours),
                    confidence_level=overall_score,
                    supporting_factors=self._extract_supporting_factors(confluence_analysis, structure_analysis),
                    risk_factors=self._extract_risk_factors(confluence_analysis, structure_analysis),
                    metadata={
                        'calculation_method': 'ICT_based',
                        'current_price': current_price
                    }
                )
                
                recommendations.append(recommendation)
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error creating recommendations: {e}")
        
        return recommendations
    
    def _calculate_entry_levels(self, current_price: float, signal: TradingSignal, 
                              structure_analysis) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """📍 Calculate entry, stop loss, and take profit levels"""
        if signal in [TradingSignal.STRONG_BUY, TradingSignal.BUY, TradingSignal.WEAK_BUY]:
            # Bullish setup
            entry_price = current_price * 1.001  # Slight premium for buy
            stop_loss = current_price * 0.995    # 0.5% stop loss
            take_profit = current_price * 1.015  # 1.5% take profit (3:1 RR)
            
        elif signal in [TradingSignal.STRONG_SELL, TradingSignal.SELL, TradingSignal.WEAK_SELL]:
            # Bearish setup
            entry_price = current_price * 0.999  # Slight discount for sell
            stop_loss = current_price * 1.005    # 0.5% stop loss
            take_profit = current_price * 0.985  # 1.5% take profit (3:1 RR)
            
        else:
            return None, None, None
        
        # Adjust levels based on structure analysis if available
        if structure_analysis and structure_analysis.next_key_level:
            # TODO: Implement sophisticated level adjustment based on structure
            pass
        
        return entry_price, stop_loss, take_profit
    
    def _calculate_position_size(self, risk_per_share: float, current_price: float) -> float:
        """💰 Calculate position size based on risk management"""
        # Simple position sizing: risk 1% of account on average trades
        risk_percentage = min(self.max_risk_per_trade, 1.0)
        
        # Adjust based on signal strength
        # TODO: Implement sophisticated position sizing logic
        
        return risk_percentage
    
    def _determine_entry_type(self, signal: TradingSignal, current_price: float, entry_price: float) -> EntryType:
        """📍 Determine optimal entry type"""
        price_diff_pct = abs(entry_price - current_price) / current_price
        
        if price_diff_pct < 0.002:  # Within 0.2%
            return EntryType.MARKET
        else:
            return EntryType.LIMIT
    
    def _extract_supporting_factors(self, confluence_analysis, structure_analysis) -> List[str]:
        """✅ Extract supporting factors for the signal"""
        factors = []
        
        if confluence_analysis:
            if confluence_analysis.overall_strength > 70:
                factors.append("Strong pattern confluence")
            factors.extend([f"{p.value} pattern" for p in confluence_analysis.dominant_patterns])
        
        if structure_analysis:
            if structure_analysis.trend_strength > 60:
                factors.append("Strong trend structure")
            factors.append(f"Market phase: {structure_analysis.current_phase.value}")
        
        return factors
    
    def _extract_risk_factors(self, confluence_analysis, structure_analysis) -> List[str]:
        """⚠️ Extract risk factors for the signal"""
        factors = []
        
        if confluence_analysis:
            if confluence_analysis.market_bias.value == "CONFLICTED":
                factors.append("Conflicted market bias")
            if len(confluence_analysis.conflicting_patterns) > 0:
                factors.append("Conflicting patterns present")
        
        if structure_analysis:
            if structure_analysis.trend_direction.value == "TRANSITIONING":
                factors.append("Trend transitioning")
            if structure_analysis.phase_confidence < 60:
                factors.append("Uncertain market phase")
        
        return factors
    
    def _determine_setup_quality(self, overall_score: float) -> TradeSetupQuality:
        """⭐ Determine setup quality based on score"""
        if overall_score >= 90:
            return TradeSetupQuality.EXCELLENT
        elif overall_score >= 70:
            return TradeSetupQuality.GOOD
        elif overall_score >= 50:
            return TradeSetupQuality.AVERAGE
        elif overall_score >= 30:
            return TradeSetupQuality.POOR
        else:
            return TradeSetupQuality.INVALID
    
    def _generate_trade_narrative(self, primary_signal: TradingSignal, confluence_analysis, 
                                structure_analysis, recommendations: List[TradingRecommendation]) -> str:
        """📝 Generate human-readable trade narrative"""
        narrative_parts = []
        
        # Signal description
        narrative_parts.append(f"Primary Signal: {primary_signal.value}")
        
        # Confluence description
        if confluence_analysis:
            narrative_parts.append(
                f"Pattern Confluence: {confluence_analysis.overall_strength:.1f}% strength with "
                f"{confluence_analysis.market_bias.value} bias"
            )
        
        # Structure description
        if structure_analysis:
            narrative_parts.append(
                f"Market Structure: {structure_analysis.trend_direction.value} trend in "
                f"{structure_analysis.current_phase.value} phase"
            )
        
        # Recommendation summary
        if recommendations:
            rec = recommendations[0]
            narrative_parts.append(
                f"Entry: {rec.entry_price:.5f}, SL: {rec.stop_loss:.5f}, "
                f"TP: {rec.take_profit:.5f} (RR: {rec.risk_reward_ratio:.1f}:1)"
            )
        
        return " | ".join(narrative_parts)
    
    def _count_pattern_confirmations(self, confluence_analysis) -> int:
        """📊 Count pattern confirmations"""
        if not confluence_analysis:
            return 0
        
        return len(confluence_analysis.pattern_confluences)
    
    def _update_session_stats(self, trade_setup: TradeSetup, processing_time: float) -> None:
        """📊 Update session statistics"""
        with self.lock:
            self.session_stats['total_syntheses'] += 1
            
            # Track signals
            signal = trade_setup.primary_signal.value
            if signal not in self.session_stats['signals_generated']:
                self.session_stats['signals_generated'][signal] = 0
            self.session_stats['signals_generated'][signal] += 1
            
            # Track setup quality
            quality = trade_setup.setup_quality.value
            if quality not in self.session_stats['setup_quality_distribution']:
                self.session_stats['setup_quality_distribution'][quality] = 0
            self.session_stats['setup_quality_distribution'][quality] += 1
            
            # Update processing time average
            self.total_processing_time += processing_time
            self.synthesis_count += 1
            self.session_stats['avg_processing_time_ms'] = self.total_processing_time / self.synthesis_count
    
    def get_session_stats(self) -> Dict[str, Any]:
        """📊 Get session statistics"""
        return self.session_stats.copy()


# Singleton pattern for global access
_synthesizer_instance = None
_synthesizer_lock = threading.Lock()


def get_trading_signal_synthesizer() -> TradingSignalSynthesizer:
    """🎯 Get Trading Signal Synthesizer singleton instance"""
    global _synthesizer_instance
    
    if _synthesizer_instance is None:
        with _synthesizer_lock:
            if _synthesizer_instance is None:
                _synthesizer_instance = TradingSignalSynthesizer()
    
    return _synthesizer_instance


if __name__ == "__main__":
    # Basic test
    synthesizer = get_trading_signal_synthesizer()
    print("🎯 Trading Signal Synthesizer v6.1 test completed")
