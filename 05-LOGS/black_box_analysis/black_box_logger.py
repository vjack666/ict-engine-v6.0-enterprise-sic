"""
🔒 BLACK BOX LOGGER v6.1 Enterprise
Sistema de logging tipo caja negra para análisis profundo del sistema ICT

Funcionalidades:
- Logging completo de detección de patrones
- Análisis de performance en tiempo real
- Persistencia de datos para análisis retrospectivo
- Métricas de salud del sistema
- Tracking de confluencias multi-patrón

Dependencies:
- smart_trading_logger (SLUC v2.1)
- threading para performance
- json para serialización
"""

import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
import logging

# Thread-safe logging imports
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "01-CORE"))
    from smart_trading_logger import get_smart_logger
    SLUC_AVAILABLE = True
except ImportError:
    SLUC_AVAILABLE = False
    logging.basicConfig(level=logging.INFO)


@dataclass
class BlackBoxEvent:
    """📊 Evento del sistema para análisis de caja negra"""
    event_type: str  # FVG_DETECTION, ORDER_BLOCK, SMART_MONEY, CONFLUENCE, PERFORMANCE
    timestamp: datetime
    symbol: str
    timeframe: str
    component: str
    data: Dict[str, Any]
    performance_ms: float
    health_status: str = "OK"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.metadata:
            self.metadata = {}


class BlackBoxLogger:
    """
    🔒 ENTERPRISE BLACK BOX LOGGER
    Sistema centralizado de logging para análisis profundo
    """
    
    def __init__(self):
        """Inicializar Black Box Logger"""
        self.base_path = Path(__file__).parent
        self.lock = threading.Lock()
        
        # Smart Trading Logger integration
        if SLUC_AVAILABLE:
            self.logger = get_smart_logger("BlackBoxLogger")
        else:
            self.logger = logging.getLogger("BlackBoxLogger")
        
        # Storage paths
        self.daily_log = self.base_path / f"daily_events_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.performance_log = self.base_path / f"performance_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.confluence_log = self.base_path / f"confluence_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.health_log = self.base_path / f"health_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        # Performance tracking
        self.session_start = datetime.now()
        self.event_count = 0
        self.performance_metrics = {
            'fvg_detection_times': [],
            'order_block_times': [],
            'smart_money_times': [],
            'confluence_times': [],
            'total_events': 0
        }
        
        self.logger.info("🔒 Black Box Logger v6.1 Enterprise initialized")
    
    def log_fvg_detection(self, symbol: str, timeframe: str, fvg_data: Dict[str, Any], 
                         performance_ms: float, health_status: str = "OK") -> None:
        """
        📊 Log FVG Detection Event
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe analyzed 
            fvg_data: Complete FVG detection data
            performance_ms: Detection time in milliseconds
            health_status: System health status
        """
        event = BlackBoxEvent(
            event_type="FVG_DETECTION",
            timestamp=datetime.now(),
            symbol=symbol,
            timeframe=timeframe,
            component="FairValueGapDetector",
            data=fvg_data,
            performance_ms=performance_ms,
            health_status=health_status,
            metadata={
                'fvg_count': len(fvg_data.get('detected_fvgs', [])),
                'bullish_count': len([f for f in fvg_data.get('detected_fvgs', []) if f.get('direction') == 'BULLISH']),
                'bearish_count': len([f for f in fvg_data.get('detected_fvgs', []) if f.get('direction') == 'BEARISH']),
                'avg_confidence': sum(f.get('confidence', 0) for f in fvg_data.get('detected_fvgs', [])) / max(len(fvg_data.get('detected_fvgs', [])), 1),
                'session_uptime': str(datetime.now() - self.session_start)
            }
        )
        
        self._write_event(event)
        self.performance_metrics['fvg_detection_times'].append(performance_ms)
        
        # Log para análisis
        self.logger.info(
            f"📊 FVG Detection: {symbol} {timeframe} | "
            f"{len(fvg_data.get('detected_fvgs', []))} FVGs | "
            f"{performance_ms:.2f}ms | {health_status}"
        )
    
    def log_order_block_detection(self, symbol: str, timeframe: str, ob_data: Dict[str, Any],
                                 performance_ms: float, health_status: str = "OK") -> None:
        """📊 Log Order Block Detection Event"""
        event = BlackBoxEvent(
            event_type="ORDER_BLOCK_DETECTION", 
            timestamp=datetime.now(),
            symbol=symbol,
            timeframe=timeframe,
            component="OrderBlockDetector",
            data=ob_data,
            performance_ms=performance_ms,
            health_status=health_status,
            metadata={
                'ob_count': len(ob_data.get('detected_obs', [])),
                'session_uptime': str(datetime.now() - self.session_start)
            }
        )
        
        self._write_event(event)
        self.performance_metrics['order_block_times'].append(performance_ms)
    
    def log_smart_money_detection(self, symbol: str, timeframe: str, sm_data: Dict[str, Any],
                                 performance_ms: float, health_status: str = "OK") -> None:
        """📊 Log Smart Money Detection Event"""
        event = BlackBoxEvent(
            event_type="SMART_MONEY_DETECTION",
            timestamp=datetime.now(),
            symbol=symbol,
            timeframe=timeframe,
            component="SmartMoneyDetector",
            data=sm_data,
            performance_ms=performance_ms,
            health_status=health_status,
            metadata={
                'sweep_count': len(sm_data.get('liquidity_sweeps', [])),
                'bos_count': len(sm_data.get('bos_signals', [])),
                'session_uptime': str(datetime.now() - self.session_start)
            }
        )
        
        self._write_event(event)
        self.performance_metrics['smart_money_times'].append(performance_ms)
    
    def log_confluence_analysis(self, symbol: str, timeframe: str, confluence_data: Dict[str, Any],
                               performance_ms: float, patterns_involved: List[str]) -> None:
        """📊 Log Multi-Pattern Confluence Analysis"""
        event = BlackBoxEvent(
            event_type="CONFLUENCE_ANALYSIS",
            timestamp=datetime.now(),
            symbol=symbol,
            timeframe=timeframe,
            component="ConfluenceAnalyzer",
            data=confluence_data,
            performance_ms=performance_ms,
            metadata={
                'patterns_count': len(patterns_involved),
                'patterns': patterns_involved,
                'confluence_strength': confluence_data.get('confluence_strength', 0),
                'session_uptime': str(datetime.now() - self.session_start)
            }
        )
        
        self._write_event(event, log_file=self.confluence_log)
        self.performance_metrics['confluence_times'].append(performance_ms)
        
        self.logger.info(
            f"🤝 Confluence Analysis: {symbol} {timeframe} | "
            f"Patterns: {', '.join(patterns_involved)} | "
            f"Strength: {confluence_data.get('confluence_strength', 0):.2f} | "
            f"{performance_ms:.2f}ms"
        )
    
    def log_performance_metrics(self, component: str, metrics: Dict[str, Any]) -> None:
        """⚡ Log Performance Metrics"""
        event = BlackBoxEvent(
            event_type="PERFORMANCE_METRICS",
            timestamp=datetime.now(),
            symbol="SYSTEM",
            timeframe="ALL",
            component=component,
            data=metrics,
            performance_ms=0.0,
            metadata={
                'session_uptime': str(datetime.now() - self.session_start),
                'total_events': self.event_count
            }
        )
        
        self._write_event(event, log_file=self.performance_log)
    
    def log_health_status(self, component: str, health_data: Dict[str, Any]) -> None:
        """🏥 Log System Health Status"""
        event = BlackBoxEvent(
            event_type="HEALTH_STATUS",
            timestamp=datetime.now(),
            symbol="SYSTEM",
            timeframe="ALL",
            component=component,
            data=health_data,
            performance_ms=0.0,
            health_status=health_data.get('status', 'UNKNOWN'),
            metadata={
                'session_uptime': str(datetime.now() - self.session_start)
            }
        )
        
        self._write_event(event, log_file=self.health_log)
    
    def _write_event(self, event: BlackBoxEvent, log_file: Optional[Path] = None) -> None:
        """📝 Write event to appropriate log file"""
        if log_file is None:
            log_file = self.daily_log
        
        with self.lock:
            try:
                # Convert event to JSON
                event_json = json.dumps(asdict(event), default=str)
                
                # Write to file
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(event_json + '\n')
                
                self.event_count += 1
                
            except Exception as e:
                self.logger.error(f"❌ Error writing black box event: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """📊 Get comprehensive session summary"""
        uptime = datetime.now() - self.session_start
        
        # Calculate averages
        avg_fvg_time = sum(self.performance_metrics['fvg_detection_times']) / max(len(self.performance_metrics['fvg_detection_times']), 1)
        avg_ob_time = sum(self.performance_metrics['order_block_times']) / max(len(self.performance_metrics['order_block_times']), 1)
        avg_sm_time = sum(self.performance_metrics['smart_money_times']) / max(len(self.performance_metrics['smart_money_times']), 1)
        avg_confluence_time = sum(self.performance_metrics['confluence_times']) / max(len(self.performance_metrics['confluence_times']), 1)
        
        summary = {
            'session_start': self.session_start.isoformat(),
            'session_uptime': str(uptime),
            'total_events': self.event_count,
            'performance_averages': {
                'fvg_detection_ms': round(avg_fvg_time, 2),
                'order_block_ms': round(avg_ob_time, 2),
                'smart_money_ms': round(avg_sm_time, 2),
                'confluence_ms': round(avg_confluence_time, 2)
            },
            'event_counts': {
                'fvg_detections': len(self.performance_metrics['fvg_detection_times']),
                'order_block_detections': len(self.performance_metrics['order_block_times']),
                'smart_money_detections': len(self.performance_metrics['smart_money_times']),
                'confluence_analyses': len(self.performance_metrics['confluence_times'])
            },
            'log_files': {
                'daily_events': str(self.daily_log),
                'performance': str(self.performance_log),
                'confluence': str(self.confluence_log),
                'health': str(self.health_log)
            }
        }
        
        return summary


# Singleton instance
_black_box_logger = None

def get_black_box_logger() -> BlackBoxLogger:
    """🔒 Get singleton Black Box Logger instance"""
    global _black_box_logger
    if _black_box_logger is None:
        _black_box_logger = BlackBoxLogger()
    return _black_box_logger


def log_fvg_detection(symbol: str, timeframe: str, fvg_data: Dict[str, Any], 
                     performance_ms: float, health_status: str = "OK") -> None:
    """🚀 Shortcut function for FVG detection logging"""
    get_black_box_logger().log_fvg_detection(symbol, timeframe, fvg_data, performance_ms, health_status)


def log_confluence_analysis(symbol: str, timeframe: str, confluence_data: Dict[str, Any],
                           performance_ms: float, patterns_involved: List[str]) -> None:
    """🚀 Shortcut function for confluence analysis logging"""
    get_black_box_logger().log_confluence_analysis(symbol, timeframe, confluence_data, performance_ms, patterns_involved)


def log_performance_summary() -> Dict[str, Any]:
    """📊 Get and log performance summary"""
    summary = get_black_box_logger().get_session_summary()
    get_black_box_logger().log_performance_metrics("BlackBoxLogger", summary)
    return summary
