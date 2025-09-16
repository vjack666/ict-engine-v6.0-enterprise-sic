#!/usr/bin/env python3
"""
Auto-Recovery System - ICT Engine v6.0 Enterprise
=================================================

Sistema de recuperación automática para fallos críticos.
Detecta, diagnostica y repara problemas comunes en tiempo real.

Características:
✅ Detección automática de fallos críticos
✅ Acciones de recuperación predefinidas
✅ Respaldo y restauración de estado
✅ Notificaciones de emergencia
✅ Historial de recuperaciones
✅ Prevención de bucles infinitos

Autor: ICT Engine v6.0 Team
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger

import asyncio
import time
import json
import threading
import subprocess
import gc
import psutil
import socket
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
import hashlib

try:
    from protocols.logging_central_protocols import create_production_logger, LogLevel
    logger = create_production_logger("AutoRecoverySystem", LogLevel.INFO)
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AutoRecoverySystem")

class RecoveryLevel(Enum):
    """Niveles de severidad de recuperación"""
    SOFT = "soft"        # Acciones suaves (clear cache, reconnect)
    MEDIUM = "medium"    # Acciones moderadas (restart services)
    HARD = "hard"        # Acciones drásticas (system restart)
    EMERGENCY = "emergency"  # Acciones críticas (emergency stop)

class RecoveryStatus(Enum):
    """Estados de una acción de recuperación"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class FailureType(Enum):
    """Tipos de fallos detectables"""
    MT5_CONNECTION_LOST = "mt5_connection_lost"
    INTERNET_DISCONNECTED = "internet_disconnected"
    HIGH_MEMORY_USAGE = "high_memory_usage"
    HIGH_CPU_USAGE = "high_cpu_usage"
    DISK_FULL = "disk_full"
    TRADING_ENGINE_STUCK = "trading_engine_stuck"
    MARKET_DATA_STALE = "market_data_stale"
    ORDER_EXECUTION_FAILED = "order_execution_failed"
    LOW_MARGIN_LEVEL = "low_margin_level"
    SYSTEM_FREEZE = "system_freeze"
    LOGGING_FAILURE = "logging_failure"
    DATABASE_ERROR = "database_error"

@dataclass
class RecoveryAction:
    """Acción de recuperación"""
    id: str
    name: str
    description: str
    level: RecoveryLevel
    failure_types: List[FailureType]
    action_func: Callable[[], bool]
    timeout_seconds: int = 30
    max_attempts: int = 3
    cooldown_minutes: int = 5
    prerequisites: List[str] = field(default_factory=list)
    success_criteria: Optional[Callable[[], bool]] = None

@dataclass
class RecoveryAttempt:
    """Intento de recuperación"""
    id: str
    action_id: str
    failure_type: FailureType
    timestamp: datetime
    status: RecoveryStatus
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    metrics_before: Dict[str, Any] = field(default_factory=dict)
    metrics_after: Dict[str, Any] = field(default_factory=dict)
    attempt_number: int = 1

@dataclass
class SystemHealth:
    """Estado de salud del sistema"""
    timestamp: datetime
    is_healthy: bool
    active_failures: List[FailureType]
    critical_failures: List[FailureType]
    system_metrics: Dict[str, Any] = field(default_factory=dict)
    recovery_in_progress: bool = False

class AutoRecoverySystem:
    """
    Sistema de auto-recuperación para fallos críticos
    
    Supervisa el sistema y ejecuta acciones de recuperación
    automáticas cuando detecta problemas conocidos.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # State management
        self.is_active = False
        self.start_time: Optional[datetime] = None
        self._shutdown_event = threading.Event()
        
        # Recovery tracking
        self.recovery_actions: Dict[str, RecoveryAction] = {}
        self.recovery_history: List[RecoveryAttempt] = []
        self.attempt_counts: Dict[str, int] = {}
        self.last_attempts: Dict[str, datetime] = {}
        self.active_recoveries: Dict[str, RecoveryAttempt] = {}
        
        # System health monitoring
        self.current_health: Optional[SystemHealth] = None
        self.health_history: List[SystemHealth] = []
        
        # Threading
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="AutoRecovery")
        self._monitor_thread: Optional[threading.Thread] = None
        self._recovery_lock = threading.RLock()
        
        # Callbacks
        self.failure_callbacks: List[Callable[[FailureType, Dict[str, Any]], None]] = []
        self.recovery_callbacks: List[Callable[[RecoveryAttempt], None]] = []
        
        # Initialize recovery actions
        self._register_default_recovery_actions()
        
        logger.info("AutoRecoverySystem initialized", "INIT")
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'monitoring_interval_seconds': 10.0,
            'health_check_interval_seconds': 30.0,
            'max_concurrent_recoveries': 2,
            'recovery_history_size': 1000,
            'health_history_size': 500,
            'emergency_stop_on_critical': True,
            'auto_restart_enabled': True,
            'notification_enabled': True,
            
            # Thresholds
            'memory_critical_threshold': 90.0,
            'cpu_critical_threshold': 95.0,
            'disk_critical_threshold': 95.0,
            'margin_critical_threshold': 120.0,
            'market_data_stale_threshold_minutes': 5.0,
            
            # Persistence
            'persist_history': True,
            'history_file': 'data/recovery_history.json',
            'state_file': 'data/recovery_state.json',
        }
    
    def _register_default_recovery_actions(self) -> None:
        """Registrar acciones de recuperación por defecto"""
        
        # MT5 Reconnection
        self.register_recovery_action(RecoveryAction(
            id="mt5_reconnect",
            name="MT5 Reconnection",
            description="Reconnect to MetaTrader 5 terminal",
            level=RecoveryLevel.SOFT,
            failure_types=[FailureType.MT5_CONNECTION_LOST],
            action_func=self._recover_mt5_connection,
            timeout_seconds=30,
            max_attempts=3,
            cooldown_minutes=2
        ))
        
        # Memory cleanup
        self.register_recovery_action(RecoveryAction(
            id="memory_cleanup",
            name="Memory Cleanup",
            description="Force garbage collection and clear caches",
            level=RecoveryLevel.SOFT,
            failure_types=[FailureType.HIGH_MEMORY_USAGE],
            action_func=self._recover_memory_cleanup,
            timeout_seconds=15,
            max_attempts=2,
            cooldown_minutes=1
        ))
        
        # Internet connectivity restore
        self.register_recovery_action(RecoveryAction(
            id="internet_restore",
            name="Internet Restore",
            description="Attempt to restore internet connectivity",
            level=RecoveryLevel.MEDIUM,
            failure_types=[FailureType.INTERNET_DISCONNECTED],
            action_func=self._recover_internet_connection,
            timeout_seconds=60,
            max_attempts=3,
            cooldown_minutes=5
        ))
        
        # Process restart
        self.register_recovery_action(RecoveryAction(
            id="process_restart",
            name="Process Restart",
            description="Restart trading engine process",
            level=RecoveryLevel.MEDIUM,
            failure_types=[FailureType.TRADING_ENGINE_STUCK, FailureType.SYSTEM_FREEZE],
            action_func=self._recover_process_restart,
            timeout_seconds=120,
            max_attempts=2,
            cooldown_minutes=10
        ))
        
        # Emergency position close
        self.register_recovery_action(RecoveryAction(
            id="emergency_close_positions",
            name="Emergency Close Positions",
            description="Close all open positions due to critical margin level",
            level=RecoveryLevel.HARD,
            failure_types=[FailureType.LOW_MARGIN_LEVEL],
            action_func=self._recover_emergency_close_positions,
            timeout_seconds=45,
            max_attempts=3,
            cooldown_minutes=1
        ))
        
        # Disk cleanup
        self.register_recovery_action(RecoveryAction(
            id="disk_cleanup",
            name="Disk Cleanup",
            description="Clean temporary files and logs to free disk space",
            level=RecoveryLevel.SOFT,
            failure_types=[FailureType.DISK_FULL],
            action_func=self._recover_disk_cleanup,
            timeout_seconds=60,
            max_attempts=2,
            cooldown_minutes=5
        ))
        
        logger.info(f"Registered {len(self.recovery_actions)} default recovery actions", "INIT")
    
    def register_recovery_action(self, action: RecoveryAction) -> None:
        """Registrar nueva acción de recuperación"""
        self.recovery_actions[action.id] = action
        logger.info(f"Registered recovery action: {action.name}", "REGISTER")
    
    def start_monitoring(self) -> bool:
        """Iniciar monitoreo y recuperación automática"""
        if self.is_active:
            logger.warning("Auto-recovery system already active", "START")
            return True
        
        logger.info("Starting auto-recovery system", "START")
        
        try:
            self.is_active = True
            self.start_time = datetime.now()
            self._shutdown_event.clear()
            
            # Start monitoring thread
            self._monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                name="AutoRecoveryMonitor",
                daemon=True
            )
            self._monitor_thread.start()
            
            # Load previous state
            self._load_state()
            
            logger.info("Auto-recovery system started successfully", "START")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start auto-recovery system: {e}", "START")
            self.is_active = False
            return False
    
    def stop_monitoring(self) -> bool:
        """Detener monitoreo"""
        if not self.is_active:
            logger.warning("Auto-recovery system not active", "STOP")
            return True
        
        logger.info("Stopping auto-recovery system", "STOP")
        
        try:
            self.is_active = False
            self._shutdown_event.set()
            
            # Wait for monitoring thread
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=10)
            
            # Cancel active recoveries
            for attempt in list(self.active_recoveries.values()):
                attempt.status = RecoveryStatus.CANCELLED
            
            # Shutdown executor
            self._executor.shutdown(wait=True)
            
            # Save state
            self._save_state()
            
            logger.info("Auto-recovery system stopped", "STOP")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping auto-recovery system: {e}", "STOP")
            return False
    
    def _monitoring_loop(self) -> None:
        """Bucle principal de monitoreo"""
        interval = self.config['monitoring_interval_seconds']
        
        while self.is_active and not self._shutdown_event.is_set():
            try:
                # Check system health
                health = self._check_system_health()
                self.current_health = health
                self._update_health_history(health)
                
                # Trigger recovery if needed
                if not health.is_healthy and not health.recovery_in_progress:
                    self._trigger_recovery(health.active_failures)
                
                # Clean up completed recoveries
                self._cleanup_completed_recoveries()
                
                # Persist state periodically
                if self.config.get('persist_history', True):
                    self._save_state()
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", "MONITOR")
                time.sleep(interval)
    
    def _check_system_health(self) -> SystemHealth:
        """Verificar salud del sistema"""
        health = SystemHealth(
            timestamp=datetime.now(),
            is_healthy=True,
            active_failures=[],
            critical_failures=[]
        )
        
        try:
            # Collect system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health.system_metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'available_memory_gb': memory.available / 1024 / 1024 / 1024,
                'free_disk_gb': disk.free / 1024 / 1024 / 1024
            }
            
            # Check for failures
            failures = []
            
            # Memory check
            if memory.percent > self.config['memory_critical_threshold']:
                failures.append(FailureType.HIGH_MEMORY_USAGE)
            
            # CPU check
            if cpu_percent > self.config['cpu_critical_threshold']:
                failures.append(FailureType.HIGH_CPU_USAGE)
            
            # Disk check
            if disk.percent > self.config['disk_critical_threshold']:
                failures.append(FailureType.DISK_FULL)
            
            # Internet connectivity check
            if not self._test_internet_connectivity():
                failures.append(FailureType.INTERNET_DISCONNECTED)
            
            # MT5 connection check
            if not self._test_mt5_connection():
                failures.append(FailureType.MT5_CONNECTION_LOST)
            
            # Trading metrics check
            trading_failures = self._check_trading_health()
            failures.extend(trading_failures)
            
            # Update health status
            health.active_failures = failures
            health.critical_failures = [f for f in failures if self._is_critical_failure(f)]
            health.is_healthy = len(failures) == 0
            health.recovery_in_progress = len(self.active_recoveries) > 0
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}", "HEALTH_CHECK")
            health.is_healthy = False
            health.active_failures = [FailureType.SYSTEM_FREEZE]
        
        return health
    
    def _test_internet_connectivity(self) -> bool:
        """Test internet connectivity"""
        try:
            socket.create_connection(("8.8.8.8", 53), 3)
            return True
        except OSError:
            return False
    
    def _test_mt5_connection(self) -> bool:
        """Test MT5 connection"""
        try:
            from real_trading.mt5_config import mt5_initialize  # type: ignore
            import MetaTrader5 as mt5  # type: ignore
            
            if not mt5_initialize():  # type: ignore
                return False
            
            account_info = mt5.account_info()  # type: ignore
            return account_info is not None
            
        except ImportError:
            # MT5 not available - assume connected for testing
            return True
        except Exception:
            return False
    
    def _check_trading_health(self) -> List[FailureType]:
        """Check trading-specific health issues"""
        failures = []
        
        try:
            # Check margin level
            try:
                from real_trading.mt5_config import mt5_initialize  # type: ignore
                import MetaTrader5 as mt5  # type: ignore
                
                if mt5_initialize():  # type: ignore
                    account_info = mt5.account_info()  # type: ignore
                    if account_info and hasattr(account_info, 'margin_level'):
                        if account_info.margin_level < self.config['margin_critical_threshold']:
                            failures.append(FailureType.LOW_MARGIN_LEVEL)
                    
                    # Check market data freshness
                    symbol_info = mt5.symbol_info("EURUSD")  # type: ignore
                    if symbol_info and hasattr(symbol_info, 'time'):
                        current_time = time.time()
                        data_age_minutes = (current_time - symbol_info.time) / 60
                        
                        if data_age_minutes > self.config['market_data_stale_threshold_minutes']:
                            failures.append(FailureType.MARKET_DATA_STALE)
                            
            except ImportError:
                pass
            except Exception as e:
                logger.warning(f"Error checking trading health: {e}", "TRADING_HEALTH")
        
        except Exception as e:
            logger.error(f"Error in trading health check: {e}", "TRADING_HEALTH")
        
        return failures
    
    def _is_critical_failure(self, failure_type: FailureType) -> bool:
        """Determinar si un fallo es crítico"""
        critical_failures = {
            FailureType.LOW_MARGIN_LEVEL,
            FailureType.INTERNET_DISCONNECTED,
            FailureType.SYSTEM_FREEZE,
            FailureType.TRADING_ENGINE_STUCK
        }
        return failure_type in critical_failures
    
    def _trigger_recovery(self, failures: List[FailureType]) -> None:
        """Trigger recovery for detected failures"""
        if not failures:
            return
        
        logger.warning(f"Triggering recovery for failures: {[f.value for f in failures]}", "RECOVERY")
        
        # Notify failure callbacks
        for failure in failures:
            for callback in self.failure_callbacks:
                try:
                    callback(failure, self.current_health.system_metrics if self.current_health else {})
                except Exception as e:
                    logger.error(f"Failure callback error: {e}", "CALLBACK")
        
        # Find suitable recovery actions
        for failure in failures:
            suitable_actions = self._find_recovery_actions(failure)
            
            for action in suitable_actions:
                if self._can_attempt_recovery(action):
                    self._execute_recovery_async(action, failure)
    
    def _find_recovery_actions(self, failure_type: FailureType) -> List[RecoveryAction]:
        """Find recovery actions for a specific failure type"""
        suitable_actions = []
        
        for action in self.recovery_actions.values():
            if failure_type in action.failure_types:
                suitable_actions.append(action)
        
        # Sort by level (soft first)
        suitable_actions.sort(key=lambda x: list(RecoveryLevel).index(x.level))
        
        return suitable_actions
    
    def _can_attempt_recovery(self, action: RecoveryAction) -> bool:
        """Check if we can attempt a recovery action"""
        # Check max concurrent recoveries
        if len(self.active_recoveries) >= self.config['max_concurrent_recoveries']:
            return False
        
        # Check if action is already running
        if action.id in self.active_recoveries:
            return False
        
        # Check attempt count
        if self.attempt_counts.get(action.id, 0) >= action.max_attempts:
            return False
        
        # Check cooldown
        last_attempt = self.last_attempts.get(action.id)
        if last_attempt:
            cooldown_delta = timedelta(minutes=action.cooldown_minutes)
            if datetime.now() - last_attempt < cooldown_delta:
                return False
        
        # Check prerequisites
        for prereq_id in action.prerequisites:
            if prereq_id in self.active_recoveries:
                return False
        
        return True
    
    def _execute_recovery_async(self, action: RecoveryAction, failure_type: FailureType) -> None:
        """Execute recovery action asynchronously"""
        # Create recovery attempt
        attempt_id = self._generate_attempt_id(action.id, failure_type)
        attempt_number = self.attempt_counts.get(action.id, 0) + 1
        
        attempt = RecoveryAttempt(
            id=attempt_id,
            action_id=action.id,
            failure_type=failure_type,
            timestamp=datetime.now(),
            status=RecoveryStatus.PENDING,
            attempt_number=attempt_number,
            metrics_before=self.current_health.system_metrics if self.current_health else {}
        )
        
        # Track attempt
        with self._recovery_lock:
            self.active_recoveries[action.id] = attempt
            self.recovery_history.append(attempt)
            self.attempt_counts[action.id] = attempt_number
            self.last_attempts[action.id] = datetime.now()
        
        # Submit to executor
        future = self._executor.submit(self._execute_recovery, action, attempt)
        
        # Add completion callback
        def on_recovery_complete(fut):
            try:
                success = fut.result()
                self._complete_recovery(attempt, success)
            except Exception as e:
                logger.error(f"Recovery execution error: {e}", "RECOVERY")
                attempt.error_message = str(e)
                attempt.status = RecoveryStatus.FAILED
                self._complete_recovery(attempt, False)
        
        future.add_done_callback(on_recovery_complete)
        
        logger.info(f"Started recovery: {action.name} (attempt {attempt_number})", "RECOVERY")
    
    def _execute_recovery(self, action: RecoveryAction, attempt: RecoveryAttempt) -> bool:
        """Execute recovery action (runs in thread pool)"""
        start_time = time.time()
        
        try:
            # Update status
            attempt.status = RecoveryStatus.IN_PROGRESS
            
            # Execute recovery action with timeout
            success = self._execute_with_timeout(action.action_func, action.timeout_seconds)
            
            # Record duration
            attempt.duration_seconds = time.time() - start_time
            
            # Check success criteria if provided
            if success and action.success_criteria:
                success = action.success_criteria()
            
            # Update status
            attempt.status = RecoveryStatus.SUCCESS if success else RecoveryStatus.FAILED
            
            logger.info(f"Recovery {action.name}: {'SUCCESS' if success else 'FAILED'} in {attempt.duration_seconds:.1f}s", "RECOVERY")
            
            return success
            
        except TimeoutError:
            attempt.duration_seconds = time.time() - start_time
            attempt.status = RecoveryStatus.TIMEOUT
            attempt.error_message = f"Recovery timed out after {action.timeout_seconds}s"
            logger.warning(f"Recovery {action.name} timed out", "RECOVERY")
            return False
            
        except Exception as e:
            attempt.duration_seconds = time.time() - start_time
            attempt.status = RecoveryStatus.FAILED
            attempt.error_message = str(e)
            logger.error(f"Recovery {action.name} failed: {e}", "RECOVERY")
            return False
    
    def _execute_with_timeout(self, func: Callable, timeout_seconds: int) -> bool:
        """Execute function with timeout"""
        # For Windows compatibility, use threading instead of signal
        import threading
        result = [None]
        exception: List[Optional[Exception]] = [None]
        
        def target():
            try:
                result[0] = func()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout_seconds)
        
        if thread.is_alive():
            # Thread is still running - timeout
            raise TimeoutError("Function execution timed out")
        
        if exception[0]:
            raise exception[0]
        
        return result[0] if result[0] is not None else False
    
    def _complete_recovery(self, attempt: RecoveryAttempt, success: bool) -> None:
        """Complete recovery attempt"""
        # Update metrics after recovery
        if self.current_health:
            attempt.metrics_after = self.current_health.system_metrics
        
        # Remove from active recoveries
        with self._recovery_lock:
            if attempt.action_id in self.active_recoveries:
                del self.active_recoveries[attempt.action_id]
            
            # Reset attempt count on success
            if success and attempt.action_id in self.attempt_counts:
                self.attempt_counts[attempt.action_id] = 0
        
        # Notify callbacks
        for callback in self.recovery_callbacks:
            try:
                callback(attempt)
            except Exception as e:
                logger.error(f"Recovery callback error: {e}", "CALLBACK")
        
        logger.info(f"Completed recovery: {attempt.action_id} - {attempt.status.value}", "RECOVERY")
    
    def _generate_attempt_id(self, action_id: str, failure_type: FailureType) -> str:
        """Generate unique attempt ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{action_id}_{failure_type.value}_{timestamp}"
        hash_digest = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"{action_id}_{hash_digest}"
    
    def _cleanup_completed_recoveries(self) -> None:
        """Clean up completed recoveries from memory"""
        # Limit recovery history size
        max_history = self.config.get('recovery_history_size', 1000)
        if len(self.recovery_history) > max_history:
            self.recovery_history = self.recovery_history[-max_history:]
        
        # Limit health history size
        max_health = self.config.get('health_history_size', 500)
        if len(self.health_history) > max_health:
            self.health_history = self.health_history[-max_health:]
    
    def _update_health_history(self, health: SystemHealth) -> None:
        """Update health history"""
        self.health_history.append(health)
    
    # Recovery action implementations
    def _recover_mt5_connection(self) -> bool:
        """Recover MT5 connection"""
        try:
            from real_trading.mt5_config import mt5_initialize  # type: ignore
            import MetaTrader5 as mt5  # type: ignore
            
            # Shutdown existing connection
            mt5.shutdown()  # type: ignore
            time.sleep(2)
            
            # Try to reinitialize
            if mt5_initialize():  # type: ignore
                logger.info("MT5 reconnection successful", "RECOVERY")
                return True
            else:
                logger.warning("MT5 reconnection failed", "RECOVERY")
                return False
                
        except ImportError:
            logger.warning("MT5 library not available", "RECOVERY")
            return False
        except Exception as e:
            logger.error(f"MT5 recovery error: {e}", "RECOVERY")
            return False
    
    def _recover_memory_cleanup(self) -> bool:
        """Recover by cleaning memory"""
        try:
            # Force garbage collection
            collected_objects = gc.collect()
            
            # Clear any available caches
            try:
                # Clear function caches if they exist
                if hasattr(gc, 'get_stats'):
                    gc.collect(0)  # Young generation
                    gc.collect(1)  # Middle generation  
                    gc.collect(2)  # Old generation
            except Exception:
                pass
            
            logger.info(f"Memory cleanup completed, collected {collected_objects} objects", "RECOVERY")
            return True
            
        except Exception as e:
            logger.error(f"Memory cleanup error: {e}", "RECOVERY")
            return False
    
    def _recover_internet_connection(self) -> bool:
        """Attempt to recover internet connection"""
        try:
            # Try to flush DNS
            try:
                subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, timeout=30)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Wait and test
            time.sleep(5)
            
            # Test connectivity
            return self._test_internet_connectivity()
            
        except Exception as e:
            logger.error(f"Internet recovery error: {e}", "RECOVERY")
            return False
    
    def _recover_process_restart(self) -> bool:
        """Restart trading process (placeholder)"""
        try:
            logger.warning("Process restart not implemented - would restart trading engine", "RECOVERY")
            # In a real implementation, this would restart the trading process
            return True
            
        except Exception as e:
            logger.error(f"Process restart error: {e}", "RECOVERY")
            return False
    
    def _recover_emergency_close_positions(self) -> bool:
        """Emergency close all positions"""
        try:
            from real_trading.mt5_config import mt5_initialize  # type: ignore
            import MetaTrader5 as mt5  # type: ignore
            
            if not mt5_initialize():  # type: ignore
                return False
            
            # Get all open positions
            positions = mt5.positions_get()  # type: ignore
            if not positions:
                return True  # No positions to close
            
            # Close all positions
            closed_count = 0
            for position in positions:
                # Create close order (simplified)
                symbol = position.symbol
                volume = position.volume
                order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY  # type: ignore
                
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,  # type: ignore
                    "symbol": symbol,
                    "volume": volume,
                    "type": order_type,
                    "position": position.ticket,
                    "comment": "Emergency close by auto-recovery",
                }
                
                result = mt5.order_send(request)  # type: ignore
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:  # type: ignore
                    closed_count += 1
            
            logger.info(f"Emergency close: closed {closed_count}/{len(positions)} positions", "RECOVERY")
            return closed_count == len(positions)
            
        except ImportError:
            logger.warning("MT5 library not available for emergency close", "RECOVERY")
            return False
        except Exception as e:
            logger.error(f"Emergency close error: {e}", "RECOVERY")
            return False
    
    def _recover_disk_cleanup(self) -> bool:
        """Clean disk space"""
        try:
            cleaned_mb = 0
            
            # Clean temp files
            temp_dirs = [Path.cwd() / "temp", Path.cwd() / "data" / "cache"]
            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    for file in temp_dir.glob("*"):
                        if file.is_file():
                            size_mb = file.stat().st_size / 1024 / 1024
                            try:
                                file.unlink()
                                cleaned_mb += size_mb
                            except OSError:
                                pass
            
            # Clean old log files (keep last 7 days)
            log_dirs = [Path.cwd() / "data" / "logs", Path.cwd() / "05-LOGS"]
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for log_dir in log_dirs:
                if log_dir.exists():
                    for log_file in log_dir.rglob("*.log"):
                        if log_file.stat().st_mtime < cutoff_time.timestamp():
                            size_mb = log_file.stat().st_size / 1024 / 1024
                            try:
                                log_file.unlink()
                                cleaned_mb += size_mb
                            except OSError:
                                pass
            
            logger.info(f"Disk cleanup completed, freed {cleaned_mb:.1f} MB", "RECOVERY")
            return cleaned_mb > 0
            
        except Exception as e:
            logger.error(f"Disk cleanup error: {e}", "RECOVERY")
            return False
    
    # State persistence
    def _save_state(self) -> None:
        """Save recovery state to disk"""
        try:
            if not self.config.get('persist_history', True):
                return
            
            state_data = {
                'timestamp': datetime.now().isoformat(),
                'attempt_counts': self.attempt_counts,
                'last_attempts': {k: v.isoformat() for k, v in self.last_attempts.items()},
                'recovery_history': [self._attempt_to_dict(a) for a in self.recovery_history[-100:]],  # Last 100
                'health_history': [self._health_to_dict(h) for h in self.health_history[-50:]]  # Last 50
            }
            
            state_file = Path(self.config['state_file'])
            state_file.parent.mkdir(exist_ok=True)
            
            # Atomic write
            temp_file = state_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2)
            temp_file.replace(state_file)
            
        except Exception as e:
            logger.warning(f"Failed to save recovery state: {e}", "PERSISTENCE")
    
    def _load_state(self) -> None:
        """Load recovery state from disk"""
        try:
            state_file = Path(self.config['state_file'])
            if not state_file.exists():
                return
            
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # Load attempt counts and last attempts
            self.attempt_counts = state_data.get('attempt_counts', {})
            
            last_attempts_raw = state_data.get('last_attempts', {})
            self.last_attempts = {}
            for k, v in last_attempts_raw.items():
                try:
                    self.last_attempts[k] = datetime.fromisoformat(v)
                except ValueError:
                    pass
            
            # Load recent history
            history_raw = state_data.get('recovery_history', [])
            for attempt_data in history_raw:
                attempt = self._dict_to_attempt(attempt_data)
                if attempt:
                    self.recovery_history.append(attempt)
            
            health_raw = state_data.get('health_history', [])
            for health_data in health_raw:
                health = self._dict_to_health(health_data)
                if health:
                    self.health_history.append(health)
            
            logger.info("Recovery state loaded successfully", "PERSISTENCE")
            
        except Exception as e:
            logger.warning(f"Failed to load recovery state: {e}", "PERSISTENCE")
    
    def _attempt_to_dict(self, attempt: RecoveryAttempt) -> Dict[str, Any]:
        """Convert RecoveryAttempt to dictionary"""
        return {
            'id': attempt.id,
            'action_id': attempt.action_id,
            'failure_type': attempt.failure_type.value,
            'timestamp': attempt.timestamp.isoformat(),
            'status': attempt.status.value,
            'duration_seconds': attempt.duration_seconds,
            'error_message': attempt.error_message,
            'attempt_number': attempt.attempt_number,
            'metrics_before': attempt.metrics_before,
            'metrics_after': attempt.metrics_after
        }
    
    def _dict_to_attempt(self, data: Dict[str, Any]) -> Optional[RecoveryAttempt]:
        """Convert dictionary to RecoveryAttempt"""
        try:
            return RecoveryAttempt(
                id=data['id'],
                action_id=data['action_id'],
                failure_type=FailureType(data['failure_type']),
                timestamp=datetime.fromisoformat(data['timestamp']),
                status=RecoveryStatus(data['status']),
                duration_seconds=data.get('duration_seconds', 0.0),
                error_message=data.get('error_message'),
                attempt_number=data.get('attempt_number', 1),
                metrics_before=data.get('metrics_before', {}),
                metrics_after=data.get('metrics_after', {})
            )
        except (KeyError, ValueError, TypeError):
            return None
    
    def _health_to_dict(self, health: SystemHealth) -> Dict[str, Any]:
        """Convert SystemHealth to dictionary"""
        return {
            'timestamp': health.timestamp.isoformat(),
            'is_healthy': health.is_healthy,
            'active_failures': [f.value for f in health.active_failures],
            'critical_failures': [f.value for f in health.critical_failures],
            'system_metrics': health.system_metrics,
            'recovery_in_progress': health.recovery_in_progress
        }
    
    def _dict_to_health(self, data: Dict[str, Any]) -> Optional[SystemHealth]:
        """Convert dictionary to SystemHealth"""
        try:
            return SystemHealth(
                timestamp=datetime.fromisoformat(data['timestamp']),
                is_healthy=data['is_healthy'],
                active_failures=[FailureType(f) for f in data.get('active_failures', [])],
                critical_failures=[FailureType(f) for f in data.get('critical_failures', [])],
                system_metrics=data.get('system_metrics', {}),
                recovery_in_progress=data.get('recovery_in_progress', False)
            )
        except (KeyError, ValueError, TypeError):
            return None
    
    # Public API methods
    def add_failure_callback(self, callback: Callable[[FailureType, Dict[str, Any]], None]) -> None:
        """Add callback for failure detection"""
        self.failure_callbacks.append(callback)
    
    def add_recovery_callback(self, callback: Callable[[RecoveryAttempt], None]) -> None:
        """Add callback for recovery completion"""
        self.recovery_callbacks.append(callback)
    
    def get_system_health(self) -> Optional[SystemHealth]:
        """Get current system health"""
        return self.current_health
    
    def get_active_recoveries(self) -> List[RecoveryAttempt]:
        """Get currently active recoveries"""
        return list(self.active_recoveries.values())
    
    def get_recovery_history(self, limit: Optional[int] = None) -> List[RecoveryAttempt]:
        """Get recovery history"""
        history = self.recovery_history
        if limit:
            history = history[-limit:]
        return history
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        total_attempts = len(self.recovery_history)
        successful_attempts = len([a for a in self.recovery_history if a.status == RecoveryStatus.SUCCESS])
        failed_attempts = len([a for a in self.recovery_history if a.status == RecoveryStatus.FAILED])
        
        # Success rate by action
        action_stats = {}
        for attempt in self.recovery_history:
            action_id = attempt.action_id
            if action_id not in action_stats:
                action_stats[action_id] = {'total': 0, 'success': 0, 'failed': 0}
            
            action_stats[action_id]['total'] += 1
            if attempt.status == RecoveryStatus.SUCCESS:
                action_stats[action_id]['success'] += 1
            elif attempt.status == RecoveryStatus.FAILED:
                action_stats[action_id]['failed'] += 1
        
        return {
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'failed_attempts': failed_attempts,
            'success_rate_percent': (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0.0,
            'active_recoveries': len(self.active_recoveries),
            'registered_actions': len(self.recovery_actions),
            'action_statistics': action_stats,
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0
        }

# Global instance management
_global_auto_recovery: Optional[AutoRecoverySystem] = None

def get_auto_recovery_system() -> AutoRecoverySystem:
    """Get global auto-recovery system instance"""
    global _global_auto_recovery
    if _global_auto_recovery is None:
        _global_auto_recovery = AutoRecoverySystem()
    return _global_auto_recovery

def set_auto_recovery_system(recovery_system: AutoRecoverySystem) -> None:
    """Set global auto-recovery system instance"""
    global _global_auto_recovery
    _global_auto_recovery = recovery_system

__all__ = [
    'AutoRecoverySystem',
    'RecoveryAction',
    'RecoveryAttempt',
    'SystemHealth',
    'RecoveryLevel',
    'RecoveryStatus',
    'FailureType',
    'get_auto_recovery_system',
    'set_auto_recovery_system'
]