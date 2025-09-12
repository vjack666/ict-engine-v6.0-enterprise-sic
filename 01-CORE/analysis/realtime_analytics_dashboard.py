"""
📊 REAL-TIME ANALYTICS DASHBOARD v6.1
Advanced analytics dashboard integration for pattern monitoring

PHASE 5 - DAY 3 Implementation:
- Real-time pattern analytics feed
- Live performance monitoring dashboard
- Pattern confluence visualization
- Trading signal monitoring interface
- Advanced analytics data streaming

Dependencies:
- PatternConfluenceEngine (v6.1)
- MarketStructureIntelligence (v6.1)
- TradingSignalSynthesizer (v6.1)
- PatternLearningSystem (v6.1)
- Dashboard Core Components (v6.1)
"""

import time
import threading
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import queue
from collections import deque, defaultdict

# Enterprise logging integration
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from ict_engine.unified_logging import (
        log_info, log_warning, log_error, log_debug,
        UnifiedLoggingSystem, create_unified_logger
    )
    SLUC_AVAILABLE = True
    def get_smart_logger(name="RealtimeAnalyticsDashboard"):
        """Wrapper para compatibilidad"""
        return create_unified_logger(name)
except ImportError:
    SLUC_AVAILABLE = False
    logging.basicConfig(level=logging.INFO)

# Analysis engines integration with robust fallbacks
from typing import Optional, Union, Any, Callable

# Define fallback classes first
class PatternTypeFallback:
    UNKNOWN = "UNKNOWN"

class MarketBiasFallback:
    NEUTRAL = "NEUTRAL"

class MarketPhaseFallback:
    UNKNOWN = "UNKNOWN"

class TrendDirectionFallback:
    SIDEWAYS = "SIDEWAYS"

class TradingSignalFallback:
    NO_SIGNAL = "NO_SIGNAL"

class TradeSetupQualityFallback:
    LOW = "LOW"

class PatternOutcomeFallback:
    UNKNOWN = "UNKNOWN"

class PatternConfidenceFallback:
    LOW = "LOW"

# Initialize availability flag
ANALYSIS_ENGINES_AVAILABLE = True

# Pattern Confluence Engine
try:
    from analysis.pattern_confluence_engine import get_confluence_engine, PatternType, MarketBias  # type: ignore
except ImportError:
    ANALYSIS_ENGINES_AVAILABLE = False
    def get_confluence_engine():  # type: ignore
        """Fallback confluence engine"""
        return None
    PatternType = PatternTypeFallback  # type: ignore
    MarketBias = MarketBiasFallback  # type: ignore

# Market Structure Intelligence
try:
    from analysis.market_structure_intelligence import get_market_structure_intelligence, MarketPhase, TrendDirection  # type: ignore
except ImportError:
    ANALYSIS_ENGINES_AVAILABLE = False
    def get_market_structure_intelligence():  # type: ignore
        """Fallback market structure intelligence"""
        return None
    MarketPhase = MarketPhaseFallback  # type: ignore
    TrendDirection = TrendDirectionFallback  # type: ignore

# Trading Signal Synthesizer
try:
    from analysis.trading_signal_synthesizer import get_trading_signal_synthesizer, TradingSignal, TradeSetupQuality  # type: ignore
except ImportError:
    ANALYSIS_ENGINES_AVAILABLE = False
    def get_trading_signal_synthesizer():  # type: ignore
        """Fallback trading signal synthesizer"""
        return None
    TradingSignal = TradingSignalFallback  # type: ignore
    TradeSetupQuality = TradeSetupQualityFallback  # type: ignore

# Pattern Learning System
try:
    from analysis.pattern_learning_system import get_pattern_learning_system, PatternOutcome, PatternConfidence  # type: ignore
except ImportError:
    ANALYSIS_ENGINES_AVAILABLE = False
    def get_pattern_learning_system():  # type: ignore
        """Fallback pattern learning system"""
        return None
    PatternOutcome = PatternOutcomeFallback  # type: ignore
    PatternConfidence = PatternConfidenceFallback  # type: ignore

# Dashboard integration (if available)
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "09-DASHBOARD"))
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False


class AnalyticsEventType(Enum):
    """📊 Analytics event types"""
    PATTERN_DETECTED = "PATTERN_DETECTED"
    CONFLUENCE_UPDATED = "CONFLUENCE_UPDATED"
    SIGNAL_GENERATED = "SIGNAL_GENERATED"
    TRADE_OUTCOME = "TRADE_OUTCOME"
    PERFORMANCE_UPDATE = "PERFORMANCE_UPDATE"
    LEARNING_INSIGHT = "LEARNING_INSIGHT"
    MARKET_STRUCTURE_CHANGE = "MARKET_STRUCTURE_CHANGE"
    SYSTEM_STATUS = "SYSTEM_STATUS"


class DashboardComponent(Enum):
    """🎛️ Dashboard components"""
    PATTERN_MONITOR = "PATTERN_MONITOR"
    CONFLUENCE_ANALYZER = "CONFLUENCE_ANALYZER"
    SIGNAL_TRACKER = "SIGNAL_TRACKER"
    PERFORMANCE_METRICS = "PERFORMANCE_METRICS"
    LEARNING_INSIGHTS = "LEARNING_INSIGHTS"
    MARKET_STRUCTURE = "MARKET_STRUCTURE"
    SYSTEM_HEALTH = "SYSTEM_HEALTH"
    TRADE_JOURNAL = "TRADE_JOURNAL"


@dataclass
class AnalyticsEvent:
    """📊 Analytics event data structure"""
    event_id: str
    event_type: AnalyticsEventType
    timestamp: datetime
    symbol: str
    timeframe: str
    component: DashboardComponent
    data: Dict[str, Any]
    priority: int = 5  # 1-10, 10 being highest
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardMetrics:
    """📈 Real-time dashboard metrics"""
    # Pattern metrics
    patterns_detected_today: int = 0
    patterns_by_type: Dict[str, int] = field(default_factory=dict)
    pattern_success_rate: float = 0.0
    avg_pattern_confluence: float = 0.0
    
    # Signal metrics
    signals_generated_today: int = 0
    signals_by_type: Dict[str, int] = field(default_factory=dict)
    signal_accuracy: float = 0.0
    avg_signal_strength: float = 0.0
    
    # Performance metrics
    total_trades_today: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_pnl_r: float = 0.0
    
    # Learning metrics
    learning_records_today: int = 0
    learning_accuracy: float = 0.0
    insights_generated: int = 0
    pattern_confidence_avg: float = 0.0
    
    # System metrics
    total_analysis_count: int = 0
    avg_processing_time_ms: float = 0.0
    system_uptime_hours: float = 0.0
    error_count: int = 0
    
    # Market metrics
    active_symbols: int = 0
    market_bias_distribution: Dict[str, int] = field(default_factory=dict)
    dominant_market_phase: str = "UNKNOWN"
    
    last_update: datetime = field(default_factory=datetime.now)


@dataclass
class LiveAnalyticsData:
    """📊 Live analytics data feed"""
    # Current state
    active_patterns: List[Dict[str, Any]] = field(default_factory=list)
    active_signals: List[Dict[str, Any]] = field(default_factory=list)
    current_confluences: List[Dict[str, Any]] = field(default_factory=list)
    market_structure_status: Dict[str, Any] = field(default_factory=dict)
    
    # Recent events (last N events)
    recent_events: deque = field(default_factory=lambda: deque(maxlen=100))
    
    # Performance tracking
    performance_timeline: List[Dict[str, Any]] = field(default_factory=list)
    pattern_heatmap: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Learning data
    learning_progression: List[Dict[str, Any]] = field(default_factory=list)
    confidence_evolution: Dict[str, List[float]] = field(default_factory=dict)


class RealTimeAnalyticsDashboard:
    """
    📊 REAL-TIME ANALYTICS DASHBOARD v6.1
    Advanced analytics dashboard integration for pattern monitoring
    """
    
    def __init__(self):
        """Initialize Real-Time Analytics Dashboard"""
        # Smart logging integration
        if SLUC_AVAILABLE:
            self.logger = get_smart_logger("RealTimeAnalyticsDashboard")
        else:
            self.logger = logging.getLogger("RealTimeAnalyticsDashboard")
        
        # Analysis engines
        self.confluence_engine = get_confluence_engine() if ANALYSIS_ENGINES_AVAILABLE else None
        self.structure_intelligence = get_market_structure_intelligence() if ANALYSIS_ENGINES_AVAILABLE else None
        self.signal_synthesizer = get_trading_signal_synthesizer() if ANALYSIS_ENGINES_AVAILABLE else None
        self.learning_system = get_pattern_learning_system() if ANALYSIS_ENGINES_AVAILABLE else None
        
        # Dashboard state
        self.lock = threading.Lock()
        self.is_active = False
        self.start_time = datetime.now()
        
        # Event streaming
        self.event_queue = queue.Queue(maxsize=1000)
        self.event_subscribers: Dict[DashboardComponent, List[Callable]] = defaultdict(list)
        self.analytics_thread = None
        
        # Data containers
        self.metrics = DashboardMetrics()
        self.live_data = LiveAnalyticsData()
        
        # Update intervals
        self.metrics_update_interval = 30  # seconds
        self.data_refresh_interval = 5     # seconds
        self.event_processing_interval = 1 # seconds
        
        # Data retention
        self.max_timeline_entries = 1000
        self.max_event_history = 500
        
        # Performance tracking
        self.total_events_processed = 0
        self.processing_times = deque(maxlen=100)
        
        self.logger.info("📊 Real-Time Analytics Dashboard v6.1 initialized")
    
    def start_analytics_streaming(self) -> None:
        """🚀 Start real-time analytics streaming"""
        if self.is_active:
            self.logger.warning("⚠️ Analytics streaming already active")
            return
        
        try:
            self.is_active = True
            self.start_time = datetime.now()
            
            # Start analytics processing thread
            self.analytics_thread = threading.Thread(
                target=self._analytics_processing_loop,
                name="AnalyticsProcessingThread",
                daemon=True
            )
            self.analytics_thread.start()
            
            # Initialize metrics
            self._initialize_dashboard_metrics()
            
            self.logger.info("🚀 Real-time analytics streaming started")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting analytics streaming: {e}")
            self.is_active = False
    
    def stop_analytics_streaming(self) -> None:
        """🛑 Stop real-time analytics streaming"""
        if not self.is_active:
            return
        
        try:
            self.is_active = False
            
            if self.analytics_thread and self.analytics_thread.is_alive():
                self.analytics_thread.join(timeout=5.0)
            
            self.logger.info("🛑 Real-time analytics streaming stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping analytics streaming: {e}")
    
    def publish_analytics_event(self, event_type: AnalyticsEventType, symbol: str, 
                               timeframe: str, component: DashboardComponent, 
                               data: Dict[str, Any], priority: int = 5, 
                               tags: Optional[List[str]] = None) -> str:
        """
        📤 Publish analytics event to dashboard
        
        Args:
            event_type: Type of analytics event
            symbol: Trading symbol
            timeframe: Analysis timeframe
            component: Dashboard component
            data: Event data
            priority: Event priority (1-10)
            tags: Optional event tags
            
        Returns:
            str: Event ID
        """
        event_id = f"EVT_{event_type.value}_{int(time.time())}"
        
        try:
            event = AnalyticsEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=datetime.now(),
                symbol=symbol,
                timeframe=timeframe,
                component=component,
                data=data,
                priority=priority,
                tags=tags or [],
                metadata={'dashboard_version': '6.1'}
            )
            
            # Add to event queue
            if not self.event_queue.full():
                self.event_queue.put(event)
            else:
                self.logger.warning("⚠️ Event queue full, dropping event")
            
            # Immediate processing for high-priority events
            if priority >= 8:
                self._process_analytics_event(event)
            
            return event_id
            
        except Exception as e:
            self.logger.error(f"❌ Error publishing analytics event: {e}")
            return event_id
    
    def subscribe_to_component(self, component: DashboardComponent, 
                             callback: Callable[[AnalyticsEvent], None]) -> None:
        """📡 Subscribe to component events"""
        with self.lock:
            self.event_subscribers[component].append(callback)
        
        self.logger.info(f"📡 Subscribed to {component.value} events")
    
    def get_live_metrics(self) -> Dict[str, Any]:
        """📊 Get current live metrics"""
        with self.lock:
            return asdict(self.metrics)
    
    def get_live_analytics_data(self) -> Dict[str, Any]:
        """📊 Get live analytics data"""
        with self.lock:
            # Convert deque to list for JSON serialization
            live_data_dict = asdict(self.live_data)
            live_data_dict['recent_events'] = list(self.live_data.recent_events)
            return live_data_dict
    
    def get_pattern_performance_heatmap(self) -> Dict[str, Dict[str, float]]:
        """🔥 Get pattern performance heatmap"""
        heatmap = {}
        
        if self.learning_system:
            performance_summary = self.learning_system.get_pattern_performance_summary()
            
            # Ensure performance_summary is not None and is iterable
            if performance_summary and hasattr(performance_summary, 'items'):
                for pattern_name, perf_data in performance_summary.items():  # type: ignore
                    heatmap[pattern_name] = {
                        'win_rate': perf_data.get('win_rate', 0.0),
                        'profit_factor': perf_data.get('profit_factor', 0.0),
                        'confidence': perf_data.get('confidence_score', 50.0),
                        'total_trades': perf_data.get('total_occurrences', 0)
                    }
        
        return heatmap
    
    def get_signal_distribution(self) -> Dict[str, int]:
        """📊 Get signal type distribution"""
        if self.signal_synthesizer:
            stats = self.signal_synthesizer.get_session_stats()
            return stats.get('signals_generated', {})
        return {}
    
    def get_confluence_analytics(self) -> Dict[str, Any]:
        """🔗 Get confluence analytics"""
        confluence_data = {
            'avg_confluence_score': 0.0,
            'pattern_distribution': {},
            'bias_distribution': {},
            'recent_confluences': []
        }
        
        if self.confluence_engine:
            # Get confluence engine stats (would need to implement in confluence engine)
            pass
        
        return confluence_data
    
    def get_market_structure_overview(self) -> Dict[str, Any]:
        """🏗️ Get market structure overview"""
        structure_data = {
            'dominant_phase': 'UNKNOWN',
            'trend_distribution': {},
            'structure_strength_avg': 0.0,
            'phase_confidence_avg': 0.0
        }
        
        if self.structure_intelligence:
            # Get structure intelligence stats (would need to implement)
            pass
        
        return structure_data
    
    def _analytics_processing_loop(self) -> None:
        """🔄 Main analytics processing loop"""
        last_metrics_update = time.time()
        last_data_refresh = time.time()
        
        while self.is_active:
            try:
                current_time = time.time()
                
                # Process events
                self._process_pending_events()
                
                # Update metrics periodically
                if current_time - last_metrics_update >= self.metrics_update_interval:
                    self._update_dashboard_metrics()
                    last_metrics_update = current_time
                
                # Refresh live data periodically
                if current_time - last_data_refresh >= self.data_refresh_interval:
                    self._refresh_live_data()
                    last_data_refresh = current_time
                
                # Brief sleep to prevent excessive CPU usage
                time.sleep(self.event_processing_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Error in analytics processing loop: {e}")
                time.sleep(5)  # Longer sleep on error
    
    def _process_pending_events(self) -> None:
        """⚡ Process pending events from queue"""
        events_processed = 0
        start_time = time.time()
        
        try:
            while not self.event_queue.empty() and events_processed < 50:  # Batch processing
                try:
                    event = self.event_queue.get_nowait()
                    self._process_analytics_event(event)
                    events_processed += 1
                except queue.Empty:
                    break
                except Exception as e:
                    self.logger.error(f"❌ Error processing event: {e}")
            
            # Track processing performance
            if events_processed > 0:
                processing_time = (time.time() - start_time) * 1000
                self.processing_times.append(processing_time)
                self.total_events_processed += events_processed
                
        except Exception as e:
            self.logger.error(f"❌ Error in event processing: {e}")
    
    def _process_analytics_event(self, event: AnalyticsEvent) -> None:
        """⚡ Process individual analytics event"""
        try:
            # Add to recent events
            with self.lock:
                self.live_data.recent_events.append({
                    'event_id': event.event_id,
                    'type': event.event_type.value,
                    'timestamp': event.timestamp.isoformat(),
                    'symbol': event.symbol,
                    'component': event.component.value,
                    'priority': event.priority,
                    'tags': event.tags
                })
            
            # Process based on event type
            if event.event_type == AnalyticsEventType.PATTERN_DETECTED:
                self._handle_pattern_detected(event)
            elif event.event_type == AnalyticsEventType.CONFLUENCE_UPDATED:
                self._handle_confluence_updated(event)
            elif event.event_type == AnalyticsEventType.SIGNAL_GENERATED:
                self._handle_signal_generated(event)
            elif event.event_type == AnalyticsEventType.TRADE_OUTCOME:
                self._handle_trade_outcome(event)
            elif event.event_type == AnalyticsEventType.PERFORMANCE_UPDATE:
                self._handle_performance_update(event)
            elif event.event_type == AnalyticsEventType.LEARNING_INSIGHT:
                self._handle_learning_insight(event)
            elif event.event_type == AnalyticsEventType.MARKET_STRUCTURE_CHANGE:
                self._handle_market_structure_change(event)
            elif event.event_type == AnalyticsEventType.SYSTEM_STATUS:
                self._handle_system_status(event)
            
            # Notify subscribers
            self._notify_subscribers(event)
            
        except Exception as e:
            self.logger.error(f"❌ Error processing analytics event {event.event_id}: {e}")
    
    def _handle_pattern_detected(self, event: AnalyticsEvent) -> None:
        """🎯 Handle pattern detection event"""
        with self.lock:
            self.metrics.patterns_detected_today += 1
            
            pattern_type = event.data.get('pattern_type', 'UNKNOWN')
            if pattern_type not in self.metrics.patterns_by_type:
                self.metrics.patterns_by_type[pattern_type] = 0
            self.metrics.patterns_by_type[pattern_type] += 1
            
            # Add to active patterns
            pattern_data = {
                'pattern_type': pattern_type,
                'symbol': event.symbol,
                'timeframe': event.timeframe,
                'strength': event.data.get('strength', 0.0),
                'timestamp': event.timestamp.isoformat(),
                'confluence_score': event.data.get('confluence_score', 0.0)
            }
            self.live_data.active_patterns.append(pattern_data)
            
            # Keep only recent patterns (last 50)
            if len(self.live_data.active_patterns) > 50:
                self.live_data.active_patterns = self.live_data.active_patterns[-50:]
    
    def _handle_confluence_updated(self, event: AnalyticsEvent) -> None:
        """🔗 Handle confluence update event"""
        with self.lock:
            confluence_data = {
                'symbol': event.symbol,
                'timeframe': event.timeframe,
                'overall_strength': event.data.get('overall_strength', 0.0),
                'pattern_count': event.data.get('pattern_count', 0),
                'market_bias': event.data.get('market_bias', 'NEUTRAL'),
                'timestamp': event.timestamp.isoformat()
            }
            self.live_data.current_confluences.append(confluence_data)
            
            # Keep only recent confluences
            if len(self.live_data.current_confluences) > 30:
                self.live_data.current_confluences = self.live_data.current_confluences[-30:]
    
    def _handle_signal_generated(self, event: AnalyticsEvent) -> None:
        """🎯 Handle signal generation event"""
        with self.lock:
            self.metrics.signals_generated_today += 1
            
            signal_type = event.data.get('signal_type', 'UNKNOWN')
            if signal_type not in self.metrics.signals_by_type:
                self.metrics.signals_by_type[signal_type] = 0
            self.metrics.signals_by_type[signal_type] += 1
            
            # Add to active signals
            signal_data = {
                'signal_type': signal_type,
                'symbol': event.symbol,
                'timeframe': event.timeframe,
                'strength': event.data.get('strength', 0.0),
                'setup_quality': event.data.get('setup_quality', 'UNKNOWN'),
                'timestamp': event.timestamp.isoformat()
            }
            self.live_data.active_signals.append(signal_data)
            
            # Keep only recent signals
            if len(self.live_data.active_signals) > 50:
                self.live_data.active_signals = self.live_data.active_signals[-50:]
    
    def _handle_trade_outcome(self, event: AnalyticsEvent) -> None:
        """📊 Handle trade outcome event"""
        with self.lock:
            self.metrics.total_trades_today += 1
            
            outcome = event.data.get('outcome', 'UNKNOWN')
            profit_r = event.data.get('profit_r', 0.0)
            
            if profit_r > 0:
                self.metrics.winning_trades += 1
            else:
                self.metrics.losing_trades += 1
            
            self.metrics.total_pnl_r += profit_r
            
            # Update win rate
            if self.metrics.total_trades_today > 0:
                self.metrics.win_rate = (self.metrics.winning_trades / self.metrics.total_trades_today) * 100
    
    def _handle_performance_update(self, event: AnalyticsEvent) -> None:
        """📈 Handle performance update event"""
        performance_data = {
            'timestamp': event.timestamp.isoformat(),
            'symbol': event.symbol,
            'metric_type': event.data.get('metric_type', 'UNKNOWN'),
            'value': event.data.get('value', 0.0),
            'metadata': event.data.get('metadata', {})
        }
        
        with self.lock:
            self.live_data.performance_timeline.append(performance_data)
            
            # Keep timeline manageable
            if len(self.live_data.performance_timeline) > self.max_timeline_entries:
                self.live_data.performance_timeline = self.live_data.performance_timeline[-self.max_timeline_entries:]
    
    def _handle_learning_insight(self, event: AnalyticsEvent) -> None:
        """💡 Handle learning insight event"""
        with self.lock:
            self.metrics.insights_generated += 1
            
            learning_data = {
                'timestamp': event.timestamp.isoformat(),
                'insight_type': event.data.get('insight_type', 'UNKNOWN'),
                'patterns': event.data.get('patterns', []),
                'confidence': event.data.get('confidence', 0.0),
                'recommendation': event.data.get('recommendation', ''),
                'priority': event.data.get('priority', 5)
            }
            
            self.live_data.learning_progression.append(learning_data)
            
            # Keep learning data manageable
            if len(self.live_data.learning_progression) > 100:
                self.live_data.learning_progression = self.live_data.learning_progression[-100:]
    
    def _handle_market_structure_change(self, event: AnalyticsEvent) -> None:
        """🏗️ Handle market structure change event"""
        with self.lock:
            self.live_data.market_structure_status = {
                'timestamp': event.timestamp.isoformat(),
                'symbol': event.symbol,
                'timeframe': event.timeframe,
                'phase': event.data.get('phase', 'UNKNOWN'),
                'trend_direction': event.data.get('trend_direction', 'UNKNOWN'),
                'trend_strength': event.data.get('trend_strength', 0.0),
                'phase_confidence': event.data.get('phase_confidence', 0.0)
            }
    
    def _handle_system_status(self, event: AnalyticsEvent) -> None:
        """🔧 Handle system status event"""
        status_type = event.data.get('status_type', 'INFO')
        if status_type == 'ERROR':
            with self.lock:
                self.metrics.error_count += 1
    
    def _notify_subscribers(self, event: AnalyticsEvent) -> None:
        """📢 Notify event subscribers"""
        try:
            subscribers = self.event_subscribers.get(event.component, [])
            for callback in subscribers:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"❌ Error in subscriber callback: {e}")
        except Exception as e:
            self.logger.error(f"❌ Error notifying subscribers: {e}")
    
    def _initialize_dashboard_metrics(self) -> None:
        """📊 Initialize dashboard metrics"""
        with self.lock:
            self.metrics = DashboardMetrics()
            self.metrics.last_update = datetime.now()
    
    def _update_dashboard_metrics(self) -> None:
        """📊 Update dashboard metrics from analysis engines"""
        try:
            with self.lock:
                # Update system metrics
                self.metrics.system_uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
                
                if self.processing_times:
                    self.metrics.avg_processing_time_ms = sum(self.processing_times) / len(self.processing_times)
                
                # Update learning metrics
                if self.learning_system:
                    learning_stats = self.learning_system.get_session_stats()
                    self.metrics.learning_records_today = learning_stats.get('total_learning_records', 0)
                    self.metrics.learning_accuracy = learning_stats.get('learning_accuracy', 0.0)
                    self.metrics.pattern_confidence_avg = learning_stats.get('avg_pattern_confidence', 0.0)
                
                # Update signal metrics
                if self.signal_synthesizer:
                    signal_stats = self.signal_synthesizer.get_session_stats()
                    signal_dist = signal_stats.get('signals_generated', {})
                    self.metrics.signals_by_type.update(signal_dist)
                    if signal_dist:
                        self.metrics.signals_generated_today = sum(signal_dist.values())
                
                self.metrics.last_update = datetime.now()
                
        except Exception as e:
            self.logger.error(f"❌ Error updating dashboard metrics: {e}")
    
    def _refresh_live_data(self) -> None:
        """🔄 Refresh live analytics data"""
        try:
            # Update pattern heatmap
            with self.lock:
                self.live_data.pattern_heatmap = self.get_pattern_performance_heatmap()
                
            # Clean up old data
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=1)  # Keep last hour of data
            
            # Remove old active patterns
            with self.lock:
                self.live_data.active_patterns = [
                    p for p in self.live_data.active_patterns
                    if datetime.fromisoformat(p['timestamp']) > cutoff_time
                ]
                
                # Remove old active signals
                self.live_data.active_signals = [
                    s for s in self.live_data.active_signals
                    if datetime.fromisoformat(s['timestamp']) > cutoff_time
                ]
                
        except Exception as e:
            self.logger.error(f"❌ Error refreshing live data: {e}")
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """📋 Get complete dashboard summary"""
        return {
            'metrics': self.get_live_metrics(),
            'live_data': self.get_live_analytics_data(),
            'pattern_heatmap': self.get_pattern_performance_heatmap(),
            'signal_distribution': self.get_signal_distribution(),
            'confluence_analytics': self.get_confluence_analytics(),
            'market_structure': self.get_market_structure_overview(),
            'system_status': {
                'is_active': self.is_active,
                'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
                'events_processed': self.total_events_processed,
                'queue_size': self.event_queue.qsize()
            }
        }


# Singleton pattern for global access
_dashboard_instance = None
_dashboard_lock = threading.Lock()


def get_realtime_analytics_dashboard() -> RealTimeAnalyticsDashboard:
    """📊 Get Real-Time Analytics Dashboard singleton instance"""
    global _dashboard_instance
    
    if _dashboard_instance is None:
        with _dashboard_lock:
            if _dashboard_instance is None:
                _dashboard_instance = RealTimeAnalyticsDashboard()
    
    return _dashboard_instance


if __name__ == "__main__":
    # Basic test
    dashboard = get_realtime_analytics_dashboard()
    dashboard.start_analytics_streaming()
    
    # Test event publication
    dashboard.publish_analytics_event(
        AnalyticsEventType.SYSTEM_STATUS,
        "TEST",
        "1H",
        DashboardComponent.SYSTEM_HEALTH,
        {"status": "test_mode", "message": "Dashboard test"},
        priority=7
    )
    
    print("📊 Real-Time Analytics Dashboard v6.1 test completed")
    
    # Clean shutdown
    time.sleep(2)
    dashboard.stop_analytics_streaming()
