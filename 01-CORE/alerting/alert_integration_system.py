#!/usr/bin/env python3
"""
Alert Integration System - ICT Engine v6.0 Enterprise
====================================================

Integrador central que conecta todos los sistemas de alertas.
Une el ProductionSystemMonitor, AutoRecoverySystem y AdvancedAlertManager.

Características:
✅ Integración centralizada de alertas
✅ Routing inteligente de notificaciones
✅ Deduplicación de alertas
✅ Escalamiento automático por prioridad
✅ Métricas de alertas en tiempo real
✅ Interfaz unificada para dashboards

Autor: ICT Engine v6.0 Team
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger

import threading
import time
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Tuple, Union
import hashlib

try:
    from protocols.logging_central_protocols import create_production_logger, LogLevel
    logger = create_production_logger("AlertIntegrationSystem", LogLevel.INFO)
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AlertIntegrationSystem")

# Import related systems
get_advanced_alert_manager = None
AdvancedAlertManager = None

try:
    from monitoring.production_system_monitor import ProductionSystemMonitor, Alert as SystemAlert, AlertLevel as SystemAlertLevel
    from emergency.auto_recovery_system import AutoRecoverySystem, RecoveryAttempt, FailureType
    from alerting.manager import AdvancedAlertManager
    
    # Try to import the function
    try:
        from alerting.manager import get_advanced_alert_manager
        ADVANCED_ALERT_MANAGER_AVAILABLE = True
    except ImportError:
        ADVANCED_ALERT_MANAGER_AVAILABLE = False
    
    ALERT_SYSTEMS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some alert systems not available: {e}", "IMPORT")
    ALERT_SYSTEMS_AVAILABLE = False
    ADVANCED_ALERT_MANAGER_AVAILABLE = False

class IntegratedAlertLevel(Enum):
    """Niveles de alerta integrados"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertSource(Enum):
    """Fuentes de alertas"""
    SYSTEM_MONITOR = "system_monitor"
    AUTO_RECOVERY = "auto_recovery"
    TRADING_ENGINE = "trading_engine"
    MT5_CONNECTION = "mt5_connection"
    MANUAL = "manual"
    EXTERNAL = "external"

class AlertCategory(Enum):
    """Categorías de alertas"""
    SYSTEM_RESOURCES = "system_resources"
    TRADING_PERFORMANCE = "trading_performance"
    CONNECTION_HEALTH = "connection_health"
    MARKET_DATA = "market_data"
    RISK_MANAGEMENT = "risk_management"
    RECOVERY_ACTIONS = "recovery_actions"
    EMERGENCY_EVENTS = "emergency_events"

@dataclass
class IntegratedAlert:
    """Alerta integrada del sistema"""
    id: str
    timestamp: datetime
    level: IntegratedAlertLevel
    source: AlertSource
    category: AlertCategory
    title: str
    message: str
    
    # Context and metadata
    component: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # State management
    acknowledged: bool = False
    resolved: bool = False
    escalated: bool = False
    
    # Routing and notifications
    channels: List[str] = field(default_factory=list)
    notified_at: Optional[datetime] = None
    
    # Correlation
    correlation_id: Optional[str] = None
    parent_alert_id: Optional[str] = None
    related_alerts: List[str] = field(default_factory=list)
    
    # Resolution
    resolved_at: Optional[datetime] = None
    resolution_message: Optional[str] = None
    auto_resolved: bool = False

@dataclass
class AlertStatistics:
    """Estadísticas de alertas"""
    timestamp: datetime
    
    # Counts by level
    debug_count: int = 0
    info_count: int = 0
    warning_count: int = 0
    critical_count: int = 0
    emergency_count: int = 0
    
    # Counts by source
    system_monitor_count: int = 0
    auto_recovery_count: int = 0
    trading_engine_count: int = 0
    
    # Response metrics
    avg_response_time_seconds: float = 0.0
    avg_resolution_time_minutes: float = 0.0
    acknowledgment_rate_percent: float = 0.0
    auto_resolution_rate_percent: float = 0.0
    
    # Active state
    active_alerts: int = 0
    escalated_alerts: int = 0
    unacknowledged_critical: int = 0

class AlertIntegrationSystem:
    """
    Sistema de integración de alertas
    
    Centraliza y coordina todas las alertas del sistema,
    proporcionando una interfaz unificada para gestión,
    routing y monitoreo de alertas.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # State management
        self.is_active = False
        self.start_time: Optional[datetime] = None
        
        # Alert storage and management
        self.active_alerts: Dict[str, IntegratedAlert] = {}
        self.alert_history: List[IntegratedAlert] = []
        self.alert_statistics: List[AlertStatistics] = []
        
        # Deduplication and correlation
        self.alert_signatures: Dict[str, str] = {}  # signature -> alert_id
        self.correlation_groups: Dict[str, List[str]] = {}  # correlation_id -> alert_ids
        
        # Threading and processing
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="AlertIntegration")
        self._alert_processor_thread: Optional[threading.Thread] = None
        self._statistics_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        self._alerts_lock = threading.RLock()
        
        # Connected systems
        self._system_monitor: Optional[ProductionSystemMonitor] = None
        self._auto_recovery: Optional[AutoRecoverySystem] = None
        self._alert_manager: Optional[Any] = None  # AdvancedAlertManager
        
        # Callbacks and handlers
        self.alert_handlers: Dict[AlertCategory, List[Callable[[IntegratedAlert], None]]] = {}
        self.escalation_handlers: List[Callable[[IntegratedAlert], None]] = []
        self.resolution_handlers: List[Callable[[IntegratedAlert], None]] = []
        # Throttling for escalation log messages
        self._last_escalation_log: Dict[str, datetime] = {}
        
        # Alert routing rules
        self.routing_rules: List[Dict[str, Any]] = []
        self._setup_default_routing_rules()
        
        logger.info("AlertIntegrationSystem initialized", "INIT")
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            # Processing intervals
            'alert_processing_interval_seconds': 2.0,
            'statistics_interval_minutes': 5.0,
            
            # Storage limits
            'max_active_alerts': 500,
            'max_history_size': 5000,
            'max_statistics_history': 1000,
            
            # Deduplication
            'deduplication_enabled': True,
            'deduplication_window_minutes': 5.0,
            
            # Auto-resolution
            'auto_resolution_enabled': True,
            'auto_resolution_timeout_minutes': 30.0,
            
            # Escalation
            'escalation_enabled': True,
            'escalation_timeout_minutes': 15.0,
            'critical_escalation_timeout_minutes': 5.0,
            
            # Persistence
            'persist_alerts': True,
            'alerts_file': '04-DATA/data/integrated_alerts.json',
            'statistics_file': '04-DATA/data/alert_statistics.json'
        }
    
    def _setup_default_routing_rules(self) -> None:
        """Setup default alert routing rules"""
        self.routing_rules = [
            # Emergency alerts - all channels
            {
                'condition': {'level': IntegratedAlertLevel.EMERGENCY},
                'channels': ['email', 'sms', 'discord', 'telegram'],
                'immediate': True
            },
            # Critical system alerts
            {
                'condition': {
                    'level': IntegratedAlertLevel.CRITICAL,
                    'category': AlertCategory.SYSTEM_RESOURCES
                },
                'channels': ['email', 'discord'],
                'immediate': True
            },
            # Trading performance alerts
            {
                'condition': {
                    'level': IntegratedAlertLevel.CRITICAL,
                    'category': AlertCategory.TRADING_PERFORMANCE
                },
                'channels': ['email', 'telegram'],
                'immediate': True
            },
            # Recovery actions
            {
                'condition': {'source': AlertSource.AUTO_RECOVERY},
                'channels': ['discord'],
                'immediate': False
            },
            # Default routing for warnings
            {
                'condition': {'level': IntegratedAlertLevel.WARNING},
                'channels': ['discord'],
                'immediate': False
            }
        ]
    
    def start_integration(self) -> bool:
        """Iniciar sistema de integración"""
        if self.is_active:
            logger.warning("Alert integration already active", "START")
            return True
        
        logger.info("Starting alert integration system", "START")
        
        try:
            self.is_active = True
            self.start_time = datetime.now()
            self._shutdown_event.clear()
            
            # Connect to available systems
            self._connect_systems()
            
            # Start processing threads
            self._alert_processor_thread = threading.Thread(
                target=self._alert_processing_loop,
                name="AlertProcessor",
                daemon=True
            )
            self._alert_processor_thread.start()
            
            self._statistics_thread = threading.Thread(
                target=self._statistics_loop,
                name="AlertStatistics",
                daemon=True
            )
            self._statistics_thread.start()
            
            # Load previous state
            self._load_persistent_state()
            
            logger.info("Alert integration system started successfully", "START")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start alert integration: {e}", "START")
            self.is_active = False
            return False
    
    def stop_integration(self) -> bool:
        """Detener sistema de integración"""
        if not self.is_active:
            logger.warning("Alert integration not active", "STOP")
            return True
        
        logger.info("Stopping alert integration system", "STOP")
        
        try:
            self.is_active = False
            self._shutdown_event.set()
            
            # Wait for threads
            for thread in [self._alert_processor_thread, self._statistics_thread]:
                if thread and thread.is_alive():
                    thread.join(timeout=2.0)
            
            # Shutdown executor
            try:
                # Fast shutdown: cancel pending tasks and return quickly
                self._executor.shutdown(wait=False, cancel_futures=True)  # type: ignore[arg-type]
            except TypeError:
                # Fallback for older Python
                self._executor.shutdown(wait=False)
            
            # Save state
            self._save_persistent_state()
            
            logger.info("Alert integration system stopped", "STOP")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping alert integration: {e}", "STOP")
            return False
    
    def _connect_systems(self) -> None:
        """Connect to available alert systems"""
        if not ALERT_SYSTEMS_AVAILABLE:
            logger.warning("Alert systems not available for integration", "CONNECT")
            return
        
        try:
            # Connect to AdvancedAlertManager
            try:
                if ADVANCED_ALERT_MANAGER_AVAILABLE and get_advanced_alert_manager is not None:
                    self._alert_manager = get_advanced_alert_manager()
                    logger.info("Connected to AdvancedAlertManager", "CONNECT")
                elif ALERT_SYSTEMS_AVAILABLE and AdvancedAlertManager is not None:
                    # Create direct instance
                    self._alert_manager = AdvancedAlertManager()
                    logger.info("Created direct AdvancedAlertManager instance", "CONNECT")
                else:
                    logger.warning("AdvancedAlertManager not available", "CONNECT")
            except Exception as e:
                logger.warning(f"Could not connect to AdvancedAlertManager: {e}", "CONNECT")
            
            # Connect to existing systems would be done through dependency injection
            # For now, we'll register callbacks when systems are provided
            
        except Exception as e:
            logger.error(f"Error connecting to systems: {e}", "CONNECT")
    
    def connect_system_monitor(self, monitor: 'ProductionSystemMonitor') -> None:
        """Connect ProductionSystemMonitor"""
        try:
            self._system_monitor = monitor
            
            # Register callback for system monitor alerts
            monitor.add_alert_callback(self._handle_system_monitor_alert)
            
            logger.info("Connected to ProductionSystemMonitor", "CONNECT")
            
        except Exception as e:
            logger.error(f"Failed to connect system monitor: {e}", "CONNECT")
    
    def connect_auto_recovery(self, recovery_system: 'AutoRecoverySystem') -> None:
        """Connect AutoRecoverySystem"""
        try:
            self._auto_recovery = recovery_system
            
            # Register callbacks
            recovery_system.add_failure_callback(self._handle_failure_detected)
            recovery_system.add_recovery_callback(self._handle_recovery_attempt)
            
            logger.info("Connected to AutoRecoverySystem", "CONNECT")
            
        except Exception as e:
            logger.error(f"Failed to connect auto recovery: {e}", "CONNECT")
    
    def _alert_processing_loop(self) -> None:
        """Main alert processing loop"""
        interval = self.config['alert_processing_interval_seconds']
        
        while self.is_active and not self._shutdown_event.is_set():
            try:
                # Process pending alerts
                self._process_pending_alerts()
                
                # Check for escalations
                if self.config.get('escalation_enabled', True):
                    self._check_escalations()
                
                # Check for auto-resolutions
                if self.config.get('auto_resolution_enabled', True):
                    self._check_auto_resolutions()
                
                # Cleanup old alerts
                self._cleanup_old_alerts()
                
                if self._shutdown_event.wait(interval):
                    break
                
            except Exception as e:
                logger.error(f"Error in alert processing loop: {e}", "PROCESSING")
                if self._shutdown_event.wait(interval):
                    break
    
    def _statistics_loop(self) -> None:
        """Statistics collection loop"""
        interval_minutes = self.config['statistics_interval_minutes']
        interval_seconds = interval_minutes * 60
        
        while self.is_active and not self._shutdown_event.is_set():
            try:
                # Generate statistics
                stats = self._generate_statistics()
                
                with self._alerts_lock:
                    self.alert_statistics.append(stats)
                    
                    # Limit statistics history
                    max_stats = self.config.get('max_statistics_history', 1000)
                    if len(self.alert_statistics) > max_stats:
                        self.alert_statistics = self.alert_statistics[-max_stats:]
                
                # Save statistics
                self._save_statistics()
                
                if self._shutdown_event.wait(interval_seconds):
                    break
                
            except Exception as e:
                logger.error(f"Error in statistics loop: {e}", "STATISTICS")
                if self._shutdown_event.wait(interval_seconds):
                    break
    
    # Alert handlers from different sources
    def _handle_system_monitor_alert(self, system_alert: 'SystemAlert') -> None:
        """Handle alert from ProductionSystemMonitor"""
        try:
            # Convert system alert to integrated alert
            integrated_alert = self._convert_system_alert(system_alert)
            
            # Process the alert
            self._process_alert(integrated_alert)
            
        except Exception as e:
            logger.error(f"Error handling system monitor alert: {e}", "HANDLER")
    
    def _handle_failure_detected(self, failure_type: 'FailureType', metrics: Dict[str, Any]) -> None:
        """Handle failure detection from AutoRecoverySystem"""
        try:
            # Create alert for detected failure
            alert = IntegratedAlert(
                id=self._generate_alert_id("failure", failure_type.value),
                timestamp=datetime.now(),
                level=self._map_failure_to_level(failure_type),
                source=AlertSource.AUTO_RECOVERY,
                category=self._map_failure_to_category(failure_type),
                title=f"System Failure Detected: {failure_type.value}",
                message=f"Auto-recovery system detected failure: {failure_type.value}",
                component="AutoRecovery",
                metadata={
                    'failure_type': failure_type.value,
                    'detection_metrics': metrics
                },
                tags=['auto_recovery', 'system_failure']
            )
            
            self._process_alert(alert)
            
        except Exception as e:
            logger.error(f"Error handling failure detection: {e}", "HANDLER")
    
    def _handle_recovery_attempt(self, recovery_attempt: 'RecoveryAttempt') -> None:
        """Handle recovery attempt from AutoRecoverySystem"""
        try:
            # Create alert for recovery attempt
            level = IntegratedAlertLevel.INFO
            if recovery_attempt.status.value == "failed":
                level = IntegratedAlertLevel.WARNING
            elif recovery_attempt.status.value == "success":
                level = IntegratedAlertLevel.INFO
            
            alert = IntegratedAlert(
                id=self._generate_alert_id("recovery", recovery_attempt.id),
                timestamp=recovery_attempt.timestamp,
                level=level,
                source=AlertSource.AUTO_RECOVERY,
                category=AlertCategory.RECOVERY_ACTIONS,
                title=f"Recovery Attempt: {recovery_attempt.action_id}",
                message=f"Recovery attempt {recovery_attempt.status.value}: {recovery_attempt.action_id}",
                component="AutoRecovery",
                metadata={
                    'recovery_id': recovery_attempt.id,
                    'action_id': recovery_attempt.action_id,
                    'failure_type': recovery_attempt.failure_type.value,
                    'status': recovery_attempt.status.value,
                    'duration_seconds': recovery_attempt.duration_seconds,
                    'attempt_number': recovery_attempt.attempt_number
                },
                tags=['auto_recovery', 'recovery_attempt', recovery_attempt.status.value]
            )
            
            # Auto-resolve related failure alerts if recovery was successful
            if recovery_attempt.status.value == "success":
                self._auto_resolve_related_failures(recovery_attempt.failure_type)
            
            self._process_alert(alert)
            
        except Exception as e:
            logger.error(f"Error handling recovery attempt: {e}", "HANDLER")
    
    def _convert_system_alert(self, system_alert: 'SystemAlert') -> IntegratedAlert:
        """Convert SystemAlert to IntegratedAlert"""
        # Map system alert level to integrated level
        level_mapping = {
            'info': IntegratedAlertLevel.INFO,
            'warning': IntegratedAlertLevel.WARNING,
            'critical': IntegratedAlertLevel.CRITICAL
        }
        
        level = level_mapping.get(system_alert.level.value, IntegratedAlertLevel.WARNING)
        
        # Determine category based on component
        category = AlertCategory.SYSTEM_RESOURCES
        if 'trading' in system_alert.component.lower():
            category = AlertCategory.TRADING_PERFORMANCE
        elif 'connection' in system_alert.component.lower() or 'mt5' in system_alert.component.lower():
            category = AlertCategory.CONNECTION_HEALTH
        
        return IntegratedAlert(
            id=self._generate_alert_id("system", system_alert.component),
            timestamp=system_alert.timestamp,
            level=level,
            source=AlertSource.SYSTEM_MONITOR,
            category=category,
            title=f"System Alert: {system_alert.component}",
            message=system_alert.message,
            component=system_alert.component,
            metadata=system_alert.metrics,
            tags=['system_monitor', system_alert.component.lower()]
        )
    
    def _process_alert(self, alert: IntegratedAlert) -> None:
        """Process an integrated alert"""
        try:
            # Check for deduplication
            if self.config.get('deduplication_enabled', True):
                if self._is_duplicate_alert(alert):
                    logger.debug(f"Duplicate alert filtered: {alert.title}", "DEDUP")
                    return
            
            # Add to active alerts
            with self._alerts_lock:
                self.active_alerts[alert.id] = alert
                self.alert_history.append(alert)
                
                # Update signatures for deduplication
                signature = self._generate_alert_signature(alert)
                self.alert_signatures[signature] = alert.id
                
                # Limit active alerts
                if len(self.active_alerts) > self.config.get('max_active_alerts', 500):
                    oldest_id = min(self.active_alerts.keys(), 
                                  key=lambda x: self.active_alerts[x].timestamp)
                    del self.active_alerts[oldest_id]
                
                # Limit history
                max_history = self.config.get('max_history_size', 5000)
                if len(self.alert_history) > max_history:
                    self.alert_history = self.alert_history[-max_history:]
            
            # Route alert to appropriate channels
            self._route_alert(alert)
            
            # Trigger handlers
            self._trigger_alert_handlers(alert)
            
            # Log alert
            logger.info(f"Processed alert: {alert.level.value.upper()} - {alert.title}", "ALERT")
            
        except Exception as e:
            logger.error(f"Error processing alert: {e}", "PROCESSING")
    
    def _is_duplicate_alert(self, alert: IntegratedAlert) -> bool:
        """Check if alert is a duplicate"""
        signature = self._generate_alert_signature(alert)
        
        if signature not in self.alert_signatures:
            return False
        
        # Check if existing alert is within deduplication window
        existing_alert_id = self.alert_signatures[signature]
        if existing_alert_id in self.active_alerts:
            existing_alert = self.active_alerts[existing_alert_id]
            time_diff = alert.timestamp - existing_alert.timestamp
            
            window_minutes = self.config.get('deduplication_window_minutes', 5.0)
            if time_diff.total_seconds() / 60 < window_minutes:
                return True
        
        return False
    
    def _generate_alert_signature(self, alert: IntegratedAlert) -> str:
        """Generate signature for alert deduplication"""
        # Create signature based on key alert properties
        signature_data = f"{alert.source.value}:{alert.category.value}:{alert.component}:{alert.title}"
        return hashlib.md5(signature_data.encode()).hexdigest()
    
    def _route_alert(self, alert: IntegratedAlert) -> None:
        """Route alert to appropriate channels"""
        matching_channels = set()
        immediate_notification = False
        
        # Find matching routing rules
        for rule in self.routing_rules:
            if self._matches_rule_condition(alert, rule['condition']):
                matching_channels.update(rule.get('channels', []))
                if rule.get('immediate', False):
                    immediate_notification = True
        
        # Set channels on alert
        alert.channels = list(matching_channels)
        
        # Send notifications
        if matching_channels:
            self._send_notifications(alert, immediate_notification)
    
    def _matches_rule_condition(self, alert: IntegratedAlert, condition: Dict[str, Any]) -> bool:
        """Check if alert matches routing rule condition"""
        for key, value in condition.items():
            alert_value = getattr(alert, key, None)
            
            if alert_value is not None and hasattr(alert_value, 'value'):  # Handle enums
                alert_value = alert_value.value
            
            if isinstance(value, list):
                if alert_value not in value:
                    return False
            elif alert_value != value:
                return False
        
        return True
    
    def _send_notifications(self, alert: IntegratedAlert, immediate: bool = False) -> None:
        """Send notifications through alert manager"""
        try:
            if self._alert_manager and hasattr(self._alert_manager, 'create_alert'):
                # Convert to AdvancedAlertManager format
                alert_data = {
                    'level': alert.level.value,
                    'title': alert.title,
                    'message': alert.message,
                    'component': alert.component,
                    'metadata': alert.metadata,
                    'channels': alert.channels
                }
                
                # Send through alert manager
                self._alert_manager.create_alert(**alert_data)
                alert.notified_at = datetime.now()
                
                logger.info(f"Sent notifications for alert {alert.id} via channels: {alert.channels}", "NOTIFY")
            
        except Exception as e:
            logger.error(f"Error sending notifications: {e}", "NOTIFY")
    
    def _trigger_alert_handlers(self, alert: IntegratedAlert) -> None:
        """Trigger registered alert handlers"""
        try:
            # Category-specific handlers
            if alert.category in self.alert_handlers:
                for handler in self.alert_handlers[alert.category]:
                    try:
                        handler(alert)
                    except Exception as e:
                        logger.error(f"Alert handler error: {e}", "HANDLER")
            
        except Exception as e:
            logger.error(f"Error triggering alert handlers: {e}", "HANDLER")
    
    def _check_escalations(self) -> None:
        """Check for alerts that need escalation"""
        if not self.config.get('escalation_enabled', True):
            return
        
        now = datetime.now()
        escalation_timeout = timedelta(minutes=self.config.get('escalation_timeout_minutes', 15))
        critical_timeout = timedelta(minutes=self.config.get('critical_escalation_timeout_minutes', 5))
        
        with self._alerts_lock:
            for alert in self.active_alerts.values():
                if alert.escalated or alert.acknowledged or alert.resolved:
                    continue
                
                # Determine timeout based on level
                timeout = critical_timeout if alert.level in [IntegratedAlertLevel.CRITICAL, IntegratedAlertLevel.EMERGENCY] else escalation_timeout
                
                if now - alert.timestamp > timeout:
                    self._escalate_alert(alert)
    
    def _escalate_alert(self, alert: IntegratedAlert) -> None:
        """Escalate an alert"""
        try:
            alert.escalated = True
            
            # Notify escalation handlers
            for handler in self.escalation_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Escalation handler error: {e}", "ESCALATION")
            
            # Send escalation notification
            escalation_alert = IntegratedAlert(
                id=self._generate_alert_id("escalation", alert.id),
                timestamp=datetime.now(),
                level=IntegratedAlertLevel.CRITICAL,
                source=alert.source,
                category=AlertCategory.EMERGENCY_EVENTS,
                title=f"ESCALATED: {alert.title}",
                message=f"Alert escalated due to no response: {alert.message}",
                component=alert.component,
                metadata=alert.metadata,
                tags=['escalation'] + alert.tags,
                parent_alert_id=alert.id
            )
            
            self._route_alert(escalation_alert)
            
            key = alert.id or alert.title
            now_ts = datetime.now()
            cooldown = timedelta(seconds=self.config.get('escalation_log_cooldown_seconds', 10))
            last_ts = self._last_escalation_log.get(key)
            if (not last_ts) or ((now_ts - last_ts) > cooldown):
                logger.warning(f"Alert escalated: {alert.title}", "ESCALATION")
                self._last_escalation_log[key] = now_ts
            
        except Exception as e:
            logger.error(f"Error escalating alert: {e}", "ESCALATION")
    
    def _check_auto_resolutions(self) -> None:
        """Check for alerts that can be auto-resolved"""
        if not self.config.get('auto_resolution_enabled', True):
            return
        
        now = datetime.now()
        timeout = timedelta(minutes=self.config.get('auto_resolution_timeout_minutes', 30))
        
        with self._alerts_lock:
            for alert in list(self.active_alerts.values()):
                if alert.resolved:
                    continue
                
                # Auto-resolve old INFO level alerts
                if alert.level == IntegratedAlertLevel.INFO and now - alert.timestamp > timeout:
                    self._resolve_alert(alert.id, "Auto-resolved due to timeout", auto_resolved=True)
    
    def _auto_resolve_related_failures(self, failure_type: 'FailureType') -> None:
        """Auto-resolve alerts related to a successful recovery"""
        with self._alerts_lock:
            for alert in list(self.active_alerts.values()):
                if alert.resolved:
                    continue
                
                # Check if alert is related to the recovered failure
                if (alert.source == AlertSource.AUTO_RECOVERY and 
                    alert.metadata.get('failure_type') == failure_type.value):
                    self._resolve_alert(alert.id, f"Auto-resolved: Recovery successful for {failure_type.value}", auto_resolved=True)
    
    def _cleanup_old_alerts(self) -> None:
        """Clean up old resolved alerts"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        with self._alerts_lock:
            # Remove old resolved alerts from active alerts
            to_remove = []
            for alert_id, alert in self.active_alerts.items():
                if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_time:
                    to_remove.append(alert_id)
            
            for alert_id in to_remove:
                del self.active_alerts[alert_id]
    
    # Helper methods
    def _map_failure_to_level(self, failure_type: 'FailureType') -> IntegratedAlertLevel:
        """Map failure type to alert level"""
        critical_failures = ['LOW_MARGIN_LEVEL', 'INTERNET_DISCONNECTED', 'SYSTEM_FREEZE']
        
        if failure_type.value in critical_failures:
            return IntegratedAlertLevel.CRITICAL
        else:
            return IntegratedAlertLevel.WARNING
    
    def _map_failure_to_category(self, failure_type: 'FailureType') -> AlertCategory:
        """Map failure type to alert category"""
        category_mapping = {
            'MT5_CONNECTION_LOST': AlertCategory.CONNECTION_HEALTH,
            'INTERNET_DISCONNECTED': AlertCategory.CONNECTION_HEALTH,
            'HIGH_MEMORY_USAGE': AlertCategory.SYSTEM_RESOURCES,
            'HIGH_CPU_USAGE': AlertCategory.SYSTEM_RESOURCES,
            'DISK_FULL': AlertCategory.SYSTEM_RESOURCES,
            'LOW_MARGIN_LEVEL': AlertCategory.RISK_MANAGEMENT,
            'MARKET_DATA_STALE': AlertCategory.MARKET_DATA,
            'TRADING_ENGINE_STUCK': AlertCategory.TRADING_PERFORMANCE,
        }
        
        return category_mapping.get(failure_type.value, AlertCategory.SYSTEM_RESOURCES)
    
    def _generate_alert_id(self, prefix: str, suffix: str) -> str:
        """Generate unique alert ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{prefix}_{suffix}_{timestamp}"
        hash_digest = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"{prefix}_{hash_digest}"
    
    def _generate_statistics(self) -> AlertStatistics:
        """Generate current alert statistics"""
        stats = AlertStatistics(timestamp=datetime.now())
        
        with self._alerts_lock:
            # Count by level
            for alert in self.active_alerts.values():
                if alert.level == IntegratedAlertLevel.DEBUG:
                    stats.debug_count += 1
                elif alert.level == IntegratedAlertLevel.INFO:
                    stats.info_count += 1
                elif alert.level == IntegratedAlertLevel.WARNING:
                    stats.warning_count += 1
                elif alert.level == IntegratedAlertLevel.CRITICAL:
                    stats.critical_count += 1
                elif alert.level == IntegratedAlertLevel.EMERGENCY:
                    stats.emergency_count += 1
            
            # Count by source
            for alert in self.active_alerts.values():
                if alert.source == AlertSource.SYSTEM_MONITOR:
                    stats.system_monitor_count += 1
                elif alert.source == AlertSource.AUTO_RECOVERY:
                    stats.auto_recovery_count += 1
                elif alert.source == AlertSource.TRADING_ENGINE:
                    stats.trading_engine_count += 1
            
            # Calculate metrics
            stats.active_alerts = len(self.active_alerts)
            stats.escalated_alerts = len([a for a in self.active_alerts.values() if a.escalated])
            stats.unacknowledged_critical = len([a for a in self.active_alerts.values() 
                                               if not a.acknowledged and a.level in [IntegratedAlertLevel.CRITICAL, IntegratedAlertLevel.EMERGENCY]])
            
            # Calculate rates from recent history
            recent_alerts = [a for a in self.alert_history if a.timestamp > datetime.now() - timedelta(hours=1)]
            if recent_alerts:
                acknowledged = len([a for a in recent_alerts if a.acknowledged])
                stats.acknowledgment_rate_percent = (acknowledged / len(recent_alerts)) * 100
                
                auto_resolved = len([a for a in recent_alerts if a.auto_resolved])
                stats.auto_resolution_rate_percent = (auto_resolved / len(recent_alerts)) * 100
        
        return stats
    
    # Public API methods
    def create_manual_alert(self, 
                          level: IntegratedAlertLevel,
                          category: AlertCategory,
                          title: str,
                          message: str,
                          component: str = "Manual",
                          metadata: Optional[Dict[str, Any]] = None,
                          tags: Optional[List[str]] = None) -> str:
        """Create manual alert"""
        alert = IntegratedAlert(
            id=self._generate_alert_id("manual", component),
            timestamp=datetime.now(),
            level=level,
            source=AlertSource.MANUAL,
            category=category,
            title=title,
            message=message,
            component=component,
            metadata=metadata or {},
            tags=tags or ['manual']
        )
        
        self._process_alert(alert)
        return alert.id
    
    def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """Acknowledge an alert"""
        with self._alerts_lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.acknowledged = True
                alert.metadata['acknowledged_by'] = user
                alert.metadata['acknowledged_at'] = datetime.now().isoformat()
                
                logger.info(f"Alert acknowledged: {alert.title} by {user}", "ACK")
            
                # Throttle duplicate escalation logs for the same alert
                key = alert.id or alert.title
                now_ts = datetime.now()
                cooldown = timedelta(seconds=self.config.get('escalation_log_cooldown_seconds', 10))
                last_ts = self._last_escalation_log.get(key)
                if not last_ts or (now_ts - last_ts) > cooldown:
                    logger.warning(f"Alert escalated: {alert.title}", "ESCALATION")
                    self._last_escalation_log[key] = now_ts
        return False
    
    def resolve_alert(self, alert_id: str, resolution_message: str = "", user: str = "system") -> bool:
        """Resolve an alert"""
        return self._resolve_alert(alert_id, resolution_message, user, auto_resolved=False)
    
    def _resolve_alert(self, alert_id: str, resolution_message: str = "", user: str = "system", auto_resolved: bool = False) -> bool:
        """Internal method to resolve alert"""
        with self._alerts_lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.now()
                alert.resolution_message = resolution_message
                alert.auto_resolved = auto_resolved
                alert.metadata['resolved_by'] = user
                alert.metadata['resolved_at'] = alert.resolved_at.isoformat()
                
                # Notify resolution handlers
                for handler in self.resolution_handlers:
                    try:
                        handler(alert)
                    except Exception as e:
                        logger.error(f"Resolution handler error: {e}", "RESOLUTION")
                
                logger.info(f"Alert resolved: {alert.title} by {user}", "RESOLVE")
                return True
        
        return False
    
    def get_active_alerts(self, level: Optional[IntegratedAlertLevel] = None, category: Optional[AlertCategory] = None) -> List[IntegratedAlert]:
        """Get active alerts with optional filtering"""
        with self._alerts_lock:
            alerts = list(self.active_alerts.values())
            
            if level:
                alerts = [a for a in alerts if a.level == level]
            
            if category:
                alerts = [a for a in alerts if a.category == category]
            
            return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_alert_statistics(self, hours: int = 24) -> AlertStatistics:
        """Get current alert statistics"""
        if self.alert_statistics:
            return self.alert_statistics[-1]
        else:
            return self._generate_statistics()
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        with self._alerts_lock:
            active_count = len(self.active_alerts)
            critical_count = len([a for a in self.active_alerts.values() 
                                if a.level in [IntegratedAlertLevel.CRITICAL, IntegratedAlertLevel.EMERGENCY]])
            
            # Determine overall health
            if critical_count > 0:
                health_status = "critical"
            elif active_count > 10:
                health_status = "degraded"
            elif active_count > 0:
                health_status = "warning"
            else:
                health_status = "healthy"
            
            return {
                'timestamp': datetime.now().isoformat(),
                'health_status': health_status,
                'active_alerts': active_count,
                'critical_alerts': critical_count,
                'systems_connected': {
                    'system_monitor': self._system_monitor is not None,
                    'auto_recovery': self._auto_recovery is not None,
                    'alert_manager': self._alert_manager is not None
                },
                'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0
            }
    
    # Handler registration
    def add_alert_handler(self, category: AlertCategory, handler: Callable[[IntegratedAlert], None]) -> None:
        """Add alert handler for specific category"""
        if category not in self.alert_handlers:
            self.alert_handlers[category] = []
        self.alert_handlers[category].append(handler)
    
    def add_escalation_handler(self, handler: Callable[[IntegratedAlert], None]) -> None:
        """Add escalation handler"""
        self.escalation_handlers.append(handler)
    
    def add_resolution_handler(self, handler: Callable[[IntegratedAlert], None]) -> None:
        """Add resolution handler"""
        self.resolution_handlers.append(handler)
    
    # Persistence methods
    def _save_persistent_state(self) -> None:
        """Save persistent state to disk"""
        try:
            if not self.config.get('persist_alerts', True):
                return
            
            # Save alerts
            alerts_data = {
                'timestamp': datetime.now().isoformat(),
                'active_alerts': [self._alert_to_dict(a) for a in self.active_alerts.values()],
                'recent_history': [self._alert_to_dict(a) for a in self.alert_history[-100:]]
            }
            
            alerts_file = Path(self.config['alerts_file'])
            alerts_file.parent.mkdir(exist_ok=True)
            
            with open(alerts_file, 'w', encoding='utf-8') as f:
                json.dump(alerts_data, f, indent=2)
            
        except Exception as e:
            logger.warning(f"Failed to save persistent state: {e}", "PERSISTENCE")
    
    def _save_statistics(self) -> None:
        """Save statistics to disk"""
        try:
            stats_file = Path(self.config['statistics_file'])
            stats_file.parent.mkdir(exist_ok=True)
            
            # Ensure datetime fields are serialized
            stats_data = [self._statistics_to_dict(stats) for stats in self.alert_statistics[-100:]]
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2)
            
        except Exception as e:
            logger.warning(f"Failed to save statistics: {e}", "PERSISTENCE")

    def _statistics_to_dict(self, stats: AlertStatistics) -> Dict[str, Any]:
        """Convert AlertStatistics to JSON-serializable dict"""
        data = asdict(stats)
        ts = data.get('timestamp')
        if isinstance(ts, datetime):
            data['timestamp'] = ts.isoformat()
        return data
    
    def _load_persistent_state(self) -> None:
        """Load persistent state from disk"""
        try:
            alerts_file = Path(self.config['alerts_file'])
            if alerts_file.exists():
                with open(alerts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load active alerts
                for alert_data in data.get('active_alerts', []):
                    alert = self._dict_to_alert(alert_data)
                    if alert:
                        self.active_alerts[alert.id] = alert
                
                logger.info("Persistent state loaded successfully", "PERSISTENCE")
        
        except Exception as e:
            logger.warning(f"Failed to load persistent state: {e}", "PERSISTENCE")
    
    def _alert_to_dict(self, alert: IntegratedAlert) -> Dict[str, Any]:
        """Convert IntegratedAlert to dictionary"""
        data = asdict(alert)
        # Convert datetime objects
        data['timestamp'] = alert.timestamp.isoformat()
        if alert.notified_at:
            data['notified_at'] = alert.notified_at.isoformat()
        if alert.resolved_at:
            data['resolved_at'] = alert.resolved_at.isoformat()
        # Convert enums
        data['level'] = alert.level.value
        data['source'] = alert.source.value
        data['category'] = alert.category.value
        return data
    
    def _dict_to_alert(self, data: Dict[str, Any]) -> Optional[IntegratedAlert]:
        """Convert dictionary to IntegratedAlert"""
        try:
            alert = IntegratedAlert(
                id=data['id'],
                timestamp=datetime.fromisoformat(data['timestamp']),
                level=IntegratedAlertLevel(data['level']),
                source=AlertSource(data['source']),
                category=AlertCategory(data['category']),
                title=data['title'],
                message=data['message'],
                component=data.get('component', ''),
                metadata=data.get('metadata', {}),
                tags=data.get('tags', []),
                acknowledged=data.get('acknowledged', False),
                resolved=data.get('resolved', False),
                escalated=data.get('escalated', False),
                channels=data.get('channels', []),
                correlation_id=data.get('correlation_id'),
                parent_alert_id=data.get('parent_alert_id'),
                related_alerts=data.get('related_alerts', []),
                resolution_message=data.get('resolution_message'),
                auto_resolved=data.get('auto_resolved', False)
            )
            
            # Handle optional datetime fields
            if data.get('notified_at'):
                alert.notified_at = datetime.fromisoformat(data['notified_at'])
            if data.get('resolved_at'):
                alert.resolved_at = datetime.fromisoformat(data['resolved_at'])
            
            return alert
            
        except (KeyError, ValueError, TypeError):
            return None
    
    def _process_pending_alerts(self) -> None:
        """Process any pending alerts"""
        # This method can be used for batch processing or delayed alerts
        pass

# Global instance management
_global_alert_integration: Optional[AlertIntegrationSystem] = None

def get_alert_integration_system() -> AlertIntegrationSystem:
    """Get global alert integration system instance"""
    global _global_alert_integration
    if _global_alert_integration is None:
        _global_alert_integration = AlertIntegrationSystem()
    return _global_alert_integration

def set_alert_integration_system(integration_system: AlertIntegrationSystem) -> None:
    """Set global alert integration system instance"""
    global _global_alert_integration
    _global_alert_integration = integration_system

__all__ = [
    'AlertIntegrationSystem',
    'IntegratedAlert',
    'AlertStatistics',
    'IntegratedAlertLevel',
    'AlertSource',
    'AlertCategory',
    'get_alert_integration_system',
    'set_alert_integration_system'
]