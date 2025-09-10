"""
🧪 ADVANCED PATTERN ANALYTICS VALIDATION v6.1
Comprehensive validation suite for FASE 2 WEEK 3 DAY 3

This script validates all components of Advanced Pattern Analytics:
- Pattern Confluence Engine (v6.1)
- Market Structure Intelligence (v6.1)
- Trading Signal Synthesizer (v6.1)  
- Pattern Learning System (v6.1)
- Real-Time Analytics Dashboard (v6.1)
- Advanced Pattern Analytics Integrator (v6.1)

All components are validated individually and as an integrated system.
"""

import time
import random
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "01-CORE"))

# Import all analytics components
try:
    from analysis.pattern_confluence_engine import get_confluence_engine, PatternType
    from analysis.market_structure_intelligence import get_market_structure_intelligence, MarketPhase
    from analysis.trading_signal_synthesizer import get_trading_signal_synthesizer, TradingSignal
    from analysis.pattern_learning_system import get_pattern_learning_system, PatternOutcome
    from analysis.realtime_analytics_dashboard import get_realtime_analytics_dashboard, AnalyticsEventType, DashboardComponent
    from analysis.advanced_pattern_analytics_integrator import get_advanced_pattern_analytics_integrator, AnalyticsMode
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importing components: {e}")
    COMPONENTS_AVAILABLE = False

# Test configuration
TEST_SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
TEST_TIMEFRAMES = ["1H", "4H", "1D"]
TEST_ITERATIONS = 10
VALIDATION_PHASES = [
    "PHASE_1_PATTERN_CONFLUENCE_ENGINE",
    "PHASE_2_MARKET_STRUCTURE_INTELLIGENCE", 
    "PHASE_3_TRADING_SIGNAL_SYNTHESIZER",
    "PHASE_4_PATTERN_LEARNING_SYSTEM",
    "PHASE_5_REALTIME_ANALYTICS_DASHBOARD",
    "PHASE_6_INTEGRATION_TESTING"
]

class ValidationResults:
    """📊 Validation results tracker"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = []
        self.performance_metrics = {}
    
    def add_result(self, phase: str, test_name: str, passed: bool, 
                   duration_ms: float = 0.0, details: str = ""):
        """Add test result"""
        if phase not in self.results:
            self.results[phase] = []
        
        self.results[phase].append({
            'test_name': test_name,
            'passed': passed,
            'duration_ms': duration_ms,
            'details': details,
            'timestamp': datetime.now()
        })
        
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            self.errors.append(f"{phase}::{test_name}: {details}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'success_rate': (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0,
            'total_duration_seconds': duration,
            'errors': self.errors,
            'phase_results': {phase: len([r for r in results if r['passed']]) for phase, results in self.results.items()},
            'performance_metrics': self.performance_metrics
        }


def generate_test_candles(periods: int = 100) -> pd.DataFrame:
    """🕯️ Generate realistic test candle data"""
    np.random.seed(42)  # Reproducible results
    
    # Start with a base price
    base_price = 1.1000
    
    # Generate price movements with some trend and volatility
    returns = np.random.normal(0.0002, 0.01, periods)  # Small trend with volatility
    prices = [base_price]
    
    for ret in returns:
        new_price = prices[-1] * (1 + ret)
        prices.append(new_price)
    
    # Create OHLC data
    ohlc_data = []
    for i in range(periods):
        open_price = prices[i]
        close_price = prices[i + 1]
        
        # Generate high and low based on open/close
        if close_price > open_price:  # Bullish candle
            high = max(open_price, close_price) + abs(close_price - open_price) * random.uniform(0.1, 0.5)
            low = min(open_price, close_price) - abs(close_price - open_price) * random.uniform(0.1, 0.3)
        else:  # Bearish candle
            high = max(open_price, close_price) + abs(open_price - close_price) * random.uniform(0.1, 0.3)
            low = min(open_price, close_price) - abs(open_price - close_price) * random.uniform(0.1, 0.5)
        
        volume = random.randint(1000, 10000)
        timestamp = datetime.now() - timedelta(hours=periods-i)
        
        ohlc_data.append({
            'timestamp': timestamp,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    return pd.DataFrame(ohlc_data)


def validate_phase_1_confluence_engine(results: ValidationResults) -> None:
    """🧪 PHASE 1: Pattern Confluence Engine Validation"""
    print("🧪 PHASE 1: Testing Pattern Confluence Engine...")
    
    try:
        confluence_engine = get_confluence_engine()
        
        # Test 1: Engine initialization
        start_time = time.time()
        if confluence_engine is not None:
            duration = (time.time() - start_time) * 1000
            results.add_result("PHASE_1_PATTERN_CONFLUENCE_ENGINE", "engine_initialization", 
                             True, duration, "Engine initialized successfully")
        else:
            results.add_result("PHASE_1_PATTERN_CONFLUENCE_ENGINE", "engine_initialization", 
                             False, 0, "Failed to initialize engine")
            return
        
        # Test 2: Basic confluence analysis
        for symbol in TEST_SYMBOLS[:2]:  # Test with 2 symbols
            for timeframe in TEST_TIMEFRAMES[:2]:  # Test with 2 timeframes
                try:
                    start_time = time.time()
                    candles = generate_test_candles(50)
                    
                    analysis = confluence_engine.analyze_confluence(candles, symbol, timeframe)
                    duration = (time.time() - start_time) * 1000
                    
                    # Validate analysis result
                    if (hasattr(analysis, 'confluence_id') and 
                        hasattr(analysis, 'overall_strength') and
                        hasattr(analysis, 'pattern_confluences')):
                        results.add_result("PHASE_1_PATTERN_CONFLUENCE_ENGINE", 
                                         f"confluence_analysis_{symbol}_{timeframe}", 
                                         True, duration, f"Analysis completed: {analysis.overall_strength:.1f}% strength")
                    else:
                        results.add_result("PHASE_1_PATTERN_CONFLUENCE_ENGINE", 
                                         f"confluence_analysis_{symbol}_{timeframe}", 
                                         False, duration, "Invalid analysis result structure")
                
                except Exception as e:
                    results.add_result("PHASE_1_PATTERN_CONFLUENCE_ENGINE", 
                                     f"confluence_analysis_{symbol}_{timeframe}", 
                                     False, 0, f"Error: {str(e)}")
        
        # Test 3: Session statistics
        try:
            stats = confluence_engine.get_session_stats()
            if isinstance(stats, dict) and 'total_analyses' in stats:
                results.add_result("PHASE_1_PATTERN_CONFLUENCE_ENGINE", "session_statistics", 
                                 True, 0, f"Stats retrieved: {stats['total_analyses']} analyses")
            else:
                results.add_result("PHASE_1_PATTERN_CONFLUENCE_ENGINE", "session_statistics", 
                                 False, 0, "Invalid statistics format")
        except Exception as e:
            results.add_result("PHASE_1_PATTERN_CONFLUENCE_ENGINE", "session_statistics", 
                             False, 0, f"Error: {str(e)}")
    
    except Exception as e:
        results.add_result("PHASE_1_PATTERN_CONFLUENCE_ENGINE", "critical_error", 
                         False, 0, f"Critical error: {str(e)}")


def validate_phase_2_structure_intelligence(results: ValidationResults) -> None:
    """🧪 PHASE 2: Market Structure Intelligence Validation"""
    print("🧪 PHASE 2: Testing Market Structure Intelligence...")
    
    try:
        structure_intelligence = get_market_structure_intelligence()
        
        # Test 1: Engine initialization
        start_time = time.time()
        if structure_intelligence is not None:
            duration = (time.time() - start_time) * 1000
            results.add_result("PHASE_2_MARKET_STRUCTURE_INTELLIGENCE", "engine_initialization", 
                             True, duration, "Structure intelligence initialized")
        else:
            results.add_result("PHASE_2_MARKET_STRUCTURE_INTELLIGENCE", "engine_initialization", 
                             False, 0, "Failed to initialize structure intelligence")
            return
        
        # Test 2: Market structure analysis
        for symbol in TEST_SYMBOLS[:2]:
            for timeframe in TEST_TIMEFRAMES[:2]:
                try:
                    start_time = time.time()
                    candles = generate_test_candles(50)
                    
                    analysis = structure_intelligence.analyze_market_structure(candles, symbol, timeframe)
                    duration = (time.time() - start_time) * 1000
                    
                    # Validate analysis result
                    if (hasattr(analysis, 'analysis_id') and 
                        hasattr(analysis, 'current_phase') and
                        hasattr(analysis, 'trend_direction')):
                        results.add_result("PHASE_2_MARKET_STRUCTURE_INTELLIGENCE", 
                                         f"structure_analysis_{symbol}_{timeframe}", 
                                         True, duration, f"Analysis: {analysis.current_phase.value} phase")
                    else:
                        results.add_result("PHASE_2_MARKET_STRUCTURE_INTELLIGENCE", 
                                         f"structure_analysis_{symbol}_{timeframe}", 
                                         False, duration, "Invalid analysis result structure")
                
                except Exception as e:
                    results.add_result("PHASE_2_MARKET_STRUCTURE_INTELLIGENCE", 
                                     f"structure_analysis_{symbol}_{timeframe}", 
                                     False, 0, f"Error: {str(e)}")
        
        # Test 3: Session statistics
        try:
            stats = structure_intelligence.get_session_stats()
            if isinstance(stats, dict):
                results.add_result("PHASE_2_MARKET_STRUCTURE_INTELLIGENCE", "session_statistics", 
                                 True, 0, "Statistics retrieved successfully")
            else:
                results.add_result("PHASE_2_MARKET_STRUCTURE_INTELLIGENCE", "session_statistics", 
                                 False, 0, "Invalid statistics format")
        except Exception as e:
            results.add_result("PHASE_2_MARKET_STRUCTURE_INTELLIGENCE", "session_statistics", 
                             False, 0, f"Error: {str(e)}")
    
    except Exception as e:
        results.add_result("PHASE_2_MARKET_STRUCTURE_INTELLIGENCE", "critical_error", 
                         False, 0, f"Critical error: {str(e)}")


def validate_phase_3_signal_synthesizer(results: ValidationResults) -> None:
    """🧪 PHASE 3: Trading Signal Synthesizer Validation"""
    print("🧪 PHASE 3: Testing Trading Signal Synthesizer...")
    
    try:
        signal_synthesizer = get_trading_signal_synthesizer()
        
        # Test 1: Engine initialization
        start_time = time.time()
        if signal_synthesizer is not None:
            duration = (time.time() - start_time) * 1000
            results.add_result("PHASE_3_TRADING_SIGNAL_SYNTHESIZER", "engine_initialization", 
                             True, duration, "Signal synthesizer initialized")
        else:
            results.add_result("PHASE_3_TRADING_SIGNAL_SYNTHESIZER", "engine_initialization", 
                             False, 0, "Failed to initialize signal synthesizer")
            return
        
        # Test 2: Signal synthesis
        for symbol in TEST_SYMBOLS[:2]:
            for timeframe in TEST_TIMEFRAMES[:2]:
                try:
                    start_time = time.time()
                    candles = generate_test_candles(50)
                    
                    trade_setup = signal_synthesizer.synthesize_trading_signals(candles, symbol, timeframe)
                    duration = (time.time() - start_time) * 1000
                    
                    # Validate trade setup
                    if (hasattr(trade_setup, 'setup_id') and 
                        hasattr(trade_setup, 'primary_signal') and
                        hasattr(trade_setup, 'setup_quality')):
                        results.add_result("PHASE_3_TRADING_SIGNAL_SYNTHESIZER", 
                                         f"signal_synthesis_{symbol}_{timeframe}", 
                                         True, duration, f"Signal: {trade_setup.primary_signal.value}")
                    else:
                        results.add_result("PHASE_3_TRADING_SIGNAL_SYNTHESIZER", 
                                         f"signal_synthesis_{symbol}_{timeframe}", 
                                         False, duration, "Invalid trade setup structure")
                
                except Exception as e:
                    results.add_result("PHASE_3_TRADING_SIGNAL_SYNTHESIZER", 
                                     f"signal_synthesis_{symbol}_{timeframe}", 
                                     False, 0, f"Error: {str(e)}")
        
        # Test 3: Session statistics
        try:
            stats = signal_synthesizer.get_session_stats()
            if isinstance(stats, dict):
                results.add_result("PHASE_3_TRADING_SIGNAL_SYNTHESIZER", "session_statistics", 
                                 True, 0, "Statistics retrieved successfully")
            else:
                results.add_result("PHASE_3_TRADING_SIGNAL_SYNTHESIZER", "session_statistics", 
                                 False, 0, "Invalid statistics format")
        except Exception as e:
            results.add_result("PHASE_3_TRADING_SIGNAL_SYNTHESIZER", "session_statistics", 
                             False, 0, f"Error: {str(e)}")
    
    except Exception as e:
        results.add_result("PHASE_3_TRADING_SIGNAL_SYNTHESIZER", "critical_error", 
                         False, 0, f"Critical error: {str(e)}")


def validate_phase_4_learning_system(results: ValidationResults) -> None:
    """🧪 PHASE 4: Pattern Learning System Validation"""
    print("🧪 PHASE 4: Testing Pattern Learning System...")
    
    try:
        learning_system = get_pattern_learning_system()
        
        # Test 1: System initialization
        start_time = time.time()
        if learning_system is not None:
            duration = (time.time() - start_time) * 1000
            results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "system_initialization", 
                             True, duration, "Learning system initialized")
        else:
            results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "system_initialization", 
                             False, 0, "Failed to initialize learning system")
            return
        
        # Test 2: Pattern recording and learning
        try:
            start_time = time.time()
            
            # Record some patterns
            record_ids = []
            for i in range(3):
                record_id = learning_system.record_pattern_detection(
                    PatternType.ORDER_BLOCK,
                    "EURUSD",
                    "1H",
                    80.0 + i * 5,  # Different strengths
                    75.0 + i * 3   # Different confluence scores
                )
                record_ids.append(record_id)
            
            duration = (time.time() - start_time) * 1000
            results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "pattern_recording", 
                             True, duration, f"Recorded {len(record_ids)} patterns")
            
            # Test 3: Outcome updates
            if record_ids:
                learning_system.update_pattern_outcome(
                    record_ids[0], 
                    PatternOutcome.WIN, 
                    2.5, 
                    "Test outcome update"
                )
                results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "outcome_update", 
                                 True, 0, "Outcome updated successfully")
        
        except Exception as e:
            results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "pattern_recording", 
                             False, 0, f"Error: {str(e)}")
        
        # Test 4: Performance summary
        try:
            performance = learning_system.get_pattern_performance_summary()
            if isinstance(performance, dict):
                results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "performance_summary", 
                                 True, 0, f"Performance data for {len(performance)} patterns")
            else:
                results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "performance_summary", 
                                 False, 0, "Invalid performance data format")
        except Exception as e:
            results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "performance_summary", 
                             False, 0, f"Error: {str(e)}")
        
        # Test 5: Session statistics
        try:
            stats = learning_system.get_session_stats()
            if isinstance(stats, dict):
                results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "session_statistics", 
                                 True, 0, "Statistics retrieved successfully")
            else:
                results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "session_statistics", 
                                 False, 0, "Invalid statistics format")
        except Exception as e:
            results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "session_statistics", 
                             False, 0, f"Error: {str(e)}")
    
    except Exception as e:
        results.add_result("PHASE_4_PATTERN_LEARNING_SYSTEM", "critical_error", 
                         False, 0, f"Critical error: {str(e)}")


def validate_phase_5_analytics_dashboard(results: ValidationResults) -> None:
    """🧪 PHASE 5: Real-Time Analytics Dashboard Validation"""
    print("🧪 PHASE 5: Testing Real-Time Analytics Dashboard...")
    
    try:
        dashboard = get_realtime_analytics_dashboard()
        
        # Test 1: Dashboard initialization
        start_time = time.time()
        if dashboard is not None:
            duration = (time.time() - start_time) * 1000
            results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "dashboard_initialization", 
                             True, duration, "Dashboard initialized")
        else:
            results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "dashboard_initialization", 
                             False, 0, "Failed to initialize dashboard")
            return
        
        # Test 2: Start analytics streaming
        try:
            start_time = time.time()
            dashboard.start_analytics_streaming()
            time.sleep(1)  # Let it start
            duration = (time.time() - start_time) * 1000
            
            if dashboard.is_active:
                results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "streaming_start", 
                                 True, duration, "Streaming started successfully")
            else:
                results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "streaming_start", 
                                 False, duration, "Streaming failed to start")
        except Exception as e:
            results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "streaming_start", 
                             False, 0, f"Error: {str(e)}")
        
        # Test 3: Event publishing
        try:
            start_time = time.time()
            event_id = dashboard.publish_analytics_event(
                AnalyticsEventType.PATTERN_DETECTED,
                "EURUSD",
                "1H",
                DashboardComponent.PATTERN_MONITOR,
                {"pattern_type": "ORDER_BLOCK", "strength": 85.0},
                priority=7,
                tags=["test", "validation"]
            )
            duration = (time.time() - start_time) * 1000
            
            if event_id:
                results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "event_publishing", 
                                 True, duration, f"Event published: {event_id}")
            else:
                results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "event_publishing", 
                                 False, duration, "Failed to publish event")
        except Exception as e:
            results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "event_publishing", 
                             False, 0, f"Error: {str(e)}")
        
        # Test 4: Live metrics
        try:
            metrics = dashboard.get_live_metrics()
            if isinstance(metrics, dict) and 'patterns_detected_today' in metrics:
                results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "live_metrics", 
                                 True, 0, "Live metrics retrieved")
            else:
                results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "live_metrics", 
                                 False, 0, "Invalid metrics format")
        except Exception as e:
            results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "live_metrics", 
                             False, 0, f"Error: {str(e)}")
        
        # Test 5: Dashboard summary
        try:
            summary = dashboard.get_dashboard_summary()
            if isinstance(summary, dict) and 'metrics' in summary:
                results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "dashboard_summary", 
                                 True, 0, "Dashboard summary retrieved")
            else:
                results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "dashboard_summary", 
                                 False, 0, "Invalid summary format")
        except Exception as e:
            results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "dashboard_summary", 
                             False, 0, f"Error: {str(e)}")
        
        # Test 6: Stop streaming
        try:
            dashboard.stop_analytics_streaming()
            time.sleep(0.5)  # Let it stop
            
            if not dashboard.is_active:
                results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "streaming_stop", 
                                 True, 0, "Streaming stopped successfully")
            else:
                results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "streaming_stop", 
                                 False, 0, "Failed to stop streaming")
        except Exception as e:
            results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "streaming_stop", 
                             False, 0, f"Error: {str(e)}")
    
    except Exception as e:
        results.add_result("PHASE_5_REALTIME_ANALYTICS_DASHBOARD", "critical_error", 
                         False, 0, f"Critical error: {str(e)}")


def validate_phase_6_integration_testing(results: ValidationResults) -> None:
    """🧪 PHASE 6: Integration Testing"""
    print("🧪 PHASE 6: Testing Complete Integration...")
    
    try:
        integrator = get_advanced_pattern_analytics_integrator(AnalyticsMode.FULL_ANALYTICS)
        
        # Test 1: System initialization
        start_time = time.time()
        initialization_success = integrator.initialize_analytics_system()
        duration = (time.time() - start_time) * 1000
        
        if initialization_success:
            results.add_result("PHASE_6_INTEGRATION_TESTING", "system_initialization", 
                             True, duration, "Integrated system initialized")
        else:
            results.add_result("PHASE_6_INTEGRATION_TESTING", "system_initialization", 
                             False, duration, "Failed to initialize integrated system")
            return
        
        # Test 2: Complete analysis
        try:
            start_time = time.time()
            candles = generate_test_candles(100)
            
            analysis_result = integrator.perform_complete_analysis(candles, "EURUSD", "1H")
            duration = (time.time() - start_time) * 1000
            
            if (hasattr(analysis_result, 'analysis_id') and 
                hasattr(analysis_result, 'overall_score') and
                hasattr(analysis_result, 'recommendation')):
                results.add_result("PHASE_6_INTEGRATION_TESTING", "complete_analysis", 
                                 True, duration, f"Analysis: {analysis_result.recommendation} ({analysis_result.overall_score:.1f})")
            else:
                results.add_result("PHASE_6_INTEGRATION_TESTING", "complete_analysis", 
                                 False, duration, "Invalid analysis result structure")
        except Exception as e:
            results.add_result("PHASE_6_INTEGRATION_TESTING", "complete_analysis", 
                             False, 0, f"Error: {str(e)}")
        
        # Test 3: Multiple analyses (stress test)
        try:
            start_time = time.time()
            analysis_count = 5
            successful_analyses = 0
            
            for i in range(analysis_count):
                try:
                    candles = generate_test_candles(50)
                    result = integrator.perform_complete_analysis(candles, random.choice(TEST_SYMBOLS), random.choice(TEST_TIMEFRAMES))
                    if hasattr(result, 'analysis_id'):
                        successful_analyses += 1
                except:
                    pass
            
            duration = (time.time() - start_time) * 1000
            
            if successful_analyses >= analysis_count * 0.8:  # 80% success rate
                results.add_result("PHASE_6_INTEGRATION_TESTING", "multiple_analyses", 
                                 True, duration, f"{successful_analyses}/{analysis_count} analyses successful")
            else:
                results.add_result("PHASE_6_INTEGRATION_TESTING", "multiple_analyses", 
                                 False, duration, f"Only {successful_analyses}/{analysis_count} analyses successful")
        except Exception as e:
            results.add_result("PHASE_6_INTEGRATION_TESTING", "multiple_analyses", 
                             False, 0, f"Error: {str(e)}")
        
        # Test 4: System status
        try:
            status = integrator.get_system_status()
            if isinstance(status, dict) and 'integration_status' in status:
                results.add_result("PHASE_6_INTEGRATION_TESTING", "system_status", 
                                 True, 0, f"Status: {status['integration_status']}")
            else:
                results.add_result("PHASE_6_INTEGRATION_TESTING", "system_status", 
                                 False, 0, "Invalid status format")
        except Exception as e:
            results.add_result("PHASE_6_INTEGRATION_TESTING", "system_status", 
                             False, 0, f"Error: {str(e)}")
        
        # Test 5: System shutdown
        try:
            integrator.shutdown_analytics_system()
            results.add_result("PHASE_6_INTEGRATION_TESTING", "system_shutdown", 
                             True, 0, "System shutdown completed")
        except Exception as e:
            results.add_result("PHASE_6_INTEGRATION_TESTING", "system_shutdown", 
                             False, 0, f"Error: {str(e)}")
    
    except Exception as e:
        results.add_result("PHASE_6_INTEGRATION_TESTING", "critical_error", 
                         False, 0, f"Critical error: {str(e)}")


def print_validation_results(results: ValidationResults) -> None:
    """📊 Print comprehensive validation results"""
    summary = results.get_summary()
    
    print("\n" + "="*80)
    print("🎯 ADVANCED PATTERN ANALYTICS VALIDATION RESULTS")
    print("="*80)
    
    print(f"\n📊 OVERALL SUMMARY:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed_tests']} ✅")
    print(f"   Failed: {summary['failed_tests']} ❌")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Total Duration: {summary['total_duration_seconds']:.2f} seconds")
    
    print(f"\n📋 PHASE RESULTS:")
    for phase, passed_count in summary['phase_results'].items():
        total_phase_tests = len(results.results.get(phase, []))
        success_rate = (passed_count / total_phase_tests * 100) if total_phase_tests > 0 else 0
        status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
        print(f"   {phase}: {passed_count}/{total_phase_tests} ({success_rate:.1f}%) {status}")
    
    if summary['errors']:
        print(f"\n❌ ERRORS ({len(summary['errors'])}):")
        for error in summary['errors']:
            print(f"   • {error}")
    
    # Detailed results
    print(f"\n📝 DETAILED RESULTS:")
    for phase, phase_results in results.results.items():
        print(f"\n{phase}:")
        for test in phase_results:
            status = "✅" if test['passed'] else "❌"
            duration_str = f" ({test['duration_ms']:.1f}ms)" if test['duration_ms'] > 0 else ""
            print(f"   {test['test_name']}: {status}{duration_str}")
            if test['details']:
                print(f"      {test['details']}")
    
    # Final verdict
    print(f"\n🏆 FINAL VERDICT:")
    if summary['success_rate'] >= 90:
        print("   🟢 EXCELLENT - All systems operational!")
    elif summary['success_rate'] >= 80:
        print("   🟡 GOOD - Minor issues detected")
    elif summary['success_rate'] >= 60:
        print("   🟠 FAIR - Some components need attention")
    else:
        print("   🔴 POOR - Significant issues require fixing")
    
    print("\n" + "="*80)


def main():
    """🚀 Main validation function"""
    print("🧪 ADVANCED PATTERN ANALYTICS VALIDATION v6.1")
    print("=" * 60)
    print("Testing all components of FASE 2 WEEK 3 DAY 3")
    print("=" * 60)
    
    if not COMPONENTS_AVAILABLE:
        print("❌ Components not available for testing")
        return
    
    results = ValidationResults()
    
    # Run all validation phases
    try:
        validate_phase_1_confluence_engine(results)
        validate_phase_2_structure_intelligence(results)
        validate_phase_3_signal_synthesizer(results)
        validate_phase_4_learning_system(results)
        validate_phase_5_analytics_dashboard(results)
        validate_phase_6_integration_testing(results)
        
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
    except Exception as e:
        print(f"\n❌ Critical validation error: {e}")
        results.add_result("VALIDATION_SYSTEM", "critical_error", False, 0, str(e))
    
    # Print results
    print_validation_results(results)
    
    # Return success status
    summary = results.get_summary()
    return summary['success_rate'] >= 80


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
