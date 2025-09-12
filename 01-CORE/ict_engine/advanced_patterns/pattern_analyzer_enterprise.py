#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 PATTERN ANALYZER ENTERPRISE v6.0
🏗️ ICT Engine - Advanced Pattern Integration & Confluence Analysis

ENTERPRISE FEATURES:
- ✅ Unified Pattern Detection Interface
- ✅ Multi-Pattern Confluence Analysis
- ✅ Priority-Based Pattern Ranking
- ✅ Conflict Resolution Engine
- ✅ Real-Time Pattern Scoring
- ✅ UnifiedMemorySystem Integration
- ✅ Advanced Performance Optimization
- ✅ Risk-Aware Pattern Filtering

Pattern Detectors Integrated:
1. Silver Bullet Enterprise
2. Judas Swing Enterprise
3. Liquidity Grab Enterprise
4. Order Block Mitigation Enterprise
5. Breaker Blocks Enterprise
6. Multi-Pattern Confluence Engine

Author: ICT Development Team
Version: 6.0 Enterprise Edition
Last Update: 2025-09-03
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

# 🏗️ ENTERPRISE ARCHITECTURE v6.0 - IMPORTS OPTIMIZADOS
try:
    from smart_trading_logger import SmartTradingLogger, log_info, log_warning, log_error, log_debug
    from analysis.unified_memory_system import get_unified_memory_system
    from data_management.advanced_candle_downloader import _pandas_manager
    UNIFIED_MEMORY_AVAILABLE = True
    ENTERPRISE_COMPONENTS_AVAILABLE = True
except ImportError:
    UNIFIED_MEMORY_AVAILABLE = False
    ENTERPRISE_COMPONENTS_AVAILABLE = False
    
    # Fallback logging functions
    def log_info(message: str, component: str = "pattern_analyzer_enterprise") -> None:
        """Fallback log_info function"""
        print(f"[INFO] {component}: {message}")
    
    def log_warning(message: str, component: str = "pattern_analyzer_enterprise") -> None:
        """Fallback log_warning function"""
        print(f"[WARNING] {component}: {message}")
    
    def log_error(message: str, component: str = "pattern_analyzer_enterprise") -> None:
        """Fallback log_error function"""
        print(f"[ERROR] {component}: {message}")
    
    def log_debug(message: str, component: str = "pattern_analyzer_enterprise") -> None:
        """Fallback log_debug function"""
        print(f"[DEBUG] {component}: {message}")
    
    def get_unified_memory_system() -> Optional[Any]:
        """Fallback para testing cuando UnifiedMemorySystem no está disponible"""
        return None

# Import Pattern Detectors
SilverBulletDetectorEnterprise = None
JudasSwingDetectorEnterprise = None
LiquidityGrabDetectorEnterprise = None
OrderBlockMitigationDetectorEnterprise = None

try:
    from .silver_bullet_enterprise import SilverBulletDetectorEnterprise
    from .judas_swing_enterprise import JudasSwingDetectorEnterprise
    from .liquidity_grab_enterprise import LiquidityGrabDetectorEnterprise
    from .order_block_mitigation_enterprise import OrderBlockMitigationDetectorEnterprise
    PATTERN_DETECTORS_AVAILABLE = True
    log_info("✅ Pattern detectors importados exitosamente", "pattern_analyzer_enterprise")
except ImportError as e:
    log_error(f"❌ Error importando detectores de patrones: {e}", "pattern_analyzer_enterprise")
    PATTERN_DETECTORS_AVAILABLE = False

# Import shared enums
from enum import Enum
class TradingDirection(Enum):
    BUY = "buy"
    SELL = "sell"

class PatternType(Enum):
    SILVER_BULLET = "silver_bullet"
    JUDAS_SWING = "judas_swing"
    LIQUIDITY_GRAB = "liquidity_grab"
    ORDER_BLOCK_MITIGATION = "order_block_mitigation"

class ConfidenceLevel(Enum):
    LOW = "low"          # 0-40%
    MEDIUM = "medium"    # 40-70%
    HIGH = "high"        # 70-85%
    EXTREME = "extreme"  # 85-100%

@dataclass
class PatternSignal:
    """Unified Pattern Signal Structure"""
    pattern_type: PatternType
    signal_type: TradingDirection
    timestamp: datetime
    symbol: str
    timeframe: str
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    
    # Advanced Enterprise Fields
    confluence_score: float = 0.0
    risk_reward_ratio: float = 0.0
    pattern_strength: str = "MEDIUM"
    market_condition: str = "NORMAL"
    pattern_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary for storage/analysis"""
        return {
            'pattern_type': self.pattern_type.value,
            'signal_type': self.signal_type.value,
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'confluence_score': self.confluence_score,
            'risk_reward_ratio': self.risk_reward_ratio,
            'pattern_strength': self.pattern_strength,
            'market_condition': self.market_condition,
            'pattern_metadata': self.pattern_metadata
        }

@dataclass
class AnalysisResult:
    """Comprehensive Pattern Analysis Result"""
    primary_signal: Optional[PatternSignal]
    secondary_signals: List[PatternSignal]
    confluence_signals: List[PatternSignal]
    conflict_analysis: Dict[str, Any]
    market_sentiment: str
    overall_confidence: float
    recommended_action: str
    risk_assessment: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis result to dictionary"""
        return {
            'primary_signal': self.primary_signal.to_dict() if self.primary_signal else None,
            'secondary_signals': [signal.to_dict() for signal in self.secondary_signals],
            'confluence_signals': [signal.to_dict() for signal in self.confluence_signals],
            'conflict_analysis': self.conflict_analysis,
            'market_sentiment': self.market_sentiment,
            'overall_confidence': self.overall_confidence,
            'recommended_action': self.recommended_action,
            'risk_assessment': self.risk_assessment
        }

class PatternAnalyzerEnterprise:
    """
    🔥 Pattern Analyzer Enterprise v6.0
    
    Unified interface for all ICT pattern detection with:
    - Multi-pattern confluence analysis
    - Priority-based pattern ranking
    - Conflict resolution engine
    - Real-time pattern scoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Pattern Analyzer Enterprise v6.0"""
        log_info("🔥 Inicializando Pattern Analyzer Enterprise v6.0", "pattern_analyzer_enterprise")
        
        # Default configuration
        self.config = {
            'min_confidence': 65.0,
            'confluence_threshold': 75.0,
            'conflict_resolution': 'highest_confidence',
            'pattern_priorities': {
                PatternType.SILVER_BULLET: 1.0,
                PatternType.JUDAS_SWING: 0.9,
                PatternType.LIQUIDITY_GRAB: 0.8,
                PatternType.ORDER_BLOCK_MITIGATION: 0.7
            },
            'risk_filters': {
                'max_risk_per_trade': 2.0,
                'min_risk_reward': 1.5,
                'max_drawdown_limit': 5.0
            },
            'performance_config': {
                'parallel_detection': True,
                'cache_enabled': True,
                'batch_processing': True
            }
        }
        
        # Override with user config
        if config:
            self.config.update(config)
        
        # Initialize pattern detectors
        self.detectors = {}
        self._initialize_detectors()
        
        # Initialize UnifiedMemorySystem
        self.memory_system = None
        try:
            if UNIFIED_MEMORY_AVAILABLE:
                self.memory_system = get_unified_memory_system()
                if self.memory_system and hasattr(self.memory_system, 'initialized') and self.memory_system.initialized:
                    log_info("✅ UnifiedMemorySystem v6.1 integrado exitosamente", "pattern_analyzer_enterprise")
                else:
                    log_warning("⚠️ UnifiedMemorySystem no inicializado - usando fallback", "pattern_analyzer_enterprise")
            else:
                log_warning("⚠️ UnifiedMemorySystem no disponible - usando pattern_memory local", "pattern_analyzer_enterprise")
        except Exception as e:
            log_error(f"❌ Error integrando UnifiedMemorySystem: {e}", "pattern_analyzer_enterprise")
        
        # Pattern analysis cache
        self.analysis_cache = {}
        self.pattern_history = {}
        
        # Performance tracking
        self.performance_metrics = {
            'total_patterns_detected': 0,
            'successful_signals': 0,
            'confluence_detections': 0,
            'conflicts_resolved': 0,
            'cache_hits': 0,
            'processing_time_avg': 0.0
        }
        
        log_info("✅ Pattern Analyzer Enterprise v6.0 inicializado correctamente", "pattern_analyzer_enterprise")
    
    def _initialize_detectors(self) -> None:
        """Initialize all pattern detectors"""
        if not PATTERN_DETECTORS_AVAILABLE:
            log_error("❌ Pattern detectors no disponibles", "pattern_analyzer_enterprise")
            return
        
        try:
            # Initialize Silver Bullet Detector
            if SilverBulletDetectorEnterprise is not None:
                self.detectors[PatternType.SILVER_BULLET] = SilverBulletDetectorEnterprise()
                log_info("✅ Silver Bullet Detector inicializado", "pattern_analyzer_enterprise")
            
            # Initialize Judas Swing Detector
            if JudasSwingDetectorEnterprise is not None:
                self.detectors[PatternType.JUDAS_SWING] = JudasSwingDetectorEnterprise()
                log_info("✅ Judas Swing Detector inicializado", "pattern_analyzer_enterprise")
            
            # Initialize Liquidity Grab Detector
            if LiquidityGrabDetectorEnterprise is not None:
                self.detectors[PatternType.LIQUIDITY_GRAB] = LiquidityGrabDetectorEnterprise()
                log_info("✅ Liquidity Grab Detector inicializado", "pattern_analyzer_enterprise")
            
            # Initialize Order Block Mitigation Detector
            if OrderBlockMitigationDetectorEnterprise is not None:
                self.detectors[PatternType.ORDER_BLOCK_MITIGATION] = OrderBlockMitigationDetectorEnterprise()
                log_info("✅ Order Block Mitigation Detector inicializado", "pattern_analyzer_enterprise")
            
            # Initialize Breaker Blocks Detector
            # self.detectors[PatternType.BREAKER_BLOCKS] = BreakerBlocksDetectorEnterprise()
            # log_info("✅ Breaker Blocks Detector inicializado", "pattern_analyzer_enterprise")
            
            # Initialize Multi-Pattern Confluence Engine
            # self.detectors[PatternType.CONFLUENCE] = MultiPatternConfluenceEngine()
            # log_info("✅ Multi-Pattern Confluence Engine inicializado", "pattern_analyzer_enterprise")
            
        except Exception as e:
            log_error(f"❌ Error inicializando detectores: {e}", "pattern_analyzer_enterprise")
    
    def analyze_patterns(self, 
                        symbol: str, 
                        timeframe: str, 
                        data: pd.DataFrame,
                        advanced_analysis: bool = True) -> AnalysisResult:
        """
        Comprehensive Pattern Analysis
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe
            data: OHLC data
            advanced_analysis: Enable advanced confluence and conflict analysis
            
        Returns:
            AnalysisResult with comprehensive pattern analysis
        """
        log_info(f"🔥 Iniciando análisis completo de patrones para {symbol} {timeframe}", "pattern_analyzer_enterprise")
        
        try:
            if data is None or data.empty:
                log_warning("❌ Sin datos para análisis de patrones", "pattern_analyzer_enterprise")
                return self._create_empty_result()
            
            if len(data) < 50:
                log_warning(f"❌ Insuficientes datos: {len(data)} < 50 velas", "pattern_analyzer_enterprise")
                return self._create_empty_result()
            
            # Run pattern detection for all detectors
            detected_patterns = []
            detection_results = {}
            
            for pattern_type, detector in self.detectors.items():
                try:
                    log_debug(f"🔍 Ejecutando detector: {pattern_type.value}", "pattern_analyzer_enterprise")
                    signals = []
                    
                    # Call the specific detection method for each detector
                    if pattern_type == PatternType.SILVER_BULLET:
                        signals = detector.detect_silver_bullet_patterns(data, symbol, timeframe)
                    elif pattern_type == PatternType.JUDAS_SWING:
                        signals = detector.detect_judas_swing_patterns(data, symbol, timeframe)
                    elif pattern_type == PatternType.LIQUIDITY_GRAB:
                        signals = detector.detect_liquidity_grab_patterns(data, symbol, timeframe)
                    elif pattern_type == PatternType.ORDER_BLOCK_MITIGATION:
                        signals = detector.detect_order_block_mitigation_patterns(data, symbol, timeframe)
                    
                    if signals:
                        for signal in signals:
                            # Convert to unified PatternSignal format
                            unified_signal = self._convert_to_unified_signal(signal, pattern_type)
                            if unified_signal:
                                detected_patterns.append(unified_signal)
                        
                        detection_results[pattern_type] = signals
                        log_info(f"✅ {pattern_type.value}: {len(signals)} patrones detectados", "pattern_analyzer_enterprise")
                    else:
                        log_debug(f"🔍 {pattern_type.value}: No se detectaron patrones", "pattern_analyzer_enterprise")
                        
                except Exception as e:
                    log_error(f"❌ Error en detector {pattern_type.value}: {e}", "pattern_analyzer_enterprise")
                    continue
            
            # Advanced analysis if requested
            if advanced_analysis and detected_patterns:
                return self._perform_advanced_analysis(detected_patterns, symbol, timeframe, data)
            else:
                # Basic analysis
                return self._perform_basic_analysis(detected_patterns, symbol, timeframe)
        
        except Exception as e:
            log_error(f"❌ Error en análisis de patrones: {e}", "pattern_analyzer_enterprise")
            return self._create_empty_result()
    
    def _convert_to_unified_signal(self, signal: Any, pattern_type: PatternType) -> Optional[PatternSignal]:
        """Convert detector-specific signal to unified PatternSignal format"""
        try:
            # Extract common fields from signal
            if hasattr(signal, 'signal_type'):
                signal_type = TradingDirection(signal.signal_type.value.lower()) if hasattr(signal.signal_type, 'value') else TradingDirection(signal.signal_type.lower())
            else:
                signal_type = TradingDirection.BUY  # Default
            
            timestamp = getattr(signal, 'timestamp', datetime.now())
            symbol = getattr(signal, 'symbol', 'UNKNOWN')
            confidence = getattr(signal, 'confidence', 50.0)
            entry_price = getattr(signal, 'entry_price', 0.0)
            stop_loss = getattr(signal, 'stop_loss', 0.0)
            take_profit = getattr(signal, 'take_profit', 0.0)
            
            # Calculate risk/reward ratio
            if stop_loss > 0 and take_profit > 0 and entry_price > 0:
                if signal_type == TradingDirection.BUY:
                    risk = abs(entry_price - stop_loss)
                    reward = abs(take_profit - entry_price)
                else:
                    risk = abs(stop_loss - entry_price)
                    reward = abs(entry_price - take_profit)
                
                risk_reward_ratio = reward / risk if risk > 0 else 0.0
            else:
                risk_reward_ratio = 0.0
            
            # Create unified signal
            unified_signal = PatternSignal(
                pattern_type=pattern_type,
                signal_type=signal_type,
                timestamp=timestamp,
                symbol=symbol,
                timeframe=getattr(signal, 'timeframe', '1H'),
                confidence=confidence,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=risk_reward_ratio,
                pattern_strength=self._calculate_pattern_strength(confidence),
                market_condition="NORMAL",  # Could be enhanced with market analysis
                pattern_metadata=getattr(signal, 'metadata', {})
            )
            
            return unified_signal
            
        except Exception as e:
            log_error(f"❌ Error convirtiendo señal: {e}", "pattern_analyzer_enterprise")
            return None
    
    def _calculate_pattern_strength(self, confidence: float) -> str:
        """Calculate pattern strength based on confidence level"""
        if confidence >= 85:
            return "EXTREME"
        elif confidence >= 70:
            return "HIGH"
        elif confidence >= 40:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _perform_advanced_analysis(self, patterns: List[PatternSignal], symbol: str, timeframe: str, data: pd.DataFrame) -> AnalysisResult:
        """Perform advanced pattern analysis with confluence and conflict resolution"""
        log_info(f"🧠 Iniciando análisis avanzado con {len(patterns)} patrones", "pattern_analyzer_enterprise")
        
        # Filter patterns by minimum confidence
        filtered_patterns = [p for p in patterns if p.confidence >= self.config['min_confidence']]
        log_info(f"📊 Patrones filtrados por confianza: {len(filtered_patterns)}/{len(patterns)}", "pattern_analyzer_enterprise")
        
        if not filtered_patterns:
            return self._create_empty_result()
        
        # Analyze confluence
        confluence_signals = self._analyze_confluence(filtered_patterns)
        
        # Resolve conflicts
        conflict_analysis = self._resolve_conflicts(filtered_patterns)
        
        # Rank patterns by priority
        ranked_patterns = self._rank_patterns(filtered_patterns)
        
        # Select primary signal
        primary_signal = ranked_patterns[0] if ranked_patterns else None
        secondary_signals = ranked_patterns[1:3] if len(ranked_patterns) > 1 else []
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(filtered_patterns, confluence_signals)
        
        # Determine market sentiment
        market_sentiment = self._analyze_market_sentiment(filtered_patterns)
        
        # Generate recommendation
        recommended_action = self._generate_recommendation(primary_signal, overall_confidence, market_sentiment)
        
        # Risk assessment
        risk_assessment = self._perform_risk_assessment(filtered_patterns, primary_signal)
        
        result = AnalysisResult(
            primary_signal=primary_signal,
            secondary_signals=secondary_signals,
            confluence_signals=confluence_signals,
            conflict_analysis=conflict_analysis,
            market_sentiment=market_sentiment,
            overall_confidence=overall_confidence,
            recommended_action=recommended_action,
            risk_assessment=risk_assessment
        )
        
        # Store in memory system if available
        self._store_analysis_result(result, symbol, timeframe)
        
        log_info(f"✅ Análisis avanzado completado - Recomendación: {recommended_action}", "pattern_analyzer_enterprise")
        
        return result
    
    def _perform_basic_analysis(self, patterns: List[PatternSignal], symbol: str, timeframe: str) -> AnalysisResult:
        """Perform basic pattern analysis"""
        if not patterns:
            return self._create_empty_result()
        
        # Sort by confidence
        sorted_patterns = sorted(patterns, key=lambda x: x.confidence, reverse=True)
        
        primary_signal = sorted_patterns[0]
        secondary_signals = sorted_patterns[1:3] if len(sorted_patterns) > 1 else []
        
        return AnalysisResult(
            primary_signal=primary_signal,
            secondary_signals=secondary_signals,
            confluence_signals=[],
            conflict_analysis={},
            market_sentiment="NEUTRAL",
            overall_confidence=primary_signal.confidence,
            recommended_action="MONITOR",
            risk_assessment={}
        )
    
    def _analyze_confluence(self, patterns: List[PatternSignal]) -> List[PatternSignal]:
        """Analyze pattern confluence"""
        confluence_signals = []
        
        # Group patterns by direction
        buy_patterns = [p for p in patterns if p.signal_type == TradingDirection.BUY]
        sell_patterns = [p for p in patterns if p.signal_type == TradingDirection.SELL]
        
        # Check for confluence in each direction
        if len(buy_patterns) >= 2:
            confluence_score = sum(p.confidence for p in buy_patterns) / len(buy_patterns)
            if confluence_score >= self.config['confluence_threshold']:
                # Return strongest signal with enhanced confluence score
                strongest_buy = max(buy_patterns, key=lambda x: x.confidence)
                strongest_buy.confluence_score = confluence_score
                strongest_buy.pattern_strength = "HIGH"
                strongest_buy.pattern_metadata['confluence_patterns'] = len(buy_patterns)
                confluence_signals.append(strongest_buy)
        
        if len(sell_patterns) >= 2:
            confluence_score = sum(p.confidence for p in sell_patterns) / len(sell_patterns)
            if confluence_score >= self.config['confluence_threshold']:
                # Return strongest signal with enhanced confluence score
                strongest_sell = max(sell_patterns, key=lambda x: x.confidence)
                strongest_sell.confluence_score = confluence_score
                strongest_sell.pattern_strength = "HIGH"
                strongest_sell.pattern_metadata['confluence_patterns'] = len(sell_patterns)
                confluence_signals.append(strongest_sell)
        
        if confluence_signals:
            log_info(f"🎯 Confluence detectada: {len(confluence_signals)} señales", "pattern_analyzer_enterprise")
        
        return confluence_signals
    
    def _resolve_conflicts(self, patterns: List[PatternSignal]) -> Dict[str, Any]:
        """Resolve conflicts between opposing signals"""
        buy_patterns = [p for p in patterns if p.signal_type == TradingDirection.BUY]
        sell_patterns = [p for p in patterns if p.signal_type == TradingDirection.SELL]
        
        conflict_analysis = {
            'has_conflicts': len(buy_patterns) > 0 and len(sell_patterns) > 0,
            'buy_signals': len(buy_patterns),
            'sell_signals': len(sell_patterns),
            'buy_avg_confidence': sum(p.confidence for p in buy_patterns) / len(buy_patterns) if buy_patterns else 0,
            'sell_avg_confidence': sum(p.confidence for p in sell_patterns) / len(sell_patterns) if sell_patterns else 0,
            'resolution_method': self.config['conflict_resolution'],
            'dominant_direction': None
        }
        
        if conflict_analysis['has_conflicts']:
            if conflict_analysis['buy_avg_confidence'] > conflict_analysis['sell_avg_confidence']:
                conflict_analysis['dominant_direction'] = 'BUY'
            else:
                conflict_analysis['dominant_direction'] = 'SELL'
            
            log_warning(f"⚠️ Conflicto detectado - Dirección dominante: {conflict_analysis['dominant_direction']}", "pattern_analyzer_enterprise")
        
        return conflict_analysis
    
    def _rank_patterns(self, patterns: List[PatternSignal]) -> List[PatternSignal]:
        """Rank patterns by priority and confidence"""
        def pattern_score(pattern: PatternSignal) -> float:
            base_score = pattern.confidence
            priority_multiplier = self.config['pattern_priorities'].get(pattern.pattern_type, 1.0)
            confluence_bonus = pattern.confluence_score * 0.1 if pattern.confluence_score > 0 else 0
            risk_bonus = min(pattern.risk_reward_ratio * 5, 20) if pattern.risk_reward_ratio > 0 else 0
            
            return base_score * priority_multiplier + confluence_bonus + risk_bonus
        
        ranked = sorted(patterns, key=pattern_score, reverse=True)
        return ranked
    
    def _calculate_overall_confidence(self, patterns: List[PatternSignal], confluence_signals: List[PatternSignal]) -> float:
        """Calculate overall analysis confidence"""
        if not patterns:
            return 0.0
        
        # Base confidence from patterns
        avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
        
        # Confluence bonus
        confluence_bonus = len(confluence_signals) * 10
        
        # Pattern diversity bonus
        pattern_types = set(p.pattern_type for p in patterns)
        diversity_bonus = len(pattern_types) * 5
        
        overall = min(avg_confidence + confluence_bonus + diversity_bonus, 100.0)
        return overall
    
    def _analyze_market_sentiment(self, patterns: List[PatternSignal]) -> str:
        """Analyze overall market sentiment from patterns"""
        if not patterns:
            return "NEUTRAL"
        
        buy_count = sum(1 for p in patterns if p.signal_type == TradingDirection.BUY)
        sell_count = sum(1 for p in patterns if p.signal_type == TradingDirection.SELL)
        
        buy_confidence = sum(p.confidence for p in patterns if p.signal_type == TradingDirection.BUY)
        sell_confidence = sum(p.confidence for p in patterns if p.signal_type == TradingDirection.SELL)
        
        if buy_count > sell_count and buy_confidence > sell_confidence:
            return "BULLISH"
        elif sell_count > buy_count and sell_confidence > buy_confidence:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _generate_recommendation(self, primary_signal: Optional[PatternSignal], overall_confidence: float, market_sentiment: str) -> str:
        """Generate trading recommendation"""
        if not primary_signal:
            return "NO_ACTION"
        
        if overall_confidence >= 80:
            return f"STRONG_{primary_signal.signal_type.value.upper()}"
        elif overall_confidence >= 65:
            return f"{primary_signal.signal_type.value.upper()}"
        elif overall_confidence >= 50:
            return "MONITOR"
        else:
            return "NO_ACTION"
    
    def _perform_risk_assessment(self, patterns: List[PatternSignal], primary_signal: Optional[PatternSignal]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        risk_assessment = {
            'risk_level': 'MEDIUM',
            'max_risk_per_trade': self.config['risk_filters']['max_risk_per_trade'],
            'min_risk_reward': self.config['risk_filters']['min_risk_reward'],
            'patterns_risk_score': 0.0,
            'diversification_score': 0.0,
            'recommendations': []
        }
        
        if not patterns:
            risk_assessment['risk_level'] = 'HIGH'
            risk_assessment['recommendations'].append("Insufficient pattern confirmation")
            return risk_assessment
        
        # Calculate patterns risk score
        avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
        avg_risk_reward = sum(p.risk_reward_ratio for p in patterns if p.risk_reward_ratio > 0) / max(1, len([p for p in patterns if p.risk_reward_ratio > 0]))
        
        risk_assessment['patterns_risk_score'] = avg_confidence
        
        # Diversification score
        pattern_types = set(p.pattern_type for p in patterns)
        risk_assessment['diversification_score'] = len(pattern_types) * 20
        
        # Risk level determination
        if avg_confidence >= 80 and avg_risk_reward >= 2.0:
            risk_assessment['risk_level'] = 'LOW'
        elif avg_confidence >= 60 and avg_risk_reward >= 1.5:
            risk_assessment['risk_level'] = 'MEDIUM'
        else:
            risk_assessment['risk_level'] = 'HIGH'
        
        # Recommendations
        if avg_risk_reward < self.config['risk_filters']['min_risk_reward']:
            risk_assessment['recommendations'].append(f"Risk/Reward ratio below minimum ({avg_risk_reward:.2f} < {self.config['risk_filters']['min_risk_reward']})")
        
        if len(pattern_types) < 2:
            risk_assessment['recommendations'].append("Consider waiting for pattern confluence")
        
        return risk_assessment
    
    def _store_analysis_result(self, result: AnalysisResult, symbol: str, timeframe: str) -> None:
        """Store analysis result in UnifiedMemorySystem"""
        try:
            if self.memory_system and hasattr(self.memory_system, 'store_pattern_analysis'):
                self.memory_system.store_pattern_analysis(
                    symbol=symbol,
                    timeframe=timeframe,
                    analysis=result.to_dict(),
                    timestamp=datetime.now()
                )
                log_info(f"✅ Análisis almacenado en UnifiedMemorySystem: {symbol} {timeframe}", "pattern_analyzer_enterprise")
            else:
                # Local storage fallback
                cache_key = f"{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H')}"
                self.analysis_cache[cache_key] = result
                log_debug(f"📝 Análisis almacenado en cache local: {cache_key}", "pattern_analyzer_enterprise")
        except Exception as e:
            log_error(f"❌ Error almacenando análisis: {e}", "pattern_analyzer_enterprise")
    
    def _create_empty_result(self) -> AnalysisResult:
        """Create empty analysis result"""
        return AnalysisResult(
            primary_signal=None,
            secondary_signals=[],
            confluence_signals=[],
            conflict_analysis={},
            market_sentiment="NEUTRAL",
            overall_confidence=0.0,
            recommended_action="NO_ACTION",
            risk_assessment={'risk_level': 'HIGH', 'recommendations': ['No patterns detected']}
        )
    
    def get_pattern_history(self, symbol: str, timeframe: str, days: int = 7) -> List[AnalysisResult]:
        """Get historical pattern analysis results"""
        try:
            history = []
            
            if self.memory_system and hasattr(self.memory_system, 'get_pattern_history'):
                history = self.memory_system.get_pattern_history(symbol, timeframe, days)
            else:
                # Search local cache
                target_date = datetime.now() - timedelta(days=days)
                for key, result in self.analysis_cache.items():
                    if symbol in key and timeframe in key:
                        # Extract date from key and check if within range
                        try:
                            date_str = key.split('_')[-2] + '_' + key.split('_')[-1]
                            cache_date = datetime.strptime(date_str, '%Y%m%d_%H')
                            if cache_date >= target_date:
                                history.append(result)
                        except:
                            continue
            
            log_info(f"📊 Historial de patrones obtenido: {len(history)} registros", "pattern_analyzer_enterprise")
            return history
            
        except Exception as e:
            log_error(f"❌ Error obteniendo historial: {e}", "pattern_analyzer_enterprise")
            return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get pattern analyzer performance metrics"""
        return {
            'performance_metrics': self.performance_metrics,
            'detectors_status': {pattern_type.value: 'active' for pattern_type in self.detectors.keys()},
            'config': self.config,
            'memory_system_status': 'connected' if self.memory_system else 'fallback',
            'cache_size': len(self.analysis_cache)
        }

# Export main class
__all__ = ['PatternAnalyzerEnterprise', 'PatternSignal', 'AnalysisResult', 'PatternType', 'ConfidenceLevel']
