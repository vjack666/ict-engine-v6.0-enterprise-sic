"""
Real Trading Logger - ICT Engine v6.0 Enterprise
Comprehensive logging system for real trading operations

Extends SmartTradingLogger with specialized trading logs
Provides audit trail for all trading activities
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
import csv
import sys

# Agregar path del proyecto para imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import central logger
try:
    from smart_trading_logger import get_smart_logger, log_info, log_warning, log_error, log_debug, SmartTradingLogger  # type: ignore
    _central_logger = get_smart_logger("RealTradingLogger")
except ImportError:
    # Fallback para compatibilidad
    class SmartTradingLogger:
        def __init__(self, name="ICT_Engine", level="INFO"):
            self.logger = logging.getLogger(name)
        def info(self, msg): self.logger.info(msg)
        def warning(self, msg): self.logger.warning(msg)
        def error(self, msg): self.logger.error(msg)
        def debug(self, msg): self.logger.debug(msg)
    
    _central_logger = SmartTradingLogger()
    def log_info(message, component="CORE"): _central_logger.info(f"[{component}] {message}")
    def log_warning(message, component="CORE"): _central_logger.warning(f"[{component}] {message}")
    def log_error(message, component="CORE"): _central_logger.error(f"[{component}] {message}")
    def log_debug(message, component="CORE"): _central_logger.debug(f"[{component}] {message}")

class RealTradingLogger:
    """
    🚀 Real Trading Logger - Enterprise Grade
    
    LOGGING CATEGORIES:
    
    📊 TRADE EXECUTION LOGS:
    - Signal generation and validation
    - Order placement and execution
    - Position modifications and closures
    - Slippage and execution quality
    
    ⚡ SAFETY & VALIDATION LOGS:
    - Risk validation checks
    - Daily limit enforcement
    - Emergency stop activations
    - Account safety validations
    
    📈 PERFORMANCE LOGS:
    - Trade performance metrics
    - Execution statistics
    - System performance data
    - Dashboard interaction logs
    
    🔒 AUDIT TRAIL:
    - Complete trade lifecycle
    - User actions and confirmations
    - System state changes
    - Compliance and regulatory logs
    """
    
    def __init__(self, base_logger=None):
        """Initialize real trading logger"""
        if base_logger is None:
            try:
                self.base_logger = get_smart_logger("RealTradingLogger") 
            except:
                self.base_logger = _central_logger
        else:
            self.base_logger = base_logger
        
        # Setup specialized log directories
        self.log_dir = Path("04-DATA/logs/trading")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different log types
        (self.log_dir / "executions").mkdir(exist_ok=True)
        (self.log_dir / "safety").mkdir(exist_ok=True)
        (self.log_dir / "performance").mkdir(exist_ok=True)
        (self.log_dir / "audit").mkdir(exist_ok=True)
        (self.log_dir / "dashboard").mkdir(exist_ok=True)
        
        # Setup specialized loggers
        self._setup_specialized_loggers()
        
        # Performance tracking
        self.session_start = datetime.now()
        self.trades_logged = 0
        self.errors_logged = 0
        
        self.base_logger.info("✅ Real Trading Logger initialized")
    
    def _setup_specialized_loggers(self) -> None:
        """Setup specialized loggers for different categories"""
        # Trade execution logger
        self.execution_logger = self._create_file_logger(
            'trade_execution',
            self.log_dir / "executions" / f"executions_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # Safety and validation logger
        self.safety_logger = self._create_file_logger(
            'trade_safety',
            self.log_dir / "safety" / f"safety_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # Performance logger
        self.performance_logger = self._create_file_logger(
            'trade_performance',
            self.log_dir / "performance" / f"performance_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # Audit trail logger
        self.audit_logger = self._create_file_logger(
            'trade_audit',
            self.log_dir / "audit" / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # Dashboard interaction logger
        self.dashboard_logger = self._create_file_logger(
            'dashboard_interactions',
            self.log_dir / "dashboard" / f"dashboard_{datetime.now().strftime('%Y%m%d')}.log"
        )
    
    def _create_file_logger(self, name: str, filepath: Path) -> logging.Logger:
        """Create a specialized file logger"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create file handler
        handler = logging.FileHandler(filepath, encoding='utf-8')
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.propagate = False
        
        return logger
    
    # TRADE EXECUTION LOGGING
    def log_signal_generated(self, signal_data: Dict[str, Any]) -> None:
        """Log trade signal generation"""
        log_entry = {
            'event': 'signal_generated',
            'timestamp': datetime.now().isoformat(),
            'signal_id': signal_data.get('signal_id'),
            'symbol': signal_data.get('symbol'),
            'direction': signal_data.get('direction'),
            'entry_price': signal_data.get('entry_price'),
            'stop_loss': signal_data.get('stop_loss'),
            'take_profit': signal_data.get('take_profit'),
            'confidence': signal_data.get('confidence'),
            'pattern_type': signal_data.get('pattern_type')
        }
        
        self.execution_logger.info(f"SIGNAL_GENERATED: {json.dumps(log_entry)}")
        self.base_logger.info(f"🎯 Signal generated: {signal_data.get('symbol')} {signal_data.get('direction')}")
    
    def log_trade_execution(self, signal_data: Dict[str, Any], 
                          execution_result: Dict[str, Any],
                          account_info: Dict[str, Any]) -> None:
        """Log complete trade execution"""
        log_entry = {
            'event': 'trade_execution',
            'timestamp': datetime.now().isoformat(),
            'signal_id': signal_data.get('signal_id'),
            'symbol': signal_data.get('symbol'),
            'direction': signal_data.get('direction'),
            'requested_size': signal_data.get('position_size'),
            'execution_price': execution_result.get('execution_price'),
            'slippage': execution_result.get('slippage'),
            'ticket': execution_result.get('ticket'),
            'success': execution_result.get('success'),
            'error_message': execution_result.get('error_message'),
            'account_balance_before': account_info.get('balance'),
            'account_equity_before': account_info.get('equity'),
            'account_margin_free_before': account_info.get('margin_free')
        }
        
        self.execution_logger.info(f"TRADE_EXECUTED: {json.dumps(log_entry)}")
        self.trades_logged += 1
        
        if execution_result.get('success'):
            self.base_logger.info(f"✅ Trade executed: {signal_data.get('symbol')} {signal_data.get('direction')} at {execution_result.get('execution_price')}")
        else:
            self.base_logger.error(f"❌ Trade failed: {signal_data.get('symbol')} {signal_data.get('direction')} - {execution_result.get('error_message')}")
            self.errors_logged += 1
    
    def log_position_modification(self, ticket: int, modification_type: str, 
                                old_values: Dict[str, Any], new_values: Dict[str, Any]) -> None:
        """Log position modification"""
        log_entry = {
            'event': 'position_modification',
            'timestamp': datetime.now().isoformat(),
            'ticket': ticket,
            'modification_type': modification_type,  # 'stop_loss', 'take_profit', 'both'
            'old_values': old_values,
            'new_values': new_values
        }
        
        self.execution_logger.info(f"POSITION_MODIFIED: {json.dumps(log_entry)}")
        self.base_logger.info(f"🔧 Position modified: #{ticket} - {modification_type}")
    
    def log_position_closure(self, ticket: int, closure_reason: str, 
                           final_pnl: float, closure_price: float) -> None:
        """Log position closure"""
        log_entry = {
            'event': 'position_closure',
            'timestamp': datetime.now().isoformat(),
            'ticket': ticket,
            'closure_reason': closure_reason,  # 'take_profit', 'stop_loss', 'manual', 'emergency'
            'final_pnl': final_pnl,
            'closure_price': closure_price
        }
        
        self.execution_logger.info(f"POSITION_CLOSED: {json.dumps(log_entry)}")
        self.base_logger.info(f"🏁 Position closed: #{ticket} - {closure_reason} - PnL: {final_pnl}")
    
    # SAFETY & VALIDATION LOGGING
    def log_validation_check(self, check_type: str, result: bool, 
                           details: Dict[str, Any]) -> None:
        """Log validation checks"""
        log_entry = {
            'event': 'validation_check',
            'timestamp': datetime.now().isoformat(),
            'check_type': check_type,
            'result': result,
            'details': details
        }
        
        self.safety_logger.info(f"VALIDATION_CHECK: {json.dumps(log_entry)}")
        
        if not result:
            self.base_logger.warning(f"⚠️ Validation failed: {check_type} - {details}")
    
    def log_limit_enforcement(self, limit_type: str, current_value: Any, 
                            limit_value: Any, action_taken: str) -> None:
        """Log limit enforcement actions"""
        log_entry = {
            'event': 'limit_enforcement',
            'timestamp': datetime.now().isoformat(),
            'limit_type': limit_type,
            'current_value': current_value,
            'limit_value': limit_value,
            'action_taken': action_taken
        }
        
        self.safety_logger.warning(f"LIMIT_ENFORCED: {json.dumps(log_entry)}")
        self.base_logger.warning(f"🚨 Limit enforced: {limit_type} - {action_taken}")
    
    def log_emergency_stop(self, trigger_reason: str, positions_affected: int, 
                         closure_results: List[Dict[str, Any]]) -> None:
        """Log emergency stop activation"""
        log_entry = {
            'event': 'emergency_stop',
            'timestamp': datetime.now().isoformat(),
            'trigger_reason': trigger_reason,
            'positions_affected': positions_affected,
            'closure_results': closure_results
        }
        
        self.safety_logger.critical(f"EMERGENCY_STOP: {json.dumps(log_entry)}")
        self.base_logger.error(f"🚨 EMERGENCY STOP: {trigger_reason} - {positions_affected} positions affected")
    
    def log_account_safety_check(self, check_results: Dict[str, Any]) -> None:
        """Log account safety validation"""
        log_entry = {
            'event': 'account_safety_check',
            'timestamp': datetime.now().isoformat(),
            'balance': check_results.get('balance'),
            'equity': check_results.get('equity'),
            'margin_level': check_results.get('margin_level'),
            'free_margin': check_results.get('free_margin'),
            'is_safe': check_results.get('is_safe'),
            'warnings': check_results.get('warnings', [])
        }
        
        self.safety_logger.info(f"ACCOUNT_SAFETY: {json.dumps(log_entry)}")
        
        if not check_results.get('is_safe'):
            self.base_logger.warning(f"⚠️ Account safety warning: {check_results.get('warnings')}")
    
    # PERFORMANCE LOGGING
    def log_execution_performance(self, symbol: str, execution_time_ms: float, 
                                slippage: float, execution_quality: str) -> None:
        """Log execution performance metrics"""
        log_entry = {
            'event': 'execution_performance',
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'execution_time_ms': execution_time_ms,
            'slippage': slippage,
            'execution_quality': execution_quality  # 'excellent', 'good', 'acceptable', 'poor'
        }
        
        self.performance_logger.info(f"EXECUTION_PERFORMANCE: {json.dumps(log_entry)}")
    
    def log_system_performance(self, cpu_usage: float, memory_usage: float, 
                             connection_latency: float) -> None:
        """Log system performance metrics"""
        log_entry = {
            'event': 'system_performance',
            'timestamp': datetime.now().isoformat(),
            'cpu_usage_percent': cpu_usage,
            'memory_usage_mb': memory_usage,
            'connection_latency_ms': connection_latency
        }
        
        self.performance_logger.info(f"SYSTEM_PERFORMANCE: {json.dumps(log_entry)}")
    
    def log_session_summary(self, trades_executed: int, success_rate: float, 
                          total_pnl: float, max_drawdown: float) -> None:
        """Log trading session summary"""
        session_duration = datetime.now() - self.session_start
        
        log_entry = {
            'event': 'session_summary',
            'timestamp': datetime.now().isoformat(),
            'session_start': self.session_start.isoformat(),
            'session_duration_minutes': session_duration.total_seconds() / 60,
            'trades_executed': trades_executed,
            'success_rate_percent': success_rate,
            'total_pnl': total_pnl,
            'max_drawdown': max_drawdown,
            'total_logs_created': self.trades_logged,
            'errors_logged': self.errors_logged
        }
        
        self.performance_logger.info(f"SESSION_SUMMARY: {json.dumps(log_entry)}")
        self.base_logger.info(f"📊 Session summary: {trades_executed} trades, {success_rate:.1f}% success, PnL: {total_pnl}")
    
    # DASHBOARD LOGGING
    def log_dashboard_action(self, action_type: str, user_data: Dict[str, Any], 
                           result: Dict[str, Any]) -> None:
        """Log dashboard user actions"""
        log_entry = {
            'event': 'dashboard_action',
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,  # 'enable_auto_trading', 'manual_execute', 'emergency_stop', etc.
            'user_data': user_data,
            'result': result
        }
        
        self.dashboard_logger.info(f"DASHBOARD_ACTION: {json.dumps(log_entry)}")
        self.base_logger.info(f"📊 Dashboard action: {action_type}")
    
    def log_dashboard_update(self, update_type: str, update_data: Dict[str, Any]) -> None:
        """Log dashboard real-time updates"""
        log_entry = {
            'event': 'dashboard_update',
            'timestamp': datetime.now().isoformat(),
            'update_type': update_type,
            'update_data': update_data
        }
        
        self.dashboard_logger.info(f"DASHBOARD_UPDATE: {json.dumps(log_entry)}")
    
    # AUDIT TRAIL
    def log_user_action(self, user_id: str, action: str, 
                       context: Dict[str, Any]) -> None:
        """Log user actions for audit trail"""
        log_entry = {
            'event': 'user_action',
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'context': context,
            'session_id': id(self)  # Simple session tracking
        }
        
        self.audit_logger.info(f"USER_ACTION: {json.dumps(log_entry)}")
    
    def log_system_state_change(self, state_type: str, old_state: Any, 
                              new_state: Any, trigger: str) -> None:
        """Log system state changes"""
        log_entry = {
            'event': 'system_state_change',
            'timestamp': datetime.now().isoformat(),
            'state_type': state_type,
            'old_state': old_state,
            'new_state': new_state,
            'trigger': trigger
        }
        
        self.audit_logger.info(f"STATE_CHANGE: {json.dumps(log_entry)}")
        self.base_logger.info(f"🔄 State change: {state_type} - {old_state} → {new_state}")
    
    def log_compliance_check(self, check_type: str, result: bool, 
                           details: Dict[str, Any]) -> None:
        """Log compliance and regulatory checks"""
        log_entry = {
            'event': 'compliance_check',
            'timestamp': datetime.now().isoformat(),
            'check_type': check_type,
            'result': result,
            'details': details
        }
        
        self.audit_logger.info(f"COMPLIANCE_CHECK: {json.dumps(log_entry)}")
        
        if not result:
            self.base_logger.error(f"🚨 Compliance violation: {check_type} - {details}")
    
    # UTILITY METHODS
    def export_daily_logs(self, date: Optional[datetime] = None) -> Dict[str, str]:
        """Export daily logs to CSV format"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y%m%d')
        export_dir = self.log_dir / "exports" / date_str
        export_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = {}
        
        # Export execution logs
        execution_file = export_dir / f"executions_{date_str}.csv"
        self._export_log_to_csv(
            self.log_dir / "executions" / f"executions_{date_str}.log",
            execution_file
        )
        exported_files['executions'] = str(execution_file)
        
        # Export safety logs
        safety_file = export_dir / f"safety_{date_str}.csv"
        self._export_log_to_csv(
            self.log_dir / "safety" / f"safety_{date_str}.log",
            safety_file
        )
        exported_files['safety'] = str(safety_file)
        
        self.base_logger.info(f"📄 Daily logs exported to: {export_dir}")
        return exported_files
    
    def _export_log_to_csv(self, log_file: Path, csv_file: Path) -> None:
        """Convert log file to CSV format"""
        if not log_file.exists():
            return
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvf:
                writer = csv.writer(csvf)
                writer.writerow(['timestamp', 'level', 'event', 'data'])
                
                for line in lines:
                    parts = line.strip().split(' | ', 2)
                    if len(parts) >= 3:
                        timestamp = parts[0]
                        level = parts[1]
                        message = parts[2]
                        
                        # Extract event and data if JSON format
                        event = 'unknown'
                        data = message
                        
                        if message.startswith('SIGNAL_GENERATED:'):
                            event = 'SIGNAL_GENERATED'
                            data = message.replace('SIGNAL_GENERATED: ', '')
                        elif message.startswith('TRADE_EXECUTED:'):
                            event = 'TRADE_EXECUTED'
                            data = message.replace('TRADE_EXECUTED: ', '')
                        # Add more event type parsing as needed
                        
                        writer.writerow([timestamp, level, event, data])
                        
        except Exception as e:
            self.base_logger.error(f"CSV export error: {str(e)}")
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        session_duration = datetime.now() - self.session_start
        
        return {
            'session_start': self.session_start.isoformat(),
            'session_duration_minutes': session_duration.total_seconds() / 60,
            'trades_logged': self.trades_logged,
            'errors_logged': self.errors_logged,
            'log_directories': {
                'executions': str(self.log_dir / "executions"),
                'safety': str(self.log_dir / "safety"),
                'performance': str(self.log_dir / "performance"),
                'audit': str(self.log_dir / "audit"),
                'dashboard': str(self.log_dir / "dashboard")
            }
        }
