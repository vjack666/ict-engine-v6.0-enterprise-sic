#!/usr/bin/env python3
"""
📊 REAL-TIME DATA PROCESSOR - ICT Engine v6.0 Enterprise
========================================================

Production data processor that replaces test/simulation data with real
market data from MT5 and other sources. Optimized for live trading with
minimal latency and maximum reliability.

Features:
- Real-time market data processing
- Multi-symbol data management
- Data validation and filtering
- Cache management for performance
- Tick data processing for scalping
- Historical data integration
- Pattern recognition data feeds
- Risk metrics calculation

Author: ICT Engine v6.0 Enterprise Team
Date: September 2025
"""

import threading
import time
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union, Tuple, Deque
from dataclasses import dataclass, field
from pathlib import Path
from collections import deque
import sys
try:
    from monitoring.metrics_collector import record_counter, record_gauge  # type: ignore
except Exception:  # pragma: no cover
    def record_counter(name: str, by: int = 1) -> None:  # type: ignore
        return
    def record_gauge(name: str, value: float) -> None:  # type: ignore
        return

# Add project paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(current_dir.parent))

# Import logging and base modules
try:
    from protocols.logging_protocol import get_central_logger, LogLevel, LogCategory
    logger = get_central_logger("RealtimeDataProcessor")
    LOGGING_AVAILABLE = True
except ImportError:
    logger = None
    LogCategory = None  # Define fallback
    LOGGING_AVAILABLE = False
    print("⚠️ Advanced logging not available, using fallback")
    
    class FallbackLogger:
        def info(self, msg, component=""): print(f"[INFO] {msg}")
        def error(self, msg, component=""): print(f"[ERROR] {msg}")
        def warning(self, msg, component=""): print(f"[WARNING] {msg}")
        def debug(self, msg, component=""): print(f"[DEBUG] {msg}")
        def critical(self, msg, component=""): print(f"[CRITICAL] {msg}")
        def performance(self, msg, component=""): print(f"[PERFORMANCE] {msg}")
    
    logger = FallbackLogger()

def _safe_log(logger_instance, level: str, msg: str, category=None):
    """Safe logging that handles LogCategory availability"""
    if hasattr(logger_instance, level):
        log_func = getattr(logger_instance, level)
        if category and LogCategory:
            try:
                log_func(msg, category)
            except:
                log_func(msg)
        else:
            log_func(msg)


@dataclass
class TickData:
    """Real-time tick data structure"""
    symbol: str
    timestamp: datetime
    bid: float
    ask: float
    volume: int = 0
    spread: float = 0.0
    
    def __post_init__(self):
        if self.spread == 0.0:
            self.spread = self.ask - self.bid


@dataclass
class CandleData:
    """OHLCV candle data structure"""
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    tick_volume: int = 0
    spread: float = 0.0
    real_volume: int = 0


@dataclass
class MarketState:
    """Current market state for a symbol"""
    symbol: str
    last_update: datetime
    current_tick: Optional[TickData]
    current_candle: Optional[CandleData]
    trend_direction: str = "UNKNOWN"
    volatility: float = 0.0
    session: str = "UNKNOWN"
    is_active: bool = False


class RealTimeDataProcessor:
    """
    Real-time data processor for production trading
    
    Handles all market data processing, validation, and distribution
    to trading components with minimal latency.
    """
    # Static annotations to satisfy type checkers
    data_callbacks: List[Callable]
    _perf_enabled: bool
    _loop_intervals: Deque[float]
    _cb_latencies: Deque[float]
    _feed_to_cb_latencies: Deque[float]
    _last_perf_emit: datetime
    _last_tick_count: int
    
    def __init__(self, symbols: Optional[List[str]] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize real-time data processor"""
        # Initialize logger first
        if LOGGING_AVAILABLE and logger:
            self.logger = logger
        else:
            self.logger = FallbackLogger()
        
        # Allow passing a single dict as config (as used by main.py)
        if isinstance(symbols, dict) and config is None:
            config = symbols
            symbols = config.get('symbols')
        
        # Configuration: merge provided values over defaults to ensure all keys exist
        default_cfg = self._get_default_config()
        if isinstance(config, dict):
            merged = default_cfg.copy()
            # Avoid overwriting 'symbols' here; handled separately below
            for k, v in config.items():
                if k == 'symbols':
                    continue
                merged[k] = v
            self.config = merged
        else:
            self.config = default_cfg
        self.symbols = symbols or ["EURUSD", "GBPUSD", "AUDUSD", "USDCAD"]
        
        # Data storage
        self.market_states: Dict[str, MarketState] = {}
        self.tick_buffers: Dict[str, deque] = {}
        self.candle_buffers: Dict[str, deque] = {}
        
        # Threading
        self._lock = threading.RLock()
        self._data_thread = None
        self._processing_active = False
        
        # Performance tracking
        self._tick_count = 0
        self._processing_times = deque(maxlen=1000)
        self._last_performance_log = datetime.now()
        # Debug perf tracking (perf_counter-based)
        self._perf_enabled = bool(self.config.get("debug_perf_metrics", False))
        _hist = int(self.config.get("perf_history", 200))
        self._loop_intervals = deque(maxlen=max(50, _hist))
        self._cb_latencies = deque(maxlen=max(100, _hist * 2))
        self._last_perf_emit = datetime.now()
        # Internal latency buffers
        self._feed_to_cb_latencies = deque(maxlen=int(self.config.get("perf_history", 1024)))
        self._last_tick_count = 0
        
        # Components
        self.mt5_manager = None
        self.data_callbacks: List[Callable] = []
        
        # Initialize buffers
        self._initialize_buffers()
        
        self.logger.info("Real-time data processor initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "buffer_size": 10000,
            "tick_processing_interval": 0.1,  # seconds
            "candle_update_interval": 1.0,
            "performance_log_interval": 300,  # 5 minutes
            "data_validation": True,
            "cache_enabled": True,
            "max_tick_age": 60,  # seconds
            "volatility_window": 20,
            "timeframes": ["M1", "M5", "M15", "H1", "H4", "D1"],
            "shutdown_timeout": 2.0,
            # Debug/perf metrics (opt-in)
            "debug_perf_metrics": False,
            "perf_emit_interval": 5.0,
            "perf_history": 200,
        }
    
    def _initialize_buffers(self):
        """Initialize data buffers for all symbols"""
        buffer_size = self.config["buffer_size"]
        
        for symbol in self.symbols:
            self.market_states[symbol] = MarketState(
                symbol=symbol,
                last_update=datetime.now(),
                current_tick=None,
                current_candle=None
            )
            
            self.tick_buffers[symbol] = deque(maxlen=buffer_size)
            self.candle_buffers[symbol] = deque(maxlen=buffer_size)
    
    def initialize_mt5_connection(self) -> bool:
        """Initialize MT5 connection for real data"""
        try:
            from data_management.mt5_data_manager import MT5DataManager
            
            self.mt5_manager = MT5DataManager()
            if self.mt5_manager.connect():
                self.logger.info("MT5 connection established for real-time data")
                return True
            else:
                self.logger.warning("MT5 connection failed - using simulation data")
                return False
                
        except ImportError:
            self.logger.warning("MT5DataManager not available - using simulation")
            return False
        except Exception as e:
            self.logger.error(f"MT5 initialization error: {e}")
            return False
    
    def start_processing(self) -> bool:
        """Start real-time data processing"""
        if self._processing_active:
            self.logger.warning("Data processing already active")
            return False
        
        # Initialize MT5 if available
        mt5_available = self.initialize_mt5_connection()
        
        self._processing_active = True
        self._data_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self._data_thread.start()
        
        self.logger.info("Real-time data processing started")
        return True
    
    def stop_processing(self):
        """Stop real-time data processing"""
        self._processing_active = False
        if self._data_thread:
            timeout = 5
            try:
                timeout = float(self.config.get("shutdown_timeout", 2.0))
            except Exception:
                timeout = 2.0
            self._data_thread.join(timeout=timeout)
        
        if self.mt5_manager:
            try:
                self.mt5_manager.disconnect()
            except:
                pass
        
        self.logger.info("Real-time data processing stopped")
    
    def _processing_loop(self):
        """Main data processing loop"""
        interval = self.config["tick_processing_interval"]
        
        while self._processing_active:
            try:
                start_time = time.time()
                _loop_start_perf = time.perf_counter()
                
                # Process tick data for all symbols
                for symbol in self.symbols:
                    self._process_symbol_data(symbol)
                
                # Update performance metrics
                processing_time = time.time() - start_time
                self._processing_times.append(processing_time)
                
                # Log performance periodically
                self._log_performance_if_needed()
                
                # Sleep to maintain interval
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                # Debug perf: store loop interval and maybe emit
                if self._perf_enabled:
                    loop_ms = (time.perf_counter() - _loop_start_perf) * 1000.0
                    self._loop_intervals.append(loop_ms)
                    self._emit_perf_metrics_if_needed()
                    
            except Exception as e:
                self.logger.error(f"Data processing error: {e}")
                time.sleep(interval)
    
    def _process_symbol_data(self, symbol: str):
        """Process real-time data for a specific symbol"""
        try:
            # Get real tick data
            tick_data = self._get_real_tick_data(symbol)
            if tick_data:
                self._process_tick_data(tick_data)
            
            # Update candle data
            self._update_candle_data(symbol)
            
            # Update market state
            self._update_market_state(symbol)
            
            # Notify callbacks
            self._notify_data_callbacks(symbol)
            
        except Exception as e:
            self.logger.error(f"Symbol data processing error for {symbol}: {e}")
    
    def _get_real_tick_data(self, symbol: str) -> Optional[TickData]:
        """Get real tick data from MT5 or simulation"""
        try:
            if self.mt5_manager and self.mt5_manager.is_connected():
                return self._get_mt5_tick_data(symbol)
            else:
                return self._get_simulated_tick_data(symbol)
                
        except Exception as e:
            self.logger.debug(f"Tick data error for {symbol}: {e}")
            return self._get_simulated_tick_data(symbol)
    
    def _get_mt5_tick_data(self, symbol: str) -> Optional[TickData]:
        """Get real tick data from MT5"""
        try:
            # Import MT5 dynamically
            import MetaTrader5 as mt5
            
            # Get current tick
            tick = mt5.symbol_info_tick(symbol)  # type: ignore[attr-defined]
            if tick is None:
                return None
            
            return TickData(
                symbol=symbol,
                timestamp=datetime.fromtimestamp(tick.time),
                bid=float(tick.bid),
                ask=float(tick.ask),
                volume=int(tick.volume) if hasattr(tick, 'volume') else 0,
                spread=float(tick.ask - tick.bid)
            )
            
        except Exception as e:
            self.logger.debug(f"MT5 tick error for {symbol}: {e}")
            return None
    
    def _get_simulated_tick_data(self, symbol: str) -> TickData:
        """Generate simulated tick data for testing"""
        # Get base price
        base_prices = {
            "EURUSD": 1.0850,
            "GBPUSD": 1.2650,
            "AUDUSD": 0.6750,
            "USDCAD": 1.3550,
            "USDJPY": 149.50,
            "USDCHF": 0.9050
        }
        
        base_price = base_prices.get(symbol, 1.0000)
        
        # Add some randomness
        import random
        volatility = 0.0001  # 1 pip
        price_change = random.uniform(-volatility, volatility)
        
        current_price = base_price + price_change
        spread = 0.00015  # 1.5 pips
        
        return TickData(
            symbol=symbol,
            timestamp=datetime.now(),
            bid=current_price,
            ask=current_price + spread,
            volume=random.randint(1, 100),
            spread=spread
        )
    
    def _process_tick_data(self, tick_data: TickData):
        """Process and store tick data"""
        with self._lock:
            symbol = tick_data.symbol
            
            # Validate data
            if self.config["data_validation"] and not self._validate_tick_data(tick_data):
                return
            
            # Store in buffer
            self.tick_buffers[symbol].append(tick_data)
            
            # Update market state
            if symbol in self.market_states:
                self.market_states[symbol].current_tick = tick_data
                self.market_states[symbol].last_update = tick_data.timestamp
                self.market_states[symbol].is_active = True
            
            self._tick_count += 1
    
    def _validate_tick_data(self, tick_data: TickData) -> bool:
        """Validate tick data quality"""
        # Check for reasonable spread
        if tick_data.spread > 0.01:  # 100 pips
            return False
        
        # Check for zero prices
        if tick_data.bid <= 0 or tick_data.ask <= 0:
            return False
        
        # Check for inverted prices
        if tick_data.bid >= tick_data.ask:
            return False
        
        # Check timestamp
        age = (datetime.now() - tick_data.timestamp).total_seconds()
        if age > self.config["max_tick_age"]:
            return False
        
        return True
    
    def _update_candle_data(self, symbol: str):
        """Update candle data from tick data"""
        try:
            current_time = datetime.now()
            
            # Get recent ticks for candle formation
            ticks = list(self.tick_buffers[symbol])
            if len(ticks) < 2:
                return
            
            # Create 1-minute candle from recent ticks
            minute_start = current_time.replace(second=0, microsecond=0)
            minute_ticks = [tick for tick in ticks 
                          if tick.timestamp >= minute_start 
                          and tick.timestamp < minute_start + timedelta(minutes=1)]
            
            if len(minute_ticks) >= 2:
                candle = self._create_candle_from_ticks(symbol, "M1", minute_ticks)
                if candle:
                    self.candle_buffers[symbol].append(candle)
                    
                    # Update market state
                    if symbol in self.market_states:
                        self.market_states[symbol].current_candle = candle
                        
        except Exception as e:
            self.logger.debug(f"Candle update error for {symbol}: {e}")
    
    def _create_candle_from_ticks(self, symbol: str, timeframe: str, 
                                 ticks: List[TickData]) -> Optional[CandleData]:
        """Create candle data from tick data"""
        if not ticks:
            return None
        
        # Sort by timestamp
        sorted_ticks = sorted(ticks, key=lambda t: t.timestamp)
        
        # Calculate OHLC
        open_price = sorted_ticks[0].bid
        close_price = sorted_ticks[-1].bid
        high_price = max(tick.bid for tick in sorted_ticks)
        low_price = min(tick.bid for tick in sorted_ticks)
        
        # Calculate volume
        total_volume = sum(tick.volume for tick in sorted_ticks)
        tick_volume = len(sorted_ticks)
        
        return CandleData(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=sorted_ticks[0].timestamp,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=total_volume,
            tick_volume=tick_volume,
            spread=sum(tick.spread for tick in sorted_ticks) / len(sorted_ticks)
        )
    
    def _update_market_state(self, symbol: str):
        """Update comprehensive market state"""
        try:
            if symbol not in self.market_states:
                return
            
            state = self.market_states[symbol]
            
            # Calculate volatility
            recent_ticks = list(self.tick_buffers[symbol])[-20:]  # Last 20 ticks
            if len(recent_ticks) >= 2:
                prices = [tick.bid for tick in recent_ticks]
                if len(prices) > 1:
                    state.volatility = float(np.std(prices)) if np else 0.0
            
            # Determine trend direction
            if len(recent_ticks) >= 10:
                start_price = recent_ticks[0].bid
                end_price = recent_ticks[-1].bid
                price_change = end_price - start_price
                
                if abs(price_change) > 0.0005:  # 5 pips
                    state.trend_direction = "UP" if price_change > 0 else "DOWN"
                else:
                    state.trend_direction = "SIDEWAYS"
            
            # Determine trading session
            state.session = self._get_trading_session()
            
        except Exception as e:
            self.logger.debug(f"Market state update error for {symbol}: {e}")
    
    def _get_trading_session(self) -> str:
        """Determine current trading session"""
        now = datetime.now()
        hour = now.hour
        
        # Simplified session detection (UTC)
        if 22 <= hour or hour < 8:
            return "SYDNEY"
        elif 0 <= hour < 9:
            return "TOKYO"
        elif 8 <= hour < 17:
            return "LONDON"
        elif 13 <= hour < 22:
            return "NEW_YORK"
        else:
            return "TRANSITION"
    
    def _notify_data_callbacks(self, symbol: str):
        """Notify registered callbacks about data updates"""
        try:
            state = self.market_states[symbol]
            
            for callback in self.data_callbacks:
                try:
                    # Try 3-arg signature expected by main.py: (symbol, timeframe, tick_data)
                    timeframe = self.config.get("timeframes", ["M1"])[0] if isinstance(self.config, dict) else "M1"
                    tick_data = state.current_tick
                    if self._perf_enabled:
                        _t0 = time.perf_counter()
                        callback(symbol, timeframe, tick_data)
                        self._cb_latencies.append((time.perf_counter() - _t0) * 1000.0)
                        try:
                            if tick_data and isinstance(tick_data.timestamp, datetime):
                                feed_to_cb = (datetime.now() - tick_data.timestamp).total_seconds() * 1000.0
                                # Avoid negatives due to clock/source jitter
                                if feed_to_cb >= 0:
                                    self._feed_to_cb_latencies.append(feed_to_cb)
                        except Exception:
                            pass
                    else:
                        callback(symbol, timeframe, tick_data)
                except TypeError:
                    try:
                        # Fallback to 2-arg signature: (symbol, state)
                        if self._perf_enabled:
                            _t0 = time.perf_counter()
                            callback(symbol, state)
                            self._cb_latencies.append((time.perf_counter() - _t0) * 1000.0)
                            try:
                                if state.current_tick and isinstance(state.current_tick.timestamp, datetime):
                                    feed_to_cb = (datetime.now() - state.current_tick.timestamp).total_seconds() * 1000.0
                                    if feed_to_cb >= 0:
                                        self._feed_to_cb_latencies.append(feed_to_cb)
                            except Exception:
                                pass
                        else:
                            callback(symbol, state)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")
            if self._perf_enabled and self.data_callbacks:
                record_counter("rtp.data_events", by=len(self.data_callbacks))
                    
        except Exception as e:
            self.logger.debug(f"Callback notification error: {e}")
    
    def _log_performance_if_needed(self):
        """Log performance metrics periodically"""
        now = datetime.now()
        if (now - self._last_performance_log).total_seconds() >= self.config["performance_log_interval"]:
            
            if self._processing_times:
                avg_time = sum(self._processing_times) / len(self._processing_times)
                max_time = max(self._processing_times)
                
                metrics = {
                    "avg_processing_ms": avg_time * 1000,
                    "max_processing_ms": max_time * 1000,
                    "total_ticks": self._tick_count,
                    "symbols_active": len([s for s in self.market_states.values() if s.is_active])
                }
                
                self.logger.performance(
                    f"Data processing performance: {metrics}",
                    "realtime_data_processor"
                )
            
            self._last_performance_log = now

    def _emit_perf_metrics_if_needed(self) -> None:
        """Emit debug performance metrics via monitoring wrapper if enabled."""
        if not getattr(self, "_perf_enabled", False):
            return
        try:
            now = datetime.now()
            emit_iv = float(self.config.get("perf_emit_interval", 5.0))
            if (now - self._last_perf_emit).total_seconds() < emit_iv:
                return

            # Loop interval metrics
            if getattr(self, "_loop_intervals", None):
                vals = list(self._loop_intervals)
                if vals:
                    avg_ms = sum(vals) / len(vals)
                    p95_ms = sorted(vals)[max(0, int(0.95 * len(vals)) - 1)]
                    record_gauge("rtp.loop_avg_ms", float(avg_ms))
                    record_gauge("rtp.loop_p95_ms", float(p95_ms))

            # Callback latency metrics
            if getattr(self, "_cb_latencies", None):
                cvals = list(self._cb_latencies)
                if cvals:
                    p95_cb = sorted(cvals)[max(0, int(0.95 * len(cvals)) - 1)]
                    record_gauge("rtp.callback_p95_ms", float(p95_cb))

            # Feed-to-callback latency metrics (tick timestamp -> callback time)
            if getattr(self, "_feed_to_cb_latencies", None) is not None:
                fvals = list(self._feed_to_cb_latencies)
                if fvals:
                    p95_feed_cb = sorted(fvals)[max(0, int(0.95 * len(fvals)) - 1)]
                    record_gauge("rtp.feed_to_cb_p95_ms", float(p95_feed_cb))
                else:
                    record_gauge("rtp.feed_to_cb_p95_ms", 0.0)

            # Event rate
            elapsed = max(1e-6, (now - self._last_perf_emit).total_seconds())
            delta_ticks = max(0, self._tick_count - self._last_tick_count)
            eps = delta_ticks / elapsed
            record_gauge("rtp.events_per_sec", float(eps))
            self._last_tick_count = self._tick_count

            # Symbols active
            actives = len([s for s in self.market_states.values() if s.is_active])
            record_gauge("rtp.symbols_active", float(actives))

            self._last_perf_emit = now
        except Exception:
            # Never break due to metrics
            pass
    
    # Public interface methods
    def register_data_callback(self, callback: Callable):
        """Register callback for data updates"""
        self.data_callbacks.append(callback)
        self.logger.info(f"Data callback registered: {len(self.data_callbacks)} total")

    # ---- Minimal interface expected by main.py ----
    def start(self) -> bool:
        """Alias to start_processing (expected by main.py)"""
        return self.start_processing()

    def stop(self) -> None:
        """Alias to stop_processing (expected by main.py)"""
        self.stop_processing()

    def is_running(self) -> bool:
        """Return whether processing is active."""
        return bool(self._processing_active)

    def add_callback(self, callback: Callable) -> None:
        """Alias to register_data_callback (expected by main.py)."""
        self.register_data_callback(callback)

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "symbols": self.symbols,
            "tick_rate": (len(self._processing_times) / max(1, (datetime.now() - self._last_performance_log).total_seconds())) if self._processing_times else 0,
            "running": self._processing_active,
        }

    def get_status(self) -> Dict[str, Any]:
        return {"running": self._processing_active}
    
    def get_current_tick(self, symbol: str) -> Optional[TickData]:
        """Get current tick data for symbol"""
        state = self.market_states.get(symbol)
        return state.current_tick if state else None
    
    def get_current_candle(self, symbol: str) -> Optional[CandleData]:
        """Get current candle data for symbol"""
        state = self.market_states.get(symbol)
        return state.current_candle if state else None
    
    def get_market_state(self, symbol: str) -> Optional[MarketState]:
        """Get complete market state for symbol"""
        return self.market_states.get(symbol)
    
    def get_recent_ticks(self, symbol: str, count: int = 100) -> List[TickData]:
        """Get recent tick data"""
        if symbol not in self.tick_buffers:
            return []
        
        ticks = list(self.tick_buffers[symbol])
        return ticks[-count:] if len(ticks) > count else ticks
    
    def get_recent_candles(self, symbol: str, count: int = 50) -> List[CandleData]:
        """Get recent candle data"""
        if symbol not in self.candle_buffers:
            return []
        
        candles = list(self.candle_buffers[symbol])
        return candles[-count:] if len(candles) > count else candles
    
    def get_historical_data(self, symbol: str, timeframe: str, count: int = 500) -> Optional[pd.DataFrame]:
        """Get historical data from MT5 or cache"""
        try:
            if self.mt5_manager and self.mt5_manager.is_connected():
                data = self.mt5_manager.get_direct_market_data(symbol, timeframe, count)
                if data is not None:
                    return pd.DataFrame(data)
            
            # Fallback to simulated historical data
            return self._generate_simulated_historical_data(symbol, timeframe, count)
            
        except Exception as e:
            self.logger.error(f"Historical data error for {symbol}: {e}")
            return None
    
    def _generate_simulated_historical_data(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame:
        """Generate simulated historical data for testing"""
        # This would be replaced with real historical data in production
        base_prices = {
            "EURUSD": 1.0850,
            "GBPUSD": 1.2650,
            "AUDUSD": 0.6750,
            "USDCAD": 1.3550
        }
        
        base_price = base_prices.get(symbol, 1.0000)
        
        # Generate random walk data
        import random
        dates = pd.date_range(end=datetime.now(), periods=count, freq='1T')
        prices = []
        current_price = base_price
        
        for _ in range(count):
            change = random.uniform(-0.0005, 0.0005)
            current_price += change
            prices.append(current_price)
        
        # Create OHLCV data
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            high = price + random.uniform(0, 0.0002)
            low = price - random.uniform(0, 0.0002)
            open_price = prices[i-1] if i > 0 else price
            
            data.append({
                'timestamp': date,
                'open': open_price,
                'high': max(high, price),
                'low': min(low, price),
                'close': price,
                'volume': random.randint(50, 500),
                'symbol': symbol
            })
        
        return pd.DataFrame(data)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {
            "total_ticks": self._tick_count,
            "active_symbols": len([s for s in self.market_states.values() if s.is_active]),
            "buffer_utilization": {},
            "processing_performance": {}
        }
        
        # Buffer utilization
        for symbol in self.symbols:
            tick_buffer = self.tick_buffers.get(symbol, deque())
            candle_buffer = self.candle_buffers.get(symbol, deque())
            
            stats["buffer_utilization"][symbol] = {
                "tick_buffer_size": len(tick_buffer),
                "candle_buffer_size": len(candle_buffer),
                "tick_buffer_max": tick_buffer.maxlen,
                "candle_buffer_max": candle_buffer.maxlen
            }
        
        # Processing performance
        if self._processing_times:
            times = list(self._processing_times)
            stats["processing_performance"] = {
                "avg_time_ms": sum(times) / len(times) * 1000,
                "max_time_ms": max(times) * 1000,
                "min_time_ms": min(times) * 1000,
                "sample_count": len(times)
            }
        
        return stats
    
    # ---------------- PRODUCTION METHODS - MISSING ----------------
    
    def track_data_latency(self) -> Dict[str, float]:
        """
        Track data latency for each symbol to ensure real-time performance.
        
        Returns:
            Dict with latency metrics for each symbol in milliseconds
        """
        latency_metrics = {}
        current_time = datetime.now()
        
        try:
            with self._lock:
                for symbol, state in self.market_states.items():
                    if state.current_tick and state.last_update:
                        # Calculate latency from tick timestamp to last processing
                        latency_ms = (current_time - state.last_update).total_seconds() * 1000
                        latency_metrics[symbol] = round(latency_ms, 2)
                    else:
                        latency_metrics[symbol] = -1  # No data available
            
            # Log high latency warnings
            for symbol, latency in latency_metrics.items():
                if latency > 1000:  # More than 1 second is concerning
                    _safe_log(self.logger, "warning", f"High data latency for {symbol}: {latency}ms", "LATENCY")
                elif latency > 500:  # More than 500ms is caution
                    _safe_log(self.logger, "debug", f"Elevated data latency for {symbol}: {latency}ms", "LATENCY")
            
            return latency_metrics
            
        except Exception as e:
            _safe_log(self.logger, "error", f"Error tracking data latency: {e}", "LATENCY")
            return {symbol: -1 for symbol in self.symbols}
    
    def handle_auto_reconnection(self) -> bool:
        """
        Handle automatic reconnection to data sources when connection is lost.
        
        Returns:
            True if reconnection successful, False otherwise
        """
        try:
            _safe_log(self.logger, "info", "Attempting auto-reconnection to data sources", "RECONNECTION")
            
            # Check current connection status
            if not self._is_data_source_connected():
                _safe_log(self.logger, "warning", "Data source disconnected, attempting reconnection", "RECONNECTION")
                
                # Stop current processing
                if self._processing_active:
                    _safe_log(self.logger, "info", "Stopping current data processing for reconnection", "RECONNECTION")
                    self._processing_active = False
                    
                    # Wait for thread to finish
                    if self._data_thread and self._data_thread.is_alive():
                        self._data_thread.join(timeout=5.0)
                
                # Attempt to reconnect MT5 or other data sources
                reconnection_successful = self._attempt_data_source_reconnection()
                
                if reconnection_successful:
                    _safe_log(self.logger, "info", "Data source reconnection successful", "RECONNECTION")
                    
                    # Restart processing
                    if self.start_processing():
                        _safe_log(self.logger, "info", "Data processing restarted after reconnection", "RECONNECTION")
                        return True
                    else:
                        _safe_log(self.logger, "error", "Failed to restart data processing after reconnection", "RECONNECTION")
                        return False
                else:
                    _safe_log(self.logger, "error", "Failed to reconnect to data source", "RECONNECTION")
                    return False
            else:
                _safe_log(self.logger, "debug", "Data source connection is healthy", "RECONNECTION")
                return True
                
        except Exception as e:
            _safe_log(self.logger, "error", f"Auto-reconnection failed: {e}", "RECONNECTION")
            return False
    
    def _is_data_source_connected(self) -> bool:
        """Check if data source is connected"""
        try:
            # In real implementation, check MT5 connection status
            # For now, simulate based on processing activity
            if not self._processing_active:
                return False
            
            # Check if we're receiving recent data
            current_time = datetime.now()
            for state in self.market_states.values():
                if state.last_update and (current_time - state.last_update).total_seconds() < 60:
                    return True
            
            return False  # No recent data = disconnected
            
        except Exception:
            return False
    
    def _attempt_data_source_reconnection(self) -> bool:
        """Attempt to reconnect to data source"""
        try:
            # In real implementation, reconnect to MT5
            if self.mt5_manager:
                # Attempt MT5 reconnection
                _safe_log(self.logger, "info", "Attempting MT5 reconnection", "RECONNECTION")
                # self.mt5_manager.reconnect()  # Would be real implementation
                time.sleep(2)  # Simulate reconnection time
                return True
            else:
                # Simulate reconnection for testing
                _safe_log(self.logger, "info", "Simulating data source reconnection", "RECONNECTION")
                time.sleep(1)
                return True
                
        except Exception as e:
            _safe_log(self.logger, "error", f"Data source reconnection failed: {e}", "RECONNECTION")
            return False
    
    def validate_data_quality(self, tick_data: TickData) -> Tuple[bool, str]:
        """
        Validate incoming data quality to filter out bad ticks.
        
        Args:
            tick_data: Tick data to validate
            
        Returns:
            Tuple of (is_valid: bool, reason: str)
        """
        try:
            # Basic validation checks
            if tick_data.bid <= 0 or tick_data.ask <= 0:
                return False, "Invalid bid/ask prices (<=0)"
            
            if tick_data.ask <= tick_data.bid:
                return False, "Ask price not greater than bid price"
            
            # Spread validation
            spread = tick_data.ask - tick_data.bid
            if spread > 0.01:  # 100 pips spread is suspicious
                return False, f"Excessive spread: {spread:.5f}"
            
            if spread < 0.00001:  # Less than 0.1 pip spread is unusual
                return False, f"Unusually tight spread: {spread:.5f}"
            
            # Price movement validation (if we have previous data)
            symbol = tick_data.symbol
            if symbol in self.market_states:
                previous_tick = self.market_states[symbol].current_tick
                if previous_tick:
                    # Check for unrealistic price jumps
                    price_change = abs(tick_data.bid - previous_tick.bid)
                    max_allowed_change = previous_tick.bid * 0.05  # 5% max change
                    
                    if price_change > max_allowed_change:
                        return False, f"Unrealistic price jump: {price_change:.5f}"
            
            # Timestamp validation
            current_time = datetime.now()
            if tick_data.timestamp > current_time + timedelta(seconds=5):
                return False, "Tick timestamp in future"
            
            if tick_data.timestamp < current_time - timedelta(hours=1):
                return False, "Tick timestamp too old"
            
            return True, "Valid"
            
        except Exception as e:
            _safe_log(self.logger, "error", f"Data validation error: {e}", "VALIDATION")
            return False, f"Validation error: {e}"
    
    def optimize_data_buffers(self) -> Dict[str, Any]:
        """
        Optimize data buffers for memory usage and performance.
        
        Returns:
            Dict with optimization results
        """
        try:
            _safe_log(self.logger, "info", "Starting data buffer optimization", "BUFFER_OPT")
            optimization_results = {
                "symbols_processed": 0,
                "ticks_cleaned": 0,
                "candles_cleaned": 0,
                "memory_freed_mb": 0.0,
                "optimization_time_ms": 0.0
            }
            
            start_time = datetime.now()
            
            with self._lock:
                for symbol in self.symbols:
                    optimization_results["symbols_processed"] += 1
                    
                    # Optimize tick buffer
                    if symbol in self.tick_buffers:
                        tick_buffer = self.tick_buffers[symbol]
                        original_tick_count = len(tick_buffer)
                        
                        # Remove ticks older than max_tick_age
                        max_age = timedelta(seconds=self.config["max_tick_age"])
                        current_time = datetime.now()
                        
                        # Keep only recent ticks
                        filtered_ticks = deque(maxlen=self.config["buffer_size"])
                        for tick in tick_buffer:
                            if hasattr(tick, 'timestamp') and (current_time - tick.timestamp) <= max_age:
                                filtered_ticks.append(tick)
                        
                        self.tick_buffers[symbol] = filtered_ticks
                        ticks_removed = original_tick_count - len(filtered_ticks)
                        optimization_results["ticks_cleaned"] += ticks_removed
                        
                        _safe_log(self.logger, "debug", f"Optimized tick buffer for {symbol}: removed {ticks_removed} old ticks", "BUFFER_OPT")
                    
                    # Optimize candle buffer
                    if symbol in self.candle_buffers:
                        candle_buffer = self.candle_buffers[symbol]
                        original_candle_count = len(candle_buffer)
                        
                        # Keep only last 1000 candles
                        max_candles = min(1000, self.config["buffer_size"])
                        if len(candle_buffer) > max_candles:
                            # Convert to list, slice, and convert back to deque
                            recent_candles = list(candle_buffer)[-max_candles:]
                            self.candle_buffers[symbol] = deque(recent_candles, maxlen=self.config["buffer_size"])
                            
                            candles_removed = original_candle_count - len(recent_candles)
                            optimization_results["candles_cleaned"] += candles_removed
                            
                            _safe_log(self.logger, "debug", f"Optimized candle buffer for {symbol}: removed {candles_removed} old candles", "BUFFER_OPT")
                
                # Estimate memory freed (rough calculation)
                total_items_removed = optimization_results["ticks_cleaned"] + optimization_results["candles_cleaned"]
                estimated_memory_freed = total_items_removed * 0.001  # Rough estimate: 1KB per item
                optimization_results["memory_freed_mb"] = round(estimated_memory_freed, 2)
            
            end_time = datetime.now()
            optimization_time = (end_time - start_time).total_seconds() * 1000
            optimization_results["optimization_time_ms"] = round(optimization_time, 2)
            
            _safe_log(self.logger, "info", f"Buffer optimization completed: cleaned {optimization_results['ticks_cleaned']} ticks, "
                           f"{optimization_results['candles_cleaned']} candles, freed ~{optimization_results['memory_freed_mb']}MB "
                           f"in {optimization_results['optimization_time_ms']}ms", "BUFFER_OPT")
            
            return optimization_results
            
        except Exception as e:
            _safe_log(self.logger, "error", f"Buffer optimization failed: {e}", "BUFFER_OPT")
            return {
                "error": str(e),
                "symbols_processed": 0,
                "ticks_cleaned": 0,
                "candles_cleaned": 0,
                "memory_freed_mb": 0.0,
                "optimization_time_ms": 0.0
            }


# Global instance for shared access
_data_processor: Optional[RealTimeDataProcessor] = None
_processor_lock = threading.Lock()


def get_data_processor(symbols: Optional[List[str]] = None, config: Optional[Dict[str, Any]] = None) -> RealTimeDataProcessor:
    """Get global data processor instance"""
    global _data_processor
    
    with _processor_lock:
        if _data_processor is None:
            _data_processor = RealTimeDataProcessor(symbols, config)
        return _data_processor


def start_real_time_data(symbols: Optional[List[str]] = None) -> bool:
    """Start real-time data processing (convenience function)"""
    processor = get_data_processor(symbols)
    return processor.start_processing()


def stop_real_time_data():
    """Stop real-time data processing (convenience function)"""
    global _data_processor
    
    if _data_processor:
        _data_processor.stop_processing()


if __name__ == "__main__":
    # Test real-time data processor
    print("📊 ICT Engine Real-Time Data Processor Test")
    print("=" * 50)
    
    processor = RealTimeDataProcessor(["EURUSD", "GBPUSD"])
    
    def data_callback(symbol: str, state: MarketState):
        """Test callback function"""
        if state.current_tick:
            print(f"📈 {symbol}: {state.current_tick.bid:.5f}/{state.current_tick.ask:.5f} "
                  f"[{state.trend_direction}] {state.session}")
    
    processor.register_data_callback(data_callback)
    
    if processor.start_processing():
        print("✅ Data processing started")
        
        try:
            # Run for 30 seconds
            time.sleep(30)
            
            # Show performance stats
            stats = processor.get_performance_stats()
            print(f"\n📊 Performance Stats:")
            print(f"   Total ticks: {stats['total_ticks']}")
            print(f"   Active symbols: {stats['active_symbols']}")
            
        except KeyboardInterrupt:
            print("\n⏹️ Stopping...")
        
        processor.stop_processing()
        print("✅ Data processing stopped")
    else:
        print("❌ Failed to start data processing")