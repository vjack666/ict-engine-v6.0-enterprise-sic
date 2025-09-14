"""
🎯 ADVANCED PATTERN ANALYTICS INTEGRATOR v6.1
Integration hub for all Advanced Pattern Analytics components

FASE 2 WEEK 3 DAY 3 - Complete Integration:
- Pattern Confluence Engine (v6.1)
- Market Structure Intelligence (v6.1) 
- Trading Signal Synthesizer (v6.1)
- Pattern Learning System (v6.1)
- Real-Time Analytics Dashboard (v6.1)

This module provides a unified interface for all analytics components,
ensuring seamless integration and coordinated operation.
"""

import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Enterprise logging integration - usando sistema unificado central
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Variables globales para evitar problemas de Pylance
# Importar sistema de logging centralizado con fallbacks
create_unified_logger_func = None
SLUC_AVAILABLE = False

try:
    # Importar directamente desde SmartTradingLogger para evitar problemas de firma
    from smart_trading_logger import SmartTradingLogger
    
    # Crear instancia global del logger
    _global_logger = SmartTradingLogger("INTEGRATOR")
    
    # Funciones de logging que usan la interfaz correcta
    def log_info(message, component="CORE"): 
        _global_logger.info(message, component)
    def log_warning(message, component="CORE"): 
        _global_logger.warning(message, component)
    def log_error(message, component="CORE"): 
        _global_logger.error(message, component)
    def log_debug(message, component="CORE"): 
        _global_logger.debug(message, component)
    
    SLUC_AVAILABLE = True
    
except ImportError:
    logging.basicConfig(level=logging.INFO)
    # Fallback logging functions - usando 'component' para consistencia con SmartTradingLogger
    def log_info(message, component="CORE"): logging.info(f"[{component}] {message}")
    def log_warning(message, component="CORE"): logging.warning(f"[{component}] {message}") 
    def log_error(message, component="CORE"): logging.error(f"[{component}] {message}")
    def log_debug(message, component="CORE"): logging.debug(f"[{component}] {message}")

# Función unificada de logging que evita redeclaración
def get_integrator_logger(name="AdvancedPatternAnalyticsIntegrator"):
    """🎯 Get unified logger for integrator"""
    if SLUC_AVAILABLE and create_unified_logger_func:
        return create_unified_logger_func(name)
    else:
        return logging.getLogger(name)

# Direct imports - sistema probado y funcional
from analysis.pattern_confluence_engine import get_confluence_engine, PatternType
from analysis.market_structure_intelligence import get_market_structure_intelligence, MarketPhase  
from analysis.trading_signal_synthesizer import get_trading_signal_synthesizer, TradingSignal
from analysis.pattern_learning_system import get_pattern_learning_system, PatternOutcome
from analysis.realtime_analytics_dashboard import get_realtime_analytics_dashboard, AnalyticsEventType, DashboardComponent

ANALYTICS_COMPONENTS_AVAILABLE = True
log_info("Todos los componentes de análisis cargados exitosamente", "INTEGRATOR")


class AnalyticsMode(Enum):
    """🎯 Analytics operation modes"""
    FULL_ANALYTICS = "FULL_ANALYTICS"         # All components active
    PATTERN_ONLY = "PATTERN_ONLY"             # Only pattern analysis
    SIGNALS_ONLY = "SIGNALS_ONLY"             # Only signal generation
    LEARNING_ONLY = "LEARNING_ONLY"           # Only learning system
    DASHBOARD_ONLY = "DASHBOARD_ONLY"         # Only dashboard
    MINIMAL = "MINIMAL"                       # Basic analytics only


class IntegrationStatus(Enum):
    """📊 Integration status"""
    NOT_INITIALIZED = "NOT_INITIALIZED"
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ERROR = "ERROR"
    SHUTDOWN = "SHUTDOWN"


@dataclass
class AnalyticsResult:
    """📊 Complete analytics result"""
    analysis_id: str
    symbol: str
    timeframe: str
    timestamp: datetime
    
    # Component results
    confluence_analysis: Optional[Any] = None
    structure_analysis: Optional[Any] = None
    trading_signals: Optional[Any] = None
    learning_record_id: Optional[str] = None
    
    # Integrated insights
    overall_score: float = 0.0
    recommendation: str = "WAIT"
    confidence_level: float = 50.0
    risk_assessment: str = "MEDIUM"
    
    # Performance metrics
    processing_time_ms: float = 0.0
    components_used: List[str] = field(default_factory=list)
    
    # Metadata
    integration_version: str = "6.1"
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedPatternAnalyticsIntegrator:
    """
    🎯 ADVANCED PATTERN ANALYTICS INTEGRATOR v6.1
    Central hub for all advanced analytics components
    """
    
    def __init__(self, mode: AnalyticsMode = AnalyticsMode.FULL_ANALYTICS):
        """Initialize Advanced Pattern Analytics Integrator"""
        # Smart logging integration - usando sistema unificado
        self.logger = get_integrator_logger("AdvancedPatternAnalyticsIntegrator")
        
        self.mode = mode
        self.status = IntegrationStatus.NOT_INITIALIZED
        self.lock = threading.Lock()
        
        # Component instances
        self.confluence_engine = None
        self.structure_intelligence = None
        self.signal_synthesizer = None
        self.learning_system = None
        self.analytics_dashboard = None
        
        # Integration state
        self.start_time = None
        self.total_analyses = 0
        self.successful_analyses = 0
        self.error_count = 0
        
        # Performance tracking
        self.processing_times = []
        self.component_performance = {}
        
        # Integration statistics
        self.integration_stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'error_rate': 0.0,
            'avg_processing_time_ms': 0.0,
            'components_active': 0,
            'uptime_hours': 0.0,
            'patterns_detected': 0,
            'signals_generated': 0,
            'learning_records_created': 0,
            'dashboard_events_published': 0
        }
        
        self.logger.info(f"🎯 Advanced Pattern Analytics Integrator v6.1 initialized - Mode: {mode.value}")
    
    def initialize_analytics_system(self) -> bool:
        """🚀 Initialize complete analytics system"""
        try:
            self.status = IntegrationStatus.INITIALIZING
            self.start_time = datetime.now()
            
            if not ANALYTICS_COMPONENTS_AVAILABLE:
                self.logger.error("❌ Analytics components not available")
                self.status = IntegrationStatus.ERROR
                return False
            
            # Initialize components based on mode
            components_initialized = 0
            
            if self.mode in [AnalyticsMode.FULL_ANALYTICS, AnalyticsMode.PATTERN_ONLY]:
                self.confluence_engine = get_confluence_engine()
                if self.confluence_engine:
                    components_initialized += 1
                    self.logger.info("✅ Pattern Confluence Engine initialized")
                
                self.structure_intelligence = get_market_structure_intelligence()
                if self.structure_intelligence:
                    components_initialized += 1
                    self.logger.info("✅ Market Structure Intelligence initialized")
            
            if self.mode in [AnalyticsMode.FULL_ANALYTICS, AnalyticsMode.SIGNALS_ONLY]:
                self.signal_synthesizer = get_trading_signal_synthesizer()
                if self.signal_synthesizer:
                    components_initialized += 1
                    self.logger.info("✅ Trading Signal Synthesizer initialized")
            
            if self.mode in [AnalyticsMode.FULL_ANALYTICS, AnalyticsMode.LEARNING_ONLY]:
                self.learning_system = get_pattern_learning_system()
                if self.learning_system:
                    components_initialized += 1
                    self.logger.info("✅ Pattern Learning System initialized")
            
            if self.mode in [AnalyticsMode.FULL_ANALYTICS, AnalyticsMode.DASHBOARD_ONLY]:
                self.analytics_dashboard = get_realtime_analytics_dashboard()
                if self.analytics_dashboard:
                    self.analytics_dashboard.start_analytics_streaming()
                    components_initialized += 1
                    self.logger.info("✅ Real-Time Analytics Dashboard initialized")
            
            # Update integration stats
            with self.lock:
                self.integration_stats['components_active'] = components_initialized
            
            if components_initialized > 0:
                self.status = IntegrationStatus.ACTIVE
                self.logger.info(f"🚀 Analytics system initialized successfully - {components_initialized} components active")
                
                # Publish system startup event
                self._publish_dashboard_event(
                    AnalyticsEventType.SYSTEM_STATUS,
                    "SYSTEM",
                    "N/A",
                    DashboardComponent.SYSTEM_HEALTH,
                    {
                        "status": "initialized",
                        "components_active": components_initialized,
                        "mode": self.mode.value
                    },
                    priority=9
                )
                
                return True
            else:
                self.status = IntegrationStatus.ERROR
                self.logger.error("❌ No components could be initialized")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error initializing analytics system: {e}")
            self.status = IntegrationStatus.ERROR
            return False
    
    def perform_complete_analysis(self, candles, symbol: str, timeframe: str) -> AnalyticsResult:
        """
        🎯 Perform complete pattern analytics analysis
        
        Args:
            candles: OHLC price data
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            AnalyticsResult: Complete analytics result
        """
        analysis_id = f"APA_{symbol}_{timeframe}_{int(time.time())}"
        start_time = time.time()
        
        try:
            if self.status != IntegrationStatus.ACTIVE:
                self.logger.warning("⚠️ Analytics system not active")
                return self._create_error_result(analysis_id, symbol, timeframe, "System not active")
            
            self.logger.info(f"🎯 Starting complete analysis: {symbol} {timeframe}")
            
            # Initialize result
            result = AnalyticsResult(
                analysis_id=analysis_id,
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.now()
            )
            
            components_used = []
            
            # 1. Pattern Confluence Analysis
            if self.confluence_engine:
                try:
                    result.confluence_analysis = self.confluence_engine.analyze_confluence(candles, symbol, timeframe)
                    components_used.append("PatternConfluenceEngine")
                    
                    # Publish confluence event
                    self._publish_dashboard_event(
                        AnalyticsEventType.CONFLUENCE_UPDATED,
                        symbol,
                        timeframe,
                        DashboardComponent.CONFLUENCE_ANALYZER,
                        {
                            "overall_strength": result.confluence_analysis.overall_strength,
                            "pattern_count": len(result.confluence_analysis.pattern_confluences),
                            "market_bias": result.confluence_analysis.market_bias.value
                        }
                    )
                    
                    with self.lock:
                        self.integration_stats['patterns_detected'] += len(result.confluence_analysis.pattern_confluences)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error in confluence analysis: {e}")
            
            # 2. Market Structure Analysis
            if self.structure_intelligence:
                try:
                    result.structure_analysis = self.structure_intelligence.analyze_market_structure(candles, symbol, timeframe)
                    components_used.append("MarketStructureIntelligence")
                    
                    # Publish structure change event
                    self._publish_dashboard_event(
                        AnalyticsEventType.MARKET_STRUCTURE_CHANGE,
                        symbol,
                        timeframe,
                        DashboardComponent.MARKET_STRUCTURE,
                        {
                            "phase": result.structure_analysis.current_phase.value,
                            "trend_direction": result.structure_analysis.trend_direction.value,
                            "trend_strength": result.structure_analysis.trend_strength,
                            "phase_confidence": result.structure_analysis.phase_confidence
                        }
                    )
                    
                except Exception as e:
                    self.logger.error(f"❌ Error in structure analysis: {e}")
            
            # 3. Trading Signal Generation
            if self.signal_synthesizer:
                try:
                    result.trading_signals = self.signal_synthesizer.synthesize_trading_signals(candles, symbol, timeframe)
                    components_used.append("TradingSignalSynthesizer")
                    
                    # Publish signal event
                    self._publish_dashboard_event(
                        AnalyticsEventType.SIGNAL_GENERATED,
                        symbol,
                        timeframe,
                        DashboardComponent.SIGNAL_TRACKER,
                        {
                            "signal_type": result.trading_signals.primary_signal.value,
                            "strength": result.trading_signals.overall_score,
                            "setup_quality": result.trading_signals.setup_quality.value,
                            "confluence_score": result.trading_signals.confluence_score
                        }
                    )
                    
                    with self.lock:
                        self.integration_stats['signals_generated'] += 1
                    
                except Exception as e:
                    self.logger.error(f"❌ Error in signal synthesis: {e}")
            
            # 4. Pattern Learning Integration
            if self.learning_system and result.confluence_analysis:
                try:
                    # Record patterns for learning
                    for pattern_confluence in result.confluence_analysis.pattern_confluences:
                        learning_record_id = self.learning_system.record_pattern_detection(
                            pattern_confluence.pattern_type,
                            symbol,
                            timeframe,
                            pattern_confluence.strength,
                            result.confluence_analysis.overall_strength
                        )
                        
                        if not result.learning_record_id:  # Store first learning record ID
                            result.learning_record_id = learning_record_id
                    
                    components_used.append("PatternLearningSystem")
                    
                    with self.lock:
                        self.integration_stats['learning_records_created'] += len(result.confluence_analysis.pattern_confluences)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error in learning integration: {e}")
            
            # 5. Generate Integrated Insights
            self._generate_integrated_insights(result)
            
            # 6. Calculate performance metrics
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time
            result.components_used = components_used
            
            # Update statistics
            with self.lock:
                self.total_analyses += 1
                self.successful_analyses += 1
                self.processing_times.append(processing_time)
                
                self.integration_stats['total_analyses'] = self.total_analyses
                self.integration_stats['successful_analyses'] = self.successful_analyses
                self.integration_stats['error_rate'] = ((self.total_analyses - self.successful_analyses) / self.total_analyses) * 100
                self.integration_stats['avg_processing_time_ms'] = sum(self.processing_times) / len(self.processing_times)
                
                if self.start_time:
                    self.integration_stats['uptime_hours'] = (datetime.now() - self.start_time).total_seconds() / 3600
            
            self.logger.info(
                f"🎯 Complete analysis finished: {symbol} | "
                f"Score: {result.overall_score:.1f} | "
                f"Recommendation: {result.recommendation} | "
                f"{processing_time:.2f}ms"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error in complete analysis: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            with self.lock:
                self.total_analyses += 1
                self.error_count += 1
            
            return self._create_error_result(analysis_id, symbol, timeframe, str(e), processing_time)
    
    def _generate_integrated_insights(self, result: AnalyticsResult) -> None:
        """💡 Generate integrated insights from all components"""
        try:
            # Calculate overall score
            scores = []
            
            if result.confluence_analysis:
                scores.append(result.confluence_analysis.overall_strength)
            
            if result.structure_analysis:
                scores.append(result.structure_analysis.trend_strength)
            
            if result.trading_signals:
                scores.append(result.trading_signals.overall_score)
            
            if scores:
                result.overall_score = sum(scores) / len(scores)
            
            # Determine recommendation
            if result.trading_signals:
                signal_map = {
                    TradingSignal.STRONG_BUY: "STRONG_BUY",
                    TradingSignal.BUY: "BUY",
                    TradingSignal.WEAK_BUY: "WEAK_BUY",
                    TradingSignal.HOLD: "HOLD",
                    TradingSignal.WAIT: "WAIT",
                    TradingSignal.WEAK_SELL: "WEAK_SELL",
                    TradingSignal.SELL: "SELL",
                    TradingSignal.STRONG_SELL: "STRONG_SELL"
                }
                result.recommendation = signal_map.get(result.trading_signals.primary_signal, "WAIT")
            
            # Calculate confidence level
            confidence_factors = []
            
            if result.confluence_analysis:
                confidence_factors.append(result.confluence_analysis.overall_strength)
            
            if result.structure_analysis:
                confidence_factors.append(result.structure_analysis.phase_confidence)
            
            if result.trading_signals:
                confidence_factors.append(result.trading_signals.overall_score)
            
            if confidence_factors:
                result.confidence_level = sum(confidence_factors) / len(confidence_factors)
            
            # Assess risk
            if result.overall_score >= 80:
                result.risk_assessment = "LOW"
            elif result.overall_score >= 60:
                result.risk_assessment = "MEDIUM"
            elif result.overall_score >= 40:
                result.risk_assessment = "HIGH"
            else:
                result.risk_assessment = "VERY_HIGH"
            
        except Exception as e:
            self.logger.error(f"❌ Error generating integrated insights: {e}")
    
    def _create_error_result(self, analysis_id: str, symbol: str, timeframe: str, 
                           error_message: str, processing_time: float = 0.0) -> AnalyticsResult:
        """❌ Create error result"""
        return AnalyticsResult(
            analysis_id=analysis_id,
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.now(),
            overall_score=0.0,
            recommendation="ERROR",
            confidence_level=0.0,
            risk_assessment="UNKNOWN",
            processing_time_ms=processing_time,
            components_used=[],
            metadata={"error": error_message}
        )
    
    def _publish_dashboard_event(self, event_type: AnalyticsEventType, symbol: str, 
                               timeframe: str, component: DashboardComponent, 
                               data: Dict[str, Any], priority: int = 5) -> None:
        """📤 Publish event to dashboard"""
        try:
            if self.analytics_dashboard:
                self.analytics_dashboard.publish_analytics_event(
                    event_type, symbol, timeframe, component, data, priority
                )
                
                with self.lock:
                    self.integration_stats['dashboard_events_published'] += 1
                    
        except Exception as e:
            self.logger.error(f"❌ Error publishing dashboard event: {e}")
    
    def update_pattern_outcome(self, learning_record_id: str, outcome: PatternOutcome, 
                             profit_r: float, feedback: Optional[str] = None) -> None:
        """📊 Update pattern outcome for learning"""
        try:
            if self.learning_system:
                self.learning_system.update_pattern_outcome(learning_record_id, outcome, profit_r, feedback)
                
                # Publish trade outcome event
                self._publish_dashboard_event(
                    AnalyticsEventType.TRADE_OUTCOME,
                    "SYSTEM",
                    "N/A",
                    DashboardComponent.TRADE_JOURNAL,
                    {
                        "learning_record_id": learning_record_id,
                        "outcome": outcome.value,
                        "profit_r": profit_r,
                        "feedback": feedback
                    },
                    priority=7
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error updating pattern outcome: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """📊 Get comprehensive system status"""
        status = {
            "integration_status": self.status.value,
            "mode": self.mode.value,
            "components": {
                "confluence_engine": self.confluence_engine is not None,
                "structure_intelligence": self.structure_intelligence is not None,
                "signal_synthesizer": self.signal_synthesizer is not None,
                "learning_system": self.learning_system is not None,
                "analytics_dashboard": self.analytics_dashboard is not None and self.analytics_dashboard.is_active
            },
            "statistics": self.integration_stats.copy(),
            "performance": {
                "total_analyses": self.total_analyses,
                "successful_analyses": self.successful_analyses,
                "error_count": self.error_count,
                "success_rate": (self.successful_analyses / self.total_analyses * 100) if self.total_analyses > 0 else 0,
                "avg_processing_time_ms": sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
            }
        }
        
        # Add component-specific status
        if self.analytics_dashboard:
            status["dashboard_summary"] = self.analytics_dashboard.get_dashboard_summary()
        
        if self.learning_system:
            status["learning_performance"] = self.learning_system.get_pattern_performance_summary()
        
        return status
    
    def pause_analytics(self) -> None:
        """⏸️ Pause analytics system"""
        if self.status == IntegrationStatus.ACTIVE:
            self.status = IntegrationStatus.PAUSED
            self.logger.info("⏸️ Analytics system paused")
    
    def resume_analytics(self) -> None:
        """▶️ Resume analytics system"""
        if self.status == IntegrationStatus.PAUSED:
            self.status = IntegrationStatus.ACTIVE
            self.logger.info("▶️ Analytics system resumed")
    
    def shutdown_analytics_system(self) -> None:
        """🛑 Shutdown complete analytics system"""
        try:
            self.status = IntegrationStatus.SHUTDOWN
            
            if self.analytics_dashboard:
                self.analytics_dashboard.stop_analytics_streaming()
            
            # Publish shutdown event
            self._publish_dashboard_event(
                AnalyticsEventType.SYSTEM_STATUS,
                "SYSTEM",
                "N/A",
                DashboardComponent.SYSTEM_HEALTH,
                {"status": "shutdown", "uptime_hours": self.integration_stats.get('uptime_hours', 0)},
                priority=9
            )
            
            self.logger.info("🛑 Analytics system shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during shutdown: {e}")


# Singleton pattern for global access
_integrator_instance = None
_integrator_lock = threading.Lock()


def get_advanced_pattern_analytics_integrator(mode: AnalyticsMode = AnalyticsMode.FULL_ANALYTICS) -> AdvancedPatternAnalyticsIntegrator:
    """🎯 Get Advanced Pattern Analytics Integrator singleton instance"""
    global _integrator_instance
    
    if _integrator_instance is None:
        with _integrator_lock:
            if _integrator_instance is None:
                _integrator_instance = AdvancedPatternAnalyticsIntegrator(mode)
    
    return _integrator_instance


if __name__ == "__main__":
    # Basic test
    integrator = get_advanced_pattern_analytics_integrator()
    
    if integrator.initialize_analytics_system():
        print("🎯 Advanced Pattern Analytics Integrator v6.1 test completed successfully")
        
        # Get system status
        status = integrator.get_system_status()
        print(f"Components active: {status['statistics']['components_active']}")
        
        # Clean shutdown
        integrator.shutdown_analytics_system()
    else:
        print("❌ Failed to initialize analytics system")
